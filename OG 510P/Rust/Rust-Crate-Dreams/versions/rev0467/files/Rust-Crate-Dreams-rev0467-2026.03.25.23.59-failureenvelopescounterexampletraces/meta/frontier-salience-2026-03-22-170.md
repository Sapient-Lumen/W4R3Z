# Frontier salience refresh 170 — 2026-03-22

This pass re-ranks the frontier after a fresh scan of current Cargo build-script, override, and delegation signals.

## Main judgment

The strongest under-modeled gap is now **delegated build-script support truth**.
Cargo’s official substrate is now explicit about build-script outputs, `OUT_DIR`, order-sensitive directives, `links`-override behavior, external-tool JSON, metabuild, multiple build scripts, and “any build script metadata”; the 2025 GSoC work connects delegation to multiple-build-scripts, deterministic ordering, and per-unit output directories; and Cargo 1.93’s notes make artifact staging, collision checking, and concurrency constraints unusually concrete.
That means the missing value is no longer another helper around `cc` or `bindgen`. It is a reviewable contract for **unit topology**, **output lanes**, **override authority**, **bridge posture**, and **delegation drift**.

## Updated high-salience set

1. **P-0484 Toolchain & Target Support Contract Kit** — still strongest because cross-target support truth remains pervasive.
2. **P-0121 FFI Boundary & Bindings Conformance Kit** — still top-tier because interop remains a core application frontier.
3. **P-0120 Unsafe Contract Auditor Kit** — still top-tier because unsafe obligations keep getting more explicit.
4. **P-0508 Cargo Build Script Delegation Kit** — promoted because Cargo’s build substrate is now concrete enough that delegated-build reviewability can be productized.
5. **P-0447 In-Place Initialization Adoption Kit** — still high because placement/address/failure truth is now very explicit.
6. **P-0036 MSRV Workspace Lab** — still crucial because version-floor truth and dependency drift remain daily pain.
7. **P-0535 Dependency Lifecycle Transition Kit** — still high because architectural dependency placement is broader than trust scoring.
8. **P-0460 Unsafe Field Invariant Ledger Kit** — still high because field-carried invariants are newly explicit substrate.

## Guardrail

When future passes touch build-time integration, prefer deepening **P-0508**, **P-0046**, or **P-0059** before inventing another `build.rs` helper, another native-probe wrapper, or another vague “declarative build” wishlist.
