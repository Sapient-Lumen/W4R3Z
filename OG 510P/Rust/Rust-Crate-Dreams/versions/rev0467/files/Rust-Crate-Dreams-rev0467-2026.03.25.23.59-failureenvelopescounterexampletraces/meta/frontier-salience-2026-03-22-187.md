# Frontier salience — 2026-03-22 (187)

This pass did **not** open another timing dashboard, cache-cleanup helper, or generic Cargo workflow doctor.
It deepened **P-0469 Cargo Rebuild Explanation Kit** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0535 Dependency Lifecycle Transition Kit**
3. **P-0011 Crate Health Contract Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0469 Cargo Rebuild Explanation Kit**
7. **P-0486 Debuggability Support Contract Kit**
8. **P-0036 MSRV Workspace Lab**
9. **P-0532 Async Runtime Assurance Profile Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0469 was the right lane to deepen now

Fresh official Rust/Cargo sources make the missing value here more specific than “better build analysis” or “another compile-times dashboard”:

- the 2025 State of Rust survey still says slow compile times and storage use remain among the biggest productivity problems;
- the March 2026 challenges write-up again keeps build times in the short list of ecosystem pain;
- current unstable Cargo docs now document persisted build-analysis sessions and `cargo report sessions`, `cargo report timings`, and `cargo report rebuilds`;
- the Cargo 1.94 development-cycle update says those report commands are becoming a real user-facing substrate;
- the relink-don’t-rebuild goal explicitly says reverse dependencies still rebuild after many edits that should ideally only relink;
- the build-dir-layout goal and March 2026 test call both say route/layout/locking shape is still active upstream work;
- Cargo’s current build-cache docs now make final-artifact and intermediate-artifact routes first-class separate paths;
- and rust-analyzer’s `cargo.targetDir` escape hatch shows that tool-owned route divergence is still a live part of ordinary workflows.

That combination sharpens the missing crate.
It is not most missing as another warehouse or graph viewer.
It is missing as a **portable rebuild-causality contract** for:

1. **comparison scope**,
2. **artifact-route drift**,
3. **observed rebuild causes**,
4. **reverse-impact honesty**, and
5. **portable support bundles**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. one **comparison-scope receipt** saying whether two sessions are actually comparable across command family, profile, targets, workspace selection, wrappers, and routes;
2. one **artifact-route drift report** saying whether build-dir, target-dir, rust-analyzer private target-dir, or wrapper-hash lanes changed the reuse context;
3. one **baseline-authority receipt** explaining why this comparison window was chosen;
4. one **reverse-impact report** that records observed fanout without pretending semantic interface change was proven;
5. one **portable rebuild-support bundle** keeping scope, route, evidence, exactness, cause, and adjacent-lane imports separate;
6. and one **manual-review zone** whenever tool-only context or route drift outruns what the bundle can honestly prove.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0469**, **P-0490**, **P-0494**, **P-0035**, and **P-0045**.

Especially resist:

- another timing dashboard that cannot export reviewable receipts,
- another cache-cleaner or retry helper that cannot explain the incident,
- another profiler that cannot separate comparison scope from cause,
- or another Cargo wrapper that quietly over-reads rust-analyzer/tool-only context as rebuild proof.
