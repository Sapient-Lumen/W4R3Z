---
id: P-0249
title: SAML2 Federation Interop & XML Security Evidence Kit — metadata validation + signed/encrypted assertions with explainable failures
status: idea
domains: [interop, identity, saml, xml, security, testing]
last_reviewed: 2026-03-05
evidence:
  - https://docs.oasis-open.org/security/saml/v2.0/saml-core-2.0-os.pdf
  - https://docs.oasis-open.org/security/saml/v2.0/saml-metadata-2.0-os.pdf
  - https://www.w3.org/TR/xmldsig-core2/
  - https://www.w3.org/TR/xmlenc-core1/
  - https://crates.io/crates/samael
  - https://terminaloutcomes.github.io/saml-rs/saml_rs/
---

## What it should provide others

A practical **SAML2 “interop lab”** that turns the hard parts of SAML into:

- **validated metadata graphs**,
- **correct-by-default XML signature/encryption pipelines**,
- and **portable evidence bundles** for “why won’t this IdP/SP pair work?”

The crate should give users:

- **Metadata linter + normalizer**: parse, resolve keys/endpoints, check clock/skew, algorithm constraints, and surface actionable diagnostics.
- **Assertion toolkit**: create/verify signed assertions; decrypt/verify encrypted assertions; enforce audience/recipient/in-response-to rules.
- **Explain mode**: structured “signature failed because canonicalization X + reference Y” style outputs (not just “invalid signature”).
- **Evidence bundles**: `*.samlbundle.zip` capturing (redacted) SAML messages + metadata snapshots + a deterministic verification trace.

## Why this is still missing

Rust has some SAML crates, but enterprise SAML remains brittle because:

- XML security is subtle (canonicalization, reference selection, algorithm policy).
- Interop requires testing across vendor IdPs/SPs; debugging needs portable artifacts.
- Most libraries focus on parsing/serialization, not **federation-grade evidence + diagnostics**.

This proposal explicitly anchors to the SAML2 core + metadata specs and W3C XML Signature/Encryption processing rules.

## Design outline

### 1) “Federation graph” model

Build an internal IR:

- entities, roles (IdP/SP), endpoints, bindings
- key material + usage constraints
- validity windows + refresh rules
- signing/encryption policies (allowed algs, required transforms)

### 2) XML security engine wrapper (policy-first)

Expose high-level APIs that require:

- explicit canonicalization choice,
- explicit reference selection rules,
- algorithm allowlist,
- safe defaults (reject ambiguous transforms).

### 3) Evidence bundle (`samlbundle`)

Zip layout:

- `metadata/` (raw + normalized)
- `messages/` (AuthnRequest, Response, Logout, etc. redacted)
- `verify-trace.json` (step-by-step verification trace)
- `verdict.json` + `notes.md`

### 4) Interop harness

A runner that can:

- act as a minimal SP and/or IdP,
- replay captured flows,
- generate matrix reports per IdP/SP profile.

## Minimum lovable MVP (4–8 weeks)

1. Metadata validator/normalizer + diagnostics
2. Verify signed assertions (common profiles) + explain output
3. `samlbundle` capture for one full AuthnRequest/Response flow

## De-risk plan

- Start by producing excellent diagnostics for metadata mistakes.
- Add signature verification next (bounded surface).
- Defer full encryption support until the trace+policy model is solid.

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5
