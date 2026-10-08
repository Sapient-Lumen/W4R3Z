# Frontier salience scan — 2026-03-16 (SBOM precursor made fixture-first)

This pass did not add a new top-level proposal.
It upgraded **P-0125 Cargo SBOM Precursor Workbench Kit** into a fixture-first, more implementation-shaped lane.

## Main judgment

The strongest contribution here is not another format emitter.
It is the **precursor capture, normalization, and review layer** above Cargo’s SBOM substrate.

That lane became much more concrete because:

- Rust’s 2026 goals explicitly target stabilizing Cargo SBOM precursor support.
- Cargo’s unstable docs already define precursor-sidecar generation, naming, and a starter schema.
- `CARGO_SBOM_PATH` gives a build-time discovery hook.
- Cargo external-tools JSON gives the primary artifact stream needed for artifact association.
- Cargo changelog work is still tightening the precursor contract (for example fully-qualified package IDs), which is a strong sign that a downstream exactness / compatibility layer is warranted.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0429 rustc_public Analysis Workbench Kit**
3. **P-0478 Cargo Future-Incompat Triage Kit**
4. **P-0125 Cargo SBOM Precursor Workbench Kit**
5. **P-0055 Cargo Workspace Toolchain Manifest Kit**
6. **P-0056 Cargo Install Policy & Cooldown Kit**
7. **P-0489 Cargo Build-Dir Consumer Transition Kit**
8. **P-0508 Cargo Build Script Delegation Kit**
9. **P-0244 SemVer API Diff Evidence Kit**
10. **P-0479 Cargo Artifact Sidecar Contract Kit**
11. **P-0507 Cargo Fix Campaign Kit**
12. **P-0484 Toolchain & Target Support Contract Kit**

## Why P-0125 rose

The archive already knew Cargo SBOM support mattered.
What it still lacked was the “someone else could build against this” layer.

The new fixture pack freezes:

- `sbom-precursor.capture-lock.json`,
- `precursor-ingest.report.json`,
- `normalized-build-graph.report.json`,
- `sbom-transform.report.json`,
- `vex-stub.report.json`,
- `sbom-diff.report.json`,
- and `evidence-source.receipt.json`.

That is meaningfully stronger than another round of prose about CycloneDX versus SPDX.

## What this pass did not do

It did **not** collapse:

- Cargo-native precursor capture,
- general sidecar attachment contracts,
- trusted-publishing or post-publish receipt crates,
- public/private dependency or SemVer witness crates,
- and higher-level provenance / policy / OCI distribution crates

into one fake “SBOM platform”.

That restraint improved the archive.

## Sources

- Rust in 2026 / Cargo SBOM precursor stabilization: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Cargo unstable SBOM docs: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo external tools / artifact messages: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo changelog (`-Z sbom` package ID clarification): https://doc.rust-lang.org/cargo/CHANGELOG.html
