# Frontier salience scan — 2026-03-16 (artifact handoff made fixture-first)

This pass did not add a new top-level proposal.
It upgraded **P-0471 Cargo Artifact Handoff Kit** into a fixture-first, more implementation-shaped lane.

## Main judgment

The strongest contribution here is not another release platform and not another raw Cargo-output parser.
It is the **produced-artifact handoff exactness layer** above Cargo JSON and below sidecar / publish / release policy crates.

That lane became much more concrete because:

- Cargo external-tools JSON already emits `compiler-artifact`, `build-script-executed`, and `build-finished` messages for machine consumers.
- `--artifact-dir` exists because downstream artifact lookup is still awkward enough to need explicit copied-output help.
- the build-dir-layout-v2 testing push explicitly tells people to run tests and release processes that touch build-dir / target-dir against the new layout,
- Cargo’s custom-final-artifact design work says build scripts cannot simply write directly into the artifact-dir because Cargo still needs collision reporting and concurrent-access safety,
- and build-analysis work is adding session identifiers that can optionally link one handoff bundle to one build invocation.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0429 rustc_public Analysis Workbench Kit**
3. **P-0478 Cargo Future-Incompat Triage Kit**
4. **P-0125 Cargo SBOM Precursor Workbench Kit**
5. **P-0471 Cargo Artifact Handoff Kit**
6. **P-0479 Cargo Artifact Sidecar Contract Kit**
7. **P-0055 Cargo Workspace Toolchain Manifest Kit**
8. **P-0056 Cargo Install Policy & Cooldown Kit**
9. **P-0489 Cargo Build-Dir Consumer Transition Kit**
10. **P-0508 Cargo Build Script Delegation Kit**
11. **P-0244 SemVer API Diff Evidence Kit**
12. **P-0507 Cargo Fix Campaign Kit**

## Why P-0471 rose

The archive already knew this was a promising idea.
What it still lacked was the “someone else can build against this tomorrow” layer.

The new fixture pack freezes:

- `artifact-handoff.lock`,
- `artifact-manifest.json`,
- `artifact-origin.receipt.json`,
- `native-output.report.json`,
- `handoff.receipt.json`,
- and `artifact-layout.diff.json`.

That is much stronger than another round of prose about “one stable artifact manifest”.

## What this pass did not do

It did **not** collapse:

- build-dir consumer transition receipts,
- artifact↔sidecar shipping policy,
- SBOM precursor normalization,
- publish identity / post-publish joins,
- or historical build-analysis storage

into one fake “artifact output” crate.

That restraint improved the archive.

## Sources

- Cargo external tools / artifact messages: https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo unstable features (`artifact-dir`, `cargo report sessions`, `build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93 / custom final artifacts discussion: https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Build dir layout v2 call for testing: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build-analysis goal / build identifiers: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
