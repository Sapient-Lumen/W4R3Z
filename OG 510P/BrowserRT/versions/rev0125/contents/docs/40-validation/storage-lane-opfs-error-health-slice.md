# Storage-lane OPFS error health slice — rev0058

## Purpose

`scheduler:storage-lane-opfs-error-health-proof` is a fast release-tier guard for the bug fixed in rev0058: OPFS provider failures were already being classified as `BRT_OPFS_*`, but the storage-lane executor only treated `BRT_STORAGE*` errors as provider-health failures. That left a path where a real OPFS quota failure could fail one scheduled write without placing the storage lane into explicit backpressure.

The slice uses a synthetic OPFS-like block-store so it can run in the browser-light release harness and keep the storage lane health policy guarded on every release sweep. The browser-backed counterpart is `browser:opfs-lane-quota-backpressure-proof`.

## Evidence checked

- `BRT_OPFS_QUOTA_EXCEEDED` is treated as a storage-lane health failure.
- The requested storage lane is marked unhealthy with the provider code as its health reason.
- Follow-on storage writes reject with `rejected-lane-unhealthy` and `noMutation: true`.
- Maintenance fallback still runs while the storage lane is unhealthy.
- Explicit recovery marks the storage lane healthy and permits a later write.

## Non-claims

This is not a browser OPFS proof, not a cross-browser quota conformance claim, not a quota-size claim, not organic eviction evidence, not a crash or durability claim, and not an automatic recovery policy. It is a cheap release guard ensuring OPFS provider codes are routed into the same health/backpressure path as generic storage-provider failures.
