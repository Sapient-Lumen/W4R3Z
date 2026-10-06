# RFC-0127: Observability as capability (trace/log authority without ambient access)

Status: **draft**

## Motivation

DeriveBSD’s security story depends on least authority.
Observability is one of the easiest places for ecosystems to regress:

- “just give ops root”
- “just mount /var/log everywhere”
- “just enable global tracing in prod”

These approaches create ambient authority and undermine compartment boundaries.

## Goals

- Define a standard grant object for observability access.
- Make observability access time-bounded and reviewable.
- Produce small, digestable evidence outputs suitable for incident attachments.
- Allow interactive workflows through portals without weakening the baseline.

## Non-goals

- Designing a full telemetry system.
- Mandating a specific backend (OpenTelemetry is an interop layer, not a requirement).
- Exposing privileged tracing directly to workloads.

## Proposal

### 1) Brokered observability

Introduce `derive-traced` (host daemon):

- owns privileged tracing primitives (DTrace, audit feed access)
- exposes a narrow RPC surface
- requires a `trace.stream.grant` to open a stream

### 2) Evidence object: `trace.stream.grant`

Schema: `spec/trace.stream.grant.schema.json`

Fields (v0.1):

- `kind`, `grant_version`
- `lease_id` (optional but strongly preferred)
- `target` (selectors: jail id, pid, microVM id, workload identity)
- `sources[]` (logs, audit, dtrace)
- `constraints`:
  - `max_duration_seconds`
  - `max_bytes`
  - `sample_rate` (optional)
  - `redaction_profile` digest (optional)
- `context`:
  - `plan_digest`, `policy_snapshot_digest`, `policy_decision_digest`
- `issued_at`, `expires_at`
- `signature`

### 3) Evidence object: `trace.capsule`

Schema: `spec/trace.capsule.schema.json`

Represents the output summary of a granted stream:

- binds to `trace.stream.grant` digest
- records window and output digests
- optionally records a summary for fast triage (counts, top events)

### 4) Policy integration

Add optional trust policy parameters:

- `observability.allowedSources`
- `observability.maxDuration`
- `observability.maxBytes`
- `observability.allowedRedactionProfiles`

Policy decision records SHOULD include:

- grant digest
- reason tag (incident id / ticket id)

### 5) Graph integration

Add capability-graph edge types:

- `emit:logs` / `emit:metrics` to broker
- `read:logs` / `read:audit` / `read:dtrace` from broker

Lint rules can then gate:

- cross-compartment read edges
- broker egress edges (telemetry export)

## References

- OpenTelemetry spec overview: https://opentelemetry.io/docs/specs/otel/overview/
- Fuchsia diagnostics capability model: https://fuchsia.dev/fuchsia-src/concepts/components/diagnostics
