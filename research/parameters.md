# Model parameters: behaviour, money, growth, institutions (workstream D)

Researched 2026-10-24. Sources are in `research/sources_D.csv` (IDs D-0xx), and machine-readable values are in `config/assumptions.draft.yaml`.

Labels: **OBSERVED**, **OBSERVED (REPORT)**, **ESTIMATED** (incl. official projections and our calculations, marked *calc*), **ASSUMPTION**, **UNVERIFIED**. Ranges are illustrative scenario bounds, not confidence intervals.

---

## 0. Headline findings that change the project

1. **The legal pathway in AGENTS.md is out of date.**
   - The *Plan to Protect Ontario Act (Budget Measures), 2025* (S.O. 2025 c.10, Sched. 2; Royal Assent 2025-06-05) replaced City of Toronto Act **s.41**: "The City does not have the power to designate, operate or maintain a highway as a toll highway". It applies "regardless of the City's purpose … including for the purpose of easing congestion".
   - The same Act **repealed s.116**, the regulation route that EX8.14 (2015) relied on.
   - A City-run charge now needs **an Act of the Legislature**, not just a provincial regulation. (D-009, D-010)
   - Separately, the *Get It Done Act, 2024* bars tolls on any **Crown** highway unless an Act authorises them (D-011). The Gardiner and DVP transfer to the Province in **fall 2027** (D-012), so after that their tolling is a provincial statutory question.
   - Whether a fee for entering a zone on City *streets* is a "toll highway" under s.41 is a legal interpretation question. **UNVERIFIED**; do not claim either way.
2. **Transferring a constant elasticity to a C$12.58 charge produces implausible results unless existing out-of-pocket costs are included.** See §1.3. This is why the behaviour model must use a total-cost base and be checked against the observed 10–25% band.
3. **Toronto's population is projected roughly flat to 2035.** The Toronto census division goes from 3.14M (2026) to 3.16M (2035), with a dip to 2030; the GTA grows 4.2% (D-013). This supports UF-001's warning against "miscalculating population growth" and argues against assuming baseline traffic growth.
4. **Toronto-specific facts for the demo** (D-018, City report, Dec 2024):
   - Downtown-core VKT is about **2.64M/day**, 148,800 in the 8–9am hour (2023).
   - Ride-hail (PTC) is **14.2%** of downtown VKT all day and 11.6% in the AM peak.
   - The downtown PM-peak travel time index is about **2.0**, meaning trips take twice their free-flow time.

---

## 1. Behavioural response

### 1.1 Elasticities (OBSERVED (REPORT))

| Case | Measure | Value | Source |
|---|---|---|---|
| Stockholm 2006 intro, charged hours, non-exempt | log-arc elasticity wrt **total trip money cost** (base EUR 2.55 = 17 km × 0.15) | **-0.87** | D-006 Table 3 |
| Stockholm 2006 → 2014 | same | -0.87 → **-1.24** (rising) | D-006 |
| Stockholm private cars only | same | -1.57 → -2.49 | D-006 |
| Stockholm, peak only at intro | same | -0.67 (off-peak -1.13) | D-006 p.10 |
| Gothenburg 2013 intro (≈25% transit share vs Stockholm ≈75%) | same | **-0.69** → -0.52 (falling) | D-006 Table 4 |
| Stockholm 2016 peak **rate increase** | same | **-0.28** (vs -0.67 at intro) | D-006 Table 5 |
| Essinge bypass extension 2016 | same | -0.16 | D-006 Table 6 |
| Stockholm, wrt charge (not total cost), Börjesson et al. 2012 | elasticity of cordon traffic | -0.70 (2006) → -0.85 (2009+) | D-005 p.9 |
| US toll roads (Janson & Levinson 2014, cited) | toll elasticity | -0.30 to -0.36 | D-006 p.6 |
| Norway toll projects (Odeck & Bråthen 2008, cited) | short / long run | -0.45 / -0.82 | D-006 p.6 |
| Stockholm transit | cross-price elasticity | 0.13 (Gothenburg 0.33) | D-006 p.10 |
| Singapore ERP (Olszewski & Xie 2005) | qualitative | cars > other vehicles; expressways > CBD cordon; AM < PM | D-024 (abstract only) |

**What transfers:**
- First-introduction elasticities are 2–4× larger than responses to later rate rises.
- Trucks and company cars respond much less than private cars.
- Long-run direction is city-specific: up in Stockholm, down in Gothenburg.
- Lower-transit, more dispersed Gothenburg has smaller elasticities. Toronto's downtown is transit-rich, but suburban approaches are not, so a Toronto value between the two is defensible as an ASSUMPTION.

### 1.2 What removed drivers did instead (OBSERVED (REPORT))

| Response | London 2003 (of 65–70k removed car trips) | Stockholm 2006 (≈23pp of ≈25% removed person car trips) |
|---|---|---|
| Switch to public transport | **50–60%** | ≈10pp work trips → **≈43%** *(calc)* |
| Divert around the zone | **20–30%** (through trips) | ≈2pp to Essinge bypass → **≈9%** *(calc)* |
| Change destination / fewer or combined trips | part of 15–25% "other" | ≈6pp discretionary → **≈26%** *(calc)* |
| Retime | part of "other" | no aggregate sign of departure-time change (D-006 p.10) |
| Professional traffic (unspecified) | — | ≈5pp → **≈22%** *(calc)* |
| Source | D-007 pp.4, 55, 60 | D-005 p.14 (two-wave panel; authors urge caution) |

Draft base shares (ASSUMPTION within these ranges): transit 45%, reroute 15%, destination/cancel/combine 25%, retime 5%, professional 10%.

In our pipeline, **rerouting comes from SUMO** wherever the network contains the alternative; the aggregate shares cover what SUMO cannot represent. This directly tests UF-001's "cut through neighbourhoods" concern instead of assuming an answer.

### 1.3 Worked check (our calculation): why the cost base matters

Model form (Börjesson, D-006): `D1/D0 = ((c0 + charge)/c0)^ε`, with charge = C$12.58.
- c0 = 20 km × C$0.22/km (Metrolinx perceived cost, 2025$) = **C$4.40** and no parking: ε = -0.3 → **-33%**; ε = -0.87 → **-69%**.
- c0 = C$19.40 (adding C$15 paid parking): ε = -0.3 → -14%; -0.5 → -22%; -0.87 → -35%.
- c0 = C$29.40 (C$25 parking): -0.3 → -10%; -0.5 → -16%; -0.87 → -27%.

The observed modern band is −11% (NYC, MTA) to −25% (London, vehicles with 4+ wheels). Stockholm's charge was about 50% of trip cost; C$12.58 would be about 290% of a Toronto fuel-only cost. **Conclusions:**
- (a) Include parking, transit fares on the alternative, and other out-of-pocket costs in c0.
- (b) Treat the share of drivers with free or employer-paid parking as a key unknown (**UNVERIFIED**).
- (c) Calibrate the base ε so the S2 result falls inside the observed band, or show clearly why Toronto would differ.
- (d) Never present the -69% case as a forecast.

### 1.4 Toronto-specific modelled response
- EX8.14 (2015) City travel-demand model: a $3 flat toll gives AM-peak-hour VKT **-9% Gardiner / -12% DVP** and saves 3 and 5 minutes. These are model outputs, so label ESTIMATED (City model) (D-008 p.13 Table 7). They are an expressway-only toll, and the reduction includes diversion to arterials. Use only as the partial S1 check.
- At very high tolls, EX8.14 found "traffic diverts away from the facilities, resulting in lower revenues" (p.12). That is the revenue–congestion trade-off, stated by the City itself.

---

## 2. Value of time (for SUMO route cost)

| Parameter | Value | Label | Source |
|---|---|---|---|
| Metrolinx appraisal VOT | $18.79/person-h (2021$) | OBSERVED (REPORT) | D-004 Table 5.35 |
| → 2025$ (× Ontario CPI 1.1564) | **$21.73/person-h** | ESTIMATED *(calc)* | D-002 |
| Occupancy | 1.15 (1.05–1.26) | ASSUMPTION (1.26 is Stockholm's value, D-005) | — |
| Per-vehicle VOT | $24.99 (22.82–54.76) | ASSUMPTION *(calc)* | — |
| High case | 2× person VOT | ASSUMPTION. Toll payers reveal higher VOT; NBER NYC uses US$40/h (D-021) | — |

Caveat: Metrolinx's VOT is an average appraisal value across modes, not a revealed willingness to pay among peak drivers.

## 3. Money conversions and discounting

- **USD/CAD 2025 annual average: 1.3978** (Bank of Canada, OBSERVED; D-001). US$9 → **C$12.58**; US$12 → C$16.77; US$15 → C$20.97 *(calc)*. A market rate is not a burden comparison.
- **CPI** (StatCan 18-10-0005-01; D-002), Ontario: 127.4 (2015), 143.2 (2021), 165.6 (2025). Factors: 2021→2025 = 1.1564; 2015→2025 = 1.2998 *(calc)*.
- **Discount rate:** TBS 2022 guide, **7% real**, with social time preference about 3% (PDF p.36; D-003). Metrolinx Ontario practice: **3.5%** real, 2.5% sensitivity (D-004). Recommended: 7% base (agreed), with 3% and 3.5% shown.

## 4. Growth and remote work

- **Ontario MOF projections (Summer 2026, reference scenario; D-013):**
  - Toronto CD: 3,271,830 (2025), 3,137,414 (2026), 3,101,770 (2031), 3,164,717 (2035), 3,567,416 (2051).
  - GTA's 5 CDs: 7.68M (2025), 7.50M (2026), 7.81M (2035), which is **+4.2% for 2026–35** *(calc)*.
- **Downtown jobs:** 643,350 (2024), 664,650 (2025) (Toronto Employment Survey; D-014; UNVERIFIED against PDF). These are establishment counts, not daily attendance.
- **Remote work:** Toronto CMA 24.7% mostly working from home (May 2024; D-016). TTC ridership about 78% of pre-pandemic in Oct 2025, with no lift from fall-2025 return-to-office policies (secondary; D-017).
- **Growth Plan Schedule 3** (3.65M people, 1.98M jobs in 2051; D-015): status after the Provincial Planning Statement 2024 is **UNVERIFIED**. Prefer the MOF projections.
- **Why traffic ≠ population:**
  - Downtown road capacity is built out (EX8.14 p.11).
  - Stockholm cordon traffic stayed flat from the 1990s to 2005 despite growth, limited by capacity (D-005 p.8).
  - Remote work persists.
  - Growth lands mostly on transit-served downtown and midtown sites.
- **Draft:** baseline cordon traffic growth of 0%/yr (−0.5% to +1%), applied identically to both futures (ASSUMPTION).

## 5. Time-of-day pricing

- **Stockholm 2006:** cordon traffic −18% in the AM peak, −23% in the PM peak, −22% midday (D-005 p.9). There was no aggregate sign of retiming, even after the 2016 peak-only rise, which cut peak and off-peak alike by about 5% (D-006 p.10). Off-peak responses are inflated by trips that pay the peak rate in the other direction.
- **Singapore ALS 1975:** a surge of vehicles waiting to enter after 9:30 forced the hours to be extended to 10:15. Congestion "shifted in time and place", and shoulder pricing was introduced in 1994 (D-023).
- **Singapore ERP:** variable pricing produced peak spreading (Olszewski & Xie 2005, abstract; D-024).
- **For S3:** the shoulder half-rate is an ASSUMPTION test of shoulder bunching. Retiming is design-dependent, ranging from 0% (Stockholm) to large (Singapore with sharp time edges).

## 6. Implementation costs and compliance

**Toronto bottom-up (EX8.14, 2015$; D-008 p.9):**

| Item | Open system | Closed system | 2025$ (× 1.2998) |
|---|---|---|---|
| Roadside per toll point | $0.56–0.75M | — | **$0.73–0.97M** *(calc)* |
| Capex total | $27.5M | $47.5M | $35.7M / $61.7M |
| Annual O&M + replacement (2031 volumes) | $30.9M | $36.6M | $40.2M / $47.6M |

These are expressway gantries with a simpler back office. A cordon needs exemptions, permits and enforcement, so treat the central system cost as a low bound.

**International reasonableness checks:**
- **Stockholm:**
  - Start-up cost 1,900 MSEK, including the information campaign and tests (D-005 p.35); about EUR 200M (D-006). The contractor later said it could be built for half (D-005 p.32).
  - Operating cost EUR 22M in year 2 (D-006).
  - Opex/revenue **31% (2008) → 12% (2013) → 7% (2016)** (D-006 Table 2).
- **London 2003 (prelim.):** annual costs £130M (£90M operation, £5M TfL admin, £20M extra buses, £15M chargepayer compliance) (D-007 Table 6.1). This is old technology; do not transfer.
- **407 ETR (Ontario, mature, distance-based):** opex/revenue **16.0% (2025)**, or 14.0% excluding the $40.9M Schedule 22 payment, and 13.3% (2024) *(calc from D-020)*.
- **NYC:** TransCore US$507M, 7–8-year design-build-operate-maintain contract (2019). Search excerpt only, **UNVERIFIED**.

**Compliance:**
- London 2003: about 35,000 penalty notices per week against about 550,000 payments, and 63% of notices paid. That implies about **2.4%** of chargeable events unrecovered *(calc)* in the early years.
- Stockholm: payment compliance "high", with no number given (D-005 p.30).
- Draft collection loss: **3% (1–6%)**, labelled ASSUMPTION.

**Taxi/ride-hail:** NYC charges per trip, paid by the passenger: high-volume FHVs US$1.50, taxis US$0.75. Passenger cars pay once per day; trucks pay US$14.40 / $21.60 at peak (D-019). Toronto PTC volume is 212,000 trips/day citywide, and PTC is 14.2% of downtown VKT (D-018).

## 7. Institutional and jurisdiction facts (Toronto)

| Fact | Status | Source |
|---|---|---|
| City cannot toll highways for any purpose (s.41 as of 2025-06-05); the s.116 regulation route is repealed | OBSERVED | D-009, D-010 |
| No toll on Crown highways unless authorised by an Act (PTHIA s.100, 2024) | OBSERVED | D-011 |
| Gardiner and DVP are City-owned until fall 2027, then provincial; up to $353M of provincial O&M funding until then | OBSERVED (REPORT) | D-012 |
| 400-series highways are provincial (Crown road authority), so PTHIA s.100 applies | OBSERVED (by statute scope) | D-011 |
| Council voted 32–9 (Dec 2016) to request a $2 toll; the Premier refused on 2017-01-27 | OBSERVED (REPORT), secondary | D-022 |
| GO/UP Express electrification (UF-001 idea): Lakeshore lines still slated; others dropped from the 10-year window; UP Express "late 2030s at the earliest" in a leaked draft | UNVERIFIED (secondary) | D-026 |
| GO/UP are provincial (Metrolinx) assets, so City toll revenue spent on them means funding a provincial agency | ESTIMATED (governance inference) | — |
| TTC buses: 100+ eBuses (June 2025), about 400 by 2026, 50% zero-emission by 2031, 100% by 2040 | OBSERVED (REPORT) | D-025 |
| EX8.14 assumed Toronto residents are about 65% of Gardiner/DVP traffic (a modelling assumption in Table 6) | OBSERVED (REPORT) | D-008 |

**Implication for adoption:** the 90-day *tool* pilot remains within City authority. The *policy* path now runs through new provincial legislation, which is a higher bar than the 2015–2017 regulation route. Any "staged roadmap to a trial" must say so plainly.

## 8. Not sourced tonight (the model must label these ASSUMPTION)

- Toronto auto occupancy for cordon crossers
- Average cordon-crossing trip length
- Paid parking cost and the share of drivers who pay it
- A Toronto-specific charge elasticity (only bounded by international values)
- Collection loss for a modern ANPR cordon
- Toronto PTC response to a per-trip fee
- Arterial ANPR cost per point (vs expressway gantry)
- Cordon back-office cost
- NYC capex and opex (primary MTA documents not found)
- Retime share
- Long-run elasticity drift
- 2025 Toronto work-from-home share
- Growth Plan Schedule 3 current status
- Full-text numeric elasticities for Singapore (Olszewski & Xie 2005; Phang & Toh 2004)
