---
id: P-0091
title: Observability Workbench Kit — cargo-native tracing + async console + profiler wiring with strong defaults
status: idea
domains: [devtools, observability, profiling, async, production]
last_reviewed: 2026-03-05
evidence:
  - https://github.com/tokio-rs/console
  - https://tokio.rs/tokio/topics/tracing
  - https://crates.io/crates/pprof
  - https://github.com/grafana/pyroscope-rs
  - https://grafana.com/docs/pyroscope/latest/configure-client/language-sdks/rust/
---

## Problem
Rust has excellent low-level observability components (`tracing`, Tokio Console, profilers like `pprof`),
but many teams still experience a Go-like gap: “one standard, trivial, batteries-included way”
to turn on useful diagnostics and performance insight in dev/CI/prod.

Common pain:
- everyone hand-rolls subscriber layers and env filters
- runtime task visibility is inconsistent across services
- CPU profiling, heap profiling, and continuous profiling feel like separate worlds
- docs exist, but the *default wiring* is not standardized

## What it provides
A crate family + `cargo` subcommand that gives other people:

1) **One-line instrumentation**
   - `obs::init()` with safe defaults (json logs optional, env-filter, span fields)
   - feature flags for common exporters/backends

2) **`cargo obs doctor`**
   - checks common misconfigs (missing `RUST_LOG`, no spans, console layer mismatch)
   - prints actionable fixes + a “known-good” minimal snippet

3) **Async runtime visibility**
   - turnkey Tokio Console layer enablement (when using Tokio)
   - graceful degrade on non-Tokio runtimes (no hard lock-in)

4) **Profiling workflows**
   - `cargo obs profile cpu -- 30s` produces a standardized bundle:
     - `profile.pb.gz` (pprof-compatible)
     - `meta.json` (build info, features, git rev)
   - optional continuous profiling integration with Pyroscope agent backends

5) **Shareable diagnostics bundles (`.obs.zip`)**
   - logs + span summaries + task stats (if available) + profiles (if captured)
   - stable schema so teams can attach bundles to issues/PRs

## Users & user stories
- **Service engineer:** “I want a known-good tracing setup and a way to collect a profile in one command.”
- **SRE:** “I want standardized artifacts I can ingest and compare across services.”
- **Library author:** “I want to emit `tracing` spans and be confident users can see them easily.”

## Prior art (and why it’s insufficient)
- Tokio Console provides async task/resource diagnostics via a toolkit of components. The missing piece is *standardized, cargo-native packaging* plus defaults that interop cleanly with profiling and export targets.  
- `tracing` docs explain how to instrument and configure, but do not impose a single “blessed wiring” for teams.  
- `pprof` and Pyroscope agent integrations exist, but adoption is fragmented.

## Design sketch
### Layered architecture
- `obs-core`: init + config schema + env + bundle writer
- `obs-tokio-console`: optional features for console wiring
- `obs-profiler`: optional CPU profiling hooks (pprof), plus “capture bundle” CLI

### Config model
- `obs.toml` or env-first config:
  - log format, filters, sampling, exporter endpoints
  - “privacy knobs” (redaction allow/deny lists)

### Conformance
- “golden bundle” tests:
  - spawn a small async workload, ensure `.obs.zip` contains expected schema fields
  - schema version tests for forward compatibility

## MVP scope
- `obs::init()` + sane defaults
- `cargo obs doctor`
- `cargo obs profile cpu` using `pprof`
- `.obs.zip` bundle format v0

## v1 scope (epic)
- continuous profiling hooks (Pyroscope)
- task visibility dashboards (console-first; allow alternatives)
- log+trace correlation helpers and redaction policies

## Risks & tradeoffs
- Too opinionated: mitigate via profiles (dev/prod) and documented escape hatches.
- Backend churn: keep bundle schema stable; treat exporters as plugins.

## Why this is “epic”
It turns Rust observability from “assemble your own wiring diagram” into a predictable, shareable workflow with standardized artifacts and great defaults.
