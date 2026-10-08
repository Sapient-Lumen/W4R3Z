# Frontier salience scan — 2026-03-16 (MSRV + workspace-boundary refresh)

This pass again avoided spraying more unrelated proposal count.
The stronger move was:

- to upgrade **P-0036 MSRV Workspace Lab** from a vague inference tool into a lane-honest policy / blame / adoption-planning crate,
- and to add **P-0506 Cargo Workspace Boundary Doctor Kit** as a missing diagnosis layer for real Cargo discovery/config surprises.

## Main judgment

The Rust ecosystem still appears to benefit most from crates that hand **other maintainers** a small, reviewable artifact instead of another ambitious substrate rewrite.
This pass sharpens that claim in two broad areas lots of users actually feel:

1. **supporting older toolchains honestly**, and
2. **explaining why Cargo discovered the wrong project or config**.

Three current signals matter most:

1. the Rust safety-critical post explicitly says the dependency-drift problem is real and calls for ecosystem-wide MSRV conventions,
2. Cargo’s docs and issues now make `resolver.incompatible-rust-versions` a real policy seam rather than an obscure implementation detail,
3. Cargo’s 1.94 development-cycle notes call out workspace/config discovery as an active design topic, including home-directory surprises, parent poisoning, and possible opt-out shapes.

Together, those make **MSRV receipts** and **workspace-boundary diagnosis bundles** look more urgent than another isolated feature crate.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0036 MSRV Workspace Lab**
3. **P-0506 Cargo Workspace Boundary Doctor Kit**
4. **P-0489 Cargo Build-Dir Consumer Transition Kit**
5. **P-0486 Debuggability Support Contract Kit**
6. **P-0242 Reproducible Build Evidence Kit**
7. **P-0256 Evidence Bundle Core Kit**
8. **P-0469 Cargo Rebuild Explanation Kit**
9. **P-0436 Target-Dir Lease & Shared Cache Coordination Kit**
10. **P-0505 Cargo Host/Target Scope Contract Kit**
11. **P-0458 Async Dyn Transition Kit**
12. **P-0465 BorrowSanitizer Workflow & Evidence Kit**

## Why P-0036 rose

MSRV is no longer well-described as “find the oldest compiler that still builds”.
The sharper value is a crate that keeps **declared support**, **resolver policy**, **active target/feature build floor**, and **metadata/tooling floor** separate, then tells another maintainer exactly which edge raised the result.

That is especially timely now that:

- the Rust project is publicly calling out the dependency-drift / convention problem,
- Cargo has a visible rust-version policy knob,
- and fresh issue reports show `build` versus `metadata` mismatches can still happen in realistic setups.

## Why P-0506 enters high

Cargo boundary confusion is one of those problems that hurts beginners, tool authors, and advanced CI users at the same time.
It is also unusually under-served: lots of docs and issue threads exist, but almost no portable artifact explains one concrete surprise cleanly.

The proposal looks worthy because it does **not** try to replace Cargo.
It just freezes one incident into:

- invocation context,
- parent probe trace,
- membership classification,
- config influence report,
- and the shortest honest advice.

## Working rule for the next few passes

Prefer work that adds:

- lane-boundary notes,
- fixture packs tied to named upstream failure modes,
- portable review bundles,
- and conservative advice vocabularies.

The archive is now dense enough that **handoff quality** is frequently worth more than raw proposal count.

## Sources

- Rust safety-critical post: https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- Cargo configuration docs: https://doc.rust-lang.org/cargo/reference/config.html
- Cargo workspace docs: https://doc.rust-lang.org/cargo/reference/workspaces.html
- Cargo issue #16597: https://github.com/rust-lang/cargo/issues/16597
- Cargo 1.94 development cycle: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- 2025 State of Rust survey: https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
