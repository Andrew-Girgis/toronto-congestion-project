"""Every number the slide deck shows, rounded and worded once (component 5).

Usage: uv run python -m cordon.export.figures   (after cordon.export.web, finance, export.nyc)

Reads web/public/data/{metrics,finance,nyc_transit,cases}.json, crossings/counts
GeoJSON, config/*.yaml and the user-feedback log, and writes
web/public/data/figures.json: {id: {value, display, label, src, note}}. The deck
(web/src/pages/present.astro) renders figures only through <Fig id=...>, and
scripts/present/check_figures.py checks the built HTML against this file.
"""

import csv
import json

import yaml

from cordon import CONFIG, ROOT

D = ROOT / "web" / "public" / "data"
MINUS = "−"
HEADLINE = "S4"


def load(name):
    return json.loads((D / name).read_text())


def signed(x, digits=1):
    s = f"{abs(x) * 100:.{digits}f}%"
    return ("+" if x > 0 else MINUS if x < 0 else "") + s


def money(x):
    return f"C${x:,.0f}M" if x >= 100 else f"C${x:,.1f}M"


def main():
    m, fin, nyc, cases = load("metrics.json"), load("finance.json"), load("nyc_transit.json"), load("cases.json")
    crossings, counts = load("crossings.geojson"), load("counts.geojson")
    scen = yaml.safe_load((CONFIG / "scenarios.yaml").read_text())["scenarios"]
    a = yaml.safe_load((CONFIG / "assumptions.yaml").read_text())
    S, s0 = m["scenarios"], m["scenarios"]["S0"]
    F = {}

    def add(fid, value, display, label, src, note=""):
        F[fid] = {"value": value, "display": display, "label": label, "src": src, "note": note}

    def rel(sid, key):
        return S[sid][key] / s0[key] - 1

    # Gap: the City has no count of cars entering downtown; how many entry roads have any recent count
    c1 = [f["properties"] for f in crossings["features"] if f["properties"]["cordon_id"] == m["cordon_id"]]
    counted = sum(p["coverage"] == "counted 2023+" for p in c1)
    add("roads_counted", counted, f"{counted} of {len(c1)}", "OBSERVED", "crossings.geojson coverage",
        "roads into downtown with a City count since 2023")
    sites = counts["features"]
    hold = sum(f["properties"]["split"] == "holdout" for f in sites)
    add("count_sites", len(sites), f"{len(sites):,}", "OBSERVED", "counts.geojson", "intersections with City turning counts")
    add("holdout_sites", hold, f"{hold:,}", "OBSERVED", "counts.geojson split=holdout", "held back to test the model")

    rate = scen[HEADLINE]["rate_by_hour"]
    r = sum(rate.values()) / len(rate)
    add("rate", r, f"C${r:.2f}", "ESTIMATED", f"scenarios.yaml {HEADLINE}.rate_by_hour", "NYC US$9 in 2025 Canadian dollars")

    # Cases: text figures from official evaluations, tagged as recorded in cases.json
    for c in cases["cases"]:
        for k in ("traffic", "speed", "money"):
            add(f"case_{c['id']}_{k}", None, c[k]["text"], c[k]["label"], f"cases.json {c['id']}.{k} [{c[k]['src']}]")

    # NYC transit, MTA open data
    y = {r["mode"]: r for r in nyc["yearly_weekday"]}
    for mode, fid in (("Subway", "subway"), ("Bus", "bus"), ("LIRR", "lirr"), ("MNR", "mnr")):
        for yr in ("2024", "2025"):
            v = y[mode][f"change_{yr}"]
            add(f"nyc_{fid}_{yr}", v, signed(v), "OBSERVED", f"nyc_transit.json yearly_weekday.{mode}.change_{yr}",
                f"weekday riders {yr} vs {int(yr) - 1}")

    # Method
    cal = a["calibration"]["observed_band_at_reference_price"]["crossing_reduction_at_reference"]
    add("resp_base", -cal["value"], signed(-cal["value"], 0), "ASSUMPTION", "assumptions.yaml calibration (NYC, MTA-reported)",
        "fewer charged trips at the New York price")
    add("resp_low", -cal["low"], signed(-cal["low"], 0), "ASSUMPTION", "assumptions.yaml calibration low")
    add("resp_high", -cal["high"], signed(-cal["high"], 0), "ASSUMPTION", "assumptions.yaml calibration high (Stockholm trial)")
    base = [r for r in fin["results"] if r["scenario"] == HEADLINE]
    bc = {r["case"]: r for r in base}
    sh = bc["base"]["transit"]["share_of_removed_to_transit"]
    add("transit_share", sh, f"{sh * 100:.0f}%", "ASSUMPTION", "finance.json transit.share_of_removed_to_transit",
        "of drivers taken off the road switch to transit (London, Stockholm)")
    v = m["validation"]
    g5 = v["holdout"]["share_geh_lt5_approaches"]
    add("fit_holdout", g5, f"{g5 * 100:.0f}%", "SIMULATED", "metrics.json validation.holdout.share_geh_lt5_approaches",
        "held-out counts the model matches closely (GEH < 5)")
    add("fit_target", 0.85, "85%", "OBSERVED (REPORT)", "metrics.json validation.criterion (UK TAG/DMRB)", "usual target")
    rr = v["holdout"]["r_approaches"]
    add("fit_r", rr, f"{rr:.2f}", "SIMULATED", "metrics.json validation.holdout.r_approaches", "correlation with held-out counts")

    # Toronto results, headline scenario
    paying = S[HEADLINE]["charged_vehicles"] / S[HEADLINE]["baseline_chargeable"] - 1
    add("s4_paying", paying, signed(paying, 0), "SIMULATED", f"metrics.json {HEADLINE} charged/baseline_chargeable",
        "cars paying to enter downtown, 6–10 a.m.")
    for sid in (HEADLINE, "S2"):
        k = sid.lower()
        add(f"{k}_zone", rel(sid, "zone_vkt_am"), signed(rel(sid, "zone_vkt_am")), "SIMULATED", f"metrics.json {sid}.zone_vkt_am",
            "traffic on downtown streets (vehicle-km)")
        add(f"{k}_boundary", rel(sid, "boundary_local_street_vkt_am"), signed(rel(sid, "boundary_local_street_vkt_am")), "SIMULATED",
            f"metrics.json {sid}.boundary_local_street_vkt_am", "traffic on local streets just outside the zone")
        add(f"{k}_vht", rel(sid, "vehicle_hours"), signed(rel(sid, "vehicle_hours")), "SIMULATED", f"metrics.json {sid}.vehicle_hours",
            "total time spent driving in the study area")
        add(f"{k}_speed", rel(sid, "zone_street_speed_kmh"), signed(rel(sid, "zone_street_speed_kmh")), "SIMULATED",
            f"metrics.json {sid}.zone_street_speed_kmh", "average speed on downtown streets")
    rer = S[HEADLINE]["rerouted_to_avoid_charge"]
    add("s4_rerouted", rer, f"{rer:,}", "SIMULATED", f"metrics.json {HEADLINE}.rerouted_to_avoid_charge", "drivers who route around the zone")

    # Money and transit, headline scenario
    g = [bc[c]["gross_per_year_cad_m"] for c in ("low", "base", "high")]
    add("gross", bc["base"]["gross_per_year_cad_m"], money(bc["base"]["gross_per_year_cad_m"]), "ESTIMATED",
        f"finance.json {HEADLINE} base gross_per_year_cad_m", "collected per year, before costs")
    add("gross_range", [min(g), max(g)], f"{min(g):,.0f}–{max(g):,.0f}", "ESTIMATED", f"finance.json {HEADLINE} all cases")
    cx = [bc[c]["capex_cad_m"] for c in ("low", "base", "high")]
    add("capex", bc["base"]["capex_cad_m"], money(bc["base"]["capex_cad_m"]), "ESTIMATED", f"finance.json {HEADLINE} base capex_cad_m",
        f"to build {bc['base']['charging_points']} charging points and the back office")
    add("capex_range", [min(cx), max(cx)], f"C${min(cx):,.0f}–{max(cx):,.0f}M", "ESTIMATED", f"finance.json {HEADLINE} all cases")
    yr1 = next(c for c in bc["base"]["cashflow"] if c["year"] == 1)
    add("opex_y1", yr1["opex"], money(yr1["opex"]), "ESTIMATED", f"finance.json {HEADLINE} base cashflow year 1 opex",
        "running cost in year one")
    npv = [bc[c]["npv_net_cad_m"]["0.07"] for c in ("low", "base", "high")]
    add("npv", npv[1], f"C${npv[1] / 1000:.1f}B", "ESTIMATED", f"finance.json {HEADLINE} base npv_net_cad_m 0.07",
        "10-year net cash, today's value at 7%")
    add("npv_range", [min(npv), max(npv)], f"C${min(npv) / 1000:.1f}–{max(npv) / 1000:.1f}B", "ESTIMATED", f"finance.json {HEADLINE} all cases")
    for k, fmt_, note in (("daily_new_transit_trips", lambda x: f"{x:,}", "new transit trips per weekday"),
                          ("am_new_transit_riders", lambda x: f"{x:,}", "new riders heading downtown, 6–10 a.m."),
                          ("ttc_fares_cad_m", money, "extra TTC fares per year (City)"),
                          ("go_fares_cad_m", money, "extra GO fares per year (Metrolinx, provincial)")):
        vals = [bc[c]["transit"][k] for c in ("low", "base", "high")]
        add(f"t_{k}", vals[1], fmt_(vals[1]), "ESTIMATED", f"finance.json {HEADLINE} base transit.{k}", note)
        add(f"t_{k}_range", [min(vals), max(vals)], f"{fmt_(min(vals))}–{fmt_(max(vals))}", "ESTIMATED", f"finance.json {HEADLINE} all cases")

    # Feedback and the ask
    with open(ROOT / "research" / "user-feedback" / "log.csv") as f:
        n = len({row["id"] for row in csv.DictReader(f)})
    add("feedback_n", n, f"{n}", "OBSERVED", "research/user-feedback/log.csv distinct id", "conversation logged at the event")
    pc = a["pilot"]["cost_cad"]
    add("pilot_cost", [pc["low"], pc["high"]], f"C${round(pc['low'], -4) / 1000:.0f}k–{round(pc['high'], -4) / 1000:.0f}k",
        "ASSUMPTION", "assumptions.yaml pilot.cost_cad (adoption/cost.md)", "staff time and hosting for 90 days")

    (D / "figures.json").write_text(json.dumps(F, indent=1, ensure_ascii=False))
    for k, x in F.items():
        print(f"{k:32} {x['display']:<40} {x['label']}")


if __name__ == "__main__":
    main()
