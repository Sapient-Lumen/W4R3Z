# Top-lane conformance kits — 2026-03-25

This note turns the leading lanes into **promise-tier and conformance-kit plans**.
It is more concrete than a frontier scan and more claim-specific than the earlier promise-bundle and package-topology notes.

## Kit A — P-0472 + P-0484
### Working family
- `support-envelope-core`
- `support-envelope-schemas`
- `cargo-support-envelope`
- `support-envelope-docsrs` *(0.3)*
- `support-envelope-targets` *(0.3)*
- `support-envelope-corpus` *(0.3)*

### Claim dimensions
- docs build
- docs target coverage
- local build replay
- toolchain/profile scope
- target/profile scope

### Default artifacts
- `claim-envelope.json`
- `probe-record.jsonl`
- `conformance-summary.md`
- `claim-diff.json`
- `recheck-plan.json`

### Honest `0.1`
Ship:
- local replayable support claims for a small named profile,
- docs.rs import support,
- unknown / refused states,
- and a stable human summary.

### Key rule
Do not collapse docs.rs success, local replay, and matrix exercise into one word like “supported”.
Those are different tiers.

## Kit B — P-0509 + P-0536 + minimal P-0535
### Working family
- `pathfinder-core`
- `pathfinder-schemas`
- `cargo-pathfinder`
- `pathfinder-importers` *(0.3)*
- `pathfinder-corpus` *(0.3)*

### Conformance role
This lane should not define support rhetoric from scratch.
It should increasingly **import** support-envelope and carry-forward conformance kits and expose them in comparison packets.

### Honest `0.1`
Ship:
- comparison cards that distinguish declared / built / replayed / exercised evidence,
- basis locks that freeze imported conformance state,
- and recheck tickets when the basis is stale.

### Key rule
Recommendation quality should increasingly depend on the freshness and strength of imported conformance claims, not only prose comparison.

## Kit C — P-0486
### Working family
- `debug-support-core`
- `debug-support-schemas`
- `cargo-debug-support`
- `debug-support-probes` *(later)*
- `debug-support-corpus` *(later)*

### Claim dimensions
- debugger + version
- operating system
- target
- async support
- expression evaluation
- pretty-printer / visualizer quality

### Honest `0.1`
Ship:
- a narrow debugger/profile matrix,
- raw probe receipts separated from reviewed claims,
- a degraded / refused vocabulary,
- and scenario fixtures for common breakage classes.

### Key rule
Probe churn must not destabilize the meaning of debugger support packets.

## Kit D — P-0431 + P-0496 + P-0125
### Working family
- `carryforward-core`
- `carryforward-schemas`
- `cargo-carryforward`
- `carryforward-source-parity` *(optional adapter)*
- `carryforward-boundary` *(optional adapter)*
- `carryforward-sbom` *(optional adapter)*
- `carryforward-corpus`

### Claim dimensions
- source parity
- alternate-registry posture
- public-boundary continuity
- inventory / SBOM precursor continuity
- advisory-triggered recheck state

### Honest `0.1`
Ship:
- carry-forward receipts across releases,
- clear alternate-registry unknown states,
- and one compact continuity summary.

### Key rule
Do not imply registry safety or mirror parity where the basis only covers crates.io defaults.

## Kit E — P-0537
### Working family
- `iteration-feedback-core`
- `iteration-feedback-schemas`
- `cargo-iteration-feedback`
- `iteration-feedback-corpus`

### Planning note
This lane should borrow proven conformance vocabulary after the support-envelope lane stabilizes it.
Likely claim dimensions:
- rebuild reason coverage,
- timing provenance,
- target-dir / build-dir sensitivity,
- and explanation completeness.

## Kit F — P-0538
### Working family
- `concurrency-contract-core`
- `concurrency-contract-schemas`
- `cargo-concurrency-contract`
- `concurrency-contract-corpus`

### Planning note
The corpus matters even more than the claim ladder here.
This lane should probably adopt conformance tiers late, after scenario semantics are better bounded.

## Cross-kit shared rule

The archive should prefer kits where:
- raw observations are append-only,
- reviewed claims are compact,
- human summaries are short,
- recheck plans are explicit,
- and refusal states are first-class.

That is now a stronger answer to “what should the crate provide other people?” than saying “a better report” or “a robust API”.
