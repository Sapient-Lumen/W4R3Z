---
id: P-0142
title: HPKE Envelope & Interop Kit — high-level hybrid encryption with test vectors and safe defaults
status: idea
domains: [crypto, security, interoperability, envelopes, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc9180
  - https://crates.io/crates/hpke
  - https://blog.cloudflare.com/hybrid-public-key-encryption/
  - https://github.com/thibmeu/age-plugin-hpke
needs:
  - Make modern hybrid public-key encryption usable safely without bespoke protocol design.
  - Provide interop test vectors, transcript fixtures, and policy knobs for real deployments.
  - Bridge standards (HPKE) into practical workflows (files, envelopes, services, key rotation).
risks:
  - Cryptographic API footguns; must constrain choices and provide “profiles”.
  - Backwards compatibility as primitives evolve; must version and pin.
  - Audit expectations and liability; should clearly scope “not audited” until it is.
---

## Problem

HPKE (RFC 9180) standardizes hybrid public key encryption for arbitrary-sized plaintexts and is used by emerging Internet standards (e.g., ECH, ODoH).  
Source: https://datatracker.ietf.org/doc/html/rfc9180

Rust has an `hpke` crate claiming RFC 9180 compliance, but developers still have to assemble envelopes, metadata policies, key discovery/rotation, and interop fixtures.  
Source: https://crates.io/crates/hpke

We also see “applicationization” pressure: e.g., an **age plugin** using HPKE to consume HPKE-encrypted files, highlighting that developers want end-user workflows, not just primitives.  
Source: https://github.com/thibmeu/age-plugin-hpke

## What this crate should provide

A **high-level envelope** and **interop harness** on top of HPKE primitives:

1. **Profiles (“boring mode”)**
   - `Base` profile: fixed suite choices (KEM/KDF/AEAD), strict metadata rules
   - `PSK` and `Auth` variants where appropriate
   - Explicit “safe default” recipient info / info fields

2. **Envelope format**
   - A stable `*.hpkeenv` binary format (or JSON + base64 variant) with:
     - suite id, encapsulated key, ciphertext, associated data, optional recipient hints
   - A `hpkeenv.schema.json` and versioning rules.

3. **CLI + cargo integration**
   - `cargo hpke {seal,open,doctor,vectors}`
   - `doctor` validates profiles, verifies metadata constraints, and checks interop settings.

4. **Interop and test vectors**
   - A curated set of **known-good vectors** for each profile:
     - inputs, outputs, transcript JSON
   - `*.hpkebundle.zip` bug reports:
     - envelope, profile, transcript, and redacted metadata.

5. **Key management adapters (optional)**
   - age recipients (as a practical integration path)
   - KMS/HSM hooks (interface only at first; no vendor lock-in)

## Users & user stories

- **Infra engineer**: “Encrypt small config blobs to a service identity with rotation and audit-friendly transcripts.”
- **Tooling author**: “Add a standards-based envelope to my CLI without designing crypto.”
- **Security reviewer**: “Verify the profile choices, vectors, and metadata rules are consistent.”

## Prior art (and why it’s insufficient)

- **RFC 9180** defines the scheme but not a concrete app envelope or operational profile.  
  Source: https://datatracker.ietf.org/doc/html/rfc9180
- **Rust `hpke` crate** provides primitives/compliance, not the “envelope + interop + workflow” layer.  
  Source: https://crates.io/crates/hpke
- **Cloudflare overview** emphasizes reuse/future-proofing and broad standards usage, reinforcing that developers want interoperable implementations.  
  Source: https://blog.cloudflare.com/hybrid-public-key-encryption/
- **age-plugin-hpke** shows real workflow demand.  
  Source: https://github.com/thibmeu/age-plugin-hpke

## MVP plan (2–3 weeks)

- Define envelope format v0 (binary) + schema doc.
- Implement `seal/open` for the Base profile using `hpke` crate.
- Publish vector generator + verifier; ship 10–20 vectors.
- Implement `doctor` checks for envelope version, suite id, and transcript verification.

## v1 plan (6–10 weeks)

- Add `PSK` and `Auth` profiles.
- Add deterministic redaction for metadata in bug bundles.
- Add adapters:
  - age recipients (interop)
  - optional KMS key-discovery interface (trait + reference impl stub)

## Conformance & testing

- Property tests: roundtrip under randomized inputs and metadata.
- Cross-impl interop: allow importing external vectors (format converters).
- Fuzz: envelope parser + transcript validator.

## Adoption strategy

- Keep the API small and “profile-first”.
- Provide security posture docs and a roadmap to an audit once stable.
