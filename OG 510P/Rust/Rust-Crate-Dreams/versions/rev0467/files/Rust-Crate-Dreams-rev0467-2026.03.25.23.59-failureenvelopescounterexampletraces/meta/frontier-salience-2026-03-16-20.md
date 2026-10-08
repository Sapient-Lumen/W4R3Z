# Frontier salience scan — 2026-03-16 (package review promoted into a fixture-first workspace-aware lane)

This pass did not add a new top-level proposal.
It upgraded **P-0470 Cargo Package Review Kit** into a more implementation-shaped lane with schema files, scenario packs, and a clearer statement of what the crate should actually hand other people.

## Main judgment

The strongest contribution here is not another publish platform and not another provenance story.
It is the **source-bundle review layer** above `cargo package` and below trusted-publishing rehearsal, post-publish registry receipts, and general attestations.

That lane became much more concrete because:

- the `cargo package` docs already define a rich packaging contract: manifest normalization, section removal, lockfile inclusion, `.cargo_vcs_info.json`, symlink flattening, build verification, and build-script source-file checks,
- the changelog says `-Zpackage-workspace` now supports packaging interdependent workspace crates without requiring publication to actual registries,
- Rust release notes now tell users not to rely on `cargo publish` as the place `.crate` artifacts persist,
- and the Cargo 1.90 development-cycle discussion made workspace-root license/readme copy-in behavior explicit enough to treat as a review seam.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0429 rustc_public Analysis Workbench Kit**
5. **P-0478 Cargo Future-Incompat Triage Kit**
6. **P-0470 Cargo Package Review Kit**
7. **P-0125 Cargo SBOM Precursor Workbench Kit**
8. **P-0471 Cargo Artifact Handoff Kit**
9. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**
11. **P-0055 Cargo Workspace Toolchain Manifest Kit**
12. **P-0244 SemVer API Diff Evidence Kit**

## Why P-0470 rose

The archive already knew package review mattered.
What it still lacked was the “another tool author could build against this tomorrow” layer.

This pass freezes:

- `package-review.lock`,
- `workspace-package-set.report.json`,
- `crate-contents.json`,
- `manifest-normalization.report.json`,
- `path-explanation.report.json`,
- `package-policy.report.json`,
- `vcs-snapshot.review.json`,
- `evidence-source.receipt.json`,
- and scenario families for workspace interdependencies, external-file copy-in, dirty VCS snapshots, and generated-asset budget warnings.

That is much stronger than another paragraph saying “review your `.crate` before publish.”

## What this pass deliberately did not do

It did **not** collapse:

- trusted publishing rehearsal,
- post-publish registry receipts,
- provenance / attestation,
- SBOM precursor capture,
- or general artifact-sidecar attachment

into one fake “publish security” crate.

That restraint improved the repo.

## Sources

- `cargo package`: https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Publishing on crates.io: https://doc.rust-lang.org/cargo/reference/publishing.html
- Cargo changelog (`-Zpackage-workspace`): https://doc.rust-lang.org/cargo/CHANGELOG.html
- Rust release notes (`cargo publish` artifact behavior): https://doc.rust-lang.org/beta/releases.html
- Cargo 1.90 development cycle (workspace license/readme copy discussion): https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
