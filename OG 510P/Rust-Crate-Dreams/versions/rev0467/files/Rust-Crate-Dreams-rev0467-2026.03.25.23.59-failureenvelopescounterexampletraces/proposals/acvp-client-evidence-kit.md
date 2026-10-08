---
id: P-0246
title: ACVP Client & Evidence Kit — spec-faithful ACVP sessions + vector processing + shareable acvpbundles
status: idea
domains: [crypto, compliance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://pages.nist.gov/ACVP/
  - https://pages.nist.gov/ACVP/draft-fussell-acvp-spec.html
  - https://github.com/usnistgov/ACVP
  - https://github.com/cisco/libacvp
  - https://crates.io/crates/acvp-parser
---

## What it should provide others

A **Rust-first, spec-faithful ACVP client toolkit** that makes algorithm validation flows:
- repeatable in CI,
- shareable as evidence,
- adaptable to multiple crypto backends (RustCrypto, ring, hardware modules),
while staying aligned with NIST’s evolving ACVP spec and JSON method documents.

## Scope and design

### 1) Core ACVP session engine
- Registration/capabilities negotiation
- Authentication and session lifecycle
- Vector set retrieval + response submission
- Robust retry/backoff + resumable sessions
- “Strict mode” (spec compliance) vs “interop mode” (server quirks)

### 2) Backend adapter API
A trait-based “algorithm runner” layer:
- Pure Rust backends (RustCrypto, etc.)
- FFI backends (OpenSSL, vendor modules)
- Hardware-backed backends (PKCS#11/HSM paths)

### 3) Evidence bundles
Define `*.acvpbundle.zip`:
- `capabilities.json` (submitted)
- `vectors/` (server prompts, normalized)
- `responses/` (submitted, normalized)
- `transcripts/` (HTTP request/response metadata, redacted)
- `verdicts/` (server results + local checksums)
- `pins/` (spec version, JSON method doc versions, tool versions)

## MVP (8–10 weeks)

1. Minimal ACVP session runner for 1–2 algorithms (e.g., AES-GCM + SHA-256)
2. `acvpbundle` pack/unpack + deterministic canonicalization
3. Adapter for a reference backend (RustCrypto) + golden tests
4. Error taxonomy + diagnostics (why a vector failed)

## De-risking

- Start with “offline bundle replay”: you can run vectors locally without live server access.
- Keep server integration behind a small HTTP layer to swap endpoints and handle quirks.

## Non-goals

- Running certification logistics.
- Replacing NIST servers or vendor-specific tooling; this is the client + evidence layer.
