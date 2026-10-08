---
id: P-0065
title: HTTP Cassette Kit — standard record/replay format + adapters across Rust HTTP clients
status: idea
domains: [testing, web, tooling]
last_reviewed: 2026-03-01
evidence:
  - https://crates.io/crates/rvcr
  - https://crates.io/crates/http-client-vcr
  - https://docs.rs/surf-vcr
needs:
  - Teams want deterministic API tests without mocking every endpoint by hand.
  - Existing crates are client-specific; a shared cassette format enables ecosystem tooling.
risks:
  - Cassette matching can become a security footgun (accidentally replaying sensitive data).
  - Too many config knobs can make adoption painful.
---

## Problem
Record/replay (“VCR”) testing is valuable for:
- deterministic integration tests,
- fast CI without hitting third-party APIs,
- reproducing intermittent failures.

Rust has multiple VCR-style crates, but they are fragmented by HTTP client stack (`reqwest`, `surf`, `http-client`). There is no de-facto **cassette format**, **redaction standard**, or **matching policy** that can be shared across tools.

## Users & user stories
- **SDK authors**: “Record one golden cassette and run tests across multiple clients/backends.”
- **App teams**: “Redact secrets and keep cassettes safe to commit.”
- **CI**: “Fail if a test tries to reach the network when a cassette exists.”

## Prior art (and why it’s insufficient)
- `rvcr`: record/replay middleware for reqwest. https://crates.io/crates/rvcr
- `http-client-vcr`: record/replay for the `http-client` ecosystem. https://crates.io/crates/http-client-vcr
- `surf-vcr`: record/replay for Surf. https://docs.rs/surf-vcr
These prove demand, but they don’t converge on shared artifacts and policies.

## Design goals / non-goals
**Goals**
- Define a stable **cassette file format** (versioned, deterministic ordering).
- Provide **redaction policy** primitives (headers, query params, JSON paths).
- Provide a **match policy** model (method+url+body hashing, tolerance knobs).
- Provide adapters for major stacks: reqwest (middleware), tower/hyper (service), http-client.

**Non-goals**
- Being a full mock server framework; focus on record/replay.

## Architecture & API sketch
Core crate: `http-cassette-core`
- `Cassette { interactions: Vec<Interaction>, schema_version }`
- `Interaction { request: Req, response: Resp, timings, metadata }`
- `Redactor` trait + built-in redactors
- `Matcher` trait + built-in matchers

Adapters:
- `http-cassette-reqwest`
- `http-cassette-tower` (works for hyper stacks)
- `http-cassette-http-client`

CLI:
- `http-cassette lint` (detect secrets, missing redaction)
- `http-cassette diff` (explain why a request didn’t match)
- `http-cassette scrub` (apply redaction policy to existing cassettes)

## Security / safety model
- Default deny-list redaction for `Authorization`, cookies, and common secret headers.
- “Safe-to-commit” mode that fails CI if unredacted secret patterns are detected.
- Optional encryption for local cassettes (not committed).

## Maintenance & governance plan
- Keep format stable and versioned; publish a JSON schema.
- Conformance fixtures: same cassette must replay identically across adapters.
- Minimal deps in core crate; adapters isolated.

## Milestones
**0.1**
- Format v0 + reqwest adapter + redaction policy + lint CLI.

**0.2**
- tower adapter + deterministic matching explanations.

**1.0**
- http-client + surf adapters + conformance suite + docs cookbook.

## Open questions
- Should the cassette format store raw bodies or hashed bodies by default?
- Best strategy for streaming responses and large payloads?

## Sources
- https://crates.io/crates/rvcr
- https://crates.io/crates/http-client-vcr
- https://docs.rs/surf-vcr
