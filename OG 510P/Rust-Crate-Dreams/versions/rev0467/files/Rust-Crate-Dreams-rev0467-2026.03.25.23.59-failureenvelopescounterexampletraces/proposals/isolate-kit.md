---
id: P-0031
title: isolate-kit — cross-platform process sandboxing primitives (Landlock/seccomp/AppContainer/etc.)
status: idea
domains: [security, sandboxing, os, tooling, plugins, enterprise]
last_reviewed: 2026-03-01
evidence:
  - https://docs.rs/landlock
  - https://crates.io/crates/extrasafe
  - https://github.com/ossf/wg-best-practices-os-developers/issues/631
  - https://github.com/wilsonzlin/fastrender/blob/main/docs/windows_sandbox.md
  - https://crates.io/crates/nanosandbox
---

# Problem

Many Rust applications need to safely handle **untrusted inputs** (documents, images, configs, plugins, templates).
The ecosystem has strong *building blocks* (Landlock, seccomp wrappers, Windows sandbox patterns), but teams still often:
- hand-roll sandboxing per project,
- ship Linux-only solutions, or
- avoid sandboxing entirely because it’s hard to do well.

We need a small, reusable, well-tested crate that makes “reasonable sandboxing” accessible and consistent.

# Users & user stories

- **App developers:** “Run a risky parser in a restricted environment without building a bespoke sandbox.”
- **Tool authors:** “I need a library that can restrict file and network access for a child process.”
- **Plugin systems:** “Run user-provided plugins with least privilege.”
- **Security-conscious orgs:** “Standardize sandbox profiles across services and CLIs.”

# Prior art (and why it’s insufficient)

- `landlock` provides safe Landlock syscalls (Linux-only).
- `extrasafe` provides ergonomics for seccomp (Linux-only), plus Landlock support.
- `nanosandbox` claims cross-platform sandboxing, but the ecosystem lacks a widely adopted, *standards-like* abstraction and conformance story.
- Real projects document Windows sandbox boundaries (Job objects + AppContainer + restricted tokens), but this knowledge is scattered.

# Design goals

1. **Cross-platform API**: the same builder pattern works on Linux/macOS/Windows.
2. **Policy-first**: declare what’s allowed (fs/net/process/env) — get the strongest available enforcement per OS.
3. **Explainability**: errors describe missing OS features or blocked operations.
4. **Profiles**: `strict`, `read_only_fs`, `no_network`, `ci_build`, `plugin_host`, etc.
5. **Testability**: conformance tests and fixtures that verify that policies actually bite.
6. **Low deps**: security tooling shouldn’t drag a huge graph.

# Non-goals

- Perfect VM-grade isolation.
- Implementing a full container runtime.

# Architecture & API sketch

```rust
use isolate_kit::{Sandbox, FsRule, NetRule, Profile};

let sb = Sandbox::new(Profile::Strict)
  .fs(FsRule::read_only("./inputs"))
  .fs(FsRule::read_write("./scratch"))
  .net(NetRule::deny_all())
  .env_allow(["RUST_LOG"])
  .deny_process_spawn();

let status = sb.spawn("my_parser", ["--in", "inputs/file.bin"])?.wait()?;
```

## Backend strategy

- Linux: prefer Landlock for filesystem restrictions; optional seccomp for syscalls; user namespaces where helpful.
- macOS: sandbox profiles where feasible; document limitations and OS version constraints.
- Windows: Job objects + restricted tokens + (where possible) AppContainer configuration.

Expose backends as optional features, but keep a stable top-level API.

# Security / safety model

- **Explicit guarantee language** per profile and OS (what is actually enforced).
- Default-deny: network and home directory.
- Encourage “parse in a worker process” rather than in-process sandbox fantasies.

# Maintenance & governance plan

- Treat platform support as first-class (CI matrix).
- Maintain a public “policy conformance suite”.
- Coordinate with related tools (cargo-build-jail, plugin kits) so they share a single sandbox substrate.

# Milestones

0. **0.1 (Linux)**: Landlock filesystem + network deny + basic env allowlist.
1. **0.2 (Windows)**: Job object + restricted token; ship a clear “boundary doc”.
2. **0.3 (macOS)**: best-effort sandbox profile integration.
3. **0.4**: conformance test harness + published results for sample apps.

# Open questions

- How to express policies without overfitting to any one OS?
- Should we include a “policy compiler” that lowers to the best available backend?

# Sources

- landlock crate docs: motivation and security-layer framing.
- extrasafe: seccomp ergonomics + Landlock support.
- OpenSSF sandboxing guidelines issue: ecosystem-level “how to sandbox” need.
- Real Windows sandbox docs from fastrender.
- nanosandbox: evidence that cross-platform demand exists, but standardization is still missing.
