# RFC-0129: Debugging by lease (record/replay) + replay capsules

Status: **draft**

## Motivation

Record/replay debugging is a rare “step-function” productivity tool.
It turns nondeterministic failures into deterministic ones and enables reverse execution.

In most ecosystems it remains:

- bespoke tooling
- hard to operate safely
- hard to share without shipping secrets

DeriveBSD’s capability-first design is a chance to make record/replay
**operationally safe** and **artifact-shaped**.

## Goals

- Define a standard grant for privileged recording.
- Define a standard capsule format for shareable replay artifacts.
- Make redaction deterministic and auditable.
- Integrate with portals/leases/consent for interactive debugging.

## Non-goals

- Mandating a single recording backend.
- Solving full “flight recorder” observability.
- Shipping secrets by default.

## Proposal

### 1) Brokered recording

Introduce `derive-debugd`:

- owns privileged capture and recording operations
- exposes a narrow RPC surface
- requires a `debug.record.grant` to start recording
- emits a `debug.replay.capsule` when complete

### 2) Evidence object: `debug.record.grant`

Schema: `spec/debug.record.grant.schema.json`

Fields (v0.1):

- `kind`, `grant_version`
- `lease_id` (optional but recommended)
- `target` selectors (pid/jail/microVM/workload)
- `mode` (e.g., `rr`, `microvm-snapshot`)
- `constraints`:
  - `max_duration_seconds`
  - `max_bytes`
  - `include_coredump` (optional)
  - `redaction_profile_digest` (optional)
- `context`:
  - `plan_digest`, `policy_snapshot_digest`, `policy_decision_digest`
  - `incident_id`
- `issued_at`, `expires_at`
- `signature`

### 3) Evidence object: `debug.replay.capsule`

Schema: `spec/debug.replay.capsule.schema.json`

Represents the recorded artifact and its sealed attachments:

- binds to `debug.record.grant` digest
- records recording digest(s) and side artifacts
- can include `redaction` receipts

### 4) Integration with portals and consent

Interactive “start recording” should usually flow through:

- `portal.grant` (lease) + `portal.consent` receipt
- then `debug.record.grant`

This keeps privilege decisions visible and auditable.

### 5) Redaction integration

When privacy filtering is needed:

- `redaction.transform` defines deterministic rules/modules
- `redaction.receipt` binds input/output under that transform

(Defined in RFC-0130.)

## References

- rr (record/replay, reverse debugging): https://rr-project.org/
- rr repo: https://github.com/rr-debugger/rr
