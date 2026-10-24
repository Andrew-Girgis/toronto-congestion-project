"""Build candidate charging boundaries and find every road that crosses them.

Usage: uv run python -m cordon.geometry.cordons

Inputs:  config/cordons/candidates.yaml, Toronto Centreline snapshot (data/raw)
Outputs: config/cordons/<id>.geojson          boundary polygon (EPSG:4326)
         data/processed/crossings.parquet     one row per road segment crossing a boundary
"""

import json

import geopandas as gpd
import numpy as np
import pandas as pd
import yaml
from shapely.geometry import LineString, Point, Polygon, mapping
from shapely.ops import nearest_points, unary_union

from cordon import CONFIG, DATA

CRS_M = "EPSG:2952"  # NAD83(CSRS) / MTM zone 10, metres; the City's own projection
BBOX = (-79.50, 43.60, -79.28, 43.72)
DRIVABLE = {
    "Expressway", "Expressway Ramp", "Major Arterial", "Major Arterial Ramp",
    "Minor Arterial", "Minor Arterial Ramp", "Collector", "Collector Ramp",
    "Local", "Access Road", "Other Ramp",
}
MEET_TOLERANCE_M = 400
FOLLOW_TOLERANCE_M = 600


def load_centreline():
    path = sorted((DATA / "raw" / "tor_centreline").glob("*/*.gpkg"))[-1]
    gdf = gpd.read_file(path, bbox=BBOX).to_crs(CRS_M)
    gdf.columns = [c.lower() if c != "geometry" else c for c in gdf.columns]
    return gdf, path


def feature(gdf, names):
    names = [names] if isinstance(names, str) else names
    sel = gdf[gdf["linear_name_full"].isin(names)]
    if sel.empty:
        raise KeyError(f"no Centreline feature named {names}")
    return unary_union(sel.geometry.values)


def meet(gdf, a, b):
    """Point where features a and b meet, or their closest approach within tolerance."""
    ga, gb = feature(gdf, a), feature(gdf, b)
    inter = ga.intersection(gb)
    if not inter.is_empty:
        return inter.centroid, 0.0
    pa, pb = nearest_points(ga, gb)
    d = pa.distance(pb)
    if d > MEET_TOLERANCE_M:
        raise ValueError(f"{a} and {b} are {d:.0f} m apart; no meeting point")
    return Point((pa.x + pb.x) / 2, (pa.y + pb.y) / 2), d


def follow(gdf, names, v1, v2):
    """Coordinates of a feature between two vertices, ordered from v1 to v2.

    Takes every vertex of the named feature lying between v1 and v2 (by projection
    onto the v1->v2 axis, within a corridor), sorted along that axis, then
    simplified. Accurate for straight streets and the mostly monotone Don River
    and CP rail corridor, which is all the candidates need.
    """
    geom = feature(gdf, names)
    a, b = np.array(v1.coords[0]), np.array(v2.coords[0])
    axis = b - a
    length = np.linalg.norm(axis)
    unit = axis / length
    normal = np.array([-unit[1], unit[0]])
    lines = getattr(geom, "geoms", [geom])
    pts = np.array([c for ln in lines for c in ln.coords])
    t = (pts - a) @ unit
    off = np.abs((pts - a) @ normal)
    keep = pts[(t > 0) & (t < length) & (off < FOLLOW_TOLERANCE_M)]
    keep = keep[np.argsort((keep - a) @ unit)]
    line = LineString([a, *keep, b]).simplify(25)
    return list(line.coords)


def build_ring(gdf, spec):
    vertices, notes = [], []
    for step in spec["ring"]:
        v = step["vertex"]
        if "point" in v:
            p = gpd.GeoSeries([Point(v["point"])], crs="EPSG:4326").to_crs(CRS_M).iloc[0]
            d = 0.0
        else:
            p, d = meet(gdf, *v["meet"])
        if d:
            notes.append(f"{' / '.join(v['meet'])}: nearest approach {d:.0f} m")
        vertices.append(p)
    coords = []
    for i, step in enumerate(spec["ring"]):
        v1, v2 = vertices[i], vertices[(i + 1) % len(vertices)]
        edge = step["edge"]
        if edge.get("straight"):
            coords += [v1.coords[0]]
        else:
            coords += follow(gdf, edge["follow"], v1, v2)[:-1]
    poly = Polygon(coords).buffer(0)
    return poly, notes


def node_degree(roads):
    ids = pd.concat([roads["from_intersection_id"], roads["to_intersection_id"]])
    return ids.value_counts()


def crossings_for(gdf, cid, zone, exclude):
    ring = zone.exterior
    roads = gdf[gdf["feature_code_desc"].isin(sorted(DRIVABLE | {"Laneway"}))]
    degree = node_degree(roads)
    hit = roads[roads.intersects(ring) & ~roads["linear_name_full"].isin(list(exclude))].copy()
    hit["cordon_id"] = cid
    pts = hit.geometry.intersection(ring)
    hit["crossing_point"] = pts.apply(lambda g: g.centroid if not g.is_empty else None)
    hit["n_intersections"] = pts.apply(lambda g: len(getattr(g, "geoms", [g])))
    # Which end of the segment lies outside the zone: the intersection an inbound
    # vehicle comes from, used to match intersection (TMC) counts.
    def outside_node(row):
        parts = getattr(row.geometry, "geoms", [row.geometry])
        start_in = zone.contains(Point(parts[0].coords[0]))
        end_in = zone.contains(Point(parts[-1].coords[-1]))
        if start_in == end_in:
            return pd.NA
        return row["to_intersection_id"] if start_in else row["from_intersection_id"]
    hit["outside_intersection_id"] = hit.apply(outside_node, axis=1)
    # A street that dead-ends against a railway or river is not an entry point:
    # its outside node must connect to at least one other road segment.
    deg = hit["outside_intersection_id"].map(degree).fillna(0)
    return hit[(deg >= 2) | hit["outside_intersection_id"].isna()]


def main():
    gdf, src = load_centreline()
    cfg = yaml.safe_load((CONFIG / "cordons" / "candidates.yaml").read_text())
    offset = cfg["inward_offset_m"]
    frames, summary = [], []
    for cid, spec in cfg["candidates"].items():
        poly, notes = build_ring(gdf, spec)
        zone = poly.buffer(-offset)
        if zone.geom_type == "MultiPolygon":
            zone = max(zone.geoms, key=lambda g: g.area)
        hits = crossings_for(gdf, cid, zone, cfg.get("exclude_roads", {}))
        frames.append(hits)
        zone_ll = gpd.GeoSeries([zone], crs=CRS_M).to_crs("EPSG:4326").iloc[0]
        fc = {"type": "FeatureCollection", "features": [{
            "type": "Feature", "geometry": mapping(zone_ll),
            "properties": {"cordon_id": cid, "name": spec["name"],
                           "rationale": " ".join(spec["rationale"].split()),
                           "area_km2": round(zone.area / 1e6, 2),
                           "label": "ASSUMPTION (candidate boundary)",
                           "build_notes": notes, "centreline_snapshot": str(src.relative_to(DATA.parent))}}]}
        (CONFIG / "cordons" / f"{cid}.geojson").write_text(json.dumps(fc))
        drv = hits[hits["feature_code_desc"].isin(sorted(DRIVABLE))]
        summary.append({"cordon": cid, "name": spec["name"], "area_km2": round(zone.area / 1e6, 2),
                        "drivable_crossings": len(drv),
                        "arterial_or_expressway": int(drv["feature_code_desc"].str.contains("Arterial|Expressway").sum()),
                        "laneway_crossings": int((hits["feature_code_desc"] == "Laneway").sum()),
                        "notes": "; ".join(notes)})
    out = pd.concat(frames)
    out["crossing_point"] = gpd.GeoSeries(out["crossing_point"], crs=CRS_M).to_crs("EPSG:4326").to_wkt()
    out = out.to_crs("EPSG:4326")
    (DATA / "processed").mkdir(parents=True, exist_ok=True)
    out.to_parquet(DATA / "processed" / "crossings.parquet")
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
