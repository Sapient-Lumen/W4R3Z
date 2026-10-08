# Frontier salience scan — 2026-03-08 (twenty-ninth pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** by freezing the next missing receiver-facing boundary in that frontier: **feature-unification policy and participant scope**.

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

Four current facts made this sharper again:

- Cargo unstable docs define `resolver.feature-unification` with explicit `selected`, `workspace`, and `package` modes.
- Resolver docs still say dependency features are unified across multiple selected workspace packages.
- The feature-unification tracking issue still has unresolved representation questions for package mode.
- The long-running package-set-sensitivity issue remains open.

That means **P-0468** should now hand other people not just cause chains, version choices, duplicate-build groups, lane reports, and platform coverage, but also:

- one `unification-scope.report.json`,
- one explicit account of selected packages versus participating packages,
- and one reviewable explanation of whether the answer changed because policy changed.

## What changed in the archive

Added:

- `meta/cargo-resolver-unification-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-29.md`
- `fixtures/cargo-resolve-why-kit/unification-scope.report.schema.json`
- `fixtures/cargo-resolve-why-kit/scenarios/workspace_mode_out_of_selection_feature_pressure/*`
- `entries/2026-03-08-152.md`

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

1. keeping the unification vocabulary small and subject-first,
2. distinguishing selected-package scope from participating-package scope,
3. and preserving explicit explanations when a policy change, not a manifest change, caused the result.

They should **not** drift into:

- another generic graph browser,
- a false claim that `cargo tree` already preserves package-mode truth,
- or a compile-time-deps/editor-parity story that forgets this is still a **resolver explanation** crate.
