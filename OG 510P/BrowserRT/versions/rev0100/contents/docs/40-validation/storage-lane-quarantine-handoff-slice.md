# Storage-lane quarantine handoff slice — rev0073

`scheduler:storage-lane-quarantine-handoff-proof` is the browser-light release guard for the timeout-quarantine handoff boundary.

The risk is that a timed-out provider operation can later settle as success or failure, remain quarantined in one executor, and then be accidentally forgotten when a fresh storage-lane adapter is created. rev0073 adds an explicit timed-out-operation quarantine ledger:

- `exportTimedOutOperationQuarantine()` serializes unsettled, successful, and failed timed-out operations.
- `importTimedOutOperationQuarantine()` restores those rows into a fresh executor and marks affected lanes unhealthy.
- `markHealthy()` refuses direct reopening while timed-out-operation quarantine remains active.
- Reviewed/scoped `clearSuccessfulTimedOutOperations()` and `clearFailedTimedOutOperations()` are still required before recovery.

The release proof creates one late success and one late failure, exports both, imports them into a fresh adapter, proves follow-on writes are rejected with `noMutation`, proves direct `markHealthy()` is rejected, then clears success and failure separately before recovery.

Non-claims: no provider cancellation, rollback, no-mutation after provider dispatch, exactly-once semantics, automatic persistence, cross-browser behavior, quota survival, eviction survival, crash recovery, OPFS durability, throughput, latency SLO, or production readiness.

Audit keywords: reviewed/scoped handoff clearing is required; this is not cancellation and not rollback.
