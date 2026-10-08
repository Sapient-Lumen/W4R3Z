# Top-lane delta rerun plans — 2026-03-25

This note translates the delta doctrine into concrete build direction for the strongest lanes.

## 1. P-0431 + P-0496 + P-0125
**Receiver:** supply-chain steward, release reviewer, offline/mirror operator

### Repeated downstream question
> What changed enough to invalidate the prior route, boundary, or inventory conclusion, and what can still carry forward without rebuilding the whole case?

### Imports
- registry and mirror posture
- source-parity observations
- public-boundary continuity deltas
- advisories, releases, and inventory triggers
- prior review/renewal state

### Exports
- `change-intake.json`
- `change-classification.json`
- `carry-forward-decision.json`
- `supersession-diff.json`
- `delta-summary.md`
- `confidence-reset.json`

### Honest `0.1`
- classify release, advisory, route, and public-boundary changes
- distinguish carry-forward, downgrade, narrow rerun, and reset
- no organization-specific workflow engine
- no supply-chain attestation platform ambition

### Worthy package family
- `continuity-delta` CLI
- `continuity-delta-core`
- `continuity-delta-schema`
- bounded registry/source/boundary adapters
- one supersession corpus

## 2. P-0509 + P-0536 + minimal P-0535
**Receiver:** crate chooser, support reviewer, platform/tooling steward

### Repeated downstream question
> Since the last decision packet, what changed in the recommendation or support basis, what still carries, and what exact slice must we rerun before we trust the new answer?

### Imports
- prior decision packets and basis locks
- review packets and signoff state
- policy packs and verdicts
- continuity delta programs
- support-basis deltas

### Exports
- reviewed delta bundle
- rerun-slice plan
- carry-forward verdict
- reopened-section map
- human delta summary

### Honest `0.1`
- one profile (`ci-minimal`)
- compare one old packet to one new packet
- show what sections are unchanged versus reopened
- no global recommendation engine
- no automatic policy rewriting

### Worthy package family
- `pathfinder-delta` CLI
- `pathfinder-delta-core`
- `pathfinder-delta-schema`
- bounded import adapters
- one decision-diff corpus

## 3. P-0472 + P-0484
**Receiver:** support reviewer, toolchain/target steward, documentation-quality reviewer

### Repeated downstream question
> Which parts of our docs/build/target support basis changed, and which old claims can still stand after a narrow refresh?

### Imports
- docs.rs metadata
- docs.rs build outcomes
- docs.rs download archives
- docs.rs rustdoc JSON
- local replay receipts
- target/toolchain facts

### Exports
- basis-delta receipt
- target-scope diff
- docs/build/API delta hint
- named “too much changed to carry forward” outcome

### Honest `0.1`
- default target + one extra target
- one docs/build/API basis diff
- one support-scope vocabulary
- no universal support oracle

## 4. P-0486
**Receiver:** debugger support maintainer, platform team, assessor for debug readiness

### Repeated downstream question
> Which debugger / OS / compiler tuples changed, which matrix cells still carry forward, and which cells require replay or reset?

### Imports
- debugger probes
- tuple receipts
- async-debug corpus witnesses
- prior review and renewal state

### Exports
- tuple-diff receipt
- matrix-cell carry-forward decision
- tuple-scoped rerun slice
- cell-level reset or supersession note

### Honest `0.1`
- extremely narrow tuple matrix
- one debugger family
- one async witness corpus
- explicit reset for unknown tuples

## Design rule across all four lanes

The delta layer should never emit a generic “something changed” banner.
It should always say:
1. what changed,
2. what class of change it is,
3. what still carries forward,
4. what exact slice must be rerun,
5. and how the new result supersedes the old one.
