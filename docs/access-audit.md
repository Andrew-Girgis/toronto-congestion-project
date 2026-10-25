# Access / tools audit: Toronto congestion pricing buildathon

Checked 2026-10-24 using metadata APIs, HEAD requests and official pages only. Large files were not downloaded.
Sizes come from CKAN `size` fields. "ds" means the resource is also in the CKAN datastore and can be queried through `datastore_search`. Toronto `datastore_search_sql` returned 403, so the SQL endpoint is unavailable and aggregation has to happen locally.

## Summary table

| Resource | Purpose | Access type | Needed tonight? | Cost/billing | What user must do | Fallback |
|---|---|---|---|---|---|---|
| Toronto CKAN: Midblock Speed/Volume/Classification (SVC) | Directional midblock volumes, speeds and heavy-vehicle share at candidate boundary crossings | No authentication | **Yes, core** | Free | Nothing | TMC approach volumes |
| Toronto CKAN: Intersection TMC, all modes | Turning/approach volumes at signalized boundary intersections | No authentication | **Yes, core** | Free | Nothing | SVC only |
| Toronto CKAN: Traffic Signal Vehicle & Pedestrian Volumes | Legacy 8-peak-hour signal counts | No authentication | No: stale (2019 files), superseded by TMC | Free | Nothing | TMC |
| Toronto CKAN: Travel Times, Bluetooth | Corridor travel times | No authentication | No: **only 2014–2017 on the portal** | Free | Nothing | SVC spot speeds; King St pilot Bluetooth summary |
| Toronto CKAN: Toronto Centreline (TCL) v2 | Road geometry and the `centreline_id` join key | No authentication | **Yes, core** (gpkg 29.5 MB) | Free | Nothing | OSM via Overpass |
| Toronto CKAN: Neighbourhoods (158) + Neighbourhood Profiles 2021 | Equity geography, income and commute mode by neighbourhood | No authentication | Yes (equity layer) | Free | Nothing | StatCan Census Profile by CT |
| Toronto CKAN: Bicycle & Micromobility Cordon Count 2022 | Shows what a downtown cordon definition looks like; bikes only | No authentication | Optional (boundary reference) | Free | Nothing | n/a |
| Toronto CKAN: King St Transit Pilot family (7 datasets) | Local before/after evaluation template (2015 baseline counts, Bluetooth TT) | No authentication | Optional | Free | Nothing | n/a |
| Toronto CKAN: PTC (ride-hail) summary & trip sample | Ride-hail volumes, needed for taxi/ride-hail treatment in revenue | No authentication | Optional, high value for the financial model | Free | Nothing | NYC TLC share as a labelled assumption |
| Toronto CKAN: KSI collisions | Safety co-benefit context | No authentication | No | Free | Nothing | n/a |
| data.ny.gov: CRZ Vehicle Entries (t6yz-b64h) | NYC post-launch entries by class, crossing and 10 minutes | No authentication (Socrata app token optional) | Yes, if there is an NYC view | Free | Nothing | Aggregate `sayj-mze2` "CRZ Entries" |
| data.ny.gov: Daily Ridership & Traffic (sayj-mze2) | Daily transit + bridges/tunnels since 2020-03-01: a true before/after | No authentication | Yes (NYC view) | Free | Nothing | MTA press releases |
| data.ny.gov: CBD VMT (jbxx-kxff) | Monthly CBD VMT from 2024-01, a pre-launch baseline | No authentication | Optional | Free | Nothing | n/a |
| data.ny.gov: CBD Bus Speeds (r6db-kkzj) | Monthly route speeds from 2023-01, with CBD/non-CBD control | No authentication | Optional | Free | Nothing | n/a |
| data.ny.gov: CBD Geofence (srxy-5nxn) | Zone polygon | No authentication | Yes (map) | Free | Nothing | Hand-digitize 60th St |
| StatCan 2021 Census commuting tables (98-10-0459-01 CSD→CSD flows by gender; 98-10-0460-01 CMA flows by mode) + WDS API | Inter-municipal commute flows into Toronto; mode at CMA level only | No authentication | Yes (coarse demand proxy) | Free | Nothing | TTS PD-level summaries |
| StatCan CT-level OD by mode | Fine-grained OD | **Requires third-party approval (custom tabulation, paid), excluded tonight** | No | Paid custom tab | — | CSD flows + neighbourhood profiles |
| DMG TTS: open PD/ward summary CSVs (dmg.utoronto.ca/download-tts-data/) | Trip characteristics by planning district/ward, 1986–2022 | No authentication (no login wording on the page) | Optional (mode share and time-of-day by PD) | Free | Nothing | Census |
| DMG TTS: iDRS/DRS cross-tabs (OD by PD, income, mode) | Downtown car-trip OD and income | **Access conditions unverified, not a dependency** (register page gives no approval or eligibility terms) | No | Unknown | Optional: register later and report back if it is instant | TTS open summaries + Census; label OD as synthetic |
| UK DfT Road Traffic API (roadtraffic.dft.gov.uk/api) | London count-point AADF 2000–2025 (by direction available) | No authentication ("This API is not authenticated") | Optional | Free | Nothing | TfL report tables |
| London Datastore: CCZ camera captures by month | TfL's zone vehicle series | No authentication for the data.gov.uk CSV mirror; the London Datastore page says login is needed for "request access" | Optional | Free | Nothing | TfL reports |
| TfL Impacts Monitoring reports (PDF) | London 2002→2003 before/after tables | No authentication | Yes (London card) | Free | Nothing | US DOT ITS summary |
| data.gov.sg: Avg Daily Traffic Entering City (d_3136f317a1f282a33fe7a2f6a907c047) | Singapore annual cordon-entry series 2004–2025 | No authentication (datastore API works keyless) | Optional (SG chart) | Free | Nothing | Report figures |
| LTA DataMall API | Current SG speeds/ERP rates | **Access conditions unverified, not a dependency** (sources conflict between instant key and waitlist) | No | Free | Nothing | Not needed: current-state only |
| Transportstyrelsen congestion-tax statistics (HTML tables per year) | Stockholm monthly weekday passages 06:00–18:29 | No authentication | Optional | Free | Nothing | Report figures |
| Trafiklab | Swedish GTFS (current) | Instant self-service (email-verified account, sandbox key on signup), but irrelevant tonight | No | Free | Nothing | n/a |
| OpenFreeMap basemap (tiles.openfreemap.org/styles/positron returns 200) | Basemap for MapLibre | No authentication, no limits; attribution required | **Yes** | Free (donation-supported) | Nothing | Carto/OSM raster |
| Carto basemaps | Alternative basemap | No key; terms restrict commercial use without an enterprise licence (UNVERIFIED current terms) | No | Free non-commercial | Nothing | OpenFreeMap |
| OSM Overpass API | Fallback road/rail geometry | No authentication; fair-use limits | Fallback only | Free | Nothing | TCL |

## Per-dataset metadata notes

### Toronto CKAN (base: https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show?id=…)
CKAN reports the licence as "License not specified" on most packages. The portal's general terms are the Open Government Licence – Toronto. **UNVERIFIED per dataset**, so cite OGL-Toronto with that caveat.

**traffic-volumes-midblock-vehicle-speed-volume-and-classification-counts (SVC)**: refreshed daily, metadata modified 2026-10-24.
- `svc_summary_data` (ds): **45,039 counts**. Fields: count_id, count_type (e.g. ATR_SPEED_VOLUME), count_date_start/end, count_duration (hours, e.g. 72), location_name, lon/lat, centreline_id, avg_daily_vol, avg_weekday_daily_vol, avg_weekend_daily_vol, AM/PM peak start and volume, avg/85th/95th speed, avg_heavy_pct. **The summary has no direction field.** CSV is 8.3 MB; the most-recent-per-location summary is 2.7 MB.
- Raw volume rows are 15-minute with a **direction** field (EB/WB/…): id, count_id, location_name, lon, lat, centreline_id, time_start, time_end, direction, volume_15min.
- Raw file sizes: volume 1990–2019 is 45–384 MB per 5-year file, but **volume_2020_2024 is only 2.5 MB** while speed_2020_2024 is 350 MB and speed_2025_2029 is 133 MB. Post-2020 directional volumes probably sit mainly in the speed files (speed-bin counts per 15 minutes). **Verify during ingestion.** Classification raw: 0.4–23 MB per block. The data dictionary is an XLSX.
- Counts are short-term (typically 24–72 h) and ad hoc ("to support a variety of safety initiatives"), not a coordinated cordon program. Dates, seasons and years vary by location.

**traffic-volumes-at-intersections-for-all-modes (TMC)**: refreshed daily, modified 2026-10-23.
- `tmc_summary_data` (ds): **30,953 counts**. Fields include count_date, count_duration (e.g. "14"), location, lon/lat, centreline_id, px (signal id), total_vehicle/bike/pedestrian, total_heavy_pct, AM/PM peak, and **approach volumes by leg (n/e/s/w_appr_vehicle, _bike, _heavy_pct)**.
- Raw CSVs: 1980s 21 MB, 1990s 38 MB, 2000s 61 MB, 2010s 54 MB, 2020s 88 MB (JSON/XML are 5–7× larger, so use CSV).
- Approach volumes are vehicles entering the intersection from each leg. At a boundary intersection, the outside-leg approach gives a directional inbound proxy, but only for the counted hours (often 8 or 14 h, not 24 h). Full-day totals need expansion factors, which is a labelled assumption.

**traffic-signal-vehicle-and-pedestrian-volumes**: XLSX of 385 KB, last resource update 2019-07-23. It holds the "most recent 8 peak hour" counts per signal. Stale; do not use as a baseline.

**travel-times-bluetooth**: yearly ZIPs for 2014 (11 MB), 2015 (17 MB), 2016 (23 MB) and 2017 (1.8 MB, partial), plus routes in WGS84 (82 KB). Resources were last updated in 2019. **There is no current Bluetooth travel-time data on the portal.**

**bicycle-and-micromobility-cordon-count**: 2022 count. Raw data 2.7 MB, summary GeoJSON 200 KB. A 2010/2013/2014 bicycle cordon package also exists.

**King St Transit Pilot**: seven packages (2015 baseline counts, volumes summary 646 KB, detailed volumes, Bluetooth TT summary 154 KB, segments, detailed TT, disaggregate headway/TT). The pilot launched 2017-11-12, Bathurst→Jarvis.

**toronto-centreline-tcl**: v2, refreshed daily. gpkg 29.5 MB, GeoJSON 93 MB, SHP 118 MB, CSV 36 MB, in EPSG:4326 and 2952.

**neighbourhoods**: 158 neighbourhoods (GeoJSON 2.1 MB) and historical 140. **neighbourhood-profiles**: 2021 is 158-model XLSX (1.8 MB); 2016/2011/2006/2001 are 140-model.

**private-transportation-companies-summary-and-trip-data**: summary stats CSV 504 KB (from 2018-01-01) and a trip sample CSV of 1.3 MB.

**ttc-ridership-all-day-weekday-for-surface-routes**: XLSX of 20 KB, "will not be updated".

**Cordon hypothesis test**: CKAN searches for "cordon", "screenline", "cordon count", "central area" and "vehicle count" found **no vehicle cordon/screenline dataset**. The cordon hits are bicycle-only. The hypothesis "Toronto lacks a published vehicle cordon baseline" is **supported for the open-data portal**. Still unchecked: whether City Planning's historical "Central Area Cordon Count" reports are published as PDFs (UNVERIFIED; worth one search before claiming that no cordon count exists anywhere).

### data.ny.gov (Socrata; licence field empty on all five)
- **t6yz-b64h** CRZ Vehicle Entries: **6,749,136 rows, 2025-01-05 → 2026-10-17**. Posted weekly at 10-minute × detection_group × vehicle_class granularity. Columns include time_period, vehicle_class (1 Cars/Pickups/Vans, 2 Single-Unit Trucks, 3 Multi-Unit Trucks, 4 Buses, 5 Motorcycles, TLC Taxi/FHV), detection_group (12 crossings), detection_region, crz_entries and excluded_roadway_entries. **MTA disclaimer: "should not be used for calculating revenue… entries do not include information about exemption statuses, payment methods, and repeat entries."** It contains **no pre-launch rows**.
- **sayj-mze2** Daily Ridership & Traffic: daily from 2020-03-01 to 2026-10-22. Modes: Subway, Bus, LIRR, MNR, SIR, AAR, BT, plus CBD Entries and CRZ Entries, which start only on 2025-01-05.
- **jbxx-kxff** CBD VMT: 60 monthly rows, 2024-01 → 2026-06, areas CRZ/ER, daily_vmt_agps, daily_vmt_cvd and an indexed VMT. This gives a pre-launch baseline at **monthly, zone-aggregate** level.
- **r6db-kkzj** CBD Bus Speeds: 686,145 rows, 2023-01 → 2026-09, monthly × hour × route with a CBD/Non-CBD flag.
- **srxy-5nxn** Geofence: polygon, "Beginning June 2024".
- Hypothesis "NY has more accessible granular historical data": **partly true**. NY has the best open post-launch microdata and open monthly pre-launch series (VMT, bus speeds, ridership). It has **no pre-launch entries microdata**, so the entries before/after rests on MTA's estimated baseline.

### Census / TTS
- StatCan **98-10-0459-01**: commuting flows CSD of residence → CSD of work, by gender (no mode), released 2022-11-30. **98-10-0460-01**: CMA/CA flows by main mode, duration and gender. Search results disagree on which number is which, so **confirm the dimensions on the table page during ingestion**. No public CSD→CSD or CT→CT flow table by mode was found. Both tables are no-auth (CSV download and WDS API).
- What these support: the share of Toronto-workplace commuters living in each GTA municipality, and mode at metro level. What they cannot identify: downtown destinations (CSD = all of Toronto), car-driver trips to a cordon, time of day, or non-work trips.
- DMG/TTS: open CSV summaries by PD (and ward) for 1986–2022 with no login wording on the page. Cells with fewer than 4 observations are suppressed. iDRS/DRS ("Since May 2016, access to both systems has been combined") says only "If you do not have an account, please register", with no terms visible. **Access conditions unverified, not a dependency.**

### London
- DfT API: keyless; endpoints include `/api/average-annual-daily-flow-by-direction`, `/api/count-points` and `/api/raw-counts`. Count points have aadf_year up to 2025. Licence not visible on the docs page (OGL expected, UNVERIFIED).
- CCZ camera captures by month: captures **since July 2010**, confirmed vehicles since Oct 2016, charging hours only. Captures drop from Jan 2011 because the Western Extension was removed. **No 2003 before/after in open data**; that evidence exists only in the report tables.
- TfL PDFs, both live (HTTP 200): Second Annual Report, Apr 2004 https://content.tfl.gov.uk/impacts-monitoring-report-2.pdf ; Sixth Annual Report, Jul 2008 https://content.tfl.gov.uk/central-london-congestion-charging-impacts-monitoring-sixth-annual-report.pdf . The Sixth report's licence permits reproduction "for research, private study and internal circulation"; extracts may be reproduced with source.

### Singapore
- data.gov.sg `d_3136f317a1f282a33fe7a2f6a907c047`: keyless datastore API, **2004–2025** (22 rows), weekdays 07:30–19:00. Values: 246,000 (2004), 303,879 (2019), 238,262 (2020), 293,699 (2025). This post-dates ALS (1975) and ERP (1998), so it is a long-run trend series, not a before/after.
- LTA DataMall: key-request process unverified (an older README says instant; a 2025 data.gov.sg page mentions a waitlist for API keys and rate limits). Not needed.

### Stockholm
- Transportstyrelsen publishes one HTML page per year (e.g. …/trangselskatt-statistik/stockholm/statistik-2025/) with monthly passages, taxable passages and foreign-vehicle share. Weekdays only, 06:00–18:29; the 2018 page shows 06:30. Pages exist back to at least 2016. **There is no 2006 trial data.** Watch for the charging-hours change when comparing years.
- Trafiklab: free account (email verification), sandbox project and key created on signup. Current GTFS only, so irrelevant tonight.

### Basemaps
- OpenFreeMap: no key, no registration, no request limits. Attribution required: "OpenFreeMap © OpenMapTiles Data from OpenStreetMap". The style URL https://tiles.openfreemap.org/styles/positron returns 200. **Recommended.**

## Claim checks (data-sources.md)

**(a) NYC 2025 gross $716.5M / operating cost $138.1M: UNVERIFIED.**
- **Resolved later:** the primary MTA CBDTP Financial Report (Dec 2025 YTD, preliminary; mta.info/document/197586 p.2) gives toll revenue $700.5M, expenses $139.2M and net $562.0M (B-NYC-003, B-NYC-004). Those figures are used; $716.5M/$138.1M remain unsupported.
- No primary source found. The only official statement located is "over $550 million in net revenue in its first year", from the Governor/MTA first-anniversary release (mta.info press release "ICYMI: Less Traffic, Better Transit…", Jan 2026). Direct fetch returned 403, so the figure was confirmed via a search excerpt only.
- Tollroads News headline (2026-01-29): "MTA Nets $562 Million In 2025…" (headline only).
- Early-2025 expenses: Jan 2025 program expenses were $9.1M plus $2M mitigation (MTA press release).
- **Do not use $716.5M/$138.1M** or the derived 19% cost ratio and "$1,100 per daily entry" coefficient until an MTA financial document is located.
- The coefficient also divides revenue by entries from t6yz-b64h, which MTA explicitly says is not for revenue calculations.

**(b) MTA 583,000/day pre-launch baseline: PARTLY VERIFIED, definition matters.**
- It is MTA's *estimated* baseline for a **typical January weekday** (NY1/NBC, Jan 13 2025, reporting MTA's first-week data). It is not an observed annual all-days average.
- data-sources.md compares it with a 2025 **all-days** mean of about 493k. That mixes weekday with all-days and January with full-year, so the implied "-15%" is not a valid comparison. MTA's own headline reduction is about 11–12%.
- Reuters (via search) cites about 490k weekday entries plus about 63k on excluded roadways.

**(c) Toronto toll study: VERIFIED with corrections.**
- Source: City of Toronto Staff Report EX8.14, "Tolling Options for the Gardiner Expressway and Don Valley Parkway", **10 September 2015**, not 2016. https://www.toronto.ca/legdocs/mmis/2015/ex/bgrd/backgroundfile-83671.pdf
- Page 13, Table 7: a modelled **$3 flat toll** gives **AM-peak-hour VKT -9% (Gardiner) and -12% (DVP)**, and peak-direction end-to-end travel time 32→29 min (-3) and 34→29 min (-5).
- These are **travel-demand-model outputs, not observations**, and are AM-peak-hour VKT, not daily vehicles.
- The "$2 toll" in the Pembina reference relates to the 2016 Council proposal, which is a separate document (not checked).
- Same report, pp. 13–14: City of Toronto Act, 2006 **s.41** prohibits a City toll highway "until a regulation is made under section 116", so a provincial regulation is required. This is the institutional constraint for any Toronto proposal.
