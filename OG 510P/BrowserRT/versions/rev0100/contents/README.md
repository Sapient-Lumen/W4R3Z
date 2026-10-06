# BrowserRT rev0100 — OPFS Block Store Rollback Valid Block Preserve

Current packaged head: `rev0100`. Current task: `browser:opfs-block-store-rollback-valid-block-preserve-proof`. Current release proof: `opfs:block-store-rollback-valid-block-preserve-proof`. Current audit: `facility:opfs-block-store-rollback-valid-block-preserve-contract-audit`.

BrowserRT is a browser runtime and evidence cube focused on OPFS-backed block storage, Web Locks coordination, quarantine/restore behavior, and small reproducible validation slices.

## Current slice

The current work hardens `OpfsAsyncBlockStore.put()` failed-put rollback. Rev0097 made rollback ownership-aware, but an owned write could still delete the final `.blk` path during a late abort or trace/observer error even when that path already contained a valid content-addressed block. Rev0100 now inspects the final block before rollback deletion and preserves it when digest/bytes are valid.

The runtime now records `rollbackIntegrityChecks`, `rollbackValidBlockPreserves`, and `rollbackIntegrityCheckFailures`; the preserve path emits `storage:opfs-block-put-rollback-preserved` with reason `valid-final-block-preserved`. Invalid or missing owned final files still take the best-effort delete rollback path.

Run the current release and audit proof with:

```bash
npm run test:current
npm run audit:current
```

Run the focused managed-browser proof with:

```bash
npm run test:browser:current
```

Important current files:

- `src/opfs-block-store.mjs`
- `tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs`
- `tools/browser_opfs_block_store_rollback_valid_block_preserve_probe.mjs`
- `tools/opfs_block_store_rollback_valid_block_preserve_contract_audit.mjs`
- `tools/lib/fake_opfs_harness.mjs`
- `docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md`

Non-claims remain explicit: this does not prove cross-browser OPFS/Web Locks behavior, quota/eviction survival, crash or power-loss durability, fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness.

Browser posture: browser-light by default; focused managed Chromium proofs are run only for the current slice unless a broader browser tier is explicitly requested.


## Carried-forward first-read anchors from rev0097

# BrowserRT carried-forward rev0097 — OPFS Block Store Owned Rollback Guard

Carried-forward packaged head: `rev0097`. Current task: `browser:opfs-block-store-owned-rollback-guard-proof`. Current release proof: `opfs:block-store-owned-rollback-guard-proof`. Current audit: `facility:opfs-block-store-owned-rollback-guard-contract-audit`.

Focus: `OpfsAsyncBlockStore` failed-put rollback is now ownership-aware. A duplicate/idempotent `put()` that only discovers a pre-existing valid block and then fails or aborts records `rollbackOwnershipSkips` and emits `storage:opfs-block-put-rollback-skipped` instead of deleting that pre-existing valid block. Owned writes that create or repair the final `.blk` path still roll back on failure. This is runtime safety work against data loss at the raw OPFS block-store boundary, with fake-opfs release proof plus managed Chromium OPFS/Web Locks proof.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id opfs:block-store-owned-rollback-guard-proof,facility:opfs-block-store-owned-rollback-guard-contract-audit --jobs 1 --json artifacts/validation/REV0097-OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD-RUN.json
node tools/current_office_audit.mjs --json artifacts/audit/REV0097-CURRENT-OFFICE-AUDIT.json
node tools/run_tests.mjs --tier browser --id browser:opfs-block-store-owned-rollback-guard-proof --jobs 1 --json artifacts/validation/REV0097-BROWSER-OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD-RUN.json
```

Non-claims: this still does not prove cross-browser OPFS/Web Locks behavior, quota survival, eviction survival, crash or power-loss durability, fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness. Storage-lane timeouts still are not provider cancellation; rev0095 AbortSignal and rev0096 write-budget guard evidence are carried forward.

---

# BrowserRT rev0093 — Expected Fingerprint Blank Intent Guard and Current Office Refactor

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

# BrowserRT rev0090 — OPFS Web Lock Quarantine Status Transition Import Proof

Historical packaged head: `rev0090`. Current task: `browser:opfs-web-lock-quarantine-status-transition-import-proof`. Current audit: `facility:storage-lane-quarantine-status-transition-import-contract-audit`.

Focus: timeout-quarantine import status transitions. The same `operationReplayKey` can move across unsettled, successful, and failed buckets during handoff; rev0090 replaces stale bucket rows instead of letting one operation appear in multiple timeout-quarantine statuses. Runtime boundary keywords: `statusTransitionReplacementCount`, `quarantineLedgerStatusTransitionReplacements`, `storage-lane:timed-out-quarantine-import-status-transition-replaced`, `BlockStoreLaneAdapter`, and `WebLockGuardedBlockStore`. No provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, fsync behavior, crash safety, power-loss safety, quota survival, eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness. `WebLockGuardedBlockStore` carries the browser OPFS/Web Locks path. Browser-light release evidence remains separate from managed Chromium evidence.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-status-transition-import-proof,facility:storage-lane-quarantine-status-transition-import-contract-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-status-transition-import-proof --jobs 1
```

---

# Historical BrowserRT rev0089 — OPFS Web Lock Quarantine Clearance Replay Key Receipt Integrity Proof

Historical packaged head: `rev0089`. Current task: `browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof`. Current audit: `facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit`.

Focus: receipt integrity for timeout-quarantine clearance: `operationReplayKeys` must match the exact cleared rows before stale replay suppression. Browser-heavy evidence uses `WebLockGuardedBlockStore`; release evidence stays browser-light. Non-claims remain explicit: no provider cancellation, rollback, no-mutation-on-timeout, cross-browser OPFS/Web Locks, quota/eviction survival, crash durability, cryptographic attestation, or production readiness.

# BrowserRT current package — rev0088

Historical packaged head: `rev0088`  
Historical revision: rev0088  
Codename: OPFS Web Lock Quarantine Review Replay Key Scope Proof  
Current task: `browser:opfs-web-lock-quarantine-review-replay-key-scope-proof`  
Current release proof: `scheduler:storage-lane-quarantine-review-replay-key-scope-proof`  
Current audit: `facility:storage-lane-quarantine-review-replay-key-scope-contract-audit`

rev0088 prevents visible-opId maintenance over-clear: timeout-quarantine review and clearance now reject ambiguous same-opId rows unless they are scoped by operationReplayKey; clearance receipts carry operationReplayKeys so partial review suppresses replay only for rows actually reviewed.

This revision keeps rev0087's operationReplayKey row identity but fixes the next maintenance edge: a visible `opId` alone is not enough review scope when multiple timeout-quarantine rows share that label. OpId-only reviewed clear/finalize now fails as ambiguous, while operationReplayKey-scoped review clears exactly one intended row.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-review-replay-key-scope-proof,facility:storage-lane-quarantine-review-replay-key-scope-contract-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-review-replay-key-scope-proof --jobs 1
```

Non-claims remain explicit: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, fsync behavior, crash safety, power-loss safety, quota survival, eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness. This includes browser-light release evidence plus managed Chromium evidence.

---

# BrowserRT historical package — rev0086

Historical packaged head: `rev0086`  
Historical carried-forward revision: rev0086  
Codename: OPFS Web Lock Quarantine Clearance Restore Registration Gate Proof  
Current task: `browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof`  
Current release proof: `scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof`  
Current audit: `facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit`

rev0086 focuses on clearance receipt restore registration gating. `restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore()` now reports success only when the restored receipt also registers into the requested lane. Wrong-lane restore rejects as a restore failure and does not install stale timeout-quarantine replay guard state; stale ledgers still backpressure after rejected restore. Valid block-store restore carries `block-store-restore-clearance-receipt` provenance, rejects stale replay, and later guarded OPFS writes verify across a retained browser profile. This is browser-light plus managed Chromium evidence; lane-wide and lane-filter guards remain carried forward.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof,facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof --jobs 1
```

Non-claims remain explicit: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, fsync behavior, crash safety, power-loss safety, quota survival, eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness.

---

# BrowserRT historical package — rev0085

Historical packaged head: `rev0085`  
Historical carried-forward revision: rev0085  
Codename: OPFS Web Lock Quarantine Clearance Lanewide Scope Proof  
Carried-forward task: `browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof`  
Carried-forward release proof: `scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof`  
Carried-forward audit: `facility:storage-lane-quarantine-clearance-lanewide-scope-contract-audit`

rev0085 focuses on timeout-quarantine clearance receipt scope. `allowLaneWide: true` now means lane-wide within one concrete lane, not lane-ambiguous or cross-lane. A self-consistent lane-wide receipt with no `lane` is rejected before it can register as a stale replay suppressor. Rejected ambiguous registration leaves stale quarantine import/backpressure active; valid lane-scoped receipts still reject stale replay and later guarded OPFS writes verify. This is browser-light plus managed Chromium evidence; lane-filtered import guard remains carried forward.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof,facility:storage-lane-quarantine-clearance-lanewide-scope-contract-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof --jobs 1
```

Non-claims remain explicit: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, fsync behavior, crash safety, power-loss safety, quota survival, eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness.

---

# BrowserRT current package — rev0084

Historical packaged head: `rev0084`  
Historical carried-forward revision: rev0084  
Codename: OPFS Web Lock Quarantine Lane Filter Import Guard Proof  
Carried-forward task: `browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof`  
Carried-forward release proof: `scheduler:storage-lane-quarantine-lane-filter-import-guard-proof`  
Carried-forward audit: `facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit`

rev0084 focuses on lane-filtered timeout-quarantine import. Wrong-lane non-empty ledgers now reject as `rejected-lane-filter-empty-import`; mixed-lane partial imports reject by default as `rejected-lane-filter-partial-import`; explicit `allowPartialImport: true` remains available but forces storage-lane backpressure, rejects follow-on writes without mutation, and requires reviewed/scoped clearing plus explicit recovery.
lane-filtered import keywords: wrong-lane, partial import, allowPartialImport.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-lane-filter-import-guard-proof,facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof --jobs 1
```

Carried-forward epoch/row replay guard ids remain visible: `browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof`, `browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof`, and their contract audits. They are guardrails, not the rev0084 current office.

Non-claims remain explicit: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, fsync behavior, crash safety, power-loss safety, quota survival, eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness. `WebLockGuardedBlockStore` carries the browser OPFS/Web Locks path. Browser-light release evidence remains separate from managed Chromium evidence.

---



Runtime boundary keywords: BlockStoreLaneAdapter and WebLockGuardedBlockStore.
Carried-forward quarantine sidecar audit keywords: row replay; status-rewritten; browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof; facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit; rejected-cleared-quarantine-row-replay. no-op clearance receipt; timed-out-quarantine-clear-noop; rejected-noop-clear. clearance receipt replay; rejected-cleared-quarantine-replay. receipt registration integrity; rejected-clearance-receipt-integrity. receipt provenance binding; rejected-clearance-receipt-provenance. restore backpressure binding; review binding; review scope; legacy clear binding; unsettled orphan review; multi-failure quarantine; late-failure-clear-review-required; late-failure-clear-scope-required. Browser-light and managed Chromium evidence stay separated.
browser-light release evidence remains explicit.
Review-scope sidecar visibility: browser:opfs-web-lock-quarantine-clearance-replay-guard-proof and browser:opfs-web-lock-quarantine-review-scope-proof remain carried-forward guardrails.
Receipt provenance sidecar visibility: browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof; facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit; registration provenance; bound provenance; browser-light.
Epoch/receipt sidecar visibility: browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof; facility:storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit; operationEpoch; same visible op ids; downgrade replay. Receipt registration integrity: browser:opfs-web-lock-quarantine-clearance-receipt-registration-integrity-proof; facility:storage-lane-quarantine-clearance-receipt-registration-integrity-contract-audit; direct receipt registration; forged receipt; rejected-clearance-receipt-integrity. Clearance receipt replay: browser:opfs-web-lock-quarantine-clearance-replay-guard-proof; facility:storage-lane-quarantine-clearance-replay-guard-contract-audit; clearance receipt; replay; clearanceReceipt.v1; rejected-cleared-quarantine-replay; browser-light.
No-op clearance sidecar visibility: browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof; facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit; zero-row clearance receipt; browser-light.


Carried-forward lane-binding sidecar visibility: `browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof`; `facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit`; `rejected-clearance-receipt-lane-binding`; row-lane mismatch; valid lane-bound receipt replay rejection. These remain guardrails while rev0084 focuses on lane-filtered import.

Lane binding carried-forward note: clearance receipt lane binding remains a guarded sidecar.


rev0086 audit anchor: browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof / facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit. The restore registration gate proves wrong-lane restore fails closed when registration rejects, valid restore remains lane-bound, and Managed Chromium verifies the OPFS/Web Locks handoff. This is not cryptographic attestation and not production readiness.
Receipt provenance binding sidecar: `browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`; `facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit`; registration provenance; bound provenance; blockVerified; browser-light.

Carried-forward quarantine evidence anchors: rev0091 browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit block integrity unverified restore WebLockGuardedBlockStore; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof facility:storage-lane-quarantine-clearance-replay-guard-contract-audit clearance receipt replay browser-light; browser:opfs-web-lock-quarantine-review-binding-proof quarantine review binding; browser:opfs-web-lock-quarantine-review-scope-proof quarantine-review-scope; browser:opfs-web-lock-quarantine-review-replay-key-scope-proof facility:storage-lane-quarantine-review-replay-key-scope-contract-audit operationReplayKey visible opId; browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof facility:storage-lane-quarantine-partial-clearance-replay-scope-contract-audit partial clearance uncleared row; browser:opfs-web-lock-quarantine-operation-replay-key-collision-proof facility:storage-lane-quarantine-operation-replay-key-collision-contract-audit; browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit lane-wide query-scope; browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit zero-row; browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit operationReplayKeys receipt integrity; browser:opfs-web-lock-quarantine-status-transition-import-proof facility:storage-lane-quarantine-status-transition-import-contract-audit browser-light; browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit quarantine-restore-backpressure; browser:opfs-web-lock-unsettled-orphan-review-proof facility:storage-lane-unsettled-orphan-review-contract-audit unsettled orphan review.
Carried-forward quarantine audit anchors for release compatibility: rev0091; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof; facility:storage-lane-quarantine-clearance-replay-guard-contract-audit; browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof; facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit; block integrity; unverified restore; browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof; facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit; quarantine-restore-backpressure; operationReplayKey; visible opId; partialClear; exactAfterPartial; unclearedImport; lanewide query scope; unsettled orphan; BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED; quarantine review scope; browser-light.
