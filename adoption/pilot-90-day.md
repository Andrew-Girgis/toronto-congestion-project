# 90-day pilot: Congestion Cordon at City of Toronto Transportation Services

**The ask (step 1 of 2):** Transportation Services runs this open tool on its internal data for 90 days and publishes what it finds. That is a low-cost, reversible decision within City authority.

**Step 2, only if the evidence holds:** a staged path toward a time-limited pricing trial (the Stockholm model: transit capacity first → trial → open evaluation → public decision). Since June 2025 this needs an **Act of the Ontario Legislature**:
- The *Plan to Protect Ontario Act (Budget Measures), 2025*, S.O. 2025 c.10, Sched. 2, re-enacted City of Toronto Act s.41: the City "does not have the power to designate, operate or maintain a highway as a toll highway". It also repealed the s.116 regulation route (verified against the ola.org Bill 24 explanatory note).
- The Gardiner and DVP are scheduled to transfer to the Province in fall 2027 (research D-012). The *Get It Done Act, 2024* bars tolls on provincial highways unless an Act authorises them (D-011).

The pilot does **not** ask the City to price anything.

## Owner and partners

| Role | Who | Why |
|---|---|---|
| Lead | **Transportation Services**: the data, analytics and traffic-modelling staff who run the count program | Owns the TMC/SVC count program this tool is built on, plus the expressway detector (RESCU) data the open portal lacks |
| Partner | **City Planning**, Transportation Planning | Boundary options, growth assumptions, consultation |
| Partner | **TTC**, service planning | Transit capacity on corridors feeding the zone; bus-speed effects |
| Partner | **Technology Services** | Hosting on City infrastructure; security review |
| Advisory | City privacy/access office (MFIPPA) | Privacy Impact Assessment scope |
| External (optional) | U of T Data Management Group | TTS origin–destination tabulations under the City's existing relationship (UNVERIFIED) |

Verify current division and unit names before presenting.

## Plan

| Days | Work | Deliverable | Gate |
|---|---|---|---|
| 1–30 | Deploy on City infrastructure (Python + SUMO + DuckDB; no licences). Add expressway detector volumes and the latest internal counts. Recalibrate the morning baseline; extend to a full weekday. | Calibration report: held-out GEH, coverage map | Baseline reproduces held-out counts. Target GEH < 5 at ≥ 85% of intersection-hours. |
| 31–60 | Run boundary options (C1 Bathurst–Parliament, C2 Bathurst–Don, C3 Dufferin–CP rail–Don), charging hours and rates. Check diversion against City-held travel-time data. Add TTS-based who-pays analysis if obtainable. | Options comparison: traffic, boundary-street diversion, revenue, costs, equity | Results stable across low/base/high and ±20% demand |
| 61–90 | Publish the open method and results. Brief Council. Run neighbourhood consultation on the diversion findings. | Public report + open repository + Council briefing note | **Decision:** stop, or commission a formal feasibility study |

## Success metrics
- Calibration and validation published, including failures.
- Every number in the public report labelled observed / estimated / simulated.
- An options table Council can act on, including a "do not proceed" option.
- No personal information processed (see `data-privacy.md`).

## Cost
See `cost.md`: about **C$50k–80k** in staff time over 90 days (ASSUMPTION), with no software licence cost.
