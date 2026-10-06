# Browser storage posture managed slice

This slice keeps the rev0132/rev0133 product diagnostic honest in a real browser. The Node/fake posture proof proves contract shape and no hidden `persist()` call; this managed Chromium proof observes the actual browser APIs, uses the postured OPFS factory, and applies the derived `writeBudgetGuard` to a tiny OPFS write.

## Claims checked

- `navigator.storage.getDirectory()` and `navigator.storage.estimate()` are visible in the managed Chromium profile.
- `diagnoseBrowserStoragePosture()` and `runtime.storage.browserStoragePosture()` return `browserrt.browser-storage-posture.v1` without requesting persistent storage by default.
- The diagnostic derives `browserrt.browser-storage-admission-policy.v1` and an enabled `writeBudgetGuard` from current quota/usage posture.
- `runtime.storage.opfsAsyncBlockStoreWithPosture()` must fail closed when posture rejects new writes and must return a store with the derived guard already installed when posture admits.
- The postured factory path runs a StorageManager estimate check before a small OPFS `put`, verifies the block, then cleans the proof prefix.
- No Web Locks are left held or pending after the proof.

## Non-claims

This is a single managed Chromium/cloudtainer posture proof. It does not claim cross-browser behavior, organic eviction survival, persistent-storage grant, quota reservation, fsync/power-loss durability, or benchmark value. `StorageManager.estimate()` remains advisory posture evidence.
