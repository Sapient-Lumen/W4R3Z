---
id: P-0262
title: Kafka Protocol Interop & Evidence Kit — wire-protocol conformance, deterministic traces, and semantic diffs
status: idea
domains: [messaging, streaming, protocols, interoperability, testing]
last_reviewed: 2026-03-05
evidence:
  - https://kafka.apache.org/protocol/
  - https://crates.io/crates/rdkafka
  - https://crates.io/crates/kafka
---
# P-0262 — Kafka Protocol Interop & Evidence Kit

**Codename:** `kafkalab`  
**Bundle:** `*.kafkabundle.zip`  
**Primary surface:** wire-protocol conformance + deterministic traces + semantic diffs

## Why this is missing
Kafka is ubiquitous, but reliable *wire-protocol* implementations are hard to test and harder to debug across broker/client versions. The official protocol guide is detailed but large and fast-moving, and interoperability failures tend to show up as production incidents with poor repro. citeturn0search6

Rust has multiple Kafka clients and Kafka-adjacent tooling, but the ecosystem lacks a **portable, redactable, replayable evidence artifact** that can be attached to a bug report or CI failure.

## What the crate should provide
A workspace that lets any Kafka client/broker/proxy implementation:

1. **Record** a session (or synthesize one) as canonical events.
2. **Normalize** and **redact** sensitive parts (topics, payloads, headers) deterministically.
3. **Replay** against another implementation/version.
4. **Diff** results in a semantic way (not byte diffs).
5. Emit a `*.kafkabundle.zip` evidence artifact.

### Target users
- Rust Kafka client maintainers
- teams building Kafka proxies / gateways
- SREs doing incident repro + regression tests
- CI systems that need stable, shareable failure artifacts

## Scope and non-goals
**In scope**
- protocol-level requests/responses (API keys, versions, correlation, flexible versions)
- authentication handshake capture (SASL phases) at the message-boundary level (not secret recovery)
- metadata/produce/fetch/group/offset transactions
- compatibility matrix runner (broker version × client version × feature profile)

**Explicit non-goals**
- a new Kafka client
- “perfect” semantic model of all broker internals
- extracting secrets from auth flows

## Proposed architecture

### Crate layout
```
kafkalab/
  kafkalab-core/        # IR, canonicalization, redaction, diff
  kafkalab-wire/        # parser/encoder for the Kafka wire protocol
  kafkalab-capture/     # TCP capture hooks + “sidecar proxy” capture mode
  kafkalab-replay/      # deterministic replayer with pacing + time controls
  kafkalab-runner/      # scenario DSL + matrix execution
  kafkalab-bundle/      # bundle I/O + schema versioning
  kafkalab-cli/         # `cargo kafkalab ...` and standalone CLI
```

### Canonical IR
- event stream: `Connect`, `Handshake`, `Request{api_key, version, corr_id, body}`, `Response{...}`, `Disconnect`
- normalized timestamps: relative + monotonic sequence numbers
- payload fields optionally summarized (hash + size + selective header sampling)

### Capture modes
- **In-process**: client uses a `Transport` trait (works for Rust clients)
- **Sidecar**: a thin TCP proxy to capture non-Rust clients (still emits the same IR)

## Bundle format (`*.kafkabundle.zip`)
Top-level:
- `manifest.json` (schema version, producer, redaction policy, broker/client versions)
- `events.ndjson.zst` (canonical IR)
- `artifacts/` (optional pcapng, logs, server properties)
- `diff/` (optional: expected vs observed semantic diff)
- `fixtures/` (scenario + matrix description)

Design goals:
- stable diffs in Git
- easy to attach to issues
- redaction is *policy-driven* and recorded in the manifest

## MVP plan (4–6 weeks)
1. Implement wire parser/encoder for a narrow slice: ApiVersions, Metadata, Produce, Fetch, FindCoordinator
2. Canonical IR + deterministic serializer + redaction policies
3. CLI: `kafkalab capture` (sidecar) + `kafkalab replay` + `kafkalab diff`
4. One reference scenario corpus + golden tests

## De-risking / “how this stays maintainable”
- **Version tables generated** from the upstream protocol description text when feasible (and pinned by commit hash) citeturn0search6
- fuzz: corpus bundles become regression tests
- each new API key adds fixtures + diff rules, not just code

## Existing ecosystem to integrate (not replace)
- Kafka’s official protocol guide as the schema reference citeturn0search6
- existing Rust Kafka clients (adapters), plus Java/Go clients via sidecar capture

