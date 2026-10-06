# Operational time-travel debugging (replay capsules in the ops spine)

DeriveBSD already defines **record/replay debugging as a capability-gated artifact** (`debug.record.grant` → `debug.replay.capsule`).

This doc tightens the *operational* story: how replay capsules plug into **change sets**, **incident bundles**, and the **structured event journal**, so we can capture “heisenbugs” safely (and repeatably) without reinventing ad-hoc debug scripts.

## Why bake this in

Record/replay debugging is a step-function tool (rr-shaped), but most OSes treat it as:

- a local developer trick
- incompatible with privacy constraints
- too hard to share across teams or incidents

DeriveBSD’s evidence-and-leases model is a chance to make “time-travel debugging”:

- **safe by default** (no ambient debug authority)
- **bounded** (time/bytes caps)
- **shareable** (capsules + deterministic redaction receipts)
- **correlatable** (events and change receipts point at the same capsule digests)

## Data model recap

- `debug.record.grant` — authority to record a target under explicit constraints.
- `debug.replay.capsule` — metadata that binds the grant digest to the recorded trace/snapshot digests.
- `debug-event` — structured event-journal records emitted by the debug broker.

See: `docs/194-debugging-by-lease-and-replay-capsules.md`, `rfcs/RFC-0129-debugging-by-lease-and-replay-capsules.md`.

## Where replay capsules attach

### 1) Change sets: “record on failure” hooks

A `change-set` step may optionally carry a **debug hook** that triggers capture **only if the step fails** (or always, for CI).

Key properties:

- the hook references a *pre-approved* `debug.record.grant` (or a policy alias that resolves to one)
- the apply engine can scope the target narrowly (usually the affected service/microVM)
- capsule digests are written into the step’s receipt list

Result: a failing rollout can produce a deterministic replay capsule *without* widening ambient debug privileges.

See: `docs/219-change-sets-and-apply-engine.md`, `spec/change.set.schema.json`.

### 2) Incident bundles: “support bundles with replay”

`incident.bundle` can optionally include replay capsules when:

- a capture grant existed, and
- policy allows inclusion/export

This makes “bundle + replay” the default escalation payload:

- `incident.bundle` contains the normal context (events, svc/fault snapshots, config/state receipts)
- optionally an `incident.timeline` digest for fast human orientation (export-safe by default)
- plus `debug.replay.capsule` digests (and optionally the trace blobs, if export policy allows)

See: `docs/216-incident-snapshots-and-support-bundles.md`, `docs/419-incident-timelines-as-derived-artifacts.md`.

### 3) Structured event journal: debug events are first-class

The debug broker emits `debug-event` records into the structured journal:

- record started/stopped
- capsule emitted
- upload/export requested/denied

These events carry the capsule digest (when present) and can share the **change correlation id**.

See: `docs/215-structured-event-log-as-evidence.md`.

## Privacy posture (non-negotiable)

- Replay capture requires explicit grants (policy or portal), never ambient.
- Replay capsules reference heavy artifacts by digest; export is explicit.
- When export is allowed, use `redaction.transform` + `redaction.receipt` for deterministic, auditable filtering.

See: `docs/195-deterministic-redaction-transforms.md`.

## Practical workflow

1. A change is applied (or a service enters a crash loop).
2. Policy decides whether capture is allowed (and which bounds/targets).
3. `derive-debugd` records and emits a `debug.replay.capsule`.
4. Change receipts and/or incident bundles reference the capsule digest.
5. Humans (or CI) replay deterministically (local rr, cloud processing, etc.) under explicit export rules.

## Prior art and ecosystem hooks

- rr (record/replay + reverse debugging) is the canonical backend for x86_64 userland traces.
- Pernosco demonstrates the “upload trace → interactive omniscient debugger link” workflow.
- Windows TTD shows the same idea as a mainstream debugging primitive.
- ReproZip is a complementary lesson: packaging the *environment and inputs* as a portable bundle.

DeriveBSD’s twist is to treat the resulting artifacts as **evidence objects** that can participate in policy, rollouts, and incident response.

Last updated: 2026-02-27r128
