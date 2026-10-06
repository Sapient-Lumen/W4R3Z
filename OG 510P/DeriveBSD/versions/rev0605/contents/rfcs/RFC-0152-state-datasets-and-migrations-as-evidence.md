# RFC-0152: State datasets and migrations as evidence

Status: Draft

## Summary

Standardize persistent state management as first-class DeriveBSD artifacts/evidence:

- `statedb` — compiled state database derived from the Plan (declares persistent volumes, schema ids/versions, policies)
- `state-migration-plan` — explicit plan describing schema migrations required between generations
- `state-migration-receipt` — evidence emitted per volume migration (success/failure, snapshot/hold details, pointers)
- `state-snapshot` — runtime view of current volumes and schema versions

Integrate with health-gated updates and incident bundles.

## Motivation

Immutable generations + atomic switch are insufficient when:
- upgrades require schema changes
- rollbacks must be safe for state
- operators need a single authoritative view of state versions

Many systems solve this late with ad-hoc scripts.
DeriveBSD can do better by treating state evolution as:
- explicit
- least-authority
- rollbackable
- explainable (receipts)

## Design

### 1) Compiled state database (`statedb`)

Schema: `spec/statedb.schema.json`.

Produced at Plan/activation compile time.
Declares:
- volumes (dataset identifiers, mountpoints, owners)
- persistence/encryption flags
- schema ids + expected versions
- snapshot requirements

### 2) Migration plan (`state-migration-plan`)

Schema: `spec/state.migration.plan.schema.json`.

A generation transition MAY include a plan describing required migrations.
Properties:
- `from_generation_digest`, `to_generation_digest`
- ordered per-volume steps
- migration artifact digests (scripts/modules) and their required placements
- safety constraints (timeouts, max downtime class)

A plan MUST be explainable and reviewable (diffable, signed).

### 3) Execution model

For each step:

1. Quiesce the relevant service/workload (or run online migration if explicitly declared).
2. Snapshot the dataset and apply a ZFS hold tag.
3. Run migration code in a constrained domain (service jail or microVM) with:
   - preopened dataset handle
   - optional access to event journal emit
4. Emit `state-migration-receipt`.

Failures MUST be handled by:
- stopping the service/workload
- rolling back the dataset to the held pre-snapshot
- leaving the hold in place until explicit operator release
- optionally emitting an `incident.bundle` for context

### 4) Runtime view (`state-snapshot`)

Schema: `spec/state.snapshot.schema.json`.

Produced by the host state manager:
- list volumes + current schema versions
- last migration receipt digests
- red flags (missing volumes, version mismatch)

### 5) Health gate integration

The health gate MAY require:
- `state-snapshot` matches the new generation’s `statedb` expectations
- all required `state-migration-receipt` objects are present and successful

This supports safe auto-rollback semantics.

## Compatibility

- This RFC is ZFS-first but intentionally describes an abstract volume model.
- It does not require a specific migration language; scripts/modules are referenced by digest.

## Open questions

- Whether to require migrations to declare reversibility beyond snapshot rollback.
- How to model online migrations (dual-writer) safely in the evidence model.
- How to represent replication/backup policy in `statedb` without turning it into an orchestrator.
