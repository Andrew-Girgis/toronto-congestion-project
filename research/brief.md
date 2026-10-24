# Research brief: what Toronto can learn from four congestion-pricing cities

*Researched 2026-10-24. Detail: `research/cases/*.md` and `research/lessons-table.md`. Sources: `research/sources.csv`. Labels: OBSERVED (REPORT) = the agency's own reported figure; ESTIMATED = causal or statistical estimate; UNVERIFIED = not confirmed against a primary source.*

## Bottom line
1. **Pricing reliably reduces traffic into a charged zone.** All five interventions saw roughly 10–22% fewer charged crossings, or far more under Singapore's 1975 scheme. Whether the zone *stays* less congested depends on what happens to the freed road space (London).
2. **Design determines the burden and the money.** Pricing per passage with a daily cap (Stockholm) versus once per day (NYC, London) changes both revenue and who pays.
3. **Every success had transit in place before charging**: London +23% bus service, Stockholm a trial bus package, Singapore park-and-ride. NYC is the exception: its toll funds a capital plan.
4. **The hard part is politics and law, not technology.** NYC took more than a decade. Stockholm needed a trial and a referendum. London's western extension was reversed. For Toronto, the 2025 re-enactment of City of Toronto Act s.41 means **no City charge without provincial legislation**.
5. **Operating cost matters early.** London spent 76% of revenue on operations in year one; Stockholm went from 31% to 7%; NYC about 20%. Automation and simple payment are what bring it down.

## The five cases (descriptive, not comparable as elasticities)

| Case | Traffic | Speed / delay | Money |
|---|---|---|---|
| New York CRZ 2025 | Entries about −11% (Jan–Oct 2025), UNVERIFIED; −8% to −14% reported | Zone speeds +11% (ESTIMATED, synthetic control) | US$700.5M tolls, US$139.2M costs, **US$562.0M net** (2025 preliminary, OBSERVED) |
| London CCZ 2003 | Cars entering −33%, all 4+ wheel vehicles −18% (OBSERVED) | Congestion −30% (2003), eroding to −8% (2006) | Opex 76% of revenue in year one; net £137M in 2007/08, 27% of revenue from penalties |
| Stockholm 2006/07 | Cordon −22% in the trial; about −20% sustained | Queues −1/3 AM, −1/2 PM | About €200M system cost including year one; opex €22M in year two |
| Singapore ALS 1975 | Cars entering −73%; all vehicles −44% (07:30–10:15) | Zone faster; ring road about 20% slower | Revenue was not the objective |
| Singapore ERP 1998 | Expressways −15%; zone −16% beyond ALS | Expressways 35 → 55 km/h | Capital S$197M; opex about S$25M/yr |

## Lessons for Toronto (what we carry into the model and the pitch)
- **Boundary:** Stockholm and Manhattan have water choke points. Downtown Toronto has the lake and the Don Valley, but open north and west edges. We compare three candidate boundaries on crossing count and count coverage, and test diversion in the simulation.
- **Response:** calibrated to the observed 10–22% band at the NYC-equivalent price rather than borrowing an elasticity from another context.
- **Money:** collections are built bottom-up from Toronto's simulated charged trips. Foreign net revenue per entry is **not** transferred. International opex ratios serve only as reasonableness checks.
- **Sequencing:** tool pilot → transit capacity → time-limited trial → evaluation → decision (Stockholm model). This requires provincial legislation.
- **Equity:** Pembina Institute (2018), using TTS, found that most commuters affected by the proposed Gardiner/DVP toll had above-median household incomes, but the toll weighed more heavily on affected lower-income households. Our open-data work cannot identify payers by income (ecological fallacy); the pilot would use TTS tabulations.

## Toronto's own history
- 2016: the City proposed a flat $2 toll on the Gardiner and DVP (described in Pembina 2018, P-001). The Province declined to allow it in early 2017 (UNVERIFIED: no primary source in the register).
- 2015: City staff report EX8.14 costed expressway tolling; its figures are modelled AM-peak VKT, not observed counts.
- 2024: the *Get It Done Act* bars tolls on provincial highways without an Act.
- 2025: the *Plan to Protect Ontario Act (Budget Measures)* re-enacted CoTA s.41: the City "does not have the power to designate, operate or maintain a highway as a toll highway".
- Fall 2027: the Gardiner and DVP are scheduled to transfer to the Province.
