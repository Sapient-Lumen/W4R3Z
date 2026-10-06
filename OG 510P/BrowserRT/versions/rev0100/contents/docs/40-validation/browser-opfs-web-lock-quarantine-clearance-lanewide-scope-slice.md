# Browser OPFS/Web Locks quarantine clearance lane-wide scope slice — rev0085

Current browser task:

```text
browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof
```

The managed Chromium proof exercises the same lane-wide receipt scope policy through BrowserRT's real OPFS block store, Web Lock guarded wrapper, and storage-lane adapter. It imports mixed timeout-quarantine rows, clears them with a reviewed lane-wide manifest for `storage`, creates a valid lane-scoped clearance receipt, then proves a lane-ambiguous self-consistent receipt is rejected.

The proof then confirms the rejected ambiguous receipt does not suppress stale quarantine import/backpressure, while a valid lane-scoped receipt still rejects stale replay and permits a later guarded OPFS write.

Non-claims: Managed Chromium/CDP only. No cross-browser OPFS/Web Locks behavior, provider cancellation, rollback, no-mutation-on-timeout, durability, quota/eviction survival, cryptographic attestation, throughput, latency SLO, or production-readiness claim.
