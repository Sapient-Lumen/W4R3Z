# Frontier salience scan — 2026-03-16 (build insights made fixture-first)

This pass did not add a new top-level proposal.
It upgraded **P-0035 cargo-build-insights** into a more fixture-first, more implementation-shaped lane.

## Main judgment

The strongest contribution here is not another dashboard and not another generic “build doctor”.
It is the **historical build-session warehouse** above Cargo's evolving `cargo report` / build-analysis substrate and below per-run rebuild support, lock contention, and tool-workflow parity crates.

That lane became much more concrete because:

- the build-analysis goal explicitly says Cargo is recording metadata across invocations and wants external tooling to analyze historical trends,
- the current unstable docs now describe persisted JSONL logs in `$CARGO_HOME/log/`, unique session ids, and `cargo report sessions` / `timings` / `rebuilds`,
- the Cargo 1.94 development-cycle update says `cargo report sessions` was added to find ids, `cargo report timings` kept gaining functionality, and unstable `--timings=FMT` was removed as redundant with `cargo report timings`,
- the build-analysis goal explicitly says there are no user-facing stability guarantees during the prototyping phase,
- and the relink-don't-rebuild goal keeps long-running rebuild pain squarely in scope.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0429 rustc_public Analysis Workbench Kit**
5. **P-0478 Cargo Future-Incompat Triage Kit**
6. **P-0125 Cargo SBOM Precursor Workbench Kit**
7. **P-0471 Cargo Artifact Handoff Kit**
8. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
9. **P-0490 Cargo Lock Contention Witness Kit**
10. **P-0055 Cargo Workspace Toolchain Manifest Kit**
11. **P-0508 Cargo Build Script Delegation Kit**
12. **P-0244 SemVer API Diff Evidence Kit**

## Why P-0035 rose

The archive already knew P-0035 was promising.
What it still lacked was the “another tool author could build against this tomorrow” layer.

This pass freezes:

- `session-series.index.json`,
- `import.receipt.json`,
- `series-summary.json`,
- `series-compatibility.report.json`,
- `exactness.report.json`,
- and scenario families for trend alerts, toolchain splits, and workspace-scope drift.

That is much stronger than another paragraph saying “historical build trends matter.”

## What this pass deliberately did not do

It did **not** collapse:

- Cargo's own recorder / report UX,
- P-0469 per-run rebuild support bundles,
- P-0494 compile-time-deps parity evidence,
- P-0490 contention / waiting stories,
- or resolver-cause proof bundles

into one fake build-performance platform.

That restraint improved the repo.

## Sources

- Cargo build-analysis goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo unstable docs (`-Zbuild-analysis`, `cargo report`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- This development-cycle in Cargo 1.94: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo changelog (`-Zbuild-analysis`): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Relink don't Rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- 2025 State of Rust survey results: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
