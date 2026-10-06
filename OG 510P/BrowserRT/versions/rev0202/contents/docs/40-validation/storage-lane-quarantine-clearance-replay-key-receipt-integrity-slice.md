# Storage-lane quarantine clearance replay-key receipt integrity slice

Current release proof: `scheduler:storage-lane-quarantine-clearance-replay-key-receipt-integrity-proof`.

Timeout-quarantine clearance receipts must bind their public `operationReplayKeys` list to the exact cleared row identities. The release-tier probe imports a synthetic mixed late-success / late-failure quarantine ledger, performs reviewed clearance, and checks that `createTimedOutOperationQuarantineClearanceReceipt()` carries the exact cleared row `operationReplayKeys`.

The proof rejects missing/extra replay keys and rejects a cleared row operationReplayKey mismatch before a receipt can suppress stale timeout-quarantine replay.

Runtime hooks: `operationReplayKeys must match cleared row operationReplayKeys`, `cleared row operationReplayKey mismatch`, `quarantineClearanceReceiptReplayKeyBindingRejected`, `clearanceRowsOperationReplayKeys`.

## Non-claims

This is not provider cancellation, not rollback, not a no-mutation-on-timeout claim, not cryptographic attestation, not tamper-proof storage, not OPFS durability, not quota/eviction survival, and not production readiness.
