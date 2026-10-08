---
id: P-0163
title: Dataflow Ergonomics Workbench Kit
status: idea
domains: [data, streaming, distributed-systems, devtools, conformance, performance]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/TimelyDataflow/timely-dataflow
  - https://crates.io/crates/differential-dataflow
  - https://docs.rs/differential-dataflow
  - https://timelydataflow.github.io/timely-dataflow/
---

# Problem

Rust has world-class low-latency dataflow foundations (**timely dataflow** and **differential dataflow**). But they are *expert tools*: extremely powerful, less approachable for the 80% use case where someone wants to embed incremental/streaming computation inside a service.

Common friction points:

- Steep learning curve: timestamps/frontiers/probes are essential but hard to operationalize.
- Operational ergonomics: “How do I expose metrics?”, “How do I checkpoint state?”, “How do I test deterministically?”, “How do I replay a production failure?”
- Integration gaps: CDC ingestion, schema evolution, state storage/backends, failure artifacts.

We’re missing an **ergonomics + operations layer** that makes dataflow systems usable by ordinary teams without forcing them to become dataflow researchers.

# What it should provide

## 1) A small, opinionated embedding API

A crate that provides:

- A “query graph” builder that maps to timely/differential primitives
- A standard way to:
  - ingest streams (in-memory, Kafka-like adapters later)
  - materialize outputs (in-memory view, RocksDB-backed, or callback)
  - perform incremental updates (UPSERT/delete semantics)

The key is an API shaped around product needs:

- `MaterializedView<K, V>` with snapshot + incremental change feed
- `Ingest<T>` that is explicitly timestamped (but with sensible defaults)
- Backpressure and bounded memory policies

## 2) Deterministic replay artifacts: `dataflowbundle.zip`

A portable “run bundle” that contains:

- `graph.json` (compiled graph plan + version)
- `inputs/` (redacted event log with timestamps)
- `state/` (optional checkpoint or content-hash pointers)
- `outputs/` (expected diffs / checksums)
- `metrics.json` (latency, frontier lag, memory)
- `repro.sh` / `repro.md` (how to replay)

This enables “attach a failing run” in GitHub issues and lets CI re-run it.

## 3) `cargo dataflow` UX

- `cargo dataflow doctor` — sanity checks (time domains, probe usage, memory caps)
- `cargo dataflow bundle` — emit a `dataflowbundle.zip`
- `cargo dataflow replay` — deterministic replay locally/CI
- `cargo dataflow diff` — compare two bundles (perf regressions, output diffs)

## 4) Conformance packs

Curated scenarios:

- windowed aggregations
- joins with late data
- exactly-once-ish ingestion simulation
- watermark semantics and out-of-order handling

Each with golden outputs and invariants.

## 5) A clear “power ladder”

Make it easy to start simple and grow:

- **MVP:** single process, single worker, in-memory state
- **v1:** multi-worker, checkpointing, backpressure, metrics
- **vNext:** pluggable state backends, CDC adapters, distributed runtime considerations

# MVP scope (2–4 weeks)

- Minimal embedding API over timely + differential
- `dataflowbundle.zip` schema v0 + replay harness
- A tiny conformance pack (3–5 scenarios)

# v1 scope (2–3 months)

- Checkpointing interface (trait) + one backend (e.g., RocksDB)
- Metrics integration (OpenTelemetry optional)
- Better failure minimization (shrink input logs)

# Why this is an “epic” crate

It turns a powerful but specialist foundation into a **practical “incremental compute inside your service” platform**, with reproducibility and conformance as first-class design goals.
