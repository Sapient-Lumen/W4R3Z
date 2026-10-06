# Browser OPFS/Web Lock unsettled timeout orphan review slice

Current browser proof in `rev0078`.

Task:

```text
browser:opfs-web-lock-unsettled-orphan-review-proof
```

The managed-Chromium proof exercises the real guarded OPFS path. It wraps a Web Lock guarded OPFS block store with a provider that writes a content-addressed block and then intentionally never resolves. The storage lane times out the operation, exports an unsettled timeout-quarantine ledger, imports that ledger into a fresh adapter, and proves that recovery remains blocked until a maintenance review explicitly finalizes the imported unsettled timeout as an orphan.

The browser proof also verifies that the provider may have committed data before the timeout. The fix is not rollback or cancellation. The fix is a conservative quarantine/review boundary:

```text
imported unsettled timeout row
  -> lane unhealthy
  -> follow-on recovery blocked
  -> unsafe finalization rejected
  -> stale review fingerprint rejected
  -> bound review finalizes orphan as failed quarantine
  -> old review cannot clear the new failure fingerprint
  -> fresh bound review clears and explicit recovery reopens the lane
```

Non-claims: Managed Chromium only. This does not claim cross-browser OPFS/Web Locks behavior, cancellation, rollback, no-mutation-on-timeout, OPFS fsync durability, power-loss safety, quota/eviction survival, persistent-storage retention, latency SLOs, automatic recovery, or production readiness.

Audit markers: this managed browser proof uses real OPFS and real Web Locks. It is not cross-browser evidence.
Exact audit markers: managed Chromium, reviewed/fingerprint-bound, BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED, cross-browser.
