# rev0658 — C++ remote tombstone application

## Mission fit

AnonSync is a C++ peer-to-peer file synchronization product. Rev0658 keeps the mission concrete by executing the next local sync mutation after verified staged-file materialization: remote tombstones. A Resilio-style sync engine must treat deletes as first-class sync events, but it must not let an old scan delete a file that changed or appeared after planning.

Rev0658 therefore adds a C++ `apply_sync_remote_tombstone` boundary. It consumes a validated remote tombstone entry plus a `DeleteLocalPath` apply-plan entry produced from `ApplyRemoteTombstone`, verifies that both pieces of evidence still agree, preflights the current target, and removes only the planned regular file.

## C++ changes

Rev0658 extends `cpp/anonsync_core/include/anonsync_core.hpp` and `cpp/anonsync_core/src/sync_domain.cpp`:

- `SyncTombstoneApplicationOptions` carries the local synchronized root for tombstone application.
- `SyncTombstoneApplicationResult` records the normalized path, absolute target path, `sync-tombstone:v1:` idempotency evidence, whether target preflight ran, whether the target existed, and whether a file was removed.
- `apply_sync_remote_tombstone` validates the remote tombstone entry, requires a matching `ApplyRemoteTombstone`/`DeleteLocalPath` apply entry, rechecks remote entry and version digests, rejects staging/conflict-copy paths, verifies target path binding, enforces symlink-ancestor rejection, preflights the current target, removes the regular file if present, and fsyncs the parent directory where supported.
- `tombstone_application_idempotency_key` binds the remote tombstone digest, remote version digest, local apply intent key, normalized path, and absolute target path.
- `preflight_tombstone_target_state` mirrors rev0657 stale-target discipline for deletes.

## Audit/refactor finding

The audit finding for this turn is that rev0655/rev0657 could plan `DeleteLocalPath`, but no C++ function executed it. That meant remote tombstones were visible in the diff/apply plan but still could not mutate the local folder safely.

Rev0658 fixes that gap for regular files. The rule is intentionally conservative:

- a remote-only tombstone is a verified no-op only if the target is still absent;
- a remote tombstone over a planned local file deletes only if the current target is a regular file whose size and SHA-256 match the planned local evidence;
- a target that appeared after planning, disappeared after planning, changed content, became a directory, became a symlink, or sits under a symlink ancestor fails before deletion.

This keeps deletes aligned with the rev0657 stale-overwrite safety model. Delete application is now a code-bearing sync mutation boundary rather than a planner-only claim.

## Safety properties added

- Remote tombstone application is tied to the diff/apply plan shape, not raw caller input.
- The remote tombstone entry digest and publisher-neutral version digest are rechecked at the apply boundary.
- Delete evidence receives a dedicated `sync-tombstone:v1:` idempotency namespace.
- Remote-only tombstones cannot delete files that appeared after planning.
- Remote-newer tombstones cannot delete files that changed after planning.
- Tombstones delete regular files only; directories, symlinks, non-regular files, and symlink ancestors fail closed.
- The parent directory is fsynced after a successful remove where supported.
- The sync-domain selftest now covers successful delete, absent-target no-op, stale changed target rejection, and newly appeared target rejection.

## Validation

Release validation was rerun after the remote tombstone application changes:

```text
100% tests passed, 0 tests failed out of 27
```

The sync-domain selftest now reports:

```text
anonsync_core sync domain model selftest passed=92 failed=0
```

A narrow AddressSanitizer/UndefinedBehaviorSanitizer build of `sync_domain.cpp` plus the sync-domain harness also passed with the same selftest summary. Full CMake sanitizer coverage remains heavy because older non-sync translation units are large; rev0658 records the narrow sanitizer scope explicitly.

The package validator is `tools/validate_rev0658_remote_tombstone_apply.py`.

## What this still does not prove

Rev0658 does not implement peer chunk receipt, partial-file transfer resume, sparse/ranged writes, crash cleanup of orphan `.part` files, conflict-copy materialization, persisted manifest/index state, authenticated manifest exchange, LAN/WAN discovery, NAT traversal, or a long-running daemon.

The next code-bearing seam should add chunk receipt/write accounting or execute `PreserveConflictCopy` materialization, now that file creation/update and regular-file deletion both have last-moment stale-target guards.
