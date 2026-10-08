---
id: P-0272
title: Apache Arrow Flight / Flight SQL Interop & Evidence Kit (flightbundle)
status: idea
domains: [data, arrow, grpc, interop, testing]
last_reviewed: 2026-03-05
evidence:
  - https://arrow.apache.org/docs/format/Flight.html
  - https://github.com/apache/arrow/blob/main/format/Flight.proto
  - https://github.com/apache/arrow-rs/blob/main/arrow-flight/README.md
  - https://docs.rs/arrow-flight/latest/arrow_flight/
  - https://arrow.apache.org/rust/arrow_flight/index.html
---

## What it should provide others

A practical way to validate and debug **Apache Arrow Flight / Flight SQL** deployments by producing portable evidence bundles:

- canonicalized Flight RPC transcripts (requests, responses, status, trailers)
- RecordBatch stream hashing (payload proof without copying large data)
- conformance profiles (e.g., required metadata, batching rules, compression)
- replay harness to reproduce server/client bugs

Deliverable: `*.flightbundle.zip` for CI, issue reports, and vendor interop testing.

## Why this is needed

Arrow Flight is used to ship high-throughput columnar data over gRPC. Implementations exist across languages; Rust has `arrow-flight` (tonic-based), but interop failures often come from:
- subtle metadata/trailer differences
- stream framing, backpressure, and batching behavior
- Flight SQL dialect mismatches
- auth/tls proxying differences

A bundle-based approach lets teams compare behavior without shipping raw datasets.

## Design sketch

### Workspace layout

- `flightbundle` — schema + redaction + IO
- `flight-ir` — canonical model of:
  - FlightService RPCs (proto decoded)
  - gRPC metadata + trailers (allowlist)
  - stream events (RecordBatch boundaries, hashes, sizes)
- `flightcapture` — capture modes:
  - in-process tonic interceptor (client/server)
  - sidecar proxy capture (grpc)
- `flightreplay` — replay to a target server with deterministic pacing
- `flightverify` — conformance checks:
  - required fields, status mapping, metadata rules
  - stream consistency (hash chain, row counts)
  - Flight SQL profile set (optional)

### Evidence bundle: `*.flightbundle.zip`

- `manifest.json` (proto/arrow versions, compression, tls mode)
- `rpc.ndjson` (canonical events)
- `streams/` (batch hash chain + sizes; optional sampled payloads)
- `profiles/` (rulesets, e.g. “flightsql-min”)
- `reports/` (diff + explain)
- `redaction.json`

### MVP (4–8 weeks)

1. tonic interceptor capture → `rpc.ndjson`
2. RecordBatch hashing + size/rowcount summaries
3. replay of unary + basic streaming paths
4. minimal `flightverify` profiles (baseline + flightsql)

## Adoption plan

- Provide a `cargo flightbundle` subcommand for capture/replay/diff
- Ship fixtures to compare Rust vs JVM vs C++ servers using the same bundle format
