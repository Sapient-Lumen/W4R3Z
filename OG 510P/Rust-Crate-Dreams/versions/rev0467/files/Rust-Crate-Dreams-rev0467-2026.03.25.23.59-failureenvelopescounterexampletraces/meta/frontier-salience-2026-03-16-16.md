# Frontier salience scan — 2026-03-16 (artifact sidecars made fixture-first)

This pass did not add a new top-level proposal.
It upgraded **P-0479 Cargo Artifact Sidecar Contract Kit** into a fixture-first, more implementation-shaped lane.

## Main judgment

The strongest contribution here is not another artifact manifest and not another SBOM emitter.
It is the **association + attachment-policy + schema-drift layer** above Cargo artifact output.

That lane became much more concrete because:

- Cargo external-tools JSON already emits `compiler-artifact` messages with filenames and package/target context.
- Cargo’s unstable `--artifact-dir` exists precisely because downstream artifact lookup is a real pain point.
- Cargo’s unstable `sbom` feature emits sidecar files beside executable and linkable outputs and exposes `CARGO_SBOM_PATH`.
- Rust’s 2026 goals make SBOM support an explicit supply-chain milestone.
- Cargo changelog work is still tightening sidecar-adjacent contract details (for example fully-qualified package IDs in SBOM precursor files), which is a strong sign that a downstream compatibility and review layer is warranted.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0429 rustc_public Analysis Workbench Kit**
3. **P-0478 Cargo Future-Incompat Triage Kit**
4. **P-0125 Cargo SBOM Precursor Workbench Kit**
5. **P-0479 Cargo Artifact Sidecar Contract Kit**
6. **P-0055 Cargo Workspace Toolchain Manifest Kit**
7. **P-0056 Cargo Install Policy & Cooldown Kit**
8. **P-0489 Cargo Build-Dir Consumer Transition Kit**
9. **P-0508 Cargo Build Script Delegation Kit**
10. **P-0244 SemVer API Diff Evidence Kit**
11. **P-0471 Cargo Artifact Handoff Kit**
12. **P-0507 Cargo Fix Campaign Kit**

## Why P-0479 rose

The archive already knew that sidecars were showing up.
What it still lacked was the “another tool author could implement against this tomorrow” layer.

The new fixture pack freezes:

- `sidecar-contract.lock`,
- `artifact-sidecar.index.json`,
- `sidecar-schema.report.json`,
- `sidecar-attachment.receipt.json`,
- `sidecar-association.receipt.json`,
- and `sidecar-surface.diff.json`.

That is meaningfully stronger than another round of prose about “companion files”.

## What this pass did not do

It did **not** collapse:

- broader artifact handoff manifests,
- SBOM precursor capture and transform-loss reporting,
- trusted publishing / post-publish receipts,
- or debug-support / docs.rs support contracts

into one fake “artifact metadata” crate.

That restraint improved the archive.

## Sources

- Cargo external tools / `compiler-artifact` messages: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo unstable features (`artifact-dir`, `sbom`, `CARGO_SBOM_PATH`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo changelog (`-Z sbom` fully-qualified package IDs): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust in 2026 / supply-chain goals: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
