# Frontier salience scan — 2026-03-16 (rebuild explanation made fixture-first)

This pass did not add a new top-level proposal.
It upgraded **P-0469 Cargo Rebuild Explanation Kit** into a more fixture-first, more implementation-shaped lane.

## Main judgment

The strongest contribution here is not another performance dashboard and not another generic “Cargo doctor”.
It is the **support-grade rebuild explanation layer** above Cargo’s evolving `cargo report` / build-analysis substrate and below historical warehousing, lock-contention witnesses, and tool-surface parity crates.

That lane became much more concrete because:

- the Cargo build-analysis goal says Cargo is recording build metadata across invocations and introducing report commands for rebuild reasons and timings,
- current unstable docs now define the persisted JSONL/session-id model and the `cargo report sessions` / `timings` / `rebuilds` command set,
- the Cargo 1.94 cycle update says `cargo report timings` kept gaining missing features and that `cargo report sessions` exists to find the ids the other report commands need,
- the relink-don’t-rebuild goal keeps “private edit still caused broad reverse-dependency rebuilds” squarely in scope,
- and build-dir-layout work keeps lock/contention and shared-cache pain adjacent enough that the rebuild bundle must preserve when a result is really about *waiting* rather than *causality*.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0469 Cargo Rebuild Explanation Kit**
3. **P-0035 cargo-build-insights**
4. **P-0429 rustc_public Analysis Workbench Kit**
5. **P-0478 Cargo Future-Incompat Triage Kit**
6. **P-0125 Cargo SBOM Precursor Workbench Kit**
7. **P-0471 Cargo Artifact Handoff Kit**
8. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
9. **P-0490 Cargo Lock Contention Witness Kit**
10. **P-0055 Cargo Workspace Toolchain Manifest Kit**
11. **P-0508 Cargo Build Script Delegation Kit**
12. **P-0244 SemVer API Diff Evidence Kit**

## Why P-0469 rose

The archive already had a good theory for P-0469.
What it lacked was the “another tool author could actually build this” layer.

The new pass freezes:

- `evidence-source.receipt.json`,
- `exactness.report.json`,
- scenario families for source-edit fanout, session-wording drift, compile-time-deps parity overlap, and contention-versus-causality,
- and a lane note that keeps rebuild explanation distinct from warehousing, lock contention, tool-surface parity, and build-signature work.

That is enough to move it from “credible concept” toward “buildable substrate crate”.

## What this pass deliberately did not do

It did **not** collapse:

- historical build-analysis warehousing,
- lock-wait/root-collision witnesses,
- compile-time-deps or rust-analyzer parity bundles,
- input-manifest / build-signature completeness,
- or build-dir-layout migration work

into one fake rebuild platform.

That restraint improved the repo.

## Sources

- Cargo build-analysis goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo unstable docs (`-Zbuild-analysis`, `cargo report`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-analysis
- This development-cycle in Cargo 1.94: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Relink don’t Rebuild goal: https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- Cargo build-dir-layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
