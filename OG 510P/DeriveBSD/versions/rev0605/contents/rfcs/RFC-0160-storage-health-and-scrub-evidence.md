# RFC-0160: Storage health + scrubbing as evidence (inventory / scrub-plan / scrub-receipt / snapshots)

Status: draft  
Last updated: 2026-02-24

## Problem
Storage failures are rarely “sudden.” They are often preceded by:
- checksum errors
- slow or flapping devices
- degraded redundancy
- missed integrity verification (no scrubs for months)

Ecosystems fail here because the signal is fragmented:
- `zpool status` strings
- ad-hoc SMART scripts
- vendor tools
- incident bundles that accidentally include data

DeriveBSD should treat storage operations and health as **typed evidence**, so health gates and incident response can reason on stable objects.

## Goals
- Define a metadata-first storage evidence lane:
  - `storage-pool-inventory`
  - `storage-health-snapshot`
  - `storage-scrub-plan`
  - `storage-scrub-receipt`
  - `storage-event`
- Make the default safe:
  - inventories/snapshots/receipts are safe to share
  - no raw file data is ever included
  - device identifiers are hashed by default
- Integrate with the ops spine:
  - optional `run-storage-scrub` change-set step
  - incident bundles include storage health evidence by default
  - health-gated updates can consult storage snapshots
  - fault manager consumes storage events

## Non-goals
- Mandating ZFS as the only storage backend.
  - The lane is ZFS-first, but the evidence model is backend-agnostic.
- Replacing full observability tooling.
  - This lane focuses on high-signal storage health and integrity operations.

## Artifacts

### `storage-pool-inventory`
Safe inventory snapshot of pools and vdev topology.

Schema: `spec/storage.pool.inventory.schema.json`.

### `storage-health-snapshot`
Health snapshot used for health gates, diagnosis, and incident bundles.

Schema: `spec/storage.health.snapshot.schema.json`.

### `storage-scrub-plan`
Explicit plan to run scrubs with optional window/throttle and optional pool checkpoint creation.

Schema: `spec/storage.scrub.plan.schema.json`.

### `storage-scrub-receipt`
Append-only evidence emitted after scrub execution.

Schema: `spec/storage.scrub.receipt.schema.json`.

### `storage-event`
Typed journal event for storage milestones and faults.

Schema: `spec/storage.event.schema.json`.

## Integration points
- `derive apply` may:
  - generate or fetch a `storage-scrub-plan`
  - execute scrubs via supervised storage agents
  - emit `storage-scrub-receipt`
  - emit `storage-event` into the structured event journal
- Incident bundles should include:
  - `storage-health-snapshot` digest
  - recent `storage-scrub-receipt` digests
  - (optional) `storage-pool-inventory` digest

## Open questions
- Should we define a dedicated `storage-policy` object, or keep policy expressed via the global policy engine?
- Do we want a first-class “device health” sub-object (SMART/NVMe log summaries) or keep it embedded in `storage-health-snapshot`?
- How should pool checkpoint creation be exposed:
  - explicit plan field (v1)
  - dedicated `storage-checkpoint-plan`/receipt (v2)

