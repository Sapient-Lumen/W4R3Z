# Frontier salience scan — 2026-03-08 (twenty-sixth pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0494 Cargo Compile-Time-Deps Workflow Kit** into a more implementation-shaped crate plan by freezing the boundary the archive still needed most in that frontier: **comparison-baseline truth and override-command provenance** above tool-only or check-like runs.

## Ranked frontier after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0469 Cargo Rebuild Explanation Kit**
3. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
4. **P-0490 Cargo Lock Contention Witness Kit**
5. **P-0496 Cargo Vendor & Source Parity Kit**
6. **P-0505 Cargo Host/Target Scope Contract Kit**
7. **P-0058 native-deps-kit**
8. **P-0503 Assurance Case Workbench Kit**
9. **P-0504 Linker Lane Contract & Diagnosis Kit**
10. **P-0486 Debuggability Support Contract Kit**

## Why P-0494 moved up

Seven current facts make it more concrete than before:

- Cargo documents `--compile-time-deps` as a permanently unstable tool-oriented mode,
- RFC 3477 keeps `cargo build` as the stronger correctness boundary,
- rust-analyzer documents `check.overrideCommand` and `cargo.buildScripts.overrideCommand` as first-class config,
- rust-analyzer documents that override commands must emit JSON,
- rust-analyzer documents `{label}` semantics that effectively narrow comparison scope,
- rust-analyzer documents `cargo.targetDir` as a real contention/duplication trade-off,
- and issue reports show that relative/custom override commands and toolchain-specific overrides still create real support incidents.

That means **P-0494** no longer needs to act like one tool-build receipt is enough.
A sharper 0.1 contract is now:

- one tool-build receipt,
- one compile-surface manifest,
- one parity report,
- one fallback plan,
- one comparison-baseline lock,
- and one override-command receipt.

## What changed in the archive

Added:

- `meta/cargo-compile-time-deps-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-26.md`
- `fixtures/cargo-compile-time-deps-workflow-kit/comparison-baseline.lock.schema.json`
- `fixtures/cargo-compile-time-deps-workflow-kit/override-command.receipt.schema.json`
- `fixtures/cargo-compile-time-deps-workflow-kit/scenarios/label_scoped_override_vs_workspace_baseline/*`
- `fixtures/cargo-compile-time-deps-workflow-kit/scenarios/relative_override_command_manual_review/*`
- `fixtures/cargo-compile-time-deps-workflow-kit/scenarios/paired_buildscripts_override_toolchain_specific/*`
- `entries/2026-03-08-149.md`

Updated:

- `proposals/cargo-compile-time-deps-workflow-kit.md`
- `fixtures/cargo-compile-time-deps-workflow-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/territory-map.md`
- `meta/llm-hygiene.md`

## What should happen next

The best next passes should prefer:

1. freezing `comparison-baseline.lock` vocabulary,
2. trying one real rust-analyzer support bundle with both check and build-script override lanes,
3. and keeping relative/custom command provenance visible instead of normalized away.

They should **not** drift into:

- a new universal wrapper framework,
- a vague editor/Cargo diagnosis dashboard,
- or an equivalence layer that quietly treats tool-only success as build correctness.

## Sources

- Cargo unstable docs (`compile-time-deps`): https://doc.rust-lang.org/cargo/reference/unstable.html#compile-time-deps
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- RFC 3477 (`cargo check` policy): https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
- Cargo build-dir layout goal: https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- rust-analyzer issue #10793: https://github.com/rust-lang/rust-analyzer/issues/10793
- rust-analyzer issue #5962: https://github.com/rust-lang/rust-analyzer/issues/5962
- esp-idf-sys issue #113: https://github.com/esp-rs/esp-idf-sys/issues/113
