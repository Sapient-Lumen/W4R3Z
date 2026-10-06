# State datasets + migrations as evidence (Bottlerocket / OSTree / ZFS-hold lessons)

Immutable host generations are only half the story.
The other half is **state**: per-service and per-workload data that must survive upgrades.

Most ecosystems discover (painfully) that “just upgrade the binary” becomes:
- hidden schema changes
- brittle one-off migration scripts
- rollbacks that boot but leave state corrupted

DeriveBSD can bake the missing primitive in early:
**treat state evolution as a policy-governed, evidence-producing workflow.**

## Prior art worth stealing

- **Bottlerocket** runs *settings migrations* sequentially across skipped versions during update.
  That is: you don’t need to upgrade one version at a time, but the system still runs every migration step in order.
  Reference: https://bottlerocket.dev/en/os/1.52.x/update/guidelines/

- **OSTree / image-mode systems** separate “immutable base” from mutable `/etc` and `/var`, and must define how changes carry forward.
  The key lesson is not the exact layout, but that **mutable directories need an explicit model**.
  References: https://bootc-dev.github.io/bootc/filesystem.html , https://ostreedev.github.io/ostree/var/

- **ZFS holds** prevent accidental deletion of “known good” snapshots.
  A hold turns “we took a snapshot” into “we can’t delete it by mistake until we release it”.
  References: https://man.freebsd.org/cgi/man.cgi?query=zfs-hold , https://docs.oracle.com/en/operating-systems/solaris/oracle-solaris/11.4/manage-zfs/holding-zfs-snapshots.html

## DeriveBSD direction

### 1) Persistent state is declared, not implied

A host generation should carry a compiled description of all persistent datasets it expects:

- per-workload state datasets (e.g. `vm/<id>/state`)
- per-service host state datasets (e.g. `system/keys`, `system/journal`)
- their schema identifiers + expected versions
- snapshot and retention requirements

Evidence object: **`statedb`** (compiled from the Plan).

See: `spec/statedb.schema.json`.

### 2) State upgrades are explicit artifacts

A new generation MAY require state migrations.
Those migrations should be represented as a **migration plan**:

- which volumes are affected
- from → to schema versions
- the migration artifact digest (script/module)
- timeouts, placement domain, and safety knobs

Evidence object: **`state-migration-plan`**.

See: `spec/state.migration.plan.schema.json`.

### 3) Every migration yields a receipt (and is rollbackable)

Before running a migration:

1. Take a **pre-migration snapshot** of the dataset.
2. Apply a **ZFS hold** with an explicit tag (so it cannot be destroyed accidentally).
3. Run the migration in a tight compartment (service jail or microVM) with only the needed capabilities.

On completion, emit a **receipt**:
- dataset id + schema from/to
- snapshot name + hold tag
- the migration artifact digest
- a pointer to event journal segments / logs
- success/failure + error classification

Evidence object: **`state-migration-receipt`**.

See: `spec/state.migration.receipt.schema.json`.

If the migration fails, rollback is:
- stop the service/workload
- rollback dataset to the pre-snapshot
- keep the held snapshot until an operator explicitly releases it
- optionally produce an `incident.bundle`

### 4) Runtime visibility: state snapshot

Operators need a single view of “what schema versions are actually present”.

Evidence object: **`state-snapshot`** (runtime state view, like `svc.snapshot`).

See: `spec/state.snapshot.schema.json`.

## Invariants worth making non-negotiable

- **No implicit migrations**: upgrading a workload image never mutates persistent state unless a `state-migration-plan` exists.
- **Version skipping is safe**: a plan can chain migrations, and activation runs them sequentially (Bottlerocket lesson).
- **Rollback safety beats cleverness**: snapshot + hold is the default rollback strategy.
- **Migrations are least-authority**: migration code runs with a preopened dataset handle and nothing else.
- **Migrations are explainable**: `derive explain` can show which migrations ran and why, via receipts.

## Suggested CLI affordances

- `derive state status` (show `state-snapshot`)
- `derive state plan --to <generation>` (show `state-migration-plan`)
- `derive state migrate --to <generation>` (execute; emits receipts)
- `derive state rollback <volume_id> --to <snapshot>` (explicit operator action)

## Integration points

- Workload rollout: `docs/35-workload-rollout-rollback.md`
- VM storage model: `docs/27-vm-storage-zfs.md`
- Health gating: `docs/112-health-gated-updates.md`
- Change sets (unify config + state + service transitions): `docs/219-change-sets-and-apply-engine.md`
- Event journal: `docs/215-structured-event-log-as-evidence.md`
- Incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
