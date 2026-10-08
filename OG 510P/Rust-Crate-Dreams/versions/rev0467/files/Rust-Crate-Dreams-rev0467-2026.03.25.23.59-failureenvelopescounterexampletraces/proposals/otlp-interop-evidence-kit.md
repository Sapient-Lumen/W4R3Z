---
id: P-0270
title: OTLP (OpenTelemetry Protocol) Interop & Evidence Kit (otlpbundle)
status: idea
domains: [observability, telemetry, networking, interop, testing]
last_reviewed: 2026-03-05
evidence:
  - https://opentelemetry.io/docs/specs/otlp/
  - https://opentelemetry.io/docs/specs/semconv/otel/sdk-metrics/
  - https://crates.io/crates/opentelemetry
  - https://crates.io/crates/opentelemetry-otlp
  - https://crates.io/crates/opentelemetry-proto
---

## What it should provide others

A practical way to validate and debug OTLP pipelines by producing **portable evidence bundles** for:

- SDK exporters (Rust and others, via adapters)
- collectors / gateways
- backends with OTLP ingestion
- test harnesses and CI systems

The kit makes “why did telemetry disappear?” problems reproducible without shipping production data.

## Why this is needed

OTLP defines encoding/transport for traces/metrics/logs, and supports partial success semantics; in practice, backends and collectors differ in:
- which signals/fields they accept
- error/partial-success handling
- compression, limits, and retry expectations

The result is brittle integrations that are hard to reproduce across environments.

## Design sketch

### Workspace layout

- `otlpbundle` — schema + redaction + IO
- `otlp-ir` — canonical representation of:
  - Export*ServiceRequest/Response (protobuf decoded)
  - transport metadata (grpc/http, compression, headers allowlist)
  - partial success details + normalized error categories
- `otlpcapture` — capture backends:
  - in-process exporter shim (wrap `opentelemetry-otlp`)
  - proxy capture (collector sidecar mode)
- `otlpreplay` — replay to collector/backend with deterministic pacing
- `otlpverify` — conformance checks:
  - schema validity
  - semantic conventions *as test profiles* (optional)
  - partial-success accounting (“rejected items count as failures”)

### Evidence bundle format: `*.otlpbundle.zip`

- `manifest.json` (signal types, versions, transport, limits)
- `trace.otlpir.jsonl` (requests/responses in canonical form)
- `profiles/` (optional) acceptance rules + semconv pin
- `reports/` explain outputs (drop reasons, rejection counts, invalid fields)
- `redaction.json` (field hashing, attribute allowlists)

## MVP (4–8 weeks)

1. Decode/encode OTLP protobufs into canonical IR + bundle IO
2. Capture adapter for `opentelemetry-otlp` exporter path
3. Replay to an OTLP endpoint and compare:
   - HTTP/gRPC status + response bodies (including partial success)
   - rejection counts and error summaries
4. 6 scenario fixtures:
   - minimal traces/metrics/logs
   - oversized attribute sets (limit behavior)
   - invalid field injection (validator behavior)
   - partial success responses

## De-risking plan

- Keep profiles optional: ship a “strict spec” profile and a “tolerant” profile.
- Redaction defaults: hash attribute values, truncate payloads, drop exemplars by default.

## Related work / overlap

This complements, not replaces, SDKs and the collector: it provides the missing **test/evidence layer** around OTLP’s real-world interoperability surface.
