# Browser OPFS block-store rollback valid-block preserve slice

Revision: rev0100  
Browser task: `browser:opfs-block-store-rollback-valid-block-preserve-proof`

## Browser evidence

The Managed Chromium proof runs against real OPFS and real Web Locks. It installs a trace sink that throws exactly once after `storage:opfs-block-write-close`, forcing `OpfsAsyncBlockStore.put()` to fail after a valid content-addressed final block has already been closed.

The proof then verifies through a fresh store instance that the block is still present, digest-valid, and byte-preserved. It also checks `rollbackValidBlockPreserves`, the failed-put rollback detail, and the `storage:opfs-block-put-rollback-preserved` event.

A guarded OPFS/Web Locks smoke path still writes, verifies, cleans up, and drains locks after the raw rollback change.

## Boundaries

The proof is focused Chromium evidence only. It does not prove cross-browser behavior, crash durability, power-loss behavior, fsync durability, quota/eviction survival, Web Locks fairness, or production storage readiness.
