# Frontier salience refresh 171 — 2026-03-22

This pass re-ranks the frontier after a fresh scan of current compile-time sandboxing, build-script policy, and proc-macro isolation signals.

## Main judgment

The strongest under-modeled gap is now **compile-time sandbox policy truth**.
The upstream Rust direction is explicit enough to make this buildable: the sandboxed-build-scripts goal ties file/network restrictions to determinism and caching, the accepted compiler-team MCP describes declared build-time powers and Cargo/rustc configuration, Cargo’s docs still expose a large build-time env/config surface, `--compile-time-deps` proves that compile-time actors form a meaningful workflow lane, and current practical tools already expose real-but-imperfect sandbox behavior.
That means the missing value is not another sandbox runtime. It is a reviewable contract for **policy authority**, **actor capability scope**, **enforcement mode**, **exception ownership**, and **policy drift**.

## Updated high-salience set

1. **P-0484 Toolchain & Target Support Contract Kit** — still strongest because support truth multiplies everywhere else.
2. **P-0121 FFI Boundary & Bindings Conformance Kit** — still top-tier because interop remains a core adoption frontier.
3. **P-0120 Unsafe Contract Auditor Kit** — still top-tier because obligation authority and witness limits remain broadly useful.
4. **P-0107 Cargo Sandbox & Capability Policy Kit** — promoted because upstream compile-time sandboxing is concrete enough that receiver-facing policy artifacts can now be productized.
5. **P-0508 Cargo Build Script Delegation Kit** — still high because delegated build topology remains a separate review layer.
6. **P-0036 MSRV Workspace Lab** — still crucial because version-floor truth keeps colliding with dependency reality.
7. **P-0535 Dependency Lifecycle Transition Kit** — still high because architectural dependency placement is broader than trust scoring.
8. **P-0460 Unsafe Field Invariant Ledger Kit** — still high because field-carried invariants are newly explicit substrate.

## Guardrail

When future passes touch compile-time trust and containment, prefer deepening **P-0107**, **P-0508**, **P-0040**, or host/target scope lanes before inventing another generic sandbox runtime, another static allowlist scanner, or another vague “secure Cargo builds” wrapper.
