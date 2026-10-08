---
id: P-0205
title: Sigstore + in-toto + SLSA Provenance Kit (artifact attestations, bundles, policy, Cargo integration)
status: idea
domains: [supply-chain, security, interoperability, tooling, provenance, policy]
last_reviewed: 2026-03-05
evidence:
  - https://docs.sigstore.dev/about/bundle/
  - https://docs.sigstore.dev/cosign/signing/overview/
  - https://github.com/sigstore/sigstore-rs
  - https://slsa.dev/spec/v1.0/provenance
  - https://github.com/in-toto/attestation
  - https://crates.io/crates/in_toto_attestation
---

# Problem

Rust has *verification* building blocks for Sigstore, and protobuf bindings for in-toto attestations, but there is still no obvious, ergonomic, well-scoped library that:
- helps projects **produce** attestations (SLSA provenance + custom predicates),
- packages them into **portable bundles** for offline verification,
- verifies them against **declarative policy**,
- and integrates cleanly with the way Rust actually ships artifacts (crates, binaries, container images, SBOMs).

Teams repeatedly invent ad-hoc JSON formats, fragile CI glue, or rely on CLI-only workflows that are hard to embed in Rust services.

# What the crate provides (for other people)

## 1) Opinionated “attestation plumbing” with escape hatches
- `AttestationBuilder` with:
  - SLSA provenance predicate helpers,
  - in-toto Statement/Envelope helpers,
  - pluggable predicate serialization.
- `BundleWriter` / `BundleReader` for Sigstore bundles.

## 2) Policy-first verification
- Minimal policy language (start small): “identity must match”, “repository must match”, “builder must be X”, “buildType must be Y”, “materials must include…”.
- Optional adapters to existing policy engines (Rego/CUE) but keep the crate usable without them.

## 3) Cargo integration primitives (library-level)
- Helpers to attach provenance/bundles to:
  - `.crate` publishing pipelines,
  - `cargo-dist`/release artifacts,
  - OCI images (as attestations/referrers), when used.

## 4) Evidence bundles for debugging
- `*.sigbundle.zip` capturing:
  - signature bundle(s),
  - provenance statements,
  - policy + evaluation trace,
  - redaction metadata for logs/identities (where needed).

# Architecture sketch

- `provenance-kit-core`: in-toto + SLSA data model helpers; canonical JSON; hashing.
- `provenance-kit-sigstore`: bundle IO + signing/verification adapters.
- `provenance-kit-policy`: policy structs + evaluator + explanation output.
- `provenance-kit-cargo`: helper APIs + reference CLI (optional) demonstrating integration.

# MVP (4–8 weeks)

1. Parse/emit SLSA provenance and in-toto Statement helpers.
2. Read Sigstore bundle format, verify identities/certs and signatures (via existing sigstore crates).
3. Tiny policy language + explain output.
4. Produce a `sigbundle.zip` report for CI.

# De-risking plan

- Start with verification + policy + explain (no signing) to reduce key material surface area.
- Add signing only after the verification path is stable and tested.
- Provide a compatibility matrix for popular flows (GitHub Actions OIDC, Rekor inclusion proofs).

# Relationship to existing proposals

- Complements (not replaces) cargo provenance work by focusing on **portable bundles + policy + explainability** across artifact types.

