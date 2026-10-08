---
id: P-0118
title: Telemetry Schema Lint & Semantic Conventions Kit (OTel + tracing)
status: idea
domains: [observability, devtools, telemetry, standards]
last_reviewed: 2026-03-05
evidence:
  - https://opentelemetry.io/docs/specs/otel/logs/
  - https://opentelemetry.io/docs/concepts/signals/logs/
  - https://docs.rs/tracing-opentelemetry
  - https://github.com/open-telemetry/opentelemetry-rust
---

# Problem

Rust teams instrument with `tracing`, then attempt to export to OpenTelemetry.
The *mechanics* exist (layers/exporters), but the chronic pain is **schema drift**:

- span/field names vary between services,
- log attributes are inconsistent (hard to query/alert),
- semantic conventions adoption is partial,
- correlation (logs ↔ traces ↔ metrics) is unreliable without discipline.

Most orgs end up building internal linters and dashboards to enforce “good telemetry”.
The ecosystem is missing a crate that makes this easy and portable.

# What it should provide other people

## 1) A telemetry schema definition

A lightweight `telemetry.schema.toml` (or JSON) that declares:
- required spans/events (by name pattern),
- required attributes + types,
- allowed values / enum sets,
- redaction rules,
- semantic convention mappings (OTel keys),
- correlation requirements (trace/span IDs in logs, resource attributes).

## 2) A cargo-native linter + test harness

- `cargo telemetry lint` — static linting over code + config (best-effort)
- `cargo telemetry test` — runtime harness that asserts emitted telemetry matches schema
- `cargo telemetry doctor` — help wiring tracing → OTel, validate exporters and env vars

Stable outputs:
- `telemetry-lint.json` (violations, severity, file/line when possible)
- `telemetry-sample.jsonl` (captured spans/logs, sanitized)
- `telemetry-report.json` (summary + semantic convention coverage score)

## 3) Capture + replay bundles

A `*.telemetrybundle.zip` for bug reports/PRs:
- captured telemetry sample,
- schema,
- normalization transforms,
- diff against previous baseline.

## 4) “Semantic conventions bridge” helpers

- macros/helpers to map `tracing` fields into OTel attribute keys,
- optional “strict mode” layer that rejects unknown keys in CI.

# MVP (4–6 weeks)

- Define schema format and a small default “best practices” profile.
- Implement runtime capture harness:
  - use a `tracing` subscriber to capture spans/events,
  - validate against schema,
  - export `telemetry-sample.jsonl` + `telemetry-report.json`.
- Provide a minimal linter:
  - check for required span names (regex over `tracing::span!` sites where possible),
  - check for required keys appearing in captured samples.

# v1 (8–16 weeks)

- Baseline management (`telemetry.baseline.jsonl`) + diff reports.
- Semantic conventions coverage scoring and recommendation output.
- Integration helpers for common stacks:
  - `axum`, `tonic`, `reqwest`, `sqlx` instrumentation patterns.

# Conformance & testing

- Golden fixtures for captured telemetry.
- Property tests for schema parsing and normalization.
- Compatibility tests across `tracing-opentelemetry` versions and OTel SDK versions.

# Notes

OpenTelemetry’s logs model emphasizes correlated signals via resource context and IDs; this kit makes that enforceable at the Rust crate/workspace level, without requiring every org to reinvent telemetry governance.

