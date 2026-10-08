# rev0657 — C++ stale-target preflight before staged-file rename

## Mission fit

AnonSync is a C++ peer-to-peer file synchronization product. Rev0657 keeps the mission concrete by hardening the local file-application path added in rev0656. A Resilio-style sync engine cannot trust that a scan result is still true at the instant it renames staged bytes into the live folder. The local file may have changed after manifest diff planning.

Rev0657 therefore adds explicit stale-target preflight to the C++ sync-domain seam. The materializer no longer treats a valid remote staged file as sufficient to overwrite whatever is currently at the target path. It now checks that the current target state still matches the local state that the diff/apply plan was built from.

## C++ changes

Rev0657 extends `cpp/anonsync_core/include/anonsync_core.hpp` and `cpp/anonsync_core/src/sync_domain.cpp`:

- `SyncManifestPlanEntry` now carries `local_size_bytes`, `remote_size_bytes`, `local_content_sha256`, and `remote_content_sha256`.
- `SyncLocalApplyPlanEntry` now carries local/remote presence bits, entry kinds, size evidence, and content-hash evidence.
- `build_sync_manifest_diff_plan` propagates local and remote file evidence from the validated manifest entries.
- `build_sync_local_apply_plan` preserves that evidence into the local apply intent.
- `sync-local-apply:v1:` idempotency keys bind the presence/kind/size/content evidence, so a stale-overwrite assumption changes the intent key.
- `materialize_staged_sync_file` preflights the target before rename and records `preflight_checked_target` plus `replaced_existing_target` in `SyncStagedFileMaterializationResult`.

## Audit/refactor finding

The audit finding for this turn is a stale local overwrite gap. Rev0656 verified the staged remote file and guarded symlink/path hazards, but if a local file changed after scan and before materialization, the final rename could still clobber an unplanned local edit.

Rev0657 fixes that gap for `StageRemoteFile` materialization. The rule is simple: a remote-only plan requires absence before rename, and a remote-newer overwrite requires the current target to match the planned local bytes.

- if the apply plan was remote-only, the target must still be absent;
- if the local side was a tombstone, the target must still be absent;
- if the apply plan was remote-newer over a local file, the target must still be a regular file with the planned size and content SHA-256;
- if the target disappeared after planning, appeared after planning, became a directory/symlink, or changed content, materialization fails before the staged file is renamed.

This is not a substitute for a persistent index or OS watcher. It is the last-moment guard that prevents the current local-apply seam from destroying unplanned local edits.

## Safety properties added

- Local/remote file content evidence now survives from manifest diff planning into local apply planning.
- Apply intent idempotency keys now bind stale-overwrite preconditions.
- Target overwrite is allowed only when the current target still matches the planned local file bytes.
- The preflight hashes the current target size and SHA-256 before allowing replacement.
- Remote-only materialization rejects a local target that appeared after planning.
- Remote-newer materialization rejects a local target that disappeared or changed after planning.
- The result object distinguishes fresh creation from replacement with `replaced_existing_target`.
- The sync-domain selftest now covers safe planned replacement, stale target rejection, target-appeared rejection, and evidence propagation.

## Validation

Release validation was rerun after the stale-target preflight changes:

```text
100% tests passed, 0 tests failed out of 27
```

The sync-domain selftest now reports:

```text
anonsync_core sync domain model selftest passed=80 failed=0
```

A narrow AddressSanitizer/UndefinedBehaviorSanitizer build of `sync_domain.cpp` plus the sync-domain harness also passed with the same selftest summary. Full CMake sanitizer coverage remains heavy because older non-sync translation units are large; rev0657 records the narrow sanitizer scope explicitly.

The package validator is `tools/validate_rev0657_stale_target_preflight.py`.

## What this still does not prove

Rev0657 does not implement peer chunk receipt, partial-file transfer resume, sparse/ranged writes, crash cleanup of orphan `.part` files, tombstone deletion execution, conflict-copy materialization, persisted manifest/index state, authenticated manifest exchange, LAN/WAN discovery, NAT traversal, or a long-running daemon.

The next code-bearing seam should add chunk receipt/write accounting, or execute tombstone/conflict local mutation intents, now that the file-fetch materializer has a last-moment stale-target guard.
