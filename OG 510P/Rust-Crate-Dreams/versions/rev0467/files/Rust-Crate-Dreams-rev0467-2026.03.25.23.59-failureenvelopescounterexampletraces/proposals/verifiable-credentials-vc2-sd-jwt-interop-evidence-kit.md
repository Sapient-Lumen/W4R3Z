---
id: P-0219
title: Verifiable Credentials 2.0 + SD-JWT VC Interop & Evidence Kit — profiles, validators, test vectors, and reproducible bundles
status: idea
domains: [identity, vc, ssi, crypto, interop, conformance, privacy]
last_reviewed: 2026-03-05
evidence:
  - https://www.w3.org/TR/vc-data-model-2.0/
  - https://www.w3.org/news/2025/the-verifiable-credentials-2-0-family-of-specifications-is-now-a-w3c-recommendation/
  - https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-10.html
  - https://docs.rs/identity_credential
  - https://github.com/spruceid/ssi
needs:
  - A pragmatic, Rust-first path to **interop-grade** VC issuance/verification across real formats (JWT VC, SD-JWT VC, data-model constraints, proof suites), without forcing every project to become an identity platform.
  - Shared corpora and golden vectors for validators, plus explainable errors and privacy-safe diagnostic bundles.
  - “Profile” primitives: most apps need a constrained VC subset (claims, algorithms, disclosure rules), not the whole universe.
risks:
  - The VC ecosystem is fragmented across proof formats, DID methods, key representations, and issuer policies.
  - Privacy hazards: bundles must default to redaction and support “secret-free” debugging.
---

## Problem

W3C Verifiable Credentials Data Model v2.0 is a Recommendation (May 15, 2025) and provides a mechanism for expressing machine-verifiable credentials.
Source: https://www.w3.org/TR/vc-data-model-2.0/
Source: https://www.w3.org/news/2025/the-verifiable-credentials-2-0-family-of-specifications-is-now-a-w3c-recommendation/

In practice, implementers need **tight profiles** (what algorithms, what claim shapes, what presentation rules) and **interop evidence** more than abstract flexibility.

SD-JWT-based Verifiable Credentials (SD-JWT VC) is being standardized in the IETF OAuth working group, defining formats and processing rules for selective disclosure.
Source: https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-10.html

Rust has building blocks (e.g., VC type crates and SSI libraries), but lacks a cohesive “interop kit” that makes it straightforward to:
- define profiles,
- validate with clear diagnostics,
- run conformance suites,
- and exchange reproducible failure artifacts.
Source: https://docs.rs/identity_credential
Source: https://github.com/spruceid/ssi

## What this crate should provide

### 1) Profile system (the core value)
- `VcProfile` describing:
  - allowed proof formats (JWT VC, SD-JWT VC; extensible)
  - allowed algorithms, key types, curves
  - claim schema constraints (JSON Schema-lite, or strongly-typed constraints)
  - clock skew, audience rules, status list rules (if used)
  - disclosure policy for SD-JWT VC
- “Profile manifests” as portable JSON/YAML.

### 2) Validators with *explainable* outcomes
- `validate_credential(profile, credential)` → structured report:
  - pass/fail
  - violations with pointers to spec/profile rule
  - severity levels (error/warn/info)
  - “suggested fix” hints

### 3) Vector suites + corpus management
- A standard fixture layout:
  - `vectors/<profile>/<case>/input.json`
  - `expected/report.json`
  - optional: `keys/` with *public* material only
- Runner that can:
  - execute local validation
  - execute external validators via adapter interface (to compare results)

### 4) Evidence bundles: `*.vcbundle.zip`
Default redaction-first:
- `profile.json`
- `credential.redacted.json` (or hashed selectively disclosed parts)
- `presentation.redacted.json` (if applicable)
- `verification/report.json` + `report.md`
- `env.json` (library versions, time, platform)
- optional: `raw/` (encrypted with recipient keys) for private sharing

### 5) Interop adapters (don’t reinvent everything)
- Adapter traits to integrate existing ecosystems:
  - DID resolver adapters (optional)
  - JOSE/JWT adapters
  - signature suite adapters
- Provide at least one “reference path” based on existing Rust libraries (behind feature flags).

## Crate design (workspace layout)

- `vc-profile` — profile types + manifest parsing
- `vc-validate` — validators + explain reports
- `vc-vectors` — corpus loader + runner
- `vc-bundle` — redactable bundle format + encryption hooks
- `cargo-vc-lab` — CLI: run vectors, validate, diff results

## Minimum lovable MVP (4–8 weeks)

1. VC Data Model v2.0 structural validation (required fields, context rules as profiled) + JWT VC validation.
   Source: https://www.w3.org/TR/vc-data-model-2.0/
2. SD-JWT VC parser + selective disclosure validation (profiled subset).
   Source: https://www.ietf.org/archive/id/draft-ietf-oauth-sd-jwt-vc-10.html
3. Vector runner + `*.vcbundle.zip` emission on failures.

## De-risk plan

- Pick 2–3 practical profiles (e.g., “employee badge”, “age over 18”, “course certificate”).
- Make privacy the default: redaction policy must be mandatory unless explicitly disabled.
- Add an “interop matrix” command that compares results between at least two validator backends (one internal, one adapter).

## Scorecard (0–5)

- Impact: 4
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5

## Prior art (and why it’s insufficient)

- VC libraries exist, but apps still need the missing layer: **profiles + conformance corpora + reproducible diagnostics**.
  Source: https://docs.rs/identity_credential
  Source: https://github.com/spruceid/ssi
