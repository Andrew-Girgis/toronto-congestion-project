import * as maplibregl from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import * as Plot from "@observablehq/plot";

maplibregl.setWorkerUrl(workerUrl); // bundlers must point MapLibre 6 at its worker

type Json = any;
const D = "/data/";
const get = async (f: string): Promise<Json> => {
  const r = await fetch(D + f);
  if (!r.ok) throw new Error(`${f}: ${r.status}`);
  return r.json();
};
const fmt = new Intl.NumberFormat("en-CA");
const pct = (x: number) => `${x > 0 ? "+" : ""}${(x * 100).toFixed(1)}%`;
const $ = (s: string) => document.querySelector(s) as HTMLElement;
const tag = (kind: string, text?: string) =>
  `<span class="tag ${kind}">${text ?? { obs: "observed", sim: "simulated", est: "estimated", asm: "assumption", unv: "unverified" }[kind]}</span>`;
const labelKind = (l: string) =>
  /UNVERIFIED/.test(l) ? "unv" : /OBSERVED/.test(l) ? "obs" : /ESTIMATED/.test(l) ? "est" : /SIMULATED/.test(l) ? "sim" : "asm";

const HEADLINE = "S4"; // NYC-style: cordon only, expressways free
let scenario = HEADLINE;
let mode = "change";
let metrics: Json, finance: Json, edges: Json, crossings: Json;

async function main() {
  [metrics, finance, edges, crossings] = await Promise.all([
    get("metrics.json"), get("finance.json"), get("edges.geojson"), get("crossings.geojson"),
  ]);
  const [cordons, counts, cases, nyc] = await Promise.all([get("cordons.geojson"), get("counts.geojson"), get("cases.json"), get("nyc_transit.json")]);
  minute(counts);
  cordonTable(cordons);
  scenarioButtons();
  buildMap(cordons, counts);
  diversion();
  sides();
  financeView(HEADLINE);
  transit(nyc);
  caseCards(cases);
  validation();
}

function S(id: string) { return metrics.scenarios[id]; }

function minute(counts: Json) {
  const c1 = crossings.features.filter((f: Json) => f.properties.cordon_id === metrics.cordon_id);
  const counted = c1.filter((f: Json) => f.properties.coverage === "counted 2023+").length;
  $("[data-bind=cover]").innerHTML = `${counted} of ${c1.length} <small>roads into downtown counted since 2023</small>`;
  $("[data-bind=nsites]").textContent = fmt.format(counts.features.length);
  const s2 = S(HEADLINE);
  if (s2) {
    $("[data-bind=s2drop]").innerHTML = `${pct(s2.charged_vehicles / s2.baseline_chargeable - 1)} <small>vehicles paying</small>`;
    const bl = s2.boundary_local_street_vkt_am / S("S0").boundary_local_street_vkt_am - 1;
    $("[data-bind=bl]").innerHTML = `${pct(bl)} <small>on boundary local streets</small>`;
    const f = finance.results.find((r: Json) => r.scenario === HEADLINE && r.case === "base");
    const lo = finance.results.find((r: Json) => r.scenario === HEADLINE && r.case === "low");
    const hi = finance.results.find((r: Json) => r.scenario === HEADLINE && r.case === "high");
    // Low/high pair traffic response with cost cases, so base can sit outside them; span all three.
    const g = [f, lo, hi].map((r: Json) => r.gross_per_year_cad_m);
    $("[data-bind=net]").innerHTML = `C$${Math.round(f.gross_per_year_cad_m)}M <small>(range ${Math.round(Math.min(...g))}–${Math.round(Math.max(...g))})</small>`;
  }
}

function cordonTable(cordons: Json) {
  const rows = cordons.features.map((f: Json) => {
    const p = f.properties;
    const xs = crossings.features.filter((x: Json) => x.properties.cordon_id === p.cordon_id);
    const major = xs.filter((x: Json) => /Arterial|Expressway/.test(x.properties.feature_code_desc));
    const counted = xs.filter((x: Json) => x.properties.coverage === "counted 2023+").length;
    const xwy = xs.filter((x: Json) => /Expressway/.test(x.properties.feature_code_desc)).length;
    return `<tr><td><b>${p.cordon_id}</b> ${p.name}${p.cordon_id === metrics.cordon_id ? " <span class=\"tag sim\">simulated</span>" : ""}</td>
      <td>${p.area_km2} km²</td><td>${xs.length} (${major.length} major)</td>
      <td>${(xs.length / p.area_km2).toFixed(1)}</td><td>${counted} of ${xs.length} (${Math.round(100 * counted / xs.length)}%)</td>
      <td>${xwy}</td><td class="muted">${p.rationale}</td></tr>`;
  });
  $("#cordon-table").innerHTML = `<tr><th>Boundary</th><th>Area</th><th>Road crossings</th><th>Crossings per km²</th><th>Counted since 2023</th><th>Expressway crossings (uncounted)</th><th>Why consider it</th></tr>${rows.join("")}`;
}

function scenarioButtons() {
  const box = $("#scenario-buttons");
  for (const id of ["S0", "S4", "S2", "S3", "S1"].filter((k) => metrics.scenarios[k])) {
    const b = document.createElement("button");
    b.textContent = id === "S0" ? "No charge" : `${id}: ${short(id)}`;
    b.dataset.s = id;
    b.setAttribute("aria-pressed", String(id === scenario));
    b.onclick = () => { scenario = id; box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); refresh(); diversion(); };
    box.appendChild(b);
  }
  document.querySelectorAll<HTMLButtonElement>("#mode-buttons button").forEach((b) => {
    b.onclick = () => {
      mode = b.dataset.mode!;
      document.querySelectorAll("#mode-buttons button").forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
      refresh();
    };
  });
}

function short(id: string) {
  return ({ S1: "Gardiner/DVP $3", S2: "Cordon + Gardiner/DVP", S3: "Cordon + Gardiner/DVP, cheaper shoulders", S4: "Cordon $12.58 (NYC-style)" } as Record<string, string>)[id] ?? id;
}

let map: maplibregl.Map;
let mapReady = false;

function buildMap(cordons: Json, counts: Json) {
  map = new maplibregl.Map({
    container: "map",
    style: "https://tiles.openfreemap.org/styles/positron",
    center: [-79.383, 43.656], zoom: 12.6, attributionControl: { compact: true },
    cooperativeGestures: true,
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-left");
  map.on("load", () => {
    map.addSource("edges", { type: "geojson", data: edges });
    map.addSource("cordons", { type: "geojson", data: cordons });
    map.addSource("crossings", { type: "geojson", data: crossings });
    map.addSource("counts", { type: "geojson", data: counts });
    map.addLayer({ id: "edges", type: "line", source: "edges", layout: { "line-cap": "round" }, paint: {} });
    map.addLayer({ id: "cordon-alt", type: "line", source: "cordons", filter: ["!=", ["get", "cordon_id"], metrics.cordon_id],
      paint: { "line-color": "#555", "line-width": 1.5, "line-dasharray": [2, 2] } });
    map.addLayer({ id: "cordon", type: "line", source: "cordons", filter: ["==", ["get", "cordon_id"], metrics.cordon_id],
      paint: { "line-color": "#c8102e", "line-width": 3 } });
    map.addLayer({ id: "counts", type: "circle", source: "counts",
      paint: { "circle-radius": 3, "circle-color": ["match", ["get", "split"], "holdout", "#a36400", "#1f7a4d"], "circle-opacity": 0.8 } });
    map.addLayer({ id: "crossings", type: "circle", source: "crossings", filter: ["==", ["get", "cordon_id"], metrics.cordon_id],
      paint: { "circle-radius": 6, "circle-stroke-width": 1.5, "circle-stroke-color": "#fff",
        "circle-color": ["match", ["get", "coverage"], "counted 2023+", "#1f7a4d", "counted before 2023 only", "#a36400",
          "expressway: no open City counts", "#b42318", "#6b6b6b"] } });
    const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });
    map.on("mousemove", "edges", (e) => {
      const p = e.features![0].properties as Json;
      const b = p.v_S0, v = p[`v_${scenario}`];
      const d = scenario === "S0" ? "" : `<br>${short(scenario)}: <b>${fmt.format(v)}</b> (${b ? pct(v / b - 1) : "n/a"})`;
      popup.setLngLat(e.lngLat).setHTML(`<b>${p.name || p.type}</b><br>No charge: ${fmt.format(b)} vehicles, 6–10 a.m.${d}<br>${tag("sim")}`).addTo(map);
    });
    map.on("mouseleave", "edges", () => popup.remove());
    mapReady = true;
    map.on("click", "crossings", (e) => {
      const p = e.features![0].properties as Json;
      new maplibregl.Popup().setLngLat(e.lngLat).setHTML(
        `<b>${p.linear_name_full}</b> (${p.feature_code_desc})<br>${p.coverage}<br>${p.last_count_date !== "NaT" ? "Last count: " + p.last_count_date : ""}<br>${p.jurisdiction}<br>${tag("obs", "observed coverage")}`).addTo(map);
    });
    refresh();
  });
}

function refresh() {
  if (!mapReady) return;
  const v = `v_${scenario}`;
  const coverage = mode === "coverage";
  map.setLayoutProperty("crossings", "visibility", coverage ? "visible" : "none");
  map.setLayoutProperty("counts", "visibility", coverage ? "visible" : "none");
  map.setLayoutProperty("cordon-alt", "visibility", coverage ? "visible" : "none");
  map.setLayoutProperty("edges", "visibility", coverage ? "none" : "visible");
  const width = ["interpolate", ["linear"], ["max", ["get", "v_S0"], ["get", v]], 50, 0.6, 1000, 2.2, 6000, 6];
  map.setFilter("edges", [">", ["max", ["get", "v_S0"], ["get", v]], 40]);
  if (mode === "change" && scenario !== "S0") {
    map.setPaintProperty("edges", "line-color", ["interpolate", ["linear"], ["-", ["get", v], ["get", "v_S0"]],
      -600, "#08306b", -200, "#2166ac", -60, "#d9dde2", 60, "#d9dde2", 200, "#d6604d", 600, "#67001f"]);
  } else {
    // Volume uses a neutral ramp so it can't be read as the blue "fewer vehicles" of the change view.
    map.setPaintProperty("edges", "line-color", ["interpolate", ["linear"], ["get", v],
      100, "#e3dccf", 1000, "#c4a77d", 3000, "#8a6a3b", 8000, "#3d2b14"]);
  }
  map.setPaintProperty("edges", "line-width", width as any);
  legend();
  const s = S(scenario);
  $("#scenario-note").innerHTML = scenario === "S0"
    ? `Baseline: trips fitted to City counts at ~80% of intersections (the other ~20% check it), routed by an equilibrium traffic model. ${tag("sim")}`
    : `${s.name}. ${s.label.replace(/\s*SIMULATED\.?/i, "")} ${tag("sim")}`;
}

function legend() {
  const el = $("#legend");
  if (mode === "coverage") {
    el.innerHTML = `<b>Can we count traffic into downtown?</b><br>
      <span style="color:#1f7a4d">●</span> crossing counted since 2023<br><span style="color:#a36400">●</span> counted before 2023 only<br>
      <span style="color:#b42318">●</span> expressway: no open City counts<br><span style="color:#6b6b6b">●</span> never counted<br>
      <span style="color:#c8102e">━</span> modelled boundary (C1) &nbsp;<span>┅</span> alternatives C2, C3<br>small dots: counted intersections (green = fit, amber = held out) ${tag("obs")}`;
  } else if (mode === "change" && scenario === "S0") {
    el.innerHTML = `<b>No charge: this is the comparison point.</b><br>Colours show traffic volume (darker = more). Pick a charge scenario to see what changes. ${tag("sim")}`;
  } else if (mode === "change" && scenario !== "S0") {
    el.innerHTML = `<b>Change in vehicles, 6–10 a.m.</b><br><span style="color:#2166ac">━</span> fewer &nbsp; <span style="color:#d6604d">━</span> more &nbsp; grey: within ±60 &nbsp; line width = traffic<br>${short(scenario)} vs no charge ${tag("sim")}`;
  } else {
    el.innerHTML = `<b>Vehicles, 6–10 a.m.</b><br>darker and wider = more traffic ${tag("sim")}`;
  }
}

function diversion() {
  const id = scenario === "S0" ? HEADLINE : scenario;
  const s = S(id), b = S("S0");
  if (!s) return;
  const blChange = s.boundary_local_street_vkt_am / b.boundary_local_street_vkt_am - 1;
  const reroute = s.rerouted_to_avoid_charge / Math.max(s.kept_chargeable, 1);
  const zoneSpeed = s.zone_street_speed_kmh / b.zone_street_speed_kmh - 1;
  const vht = s.vehicle_hours / b.vehicle_hours - 1;
  $("#diversion-cards").innerHTML = `
    <div class="card"><div class="stat">${pct(blChange)}</div><p>traffic (vehicle-km) on local and collector streets within 800 m outside the zone, ${short(id)} ${tag("sim")}</p></div>
    <div class="card"><div class="stat">${(reroute * 100).toFixed(0)}%</div><p>of drivers facing the charge who kept driving found a route around it (${fmt.format(s.rerouted_to_avoid_charge)} vehicles). London: 20–30% of removed trips diverted around the zone. ${tag("sim")}</p></div>
    <div class="card"><div class="stat">${pct(zoneSpeed)}</div><p>average speed on streets inside the zone (expressways excluded; ${fmt.format(b.zone_street_speed_kmh)} → ${fmt.format(s.zone_street_speed_kmh)} km/h). Zone traffic ${pct(s.zone_vkt_am / b.zone_vkt_am - 1)}; vehicle-hours across the whole study area ${pct(vht)}. ${tag("sim")}</p></div>
    ${S("S2") && S("S4") ? `<div class="card"><div class="stat">${pct(S("S2").zone_vkt_am / b.zone_vkt_am - 1)} vs ${pct(S("S4").zone_vkt_am / b.zone_vkt_am - 1)}</div><p><b>Lesson from New York: leave the bypass free.</b> Zone traffic with the Gardiner/DVP also charged (S2) vs cordon only (S4). Charging the expressways mostly pushes their traffic onto Lake Shore and side streets: study-area vehicle-hours ${pct(S("S2").vehicle_hours / b.vehicle_hours - 1)} vs ${pct(S("S4").vehicle_hours / b.vehicle_hours - 1)}. ${tag("sim")}</p></div>` : ""}`;
}

function sides() {
  const rows: Json[] = [];
  for (const id of ["S0", HEADLINE]) {
    const s = S(id);
    if (!s) continue;
    for (const [side, n] of Object.entries(s.cordon_inbound_by_side_am)) rows.push({ side, n, scen: id === "S0" ? "No charge" : "Cordon $12.58" });
  }
  $("#side-chart").replaceChildren(Plot.plot({
    height: 260, marginLeft: 60, x: { label: null }, y: { label: "vehicles 6–10 a.m.", grid: true }, fx: { label: null },
    color: { domain: ["No charge", "Cordon $12.58"], range: ["#7fa7c9", "#c8102e"], legend: true },
    marks: [Plot.barY(rows, { fx: "side", x: "scen", y: "n", fill: "scen", tip: true }), Plot.ruleY([0])],
  }));
}

function financeView(id: string) {
  const box = $("#fin-buttons");
  if (!box.childElementCount) {
    for (const s of ["S4", "S2", "S3", "S1"]) {
      const b = document.createElement("button");
      b.textContent = `${s}: ${short(s)}`;
      b.onclick = () => { box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); financeView(s); };
      b.setAttribute("aria-pressed", String(s === id));
      box.appendChild(b);
    }
  }
  const res = finance.results.filter((r: Json) => r.scenario === id);
  const byCase = Object.fromEntries(res.map((r: Json) => [r.case, r]));
  const years = byCase.base.cashflow.map((c: Json) => c.year);
  const band = years.map((y: number, i: number) => ({ year: y, lo: byCase.low.cashflow[i].cumulative_net, hi: byCase.high.cashflow[i].cumulative_net, base: byCase.base.cashflow[i].cumulative_net }));
  $("#cash-chart").replaceChildren(Plot.plot({
    height: 280, marginLeft: 60, x: { label: "year (negative = build years)", tickFormat: "d" }, y: { label: "cumulative net, C$M (2025)", grid: true },
    marks: [Plot.areaY(band, { x: "year", y1: "lo", y2: "hi", fill: "#a36400", fillOpacity: 0.18 }),
      Plot.lineY(band, { x: "year", y: "base", stroke: "#a36400", strokeWidth: 2.5, tip: true }), Plot.ruleY([0])],
  }));
  const row = (k: string, f: (r: Json) => string) => `<tr><th>${k}</th>${["low", "base", "high"].map((c) => `<td>${f(byCase[c])}</td>`).join("")}</tr>`;
  $("#fin-table").innerHTML = `<tr><th></th><th>Weaker traffic response, higher costs</th><th>Base</th><th>Stronger traffic response, lower costs</th></tr>
    ${row("Fewer charged trips (AM)", (r) => pct(-r.am_reduction_in_charged_traffic))}
    ${row("Gross collections / yr", (r) => `C$${r.gross_per_year_cad_m}M`)}
    ${row("Capital cost", (r) => `C$${r.capex_cad_m}M (${r.charging_points} points)`)}
    ${row("10-yr NPV of net cash @7%", (r) => `C$${fmt.format(r.npv_net_cad_m["0.07"])}M`)}
    ${row("…@3.5% (Metrolinx)", (r) => `C$${fmt.format(r.npv_net_cad_m["0.035"])}M`)}
    ${row("Cumulative cash positive", (r) => (r.payback_year ? `year ${r.payback_year}` : "not within 10 yrs"))}`;
}

function transit(nyc: Json) {
  const modes: Record<string, string> = { Subway: "Subway", Bus: "Bus", LIRR: "Long Island Rail Road", MNR: "Metro-North" };
  const bars = nyc.yearly_weekday.flatMap((r: Json) => [
    { mode: modes[r.mode], period: "2024 vs 2023 (before)", change: r.change_2024 * 100 },
    { mode: modes[r.mode], period: "2025 vs 2024 (charge in place)", change: r.change_2025 * 100 }]);
  $("#nyc-chart").replaceChildren(Plot.plot({
    height: 260, marginLeft: 44, x: { axis: null }, y: { label: "change in weekday riders (%)", grid: true }, fx: { label: null, domain: Object.values(modes) },
    color: { domain: ["2024 vs 2023 (before)", "2025 vs 2024 (charge in place)"], range: ["#b8b2a7", "#c8102e"], legend: true },
    marks: [Plot.barY(bars, { fx: "mode", x: "period", y: "change", fill: "period", tip: true }), Plot.ruleY([0])],
  }));
  const y = Object.fromEntries(nyc.yearly_weekday.map((r: Json) => [r.mode, r]));
  const e = nyc.zone_entries_weekday;
  $("#nyc-facts").innerHTML = `
    <li>Subway: ${pct(y.Subway.change_2025)} in 2025, after ${pct(y.Subway.change_2024)} the year before ${tag("obs")}</li>
    <li>Bus: ${pct(y.Bus.change_2025)} in 2025, after ${pct(y.Bus.change_2024)} the year before ${tag("obs")}</li>
    <li>Commuter rail grew <em>more slowly</em> than before (Long Island Rail Road ${pct(y.LIRR.change_2025)} vs ${pct(y.LIRR.change_2024)}) ${tag("obs")}</li>
    <li>Vehicles entering the zone: ${fmt.format(e[0].entries)} per weekday in 2025, ${fmt.format(e[e.length - 1].entries)} so far in 2026 ${tag("obs")}</li>`;
  const res = finance.results.filter((r: Json) => r.scenario === HEADLINE);
  const c = Object.fromEntries(res.map((r: Json) => [r.case, r]));
  const rng = (f: (t: Json) => number, pre = "", suf = "") => `<b>${pre}${fmt.format(f(c.base.transit))}${suf}</b><small class="muted">range ${pre}${fmt.format(f(c.low.transit))}–${fmt.format(f(c.high.transit))}${suf}</small>`;
  $("#transit-cards").innerHTML = `
    <div class="stat">${rng((t) => t.daily_new_transit_trips)}<small>new transit trips per weekday, both directions ${tag("est")}</small></div>
    <div class="stat">${rng((t) => t.am_new_transit_riders)}<small>new riders heading downtown, 6–10 a.m. ${tag("est")}</small></div>
    <div class="stat">${rng((t) => t.ttc_fares_cad_m, "C$", "M")}<small>extra TTC fares per year (City) ${tag("est")}</small></div>
    <div class="stat">${rng((t) => t.go_fares_cad_m, "C$", "M")}<small>extra GO fares per year (Metrolinx, provincial) ${tag("est")}</small></div>
    <p class="src">About ${Math.round(c.base.transit.share_of_removed_to_transit * 100)}% of drivers the charge takes off the road switch to transit (London 50–60%, Stockholm about 43%) ${tag("asm")}. The rest change destination, combine trips, travel outside charging hours or are commercial trips. Fares are small next to the charge itself (C$${c.base.gross_per_year_cad_m}M a year gross): the transit money comes mainly from how the charge revenue is spent.</p>`;
}

function caseCards(cases: Json) {
  const line = (x: Json) => `${x.text} ${tag(labelKind(x.label), x.label.split(" (")[0].toLowerCase())}<span class="src"> [${x.src}]</span>`;
  $("#case-cards").innerHTML = cases.cases.map((c: Json) => `
    <article class="card">
      <h3>${c.city} <span class="muted">${c.year}</span></h3>
      <p class="muted">${c.design}</p>
      <p><b>Traffic:</b> ${line(c.traffic)}</p>
      <p><b>Speed:</b> ${line(c.speed)}</p>
      <p><b>Money:</b> ${line(c.money)}</p>
      <p><b>Transit:</b> ${c.transit}</p>
      <p><b>Struggle:</b> ${c.struggle}</p>
      <p><b>Worked:</b> ${c.worked} <b>Didn't:</b> ${c.didnt}</p>
      <p class="callout"><b>For Toronto:</b> ${c.toronto}</p>
    </article>`).join("") + `<p class="src">${cases.note}</p>`;
}

function validation() {
  const v = metrics.validation;
  const h = v.holdout, c = v.calibration;
  $("#validation").innerHTML = `
    <p>We fitted the trips to counts at about 80% of intersections and kept the other 20% back as a test. Below: modelled vs counted vehicles entering each intersection, hour by hour.</p>
    <table><tr><th></th><th>Fitted sites</th><th>Held-out sites</th></tr>
      <tr><td>Intersection-hours within GEH 5</td><td>${(c.share_geh_lt5_intersection_hours * 100).toFixed(0)}%</td><td><b>${(h.share_geh_lt5_intersection_hours * 100).toFixed(0)}%</b></td></tr>
      <tr><td>Intersection-hours within GEH 10</td><td>${(c.share_geh_lt10_intersection_hours * 100).toFixed(0)}%</td><td>${(h.share_geh_lt10_intersection_hours * 100).toFixed(0)}%</td></tr>
      <tr><td>Approach-hours within GEH 5</td><td>${(c.share_geh_lt5_approaches * 100).toFixed(0)}%</td><td>${(h.share_geh_lt5_approaches * 100).toFixed(0)}%</td></tr>
      <tr><td>Vehicles counted vs simulated</td><td>${fmt.format(c.total_observed)} / ${fmt.format(c.total_simulated)}</td><td>${fmt.format(h.total_observed)} / ${fmt.format(h.total_simulated)}</td></tr>
      <tr><td>Correlation (approach volumes)</td><td>${c.r_approaches}</td><td>${h.r_approaches}</td></tr></table>
    <p class="callout warn"><b>Below the usual target.</b> Only ${(h.share_geh_lt5_approaches * 100).toFixed(0)}% of held-out approach-hours are within GEH 5 (common target: 85%), and the model carries ${(100 * h.total_simulated / h.total_observed).toFixed(0)}% of counted volume. Treat street-level numbers as indicative, not forecasts. Recalibrating on the City's internal data (expressway detectors, signal timings) is the first task of the pilot.</p>
    <p class="src">GEH is the standard statistic for comparing modelled and counted traffic. ${v.criterion} ${tag("sim", "simulated vs observed")}</p>`;
}

main().catch((e) => {
  console.error(e);
  document.querySelectorAll("[data-bind]").forEach((el) => (el.innerHTML = "<small>data not built yet</small>"));
});
