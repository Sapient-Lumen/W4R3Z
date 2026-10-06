# Backups and restores as derived operations

Backups are not “external tooling”; they are **part of the system’s evidence model**.
If state replication and restores live outside DeriveBSD’s Spec→Lock→Plan→Artifact pipeline, then the most important incident questions become unanswerable:

- *What state was backed up, when, and under which policy?*
- *Was the backup encrypted, with which key policy, and who/what authorized it?*
- *Was retention applied as intended (and can we prove deletion)?*
- *Can we restore it today, or have we only been producing “feel-good artifacts”?*

DeriveBSD treats backup + restore as **derived operations** that produce typed plans and receipts, so the story is reviewable, automatable, and auditable.

## Design stance

- **Backups are state-scoped**: the immutable store is reproducible; state datasets are not.
- **Backups are policy-governed**: encryption, destinations, and retention are expressed as policy inputs.
- **Backups are explainable**: every run emits a receipt that can be joined to the causality graph.
- **Restores are rehearsed**: a backup that has never been restored is an untested hypothesis.

## Objects

### `backup.plan`
A `backup.plan` is a concrete, executable intent produced by planning from higher-level backup policy + current state inventory.

Key fields (see schema):
- what state datasets are in scope (dataset selectors)
- which snapshot strategy to use (explicit snapshot vs reuse an existing tagged snapshot)
- which transport adapter to use (`zfs.send`, `restic`, `tar+hash`, …)
- where bytes may go (destination ref / transport policy handle)
- what encryption policy applies (crypto portal ref / key policy handle)
- what retention/prune rules apply

Schema: `spec/backup.plan.schema.json`

### `backup.receipt`
A `backup.receipt` records what actually happened:

- which plan ran (digest + plan id)
- which dataset snapshots were captured
- content digests for exported bytes (stream digest / pack digest)
- transport receipts for delivery (so “what left the machine?” is provable)
- crypto op receipts for encrypt/sign operations when applicable
- retention/prune actions taken

Schema: `spec/backup.receipt.schema.json`

### Restore (future: plan + receipt)
This archive does not yet standardize `restore.plan`/`restore.receipt`, but the shape is clear:

- restore is a **change set** that applies a previous state snapshot into a target dataset (possibly into a quarantine namespace first)
- restores should always emit receipts, and they should be able to run in a sandbox (microVM) for drills

The immediate win is to standardize restore drills as receipts (below), while leaving the exact restore apply-engine as a later hardening milestone.

## Plumbing into existing lanes

- **State datasets**: `docs/217-state-datasets-and-migrations-as-evidence.md`
  - backup scope should reference state datasets by stable identifiers (dataset roles / state ids), not ad-hoc mount paths.
- **ZFS replication**: `docs/126-zfs-send-distribution.md`, `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`
  - `backup.plan.method=zfs.send` is an adapter mode; send streams are signed/hashed artifacts; resumable receive and bookmarks make it operationally robust.
- **Export + transport policy**: `docs/251-export-policies-and-support-bundle-portal.md`, `docs/255-policy-constrained-transports.md`
  - backup delivery uses the same transport policy machinery; the difference is scheduling + retention.
- **Crypto operations portal**: `docs/306-crypto-operations-portal-and-split-keys.md`
  - backup encryption keys are not files; they are portalized operations with receipts.
- **Evidence joins**: `docs/246-causality-graphs-and-minimal-evidence-bundles.md`
  - receipts join: `backup.receipt` → `transport.receipt` → `export.receipt` (if exported) → incident bundle.

## Anti-patterns

- **“rsync /etc somewhere”**: configuration is already derived; state is elsewhere; receipts disappear.
- **Unencrypted backups by default**: almost always a policy failure; if allowed, it should be explicit and loud.
- **Backups without restore drills**: operationally equivalent to no backups.
- **Retention as folklore**: “we keep 30 days” is meaningless without pruning receipts.

## Suggested day-0 posture

- Provide a conservative built-in backup adapter set:
  - `zfs.send` (preferred for ZFS state datasets)
  - `restic` (optional, for non-ZFS or object-store friendly backends)
- Default receipts are **digest-first** (no pathnames / filenames unless policy allows), and detailed metadata is only included inside support bundles under export policy.
- Make restore drills cheap: spin up a microVM, apply into a quarantine dataset, run health checks, emit receipts.

Accepted default boundary note: profile-shaped backup/recovery defaults now live in `docs/464-backup-and-restore-posture-by-profile.md`.

See also: `docs/317-restore-drills-and-continuous-recovery-testing.md`, `docs/464-backup-and-restore-posture-by-profile.md`

Last updated: 2026-03-06r193
