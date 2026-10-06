# Browser OPFS block-store write-budget duplicate bypass slice

Revision: rev0099  
Task: `browser:opfs-block-store-write-budget-duplicate-bypass-proof`

This managed Chromium proof exercises the rev0099 duplicate-aware write-budget guard in a real browser page. The probe seeds a valid OPFS block, patches `navigator.storage.estimate()` to report an impossible budget, and then performs the same put again through a budgeted store.

The browser proof checks:

- OPFS, Web Locks, `navigator.storage.estimate()`, secure context, and cross-origin isolation are present;
- a valid duplicate put succeeds even while the patched estimate would reject any new write;
- the duplicate path does not call the patched estimate;
- the duplicate path records `writeBudgetDuplicateBypasses` and emits `storage:opfs-block-write-budget-duplicate-bypass`;
- a new non-duplicate put still calls the patched estimate once and rejects with `BRT_OPFS_WRITE_BUDGET_EXCEEDED` before mutable OPFS open;
- a passing raw budget write still verifies;
- a guarded OPFS/Web Locks write/verify path still succeeds and ends with no held or pending locks.

Non-claims: this is managed Chromium evidence only, not Firefox/Safari/cross-browser conformance. Patching `navigator.storage.estimate()` proves BrowserRT control flow around estimates; it does not prove real quota reservation, browser eviction behavior, fsync durability, crash recovery, power-loss safety, multi-tab atomicity, tamper resistance, or production readiness.
