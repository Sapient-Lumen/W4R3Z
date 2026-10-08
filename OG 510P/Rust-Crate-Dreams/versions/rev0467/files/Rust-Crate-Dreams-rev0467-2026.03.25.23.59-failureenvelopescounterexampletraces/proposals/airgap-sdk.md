---
id: P-0018
title: Airgap SDK — one bundle for rustup toolchains + Cargo dependencies (verified, reproducible)
status: idea
domains: [offline, enterprise, cargo, rustup]
last_reviewed: 2026-03-01
evidence:
  - https://www.reddit.com/r/rust/comments/v889xy/offlineish_installation_mirroring_of_rust/
  - https://github.com/panamax-rs/panamax
  - https://rust-lang.github.io/rustup/environment-variables.html
  - https://users.rust-lang.org/t/proper-offline-install/116256
---

# Problem
Air-gapped environments have *two* painful problems:
1) **Rust toolchains** (rustc, std for targets, clippy, rustfmt, etc.)
2) **Third-party crates**
Teams regularly report that toolchain components/targets are hard to mirror and that offline installs miss components.

There are tools to mirror pieces, but the ecosystem lacks a single, deterministic “bundle artifact” that captures:
- toolchain requirements (from `rust-toolchain.toml`),
- the workspace dependency snapshot (from `Cargo.lock`),
- and verified checksums for all downloaded materials.

# Users & user stories
- **Defense/regulated orgs**: “Generate an offline bundle on an internet machine, carry it across the airgap, and install with 1 command.”
- **CI/CD**: “Pin toolchain + deps as an auditable artifact for reproducible builds.”
- **Platform teams**: “Host an internal mirror and give devs a copy-paste config.”

# Prior art
- Panamax mirrors rustup + crates.io, but orgs still need project-scoped, reproducible bundles with explicit manifests.
- rustup supports custom dist servers via env vars, but configuring + mirroring correctly is error-prone.

# Design goals
- Produce a single bundle (tar/zip) containing:
  - rustup dist mirror subset needed for a specific toolchain/components/targets
  - crates snapshot for a specific workspace build plan
  - a `manifest.json` with sha256 for everything
- Apply bundle on offline machine:
  - configure `RUSTUP_DIST_SERVER` to point to local mirror
  - configure Cargo registry source replacement to local snapshot
- Offline-first: no network required to use the bundle.

# Architecture & API sketch
## CLI (`airgap-sdk`)
- `airgap-sdk bundle` (run online)
  - reads `rust-toolchain.toml`
  - downloads required components/targets (verified)
  - downloads `.crate` artifacts for resolved deps
  - writes `bundle/manifest.json` + `bundle/config/` snippets
- `airgap-sdk apply` (run offline)
  - installs/updates rustup dist mirror
  - writes `.cargo/config.toml` (or prints instructions)
  - verifies checksums

## Extensibility
- Plugin interface for:
  - alternate registries,
  - org policy checks,
  - signing the manifest (future: sigstore).

# Security / safety model
- Integrity: sha256 verification for every downloaded artifact.
- Optional signing for manifests (future, aligns with provenance work).

# Maintenance & governance plan
- Keep to stable file formats and explicit manifests.
- Provide end-to-end tests using a small workspace + a minimal toolchain spec.

# Milestones
- **0.1**: toolchain subset mirroring + manifest
- **0.2**: crate snapshot bundling + apply path
- **0.3**: multi-target support + docs for enterprise mirrors
- **1.0**: signed bundles + policy hooks + hardening

# Scorecard (0–5)
- Impact: 5
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5

# Sources
- https://www.reddit.com/r/rust/comments/v889xy/offlineish_installation_mirroring_of_rust/
- https://github.com/panamax-rs/panamax
- https://rust-lang.github.io/rustup/environment-variables.html
- https://users.rust-lang.org/t/proper-offline-install/116256
