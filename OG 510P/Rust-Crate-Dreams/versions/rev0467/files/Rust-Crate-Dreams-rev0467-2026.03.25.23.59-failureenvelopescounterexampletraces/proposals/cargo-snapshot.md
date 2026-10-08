---
id: P-0001
title: Cargo Snapshot — reproducible offline mirrors & air-gap transfer
status: idea
domains: [cargo, enterprise, supply-chain, offline]
last_reviewed: 2026-02-28
evidence:
  - https://users.rust-lang.org/t/alternate-crates-io-index-repo/133959
  - https://users.rust-lang.org/t/how-to-transfer-crates-to-a-private-registry/121156
  - https://rust-lang.github.io/rfcs/2141-alternative-registries.html
---

# Problem
Cargo can *technically* use alternate registries, but **getting a robust offline mirror + air-gap transfer workflow** is still described as brittle and under-documented by practitioners. The “happy path” for enterprises (no internet, allow-lists, reproducible snapshots) remains hard.

# Users & user stories
- Defense/critical infrastructure teams: “I need an allow-listed snapshot of crates + sources + checksums I can sneaker-net across an air gap.”
- Regulated fintech/healthcare: “I need an auditable SBOM and a deterministic dependency snapshot for every release.”
- CI operators: “I need a cache/mirror that works without internet and doesn’t corrupt builds.”

# Prior art (and why it’s insufficient)
- Existing mirroring tools and private registries exist, but threads still report fragility and missing docs for end-to-end workflows (mirror → transfer → consume).  
  See air-gap transfer requests and offline mirror frustration threads (sources above).

# Design goals
- Reproducible, content-addressed **“crate snapshot”** format:
  - index metadata + crate tarballs + checksums + yanked info
  - optional full `Cargo.lock` resolution capture
- Allow-list driven: mirror *exactly* what policy permits.
- Air-gap first: export/import bundles with integrity verification.
- Pluggable storage (filesystem, S3-like, artifact repo).
- Optional security hooks: RustSec scan, signatures, provenance capture.

# Non-goals
- Replacing crates.io.
- Solving every enterprise proxy/cache configuration.
- A full package repository manager UI.

# Architecture & API sketch
- CLI (primary): `cargo snapshot ...`
  - `cargo snapshot resolve --manifest-path ... --out snapshot.cars` (cars = Cargo ARchive Snapshot)
  - `cargo snapshot mirror --allowlist allow.toml --out dir/`
  - `cargo snapshot export --snapshot dir/ --out bundle.tar.zst`
  - `cargo snapshot import --bundle bundle.tar.zst --into mirror/`
- Library crates:
  - `snapshot-format` (serde + versioned schema)
  - `snapshot-store` (traits for blob/index backends)
  - `snapshot-verify` (hash/signature verification)

# Security / safety model
- Strong hashing (sha256/sha512) over all artifacts.
- Optional Sigstore-style provenance hooks (leave pluggable).
- Hardened parsing (deny unsafe by default; fuzz snapshot readers).

# Maintenance & governance plan
- Start as a cargo subcommand crate with minimal deps.
- Publish a reference “air-gap cookbook” in-repo.
- Set up a maintainer rotation and a “succession” policy.

# Milestones
- 0.1: export/import for a resolved workspace (Cargo.lock based)
- 0.2: registry mirror mode (allow-list + sparse index compatibility)
- 0.3: integrity verification + SBOM emission (SPDX/CycloneDX bridge)
- 1.0: stable snapshot format + documented enterprise playbooks

# Open questions
- Best snapshot granularity: per-workspace vs per-registry slice?
- How to represent yanks and index history deterministically?

# Sources
- https://users.rust-lang.org/t/alternate-crates-io-index-repo/133959
- https://users.rust-lang.org/t/how-to-transfer-crates-to-a-private-registry/121156
- https://rust-lang.github.io/rfcs/2141-alternative-registries.html
