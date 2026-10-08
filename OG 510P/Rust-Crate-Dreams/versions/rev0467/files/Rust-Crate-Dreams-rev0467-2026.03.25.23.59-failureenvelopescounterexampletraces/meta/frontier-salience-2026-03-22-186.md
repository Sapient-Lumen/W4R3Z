# Frontier salience — 2026-03-22 (186)

This pass did **not** open another cross-target bootstrapper, installer wrapper, or CI matrix helper.
It deepened **P-0484 Toolchain & Target Support Contract Kit** instead.

## Current top frontier

1. **P-0484 Toolchain & Target Support Contract Kit**
2. **P-0535 Dependency Lifecycle Transition Kit**
3. **P-0011 Crate Health Contract Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0120 Unsafe Contract Auditor Kit**
6. **P-0486 Debuggability Support Contract Kit**
7. **P-0036 MSRV Workspace Lab**
8. **P-0532 Async Runtime Assurance Profile Kit**
9. **P-0469 Cargo Rebuild Explanation Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**

## Why P-0484 was the right lane to deepen now

Fresh official Rust sources make the missing value here more specific than “better cross-compilation docs” or “another support matrix generator”:

- the January 2026 safety-critical write-up explicitly asks for target-focused readiness checklists that translate raw target-tier information into practical adoption guidance;
- the March 2026 challenges write-up says cross-compilation friction, `no_std` ecosystem gaps, and domain-specific pain still scale with experience;
- rustup 1.29.0 now makes host availability and environment shape more concrete again by adding official Solaris hosts and better `rust-analyzer` PATH fallback behavior;
- rustup’s override docs are still explicit that `path` toolchains ignore `components`, `targets`, and `profile`;
- Cargo’s current build-cache/config docs now keep `target-dir` and `build-dir` separate with configurable authority routes;
- docs.rs metadata/build docs make default targets, explicit target lists, and hosted sandbox limits concrete;
- and the October 2025 docs.rs default-target change proved that a project’s *public docs surface* can drift even when its own local support policy was left implicit.

That combination sharpens the missing crate.
It is not most missing as another matrix visualizer.
It is missing as a **portable support contract** for:

1. **imported upstream authority**,
2. **project-local support class**,
3. **public docs surface**,
4. **portable bundle shape**, and
5. **manual-review honesty where those disagree**.

## The sharper gap

What still looks missing is a crate that gives other people:

1. one **upstream-support-authority import receipt** saying which facts came from Rust-project policy, rustup, docs.rs, or Cargo docs and what those facts do *not* prove;
2. one **public-docs-surface receipt** saying what docs.rs is actually exposing and whether defaults were implicit;
3. one **portable toolchain-support bundle** keeping authority, local policy, docs posture, prerequisites, route, topology, and readiness receipts together;
4. one **support-posture verdict** that does not over-read those narrower artifacts; and
5. one **manual-review zone** whenever “officially available”, “publicly documented”, and “project-supported” diverge.

## Guardrail

Do not add another nearby lane unless it clearly escapes **P-0484**, **P-0472**, **P-0036**, **P-0490**, and linker-lane diagnosis work.

Especially resist:

- another target-matrix dashboard,
- another docs.rs wrapper that cannot separate public docs surface from real support class,
- another installer/bootstrap helper that cannot export reviewable receipts,
- or another cross-target doctor that confuses upstream availability with project support.

