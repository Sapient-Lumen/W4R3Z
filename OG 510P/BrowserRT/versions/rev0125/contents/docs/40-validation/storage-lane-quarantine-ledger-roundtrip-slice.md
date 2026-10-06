# Storage-lane timeout quarantine ledger roundtrip slice

Current release-tier proof: `scheduler:storage-lane-quarantine-ledger-roundtrip-proof`.

This slice protects the maintenance boundary for storage-lane operations that time out and later settle. The proof creates one late provider success and one late provider failure after `BRT_STORAGE_OPERATION_TIMEOUT`, exports the mixed timeout quarantine ledger, imports it into a fresh storage lane, and verifies that recovery remains blocked until the mixed outcome quarantine is reviewed and scoped.

The runtime bug fixed in this slice was that quarantine export/import had grown as a partial branch without an executable proof: the exported ledger could lose its schema because of duplicate quarantine report methods, import counters were not initialized, and `clearTimedOutOperationQuarantine()` only proxied category-specific clears instead of supporting a reviewed/scoped mixed-outcome clear.

Evidence required:

- `storage-lane:timed-out-quarantine-export`
- `storage-lane:timed-out-quarantine-import`
- `storage-lane:timed-out-quarantine-clear-rejected`
- `storage-lane:timed-out-quarantine-cleared`
- `timed-out-quarantine-clear-review-required`
- `timed-out-quarantine-clear-review-token-required`
- `timed-out-quarantine-clear-scope-required`

Non-claims: this does not prove browser behavior, cross-browser behavior, OPFS durability, fsync, crash safety, quota survival, eviction survival, cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, production operator workflow, latency SLOs, or production readiness.

Explicit wording for contract audit: this slice does not prove cross-browser, quota, eviction, crash, durability, cancellation, rollback, SLO, or production behavior.

Audit phrase: not cancellation; not rollback; not production readiness.

The concrete schema string is brt.storageLane.timedOutOperationQuarantine.v1, and each unified clear uses a review token plus scoped operation ids or explicit lane-wide intent.
