# Pilot cost (90 days)

Every line below is an **ASSUMPTION** to be confirmed with the division. Staff rates are illustrative loaded costs, not City salary schedules.

| Line | Basis | Low | High |
|---|---|---|---|
| Transportation modeller, 0.5 FTE × 0.25 yr | C$120k–170k loaded per FTE-year (ASSUMPTION) | 15,000 | 21,250 |
| Data analyst, 0.5 FTE × 0.25 yr | same | 15,000 | 21,250 |
| Project lead / communications, 0.1 FTE-year equivalent | same | 12,000 | 17,000 |
| Privacy Impact Assessment scoping and legal review | external or internal effort (ASSUMPTION) | 10,000 | 20,000 |
| Hosting (City cloud or on-premises VM) | open-source stack; one workstation-class VM | 0 | 2,000 |
| Software licences | SUMO (EPL-2.0), DuckDB (MIT), Astro (MIT), MapLibre (BSD) | 0 | 0 |
| **Total** | | **52,000** | **81,500** |

Rounded: **about C$50k–80k.**

## Not in the pilot: implementing an actual charge

These come from the scenario model (`web/public/data/finance.json`), with ranges:
- **Capital:** charging points × C$0.73–0.97M each (City EX8.14 2015 toll-point cost, CPI-adjusted; expressway gantries, so arterial cameras may be cheaper, UNVERIFIED), plus a central system of C$6.5–25M.
- **Operating:** 30% of collections in year one, falling to 11% (Stockholm 31% → 7%; London 76% in year one; 407 ETR 13–16%).
- **Benchmarks:** Stockholm about €200M including year one; Singapore ERP S$197M capital; NYC's operations contract about US$507M (UNVERIFIED).
