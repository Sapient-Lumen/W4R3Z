# RFC-0150: Structured event journal as evidence (`event.record`, `event.segment`)

Status: Draft

## Summary

Define a host-local, append-only **event journal** with two stable evidence artifacts:

- `event.record` — a common envelope for structured events (service, fault, policy, audit)
- `event.segment` — segment metadata that binds a journal blob to digests and a continuity chain

Require `svc-event` and `fault-event` to conform to the `event.record` envelope so tools can query/export uniformly.

## Motivation

DeriveBSD already treats builds and updates as verifiable artifacts.
Operations data (service state changes, faults, health probes) is equally critical:

- debugging without ambient “read all logs” authority
- health-gated rollout decisions based on *typed* signals
- auditable timelines (what happened, when, and from where)

Most systems bolt this on late and end up with:
- strings instead of data
- inconsistent severities and timestamps
- overbroad log access as an escape hatch

## Design

### 1) Event envelope (`event.record`)

See `spec/event.record.schema.json`.

Requirements for journal-eligible events:

- MUST include `kind`, `event_version`, `at`
- SHOULD include `event_id` (UUID) for correlation
- SHOULD include `source` with `name` and `host_id`
- MAY include integrity fields:
  - `prev_digest` for hash chaining
  - `signature` when policy requires non-repudiation

### 2) Journal segmentation (`event.segment`)

See `spec/event.segment.schema.json`.

A segment is a blob in the store (or state dataset) containing N event records in a fixed encoding.
The segment metadata binds:

- `file_digest` (content hash)
- `merkle_root_digest` (order-independent integrity)
- `chain_head_digest` and `prev_chain_head_digest` (order-dependent continuity)

### 3) Capability-gated access

- Reading events is an observability capability, granted by policy or portal.
- Export adapters must preserve integrity metadata (carry along segment evidence).

## Compatibility

- `svc-event` and `fault-event` schemas are updated to align with the envelope:
  - add `event_id` and `source` where missing
  - standardize timestamp field name to `at`
- Existing logs can be bridged:
  - syslog ingest produces `kind: syslog-line` with a structured payload
  - OTLP export maps `severity_number`, `tags`, and `payload` attributes

## Open questions

- Preferred on-disk encoding: compact binary vs JSONL+compression.
- Retention/GC policy for high-volume streams.
- Whether some streams must always be signed (security/audit).

