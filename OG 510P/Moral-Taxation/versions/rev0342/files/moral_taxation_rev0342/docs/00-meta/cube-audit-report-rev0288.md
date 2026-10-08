# Rev0288 cube audit report

## What was audited

Rev0288 audits the remedy/incidence layer. Rev0287 separated ordinary citations from currentness dependencies; the next structural defect was that a route could carry `remedy_type` values without a machine-readable statement of what the remedy actually does.

## Findings

1. **Remedy labels were too weak.** A route could say `rebate`, `waiver`, `audit`, `fallback_channel`, or `clawback` while leaving the default move, blocked move, escalation trigger, and proceeds rule implicit.
2. **A separate remedy-profile layer is better than adding more axes.** The 23 axes remain the classifier. `docs/00-meta/remedy-profiles.json` now carries the operational remedy spine for every route.
3. **Profiles are complete for the whole cube.** Every route record now has one remedy profile tied to family, incidence problem, guardrails, escalation, source-currentness linkage, and proceeds-integrity posture.
4. **The source-currentness layer remained disciplined.** Rev0288 did not turn remedy sources into currentness refs; existing currentness refs remain legal/operational refresh dependencies.

## Counts

| Measure | Count |
|---|---:|
| Route records | 152 |
| Calibration files | 150 |
| Remedy profiles | 152 |
| Source-currentness-tracked records | 19 |
| Source-currentness refs | 41 |

## Editorial rule going forward

Do not approve a route because its `remedy_type` sounds right. Ask whether the remedy profile identifies who is repaired, what move is blocked, when escalation happens, and whether proceeds are traced or deliberately not applicable.
