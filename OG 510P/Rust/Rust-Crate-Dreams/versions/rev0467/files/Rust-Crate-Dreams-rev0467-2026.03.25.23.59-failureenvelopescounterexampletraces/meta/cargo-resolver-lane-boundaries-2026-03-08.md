# Cargo resolver explanation — dependency-kind lanes + platform coverage (2026-03-08)

Purpose: keep **P-0468 Cargo Resolver Explanation Kit** pointed at the review artifact that still is not boring today.

## Main judgment

The next worthwhile work on **P-0468** is not another graph dump and not another promise of perfect solver truth.
It is a support artifact that freezes:

1. **dependency-kind lane partition** — normal vs build/proc-macro vs dev,
2. **platform coverage** — which target-specific clauses were actually in scope for the selected command,
3. **surface exactness** — whether a claim came from a close investigative view or a richer unit/build view,
4. and **manual-review boundaries** when those surfaces disagree or merge lanes.

That sharper boundary is justified by six current facts:

- Cargo’s resolver docs say resolver v2 avoids unifying features for target-specific dependencies that are not currently being built.
- The same docs say build-dependencies and proc-macros do not share features with normal dependencies, and dev-dependencies only activate when the needed targets are being built.
- The features chapter repeats those same lane-split rules, which means the split is user-facing policy, not an implementation accident.
- `cargo tree` says its feature view is only *pretty close* to what Cargo will build and may merge features that are separate in the actual build.
- `cargo metadata` includes all targets unless `--filter-platform` is used, so a graph export can over-state platform coverage unless the receipt freezes that choice.
- Current issue reports still show feature views and real builds diverging for dev-dependency and proc-macro/build interactions.

So the missing crate layer is the **lane-aware why-bundle**, not another generic dependency graph crate.

## The sharper missing artifacts

Two small artifacts now deserve to be first-class in the fixture family:

### 1. `lane-partition.report.json`

This report should say, per package when needed:

- which dependency kinds were in play,
- whether the observed surface merged or separated those lanes,
- what feature set was observed per lane,
- whether the crate is claiming an exact lane partition or only a conservative approximation,
- and whether a reviewer should treat the result as manual-review-required.

This is especially important when:

- the same package appears as a normal and dev dependency,
- a proc-macro/helper pair is used from both normal and build contexts,
- or `cargo tree` gives a human-friendly merged view while the actual build keeps lanes separate.

### 2. `platform-coverage.report.json`

This report should say:

- which targets were requested,
- whether metadata was captured with `--filter-platform`,
- which target-specific dependency clauses were included or omitted,
- whether an omitted clause was expected because the target was not being built,
- and whether the coverage statement is exact, conservative, or manual-review-required.

This matters because “the graph contains Windows-only edges” and “the selected Linux build actually enabled the Windows feature” are not the same claim.

## Recommended fixture pressure

Prefer small scenarios that keep these boundaries visible:

1. a resolver-v2 normal+dev dependency where `cargo tree` merges features,
2. a non-matching target-specific dependency clause that must be recorded as out of scope,
3. and one proc-macro/build-vs-normal scenario where the bundle admits manual review rather than inventing certainty.

## Recommended archive stance

For the next few passes, prefer:

- `lane-partition.report` and `platform-coverage.report` schema work,
- tiny scenario bundles,
- stronger exactness language in **P-0468**,
- and explicit capture of `--filter-platform` / selected targets.

Avoid drifting into:

- another generic graph API,
- a claim that `cargo tree` is exact build truth,
- or a mega Cargo doctor that tries to absorb host/target scope, linker diagnosis, and tool-workflow parity.

## Sources

- Cargo dependency resolution: https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo features: https://doc.rust-lang.org/cargo/reference/features.html
- `cargo tree`: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- `cargo metadata`: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo unstable features (`unit-graph`, `feature-unification`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo issue #11261 (`cargo tree` merged dev + normal features): https://github.com/rust-lang/cargo/issues/11261
- Cargo issue #14415 (proc-macro/build-vs-normal feature split pain): https://github.com/rust-lang/cargo/issues/14415
