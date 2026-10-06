# Storage-lane quarantine clearance lane-wide query scope slice

Current in rev0087: `scheduler:storage-lane-quarantine-clearance-lanewide-query-scope-proof`.

This slice hardens a narrow but risky clearance-receipt boundary.  rev0085 made `allowLaneWide: true` receipts require a concrete lane, but the receipt query/replay lookup path still treated lane-wide receipts as visible to every lane.  That is too broad for timeout-quarantine handoff tooling: lane-wide means all selected timeout rows within one lane, not a cross-lane or wrong-lane receipt.

The release-light proof creates a synthetic timeout-quarantine ledger for `storage`, reviews and clears it with `allowLaneWide: true`, registers the resulting lane-scoped clearance receipt, then verifies:

- `clearedTimedOutOperationQuarantineClearanceReceipts('storage')` returns the storage receipt.
- `clearedTimedOutOperationQuarantineClearanceReceipts('maintenance')` returns no receipt.
- exact stale `storage` replay still rejects as `rejected-cleared-quarantine-replay`.
- a `maintenance` timeout-quarantine ledger using the same visible operation ids imports normally, forces backpressure, and is not suppressed by the storage receipt.
- a later storage-lane write still verifies.

Non-claims: this proof does not claim not provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, cryptographic attestation, tamper-proof storage, cross-browser behavior, OPFS durability, quota/eviction survival, throughput, latency SLOs, or production readiness.

Explicit wrong-lane query assertion: wrong-lane receipt visibility is rejected by the lane-scoped query path.
