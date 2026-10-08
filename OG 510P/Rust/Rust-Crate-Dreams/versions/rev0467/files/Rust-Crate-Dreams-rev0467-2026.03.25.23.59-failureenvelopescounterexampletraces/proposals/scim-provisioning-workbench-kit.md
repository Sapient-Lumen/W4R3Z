---
id: P-0183
title: SCIM Provisioning Workbench Kit (Server + Client + Conformance)
status: idea
domains: [identity, enterprise, web, tooling, conformance]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc7644
  - https://crates.io/crates/scim-server
  - https://crates.io/crates/scim_v2
  - https://scim.cloud/
---

# Problem

SCIM is “simple” in theory, but provisioning interoperability in practice is messy:

- Different IdPs interpret schemas, patch semantics, filters, and pagination differently.
- Servers need safe, auditable mapping from SCIM resources to internal identity stores.
- Operators need **reproducible incident artifacts** when deprovisioning goes wrong.

Rust has SCIM crates, but it lacks a **workbench** that makes SCIM correctness measurable and operational.

# What it should provide

## A. A reference server core (embeddable)

A library-first SCIM server core that:
- implements RFC 7644 behavior (CRUD, PATCH, filters, pagination),
- supports pluggable storage backends (SQL, LDAP-ish, in-memory),
- exposes hooks for policy and audit logging.

## B. A conformance harness + corpora

- A scenario runner that exercises:
  - PATCH edge cases (path syntax, add/replace/remove),
  - filter correctness and performance characteristics,
  - pagination and stable sorting.
- A growing corpus of **real-world IdP quirks** captured as fixtures.

## C. Portable evidence bundles

`*.scimbundle.zip` for reproducible triage:

- `report.json` (server version, profile, failures)
- `http/` request/response transcripts (redacted PII)
- `db/` optional normalized state snapshots (hashed)
- `replay/` commands to reproduce against the reference server

## D. `cargo scim …` UX

- `cargo scim serve` — reference server for local interop testing.
- `cargo scim test` — run the conformance suite against any endpoint.
- `cargo scim bundle` — capture a scimbundle for CI failure artifacts.

# MVP

- Reference server core supporting:
  - `/Users`, `/Groups`, `ServiceProviderConfig`, `ResourceTypes`,
  - basic filters + pagination.
- Transcript capture + redaction + bundle v0.
- A “known-good” compatibility suite for a minimal SCIM subset.

# v1

- Formalize **profiles** (minimal provisioning, enterprise provisioning, strict patch).
- Add fuzz/quickcheck-style generators for PATCH and filters.
- Provide adapters: “SCIM → internal model” mapping helpers with explicit invariants.

# Design notes

- Treat schema handling as a policy boundary: explicit mapping tables and validation.
- Provide a **PII redaction DSL** (mask emails, stable hashing for user ids).
- Make “delete semantics” and “deprovision semantics” explicit and testable.

# Why it’s epic

SCIM is a deep enterprise pain point: a workbench that makes SCIM *conformant, testable, and debuggable* would save teams months and would be widely reusable.
