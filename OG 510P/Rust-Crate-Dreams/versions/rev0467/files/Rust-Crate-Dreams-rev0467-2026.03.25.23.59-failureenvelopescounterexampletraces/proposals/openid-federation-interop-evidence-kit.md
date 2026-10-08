---
id: P-0290
title: OpenID Federation 1.0 Interop & Evidence Kit — trust-chain resolution, policy diffs, and reproducible federation bundles
status: idea
domains: [identity, authn, oauth, oidc, security, testing]
last_reviewed: 2026-03-05
evidence:
  - https://openid.net/specs/openid-federation-1_0.html
  - https://openid.net/openid-federation-1-0-final-specification-approved/
  - https://crates.io/crates/openid-federation
---

## What it should provide others

A **federation-first interop and debugging toolkit** for OpenID Federation 1.0:
- Deterministic **trust-chain discovery** and resolution (entity configurations, statements, anchors).
- **Policy / metadata diffs** across environments (staging vs prod) and across time.
- Shareable **evidence bundles** for “why did registration / trust evaluation fail?”

OpenID Federation 1.0 describes how entities establish trust via a **Trust Anchor** and can form multi-level federations. The OpenID Foundation approved it as a **Final Specification** (IP protections; stable target for implementers).  

## Proposed crate/workspace shape

- `oidcfed-ir` — canonical IR for entity configs, statements, trust chains, and policy outcomes
- `oidcfed-resolve` — resolver + caching + pinning (time/exp based) with deterministic output
- `oidcfed-verify` — signature validation, metadata policy evaluation, “explain” traces
- `oidcfed-adapters` — adapter layer over existing crates (start with `openid-federation`)
- `oidcfed-cli` — `resolve`, `verify`, `diff`, `bundle`, `explain`

### Bundle format: `*.oidcfedbundle.zip`
- `manifest.json` (spec version, clock, trust anchors, resolver options)
- `inputs/` (entity configs + statements as fetched, with HTTP metadata)
- `normalized/` (canonical JSON forms; deterministic ordering)
- `chain.json` (resolved trust chain DAG + selected paths)
- `policy.json` (computed metadata policy outcomes)
- `verdict.json` + `explain.md` (first failure + human-readable reasoning)

## MVP (4–8 weeks)

1. **Canonical normalization + chain resolution** (deterministic output, stable hashes).
2. **Explain mode** for common failures:
   - signature invalid / wrong key
   - statement expired / clock skew
   - metadata policy excludes client/issuer
3. **Diff tool**: compare two bundles and show exactly which statement/policy changed.

## De-risk plan

- Start by wrapping `openid-federation` for parsing/verification; focus on **artifact format + determinism + explain**.
- Make network fetching optional; accept offline inputs for CI.

## Success metrics

- A failed federation onboarding can be reduced to a single `oidcfedbundle.zip`.
- Teams can diff “why it worked yesterday but not today” without re-running the whole environment.
