# AnonSync rev0900 revision notes

Package: `AnonSync-rev0900-2026.07.25.23.01-bootstraprecord-durableresume-identityonlycommit-obsidianbridge.zip`

## Durable bootstrap authority

- Added a deterministic hidden bootstrap record whose bytes are exactly the
  canonical future deployment manifest.
- The record is published with immutable create-new semantics before any store
  mutation, then bounded, decoded, path-bound, namespace-checked, and reconciled
  to exact file-and-parent durability on every read.
- Extracted a strict exact-byte deployment-manifest decoder so staged authority
  uses the existing canonical grammar and self-digest rather than a second
  configuration format.
- Added compiled coverage for deterministic naming, byte identity, private
  mode, duplicate refusal, copy/tamper rejection, and namespace collision.

## Idempotent bounded recovery

- Added   `anonsync_replica init-resume --manifest ABSOLUTE_JSON`.
- Recovery takes every path, identity, role, and limit only from the exact
  durable record.
- All present resources are identity-attested before any role-state work or
  missing-store creation.
- Missing resources can be created only when every present resource and the
  files root remain at bootstrap genesis.
- A complete exact-bound deployment may republish a lost final manifest even
  after operational advancement.
- A committed deployment is checked through a separate identity-only path: it
  cannot recreate a missing store, initialize schema, or reconcile membership.
- Orphan SQLite sidecars, copied records, foreign stores, advanced partial sets,
  and committed incomplete sets fail closed.

## Audit and refactor

- Split complete-store identity attestation from role-state and membership
  reconciliation so committed idempotence is not a hidden repair operation.
- Closed a restart durability hole by reconciling visible record and final
  manifest entries to exact file-and-parent durability before accepting them.
- Refactored bootstrap/open/binding audits around shared authority frontiers
  instead of the old assumption that creation lived lexically inside one
  command.
- Updated the bounded-reader closed inventory to name the new record consumer;
  retained the stale-inventory failure as intermediate evidence.
- Rejected a recovered build cache rooted in another workspace and validated in
  a clean explicit GCC 14 Debug tree.

## Validation

- Full GCC 14 Debug registry: **221/221**.
- Focused product/authority lane: **12/12**.
- Resume process proof: **9 scenarios**.
- Source audits: bootstrap **24/24**, database-open **17/17**, deployment
  binding **23/23**, bounded-reader **23/23**, payload store **33/33**.
- Release path policy: **14/14**.
- Separate GCC 14 ASan/UBSan focused build and process lane passed.

## Explicit nonclaims and next work

SQLite main-file creation and deployment binding are still separate durable
steps, so a crash can strand an unbound main file. There is no automatic
rollback, residue quarantine, descriptor-rooted deployment capability,
cross-store transaction, hostile-writer signature, forensic read-only status,
production supervisor, chunked transfer resume, causal directory semantics,
reachability/GC, at-rest encryption, or anonymity/traffic-analysis claim.

The detailed cutpoint analysis, research, and recommended sequence are in
`CRASH_RECOVERABLE_BOOTSTRAP_RECORD_AND_IDEMPOTENT_RESUME_AUDIT_rev0900.md`.
