---
id: P-0184
title: SD-JWT & SD-JWT VC Interop Workbench Kit (Selective Disclosure)
status: idea
domains: [security, identity, privacy, standards, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/rfc9901/
  - https://crates.io/crates/sdjwt
  - https://crates.io/crates/ssi-sd-jwt
  - https://datatracker.ietf.org/doc/draft-ietf-oauth-selective-disclosure-jwt/22/
---

# Problem

Selective Disclosure JWTs (SD-JWT) are now standardized, but real deployments need more than “a crypto crate”:

- Ecosystems will diverge on claim formats, hashing choices, disclosure ordering, and error handling.
- Implementations need **interoperability fixtures** and **negative tests** (privacy and misuse cases).
- Developers need tooling to produce and validate artifacts without leaking private disclosures.

Rust has SD-JWT implementations, but it lacks an **interop workbench** that makes correctness and compatibility visible.

# What it should provide

## A. Profiles and canonicalization rules

Define a small set of named profiles:

- `sdjwt-basic` — simple structured SD-JWT
- `sdjwt-vc` — SD-JWT based Verifiable Credentials profile (where applicable)
- `sdjwt-privacy` — strict rules for redaction, disclosure minimization, and replay semantics

Each profile specifies:
- permitted algorithms,
- disclosure ordering/canonicalization expectations,
- claim selection and nesting rules.

## B. Conformance vectors + corpus packs

A versioned `sdjwt-corpus/` with:
- positive vectors (issuer → holder → verifier),
- negative vectors (tampered disclosures, wrong hash, wrong binding),
- “privacy tests” (ensure undisclosed fields are not reconstructible).

## C. Portable evidence bundles

`*.sdjwtbundle.zip` with:

- `report.json` (profile + pass/fail, algorithms, canonicalization mode)
- `artifacts/` (SD-JWTs, disclosures, redacted presentations)
- `trace/` (verification steps, without leaking secrets)
- `replay/` scripts to rerun verification in a clean environment

## D. `cargo sdjwt …` UX

- `cargo sdjwt issue` — produce SD-JWT from JSON + policy.
- `cargo sdjwt present` — select disclosures.
- `cargo sdjwt verify` — verify + emit report/bundle.
- `cargo sdjwt diff` — compare outputs across versions/implementations.

# MVP

- Implement `sdjwt-basic` profile conformance runner.
- Ship initial vector set derived from the RFC examples (plus independent tests).
- Bundle format v0 + redaction policy.

# v1

- Add SD-JWT VC profile corpus and interop harness across multiple Rust crates.
- Add “profile lint” to detect ambiguous or non-portable claim designs.
- Provide a small “fixture registry” format so ecosystems can share corpora.

# Design notes

- Make canonicalization choices explicit and testable.
- Keep the workbench neutral: it should *test* implementations, not anoint one.

# Why it’s epic

SD-JWT is poised to become a default privacy primitive in identity systems; a Rust workbench that makes interoperability and privacy failure modes visible would punch far above its weight.
