# Browser OPFS/Web Lock quarantine status-transition import slice — rev0090

Current browser slice: `browser:opfs-web-lock-quarantine-status-transition-import-proof`.

The managed Chromium proof exercises the same status-transition import policy with a real OPFS-backed `OpfsAsyncBlockStore`, `WebLockGuardedBlockStore`, Web Locks, and `BlockStoreLaneAdapter`. Synthetic timeout-quarantine ledgers drive the handoff/import edge, while the guarded OPFS path verifies that the adapter can still recover and perform a later real guarded write after the status-transition row is reviewed and cleared.

The browser proof checks:

```text
successful import:  one successful timeout-quarantine row
failed import:      same operationReplayKey replaces successful row
unsettled import:   same operationReplayKey replaces failed row
success re-import:  same operationReplayKey replaces unsettled row
clearance receipt:  rejects stale replay of final transitioned row
OPFS/Web Locks:     later guarded write verifies and lock state drains
```

This is a Managed Chromium/CDP proof only. It does not prove cross-browser OPFS/Web Locks behavior, provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, fsync behavior, crash safety, quota survival, eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness.
