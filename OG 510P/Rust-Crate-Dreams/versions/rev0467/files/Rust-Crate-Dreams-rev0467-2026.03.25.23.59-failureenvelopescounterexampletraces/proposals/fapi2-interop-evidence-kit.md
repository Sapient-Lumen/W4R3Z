---
id: P-0280
title: FAPI 2.0 / OAuth High-Security Profile Interop & Evidence Kit — conformance packs, explainable policy checks, and replayable auth traces
status: idea
domains: [identity, security, oauth, openid, interoperability, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://openid.net/specs/fapi-security-profile-2_0-final.html
  - https://openid.net/wg/fapi/specifications/
  - https://www.rfc-editor.org/rfc/rfc9449.html
  - https://www.rfc-editor.org/rfc/rfc8725.html
  - https://crates.io/crates/openidconnect
  - https://crates.io/crates/oauth2
---
## What it should provide others

A **portable, replayable, explainable** workflow for implementing and testing *high-security* OAuth/OpenID deployments (FAPI‑style), especially when real deployments require a **tight, auditable profile** (DPoP / sender-constrained tokens, hardened redirect handling, strict client auth, etc.).

The gap is not “another OAuth client/server crate”; it’s:
- **profile-as-code**: a machine-checkable policy layer describing *what this deployment claims to implement*
- **conformance packs**: scenario suites that produce **evidence bundles** for CI and audits
- **semantic diffs**: compare two deployments’ behavior and pinpoint the first divergence

## Why now (ecosystem gap)

Rust has strong building blocks (`oauth2`, `openidconnect`), but teams still reinvent:
- consistent security defaults (BCP-aligned) and profile checklists
- test harnesses that verify the *whole* flow, not just token parsing
- reproducible bug reports (“issuer A works, issuer B fails”) that don’t leak secrets

FAPI 2.0 is explicitly intended for high-value data scenarios and emphasizes interoperable security mechanisms across client↔AS and client↔RS interfaces — which is exactly where bundle-first evidence pays off.

## Proposed crate shape (workspace)

- `fapikit-policy` — typed policy model (profile requirements, optional features, key constraints)
- `fapikit-scenarios` — scenario DSL (auth code + PKCE + PAR, DPoP, refresh rotation, etc.)
- `fapikit-capture` — adapters to log/capture:
  - HTTP (request/response) with deterministic redaction
  - JOSE objects (JWS/JWE/JWK) as structured events
- `fapikit-verify` — rules engine that produces **explainable** pass/fail with citations to policy clauses
- `fapikit-diff` — semantic diff between runs (what changed, where divergence begins)
- `fapikit-bundle` — `*.fapibundle.zip` IO (schema, signing hooks, optional DSSE)
- `cargo-fapikit` — CLI for CI + local repro

### Bundle contract (high-level)

A `*.fapibundle.zip` should contain:
- `policy.yaml` (declared profile + knobs)
- `run-metadata.json` (versions, clocks, environment fingerprints)
- `events.ndjson` (canonical event stream: redirects, token requests, proofs, validation decisions)
- `redaction.json` (what was removed, why, and how to reproduce locally)
- `verdict.json` + `explain.md` (rule outcomes and “why”)

## Minimum lovable MVP (4–8 weeks)

1. `fapikit-bundle` schema + deterministic redaction primitives for HTTP + JWT/DPoP proof objects
2. `fapikit-verify` with a small but high-value ruleset:
   - DPoP proof validation and replay protection signals
   - JWT BCP checks (alg, typ, critical headers policy hooks)
3. `cargo-fapikit run` against a stub AS/RS + a real OIDC provider (where possible) producing diffable bundles

Deliverable: a CI job that outputs a `results.fapibundle.zip` artifact and a human-readable “why failed” report.

## De-risk plan

- Start as a **harness + evidence layer** that consumes existing OAuth/OIDC crates, not a new protocol implementation.
- Begin with a “**profile subset**” that is broadly useful even outside financial APIs (DPoP/JWT BCP + hardened redirect/issuer handling).
- Provide adapters for popular Rust web frameworks later; keep core runtime-agnostic.

## Scorecard (0–5)

- Impact: 5
- Neglectedness: 4
- Feasibility: 3
- Adoptability: 4
- Sustainability: 3
- Differentiation: 5 (profile-as-code + evidence bundles + semantic diff)
