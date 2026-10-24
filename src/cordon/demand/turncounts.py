"""Turn City turning-movement counts (TMC) into SUMO calibration targets.

Usage: uv run python -m cordon.demand.turncounts

For each counted intersection in the study area we take the most recent count in
the base window (weekdays, 2023 onward, excluding July, August and December), sum
cars and trucks by hour for 06:00-10:00, and match every approach leg (N/E/S/W on
Toronto's street grid) and movement (left/through/right) to a SUMO edge relation.
Buses are excluded: TTC buses run fixed routes and are not part of the demand that
responds to a charge.

Counts come from different days at different sites. Treating them together as a
"typical base-window weekday" is an ASSUMPTION; the validation step reports how
well a single simulated day reproduces them.

Outputs (sim/demand/):
  turns_calibration.xml   routeSampler targets (~80% of sites)
  turns_holdout.xml       held-out sites for validation (~20%, fixed seed)
  edges_<split>.xml       approach-leg totals where turns could not be mapped (divided roads)
  turn_mapping.csv        every leg/movement with its SUMO edges or the reason it failed
"""

import math
import random
import sys
from xml.sax.saxutils import quoteattr

import duckdb
import pandas as pd
import sumo

sys.path.append(str(sumo.SUMO_HOME) + "/tools")
import sumolib  # noqa: E402

from cordon import DATA, ROOT  # noqa: E402

BBOX = (-79.432, 43.620, -79.327, 43.690)
BASE_FROM = "2023-01-01"
HOURS = [6, 7, 8, 9]
GRID_ROTATION_DEG = 17.0  # Toronto's street grid "north" is ~17 deg west of true north
NODE_SNAP_M = 40
CLUSTER_M = 60  # divided roads become several SUMO junctions; search this far for a missing leg
HOLDOUT_SHARE = 0.2
SEED = 42
MOVE_DIRS = {"t": {"s"}, "l": {"l", "L"}, "r": {"r", "R"}}
NET = ROOT / "sim" / "net" / "study_area.net.xml.gz"
OUT = ROOT / "sim" / "demand"


def load_counts():
    con = duckdb.connect()
    legs, moves = "nesw", "tlr"
    selects = ",\n".join(
        f"sum(coalesce({l}_appr_cars_{m},0) + coalesce({l}_appr_truck_{m},0)) as {l}_{m}"
        for l in legs for m in moves)
    df = con.execute(f"""
        with r as (
          select * from read_csv_auto('{DATA}/raw/tor_tmc/*/tmc_raw_data_2020_2029.csv')
          where longitude between {BBOX[0]} and {BBOX[2]} and latitude between {BBOX[1]} and {BBOX[3]}
            and count_date >= '{BASE_FROM}' and dayofweek(count_date) between 1 and 5
            and month(count_date) not in (7, 8, 12)
        ),
        latest as (
          select centreline_id, arg_max(count_id, count_date) count_id from r group by 1
        )
        select r.centreline_id site_id, r.count_id, any_value(r.count_date) count_date,
               any_value(r.location_name) location_name, any_value(r.longitude) lon,
               any_value(r.latitude) lat, hour(r.start_time) hr, count(*) n_slots,
               {selects}
        from r join latest using (centreline_id, count_id)
        where hour(r.start_time) in ({",".join(map(str, HOURS))})
        group by r.centreline_id, r.count_id, hour(r.start_time)
    """).df()
    full = df[df.n_slots == 4]  # keep hours with all four 15-minute slots
    long = full.melt(id_vars=["site_id", "count_id", "count_date", "location_name", "lon", "lat", "hr"],
                     value_vars=[f"{l}_{m}" for l in legs for m in moves], var_name="lm", value_name="veh")
    long[["leg", "move"]] = long.lm.str.split("_", expand=True)
    return long.drop(columns="lm"), len(df), len(full)


def grid_heading(edge):
    shape = edge.getShape()
    (x1, y1), (x2, y2) = shape[-2], shape[-1]
    true_heading = math.degrees(math.atan2(x2 - x1, y2 - y1)) % 360
    return (true_heading + GRID_ROTATION_DEG) % 360


def leg_of(heading):
    """Approach leg = the side vehicles come FROM (heading south => north leg)."""
    if 135 <= heading < 225:
        return "n"
    if 315 <= heading or heading < 45:
        return "s"
    if 225 <= heading < 315:
        return "e"
    return "w"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    net = sumolib.net.readNet(str(NET), withInternal=False)
    counts, n_hours, n_full = load_counts()
    sites = counts.drop_duplicates("site_id")[["site_id", "lon", "lat", "location_name", "count_date"]]

    nodes = [n for n in net.getNodes() if len(n.getIncoming()) >= 2]
    rows = []
    edge_map = {}  # (site, leg, move) -> (from_edge, to_edge)
    leg_edge = {}  # (site, leg) -> approach edge, for legs mapped only as a total
    for s in sites.itertuples():
        x, y = net.convertLonLat2XY(s.lon, s.lat)
        best = min(nodes, key=lambda n: (n.getCoord()[0] - x) ** 2 + (n.getCoord()[1] - y) ** 2)
        d = math.dist(best.getCoord(), (x, y))
        if d > NODE_SNAP_M:
            rows.append({"site_id": s.site_id, "status": f"no SUMO junction within {NODE_SNAP_M} m ({d:.0f} m)"})
            continue
        by_leg = {}
        for e in best.getIncoming():
            if e.getFunction() == "internal" or not e.allows("passenger"):
                continue
            by_leg.setdefault(leg_of(grid_heading(e)), []).append(e)
        cluster = [n for n in nodes if math.dist(n.getCoord(), (x, y)) <= CLUSTER_M]
        cluster_ids = {n.getID() for n in cluster}
        for leg in "nesw":
            cands = by_leg.get(leg, [])
            if not cands:
                # Fallback: an approach on this leg into another junction of the same
                # divided-road cluster, coming from outside the cluster.
                alt = [e for n in cluster for e in n.getIncoming()
                       if e.getFromNode().getID() not in cluster_ids and e.allows("passenger")
                       and leg_of(grid_heading(e)) == leg]
                if alt:
                    e = max(alt, key=lambda e: (e.getLaneNumber(), e.getPriority()))
                    leg_edge[(s.site_id, leg)] = e.getID()
                    rows.append({"site_id": s.site_id, "leg": leg, "from_edge": e.getID(),
                                 "status": "leg total only (divided-road cluster)"})
                else:
                    rows.append({"site_id": s.site_id, "leg": leg, "status": "no incoming edge on this leg"})
                continue
            frm = max(cands, key=lambda e: (e.getLaneNumber(), e.getPriority()))
            for move, dirs in MOVE_DIRS.items():
                outs = []
                for to_edge, conns in frm.getOutgoing().items():
                    if any(c.getDirection() in dirs for c in conns):
                        outs.append(to_edge)
                if not outs:
                    rows.append({"site_id": s.site_id, "leg": leg, "move": move, "from_edge": frm.getID(),
                                 "status": "no connection with this turn direction"})
                    continue
                to = max(outs, key=lambda e: (e.getLaneNumber(), e.getPriority()))
                edge_map[(s.site_id, leg, move)] = (frm.getID(), to.getID())
                rows.append({"site_id": s.site_id, "leg": leg, "move": move, "from_edge": frm.getID(),
                             "to_edge": to.getID(), "node": best.getID(), "snap_m": round(d, 1), "status": "ok"})
    mapping = pd.DataFrame(rows).merge(sites, on="site_id", how="left")
    mapping.to_csv(OUT / "turn_mapping.csv", index=False)

    counts["key"] = list(zip(counts.site_id, counts.leg, counts["move"]))
    mapped = counts[counts.key.isin(edge_map)].copy()
    # Zero-volume movements on legs that physically exist are informative targets;
    # keep them. Movements whose leg has no SUMO edge were dropped above.
    mapped[["from_edge", "to_edge"]] = pd.DataFrame(mapped.key.map(edge_map).tolist(), index=mapped.index)
    # Two TMC movements can map to the same SUMO relation (e.g. a slip lane); sum them.
    rel = mapped.groupby(["site_id", "hr", "from_edge", "to_edge"], as_index=False).veh.sum()

    site_ids = sorted(set(rel.site_id) | {k[0] for k in leg_edge})
    random.Random(SEED).shuffle(site_ids)
    n_hold = round(len(site_ids) * HOLDOUT_SHARE)
    holdout = set(site_ids[:n_hold])
    rel["split"] = rel.site_id.map(lambda s: "holdout" if s in holdout else "calibration")
    rel.to_csv(OUT / "turn_targets.csv", index=False)

    counts["leg_key"] = list(zip(counts.site_id, counts.leg))
    legs = counts[counts.leg_key.isin(leg_edge)].groupby(["site_id", "leg", "hr"], as_index=False).veh.sum()
    legs["edge"] = [leg_edge[(a, b)] for a, b in zip(legs.site_id, legs.leg)]
    legs["split"] = legs.site_id.map(lambda s: "holdout" if s in holdout else "calibration")
    legs = legs.groupby(["split", "hr", "edge", "site_id"], as_index=False).veh.sum()
    legs.to_csv(OUT / "edge_targets.csv", index=False)
    for split in ("calibration", "holdout"):
        part = legs[legs.split == split].groupby(["hr", "edge"], as_index=False).veh.max()
        with open(OUT / f"edges_{split}.xml", "w") as f:
            f.write('<data>\n')
            for hr in HOURS:
                f.write(f'  <interval id="h{hr:02d}" begin="{hr * 3600}" end="{(hr + 1) * 3600}">\n')
                for r in part[part.hr == hr].itertuples():
                    f.write(f'    <edge id={quoteattr(r.edge)} entered="{int(r.veh)}"/>\n')
                f.write('  </interval>\n')
            f.write('</data>\n')

    for split in ("calibration", "holdout"):
        part = rel[rel.split == split]
        with open(OUT / f"turns_{split}.xml", "w") as f:
            f.write('<data>\n')
            for hr in HOURS:
                f.write(f'  <interval id="h{hr:02d}" begin="{hr * 3600}" end="{(hr + 1) * 3600}">\n')
                for r in part[part.hr == hr].itertuples():
                    f.write(f'    <edgeRelation from={quoteattr(r.from_edge)} to={quoteattr(r.to_edge)} count="{int(r.veh)}"/>\n')
                f.write('  </interval>\n')
            f.write('</data>\n')

    ok = mapping[mapping.status == "ok"]
    print(f"site-hours read: {n_hours}, complete hours kept: {n_full}")
    print(f"sites: {len(sites)} | snapped: {mapping[~mapping.status.str.startswith('no SUMO', na=False)].site_id.nunique()}"
          f" | with >=1 mapped movement: {ok.site_id.nunique()}")
    print(mapping.status.str.replace(r"\(.*\)", "", regex=True).value_counts().to_string())
    print(f"calibration sites: {len(site_ids) - n_hold}, holdout sites: {n_hold}")
    print(f"AM (06-10) vehicles in targets: calibration {int(rel[rel.split=='calibration'].veh.sum()):,}, "
          f"holdout {int(rel[rel.split=='holdout'].veh.sum()):,}")


if __name__ == "__main__":
    main()
