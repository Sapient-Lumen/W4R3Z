# Observability as a capability (no ambient debug authority)

DeriveBSD already treats filesystem, networking, and privileged operations as **explicit capabilities**.
Observability must follow the same rule.

If “debug” is ambient authority, it becomes the escape hatch that defeats least-privilege designs.
If “debug” is capability-scoped, it becomes a safe, reviewable tool.

## Goals

- Make tracing/log access **explicitly granted** (policy or interactive portal).
- Keep evidence **small by default**, but forensics-friendly when needed.
- Support both:
  - *operators* (incident response)
  - *developers* (local, interactive workflows)

## Model

### 1) A broker owns the power tools

A host daemon (`derive-traced`) owns privileged observability primitives:

In addition to “raw” tracing, DeriveBSD should expose a **structured event journal** (see `docs/215-structured-event-log-as-evidence.md`).
Trace grants can name specific event streams (service, fault, audit) and time bounds, instead of handing out blanket access to `/var/log/*`.


- DTrace probes/scripts
- OpenBSM audit feeds
- kernel counters
- host log access

Workloads and service compartments never run DTrace directly.

### 2) Access is granted via digest-pinned, time-bounded handles

The standard authorization object is a **trace stream grant**:

- who is requesting / who is targeted
- which signal sources are allowed (logs, audit, DTrace)
- bounds (time window, bytes, sample limits)
- redaction profile (deterministic filters)

Grants are typically leased and revocable.

Evidence objects:

- `trace.stream.grant` (authorization)
- `trace.capsule` (output summary + digests)
- `redaction.transform` (optional deterministic privacy filter)
- `redaction.receipt` (optional proof of applied redaction)

Schemas:
- `spec/trace.stream.grant.schema.json`
- `spec/trace.capsule.schema.json`
- `spec/redaction.transform.schema.json`
- `spec/redaction.receipt.schema.json`

### 3) “Diagnostics routing” is part of the capability graph

Fuchsia treats diagnostics as a routed capability (logs/Inspect are mediated by an archivist).
DeriveBSD should treat observability similarly:

- define explicit graph edges for:
  - “emit logs/metrics to broker”
  - “read logs/metrics/traces from broker”
- lint these edges like any other “danger edge”

This makes it reviewable when a workload gains the ability to observe others.

Reference:
- Fuchsia diagnostics concepts (logs, Inspect, archivist): https://fuchsia.dev/fuchsia-src/concepts/components/diagnostics

## Export and ecosystem interoperability (optional)

When exporting telemetry off-host, treat the exporter as a compartment with explicit egress authority.
Use OpenTelemetry semantics as an interop layer, but keep grants/receipts DeriveBSD-native.

Reference:
- OpenTelemetry specification overview: https://opentelemetry.io/docs/specs/otel/overview/

## Invariants

- No global “debug mode”.
- Observability access is **policy-gated** and **time-bounded**.
- Outputs are sealed as digests (`trace.capsule`) and attachable to incident records.

See also:
- `docs/120-observability-explainability-dtrace.md`
- `docs/189-capability-graph-lint-and-viz.md`
- `docs/179-portals-and-powerbox.md`

Last updated: 2026-02-24
