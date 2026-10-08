---
id: P-0193
title: Verifiable Credentials v2 Interop Workbench Kit
status: idea
domains: [security, identity, interop, privacy, compliance]
last_reviewed: 2026-03-05
evidence:
  - https://www.w3.org/TR/vc-data-model-2.0/
  - https://www.w3.org/news/2025/the-verifiable-credentials-2-0-family-of-specifications-is-now-a-w3c-recommendation/
  - https://w3c.github.io/vc-data-model-2.0-test-suite/
---

# P-0193 — Verifiable Credentials v2 Interop Workbench Kit

## Problem / why now

The W3C **Verifiable Credentials Data Model v2.0** is now a Recommendation, and the VC 2.0 family explicitly aims to pair the data model with widely adopted securing mechanisms (JOSE/COSE, selective disclosure, etc.). citeturn0search3turn0search15

In practice, implementers still struggle with:
- fragmented profiles (“which suites and encodings are allowed?”),
- underspecified interoperability edges,
- and painful debugging when a verifier rejects a credential.

The W3C ecosystem also maintains a **VC v2.0 interoperability report suite**, which is exactly the kind of “truthy” conformance input Rust tooling should learn from. citeturn0search23

## What this crate/tooling should provide other people

A pragmatic workbench that makes VC integration boring:

1. **Profiles as code**
   - A profile format that constrains:
     - allowed VC fields/extensions
     - allowed securing methods (JOSE/COSE families)
     - clock skew, audience rules, key binding expectations
   - Output: `vc-profile.json`

2. **Verification pipeline with explainability**
   - A verifier that can emit:
     - structured failure reasons
     - “explain traces” showing which rule failed
   - Deterministic formatting for CI diffs.

3. **Interop runner**
   - Run (or import) W3C interop vectors and local corpora:
     - “known-good”
     - “privacy-negative” (leakage tests)
     - “malleability” cases
   - Produce `interop-report.json`.

4. **Incident bundles (`vcbundle.zip`)**
   - Shareable, redacted bug reports:
     - credential/presentation (optionally encrypted at rest)
     - verification config/profile
     - key material references (not raw private keys)
     - verifier traces and normalization outputs

5. **Adapters**
   - Provide a narrow adapter surface so different crypto backends can plug in.

## Artifact format: `vcbundle.zip`

- `manifest.json` (versions, profile id, timestamp normalization)
- `inputs/` (credential/presentation with redaction map)
- `profile/` (profile JSON + resolved defaults)
- `keys/` (public keys, DID docs, metadata; no private keys)
- `trace/` (stepwise verification trace)
- `report.json` (final verdict + reasons)

## MVP → v1 plan

### MVP
- Profile schema + verifier skeleton with structured reasons.
- Corpus runner with a small curated set + import hooks for official interop vectors.
- Bundle writer.

### v1
- Full interop harness integration against the VC v2.0 test suite inputs.
- Differential testing across multiple crypto backends.
- Tooling: `cargo vc doctor` and `cargo vc verify --explain`.

## Evidence / references

- VC Data Model v2.0 Recommendation and its ecosystem framing. citeturn0search3turn0search15
- VC v2.0 interoperability report suite exists and should be treated as a conformance anchor. citeturn0search23
