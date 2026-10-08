# Top-lane renewal loop plans — 2026-03-25

This note translates the renewal doctrine into concrete build direction for the strongest lanes.

## 1. P-0509 + P-0536 + minimal P-0535
**Receiver:** crate chooser, release reviewer, platform/tooling steward

### Repeated downstream question
> We already approved this lane’s decision packet. What exactly must we rerun next month or after a registry/release event, and what can remain trusted without reopening the whole case?

### Imports
- review packets and signoff state
- policy packs and verdicts
- continuity / parity / off-ramp triggers
- support-envelope freshness signals
- basis locks

### Exports
- `renewal-program.json`
- `freshness-budget.json`
- `renewal-ticket.json`
- `renewal-ledger.jsonl`
- `stewardship-summary.md`
- `supersession-record.json`

### Honest `0.1`
- one profile (`ci-minimal`)
- one decision packet renewed at a time
- time-based and event-based triggers
- cheap rerun slice = basis import + verdict replay + summary diff
- deep rerun trigger = major release / boundary drift / parity break

### Worthy package family
- `pathfinder-renew` CLI
- `pathfinder-renew-core`
- `pathfinder-renew-schema`
- bounded trigger adapters
- one renewal corpus

## 2. P-0431 + P-0496 + P-0125
**Receiver:** supply-chain steward, offline / mirror operator, long-lived product maintainer

### Repeated downstream question
> Which ecosystem events should force renewal, and how do we carry or retire prior approvals when the route to the crate changes?

### Imports
- registry and mirror posture
- source-parity observations
- public-boundary continuity deltas
- advisories / release changes

### Exports
- event-trigger bundle
- carry-forward note
- parity-drift renewal slice
- retirement / supersession reason

### Honest `0.1`
- track release, advisory, mirror, and source-route triggers
- distinguish `due`, `grace`, and `stale`
- no full policy engine
- no supply-chain attestation suite

### Practical warning
This lane should define triggers and carry-forward semantics, not try to own every organization’s ticket workflow.

## 3. P-0472 + P-0484
**Receiver:** support reviewer, toolchain/target steward, documentation-quality reviewer

### Repeated downstream question
> Which parts of our support story can be cheaply refreshed from hosted or local basis, and which stale states require deeper replay?

### Imports
- docs.rs metadata
- docs.rs build outcomes
- docs.rs download archives
- docs.rs rustdoc JSON
- local replay receipts
- target/toolchain facts

### Exports
- basis freshness class
- support-basis delta
- cheap replay slice hint
- named “too stale to trust” outcome

### Honest `0.1`
- default target + one extra target
- one freshness class vocabulary
- one docs/build/API replay slice
- no global support oracle

## 4. P-0486
**Receiver:** debugger support maintainer, platform team, assessor for debug readiness

### Repeated downstream question
> Which debugger / OS / compiler tuples must be rerun, and when does a previously approved matrix cell expire?

### Imports
- debugger probes
- tuple receipts
- async-debug corpus witnesses
- review packet state

### Exports
- matrix renewal ticket
- tuple freshness state
- partial-renewal summary
- cell-level supersession note

### Honest `0.1`
- extremely narrow tuple matrix
- one debugger family
- one async witness corpus
- visible refusal for untested tuples

## Design rule across all four lanes

The renewal loop should not be a vague “monitoring” story.
It should always say:
1. what changed,
2. which renewal unit is affected,
3. what the cheapest honest rerun is,
4. whether human review is required,
5. and how the old result is retired or superseded.
