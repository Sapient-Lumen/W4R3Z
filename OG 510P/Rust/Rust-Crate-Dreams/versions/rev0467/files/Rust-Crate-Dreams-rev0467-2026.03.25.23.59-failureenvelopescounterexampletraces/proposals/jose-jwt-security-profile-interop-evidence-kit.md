---
id: P-0252
title: JOSE/JWT Security Profile & Interop Evidence Kit — canonical JOSE IR, policy explainers, and vector bundles
status: idea
domains: [security, identity, crypto, interop, conformance, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://www.rfc-editor.org/rfc/rfc8725.html
  - https://www.rfc-editor.org/rfc/rfc7515.html
  - https://www.rfc-editor.org/rfc/rfc7516.html
  - https://www.rfc-editor.org/rfc/rfc7519.html
---
## Why this is missing
Rust has multiple JWT/JWS/JWE crates, but teams still repeatedly re-invent:
- which algorithms/headers are acceptable,
- how to avoid common JWT pitfalls,
- how to capture a *replayable* failing token verification case without leaking secrets.

RFC 8725 (JWT Best Current Practices) exists, but there is no **standardized evidence bundle** and no shared, explainable “policy engine” for Rust JWT usage. (See evidence link.)

## What the crate provides
A set of crates that produce **`*.josebundle.zip`** artifacts and can run a **policy-backed interop suite** across libraries.

### Core crates/modules
- `jose-ir`: a canonical intermediate representation for JWS/JWE/JWT (headers/claims normalized by explicit rules).
- `policy`: a declarative policy language (“allow algs… require aud… forbid crit unless…”) plus an “explain” trace.
- `vectors`: tooling to import/export JSON test vectors and attach provenance (where they came from).
- `josebundle`: redaction-safe evidence bundles with:
  - token + decoded structure,
  - key material *references* (never private keys),
  - verification parameters and expected outcomes,
  - an explain trace (“failed because alg none”, “kid mismatch”, “aud missing”, etc.)

### Bundle format sketch
`josebundle/`
- `policy.json` (declarative policy + schema version)
- `inputs/token.txt` (or detached JWS parts)
- `inputs/context.json` (iss/aud/nonce/time)
- `keys/` (public JWKs, x5c chains; private keys omitted)
- `trace.jsonl` (explain events)
- `verdict.json` (pass/fail + reason codes)

## MVP plan (4–6 weeks)
1. `policy` + `explain` trace for the top ~15 JWT pitfalls from RFC 8725 (algorithm restrictions, audience/issuer checks, clock skew, etc.).
2. `josebundle` pack/unpack + redaction profiles.
3. `jose-ir` canonicalization + stable diff rendering.
4. Adapter for 1–2 existing Rust JWT crates to run vectors + generate bundles.

## De-risking
- Scope it as **interop/policy/evidence**; do not implement new crypto primitives.
- Keep policy “small but sharp”: opinionated defaults + escape hatches.

## What users get
- A reusable, explainable “JWT policy engine” and evidence bundle that makes security reviews and debugging tractable.
