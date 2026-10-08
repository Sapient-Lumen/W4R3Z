# rev0652 — C++ sync folder-manifest seam

## What changed

Rev0652 deepens the C++ sync-domain model from individual entries to an ordered folder snapshot. It adds public C++ API surface for:

- `SyncFolderManifest`;
- `validate_sync_folder_manifest`;
- `sync_folder_manifest_digest`.

It also fixes an audit-discovered path validation gap: the UTF-8 checker now rejects overlong two-byte sequences such as `C1 80`, not only the `C0 xx` family.

The existing regression remains:

```bash
anonsync_core --selftest-sync-domain-model
```

The selftest now covers entry-level rules plus folder-manifest sorting, duplicate path rejection, folder/device mismatch rejection, positive manifest counters, manifest-counter digest binding, and the overlong UTF-8 path regression.

## Why this seam

A Resilio-style sync product compares folder snapshots, not isolated files. Rev0651 gave AnonSync a portable representation for one file or tombstone. Rev0652 adds the minimum deterministic snapshot boundary needed before local folder scanning, manifest exchange, and manifest diff planning can be honest.

Without this seam, future peer/session code could accept ambiguous batches such as two entries for the same path, entries from the wrong folder, or entries whose digest is independent of the publishing manifest counter. Those are sync-product problems, not generic authorization problems.

## Folder-manifest invariants

`validate_sync_folder_manifest` enforces:

- `folder_id` and `device_id` are lowercase portable sync IDs;
- `manifest_counter` is positive;
- entry count stays under the current in-memory safety ceiling;
- every entry belongs to the same `folder_id` and `device_id` as the folder manifest;
- every entry passes `validate_sync_manifest_entry`;
- entries are byte-lexicographically sorted by canonical relative path; in short, entries are sorted by unique canonical path;
- paths are unique inside one device's folder snapshot.

The sorted unique path rule is intentionally strict. A single device's published folder view must not contain two current records for the same portable path. Conflict alternatives may later be represented by conflict records or conflict-copy policy, but the base folder snapshot cannot be ambiguous.

## Digest boundary

`sync_folder_manifest_digest` validates the manifest and hashes a length-prefixed tuple under `anonsync-sync-folder-manifest-v1`. The digest binds:

- folder identity;
- publishing device identity;
- manifest counter;
- entry count;
- ordered entry digests.

The selftest verifies that repeated digesting is deterministic and that changing `manifest_counter` changes the folder-manifest digest. This gives future manifest exchange code a stable identity for “this peer's view of this folder at this counter.”

## Audit/refactor notes

The implementation stays inside `sync_domain.cpp` rather than expanding `runner.cpp`, `sqlite_replay_ledger.cpp`, or `reporting_selftests.cpp`. This keeps the refactor direction aligned with the corrected mission: sync-domain behavior belongs in a sync-domain translation unit, while existing ledger/admission code should be wrapped only when a concrete sync mutation is ready.

The doc audit also corrected the C++ README's reservation API type spelling to match the public header: `IngressReservationResult`.

## Validation performed

- Release configure/build passed with `-O0 -DNDEBUG`.
- `anonsync_core --selftest-sync-domain-model` passed: `passed=26 failed=0`.
- Full Release CTest passed: 27/27.
- Sanitizer Debug build passed for `--selftest-sync-domain-model` with `ANONSYNC_ENABLE_SANITIZERS=ON`.
- Package validator passed: `python3 tools/validate_rev0652_sync_folder_manifest.py`.

## Honest ceiling

Rev0652 does not scan real folders, inspect filesystem metadata, hash file contents from disk, maintain a persistent manifest/index database, exchange manifests with peers, diff local and remote manifests, request chunks, transfer content, resolve conflicts, or bind folder-manifest publication into SQLite/WAL rows. The next C++ move should build a deterministic local folder/index harness that consumes fixture directories and emits `SyncFolderManifest` values under this policy.
