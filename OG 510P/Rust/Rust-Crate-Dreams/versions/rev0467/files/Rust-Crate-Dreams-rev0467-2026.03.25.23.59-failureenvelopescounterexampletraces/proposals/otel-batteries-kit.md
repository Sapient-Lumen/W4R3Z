---
id: P-0077
title: OTel Batteries Kit — one “right way” to ship tracing/metrics/logs with Rust
status: idea
domains: [observability, tracing, opentelemetry, diagnostics, tooling]
last_reviewed: 2026-03-04
evidence:
  - https://opentelemetry.io/docs/languages/rust/getting-started/
  - https://docs.rs/tracing-opentelemetry
  - https://github.com/open-telemetry/opentelemetry-rust/issues/3376
---

## Problem
The building blocks exist (`tracing`, `tracing-opentelemetry`, OpenTelemetry SDK crates), but the ecosystem lacks a **cohesive, low-friction, convention-driven kit** that makes “instrumentation done right” the default.

Teams repeatedly re-discover:
- which propagators/exporters to use
- how to map `tracing` spans/events to OTLP in a consistent way
- how to apply semantic conventions and resource attributes
- how to debug missing context / partial traces
- how to choose stable vs experimental feature flags

## Thesis
Observability should feel like a **standard runtime service**:
- consistent across crates
- easy to adopt incrementally
- safe defaults with explicit escape hatches
- strong diagnostic UX (“doctor” tooling)

## What it should provide (MVP)
### 1) `otel_batteries::install()` with profiles
- `dev()`, `staging()`, `prod()` presets:
  - sampling
  - span limits
  - batch/export configuration
  - log correlation
- Env-var override layer (12-factor friendly)

### 2) Conventions module
- HTTP server/client
- DB operations
- messaging (publish/consume)
- background jobs / scheduled tasks
- error recording guidelines

### 3) Propagation & context correctness
- default propagators + per-request extraction/injection helpers
- a small “context audit” mode that can warn on common mistakes

### 4) `cargo otel doctor`
- scans dependency graph + enabled features
- warns about conflicting global subscribers
- checks that the chosen exporters are actually wired and emitting
- suggests fixes

## Non-goals (initially)
- Competing with the OpenTelemetry spec process
- Providing a custom collector; rely on OTLP exporters

## “Epic” extension ideas
- Golden OTLP fixtures + conformance tests for common frameworks (`axum`, `tower`, `tonic`, `sqlx`)
- Integration test harness that runs a collector and asserts on emitted telemetry
- A lightweight “trace diff” tool for regressions in span shape/attributes
