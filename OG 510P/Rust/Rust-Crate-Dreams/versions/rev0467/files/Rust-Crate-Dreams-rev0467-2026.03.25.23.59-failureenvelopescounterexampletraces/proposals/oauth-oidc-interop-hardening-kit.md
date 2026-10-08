---
id: P-0182
title: OAuth/OIDC Interop & Hardening Kit (PAR + DPoP + Profiles)
status: idea
domains: [security, identity, web, tooling, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc9126
  - https://www.rfc-editor.org/rfc/rfc9449.html
  - https://crates.io/crates/openidconnect
  - https://crates.io/crates/oauth2-test-server
---

# Problem

Rust has strong OAuth2 / OpenID Connect client libraries, but **production-grade interoperability** still costs a lot of bespoke work:

- Optional extensions (e.g., **PAR**, DPoP) shift security posture and failure modes.
- Providers differ on strictness, edge cases, and error semantics.
- Debugging is painful because requests are sensitive and often non-reproducible.

The ecosystem lacks a **bundle-first “interop lab”** that:
1) defines *profiles* (what you actually implement), and  
2) turns failures into shareable, redacted artifacts.

# What it should provide

## A. Profiles, not just “support”
A small set of named profiles that map to real deployments:

- `oidc-basic` (Discovery + Auth Code + PKCE)
- `oidc-par` (PAR enabled, request-URI flow)
- `oauth-dpop` (sender-constrained access tokens via DPoP)
- `oidc-high-assurance` (PAR + DPoP + strict redirect URI + nonce/jti rules)

Each profile includes:
- required endpoints, parameters, JWS/JWK expectations,
- expected error codes and retry guidance,
- a **compatibility matrix** format.

## B. A portable evidence bundle format

A `*.oauthbundle.zip` that enables reproducible triage without leaking secrets:

- `report.json` (normalized outcome + profile + environment fingerprints)
- `http/` captured requests/responses (redacted; deterministic ordering)
- `keys/` public JWKs used, key ids, and algorithm policy
- `replay/` scripts to re-run against a local test server
- `redaction.json` policy + proof of redaction passes

## C. `cargo oauth-lab …` UX

- `cargo oauth-lab doctor` — validates configuration, discovery docs, JWKS rotation, clock skew.
- `cargo oauth-lab run --profile oidc-par` — executes scenario suites.
- `cargo oauth-lab bundle` — produces the `oauthbundle.zip` with redaction.
- `cargo oauth-lab diff` — compares two runs (regressions, provider change).

# MVP (ship in weeks)

- Implement `oidc-basic` + `oidc-par` scenario suites (against:
  - an embedded in-memory test server, and
  - one “real provider” adapter as reference).
- Bundle format v0 with strict redaction and deterministic serialization.
- A minimal provider adapter trait:
  - discovery URL, client auth method, special params.

# v1 (ship in months)

- Add `oauth-dpop` and `oidc-high-assurance` profiles.
- Introduce a **conformance corpus**: provider quirks captured as tests with public fixtures.
- Add a “fuzz the boundary” mode for parameter permutations (controlled).

# Design notes

- Keep the core engine runtime-agnostic; provide Tokio default runner.
- Prefer **artifact determinism** over cleverness: stable ordering, stable JSON, stable timestamps.
- Treat redaction as a first-class pipeline with unit tests and “leak checks”.

# Conformance & tests

- Golden fixtures for PAR request objects and DPoP proofs.
- Negative suites: replay detection, clock skew, nonce mismatch.
- Compatibility matrix tests ensure “profile claims” remain honest across releases.

# Prior art & ecosystem fit

- Aligns with PAR and DPoP standard semantics. (RFC 9126, RFC 9449)
- Builds on existing Rust OIDC/OAuth libraries rather than replacing them. (e.g., `openidconnect`)
