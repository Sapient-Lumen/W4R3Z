
# Frontier salience — 2026-03-22 (184)

This pass did **not** open another MSRV finder, version badge, or CI-matrix helper lane.
It deepened **P-0036 MSRV Workspace Lab** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0011 Crate Health Contract Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0036 MSRV Workspace Lab**
7. **P-0532 Async Runtime Assurance Profile Kit**
8. **P-0486 Debuggability Support Contract Kit**
9. **P-0469 Cargo Rebuild Explanation Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0036 was the right lane to deepen now

Fresh Cargo docs and issue traffic make the missing value here more specific than “find one minimum compiler”:

- the Cargo `rust-version` docs now frame MSRV as an explicit package support promise and say it affects all Cargo targets in the package;
- the Cargo resolver docs are explicit that `fallback` uses heuristics in mixed-MSRV workspaces and can still pick versions that are too low or too high for some members because one lockfile must serve the workspace;
- the Rust 2024 Edition Guide and Cargo workspace docs are explicit that resolver choice is a root-level workspace setting and that virtual workspaces must set `workspace.resolver` explicitly;
- Cargo’s changelog now warns when a virtual workspace omits `workspace.resolver`, and Cargo 1.83 made lockfile v4 the default for create/update flows with a compatibility warning for older MSRVs;
- Rust 1.93 release notes say Cargo now respects `rust-version` when generating lockfiles;
- live Cargo issues show command-family divergence is real: `cargo run` can succeed while `cargo metadata` fails, and mixed-MSRV workspaces can still produce surprising or suboptimal resolution behavior;
- `cargo-msrv` remains useful and keeps improving, but its center of gravity is still find/verify, not publishing a portable multi-command support contract.

That combination makes the missing crate less “another searcher” and more a **reviewable workspace-support and authoring-floor contract**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. **effective workspace-promise truth**,
2. **policy-split drift truth**,
3. **portable MSRV support bundles**,
4. **command-family versus lockfile-authoring honesty**, and
5. **manual-review honesty when one workspace promise cannot stay singular**.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0036**, **P-0468**, **P-0484**, and **P-0535**.

Especially resist:

- another “one-number MSRV” badge generator,
- another brute-force finder that cannot export policy activation or command-family truth,
- another CI matrix expander without reviewable receipts,
- or another dashboard that cannot say whether lockfile authoring, metadata, and build support mean different things.
