# Browser OPFS Web Lock late-settlement recovery-gate slice

Revision: rev0069  
Task: `browser:opfs-web-lock-late-settlement-recovery-gate-proof`  
Current role: explicit managed-Chromium proof for late provider settlement gating with real OPFS and Web Locks.

## Purpose

rev0068 proved that a storage-lane operation can time out after a guarded OPFS provider has already acquired the mutation Web Lock. rev0069 targets the next risk: the Web Lock may be released while the provider promise remains unresolved. If BrowserRT only waits for Web Lock state to settle, it can reopen the lane too early.

The browser proof uses a real OPFS async block store behind BrowserRT's Web Lock guarded wrapper, then wraps that store with a delayed provider surface. The wrapped provider writes a real OPFS block and releases the Web Lock, but does not settle the storage-lane operation until the test explicitly releases it.

## Evidence shape

The proof verifies:

- The timed-out operation fails as `BRT_STORAGE_OPERATION_TIMEOUT`.
- Web Lock query rows show `heldCount: 0` and `pendingCount: 0` after timeout.
- The OPFS block written before timeout is present, preserving the non-claim that timeout is not cancellation.
- `recoverWhenStoreSettled()` still refuses recovery with `timed-out-operation-still-unsettled`.
- Late provider settlement is traced as `storage-lane:late-provider-settlement`.
- Late success does not retroactively publish a successful adapter result for the failed scheduler operation.
- Explicit recovery after late settlement allows a later guarded OPFS write to verify.

## Non-claims

This is a managed Chromium/CDP proof only. It is not cancellation, rollback, no-mutation, exactly-once, automatic recovery, no cross-browser OPFS/Web Locks claim, no OPFS durability/fsync/power-loss claim, no quota or eviction survival claim, no persistent-retention claim, no throughput or latency SLO, and no production-readiness claim.

Cross-browser, quota, eviction, and crash behavior remain separate proof targets.


Explicit phrase guard: not cancellation, not rollback, no cross-browser behavior, and late provider settlement remains a recovery-gate proof rather than a production guarantee.
