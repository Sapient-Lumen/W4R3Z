# Frontier salience scan — 2026-03-16 (build-std lane upgraded around stage-aware recipes, locks, and receipts)

This pass did not add a new top-level proposal.
It upgraded **P-0430 Build-Std Workbench Kit** into a more implementation-shaped lane by adding the next missing support-layer artifacts: **stage-posture reports, evidence-source receipts, and a real schema/scenario substrate**.

## Main judgment

The strongest contribution here is not another thin wrapper around `-Z build-std`.
It is the boring crate that can hand other people:

- one sysroot recipe,
- one sysroot lock,
- one direct build receipt,
- one stage report,
- one diff report,
- and one evidence-source receipt.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0429 rustc_public Analysis Workbench Kit**
5. **P-0490 Cargo Lock Contention Witness Kit**
6. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
7. **P-0430 Build-Std Workbench Kit**
8. **P-0478 Cargo Future-Incompat Triage Kit**
9. **P-0470 Cargo Package Review Kit**
10. **P-0125 Cargo SBOM Precursor Workbench Kit**
11. **P-0471 Cargo Artifact Handoff Kit**
12. **P-0055 Cargo Workspace Toolchain Manifest Kit**
13. **P-0244 SemVer API Diff Evidence Kit**

## Why P-0430 moved up

Fresh official substrate now lines up around four sharper truths:

- Rust’s 2025H2 goals explicitly target stabilizing a core MVP of `build-std`.
- The July 2025 goals update split the work into a staged plan: manual enablement, explicit std dependencies, target-modifier/codegen options, and automatic rebuild behavior.
- The October 2025 program-management update says build-std RFCs were posted for context, always-on rebuild configuration, and explicit std dependencies.
- Cargo’s unstable docs already define concrete operational constraints for the current workflow, while the changelog keeps tightening `-Zbuild-std`, `build-std-features`, and target-spec probing behavior.

That means a crate can now promise something better than “we ran Cargo with nightly flags.”
It can promise a compact bundle that says:

- what recipe was intended,
- what source/toolchain inputs were actually used,
- which stage posture the workflow belongs to,
- and what changed across two sysroot builds.

## What changed in the archive

Added:
- `meta/build-std-workbench-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-23.md`
- `fixtures/build-std-workbench-kit/`
- `entries/2026-03-16-194.md`

Updated:
- `proposals/build-std-workbench-kit.md`
- `README.md`
- `INDEX.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- ABI coherence profiles,
- sanitizer instrumentation receipts,
- source-path / source-availability diagnosis,
- or compile-time-deps/editor parity

into one fake “sysroot support” crate.

## Sources

- Project goals for 2025H2: https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/
- Project goals update — July 2025: https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- Program management update — October 2025: https://blog.rust-lang.org/inside-rust/2025/11/19/program-management-update--october-2025/
- Cargo unstable docs (`build-std`): https://doc.rust-lang.org/cargo/reference/unstable.html#build-std
- Cargo changelog (`-Zbuild-std`, `build-std-features`, target-spec probing): https://doc.rust-lang.org/cargo/CHANGELOG.html
