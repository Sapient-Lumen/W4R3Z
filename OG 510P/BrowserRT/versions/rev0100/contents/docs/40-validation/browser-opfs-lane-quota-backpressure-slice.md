# Browser OPFS lane quota/backpressure slice — rev0058

## Purpose

`browser:opfs-lane-quota-backpressure-proof` is the browser-backed storage-risk slice for rev0058. It connects the rev0057 quota-pressure proof to the runtime storage lane rather than testing the OPFS block-store in isolation.

The proof launches managed Chromium/CDP, serves a cross-origin-isolated probe page, cleans the OPFS prefix, sets a bounded origin quota override, schedules OPFS block puts through `OpfsBlockStoreStorageLaneAdapter`, and writes unique blocks until Chromium rejects a write under the quota. It then verifies that the failed content hash is absent after best-effort rollback, confirms the storage lane is unhealthy, confirms follow-on writes reject without queue mutation, routes maintenance work, cleans up, marks the lane healthy, and proves a small post-cleanup write can succeed under the same quota override.

## Runtime bugs this protects

- OPFS provider codes such as `BRT_OPFS_QUOTA_EXCEEDED` must mark the storage lane unhealthy.
- Failed OPFS content-addressed puts should attempt rollback so partial block files do not masquerade as present content.
- `cleanupForTest()` must invalidate the cached OPFS directory handle; otherwise the next write after cleanup can fail with `NotFoundError` against a stale handle.
- `rt.opfsBlockStoreStorageLaneAdapter({ schedulerConfig })` must actually pass scheduler configuration through to the runtime-created scheduler.

## Evidence checked

- CDP `Storage.getUsageAndQuota` and `Storage.overrideQuotaForOrigin` operate on the probe origin.
- At least one scheduled OPFS lane write succeeds before quota rejection.
- A real browser-backed `BRT_OPFS_QUOTA_EXCEEDED` failure reaches the storage-lane result row.
- Failed-put rollback is attempted and the failed hash is absent after rollback.
- The storage lane is unhealthy with `BRT_OPFS_QUOTA_EXCEEDED` as health reason.
- Follow-on writes reject with `rejected-lane-unhealthy` and `noMutation: true`.
- Maintenance fallback can still estimate/cleanup.
- Explicit recovery permits a small post-cleanup write.
- The CDP quota override is reset before teardown.

## Non-claims

This is Chromium-in-cloudtainer evidence only. It is not cross-browser quota conformance, not organic low-disk eviction evidence, not an OPFS fsync, crash, power-loss, or durability guarantee, not a persistent-storage permission claim, and not a throughput or capacity benchmark. Recovery is explicit/manual after cleanup; this slice does not claim automatic browser storage reclamation.
