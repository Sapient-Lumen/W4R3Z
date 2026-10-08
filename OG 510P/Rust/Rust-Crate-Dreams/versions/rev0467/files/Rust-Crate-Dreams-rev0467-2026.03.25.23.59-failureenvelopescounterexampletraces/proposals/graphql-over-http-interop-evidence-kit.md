---
id: P-0255
title: GraphQL over HTTP Interop & Evidence Kit — request/response canonicalization, multipart upload traces, and conformance bundles
status: idea
domains: [web, api, interop, conformance, tooling, developer-tools]
last_reviewed: 2026-03-05
evidence:
  - https://spec.graphql.org/
  - https://graphql.github.io/graphql-over-http/draft/
  - https://github.com/jaydenseric/graphql-multipart-request-spec
---

## Why this is missing
GraphQL is widely used, but interoperability issues concentrate in the “edges”:
- over-HTTP semantics (content types, error shapes, batching),
- file uploads (multipart conventions),
- caching/proxy interaction,
- differing interpretations across server/client libs.

There is a draft GraphQL-over-HTTP specification aimed at maximizing interoperability, plus a widely used multipart upload convention, but Rust lacks a **portable conformance + evidence bundle** layer.

## What the crate provides
A workspace producing **`*.gqlbundle.zip`** artifacts and running a conformance suite:

- Canonical HTTP transcript capture: method, headers (redacted), body, status, response content-type, and parsed GraphQL response.
- Semantic diffing: “same query, different error shape” / “content-type mismatch”.
- Multipart upload capture aligned with the de facto multipart request spec (for tooling and interop).

### Core crates/modules
- `gql-http`: canonical transcript IR for GraphQL-over-HTTP (request/response).
- `gqlbundle`: bundle schema + redaction (tokens/cookies) + deterministic ordering.
- `conformance`: a runner that executes scenarios against:
  - Rust servers (async frameworks),
  - external endpoints,
  - client libraries via adapters (optional).
- `multipart`: parser and canonicalizer for GraphQL multipart request structure.

## Bundle format sketch
`gqlbundle/`
- `meta.json`
- `scenarios/<name>/request.http` + `response.http` (canonical form)
- `scenarios/<name>/parsed.json` (graphql response + errors)
- `multipart/` (if present): `map.json`, file part hashes, size metadata
- `verdict.json` + `diff.md`

## MVP plan (4–6 weeks)
1. Bundle schema + redaction + canonical HTTP transcript format.
2. A small conformance corpus covering:
   - GET vs POST
   - content-type expectations
   - error envelope shape and status
   - batching (if supported)
3. Multipart request capture + canonicalization for upload flows.

## De-risking
- Keep the “engine” small: lean on existing GraphQL parsers/executors; focus on the evidence/conformance layer.
- Encode “draftness” explicitly: pin spec versions in bundles and allow multiple profiles.

## What users get
- CI-grade conformance tests and shareable evidence bundles when clients/servers disagree.
