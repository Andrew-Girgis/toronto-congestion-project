"""Dated snapshots of MTA open data from data.ny.gov (Socrata; no account needed).

Usage: uv run python -m cordon.ingest.nyc

Writes data/raw/nyc_<dataset>/<YYYY-MM-DD>/<dataset>.csv and appends rows to data/manifest.csv.
"""

import csv
import hashlib
from datetime import date, datetime, timezone

import httpx

from cordon import DATA, ROOT

DATASETS = {
    "sayj-mze2": "MTA Daily Ridership and Traffic: Beginning 2020",
    "jbxx-kxff": "MTA Vehicle Miles Traveled in the CBD",
    "t6yz-b64h": "MTA Congestion Relief Zone Vehicle Entries: Beginning 2025",
}
# Hourly entries by detection group are large; daily totals are enough here.
QUERIES = {
    "t6yz-b64h": "$select=date_trunc_ymd(toll_date) as day, sum(crz_entries) as crz_entries,"
                 "sum(excluded_roadway_entries) as excluded_roadway_entries&$group=day&$order=day&$limit=5000",
}
BASE = "https://data.ny.gov/resource"


def main():
    today = date.today().isoformat()
    rows = []
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        for ds, name in DATASETS.items():
            url = f"{BASE}/{ds}.csv?" + QUERIES.get(ds, "$limit=500000")
            r = client.get(url)
            r.raise_for_status()
            out = DATA / "raw" / f"nyc_{ds}" / today / f"{ds}.csv"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(r.content)
            rows.append({"source_id": f"nyc_{ds}", "package": ds, "resource_name": name, "resource_id": ds,
                         "url": url, "file": str(out.relative_to(ROOT)),
                         "retrieved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest(),
                         "resource_last_modified": "", "licence": "NY Open Data terms (data.ny.gov)"})
            print(f"{ds}: {len(r.content):,} bytes -> {out.relative_to(ROOT)}")
    with open(DATA / "manifest.csv", "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writerows(rows)


if __name__ == "__main__":
    main()
