# Top-lane review-handoff plans (2026-03-25)

This note turns the review-packet doctrine into concrete planning for the leading lanes.

## Kit A — P-0509 + P-0536 + minimal P-0535
### Review role
This is the first **review-front-door** lane.
It should assemble imported evidence, policy, and continuity signals into the one packet another human can actually approve.

### Working family
- `pathfinder-core`
- `pathfinder-schemas`
- `cargo-pathfinder`
- `pathfinder-review` *(0.3 or merged CLI surface)*
- `pathfinder-corpus`

### Imports
- support exchange bundles
- conformance claims
- policy packs and verdicts
- continuity/parity triggers
- frozen basis locks

### Exports
- `review-intake.json`
- `review-packet.json`
- `signoff-ledger.jsonl`
- `override-register.json`
- `maintenance-summary.md`
- `reapproval-plan.json`

### Honest `0.1`
Ship:
- one receiver-facing review packet for crate-selection / adoption decisions,
- a short maintenance summary,
- append-only signoff history,
- and visible expiries on overrides and stale packets.

### Key rule
Do not make reviewers read raw evidence bundles to understand the recommendation.
The reviewed packet must surface decisive evidence and named non-claims directly.

## Kit B — P-0472 + P-0484
### Review role
This lane is the main **decisive-evidence supplier**.
It should increasingly export review-ready evidence excerpts rather than forcing downstream tools to summarize docs/build/target truth themselves.

### Working family
- `support-envelope-core`
- `support-envelope-schemas`
- `cargo-support-envelope`
- `support-envelope-review-excerpts` *(0.3)*
- `support-envelope-corpus`

### Imports
- docs.rs build metadata
- docs.rs rustdoc JSON
- docs.rs download archives
- local replay receipts
- target/toolchain semantics

### Exports
- decisive evidence excerpt set
- scope/matrix summary
- named unknown and refused states
- delta since prior packet
- evidence freshness signal

### Honest `0.1`
Ship:
- compact excerpts for docs/build/target reality,
- one stable summary vocabulary,
- and explicit unknown/refused cases.

### Key rule
Do not turn hosted-surface success into a review-ready claim without showing the matrix scope and evidence tier.

## Kit C — P-0431 + P-0496 + P-0125
### Review role
This lane is the main **reapproval and supersession trigger ring**.
It should tell later reviewers when a once-good packet is no longer safe to inherit blindly.

### Working family
- `carryforward-core`
- `carryforward-schemas`
- `cargo-carryforward`
- `carryforward-review-triggers` *(0.3)*
- `carryforward-corpus`

### Imports
- source parity observations
- registry and mirror posture
- public-boundary continuity receipts
- SBOM precursor routes and deltas
- advisory-triggered events

### Exports
- reapproval trigger bundle
- supersession note
- inherited-vs-fresh review guidance
- continuity delta summary

### Honest `0.1`
Ship:
- event-driven invalidation or refresh guidance,
- continuity deltas between reviewed packets,
- and explicit “safe to inherit / must reapprove / unknown” signals.

### Key rule
Do not treat prior approval as evergreen.
Continuity outputs should make inherited trust conditional and reviewable.

## Kit D — P-0486
### Review role
This lane should borrow the shared review packet after the support and continuity rings define it.
Its special burden is matrix churn.

### Working family
- `debug-support-core`
- `debug-support-schemas`
- `cargo-debug-support`
- `debug-support-review`
- `debug-support-corpus`

### Imports
- debugger probes
- OS/version matrix receipts
- async-debug witnesses
- pretty-printer and expression-eval receipts

### Exports
- debugger review packet
- matrix-limited approval summary
- stale-on-version-change trigger set
- explicit non-claim list

### Honest `0.1`
Ship:
- one narrow debugger/OS matrix packet,
- visible version-scoped approval,
- and immediate staleness when the checked matrix changes.

### Key rule
The narrower and more explicit the matrix, the more honest the first release.

## Kit E — P-0537
### Review role
Later borrower.
This lane becomes review-ready when build-analysis exports are stable enough to summarize without lying.

### Planning note
Review packets here should probably focus on:
- rebuild reason summaries,
- repeat offender crates,
- and rerun suggestions,
not on broad permanent support claims.

## Kit F — P-0538
### Review role
Later borrower.
This lane likely needs scenario verdicts before it needs generic review-packet standardization.

### Planning note
A first review packet here should probably be scenario-specific and refusal-heavy.

## Cross-kit shared rule

The archive should prefer review layers where:
- the human packet is shorter than the raw bundle,
- the decisive evidence slice is explicit,
- signoff history is append-only,
- overrides are visible and expiring,
- and later reviewers can tell whether to inherit, refresh, or reject.

That is now a stronger answer to “what should the crate provide other people?” than saying “review tools” or “approval dashboards”.
