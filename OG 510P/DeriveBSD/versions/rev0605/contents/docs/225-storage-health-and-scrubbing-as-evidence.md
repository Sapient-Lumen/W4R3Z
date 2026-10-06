# Storage health + scrubbing as evidence (ZFS pools / SMART / receipts)

Storage is the substrate that makes “immutable system + explicit state” real.
And yet most OS stacks still treat disk/pool health as:
- strings in logs
- dashboards wired to fragile regex
- surprise data-loss after months of silent checksum errors

DeriveBSD’s advantage is that we can bake storage operations into the **ops evidence spine**:
**inventory → explicit plans → receipts → snapshots → typed events → bounded export**.

This lane is intentionally **metadata-first**:
- safe to include in incident bundles by default
- queryable for health gates and fleet policy
- avoids turning “support bundles” into accidental data exfiltration

## Lessons worth stealing

### ZFS scrub is an integrity primitive, not a chore
A scrub verifies checksums across the pool and (for mirrored/RAIDZ devices) can automatically repair discovered damage.
Treating scrubs as a first-class operation with receipts lets you answer:
- *When did we last verify integrity?*
- *Did we repair anything?*
- *Did errors begin after a specific change-set?*

### ZFS events (ZED/zevents) are a clean signal plane
OpenZFS emits structured events (device faults, resilver progress, scrub completion).
If we route those into the structured event journal as typed events, storage becomes correlatable with:
- rollouts
- service crash loops
- resource pressure

### Pool checkpoints are under-used but perfect for risky maintenance
A `zpool checkpoint` is a pool-wide “rewind point” (not a snapshot) that can be reverted to later.
It’s a great *greenfield* primitive to expose as a policy-gated step for:
- firmware or driver updates
- risky ZFS feature flag changes
- storage topology maintenance

## Evidence objects

### 1) `storage-pool-inventory` (safe inventory)
A privacy-safe inventory snapshot:
- pool names/guids, feature flags, ashift
- vdev topology (mirror/raidz/etc)
- device identity hashes (never raw serials by default)

Schema: `spec/storage.pool.inventory.schema.json`.

### 2) `storage-scrub-plan` (explicit operation plan)
An explicit, signed plan for running integrity checks:
- which pools
- time window + throttling hints
- whether to create a pool checkpoint first (policy-gated)

Schema: `spec/storage.scrub.plan.schema.json`.

### 3) `storage-scrub-receipt` (append-only evidence)
Evidence emitted after scrub execution:
- per-pool outcome (success/failed/partial)
- repaired errors and observed checksum errors
- pointers into the event journal
- correlation to a `change-set` step (if run as part of a change)

Schema: `spec/storage.scrub.receipt.schema.json`.

### 4) `storage-health-snapshot` (health gate input)
A compact health snapshot that answers:
- is the pool ONLINE/DEGRADED/FAULTED?
- are there read/write/checksum errors?
- what was the last scrub outcome and when?
- are any devices reporting poor health signals?

Schema: `spec/storage.health.snapshot.schema.json`.

### 5) `storage-event` (typed journal events)
Typed events in the structured event journal:
- `storage.pool.degraded`
- `storage.scrub.started` / `storage.scrub.completed`
- `storage.resilver.started` / `storage.resilver.completed`
- `storage.checkpoint.created` / `storage.checkpoint.discarded`

Schema: `spec/storage.event.schema.json`.

## Wiring into the ops spine

- **health-gated updates**: allow policy to require a `storage-health-snapshot` check (e.g., block activation on degraded pools or fresh checksum errors).
- **change sets**: add an optional `run-storage-scrub` step referencing a `storage-scrub-plan`.
- **incident bundles**: include `storage-health-snapshot` and recent scrub receipts by default (metadata-only).
- **fault management**: ingest storage-events and snapshots to classify and remediate (disk replacement workflows, resilver tracking).

official support handoff can now carry `storage_scrub_receipt_digests` when integrity verification materially shaped the incident.
That keeps exact scrub / repair proof on the typed bundle contract instead of asking support to reconstruct the story from `zpool status` transcripts, dashboard screenshots, or shell notes.
Keep the split explicit:
- `storage_pool_inventory_digest` says what bounded pool topology / feature posture existed,
- `storage_health_snapshot_digest` says what current health state the host believed at handoff time,
- `storage_scrub_receipt_digests` say which exact bounded integrity-verification action participated.

See: `docs/112-health-gated-updates.md`, `docs/219-change-sets-and-apply-engine.md`, `docs/213-fault-management-architecture.md`,
`docs/215-structured-event-log-as-evidence.md`, `docs/216-incident-snapshots-and-support-bundles.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/635-incident-bundles-carry-storage-scrub-proof-by-digest.md`, RFC-0160.

Last updated: 2026-03-21r365
