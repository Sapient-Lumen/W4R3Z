---
id: P-0015
title: Cargo Attest — build provenance + in-toto attestations for Rust crates and binaries
status: idea
domains: [supply-chain, provenance, cargo, security]
last_reviewed: 2026-03-01
evidence:
  - https://crates.io/docs/trusted-publishing
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://slsa.dev/spec/v1.0/provenance
  - https://github.com/in-toto/attestation
  - https://internals.rust-lang.org/t/pre-rfc-using-sigstore-for-signing-and-verifying-crates/18115
---

# Problem
crates.io is moving toward **tokenless publishing** via OIDC (“Trusted Publishing”), reducing the risk of leaked API tokens.
But Rust still lacks a widely adopted, end-to-end story for **artifact-level attestations** (what was built, from what sources, by what builder, under what inputs) that downstream systems can verify.

# Users & user stories
- **Org security**: “Prove this crate/binary was built in CI from this repo+ref, with these deps, and hasn’t been tampered with.”
- **Consumers**: “Verify provenance before deploying.”
- **Registry operators / private registries**: “Store attestations alongside artifacts.”

# Prior art (and gaps)
- Trusted Publishing secures *who can publish*, not *what was built*.
- There are ecosystem specs and tools (SLSA provenance, in-toto attestations, Sigstore) but no Cargo-native, Rust-first “golden path” that outputs attestations for crates/binaries in a predictable location and schema.

# Design goals
- Generate **in-toto statements** with a SLSA provenance predicate for:
  1) `cargo package` output (`.crate`)
  2) `cargo build` output (binaries)
- Support both:
  - **keyless** signing (OIDC flows; CI-friendly),
  - **keyful** signing (local keys/KMS; enterprise).
- Deterministic subject identity: stable hashes for produced artifacts + resolved dependency graph.

## Non-goals
- Changing Cargo/crates.io protocols (initially). This crate produces artifacts that registries/tools *can* adopt later.

# Architecture & API sketch
## Crates
- `attest_core`: statement types + hashing + serialization
- `attest_sign`: pluggable signer interface (keyless/keyful)
- `cargo-attest` (CLI)
  - `cargo attest package` → `target/attestations/<pkg>/<ver>/<hash>.intoto.json`
  - `cargo attest build` → `target/attestations/...` for binaries

## Key interfaces
- `Subject { name, digest: { sha256 }, uri? }`
- `BuildInfo { repo, ref, builder_id, build_type, materials[] }`
- `Predicate` supports SLSA Provenance v1 (and allows additional predicates later).

# Verification workflow
- `cargo attest verify --policy policy.toml`
- Policies can require:
  - builder identity,
  - repo/ref allowlist,
  - reproducible inputs (lockfile hash),
  - transparency log inclusion (optional).

# Security / safety model
- Treat build metadata as sensitive in some orgs (paths, env vars). Provide redaction knobs and clear defaults.
- Signed artifacts should be verifiable offline.

# Maintenance & governance plan
- Keep core types stable and small.
- Integration tests in GH Actions showing:
  - Trusted Publishing + attestation output,
  - local signing,
  - verification.

# Milestones
- **0.1**: package attestations (in-toto statement + SLSA provenance skeleton)
- **0.2**: binary attestations + subject hashing conventions
- **0.3**: keyless signing adapter + verification CLI
- **1.0**: stable schemas + policy engine + docs + examples

# Scorecard (0–5)
- Impact: 5
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5

# Open questions
- Where should attestations live for crates.io in the long run (index, sidecar store, transparency log)?
- What minimal metadata should be included by default without leaking secrets?

# Sources
- https://crates.io/docs/trusted-publishing
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://slsa.dev/spec/v1.0/provenance
- https://github.com/in-toto/attestation
- https://internals.rust-lang.org/t/pre-rfc-using-sigstore-for-signing-and-verifying-crates/18115
