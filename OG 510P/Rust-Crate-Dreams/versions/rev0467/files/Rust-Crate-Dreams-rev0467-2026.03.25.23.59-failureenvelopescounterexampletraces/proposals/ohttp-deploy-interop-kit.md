---
id: P-0194
title: OHTTP Deploy & Interop Kit — privacy gateways with reproducible bundles (OHTTP/BHTTP/HPKE)
status: idea
domains: [networking, privacy, http, security, interop, devtools]
last_reviewed: 2026-03-05
evidence:
  - https://www.ietf.org/rfc/rfc9458.html
  - https://datatracker.ietf.org/doc/rfc9292/
  - https://crates.io/crates/ohttp
  - https://crates.io/crates/bhttp
  - https://developers.google.com/safe-browsing/ohttp/reference
needs:
  - A “golden-path” crate/tooling set for deploying and operating Oblivious HTTP gateways/relays in Rust (today this is piecemeal and hard to debug reproducibly).
  - Portable incident artifacts so privacy gateways can be debugged without copying logs or sensitive payloads.
risks:
  - OHTTP deployments are niche; adoption depends on “one-click” value (doctor, capture, conformance) not just another implementation.
  - Privacy systems fail catastrophically when misconfigured; the kit must make unsafe states hard to reach.
---

# Problem

Oblivious HTTP (OHTTP) defines a way to forward encrypted HTTP messages so an origin server cannot link requests to a client identity, while limiting trust in intermediaries. However, deploying OHTTP in practice needs more than protocol encode/decode:

- key configuration distribution and rotation
- gateway/relay operational wiring (HTTP/2/HTTP/3 edge, metrics, rate limits)
- deterministic, redacted debugging artifacts for “this request fails” without leaking user data
- interoperability testing across implementations

Rust has building blocks (`ohttp`, `bhttp`), but lacks an *ops-grade* “deploy & interop kit” that turns the protocol into a maintainable service.

# Users & user stories

- **Privacy gateway operators**: “I want to rotate keys, observe error rates, and debug failures without storing user payloads.”
- **Client authors**: “I want a high-level client that can negotiate configs and produce a reproducible bug bundle.”
- **Auditors/security reviewers**: “I want conformance tests and ‘unsafe configuration’ checks.”

# Prior art (and why it’s insufficient)

- RFC 9458 OHTTP, RFC 9292 Binary HTTP: standards, not deploy tooling.
- `ohttp` + `bhttp`: core encoding/decoding, but not gateway UX, capture, or conformance.
- Service-specific gateways (e.g., Safe Browsing gateway docs) show the shape of the problem, but are not reusable.

# Design goals / non-goals

**Goals**
- Provide a stable, audited core for *operational* OHTTP gateways and clients.
- Make failures reproducible with a portable, redacted bundle format.
- Ship an interop runner + vector suite (client↔gateway, gateway↔target), with CI recipes.

**Non-goals**
- Replace general HTTP stacks (hyper/reqwest) or QUIC stacks; integrate with them.
- Promise anonymity beyond what OHTTP provides; instead, make configuration transparent and testable.

# Architecture & API sketch

Crates (workspace):

- `ohttp-kit-core`: types for configs, rotation, error taxonomy, redaction rules.
- `ohttp-kit-gateway`: gateway service glue:
  - HTTP edge integration points
  - key store trait (`KeyStore`: load/rotate, publish configs)
  - target routing policies
- `ohttp-kit-client`: high-level client wrapper:
  - config discovery hooks
  - request encapsulation with metadata-minimizing defaults
- `ohttp-kit-bundle`: artifact format + writer/reader for incident bundles.
- `cargo-ohttp`: CLI:
  - `cargo ohttp doctor` — validate deployment, keys, HTTP endpoints
  - `cargo ohttp capture` — produce bundles from failing transactions
  - `cargo ohttp interop` — run scenario suites and emit reports

# Bundle format: `*.ohttpbundle.zip`

Top-level:
- `report.json` (schema_version, environment fingerprints, summary, verdicts)
- `input/` (sanitized request metadata, negotiated suite IDs, config IDs)
- `artifacts/` (bhttp-encoded messages *after* redaction, error chains, timing)
- `policy/` (redaction policy used, allowlist decisions)

Redaction defaults:
- remove raw URLs/headers unless explicitly allowlisted
- hash any stable identifiers
- never store decrypted payload bytes by default

# Security / safety model

- Explicit “privacy invariants” checked in `doctor` (e.g., no logging of cleartext payloads; no stable user identifiers in bundles).
- Key material never written to bundles; bundle contains only config IDs and suite identifiers.
- Dependency minimization and fuzzing of bhttp parsing surfaces.

# Maintenance & governance plan

- Maintain an “interop matrix” in-repo for versions of `ohttp`/`bhttp` and reference implementations.
- Include a security policy and rotation playbooks.
- Keep bundle schema additive; version bumps only on breaking changes.

# Milestones (0.1 / 0.2 / 1.0)

**0.1**
- `cargo ohttp doctor`, basic gateway wrapper, bundle writer/reader.
- minimal scenario suite (happy path + common errors).

**0.2**
- key rotation helpers + config publishing patterns
- conformance vectors from RFCs + fuzz corpus integration

**1.0**
- stable bundle schema + interop runner
- “known-safe defaults” profiles for common deployments

# Open questions

- Best abstraction boundary between HTTP edge and gateway core (hyper/axum vs tower traits)?
- How to model config discovery without baking in DNS/SVCB assumptions?

# Sources

- https://www.ietf.org/rfc/rfc9458.html
- https://datatracker.ietf.org/doc/rfc9292/
- https://crates.io/crates/ohttp
- https://crates.io/crates/bhttp
- https://developers.google.com/safe-browsing/ohttp/reference
