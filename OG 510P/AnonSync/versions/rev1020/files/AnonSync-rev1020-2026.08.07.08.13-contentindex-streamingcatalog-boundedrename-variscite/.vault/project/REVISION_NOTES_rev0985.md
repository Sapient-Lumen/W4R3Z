# AnonSync rev0985 revision notes

## Role-bound database backup

Rev0985 extends the immutable offline database backup command with an optional
canonical `--role` selecting `replica`, `file-effect`, `tls-membership`,
`tls-membership-anchor`, or `folder-catalog`.

Each explicit role is bound to the deployment manifest, exact database
pathname, role-specific application ID and deployment-binding row, complete
current schema, compact logical-state cutpoint, bounded canonical SQLite image,
and private create-new artifact. The primary replica remains compatible with
the released v1 inspector and replacement owner. The other four artifacts are
inspection-only.

## Backward compatibility

Commands without `--role` preserve the exact v1 response schemas and primary
replica behavior:

```text
anonsync_sync database-backup-create --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE
anonsync_sync database-backup-inspect --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE
```

Explicit roles use v2 responses. The copy, publication, source bracket, bounds,
and singleton remain in `SyncReplicaDatabaseBackupOwner`; the CLI is only a
strict parser and renderer.

## Audit/refactor

The adjacent audit found that filename-free SQLite images deserialized with the
read-only flag do not reliably satisfy `sqlite3_db_readonly() == 1`. The shared
TLS-policy SQLite profile now models `ForensicReadOnlyDetached` separately from
named forensic files and mutable detached bootstrap images. Named forensic
readers retain the native read-only gate; detached images retain query-only,
unnamed-main, MEMORY-journal, sealed-byte, and behavioral write-denial proof.

File-effect and folder-catalog owners gained explicit offline observers that
validate persisted canonical root text and digests without opening the
synchronized root. Embedded NULs and the existing root-text limits fail closed.
Membership and anchor owners gained explicit detached forensic observers rather
than one-off backup exceptions.

A dedicated shipping-process regression exercises all five roles with the
payload and files roots absent, then with every source database family absent.
It also proves role confusion denial, private sidecar-free artifacts, unchanged
source families, strict JSON, and v1 explicit-replica compatibility.

## Boundary

This revision produces five independently consistent database artifacts. It is
not a Complete-share backup, does not claim cross-database atomicity, contains
no payload bytes, credentials, or configuration, and adds no restore path for
the four new roles. The next product edge is one documented backup-set and
recovery model spanning databases, payload reachability and bytes, credentials,
configuration, recovery epochs, and partial-set failure.

## Validation

Exact rev0985 source passed the fresh GCC 14.2 Debug complete graph (536/536 configured build edges), all 264/264 registered tests in indexed final-source accounting, and an independent 42/42 product replay. Focused GCC proofs passed 108 file-effect SQLite-owner checks, 470 folder-owner checks, the existing 598-check database backup/recovery/replacement process oracle, and the new 699-check five-role backup oracle. Source audits passed 28/28 original backup checks, 31/31 role-bound backup checks, 39/39 TLS-membership profile checks, and 412/412 structural authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 42/42 product tests passed with leak detection and halt-on-error, including the direct 470-check folder-owner proof at 1,479,148 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0984 parent SHA-256 matched 0dcadb3e3bd4aa620e80e39ba009b9bdbbf89686b638c61c2e1fc4db961cd664 and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 585 files / 27,187,739 bytes with SHA-256 ec2072db6a95736b907e8363844ac46cad7550c78433af2f9f0d359c4a9fdeb6.

## Archive

AnonSync-rev0985-2026.08.03.18.23-roleboundbackup-detachedprofile-sharerecoverymap-orthoclase.zip
