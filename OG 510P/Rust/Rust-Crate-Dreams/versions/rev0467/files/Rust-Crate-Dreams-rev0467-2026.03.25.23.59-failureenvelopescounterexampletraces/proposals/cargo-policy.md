---
id: P-0007
title: cargo-policy — enforce org security & compliance gates (SBOM/provenance/vetting)
status: idea
domains: [cargo, supply-chain, security, compliance]
last_reviewed: 2026-02-28
evidence:
  - https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  - https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
  - https://rustsec.org/advisories/
  - https://weihanglo.tw/posts/2024/the-missing-parts-in-cargo/
---

# Problem
Rust has great *pieces* (RustSec, SBOM tools, vetting), but organizations still struggle to turn them into a coherent policy gate. Cargo also falls short in some enterprise settings (offline constraints, audit requirements, cache/proxy realities).

# Users & user stories
- Security teams: “Block builds that violate policy (vulns, licenses, provenance).”
- Release engineering: “Generate SBOM + attestations for every build.”
- Developers: “Tell me exactly what failed and how to fix it.”

# Prior art (and why it’s insufficient)
- Tools exist, but require assembling bespoke pipelines; policies drift across repos.

# Design goals
- `cargo policy check` with a policy file (TOML):
  - vulnerability thresholds (RustSec)
  - license allow/deny
  - dependency “age” rules (staleness)
  - allow/deny registries/sources
- `cargo policy sbom` (wrapper around existing SBOM emitters)
- `cargo policy attest` (provenance hooks; pluggable)
- Machine-readable output for CI.

# Non-goals
- Replacing every existing tool; prefer integration.
- A hosted service.

# Architecture & API sketch
- `cargo-policy` CLI
- `policy-core` (policy schema + evaluation engine)
- `adapters/` (RustSec, SBOM emitters, license scanner)

# Security / safety model
- Treat policy as code (reviewed, versioned).
- Lock down network access in CI; support offline mode.

# Maintenance & governance plan
- Keep policy schema conservative and versioned.
- Compatibility across cargo versions.

# Milestones
- 0.1: RustSec + license gating
- 0.2: SBOM generation and verification in CI
- 0.3: provenance hooks + offline-friendly mode
- 1.0: stable policy schema + docs + examples

# Sources
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- https://rustsec.org/advisories/
- https://weihanglo.tw/posts/2024/the-missing-parts-in-cargo/
