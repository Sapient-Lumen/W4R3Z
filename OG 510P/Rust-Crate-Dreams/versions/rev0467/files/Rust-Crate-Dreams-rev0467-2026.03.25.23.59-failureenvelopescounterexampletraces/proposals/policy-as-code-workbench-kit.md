---
id: P-0116
title: Policy-as-Code Workbench Kit (Rego in-process)
status: idea
domains: [security, authorization, policy, tooling, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/microsoft/regorus
  - https://crates.io/crates/regorus
  - https://openpolicyagent.org/ecosystem
  - https://github.com/open-policy-agent/awesome-opa
---

# Problem

Rust teams increasingly want **policy-as-code** (authorization, admission control, data access constraints, compliance rules) *inside* services, CLIs, and edge agents.

The missing piece is not just “a Rego interpreter exists” (it does), but a **workbench** that makes policies:
- testable (fast, hermetic, CI-friendly),
- explainable (why allow/deny?),
- debuggable (where did evaluation go wrong?),
- portable (a stable policy bundle format),
- safe (guardrails on built-ins, timeouts, memory, and `no_std` targets).

Today, the ecosystem has powerful building blocks (notably **Regorus**), but most teams still end up with bespoke scripts and one-off glue for testing, coverage, and “explain” UX.

# What it should provide other people

A cargo-native toolkit that turns Rego policy into a **first-class Rust artifact**, with stable, shareable outputs:

## 1) Standard policy bundle format

A `policybundle/` directory spec + `policybundle.zip` packaging:
- policy modules (`.rego`) + optional data documents (`data.json` / CBOR),
- an explicit **built-in allowlist** (and version),
- evaluation constraints (max steps / timeouts / recursion guards),
- version pinning against Rego language mode (e.g. “OPA v1 semantics”).

## 2) `cargo policy` workflows

- `cargo policy test` — run policy tests with deterministic fixtures
- `cargo policy explain <query>` — produce human/audit-friendly explanations
- `cargo policy coverage` — report “rule coverage” across a test suite
- `cargo policy fmt/lint` — opinionated formatting + lints (footguns, shadowed vars)
- `cargo policy doctor` — validate bundle integrity, pinned semantics, and risky builtins

All commands emit stable machine artifacts:
- `policy-report.json` (summary, versions, constraints, perf counters)
- `policy-explain.json` (trace tree, decisions, redaction-safe)
- `policy-coverage.json` (rule hit counts, dead rules, untested branches)

## 3) “Explain” UX that humans will actually use

A structured trace tree with:
- minimal diffs (what changed from allow → deny),
- rule-by-rule justifications,
- redaction policies (PII scrubber hooks),
- linkable spans (source location in `.rego` + rule ID).

## 4) Safety profiles

Profiles like:
- `edge-no-alloc` (no_std, low memory)
- `server-audit` (full traces, strict timeouts)
- `admission-control` (deterministic, no network/system calls, constrained builtins)

# MVP (4–6 weeks)

1. Bundle spec + `policybundle.zip` pack/unpack.
2. Adapter over **Regorus** for evaluation with explicit constraints.
3. `cargo policy test` with a minimal test DSL:
   - `input.json` + expected decision + optional assertions on “explain” fields.
4. Emit `policy-report.json` + `policy-explain.json`.
5. Seed fixture corpus:
   - ABAC/RBAC examples,
   - deny-by-default patterns,
   - common pitfalls (undefined vars, partial evaluation surprises).

# v1 (8–16 weeks)

- Coverage reporting + dead-rule detection.
- Deterministic “explain diff” (compare two bundle versions).
- Policy “ABI” checking: warn when rule interfaces change (expected inputs/outputs).
- Optional integration points:
  - `axum` extractor middleware,
  - `kube` admission webhook helper,
  - `tonic` interceptor helper.

# Conformance & testing

- “Golden” explain traces for canonical policies.
- Differential tests:
  - compare Regorus vs an external OPA binary (optional) for known cases.
- Fuzz policy bundle parsing + trace serialization.

# Non-goals

- Replacing OPA as a server.
- Supporting every OPA builtin on day one; start with an allowlisted subset.

# Notes & ecosystem fit

OPA’s ecosystem explicitly emphasizes policy testing and debugging workflows; this kit focuses on delivering those ergonomics *in-process* for Rust, while leveraging modern Rust-native interpreters such as Regorus.  

