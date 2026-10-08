---
id: P-0179
title: Content Authenticity (C2PA) ShipKit
status: idea
domains: [security, media, provenance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html
  - https://crates.io/crates/c2pa
  - https://opensource.contentauthenticity.org/docs/rust-sdk/docs/usage/
---

# Problem

Rust is increasingly used for media tooling, moderation pipelines, and AI/ML asset processing, but “content credentials” support is still hard to deploy end‑to‑end: you need signing keys, claim construction, embedding/extraction across formats, redaction rules, and reproducible verification artifacts. Teams end up with bespoke glue code and no shared conformance corpus.

C2PA defines a standard for provenance and authenticity of media content via signed manifests (“Content Credentials”), but ecosystem adoption needs practical deployment workflows and testable interoperability.

# What it provides

- A stable **artifact format**: `c2pabundle.zip`
  - `input/` (redacted sample or hash-only placeholder)
  - `manifest.json` (canonicalized claim/ingredients)
  - `embed_report.json` (where/how embedded)
  - `verify_report.json` (all checks, warnings, chain status)
  - `keys/` (public cert chain; private keys never required)
- A **crate** (`c2pa-shipkit`) that wraps existing C2PA primitives into opinionated workflows:
  - build claims (ingredients, assertions, thumbnails) and sign
  - embed/extract for common media types via feature-gated adapters
  - verification profiles (strict, lenient, “moderation”, “forensics”)
  - deterministic “canonicalization” helpers to make diffs meaningful
- A **CLI**: `cargo c2pa {sign,verify,extract,bundle,doctor}`
- A **conformance pack**: curated fixtures + “expected verify outcomes” (good, degraded, broken-chain, tampered, unsupported-assertion)

# Users & user stories

- Media pipeline engineer: “Given a JPEG, sign a claim, embed it, and produce a bundle that a reviewer can verify offline.”
- Trust & safety: “Verify at ingestion and attach `verify_report.json` to internal evidence; fail closed under strict profile.”
- ML researcher: “Attach provenance to model artifacts/datasets; prove derivations by ingredient chains.”

# Prior art (and why it’s insufficient)

- `c2pa` crate implements portions of the spec, but does not standardize deployment artifacts, corpora, or CI-oriented diffs.
- CAI documentation explains usage and supported platforms, but leaves operational patterns (key mgmt, bundle redaction, policy) to each org.

# Design goals

- Make C2PA workflows **boringly reproducible** (bundle-first).
- Provide **policy hooks** (what assertions allowed; ingredient depth; hash-only mode).
- Keep adapters optional (features) and avoid locking users into one media stack.

# Non-goals

- Defining new provenance standards (this is a ShipKit around C2PA).
- Managing private keys (integrate with HSM/KMS; accept signing callbacks).

# Architecture & API sketch

- `Builder` → `Claim` → `Signer` → `Embedder`
- `Verifier` with `Profile` and `Policy`:
  - `verify(input, profile) -> VerifyReport`
- `Bundle` module:
  - `Bundle::from_signing(...)`
  - `Bundle::from_verification(...)`

# Security / safety model

- No private keys in bundles; support sign via external callback (KMS/HSM).
- Redaction modes:
  - full media
  - cropped media
  - hashes only (ingredient hashes + manifest)
- Verification report separates “cryptographic validity” vs “policy compliance”.

# Maintenance & governance plan

- Start as a thin layer around `c2pa` (and adapters), with fixtures and CI.
- Explicit semver for bundle schema; add forward-compatible fields only.

# Milestones

- MVP: `verify` + bundle schema + corpus + `cargo c2pa bundle`.
- v1: `sign` workflow, embed/extract adapters, policy profiles, `doctor`.
- v2: interop runner (matrix against other SDKs), richer assertion plugins.

# Open questions

- Best default canonicalization strategy for claim JSON to maximize diff stability?
- Which media formats get “core” support vs “adapter” support?

# Sources

- C2PA Technical Specification.
- `c2pa` crate / CAI Rust SDK docs (platform support and usage).
