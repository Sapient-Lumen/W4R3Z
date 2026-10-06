# Start here — BrowserRT rev0100

Current packaged head: `rev0100`. Current task: `browser:opfs-block-store-rollback-valid-block-preserve-proof`. Current audit: `facility:opfs-block-store-rollback-valid-block-preserve-contract-audit`.

The current work is the valid-block preserve rollback slice for `OpfsAsyncBlockStore.put()`. Failed owned writes now inspect the final content-addressed block before delete rollback; if late trace failure or abort occurs after a valid block is already committed, BrowserRT preserves the block, reports `rollbackValidBlockPreserves`, and emits `storage:opfs-block-put-rollback-preserved`. Invalid or missing owned files still roll back.

Primary commands:

```bash
npm run test:current
npm run audit:current
npm run test:browser:current
```

Important current files:

- `src/opfs-block-store.mjs`
- `tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs`
- `tools/browser_opfs_block_store_rollback_valid_block_preserve_probe.mjs`
- `tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs`
- `docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md`

Audit/refactor focus: the OPFS rollback path now has explicit integrity-check counters and preserve traces, and the contract audit checks current-office routing so this safety slice stays connected to human commands without expanding registry bureaucracy.

Do not treat this as a broad browser conformance, durability, quota, crash-recovery, or production-readiness claim.

Browser posture: browser-light by default; focused managed Chromium proofs are run only for the current slice unless a broader browser tier is explicitly requested.

Non-claim terms carried for cube audits: cross-browser, quota, eviction, crash, browser-light, fsync.


## Carried-forward first-read anchors from rev0097

# Start here — BrowserRT carried-forward rev0097

Carried-forward packaged head: `rev0097`. Current task: `browser:opfs-block-store-owned-rollback-guard-proof`. Current audit: `facility:opfs-block-store-owned-rollback-guard-contract-audit`.

The current work is the `OpfsAsyncBlockStore` owned rollback guard. Duplicate/idempotent `put()` calls that find a pre-existing valid block no longer risk deleting that block if a later trace, abort, or inspection failure happens inside the same call. Those paths now produce `rollbackOwnershipSkips` and `storage:opfs-block-put-rollback-skipped`; owned final-block writes still roll back when they fail.

Suggested focused commands:

```sh
python3 tools/check_cube.py
npm run test:current
npm run audit:current
npm run test:browser:current
```

Boundary reminders: storage-lane timeouts still are not provider cancellation, and this revision still does not claim cross-browser coverage, quota survival, eviction survival, crash durability, OPFS fsync durability, Web Locks fairness, cryptographic attestation, or production readiness.

---

# START HERE — BrowserRT rev0093 — Expected Fingerprint Blank Intent Guard and Current Office Refactor

Historical packaged head: `rev0093`. Current task: `browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof`. Current audit: `facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit`.

Focus: Provider-backed block integrity plus timeout-quarantine ledger and clearance-receipt restore now fail closed when an operator supplies a blank expected-fingerprint string, instead of silently treating the restore as unpinned. Valid-but-wrong blocks still reject before import or receipt registration; the current-office command surface is now audited and historical current-named shortcuts were renamed to explicit replay aliases. This remains expected-fingerprint intent checking, not cryptographic attestation; no provider cancellation, rollback, durability, quota/eviction, cross-browser, latency SLO, or production-readiness claim is made.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof,facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit --jobs 1
node tools/current_office_audit.mjs --json artifacts/audit/REV0093-CURRENT-OFFICE-AUDIT.json
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof --jobs 1
```

---

# Historical BrowserRT rev0092 — OPFS Web Lock Quarantine Restore Expected Fingerprint Proof

Historical packaged head: `rev0092`. Historical task: `browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof`. Historical audit: `facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit`.

rev0092 introduced expected-fingerprint restore binding for valid-but-wrong timeout-quarantine ledgers and clearance receipts. rev0093 carries that evidence forward and adds the blank-intent fail-closed guard plus current-office command audit.

---

# START HERE — BrowserRT rev0092 — OPFS Web Lock Quarantine Restore Expected Fingerprint Proof

Non-claims include cross-browser, browser-light-vs-browser proof separation, quota, eviction, crash, durability, and production readiness.

Former packaged head: `rev0092`. Former task: `browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof`. Former audit: `facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit`.

Focus: Provider-backed timeout-quarantine ledger and clearance-receipt restore now require the expected fingerprint supplied by the restore caller; rev0091 block integrity verification remains the provider-backed block boundary. Valid block-store/OPFS blocks that belong to the wrong quarantine or clearance receipt reject before quarantine import or receipt registration, so a fresh adapter cannot accidentally install valid-but-wrong maintenance state. This is expected-fingerprint binding, not cryptographic attestation; no provider cancellation, rollback, durability, quota/eviction, cross-browser, latency SLO, or production-readiness claim is made.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof,facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof --jobs 1
```

---
Receipt provenance binding sidecar: `browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`; `facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit`; registration provenance; bound provenance; blockVerified; browser-light.

Carried-forward quarantine evidence anchors: rev0091 browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit block integrity unverified restore WebLockGuardedBlockStore; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof facility:storage-lane-quarantine-clearance-replay-guard-contract-audit clearance receipt replay browser-light; browser:opfs-web-lock-quarantine-review-binding-proof quarantine review binding; browser:opfs-web-lock-quarantine-review-scope-proof quarantine-review-scope; browser:opfs-web-lock-quarantine-review-replay-key-scope-proof facility:storage-lane-quarantine-review-replay-key-scope-contract-audit operationReplayKey visible opId; browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof facility:storage-lane-quarantine-partial-clearance-replay-scope-contract-audit partial clearance uncleared row; browser:opfs-web-lock-quarantine-operation-replay-key-collision-proof facility:storage-lane-quarantine-operation-replay-key-collision-contract-audit; browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit lane-wide query-scope; browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit zero-row; browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit operationReplayKeys receipt integrity; browser:opfs-web-lock-quarantine-status-transition-import-proof facility:storage-lane-quarantine-status-transition-import-contract-audit browser-light; browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit quarantine-restore-backpressure; browser:opfs-web-lock-unsettled-orphan-review-proof facility:storage-lane-unsettled-orphan-review-contract-audit unsettled orphan review.
Carried-forward quarantine audit anchors for release compatibility: rev0091; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof; facility:storage-lane-quarantine-clearance-replay-guard-contract-audit; browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof; facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit; block integrity; unverified restore; browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof; facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit; quarantine-restore-backpressure; operationReplayKey; visible opId; partialClear; exactAfterPartial; unclearedImport; lanewide query scope; unsettled orphan; BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED; quarantine review scope; browser-light.
