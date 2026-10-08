---
id: P-0005
title: Telemetry Kit — tracing + OpenTelemetry that is correct by default
status: idea
domains: [observability, tracing, opentelemetry, dx]
last_reviewed: 2026-02-28
evidence:
  - https://github.com/open-telemetry/opentelemetry-rust/issues/1571
  - https://news.ycombinator.com/item?id=42655102
  - https://www.datadoghq.com/blog/monitor-rust-otel/
---

# Problem
Instrumentation is easy to get *almost* right and then ship inconsistent traces/metrics/logs. Rust also has two prominent tracing APIs (Tokio `tracing` and OpenTelemetry’s tracing API) with ongoing alignment questions.

# Users & user stories
- Platform teams: “One sanctioned way to do telemetry across services.”
- App teams: “Add env-var config and get correct exports without reading 10 docs.”
- Library authors: “Emit spans/events that map cleanly to OTel.”

# Prior art (and why it’s insufficient)
- Individual crates exist (tracing, opentelemetry, exporters), but integration remains easy to misconfigure, and cross-API alignment is still debated.

# Design goals
- A “one-liner” init that supports:
  - OTLP exporter (grpc/http)
  - structured logs
  - trace context propagation
  - resource detection (service.name, version, env)
- Opinionated defaults, but configurable.
- Feature-flagged exporters to keep dependencies slim.
- A compatibility layer that maps `tracing` spans to OTel correctly.

# Non-goals
- Replacing the OpenTelemetry SDK.
- Vendor-specific SDK features.

# Architecture & API sketch
- `telemetry-kit` (high-level facade)
- `telemetry-kit-core` (config schema, env parsing, resource detection)
- `telemetry-kit-exporters/*` (otlp, stdout, etc.)

Example:
```rust
telemetry_kit::init_from_env()
  .with_service("payments")
  .with_version(env!("CARGO_PKG_VERSION"))
  .install()?;
```

# Security / safety model
- Avoid exporting sensitive fields by default (PII guards, attribute allow/deny lists).
- Safe parsing of env vars and endpoints.

# Maintenance & governance plan
- Track OTel spec changes explicitly.
- Provide a “semantic conventions” module pinned to versions.

# Milestones
- 0.1: traces + logs to OTLP with sane defaults
- 0.2: metrics + exemplars
- 0.3: propagation + middleware for common web frameworks
- 1.0: stability + conformance checks

# Sources
- https://github.com/open-telemetry/opentelemetry-rust/issues/1571
- https://news.ycombinator.com/item?id=42655102
- https://www.datadoghq.com/blog/monitor-rust-otel/
