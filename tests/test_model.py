"""Sanity tests for the data pipeline and the behaviour/finance models."""

import csv
import hashlib
from pathlib import Path

import pandas as pd
import pytest
import yaml

from cordon import CONFIG, DATA, ROOT
from cordon.behaviour.response import load_assumptions, removed_share, response_for, solve_c0

LABELS = ("OBSERVED", "ESTIMATED", "ASSUMPTION", "UNVERIFIED", "SIMULATED", "MODELLED")


def test_calibration_hits_target():
    for case, target in (("low", 0.10), ("base", 0.15), ("high", 0.22)):
        r = response_for(case)
        assert removed_share(12.58, r.c0, r.elasticity) == pytest.approx(target, abs=1e-9)


def test_response_increases_with_price_and_is_bounded():
    r = response_for("base")
    shares = [removed_share(p, r.c0, r.elasticity) for p in (0, 3, 6.29, 12.58, 20)]
    assert shares[0] == 0
    assert all(a < b for a, b in zip(shares, shares[1:]))
    assert shares[-1] < 1


def test_composition_excludes_reroute_and_sums_to_one():
    comp = response_for("base").composition
    assert "reroute_around_zone" not in comp
    assert sum(comp.values()) == pytest.approx(1)


def test_revenue_congestion_tradeoff():
    """A stronger response at the same price means fewer paying trips, so less revenue."""
    revenue = []
    for target in (0.10, 0.15, 0.22):
        c0 = solve_c0(-0.5, target, 12.58)
        paying = 1 - removed_share(12.58, c0, -0.5)
        revenue.append(paying * 12.58)
    assert revenue[0] > revenue[1] > revenue[2]


def test_every_assumption_is_labelled():
    a = load_assumptions()
    missing = []

    def walk(node, path):
        if isinstance(node, dict):
            if "value" in node and "label" not in node:
                missing.append(path)
            for k, v in node.items():
                walk(v, f"{path}.{k}")
    walk(a, "assumptions")
    assert not missing, missing
    assert all(any(l in str(n.get("label", "")) for l in LABELS)
               for n in _leaves(a) if isinstance(n, dict) and "label" in n)


def _leaves(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _leaves(v)


def test_manifest_checksums_match_raw_files():
    rows = list(csv.DictReader(open(DATA / "manifest.csv")))
    assert rows
    for r in rows:
        p = ROOT / r["file"]
        if not p.exists():
            pytest.skip("raw snapshots not downloaded (run `make data`)")
        assert hashlib.sha256(p.read_bytes()).hexdigest() == r["sha256"], r["file"]


def test_crossings_have_no_duplicates():
    p = DATA / "processed" / "crossing_coverage.parquet"
    if not p.exists():
        pytest.skip("run `make coverage`")
    df = pd.read_parquet(p)
    assert not df.duplicated(["cordon_id", "centreline_id"]).any()
    assert set(df.coverage.unique()) <= {"counted 2023+", "counted before 2023 only",
                                         "expressway: no open City counts", "never counted (within 250 m)"}


def test_scenarios_compare_against_same_baseline():
    s = yaml.safe_load((CONFIG / "scenarios.yaml").read_text())
    assert "S0" in s["scenarios"] and s["scenarios"]["S0"]["charges"] == "none"
    for k, v in s["scenarios"].items():
        if k != "S0":
            assert set(v["rate_by_hour"]) == {6, 7, 8, 9}
