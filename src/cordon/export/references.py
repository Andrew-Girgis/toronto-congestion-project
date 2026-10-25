"""Numbered reference list for the deck's sources slides and per-slide source lines (component 5).

Usage: uv run python -m cordon.export.references

Reads research/sources.csv (one row per claim; rows sharing a URL are one document)
and data/manifest.csv (datasets), and writes web/public/data/references.json:
{repo, groups: [{name, items: [{n, ids, author, title, published, url, where, status}]}],
by_id: {source_id: n}}. Register rows with no URL are claims we checked, not sources,
so they are left out. Documents whose every row is UNVERIFIED go in their own group.
"""

import csv
import json

from cordon import ROOT

OUT = ROOT / "web" / "public" / "data" / "references.json"
REPO = "https://github.com/Andrew-Girgis/toronto-congestion-project"

GROUPS = [
    ("toronto_today", "Toronto today"),
    ("toronto_data", "Toronto data"),
    ("toronto_policy", "Toronto and Ontario: law, policy, costs and growth"),
    ("nyc", "New York"),
    ("london", "London"),
    ("stockholm", "Stockholm"),
    ("singapore", "Singapore"),
    ("methods", "Methods, prices and exchange rates"),
    ("software", "Software and basemap"),
    ("images", "Images (user-supplied; licences unverified)"),
    ("unverified", "Consulted, not verified against the primary source"),
]

# Register documents filed by their first row's prefix, with the exceptions below
PREFIX = {"A": "toronto_today", "B-NYC": "nyc", "N": "nyc", "B-LON": "london", "B-STO": "stockholm",
          "B-ALS": "singapore", "B-ERP": "singapore", "T": "toronto_policy", "M": "toronto_policy",
          "P": "toronto_policy", "D": "toronto_policy", "IMG": "images"}
FILE_AS = {"B-LON-012": "stockholm", "D-005": "stockholm", "D-006": "stockholm", "D-023": "singapore",
           "D-024": "singapore", "D-001": "methods", "D-002": "methods", "D-003": "methods",
           "D-004": "methods", "D-028": "methods"}

# Datasets from data/manifest.csv; the rest of the manifest is documents already in the register
DATASETS = {
    "tor_tmc": "Traffic Volumes at Intersections for All Modes (turning movement counts)",
    "tor_svc": "Traffic Volumes: Midblock Vehicle Speed, Volume and Classification Counts",
    "tor_centreline": "Toronto Centreline (TCL)",
    "tor_neighbourhoods": "Neighbourhoods (158)",
    "tor_neighbourhood_profiles": "Neighbourhood Profiles (2021 Census)",
    "tor_ptc": "Private Transportation Companies: Summary and Trip Data",
    "tor_bike_cordon": "Bicycle and Micromobility Cordon Count",
}

SOFTWARE = [
    ("sw-sumo", "Eclipse Foundation", "SUMO: Simulation of Urban MObility (routeSampler)", "https://eclipse.dev/sumo/"),
    ("sw-aequilibrae", "AequilibraE developers", "AequilibraE: traffic assignment", "https://www.aequilibrae.com/"),
    ("sw-duckdb", "DuckDB Foundation", "DuckDB with the spatial extension", "https://duckdb.org/"),
    ("sw-maplibre", "MapLibre", "MapLibre GL JS", "https://maplibre.org/"),
    ("sw-openfreemap", "OpenFreeMap", "OpenFreeMap Positron basemap (© OpenMapTiles)", "https://openfreemap.org/"),
    ("sw-astro", "Astro", "Astro (this deck and site)", "https://astro.build/"),
]


def group_of(sid):
    if sid in FILE_AS:
        return FILE_AS[sid]
    head = sid.rsplit("-", 1)[0]
    return PREFIX.get(head) or PREFIX.get(sid.split("-")[0], "toronto_policy")


def main():
    rows = list(csv.DictReader((ROOT / "research" / "sources.csv").open()))
    docs = {}  # url -> document, in register order
    for r in rows:
        key = r["url"].strip() or None
        if not key or r["title"].startswith("data-sources.md"):
            continue
        d = docs.setdefault(key, {"ids": [], "rows": []})
        d["ids"].append(r["source_id"])
        d["rows"].append(r)

    items = {g: [] for g, _ in GROUPS}
    for url, d in docs.items():
        first = d["rows"][0]
        unverified = all(r["label"].startswith("UNVERIFIED") for r in d["rows"])
        g = group_of(d["ids"][0])
        if unverified and g != "images":
            g = "unverified"
        checked = sorted({r["verified_on"] for r in d["rows"] if r["verified_on"]})
        items[g].append({
            "ids": d["ids"],
            "author": first["publisher_or_author"],
            "title": first["title"],
            "published": first["published"],
            "url": url if url.startswith("http") else "",
            "where": "; ".join(dict.fromkeys(r["location_in_source"] for r in d["rows"] if r["location_in_source"])),
            "status": "unverified" if unverified else (f"checked {checked[-1]}" if checked else ""),
        })

    for r in csv.DictReader((ROOT / "data" / "manifest.csv").open()):
        sid = r["source_id"]
        if sid in DATASETS and not any(sid in i["ids"] for i in items["toronto_data"]):
            items["toronto_data"].append({
                "ids": [sid], "author": "City of Toronto Open Data", "title": DATASETS[sid],
                "published": f"retrieved {r['retrieved_at'][:10]}",
                "url": f"https://open.toronto.ca/dataset/{r['package']}/", "where": "",
                "status": "Open Government Licence – Toronto"})
        elif sid == "osm" and not any("osm" in i["ids"] for i in items["toronto_data"]):
            items["toronto_data"].append({
                "ids": ["osm"], "author": "OpenStreetMap contributors", "title": "OpenStreetMap road network (Overpass API)",
                "published": f"retrieved {r['retrieved_at'][:10]}", "url": "https://www.openstreetmap.org/copyright",
                "where": "", "status": "ODbL 1.0"})
    for sid, author, title, url in SOFTWARE:
        items["software"].append({"ids": [sid], "author": author, "title": title, "published": "",
                                  "url": url, "where": "", "status": "open source"})

    out, by_id, n = [], {}, 0
    for g, name in GROUPS:
        for it in items[g]:
            n += 1
            it["n"] = n
            for i in it["ids"]:
                by_id[i] = n
        out.append({"id": g, "name": name, "items": items[g]})
    OUT.write_text(json.dumps({"repo": REPO, "groups": out, "by_id": by_id}, ensure_ascii=False, indent=1) + "\n")
    print(f"{OUT.relative_to(ROOT)}: {n} references in {sum(bool(g['items']) for g in out)} groups")


if __name__ == "__main__":
    main()
