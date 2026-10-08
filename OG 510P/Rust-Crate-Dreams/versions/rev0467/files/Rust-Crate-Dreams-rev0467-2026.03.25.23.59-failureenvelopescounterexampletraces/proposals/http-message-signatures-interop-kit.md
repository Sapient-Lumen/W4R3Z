---
id: P-0180
title: HTTP Message Signatures Interop Kit
status: idea
domains: [security, networking, web, interoperability]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/rfc9421/
  - https://github.com/junkurihara/httpsig-rs
  - https://socialhub.activitypub.rocks/t/rfc-9421-http-signatures-in-2026/8427
---

# Problem

HTTP Message Signatures (RFC 9421) standardize signing/verification over HTTP message components, but real interoperability depends on profiles: which components must be signed, which algorithms are allowed, how nonces are handled, and how intermediaries transform messages.

In Rust, there are implementations, but the ecosystem lacks (1) a shared profile registry, (2) conformance fixtures, and (3) ergonomic integration with common HTTP stacks (hyper/reqwest/axum) plus CI-friendly artifacts.

# What it provides

- A crate `http-sig-interop` that offers:
  - request/response signing + verification (RFC 9421 aligned)
  - integration layers for `http` types and common frameworks (feature-gated)
  - profile definitions (API gateway profile, ActivityPub profile draft, “strict minimal”)
- A conformance suite + fixture corpus:
  - canonical test vectors (`sigparams`, covered components)
  - “transformation cases” (proxy header normalization, whitespace, duplicates)
  - multi-signature confusion guardrails
- A standard artifact: `httpsigbundle.zip`
  - request/response captures (sanitized)
  - parsed signature inputs
  - verification trace + failure reasons
  - profile used and allowed algorithms list
- CLI: `cargo httpsig {sign,verify,lint,doctor}`

# Users & user stories

- API platform engineer: “Enforce that all ingress requests carry a valid signature over method/authority/path/date, under profile X.”
- Federation server maintainer: “Interop test against other implementations; share a failing bundle with upstream.”
- Security reviewer: “See exactly what was signed and why verification failed.”

# Prior art (and why it’s insufficient)

- RFC 9421 defines mechanism, not deployment profiles.
- `httpsig-rs` demonstrates RFC 9421 support but is “WIP” and scoped; the missing piece is ecosystem-wide profile + corpus + tooling.
- Fediverse implementers are actively discussing how to apply RFC 9421 in practice, highlighting the need for agreed profiles and fixtures.

# Design goals

- Interop-first: fixtures, profiles, and traces are first-class.
- Minimize footguns: default safe behavior around multiple signatures.
- Easy adoption: integrate with `http` crate types; avoid runtime lock-in.

# Non-goals

- Replacing TLS; this is for application-level signatures where needed.
- Defining a single universal profile; ship a registry + tooling.

# Architecture & API sketch

- `Profile` (required components, algorithm set, required params)
- `Signer`/`Verifier` over `http::Request`/`http::Response`
- `Trace` module for diffable verification logs
- `Bundle` helpers for redacted capture and replay

# Security / safety model

- Explicitly address “multiple signature confusion” by:
  - default single-signature verify
  - opt-in multi-signature mode with RFC-recommended constraints
- Redaction hooks for sensitive headers and bodies.

# Maintenance & governance plan

- Profiles live as data (TOML/YAML) with versioning; PR review requires new fixtures.
- Publish a “profile authoring guide” and interop CI recipe.

# Milestones

- MVP: verify + lint + bundle schema + 30–50 fixtures.
- v1: framework adapters + signer, profile registry, interop runner.
- v2: transformation fuzzing, cross-lang interop harness.

# Open questions

- Which header canonicalization rules should be default vs profile-specific?
- How to represent body coverage policies consistently across frameworks?

# Sources

- RFC 9421 (HTTP Message Signatures).
- httpsig-rs implementation notes.
- Fediverse discussion on RFC 9421 profile recommendations.
