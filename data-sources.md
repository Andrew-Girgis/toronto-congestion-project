# Data sources for a Toronto congestion pricing analysis

> **Note (2026-10-25):** these are the original starting notes and are kept unedited as UNVERIFIED input. Several figures below were later corrected (NYC 2025 finances, the 583k baseline comparison, London year-one results, the Singapore sources, and the City's tolling power after June 2025). See AGENTS.md §8, `docs/access-audit.md` and `research/sources.csv` for the checked values.

Compiled 2026-10-23, updated 2026-10-24 (Stockholm and Singapore deep dives and a cross-case summary added as Sections 8 to 10). Every dataset below was verified against its official catalogue.
Dataset page pattern for Toronto: https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/<id>
Dataset page pattern for New York State: https://data.ny.gov/d/<id> (API: https://data.ny.gov/resource/<id>.json)

## 1. Toronto baseline: where the traffic actually is

**City of Toronto Open Data** (open.toronto.ca)

- **Traffic Volumes, Midblock Vehicle Speed, Volume and Classification Counts** (id: traffic-volumes-midblock-vehicle-speed-volume-and-classification-counts, CSV/JSON)
  Segment-level volumes AND speeds by vehicle class. This is your hotspot dataset: join volume against speed to find where delay concentrates.
- **Traffic Signal Vehicle and Pedestrian Volumes** (id: traffic-signal-vehicle-and-pedestrian-volumes)
  Turning movement counts at signalized intersections. Good for cordon entry points: count what crosses a candidate boundary street.
- **Traffic Volumes, Multimodal Intersection Turning Movement Counts** (id: traffic-volumes-at-intersections-for-all-modes)
- **Travel Times, Bluetooth** (id: travel-times-bluetooth, XLSX/ZIP)
  Corridor travel times from Bluetooth sensors. Your before/after speed metric, same role as NYC DOT speeds and TfL journey times.
- **Bicycle and Micromobility Cordon Count** (id: bicycle-and-micromobility-cordon-count, CSV/GeoJSON/SHP)
  Note the gap: Toronto publishes a downtown cordon count for bikes only. There is no published vehicle cordon count, so a Toronto proposal has to build cordon entries from the midblock and intersection counts above. NYC and London both anchored their evaluations on cordon entries.
- **Motor Vehicle Collisions, Killed or Seriously Injured** (id: motor-vehicle-collisions-involving-killed-or-seriously-injured-persons)
  For the safety co-benefit analysis (NYC tracked collision changes too).

**Toronto's own before/after precedent: the King Street Transit Pilot (2017)**
A full published evaluation dataset family on Toronto Open Data: traffic and pedestrian volume summaries and detail, Bluetooth travel time summary, segments (SHP/GeoJSON) and detail, plus 2015 baseline counts. Search "king" in the catalogue. This is the closest local template for how Toronto measures an intervention's traffic displacement and travel time effects.

## 2. GTA travel demand: who drives downtown, and what a charge would do

- **Transportation Tomorrow Survey (TTS), 2022 and 2016 waves**
  Data Management Group, University of Toronto (https://dmg.utoronto.ca, access via their iDRS retrieval system). The GTA's household travel survey (about a 5% sample): origin-destination flows by mode, time of day, purpose, and household income. This is the dataset you use to estimate how many downtown car trips a charge removes, which trips shift to transit, and who pays. Boundary/traffic zone files: https://mdl.library.utoronto.ca/collections/geospatial-data/transportation-tomorrow-survey-reports-and-boundary-files. Historical TTS data is also on the Ontario Data Catalogue (data.ontario.ca).
- **Statistics Canada, 2021 Census commuting tables**
  Commuting flows into downtown Toronto by mode and income at fine geography. Free, and the standard cross-check on TTS.
- **Existing Toronto analysis to build on**
  - Pembina Institute, "Fare Pricing" (2018): equity analysis of the City's 2016 proposed $2 toll on the DVP and Gardiner, built on TTS data. Finding: most affected commuters are above median income, but the burden share is higher for affected low-income households, so mitigation design matters. https://www.pembina.org/pub/fare-pricing
  - City of Toronto 2016 toll studies: a $3 flat toll on the Gardiner and DVP was estimated to cut vehicles on those highways by about 9% and 12% and save 3 to 5 minutes end to end. The province blocked the tolls in 2017, so any Toronto proposal needs provincial approval. That is a design constraint, not a footnote.
  - U of T School of Cities, municipal election issue brief on congestion pricing (2026): proposes a downtown zone modelled on London, Stockholm, Singapore and New York. https://schoolofcities.utoronto.ca/research-publications/municipal-election/

## 3. New York: Congestion Relief Zone (live since Jan 5, 2025)

Charge: $9 peak / $2.25 off-peak for cars with E-ZPass, once per day, Manhattan below 60th St.

**Raw data, NY State Open Data (data.ny.gov)**
- **MTA Congestion Relief Zone Vehicle Entries: Beginning 2025** (id: t6yz-b64h). The core dataset: entries by time, vehicle class, and detection point, before/after ready.
- **MTA Vehicle Miles Traveled in the Central Business District: Beginning 2024** (id: jbxx-kxff)
- **MTA Central Business District Bus Speeds: Beginning 2023** (id: r6db-kkzj)
- **MTA Daily Ridership and Traffic: Beginning 2020** (id: sayj-mze2). Transit side of the mode shift.
- **MTA Central Business District Geofence** (id: srxy-5nxn). The zone boundary as data, handy when you design a Toronto cordon.

**NYC Open Data (data.cityofnewyork.us)**
- **Automated Traffic Volume Counts** (id: 7ym2-wayt) and **DOT Traffic Speeds** (id: i4gi-tjb9). Street-level counts and speeds, including streets outside the zone for displacement checks.

**Independent tracking**
- **NYU C2SMART Manhattan Congestion Tracker**: https://c2smart.engineering.nyu.edu/manhattan-congestion-tracker/
  Camera-based multimodal density (cars, trucks, bikes, pedestrians) in zone vs buffer zone, updated regularly. A good model for an independent Toronto dashboard.

**Headline results (MTA first evaluation + NBER analysis)**
- Vehicle entries down about 11% in year one, roughly 27 million fewer entries.
- Speeds inside the zone up about 11% (NBER); early crossing travel times from New Jersey down 30 to 40%.
- PM2.5 inside the zone down about 13% (Columbia study).
- Net revenue over $550M in year one, funding a $15B transit capital program.

## 4. London: Congestion Charge (live since Feb 2003)

Charge: flat daily charge, currently £18 (2026), weekdays 7:00 to 18:00, central London zone.

**Evaluation reports (the gold standard to copy)**
- **TfL Impacts Monitoring reports, First to Sixth Annual (2004 to 2008)**. Search "Central London Congestion Charging Impacts Monitoring" on tfl.gov.uk. Key results:
  - Vehicles with four or more wheels entering the zone fell about 25% in year one, roughly 70,000 fewer per day; cars entering fell about 18%.
  - Congestion (excess delay) fell about 30% at first; speeds rose about 30%; trip times fell about 14%.
  - Five years on, entering traffic was still about 21% below pre-charge levels.
  - The cautionary finding: by 2008, delay had returned to roughly pre-charge levels even though volumes stayed down, because road space was reallocated and dug up for works. Lesson for Toronto: track volumes and delay as separate outcomes, and decide in advance who gets the freed road space.
  - Long run: cars entering the centre fell about 44% from 2002 to 2015 while total people entering rose about 23%.
  - US DOT summary of the TfL findings: https://www.itskrs.its.dot.gov/2011-b00762
- **Leape (2006), "The London Congestion Charge," Journal of Economic Perspectives**. The canonical academic write-up.

**Raw data**
- **UK Department for Transport, Road Traffic Statistics**: https://roadtraffic.dft.gov.uk/
  Street-level annual average daily flow by count point back to 2000, CSV/JSON plus an API. Use the London boroughs to reconstruct zone and boundary traffic over two decades.
- **London Datastore** (data.london.gov.uk): GLA open data, including travel demand survey material (London Travel Demand Survey) for mode share context.
- **TfL "Travel in London" annual reports**: mode share, traffic volumes and speeds trends for the whole city.

## 5. The analysis recipe (how the pieces fit)

1. **Hotspots**: Toronto midblock counts (volume vs speed) to map delay, then pick a candidate cordon (existing proposals use roughly south of Bloor, Bathurst to Parliament, plus the Gardiner/DVP question).
2. **Baseline cordon entries**: build them from Toronto intersection and midblock counts at boundary crossings, mirroring MTA's vehicle entries dataset.
3. **Effect sizes**: apply NYC and London elasticities as your range (entries down roughly 10 to 25%, speeds up roughly 10 to 30%), and sensitivity-test the charge level ($5, $10, $15) using TTS trip data.
4. **Before/after design**: difference-in-differences against control corridors outside the zone, exactly how NYC was evaluated, with boundary displacement checked the way TfL did.
5. **Mode shift capacity**: TTC and GO ridership headroom from census and TTS mode shares, since 50 to 60% of London's removed car trips shifted to transit.
6. **Equity and revenue**: TTS income distribution of affected drivers (Pembina's method), revenue at MTA-style net figures, and mitigation design (discounts, exemptions) costed against it.

## Optional fourth case

Covered in full below: Stockholm is Section 8 and Singapore is Section 9, with the cross-case summary in Section 10.

## 6. Before/after raw data and the revenue math (added 2026-10-23)

**Does the same kind of traffic-level data exist for NYC and London?**

New York, yes, in full raw form (all on data.ny.gov, checked live 2026-10-23):
- **Congestion Relief Zone Vehicle Entries (t6yz-b64h)**: 6.7M rows at 10-minute granularity, by vehicle class and detection point, with CRZ entries vs excluded-roadway entries. Starts on launch day (2025-01-05), so the "before" period comes from the two datasets below plus the MTA's published 2024 baseline of about 583,000 entries/day.
- **MTA Daily Ridership and Traffic (sayj-mze2)**: daily subway, bus, commuter rail and bridge/tunnel traffic back to 2020. True before/after for both transit ridership and crossing volumes.
- **MTA CBD Bus Speeds (r6db-kkzj)**: monthly by route from 2023, flagged CBD vs Non-CBD. Before/after speeds with a built-in control group.
- NYC Open Data adds street-level counts (7ym2-wayt) and DOT speeds (i4gi-tjb9) for displacement checks.

London, yes but more scattered:
- **London Datastore: "Traffic Flows, Borough"** (annual flows by borough), **"Camera Captures and Confirmed Vehicles seen in the Congestion Charge Zone by Month"** (TfL's own monthly vehicle series for the zone), **"Public Transport Journeys by Type of Transport"** (ridership series), **"Bus Use and Supply Data 1999-2022"**.
- **DfT Road Traffic Statistics** (roadtraffic.dft.gov.uk): street-level AADF by count point back to 2000.
- The clean 2002 vs 2003 before/after numbers live in the tables of TfL's Impacts Monitoring reports rather than one tidy raw file. London launched in 2003, before the open data era, so the evaluation is report-based.

**The revenue math, calibrated on real outcomes**

New York, calendar 2025: gross revenue $716.5M, operating cost $138.1M (about 19%), net about $578M, on roughly 520,000 entries/day after an 11% drop. That works out to about $3 of net revenue per entry, far below the $9 headline toll, because of tunnel crossing credits, the $2.25 overnight rate, per-trip taxi/FHV fees, exemptions and discounts. Lesson: never estimate Toronto revenue as entries × toll. Use a realized net-per-entry coefficient (NYC: net ≈ daily entries × about $1,100 per year).

London: net revenue is reinvested in transport by law. TfL 2017/18: gross £229.8M, operating cost £57.7M (25%), net £155.9M. Early years were far worse (2006/07 operating cost £130M on £252M gross, net £89M) because of older tolling tech, another argument for using NYC's cost ratio, not London's early one. Gross revenue over London's first 15 years was about £2.5B. The 2024/25 gross was £202.8M at the £15 rate; the £18 rate from January 2026 projects to over £243M.

Illustrative Toronto scenarios at a $10 charge, 15% entry drop, NYC-realized net coefficient (about $1,100 per daily entry per year, applied to post-drop entries):
- 200,000 entries/day before, 170,000 after: net roughly $190M/year
- 300,000 before, 255,000 after: net roughly $280M/year
- 500,000 before, 425,000 after: net roughly $470M/year
The one input these scenarios need is Toronto's real baseline: daily vehicle entries into a candidate zone, which has to be built from the city's boundary intersection and midblock counts (Section 1). NYC's zone had about 583,000 entries/day before charging.

**Transit: did the money and the riders show up?**

New York:
- The revenue is bonded: it unlocked $15B for the MTA 2020-2024 capital plan. In 2025 alone, over $5B of congestion-funded projects were committed: 435 new R211 subway cars, CBTC signal upgrades on the A and C lines, accessibility upgrades at 23 stations (about $2B), Second Avenue Subway Phase 2 tunneling, 300 M9A railcars, 44 new locomotives. Stations carry signage crediting congestion pricing.
- Ridership (Jan to May 2025 vs same period 2024): subway +7%, bus +12%, LIRR +8%, Metro-North +6%, paratransit +21%. Bus speeds inside the zone +3.2% on average, up to +25% on some routes.

London:
- 100% of net revenue must by law be spent on London transport. Early spending leaned heavily on buses: TfL added about 300 buses on launch day, plus bus priority measures.
- Bus passengers entering the zone in the morning peak rose by about 29,000 in year one; bus passenger numbers rose about 18% in year one and 12% in year two; rush-hour bus passengers entering the zone rose roughly 37 to 40%. Bus excess waiting time (unreliability) fell about 30% in year one.
- Of the car trips removed, TfL estimated 50 to 60% shifted to transit (see Section 4).

Toronto read: the pattern in both cities is (1) charge revenue is legally fenced for transit capital, (2) buses are the fastest visible win because they use the freed road space immediately, and (3) ridership gains show up within the first year. For the TTC, the direct analogues are bus speed/reliability gains on downtown routes and a dedicated capital stream against the state-of-good-repair backlog.

## 7. Computed from the raw NYC files (checked 2026-10-23, data.ny.gov Socrata API)

**Transit ridership, full year before vs full year after (sayj-mze2, weekday daily averages):**

| Mode | 2024 (before) | 2025 (after) | Change |
|---|---|---|---|
| Subway | 3,262,847 | 3,513,606 | +7.7% |
| Bus | 1,117,144 | 1,202,142 | +7.6% |
| LIRR | 204,505 | 223,124 | +9.1% |
| Metro-North | 178,337 | 190,241 | +6.7% |
| Bridges and Tunnels traffic | 928,310 | 932,457 | +0.4% |

Caveats: these are observed year-over-year changes, not a causal estimate; part of the ridership growth is the continuing post-2020 recovery trend. Bridge/tunnel traffic covers all MTA crossings region-wide (some outside the zone), so it is not the zone-entry measure; MTA's own reported figure for entries into the zone is an 11% drop in year one.

**Zone entries composition (t6yz-b64h, Jan 5 to Dec 31, 2025):**
- Average daily entries, all days: about 493,000 (178.2M total over 361 days). Peak-period entries (weekday 5am-9pm, weekend 9am-9pm) were 76.5% of the total; overnight entries 23.5%, charged at the $2.25 rate.
- Vehicle class mix: cars/pickups/vans 56.9%, TLC taxis and for-hire vehicles 37.3% (66.4M entries, billed per trip rather than by daily charge), single/multi-unit trucks 3.9%, buses 1.6%, motorcycles 0.4%.
- Two things this explains: the $3 net revenue per entry (overnight entries pay a quarter of the rate, and more than a third of entries are taxis on a separate per-trip schedule) and why buses, not cars, show the fastest service improvement.

Toronto modelling notes from this: expect a large ride-hail/taxi share inside any downtown zone, and separate the taxi treatment from the car toll in the revenue model. The overnight rate share tells you how much of Toronto's entry volume sits in reduced-rate hours. Still missing: Toronto's baseline daily entries into a candidate zone, built from the boundary counts in Section 1.

## 8. Stockholm: congestion tax (trial 2006, permanent 2007)

Researched 2026-10-24. Sources: Transportstyrelsen (official rates page), Eliasson et al. (2009), Börjesson & Kristoffersson (2018), ITF/OECD (2018).

**Design.** A national tax (the Riksdag legislates it, Transportstyrelsen collects), not a city fee, which matters for Toronto: senior-government legislation was required. Single cordon around the inner city, about 30 km², 18 control points, charged in both directions. Sequence: trial 3 January to 31 July 2006, referendum 17 September 2006, permanent from 1 August 2007. The referendum passed inside the city with a yes vote reported between 51% and 53% depending on the tally, while most surrounding municipalities voted no. Trial rates: SEK 10 to 20 per passage by time of day, daily cap SEK 60. Current rates: SEK 11 to 45 per passage in peak season, daily cap SEK 135. The one free bypass, the Essingeleden, was brought into the scheme in 2016.

**Findings.**
- Cordon crossings during charged hours fell **22%** in the trial, about 100,000 fewer passages per day (Eliasson et al. 2009). When the trial ended and charges stopped, traffic almost returned to previous volumes, then fell again when the tax returned. That on-off-on pattern is the cleanest causal evidence in the whole congestion pricing literature.
- Long run: the reduction stabilised at about **20%** and held for a decade despite population, income and car ownership growth (Börjesson & Kristoffersson 2018).
- Delay on arterials fell by about a third in the morning peak and half in the afternoon peak; queuing time and travel time variability fell 30 to 50% on bottleneck links.
- Displacement was small: traffic on the free Essinge bypass rose only **0 to 4%**; the Southern Link rose about 10%, much of it background growth.

**Revenue and where it goes.** Trial revenue was about SEK 399 million in under 7 months. Annual revenue (ITF/OECD, from Transportstyrelsen): 70.9 million euros in 2008, 91.4 million in 2015, 140 million in 2016 after the rate rise and the Essingeleden addition. The operating cost share collapsed as the system matured: **31% of revenue in 2008, 12% in 2013, 7% in 2016**. The earmarking history is the political lesson: revenue was first planned for public transport, flipped entirely to road construction in October 2006, then earmarked in the 2007 agreement to the Stockholm Bypass, with the 2016 increase directed in part to the Metro extension. It has never gone to general revenue, and the ITF credits the revenue deal as the turning point that won over local politicians.

**Transit.** Service was expanded before charging began: from August 2005, 16 new bus lines and about **7% more SL service**, plus park-and-ride capacity up 29%. Measured public transport trips across the cordon rose 6 to 7% during the trial; netting out a pre-existing trend, about **4 to 5% is attributable to the charges** (Börjesson et al. 2012). Of the roughly 45,000 work and school car trips priced off the cordon per day, about 43,000 switched to public transport. The bus expansion alone explained at most 0.1 percentage points of the 22% traffic drop: the charge did the work, the extra capacity absorbed it.

**Open data: strong today, nothing for 2006.** Trafiklab (Samtrafiken) publishes GTFS, GTFS-Realtime and NeTEx service data for all Swedish transit including SL, and Trafikverket runs an open traffic information API, but both are current-state only. The KoDa historical GTFS archive starts around 2019. SL ridership is not published as an open dataset, and Stockholm's open data portal launched in 2011. Transportstyrelsen publishes monthly congestion tax statistics (passages and tax decisions), though the series start date could not be confirmed. Verdict: the 2006 before/after evidence exists only inside the evaluation reports listed below, not as downloadable data.

**Key reports.**
- City of Stockholm (2006), "Facts and Results of the Stockholm Trials," the official trial evaluation.
- Eliasson, Hultkrantz, Nerhagen & Rosqvist (2009), "The Stockholm congestion-charging trial 2006: Overview of effects," Transportation Research Part A 43, 240-250.
- Eliasson (2009), "A cost-benefit analysis of the Stockholm congestion charging system," Transportation Research Part A 43, 468-480 (net social surplus about SEK 683 million per year).
- Börjesson & Kristoffersson (2018), "The Swedish congestion charges: Ten years on," Transportation Research Part A 107, 35-51.
- Börjesson et al. (2018), "Long-term effects of the Swedish congestion charges," OECD/ITF Discussion Paper (source of the revenue and operating cost table).
- Rates and rules: https://www.transportstyrelsen.se/en/road/vehicles/taxes-and-fees/road-tolls/congestion-taxes-in-stockholm-and-gothenburg/congestion-tax-in-stockholm/hours-and-amounts-in-stockholm/

## 9. Singapore: Area Licensing Scheme (1975) and Electronic Road Pricing (1998)

Researched 2026-10-24. Sources: National Library Board Singapore (ALS history), LTA and LTA DataMall, Phang & Toh (2004), Menon & Chin (2004), Olszewski (1999), Chin (2010).

**Design.** The world's first congestion pricing: the Area Licensing Scheme launched 2 June 1975, a paper licence (S$3 per day) to enter a 670 hectare Restricted Zone (later 720 ha) in the morning peak, extended over the years to the full working day. Electronic Road Pricing replaced it in 1998 (first gantries 1 April 1998, full Restricted Zone operation by September 1998). ERP is the opposite design from Stockholm and New York in one key way: **per passage, per gantry, with no daily cap**, rates varying in 30-minute slices by vehicle class. Rates are reviewed quarterly against published speed targets (45 to 65 km/h on expressways, 20 to 30 km/h on arterials and in the zone) and adjusted in small steps, which has kept rate changes technocratic and uncontroversial. ERP 2.0, a satellite (GNSS) system, becomes fully effective 1 January 2027; distance-based charging is possible but not planned for now.

**Findings.**
- ALS: total vehicles entering the zone fell **44%** (74,000 to 41,500 per day, March to October 1975), and cars fell about **73%**. Zone speeds rose from under 20 km/h to about 33 km/h. Displacement is well documented: traffic bunched into the shoulder periods just outside charging hours and onto bypass routes (Phang & Toh 2004). Toronto lesson: price the shoulders and the obvious bypasses from day one.
- ERP vs ALS: traffic fell a **further 10 to 15%**, and 15% daily / 16% in the morning peak after one year, even though ERP prices per trip (S$0.50 to 2.50) were lower than the ALS day licence. The mechanism matters for Toronto: about 23% of ALS-era trips were repeat entries on one day licence, and per-passage pricing priced each of them. **Per-passage beats a day pass.**
- Initial expressway effect: volumes down 15%, speeds up from 35 to 55 km/h in charged hours (Chin 2010).
- Long run, ERP manages volumes against growth rather than shrinking them: the city-entry traffic series (below) rises from 246,000 per day in 2004 to about 300,000 in 2011 and flattens after, while LTA holds priced points inside the speed bands by adjusting rates.

**Revenue and where it goes, with a warning.** ERP revenue was about S$80 million per year gross with about S$16 million operating cost (roughly 20%) around 2003 (Menon & Chin 2004), and S$160 million (2013) and S$152 million (2014) in later budget analysis; no official ERP-only figure after 2014 could be verified. Critically, **ERP revenue is not ring-fenced**: it goes to the government Consolidated Fund. And the big fiscal instrument is separate: the Certificate of Entitlement (COE) vehicle quota, an auctioned 10-year right to own a car, raises S$2.3 to 4.7 billion per year, roughly 25 times ERP revenue. Do not cite Singapore as a transit funding model, and do not conflate COE money with congestion pricing money.

**Transit: handle with care.** The one-year ERP evaluation found **no significant modal shift** (Olszewski 1999): drivers cut repeat trips, retimed and rerouted instead of switching. The ALS-era shift was real but came bundled with park-and-ride and bus measures (car pools up 35% at launch; a secondary figure has transit's share of zone work trips rising from 33% before the ALS to about 70% by 1983). Long-run ridership grew strongly, from 4.17 million trips per day in 2005 to 7.69 million in 2019 and 7.46 million in 2024, but that is driven by rail expansion, bus contracting, population growth and the COE ownership cap, not attributable to ERP alone. Peak transit mode share actually fell from 67% (1997) to 59% (2008) before recovering to 63% (2013). The honest Singapore claim for Toronto: pricing plus ownership restraint plus sustained transit investment sustains a high-transit city; pricing by itself does not create one.

**Open data: excellent now, nothing for 1975 or 1998.**
- **LTA DataMall** (https://datamall.lta.gov.sg/content/datamall/en/dynamic-data.html, free account key): APIs for ERP rates, traffic speed bands, traffic flow, and monthly passenger volumes by bus stop, train station and origin-destination pair as CSV.
- **LTA ridership statistics**: official PDFs, yearly 2005 to 2022 (DataMall lists a series running 2006 to 2025) and monthly 2019 to 2023.
- **data.gov.sg, "Average Daily Traffic Volume Entering the City"**: annual series 2004 to 2025, weekdays 07:30 to 19:00, the closest thing to a long-run cordon entry count anywhere in this file.
- Nothing open reaches the 1975 or 1998 implementations; the before/after evidence for both lives in the reports below.

**Key reports.**
- Holland & Watson (1978), "Traffic Restraint in Singapore" (World Bank), the original ALS evaluation.
- Phang & Toh (2004), "Road congestion pricing in Singapore: 1975 to 2003," Journal of Transport Economics and Policy 38(3), 371-395.
- Menon & Chin (2004), "ERP in Singapore: what's been learnt from five years of operation?"
- Olszewski (1999), "ERP in Singapore: a perspective one year on."
- Chin (2010), "Electronic Road Pricing: Experience & Lessons from Singapore," SIM Series 33.
- Current rates example: LTA, "Revised ERP Rates from 1 September 2025," https://www.lta.gov.sg/content/ltagov/en/newsroom/2025/8/news-releases/revised-erp-rates-from-1-september-2025.html

## 10. Cross-case evidence: what Toronto can concretely claim

All five cases side by side. Figures are the headline evaluation results from Sections 3, 4, 8 and 9; treat Singapore's ALS row as a different era (paper licences, bundled measures) and not as a prediction for Toronto.

| Case | Traffic / entries effect | Speed / delay effect | Net revenue | Revenue to transit? | Transit ridership effect |
|---|---|---|---|---|---|
| New York 2025 ($9 peak daily charge) | Entries down 11% in year one | Speeds up about 11% inside the zone | About $578M net in 2025 (gross $716.5M, operating about 19%) | Yes: bonded into a $15B transit capital plan | Observed 2024 to 2025: subway +7.7%, bus +7.6% (partly post-pandemic recovery) |
| London 2003 (£5 at launch, £18 now) | Vehicles entering down 25% at launch, cars down 18%; still about 21% down at five years | Speeds up about 30%, delay down 25 to 30% at first; delay later crept back as road space was reallocated | £155.9M net in 2017/18 (gross £229.8M, operating 25%) | Yes: 100% of net revenue to London transport, by law | Bus passengers entering the zone up about 29,000 in the morning peak in year one; bus use up 18% year one |
| Stockholm 2006 (SEK 10 to 20 per passage, cap SEK 60) | Cordon crossings down 22% in the trial, about 20% sustained for a decade | Arterial delay down a third (AM) to a half (PM); queues down 30 to 50% | Revenue 70.9M euros (2008) rising to 140M euros (2016); operating share fell 31% to 7% | Earmarked to regional transport capital: roads first (Bypass), later also Metro; never general revenue | Trips across the cordon up 6 to 7% measured, about 4 to 5% attributable to the charge; capacity added before launch |
| Singapore ALS 1975 (S$3/day licence) | Zone entries down 44%, cars down about 73% | Zone speeds from under 20 to about 33 km/h | Not the point of the scheme; small by modern standards | No (general revenue era) | Shift came bundled with park-and-ride and bus measures; car pools up 35% |
| Singapore ERP 1998 (per passage, no cap) | A further 10 to 15% off the already-priced ALS baseline; 15% daily after one year | Expressway speeds 35 to 55 km/h in charged hours; speed bands held by quarterly rate reviews since | About S$80M/yr gross around 2003 (operating about 20%); S$152 to 160M in 2013/14 | No: Consolidated Fund, not ring-fenced | No significant modal shift in year one (Olszewski); long-run ridership growth driven by rail expansion and the COE cap |

**Predictions Toronto can defend from this table.**
1. **Driver drop: expect 10 to 25%.** Every modern case lands in that band (New York 11%, London 18 to 25%, Stockholm 20 to 22%). The Section 6 scenarios use 15%, the middle of the band.
2. **Speeds improve more than volumes fall.** Delay and queue effects (30 to 50% in Stockholm, about 30% in early London) run ahead of the volume drop, because traffic near capacity is nonlinear. But London warns that delay returns if the freed space is given away without a plan.
3. **Net revenue: use the realized coefficient, not the headline toll.** New York nets about $3 per entry and about $1,100 per daily entry per year (Section 6). Operating cost share starts high and falls with maturity (Stockholm 31% to 7%, London over 50% in early years to 25%, New York about 19% with modern plate tech), so Toronto should budget a worse net in years one and two than at maturity.
4. **Transit ridership rises when, and only when, capacity is there.** Stockholm added service months before launch and got a clean 4 to 5% attributable transit gain; London's buses, using freed road space, were the year-one win; New York's gains ride on $15B of bonded capital. Singapore is the counterexample: pricing with no bundled transit package produced no measurable mode shift in year one. The Toronto proposal should pair the charge with bus priority and service increases on the corridors feeding the zone, funded or announced with the charge.
5. **Earmarking is the politics.** London (by law), New York (bonded capital plan) and Stockholm (earmark deal credited with winning over politicians) all fenced the money for transport. Singapore, the one case that did not, also never had to win a public vote on it. Toronto needs provincial approval, so a visible transit earmark is both policy and strategy.
6. **Design details that recur:** per-passage pricing beats a flat day licence (Singapore's extra 10 to 15% came from pricing repeat trips); price the shoulders and bypasses (Singapore's shoulder bunching, Stockholm's Essingeleden eventually tolled); a published rate-adjustment rule (Singapore's quarterly speed-band reviews) keeps later increases boring; and publish the counts from day one. Neither Stockholm nor Singapore released open before/after data, which is why their evidence sits in reports; New York did, which is why its numbers are the most reusable here. Toronto can beat all four on transparency by releasing cordon counts and transit boardings as open data from launch.
