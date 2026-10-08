---
id: P-0079
title: Rebuilder Network Kit — reproducible build verification as a first-class Rust workflow
status: idea
domains: [supply-chain, reproducibility, cargo, security, tooling]
last_reviewed: 2026-03-04
evidence:
  - https://internals.rust-lang.org/t/verifying-rustc-releases-with-reproducible-builds/4502
  - https://internals.rust-lang.org/t/reproducible-builds-for-rustc-gsoc-25-idea/22532
  - https://slsa.dev/spec/v1.1/faq
---

## Problem
Cargo helps with repeatable dependency resolution, but independent rebuild verification (bit-for-bit or policy-defined equivalence) is still difficult for typical Rust projects.

Without a standard “rebuild capsule” format and runner, every project invents ad-hoc Dockerfiles or Nix setups, and verification never becomes routine.

## Thesis
Make “anyone can rebuild this and verify it” feel like:
- `cargo publish`
- `cargo test`
- `cargo doc`

## What it should provide other people (MVP)
### 1) Rebuild capsule format
A signed bundle that includes:
- toolchain identity (rustc, cargo, linker)
- dependency graph snapshot
- build command + features
- a policy for build script I/O capture/allowlist
- `SOURCE_DATE_EPOCH` and other determinism knobs

### 2) Runner backends
Pluggable execution:
- Docker/Podman
- Nix
- VM-based runner (for high assurance)

### 3) Verifier
- compares artifacts (hashes + metadata)
- emits a signed rebuild attestation that can be linked to provenance

### 4) Developer UX
- `cargo rebuild capsule` to generate and publish capsules
- `cargo rebuild verify` to run capsule + attest success/failure
- “why did this differ?” diagnostics:
  - env var diffs
  - file order/timestamps
  - build script outputs

## Compatibility strategy
Ship “repro levels”:
- Level 0: functional equivalence checks (ELF/PE metadata normalized)
- Level 1: deterministic archive ordering + timestamps
- Level 2: bit-for-bit identical outputs under a hermetic runner

## “Epic” extension ideas
- A public “rebuilder pool” protocol so multiple independent parties can verify popular crates.
- Registry integration (crates.io / OCI) to attach capsules and attestations.
