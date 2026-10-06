# Storage-lane unsettled timeout orphan review slice

Current in `rev0078`.

Task:

```text
scheduler:storage-lane-unsettled-orphan-review-proof
```

This release-tier proof covers the maintenance boundary for imported unsettled timeout quarantine. A provider operation can time out at the storage-lane layer after it has already committed data but before it returns. If that unsettled row is exported and later imported into a fresh adapter, there may be no live provider promise left that can settle it.

The proof verifies that BrowserRT keeps the lane backpressured, rejects unsafe orphan finalization, requires a reviewed and fingerprint-bound manifest to classify the imported unsettled timeout as an orphaned late failure, then requires a fresh reviewed/fingerprint-bound clear before recovery.

Earned behavior:

```text
BRT_STORAGE_OPERATION_TIMEOUT
  -> exported unsettled timeout quarantine
  -> imported unsettled row forces backpressure
  -> recovery blocks as timed-out-operation-still-unsettled
  -> reviewed/fingerprint-bound orphan finalization moves the row to failed quarantine
  -> stale old review cannot clear the finalized failure
  -> fresh reviewed/fingerprint-bound clear permits explicit recovery
```

Non-claims: this does not claim provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, OPFS durability, cross-browser behavior, quota/eviction survival, automatic recovery, or production readiness.

Audit markers: the finalization review carries `reviewFingerprint` binding. This is not cancellation and not rollback; it is a maintenance classification boundary for an imported unsettled timeout orphan.

Exact audit phrase: reviewFingerprint-bound orphan finalization is not cancellation.
