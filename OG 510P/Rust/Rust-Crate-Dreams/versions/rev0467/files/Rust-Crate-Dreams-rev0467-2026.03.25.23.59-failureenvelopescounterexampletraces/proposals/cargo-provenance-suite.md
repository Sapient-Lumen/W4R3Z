---
id: P-0075
title: Cargo Provenance Suite — one-stop SBOM + SLSA provenance + Sigstore verification for Rust artifacts
status: idea
domains: [cargo, supply-chain, security, sbom, provenance]
last_reviewed: 2026-03-04
evidence:
  - https://mozilla.github.io/cargo-vet/
  - https://slsa.dev/spec/v1.1/faq
  - https://crates.io/crates/sigstore-verification
  - https://edu.chainguard.dev/open-source/sigstore/cosign/how-to-sign-an-sbom-with-cosign/
needs:
  - Make “ship Rust safely” a mostly-mechanical path for teams.
  - Reduce glue work across SBOM, provenance, verification, and policy gates.
risks:
  - Too much scope (needs a narrow, composable core).
  - Standards churn and CI integration variance.
---

## Problem

Rust teams increasingly need supply-chain evidence: dependency audits, SBOMs, provenance, and artifact signature verification. The pieces exist but are stitched together ad-hoc:

- `cargo vet` helps ensure third-party dependencies have been audited by trusted entities.  
  Source: https://mozilla.github.io/cargo-vet/
- SLSA provenance focuses on build trust and notes provenance can be coarse-grained/best-effort for dependencies.  
  Source: https://slsa.dev/spec/v1.1/faq
- Rust libraries exist for Sigstore verification (e.g., `sigstore-verification`).  
  Source: https://crates.io/crates/sigstore-verification
- Cosign attestations commonly attach SBOMs or SLSA provenance to artifacts.  
  Source: https://edu.chainguard.dev/open-source/sigstore/cosign/how-to-sign-an-sbom-with-cosign/

What’s missing: a coherent suite that produces **evidence bundles** and verifies them with **policy gates**.

## Design goals

- Composable core + thin CLIs, not a monolith.
- Policy-first verification (`policy.toml` allow/deny rules, justified exceptions).
- Standard “bundle manifest” format referencing digests + attestations + audit summaries.

## Crates

- `cargo_provenance_core` — types + manifest schema
- `cargo-provenance` — `sbom|attest|verify|bundle`
- `cargo_provenance_policy` — policy evaluation
- `cargo_provenance_adapters` — adapters to cargo-vet + Sigstore verification

## Milestones

- 0.1: bundle manifest schema + verify engine + bundle output
- 0.2: integrate cargo-vet summaries + Sigstore verification adapter
- 0.3: SBOM generation adapter + signing workflow docs
- 1.0: stable schemas + conformance suite

## Sources

- https://mozilla.github.io/cargo-vet/
- https://slsa.dev/spec/v1.1/faq
- https://crates.io/crates/sigstore-verification
- https://edu.chainguard.dev/open-source/sigstore/cosign/how-to-sign-an-sbom-with-cosign/
