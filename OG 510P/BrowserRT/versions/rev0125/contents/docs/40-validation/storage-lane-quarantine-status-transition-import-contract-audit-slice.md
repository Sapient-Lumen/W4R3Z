# Storage-lane quarantine status-transition import contract audit — rev0090

Current audit slice: `facility:storage-lane-quarantine-status-transition-import-contract-audit`.

The audit keeps the status-transition import proof wired to runtime code, release/browser probes, manifest entries, surface inventory, first-read docs, and non-claim text. Its most important runtime anchors are:

```text
statusTransitionReplacementCount
quarantineLedgerStatusTransitionReplacements
storage-lane:timed-out-quarantine-import-status-transition-replaced
removeExistingTimedOutRow
operationReplayKey
```

The audit exists because this bug is easy to reintroduce: visible `opId` is useful for review, but timeout-quarantine row identity is now `operationReplayKey`. Importing a status update by deleting only visible `opId` can leave stale rows in the old status bucket.

Non-claims: the audit does not launch Chromium, does not replace the release or browser proof, and does not claim provider cancellation, rollback, no-mutation-on-timeout, durability, quota/eviction survival, cryptographic attestation, tamper-proof storage, or production readiness.
