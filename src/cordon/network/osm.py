"""Fetch the OpenStreetMap road network for the simulation area (Overpass API, no key).

Usage: uv run python -m cordon.network.osm

The study area is the union of candidate boundaries C1 and C2 plus a ~1.5 km
buffer, so diversion onto boundary streets and the downtown Gardiner, DVP and
Lake Shore is inside the network. Saved as a dated snapshot and recorded in
data/manifest.csv like every other source.
"""

import csv
import hashlib
from datetime import datetime, timezone

import httpx

from cordon import DATA

BBOX = (43.620, -79.432, 43.690, -79.327)  # south, west, north, east
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
HIGHWAYS = ("motorway|motorway_link|trunk|trunk_link|primary|primary_link|secondary|"
            "secondary_link|tertiary|tertiary_link|unclassified|residential|living_street")
QUERY = f"""
[out:xml][timeout:180];
(
  way["highway"~"^({HIGHWAYS})$"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
);
(._;>;);
(._; node["highway"="traffic_signals"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]}););
out body;
"""


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    outdir = DATA / "raw" / "osm" / today
    outdir.mkdir(parents=True, exist_ok=True)
    dest = outdir / "study_area.osm.xml"
    for endpoint in ENDPOINTS:  # public mirrors of the same OSM data
        try:
            r = httpx.post(endpoint, data={"data": QUERY}, timeout=300,
                           headers={"User-Agent": "congestion-cordon research (buildathon)"})
            r.raise_for_status()
            break
        except httpx.HTTPError as e:
            print(f"{endpoint}: {e}")
    else:
        raise SystemExit("all Overpass endpoints failed")
    dest.write_bytes(r.content)
    digest = hashlib.sha256(r.content).hexdigest()
    with open(DATA / "manifest.csv", "a", newline="") as f:
        csv.writer(f).writerow([
            "osm", "overpass", "study_area roads", "", endpoint, str(dest.relative_to(DATA.parent)),
            datetime.now(timezone.utc).isoformat(timespec="seconds"), len(r.content), digest, "",
            "ODbL 1.0 (© OpenStreetMap contributors)"])
    print(f"{dest} {len(r.content) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
