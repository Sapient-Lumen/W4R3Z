---
id: P-0094
title: Hermetic Build Capsule Kit (Cargo-focused) — portable frozen builds via a standard capsule artifact
status: idea
domains: [supply-chain, build, reproducibility, devtools, security]
last_reviewed: 2026-03-05
evidence:
  - https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
  - https://doc.rust-lang.org/cargo/commands/cargo-fetch.html
  - https://doc.rust-lang.org/cargo/commands/cargo.html
  - https://users.rust-lang.org/t/how-to-build-project-offline-when-cargo-vendor-is-not-working/90110
---

# Problem
Cargo offers pieces for offline and deterministic builds (`--offline`, `--locked`) and dependency vendoring (`cargo vendor`), but teams still struggle to produce a **portable, verifiable “frozen build” artifact** that can be moved between machines and CI environments.

# What it provides
- **Capsule specification**: `*.cargocapsule.zip`
  - workspace source snapshot (or references + hashes)
  - `Cargo.lock` + manifest hashes
  - `vendor/` dependencies + `.cargo/config.toml` wiring
  - toolchain pins and target triples
  - `meta.json` describing how it was produced
- **CLI / cargo subcommand**
  - `cargo capsule build` (create capsule)
  - `cargo capsule verify` (hash checks + lock invariants)
  - `cargo capsule unpack` (restore workspace + config)
- **Hermeticity report**
  - identifies non-hermetic edges (build scripts, external system libs, env vars)

# Users & user stories
- **CI/platform teams**: “Freeze a build and move it across runners reliably.”
- **Airgapped environments**: “Build without network, with verifiable deps.”
- **Release engineers**: “Attach a capsule to a release as evidence.”

# Prior art (and why it’s insufficient)
- `cargo vendor` + offline flags solve pieces, but there is no *standard artifact* teams can exchange or publish as a repeatable unit.

# Design goals
- Capsule format is small, verifiable, and versioned.
- Works with stock Cargo (capsule tool just orchestrates and packages).
- Clear error messages and “doctor”-style diagnostics.

# Non-goals
- Replacing Nix/Bazel (interop is a plus).
- Solving every system dependency (document + optional probes).

# Architecture & API sketch
- `capsule_spec` module: format + hashing rules
- `capsule_cli`: pack/unpack/verify
- `capsule_probe`: optional system-dependency detection

# Security / safety model
- Verification is default; treat capsules as untrusted until verified.
- Provide optional signature hooks (but keep base usable without signing).

# Maintenance & governance plan
- Strict semantic versioning for capsule format.
- Conformance fixtures: golden capsules that must verify on CI.

# Milestones
- 0.1: pack/unpack + verify + minimal spec
- 0.2: hermeticity report + better diagnostics
- 0.3: CI templates + integration docs
- 1.0: stable capsule format + conformance suite

# Open questions
- How to encode system library dependencies (document vs capture).
- How to handle git deps/submodules cleanly.

# Sources
- See evidence links above.
