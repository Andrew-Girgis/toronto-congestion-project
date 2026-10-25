"""Ten-year financial model for each priced scenario (component 4).

Usage: uv run python -m cordon.finance.cashflow

Gross collections are built from chargeable events AFTER the behavioural
response, times the rate that applied, never from a foreign net-per-entry ratio:

  AM charge events (SUMO, 06:00-10:00, once per vehicle)
    / AM share of charged-day entries          -> charged-day entries
    x (1 - repeat entries under once-per-day)   (cars; trucks pay per entry)
    x (1 - exempt/discounted share)
    x charging days per year
    x (1 - collection loss)
  + ride-hail trips x per-trip fee (instead of the daily charge)

Costs are kept separate: capital (charging points + central system), operating
(share of gross, falling with maturity), then allocations of net to transit
service and equity mitigation. All values are 2025 CAD, real terms. Toll
revenue is a transfer, not a social benefit, and is never added to time savings.

Low/base/high are illustrative scenario ranges (not confidence intervals). SUMO
runs the base response only; low/high scale the simulated reduction in charged
traffic by the ratio of low/high to base removal at each scenario's price.

Inputs:  sim/out/summary.json (from cordon.sim.scenarios), config/*.yaml,
         data/processed/crossing_coverage.parquet
Output:  web/public/data/finance.json
"""

import json

import pandas as pd
import yaml

from cordon import CONFIG, DATA, ROOT
from cordon.behaviour.response import load_assumptions, removed_share, response_for

YEARS = 10


def v(node, case="base"):
    if not isinstance(node, dict):
        return node
    key = {"base": "value", "low": "low", "high": "high"}[case]
    return node.get(key, node["value"])


def npv(flows, rate):
    """flows indexed from the first implementation year; year 0 is undiscounted."""
    return sum(f / (1 + rate) ** t for t, f in enumerate(flows))


def charging_points(cordon_id, n_expressway_points):
    cov = pd.read_parquet(DATA / "processed" / "crossing_coverage.parquet")
    return int((cov.cordon_id == cordon_id).sum()) + n_expressway_points


def scenario_finance(name, sim, a, scen_cfg, case):
    d, f, c = a["design"], a["finance"], a["costs"]
    # Pessimistic case pairs low traffic response with high costs and vice versa,
    # so the band shows the spread of plausible net outcomes.
    cost_case = {"low": "high", "base": "base", "high": "low"}[case]
    base_resp, case_resp = response_for("base", a), response_for(case, a)
    rates = scen_cfg["rate_by_hour"]
    mean_rate = sum(rates.values()) / len(rates)
    scale = (removed_share(mean_rate, case_resp.c0, case_resp.elasticity)
             / max(removed_share(mean_rate, base_resp.c0, base_resp.elasticity), 1e-9))
    b = sim["baseline_chargeable"]
    r_base = 1 - sim["charged_vehicles"] / b if b else 0
    charged = b * (1 - min(r_base * scale, 0.95))
    avg_charge = sim["charge_revenue"] / max(sim["charged_vehicles"], 1)

    am_share = v(d["am_window_share_of_charged_day_entries"], cost_case)
    day_entries = charged / am_share
    trucks = day_entries * v(d["heavy_vehicle_share_of_crossings"])
    ptc = day_entries * v(a["taxi_ridehail"]["ptc_share_downtown_vkt_am_peak"])
    cars = day_entries - trucks - ptc
    once_per_day = scen_cfg["once_per"] == "day"
    car_events = cars * (1 - v(d["repeat_entry_share_once_per_day"], cost_case)) if once_per_day else cars
    exempt = 1 - v(d["exempt_or_discounted_share"], cost_case)
    loss = 1 - v(a["compliance"]["collection_loss_share"], cost_case)
    days = v(d["charging_days_per_year"])
    ptc_fee = v(d["ptc_per_trip_fee_cad"], cost_case) if once_per_day else avg_charge
    gross_daily = ((car_events + trucks * v(d["truck_rate_multiplier"])) * avg_charge * exempt
                   + ptc * ptc_fee)
    gross_year = gross_daily * days * loss / 1e6  # CAD M

    points = charging_points(sim["cordon_id"], sim["n_expressway_points"]) if sim["cordon_id"] else sim["n_expressway_points"]
    capex = (points * v(c["roadside_per_charging_point_2025"], cost_case)
             + v(c["central_system_capex_2025"], cost_case))
    impl = v(f["implementation_years_before_launch"])
    opex_shares = f["opex_share_by_year"]["value"]
    rows = []
    for t in range(impl):
        rows.append({"year": t - impl + 1, "phase": "implementation", "gross": 0.0, "opex": 0.0,
                     "capex": capex / impl})
    for y in range(1, YEARS + 1):
        g = gross_year * (v(f["ramp_up_year1_collection_factor"]) if y == 1 else 1)
        share = opex_shares[y - 1]
        if cost_case == "high":
            share = max(share, v(c["opex_share_of_gross"], "high")) if y <= 2 else share * 1.25
        elif cost_case == "low":
            share *= 0.8
        rows.append({"year": y, "phase": "operating", "gross": g, "opex": g * share, "capex": 0.0})
    df = pd.DataFrame(rows)
    df["net"] = df.gross - df.opex - df.capex
    df["cumulative_net"] = df.net.cumsum()
    pos = df[df.net > 0]
    df["transit_service"] = (df.net.clip(lower=0) * v(f["transit_service_share_of_net"]))
    df["equity_mitigation"] = (df.net.clip(lower=0) * v(f["equity_mitigation_share_of_net"]))
    df["other_transport"] = df.net.clip(lower=0) - df.transit_service - df.equity_mitigation
    flows = df.net.tolist()
    transit = transit_shift(sim, a, case, scale, am_share)
    return {
        "scenario": name, "case": case,
        "label": "ESTIMATED (scenario model; inputs labelled in config/assumptions.yaml)",
        "charged_am_vehicles": round(charged), "baseline_chargeable_am": round(b),
        "am_reduction_in_charged_traffic": round(1 - charged / b, 3) if b else None,
        "avg_charge_cad": round(avg_charge, 2), "charging_points": points,
        "gross_per_year_cad_m": round(gross_year, 1), "capex_cad_m": round(capex, 1),
        "npv_net_cad_m": {r: round(npv(flows, r), 1) for r in (0.07, 0.035, 0.03)},
        "payback_year": int(df[df.cumulative_net > 0].year.min()) if (df.cumulative_net > 0).any() else None,
        "first_positive_year": int(pos.year.min()) if len(pos) else None,
        "cashflow": df.round(2).to_dict(orient="records"),
        "transit": transit,
    }


def transit_shift(sim, a, case, scale, am_share):
    """New transit trips from drivers the charge takes off the road, and the fares they pay.

    Removed vehicles (off-network, not rerouted) x transit share of non-reroute responses
    x occupancy x trips per entry. Fares split between TTC (City) and GO (Metrolinx, provincial).
    """
    t, comp = a["transit_response"], a["behaviour"]["response_composition_of_removed_trips"]
    others = {k: v(n) for k, n in comp.items() if isinstance(n, dict) and k != "reroute_around_zone"}
    others["switch_to_transit"] = v(comp["switch_to_transit"], case)
    to_transit = others["switch_to_transit"] / sum(others.values())
    removed_am = (sim.get("removed_offnetwork", 0) + sim.get("retimed_to_shoulder", 0)) * scale
    people_am = removed_am * to_transit * v(a["value_of_time"]["vehicle_occupancy_auto"])
    daily_trips = people_am / am_share * v(t["one_way_trips_per_removed_entry"])
    go = v(t["go_share_of_new_transit_trips"], case)
    days = v(a["design"]["charging_days_per_year"])
    ttc_fares = daily_trips * (1 - go) * v(t["ttc_average_fare_cad"]) * days / 1e6
    go_fares = daily_trips * go * v(t["go_average_fare_cad"]) * days / 1e6
    return {"label": "ESTIMATED", "share_of_removed_to_transit": round(to_transit, 3),
            "am_new_transit_riders": round(people_am), "daily_new_transit_trips": round(daily_trips),
            "ttc_fares_cad_m": round(ttc_fares, 1), "go_fares_cad_m": round(go_fares, 1)}


def main():
    a = load_assumptions()
    scen = yaml.safe_load((CONFIG / "scenarios.yaml").read_text())["scenarios"]
    summary = json.loads((ROOT / "sim" / "out" / "summary.json").read_text())
    out = {"currency": "CAD", "price_base_year": 2025, "real_terms": True, "horizon_years": YEARS,
           "discount_rates": {"0.07": "Treasury Board of Canada CBA guide", "0.035": "Metrolinx BCM",
                              "0.03": "social time preference sensitivity"},
           "note": "Financial cash flows only. Time savings, reliability and emissions are reported "
                   "separately and toll payments are not counted as a social benefit.",
           "results": []}
    for name, sim in summary.items():
        if name == "S0":
            continue
        for case in ("low", "base", "high"):
            out["results"].append(scenario_finance(name, sim, a, scen[name], case))
    dest = ROOT / "web" / "public" / "data" / "finance.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1))
    for r in out["results"]:
        print(f"{r['scenario']} {r['case']:5} charged_am={r['charged_am_vehicles']:>7,} "
              f"gross=${r['gross_per_year_cad_m']:>6.1f}M/yr capex=${r['capex_cad_m']:>5.1f}M "
              f"NPV7=${r['npv_net_cad_m'][0.07]:>7.1f}M payback={r['payback_year']} "
              f"transit/day={r['transit']['daily_new_transit_trips']:,} fares TTC ${r['transit']['ttc_fares_cad_m']}M GO ${r['transit']['go_fares_cad_m']}M")


if __name__ == "__main__":
    main()
