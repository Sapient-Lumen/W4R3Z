# rev0081 storage-lane quarantine clearance row replay guard contract audit slice

Audit task: `facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit`

The audit checks that the rev0081 row-replay guard is wired through runtime code, release-light proof, browser proof, docs, manifest, impact map, surface inventory, package scripts, Makefile, changelog, and first-read currentness surfaces.

Required runtime markers include:

```text
clearedRowKeys
clearedOperationKeys
clearedReplayKeys
timed-out-quarantine-import-rejected-cleared-row
rejected-cleared-quarantine-row-replay
storage-lane:timed-out-quarantine-import-row-replay-rejected
quarantineLedgerRowReplayRejected
```

The audit is static and browser-light. It is not a substitute for the managed Chromium proof.
