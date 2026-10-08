---
id: P-0030
title: cargo-build-jail — sandbox build scripts & builds (secure + more deterministic)
status: idea
domains: [cargo, security, supply-chain, determinism, tooling, enterprise]
last_reviewed: 2026-03-01
evidence:
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
  - https://github.com/madsmtm/cargo-sandbox
  - https://internals.rust-lang.org/t/sandbox-build-rs-and-proc-macros/16345
  - https://internals.rust-lang.org/t/pre-rfc-sandboxed-deterministic-reproducible-efficient-wasm-compilation-of-proc-macros/19359
---

# Problem

Rust builds can execute **arbitrary code** via `build.rs` and procedural macros.
This creates:
- supply-chain risk (malicious or compromised build-time code can read secrets, phone home, or tamper artifacts),
- non-determinism (network/time/env leaks), and
- practical friction for “untrusted build” contexts (CI, code review workflows, vendor drops, air-gapped builds).

Rust Project Goals already recognize this and describe an opt-in approach to sandbox build scripts, but most teams need a usable tool *today*.

# Users & user stories

- **Enterprise / regulated teams:** “Run `cargo build` in CI without exposing secrets or unrestricted network/filesystem.”
- **Maintainers & reviewers:** “Audit or build an untrusted PR without fearing build-time RCE.”
- **Air-gapped environments:** “Ensure build scripts don’t unexpectedly depend on the network; make failures explainable.”
- **Tool authors:** “Get a stable ‘sandbox build’ primitive to embed in other workflows.”

# Prior art (and why it’s insufficient)

- `cargo-sandbox` aims at “fearlessly running Cargo builds” but is incomplete on Linux/Windows and not yet a standard workflow.
- Bubblewrap-style wrappers (scripts) exist, but aren’t cross-platform, aren’t Cargo-native, and often lack explainable policy failures.
- Proc-macro sandboxing via Wasm is being explored upstream; we still need a practical bridge strategy (OS sandboxing, optional Wasm runners where feasible).

# Design goals

1. **One command**: `cargo build-jail build/test/check/doc ...`
2. **Profiles**: strict default for CI + local “developer-friendly” mode.
3. **Explainability**: when sandbox blocks an action, users get a clear reason and remediation path.
4. **Determinism mode**: time/env/net constraints to improve caching and reproducibility.
5. **Cross-platform**: Linux/macOS/Windows with best-effort feature detection and graceful degradation.
6. **Composable**: usable as a library (via `isolate-kit`) and integrates with policy systems (`cargo-policy`, `cargo-vet`, future TUF).

# Non-goals

- Replacing Cargo or rustc.
- Perfect isolation in all environments (goal is “meaningfully safer by default”, with clear guarantees per platform/profile).

# Architecture & API sketch

## Core idea

Wrap Cargo by:
- launching cargo/rustc in a constrained environment (process sandbox), and
- enforcing a **capabilities policy** for build-time execution (build scripts + proc macro compile/load side effects).

Implementation is split:

- **`isolate-kit`** (library): OS sandboxing primitives (see P-0031).
- **`cargo-build-jail`** (binary): policy, UX, config, integration.

## Policy model (conceptual)

A policy is a set of allowances:
- filesystem: read/write allowlists (project dir read; target dir write; no `$HOME` by default)
- network: none by default (opt-in domains/ports)
- environment: allowlist of env vars; redact secrets
- processes: allow/deny spawning
- clock/randomness: deterministic mode controls

Config locations:
- `Cargo.toml` (workspace policy)
- `.cargo/build-jail.toml`
- CI presets (GitHub Actions templates)

# Security / safety model

- **Threat model (MVP):** mitigate accidental or opportunistic build-time data exfiltration and reduce blast radius.
- **Explicit limits:** declare what the sandbox does and does not protect against on each OS.
- Default deny for: `$HOME`, SSH keys, network, arbitrary process spawn.

# Maintenance & governance plan

- Start as an **incubator** crate with strict dependency policy.
- Clearly document platform support matrix and security boundaries.
- Encourage integration rather than fragmentation: provide adapter hooks for other tools.

# Milestones

0. **Spike:** Linux “bwrap/landlock/seccomp” sandbox wrapper working on a demo workspace.
1. **0.1:** `cargo build-jail build` with filesystem + network deny + clear error messages.
2. **0.2:** Windows support (Job objects + restricted token/AppContainer-style boundary) and macOS.
3. **0.3:** Determinism mode (time/env/net controls) + artifact report.
4. **1.0:** Stable policy schema + compatibility with `cargo-capabilities` (P-0033).

# Open questions

- Best interface for proc-macro isolation before Wasm-based solutions mature?
- How to provide “escape hatches” without turning them into silent footguns?
- What should the policy language look like to keep it small but expressive?

# Sources

- Rust Project Goal: Explore sandboxed build scripts (motivation + opt-in framing).
- cargo-sandbox (existing attempt; shows feasibility + gaps).
- Sandbox build.rs and proc macros (community discussion).
- Pre-RFC: Wasm sandboxing for proc macros (upstream direction).
