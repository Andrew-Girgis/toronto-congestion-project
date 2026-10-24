# Methodology

How each component works, in pipeline order. The rules behind every choice are in `AGENTS.md`.

## 1. Geometry: road network and candidate boundaries
- **Road centreline:** Toronto Centreline v2 (City Open Data), saved as a dated snapshot. It is used for boundary construction, crossing detection, road jurisdiction and joining counts.
- **Simulation network:** OpenStreetMap (Overpass, ODbL) for the study area (43.620–43.690 N, 79.432–79.327 W), converted with SUMO `netconvert`. OSM has the lane counts, turn restrictions and signals that Centreline lacks.
- **Candidate boundaries** (`config/cordons/candidates.yaml`): rings traced along Centreline features (streets, the Don River, the CP rail corridor) and closed through the harbour. Each zone is shrunk 20 m inward, so traffic travelling *along* a boundary street is outside the zone.
  - C1 Bathurst–Bloor–Parliament
  - C2 Bathurst–Bloor–Don River
  - C3 Dufferin–CP Rail–Don River
- **Crossings:** drivable Centreline segments that intersect the shrunken ring. Streets that dead-end against a railway or river don't count (the outside node must connect to another road). One documented exclusion: the Island Airport approach.

## 2. Observed traffic
- **Count coverage** (`cordon.observed.coverage`): a crossing counts as covered if a TMC or SVC count on the same street lies within 250 m. The nearest qualifying count, its date and distance are recorded. Expressways have no open City counts (the RESCU detector feed isn't published).
- **Calibration targets** (`cordon.demand.turncounts`):
  - Selection: the most recent TMC count per intersection in the base window (weekdays from 2023-01-01, excluding July, August and December), 06:00–10:00, hours with all four 15-minute slots. Cars and trucks are counted; buses are excluded.
  - Matching: each approach leg (N/E/S/W on Toronto's street grid, rotated about 17° from true north) and movement (left/through/right) is matched to a SUMO edge relation. Where divided roads split a junction, the leg total is used as an edge count instead.
  - About 20% of intersections are held out (fixed seed) for validation.
  - Assumption: counts from different days are combined as one "typical base-window weekday".

## 3. Baseline demand and simulation
- **Candidate routes:** SUMO `randomTrips` (fringe factor 20, minimum 400 m, validated).
- **Demand fitting:** SUMO `routeSampler` selects routes to match hourly turn and edge counts at calibration sites.
- **Simulation:** SUMO microsimulation from 06:00 to 10:00, plus one hour to clear. Teleport after 300 s of standstill. Outputs: hourly edge data, trip info, routes with exit times, and an 8% vehicle trace sample for the animation.
- **Validation:** simulated turning movements (from route exit times) are compared with held-out counts using GEH. Results are in `metrics.json` and the demo.

## 4. Behavioural response (aggregate)
- **Calibration:** the share of chargeable crossings removed at the reference price (NYC US$9 = C$12.58) is calibrated to observed results elsewhere, 15% base (10–22%). It is not estimated from Toronto data. A constant-elasticity curve D1 = D0((c0+p)/c0)^e (e = −0.5) carries that response to other prices, with c0 solved per case.
- **Response split:** removed trips divide into mode switch, destination change or cancellation, retiming and commercial trips not made, with shares from London and Stockholm. Rerouting is not taken from those shares: SUMO produces it.
- **Rerouting:** drivers who still face the charge are re-routed by `duarouter` on baseline hourly travel times plus the toll converted to time (C$24.99 per vehicle-hour). Other drivers keep their routes. This is a one-shot response, not an equilibrium.

## 5. Financial model
- **Collections:** charged trips from the simulation (06:00–10:00) are expanded to the charging day (AM share 38%, ASSUMPTION), then adjusted for once-per-day repeat entries, exemptions, the truck multiplier, ride-hail per-trip fees, collection loss and 250 charging days.
- **Costs:** capital = charging points × the City's 2015 toll-point cost (CPI-adjusted) + a central system. Operating cost is a falling share of collections. Two implementation years come before launch.
- **Reporting:** 2025 CAD real, 10 years, NPV at 7% (Treasury Board), 3.5% (Metrolinx) and 3%. Low/base/high pair traffic response with costs. Toll revenue is a transfer and is never added to time savings.

## 6. Labels
Every displayed value is OBSERVED, OBSERVED (REPORT), ESTIMATED, SIMULATED, ASSUMPTION or UNVERIFIED. Sources are in `research/sources.csv`.
