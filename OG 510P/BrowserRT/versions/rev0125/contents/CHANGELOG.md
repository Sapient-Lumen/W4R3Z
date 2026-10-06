## rev0125 — 2026-06-18 — Guarded staged recovery serialization

- Kept OPFS Raw Composite AbortSignal as the current proof office while fixing the next risky staged-write seam: recovery across provider instances must share the same coordination boundary as writes.
- Added `WebLockGuardedBlockStore.recoverStagedWrites()`, routed through the same exclusive Web Lock as guarded `put()`, `delete()`, and `cleanupForTest()`.
- Added a fake-OPFS/fake-Web-Locks proof that first demonstrates the unguarded race, then proves guarded recovery queues behind a live staged put, runs only after publish cleanup, and leaves the canonical `.blk` readable.
- Added `opfs:block-store-guarded-staged-recovery-proof` and `facility:opfs-block-store-guarded-staged-recovery-contract-audit`.
- Current proof anchors remain `opfs:block-store-raw-composite-abort-signal-proof`, `browser:opfs-block-store-raw-composite-abort-signal-proof`, and `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`; guarded staged recovery is the risk-reduction wedge under that office.

## rev0122 — 2026-06-18 — OPFS staged commit temp publish

- Kept OPFS Raw Composite AbortSignal as the current proof office while fixing the next risky storage seam: direct final-path writes during content-addressed puts.
- `OpfsAsyncBlockStore.put()` now writes new content to a same-bucket staged temp file, verifies the staged digest, publishes the canonical `.blk` only after staging succeeds, and deletes staged temp files on success or failure.
- Abort after staged close but before final publish now leaves no canonical digest and requires no final-path rollback; corrupt final-block repair now also routes through staged verification before republishing.
- Added `opfs:block-store-staged-commit-proof` and `facility:opfs-block-store-staged-commit-contract-audit`.
- Current proof anchors remain `opfs:block-store-raw-composite-abort-signal-proof`, `browser:opfs-block-store-raw-composite-abort-signal-proof`, and `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`; staged commit is the risk-reduction wedge under that office.

## rev0120 — 2026-06-18 — OPFS close-boundary runtime ownership

- Kept OPFS Raw Composite AbortSignal as the current proof office while taking the next risky runtime seam: provider close and runtime-owned storage teardown.
- `OpfsAsyncBlockStore` now has an explicit closed state plus `close()`/`closeAsync()`; post-close operations reject with `BRT_OPFS_STORE_CLOSED` and trace `storage:opfs-blockstore-closed-reject`.
- `BlockStoreLaneAdapter` and `WebLockGuardedBlockStore` now have explicit close states and `ownStore` ownership semantics so wrappers can close internally-created OPFS stores without stealing caller-owned stores.
- `boot().closeAsync()` now owns and closes OPFS async stores, OPFS storage-lane adapters, OPFS Web Lock guards, and their internally-created stores.
- Added a fake-OPFS behavioral proof for the close boundary: a closed provider rejects future work, but an acknowledged block survives a fresh provider reopen.
- Added a close-boundary contract audit and extended the runtime lifecycle audit/smoke test around OPFS-owned resources.
- Refactored cube ballast by compacting historical validation/architecture prose that was not part of current enforcement; see `artifacts/datacube-audit/REV0120-VALIDATION-DOC-BALLAST-COMPACTION.json`.
- Current proof anchors remain `opfs:block-store-raw-composite-abort-signal-proof`, `browser:opfs-block-store-raw-composite-abort-signal-proof`, and `facility:opfs-block-store-raw-composite-abort-signal-contract-audit`; `OpfsAsyncBlockStore`/`abortSignal` stay the current-office proof vocabulary.

## rev0119 — 2026-06-18 — Scoped lifecycle cancel escalation

- Added `OperationScope` as the concrete owner for child scopes, closeable resources, cleanup callbacks, abort propagation, and deterministic close reports.
- Linked `BoundedChannel`, runtime `channel()`, and worker calls to operation scopes so cancellation/close has a product object to attach to.
- Added opt-in `WorkerAgent.call({ terminateOnCancel: true, cancelGraceMs })` escalation and a non-cooperative busy-loop proof that termination, not prose, stops stuck abandoned worker work.
- Removed the package `./internal` export and updated public/package audits so the root package boundary stays sealed.
- Extended the runtime lifecycle audit and smoke test to cover scope, scoped resource close, cancellation escalation, and non-cooperative worker termination.

## rev0118 — 2026-06-18 — Bounded lifecycle cancellation close

- Kept the raw OPFS composite AbortSignal current office while making runtime lifecycle fixes instead of adding another proof family.
- BoundedChannel now limits pending senders and receivers, supports abort/timeout cleanup, and closes queued/waiting work explicitly.
- WorkerAgent now has a ready deadline, sends cooperative cancellation on timeout/caller abort, and classifies late settlements after cancellation.
- Node/browser worker shells now maintain per-call AbortControllers and acknowledge cancellation.
- boot() now tracks closeable resources, exposes ownedResources(), and adds deterministic closeAsync() while preserving legacy close() trace compatibility.

## Carried-forward audit anchors compacted for release checks

The following historical anchors are retained as a compact compatibility ledger, not as current-office doctrine: late-failure; timed-out-operation-late-failure; BRT_STORAGE_OPERATION_TIMEOUT; browser:opfs-web-lock-service-worker-shutdown-boundary-proof; browser:opfs-web-lock-service-worker-restart-update-proof; browser:opfs-web-lock-multi-failure-quarantine-proof; facility:storage-lane-multi-failure-quarantine-contract-audit; late-failure-clear-review-required; late-failure-clear-scope-required; browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof; facility:storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit; operationEpoch; opId collision; browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof; facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit; lane-wide; query; browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof; facility:storage-lane-quarantine-clearance-lanewide-scope-contract-audit; lane-ambiguous; lane-scoped; browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof; facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit; rejected-clearance-receipt-lane-binding; wrong-lane; browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof; facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit; registration provenance; blockVerified; rejected-clearance-receipt-provenance; browser:opfs-web-lock-quarantine-clearance-receipt-registration-integrity-proof; facility:storage-lane-quarantine-clearance-receipt-registration-integrity-contract-audit; direct receipt registration; rejected-clearance-receipt-integrity; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof; facility:storage-lane-quarantine-clearance-replay-guard-contract-audit; rejected-cleared-quarantine-replay; clearanceReceipt.v1; browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof; facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit; operationReplayKeys; receipt; browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof; facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit; restore registration gate; browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof; facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit; rejected-cleared-quarantine-row-replay; status-rewritten; browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof; facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit; lane-filtered import; browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof; facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit; timed-out-quarantine-clear-noop; rejected-noop-clear; browser:opfs-web-lock-quarantine-operation-replay-key-collision-proof; facility:storage-lane-quarantine-operation-replay-key-collision-contract-audit; operationReplayKey; visible opId; browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof; facility:storage-lane-quarantine-partial-clearance-replay-scope-contract-audit; partial clearance; uncleared row; browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof; facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit; blank expected-fingerprint; browser:opfs-web-lock-quarantine-review-replay-key-scope-proof; facility:storage-lane-quarantine-review-replay-key-scope-contract-audit.

## Older revision narrative

Detailed pre-rev0118 prose lives in prior packaged revisions. This cube keeps the machine-relevant anchor ledger above so release audits remain reachable while reducing cloudtainer ballast.
