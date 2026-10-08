---
id: P-0060
title: openapi-sdk-kit — modern OpenAPI client/server codegen with conformance, mocks, and upgrade-friendly diffs
status: idea
domains: [web, tooling, codegen, api]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/OpenAPITools/openapi-generator/issues/6178
  - https://github.com/oxidecomputer/progenitor
  - https://paperclip-rs.github.io/paperclip/
  - https://www.reddit.com/r/rust/comments/x9zkr7/recommendations_for_rust_openapi_client/
needs:
  - Provide an ergonomic, “Rusty” OpenAPI workflow that teams can adopt without hand-maintaining clients.
  - Make generated code testable, mockable, and stable under regeneration (minimal diffs).
risks:
  - OpenAPI surface area is huge; must focus on a narrow, high-value feature set first.
  - Codegen bikeshedding and framework lock-in can block adoption.
---

## Problem

Rust has multiple ways to *describe* APIs (e.g., utoipa) and multiple codegen tools (e.g., progenitor, paperclip), but teams still struggle to pick a workflow that is:

- idiomatic in modern async Rust,
- strongly typed end-to-end,
- easy to mock in tests, and
- stable across regeneration (minimal diffs, predictable formatting).

External generators have historically produced non-idiomatic or weakly typed Rust clients (e.g., futures version mismatch and untyped returns), reinforcing the need for a Rust-first “golden path”.

## Users & user stories

- **API consumers**: “Generate a client I can use and mock in tests without touching the generated code.”
- **API producers**: “Generate server stubs/middlewares that match my framework (axum/actix) and keep drift low.”
- **Platform teams**: “Standardize client generation across services and verify compatibility in CI.”

## Prior art (and why it’s insufficient)

- `openapi-generator` Rust generator has had long-standing ergonomic issues (async/futures versioning, weak typing).  
  https://github.com/OpenAPITools/openapi-generator/issues/6178
- `progenitor` is a strong OpenAPI 3.0 client generator, but there’s still missing ecosystem glue: conformance suites, stable IR, and “upgrade-friendly diff discipline” across generators.  
  https://github.com/oxidecomputer/progenitor
- `paperclip` aims at type-safe APIs and codegen, but users still perceive fragmentation and varying production readiness across approaches.  
  https://paperclip-rs.github.io/paperclip/

## Design goals / non-goals

### Goals
- **Stable intermediate representation (IR)** for OpenAPI 3.0/3.1 that is easier to target than raw spec JSON.
- **Conformance suite**: fixtures + golden tests that validate the generator across common OpenAPI patterns.
- **Generation discipline**:
  - stable formatting (rustfmt + deterministic ordering),
  - minimal diffs on regeneration,
  - explicit “hand-edit escape hatches” via partial templates or extension traits.
- **Mocks by default**: generate strongly typed mocks for client calls.

### Non-goals
- Be “the one generator to rule them all” in v0.1. Start with a pragmatic client generator and a shared IR/testkit.

## Architecture & API sketch

### Crates
- `openapi-ir` — parse OpenAPI into a normalized, versioned IR:
  - resolves `$ref`s, normalizes schemas, and records provenance for diagnostics.
- `openapi-testkit` — conformance fixtures and golden outputs:
  - known tricky specs (pagination, oneOf/anyOf, nullable, auth schemes)
  - “compile tests” + runtime tests with mocked HTTP servers.
- `openapi-gen-client` — generator that targets:
  - `reqwest` + `tower` middleware hooks for retries/auth/logging
  - optional `wasm` HTTP client backend later
- `openapi-gen-server` (later) — optional server scaffolding for axum/actix.

### Generated code conventions
- A `Client` type with:
  - typed request builders and typed responses
  - pluggable “transport” trait so users can swap HTTP stacks or inject mocks
- Error model:
  - typed error enum with status/body decode errors and response classification
- Auth:
  - traits for API key/bearer/OAuth token providers.

## Security / safety model

- Never treat OpenAPI documents as trusted input:
  - enforce size limits,
  - safe `$ref` resolution (no network in default mode),
  - warn on suspicious patterns.
- Encourage compile-time safety over runtime stringly-typed plumbing.

## Maintenance & governance

- Publish IR schema guarantees (additive changes, clear versioning).
- Keep test fixtures as first-class; require new features to add fixtures.
- Avoid framework lock-in by separating transport traits and adapters.

## MVP milestones

- **0.1**: `openapi-ir` + `openapi-testkit` + a minimal client generator for a subset (GET/POST JSON, basic auth).
- **0.2**: richer schema handling (oneOf/anyOf), typed errors, pagination streams.
- **0.3**: mock generation + compatibility reports (API diff between spec versions).
