---
id: P-0220
title: RISC-V Architectural Tests Conformance & Evidence Kit — run ACT/arch-test suites, normalize results, and ship repro bundles
status: idea
domains: [embedded, risc-v, conformance, tooling, ci, hardware]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/riscv/riscv-arch-test
  - https://riscof.readthedocs.io/en/latest/intro.html
  - https://riscv.atlassian.net/wiki/spaces/TAXX/pages/576847877/Architectural%2BCompatibility%2BTest
needs:
  - A Rust-first library + CLI to run RISC-V architectural tests (ACT/arch-test) across simulators/emulators/targets and produce deterministic, shareable reports.
  - Canonical result normalization so CI can diff outcomes across toolchains, commits, and target configurations.
  - A single “evidence bundle” format to attach failures to issues and vendor support tickets.
risks:
  - The test ecosystem mixes repos/tools (arch-test, riscof, simulators). The kit must be adapter-based and not hardcode one runner.
  - Hardware targets add non-determinism (timing, traps). Must focus on *architectural* pass/fail and metadata, not performance.
---

## Problem

RISC-V maintains an architectural test suite designed to certify faithful implementation of the RISC-V specification (ACT/arch-test).
Source: https://github.com/riscv/riscv-arch-test

The RISCOF framework exists to run architectural tests against a target configuration.
Source: https://riscof.readthedocs.io/en/latest/intro.html

RISC-V’s own guidance emphasizes that passing architectural tests is a minimal filter and part of compatibility/trademark prerequisites.
Source: https://riscv.atlassian.net/wiki/spaces/TAXX/pages/576847877/Architectural%2BCompatibility%2BTest

In practice, teams building firmware, OS ports, or silicon validation tooling need:
- a stable way to run suites across QEMU/Spike/renode/hardware,
- normalized results for CI,
- and portable artifacts for triage.

Rust is a good fit for such tooling (reliable CLI, structured output, cross-platform), but there isn’t a widely adopted, ergonomic Rust crate that standardizes the “run → normalize → diff → bundle” workflow.

## What this crate should provide

### 1) Adapter-based runners
- `Runner` trait:
  - `prepare(target, suite, config)`
  - `run(test_case)`
  - `collect()`
- Built-in adapters (MVP picks 1–2):
  - `riscof` adapter (invoke riscof, parse outputs)
  - `spike`/`qemu` “raw” adapter for a minimal pipeline

### 2) Canonical result model
- `TestOutcome { pass|fail|skip, reason, trap_code?, signature_hash?, stdout_hash? }`
- Stable IDs for tests, pinned suite commit hashes.
- Normalization rules:
  - path redaction
  - stable ordering
  - consistent environment capture (toolchain versions, ISA strings)

### 3) Diff engine
- Compare two runs:
  - regressions (pass→fail)
  - improvements (fail→pass)
  - flaky flags (inconsistent outcomes)
- “Explain” hints:
  - likely ISA/profile mismatch
  - likely toolchain mismatch

### 4) Evidence bundles: `*.riscvtestbundle.zip`
Bundle structure:
- `suite.json` (suite repo/commit, profile/ISA)
- `target.json` (runner adapter, emulator/hardware descriptors)
- `env.json` (compiler/binutils versions, host OS, seeds)
- `results/results.json` (canonical outcomes)
- `logs/` (optional compressed logs)
- `diff/` (if produced)
- `repro/` (minimal command line and config snapshot)

### 5) UX
- `cargo riscv-test run --profile rv64gc --runner riscof --target qemu`
- `cargo riscv-test diff a.riscvtestbundle.zip b.riscvtestbundle.zip`
- `cargo riscv-test triage *.zip`

## Crate design (workspace layout)

- `riscvtest-core` — canonical types + normalization
- `riscvtest-runner` — runner traits + adapters
- `riscvtest-diff` — diff and report generation
- `riscvtest-bundle` — bundle IO + redaction policies
- `cargo-riscvtest` — CLI

## Minimum lovable MVP (4–8 weeks)

1. RISCOF adapter that:
  - runs a pinned suite
  - parses outcomes into canonical JSON
  - emits a bundle on failure
  Source: https://riscof.readthedocs.io/en/latest/intro.html
2. Diff engine + `cargo riscv-test diff`.
3. Add a second adapter (QEMU or Spike) to prove adapter model.

## De-risk plan

- Start with simulator targets to reduce nondeterminism.
- Build a tiny corpus of “known-failing” configurations to validate explainers.
- Keep scope to *architectural outcomes*; no performance claims.

## Scorecard (0–5)

- Impact: 3
- Neglectedness: 4
- Feasibility: 4
- Adoptability: 3
- Sustainability: 3
- Differentiation: 4
