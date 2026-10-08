---
id: P-0013
title: Connector Kit — typed connector runtime for sources/sinks with test + observability baked in
status: idea
domains: [data, integration, observability, runtime]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/apache/iggy/issues/2753
  - https://iggy.apache.org/blogs/2025/06/06/connectors-runtime/
  - https://crates.io/crates/danube-connect-core
  - https://docs.rs/danube-connect-core/latest/danube_connect_core/index.html
---

## What it should provide others

A framework for writing **production-grade connectors** (sources/sinks) with consistent:
- configuration
- backpressure and batching
- retries and dead-lettering
- metrics + tracing
- integration testing harnesses

Think: “write the business logic of a connector, not the plumbing.”

## Why this is still missing

Rust has excellent building blocks (Tokio, Serde, tracing), but connector authors repeatedly re-implement:
- stateful offset/checkpointing
- retry semantics
- idempotency patterns
- observability wiring
- test harnesses (fault injection, simulated sinks)

Some projects build connector ecosystems and track huge connector roadmaps; a shared kit could reduce duplication.

## Core abstractions

- `SourceConnector`: produces typed records + checkpoints
- `SinkConnector`: consumes records with idempotency + transactional hints
- `Codec`: schema-aware encoding (JSON/Avro/Protobuf adapters)
- `Runtime`: handles concurrency, batching, retries, backpressure
- `Harness`: deterministic integration tests with fault injection

## MVP

1. Runtime skeleton: concurrency + backpressure + retry policies
2. Checkpointing interface + sample implementations
3. Observability: `tracing` + metrics facade, OTel optional feature
4. Reference connectors: HTTP poller (source) + PostgreSQL writer (sink)

## Adoption plan

- Make the runtime usable standalone *or* embeddable in a larger system.
- Provide a “connector cookbook” with patterns: exactly-once-ish, at-least-once, idempotent writes.
