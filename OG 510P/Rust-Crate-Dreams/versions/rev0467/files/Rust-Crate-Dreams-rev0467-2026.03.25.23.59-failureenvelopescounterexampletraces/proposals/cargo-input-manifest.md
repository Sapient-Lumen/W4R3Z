---
id: P-0045
title: cargo-input-manifest — build signatures & input manifests for Cargo builds
status: idea
domains: [cargo, reproducible-builds, caching, supply-chain]
last_reviewed: 2026-03-01
evidence:
  - https://www.reddit.com/r/rust/comments/z0jtlc/get_a_list_of_all_input_files_used_by_cargo_build/
  - https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  - https://github.com/rust-lang/cargo/issues/2607
  - https://github.com/rust-lang/cargo/issues/8612
---

# Problem
Tooling for **reproducible builds, caching, and auditability** often needs a definitive answer to:
> “What *exactly* were the inputs to this build?”

Today, getting a complete input set is hard:
- Rustc can emit dep-info for a single compilation unit, but Cargo orchestrates many units, build scripts, proc macros, and generated files.
- Users explicitly ask for a file list / checksums / “build signature” (see evidence).
- Without a canonical artifact, people reinvent partial solutions (Docker-layer heuristics, bespoke file walkers, build logs, CI caching guesses).

# Users & user stories
- **CI/platform engineers**: “I need a deterministic build signature so cache keys and artifact promotion are reliable.”
- **Security/compliance**: “I need an evidence pack: inputs + toolchain + dependency graph for an audit.”
- **Build performance teams**: “I need to understand what changed between builds and why rebuilds happened.”
- **Reproducible-builds folks**: “I want a machine-verifiable input manifest for rebuild verification.”

# Prior art (and why it’s insufficient)
- Cargo is prototyping **build analysis** (`cargo report rebuild-reasons` / timing) but that is not yet a stable, widely-available input manifest artifact. (Evidence link.)
- Deterministic build ordering and “replayable” build plans have been requested for years. (Evidence link.)
- Reproducible `.crate` packaging is still a request — build signatures would directly support “what changed?” and “why aren’t outputs identical?”. (Evidence link.)

# Design goals
- Produce a **stable, deterministic “input manifest” artifact** for a Cargo build:
  - list of input files (workspace + dependencies + generated inputs)
  - digests (configurable: hash paths+metadata only, or content hashes)
  - environment influences (selected env vars, RUSTFLAGS/build.rustflags, target triple)
  - toolchain identity (rustc/cargo versions, host triple)
  - build plan fingerprint (packages/features/targets selected)
- Explainability: generate a diff between two manifests (“what inputs changed?”).
- Privacy controls: path redaction, hash-only mode, and allowlisted env capture.
- Integrate with emerging Cargo directions instead of fighting them (build-analysis, future `cargo report`).

# Non-goals
- Proving full bit-for-bit reproducibility by itself (that’s a larger system).
- Replacing Cargo’s own planned reporting formats.
- A universal solution for non-Rust external tools (but we should record them if we can detect them).

# Architecture & API sketch
## CLI (primary)
- `cargo input-manifest build [--] <cargo args...>`
- `cargo input-manifest diff <manifest_a> <manifest_b>`
- `cargo input-manifest verify --expected <manifest>`

## Library
- `InputManifest::collect(CollectConfig) -> Manifest`
- `Manifest::diff(&self, other) -> DiffReport`

## Data sources (layered)
1. **Preferred**: Cargo build-analysis DB (nightly/unstable where available).
2. **Rustc dep-info**: parse `.d` files for each compilation unit.
3. **Filesystem watcher fallback**: observe reads during the build (best-effort; OS dependent).
4. **Cargo metadata**: capture the resolved package graph and selected features/targets.

# Security / safety model
- Treat manifests as sensitive: paths, env, and file hashes can leak information.
- Default to **minimal capture** + explicit opt-ins for broader env/path collection.
- Provide a “CI-safe mode” that stores only relative paths + content hashes.

# Maintenance & governance
- Keep dependencies minimal (serde + hashing + small parsers).
- Nightly integration behind feature flags (do not block stable users).
- Conformance fixtures: small workspaces that exercise build.rs, proc macros, codegen, and path dependencies.

# Success criteria
- CI users can adopt manifest-based caching keys and see fewer “mysterious cache misses”.
- Reproducibility workflows can attach the manifest to artifacts as an evidence pack.
- The tool produces actionable diffs that explain rebuild/regression causes.
