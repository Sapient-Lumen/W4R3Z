# Rev0985 role-bound offline database backup audit

## Five role-bound SQLite artifacts

Rev0985 extends the released immutable backup owner from the primary replica
SQLite database to every SQLite authority selected by one deployment manifest:

1. `replica`;
2. `file-effect`;
3. `tls-membership`;
4. `tls-membership-anchor`; and
5. `folder-catalog`.

The shipping commands are:

```text
anonsync_sync database-backup-create \
  --manifest ABSOLUTE_JSON \
  --snapshot ABSOLUTE_SQLITE \
  --role replica|file-effect|tls-membership|tls-membership-anchor|folder-catalog

anonsync_sync database-backup-inspect \
  --manifest ABSOLUTE_JSON \
  --snapshot ABSOLUTE_SQLITE \
  --role replica|file-effect|tls-membership|tls-membership-anchor|folder-catalog
```

Omitting `--role` retains the exact released v1 primary-replica behavior and
response schema. Supplying a role selects the v2 response and one explicit
manifest-bound database authority. An explicit `replica` artifact remains
readable by the v1 inspector and is still the only role accepted by the
released database-replacement ceremony.

The extension does not add a second copy engine. Every role uses the existing
deployment singleton, artifact-path geometry checks, transactionally pinned
SQLite serialization, 512 MiB/262,144-page limits, complete source cutpoint
bracket, create-new mode-0600 publication, sidecar denial, resident-byte seal,
and independent postpublication reopening.

## Consistency boundary

One artifact proves one transactionally consistent SQLite database image. The
five artifacts are independently captured and independently inspected. They do
not share a cross-database transaction, generation, action receipt, or atomic
publication boundary.

The v2 operator response therefore states:

- `continuity_scope = single_role_database_image`;
- `cross_database_atomicity = false`;
- `complete_share_backup = false`;
- payload bytes, credentials, and configuration are not included; and
- only the replica role has `restore_supported = true`.

This is a deliberate prerequisite for a complete-share backup design, not a
claim that five separately captured files can be restored together without a
higher-level consistency and recovery protocol.

## Detached read-only correction

SQLite deserialized with `SQLITE_DESERIALIZE_READONLY` may still report
`sqlite3_db_readonly(..., "main") == 0`. Treating that value as the only
read-only authority would reject a valid immutable detached image, while
weakening the check globally would blur named-file and filename-free semantics.

Rev0985 adds a distinct shared
`ForensicReadOnlyDetached` TLS-policy/profile disposition. It requires an
unnamed main database, the hardened query-only connection profile, and MEMORY
journaling; it is barred from mutable owner construction. Named forensic
connections retain their native `sqlite3_db_readonly() == 1` requirement. The
sealed snapshot layer continues to behaviorally prove that writes fail with
SQLite's typed read-only result.

The membership and membership-anchor owners now expose explicit detached
forensic inspectors using that shared disposition. The primary replica already
had a detached inspector. No role-specific exception is embedded in the backup
owner.

## Root-cold file-effect and folder-catalog inspection

The file-effect and folder-catalog schemas retain the configured synchronized
root pathname as part of their durable identity. Ordinary online owners also
open and attest that root, but offline artifact inspection must remain useful
when the synchronized tree is unavailable.

Rev0985 adds named and detached observers that:

- validate the persisted root text as the exact canonical manifest pathname;
- reject embedded NUL bytes;
- retain the existing 32 KiB file-effect and 16 KiB folder-catalog text limits;
- validate the persisted root/attestation digest and complete current schema;
- never open, scan, create, or mutate the configured files root; and
- never initialize or migrate the selected database.

The shipping process regression removes both payload and synchronized roots
before backup creation, then removes every live selected SQLite family before
detached inspection. All five role artifacts remain inspectable, and none of
the absent authorities is recreated.

## Authority and failure properties

A role is not a presentation hint. It selects an expected deployment-binding
role, application ID, manifest digest, database pathname, folder identity, and
local actor. Inspecting a file-effect artifact as a folder catalog fails closed
before the artifact can be reported as valid.

Each source observation is reduced to a compact role cutpoint:

- source role and exact database pathname;
- role generation or transition sequence;
- logical retained-record count;
- canonical complete-state digest; and
- an independent role-specific auxiliary digest.

Replica observations additionally retain the released database incarnation,
recovery epoch, and complete primary cutpoint. The before/captured/after
cutpoints must compare exactly, and the durable reopened artifact must compare
to the captured observation exactly.

## What remains missing

Rev0985 does **not** provide:

- Complete-share backup;
- one atomic snapshot spanning the five SQLite databases;
- payload-byte backup or payload-manifest export;
- TLS private-key or other credential backup;
- deployment configuration and service-unit backup;
- restore commands for file-effect, membership, anchor, or catalog artifacts;
- an external anti-rollback or trusted-time anchor;
- retention, quota, ENOSPC, or garbage-collection policy; or
- a user-facing backup set, chronology, validation drill, or restore wizard.

The next safe product step is to define one complete-share backup-set format and
consistency model. That design must decide whether the service is stopped for a
single offline cut, whether an immutable multi-component receipt binds separate
captures, how payload reachability is represented, which credentials are
portable, how recovery epochs advance, and what happens when only a subset of
components is usable.

## Evidence boundary

`tools/test_anonsync_database_role_backup.py` is a shipping-process oracle. It
exercises all five roles, strict JSON, root-cold creation, source-absent detached
inspection, role confusion, private sidecar-free artifacts, source-family
stability, and explicit-replica v1 compatibility.

`tools/audit_sync_replica_database_role_backup.py` is a lexical source-shape
audit. It is not semantic proof of SQLite, POSIX identity, durability,
allocation success, cryptography, or crash behavior. Runtime, sanitizer,
reconstruction, and package evidence remain load-bearing.
