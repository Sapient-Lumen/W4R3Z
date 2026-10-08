---
id: P-0217
title: Messaging Layer Security (MLS) Interop & Conformance Evidence Kit — vectors, transcripts, and bundle-first debugging
status: idea
domains: [crypto, security, messaging, e2ee, interop, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/rfc9420/
  - https://crates.io/crates/openmls
  - https://eprint.iacr.org/2025/229.pdf
needs:
  - A neutral, implementation-agnostic MLS conformance runner that produces shareable evidence bundles.
  - A single place to host and version-pin known-good test vectors, negative cases, and cross-impl transcripts.
  - Developer tooling to answer “where did group state diverge?” without leaking secrets.
risks:
  - High sensitivity: must make redaction the default and avoid bundling secret key material.
  - MLS is complex; must scope MVP to a narrow profile (one ciphersuite, basic proposals) and grow iteratively.
---

## Problem

Messaging Layer Security (MLS) is standardized in RFC 9420 and targets scalable group end-to-end encryption with forward secrecy and post-compromise security.
Source: https://datatracker.ietf.org/doc/rfc9420/

Rust has MLS implementations such as OpenMLS.
Source: https://crates.io/crates/openmls

But interop remains hard: failures can appear as “group state mismatch” with little explanation, and existing tests are usually *implementation-local*. The ecosystem lacks a **shared, bundle-first interop harness** that:
- runs conformance profiles against multiple implementations,
- records transcripts in a comparable way,
- and produces artifacts safe to share.

## What this crate should provide

### 1) `mls-conformance` core runner
- A profile system that pins:
  - protocol version + extensions
  - ciphersuite(s)
  - credential/identity mode
  - supported proposals and policy knobs
- Scenario DSL:
  - create group, add/remove, update, commit, application messages
  - out-of-order delivery and async joins

### 2) Evidence bundles: `*.mlsbundle.zip`
Redaction-first, secret-free by default:
- `profile.json`
- `scenario.json`
- `impls.json` (versions, features)
- `transcript.json`:
  - message sequence (MLS wire bytes optionally hashed)
  - group epoch timeline
  - commit metadata (proposal types, sizes)
- `state-hashes.json`:
  - hashes of key schedule inputs/outputs *without* keys
  - tree hash / transcript hash checkpoints
- `diff/report.md` + `diff/report.json`

### 3) Vector & fixture packs
- Versioned packs aligned to RFC 9420 sections:
  - encoding/decoding vectors
  - negative vectors (malformed, policy violations)
  - interop transcripts harvested from runs (bundle format)

### 4) Implementation adapters
- Rust-native adapter traits:
  - `Impl::process(msg) -> events`
  - `Impl::export_public_state() -> digest set`
- CLI adapter for non-Rust implementations (stdin/stdout protocol with CBOR)

### 5) Differential diagnostics
- “First divergence finder”:
  - compare state-hash checkpoints and binary search the message index
- “Explain” layer for common divergence classes:
  - proposal ordering
  - signature context differences
  - extension mismatch

## Prior art & why this is still missing

- MLS is standardized (RFC 9420) but the day-to-day dev experience for conformance and interop still lacks shareable evidence.
  Source: https://datatracker.ietf.org/doc/rfc9420/
- OpenMLS and others exist; we need a runner that is *implementation-neutral* and produces redaction-safe artifacts.
  Source: https://crates.io/crates/openmls

## MVP plan (4–8 weeks)

1. Define bundle + transcript format, focusing on secret-free state hashes.
2. Implement one Rust adapter (OpenMLS) + one stub CLI adapter.
3. Ship 10 scenarios:
   - group creation, add/remove, update, commit, basic app messages
4. `cargo mls-lab run` and `cargo mls-lab diff`.

## v1 plan (8–12 weeks)

- Expand profiles (multiple ciphersuites), add out-of-order & retry scenarios.
- Add fuzz/minimization hooks for message sequences.
- Add security review notes and explicit leakage analysis.

## Scorecard (0–5)
- Impact: 4
- Neglectedness: 3
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (secret-free divergence bundles + interop runner)
