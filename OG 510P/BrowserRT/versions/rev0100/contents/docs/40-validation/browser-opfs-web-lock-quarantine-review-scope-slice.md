# Browser OPFS Web Lock quarantine review scope slice — rev0078

Current browser task:

```text
browser:opfs-web-lock-quarantine-review-scope-proof
```

This managed Chromium proof exercises the real guarded OPFS path through `WebLockGuardedBlockStore`, the storage-lane adapter, and timeout-quarantine import/review/clear behavior.

The proof creates guarded OPFS writes that time out at the storage-lane boundary, later settle as mixed late success/failure quarantine, then verifies:

```text
Managed Chromium only
real guarded OPFS writes through Web Locks
quarantineFingerprint and reviewFingerprint are exported
scope override is rejected
timed-out-quarantine-clear-review-manifest-scope-override is rejected
count mismatch is rejected
timed-out-quarantine-clear-review-manifest-count-mismatch is rejected
recovery only happens after a scope-bound review manifest clears the current quarantine
```

The important runtime boundary is that a review manifest is not merely a token. It is a scoped maintenance artifact. A caller cannot pass a manifest and then supply wider categories, different opIds, lane-wide intent, review tokens, or review fingerprints at clear time.

Non-claims: this is Managed Chromium/CDP evidence only. It is not cryptographic attestation, not tamper-proof storage, does not claim rollback, does not claim cancellation, does not prove no mutation after timeout, and does not prove cross-browser OPFS/Web Locks behavior, OPFS durability, quota/eviction survival, SLOs, or production readiness.

Audit phrases: token override is rejected; fingerprint override is rejected; not cryptographic attestation; not claim rollback.
