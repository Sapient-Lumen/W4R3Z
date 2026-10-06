# Backup and restore posture by profile

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** operability, isolation, supply-chain  
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt  

DeriveBSD already has a credible **backup / restore** lane.
What this doc decides is narrower and more important for coherence:
**what is the default backup + recovery posture for each product shape?**

This is intentionally **not** a backend choice.
It is a product-default decision.

See also:
- ADR: `adrs/ADR-0054-backup-and-restore-posture-by-profile.md`
- backups as derived operations: `docs/316-backups-and-restores-as-derived-operations.md`
- restore drills: `docs/317-restore-drills-and-continuous-recovery-testing.md`
- ZFS replication discipline: `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`
- product profiles: `docs/411-product-profiles-as-compilation-target.md`

## Why this needs a hard decision

Every serious system eventually answers the same uncomfortable questions:

- do we back up the **whole machine** or the **state that actually matters**?
- is the recovery path explicit and testable, or implicit and hopeful?
- are restore drills part of the default claim or an optional best practice?
- does a human workstation recover through user-visible exports/state, or through opaque admin cloning?

If the archive leaves this as “we’ll decide later,” real systems drift toward:

- full-host image folklore on replaceable fleet hosts,
- mystery sync / whole-device clone assumptions on workstations,
- compatibility defaults that swallow the secure path,
- or regulated/factory claims with no rehearsed recovery evidence.

So we decide the **default recovery authority model** now, while leaving cadence, retention, and tool choice open.

## Product-shape defaults

### A) Secure fleet host (`fleet_host`)

Default: `state-replication-with-restore-drills`

- Fleet hosts are replaceable; the primary recovery contract is **state dataset replication**.
- Restore drills are part of the default story.
- Whole-host image capture may exist for specific break-glass cases, but it is not the ordinary recovery model.

### B) Secure workstation (`workstation`)

Default: `exports-or-home-replication`

- Workstations prefer explicit user exports and/or replication of portable-home or user-state datasets.
- Recovery should remain user-visible and explainable.
- The default should not quietly collapse into ambient whole-device cloning.

### C) General-purpose OS (`general_os`)

Default: `user-choice`

- Broad compatibility keeps backup tooling flexible.
- When the Derive-managed lane is used, it remains typed, receipted, and reviewable.
- Compatibility is allowed, but it should not silently redefine workstation or fleet defaults.

### D) Appliance factory / regulatory (`appliance_factory`)

Default: `replication-and-restore-drills`

- Factory/regulatory shapes require receipted replication plus recurring restore drills as the ordinary claim.
- Offline or controlled restore targets remain the norm.
- “We have backups somewhere” is not enough.

## Cross-profile invariants

Regardless of profile:

- immutable/reproducible store content is not the same thing as mutable state datasets
- backup operations should emit typed plans/receipts when running in the Derive lane
- restore success matters more than backup optimism
- recovery claims should stay explainable under incident pressure
- ordinary restore should stay quarantine-first through `restore.plan` → `restore.receipt`, with `replacement-target` remaining an explicit stronger promotion step
- key handling and export/redaction policy must stay visible rather than becoming side-channel folklore

## What this does *not* decide

Still open:

- exact restore-drill cadence by data class / product shape
- retention budgets and deletion evidence defaults
- preferred backup engine beyond existing lanes/adapters
- restore-target quarantine semantics and user-facing UX details
- privacy budgets for detailed backup/restore receipts and support exports

That work stays implementation-level.
This doc only fixes the product-default boundary so the archive can keep converging without drifting.
The shared restore apply contract that all four profiles inherit now lives in `docs/620-restore-plans-and-receipts-stay-quarantine-first-and-promotion-shaped.md`.

## Design cue from current systems

Three current-system lessons matter here:

- CISA’s current StopRansomware guidance still tells operators to maintain **offline, encrypted backups** and to **regularly test** backup availability and integrity.
- NIST SP 800-184 still treats recovery as a real plan/playbook/test discipline and explicitly discusses restoring systems from **checked** backups.
- OpenZFS’ current send/receive docs still preserve strong operational primitives — resumable receives, bookmark-based incremental continuity, and raw-send discipline — that map well to DeriveBSD’s state-replication lane.

DeriveBSD should steal the lesson, not the surrounding admin folklore.

Last updated: 2026-03-21r350
