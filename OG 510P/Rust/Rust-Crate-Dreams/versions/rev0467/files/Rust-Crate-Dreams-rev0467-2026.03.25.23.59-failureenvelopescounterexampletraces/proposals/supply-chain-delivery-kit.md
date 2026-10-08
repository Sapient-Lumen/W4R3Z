---
id: P-0119
title: Supply-Chain Delivery Kit (TUF + in-toto + policy bundles)
status: idea
domains: [supply-chain, security, release, ota, provenance]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/tough
  - https://docs.rs/tough
  - https://github.com/awslabs/tough
  - https://crates.io/crates/in-toto
  - https://github.com/in-toto/in-toto
  - https://internals.rust-lang.org/t/about-supply-chain-attacks/14038
---

# Problem

Rust teams increasingly want **end-to-end integrity** for releases and updates: not just “the crate tarball hashes”, but also:
- *who* built it, *how*, and *from what source* (provenance / attestations),
- *what update channel* it belongs to (targets, delegations, rollback/expiration),
- and *how consumers verify* policies consistently in CI and on devices.

Pieces exist (SBOM tools, provenance tools, TUF clients), but they don’t compose into a coherent, ergonomic, “ship this in production” Rust-native workflow.

# What it provides

A **Supply-Chain Delivery Kit** centered around a portable artifact contract:

1. **A unified metadata envelope**
   - `delivery-bundle.zip` containing:
     - TUF repository snapshot + targets metadata (with expiry checks)
     - optional in-toto layout + link metadata for build steps
     - optional SBOM + provenance (SLSA-style statements)
     - `policy.toml` (consumer-side policy: required keys, expiry windows, required attestations)
     - `report.json` (normalized verification results)

2. **Crate surface (library)**
   - `delivery::verify(bundle, policy)` producing a structured report:
     - key trust chain
     - target selection / delegation trace
     - rollback detection
     - expiry warnings
     - attestation verification results
   - `delivery::publish(...)` helpers for building repositories and signing targets.

3. **Cargo UX**
   - `cargo delivery verify <bundle>` (CI-friendly)
   - `cargo delivery publish` (produce a signed repo + bundle)
   - `cargo delivery doctor` (detect common mistakes: clock skew, missing delegations, stale metadata)

4. **Conformance suite**
   - golden bundles covering:
     - rollback / freeze / mix-and-match attacks (TUF threat model)
     - expired metadata
     - wrong keys / rotated keys
     - missing / tampered attestations
   - fuzz corpus for metadata parsing and policy edge-cases.

# Users & user stories

- **Maintainers shipping binaries**: “I need a standard, well-audited way for users to verify updates.”
- **Platform/SRE teams**: “We need policy gates for what we will run in production.”
- **Embedded/IoT teams**: “We need offline-first update verification with clear rollback protection.”

# Prior art (and why it’s insufficient)

- `tough` is a solid Rust TUF client but does not “complete the loop” into a full delivery workflow with policy + attestations + bundles.
- in-toto frameworks exist but aren’t integrated into an ergonomic Rust delivery pipeline by default.
- A lot of real-world pipelines hand-roll signing/verification glue, which is fragile and inconsistent.

# Design goals

- **Artifact-first**: the bundle is the collaboration unit (attach it to issues, store in CI artifacts, share with vendors).
- **Policy clarity**: verification should be explainable (“why accepted / rejected”).
- **Interop, not monopoly**: support multiple signers/KMS backends, and don’t lock to one CI vendor.

# MVP plan

- Accept a `delivery-bundle.zip` with:
  - TUF metadata + target files
  - `policy.toml`
- Verify: expiry + threshold keys + rollback protection + target hash matching.
- Emit `report.json` + a human-readable summary.
- Provide a generator that can create a minimal repo + sign targets locally.

# v1 plan

- Add optional in-toto verification (layout + link metadata).
- Add provenance attestations as optional requirements.
- Add a curated conformance bundle suite and publish it as versioned fixtures.

# Risks & mitigations

- **Cryptography footguns** → minimize custom crypto; lean on established libs; keep interfaces narrow.
- **Policy complexity** → ship a small set of safe profiles, allow advanced extensions later.
