# Debugging by lease: replay capsules (time-travel without ambient authority)

DeriveBSD should make *high-leverage debugging* possible **without** reintroducing ambient authority.

Record/replay debugging (rr-shaped “time-travel”) is one of the most powerful debugging techniques,
but in most ecosystems it remains bespoke tooling rather than a first-class operational primitive.

DeriveBSD can bake in the missing pieces:

- **explicit authority** (recording is privileged; it must be granted)
- **bounded capture** (duration/bytes caps)
- **portable artifacts** (shareable replay capsules)
- **privacy by construction** (deterministic redaction transforms)

## Goals

- Enable deterministic reproduction of “heisenbugs” and race conditions.
- Prefer to *reduce capture needs* by using deterministic execution lanes where possible (deterministic scheduling makes replay capsules smaller). See: `docs/377-deterministic-concurrency-lane.md`.
- Produce a small, shareable artifact: a **replay capsule**.
- Make recording access policy/portal-gated and time-bounded.
- Keep secrets out by default; allow for forensics mode with explicit consent.

## Model

### 1) A broker owns recording and capture

A host daemon (`derive-debugd`) owns privileged capture operations:

- start/stop recording for a target (process tree, jail, microVM)
- collect bounded side artifacts (coredump, stacks, selected logs)
- seal outputs by digest and emit a capsule

### 2) Recording requires an explicit grant

The standard authorization object is **`debug.record.grant`**:

- target selectors (pid/jail/microVM/workload)
- recording mode (rr-style userland, or microVM snapshot/replay)
- bounds (time/bytes)
- optional redaction profile digest

Schema: `spec/debug.record.grant.schema.json`

### 3) Output is a replay capsule

A **`debug.replay.capsule`** binds:

- the grant digest
- the recording artifact digest (rr trace or snapshot log)
- side artifacts (coredump digest, log digests)
- optional time/entropy snapshot digest (if virtualized)
- redaction receipts (if any)

Schema: `spec/debug.replay.capsule.schema.json`

### 4) Redaction is deterministic and auditable

Any privacy filtering MUST be expressed as a hashable, signed transform:

- `redaction.transform` (profile/module)
- `redaction.receipt` (input digest → output digest under transform)

See: `docs/195-deterministic-redaction-transforms.md`.

## Invariants

- Recording is never ambient; it always requires a grant (policy or portal).
- Capsules reference heavy data by digest; exports are explicit.
- Cross-compartment debug requires **leases** and **consent receipts**.

See also:
- `docs/220-operational-time-travel-debugging.md` (how replay capsules plug into change sets, incident bundles, and the event journal)
- `docs/192-observability-as-capability.md`
- `docs/182-capability-leases-and-revocation.md`
- `docs/197-time-and-rng-authority.md`
- `docs/185-portal-consent-and-audit-receipts.md`

Last updated: 2026-02-27r107
