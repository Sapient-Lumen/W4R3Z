# Browser OPFS/Web Lock quarantine clearance epoch replay guard slice

Current in rev0082.

This Managed Chromium slice runs the operation-epoch replay guard against real BrowserRT OPFS/Web Lock storage paths.

The browser proof creates real guarded OPFS timeout-quarantine rows, clears them with a reviewed receipt, restores the receipt into a fresh adapter, then verifies three boundaries:

- the old exact timeout-quarantine ledger rejects as stale cleared replay;
- a status-rewritten stale row with the original operation epoch rejects as row replay;
- an epoch-stripped stale row rejects as downgrade replay;
- a new timeout quarantine with the same-opId / same visible op ids but a different operation epoch imports/backpressures normally and recovers only after reviewed clearing.

Non-claims: managed Chromium/CDP only; no cross-browser OPFS/Web Locks claim. Operation epochs are not cryptographic attestation. Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, durability, quota/eviction, SLO, or production-readiness evidence.


Explicit non-claim marker: no provider cancellation, rollback, no-mutation-on-timeout, cross-browser, quota, eviction, crash, or production-readiness claim.
