# Storage-lane quarantine review replay-key scope slice

Task: `scheduler:storage-lane-quarantine-review-replay-key-scope-proof`

This release-light slice covers the review/clearance risk left after timeout-quarantine rows became keyed by `operationReplayKey`. Distinct timeout rows may legitimately share the same visible `opId` when they come from different operation epochs. A maintenance review scoped only to that visible `opId` would be ambiguous and could over-clear more than the operator intended.

The proof imports a synthetic ledger with two late-success timeout-quarantine rows that share a visible `opId` but have distinct `operationReplayKey` values. It verifies an opId-only review clear fails as `timed-out-quarantine-clear-opid-ambiguous`, then clears exactly one row by `operationReplayKey`. A clearance receipt for that first row rejects stale replay of the cleared row but does not suppress the uncleared same-opId row. Recovery remains blocked until the second row is separately reviewed and cleared by its own replay key.

Non-claims: this is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, cryptographic attestation, durability, quota/eviction survival, throughput, latency, or production-readiness evidence.
