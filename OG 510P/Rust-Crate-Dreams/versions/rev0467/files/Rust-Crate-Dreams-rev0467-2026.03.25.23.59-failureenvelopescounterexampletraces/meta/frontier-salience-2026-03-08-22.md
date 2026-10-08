# Frontier salience scan — 2026-03-08 (twenty-second pass)

## Main judgment

This pass **did not** add a new top-level proposal.

Instead, it upgraded **P-0468 Cargo Resolver Explanation Kit** into a more implementation-shaped crate plan by freezing the two boundaries the archive still needed most: **MSRV-aware version choice** and **exact/manual-review evidence limits**.

## Ranked frontier after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0469 Cargo Rebuild Explanation Kit**
3. **P-0505 Cargo Host/Target Scope Contract Kit**
4. **P-0503 Assurance Case Workbench Kit**
5. **P-0504 Linker Lane Contract & Diagnosis Kit**
6. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
7. **P-0486 Debuggability Support Contract Kit**
8. **P-0433 MC/DC Coverage Workbench Kit**
9. **P-0453 Safety Contract Consumer Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0468 moved up

Five current facts make it more concrete than before:

- Cargo’s resolver docs now spell out MSRV-aware version preference and mixed-workspace heuristics.
- The same docs also spell out the two-pass feature story: lockfile-time “all workspace features enabled” versus compile-time selected features.
- `cargo tree` explicitly says its view is only *pretty close* to what Cargo will build and does not guarantee exact equivalence.
- The Cargo plumbing goal still says `cargo metadata` excludes feature resolution.
- `--unit-graph` remains unstable and its tracking issue still has unresolved design questions, which means a receiver-facing bundle must preserve uncertainty instead of hiding it.

## What changed in the archive

Added:

- `meta/cargo-resolver-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-22.md`
- `fixtures/cargo-resolve-why-kit/resolve-why.lock.schema.json`
- `fixtures/cargo-resolve-why-kit/scenarios/msrv_workspace_version_choice/*`
- `fixtures/cargo-resolve-why-kit/scenarios/workspace_selection_masks_missing_feature/*`
- `entries/2026-03-08-145.md`

Updated:

- `proposals/cargo-resolver-explanation-kit.md`
- `fixtures/cargo-resolve-why-kit/README.md`
- `fixtures/cargo-resolve-why-kit/resolver-choice.receipt.schema.json`
- `README.md`
- `INDEX.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/territory-map.md`
- `meta/llm-hygiene.md`

## What should happen next

The best next passes should prefer:

1. freezing `resolve-why.lock` and receipt exactness vocabulary,
2. proving adapter-free capture on one tiny real workspace,
3. and keeping resolver why-bundles separate from rebuild receipts, workspace-hack optimization, and generic graph exports.

They should **not** drift into:

- another graph query library,
- another “Cargo doctor” that absorbs every build concern,
- or a faux-certainty tool that treats `cargo tree` output as exact build truth.

## Sources

- Cargo dependency resolution: https://doc.rust-lang.org/cargo/reference/resolver.html
- `cargo tree`: https://doc.rust-lang.org/cargo/commands/cargo-tree.html
- Cargo unstable features: https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo plumbing goal: https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Tracking issue for `--unit-graph`: https://github.com/rust-lang/cargo/issues/8002
- Tracking issue for workspace feature-unification: https://github.com/rust-lang/cargo/issues/14774
- Cargo issue on workspace feature masking: https://github.com/rust-lang/cargo/issues/14021
