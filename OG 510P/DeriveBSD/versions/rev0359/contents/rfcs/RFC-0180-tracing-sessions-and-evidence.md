# RFC-0180: Tracing sessions as evidence

Status: Draft

## Problem

Dynamic tracing is often treated as “admin magic” rather than an auditable workflow.
In DeriveBSD, debug authority must be explicit, leased, and explainable.

## Goals

- Make tracing requests a typed artifact (`trace.session`).
- Run tracing under an authority lease (debug grant / breakglass).
- Capture outputs as evidence objects.
- Enable bundling and causal linking.

## Proposal

1) Introduce `trace.session` spec.
2) Introduce `trace.receipt` emitted on start/stop.
3) Introduce `trace.output` metadata objects.
4) Extend incident bundles to include trace digests.

## Safety constraints

- Default to aggregate / low-volume outputs.
- Require scope and duration bounds.
- Integrate deterministic redaction transforms for export.

## Implementation sketch

- `derive trace run session.json`:
  - validates session
  - obtains debug lease
  - runs dtrace/bpf tool in confined helper
  - stores outputs + emits receipts/events

References:
- `docs/248-tracing-observability-as-evidence.md`
