# rev0107 OPFS raw composite AbortSignal contract audit slice

`facility:opfs-block-store-raw-composite-abort-signal-contract-audit` checks that the raw OPFS provider, release proof, browser proof, docs, manifest rows, impact map, surface inventory, current-office scripts, Makefile targets, and package pruning all agree on the rev0107 slice.

The audit is intentionally narrow. It prevents this runtime seam from becoming another drift-prone registry entry, but runtime evidence comes from the release and managed Chromium proofs.

Checked markers include `composeAbortSignals`, `OPFS_COMPOSITE_ABORT_CLEANUP`, `storage:opfs-block-composite-abort-signal`, `compositeAbortSignals`, `abortSignalOptionPairs`, `BRT_OPFS_OPERATION_ABORTED`, and `BRT_OPFS_ABORT_SIGNAL_INVALID`.

Non-claims remain explicit: no cross-browser coverage, no quota or eviction survival proof, no fsync or crash durability claim, no Web Locks fairness claim, and no production readiness claim.

Audit anchor: OpfsAsyncBlockStore / opfsasyncblockstore raw composite AbortSignal coverage.
