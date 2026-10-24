# Singapore: Electronic Road Pricing (ERP), first gantries 1 April 1998; Restricted Zone from September 1998

Workstream B case file. Researched 2026-10-24. Source IDs refer to `research/sources_B.csv`.

**This is a separate intervention from ALS (1975).** It replaced ALS paper licences in the Restricted Zone and the Road Pricing Scheme on expressways.

**Primary or near-primary sources read this session**
- Menon, A.P.G. & Guttikunda, S. (2010), *Electronic Road Pricing: Experience & Lessons from Singapore*, SIM-air Working Paper Series 33-2010: https://urbanemissions.info/wp-content/uploads/docs/SIM-33-2010.pdf. Menon is a former LTA Chief Transportation Engineer. Cited as "Menon 2010".
  - **Correction:** `data-sources.md` cites this as "Chin (2010), SIM Series 33". The SIM 33 author list is Menon & Guttikunda.
- LTA rate-review news releases (2025–2026).

## Charge design and changes over time

**Per passage, per gantry, no daily cap.**
- Rates vary by gantry, vehicle class and half-hour slot (Menon 2010 pp. 3–6).
- Motorcycles pay half the car rate.
- Paper ALS allowed unlimited entries on one licence, which Menon describes as "not keeping in the spirit of… congestion pricing". **Per-use charging was the reason for ERP** (Menon 2010 p.3).

**Rate-setting rule.** Rates are reviewed **quarterly** against target speed bands: **20–30 km/h on arterials/downtown and 45–65 km/h on expressways** (B-ERP-003).
- Below the lower bound, the half-hour rate rises. Above the upper bound, it falls.
- Since 2008 the review uses the **85th-percentile speed**, not the mean, and rate changes are in S$1 steps (Menon 2010 pp. 3, 6).
- LTA's March 2026 release still cites the 45–65 and 20–30 km/h bands. Its September 2026 release confirms continued quarterly reviews.

**Growth.** Gantries expanded to 66 by 2009 (Menon 2010 p.4). Saturday charging was added in 2005. Foreign vehicles can pay a flat S$10/day option.

**ERP 2.0** (satellite/GNSS on-board units). Contract awarded in 2016 to the NCS–MHI consortium for **S$556M** (MOT parliamentary reply 2023, via search excerpt; B-ERP-006, UNVERIFIED). Full transition is around 2026–2027. Distance-based charging is technically possible but not planned.

## Traffic, speed and reliability outcomes

Source: Menon 2010 p.8 [PDF p.10]; "initial traffic monitoring"; B-ERP-002.

| Metric | Result | Label |
|---|---|---|
| Expressway volumes, ERP hours | **−15%** | OBSERVED (REPORT) |
| Expressway speeds, ERP hours | **35 → 55 km/h** | OBSERVED (REPORT) |
| AM peak reduction | about −14% | OBSERVED (REPORT) |
| Restricted Zone traffic | **−16%**; speeds 25–35 km/h | OBSERVED (REPORT) |

**These are early monitoring figures.** Menon 2010 gives no exact before/after periods, and they are not causal estimates. The comparison is ERP vs the *already-priced* ALS/RPS baseline, so the −16% is an increment on top of earlier pricing.

**Long-run pattern.** The city-entry series on data.gov.sg (weekdays 07:30–19:00) runs from 246,000 (2004) to 293,699 (2025) (`docs/access-audit.md`; B-ERP-008). ERP *manages* volume against growth through rate adjustment rather than shrinking it.

**UNVERIFIED claims in `data-sources.md`:**
- "about 23% of ALS-era trips were repeat entries" (B-ERP-007): the per-use rationale is confirmed (Menon 2010 p.3), but the 23% figure was not found.
- "no significant modal shift in year one (Olszewski 1999)" (B-ERP-010): not checked.
- Olszewski & Xie (2005, *TR-A* 39) found elasticity higher for cars and higher on expressways than at the city cordon (abstract only).

## Transit and complementary measures

- **There was no bundled transit package at ERP launch** comparable to Stockholm's or London's.
- Long-run ridership growth in Singapore is driven by MRT expansion, bus contracting, population and the COE ownership cap. It is not attributable to ERP.

## Capital and operating costs

**From Menon 2010 p.4 [PDF p.6]; B-ERP-001:**
- **Capital cost S$197M**, "since its inception in September 1998".
- **Operation and maintenance about S$25M/year** for 66 gantries (2009).
- **In-vehicle units were given free to all existing vehicles in 1998.** A new unit cost about S$155 at the time of the paper (p.4 [PDF p.6]); the free fitting for existing vehicles is stated on p.8 [PDF p.10].

`data-sources.md`'s "about S$80M/year gross, S$16M operating around 2003" (Menon & Chin 2004) was not verified. A secondary case study (development.asia) repeats S$200M capital / S$16M O&M / S$80M revenue (UNVERIFIED).

## Revenue and use

- **Revenue is estimated at S$144M in 2008–09** (Menon 2010 p.4). O&M of S$25M is about 17% of revenue.
- **Secondary, UNVERIFIED (B-ERP-005):**
  - "about $100M per year" (Transport Minister, 2008 Committee of Supply);
  - S$116–159M per year in 2009–2011 (2012 parliamentary disclosure via press).
- **Not ring-fenced.** Revenue goes to the Consolidated Fund. This is per `data-sources.md` and widely reported, but not re-verified this session (B-ERP-009).
- **Do not conflate with COE.** Certificate of Entitlement auction revenue is a separate, much larger fiscal instrument.

## Technology, procurement and implementation

- **Technology:** dedicated short-range communications between gantries and an in-vehicle unit, with a stored-value CashCard (Menon 2010 pp. 4–7).
- **Search for an automatic system began in 1989.**
- **Rollout:** units fitted to about 900,000 vehicles, then a **trial period with all charges set to zero**, so motorists could test units and cards.
- **Reliability:** in August 1999, 5.8M transactions/month with **0.03% error** and 0.7% violations, mostly forgotten CashCards (Menon 2010 p.7; B-ERP-004).

**Menon's lessons (Box 3, p.9):**
- tailor the system to local traffic; off-the-shelf equipment is not adequate;
- perceived reliability is everything, so test exhaustively;
- plan unit fitting to avoid hassle;
- invest heavily in user education and media.

## Exemptions and mitigation

- Emergency vehicles are exempt.
- Public buses on designated routes pay; costs are borne by operators (MOT written reply 2023, via search; UNVERIFIED).
- Motorcycles pay half.
- No income-based discounts were found.

## Public acceptance and communications

- **Extensive publicity** before launch, including newspaper campaigns. From the first day the system "worked smoothly" (Menon 2010 p.8).
- **Rate changes are kept routine** by the published speed-band rule and quarterly cadence. This depoliticises pricing.
- **No electoral or referendum test** in Singapore's governance context.

## What worked

- **A per-use rule** priced repeat entries that the ALS day licence did not.
- **A transparent, formula-based rate review** (speed bands, quarterly).
- **A free unit rollout plus a zero-charge trial.**
- **High reliability.**
- **Long-run volume management** against growth.

## What didn't work or remains uncertain

- **Revenue transparency is poor.** No official ERP-only revenue series was found after about 2014.
- **No measurable mode-shift evidence** was verified this session.
- **Rate-setting by speed bands targets flow efficiency, not equity**, and per-gantry charges can push traffic onto unpriced parallel roads. Not quantified here.
- **ERP 2.0's final cost and privacy implications** (GNSS tracking) remain open.

## Relevance for Toronto

1. **A published rate-adjustment rule** (target speed bands, a fixed review cadence, small steps) keeps later increases technocratic rather than political. It is directly transferable as a governance design.
2. **Per-passage charging prices repeat trips.** A once-per-day cap (NYC) leaves them unpriced.
3. **Use a zero-charge trial period** for technology shake-out.
4. **Do not cite Singapore as a transit-funding model.** Its revenue goes to general funds, and its traffic outcomes are inseparable from the COE ownership quota.
