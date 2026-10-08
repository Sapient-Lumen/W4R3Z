# Frontier salience refresh 169 — 2026-03-22

This pass re-ranks the frontier after a fresh scan of official Rust language/planning material and the current in-place-initialization substrate.

## Main judgment

The strongest under-modeled gap is now **in-place initialization adoption evidence**.
Rust’s official planning now explicitly ties together field projections, reborrowing, and design alignment on in-place initialization; the in-place-initialization goal names large heap values, C++ interop, pinned C out-pointers, async trait-object returns, and self-referential types; and current crates like `pin-init`, `moveit`, and Crubit `Ctor` prove the individual execution lanes already exist.
That means the missing value is no longer another macro or another abstract proposal recap. It is a reviewable contract for **placement topology**, **constructor lane**, **address commit**, **failure cleanup**, and **transition drift**.

## Updated high-salience set

1. **P-0484 Toolchain & Target Support Contract Kit** — still strongest because support truth remains a pervasive ecosystem gap.
2. **P-0121 FFI Boundary & Bindings Conformance Kit** — still top-tier because interop remains a core application-area frontier.
3. **P-0120 Unsafe Contract Auditor Kit** — still top-tier because unsafe obligations keep getting more explicit.
4. **P-0447 In-Place Initialization Adoption Kit** — promoted because official Rust planning and real substrate now make a placement/address/failure review layer unusually concrete and high leverage.
5. **P-0036 MSRV Workspace Lab** — still crucial because version-floor truth and dependency drift remain daily pain.
6. **P-0535 Dependency Lifecycle Transition Kit** — still high because architectural dependency placement is broader than trust scoring.
7. **P-0460 Unsafe Field Invariant Ledger Kit** — still high because field-carried invariants are newly explicit substrate.
8. **P-0459 Clippy Safety Profile & Waiver Kit** — still high because safety/lint policy evidence is now operationally real.

## Guardrail

When future passes touch pinned construction, prefer deepening **P-0447** or **P-0440** before inventing another macro wrapper, another pinning cookbook, or another language-proposal summary.
