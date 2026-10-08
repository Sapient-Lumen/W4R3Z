---
id: P-0154
title: Wasm Portability & Deployment Evidence Kit (Wasmtime + Pulley)
status: idea
domains: [wasm, toolchain, runtime, devtools, portability, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://docs.wasmtime.dev/api/wasmtime/
  - https://crates.io/crates/wasmtime
  - https://docs.wasmtime.dev/examples-pulley.html
  - https://github.com/bytecodealliance/wasmtime/blob/main/docs/stability-platform-support.md
---
# Problem

Wasm is often sold as “portable”, but in practice portability depends on:

- which compiler backend is available on the host (Cranelift/Winch vs interpreter paths)
- component-model plumbing and ABI surfaces
- host capability policies (filesystem, network, clocks)
- reproducibility (exact toolchain + flags + adapters)

Wasmtime is a leading Rust-native runtime, and it now includes **Pulley**, a portable interpreter path for architectures not covered by JIT backends. Still, teams lack a **standardized way to prove and debug** “this component runs on target X with policy Y”.

# What it should provide

## 1) A portable “deployment capsule” format
A standard `wasmbundle.zip` with:

- `manifest.json` (engine version, features, component/module hash, adapter hashes)
- `artifact/` compiled wasm + component metadata
- `host_policy/` capability policy (fs/net/clock/env) + allowlist
- `run/` deterministic inputs (redactable), seeds, time model
- `outputs/` expected outputs or assertions
- `logs/` normalized engine logs/traps/backtraces
- `perf.json` (optional): instantiation time, memory, fuel, etc.

## 2) A conformance harness for “portable execution”
- Matrix runner: x86_64/aarch64 plus “fallback path” via Pulley
- Profiles: module vs component, WASI versions, async vs sync embedding
- “Golden” fixtures for common pitfalls: clocks, fd rights, preopens, UTF-8 paths, etc.

## 3) Cargo UX: `cargo wasm-deploy`
- `build` (produce bundle), `verify` (run against policy), `doctor` (diagnose portability issues)
- optional integration with OCI artifact storage (push/pull bundles)

## 4) A maintenance story that keeps pace with Wasmtime evolution
- Pin schema versions and bundle readers
- Keep fixture corpora small but meaningful; accept external “fixture packs”

# MVP → v1 roadmap

1) **MVP (0.x)**: `wasmbundle.zip` schema + `cargo wasm-deploy verify` for module execution + policy file.
2) **v0.5**: component-model support + Pulley-based portability checks + CI matrix runner.
3) **v1.0**: conformance packs for WASI/component features + stable reports + OCI distribution integration.

# Design notes

- Make portability failures *actionable*: “this uses unsupported hostcalls on target”, “this needs JIT backend”, “this policy denies DNS”.
- Keep it embedder-friendly: library-first, plugin optional.

# Why this is worthy

It turns “Wasm portability” into a **testable contract** and creates a common artifact for debugging and compliance—exactly the kind of glue the ecosystem benefits from.
