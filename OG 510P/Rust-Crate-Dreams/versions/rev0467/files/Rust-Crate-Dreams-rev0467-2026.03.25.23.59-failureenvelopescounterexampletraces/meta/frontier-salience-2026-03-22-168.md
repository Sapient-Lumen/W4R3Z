# Frontier salience refresh 168 — 2026-03-22

This pass re-ranks the frontier after a fresh scan of official Rust/Cargo/Clippy sources and the current archive.

## Main judgment

The strongest under-modeled gap is now **lint-policy evidence**.
Rust’s official 2026 plan now explicitly names safety-critical lints in Clippy, Cargo has first-class manifest/workspace lint configuration plus an emerging nightly `[lints.cargo]` surface, and Clippy configuration is rich enough to materially change the meaning of a “clean” run.
That means the missing value is no longer another lint runner. It is a reviewable contract for **policy authority**, **checked scope**, **diagnostic channel**, **waiver decisions**, and **drift**.

## Updated high-salience set

1. **P-0484 Toolchain & Target Support Contract Kit** — still strongest because support truth remains a pervasive ecosystem gap.
2. **P-0121 FFI Boundary & Bindings Conformance Kit** — still top-tier because interop remains a core application-area frontier.
3. **P-0120 Unsafe Contract Auditor Kit** — still top-tier because the unsafe obligation layer keeps getting more explicit.
4. **P-0459 Clippy Safety Profile & Waiver Kit** — promoted because official Rust/Cargo/Clippy substrate now makes a lint-policy evidence layer unusually buildable and high leverage.
5. **P-0036 MSRV Workspace Lab** — still crucial because version-floor truth and dependency drift remain daily pain.
6. **P-0535 Dependency Lifecycle Transition Kit** — still high because architectural dependency placement is broader than trust scoring.
7. **P-0460 Unsafe Field Invariant Ledger Kit** — still high because field-carried invariants are newly explicit substrate.
8. **P-0455 Doctest Extraction & Support Contract Kit** — still high because docs remain canonical and executable support truth matters.

## Guardrail

When future passes touch lint-heavy work, prefer deepening **P-0459** or **P-0473** before inventing another static-analysis dashboard, another waiver spreadsheet, or another “strict mode” wrapper.
