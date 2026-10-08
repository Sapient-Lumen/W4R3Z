# rev0660 — C++ staged chunk receipt/resume

## Mission fit

AnonSync is a C++ peer-to-peer file synchronization product. Rev0660 keeps the mission concrete by adding the next transfer primitive below complete staged-file materialization: receipt-backed chunk writes.

A Resilio-style sync engine cannot require every remote file to appear as a fully formed `.part` file before the local mutation layer can reason about it. It needs to receive chunks out of order, record which chunks are durably present, resume without redownloading matching chunks, and avoid mistaking sparse holes or stale receipts for verified content. Rev0660 turns that requirement into a C++ sync-domain boundary.

## C++ changes

Rev0660 extends `cpp/anonsync_core/include/anonsync_core.hpp` and `cpp/anonsync_core/src/sync_domain.cpp`:

- `SyncChunkReceiptWriteOptions` carries the local synchronized root and staging root.
- `SyncChunkReceiptWriteResult` records the normalized path, staging path, receipt path, chunk offset/length/hash, `sync-chunk-receipt:v1:` idempotency key, write/reuse flags, completion status, verified chunk count, and complete staged-file content hash when available.
- `write_sync_staged_chunk` validates a remote file entry, requires an apply entry that stages a remote file, rebinds remote entry and publisher-neutral version digests, verifies that the supplied chunk belongs to the remote manifest entry, verifies chunk length and SHA-256 before writing, writes the bytes at the manifest offset, fsyncs the staged file, and atomically installs a deterministic receipt file.
- Existing matching receipts are reused only after the staged file range still hashes to the manifest chunk.
- Completion is reported only when every manifest chunk has a matching receipt and the entire staged file verifies against manifest chunk and content hashes.
- Receipt paths are derived from the same remote entry digest used for the staging path and stay under the configured staging root.

## Audit/refactor finding

The audit finding for this turn is that rev0656 through rev0659 could safely consume a complete staged file but had no transfer primitive that produced that file. Callers had to write the `.part` file out of band, which left no durable chunk-level evidence and no reliable resume boundary.

Rev0660 fixes that first local transfer gap:

- a received chunk is not trusted until its byte length and SHA-256 match the manifest chunk;
- receipt creation happens only after the staged range has been written and re-read by hash;
- a duplicate chunk can be skipped by reusing its receipt, but only if the staged bytes still match;
- completion cannot be inferred from file size or sparse holes because every chunk receipt must exist and the complete staged file is reverified.

## Safety properties added

- Chunk writes are tied to `StageRemoteFile` or remote-file `PreserveConflictCopy` apply entries, not raw caller-provided paths.
- The remote entry digest and publisher-neutral version digest are rechecked at the chunk-write boundary.
- The local root and staging root must be existing non-symlink directories and must not overlap.
- Staging and receipt paths are resolved from normalized sync paths and are checked for symlink ancestors.
- Wrong chunk bytes fail before any receipt is committed.
- Existing receipts fail closed when the staged chunk range no longer matches the manifest hash.
- Complete-file readiness is reported only after all receipts and all staged bytes verify.
- Receipt evidence receives a dedicated `sync-chunk-receipt:v1:` namespace.

## Validation

Release CTest passed for the active C++ binary:

```text
100% tests passed, 0 tests failed out of 27
```

The sync-domain selftest now reports:

```text
anonsync_core sync domain model selftest passed=121 failed=0
```

The new selftest coverage includes out-of-order chunk receipt writes, receipt reuse, complete-file handoff into `materialize_staged_sync_file`, wrong-byte rejection, receipt/staged-byte tamper rejection, and all-zero chunk missing-file rejection.

The package validator is `tools/validate_rev0660_chunk_receipt_resume.py`.

## What this still does not prove

Rev0660 does not persist transfer state across process restart, schedule peer chunk requests, clean up orphan `.part` or `.chunks` directories after crash, delete receipt sidecars after materialization, encrypt or authenticate transport, exchange manifests with peers, or run as a daemon.

The next code-bearing seam should add persisted transfer state and cleanup, or a fake authenticated peer session that drives manifest diff, chunk receipt writes, file materialization, tombstone application, and conflict preservation end-to-end.
