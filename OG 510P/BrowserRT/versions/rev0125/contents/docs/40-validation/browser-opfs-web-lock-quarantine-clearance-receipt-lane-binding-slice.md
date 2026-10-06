# Browser OPFS/Web Lock timeout-quarantine clearance receipt lane-binding slice

Revision: rev0084  
Browser proof: `browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof`

This Managed Chromium proof repeats the clearance receipt lane-binding boundary over real OPFS and real Web Locks. It uses `WebLockGuardedBlockStore` and `BlockStoreLaneAdapter` to create real guarded OPFS mutations that time out at the storage-lane scheduler, later settle as one success and one failure, and produce a reviewed `clearanceReceipt.v1`.

The browser proof checks that:

```text
receipt row lane mismatch fails validation
wrong-lane direct registration rejects as rejected-clearance-receipt-lane-binding
wrong-lane rejection does not suppress stale quarantine import/backpressure
valid lane-bound registration rejects stale replay without poisoning the lane
real guarded OPFS writes before and after the guard verify
final held/pending Web Locks drain to zero
```

The earned claim is narrow: in managed Chromium, direct timeout-quarantine clearance receipt registration is lane-bound and cannot silently re-register a storage-lane clearance receipt under another lane.

Non-claims: managed Chromium/CDP only; not cross-browser OPFS/Web Locks behavior, no OPFS fsync/durability/power-loss claim, no quota/eviction/persistent-storage retention claim, no provider cancellation/rollback/no-mutation-on-timeout claim, and no production readiness claim.
