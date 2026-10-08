---
id: P-0115
title: Build-time Sandbox Runtime API Kit
status: idea
domains: [security, build-systems, tooling, supply-chain]
last_reviewed: 2026-03-05
evidence:
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
  - https://github.com/rust-lang/cargo/issues/5720
  - https://github.com/rust-lang/compiler-team/issues/475
---

# Problem

Build scripts and proc-macros are *build-time execution*—a long-recognized security and determinism risk. The Rust project goals explicitly call out sandboxed build scripts as an ecosystem need, and Cargo has had “sandbox/jail build scripts” discussions for years. citeturn0search3turn1search3

Multiple experimental tools exist, but what’s missing is a **shared runtime API + policy model** that can:
- be adopted incrementally (per workspace, per dependency class),
- produce stable “what happened” evidence artifacts,
- and align with eventual first-class Cargo/rustc sandboxing directions (rather than fighting them). citeturn1search19

# What it provides

1. **A portable capability policy schema**
   - capabilities: fs read/write roots, env var allowlist, net off/on, process spawning, syscalls subset (platform-specific mapping)
   - per-package overrides and “default deny” profiles
   - policy lints (“this crate requests net for build.rs; explain why”)

2. **A userland sandbox runtime API**
   - `SandboxRuntime` trait with backends (Linux namespaces+seccomp, macOS sandbox, Windows job objects/appcontainers where possible)
   - fallback “audit-only” mode that records accesses without blocking

3. **Evidence artifacts**
   - `sandbox-report.json`: normalized access log + policy decisions + hashes
   - `*.buildcapsule.zip`: minimal reproducible build capsule for forensic review (ties into the archive’s broader “artifact-first” approach)

4. **Cargo UX**
   - `cargo sandbox {build,test,doctor,explain}`
   - “Doctor” checks for common footguns (e.g., build scripts writing outside target dir)

# Users & user stories

- **Security-conscious dev:** “I want to run `cargo build` on untrusted code with meaningful containment.”
- **CI maintainer:** “I want to enforce ‘no network’ at build time, with clear exceptions.”
- **Crate author:** “I want to prove my build.rs is pure/deterministic.”

# Prior art (and why it’s insufficient)

- The Rust project goal documents a direction, but a shared userland runtime+policy crate can accelerate experimentation and converge on a usable model. citeturn0search3
- Cargo issue discussions identify high-level restrictions and strategies, but there’s no standard artifact/reporting pipeline that makes adoption safe and auditable. citeturn1search3
- The compiler team MCP frames build-time execution sandboxing as a cross-team major change; userland can prototype policy ergonomics and reports now. citeturn1search19

# Design goals

- **Policy clarity:** explain *why* a capability is requested and used.
- **Evidence-first:** every run can emit a stable report; diffs are CI-friendly.
- **Composable backends:** different OS mechanisms behind a stable trait.
- **Incremental rollout:** audit-only → warn → enforce.

# Non-goals

- Perfect isolation against kernel escape; focus on raising the bar and reducing accidents.
- Replacing future built-in Cargo/rustc solutions; aim to align with them.

# Architecture & API sketch

Crates:
- `build-sandbox-policy` (schema + lints)
- `build-sandbox-runtime` (trait + backends)
- `cargo-sandboxx` (CLI integration; intentionally distinct from existing names)

API:
- `Policy::evaluate(requested, observed) -> Decision`
- `SandboxRuntime::run(cmd, policy) -> RunReport`

# Security / safety model

- Threat model is “untrusted build-time code” (build.rs/proc-macros) with host user privileges.
- Default to least privilege; provide “break-glass” overrides with mandatory justification strings in config.

# Maintenance & governance plan

- Treat the policy schema as semver-stable; add capabilities via feature gates.
- Keep OS backends in separate crates/modules to avoid destabilizing the core.

# Milestones

- **MVP:** audit-only mode + `sandbox-report.json` + Linux backend.
- **v0.5:** enforce mode + policy lints + macOS backend.
- **v1:** adoption guides; compatibility notes with Cargo’s evolving sandbox efforts.

# Open questions

- Best way to model proc-macro needs vs build.rs needs (likely separate profiles).
- How to capture “file writes that affect determinism” vs “benign writes”.

# Sources

- Rust project goal: sandboxed build scripts. citeturn0search3
- Cargo issue: sandbox/jail build scripts. citeturn1search3
- Compiler-team MCP: build-time execution sandboxing. citeturn1search19
