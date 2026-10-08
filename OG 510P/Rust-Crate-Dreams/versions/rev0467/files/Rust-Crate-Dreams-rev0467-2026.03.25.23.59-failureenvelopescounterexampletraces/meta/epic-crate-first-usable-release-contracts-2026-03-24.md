# Epic crate first-usable release contracts — 2026-03-24

## Why this note exists

The archive already has a better epic-crate bar than it did before.
But “epic” can still drift into fantasy unless the repo keeps asking a harsher question:

> what would `0.1.0` give another person next month?

This note defines a **first usable release contract** for the leading lanes.

## The contract

A proposal is ready for first-build treatment only if it can name:
- one receiver cohort,
- one repeated workflow,
- one packet family,
- one basis/replay story,
- and one refusal boundary.

If it cannot, it is probably still research.

## Applied to the leading lanes

### P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit

Receiver:
- the engineer or staff reviewer who must choose a starter set under time pressure.

Repeated workflow:
- compare 3–8 plausible crates for one task profile, eliminate mismatches honestly, and hand off the result.

A good `0.1.0` should provide:
- `task-profile.json`
- `decision-packet.manifest.json`
- `candidate-elimination.receipt.json`
- `starter-set.lock.json`
- `basis-lock.manifest.json`
- `answer-boundary.note.md`

It should refuse to claim:
- universal “best crate” answers,
- performance truth without explicit evidence,
- or cross-target support that was not part of the packet basis.

### P-0536 Crate Knowledge Pack Kit

Receiver:
- the reviewer, support engineer, or assistant/tool consumer who needs a compact but auditable crate basis.

Repeated workflow:
- answer recurring crate questions without re-reading floating docs pages from scratch.

A good `0.1.0` should provide:
- `review-packet.manifest.json`
- `assistant-context.pack.json`
- `claim-trace.report.json`
- `query-support.matrix.json`
- `basis-lock.manifest.json`
- `citation-locator.receipt.json`
- `answer-boundary.note.md`

It should refuse to claim:
- security or performance certainty beyond the imported basis,
- stable cross-version item identity unless it has the evidence,
- or that its compact pack replaces direct manual review.

### P-0486 Debuggability Support Contract Kit

Receiver:
- the engineer trying to answer “can I debug this target/toolchain/runtime combination and what evidence backs that answer?”

Repeated workflow:
- evaluate debugger viability before or during incident work.

A good `0.1.0` should provide:
- `debug-capability.matrix.json`
- `debug-session.receipt.json`
- `symbol-surface.report.json`
- `basis-lock.manifest.json`
- `manual-gap.note.md`

It should refuse to claim:
- that one successful session implies broad incident readiness,
- or that debugger attachment equals usable variable, frame, and pretty-printer fidelity.

### P-0472 Docs.rs Build Parity & Evidence Kit

Receiver:
- the maintainer trying to understand why hosted docs fail or drift from local builds.

Repeated workflow:
- reproduce hosted/local documentation mismatches and file a useful issue bundle.

A good `0.1.0` should provide:
- `parity-run.receipt.json`
- `hosted-vs-local.report.json`
- `recipe-drift.note.md`
- `issue-bundle.manifest.json`

It should refuse to claim:
- perfect docs.rs emulation,
- or target-complete documentation parity without explicit coverage.

### P-0496 Cargo Vendor & Source Parity Kit

Receiver:
- the platform or release engineer who must prove what source universe a workspace is allowed to use.

Repeated workflow:
- verify that vendored, mirrored, or alternate-registry sources match policy.

A good `0.1.0` should provide:
- `source-universe.manifest.json`
- `mirror-parity.report.json`
- `source-policy.lock.json`
- `drift-gap.note.md`

It should refuse to claim:
- full supply-chain security,
- or byte-for-byte equivalence beyond the captured policy and source surfaces.

## Ranking implication

A proposal that cannot name a first usable release contract should fall behind one that can, even if the idea is exciting.
The archive should prefer **smaller packets with credible handoff** over larger fantasy platforms.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://doc.rust-lang.org/cargo/reference/external-tools.html
- https://doc.rust-lang.org/cargo/commands/cargo-package.html
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
