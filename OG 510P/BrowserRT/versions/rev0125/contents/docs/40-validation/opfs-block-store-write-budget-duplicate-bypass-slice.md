# OPFS block-store write-budget duplicate bypass slice

Revision: rev0099  
Task: `opfs:block-store-write-budget-duplicate-bypass-proof`

This slice fixes a false-rejection risk introduced by the write-budget guard. Before rev0099, `OpfsAsyncBlockStore.put()` could check `StorageManager.estimate()` before digesting and deduplicating the payload. That meant a valid idempotent duplicate put could be rejected by an impossible quota/reserve policy even though it would not write a new block or consume new OPFS bytes.

The provider now performs a read-only duplicate/corrupt check first and only applies `writeBudgetGuard` to writes that would mutate OPFS:

- verified valid duplicate blocks bypass the budget guard and emit `storage:opfs-block-write-budget-duplicate-bypass`;
- file-presence duplicate checks with `verifyExistingBlocksOnPut: false` also bypass the budget guard;
- new non-duplicate writes still call the budget guard before creating prefix, bucket, or block files;
- corrupt-block repairs check the budget before deleting the corrupt existing block;
- skipped duplicate budget checks increment `writeBudgetDuplicateBypasses`.

The release proof uses the shared fake-OPFS harness and a new `createStorageEstimateRecorder()` helper. It proves that duplicate puts do not call `navigator.storage.estimate()` and do not mutate the fake OPFS tree, while new writes and corrupt-block repairs still reject before provider mutation under impossible budgets.

Non-claims: this remains an estimate-based preflight, not a storage reservation. It does not prove cross-browser behavior, quota or eviction survival, persistent-storage retention, fsync durability, crash/power-loss recovery, multi-tab atomicity, Web Locks fairness, tamper-proof storage, or production readiness.
