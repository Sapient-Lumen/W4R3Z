# Storage-lane quarantine status-transition import slice — rev0090

Current runtime slice: `scheduler:storage-lane-quarantine-status-transition-import-proof`.

This slice protects the timeout-quarantine import path when the same timed-out provider operation is later imported under a different settlement status. Timeout quarantine rows are keyed by `operationReplayKey`, not by visible `opId` alone. A handoff ledger may first report a row as late-success, then a later ledger may report the same `operationReplayKey` as late-failure or unsettled. The importer must replace the old status bucket row instead of leaving the same operation present in multiple buckets.

The runtime now removes existing rows by `operationReplayKey` across unsettled, successful, and failed timeout-quarantine buckets before installing the imported row in its target bucket. It also removes legacy visible-`opId` entries for compatibility with older imported state, emits `storage-lane:timed-out-quarantine-import-status-transition-replaced`, and reports `statusTransitionReplacementCount`.

The release proof imports the same `operationReplayKey` through successful -> failed -> unsettled -> successful status transitions and verifies that the quarantine contains exactly one row after each transition. It then clears by review-bound replay key, creates a clearance receipt, and verifies that stale replay of the final transitioned row is rejected.

Non-claims: this is not provider cancellation, not rollback, not no-mutation-on-timeout, not exactly-once semantics, not automatic recovery, not cryptographic attestation, not tamper-proof storage, and not production readiness.
