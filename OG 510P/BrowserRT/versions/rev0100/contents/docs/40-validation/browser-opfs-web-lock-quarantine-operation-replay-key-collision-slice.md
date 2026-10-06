# Browser OPFS/Web Lock quarantine operation replay-key collision slice

Task: `browser:opfs-web-lock-quarantine-operation-replay-key-collision-proof`

This Managed Chromium proof carries the operation-replay-key collision policy over the real guarded OPFS/Web Locks path. The browser page creates a timeout-quarantine ledger with same visible opId rows and distinct `operationReplayKey` values, imports it through `BlockStoreLaneAdapter`, clears it with reviewed/fingerprint-bound maintenance scope, registers a clearance receipt, rejects stale exact and single-row replay, and verifies a later guarded OPFS write.

The proof also checks the adjacent rev0087 scope cleanup: a lane-wide clearance receipt registered for `storage` is visible under the `storage` query and not under `maintenance`.

Non-claims: managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior, provider cancellation, rollback, no-mutation-on-timeout, OPFS durability/fsync, quota/eviction survival, cryptographic attestation, SLO, or production-readiness claim.
