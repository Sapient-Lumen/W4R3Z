# Frontier salience scan — 2026-03-16 (future-incompat made fixture-first)

This pass did not add a new top-level proposal.
It upgraded **P-0478 Cargo Future-Incompat Triage Kit** into a fixture-first, more implementation-shaped lane.

## Main judgment

The strongest contribution here is not another diagnostics viewer.
It is the **shared memory and release-truth layer** above Cargo’s future-incompat substrate.

The official picture now makes that lane unusually concrete:

- Cargo already detects future-incompatible warnings in dependencies and can print a full report.
- `cargo report` already recalls stored reports and can filter by report id or package.
- Cargo config already exposes a dedicated `[future-incompat-report]` table.
- The build-analysis goal explicitly treats future-incompat reports as one of the few build-adjacent things Cargo already persists.
- Rust release notes show that the contents of future-incompat reports can expand across compiler eras (for example const-eval errors entering the report surface).

That means the missing crate is the boring coordination layer with:

1. a capture lock,
2. a finding snapshot,
3. an owner / waiver / release ledger,
4. an evidence-source receipt,
5. and a diff / gate bundle.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0429 rustc_public Analysis Workbench Kit**
3. **P-0478 Cargo Future-Incompat Triage Kit**
4. **P-0055 Cargo Workspace Toolchain Manifest Kit**
5. **P-0056 Cargo Install Policy & Cooldown Kit**
6. **P-0489 Cargo Build-Dir Consumer Transition Kit**
7. **P-0508 Cargo Build Script Delegation Kit**
8. **P-0244 SemVer API Diff Evidence Kit**
9. **P-0507 Cargo Fix Campaign Kit**
10. **P-0484 Toolchain & Target Support Contract Kit**
11. **P-0477 Cargo Publish Receipt Join Kit**
12. **P-0480 Cargo Global Cache Policy & GC Receipt Kit**

## Why P-0478 rose

Earlier archive work already knew that Cargo future-incompat reporting mattered.
What it still lacked was the “someone else could actually build against this” layer.

The new fixture pack freezes:

- `future-incompat.capture-lock.json`,
- `finding-snapshot.report.json`,
- `triage-ledger.report.json`,
- `owner-map.policy.json`,
- `waiver-ledger.policy.json`,
- `release-gate.report.json`,
- `remediation-candidates.report.json`,
- and `evidence-source.receipt.json`.

That is meaningfully stronger than another round of prose about dependency-risk warnings.

## What this pass did not do

It did **not** collapse:

- official Cargo report storage/display,
- general build-analysis warehousing,
- fix-orchestration / codemod work,
- resolver explanation,
- and semver / upgrade proof crates

into one fake “dependency warning platform”.

That restraint improved the archive.

## Sources

- Cargo future incompat report reference: https://doc.rust-lang.org/cargo/reference/future-incompat-report.html
- `cargo report`: https://doc.rust-lang.org/cargo/commands/cargo-report.html
- Cargo config (`[future-incompat-report]`): https://doc.rust-lang.org/cargo/reference/config.html
- Cargo build analysis goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Rust release notes (const-eval errors in future-incompat reports): https://doc.rust-lang.org/beta/releases.html
