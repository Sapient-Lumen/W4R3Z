# Support record — Claude

## Metadata
- **surface key:** `claude`
- **record status:** `backfilled-from-evidence`
- **default browser lane:** `chromium-live`
- **last reviewed:** `2026-03-20`
- **rollout priority:** `reference adapter`
- **approved source baseline:** `claude-product-overview + shared-browser-substrate`

## Scope and assumptions
Current reference adapter and strongest real lane in the repo. The record is now backfilled from named repo-current artifacts, but it still lacks a live official-surface bundle for the current archive.

## Workflow rows

| workflow | current tier | lane | evidence refs / posture | caveats | promotion requirement |
|---|---|---|---|---|---|
| surface-detect | experimental | chromium-live | held bundle `claude-reference-chromium-live-rev0128`; reference adapter plus repo-current truth surfaces are named | live route/layout variants still need official-surface capture | attach one live route/state bundle and confirm current selector posture |
| receiver-resolve | experimental | chromium-live | held bundle `claude-reference-chromium-live-rev0128`; receiver work exists in current adapter/probe surfaces | multi-frame ambiguity can still matter on the live surface | backfill one live receiver audit and frame-resolution artifact |
| composer-read | experimental | chromium-live | held bundle `claude-reference-chromium-live-rev0128`; adapter notes plus synthetic fixture baseline are named | current live editor model still lacks a dated official-surface artifact | capture before/after composer state on a live Claude route |
| composer-write | experimental | chromium-live | held bundle `claude-reference-chromium-live-rev0128`; write path exists in the reference adapter story | writeback semantics still need live readback-confirmed proof | capture one official-surface readback-confirmed action outcome |
| turn-submit | experimental | chromium-live | reference adapter intent exists, but the new held bundle stops short of claiming live submit proof | no current official-surface submit bundle is named yet | capture real submit support bundle with before/after state and route witness |
| generation-read | investigated | chromium-live | held bundle `claude-reference-chromium-live-rev0128` records repo-current truth but not live generation proof | state classification still needs formal lane proof on the official surface | capture post-submit generation snapshots from a live route |
| latest-turn-read | experimental | chromium-live | held bundle `claude-reference-chromium-live-rev0128`; latest-turn read remains part of the reference story | parsing rules and partial-vs-complete evidence still need a dated live artifact | capture a live latest-turn snapshot artifact |
| support-capture | experimental | chromium-live | held bundle `claude-reference-chromium-live-rev0128` plus queue/contract surfaces now exist | live official-surface bundle still missing, so publication remains on hold | capture one live support bundle and promote it from hold to published-ready |


## Source authority posture
The source lock now names one first-party Claude product anchor plus shared browser/runtime references for MV3 lifecycle, native messaging, and route/history semantics. Those sources justify product/runtime framing, but they still do not replace the live official-surface workflow evidence this record is missing.

## Known blockers and risk notes
- route/layout variation over time
- receiver ambiguity in complex frame states
- streaming/partial latest-turn classification drift
- current named support bundle is intentionally held pending live official-surface proof

## Baseline capture plan
- open the main logged-in route for the surface
- confirm `surface-detect` and `receiver-resolve` first
- capture at least one composer state snapshot and one route/diagnostics snapshot
- treat the first useful failed run as evidence, not as wasted work

## Promotion notes
- `experimental` is now backed by the held bundle `claude-reference-chromium-live-rev0128`, but that bundle is still intentionally weaker than a live official-surface proof packet.
- To reach `provisional`, the record needs current live evidence, known caveats, and a publishable support bundle for one lane.
- Stronger claims without named official-surface artifact refs should be treated as incomplete.

## Update history
- `2026-03-20` — backfilled from evidence using held bundle `claude-reference-chromium-live-rev0128`, support-surface snapshot, control-plane report, and current operator handoff artifacts

## Next action
Capture one live logged-in Claude bundle, then promote the held bundle or replace it with a publishable official-surface support bundle.
