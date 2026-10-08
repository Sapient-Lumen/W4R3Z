# rev0651 — C++ sync-domain model seam

## What changed

Rev0651 turns the corrected AnonSync mission into the first small C++ sync-domain API. It adds `cpp/anonsync_core/src/sync_domain.cpp` plus public types in `include/anonsync_core.hpp` for:

- portable relative sync paths;
- file and tombstone manifest entries;
- chunk ranges and chunk hash coverage;
- version-lineage entries;
- manifest entry digests;
- sync-scoped mutation idempotency keys.

The new CTest/CLI regression is:

```bash
anonsync_core --selftest-sync-domain-model
```

## Why this seam

The cube had strong admission/replay/ledger machinery but no C++ object that clearly meant “a file in a shared folder.” That made it too easy for future work to keep improving generic evidence paths instead of building AnonSync. This revision creates the minimum model that future folder scanning, manifest exchange, transfer planning, conflict handling, and ledger mutation work can attach to.

## Path policy

`normalize_sync_relative_path` is deliberately conservative because AnonSync is cross-device sync, not a local POSIX-only archiver. A path is accepted only when it is:

- nonempty and at most 4096 bytes;
- valid UTF-8;
- relative, not absolute or drive-qualified;
- slash-separated with `/` only;
- free of empty components and dot segments;
- free of ASCII control bytes and portable-invalid filename bytes such as backslash, colon, wildcard, quote, angle brackets, and pipe;
- free of trailing component space/dot;
- free of Windows reserved device components such as `CON`, `AUX`, `NUL`, `COM1`, and `LPT1`.

This is not the final filesystem policy. It is the manifest identity policy that keeps peers from disagreeing about obvious path aliases before a scanner or watcher exists.

## Manifest validation

`validate_sync_manifest_entry` currently proves structural invariants only:

- `folder_id`, `device_id`, optional `conflict_set_id`, and lineage device IDs use lowercase portable sync IDs;
- lineage is required, sorted by device id, unique, and positive-countered;
- file entries require lowercase SHA-256 content hashes;
- nonempty file entries require contiguous positive chunk ranges starting at offset zero and covering exactly `size_bytes`;
- zero-byte file entries carry no chunks;
- tombstones carry zero size and no content hash or chunks.

## Idempotency boundary

`sync_mutation_idempotency_key` accepts only sync operations:

- `publish_manifest`
- `reserve_chunk_transfer`
- `commit_file_version`
- `apply_tombstone`
- `record_conflict`

It returns `sync:v1:<sha256>` over a length-prefixed tuple containing the operation and stable manifest-entry digest. The selftest verifies that repeated keys are deterministic, different operations do not collide at the namespace level, and `generic_effect` is rejected at this sync-domain boundary.

## Audit/refactor notes

This revision intentionally isolates the new sync model in a separate translation unit instead of adding more branches to `runner.cpp`, `sqlite_replay_ledger.cpp`, or `reporting_selftests.cpp`. That is the refactor direction for the cube: split by sync trust domain before adding more behavior to the largest legacy files.

## Validation performed

- Release configure/build passed with `-O0 -DNDEBUG`.
- `anonsync_core --selftest-sync-domain-model` passed.
- Full Release CTest passed: 27/27.
- Sanitizer Debug build passed for `--selftest-sync-domain-model` with `ANONSYNC_ENABLE_SANITIZERS=ON`.
- Package validator passed: `python3 tools/validate_rev0651_sync_domain_model.py`.

## Honest ceiling

Rev0651 does not scan folders, hash real files, maintain a manifest database, watch filesystem events, connect to peers, exchange manifests, request chunks, transfer content, write final files, create conflict copies, or bind the sync model into SQLite/WAL mutation rows. The next C++ move should build a deterministic local folder/index harness that consumes this model.
