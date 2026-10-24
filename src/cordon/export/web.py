"""Export model outputs to small web layers with labels (component 5).

Usage: uv run python -m cordon.export.web

Writes to web/public/data/:
  cordons.geojson     candidate boundaries C1-C3 (ASSUMPTION)
  crossings.geojson   boundary crossings with count coverage (OBSERVED coverage)
  counts.geojson      counted intersections used for calibration/validation (OBSERVED)
  edges.geojson       modelled AM volumes and speeds per road, S0-S3 (SIMULATED, static assignment)
  metrics.json        scenario metrics, validation (GEH), diversion and approach-side burden
"""

import json
import math
import sys
from collections import defaultdict

import geopandas as gpd
import pandas as pd
import sumo
import yaml
from shapely.geometry import LineString
from shapely.ops import transform

sys.path.append(str(sumo.SUMO_HOME) + "/tools")
import sumolib  # noqa: E402

from cordon import CONFIG, DATA, ROOT  # noqa: E402

NET = ROOT / "sim" / "net" / "study_area.net.xml.gz"
OUT = ROOT / "sim" / "out"
WEB = ROOT / "web" / "public" / "data"
DEMAND = ROOT / "sim" / "demand"
LOCAL_TYPES = {"highway.residential", "highway.unclassified", "highway.living_street", "highway.tertiary"}
BOUNDARY_BAND_M = 800
GRID_ROTATION_DEG = 17.0


def r5(x):
    return round(x, 5)


def geh(m, c):
    return math.sqrt(2 * (m - c) ** 2 / (m + c)) if m + c > 0 else 0.0


def link_stats(lk, length):
    """scenario -> edge -> (vehicles 06-10, flow-weighted mean speed km/h) from the assignment."""
    out = {}
    for sc, g in lk.groupby("scenario"):
        agg = g.assign(vkt=g.flow * g.edge.map(length) / 1000, vht=g.flow * g.time_min / 60).groupby("edge").agg(
            veh=("flow", "sum"), vkt=("vkt", "sum"), vht=("vht", "sum"), tmin=("time_min", "max"))
        spd = (agg.vkt / agg.vht).where(agg.vht > 0, agg.index.map(length) / 1000 / (agg.tmin / 60))
        out[sc] = {e: (v, sp) for e, v, sp in zip(agg.index, agg.veh, spd)}
    return out


def validation(lk):
    """Assigned S0 flow on each counted approach vs the City count, by hour, calibration vs held-out sites."""
    s0 = lk[lk.scenario == "S0"].set_index(["edge", "hour"]).flow
    tt = pd.read_csv(DEMAND / "turn_targets.csv")
    appr = tt.groupby(["split", "site_id", "hr", "from_edge"], as_index=False).veh.sum().rename(columns={"from_edge": "edge"})
    et = pd.read_csv(DEMAND / "edge_targets.csv")
    appr = pd.concat([appr, et[["split", "site_id", "hr", "edge", "veh"]]], ignore_index=True)
    appr["sim"] = [float(s0.get((e, h), 0.0)) for e, h in zip(appr.edge, appr.hr)]
    out = {}
    for split, g in appr.groupby("split"):
        g = g.assign(geh=[geh(m, c) for m, c in zip(g.sim, g.veh)])
        site = g.groupby(["site_id", "hr"]).agg(sim=("sim", "sum"), obs=("veh", "sum")).reset_index()
        site["geh"] = [geh(m, c) for m, c in zip(site.sim, site.obs)]
        out[split] = {
            "approach_hours": len(g),
            "share_geh_lt5_approaches": round((g.geh < 5).mean(), 3),
            "share_geh_lt10_approaches": round((g.geh < 10).mean(), 3),
            "intersection_hours": len(site),
            "share_geh_lt5_intersection_hours": round((site.geh < 5).mean(), 3),
            "share_geh_lt10_intersection_hours": round((site.geh < 10).mean(), 3),
            "total_observed": int(g.veh.sum()), "total_simulated": int(g.sim.sum()),
            "r_approaches": round(float(g[["sim", "veh"]].corr().iloc[0, 1]), 3),
        }
        if split == "holdout":
            site.to_csv(DEMAND / "holdout_site_fit.csv", index=False)
    out["criterion"] = ("GEH < 5 for >= 85% of counts is a common calibration target for assignment models "
                        "(UK TAG/DMRB); reported for transparency, not as a pass/fail claim. Compared at "
                        "approach level (all movements entering an intersection from one leg).")
    return out


def approach_side(pt_xy, centre_xy):
    dx, dy = pt_xy[0] - centre_xy[0], pt_xy[1] - centre_xy[1]
    bearing = (math.degrees(math.atan2(dx, dy)) + GRID_ROTATION_DEG) % 360
    return ["north", "east", "south", "west"][int(((bearing + 45) % 360) // 90)]


def main():
    WEB.mkdir(parents=True, exist_ok=True)
    scen_all = yaml.safe_load((CONFIG / "scenarios.yaml").read_text())
    cordon_id = scen_all["simulation"]["cordon_for_area_charge"]
    lk = pd.read_parquet(OUT / "assign" / "links.parquet")
    names = [s for s in scen_all["scenarios"] if s in set(lk.scenario)]
    net = sumolib.net.readNet(str(NET))

    # Cordons
    feats = []
    for cid in ("C1", "C2", "C3"):
        feats += json.loads((CONFIG / "cordons" / f"{cid}.geojson").read_text())["features"]
    (WEB / "cordons.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}))

    # Crossings with coverage
    cov = pd.read_parquet(DATA / "processed" / "crossing_coverage.parquet")
    cov["geometry"] = gpd.GeoSeries.from_wkt(cov.crossing_wkt)
    cg = gpd.GeoDataFrame(cov, geometry="geometry", crs="EPSG:4326")
    keep = ["cordon_id", "linear_name_full", "feature_code_desc", "jurisdiction", "coverage",
            "last_count_date", "nearest_recent_site", "geometry"]
    cg = cg[keep].assign(last_count_date=cg.last_count_date.astype(str), label="OBSERVED (coverage)")
    (WEB / "crossings.geojson").write_text(cg.to_json(drop_id=True))

    # Counted intersections
    tt = pd.read_csv(DEMAND / "turn_targets.csv")
    tm = pd.read_csv(DEMAND / "turn_mapping.csv").drop_duplicates("site_id")
    sites = tt.groupby(["site_id", "split"], as_index=False).veh.sum().merge(
        tm[["site_id", "location_name", "lon", "lat", "count_date"]], on="site_id")
    sg = gpd.GeoDataFrame(sites, geometry=gpd.points_from_xy(sites.lon, sites.lat), crs="EPSG:4326")
    sg = sg.drop(columns=["lon", "lat"]).rename(columns={"veh": "am_vehicles_counted_movements"})
    sg["label"] = "OBSERVED (City TMC, most recent weekday count since 2023)"
    (WEB / "counts.geojson").write_text(sg.to_json(drop_id=True))

    # Edges with simulated volumes/speeds per scenario
    zone = gpd.read_file(CONFIG / "cordons" / f"{cordon_id}.geojson").geometry.iloc[0]
    zone_xy = transform(lambda x, y, z=None: net.convertLonLat2XY(x, y), zone)
    band = zone_xy.buffer(BOUNDARY_BAND_M).difference(zone_xy)
    stats = link_stats(lk, {e.getID(): e.getLength() for e in net.getEdges()})
    used = set().union(*[set(v) for v in stats.values()]) if stats else set()
    features, edge_meta = [], {}
    for eid in used:
        e = net.getEdge(eid)
        shape = e.getShape()
        line = LineString(shape)
        mid = line.interpolate(0.5, normalized=True)
        in_zone = zone_xy.contains(mid)
        boundary_local = (e.getType() in LOCAL_TYPES) and band.contains(mid)
        street = not e.getType().startswith("highway.motorway")
        edge_meta[eid] = (in_zone, boundary_local, e.getLength(), street)
        props = {"id": eid, "name": e.getName() or "", "type": e.getType().replace("highway.", ""),
                 "zone": in_zone, "bl": boundary_local}
        for s in names:
            vol, spd = stats[s].get(eid, (0.0, None))
            props[f"v_{s}"] = round(vol)
            props[f"s_{s}"] = round(spd, 1) if spd is not None else None
        coords = [[r5(c) for c in net.convertXY2LonLat(x, y)] for x, y in shape]
        features.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": coords},
                         "properties": props})
    (WEB / "edges.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": features}))

    # Metrics per scenario: zone and boundary-street effects, approach-side burden
    summary = json.loads((OUT / "summary.json").read_text())
    charged = json.loads((OUT / "charged_edges.json").read_text())
    centre = zone_xy.centroid.coords[0]
    sides = {}
    for eid in charged["cordon_inbound"]:
        e = net.getEdge(eid)
        sides[eid] = approach_side(e.getToNode().getCoord(), centre)
    for s in names:
        st = stats[s]
        zone_vkt = sum(v * edge_meta[k][2] / 1000 for k, (v, _) in st.items() if edge_meta[k][0])
        bl_vkt = sum(v * edge_meta[k][2] / 1000 for k, (v, _) in st.items() if edge_meta[k][1])
        # Zone street speed with fixed (S0) vehicle-km weights: the time to drive the baseline's
        # zone street-km at this scenario's speeds. Fixed weights avoid a mix effect (less
        # expressway traffic would otherwise lower the average even if every street got faster).
        w0 = {k: v * edge_meta[k][2] / 1000 for k, (v, sp) in stats["S0"].items()
              if edge_meta[k][0] and edge_meta[k][3] and sp and v > 0}
        hrs = sum(w / st[k][1] for k, w in w0.items() if st.get(k, (0, None))[1])
        zone_speed = sum(w0.values()) / hrs if hrs else None
        side_counts = defaultdict(float)
        for eid, side in sides.items():
            side_counts[side] += st.get(eid, (0, None))[0]
        summary[s].update({"zone_vkt_am": round(zone_vkt), "zone_street_speed_kmh": round(zone_speed, 1),
                           "boundary_local_street_vkt_am": round(bl_vkt),
                           "cordon_inbound_by_side_am": {k: round(v) for k, v in side_counts.items()}})
    metrics = {"scenarios": summary, "validation": validation(lk),
               "labels": {"scenario_metrics": "SIMULATED (static equilibrium assignment)", "validation": "SIMULATED vs OBSERVED (held-out City counts)"},
               "cordon_id": cordon_id}
    (WEB / "metrics.json").write_text(json.dumps(metrics, indent=1))

    print(json.dumps(metrics["validation"], indent=1))


if __name__ == "__main__":
    main()
