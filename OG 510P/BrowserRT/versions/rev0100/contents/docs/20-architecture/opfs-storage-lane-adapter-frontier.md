# OPFS block-store storage-lane adapter frontier

Current revision: rev0055

`OpfsBlockStoreStorageLaneAdapter` is a narrow bridge between the async browser-window `OpfsAsyncBlockStore` and the existing BrowserRT scheduling substrate.

It exists to answer one question:

> Can OPFS block-store operations be represented as storage-lane tasks with scheduling, drain, trace, snapshot, and validation evidence?

The current adapter supports:

- `schedulePut(bytes)`
- `scheduleGet(ref)`
- `scheduleHas(ref)`
- `scheduleVerify(ref)`
- `scheduleDelete(ref)`
- `scheduleEstimate()`
- `scheduleCleanupForTest()`
- `drain()` / `executeNext()`
- `validateOpfsStorageLaneAdapterSnapshot()`

The adapter intentionally uses async OPFS APIs in the browser window. It does **not** use sync access handles, a browser Worker storage lane, Web Locks, SharedWorker leadership, journaling, manifest recovery, or quota-pressure simulation.

## Why this bridge matters

Earlier fake-provider proofs earned scheduler, retry, budget, breaker, bulkhead, admission, and overload-governance vocabulary. Rev0038 earned the async OPFS block-store provider. Rev0039 begins to connect the two worlds without pretending the whole storage stack is done.

## Current earned claim

The adapter can schedule OPFS block operations through `StorageLaneExecutor` and `CrossLaneScheduler` in a managed Chromium/CDP proof and leave the scheduler empty after drain.

## Current non-claims

- No OPFS durability, fsync, quota, eviction, crash-recovery, or browser restart claim.
- No OPFS storage-lane durability proof.
- No OPFS sync access handle storage-lane proof.
- No OPFS browser Worker storage-lane proof.
- No OPFS multi-tab coordination proof.
- No OPFS performance claim.
- No production storage scheduler claim.


Refactor note: this bridge is deliberately layered on `BlockStoreLaneAdapter` and `StorageLaneExecutor` so future OPFS providers can share storage-lane semantics instead of forking scheduler behavior.

Current proof task: `browser:opfs-storage-lane-adapter-proof`.
Current audit task: `facility:opfs-storage-lane-adapter-contract-audit`.
