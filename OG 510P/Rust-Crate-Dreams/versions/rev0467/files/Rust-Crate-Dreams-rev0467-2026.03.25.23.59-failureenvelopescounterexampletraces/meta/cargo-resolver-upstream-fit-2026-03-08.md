# Cargo resolver explainability — upstream-fit note (2026-03-08)

Purpose: keep **P-0468 Cargo Resolver Explanation Kit** aligned with what Cargo and existing ecosystem tools already do.

## Main judgment

The resolver-explanation frontier is now strong enough that the archive should stop describing it as a speculative graph-tool dream.

Cargo already has:

- official resolver and features documentation,
- troubleshooting guidance built around `cargo tree --invert`, `--edges features`, and `--duplicates`,
- stable `cargo metadata` graph context,
- unstable `--unit-graph` output that can expose build-unit / feature-resolution-adjacent data,
- unstable `resolver.feature-unification` modes that make duplicate-build explanations more policy-sensitive,
- and a Cargo plumbing direction that explicitly splits resolution / feature resolution / build planning into separate phases.

The ecosystem also already has real graph/query/simulation substrate:

- `guppy` for querying Cargo dependency graphs and feature graphs from `cargo metadata`,
- `hakari` / `cargo hakari` for simulating Cargo builds and reasoning about repeated feature sets in workspaces.

So the missing value is **not** “a crate that finally lets Rust reason about Cargo graphs.”
It is a crate that standardizes the **receiver-facing explanation artifact** above those surfaces.

## What P-0468 should own

P-0468 should own:

- short feature-cause chains,
- compact version-choice receipts,
- duplicate-build group explanations,
- graph-diff reports,
- explicit unknowns,
- and a stable, review-oriented schema.

## What P-0468 should not own

P-0468 should **not** try to become:

- another generic graph query API,
- another workspace-hack generator,
- a replacement for `guppy`,
- a replacement for `cargo hakari`,
- or a full solver-branch debugger.

## Recommended 0.1 artifact vocabulary

For the current repo frontier, the minimal stable artifact vocabulary should be:

- `resolve-why.lock`
- `feature-causes.json`
- `version-choices.json`
- `duplicate-builds.json`
- `resolver-choice.receipt.json`
- optional `resolution-diff.report.json`

These artifacts are easier to explain to reviewers and support recipients than raw tree output or bespoke tool logs.

## Data-source layering rule

Future work on this frontier should prefer this order:

1. stable Cargo inputs first (`cargo metadata`, `cargo tree`, lockfile diff),
2. nightly Cargo inputs second (`--unit-graph`, `-Z feature-unification`),
3. third-party graph/simulation adapters third (`guppy`, `hakari`-adjacent reasoning),
4. and explicit `manual_review_required` markers whenever a bundle crosses from observed fact into inference.

## Repo implication

For the next few passes, the archive should prefer:

- proposal refreshes for **P-0468**,
- schema stabilization for version-choice and diff receipts,
- tiny scenario bundles,
- and vocabulary alignment with **P-0469** / **P-0035**,

rather than adding another generic Cargo graph or feature-management proposal.

## Sources

- Cargo dependency resolution: https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo features: https://doc.rust-lang.org/cargo/reference/features.html
- `cargo tree`: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- `cargo metadata`: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo unstable features (`--unit-graph`, `resolver.feature-unification`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- `guppy`: https://docs.rs/guppy/latest/guppy/
- `cargo hakari`: https://docs.rs/cargo-hakari/latest/cargo_hakari/
