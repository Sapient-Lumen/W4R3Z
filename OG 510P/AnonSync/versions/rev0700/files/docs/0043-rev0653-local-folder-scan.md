# rev0653 — C++ local folder scan/index seam

## What changed

Rev0653 adds the first C++ path that turns real local files into AnonSync manifest state. The new public pieces are:

- `SyncFolderScanOptions` in `cpp/anonsync_core/include/anonsync_core.hpp`;
- `build_sync_folder_manifest_from_directory` in `cpp/anonsync_core/src/sync_domain.cpp`.

Given a local root path, folder id, device id, manifest counter, lineage counter, and chunk size, the scanner walks the directory tree and returns a validated `SyncFolderManifest`.

## Why this seam

Rev0651 and rev0652 defined manifest identity, but the cube still had no C++ code that looked at a folder on disk. That meant AnonSync could validate synthetic entries while still not behaving like a file-sync engine. Rev0653 closes that gap without jumping to networking or watchers: local indexing now exists as a deterministic C++ function that can feed future diff, transfer, persistence, and peer-session work.

## Scanner behavior

`build_sync_folder_manifest_from_directory` currently:

- resolves and verifies that the scan root is a directory;
- requires positive `manifest_counter`, positive `lineage_counter`, and positive bounded `chunk_size_bytes`;
- recursively visits filesystem entries under the root;
- rejects symlinks before treating an entry as a file;
- rejects non-regular entries;
- converts every regular file path to a slash-separated relative manifest path;
- applies `normalize_sync_relative_path` to every indexed file path;
- hashes the whole file content with SHA-256;
- emits per-chunk SHA-256 ranges with contiguous offsets and lengths;
- emits no chunks for zero-byte files while still binding the SHA-256 of empty content;
- stamps a single local lineage entry from the scan options;
- sorts all entries by canonical path;
- validates the final `SyncFolderManifest` before reporting success.

The scanner returns a `SyncValidationResult`, not a partially trusted manifest. A failed scan clears the output manifest and reports a reason.

## Audit/refactor notes

The main audit/refactor decision was to keep local indexing in `sync_domain.cpp` and the public sync-domain header rather than wiring another branch into `runner.cpp` or expanding the older ledger files. That keeps this revision focused on AnonSync's file-sync domain.

The scanner also establishes a fail-closed filesystem stance that future watchers and transfer staging should inherit: symlinks and unsupported entry types are not silently followed, skipped, or turned into manifest identity. If AnonSync later supports symlink synchronization, that should be a separate explicit manifest entry kind with its own security model.

The implementation hashes content incrementally for the full-file digest and per chunk for chunk identity. It avoids requiring whole-file buffering for the content digest, but this is still a local synchronous scan, not a production resource-governed indexer.

## Validation performed

- Release configure/build passed with `-O0 -DNDEBUG`.
- `anonsync_core --selftest-sync-domain-model` passed: `passed=38 failed=0`.
- Full Release CTest passed: 27/27.
- Sanitizer Debug build passed for `--selftest-sync-domain-model` with `ANONSYNC_ENABLE_SANITIZERS=ON`.
- Package validator passed: `python3 tools/validate_rev0653_local_folder_scan.py`.

## Honest ceiling

Rev0653 does not persist scan state, query file metadata policy beyond content bytes/path, watch directories, diff local and remote manifests, exchange manifests with peers, request chunks, stage partial downloads, apply file updates, record tombstones from live deletes, resolve conflicts, or bind scan results into SQLite/WAL sync mutations. The next C++ move should compare two `SyncFolderManifest` values and produce deterministic sync actions.
