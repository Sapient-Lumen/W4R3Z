---
id: P-0010
title: Cargo SBOM Kit — shared foundation for SBOM/provenance verification across tools
status: idea
domains: [cargo, security, supply-chain, compliance]
last_reviewed: 2026-03-01
evidence:
  - https://internals.rust-lang.org/t/idea-a-small-crate-for-verifying-crates-generating-sboms-future-proof-for-signing/23574
  - https://rustsec.org/
  - https://github.com/mozilla/cargo-vet
  - https://internals.rust-lang.org/t/pre-rfc-cargo-sbom/19842
  - https://docs.rs/crate/cargo-sbom/latest
  - https://crates.io/crates/cargo-cyclonedx
---

## What it should provide others

A **single, correct, well-tested foundation** for tools that generate or verify SBOMs and provenance for Cargo projects.

The crate should give users:

- **Canonical Cargo graph extraction** (workspace + features + targets) with stable output.
- **Normalization rules** so multiple tools don't drift.
- **SBOM emitters** behind feature flags (CycloneDX/SPDX), but with a shared core model.
- **Verification hooks**:
  - lockfile consistency checks
  - source integrity (registry vs git)
  - provenance inputs (CI OIDC, attestations) as optional adapters

## Why this is still missing

Multiple SBOM tools re-implement “parse Cargo metadata + resolve edges + map to SBOM” slightly differently, leading to drift and inconsistent results.

## Design principles

- **Core model first**: small, dependency-light, strict semver.
- **Pluggable output**: SBOM formats as thin layers.
- **Test corpus**: real-world workspaces + feature combinations.

## MVP

1. Core graph model: packages, targets, features, sources, checksums.
2. Deterministic JSON output for the graph (for golden tests).
3. One SBOM output (CycloneDX or SPDX) as a reference implementation.
4. “Verification mode” that reports inconsistencies and risky sources.

## Adoption plan

- Make it easy for existing tools (and CI) to adopt by exposing a stable CLI + library API.
- Provide a “compatibility suite” so tool authors can validate they match the shared core.
