# AGENTS.md — Congestion Cordon

Guide for every agent and contributor working in this repo. Read it fully before starting work. `CLAUDE.md` imports this file; keep project guidance here, not there.

## 1. What this project is

**Congestion Cordon: Testing the case for congestion pricing in Toronto** is an open, evidence-based research and simulation tool. It asks whether, where and how congestion pricing could work in Toronto, using what New York, London, Stockholm and Singapore actually observed.

It does **not** assume pricing is beneficial, and it does **not** treat revenue maximisation as the goal. A finding that pricing would not work, or would work only under specific conditions, is a valid result.

**Context:** built for a Toronto civic buildathon. Built 2026-10-24, presented 2026-10-25. Built in one evening, so cut scope before compromising analytical quality.

**One-minute version (the councillor test):**
> Downtown Toronto traffic is slow, and the City's open data has no count of how many vehicles enter downtown each day. We built an open simulator on the City's own traffic counts. It shows what a downtown charge could do to traffic, travel times, nearby neighbourhoods and the City budget, and where it could backfire. It sits next to what actually happened in four cities that did it. **The ask:** first, Transportation Services runs a 90-day pilot of this tool on its internal data. Then, only if the evidence supports it, a staged path toward a time-limited pricing trial (Stockholm-style). Since June 2025 that needs an Act of the Ontario Legislature.

## 2. How we are judged and what "exceptional" means here

| Criterion | Weight | Exceptional (5/5) target | How we hit it | Evidence artifact |
|---|---|---|---|---|
| Impact on Toronto | 30 | Large/underserved group, clear before and after, evidence of the problem | Downtown commuters, transit riders, boundary neighbourhoods. Observed congestion from City counts. International before/after evidence. | `web/` map, `research/brief.md` |
| It works | 25 | End-to-end live demo on real/open data, usable today | City open data → DuckDB → SUMO calibrated to City counts → scenarios → Astro demo. Runs offline from saved snapshots. | `web/`, `docs/validation.md` |
| **Path to City adoption** | 20 | Owner, cost, data and privacy plan, a 90-day pilot the City could say yes to | Named owner and partners, costed pilot with labelled assumptions, privacy-by-design data plan, day-by-day 90-day plan with decision gates | `adoption/` |
| **User insight** | 15 | Grounded in data **and real user feedback gathered during the event** | Open-data findings plus a structured intercept protocol run at the event. Every quote and tally is real, dated and logged. Feedback visibly changed the product. | `research/user-feedback/` |
| **Clarity** | 10 | A non-technical councillor gets it in one minute | Landing view of problem → evidence → simulated effect → who is affected → the ask. Plain language, no jargon on the first screen, every number labelled. | `web/` landing, `README.md` |

Impact and It works are expected to score high if the demo runs on Toronto data. **Put extra care into Adoption, User insight and Clarity.**

### Adoption requirements (must all exist in `adoption/`)
- **Owner.** Proposed lead: City of Toronto **Transportation Services**, which runs the traffic count program behind our data. Partners: **City Planning** (Transportation Planning), **TTC** (transit capacity), **Data & Analytics/Technology Services** (hosting). For the policy itself, the **Province** must legislate. Since the *Plan to Protect Ontario Act (Budget Measures), 2025* (S.O. 2025 c.10, Sched. 2, Royal Assent June 2025), City of Toronto Act s.41 states the City "does not have the power to designate, operate or maintain a highway as a toll highway", and the s.116 regulation route that EX8.14 (2015) relied on is repealed (verified: ola.org Bill 24 explanatory note). The *Get It Done Act, 2024* bars tolls on provincial (Crown) highways unless an Act authorises them, and the Gardiner and DVP are scheduled to transfer to the Province in fall 2027 (research D-011, D-012). Whether a zone charge on City streets is a "toll highway" is a legal question: UNVERIFIED, so make no claim either way. Verify current division and unit names before presenting.
- **Both asks, tool first (agreed framing).** (1) **Now:** adopt this *tool* in a 90-day pilot. This is a low-cost, reversible decision within City authority. (2) **Then, conditional:** a staged roadmap toward a time-limited pricing trial modelled on Stockholm's 2006 trial → referendum → permanent sequence. It needs **provincial legislation** (a regulation is no longer enough). Its gates: the pilot's evidence passes, transit capacity is in place before launch, a revenue earmark is agreed, and a public vote or Council mandate. Never present (2) as something the City can approve alone.
- **Boundary cost driver (from user feedback, see `research/user-feedback/`).** The number of crossings a boundary must instrument drives capital/enforcement cost and leakage risk. Prefer natural choke points: the lake, the Don Valley crossings, rail corridors. Report crossings per candidate boundary.
- **Revenue use is a choice to show, not assume.** Present options with trade-offs: TTC bus priority/service, a transit capital backlog, electrification of above-ground transit (raised in feedback; check what Metrolinx GO Expansion already funds and whether UP Express/GO are provincial assets outside City control), and equity mitigation. Earmarking was decisive politically in London, Stockholm and NYC.
- **Cost.** Pilot cost as staff time plus hosting, every line a labelled ASSUMPTION with its basis. Policy implementation cost (capital/operating) comes from the financial model with ranges and international reasonableness checks.
- **Data and privacy plan.** The tool uses aggregate counts only: no licence plates, no individual trips, no personal information. Any future use of TTS microdata or enforcement/plate data is under MFIPPA with a Privacy Impact Assessment and a data-sharing agreement. State retention, access controls and an open-code/open-method commitment.
- **90-day pilot.** Days 0–30: deploy on City infrastructure, swap in current internal counts, recalibrate. Days 31–60: validate against held-out counts and City-held travel-time data, run cordon options. Days 61–90: publish the method and results, brief Council, go/no-go on a formal feasibility study. Each phase has deliverables, a decision gate and success metrics.

### User insight requirements
- **Never fabricate** quotes, interviews, survey responses, personas presented as real people, or counts of conversations.
- `research/user-feedback/protocol.md` holds a 3–5 minute intercept script (consent line, no names or contact details collected, about 6 questions: how they get downtown, what a charge would change, who they worry about, what would make it fair).
- `log.csv` holds one row per conversation: date, time, setting, respondent type (self-described), answers. No personal identifiers.
- `synthesis.md` records n, themes, direct quotes (with permission) and **what we changed because of it**.
- Data-derived segments (e.g. "suburban drivers with no direct transit alternative") are allowed if labelled as derived from data, not as interviewed people.
- Public evidence on acceptance (Stockholm referendum, published Toronto consultations) is secondary evidence, labelled as such.

**Collected so far** (details in `research/user-feedback/log.csv` and `synthesis.md`): n = 1 conversation at the event (2026-10-24) with an event participant who has policy/technology experience. The name is withheld pending consent. Each concern below maps to a product requirement:

| Feedback | Product requirement |
|---|---|
| Population growth could be miscalculated | Growth assumptions explicit, with low/base/high and sensitivity. Traffic does not scale one-for-one with population. |
| Where in Toronto, and when (what times)? | Candidate boundaries compared on a map; time-of-day scenario (S3); charging hours shown plainly |
| Area-based discrimination, e.g. commuters arriving from the west on the 401 | **Approach-direction burden view**: inbound crossings by approach side (west/north/east) against the transit alternatives available on each side. Ecological caveats apply. |
| Predict the money raised | 10-year financial model with ranges; gross vs net; the revenue–congestion trade-off |
| Singapore, London, NYC and Stockholm have done it | International panels |
| Their struggles (marketing/communications, implementation cost) and what worked or didn't | Lessons table per city: implementation cost, communications, legal/political fights, what worked, what didn't, what remains uncertain. **Not cut for time.** |
| Stockholm and NYC have clear choke points; in Toronto, drivers can leave major roads for neighbourhood streets | **Hypothesis to test, not assume**: the participant expects drivers to face "pay a small fee and arrive fast vs. take much longer and save". SUMO reroute outputs must show the actual diversion and travel-time penalty through boundary neighbourhoods. Boundary choice favours choke points. |
| Use revenue to electrify above-ground transit (GO, UP Express) instead of diesel | Revenue-use option, fact-checked for jurisdiction and existing funding |

More conversations would strengthen this criterion. Log each one the same way.

### Clarity requirements
- The first screen of the demo states the problem, the evidence, the simulated effect, who is affected and the ask, readable aloud in under 60 seconds.
- Plain-language labels ("cars entering downtown per morning", not "cordon entries, AM peak"). A glossary is available but not required.
- Every displayed value carries a tag: **OBSERVED**, **OBSERVED (REPORT)**, **ESTIMATED**, **SIMULATED**, **ASSUMPTION** or **UNVERIFIED**.
- Limitations are visible, not buried.

## 3. Non-negotiable rules

**Research integrity**
1. Do not fabricate observations, URLs, dataset IDs or verified-looking numbers. Mark unchecked claims **UNVERIFIED**. Clearly labelled synthetic inputs are allowed for demonstration.
2. Every consequential claim needs a source in `research/sources.csv`: URL, publication date, observation period, units, geography, intervention and limitations. Keep source-reported findings separate from our calculations.
3. Treat `data-sources.md` as unverified starting notes. Known problems are listed in §8.
4. Every Toronto assumption traces to a local dataset, a named case study, published research, or an explicitly labelled modelling assumption. Do not force a foreign analogy where local evidence exists.
5. Separate descriptive before/after changes from causal estimates. Name confounders: construction, weather, transit changes, the economy, pandemic recovery.
6. Do not infer an individual driver's income from neighbourhood averages without stating the ecological-inference limitation.
7. A missing dataset leads to reduced scope or a transparent fallback, never an unsupported estimate.

**Access and spending**
8. No dependency that needs discretionary third-party approval (institutional access, data-sharing agreements, vendor contact, manually approved accounts). Public downloads, open APIs and genuinely instant self-service accounts are fine; verify registration really is automatic first.
9. Free and open-source only. Do not buy anything, enable billable APIs, deploy publicly, or push to a remote without the user's explicit authorisation. Local commits are authorised.

**Secrets**
10. Never print or commit secrets. `.senv` is an encrypted store managed by `s`; inject with `s KEY -- <cmd>`. Never run `s get` or `s export`. Tell the user which environment variable to set and keep working on other tasks meanwhile.

## 4. Agreed design decisions (2026-10-24)

| Area | Decision |
|---|---|
| Repo | This folder, standalone, with its own GitHub repo (the user creates the remote). Not connected to any other project. |
| Frontend | **Astro** site in `web/`, with MapLibre GL JS 6 (ESM build, `maplibre-gl.mjs`) on the OpenFreeMap Positron basemap (no key; attribution required) and deck.gl TripsLayer for vehicle playback. Reads only precomputed files from `web/public/data/`; no live research APIs during the demo. |
| Pipeline | Python 3.14 in the project `.venv`, run via `uv`. DuckDB with the spatial extension loaded in every connection; Parquet for processed tables; GeoJSON for small web layers. H3 only where hexagons help the analysis. Tippecanoe only if a layer is too large for GeoJSON. |
| Simulation | **SUMO 1.28** (`eclipse-sumo` wheel). Mesoscopic simulation with signal-delay penalties (switched from microsimulation for runtime; full junction control deadlocked) of downtown plus about a 1.5 km buffer (includes the downtown Gardiner, DVP and Lake Shore), weekday 06:00–10:00. Demand is fitted to observed City counts with SUMO `routeSampler`; about 20% of count stations are held out and the fit is reported (GEH). AequilibraE 1.7.2 is installed but optional. MATSim is not used. |
| Behaviour | An aggregate response layer, parameterised from cited evidence, splits affected trips into: continue and pay, reroute, change departure time, switch mode, combine/cancel. Only "continue" and "reroute" stay on the SUMO network. Rerouting uses toll plus value-of-time route cost. Removed trips do **not** all go to transit. |
| Scenarios | Compared with the **same** no-pricing baseline: **S1** Gardiner/DVP $3 flat (a *partial*, labelled check against EX8.14 Table 7 and **not** a like-for-like replication, because the network only covers the expressways' downtown ends). **S2** Downtown cordon + Gardiner/DVP at about C$12.50 (NYC US$9 peak converted at a cited 2025 rate). **S3** Time-varying: C$12.50 at 07:00–09:00, C$6.25 for 06:00–07:00 and 09:00–10:00 (the shoulder rate is an ASSUMPTION). SUMO runs the base response only; low/base/high and rate sensitivity ($5–$20) come from the aggregate model. |
| Cordon boundary | Chosen from count coverage, crossing geometry and natural choke points (fewer crossings means lower enforcement cost and less leakage), with the reasoning documented. Record road jurisdiction (City vs provincial) and institutional requirements per option. |
| Future | SUMO simulates the calibrated base year only. The 10-year financial and scenario model compares with-pricing vs without-pricing futures under the same population, employment, remote-work and infrastructure assumptions. Traffic does not grow one-for-one with population. |
| Finance | 2025 CAD, real terms, 10-year horizon. Discount rate 7% real (Treasury Board of Canada CBA guide; verify citation) with 3% sensitivity. Gross collections = chargeable events after behavioural response × applicable rates (hours, vehicle classes, repeat crossings/caps, exemptions, taxi/ride-hail treatment, collection loss). Separate capex, opex, transit service, mitigation, net cash. Toll revenue is kept separate from social benefits, with no double counting. Show that stronger congestion reduction can lower revenue. **No foreign net-revenue-per-entry transfer.** |
| Equity | Context layers (2021 neighbourhood income, transit access) plus SIMULATED diversion exposure on boundary streets. Pembina/TTS findings are cited with caveats. No claims about who pays by home area, because there is no OD data. |
| International | City-level panels with zone outlines and report-sourced metrics (OBSERVED (REPORT)), plus NYC charts from data.ny.gov. **No street-level historical maps**: no case has open pre-launch street data. Singapore 1975 ALS and 1998 ERP are separate interventions. |
| Scope cuts, in order | 1) S3 time-varying run → 2) international panels shrink to the cross-case table **plus the lessons table** (the lessons table is never cut; users asked for it) → 3) animation becomes the link-change map only. |

## 5. Stack and environment status (verified 2026-10-24)

| Capability | Status | Notes |
|---|---|---|
| Project `.venv` (Python 3.14.7) | working | Has aequilibrae 1.7.2, geopandas 1.2, pandas 3.1, pyarrow, pyproj, shapely. Created with `python -m venv`; to be managed with `uv` and `pyproject.toml`. |
| `eclipse-sumo` 1.28, `duckdb`, `pdfplumber` | resolve for this venv | Not yet added. `routeSampler.py` ships in `$SUMO_HOME/tools`. |
| DuckDB CLI v2.0.0 (`~/.duckdb/cli/latest/duckdb`) | working | spatial + h3 load. Use `-no-agent` for readable output. |
| Java 21 (Homebrew `openjdk@21`) | installed, not on PATH | `/opt/homebrew/opt/openjdk@21/bin/java`. Only needed for MATSim, which we don't use. |
| Node 24, npm | working | For Astro. |
| Playwright MCP | working | Demo QA: rendering, controls, tooltips, console errors. |
| MapLibre MCP | working | Style validation and rendering; reports GL JS 6.15.0. |
| Context7 CLI (`npx ctx7@latest`) | working | Library docs. Use the CLI, not both routes. |
| Codex CLI 0.162.1 | configured, untested | `codex exec -m gpt-6-astra "..."` is available but uses subscription quota. The Claude plugin is not installed. |
| frontend-design plugin | not enabled here | Use `artifact-design` / `dataviz` guidance, or the user enables it with `/plugin`. |
| great_expectations (Python) | not installed | Not needed; use DuckDB/pandas assertions in `tests/`. |
| Tippecanoe | installed | Only if a layer exceeds about 10 MB. |

## 6. Repository structure

```
toronto-congestion-project/
├── AGENTS.md                 # this file (source of truth for agents)
├── CLAUDE.md                 # imports AGENTS.md
├── README.md                 # public overview
├── data-sources.md           # original starting notes; UNVERIFIED input (see §8)
├── pyproject.toml, uv.lock   # Python dependencies
├── Makefile                  # data / sim / model / web / check targets
├── config/
│   ├── scenarios.yaml        # S0–S3 definitions: rates, hours, boundary, response case
│   ├── assumptions.yaml      # every modelling assumption: value, low/high, source_id, label
│   └── cordons/              # candidate boundaries (GeoJSON) + rationale
├── data/                     # large files gitignored; manifests committed
│   ├── raw/<source_id>/<YYYY-MM-DD>/   # untouched downloads, dated snapshots
│   ├── processed/            # cleaned Parquet
│   └── manifest.csv          # source_id, url, retrieved_at, sha256, licence, notes
├── src/cordon/       # Python package, one module per component
│   ├── ingest/               # 1 geometry + 2 observed counts/demand (reproducible downloads)
│   ├── network/              # SUMO network build from Centreline/OSM
│   ├── demand/               # routeSampler calibration + holdout validation
│   ├── behaviour/            # 3 aggregate response model
│   ├── finance/              # 4 financial model (annual + cumulative cash flow)
│   └── export/               # 5 web-ready GeoJSON/JSON + labels
├── sim/                      # SUMO configs; outputs gitignored
├── research/
│   ├── sources.csv           # source register
│   ├── brief.md              # research brief + case and lessons tables
│   ├── cases/                # nyc, london, stockholm, singapore-als, singapore-erp
│   └── user-feedback/        # protocol.md, log.csv, synthesis.md
├── adoption/                 # owner.md, pilot-90-day.md, cost.md, data-privacy.md
├── docs/                     # access-audit.md, methodology.md, validation.md, gaps-and-next-steps.md
├── web/                      # Astro site; public/data/ holds precomputed, committed outputs
└── tests/                    # data checks + model invariants
```

The five components stay separate: (1) basemap/road geometry, (2) observed traffic and demand, (3) behavioural/scenario model, (4) financial model, (5) maps, charts and narrative. Downstream code reads upstream outputs from files, never by importing internal state.

## 7. Data and modelling conventions

**Acquisition**
- Discover through the CKAN API (`https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show?id=<id>`) and Socrata metadata (`https://data.ny.gov/api/views/<id>.json`).
- Download into dated snapshot folders and record each in `data/manifest.csv`. Never edit raw files.
- Toronto `datastore_search_sql` returns 403, so aggregate locally in DuckDB.
- Use CSV over JSON/XML for Toronto bulk files (5–7× smaller).

**Before combining counts**, check and record: year, season, weekday; interval and direction; vehicle class; duplicates and overlaps; missing boundary crossings; consistency between intersection (TMC) approach volumes, midblock (SVC) volumes and the boundary geometry. Never sum incompatible observations into a precise-looking daily total. Expansion from counted hours to a full day is a labelled ASSUMPTION.

**Known data facts**
- SVC summary has no direction field; the raw 15-minute rows do.
- Post-2020 directional volumes may sit in the speed files; verify.
- TMC counts typically cover 8 or 14 hours, with approach volumes by leg.
- Bluetooth travel times on the portal stop in 2017.
- No vehicle cordon count is on the portal; cordon datasets are bikes only.

**Modelling**
- Compare with-pricing vs without-pricing for the same year and assumptions.
- Use low/base/high plus sensitivity. Call these *illustrative scenario ranges*, not confidence intervals, unless they are statistically estimated.
- Never derive street-level speed changes mechanically from a citywide percentage; street-level effects come only from SUMO and are labelled SIMULATED.
- A SUMO forecast is credible only after the baseline reproduces held-out counts. Report GEH and the share of stations under GEH 5. If calibration fails, say so on screen.
- All parameters live in `config/*.yaml` with `source_id` and a label; none are hard-coded.

**Charging design facts to respect in the finance model**
- NYC charges passenger vehicles once per day but trucks per entry, and TLC taxis/FHVs per trip.
- Stockholm charges per passage with a daily cap.
- Singapore ERP charges per passage with no cap.
- Toronto ride-hail (PTC) data exists on the portal; use it for the taxi/ride-hail line.

## 8. Verified facts and corrections (do not reintroduce the errors)

| Claim in `data-sources.md` | Status | Use instead |
|---|---|---|
| NYC 2025 gross $716.5M / opex $138.1M / net ~$578M; "$1,100 net per daily entry" | **Not supported** | MTA CBDTP Financial Report, Dec 2025 YTD (preliminary, accrual), mta.info/document/197586 p.2: toll revenue **$700.5M**, expenses **$139.2M** (19.9%), net **$562.0M**. Never use a per-entry coefficient; MTA says entries data "should not be used for calculating revenue". |
| NYC 583k/day baseline vs 493k/day 2025 → -15% | **Invalid comparison** (MTA *estimated* January weekday vs all-days annual mean) | MTA-reported about 11–12% reduction |
| Toronto 2016 toll study, $3 toll, -9%/-12% vehicles | **Corrected** | EX8.14, 10 Sep 2015, p.13 Table 7: *modelled* AM-peak-hour **VKT** -9% Gardiner, -12% DVP; travel time -3/-5 min. https://www.toronto.ca/legdocs/mmis/2015/ex/bgrd/backgroundfile-83671.pdf |
| City can toll with a provincial regulation (s.41/s.116; EX8.14 2015, data-sources.md §2) | **Superseded (June 2025)** | s.41 re-enacted as an outright bar; s.116 repealed (Plan to Protect Ontario Act (Budget Measures), 2025, Sched. 2). Needs an Act of the Legislature. |
| London year one: vehicles -25%, cars -18% | **Swapped** | TfL Second Annual Report Table 3.1: 4+-wheel vehicles entering **-18%**, cars **-33%**. Congestion relief fell from 30% to 8% by 2006. |
| Singapore ALS speeds "<20 to 33 km/h"; "Chin (2010) SIM 33" | **Unsupported / misattributed** | Holland & Watson (1977): pre-launch speed data unusable; ALS -44% all vehicles / -73% cars for 07:30-10:15 only. SIM 33 is Menon & Guttikunda (2010). |
| "Every dataset verified" | Not accepted | See `docs/access-audit.md` |
| "Toronto lacks a published vehicle cordon baseline" | Supported for the open-data portal | Historical City Planning cordon reports still unchecked |
| "NY has more granular historical data" | Partly true | Rich post-launch microdata; no pre-launch entries microdata |
| 10–25% traffic drops as "elasticities" | Wrong framing | These are observed reductions at different price levels. A charge-response curve needs its own sources. |

## 9. Commands

All targets exist (see `Makefile`). Tests: `make check` (pytest, `tests/`).

```bash
uv sync                      # install Python deps into .venv
make data                    # download dated snapshots + manifest, build processed Parquet
make sim                     # build SUMO net, calibrate baseline, run S0–S3
make model                   # aggregate behaviour + financial model → outputs
make web                     # export web data, then: cd web && npm run dev
make check                   # data tests and model invariants (pytest)
make serve                   # demo at http://localhost:4321
```

DuckDB CLI: `~/.duckdb/cli/latest/duckdb -no-agent`. In Python: `con.load_extension("spatial")` in every connection.

## 10. Working with agents

- Prefer forks for research, since they inherit context. Fresh subagents and Codex (`codex exec`) start cold: pass the task, absolute file paths, these rules (§3) and the output file path. Have them write results to files, not chat.
- Research workstreams: A) Toronto baseline and coverage; B) international outcomes and implementation; C) equity and geography; D) growth, timing and behavioural parameters.
- Verify generated outputs yourself before reporting: open the file, check the numbers, render the map.
- Before the presentation, use Playwright on the demo: map renders, controls work, tooltips show labels, scenario numbers match the model output, no console errors.

## 11. Definition of done for the demo

1. Access/tools audit (`docs/access-audit.md`)
2. Plan and repo structure (this file + `README.md`)
3. Source register + research brief with case and lessons tables
4. Toronto baseline coverage assessment with reproducible ingestion
5. Vertical slice: acquired data → cleaned table → map/chart → documented finding
6. SUMO baseline calibrated and validated; S1–S3 simulated; aggregate and financial ranges
7. Adoption pack (owner, cost, data/privacy, 90-day pilot)
8. User feedback logged and synthesised, and visibly reflected in the demo
9. Gaps, validation status and next milestones (including future restricted-data integration: TTS iDRS, City internal counts, probe travel times)
