# rev0656 — C++ verified staged-file materialization

## Mission fit

AnonSync is a C++ peer-to-peer file synchronization product. Rev0656 keeps that mission concrete by taking the next step after rev0655 local apply planning: a fetched remote file can now be verified from a staged file and atomically moved into the synchronized folder.

Rev0655 could say “stage this remote file here, then target this local path later.” That was still a promise. Rev0656 adds the first guarded local mutation primitive for `StageRemoteFile` entries: validate the apply intent against the remote manifest entry, verify staged bytes against the expected chunk hashes and whole-file SHA-256, fsync, and rename into place.

## C++ changes

Rev0656 adds these public C++ types and function to `cpp/anonsync_core/include/anonsync_core.hpp`:

- `SyncStagedFileMaterializationOptions`
- `SyncStagedFileMaterializationResult`
- `materialize_staged_sync_file`

The implementation lives in `cpp/anonsync_core/src/sync_domain.cpp`. It consumes:

1. a validated remote `SyncManifestEntry` of kind `File`;
2. a `SyncLocalApplyPlanEntry` whose source action is `FetchRemoteFile` and local action is `StageRemoteFile`;
3. explicit local and staging roots.

Before it mutates disk, it checks that the apply entry path matches the remote entry path, that remote digest evidence matches `sync_manifest_entry_digest` and `sync_manifest_entry_version_digest`, that target/staging paths match the deterministic paths produced by the apply planner, and that local/staging roots are distinct non-symlink directories.

On success it verifies every expected chunk hash in order, verifies the whole-file content hash and size, fsyncs the staged file, creates target parent directories, rejects symlink ancestors under the synchronized root, atomically renames the staged file into the target path, fsyncs the target file and parent directory where supported, and returns `sync-materialize:v1:` commit evidence. In short, the commit path fsyncs where supported before and after the atomic rename boundary.

## Audit/refactor finding

The audit finding for this turn is a local mutation safety gap: rev0655 target/staging/conflict paths were lexically rooted, but existing symlink ancestors under the synchronized tree could redirect a later write/rename. Rev0656 tightens the apply planner and materializer with existing-parent symlink-ancestor rejection under the local root and staging root.

This is intentionally narrower than a complete transfer engine. The code still assumes a complete staged file already exists; it does not yet accept individual chunks from a peer or maintain partial-transfer state.

## Safety properties added

- `StageRemoteFile` materialization now requires matching remote entry digest and publisher-neutral version digest evidence.
- Staged files must be regular files, not symlinks.
- Existing target paths must not be symlinks, and directory targets are rejected.
- Existing symlink ancestors below the local root or staging root are rejected before planning or materialization succeeds.
- The staged file is read according to the manifest chunk table; chunk hash mismatch, short read, trailing bytes, size mismatch, or content hash mismatch fail before rename.
- Staged file, final target file, and target parent directory are fsynced where supported.
- The final move uses `std::filesystem::rename` after verification, giving an atomic local handoff on POSIX filesystems.
- The result carries target path, previous staging path, verified byte count, verified chunk count, content hash, and a deterministic `sync-materialize:v1:` idempotency key.

## Validation

Release validation was rerun after the materialization/refactor changes:

```text
100% tests passed, 0 tests failed out of 27
```

The sync-domain selftest now covers the materialization seam:

```text
anonsync_core sync domain model selftest passed=71 failed=0
```

A narrow AddressSanitizer/UndefinedBehaviorSanitizer build of `sync_domain.cpp` plus the sync-domain harness also passed with the same selftest summary. Full CMake sanitizer coverage remains heavy because older non-sync translation units are large; rev0656 records the narrow sanitizer scope explicitly.

The package validator is `tools/validate_rev0656_verified_stage_rename.py`.

## What this still does not prove

Rev0656 does not implement chunk receipt from a peer, partial-file transfer resume, sparse/ranged writes, crash cleanup of orphan `.part` files, tombstone deletion execution, conflict-copy materialization, persisted manifest/index state, authenticated manifest exchange, LAN/WAN discovery, NAT traversal, or a long-running daemon.

The next code-bearing seam should add chunk receipt/write accounting or persist the local manifest/index so staged materialization can survive process restart and prove exactly what remains incomplete after a crash.
