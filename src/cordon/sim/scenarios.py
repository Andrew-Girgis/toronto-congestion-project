"""Run the baseline and priced scenarios in SUMO and summarise them.

Usage: uv run python -m cordon.sim.scenarios [S0 S1 S2 S3]

S0 simulates the calibrated baseline demand (sim/demand/baseline.rou.xml).
For each priced scenario:
  1. Charged edges: inbound edges crossing the cordon (from-node outside,
     to-node inside) and/or entries onto the Gardiner/DVP (on-ramps and
     mainline edges entering the network).
  2. Chargeable vehicles: baseline vehicles whose route uses a charged edge.
  3. Aggregate response (cordon.behaviour.response): at the rate for the hour,
     a share leaves the AM car network (mode shift, destination change or
     cancellation, retiming outside the window, commercial trips not made).
     In S3 the retiming share moves from peak into the cheaper shoulder hours.
  4. Rerouting: the remaining chargeable vehicles are re-routed by duarouter on
     baseline hourly travel times plus the toll converted to time
     (value of time per vehicle-hour). Uncharged vehicles keep their routes:
     this is a one-shot response, not an equilibrium assignment.
  5. Simulate (SUMO mesoscopic model with junction control) and compare with S0.

Outputs: sim/out/<S>/ (SUMO outputs), sim/out/summary.json
"""

import json
import random
import subprocess
import sys
import xml.etree.ElementTree as ET

import geopandas as gpd
import sumo
import yaml
from shapely.geometry import Point
from shapely.ops import transform

sys.path.append(str(sumo.SUMO_HOME) + "/tools")
import sumolib  # noqa: E402

from cordon import CONFIG, ROOT  # noqa: E402
from cordon.behaviour.response import load_assumptions, response_for  # noqa: E402

NET = ROOT / "sim" / "net" / "study_area.net.xml.gz"
BASE_ROUTES = ROOT / "sim" / "demand" / "baseline.rou.xml"
OUT = ROOT / "sim" / "out"
BIN = ROOT / ".venv" / "bin"
EXPRESSWAY_NAMES = ("Gardiner", "Don Valley")
SEED = 42
FCD_PROBABILITY = 0.08  # share of vehicles traced for the animation


MESO_OPTS = ["--mesosim", "--meso-tls-penalty", 1, "--meso-tls-flow-penalty", 1, "--meso-minor-penalty", 3]


def run(cmd):
    print("  $", " ".join(str(c) for c in cmd[:3]), "...", flush=True)
    subprocess.run([str(c) for c in cmd], check=True, stdout=subprocess.DEVNULL)


def write_additional(path, outdir):
    path.write_text(f"""<additional>
  <vType id="car" vClass="passenger"/>
  <edgeData id="hourly" period="3600" file="{outdir / 'edgedata.xml'}" excludeEmpty="true"/>
</additional>
""")


def simulate(name, routes, sim_cfg):
    outdir = OUT / name
    outdir.mkdir(parents=True, exist_ok=True)
    add = outdir / "outputs.add.xml"
    write_additional(add, outdir)
    run([BIN / "sumo", "-n", NET, "-r", routes, "-a", add,
         "--begin", sim_cfg["begin_s"], "--end", sim_cfg["end_s"] + 3600,
         # Mesoscopic queue model (~8x faster than microsimulation on this 279k-vehicle
         # morning). Full junction control deadlocked the network, so signals are
         # represented by green-split delay and headway penalties instead.
         *MESO_OPTS, "--statistic-output", outdir / "stats.xml",
         "--time-to-teleport", 300, "--ignore-route-errors", "--no-step-log", "--no-warnings",
         "--seed", SEED, "--tripinfo-output", outdir / "tripinfo.xml",
         "--vehroute-output", outdir / "vehroutes.xml", "--vehroute-output.exit-times",
         "--device.fcd.probability", FCD_PROBABILITY, "--fcd-output", outdir / "fcd.xml",
         "--fcd-output.geo", "--device.fcd.period", 10])
    return outdir


def read_routes(path):
    """vehicle id -> (depart seconds, [edges]) from a SUMO route file."""
    out = {}
    for _, el in ET.iterparse(path):
        if el.tag == "vehicle":
            r = el.find("route")
            out[el.get("id")] = (float(el.get("depart")), r.get("edges").split())
            el.clear()
    return out


def charged_edges(net, cordon_id):
    """Return (cordon inbound edges, expressway entry edges) as sets of edge ids."""
    inbound = set()
    if cordon_id:
        zone = gpd.read_file(CONFIG / "cordons" / f"{cordon_id}.geojson").geometry.iloc[0]
        zone_xy = transform(lambda x, y, z=None: net.convertLonLat2XY(x, y), zone)
        for e in net.getEdges():
            if not e.allows("passenger"):
                continue
            a_in = zone_xy.contains(Point(e.getFromNode().getCoord()))
            b_in = zone_xy.contains(Point(e.getToNode().getCoord()))
            if not a_in and b_in:
                inbound.add(e.getID())

    def is_xwy(e):
        return e.getType() == "highway.motorway" and any(n in (e.getName() or "") for n in EXPRESSWAY_NAMES)

    entries = set()
    for e in net.getEdges():
        if is_xwy(e):
            preds = e.getFromNode().getIncoming()
            if not preds:
                entries.add(e.getID())  # mainline entering the study area
        elif e.getType() == "highway.motorway_link" and any(is_xwy(o) for o in e.getOutgoing()):
            entries.add(e.getID())  # on-ramp onto the Gardiner/DVP
    return inbound, entries


def nyc_style_cordon(net, cordon_id, inbound):
    """Cordon charge with the expressway mainline free, as New York leaves the FDR Drive and West
    Side Highway uncharged: surface roads crossing into the zone, plus expressway off-ramps that
    lead into the zone (drivers pay when they exit into it)."""
    zone = gpd.read_file(CONFIG / "cordons" / f"{cordon_id}.geojson").geometry.iloc[0]
    zone_xy = transform(lambda x, y, z=None: net.convertLonLat2XY(x, y), zone)
    surface = {eid for eid in inbound if not net.getEdge(eid).getType().startswith("highway.motorway")}
    exits = {e.getID() for e in net.getEdges()
             if e.getType() == "highway.motorway_link"
             and any(i.getType() == "highway.motorway" for i in e.getFromNode().getIncoming())
             and zone_xy.contains(Point(e.getToNode().getCoord()))}
    return surface | exits


def hour_of(t):
    return int(t // 3600)


def build_scenario_routes(name, cfg, sim_cfg, base, charged, resp, a, net):
    rng = random.Random(SEED)
    rates = {int(k): v for k, v in cfg["rate_by_hour"].items()}
    retime_share = resp.composition["retime_outside_charged_hours"]
    removed, retimed, keep_charged, keep_free = [], [], {}, {}
    for vid, (dep, edges) in base.items():
        if not charged.intersection(edges):
            keep_free[vid] = (dep, edges)
            continue
        h = hour_of(dep)
        p_off = resp.offnetwork_share(rates.get(h, 0))
        if rng.random() < p_off:
            # In S3 the retiming share shifts from peak to a cheaper shoulder hour.
            shoulder = [hh for hh, r in rates.items() if r < rates.get(h, 0)]
            if shoulder and rng.random() < retime_share:
                new_h = rng.choice(shoulder)
                dep = new_h * 3600 + rng.random() * 3600
                retimed.append(vid)
                keep_charged[vid] = (dep, edges)
            else:
                removed.append(vid)
            continue
        keep_charged[vid] = (dep, edges)

    outdir = OUT / name
    outdir.mkdir(parents=True, exist_ok=True)
    # Generalised-cost weights: baseline hourly travel time + toll converted to seconds.
    vot_s = a["value_of_time"]["sumo_vot_per_vehicle_hour"]["value"] / 3600
    base_ed = ET.parse(OUT / "S0" / "edgedata.xml").getroot()
    w = ET.Element("meandata")
    for interval in base_ed.findall("interval"):
        h = hour_of(float(interval.get("begin")))
        iv = ET.SubElement(w, "interval", begin=interval.get("begin"), end=interval.get("end"))
        seen = set()
        for ed in interval.findall("edge"):
            eid = ed.get("id")
            tt = float(ed.get("traveltime") or 0) or net.getEdge(eid).getLength() / net.getEdge(eid).getSpeed()
            toll_s = rates.get(h, 0) / vot_s if eid in charged else 0
            ET.SubElement(iv, "edge", id=eid, traveltime=f"{tt + toll_s:.1f}")
            seen.add(eid)
        for eid in charged - seen:  # charged edges with no baseline traffic still carry the toll
            e = net.getEdge(eid)
            ET.SubElement(iv, "edge", id=eid, traveltime=f"{e.getLength() / e.getSpeed() + rates.get(h, 0) / vot_s:.1f}")
    ET.ElementTree(w).write(outdir / "weights.xml")

    trips = outdir / "charged.trips.xml"
    with open(trips, "w") as f:
        f.write('<routes>\n  <vType id="car" vClass="passenger"/>\n')
        for vid, (dep, edges) in sorted(keep_charged.items(), key=lambda kv: kv[1][0]):
            f.write(f'  <trip id="{vid}" type="car" depart="{dep:.2f}" from="{edges[0]}" to="{edges[-1]}"/>\n')
        f.write('</routes>\n')
    rerouted = outdir / "charged.rou.xml"
    run([BIN / "duarouter", "-n", NET, "--route-files", trips, "-o", rerouted,
         "--weight-files", outdir / "weights.xml", "--weight-attribute", "traveltime",
         "--ignore-errors", "--no-warnings", "--no-step-log", "--seed", SEED])
    new = read_routes(rerouted)

    routes = outdir / "scenario.rou.xml"
    allv = {**keep_free, **{vid: new.get(vid, keep_charged[vid]) for vid in keep_charged}}
    with open(routes, "w") as f:
        f.write('<routes>\n  <vType id="car" vClass="passenger"/>\n')
        for vid, (dep, edges) in sorted(allv.items(), key=lambda kv: kv[1][0]):
            f.write(f'  <vehicle id="{vid}" type="car" depart="{dep:.2f}"><route edges="{" ".join(edges)}"/></vehicle>\n')
        f.write('</routes>\n')
    avoided = sum(1 for vid in keep_charged if vid in new and not charged.intersection(new[vid][1]))
    return routes, {"removed_offnetwork": len(removed), "retimed_to_shoulder": len(retimed),
                    "kept_chargeable": len(keep_charged), "rerouted_to_avoid_charge": avoided}


def charged_from_vehroutes(outdir, charged, rates, once_per):
    """Charge events from the simulated routes, priced at the hour the vehicle crossed."""
    n, revenue = 0, 0.0
    for _, el in ET.iterparse(outdir / "vehroutes.xml"):
        if el.tag == "vehicle":
            r = el.find("route")
            edges, exits = r.get("edges").split(), r.get("exitTimes", "").split()
            hits = [float(exits[i]) for i, e in enumerate(edges) if e in charged and i < len(exits)]
            if hits:
                times = hits[:1] if once_per in ("day", "trip") else hits
                n += 1
                revenue += sum(rates.get(hour_of(t), 0) for t in times)
            el.clear()
    return n, revenue


def network_metrics(outdir):
    trips = ET.parse(outdir / "tripinfo.xml").getroot().findall("tripinfo")
    dur = [float(t.get("duration")) for t in trips]
    dist = [float(t.get("routeLength")) for t in trips]
    return {"completed_trips": len(trips),
            "vehicle_hours": round(sum(dur) / 3600, 1),
            "vehicle_km": round(sum(dist) / 1000, 1),
            "mean_trip_min": round(sum(dur) / max(len(dur), 1) / 60, 2),
            "mean_speed_kmh": round((sum(dist) / 1000) / max(sum(dur) / 3600, 1e-9), 2),
            "teleports_note": "see SUMO log; teleport after 300 s of standstill"}


def main(selected):
    scen_all = yaml.safe_load((CONFIG / "scenarios.yaml").read_text())
    sim_cfg, scen = scen_all["simulation"], scen_all["scenarios"]
    a = load_assumptions()
    resp = response_for(sim_cfg["response_case"], a)
    net = sumolib.net.readNet(str(NET))
    cordon_inbound, xwy_entries = charged_edges(net, sim_cfg["cordon_for_area_charge"])
    print(f"cordon {sim_cfg['cordon_for_area_charge']} inbound edges: {len(cordon_inbound)}; "
          f"expressway entry edges: {len(xwy_entries)}")
    summary = {}
    names = [n for n in (selected or list(scen)) if n != "merge"]
    base = read_routes(BASE_ROUTES)
    if "S0" in names:
        print("S0: baseline")
        simulate("S0", BASE_ROUTES, sim_cfg)
        summary["S0"] = {"name": scen["S0"]["name"], **network_metrics(OUT / "S0")}
        (OUT / "S0" / "summary.json").write_text(json.dumps(summary["S0"], indent=1))
    for name in [n for n in names if n != "S0"]:
        cfg = scen[name]
        print(f"{name}: {cfg['name']}")
        charged = {"expressway_entries": xwy_entries,
                   "cordon_inbound": nyc_style_cordon(net, sim_cfg["cordon_for_area_charge"], cordon_inbound),
                   "cordon_and_expressway_entries": cordon_inbound | xwy_entries}[cfg["charges"]]
        rates = {int(k): v for k, v in cfg["rate_by_hour"].items()}
        b_charged, _ = charged_from_vehroutes(OUT / "S0", charged, rates, cfg["once_per"])
        routes, resp_counts = build_scenario_routes(name, cfg, sim_cfg, base, charged, resp, a, net)
        outdir = simulate(name, routes, sim_cfg)
        n, rev = charged_from_vehroutes(outdir, charged, rates, cfg["once_per"])
        summary[name] = {
            "name": cfg["name"], "label": cfg["label"],
            "cordon_id": None if cfg["charges"] == "expressway_entries" else sim_cfg["cordon_for_area_charge"],
            "n_cordon_inbound_edges": 0 if cfg["charges"] == "expressway_entries" else len(cordon_inbound),
            "n_expressway_points": len(xwy_entries),
            "baseline_chargeable": b_charged, "charged_vehicles": n, "charge_revenue": round(rev, 2),
            "response_case": sim_cfg["response_case"], **resp_counts, **network_metrics(outdir)}
        print("  ", {k: summary[name][k] for k in ("baseline_chargeable", "charged_vehicles",
                                                   "removed_offnetwork", "rerouted_to_avoid_charge")})
        (outdir / "summary.json").write_text(json.dumps(summary[name], indent=1))
    # Per-scenario summaries let S1-S3 run as parallel processes; merge whatever exists.
    merged = {n: json.loads((OUT / n / "summary.json").read_text())
              for n in scen if (OUT / n / "summary.json").exists()}
    (OUT / "summary.json").write_text(json.dumps(merged, indent=1))
    (OUT / "charged_edges.json").write_text(json.dumps(
        {"cordon_inbound": sorted(cordon_inbound), "expressway_entries": sorted(xwy_entries)}))


if __name__ == "__main__":
    main(sys.argv[1:])
