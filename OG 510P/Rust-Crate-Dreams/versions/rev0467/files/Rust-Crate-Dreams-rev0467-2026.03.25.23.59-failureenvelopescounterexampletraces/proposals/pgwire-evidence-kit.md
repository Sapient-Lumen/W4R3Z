---
id: P-0268
title: PostgreSQL Wire Protocol Interop & Evidence Kit (pgbundle)
status: idea
domains: [database, networking, interop, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://www.postgresql.org/docs/current/protocol.html
  - https://www.postgresql.org/docs/current/protocol-message-formats.html
  - https://www.postgresql.org/docs/current/protocol-message-types.html
  - https://www.postgresql.org/docs/current/protocol-logicalrep-message-formats.html
  - https://crates.io/crates/postgres-protocol
  - https://crates.io/crates/tokio-postgres
  - https://crates.io/crates/sqlx
  - https://crates.io/crates/pgwire
---

## What it should provide others

A **portable, redactable, deterministic** way to capture, replay, and diff PostgreSQL “wire” interactions (protocol v3) across clients/servers and compatibility layers — producing shareable artifacts for CI, bug reports, and vendor interop.

If you’re writing any of these:

- a Postgres-compatible server (or proxy / pooler / gateway)
- a driver / ORM
- a protocol-aware middleware (auth, observability, security)

…you get a standard **evidence bundle** instead of bespoke packet dumps and “works on my machine” repros.

## Why this seems missing in Rust

There are good drivers and protocol crates, but no widely adopted **interop harness** that:

- normalizes protocol traces into a stable IR
- makes failures **diffable** across implementations
- bakes in privacy controls (query/value redaction, identifier hashing)
- yields minimal reproductions via trace shrinking

## Design sketch

### Workspace layout

- `pgbundle` — bundle schema + IO + signing hooks (optional)
- `pgwire-ir` — canonical intermediate representation for messages + typed fields
- `pgcapture` — capture backends:
  - client-side shim (wrap `tokio-postgres` / `sqlx` connectors)
  - server-side shim (wrap pgwire server implementations)
  - optional pcap ingest (best-effort; lower fidelity)
- `pgreplay` — deterministic replay runner (client or server mode)
- `pgdiff` — semantic diffs and “explain” reports:
  - auth method mismatches, parameter status drift
  - extended query flow divergences (Parse/Bind/Describe/Execute/Sync)
  - error class/state code deltas
- `pgshrink` — delta-debugging reducer for traces (minimize to failing subset)

### Evidence bundle format: `*.pgbundle.zip`

Bundle holds:

- `manifest.json` (schema version, redaction policy, tool versions)
- `trace.pgwireir.jsonl` (canonical message stream)
- `env/` (server version banner, parameters, extensions, TLS mode, locale)
- `fixtures/` (optional) named datasets / prepared statements / copy inputs
- `reports/` diffs + explain summaries
- `signatures/` (optional) DSSE envelope / attestations

## MVP (4–8 weeks)

1. **Canonical IR + JSONL trace** for core startup/auth + simple query + extended query
2. Capture via a **client shim** (feature-gated) + replay against a server
3. `pgdiff` v0:
   - message-type and field-level diffs
   - normalized errors (severity, SQLSTATE, position fields)
4. Redaction presets:
   - replace literals, hash identifiers, drop payloads for COPY

## De-risking plan

- Start with the official message format definitions and typed message data types.
- Treat pcap ingest as “best effort” (TCP reassembly, TLS blindness) and keep it optional.
- Make capture adapters opt-in and lightweight (no deep integration required).

## Non-goals (initially)

- Full SQL semantic verification
- Full logical replication compliance
- TLS decryption / keylog support (can be a later extension)

## Related work / overlap

- `postgres-protocol`, `tokio-postgres`, `sqlx` already handle protocol mechanics.
- Some non-Postgres systems implement PGWire for compatibility; this kit targets **evidence + conformance**, not another PG server.
