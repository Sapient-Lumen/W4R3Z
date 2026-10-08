# Frontier salience scan — 2026-03-08 (thirty-third pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing another missing receiver-facing boundary in that frontier: **dependency identity, rename surfaces, and registry truth**.

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

- Cargo dependency-spec docs say that when a dependency is renamed, feature names take after the **dependency name**, not the original package name.
- The same docs say transitive dependency-feature forwarding follows that renamed dependency key too.
- `cargo metadata` docs say package definitions are intended to reproduce manifest information even when resolve output is filtered by target.
- Registry-index docs say renamed dependencies swap fields across publish API / index / `cargo metadata`, so the alias and original package name do not live in the same slot everywhere.
- Cargo issue #12546 says inherited workspace dependencies still cannot simply be renamed from the member side.
- Recent private-registry issue history says renamed + gated dependencies can still produce missing-package or verification failures where another person needs an honest identity explanation.

That means **P-0468** should now hand other people not just feature causes, version choices, duplicate-build groups, lane reports, platform coverage, unification scope, feature intent, dependency origin, and feature origin, but also:

- one `dependency-identity.report.json`,
- one explicit account of the local dependency key versus the original package name,
- and one reviewable explanation of how the same rename appears in manifest features, `cargo metadata`, and registry/index publication.

## What changed in the archive

Added:

- `meta/cargo-resolver-dependency-identity-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-33.md`
- `fixtures/cargo-resolve-why-kit/dependency-identity.report.schema.json`
- `fixtures/cargo-resolve-why-kit/scenarios/renamed_optional_dependency_feature_namespace/*`
- `fixtures/cargo-resolve-why-kit/scenarios/workspace_inherited_dependency_rename_ignored/*`
- `entries/2026-03-08-156.md`

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

1. keeping `dependency-identity.report` short and subject-first,
2. preserving local dependency key versus original package name explicitly,
3. preserving feature-reference tokens separately from registry/index field mappings,
4. and preserving when inheritance or registry publication makes the answer conservative or manual-review-required.

They should **not** drift into:

- another generic Cargo manifest linter,
- a fake claim that every surface uses the same field names for renamed dependencies,
- or a vague “renaming is confusing” story that loses the difference between local dependency keys, package names, metadata fields, and publish/index fields.
