# ZFS replication: resume tokens, bookmarks, and receipted backups

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Plan→Apply→Receipt  

Defaults vary by profile.

DeriveBSD already treats `zfs send`/`zfs recv` streams as **signed artifacts** for distribution (`docs/126-zfs-send-distribution.md`) and treats backups as **derived operations with typed plans/receipts** (`docs/316-backups-and-restores-as-derived-operations.md`).

This doc captures three ZFS features that are unusually well-matched to the Derive model but are often underused or implemented ad-hoc:

1) **Resumable receives** (avoid “restart from zero” and eliminate silent partial-state loss)
2) **Bookmarks as incremental anchors** (enable snapshot GC without breaking incremental replication)
3) **Encryption-aware replication discipline** (avoid raw/non-raw mixing footguns)

## 1) Resumable receive as an evidence-bearing workflow

OpenZFS supports saving partially received state (`zfs receive -s`) and resuming it with a resume token (`zfs send -t <token>`). It also supports aborting saved partial state (`zfs receive -A`).

References:
- `zfs receive -s` and `zfs receive -A`: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-recv.8.html
- `zfs send -t <receive_resume_token>`: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-send.8.html

### DeriveBSD stance

- Resumability is **default-on** for long-haul or policy-approved remote replication.
- A `backup.plan` using `method=zfs.send` SHOULD carry:
  - `receive_resumable=true`
  - a policy-approved `target_dataset`
  - a “resume token handling” policy (save/resume/abort thresholds)
- A `backup.receipt` SHOULD record:
  - whether a resumable receive was used
  - any `receive_resume_token` that was observed/consumed (hash or redacted token if needed)
  - whether an abort (`receive -A`) occurred and why

This makes “we lost the connection” a **receipted and reviewable** event rather than folklore.

## 2) Bookmarks: incremental replication without snapshot hoarding

OpenZFS can generate incremental send streams using a **bookmark** as the “from” anchor (`zfs send -i snapshot|bookmark …`). Bookmarks are lightweight and allow GC of old snapshots while preserving incremental replication continuity.

References:
- `zfs send` incremental-from-bookmark: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-send.8.html
- Bookmarks and redaction bookmarks: `docs/130-zfs-bookmarks-and-redaction.md`

### DeriveBSD stance

- Treat “replication continuity anchors” as *state* that deserves evidence:
  - promote a bookmark as the canonical anchor after a successful receive
  - record bookmark creation in receipts
- Prefer bookmarks for long-lived replication graphs where snapshot retention is expensive.
- Keep snapshot naming deterministic (planner-chosen) so receipts remain easy to join.

## 3) Encryption-aware replication discipline (raw vs non-raw)

ZFS native encryption is a strong primitive for DeriveBSD’s state datasets (`docs/409-zfs-encryption-and-key-management.md`). When replicating encrypted datasets, ZFS distinguishes between:

- **raw sends** (`zfs send -w`): ciphertext + IV sets are replicated as-is
- **non-raw sends**: data is decrypted on sender and re-encrypted on receiver

OpenZFS documents a key operational constraint: mixing raw and non-raw receives for the same dataset lineage can cause incremental raw receives to fail; best practice is to pick one mode and stick with it.

Reference:
- Raw send/receive restrictions and IV-set explanation: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-recv.8.html

### DeriveBSD stance

- Encrypted state replication SHOULD default to **raw sends** for off-host backup targets that must not hold keys.
- A `backup.plan` MUST declare whether the stream is raw vs non-raw when encryption is in play.
- Promotion into “live namespaces” MUST remain quarantine→verify→promote (distribution lane invariant).

## 4) Automation as an adapter lane (zrepl / sanoid / syncoid)

Many operators rely on tools such as `zrepl` (daemonized replication + pruning) or `sanoid/syncoid` (snapshotting + replication scripts). These can be extremely practical, but in DeriveBSD they should be treated as **Tier E adapters** that emit Derive receipts and can be strangled/replaced over time.

References:
- zrepl: https://zrepl.github.io/
- OpenZFS wiki entry: https://openzfs.org/wiki/Zrepl
- sanoid/syncoid: https://github.com/jimsalterjrs/sanoid

### DeriveBSD stance

- Allow these tools behind a transport/backup adapter interface.
- Require receipts that capture:
  - selected datasets
  - send/recv flags (including raw/resume)
  - snapshot/bookmark anchors
  - pruning actions
- Over time, replace the adapter implementation with a Derive-native engine while keeping the plan/receipt schema stable.

## 5) Profile defaults (keep A–D viable)

Backups/replication must exist for all product shapes, but defaults differ:

- **A) Fleet host**: replication lane commonly enabled; resumable receives recommended; strict evidence retention.
- **B) Workstation**: prefer portal-governed “personal exports” and optionally replication for home datasets.
- **C) General OS**: keep replication available but not mandatory; make it easy.
- **D) Appliance factory / regulatory**: replication + restore drills are central; offline mirror kits and deterministic retention are expected.

See: `docs/411-product-profiles-as-compilation-target.md`, `docs/412-product-profile-matrix.md`, `docs/464-backup-and-restore-posture-by-profile.md`.

## Implementation hooks (kept minimal)

- `backup.plan` and `backup.receipt`: `spec/backup.plan.schema.json`, `spec/backup.receipt.schema.json`
- Distribution lane invariants: `docs/126-zfs-send-distribution.md`
- Restore drills: `docs/317-restore-drills-and-continuous-recovery-testing.md`

Last updated: 2026-03-06r193
