# Validation status

*Updated 2026-10-24. Numbers come from `web/public/data/metrics.json` (`validation`), written by `cordon.export.web`.*

## Summary
The street-level baseline is **below the usual calibration target**, and the demo says so on screen. Treat street-level results as indicative scenario comparisons, not forecasts. Recalibrating on the City's internal data (expressway detectors, signal timings, current counts) is the first task of the 90-day pilot.

## Held-out test
About 20% of counted intersections (111 of 555, fixed seed 42) were withheld from fitting. Modelled S0 flows are compared with City counts per approach (all movements entering an intersection from one leg) and hour, 06:00–10:00.

| Metric | Fitted sites | Held-out sites |
|---|---|---|
| Approach-hours within GEH 5 | 57% | **43%** |
| Approach-hours within GEH 10 | 79% | 71% |
| Intersection-hours within GEH 5 | 37% | 39% |
| Modelled ÷ counted vehicles | 77% | 86% |
| Correlation (approach volumes) | 0.82 | 0.74 |

A common target for assignment models is GEH < 5 at 85% or more of count locations (UK TAG/DMRB). We report it for transparency, not as a pass/fail claim.

## What we tried, and why the method changed
1. **SUMO microsimulation** of the counts-fitted demand (279k vehicles, 06:00–10:00): too slow for the timebox, and congested.
2. **SUMO mesoscopic, full junction control:** network-wide deadlock. Mean speed for 08:00 departures was 4.8 km/h, and only 45% of vehicles finished.
3. **Mesoscopic with signal-delay penalties** (two variants): still about 120k vehicles that never entered the network.
4. **Longer candidate trips** (132k vehicles, same counts): still jammed, with 17k vehicles teleported out of jams. That ruled out demand volume as the main cause.
5. **Network rebuilt without ramp guessing:** still jammed. The jams started at low volume (about 520 veh/h on a three-lane arterial) where arterials meet expressway ramps (Lake Shore West near the Gardiner ramps; Bayview at the Bayview/Bloor/DVP ramps) and spread backwards. We concluded this was a network-build defect we could not fix within the timebox.
6. **Static equilibrium assignment** (AequilibraE, BPR curves, hourly): cannot gridlock. Re-routing *all* trips, though, moved traffic off the counted arterials (held-out approach-hours within GEH 5: 27%).
7. **Hybrid (current):** trips that never touch a charged link keep their counts-fitted routes as fixed traffic; only trips that touch a charged link choose routes in equilibrium, with the toll converted to time. Held-out approach-hours within GEH 5 rose to 43%.

The fitted routes alone, with no re-routing at all, score 51% within GEH 5 on held-out approach-hours.

## Known biases
- **Speed gains likely understated.** No queues or signal timings, and a baseline less congested than real mornings. Zone street speed changes by about 1%, against New York's estimated +11%.
- **Diversion likely overstated.** A single value of time (C$12.58 ≈ 30 minutes of detour) and no driver habit.
- **Fixed traffic can't move.** Trips on fixed routes can't avoid newly busier boundary streets, which overstates the extra delay those streets cause.
- **Expressways are uncalibrated.** There are no open counts for the Gardiner or DVP.
- **Counts come from different days** at each site and are combined as one typical weekday.

## Sanity checks done
- Model invariants and data checksums: `make check` (8 tests).
- AM share of daily traffic measured from 652 City 14-hour counts (27.6%) instead of assumed.
- Collections cross-checked against charged vehicles × rates. Foreign revenue per entry is not transferred.
- The map colour bug, where volume and "fewer vehicles" shared the same blue, was found in user review and fixed.
