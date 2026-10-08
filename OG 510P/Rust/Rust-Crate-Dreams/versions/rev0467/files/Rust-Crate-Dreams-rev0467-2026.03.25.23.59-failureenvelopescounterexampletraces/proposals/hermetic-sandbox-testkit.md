---
id: P-0240
title: Hermetic Sandbox TestKit — reproducible, policy-driven Linux sandboxes for tests/CI with explainable syscall budgets
status: idea
domains: [security, sandboxing, testing, supply-chain]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/sandbox-rs
  - https://crates.io/crates/seccompiler
  - https://crates.io/crates/seccomp
  - https://crates.io/crates/syd
---

## What it should provide others

A **developer-friendly, CI-grade sandbox runner** for Linux that makes “run untrusted code with guardrails” a default workflow, producing auditable artifacts.

The crate should provide:

- **Hermetic execution wrapper** for tests, build steps, and fuzzers.
- **Policy language** (high-level) that compiles to kernel mechanisms:
  - seccomp filters
  - namespaces (user/mount/net)
  - Landlock where available
- **Explain mode**: “why was this syscall/file/network denied?” + suggested minimal allow rule.
- **Budgeting**: time, memory, file size, process count, network egress rules.
- **Evidence bundles**: `*.sandboxbundle.zip` with policy, denials, syscall summaries, and repro instructions.

## Why this is still missing

The ecosystem has *pieces* but not a cohesive “kit” with a great UX:

- `seccomp` and `seccompiler` provide building blocks for syscall filtering.
- `sandbox-rs` and `syd` show growing appetite for higher-level sandboxing.

What’s missing is the **integration layer**: policy → compilation → explainability → evidence artifacts → easy CI wiring.

## Design outline

### 1) Library core + CLI

- `sandboxkit-core`: policy IR, compiler to backends, evidence emitter.
- `sandboxkit-cli`: `sandboxkit run --policy policy.toml -- <cmd>`.

### 2) Backend architecture

Backends should be modular:

- `backend_seccomp` (seccompiler-first)
- `backend_namespaces`
- `backend_landlock` (feature-gated)

### 3) Policy model

A policy is declarative and diffable:

- filesystem allowlist (read/write/exec)
- network (off by default; allowlist by CIDR/port)
- syscalls (profiles: rust-test, cargo-build, clang-build, node-build, etc.)
- resource budgets

### 4) Explain mode

- capture denial events
- map to policy clauses
- emit suggestions: “add read access to /etc/resolv.conf” or “allow `clock_gettime`”

## Minimum lovable MVP (4–8 weeks)

1. CLI runner with seccomp + namespaces (no Landlock initially).
2. 2–3 preset policies: `rust-tests`, `cargo-build`, `proc-macro-build`.
3. Evidence bundle output.
4. “learning mode”: run permissive, record syscalls/files, propose minimal policy.

## De-risk plan

- Start with “test runner” use-case (single process tree, predictable needs).
- Keep policy stable; treat backends as replaceable.

## Scorecard (0–5)

- Impact: 5
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (explain + learning mode + evidence bundles)
