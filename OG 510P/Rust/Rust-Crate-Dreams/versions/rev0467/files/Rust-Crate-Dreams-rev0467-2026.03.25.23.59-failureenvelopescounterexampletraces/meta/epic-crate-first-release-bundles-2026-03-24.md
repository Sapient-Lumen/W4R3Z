# Epic crate first-release bundles — 2026-03-24

This note gives the archive a more operational answer to:

> What should an actually worthy `0.1` release hand other people?

The delivery cards already say what the leading crates promise.
This note turns that into a smaller first-release bundle plan.

## Main judgment

A worthy epic crate should usually ship a **small bundle family** before it ships a large surface area.
The bundle should be good enough for another engineer, reviewer, or operator to use without reading the whole codebase.

## P-0509 — Pathfinder

`0.1` first-release bundle:
- `decision-brief.md`
- `starter-set.bundle.json`
- `candidate-elimination.receipt.json`
- `manual-review.note.md`
- `revisit-trigger.policy.json`

Why this is enough:
- it covers first choice, review, and later reconsideration.

## P-0536 — Crate Knowledge Pack

`0.1` first-release bundle:
- `assistant-context.pack.json`
- `claim-trace.report.json`
- `citation-locator.receipt.json`
- `query-support.matrix.json`
- `answer-boundary.note.md`

Why this is enough:
- it makes the crate useful to humans and tools without pretending full semantic understanding.

## P-0486 — Debuggability Support

`0.1` first-release bundle:
- `session-family.report.json`
- `capability-witness.report.json`
- `claim-ceiling.report.json`
- `debug-support-bundle.manifest.json`
- `manual-review.note.md`

Why this is enough:
- it provides a support contract without collapsing all debugger behavior into one score.

## P-0472 — Docs.rs Build Parity

`0.1` first-release bundle:
- `build-surface.receipt.json`
- `parity-gap.report.json`
- `issue-bundle.manifest.json`
- `hosted-assumption.note.md`

Why this is enough:
- it serves the maintainer fighting hosted/local drift immediately.

## P-0535 — Dependency Lifecycle Transition

`0.1` first-release bundle:
- `selection-anchor.receipt.json`
- `reresolution-risk.report.json`
- `offramp-bundle.manifest.json`
- `override-authority.receipt.json`

Why this is enough:
- it makes transition risk visible without becoming a whole policy platform.

## P-0484 — Toolchain & Target Support

`0.1` first-release bundle:
- `target-support.receipt.json`
- `host-target-route.report.json`
- `external-prerequisite.report.json`
- `support-bundle.manifest.json`

Why this is enough:
- it prevents fake yes/no target claims and helps harder-domain adopters quickly.

## P-0058 — Native Deps

`0.1` first-release bundle:
- `native-contract.toml`
- `native-resolution.report.json`
- `backend-attempts.receipt.json`
- `abi-provenance.report.json`
- `consumer-doctor.txt`

Why this is enough:
- it makes native assumptions reviewable without trying to replace a package manager.

## Product rule

If a proposal cannot name a first-release bundle this compact, it is probably still a research topic rather than a buildable crate.
