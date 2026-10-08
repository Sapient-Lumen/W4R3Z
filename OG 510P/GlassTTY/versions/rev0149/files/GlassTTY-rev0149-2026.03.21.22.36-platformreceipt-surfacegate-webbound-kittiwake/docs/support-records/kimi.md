# Support record — Kimi

## Metadata
- **surface key:** `kimi`
- **record status:** `seeded`
- **default browser lane:** `chromium-live`
- **last reviewed:** `2026-03-19`
- **rollout priority:** `phase-3`

## Scope and assumptions
Official surface to widen coverage beyond the most common western chat surfaces.

## Workflow rows

| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |
|---|---|---|---|---|---|
| surface-detect | investigated | chromium-live | profile seeded; no formal evidence yet | surface not yet implemented in-tree | capture first baseline and support bundle |
| receiver-resolve | investigated | chromium-live | profile seeded; no formal evidence yet | surface not yet implemented in-tree | capture first baseline and support bundle |
| composer-read | investigated | chromium-live | profile seeded; no formal evidence yet | surface not yet implemented in-tree | capture first baseline and support bundle |
| composer-write | investigated | chromium-live | profile seeded; no formal evidence yet | surface not yet implemented in-tree | capture first baseline and support bundle |
| turn-submit | investigated | chromium-live | profile seeded; no formal evidence yet | surface not yet implemented in-tree | capture first baseline and support bundle |
| generation-read | investigated | chromium-live | profile seeded; no formal evidence yet | surface not yet implemented in-tree | capture first baseline and support bundle |
| latest-turn-read | investigated | chromium-live | profile seeded; no formal evidence yet | surface not yet implemented in-tree | capture first baseline and support bundle |
| support-capture | investigated | chromium-live | profile seeded; no formal evidence yet | surface not yet implemented in-tree | capture first baseline and support bundle |

## Known blockers and risk notes
- layout and localization variation
- compose/submit cues may differ materially
- limited prior evidence in repo

## Baseline capture plan
- open the main logged-in route for the surface
- confirm `surface-detect` and `receiver-resolve` first
- capture at least one composer state snapshot and one route/diagnostics snapshot
- treat the first useful failed run as evidence, not as wasted work

## Promotion notes
- To reach `experimental`, this surface needs at least one named support bundle or equivalent artifact for one lane.
- To reach `provisional`, the record needs current evidence, known caveats, and clearer drift posture.
- Stronger claims without named artifact refs should be treated as incomplete.

## Next action
Capture first baseline and record route/composer conventions before designing adapter logic.
