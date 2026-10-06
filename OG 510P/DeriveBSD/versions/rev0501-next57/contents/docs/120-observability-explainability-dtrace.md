# Observability as explainability: DTrace + auditing (OpenBSM)

DeriveBSD’s promise is not just “reproducible”, but **explainable**:
- why a bit exists
- where it came from
- what it depended on
- what it did at runtime

Build provenance answers the first half. Production debugging and incident response often require the second.

## Why bake this in early

Traditional OSes treat tracing/auditing as an optional afterthought.
For DeriveBSD, observability is part of the security story:
- detect policy violations (unexpected network, unexpected exec)
- bound blast radius with evidence
- provide postmortem artifacts that are digestable and attachable to deployments

## BSD-native primitives worth leaning on

### DTrace (dynamic tracing)

FreeBSD includes DTrace for diagnosing kernel and userspace behavior in production.

Reference:
- FreeBSD Handbook: DTrace: https://docs.freebsd.org/en/books/handbook/dtrace/

DeriveBSD opportunities:
- ship a minimal set of reviewed DTrace scripts as **derived tools** (versioned, signed)
- allow policy-gated “trace capsules” that capture bounded evidence during an incident
- treat observability access as a **capability** (no ambient debug authority)

### OpenBSM auditing

Auditing provides structured records for security-relevant events.

Reference:
- FreeBSD Handbook: Auditing: https://docs.freebsd.org/en/books/handbook/audit/

DeriveBSD opportunities:
- define a baseline audit policy for the host control plane
- attach audit summaries (digests) into `boot.health.report` and deployment records

## Evidence objects (small, replayable)

Evidence should be digestable and attachable:

- `trace.stream.grant`:
  - who/what is observed
  - allowed sources (logs/audit/dtrace)
  - bounds (time/bytes/sampling)
  - lease + expiry
- `trace.capsule`:
  - grant digest
  - time window
  - output digests (raw logs stored separately)
  - optional redaction receipts

- `debug.record.grant`:
  - authority to start a bounded record/replay capture
  - optional redaction profile digest
- `debug.replay.capsule`:
  - record/replay trace digest + side artifacts

- `audit.summary`:
  - count + digests of rotated audit files
  - policy id used

The key is to keep evidence **small by default**, with an escape hatch for “forensics mode” when needed.

Schemas:
- `spec/trace.stream.grant.schema.json`
- `spec/trace.capsule.schema.json`
- `spec/debug.record.grant.schema.json`
- `spec/debug.replay.capsule.schema.json`
- `spec/redaction.transform.schema.json`
- `spec/redaction.receipt.schema.json`

See also: `docs/192-observability-as-capability.md`, `docs/52-host-auditing-openbsm.md`, `docs/112-health-gated-updates.md`.

Last updated: 2026-02-24
