# Browser OPFS/Web Lock quarantine review replay-key scope slice

Task: `browser:opfs-web-lock-quarantine-review-replay-key-scope-proof`

This managed Chromium slice proves the same maintenance boundary over the real BrowserRT OPFS/Web Lock provider stack. It uses a real `OpfsAsyncBlockStore`, `WebLockGuardedBlockStore`, and `BlockStoreLaneAdapter`, then imports a timeout-quarantine ledger containing two same-visible-opId rows with distinct `operationReplayKey` values.

The page proof verifies that an opId-only reviewed clear is rejected as ambiguous, an `operationReplayKey`-scoped review clears one row, replay of that cleared row is rejected, the uncleared same-opId row can still import and force backpressure, and a later guarded OPFS write verifies after both replay-key-scoped rows are reviewed/cleared and the lane is explicitly recovered. Final Web Lock state must drain to zero.

Non-claims: Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior, provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota/eviction survival, cryptographic attestation, SLO, or production-readiness claim.
