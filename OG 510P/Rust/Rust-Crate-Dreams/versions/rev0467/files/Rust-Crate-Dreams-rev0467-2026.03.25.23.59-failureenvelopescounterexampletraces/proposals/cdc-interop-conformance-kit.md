---
id: P-0113
title: CDC Interop & Conformance Kit
status: idea
domains: [data, databases, streaming, testing]
last_reviewed: 2026-03-05
evidence:
  - https://crates.io/crates/rivven-cdc/0.0.11
  - https://crates.io/crates/pg2any_lib
  - https://debezium.io/documentation/reference/stable/integrations/cloudevents.html
  - https://debezium.io/documentation/reference/stable/integrations/serdes.html
---

# Problem

“CDC in Rust” exists, but it’s fragmented: each project invents its own event envelope, schema-change semantics, snapshot+catchup strategy, and testing story. Even when a crate works for one database pair, it’s hard to **trust correctness**, compare implementations, or swap sinks/sources.

The missing thing is not “yet another Postgres logical replication crate.” It’s a **portable contract**: event envelope + compatibility matrix + conformance corpora + replay harness + reference adapters.

# What it provides

Deliverables others can rely on:

1. **A standard CDC envelope**
   - `CdcEnvelope` (op, source, tx metadata, timestamps, schema id, key, before/after, tombstone)
   - Optional “CloudEvents view” for integration pipelines
   - A defined schema-change stream (DDL + type mapping hints), not just row changes

2. **Interop adapters**
   - Source adapters: Postgres logical replication (slot-based), MySQL/MariaDB (binlog), etc. (initial focus: Postgres, because Rust has real crates already)
   - Sink adapters: JSONL, Kafka (serde), Parquet/Arrow, “apply to target DB” helpers
   - A “bridge” layer that can translate between this envelope and Debezium-style envelopes (for mixed ecosystems)

3. **Artifact-first testing**
   - `*.cdc-corpus.zip`: recorded streams (row ops + schema events) + ground-truth end state + version metadata
   - `cdc-replay`: deterministic replay runner that validates invariants (idempotency, ordering, snapshot+catchup correctness)
   - `cdc-diff`: “expected vs observed” report with minimal counterexample slicing

4. **Cargo UX**
   - `cargo cdc {capture,replay,doctor,bench}`
   - “Doctor” checks: slot config, WAL retention, permissions, schema mapping warnings

# Users & user stories

- **Pipeline builder:** “I want to replicate Postgres to a data lake; I need schema changes and replays that don’t silently corrupt.”
- **Crate author:** “I wrote a CDC source; I want to prove it conforms and compare performance fairly.”
- **Operator:** “I need a replayable failure bundle for a 3am incident.”

# Prior art (and why it’s insufficient)

- Rust CDC crates for Postgres/logical replication exist and are improving, but they don’t share a contract or conformance story. citeturn0search0turn1search1turn1search9
- Debezium documents rich envelopes and even CloudEvents mapping; Rust users often want to interoperate with that world without adopting Kafka Connect. citeturn1search4turn1search12turn1search0

# Design goals

- **Correctness-first:** defined semantics for ordering, transactions, and schema changes.
- **Interop-first:** adapters should let you speak “Debezium-ish” when needed.
- **Corpus-driven:** compatibility is proven by replaying known streams and end-state checks.
- **Minimal surface:** focus on envelope + harness; don’t become a whole stream processor.

# Non-goals

- Providing a full managed replication service.
- Solving every source DB in v1 (start with Postgres + one more).

# Architecture & API sketch

Crates:
- `cdc-envelope` (serde types, schema ids, canonical JSON encoding)
- `cdc-corpus` (recording format + zip bundle helpers)
- `cdc-replay` (runner + validators + minimizer)
- `cdc-adapter-postgres` (logical replication -> envelope)
- `cdc-interop-debezium` (translate Debezium-style into/out of envelope)

Key traits:
- `Source` -> `Stream<Item=CdcEnvelope>`
- `Sink` consumes envelopes with at-least-once semantics
- `Validator` runs invariants on a replay run

# Security / safety model

- Treat corpora as untrusted input: strict limits, bounded decoding, fuzz targets.
- Optional redaction hooks (PII) when capturing corpora.

# Maintenance & governance plan

- Keep envelope stable; version via explicit schema ids.
- Conformance corpus PRs require a reproducible generator and expected end-state hash.
- Encourage third-party adapters; maintainers focus on envelope + harness.

# Milestones

- **MVP:** envelope + corpus format + replay harness + Postgres adapter producing corpora.
- **v0.5:** Debezium interop module + schema-change events + minimization tool.
- **v1:** conformance suite published; at least 2 independent sources pass it.

# Open questions

- Best default for schema evolution representation (logical DDL vs structured type changes).
- How to handle “exactly once” semantics across sinks (likely out of scope).

# Sources

- Rust CDC crates / logical replication implementations and docs. citeturn0search0turn1search1turn1search9
- Debezium envelope + CloudEvents mapping docs. citeturn1search4turn1search12
