# Rev0287 cube audit report

## What was audited

Rev0287 audits source-lineage semantics inside the datacube. Rev0286 made every route structurally complete, but the next defect was subtler: some records promoted ordinary broad citations into `source_currentness_refs`. A currentness ref should mean “this source must be refreshed because the route depends on a volatile legal, operational, litigation, implementation, quarterly, filing-season, AI-governance, or data-projection posture,” not “this source appears somewhere in the memo.”

## Findings

1. **S15 currentness contamination found and repaired.** The IEA AI-energy source was cited across many general calibration memos, but only data-center/frontier-AI capacity routes needed it as a volatile currentness anchor. Rev0287 leaves ordinary citations alone and confines `source_currentness_refs=S15` to the relevant AI/data-center records.
2. **Every currentness reference now has a local claim.** Records using `source_currentness_refs` now also carry `source_currentness_claims`, one per source ID, stating the current claim and the reason for future refresh.
3. **Registry entries now need route use.** The source-currentness registry is no longer allowed to collect dangling volatile sources that no cube route actually tracks.
4. **Beneficial-ownership reporting became currentness-aware.** The BOI registry route now tracks FinCEN's 2025 interim final-rule posture through S526/S527 rather than treating BOI status as a stable transparency premise.
5. **Global-minimum-tax coordination became currentness-aware.** The international coordination ladder now tracks OECD May 2026 central GloBE Information Return filing/exchange guidance through S652.

## Currentness audit counts

| Measure | Count |
|---|---:|
| Route records | 151 |
| Records with source-currentness refs | 19 |
| Total source-currentness refs | 41 |
| Registry entries | 35 |
| S15 currentness records after repair | 3 |

## S15 currentness records after repair

- `data_center_local_burden`
- `frontier_ai_host_market_controller_jurisdiction`
- `frontier_scarce_capacity_threshold`

## Editorial rule going forward

A source can be cited without being a currentness anchor. Promote a source into `source_currentness_refs` only when a route's answer would change if that source's status, date, implementation posture, rulemaking posture, litigation posture, quarterly factor, or official projection changed.
