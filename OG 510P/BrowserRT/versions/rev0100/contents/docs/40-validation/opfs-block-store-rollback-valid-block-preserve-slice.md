# OPFS block-store rollback valid-block preserve slice

Revision: rev0100  
Release task: `opfs:block-store-rollback-valid-block-preserve-proof`

## Why this exists

Before rev0100, `OpfsAsyncBlockStore.put()` treated an owned failed write as safe to delete during rollback once the current call had created the final `.blk` path. That was too destructive for a content-addressed block store and preserve a valid block when bytes already match the hash. A late caller abort, trace/observer failure, or same-hash interleaving could happen after the final file already contained valid bytes for its SHA-256 path; deleting that file would turn a local failure into data loss for a valid idempotent block.

Rev0100 changes failed-put rollback so it performs a read-only integrity check first. If the final file is present and its digest matches the path, rollback preserves the file and records `valid-final-block-preserved`. If the file is missing, invalid, partial, or unreadable, the existing best-effort delete path remains active.

## Runtime markers

- `rollbackValidBlockPreserves`
- `rollbackIntegrityChecks`
- `rollbackIntegrityCheckFailures`
- `storage:opfs-block-put-rollback-preserved`
- `storage:opfs-block-put-rollback-preserve-check-error`
- `failed-put-rollback-preserve-check`
- `valid-final-block-preserved`

## Proof coverage

`tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs` covers three fake-OPFS cases:

1. a trace sink throws after `storage:opfs-block-write-close`; the put rejects, but the valid final block verifies and remains readable;
2. a caller aborts after close; the put rejects with `BRT_OPFS_OPERATION_ABORTED`, but the valid final block verifies and remains readable;
3. an invalid owned write failure before final bytes commit still rolls back and deletes the invalid file.

## Non-claims

This is not a transaction system. A failed `put()` may leave a valid content-addressed block behind, and callers should treat that as an idempotent side effect rather than as an acknowledged application-level commit. This proof does not claim cancellation, fsync durability, crash or power-loss recovery, cross-tab atomicity, cross-browser conformance, quota/eviction survival, or production readiness.
