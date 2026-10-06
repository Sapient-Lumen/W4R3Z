# Browser OPFS block-store write budget guard slice

Revision: rev0096  
Task: `browser:opfs-block-store-write-budget-guard-proof`

This managed Chromium slice checks the same write-budget guard in the browser realm with real `navigator.storage.estimate()` and real OPFS. It runs impossible projected-ratio rejections and verifies that those rejected puts leave the provider unopened. It then runs passing raw OPFS and Web-Lock-guarded OPFS writes to prove the guard does not break the normal put/verify/cleanup path when thresholds are satisfiable.

Evidence required by the browser proof:

- `navigator.storage.estimate()` reports numeric quota and usage for the proof origin;
- impossible constructor `writeBudgetGuard` rejects with `BRT_OPFS_WRITE_BUDGET_EXCEEDED` before OPFS opens;
- impossible per-put `writeBudgetGuard` rejects with `BRT_OPFS_WRITE_BUDGET_EXCEEDED` before OPFS opens;
- passing raw OPFS write verifies and cleans up;
- passing Web-Lock-guarded OPFS write verifies and the Web Lock drains.

Non-claims: managed Chromium only; no cross-browser, organic eviction, browser quota policy, storage reservation, fsync, durability, crash/power-loss, production-readiness, or capacity guarantee.

- rev0190: writeBudgetGuard budgets staged OPFS puts using transient staged+final bytes before mutation; this remains StorageManager.estimate()-based preflight, not a browser quota or eviction/durability claim.
- rev0191: the release fake-OPFS proof adds a same-JS-realm reservation guard for overlapping raw-store puts; the browser slice remains the real-OPFS estimate/open check and does not claim cross-tab reservation.
