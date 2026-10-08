# Cargo Sandbox & Capability Policy frontier — 2026-03-22

## Why this lane is sharper now

The old story was “sandboxing build scripts and proc macros would be nice”.
The current story is much more concrete:

- Rust has an accepted project goal for sandboxed build scripts.
- The compiler-team MCP describes a future with declared build-time powers, a minimal API, and Cargo/rustc configuration.
- Cargo’s documented environment/config behavior still makes actor scope easy to misunderstand.
- `--compile-time-deps` proves that compile-time actors are already a meaningful standalone workflow.
- current practical tools (`cackle`, `cargo-sandbox`) demonstrate real adoption value while also exposing granularity and platform limits.

So the missing crate is no longer a hypothetical runtime experiment.
It is the **support contract above current and future runners**.

## The sharpest missing artifact layer

The archive should treat this lane as primarily about five review objects:

1. **policy authority** — where the effective policy came from,
2. **actor capability scope** — who got which powers,
3. **enforcement mode** — observe vs audit vs enforce,
4. **exception ownership** — break-glass grants and their owners,
5. **policy drift** — what changed materially.

## Why adjacent lanes are not enough

- Runtime crate-authority lanes describe a library’s ambient authority at runtime, not build-time execution policy.
- Delegated-build lanes describe unit topology and output ownership, not capability grants.
- Proc-macro migration lanes describe future Wasm-readiness and compatibility, not current policy truth.
- OS sandbox crates describe mechanisms, not a Cargo-facing review bundle.

## Desired outcome

A team should be able to hand another team one bundle and let them answer:

- which compile-time actors are trusted with filesystem/network/process/env access,
- which backend and mode actually enforced those choices,
- what exceptions exist,
- and whether the policy story broadened since the last release.
