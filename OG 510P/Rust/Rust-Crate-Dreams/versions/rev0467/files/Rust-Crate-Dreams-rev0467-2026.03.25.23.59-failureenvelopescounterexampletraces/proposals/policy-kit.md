---
id: P-0052
title: policy-kit — safe, testable embedded policy engines (CEL + OPA/Rego Wasm adapters)
status: idea
domains: [policy, security, runtime, tooling]
last_reviewed: 2026-03-01
evidence:
  - https://crates.io/crates/cel
  - https://openpolicyagent.org/docs/wasm
  - https://openpolicyagent.org/docs/integration
---

# Problem
Rust applications increasingly need **embedded policy** (authorization, admission control, routing rules, feature gating). The ecosystem has engines (CEL; OPA/Rego via Wasm), but teams still rebuild the same glue:
- typed context binding
- evaluation limits (time/step/budget)
- explain traces
- policy test bundles for CI

# Users & user stories
- Platform team: “We want one policy layer across services; policies must be testable and safe.”
- OSS maintainer: “I need an embedded rule language that won’t become a security liability.”
- App dev: “I want a stable Decision API that can swap CEL ↔︎ OPA Wasm.”

# Prior art (and why it’s insufficient)
- CEL crates provide evaluation, but not a full “safe embedding kit.”
- OPA can compile Rego to Wasm, but host integration patterns and limits are left to users.

# Design goals
- A core `PolicyEngine` trait + a stable `Decision` + explain trace model.
- Standard policy test bundle format and runner.
- Adapters: `policy-cel`, `policy-opa-wasm` (and optional others).

# Non-goals
- Writing a new policy language.
- Running a full OPA server inside your process.

# Architecture & API sketch
- `policy-kit-core`:
  - `Engine::evaluate(policy, input, data) -> Decision`
  - Limits: `max_time`, `max_memory`, `max_output_bytes`, `max_steps` (where supported)
  - `Decision { outcome, reasons[], trace? }`
- `policy-kit-test`:
  - `policy test` runs bundles: policy + inputs + expected outcomes + golden traces.
- Adapters:
  - CEL adapter wraps `cel` crate.
  - OPA Wasm adapter runs a Wasm module in Wasmtime (or pluggable runtime), using OPA Wasm calling conventions.

# Security / safety model
- Sandbox execution where possible (Wasm).
- Hard limits are first-class config; safe defaults.
- Input validation + no implicit network access.

# Maintenance & governance plan
- Keep core small; adapters in separate crates.
- “Policy test bundles” become the stable interface even if engines change.

# Milestones
- 0.1: core + CEL adapter + test bundle runner.
- 0.2: OPA Wasm adapter + explain traces.
- 0.3: policy registry conventions + tooling to package policies.

# Open questions
- Standard trace vocabulary across engines.
- How to represent partial evaluation / unknowns.

# Sources
See front matter links.
