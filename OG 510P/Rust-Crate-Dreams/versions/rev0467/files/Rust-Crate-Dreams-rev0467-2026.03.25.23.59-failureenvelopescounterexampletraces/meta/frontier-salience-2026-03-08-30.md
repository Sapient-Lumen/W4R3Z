# Frontier salience scan — 2026-03-08 (thirtieth pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundary in that frontier: **feature intent and suppression truth**.

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

Five current facts made this sharper again:

- Cargo features docs explicitly warn that `default-features = false` may still fail to keep defaults off if another dependency path enables them.
- The same docs say `--no-default-features` applies to the selected packages.
- Resolver docs still say dependency features unify across multiple selected workspace packages.
- The feature-unification tracking issue is still open.
- Open issues still show that the effective feature state can differ across `--bin`, `-p`, workspace-root, and dependency-edge contexts.

That means **P-0468** should now hand other people not just feature causes, version choices, lane reports, platform coverage, and unification participant scope, but also:

- one `feature-intent.report.json`,
- one explicit account of positive versus negative feature intent,
- and one reviewable explanation of why a feature stayed on even when the subject asked for it to stay off.

## What changed in the archive

Added:

- `meta/cargo-resolver-feature-intent-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-30.md`
- `fixtures/cargo-resolve-why-kit/feature-intent.report.schema.json`
- `fixtures/cargo-resolve-why-kit/scenarios/default_features_false_masked_by_workspace/*`
- `fixtures/cargo-resolve-why-kit/scenarios/bin_subject_feature_pressure/*`
- `entries/2026-03-08-153.md`

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

1. keeping the feature-intent vocabulary small and subject-first,
2. distinguishing **asked to enable** from **asked to keep off**,
3. and preserving explicit explanations when workspace pressure overrides negative intent.

They should **not** drift into:

- another generic feature-matrix runner,
- a false claim that `cargo tree` or raw graph exports already preserve subject intent,
- or a broad workflow/IDE tool that forgets this is still a **resolver explanation** crate.
