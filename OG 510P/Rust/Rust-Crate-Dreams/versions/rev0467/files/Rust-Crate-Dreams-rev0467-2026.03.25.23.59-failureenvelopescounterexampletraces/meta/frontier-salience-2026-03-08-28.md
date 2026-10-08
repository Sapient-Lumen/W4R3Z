# Frontier salience scan — 2026-03-08 (twenty-eighth pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** into a more implementation-shaped crate plan by freezing the next missing boundary in that frontier: **dependency-kind lane partition and platform-coverage truth**.

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

## Why P-0468 was still the best next move

Six current facts make the crate boundary sharper again:

- Cargo’s resolver docs say resolver v2 keeps target-specific inactive edges, build/proc-macro lanes, and dev lanes from unifying in important cases.
- The features docs repeat those same lane-split rules, making them user-facing contract and not just internal behavior.
- `cargo tree` says its feature view is only *pretty close* to what Cargo will build and may merge features for convenience.
- `cargo metadata` includes all targets unless `--filter-platform` narrows the resolve output.
- `--unit-graph` now documents that it captures the internal graph more completely, including feature relationships between dependency kinds, but it remains unstable.
- Current issue reports still show dev-lane and proc-macro/build-lane cases where human-facing views and actual build behavior diverge.

That means **P-0468** should now hand other people not just cause chains and version receipts, but also:

- one `resolve-why.lock`,
- one `feature-causes.json`,
- one `version-choices.json`,
- one `duplicate-builds.json`,
- one `lane-partition.report.json`,
- one `platform-coverage.report.json`,
- one `resolver-choice.receipt.json`,
- and one `resolution-diff.report.json` when two captures are compared.

## What changed in the archive

Added:

- `meta/cargo-resolver-lane-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-28.md`
- `fixtures/cargo-resolve-why-kit/lane-partition.report.schema.json`
- `fixtures/cargo-resolve-why-kit/platform-coverage.report.schema.json`
- `fixtures/cargo-resolve-why-kit/scenarios/resolver2_dev_normal_tree_merge_warning/*`
- `fixtures/cargo-resolve-why-kit/scenarios/nonmatching_target_specific_dependency_omitted/*`
- `fixtures/cargo-resolve-why-kit/scenarios/proc_macro_build_normal_lane_manual_review/*`
- `entries/2026-03-08-151.md`

Updated:

- `proposals/cargo-resolver-explanation-kit.md`
- `fixtures/cargo-resolve-why-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/territory-map.md`
- `meta/llm-hygiene.md`

## What should happen next

The best next passes should prefer:

1. keeping lane vocabulary small and conservative,
2. freezing `--filter-platform` and selected-target choices in every serious bundle,
3. and preserving manual-review markers whenever human-facing views merge lanes the selected build may separate.

They should **not** drift into:

- another generic graph browser,
- a false claim that stable Cargo surfaces already expose exact dependency-kind feature truth,
- or a broad host/target/build-script doctor that forgets P-0468 is still a **resolver explanation** crate.

## Sources

- Cargo dependency resolution: https://doc.rust-lang.org/cargo/reference/resolver.html
- Cargo features: https://doc.rust-lang.org/cargo/reference/features.html
- `cargo tree`: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- `cargo metadata`: https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- Cargo unstable features (`unit-graph`, `feature-unification`): https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo issue #11261: https://github.com/rust-lang/cargo/issues/11261
- Cargo issue #14415: https://github.com/rust-lang/cargo/issues/14415
