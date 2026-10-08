# Frontier salience scan — 2026-03-08 (twenty-seventh pass)

## Main judgment

This pass again did **not** add a new top-level proposal.

Instead, it upgraded **P-0494 Cargo Compile-Time-Deps Workflow Kit** into a more implementation-shaped crate plan by freezing the next boundary the archive still needed most in that frontier: **selection coverage and workspace invocation truth** above tool-only or check-like runs.

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

## Why P-0494 is still worth deepening

Seven current facts make the crate boundary sharper again:

- Cargo still documents `--compile-time-deps` as tool-oriented unstable substrate,
- rust-analyzer documents `cargo.allTargets = true` by default,
- rust-analyzer documents that `check.allTargets` inherits that target-class coverage unless overridden,
- Cargo documents `--all-targets` as a real expansion across lib/bin/test/bench/example lanes,
- rust-analyzer documents `check.workspace = true` by default and says `{label}` behaves much like `check.workspace = false`,
- rust-analyzer documents `per_workspace` and `once` invocation strategies for override commands,
- and issue reports show both dev-proc-macro coverage holes and startup-scope leakage in practice.

That means **P-0494** should not stop at command provenance.
A sharper 0.1 contract is now:

- one tool-build receipt,
- one compile-surface manifest,
- one parity report,
- one fallback plan,
- one comparison-baseline lock,
- one override-command receipt,
- one selection-coverage report,
- and one workspace-invocation receipt.

## What changed in the archive

Added:

- `meta/cargo-tool-workflow-coverage-boundaries-2026-03-08.md`
- `meta/frontier-salience-2026-03-08-27.md`
- `fixtures/cargo-compile-time-deps-workflow-kit/selection-coverage.report.schema.json`
- `fixtures/cargo-compile-time-deps-workflow-kit/workspace-invocation.receipt.schema.json`
- `fixtures/cargo-compile-time-deps-workflow-kit/scenarios/alltargets_false_dev_proc_macro_gap/*`
- `fixtures/cargo-compile-time-deps-workflow-kit/scenarios/check_workspace_false_first_run_leakage/*`
- `fixtures/cargo-compile-time-deps-workflow-kit/scenarios/linked_projects_once_opened_root_scope/*`
- `entries/2026-03-08-150.md`

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

1. keeping target-class coverage vocabulary small and conservative,
2. trying one real support bundle that includes both `selection-coverage.report.json` and `workspace-invocation.receipt.json`,
3. and preserving exact/manual-review boundaries for startup leakage instead of sanding them down.

They should **not** drift into:

- a rust-analyzer fork,
- a generic diagnostics dashboard,
- or a false claim that tool-facing success proves full-build or full-workspace coverage.

## Sources

- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- Cargo build command docs: https://doc.rust-lang.org/cargo/commands/cargo-build.html
- Cargo unstable docs (`compile-time-deps`): https://doc.rust-lang.org/cargo/reference/unstable.html#compile-time-deps
- RFC 3477 (`cargo check` policy): https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
- rust-analyzer issue #18528: https://github.com/rust-lang/rust-analyzer/issues/18528
- rust-analyzer issue #17126: https://github.com/rust-lang/rust-analyzer/issues/17126
