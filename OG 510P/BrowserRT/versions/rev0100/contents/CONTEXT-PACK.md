# BrowserRT context pack — rev0100

Current head: `rev0100` / `0.0.100`. Codename: OPFS Block Store Rollback Valid Block Preserve. Package slug: `opfs-block-store-rollback-valid-block-preserve-current-proof`. Current task: `browser:opfs-block-store-rollback-valid-block-preserve-proof`. Current release proof: `opfs:block-store-rollback-valid-block-preserve-proof`. Current audit: `facility:opfs-block-store-rollback-valid-block-preserve-contract-audit`.

## What changed now

- Hardened `OpfsAsyncBlockStore.put()` failed-put rollback so an owned rollback performs a valid-block preserve check before deleting the final content-addressed path.
- Preserved valid final blocks after late trace/observer failure and after explicit aborts that occur once valid bytes are committed.
- Kept invalid or missing owned files on the existing delete rollback path.
- Added `rollbackIntegrityChecks`, `rollbackValidBlockPreserves`, `rollbackIntegrityCheckFailures`, `storage:opfs-block-put-rollback-preserved`, and reason `valid-final-block-preserved`.
- Added release proof `opfs:block-store-rollback-valid-block-preserve-proof`, managed Chromium proof `browser:opfs-block-store-rollback-valid-block-preserve-proof`, and contract audit `facility:opfs-block-store-rollback-valid-block-preserve-contract-audit` with current-office routing to `opfs-block-store-rollback-valid-block-preserve-current-proof`.
- Non-claims remain explicit: this does not prove cross-browser OPFS/Web Locks behavior, quota/eviction survival, crash or power-loss durability, fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness.

## Carried-forward rev0099 — OPFS Block Store Write Budget Duplicate Bypass

- Rev0099 made raw OPFS `writeBudgetGuard` duplicate-aware: valid no-op duplicate puts bypass estimate rejection, while new writes and corrupt repairs still check before mutation.
- Carried evidence includes `writeBudgetDuplicateBypasses`, `storage:opfs-block-write-budget-duplicate-bypass`, fake storage estimate recorder refactor, release/browser proofs, and contract audit.

# BrowserRT context pack — rev0099

Current head: `rev0099` / `0.0.99`. Codename: OPFS Block Store Write Budget Duplicate Bypass. Package slug: `opfs-block-store-write-budget-duplicate-bypass-current-proof`. Current task: `browser:opfs-block-store-write-budget-duplicate-bypass-proof`. Current release proof: `opfs:block-store-write-budget-duplicate-bypass-proof`. Current audit: `facility:opfs-block-store-write-budget-duplicate-bypass-contract-audit`.

## What changed now

Rev0099 makes raw OPFS write-budget enforcement duplicate-aware. `OpfsAsyncBlockStore.put()` no longer asks `StorageManager.estimate()` for an idempotent duplicate over an existing valid block, because that path writes no new bytes. The provider uses read-only prefix/bucket lookup, records `writeBudgetDuplicateBypasses`, emits `storage:opfs-block-write-budget-duplicate-bypass`, and returns budget metadata showing a duplicate bypass. New writes and corrupt repairs still check budget before OPFS mutation.

## Evidence to rerun

- `opfs:block-store-write-budget-duplicate-bypass-proof` — fake OPFS proof for verified duplicate bypass, unverified duplicate bypass, new-write rejection before mutation, corrupt-repair rejection while preserving the corrupt file, and passing-budget writes.
- `browser:opfs-block-store-write-budget-duplicate-bypass-proof` — managed Chromium proof with real OPFS/Web Locks and patched `navigator.storage.estimate()` call-count assertions.
- `facility:opfs-block-store-write-budget-duplicate-bypass-contract-audit` — static contract audit for runtime needles, fake harness estimate recorder, docs, manifest, impact map, surface inventory, package scripts, Makefile, `check_cube`, and current-office guards.

## Refactor note

`tools/lib/fake_opfs_harness.mjs` now exports `createStorageEstimateRecorder(...)` so future OPFS budget/quota proofs can assert estimate behavior and pre-estimate filesystem state without another bespoke harness.

## Boundaries

This slice is not a quota reservation, does not prove cross-browser behavior, quota/eviction survival, crash recovery, OPFS fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness. Browser posture remains browser-light except for the focused managed Chromium proof.


## Carried-forward first-read anchors from rev0097

# BrowserRT context pack — carried-forward rev0097

Carried-forward head: `rev0097` / `0.0.97`. Codename: OPFS Block Store Owned Rollback Guard. Package slug: `opfs-block-store-owned-rollback-guard-current-proof`. Current task: `browser:opfs-block-store-owned-rollback-guard-proof`. Current release proof: `opfs:block-store-owned-rollback-guard-proof`. Current audit: `facility:opfs-block-store-owned-rollback-guard-contract-audit`.

Runtime focus: `OpfsAsyncBlockStore` failed-put rollback now tracks whether the current `put()` owns the final block path. Duplicate/idempotent puts over a pre-existing valid block skip rollback on later failure, increment `rollbackOwnershipSkips`, emit `storage:opfs-block-put-rollback-skipped`, and preserve bytes. Owned write failures still remove newly-created final blocks.

Evidence focus: release proof uses the shared fake-opfs harness to simulate duplicate trace failure, duplicate abort during inspection, and owned write failure rollback. Browser proof uses managed Chromium, real OPFS, and real Web Locks, then drains locks after an `opfsWebLockGuardedBlockStore` write/verify. This remains a browser-light-plus-focused-browser slice, not a broad browser tier.

Non-claims: no cross-browser conformance, quota survival, eviction survival, crash/power-loss durability, fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness.

---

# BrowserRT context pack — rev0093 — Expected Fingerprint Blank Intent Guard and Current Office Refactor

Current task: `browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof`. Current audit: `facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit`. Runtime focus: block integrity plus expected-fingerprint restore binding for provider-backed timeout-quarantine ledgers and clearance receipts, now including a blank expected-fingerprint fail-closed guard so operator intent cannot be accidentally stripped by whitespace. `BlockStoreLaneAdapter` rejects blank, valid-but-wrong, or wrong-preclearance restore blocks before quarantine import or clearance receipt registration. `WebLockGuardedBlockStore` carries the browser OPFS/Web Locks path. Browser-light release evidence remains separate from managed Chromium OPFS/Web Locks evidence. Current-office audit covers npm current aliases, Makefile package/verify targets, central metadata, and manifest output prefixes. Non-claims: no provider cancellation, rollback, cross-browser, quota, eviction, crash, cryptographic attestation, or production readiness.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof,facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit --jobs 1
node tools/current_office_audit.mjs --json artifacts/audit/REV0093-CURRENT-OFFICE-AUDIT.json
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof --jobs 1
```

---
Receipt provenance binding sidecar: `browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`; `facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit`; registration provenance; bound provenance; blockVerified; browser-light.

Carried-forward quarantine evidence anchors: rev0091 browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit block integrity unverified restore WebLockGuardedBlockStore; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof facility:storage-lane-quarantine-clearance-replay-guard-contract-audit clearance receipt replay browser-light; browser:opfs-web-lock-quarantine-review-binding-proof quarantine review binding; browser:opfs-web-lock-quarantine-review-scope-proof quarantine-review-scope; browser:opfs-web-lock-quarantine-review-replay-key-scope-proof facility:storage-lane-quarantine-review-replay-key-scope-contract-audit operationReplayKey visible opId; browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof facility:storage-lane-quarantine-partial-clearance-replay-scope-contract-audit partial clearance uncleared row; browser:opfs-web-lock-quarantine-operation-replay-key-collision-proof facility:storage-lane-quarantine-operation-replay-key-collision-contract-audit; browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit lane-wide query-scope; browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit zero-row; browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit operationReplayKeys receipt integrity; browser:opfs-web-lock-quarantine-status-transition-import-proof facility:storage-lane-quarantine-status-transition-import-contract-audit browser-light; browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit quarantine-restore-backpressure; browser:opfs-web-lock-unsettled-orphan-review-proof facility:storage-lane-unsettled-orphan-review-contract-audit unsettled orphan review.
Carried-forward quarantine audit anchors for release compatibility: rev0091; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof; facility:storage-lane-quarantine-clearance-replay-guard-contract-audit; browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof; facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit; block integrity; unverified restore; browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof; facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit; quarantine-restore-backpressure; operationReplayKey; visible opId; partialClear; exactAfterPartial; unclearedImport; lanewide query scope; unsettled orphan; BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED; quarantine review scope; browser-light.
