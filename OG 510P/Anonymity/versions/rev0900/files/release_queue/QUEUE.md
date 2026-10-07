# Queue Ledger

_Generated from `release_queue/QUEUE_INDEX.json` and `release_queue/LATEST_DECISION.json`. Do not edit by hand; rerun `python3 -B publishing/render_queue_surfaces.py --root .` or `make rebuild-surfaces`._

## Current status

- Generated for revision: `rev0900`
- Latest decision note: `release_queue/decisions/2026.06.18-1154-obschannel-counterexamples-modelbinding-validatorcut-no-publication.md`
- Latest decision summary: Rev0900 (`Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip`) repairs a release-adjacent inference that treated a scalar observation probability as an independent erasure channel. Equal per-secret reveal rates do not determine the conditional output law: an explicit three-secret cyclic-reveal mechanism has reveal probability one half for every secret, yet leaks one full bit and permits exact recovery with probability two thirds. The scalar-erasure calculation reports only 0.321928094887 bits and exact recovery 5/12, so it is not a certificate for that mechanism.
- Published queue: 7 post-policy Anonymity publications
- Locally reviewed / publication-blocked (`published_ready`): 8 explicit entries
  - `release_queue/published_ready/2026.03.16-paperA-release-property-published-ready.md`
  - `release_queue/published_ready/2026.03.16-paperA-schedule-only-retries-published-ready.md`
  - `release_queue/published_ready/2026.03.16-paperB-anondht-profiling-published-ready.md`
  - `release_queue/published_ready/2026.03.16-paperC-abom-oinl-published-ready.md`
  - `release_queue/published_ready/2026.03.16-paperD-spectral-delegation-published-ready.md`
  - `release_queue/published_ready/2026.03.17-paper1-notarized-certificates-published-ready.md`
  - `release_queue/published_ready/2026.03.17-paperB-auditable-trace-published-ready.md`
  - `release_queue/published_ready/2026.03.17-paperC-disagreement-recertification-published-ready.md`
- Candidate queue: 5 explicit entries
  - `release_queue/candidates/2026.03.16-paper1A-notarized-addendum-candidate.md`
  - `release_queue/candidates/2026.03.16-paper1A-state-calibration-addendum-candidate.md`
  - `release_queue/candidates/2026.03.16-paper2-advantage-contracts-candidate.md`
  - `release_queue/candidates/2026.03.16-paper2A-psc-q-addendum-candidate.md`
  - `release_queue/candidates/2026.03.16-paper3A-cppc-addendum-candidate.md`
- Hold queue: 61 explicit entries
  - `release_queue/hold/2026.03.16-congestion-series-index-hold.md`
  - `release_queue/hold/2026.03.16-paper17-worked-example-hold.md`
  - `release_queue/hold/2026.03.16-paperA-bossfight-observation-channel-repair-hold.md`
  - `release_queue/hold/2026.03.16-paperA-posterior-mass-true-odds-repair-hold.md`
  - `release_queue/hold/2026.03.16-paperB-addendum-independence-scenario-hold.md`
  - `release_queue/hold/2026.03.17-paper2-mucc-contact-cost-privacy-nonclaim-hold.md`
  - `release_queue/hold/2026.03.17-paper3-closed-view-alert-cap-repair-hold.md`
  - `release_queue/hold/2026.03.17-paperB-mceq-support-discipline-hold.md`
  - `release_queue/hold/2026.03.17-paperB-observation-channel-witness-hold.md`
  - `release_queue/hold/2026.03.17-paperC-model-binding-gate-hold.md`
  - `release_queue/hold/2026.03.19-paper12-receipt-line-items-schema-hold.md`
  - `release_queue/hold/2026.03.19-paper18-plan-state-equivalence-hold.md`
  - `release_queue/hold/2026.03.19-paper20-auditor-replay-hold.md`
  - `release_queue/hold/2026.03.19-paper24-math-backbone-crosswalk-hold.md`
  - `release_queue/hold/2026.03.19-paper31-downstream-normal-forms-hold.md`
  - `release_queue/hold/2026.03.19-paper32-release-spine-hold.md`
  - `release_queue/hold/2026.03.19-paper33-release-obligations-hold.md`
  - `release_queue/hold/2026.03.19-paper34-status-envelopes-hold.md`
  - `release_queue/hold/2026.03.19-paper54-answer-review-menus-hold.md`
  - `release_queue/hold/2026.03.19-paper55-series-spines-hold.md`
  - `release_queue/hold/2026.03.19-paper6-artifact-policy-hold.md`
  - `release_queue/hold/2026.03.19-paper60-public-request-carryforward-hold.md`
  - `release_queue/hold/2026.03.19-paper61-public-request-notices-hold.md`
  - `release_queue/hold/2026.03.19-paper62-notice-normal-forms-hold.md`
  - `release_queue/hold/2026.03.19-paper63-notice-selections-hold.md`
  - `release_queue/hold/2026.03.19-paper64-response-menus-hold.md`
  - `release_queue/hold/2026.03.19-paper65-response-packets-hold.md`
  - `release_queue/hold/2026.03.19-paper66-packet-carryforward-hold.md`
  - `release_queue/hold/2026.03.19-paper67-packet-delta-ledgers-hold.md`
  - `release_queue/hold/2026.03.19-paper68-refresh-notices-hold.md`
  - `release_queue/hold/2026.03.19-paper69-refresh-notice-normal-forms-hold.md`
  - `release_queue/hold/2026.03.19-paper70-refresh-notice-selections-hold.md`
  - `release_queue/hold/2026.03.19-paper71-successor-response-menus-hold.md`
  - `release_queue/hold/2026.03.19-paper72-successor-response-packets-hold.md`
  - `release_queue/hold/2026.03.19-paper73-request-side-terminal-hold.md`
  - `release_queue/hold/2026.03.19-paper74-paired-terminal-discipline-hold.md`
  - `release_queue/hold/2026.03.19-paper75-paired-terminal-cutover-hold.md`
  - `release_queue/hold/2026.03.20-paper58-request-fulfillment-certificates-hold.md`
  - `release_queue/hold/2026.03.20-paper59-public-request-status-envelopes-hold.md`
  - `release_queue/hold/2026.03.21-paper35-sentence-locks-hold.md`
  - `release_queue/hold/2026.03.21-paper36-challenge-routes-hold.md`
  - `release_queue/hold/2026.03.21-paper37-challenge-stop-profiles-hold.md`
  - `release_queue/hold/2026.03.21-paper38-challenge-branch-maps-hold.md`
  - `release_queue/hold/2026.03.21-paper39-challenge-coverage-certificates-hold.md`
  - `release_queue/hold/2026.03.21-paper40-challenge-surface-hooks-hold.md`
  - `release_queue/hold/2026.03.21-paper41-challenge-terminal-witness-ledgers-hold.md`
  - `release_queue/hold/2026.03.21-paper42-challenge-coverage-witness-packs-hold.md`
  - `release_queue/hold/2026.03.21-paper43-challenge-coverage-witness-slices-hold.md`
  - `release_queue/hold/2026.03.21-paper44-challenge-coverage-witness-cores-hold.md`
  - `release_queue/hold/2026.03.21-paper45-answer-capsules-hold.md`
  - `release_queue/hold/2026.03.21-paper46-answer-sheets-hold.md`
  - `release_queue/hold/2026.03.21-paper47-answer-cards-hold.md`
  - `release_queue/hold/2026.03.21-paper48-answer-carrier-slots-hold.md`
  - `release_queue/hold/2026.03.21-paper49-answer-audit-trails-hold.md`
  - `release_queue/hold/2026.03.21-paper50-answer-citation-dockets-hold.md`
  - `release_queue/hold/2026.03.21-paper51-answer-publication-profiles-hold.md`
  - `release_queue/hold/2026.03.21-paper52-answer-disclosure-packets-hold.md`
  - `release_queue/hold/2026.03.21-paper53-answer-escalation-ladders-hold.md`
  - `release_queue/hold/2026.03.21-paper56-public-request-contracts-hold.md`
  - `release_queue/hold/2026.03.21-paper57-requestable-evidence-classes-hold.md`
  - `release_queue/hold/2026.03.28-paper76-theorem-to-publication-spine-hold.md`

## Safe interpretation

The queue is intentionally conservative.
Use `release_queue/LATEST_DECISION.md` for the newest rationale, `release_queue/DECISION_INDEX.md` for the compact history, and `reports/lifecycle_gate_status.json` for the current gate statuses.

## Operating rule

When a paper is moved:

- add a written decision note under `release_queue/decisions/`,
- place a short state file in the relevant queue subdirectory,
- rerun the queue-surface renderer and trust checks, and
- do not move more than the evidence justifies.

## Review universe

Paper-level review should start from the inventory, not from ad hoc repo browsing.
Use `release_queue/REVIEW_INVENTORY.md` and `publishing/REVIEW_ORDER.md`.

## Fast machine surfaces

- `release_queue/LATEST_DECISION.json` gives the latest decision in a compact machine-readable form.
- `release_queue/DECISION_INDEX.json` gives the cumulative machine-readable decision history.
- `reports/lifecycle_gate_status.json` gives the compact stage-by-stage gate status.
