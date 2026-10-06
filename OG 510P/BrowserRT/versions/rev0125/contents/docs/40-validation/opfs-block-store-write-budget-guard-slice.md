# OPFS block-store write budget guard slice

Revision: rev0096  
Task: `opfs:block-store-write-budget-guard-proof`

This slice adds an opt-in `writeBudgetGuard` to `OpfsAsyncBlockStore.put()`. When enabled, the provider asks `navigator.storage.estimate() / StorageManager.estimate()` for quota/usage-shaped data before digest/open/write work, computes projected usage after the requested block, and rejects locally with `BRT_OPFS_WRITE_BUDGET_EXCEEDED` when the configured reserve or projected usage ratio would be violated.

The guard is deliberately conservative. A rejected call does not open OPFS, create bucket directories, create a final block file, or rely on a later rollback. `requireEstimate: true` rejects with `BRT_OPFS_ESTIMATE_UNAVAILABLE` when `navigator.storage.estimate() / StorageManager.estimate()` is missing or incomplete; `requireEstimate: false` records the unavailable estimate path and lets the caller proceed.

The release proof uses the shared fake-OPFS harness with estimate injection to check:

- constructor-level `minFreeBytes` rejection before OPFS open;
- per-put `maxUsageRatio` rejection before OPFS open;
- required-estimate failure when `estimate()` is unavailable;
- optional-estimate pass-through;
- passing budget guard write/verify behavior;
- invalid threshold rejection via `BRT_OPFS_WRITE_BUDGET_INVALID`.

Non-claims: this is not a reservation, fsync, durability, quota-policy, organic eviction, crash-recovery, production-capacity, performance, or cross-browser proof. Storage estimates are approximate; the guard only prevents starting a write when BrowserRT's local policy says the observed estimate is already too tight.
