---
id: P-0140
title: Perfetto Trace Workbench Kit — cargo-native performance tracing with shareable trace bundles
status: idea
domains: [profiling, tracing, devtools, performance, observability]
last_reviewed: 2026-03-05
evidence:
  - https://perfetto.dev/docs/reference/trace-packet-proto
  - https://perfetto.dev/docs/quickstart/traceconv
  - https://docs.rs/tracing-perfetto/latest/tracing_perfetto/
  - https://crates.io/crates/perfetto-writer
needs:
  - Make high-fidelity performance traces easy to capture, view, diff, and share across teams.
  - Bridge the gap between “tracing spans” and “system-level timelines” without bespoke tooling.
  - Provide a stable artifact format for bug reports and CI regressions.
risks:
  - Trace size and overhead (need sampling, rate limits, and redaction).
  - Cross-platform capture nuances (Linux/macOS/Windows; container/CI).
  - Schema stability (Perfetto protobuf evolves; need versioning and compatibility shims).
---

## Problem

Rust has strong building blocks for instrumentation (`tracing`) but performance investigations often devolve into ad-hoc stacks: a profiler here, a bespoke JSON trace there, a different UI per team. Meanwhile, Perfetto offers a powerful browser-based UI and a native protobuf format built around a linear stream of `TracePacket`s, plus conversion tooling (`traceconv`) and guidance for synthetic traces.  
Sources: https://perfetto.dev/docs/reference/trace-packet-proto , https://perfetto.dev/docs/quickstart/traceconv

The ecosystem has emerging pieces (`tracing-perfetto`, `perfetto-writer`) but lacks a cohesive, cargo-native “golden path” that produces shareable trace artifacts and supports CI workflows.

## What this crate should provide

A **workbench** (library + CLI) that standardizes “capture → package → view → compare → share” for Perfetto traces:

1. **`cargo perfetto capture`**  
   - Run a command under tracing capture (via `tracing` layer) and write Perfetto protobuf.
   - Config presets: `cpu-light`, `io-light`, `async-tasks`, `render`, `db`, `custom`.
   - Controls: sampling, buffer size, duration, rate limits, “privacy levels” (redaction).

2. **`cargo perfetto bundle`** (the collaboration unit)  
   Produces a single `*.perfettobundle.zip` containing:
   - `trace.pftrace` (protobuf)
   - `bundle.json` (tool versions, config preset, schema versions, platform fingerprint)
   - optional `symbols/` (if enabled) and `notes.md` (user-provided context)
   - optional `traceconv/` derivatives (e.g., JSON for quick diffs)

3. **`cargo perfetto open`**  
   - Opens the trace in Perfetto UI (local file), with sanity checks and hints.

4. **`cargo perfetto diff`**  
   - CI-friendly “summary diff”: span durations, thread/track utilization, key counters.
   - Outputs `perfetto-report.json` (stable schema) for dashboards.

## Users & user stories

- **Library maintainer**: “A user filed a perf regression; I want a trace bundle I can open, reproduce, and diff.”
- **Embedded/devices**: “We need a low-overhead timeline of task execution on constrained systems.”
- **CI owner**: “Fail PRs that regress P95 latency or introduce new long spans on critical code paths.”

## Prior art (and why it’s insufficient)

- **Perfetto native format & docs**: the capabilities exist, but integration patterns are scattered.  
  Sources: https://perfetto.dev/docs/reference/trace-packet-proto , https://perfetto.dev/docs/quickstart/traceconv
- **`tracing-perfetto`**: outputs Perfetto traces but doesn’t define the ecosystem workflow, bundle formats, and CI diffing contracts.  
  Source: https://docs.rs/tracing-perfetto/latest/tracing_perfetto/
- **`perfetto-writer`**: low-level building block; needs a “workbench” layer with defaults and artifact conventions.  
  Source: https://crates.io/crates/perfetto-writer

## MVP plan (2–4 weeks)

- Implement `cargo perfetto capture` with:
  - tracing layer → Perfetto protobuf file
  - 2 presets (`cpu-light`, `async-tasks`)
  - `*.perfettobundle.zip` emitter (trace + bundle.json)
- Provide a small Rust example app + CI job that generates and uploads the bundle on perf failures.
- Add a `bundle.schema.json` and validate on emit.

## v1 plan (6–10 weeks)

- `diff` report: stable metrics extraction (top spans, critical path approximation, track utilization).
- Redaction: deterministic hashing for string fields + allowlist/denylist filters.
- Toolchain adapters: `tokio-console` correlation hints; `pprof` import as track (optional).

## Conformance & testing

- Golden corpus of small traces and expected `perfetto-report.json`.
- Fuzzing: protobuf decoding/encoding and bundle ingestion.
- Compatibility matrix: Perfetto UI (web) sanity tests + traceconv conversions.

## Adoption strategy

- Start as a **cargo subcommand + small library**; keep hooks runtime-agnostic.
- Provide copy-paste GitHub Actions step: “capture perfetto bundle on failing perf test”.
