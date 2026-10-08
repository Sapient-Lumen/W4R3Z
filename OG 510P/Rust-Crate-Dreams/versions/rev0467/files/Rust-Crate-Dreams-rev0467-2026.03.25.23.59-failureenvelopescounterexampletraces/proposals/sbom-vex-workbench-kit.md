---
id: P-0102
title: SBOM + VEX Workbench Kit — generate, diff, and triage SBOMs with portable VEX outputs for Cargo projects
status: idea
domains: [security, supply-chain, cargo, policy, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/cargo-sbom
  - https://github.com/CycloneDX/cyclonedx-rust-cargo
  - https://cyclonedx.org/capabilities/vex/
  - https://trivy.dev/docs/v0.51/supply-chain/vex/
needs:
  - teams can generate SBOMs, but lack **standard diff + triage + VEX publication** workflows for Rust
  - “security SBOMs” and “compliance SBOMs” pull in different directions; Rust teams need an ergonomic bridge
  - CI needs a stable artifact to store decisions (false positives, not affected, mitigations) and keep them consistent
---

# Problem

Rust has multiple SBOM generators, but the hard part is not *generation*:
- SBOMs are noisy and frequently changing; teams need **stable diffing** to understand risk impact.
- Vulnerability scanners produce findings; teams need **portable, reviewable triage output** (VEX) that can be reused across runs and tools.
- Cargo features/MSRV/target triples complicate “what is actually shipped”.

# What it provides

## 1) A cargo-native workflow
- `cargo sbomx build` → generates SBOM(s) for a workspace with a declared **scope**:
  - `--profile release|dev`
  - `--target <triple>`
  - `--features <set>` / `--all-features`
- `cargo sbomx diff <old> <new>` → stable diff report (packages, licenses, suppliers, hashes, relationships)
- `cargo sbomx triage` → interactive / config-driven triage producing **VEX** output

## 2) Standard artifacts
- `sbom.json` (CycloneDX or SPDX, selected by flag)
- `sbom.diff.json` (stable, tool-independent diff format)
- `vex.json` (CycloneDX VEX / OpenVEX / CSAF adapter layer — start with CycloneDX VEX)
- `triage.toml` (human-editable policy + waivers with expiry)

## 3) “Policy gates” people can actually use
- License policy (deny/allow/notice)
- Dependency policy (ban list, allow list, namespace rules)
- Vulnerability policy (fail on CVSS threshold unless VEX says “not affected” with rationale)

# Users & user stories

- **Security engineer**: “We already scan; I want one canonical triage output we can review in PRs.”
- **Maintainer**: “I want to publish SBOM+VEX for releases with minimal setup.”
- **Compliance**: “Give me SPDX; security wants CycloneDX; don’t make us run 5 tools.”

# Prior art (and why it’s insufficient)

- `cargo-sbom` generates SBOMs (SPDX) but doesn’t define a triage + VEX workflow.
- `cyclonedx-rust-cargo` generates CycloneDX SBOMs, but teams still need consistent diffing and triage artifacts.
- External scanners (e.g., Trivy) support VEX, but Rust teams need Cargo-shaped inputs, stable scoping, and a Rust-native policy format.

# Design goals

- **Reproducible scoping**: SBOM must be tied to target/profile/features.
- **Diff-first**: changes should be reviewable like code changes.
- **Tool-agnostic triage**: VEX output usable by multiple scanners.
- **Low-friction publishing**: release automation should be straightforward.

# Non-goals

- Building a new vulnerability database. Integrate with existing sources (OSV, etc.) via adapters.
- Replacing enterprise scanners; instead: feed them better, reuse their outputs.

# Architecture & API sketch

- Parse Cargo metadata + lockfile + build graph.
- Build a normalized package identity (name, version, source, checksum).
- Emit SBOM via existing libraries where possible; wrap with stable diff layer.
- Triage engine:
  - input: findings (from scanner JSON) + policy + SBOM
  - output: VEX + report

# Security / safety model

- Protect against “policy bypass”:
  - triage waivers must carry rationale + expiry
  - `cargo sbomx verify` checks VEX matches current SBOM (no stale waivers)
- “Signed artifacts” optional: integrate with existing provenance/attestation tools rather than inventing a new signature scheme.

# Maintenance & governance plan

- Treat artifact schemas as versioned contracts.
- Maintain a fixture suite of representative Cargo workspaces (features, targets, proc-macros).

# Milestones

1) MVP
   - Generate CycloneDX + SPDX (via existing tools/libs)
   - Emit `sbom.diff.json`
2) v1
   - VEX generation + `triage.toml`
   - CI integration + publishing guide
3) vNext
   - Multiple VEX flavors (OpenVEX/CSAF) adapters
   - Multi-target aggregation

# Open questions

- Best stable diff semantics for dependency relationships and feature-derived edges?
- How to model “optional” deps in a human-comprehensible way?

# Sources

- `cargo-sbom` (Cargo SBOM generator; SPDX): https://crates.io/crates/cargo-sbom
- CycloneDX Cargo plugin: https://github.com/CycloneDX/cyclonedx-rust-cargo
- CycloneDX VEX capability overview: https://cyclonedx.org/capabilities/vex/
- Trivy VEX docs (CSAF support and SBOM-agnostic VEX usage): https://trivy.dev/docs/v0.51/supply-chain/vex/
