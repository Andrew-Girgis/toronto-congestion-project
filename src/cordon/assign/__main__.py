"""Static user-equilibrium assignment of the counts-fitted demand, S0-S3 (component 3, network).

Usage: uv run python -m cordon.assign

Why static: SUMO mesoscopic runs of the same demand deadlocked at expressway-ramp junctions of
the OSM-built network, even at half demand, so their street-level results were not credible.
An equilibrium assignment with BPR volume-delay curves cannot gridlock, and every driver who
still faces the charge chooses a route on time + toll / value of time.

Steps, per hour 06-09:
  1. Demand: the routeSampler baseline routes (fitted to City counts). Trips whose fitted route
     never touches a charged link (cordon inbound or expressway entry) stay on that route as a
     fixed preload: re-routing them would only move traffic off the counted streets the routes
     were fitted to. Trips that do touch one form the route-choosing class (OD by nodes).
  2. S0: equilibrium-assign the route-choosing class on top of the preload; select-link analysis
     finds which of its trips use charged links (per scenario set).
  3. Scenario: remove the off-network share of those trips (calibrated response; S3 moves the
     retiming share from peak to shoulder hours), then re-assign with the toll as a fixed cost.
     Rerouting around the charge emerges from the assignment.

Outputs: sim/out/assign/links.parquet (edge, hour, scenario, flow, time) and
sim/out/summary.json + charged_edges.json (same schema the finance model and web export read).
"""

import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

import numpy as np
import pandas as pd
import sumo
import yaml
from aequilibrae.matrix import AequilibraeMatrix
from aequilibrae.paths import Graph, TrafficAssignment, TrafficClass

sys.path.append(str(sumo.SUMO_HOME) + "/tools")
import sumolib  # noqa: E402

from cordon import CONFIG, ROOT  # noqa: E402
from cordon.behaviour.response import load_assumptions, response_for  # noqa: E402
from cordon.sim.scenarios import charged_edges  # noqa: E402

NET = ROOT / "sim" / "net" / "study_area.net.xml.gz"
ROUTES = ROOT / "sim" / "demand" / "baseline.rou.xml"
OUT = ROOT / "sim" / "out"
HOURS = (6, 7, 8, 9)


def build_links(net, a):
    cap = a["assignment"]["capacity_veh_per_lane_hour"]["value"]
    sig = a["assignment"]["signal_delay_min"]["value"]
    nodes = {n.getID(): i + 1 for i, n in enumerate(net.getNodes())}
    rows = []
    for i, e in enumerate(net.getEdges()):
        t = e.getType().replace("highway.", "")
        ff = e.getLength() / e.getSpeed() / 60 + (sig if e.getToNode().getType() == "traffic_light" else 0)
        rows.append({"link_id": i + 1, "edge": e.getID(), "a_node": nodes[e.getFromNode().getID()],
                     "b_node": nodes[e.getToNode().getID()], "direction": 1,
                     "distance": e.getLength() / 1000, "free_flow_time": ff,
                     "capacity": e.getLaneNumber() * cap.get(t, 450),
                     "b": a["assignment"]["bpr_alpha"]["value"], "power": a["assignment"]["bpr_beta"]["value"]})
    return pd.DataFrame(rows), nodes


def hourly_demand(net, nodes, movable_edges):
    """Split the fitted routes by hour into a route-choosing OD class and a fixed edge preload.

    Returns ({hour: {(o, d): vehicles}}, {hour: {edge: vehicles}}, {hour: fixed trips})."""
    dem = {h: defaultdict(float) for h in HOURS}
    pre = {h: defaultdict(float) for h in HOURS}
    fixed = defaultdict(int)
    for _, el in ET.iterparse(ROUTES):
        if el.tag == "vehicle":
            edges = el.find("route").get("edges").split()
            h = int(float(el.get("depart")) // 3600)
            if h in dem:
                if movable_edges.intersection(edges):
                    o = nodes[net.getEdge(edges[0]).getFromNode().getID()]
                    d = nodes[net.getEdge(edges[-1]).getToNode().getID()]
                    dem[h][(o, d)] += 1
                else:
                    fixed[h] += 1
                    for e in edges:
                        pre[h][e] += 1
            el.clear()
    return dem, pre, fixed


def to_array(od, n):
    m = np.zeros((n, n))
    for (o, d), v in od.items():
        m[o - 1, d - 1] += v
    return m


def assign(links, arr, toll_by_link, select, a, preload):
    """One equilibrium assignment on top of a fixed preload (vehicles per link_id).

    Returns (total link flows incl. preload, congested times, {set: select-link OD total}, OD, rgap)."""
    net_df = links.assign(toll=links.link_id.map(toll_by_link).fillna(0.0))
    g = Graph()
    g.network = net_df
    g.mode = "c"
    centroids = np.arange(1, arr.shape[0] + 1, dtype=np.int64)
    g.prepare_graph(centroids, remove_dead_ends=False)
    g.set_graph("free_flow_time")
    g.set_skimming(["free_flow_time"])
    g.set_blocked_centroid_flows(False)

    m = AequilibraeMatrix()
    m.create_empty(zones=arr.shape[0], matrix_names=["car"], memory_only=True)
    m.index[:] = centroids
    m.matrix["car"][:, :] = arr
    m.computational_view(["car"])

    tc = TrafficClass("car", g, m)
    vot_min = a["value_of_time"]["sumo_vot_per_vehicle_hour"]["value"] / 60
    tc.set_fixed_cost("toll")
    tc.set_vot(vot_min)  # generalised cost (min) = time + toll / (C$ per minute)
    if select:
        tc.set_select_links({k: [(int(l), 1) for l in v] for k, v in select.items()})
    ta = TrafficAssignment()
    ta.add_class(tc)
    ta.set_vdf("BPR")
    ta.set_vdf_parameters({"alpha": "b", "beta": "power"})
    ta.set_capacity_field("capacity")
    ta.set_time_field("free_flow_time")
    pl = links.link_id.map(preload).fillna(0.0).values
    ta.add_preload(pd.DataFrame({"link_id": links.link_id, "direction": 1, "preload": pl}), "fitted_routes")
    ta.set_algorithm("bfw")
    ta.max_iter = a["assignment"]["max_iter"]["value"]
    ta.rgap_target = a["assignment"]["rgap_target"]["value"]
    ta.execute()
    res = ta.results()  # indexed by link_id
    flow = res["PCE_AB"].reindex(links.link_id).fillna(0).values  # total flow: class loads + preload
    time = res["Congested_Time_AB"].reindex(links.link_id).values
    sl = {k: float(np.nansum(tc.results.select_link_od.matrix[k])) for k in (select or {})}
    sl_od = {k: np.array(tc.results.select_link_od.matrix[k]).reshape(arr.shape) for k in (select or {})}
    return flow, time, sl, sl_od, ta.assignment.rgap


def main():
    a = load_assumptions()
    scen_all = yaml.safe_load((CONFIG / "scenarios.yaml").read_text())
    sim_cfg, scen = scen_all["simulation"], scen_all["scenarios"]
    resp = response_for(sim_cfg["response_case"], a)
    net = sumolib.net.readNet(str(NET))
    links, nodes = build_links(net, a)
    eid2link = dict(zip(links.edge, links.link_id))
    inbound, xwy = charged_edges(net, sim_cfg["cordon_for_area_charge"])
    sets = {"xwy": sorted(eid2link[e] for e in xwy),
            "cordon_xwy": sorted(eid2link[e] for e in inbound | xwy)}
    set_of = lambda cfg: "xwy" if cfg["charges"] == "expressway_entries" else "cordon_xwy"  # noqa: E731
    n = len(nodes)
    dem, pre_e, fixed = hourly_demand(net, nodes, inbound | xwy)
    pre = {h: {eid2link[e]: v for e, v in pre_e[h].items()} for h in HOURS}
    print(f"links {len(links)}, zones {n}, route-choosing trips {sum(sum(d.values()) for d in dem.values()):,.0f}, "
          f"fixed-route trips {sum(fixed.values()):,}")

    records, summary, base_sl_od, base_sl = [], {}, {}, {}
    arrays = {h: to_array(dem[h], n) for h in HOURS}
    for h in HOURS:
        flow, time, sl, sl_od, gap = assign(links, arrays[h], {}, sets, a, pre[h])
        base_sl_od[h], base_sl[h] = sl_od, sl
        records.append(pd.DataFrame({"edge": links.edge, "hour": h, "scenario": "S0", "flow": flow, "time_min": time}))
        print(f"S0 {h}:00 rgap={gap:.4f} trips={arrays[h].sum():,.0f} chargeable={sl}")
    summary["S0"] = {"name": scen["S0"]["name"], "trips": float(sum(arrays[h].sum() + fixed[h] for h in HOURS))}

    retime_share = resp.composition["retime_outside_charged_hours"]
    for name, cfg in scen.items():
        if name == "S0":
            continue
        k = set_of(cfg)
        rates = {int(h): v for h, v in cfg["rate_by_hour"].items()}
        shoulders = lambda h: [hh for hh, r in rates.items() if r < rates.get(h, 0)]  # noqa: E731
        adj = {h: arrays[h].copy() for h in HOURS}
        removed = retimed = 0.0
        for h in HOURS:
            off = base_sl_od[h][k] * resp.offnetwork_share(rates.get(h, 0))
            adj[h] -= off
            sh = shoulders(h)
            if sh:  # S3: part of the response is moving to a cheaper hour, not leaving
                moved = off * retime_share
                for hh in sh:
                    adj[hh] += moved / len(sh)
                retimed += moved.sum()
                removed += off.sum() - moved.sum()
            else:
                removed += off.sum()
        charged = rev = kept = 0.0
        for h in HOURS:
            toll = {l: rates.get(h, 0) for l in sets[k]}
            flow, time, sl, _, gap = assign(links, adj[h], toll, {k: sets[k]}, a, pre[h])
            charged += sl[k]
            rev += sl[k] * rates.get(h, 0)
            records.append(pd.DataFrame({"edge": links.edge, "hour": h, "scenario": name, "flow": flow, "time_min": time}))
            print(f"{name} {h}:00 rgap={gap:.4f} charged={sl[k]:,.0f}")
        b_charged = sum(base_sl[h][k] for h in HOURS)
        kept = b_charged - removed  # chargeable trips still travelling (including retimed)
        summary[name] = {
            "name": cfg["name"], "label": cfg["label"],
            "cordon_id": None if k == "xwy" else sim_cfg["cordon_for_area_charge"],
            "n_cordon_inbound_edges": 0 if k == "xwy" else len(inbound), "n_expressway_points": len(xwy),
            "baseline_chargeable": round(b_charged), "charged_vehicles": round(charged),
            "charge_revenue": round(rev, 2), "response_case": sim_cfg["response_case"],
            "removed_offnetwork": round(removed), "retimed_to_shoulder": round(retimed),
            "kept_chargeable": round(kept), "rerouted_to_avoid_charge": round(max(kept - charged, 0)),
            "trips": float(sum(adj[h].sum() + fixed[h] for h in HOURS))}
        print("  ", {x: summary[name][x] for x in ("baseline_chargeable", "charged_vehicles",
                                                    "removed_offnetwork", "rerouted_to_avoid_charge")})

    lk = pd.concat(records, ignore_index=True)
    length = dict(zip(links.edge, links.distance))
    lk["vkt"] = lk.flow * lk.edge.map(length)
    lk["vht"] = lk.flow * lk.time_min / 60
    for s, g in lk.groupby("scenario"):
        summary[s].update({"vehicle_km": round(g.vkt.sum()), "vehicle_hours": round(g.vht.sum()),
                           "mean_speed_kmh": round(g.vkt.sum() / g.vht.sum(), 1),
                           "mean_trip_min": round(g.vht.sum() * 60 / summary[s]["trips"], 1),
                           "method": "hourly static equilibrium assignment (AequilibraE BFW, BPR) of trips touching charged links, on top of fixed counts-fitted routes for all other trips"})
    (OUT / "assign").mkdir(parents=True, exist_ok=True)
    lk.to_parquet(OUT / "assign" / "links.parquet", index=False)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1))
    (OUT / "charged_edges.json").write_text(json.dumps(
        {"cordon_inbound": sorted(inbound), "expressway_entries": sorted(xwy)}))
    print(json.dumps({s: {k: v for k, v in d.items() if k in ("vehicle_hours", "mean_speed_kmh")} for s, d in summary.items()}))


if __name__ == "__main__":
    main()
