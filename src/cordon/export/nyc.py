"""New York before/after transit and traffic series for the web page (component 5).

Usage: uv run python -m cordon.export.nyc

Reads the latest data/raw/nyc_* snapshots (cordon.ingest.nyc) and writes
web/public/data/nyc_transit.json: monthly weekday-average ridership by mode,
zone vehicle entries, and year-on-year changes. All values OBSERVED (MTA open
data); the trend comparison is our calculation and descriptive, not causal.
"""

import json

import duckdb

from cordon import DATA, ROOT

LAUNCH = "2025-01-05"


def latest(ds):
    return sorted((DATA / "raw" / f"nyc_{ds}").glob("*/*.csv"))[-1]


def main():
    con = duckdb.connect()
    con.load_extension("spatial")
    rid, ent = latest("sayj-mze2"), latest("t6yz-b64h")
    con.execute(f"""create view r as select date::date d, mode, count::double n from read_csv('{rid}')
                    where dayofweek(date::date) between 1 and 5""")
    monthly = con.execute("""
        select strftime(date_trunc('month', d), '%Y-%m') as month, mode, round(avg(n)) as riders
        from r where mode in ('Subway', 'Bus', 'LIRR', 'MNR') and d >= '2023-01-01'
          and date_trunc('month', d) < date_trunc('month', (select max(d) from r))
        group by all order by 1, 2""").fetchall()
    yearly = con.execute("""
        with y as (select mode, year(d) as yr, avg(n) as n from r where year(d) between 2023 and 2025 group by all)
        select a.mode, round(a.n) as y2023, round(b.n) as y2024, round(c.n) as y2025,
               round(b.n / a.n - 1, 4) as change_2024, round(c.n / b.n - 1, 4) as change_2025,
               round(c.n - b.n * b.n / a.n) as above_2024_trend
        from y a join y b on a.mode = b.mode and b.yr = 2024 join y c on a.mode = c.mode and c.yr = 2025
        where a.yr = 2023 and a.mode in ('Subway', 'Bus', 'LIRR', 'MNR') order by 1""").fetchall()
    entries = con.execute(f"""
        select year(day::date) as yr, round(avg(crz_entries)) as weekday_entries, count(*) as days
        from read_csv('{ent}') where dayofweek(day::date) between 1 and 5 group by 1 order by 1""").fetchall()
    out = {
        "label": "OBSERVED", "source_ids": ["N-001", "N-003"], "launch": LAUNCH,
        "monthly_weekday": [{"month": m, "mode": k, "riders": n} for m, k, n in monthly],
        "yearly_weekday": [dict(zip(["mode", "y2023", "y2024", "y2025", "change_2024", "change_2025",
                                     "above_2024_trend"], row)) for row in yearly],
        "zone_entries_weekday": [{"year": y, "entries": e, "days": d} for y, e, d in entries],
        "caveat": "System-wide ridership, not trips to the zone. Return-to-office and pandemic recovery "
                  "were also raising ridership, so growth above trend is not all due to pricing.",
    }
    dest = ROOT / "web" / "public" / "data" / "nyc_transit.json"
    dest.write_text(json.dumps(out, indent=1))
    for row in out["yearly_weekday"]:
        print(row)
    print(out["zone_entries_weekday"])


if __name__ == "__main__":
    main()
