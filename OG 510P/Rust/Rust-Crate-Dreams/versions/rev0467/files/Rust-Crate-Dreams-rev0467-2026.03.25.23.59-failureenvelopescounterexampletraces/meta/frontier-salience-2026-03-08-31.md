# Frontier salience scan — 2026-03-08 (thirty-first pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundary in that frontier: **workspace dependency inheritance and manifest-origin truth**.

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

Six current facts made this sharper again:

- Cargo workspace docs say features declared in `[workspace.dependencies]` are additive with member dependency features.
- Cargo dependency-spec docs still say inherited dependencies cannot use keys other than `optional` and `features`, with `default-features` named as an example.
- A current docs issue says that wording is easy to misread against what Cargo actually accepts or does.
- Cargo issue history shows member `default-features = false` can still be neutralized by workspace inheritance.
- Rust release notes document the converse case where a member inherited dependency with `default-features = true` re-enables defaults from a workspace dependency that disabled them.
- Cargo issue history still shows target-specific inherited dependencies are a real place where the answer becomes conservative or manual-review territory.

That means **P-0468** should now hand other people not just feature causes, version choices, lane reports, platform coverage, unification scope, and feature intent, but also:

- one `dependency-origin.report.json`,
- one explicit account of whether effective dependency policy came from workspace root, member manifest, or both,
- and one reviewable explanation of whether default features were disabled, neutralized, or re-enabled.

## What changed in the archive

Added:

- `meta/cargo-resolver-workspace-inheritance-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-31.md`
- `fixtures/cargo-resolve-why-kit/dependency-origin.report.schema.json`
- `fixtures/cargo-resolve-why-kit/scenarios/workspace_inherited_default_features_reenabled/*`
- `fixtures/cargo-resolve-why-kit/scenarios/target_specific_inherited_dependency_scope/*`
- `entries/2026-03-08-154.md`

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

1. keeping `dependency-origin.report` compact and subject-first,
2. preserving manifest origin instead of flattening everything into one dependency line,
3. and distinguishing disabled, neutralized, re-enabled, and manual-review-required outcomes for default features.

They should **not** drift into:

- another generic workspace manifest normalizer,
- a false claim that the member manifest alone authored the final dependency policy,
- or a broad cross-build/config story that forgets this is still a **resolver explanation** crate.
