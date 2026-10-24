# Stockholm: congestion tax (trial 3 Jan – 31 Jul 2006; permanent from 1 Aug 2007)

Workstream B case file. Researched 2026-10-24. Source IDs refer to `research/sources_B.csv`.

**Primary sources read this session**
- **Eliasson (2006):** "The Stockholm congestion charging system", a WCTR paper by the trial's scientific lead summarising the official evaluation. Cited here as "Eliasson WCTR".
- **Börjesson & Kristoffersson (2017):** *The Swedish Congestion Charges: Ten Years On*, CTS Working Paper 2017:2, https://www.transportportal.se/swopec/cts2017-2.pdf. The published version is in *Transportation Research Part A* 107 (2018). Cited here as "CTS 2017:2".
- **Transportstyrelsen** current rates page.

The ITF/OECD discussion paper (source of the 2008–2016 revenue and operating-cost series in `data-sources.md`) returned HTTP 403, so those figures stay **UNVERIFIED**.

## Charge design and changes over time

**Legal form.** A **national tax**, legislated by the Riksdag and collected by the Swedish Transport Agency. It is not a municipal fee, so senior-government legislation was required.

**Trial design (Eliasson WCTR; B-STO-018)**
- Single cordon, charged both directions.
- SEK 10 / 15 / 20 per passage by time of day.
- **Daily cap SEK 60.**
- Weekdays 06:30–18:30.
- About **30% of passages were exempt** (taxis, alternative-fuel cars and others; B-STO-002).

**Sequence**
- Trial 3 January – 31 July 2006.
- Referendum 17 September 2006.
- Permanent from 1 August 2007.
- In **January 2016** the peak charge rose **75%** (EUR 2 → 3.5) and the **Essingeleden bypass was brought into the charge** (CTS 2017:2 p.2; B-STO-013).

**Current rates in the city centre** (B-STO-016):
- SEK 11–45 per passage in peak season and SEK 11–35 in low season.
- **Maximum SEK 135/day** in peak season (SEK 105 in low season).
- Charging hours 06:00–18:29.
- **No charge in July**, except the first five weekdays.
- Essingeleden is charged SEK 11–40.

## Traffic, speed and reliability outcomes

| Metric | Result | Period / definition | Label | Source |
|---|---|---|---|---|
| Cordon passages, charged hours | **−22%** vs spring 2005 | Trial 2006, stable each month after the first | OBSERVED (REPORT) | B-STO-001 |
| Daily cordon passages | 371,300 passages; 115,100 tax decisions | Average day, May 2006 | OBSERVED (REPORT) | B-STO-002 |
| Long-run cordon reduction | **about 20%** (stabilised) | 2006 onward, adjusted for external factors | ESTIMATED | B-STO-010 |
| Queue time on approach roads | −1/3 AM peak, −1/2 PM peak | Trial | OBSERVED (REPORT) | B-STO-003 |
| Worst-decile travel times | improved by a factor of 3+ on some arterials (PM) | Trial | OBSERVED (REPORT) | B-STO-003 |
| Essingeleden (free bypass) | +0–4% by month | Trial | OBSERVED (REPORT) | B-STO-001 |
| Southern Link | about +5–10% attributed to the charge, uncertain (bridge-closure confound) | Trial | OBSERVED (REPORT) | B-STO-001 |

- **On–off–on evidence.** Traffic returned toward pre-trial levels when the trial ended and fell again when charges were reintroduced in 2007. This is the strongest quasi-experimental evidence among the cases (per `data-sources.md`; consistent with CTS 2017:2 but not re-verified by page this session).
- **The design forecast was 20–25%**, against a political target of 10–15% (Eliasson WCTR). The model predicted the *peak* reduction accurately but under-predicted the off-peak response (CTS 2017:2 p.14).

**Elasticities w.r.t. total trip cost** (CTS 2017:2; B-STO-012; ESTIMATED). Useful for Toronto's aggregate model, with care:
- Charged hours: **−0.70 at introduction (2006), rising to −0.86 (2011)**. Elasticity *grows* over time in Stockholm.
- Private cars only (excluding company cars, taxis and trucks): about −1.27 (2006), rising to just under −1.9.
- At introduction: **peak −0.49, off-peak −0.89**. Off-peak is about 1.8× more elastic, consistent with commuting trips being less elastic.
- The elasticity of the **2016 increase was lower** than at introduction. The most price-sensitive traffic had already gone, and a "zero-price effect" may apply.
- **Definition:** cost = 13 km × EUR 0.13/km (about EUR 1.95) + charge, in 2006 prices. This is *not* an elasticity w.r.t. the charge alone.
- Gothenburg (2013): −0.69 at introduction, declining to −0.52 (2015). Long-run elasticity can fall where transit alternatives are weak (Gothenburg transit share of commuting across the cordon about 25%, vs 75% in Stockholm; CTS 2017:2 p.12).

## Transit outcomes and complementary investment

**Expanded before launch.** From August 2005: new bus lines, 197 new buses and park-and-ride. The public-transport extension cost about **SEK 1.7bn** in total, including SEK 580M for buses and SEK 460M for new bus services (Eliasson WCTR; B-STO-006).

**Public transport travel +6%** (spring 2006 vs 2005). The **charges explain about 4.5 points**; higher petrol prices and other factors explain about 1.5 (B-STO-004).

**The bus expansion alone explained at most 0.1 percentage points of the 22% traffic drop.** Expanded transit in autumn 2005, before charging, had no measurable effect on transit trips (B-STO-005). The charge did the work, and the capacity absorbed it.

## Capital and operating costs

- **Trial charging system: about SEK 1.9bn total.** SEK 1.05bn was spent before launch; SEK 0.85bn was 2006 running and development costs (Eliasson WCTR; B-STO-006).
- CTS 2017:2 p.9 gives the **investment as about EUR 200M**, including planning, commissioning and first-year operation (B-STO-011).
- Hamilton (2011, cited in CTS 2017:2) says the main cost driver was **extreme resilience requirements** (redundant components, processes and staffing) **because of high political risk**.
- The call centre was heavily oversized: about 2,200 calls per day against 30,000 expected (Eliasson WCTR).
- **Operating cost:** estimated at about SEK 220M per year (Eliasson WCTR). Actual: **EUR 22M** in year 2 (CTS 2017:2 p.9), and **EUR 24M in 2013** for the Stockholm and Gothenburg systems combined.
- **Gothenburg** (2013) cost EUR 76M, about half for the national central system that replaced the original IBM-managed one. It was much cheaper because it reused Stockholm's proven design.

## Gross collections, net proceeds and use of revenue

- **Cost–benefit analysis (Eliasson 2009, via WCTR; MODELLED):**
  - annual toll revenue about **SEK 804M**;
  - financial surplus SEK 500–600M per year after operating costs;
  - social surplus about SEK 700M+ per year;
  - start-up cost recovered in social benefits in about **4 years**.
  - A critical counter-analysis (Prud'homme & Kopp 2006) found costs exceeding benefits. It is pre-steady-state and contested.
- **UNVERIFIED** (ITF table not accessible): EUR 70.9M (2008) → 140M (2016); operating share 31% → 12% → 7%; trial revenue SEK 399M (B-STO-017).
- **Earmarking history.** Revenue was first planned for public transport, then switched to roads in 2006. The **2007 agreement** created a transport investment package funded **50% by charge revenue and 50% by the national government**, with revenue earmarked for the **Stockholm Bypass**. The 2016 increase was partly directed to the Metro extension.
- CTS 2017:2 p.19 calls the 2007 deal **"a turning point for the political support"**. Local leaders had feared losing national infrastructure grants if they used charge revenue (B-STO-014).

## Technology and implementation

- **Technology.** The trial used transponders plus ANPR. The current system is ANPR with monthly invoice by default, and 25% pay by direct debit (CTS 2017:2 p.7).
- **The system "worked very well technically".**
- **Compliance was very high** and complaints far below expectations.
- **Procurement problems.** Legal complaints about the technology procurement shortened the trial period (Eliasson WCTR).
- **Businesses struggled** with administration and vehicle tracking at launch, which was fixed for the 2007 restart.

## Exemptions and mitigation

- About 30% of passages were exempt in the trial (B-STO-002).
- Alternative-fuel cars were exempt until 2012.
- Taxis were exempt in 2006.
- **Company cars** are 37% of passenger cars crossing the cordon. Charges were tax-deductible for some, which weakens the price signal (CTS 2017:2 p.2; B-STO-015).

## Public acceptance, communications, political

- **Polling (Eliasson WCTR; B-STO-008):** in autumn 2005, before the trial, about **55%** called it a bad decision. By April–May 2006 **53% said good, 41% bad**. Media coverage flipped from alarm to positive within weeks.
- **Referendum, 17 September 2006 (B-STO-009):** City of Stockholm **53% yes / 47% no**. Fourteen surrounding municipalities that held their own votes went **40% yes / 60% no**. Combined, 48/52, hard to interpret because many municipalities held no vote.
- The new national government reintroduced the charge in August 2007.
- **Political support** was low across parties except the Greens before 2006. All established parties came to support it, helped by the revenue/grant deal (CTS 2017:2 p.19).
- **Public support** kept rising in Stockholm but began declining in Gothenburg after its 2015 increase, which was imposed to co-finance the West Swedish Package (West Link, BCR 0.45), "not justified by congestion" (CTS 2017:2 p.20).

## What worked

- **The trial-then-referendum sequence let people experience the benefit** before voting. Support flipped from 55% negative to 53% positive.
- **Per-passage time-of-day charges with a daily cap**, plus shoulder steps.
- **Visible travel-time gains.**
- **Transit capacity added before launch** absorbed mode shift.
- **The earmark deal** (50/50 with the national government, a bypass) won political support.
- **Operating cost fell steeply** as the system matured.

## What didn't work

- **Very high start-up cost**, driven by political risk, an oversized call centre and time pressure. Eliasson: "investment could have been lower with less time pressure".
- **Suburban voters opposed** the charge (40% yes).
- **Using charge revenue to co-finance projects unrelated to congestion** (Gothenburg) eroded public support.
- **Company-car tax deductibility** blunted the price signal.

## Remaining uncertainty

- Revenue and operating-share series after 2008 (UNVERIFIED here).
- Distributional effects. Not covered this session; Eliasson & Mattsson 2006 exists but was not checked.

## Relevance for Toronto

Stockholm is the most transferable **process model**:
- a time-limited trial;
- evaluation published openly;
- a public vote, or Council mandate;
- then a permanent scheme.

Like Stockholm, Toronto needs **senior-government legislation** (City of Toronto Act s.41/s.116 regulation).

Use Stockholm's **trip-cost elasticities only as an explicitly labelled range** in Toronto's aggregate model. Toronto's transit share for trips crossing a downtown cordon should come from local data (TTS summaries, Census), not from Stockholm's 75%.
