# Data and privacy plan

## What the tool uses today
- **Aggregate traffic counts only:** City of Toronto Open Data intersection (TMC) and midblock (SVC) counts, the road centreline, and neighbourhood boundaries and profiles; OpenStreetMap roads; published reports.
- **No personal information:** no licence plates, no individual trips, no device IDs, no names. Simulated "vehicles" are synthetic agents fitted to counts.

## What the pilot would add (City-held, aggregate)
- Expressway detector (RESCU) volumes and speeds, latest counts, and corridor travel times. All are aggregate.
- Optionally, TTS origin–destination **tabulations** (aggregated by zone, with small cells suppressed), not microdata.

Data stays on City infrastructure. Outputs published openly are aggregate and labelled.

## If the City later considers an actual charge
Enforcement would involve licence-plate images: personal information under **MFIPPA** (Municipal Freedom of Information and Protection of Privacy Act). Before any such step:
- Privacy Impact Assessment and public summary
- Data minimisation: plate reads used only for charging and enforcement, then deleted on a fixed schedule
- Strict access controls and audit logging; no secondary use (for example policing) without a legal basis and public notice
- Lessons from elsewhere: Singapore's satellite-based ERP 2.0 drew privacy questions (research B), and London and Stockholm operate camera enforcement with published retention rules (details to confirm)

## Openness
Code, configuration, assumptions and source register are public in this repository. Every published number carries its label (observed / estimated / simulated / assumption / unverified).
