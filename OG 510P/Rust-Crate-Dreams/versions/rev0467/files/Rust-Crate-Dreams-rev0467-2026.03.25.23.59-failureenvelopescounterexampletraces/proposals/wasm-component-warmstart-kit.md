---
id: P-0103
title: Wasm Component Warmstart Kit — pre-initialize modules/components safely with build-time snapshots and conformance fixtures
status: idea
domains: [wasm, performance, component-model, tooling, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/wizer
  - https://github.com/dicej/component-init
  - https://bytecodealliance.org/projects
  - https://docs.wasmtime.dev/api/wasmtime/component/struct.Component.html
needs:
  - wasm workloads often pay heavy startup/init costs; warmstart techniques exist but are ad-hoc
  - module warmstart (Wizer) and component warmstart (component-init) are **not packaged as a standard workflow**
  - teams need reproducibility, determinism, and security guidance (what is safe to snapshot?)
---

# Problem

Many Wasm applications load data, build tables, compile regexes, or initialize interpreters on first request.
Warmstarting (build-time pre-initialization with state snapshotting) can eliminate that cost, but today it is:
- project-specific scripting
- difficult to reason about determinism
- hard to validate across runtimes and platforms

# What it provides

## 1) A standard warmstart artifact format
- `module.wasm` or `component.wasm`
- `warmstart.json` (what ran, runtime versions, exported init ABI, determinism settings)
- `snapshot.wasm` (pre-initialized output)
- `fixtures/` (inputs used during init: databases, tables)
- `conformance/` (expected exports, memory/table sizes, checksum)

Name: `*.warmstart.zip`

## 2) A cargo / CI friendly UX
- `cargo wasm-warmstart build`
  - supports module (`wizer`) and component model (`component-init`) flows
  - declarative config: init function, allowed imports, fixture paths
- `cargo wasm-warmstart verify`
  - re-runs init in a sandboxed runtime and checks snapshot determinism (hashes, exported globals, memory sizes)
- `cargo wasm-warmstart doctor`
  - checks “unsafe snapshot” patterns (e.g., time, randomness, host IO) and suggests mitigations

## 3) A small Rust API for embedding in platforms
- `warmstart::Builder` (produces snapshot with selected backend)
- `warmstart::Verifier` (determinism + policy checks)
- `warmstart::Backend` trait (Wasmtime/Wizer/component-init)

# Users & user stories

- **Edge runtime teams**: “We want fast cold starts without writing bespoke build scripts.”
- **Library authors**: “We ship a Wasm plugin; users want instant startup.”
- **Platform operators**: “We need determinism and a policy story before we accept snapshots from others.”

# Prior art (and why it’s insufficient)

- Wizer demonstrates module pre-initialization and is used in real deployments to reduce startup time, but teams still need repeatable packaging and verification.
- `component-init` extends the idea to the WebAssembly Component Model, but again lacks standard artifacts and cargo UX.
- Bytecode Alliance tooling exists (wit-bindgen, wit-deps, etc.), but warmstart is not “end-to-end packaged”.

# Design goals

- **Determinism**: snapshot should be reproducible given the same inputs and toolchain.
- **Security**: clear policy for imports and hostcalls allowed during init.
- **Interop**: outputs should work across Wasmtime versions (within reason) and ideally other runtimes.
- **Auditability**: artifacts must explain what ran and with what inputs.

# Non-goals

- Making nondeterministic init “magically safe”. Provide tooling and patterns, not miracles.
- Replacing runtime-level compilation caching (complements it).

# Architecture & API sketch

Backends:
- Module backend: `wizer` / `wasmtime-wizer`
- Component backend: `component-init` + Wasmtime component support

Verification:
- Re-run init with the same fixtures; compare produced snapshot hash.
- Optional “semantic” checks (exports count, memory size, WIT signature).

# Security / safety model

- Default deny: disallow filesystem/network imports during init unless explicitly allowed.
- Encourage “pure init”: load fixtures from embedded resources, avoid time/random.
- Provide “policy profiles”: `strict`, `balanced`, `unsafe-dev`.

# Maintenance & governance plan

- Version artifact schema; treat it like a contract.
- Keep a public conformance corpus (tiny fixtures) so regressions are caught early.

# Milestones

1) MVP
   - module warmstart flow + artifact format
   - verify determinism + basic doctor checks
2) v1
   - component warmstart via `component-init`
   - conformance fixtures + CI template
3) vNext
   - multi-runtime support if feasible; richer policy language

# Open questions

- How stable are snapshots across runtime versions? (document and test it)
- Best abstraction for “component init ABI” and WIT integration?

# Sources

- Wizer crate: https://crates.io/crates/wizer
- Component pre-initializer (`component-init`): https://github.com/dicej/component-init
- Bytecode Alliance projects list (tool ecosystem context): https://bytecodealliance.org/projects
- Wasmtime Component API docs: https://docs.wasmtime.dev/api/wasmtime/component/struct.Component.html
