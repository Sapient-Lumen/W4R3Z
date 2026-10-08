# Support record template

Use this template for `docs/support-records/<surface>.md`.

# Support record — <Surface name>

## Metadata
- **surface key:** `<surface-key>`
- **record status:** `seeded` | `backfilled-from-evidence` | `current` | `stale`
- **default browser lane:** `<lane-key>`
- **last reviewed:** `<YYYY-MM-DD>`
- **rollout priority:** `<reference|second-adapter|phase-2|phase-3>`

## Scope and assumptions
- supported URL family or route family
- auth/session assumptions
- current intended browser lanes
- important compose/receiver assumptions

## Workflow rows

| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |
|---|---|---|---|---|---|
| surface-detect | investigated | chromium-live | no formal record yet | route drift possible | capture one named support bundle |
| receiver-resolve | investigated | chromium-live | no formal record yet | multi-frame ambiguity unknown | capture receiver audit |
| composer-read | investigated | chromium-live | no formal record yet | editor model not yet audited | produce before/after state snapshot |
| composer-write | investigated | chromium-live | no formal record yet | writeback semantics unknown | verify readback and action outcome |
| turn-submit | investigated | chromium-live | no formal record yet | submit control not yet audited | capture first real submit bundle |
| generation-read | investigated | chromium-live | no formal record yet | streaming cues unknown | classify state transitions |
| latest-turn-read | investigated | chromium-live | no formal record yet | parsing rules not yet stable | capture turn snapshot |
| support-capture | investigated | chromium-live | no formal record yet | bundle schema still being formalized | write first named support bundle |

## Known blockers and risk notes
- route/layout variance
- iframe or frame targeting concerns
- streaming or virtualization concerns
- modal/interstitial concerns
- auth/session caveats

## Baseline capture plan
- first route to open
- first workflow to prove
- minimum artifact set to capture
- what counts as a useful failed run

## Promotion notes
- what is needed to reach `experimental`
- what is needed to reach `provisional`
- what evidence would still be insufficient

## Update history
- `<YYYY-MM-DD>` — seeded/backfilled/updated/promoted/demoted/staled with short note and evidence refs

## Next action
- the single highest-leverage next capture or implementation step
