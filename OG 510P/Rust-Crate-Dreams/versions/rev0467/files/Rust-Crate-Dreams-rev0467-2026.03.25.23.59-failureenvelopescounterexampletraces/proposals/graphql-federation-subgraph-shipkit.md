---
id: P-0192
title: GraphQL Federation Subgraph ShipKit
status: idea
domains: [web, api, graphql, tooling, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://www.apollographql.com/docs/graphos/schema-design/federated-schemas/reference/subgraph-spec
  - https://github.com/apollographql/supergraph-demo
---

# P-0192 — GraphQL Federation Subgraph ShipKit

## Problem / why now

Apollo Federation 2 defines a set of schema additions and runtime behaviors that a server must implement to be a compliant **subgraph** (including enhanced introspection via `Query._service` and correct entity resolution). citeturn0search1

Rust has multiple GraphQL servers/frameworks, but the “Federation correctness surface” tends to be:
- re-implemented ad hoc,
- poorly tested across versions,
- and hard to debug when supergraph composition or entity resolution breaks.

Meanwhile, the ecosystem already trusts Rust for federation at the router layer (Apollo Router is written in Rust). citeturn0search9  
What’s missing is the *subgraph shipkit*.

## What this crate/tooling should provide other people

A cross-framework “federation compliance module” + harness:

1. **Federation 2 schema augmentation**
   - Inject required federation directives/types
   - Generate `_service { sdl }` automatically
   - Provide an ergonomic API for `@key` entity resolvers

2. **Request normalization & diagnostics**
   - Helpers for parsing federation representations
   - Structured error output for common misconfigurations:
     - missing key fields
     - inconsistent type ownership
     - partial entity resolution

3. **Interop / compatibility harness**
   - A test runner that:
     - composes subgraph SDLs against a supergraph compiler
     - runs scripted query suites for entity resolution
   - Emits `*.gqlbundle.zip` containing:
     - SDLs
     - composed supergraph errors (if any)
     - query traces (redacted)
     - minimal failing queries

4. **Framework adapters**
   - Thin integration layers for common Rust GraphQL frameworks
   - “Bring your own executor” boundaries so the crate doesn’t force a runtime choice

## Artifact: `gqlbundle.zip`

A portable artifact to share a federation failure:

- `subgraph.graphql` (SDL)
- `supergraph/` (composition inputs + errors)
- `queries/` (minimized failing queries + expected vs observed)
- `traces/` (normalized traces, redacted)
- `report.json` (environment + versions)

## MVP → v1 plan

### MVP
- Standalone federation augmentation + `_service` handling.
- Entity resolver helper API.
- CLI: `cargo federation test` that runs a minimal compliance suite and outputs `gqlbundle.zip` on failure.

### v1
- Expanded compatibility suite mapped to the Federation 2 spec sections (tagged tests).
- Composition regression suite.
- Adapter ecosystem for major Rust GraphQL servers.

## Evidence / references

- Federation 2 subgraph requirements and behaviors. citeturn0search1
- Existence of a production Rust federation runtime (Apollo Router) indicates Rust is viable and high-performance in this space. citeturn0search9
