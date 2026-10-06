# Storage-lane quarantine clearance restore registration gate slice

Revision: rev0086  
Task: `scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof`

## Purpose

This slice protects a maintenance handoff boundary: restoring a timeout-quarantine clearance receipt from a block store must not report success if the restored receipt cannot be registered into the requested lane.

Before rev0086, `restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore()` could decode and validate a receipt, call registration, and still return `ok: true` even when registration rejects. That made a failed restore look like usable replay-guard state.

## Behavior proved

The release-light proof uses a synthetic block store and verifies:

- a storage-lane timeout-quarantine ledger imports and forces backpressure;
- reviewed/scoped clearing creates a valid clearance receipt;
- the receipt persists as a content-addressed block;
- restoring that storage receipt into the maintenance lane fails closed as `rejected-clearance-receipt-lane-binding`;
- rejected restore does not install stale replay guard state;
- importing the stale ledger after rejected restore still forces backpressure;
- restoring the same receipt into the storage lane succeeds with `block-store-restore-clearance-receipt` provenance;
- only the valid restore rejects stale replay and permits a later write.

## Runtime changes

`src/block-store-lane-adapter.mjs` now treats clearance receipt restore as successful only when registration also succeeds. Registration failure increments restore-rejection stats and emits:

```text
block-store-lane:quarantine-clearance-receipt-restore-rejected
```

The restore path also registers against the requested restore lane instead of silently substituting `receipt.lane`, so wrong-lane restore is not a bypass.

## Non-claims

This is browser-light synthetic storage evidence, not OPFS/Web Locks evidence. It does not claim OPFS/Web Locks behavior, cryptographic attestation, tamper-proof storage, provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota/eviction survival, latency SLOs, or production readiness.


## rev0086 audit anchor

This restore registration gate slice records wrong-lane restore behavior: registration rejects before replay guard state installs, the valid restore path is lane-bound, and the Managed Chromium side proves the OPFS/Web Locks handoff. This is not cryptographic attestation and not production readiness.
