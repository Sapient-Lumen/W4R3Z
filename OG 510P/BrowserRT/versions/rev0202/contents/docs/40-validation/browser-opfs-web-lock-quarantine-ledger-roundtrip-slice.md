# Browser OPFS/Web Lock quarantine ledger roundtrip slice

Current browser proof: `browser:opfs-web-lock-quarantine-ledger-roundtrip-proof`.

This managed Chromium proof exercises the same mixed timeout quarantine ledger boundary with real OPFS writes and real Web Locks. Two guarded OPFS mutations are dispatched through the storage lane. Both time out at the storage-lane budget after mutating OPFS. One provider later succeeds and one later fails. BrowserRT exports the mixed ledger, imports it into a fresh storage-lane adapter, refuses recovery, rejects unsafe unified clears, then recovers only after a reviewed/scoped mixed-outcome clear.

Substance checked:

- real guarded OPFS blocks verify before and after late settlement;
- the exported ledger contains schema `brt.storageLane.timedOutOperationQuarantine.v1` and both success/failure buckets;
- importing the ledger marks the lane unhealthy with `timed-out-operation-quarantine-imported`;
- `recoverWhenStoreSettled()` blocks first on late success, then on late failure after only success is cleared;
- a later guarded OPFS write verifies only after all imported late outcomes are reviewed and cleared.

Non-claims: this is a Managed Chromium/CDP proof only. It does not prove cross-browser OPFS/Web Locks behavior, mobile/background lifecycle behavior, Service Worker lifecycle behavior, organic quota or eviction behavior, crash recovery, OPFS durability, fsync behavior, power-loss safety, cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, throughput, latency SLOs, or production readiness.

Explicit wording for contract audit: this slice does not prove cross-browser, quota, eviction, crash, durability, cancellation, rollback, SLO, or production behavior.
