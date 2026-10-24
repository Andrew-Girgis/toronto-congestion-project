"""Export model outputs to small web layers with labels (component 5).

Usage: uv run python -m cordon.export.web

Writes to web/public/data/:
  cordons.geojson     candidate boundaries C1-C3 (ASSUMPTION)
  crossings.geojson   boundary crossings with count coverage (OBSERVED coverage)
  counts.geojson      counted intersections used for calibration/validation (OBSERVED)
  edges.geojson       simulated AM volumes and speeds per road, S0-S3 (SIMULATED)
  trips_<S>.json      sampled vehicle traces for the animation (SIMULATED)
  metrics.json        scenario metrics, validation (GEH), diversion and approach-side burden
"""

import json
import math
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

import geopandas as gpd
import pandas as pd
import sumo
import yaml
from shapely.geometry import LineString, Point
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
TRIP_WINDOW = (7 * 3600, 9 * 3600)  # animation window, 07:00-09:00


def r5(x):
    return round(x, 5)


def geh(m, c):
    return math.sqrt(2 * (m - c) ** 2 / (m + c)) if m + c > 0 else 0.0


def edge_stats(path):
    """edge -> (vehicles entered 06-10, sampled-seconds-weighted mean speed km/h)."""
    veh, ss, spd = defaultdict(float), defaultdict(float), defaultdict(float)
    for interval in ET.parse(path).getroot().findall("interval"):
        for e in interval.findall("edge"):
            eid = e.get("id")
            veh[eid] += float(e.get("entered") or 0)
            s = float(e.get("sampledSeconds") or 0)
            if s and e.get("speed"):
                ss[eid] += s
                spd[eid] += s * float(e.get("speed"))
    return {eid: (veh[eid], (spd[eid] / ss[eid] * 3.6) if ss[eid] else None) for eid in veh}


def simulated_turns(vehroutes):
    """(from, to, hour) -> vehicles, from exit times in the simulated routes."""
    turns = defaultdict(int)
    for _, el in ET.iterparse(vehroutes):
        if el.tag == "vehicle":
            r = el.find("route")
            edges, exits = r.get("edges").split(), r.get("exitTimes", "").split()
            for i in range(min(len(edges) - 1, len(exits))):
                turns[(edges[i], edges[i + 1], int(float(exits[i]) // 3600))] += 1
            el.clear()
    return turns


def validation():
    sim = simulated_turns(OUT / "S0" / "vehroutes.xml")
    tt = pd.read_csv(DEMAND / "turn_targets.csv")
    tt["sim"] = [sim.get((f, t, h), 0) for f, t, h in zip(tt.from_edge, tt.to_edge, tt.hr)]
    out = {}
    for split, g in tt.groupby("split"):
        g = g.assign(geh=[geh(m, c) for m, c in zip(g.sim, g.veh)])
        site = g.groupby(["site_id", "hr"]).agg(sim=("sim", "sum"), obs=("veh", "sum")).reset_index()
        site["geh"] = [geh(m, c) for m, c in zip(site.sim, site.obs)]
        big = g[g.veh >= 100]
        corr = g[["sim", "veh"]].corr().iloc[0, 1]
        out[split] = {
            "movement_hours": len(g),
            "share_geh_lt5_movements": round((g.geh < 5).mean(), 3),
            "share_geh_lt5_movements_ge100veh": round((big.geh < 5).mean(), 3) if len(big) else None,
            "intersection_hours": len(site),
            "share_geh_lt5_intersection_hours": round((site.geh < 5).mean(), 3),
            "share_geh_lt10_intersection_hours": round((site.geh < 10).mean(), 3),
            "total_observed": int(g.veh.sum()), "total_simulated": int(g.sim.sum()),
            "r_movements": round(float(corr), 3),
        }
        if split == "holdout":
            site.to_csv(DEMAND / "holdout_site_fit.csv", index=False)
    out["criterion"] = ("GEH < 5 for >= 85% of counts is the common UK DMRB/FHWA calibration target "
                        "for assignment models; reported here for transparency, not as a pass/fail claim.")
    return out


def approach_side(pt_xy, centre_xy):
    dx, dy = pt_xy[0] - centre_xy[0], pt_xy[1] - centre_xy[1]
    bearing = (math.degrees(math.atan2(dx, dy)) + GRID_ROTATION_DEG) % 360
    return ["north", "east", "south", "west"][int(((bearing + 45) % 360) // 90)]


def main():
    WEB.mkdir(parents=True, exist_ok=True)
    scen_all = yaml.safe_load((CONFIG / "scenarios.yaml").read_text())
    cordon_id = scen_all["simulation"]["cordon_for_area_charge"]
    names = [s for s in scen_all["scenarios"] if (OUT / s / "edgedata.xml").exists()]
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
    stats = {s: edge_stats(OUT / s / "edgedata.xml") for s in names}
    used = set().union(*[set(v) for v in stats.values()]) if stats else set()
    features, edge_meta = [], {}
    for eid in used:
        e = net.getEdge(eid)
        shape = e.getShape()
        line = LineString(shape)
        mid = line.interpolate(0.5, normalized=True)
        in_zone = zone_xy.contains(mid)
        boundary_local = (e.getType() in LOCAL_TYPES) and band.contains(mid)
        edge_meta[eid] = (in_zone, boundary_local, e.getLength())
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
        bl_veh = sum(v for k, (v, _) in st.items() if edge_meta[k][1])
        zs = [(v * edge_meta[k][2], sp) for k, (v, sp) in st.items() if edge_meta[k][0] and sp]
        zone_speed = sum(w * sp for w, sp in zs) / max(sum(w for w, _ in zs), 1e-9)
        side_counts = defaultdict(float)
        for eid, side in sides.items():
            side_counts[side] += st.get(eid, (0, None))[0]
        summary[s].update({"zone_vkt_am": round(zone_vkt), "zone_mean_speed_kmh": round(zone_speed, 1),
                           "boundary_local_street_vehicles_am": round(bl_veh),
                           "cordon_inbound_by_side_am": {k: round(v) for k, v in side_counts.items()}})
    metrics = {"scenarios": summary, "validation": validation(),
               "labels": {"scenario_metrics": "SIMULATED", "validation": "SIMULATED vs OBSERVED (held-out City counts)"},
               "cordon_id": cordon_id}
    (WEB / "metrics.json").write_text(json.dumps(metrics, indent=1))

    # Animation traces (sampled vehicles, 07:00-09:00)
    for s in names:
        paths = defaultdict(list)
        for _, el in ET.iterparse(OUT / s / "fcd.xml"):
            if el.tag == "timestep":
                t = float(el.get("time"))
                if TRIP_WINDOW[0] <= t <= TRIP_WINDOW[1]:
                    for v in el.findall("vehicle"):
                        paths[v.get("id")].append((r5(float(v.get("x"))), r5(float(v.get("y"))), int(t - TRIP_WINDOW[0])))
                el.clear()
        trips = [{"p": [[x, y] for x, y, _ in pts], "t": [t for _, _, t in pts]}
                 for pts in paths.values() if len(pts) > 2]
        (WEB / f"trips_{s}.json").write_text(json.dumps(trips, separators=(",", ":")))
        print(f"{s}: {len(trips)} traced vehicles")
    print(json.dumps(metrics["validation"], indent=1))


if __name__ == "__main__":
    main()
