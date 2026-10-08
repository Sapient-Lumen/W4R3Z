---
id: P-0203
title: Audio Plugin Interop, Sandbox, and Golden‑DSP Lab Kit (CLAP/VST3)
status: idea
domains: [audio, interoperability, tooling, sandboxing, testing]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/free-audio/clap
  - https://steinbergmedia.github.io/vst3_dev_portal/pages/FAQ/Licensing.html
  - https://github.com/steinbergmedia/vst3sdk
---

# Problem

Rust audio work is thriving, but shipping *host-quality* plugin tooling is still painful:
- plugin scanning is brittle and can crash hosts,
- behavior differs by DAW/OS, and regressions are hard to reproduce,
- “does this plugin render the same audio?” is rarely testable in CI,
- sandboxing and ABI conformance checks are ad-hoc.

We have wrappers and frameworks, but lack a **shared interop lab** with portable evidence bundles.

# What it provides

A crate + CLI that turns plugin interop into deterministic artifacts:

- `audiolab` CLI:
  - scan + validate plugins (CLAP and VST3)
  - run *golden DSP* tests (offline render → hash/diff)
  - capture crashes and isolate plugins via sandbox profiles
  - emit `*.audiobundle.zip` with reports + minimal repro inputs

- Rust library:
  - stable plugin discovery + metadata normalization
  - “render harness” (offline, deterministic scheduling, fixed RNG)
  - ABI conformance + extension probing (CLAP) and interface probing (VST3)
  - sandbox adapters (process isolation, seccomp/job objects where available)

# Users & user stories

- **DAW authors**: “Scan third-party plugins safely; isolate crashes; keep a repro bundle.”
- **Plugin authors**: “Run a golden test matrix across platforms before release.”
- **CI**: “Detect nondeterministic render regressions and performance cliffs.”

# Prior art (and why it’s insufficient)

- CLAP defines a stable ABI and extension model, but does not provide a turnkey conformance + evidence workflow.  
- VST3 SDK is MIT licensed and widely used, but host implementers still rebuild validation and scanning toolchains.  
- Existing Rust wrappers/frameworks do not standardize **portable golden-test bundles**.

# Design goals

- Deterministic offline rendering harness for golden tests.
- Crash-safe scanning with strong sandbox defaults.
- Standard evidence bundles to share failures and reproduce quickly.
- Modular: usable as a library in existing hosts.

# Non-goals

- A full DAW.
- Replacing existing plugin frameworks; integrate with them.

# Architecture & API sketch

Crates:
- `audiolab-core` (discovery, normalization, bundle IO)
- `audiolab-clap` (CLAP host harness + extension probes)
- `audiolab-vst3` (VST3 host harness + interface probes)
- `audiolab-sandbox` (process isolation + policy)
- `audiolab-cli`

`audiobundle.zip`:
- `manifest.json` (OS/CPU, host version, sandbox profile)
- `plugins.json` (normalized descriptors)
- `runs/` (per plugin: conformance + render report)
- `audio/` (optional reference WAV + hashes)
- `logs/` (crash traces, host logs)

# Security / safety model

- Default to process isolation for untrusted plugins.
- Explicit policies for filesystem/network access in scan/test mode.
- Redaction hooks for proprietary plugin metadata where needed.

# Maintenance & governance plan

- Version the bundle schema; publish fixtures and sample plugins.
- Encourage community contributions of test vectors and harness adapters.

# Milestones

1. MVP: discovery + CLAP scan + bundle format
2. Deterministic render harness + golden test diffs
3. VST3 scan/harness integration
4. Sandboxing adapters (per OS)
5. Conformance suite library + public fixture corpus

# Open questions

- How to define “acceptable nondeterminism” thresholds in DSP diffs?
- Best cross-platform sandbox story for plugin scanning in Rust?

# Sources

- CLAP Audio Plugin API — https://github.com/free-audio/clap
- Steinberg VST3 licensing FAQ (MIT) — https://steinbergmedia.github.io/vst3_dev_portal/pages/FAQ/Licensing.html
- VST3 SDK repository — https://github.com/steinbergmedia/vst3sdk
