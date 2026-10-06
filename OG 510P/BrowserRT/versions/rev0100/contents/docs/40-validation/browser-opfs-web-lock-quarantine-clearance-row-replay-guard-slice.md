# rev0081 browser OPFS/Web Lock quarantine clearance row replay guard slice

Current browser task: `browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof`

This Managed Chromium proof exercises the same row-replay guard through real OPFS content-addressed writes, BrowserRT's Web Lock guarded block-store wrapper, and the storage-lane adapter.

The proof creates one late-success and one late-failure guarded OPFS timeout outcome, exports the timeout-quarantine ledger, clears it with a reviewed/fingerprint-bound manifest, persists a `clearanceReceipt.v1` block through OPFS, restores the receipt into a fresh adapter, and then rejects:

```text
exact stale pre-clearance ledger replay
modified ledger replay containing already-cleared rows
status-rewritten replay of an already-cleared operation identity
```

The lane remains healthy and quarantine-empty after rejected row replay, and a later guarded OPFS write verifies.

Non-claims: managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior, provider cancellation, rollback, no-mutation-on-timeout, exactly-once behavior, OPFS durability, quota survival, eviction survival, throughput SLO, or production readiness.

Rejected row replay disposition: `rejected-cleared-quarantine-row-replay`. This is not cross-browser evidence.
