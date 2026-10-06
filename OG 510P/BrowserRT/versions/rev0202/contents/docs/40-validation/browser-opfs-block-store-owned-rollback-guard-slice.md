# Browser OPFS block-store owned rollback guard slice

Revision: rev0097  
Task: `browser:opfs-block-store-owned-rollback-guard-proof`

This managed Chromium slice checks the ownership-aware rollback guard with real OPFS. It seeds a valid content-addressed block, runs a duplicate put through a trace object that throws after duplicate classification, and then verifies that the original block still exists, verifies, and reads back byte-for-byte. The failure must report skipped rollback rather than attempted/deleted rollback.

The proof also runs a small Web-Lock-guarded OPFS write/verify/cleanup path after the raw duplicate failure, so the current browser proof still touches the OPFS + Web Locks integration surface and verifies that locks drain.

Evidence required by the browser proof:

- real OPFS is available in the managed browser page;
- duplicate put failure rejects with `BRT_OPFS_OPERATION_FAILED` but records `rollback.attempted === false` and `rollback.skipped === true`;
- the existing block verifies and reads back byte-for-byte after the duplicate failure;
- `rollbackOwnershipSkips` increments while `rollbackAttempts` stays zero for the duplicate-failure path;
- guarded OPFS/Web Locks put/verify succeeds and the lock manager ends with no held or pending locks.

Non-claims: managed Chromium only; no cross-browser, organic eviction, browser quota policy, fsync, durability, crash/power-loss, atomic multi-tab write, production-readiness, or capacity guarantee. This proves the duplicate failure path does not delete a pre-existing block; it does not prove a general transactional OPFS store.
