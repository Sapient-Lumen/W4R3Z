---
id: P-0096
title: Capability Sandbox Policy Kit — portable capability DSL + audit feedback + “policy doctor”
status: idea
domains: [security, sandboxing, devtools, linux, supply-chain]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/landlock
  - https://landlock.io/rust-landlock/landlock/
  - https://github.com/ossf/wg-best-practices-os-developers/issues/631
  - https://www.openwall.com/lists/oss-security/2025/05/19/2
---
# Problem
We have powerful sandboxing primitives, but it’s hard to:
- author **least-privilege** policies without deep platform knowledge
- debug why a policy blocks something (and iterate safely)
- keep policies current as apps evolve

Landlock enables unprivileged sandboxing on Linux, but policy authoring and diagnostics remain specialist work.

# What it provides
A policy-centered developer experience for sandboxing:

## Portable policy model
- simple capability DSL (filesystem, network, exec, IPC, time, randomness)
- compilation targets:
  - Linux: Landlock (+ optional seccomp layer)
  - macOS / Windows: best-effort mappers with explicit “unsupported” diagnostics
- presets: `read_only_parser`, `net_client`, `wasm_runner`, `git_like_tool`

## Policy doctor (critical UX)
- “audit mode”: collect denials, propose minimal edits
- parse kernel audit / Landlock events where available
- outputs `policy-diff.md` + updated policy draft

## Embedding & launching
- library API: `Sandbox::new(policy).run(cmd)`
- in-process mode where supported (e.g., Landlock restricting ambient rights)

## Reproducible policy tests
- `cargo sandbox test`: allow/deny assertions + conformance vectors
- `*.sandboxfail.zip` bundles: policy, denials, repro commands

# MVP
Linux-first:
- DSL → Landlock rules
- audit mode + suggested edits
- small fixture suite + cookbook recipes

# v1 roadmap
- optional seccomp layer on Linux (feature-gated)
- cross-platform mappers + “portable core + platform extensions”
- CI gate: “no new denials” regression tests

# Risks
- portability is intrinsically lossy; diagnostics must be explicit about enforcement guarantees.
