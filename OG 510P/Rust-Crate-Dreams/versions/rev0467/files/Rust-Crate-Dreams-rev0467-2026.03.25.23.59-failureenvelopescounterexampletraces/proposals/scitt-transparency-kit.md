---
id: P-0247
title: SCITT Transparency & Receipts Kit — interoperable statement submission + receipt verification + scittbundles
status: idea
domains: [supply-chain, transparency, security]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/draft-ietf-scitt-architecture-22
  - https://datatracker.ietf.org/doc/draft-ietf-scitt-scrapi/
  - https://datatracker.ietf.org/group/scitt/about/
  - https://scitt.io/scitt-specs.html
---

## What it should provide others

A **practical Rust kit** for building and consuming SCITT-style transparency services:
- create/submit signed statements,
- verify receipts/proofs,
- query and audit logs,
- and share the whole story as a portable `*.scittbundle.zip`.

This is the missing middle between “I can sign an SBOM” and “I can operate a transparency workflow that auditors and downstreams can replay.”

## Scope and design

### 1) Statement and receipt APIs
- Statement builder:
  - envelopes for signed “claims” (payload-agnostic)
  - stable content addressing (hashing + canonicalization)
- Receipt verifier:
  - chain/proof verification
  - “why trusted?” explain output (keys, endorsements, policies)

### 2) SCITT reference API client
Implement the draft SCITT “reference APIs” surface so Rust clients can:
- submit statements
- fetch receipts
- perform key discovery
- query by artifact references

### 3) Evidence bundles
Define `*.scittbundle.zip`:
- `statements/` (canonicalized payloads)
- `receipts/` (proofs)
- `keys/` (discovered/pinned keys + provenance)
- `queries/` (what queries were run)
- `audit/` (local verification results + reasons)
- `pins/` (draft versions + profiles)

## MVP (6–8 weeks)

1. Canonical statement hashing + receipt verification skeleton
2. Minimal SCRAPI client (submit + get receipt)
3. `scittbundle` format + deterministic pack/unpack
4. “Explain” output for verification failures

## Non-goals

- Building a full transparency service (that’s its own project).
- Defining a new supply-chain format; payloads can be SPDX/CycloneDX/SLSA/etc.
