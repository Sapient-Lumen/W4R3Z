---
id: P-0181
title: RISC-V Emulation & ISA Conformance Kit
status: idea
domains: [systems, emulation, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/d0iasm/rvemu
  - https://book.rvemu.app/
  - https://github.com/riscv-software-src/riscv-tests
  - https://github.com/riscv/riscv-arch-test
---

# Problem

Rust has multiple RISC-V emulators/ISS projects and many embedded/OS projects targeting RISC-V, but there’s no shared, Rust-friendly harness for running official ISA tests, collecting comparable traces, and producing reproducible failure artifacts. This slows emulator correctness work and makes it hard to compare implementations.

rvemu demonstrates a capable Rust RISC-V emulator (RV64GC, privileged ISA, devices), but the ecosystem lacks a standardized conformance runner and artifact format for “ISA regression” across emulators and configurations.

# What it provides

- A standard **artifact**: `riscvbundle.zip`
  - target config (`isa.yaml` / `march`, privilege, MMU)
  - test selection manifest (riscv-tests / arch-test IDs)
  - run logs + exit status + signature outputs
  - optional instruction trace (compressed)
  - minimized reproducer (single test + seed)
- A crate + CLI: `cargo riscv-conformance {run,triage,diff,doctor}`
  - adapters to run tests under different backends (rvemu, spike, qemu; feature-gated)
  - normalization layer to compare outcomes (signatures, traces, traps)
  - snapshotting for CI (baseline vs PR diff)
- Curated profiles:
  - “RV64GC userland”
  - “Privileged Sv39 + devices”
  - “Minimal RV32IM”
- Fixture corpora:
  - known-good outputs for selected profiles
  - “regression seeds” from real bugs

# Users & user stories

- Emulator author: “Run arch tests nightly; when something fails, share a bundle that others can replay locally.”
- Embedded team: “Validate toolchain + emulator + firmware tests under a pinned RV32 profile.”
- Educator: “Use the harness to demonstrate ISA behavior and debugging via traces.”

# Prior art (and why it’s insufficient)

- `rvemu` provides emulator implementation and a companion book, but not a standardized conformance pipeline.
- `riscv-tests` and `riscv-arch-test` exist, but integrating them with Rust tools, artifact capture, and CI diffs is non-trivial and repeatedly re-invented.

# Design goals

- Make conformance runs **repeatable and comparable** across backends.
- Provide a small “core” with optional adapters (don’t hard-depend on qemu/spike).
- Keep artifacts small via compression + trace sampling.

# Non-goals

- Replacing the official test frameworks; instead provide Rust-native glue + artifacts.
- Full-system fuzzing (possible later via plug-ins).

# Architecture & API sketch

- `Backend` trait: `run(test, cfg) -> RunOutput`
- `Normalizer`: convert backend outputs → canonical `TestResult`
- `Bundle`: pack results + traces + config + reproduction script
- `Diff`: compare bundles across commits/backends

# Security / safety model

- Bundles may include binaries; provide a “hash-only” or “no-binary” mode.
- Default replay runs in a sandboxed temp dir; no network.

# Maintenance & governance plan

- Keep test selection small and reviewable; publish “profile governance” rules.
- CI matrix for major OSes; adapters are feature-gated and optional.

# Milestones

- MVP: backend for rvemu + riscv-tests subset + bundle schema + diff.
- v1: add arch-test integration + spike/qemu adapters, CI recipe templates.
- v2: trace compare tooling + minimization + profile registry.

# Open questions

- Best canonical trace format for cross-backend comparisons?
- How to manage evolving official tests while keeping stable baselines?

# Sources

- rvemu repository and companion book.
- riscv-tests repository.
- riscv-arch-test repository.
