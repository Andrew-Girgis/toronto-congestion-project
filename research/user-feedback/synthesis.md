# User feedback synthesis

**Status:** n = 1 conversation (UF-001), in person at the buildathon, 2026-10-24. The participant's name is withheld until they consent to being named. Notes were taken by the project lead and are paraphrased, not recorded verbatim.

One conversation is a signal, not a representative sample. More conversations should be logged in `log.csv` using `protocol.md`.

## Themes and what we changed

| # | What we heard | What we changed in the product | Where |
|---|---|---|---|
| 1 | Population growth could be miscalculated | Growth is an explicit assumption with low/base/high and sensitivity. We do not scale traffic one-for-one with population. | `config/assumptions.yaml`, finance model |
| 2 | Where in Toronto, and when? | Candidate boundaries compared on the map; a time-of-day scenario (S3); charging hours shown plainly | map, S3 |
| 3 | Charging one approach (e.g. the 401 from the west) can feel like discrimination against those commuters | Approach-direction burden view: inbound crossings by side of the city against the transit alternatives on that side | equity panel |
| 4 | Predict the money raised | 10-year financial model with gross vs net, ranges, and the trade-off that more congestion relief can mean less revenue | finance panel |
| 5 | Learn from Singapore, London, NYC and Stockholm: their struggles, costs, communications, what worked and what didn't | Per-city lessons table, protected from scope cuts | international panels |
| 6 | Stockholm and NYC have clear choke points; Toronto drivers could cut through neighbourhoods, though the participant expects most to choose "pay and arrive fast" over "take much longer and save" | **Tested, not assumed:** the SUMO reroute run measures how much traffic diverts onto boundary-neighbourhood streets and the travel-time penalty for doing so. Boundary options are scored on the number of crossings and natural choke points. | simulation, boundary comparison |
| 7 | Spend revenue on electrifying above-ground transit (GO, UP Express) | Added as a revenue-use option. To check: GO/UP are provincial (Metrolinx) assets, and part of their electrification may already be funded under GO Expansion. | adoption, finance |

## Open questions for the next conversations
- Would a charge change how *you* get downtown? What would you switch to?
- Which design feels fairer: per entry, per day, or time-varying?
- Who do you worry would be hurt most?
- What would the money need to be spent on for you to support it?
