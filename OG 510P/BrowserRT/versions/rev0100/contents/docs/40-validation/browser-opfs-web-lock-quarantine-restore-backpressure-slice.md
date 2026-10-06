# Browser OPFS/Web Lock quarantine restore backpressure slice

Revision: rev0077  
Task: `browser:opfs-web-lock-quarantine-restore-backpressure-proof`

This Managed Chromium proof uses real OPFS, real Web Locks, BrowserRT's guarded OPFS block store, and the storage-lane adapter. It imports a non-empty timeout-quarantine ledger with `markUnhealthy: false` / `markUnhealthy:false`, observes forced lane backpressure, rejects a candidate write with `reviewFingerprint`, noMutation, verifies the rejected digest is absent, then performs review-fingerprint-bound reviewed/scoped clearing and a later verified guarded OPFS write.

Non-claims: managed Chromium/CDP only; no cross-browser claim, no OPFS fsync durability, no crash or power-loss safety, no quota/eviction/persistent-retention guarantee, no provider cancellation, no rollback, no no-mutation guarantee after provider dispatch, and no production readiness.

Audit keywords: review fingerprint, noMutation, forced backpressure, cross-browser, durability, production readiness.
