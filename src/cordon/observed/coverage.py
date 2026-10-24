"""Assess whether City counts cover each boundary crossing.

Usage: uv run python -m cordon.observed.coverage

A crossing is "covered" when a turning-movement count (TMC, at an intersection)
or a midblock count (SVC) on the same street lies within MATCH_RADIUS_M of the
crossing point. The nearest qualifying count is recorded with its date and
distance, so every match can be audited. Expressways carry no City TMC/SVC
counts in the open data (the RESCU detector feed is not published), which is
reported as a gap rather than filled.

Output: data/processed/crossing_coverage.parquet
"""

import duckdb
import pandas as pd

from cordon import DATA

MATCH_RADIUS_M = 250
RECENT_FROM = "2023-01-01"  # post-pandemic base window; older counts reported separately


def main():
    con = duckdb.connect()
    con.load_extension("spatial")
    raw = DATA / "raw"
    con.execute(f"""
        create table x as
        select cordon_id, centreline_id, linear_name_full, linear_name, feature_code_desc,
               jurisdiction, from_intersection_id, to_intersection_id, outside_intersection_id,
               st_transform(st_geomfromtext(crossing_point), 'EPSG:4326', 'EPSG:2952', always_xy := true) pt
        from '{DATA / "processed" / "crossings.parquet"}'
        where feature_code_desc <> 'Laneway';

        create table counts as
        select 'TMC' kind, count_id, location_name, count_date::date count_date,
               count_duration::varchar duration,
               st_transform(st_point(longitude, latitude), 'EPSG:4326', 'EPSG:2952', always_xy := true) pt
        from read_csv_auto('{raw}/tor_tmc/*/tmc_summary_data.csv', types={{'count_duration':'VARCHAR'}})
        union all
        select 'SVC', count_id, location_name, count_date_start::date,
               count_duration::varchar,
               st_transform(st_point(longitude, latitude), 'EPSG:4326', 'EPSG:2952', always_xy := true)
        from read_csv_auto('{raw}/tor_svc/*/svc_summary_data.csv');
    """)
    df = con.execute(f"""
        with m as (
          select x.cordon_id, x.centreline_id, c.kind, c.count_id, c.location_name, c.count_date, c.duration,
                 st_distance(x.pt, c.pt) dist_m
          from x join counts c
            on st_dwithin(x.pt, c.pt, {MATCH_RADIUS_M})
           and c.location_name ilike '%' || x.linear_name || '%'
        ),
        best as (
          select cordon_id, centreline_id,
                 max(count_date) last_count_date,
                 max(count_date) filter (where kind = 'TMC') last_tmc,
                 max(count_date) filter (where kind = 'SVC') last_svc,
                 arg_min(location_name, dist_m) filter (where count_date >= '{RECENT_FROM}') nearest_recent_site,
                 min(dist_m) filter (where count_date >= '{RECENT_FROM}') nearest_recent_m,
                 count(*) filter (where count_date >= '{RECENT_FROM}') n_recent_counts
          from m group by all
        )
        select x.* exclude (pt), st_astext(st_transform(x.pt, 'EPSG:2952', 'EPSG:4326', always_xy := true)) crossing_wkt,
               b.* exclude (cordon_id, centreline_id),
               case when x.feature_code_desc ilike 'Expressway%' then 'expressway: no open City counts'
                    when b.last_count_date >= '{RECENT_FROM}' then 'counted 2023+'
                    when b.last_count_date is not null then 'counted before 2023 only'
                    else 'never counted (within {MATCH_RADIUS_M} m)' end coverage
        from x left join best b using (cordon_id, centreline_id)
    """).df()
    out = DATA / "processed" / "crossing_coverage.parquet"
    df.to_parquet(out)
    df["major"] = df.feature_code_desc.str.contains("Arterial|Expressway")
    print(pd.crosstab([df.cordon_id], df.coverage, margins=True).to_string())
    print()
    print(pd.crosstab([df.cordon_id], df[df.major].coverage).to_string())


if __name__ == "__main__":
    main()
