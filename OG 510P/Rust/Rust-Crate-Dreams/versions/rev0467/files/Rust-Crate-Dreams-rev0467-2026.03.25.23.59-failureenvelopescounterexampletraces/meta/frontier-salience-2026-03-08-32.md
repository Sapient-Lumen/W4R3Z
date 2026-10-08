# Frontier salience scan — 2026-03-08 (thirty-second pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing another missing receiver-facing boundary in that frontier: **feature origin, hidden optional-dependency aliases, and weak dependency forwarding preconditions**.

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

- Cargo feature docs say optional dependencies automatically create implicit feature aliases.
- The same docs say any `dep:` reference suppresses that implicit alias.
- The same docs say `pkg/feat` also activates an optional dependency, while `pkg?/feat` only forwards a feature if another path already activated that dependency.
- Registry index docs still preserve namespaced and weak dependency syntax separately in `features2`, which is a sign that authored feature syntax is real substrate rather than a throwaway presentation detail.
- Cargo issue history says `cargo metadata` lost the ability to distinguish magically created optional-dependency features from explicit user-authored features.
- Current issue reports and changelog notes show that `dep:` / `pkg/feat` / `pkg?/feat` combinations can still produce confusing errors, edge cases, or misleading downstream interpretations.

That means **P-0468** should now hand other people not just feature causes, version choices, duplicate-build groups, lane reports, platform coverage, unification scope, feature intent, and dependency origin, but also:

- one `feature-origin.report.json`,
- one explicit account of whether a feature-like name is public, hidden, implicit, or not actually a real manifest feature,
- and one reviewable explanation of whether a dependency-feature clause activated an optional dependency directly or only forwarded a feature conditionally.

## What changed in the archive

Added:

- `meta/cargo-resolver-feature-origin-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-32.md`
- `fixtures/cargo-resolve-why-kit/feature-origin.report.schema.json`
- `fixtures/cargo-resolve-why-kit/scenarios/dep_syntax_hidden_optional_alias/*`
- `fixtures/cargo-resolve-why-kit/scenarios/weak_dependency_feature_requires_prior_activation/*`
- `entries/2026-03-08-155.md`

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

1. keeping `feature-origin.report` short and subject-first,
2. preserving whether a feature name is public, hidden, implicit, or merely feature-like,
3. and preserving whether optional-dependency activation was direct, conditional, or still manual-review territory.

They should **not** drift into:

- another generic Cargo feature visualizer,
- a false claim that every emitted `cfg(feature = ...)` name is a real public feature,
- or a vague “optional dependencies are confusing” story that loses the difference between `dep:`, `pkg/feat`, and `pkg?/feat`.
