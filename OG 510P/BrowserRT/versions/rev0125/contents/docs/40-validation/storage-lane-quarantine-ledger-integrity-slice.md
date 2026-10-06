# Storage-lane quarantine ledger integrity slice — rev0074

Current task: `scheduler:storage-lane-quarantine-ledger-integrity-proof`  
Current audit: `facility:storage-lane-quarantine-ledger-integrity-contract-audit`

This release-tier proof covers the browser-light contract for `brt.storageLane.timedOutOperationQuarantine.v1` import integrity. The risky boundary is not ledger export itself; it is a fresh adapter accepting a malformed, partial, ambiguous, or duplicate quarantine ledger and thereby losing timeout quarantine state during handoff.

The proof verifies that import now **fail closed** and is **atomic**. Ledgers with missing `counts`, a `counts.total mismatch`, a missing required bucket array, a duplicate opId across buckets, a missing opId, or an unsupported schema reject as `timed-out-quarantine-import-rejected` with disposition `rejected-ledger-integrity`. Rejection leaves the quarantine maps unchanged and does not mark the storage lane unhealthy.

A valid ledger still imports, marks the lane unhealthy as `timed-out-operation-quarantine-imported`, rejects follow-on writes with `noMutation`, requires reviewed/scoped clearing, and only then permits explicit recovery.

Non-claims: this is not cryptographic attestation, not tamper-proof signing, not production ledger governance, not browser execution, not cancellation, not rollback, not no-mutation-on-timeout, not OPFS durability, not cross-browser behavior, not quota or eviction evidence, and not production readiness.

Exact guardrail phrase: not cryptographic, not production.
