# New York City: Congestion Relief Zone (CRZ), launched 5 January 2025

Workstream B case file. Researched 2026-10-24. Source IDs refer to `research/sources_B.csv`.

**Labels**
- **OBSERVED (REPORT):** taken from an agency or official document.
- **ESTIMATED:** a causal or statistical estimate.
- **MODELLED:** a forecast or appraisal.
- **UNVERIFIED:** not confirmed against a primary document this session.

The MTA first evaluation report (mta.info/document/195631) and the MTA annual disclosure statement (document/199581) both returned HTTP 403 to direct download. Figures from them are marked UNVERIFIED unless they were confirmed elsewhere.

## Charge design and changes over time

**Zone and charging hours**
- The zone is Manhattan local streets at and south of 60th St.
- FDR Drive, the West Side Highway/Route 9A and the Hugh L. Carey Tunnel connections to West St are excluded.
- Peak hours are 05:00–21:00 on weekdays and 09:00–21:00 on weekends. Overnight rates are 75% lower. (B-NYC-011)

**Rates (E-ZPass), peak / overnight (B-NYC-011)**

| Vehicle | Peak | Overnight | How charged |
|---|---|---|---|
| Passenger vehicles | $9.00 | $2.25 | once per day |
| Motorcycles | $4.50 | $1.05 | once per day |
| Single-unit trucks and some buses | $14.40 | $3.60 | per entry |
| Multi-unit trucks and tour buses | $21.60 | $5.40 | per entry |
| Taxis, green cabs, black cars | $0.75 per trip | $0.75 per trip | passenger pays |
| High-volume FHVs (Uber/Lyft) | $1.50 per trip | $1.50 per trip | passenger pays |

- Vehicles without E-ZPass pay about 50% more (B-NYC-007, CBC slide 10).

**Crossing credits.** Peak-period E-ZPass entries via the Lincoln, Holland, Queens-Midtown or Hugh L. Carey tunnels get a credit of up to $3 for cars and up to $12 for large trucks. There are no credits overnight. (B-NYC-011)

**Scheduled increases.** Cars rise to $12 in 2028 and $15 in 2031 (B-NYC-011). The originally approved car toll was $15. Governor Hochul paused the program on 5 June 2024 and relaunched it at $9 on 14 November 2024 (B-NYC-016, UNVERIFIED: press).

**Legal basis.** The 2019 NY State Budget authorized the program and mandated:
- some exemptions;
- the crossing credits;
- support for $15B of MTA capital projects;
- a Traffic Mobility Review Board to recommend rates. (B-NYC-017)

## Traffic, speed and reliability outcomes

| Metric | Result | Period / definition | Label | Source |
|---|---|---|---|---|
| Vehicle entries to CRZ | −11% | Jan–Oct 2025 vs MTA historical baseline (October 2023 data with seasonal adjustment factors, per CBC slide 15) | UNVERIFIED (MTA report via secondary coverage) | B-NYC-008 |
| Vehicle entries to CBD | −8% to −14% | "One year later" range | OBSERVED (REPORT), independent analyst (Citizens Budget Commission) | B-NYC-007 |
| CRZ vehicle-miles | −7.1% | Jan–Sep 2025 YoY | UNVERIFIED | B-NYC-008 |
| Cordon-area road speeds | +11% | Google Maps travel times, generalized synthetic control | ESTIMATED (causal, NBER WP 33584, not peer reviewed) | B-NYC-009 |
| CBD average speed | 8.2 → 9.7 mph (+15%) | vs 5 control cities | ESTIMATED (simpler design, NBER Digest) | B-NYC-010 |
| Speeds of FHV trips entirely inside the CBD | +1% (8.45 → 8.50 mph) | 2024 vs 2025 TLC trip records | OBSERVED (REPORT), descriptive | B-NYC-007 |
| Multi-unit truck entries | −20% | 2025 | OBSERVED (REPORT) | B-NYC-007 |
| Uber/Lyft trips / taxi trips | −6% / +13% | 2024 vs 2025 monthly averages | OBSERVED (REPORT) | B-NYC-007 |

**Retiming is visible.** Entries spike just before 05:00 and at 21:00, on both sides of the peak window, and this persisted through 2025 (B-NYC-007, CBC slides 21–22). Shoulder bunching appears in NYC just as it did in Singapore in 1975.

**Speed estimates disagree** (11% vs 15% vs 1% vs MTA's reported 4.6%). They use different methods, roads and periods. Only the NBER synthetic-control figure is a causal design. The disagreement is itself a finding: "speed improvement" depends heavily on what is measured.

**Confounders:** post-pandemic recovery, return-to-office trends and weather. Federal litigation uncertainty could also have affected behaviour.

## Transit outcomes and complementary investment

- **Revenue use.** Revenue is legally committed to the MTA capital program; the $15B capital plan is backed by bonding against the revenue stream (B-NYC-017). There was no large pre-launch service expansion comparable to Stockholm's or London's.
- **Subway ridership.**
  - Annual ridership rose from 1.21B (2024) to about 1.30B (2025), +7.7% (B-NYC-018, advocacy presentation at a TRB webinar).
  - AM-peak subway trips to the CRZ rose by about 40,589 per day (+7%).
  - These are descriptive figures. Ridership was already recovering from the pandemic.
- **Main-thread computation.** The year-on-year weekday comparison in `data-sources.md` §7 (from data.ny.gov `sayj-mze2`) belongs to the main thread and is not re-verified here.

## Capital and operating costs

**Tolling system contract.** TransCore was awarded a $507M design-build-operate-maintain contract in 2019. It was amended to about $555–556M after delays, and extended to 2030 (B-NYC-013, UNVERIFIED: press). A policy document cites more than $427M allocated through the MTA Capital Dashboard (UNVERIFIED).

**Operating costs, 2025 (B-NYC-003):**
- Total program expenses were **$139.2M** (accrual, preliminary).
- Largest lines: maintenance and other operating contracts, $84.6M; other business expenses (likely credit card processing), $33.3M; professional services, $16.4M; labour, $4.6M.
- Depreciation of $18.8M is excluded from expenses.
- Debt service of about $1.5M/month is excluded (B-NYC-005, UNVERIFIED).
- Expenses were **19.9% of total revenue**.

## Gross collections, net proceeds and use of revenue

The primary source is the **MTA CBDTP Financial Report, December 2025 year-to-date**, accrual statement of operations, p.2 (https://www.mta.info/document/197586). Results are marked "preliminary and subject to audit review".

| Line (2025, Jan 5 – Dec 31) | Actual | Forecast |
|---|---|---|
| Vehicle toll revenue | **$700.465M** | $677.262M |
| Other operating revenue | $0.772M | $0.145M |
| Investment income | $0.000M | $10.361M |
| Total revenue | **$701.237M** | $687.768M |
| Total expenses (excl. depreciation) | **$139.207M** | $139.505M |
| Net surplus | **$562.029M** | $548.263M |

**Corrections to `data-sources.md`:**
- The figures "gross $716.5M, operating cost $138.1M, net about $578M" do not match the primary report.
- Use **toll revenue $700.5M, expenses $139.2M, net $562.0M** instead.
- The Citizens Budget Commission slide says "MTA collected $578M in 2025" (B-NYC-006). Its definition differs, perhaps cash rather than accrual or including other items; it is unreconciled.
- The governor's office says "over $550M net".
- The MTA disclosure says net $562.0M exceeded the $500M projection (B-NYC-005, UNVERIFIED).

**Revenue mix.** Cars, taxis and FHVs make up over 90% of revenue (CBC slide 31, chart only). The MTA "strongly discourages revenue estimation using other data sources" (CBC slide 29; MTA disclaimer on t6yz-b64h).

## Technology, procurement and implementation timeline

**Timeline**
- **2007:** Mayor Bloomberg proposes an $8 charge south of 86th St. The NY Assembly never votes on it, and it dies in 2008 (B-NYC-016, UNVERIFIED: press).
- **2019:** State budget authorization (B-NYC-017). TransCore is selected the same year.
- **27 June 2023:** FHWA Finding of No Significant Impact after the environmental assessment (B-NYC-016).
- **5 June 2024:** Governor pauses the program indefinitely, about 3 weeks before its planned 30 June start.
- **14 November 2024:** Relaunch announced at $9.
- **5 January 2025:** Launch.

**Technology.** Overhead gantries and cameras at entry points read E-ZPass transponders, with licence plates billed by mail as the fallback.

## Exemptions and mitigation

- **Low-Income Discount Plan:** 50% off the peak toll after the first 10 peak trips in a calendar month. Eligibility is federal AGI ≤ $50,000 or enrolment in SNAP, WIC or TANF (B-NYC-012, UNVERIFIED: MTA deck seen via search excerpt).
- **Low-Income Tax Credit:** for CRZ residents with NY AGI under $60,000.
- **Disability exemption:** IDEP covers people whose disabilities prevent them from using transit, and there is an organizational disability plan.
- **Other exemptions:** emergency vehicles and eligible buses.
- **Environmental-justice mitigation:** commitments from the environmental assessment (e.g. Bronx air-quality measures) exist but were not quantified this session (UNVERIFIED).

## Public acceptance, communications, political and legal challenges

**Public opinion**
- **April 2024:** 63% of NY State voters opposed, including 64% of NYC voters (Siena; B-NYC-014, UNVERIFIED: via search).
- **December 2024:** NYC voters 32% support, 56% oppose.
- **March 2025, two months after launch:** NYC 42% support, 35% oppose (n = 312 NYC voters). A Quinnipiac poll the same week found 41% support, 54% oppose.
- **Reading:** support rose after launch, but polls conflict.

**Political**
- **2008:** the Bloomberg plan died in Albany.
- **2024:** the governor's pause, widely attributed to suburban electoral concerns (B-NYC-016).
- **Coalition:** a broad advocacy coalition (Riders Alliance, Regional Plan Association, Tri-State Transportation Campaign, business groups including the Real Estate Board of New York) was credited with reversing the pause (TRB webinar slides 45–48).

**Legal**
- Lawsuits from New Jersey and others challenged the environmental review.
- **Federal challenge:** USDOT sent termination letters on 19 February and 21 April 2025. A preliminary injunction followed on 28 May 2025. On 3 March 2026 Judge Liman vacated the letters as arbitrary and capricious, without a permanent injunction. DOJ appealed to the Second Circuit (B-NYC-015, UNVERIFIED: press).
- A putative class action was filed in the District of New Jersey in December 2025 (UNVERIFIED).

**Communications lesson.** The CBC slide calls the "Valley of political death" "real but survivable" (B-NYC-007, slide 35). Support fell before launch and recovered after people experienced the results.

## What worked

- **Revenue came in above projection** in year one ($562M net vs $500M projected; B-NYC-004/005).
- **Measurable traffic reduction.** A causal estimate finds speeds up on cordon-area roads *and* spillover speed gains outside the cordon on roads used by cordon-bound drivers (B-NYC-009).
- **Legally ring-fenced, bonded capital revenue** made the benefit concrete: it funds visible projects.
- **Modern E-ZPass and plate tolling** kept operating costs to about 20% of revenue in year one, much better than London's first year (76%; B-LON-012).

## What didn't work or remains contested

- **Taxi/FHV per-trip charges are low** ($0.75–$1.50) while FHVs are a large share of zone vehicle-miles. Komanoff (TRB slide 39) puts it at "nearly half of congestion-zone vehicle miles", an analyst claim, UNVERIFIED. This weakens the congestion effect per dollar.
- **Peak-edge bunching** at 05:00 and 21:00 shows the cliff-edge rate schedule is too coarse.
- **The $9 rate was a political compromise**, lower than the $15 approved after the Traffic Mobility Review Board's analysis, so the design was not optimized for congestion.
- **Speed gains inside the zone are disputed**: 1% (TLC trips) to 15% (NBER digest).
- **Prolonged litigation risk**, both federal and from New Jersey.

## What remains uncertain

- The long-run elasticity once the $12 and $15 steps take effect.
- Whether ridership gains are attributable to pricing or to post-pandemic recovery.
- Distributional outcomes. No published payer-income analysis was found this session.
- The final audited 2025 net figure.

## Relevance for Toronto

- **Geography.** NYC had a geographically obvious zone bounded by rivers, with priced tunnel and bridge choke points (Komanoff, TRB slide 38). Toronto's downtown lacks this on its north and west sides, so the user-feedback point about choke points (UF-001) is supported by this source.
- **Transit.** NYC's dense rapid transit made the equity argument easier; Toronto's transit coverage differs by approach direction.
- **Revenue modelling.** Toronto revenue must be modelled bottom-up. NYC's realized ratio (net/gross about 0.80 in year one) is usable only as a **reasonableness check**, not a per-entry coefficient.
