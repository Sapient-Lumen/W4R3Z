# ADR-0054: Backup and restore posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has the ingredients for a credible **backup + recovery** lane:
`docs/316-backups-and-restores-as-derived-operations.md` makes backups typed and receipted,
`docs/317-restore-drills-and-continuous-recovery-testing.md` makes restore drills evidence-bearing,
and `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md` shows how state replication can stay operationally robust.

What the archive still lacked was the **product-shape default**.
Without that, the archive drifts into incompatible assumptions:

- A quietly grows “just image the whole host” folklore even though fleet hosts are derived and replaceable.
- B drifts toward opaque whole-device cloning or mystery sync instead of explicit user recovery surfaces.
- C cannot tell which backup posture is compatibility and which is Derive guidance.
- D risks claiming recoverability/compliance without recurring restore drills.

We do **not** need to choose one backup engine or one retention table here.
We do need a stable, checkable answer to:

- whether derived fleet hosts are backed up as whole machines or as **state datasets**,
- whether workstation recovery is export-first vs ambient whole-disk cloning,
- whether compatibility-oriented installs get a mandated backup stack,
- and whether factory/regulatory shapes require restore drills as part of the default claim.

## Decision

We define backup/recovery posture as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json` under the stable `backups` knob.

### A) `fleet_host`

Default posture: `state-replication-with-restore-drills`

- Fleet hosts are replaceable; the primary backup contract is **state dataset replication**, not whole-host image nostalgia.
- Restore drills are part of the default claim.
- Full-host image capture may exist for specific break-glass workflows, but it is not the primary recovery model.

### B) `workstation`

Default posture: `exports-or-home-replication`

- Human-facing workstations prefer explicit user exports and/or replication of portable-home or user-state datasets.
- The default recovery story should remain user-visible and explainable, not a silent whole-device clone assumption.
- This keeps backup posture aligned with the workstation’s split between trusted host UI and AppVMs.

### C) `general_os`

Default posture: `user-choice`

- Broad compatibility keeps the backup tool choice open.
- When Derive-managed backup lanes are used, they still emit typed plans/receipts and should not silently redefine B’s tighter posture.
- Compatibility is allowed; invisibility is not.

### D) `appliance_factory`

Default posture: `replication-and-restore-drills`

- Production/factory/regulatory shapes require receipted replication plus recurring restore drills as the default recovery claim.
- “We have backups” is not enough; recoverability must be exercised and evidenced.
- Offline or controlled restore targets remain the norm.

## Consequences

- Product profiles now carry a stable `backups` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back toward full-host image folklore, mystery sync, or unevidenced recoverability claims.
- Open questions narrow to implementation detail: drill cadence, retention classes, restore-target quarantine defaults, backup-key availability, and privacy/redaction budgets.

## Non-goals

- Choosing one mandatory backup engine for all profiles.
- Fixing exact restore-drill cadence or retention windows in this ADR.
- Designing the full operator or end-user backup UI.
