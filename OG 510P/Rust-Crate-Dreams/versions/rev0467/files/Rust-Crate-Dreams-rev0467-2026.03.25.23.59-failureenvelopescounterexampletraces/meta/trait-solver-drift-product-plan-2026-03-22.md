# Trait Solver Drift Witness Kit — product plan (2026-03-22)

## Product shape

Deliver **P-0442** as:

1. a library for capture / normalize / classify / package;
2. a cargo subcommand for CI and issue filing;
3. a compact schema family that other tools can import.

## Receiver-facing promise

Given two configured runs, another engineer should be able to tell:

- which solver lane ran,
- which obligation class changed,
- whether the change is semantic or diagnostic,
- what transformations were applied to diagnostics,
- and whether a minimized witness still faithfully represents the source case.

## v0.1 commands

- `cargo solver-witness run`
- `cargo solver-witness diff`
- `cargo solver-witness reduce`
- `cargo solver-witness pack`

## v0.1 artifact set

- `comparison-lane.receipt.json`
- `corpus-authority.receipt.json`
- `obligation-class.report.json`
- `diagnostic-normalization.receipt.json`
- `solver-drift.diff.json`
- `solver-support-bundle.manifest.json`

## v0.1 implementation stance

- stable-first corpus support (`ui_test` or `trybuild`)
- nightly preview lane optional, not required for every command
- explicit exactness / manual-review posture whenever comparison scope is mixed or unclear

## Stage 1

Freeze the lane taxonomy and obligation taxonomy.
Do not chase deep compiler introspection yet.

## Stage 2

Add witness-generation lane and minimization lineage.

## Stage 3

Add richer compiler-substrate imports only if they can be kept optional and non-fragile.

## Adoption targets

1. trait-heavy public crates,
2. proc-macro ecosystems,
3. compiler-adjacent CI runs on nightly,
4. upstream issue filing for next-solver regressions.
