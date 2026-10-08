---
id: P-0157
title: FHE Application Workbench Kit
status: idea
domains: [cryptography, privacy, ml, interop, devtools, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://docs.zama.org/tfhe-rs
  - https://crates.io/crates/tfhe
  - https://github.com/zama-ai/tfhe-rs
  - https://github.com/jonaschn/awesome-he
---
# Problem

Fully Homomorphic Encryption (FHE) in Rust is getting real: strong libraries exist, but application teams still hit a cliff:

- Choosing parameters / feature sets is hard to do safely and reproducibly.
- Performance regressions are difficult to diagnose (CPU vs GPU backends, key sizes, encodings).
- Interop formats for “encrypted payloads” and “evaluation keys” are ad hoc.
- Debugging often can’t share raw data, so incidents become unhelpfully vague.

What’s missing is the **application workbench layer**: profiles, artifacts, conformance, and reproducible performance/semantic checks that sit *above* the cryptographic core crates.

# What it should provide

## 1) Opinionated “profiles” for common app shapes

A profile system (versioned) that encodes safe defaults and constraints:

- boolean / small-int / integer / string workloads
- latency vs throughput profiles
- CPU-only vs GPU-accelerated profiles
- key rotation + serialization constraints

Output should be machine-readable: `profile.json` + `constraints.json` + “why” notes.

## 2) A standard bundle format for private bug reports

A redactable `fhebundle.zip` that allows sharing **semantic and performance evidence** without leaking plaintext:

- `manifest.json` (library versions, backend, CPU/GPU features, profile id)
- `params.json` (public parameter choices; redaction rules)
- `ops.jsonl` (operation trace over ciphertext types—no plaintext)
- `key-meta.json` (sizes, rotation epochs, but no secret key material)
- `perf.json` (timings, memory, GPU kernel counters if available)
- `conformance.json` (expected invariants: noise budget constraints, roundtrip checks on synthetic data)
- `repro/` scripts to re-run on synthetic plaintext corpora that match the same op-shape

## 3) Conformance packs and “known-good” vectors

- Serialization stability checks across versions (forward/back compatibility policy)
- Cross-backend equivalence (CPU vs GPU outputs must match within defined rules)
- Fuzz/minimize support for operation traces that trigger failures

# MVP → v1 plan

### MVP
- `fhebundle.zip` schema + collector macros/helpers
- Profile definitions + a `cargo fhe doctor` that checks feature selections and emits a report
- Minimal conformance harness for (a) serialization and (b) trace replay on synthetic corpora

### v1
- Backend adapters (start with TFHE-rs; later others)
- CI mode: run standardized microbenchmarks + regression diffs
- Interop spec: stable “encrypted payload envelope” for networked services

# Why this is “epic” (and not redundant)

Cryptographic cores should stay focused; the missing crate is the **ops layer** that turns FHE from “library you can call” into “system you can operate and debug.”
