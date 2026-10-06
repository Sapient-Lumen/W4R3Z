# Storage-lane quarantine clearance epoch replay guard slice

Current in rev0082.

This browser-light slice proves that timeout-quarantine clearance replay guards are bound to a per-executor operation epoch instead of only to the caller-visible `opId`.

The risk: rev0081 correctly rejected stale cleared-row replay, but the row/operation replay keys were based too heavily on lane/kind/opId. A fresh adapter can legitimately reuse the same caller-supplied operation id after restart or handoff. A receipt for the old cleared timeout should not suppress a new timeout quarantine merely because the op id string repeats.

rev0082 adds `operationEpoch` and `operationReplayKey` to timed-out quarantine rows. The release proof checks:

- exact stale ledger replay remains rejected;
- status-rewritten stale rows that preserve the old operation epoch reject by operation replay key;
- epoch-stripped stale rows reject as a downgrade replay;
- a fresh same-opId timeout quarantine with a different operation epoch imports and forces backpressure normally;
- the imported fresh quarantine still requires reviewed clearing before explicit recovery.

Non-claims: operation epochs are replay-scoping/collision-avoidance markers, not cryptographic identity, attestation, or tamper-proof storage. This proof does not claim provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, OPFS durability, cross-browser behavior, quota/eviction survival, latency SLOs, or production readiness.


Explicit non-claim marker: no provider cancellation, rollback, no-mutation-on-timeout, cross-browser, quota, eviction, crash, or production-readiness claim.
