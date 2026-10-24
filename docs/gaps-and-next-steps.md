# Gaps, validation status and next milestones

## Data gaps (and what fills them)

| Gap | Effect tonight | Fills it | Access |
|---|---|---|---|
| **Expressway volumes** (Gardiner, DVP): the RESCU detector feed is not on the open portal | Expressway flows are not calibrated. S1 (Gardiner/DVP toll) is illustrative only, and cordon revenue misses some expressway entries. | City RESCU loop data | City-held: in the 90-day pilot |
| **Who pays, by home area and income**: no public trip-level origin–destination data | No payer-by-home-area or income claims; context only | TTS 2022 cross-tabulations (U of T DMG iDRS) | Account conditions unverified; possible through the City's existing relationship |
| **Current corridor travel times**: Bluetooth data on the portal stops in 2017 | Simulated speeds can't be checked against observed travel times | City probe or Bluetooth data; commercial probe data | City-held / licensed |
| **Counts on different days at each site** | Combined as one typical weekday (labelled assumption) | A coordinated cordon count on one day | City field program |
| **Full-day profile, inbound only** | Measured all-direction AM share (27.6% of 06:00–19:00, 652 City 14-hour counts) used as a proxy; inbound share likely higher (pessimistic bound 33%) | Directional 14-hour counts on the cordon crossings | Open (partly done) |
| **Ride-hail share at the cordon** | City-wide AM share (11.6% of downtown vehicle-km) applied as a stand-in | PTC trip files 2018–2026 on the portal (zone-level origin and destination) | Open: next step |
| **Toronto-specific behavioural response** | Calibrated to the international band | Stated-preference survey, or TTS-based mode-choice model | Survey / restricted |
| **Legal status of a zone charge on City streets** under re-enacted s.41 | No claim either way (UNVERIFIED) | City Legal opinion | City |

## Validation status
- **Baseline:** fitted to ~80% of counted intersections. Fit and held-out GEH are reported in the demo (`metrics.json`). Expressways are uncalibrated.
- **Scenarios:** simulated with a one-shot reroute; no equilibrium iteration. The emergent reroute share is compared with London's 20–30% as a plausibility check.
- **Finance:** bottom-up from charged trips. International operating-cost ratios are used only as reasonableness bounds.
- **Not done:** sensitivity of the SUMO results to demand (±20%) and to the value of time; a second assignment iteration.

## Next milestones
1. Directional (inbound-only) AM share at C1 crossings (refines the measured 27.6% all-direction share).
2. Ride-hail share at the cordon from PTC trip files (replaces a stand-in).
3. Full-day simulation (06:00–19:00) and a dynamic user-equilibrium iteration (`duaIterate`).
4. Run C2 and C3 in SUMO, so boundary choice is tested on diversion as well as crossings.
5. Restricted-data integration in the pilot: RESCU, TTS cross-tabulations, probe travel times. Each goes through a data-sharing agreement and a Privacy Impact Assessment scope check.
6. More user conversations (protocol in `research/user-feedback/protocol.md`), especially drivers from the 905 region and people living in boundary neighbourhoods.
