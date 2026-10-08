---
id: P-0145
title: Threshold Signing Service Kit — FROST-based signing flows with transcripts, policies, and test vectors
status: idea
domains: [cryptography, security, threshold, protocols, reliability]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc9591
  - https://www.rfc-editor.org/info/rfc9591
  - https://github.com/openjournals/joss-reviews/issues/10119
  - https://lantr.io/blog/frost-schnorr-threshold-signatures-bitcoin/
needs:
  - Make threshold signing operational: policies, rotations, transcripts, and incident-friendly evidence bundles.
  - Provide a practical “service kit” that teams can embed, not just a low-level protocol implementation.
  - Ensure correctness and safety via conformance vectors + replayable transcripts.
---

## What this crate should provide (to other people)

A **service-grade kit** for threshold Schnorr signing using **FROST (RFC 9591)**:
- A clear, minimal API for:
  - DKG (or pluggable key share provisioning)
  - signing sessions (commitments, nonces, partial sigs, aggregation)
  - signer set management and policy enforcement (threshold, quorum rules)
- Portable **`*.frostbundle.zip`** artifacts for:
  - incident response (“why did this signature happen?”)
  - reproducible bug reports (redacted transcripts + vector checks)
- A conformance suite:
  - RFC test vectors where possible + additional cross-impl vectors
  - transcript replay harness with minimization of failing cases

## Scope and non-goals

**In-scope**
- “Operational surface area” around FROST: policy, logs, transcripts, replay.
- Integrations that matter: storage, transport, and observability hooks.

**Out of scope**
- Replacing mature curve implementations or building a full HSM.
- Defining organizational custody processes (provide primitives + guidance).

## Design sketch

### Architecture
- **Core protocol adapter**: trait that abstracts curve/hash ciphersuite choices.
- **Session manager**: deterministic state machine with explicit timeouts and replay IDs.
- **Policy engine**
  - signer membership (who can sign)
  - rate limits / allowlists (what can be signed)
  - approval hooks (e.g., require external attestation / human-in-the-loop)
- **Transcript model** (redactable)
  - message schedule + commitments + identifiers
  - hashed payload references (avoid leaking message content)

### Artifact format: `frostbundle.zip`
- `manifest.toml` (ciphersuite, threshold, participant IDs, versions)
- `transcript.jsonl` (events, redacted)
- `vectors/` (inputs + expected outputs when applicable)
- `report.json` (verification results + failure minimization)

## MVP → v1 plan

**MVP**
- Implement session manager + transcript capture/replay
- Provide `frostbundle.zip` + verifier CLI
- One ciphersuite profile with an integration example

**v1**
- Policy hooks + pluggable storage/transports
- Cross-impl vector import/export format
- Hardening: fuzzing harness on transcript parser + session machine

## Adoption strategy

- Ship as a library with an optional “sidecar service” binary.
- Target early adopters: wallets, signing gateways, distributed key custody services.
- Make it easy to add: start with transcript-only wrapper around an existing FROST impl, then deepen.
