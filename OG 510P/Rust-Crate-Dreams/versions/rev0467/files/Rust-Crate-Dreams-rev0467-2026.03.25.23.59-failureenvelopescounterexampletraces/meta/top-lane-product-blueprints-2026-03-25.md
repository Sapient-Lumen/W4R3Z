# Top-lane product blueprints — 2026-03-25

This note turns the current leading lanes into **build programs**.
It is intentionally more concrete than a frontier scan and more compact than the older per-proposal product-plan notes.

## Blueprint A — P-0509 + P-0536 + minimal P-0535
### Product thesis
Help a team decide **which Rust crate stack to adopt for a named task**, freeze the basis for that answer, and reopen it honestly when signals drift.

### Receiver
- platform team
- project lead
- staff engineer
- educator or template owner

### Repeated downstream question
“What crate or starter set should we adopt for this job, why, and what would cause us to revisit that answer?”

### Imported surfaces
- crates.io metadata and policy/trust signals
- docs.rs package/docs surfaces
- crate-authored README/docs imports
- local task profile and org policy files
- optional health/trust imports from adjacent kits

### Core commands
- `cargo pathfinder init`
- `cargo pathfinder import`
- `cargo pathfinder explain`
- `cargo pathfinder freeze`
- `cargo pathfinder reopen`
- `cargo pathfinder diff`

### Acceptance packet family
- `task-profile.json`
- `decision-pack.report.json`
- `review-packet.pack.json`
- `basis-lock.json`
- `offer.summary.md`
- `recheck-trigger.ticket.json`

### Honest `0.1`
- one task lane at a time
- one local or CI operator
- no universal scoring claims
- no hosted recommendation service

### Strong `0.3`
- policy overlays
- reusable starter-set locks
- richer diffing and reopen workflows
- limited org-level presets

### Real `1.0`
- stable packet schema
- multi-team handoff semantics
- clear supersession rules
- repeatable acceptance workflow across multiple domains

### Refusal boundary
- not an official Rust blessing process
- not a universal best-crate oracle
- not proof that a selected stack is correct for every future scope change

## Blueprint B — P-0472 + P-0484
### Product thesis
Turn docs.rs, build recipe, target, and toolchain ambiguity into **bounded support-envelope truth**.

### Receiver
- crate maintainer
- release engineer
- platform integrator
- embedded or cross-platform adopter

### Repeated downstream question
“What do we actually know about docs/build/target/toolchain support for this crate or workspace?”

### Imported surfaces
- docs.rs build metadata and rustdoc JSON surfaces
- target defaults and docs.rs build behavior
- rust-toolchain and Cargo config
- installed components/targets and local build receipts

### Core commands
- `cargo docs-parity preflight`
- `cargo docs-parity diff`
- `cargo target-support inspect`
- `cargo target-support explain`

### Acceptance packet family
- `docs-build-parity.report.json`
- `docs-surface.report.json`
- `target-support.report.json`
- `toolchain-component.report.json`
- `support-ceiling.note.md`

### Honest `0.1`
- one workspace or crate at a time
- local-vs-hosted docs parity with explicit caveats
- target/toolchain import with “supported vs built vs documented vs unknown” language

### Strong `0.3`
- matrix presets for common targets
- reusable support-envelope summaries
- drift detection against changed docs.rs defaults or toolchain baselines

### Real `1.0`
- stable vocabulary for support claims
- handoff-grade receipts for cross-team support review
- clear promotion path into higher-assurance evidence bundles

### Refusal boundary
- not certification
- not proof that every target permutation works
- not a replacement for upstream platform policy or Rust tier policy

## Blueprint C — P-0486
### Product thesis
Export **debuggability support envelopes** instead of vague promises that a crate or target is “debuggable”.

### Receiver
- systems engineer
- platform team
- toolchain support engineer

### Repeated downstream question
“What debugger/OS/version combinations can we honestly support for this Rust target and what evidence backs that claim?”

### Imported surfaces
- debug symbol and sidecar outputs
- debugger matrix fixtures
- async-debugging scenario corpus
- target/toolchain support imports from Blueprint B

### Acceptance packet family
- `debug-matrix.report.json`
- `sidecar-availability.report.json`
- `async-debug.claim-ceiling.note.md`
- `debug-support.summary.md`

### Honest `0.1`
- matrix report for a limited debugger/OS/target set
- explicit degraded and refusal outputs

### Strong `0.3`
- richer scenario corpus
- support regression diffs
- import from CI witness bundles

### Real `1.0`
- stable matrix vocabulary
- handoff-grade debugger support packet for downstream teams

### Refusal boundary
- not a debugger replacement
- not proof of whole-program debuggability or async correctness

## Blueprint D — P-0431 + P-0496 + P-0125
### Product thesis
Keep acceptance packets **alive through publication, mirroring, public-boundary, and inventory drift**.

### Receiver
- supply-chain reviewer
- release or packaging engineer
- platform governance owner

### Repeated downstream question
“What changed in the public boundary, source identity, or build inventory, and does it reopen our prior acceptance?”

### Acceptance packet family
- `public-boundary.report.json`
- `source-parity.report.json`
- `sbom-precursor.delta.json`
- `carry-forward.summary.md`

### Honest `0.1`
- one carry-forward report per change event
- clear imported-vs-observed distinction

### Refusal boundary
- not full provenance attestation
- not proof that a mirror or vendor tree is morally identical in every meaningful way

## Blueprint E — P-0537 and P-0538 as research-first lanes
### Product thesis
Keep iteration truth and concurrency semantics **hot but disciplined**.

### Honest `0.1`
- P-0537 should explain rebuilds and hotspots, not promise universal compile-time cures.
- P-0538 should compare semantics and refusal boundaries, not promise concurrency correctness.

### Why not higher yet?
These lanes are highly important, but the archive still has better evidence and clearer packet shapes for the earlier stacks.

## Cross-blueprint rule

A top-lane crate is strong when it can answer all of these in one place:
- who receives the output,
- what repeated question it answers,
- what it imports,
- what packets it emits,
- what `0.1` can honestly promise,
- what `1.0` would stabilize,
- and what it still refuses to claim.
