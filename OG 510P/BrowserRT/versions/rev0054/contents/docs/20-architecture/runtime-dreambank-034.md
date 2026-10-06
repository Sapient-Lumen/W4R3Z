# Runtime dreambank 034 — OPFS as a scheduled storage provider

Current revision: rev0054

The dream is that BrowserRT storage providers eventually become schedulable runtime participants:

```txt
provider capability → lane admission → scheduled operation → trace event → provider result → recovery/non-claim boundary
```

Rev0039 adds the baby rung for OPFS:

```txt
OpfsAsyncBlockStore
  ↓
OpfsBlockStoreStorageLaneAdapter
  ↓
StorageLaneExecutor
  ↓
CrossLaneScheduler
```

This should eventually enable:

- OPFS block-store providers behind admission budgets;
- OPFS journal/manifest providers behind storage-lane recovery contracts;
- worker-only sync-handle providers behind exclusive leases;
- Web Locks or SharedWorker leaders for same-origin coordination;
- fake-provider model walks before browser spending;
- per-provider trace spans for every byte-moving operation.

The dreambank warning is equally important: do not collapse provider proof into durability proof. OPFS being available and readable after a page reload is useful evidence, but it is not a crash-recovery, quota, eviction, browser-restart, sync-handle, or multi-tab proof.
