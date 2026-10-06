# OPFS block-store owned rollback guard slice

Revision: rev0097  
Task: `opfs:block-store-owned-rollback-guard-proof`

This slice fixes ownership-aware rollback for failed puts in `OpfsAsyncBlockStore`. Before rev0097, any error after a content hash was known could call failed-put rollback for that hash. That was too broad: a duplicate/idempotent put that discovered a pre-existing valid block and then failed late could delete content the call did not create.

The provider now tracks whether the current `put()` owns the final block path. Rollback is allowed only after the current put has repaired a corrupt final path or has begun creating/writing the final file. Duplicate paths and abort/error paths that only inspected a pre-existing valid block record `rollbackOwnershipSkips` and emit `storage:opfs-block-put-rollback-skipped` instead of deleting the final block.

The release proof uses the shared fake-OPFS harness to check:

- duplicate put failure after duplicate classification skips rollback and preserves the existing valid block;
- duplicate put abort during existing-block inspection skips rollback and preserves the existing valid block;
- a failed write after this put creates the final file still attempts rollback and deletes the owned partial/final file;
- rollback ownership decisions are visible in stats, trace, and provider error detail.

Non-claims: this is not cross-browser coverage, cross-tab atomicity, a compare-and-swap write protocol, fsync durability, crash recovery, eviction survival, quota policy, production readiness, or adversarial storage tamper resistance. It is a local provider guard that prevents BrowserRT's own failed-put cleanup from deleting a valid block it merely found.
