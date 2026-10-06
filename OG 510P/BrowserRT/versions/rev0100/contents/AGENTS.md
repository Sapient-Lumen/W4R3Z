# BrowserRT agent notes — rev0100

Current revision: rev0100. Current version: 0.0.100. Codename: OPFS Block Store Rollback Valid Block Preserve.

Current package slug: `opfs-block-store-rollback-valid-block-preserve-current-proof`. Current task: `browser:opfs-block-store-rollback-valid-block-preserve-proof`. Current release proof: `opfs:block-store-rollback-valid-block-preserve-proof`. Current audit: `facility:opfs-block-store-rollback-valid-block-preserve-contract-audit`.

Focus for this head: OPFS failed-put rollback now preserves a valid content-addressed final block instead of deleting it after a late abort/observer failure. Runtime evidence includes `rollbackValidBlockPreserves`, `rollbackIntegrityChecks`, `storage:opfs-block-put-rollback-preserved`, and `valid-final-block-preserved`.

Primary commands are `npm run test:current`, `npm run audit:current`, and `npm run test:browser:current`. Keep broader browser work explicit; the cube is browser-light by default.

Boundary reminders: Non-claims remain explicit: this does not prove cross-browser OPFS/Web Locks behavior, quota/eviction survival, crash or power-loss durability, fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness.


## Carried-forward first-read anchors from rev0097

# BrowserRT agent handoff — carried-forward rev0097

Carried-forward revision: rev0097. Codename: OPFS Block Store Owned Rollback Guard. Current task: `browser:opfs-block-store-owned-rollback-guard-proof`. Current release proof: `opfs:block-store-owned-rollback-guard-proof`. Current audit: `facility:opfs-block-store-owned-rollback-guard-contract-audit`.

Priority for follow-on work: keep changes concrete and runtime-facing. This slice fixes the raw OPFS rollback ownership seam: a duplicate `put()` over a pre-existing valid block can fail or abort without deleting storage it did not create, and the evidence must show `rollbackOwnershipSkips`, `storage:opfs-block-put-rollback-skipped`, and preserved bytes.

Important carried-forward context: rev0095 added explicit AbortSignal handling for raw OPFS provider operations and rev0096 added the advisory write-budget guard. The shared fake-opfs harness is now the preferred way to prove OPFS edge cases without copy-pasting filesystem doubles. Storage-lane operation timeouts are still not provider cancellation. Non-claims remain explicit for cross-browser behavior, quota, eviction, crash, power-loss, fsync, Web Locks fairness, cryptographic attestation, and production readiness.

---

Historical revision: rev0093. Codename: Expected Fingerprint Blank Intent Guard and Current Office Refactor. Current task: `browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof`. Current audit: `facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit`. Work on runtime substance first: block integrity remains the provider-backed boundary; blank expected-fingerprint restore intent must fail closed before decode/import/registration, valid-but-wrong restore blocks must still reject, and current-office commands must point at this slice. Browser-light release proof plus managed Chromium proof are wired. Non-claims remain explicit: no provider cancellation, rollback, cross-browser, quota, eviction, crash, cryptographic attestation, or production readiness.

Run first:

```sh
make plan
python3 tools/check_cube.py
node tools/run_tests.mjs --tier release --id scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof,facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit --jobs 1
node tools/run_tests.mjs --tier browser --id browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof --jobs 1
```

---

Historical revision: rev0090
Codename: OPFS Web Lock Quarantine Status Transition Import Proof
Current task: `browser:opfs-web-lock-quarantine-status-transition-import-proof`
Current audit: `facility:storage-lane-quarantine-status-transition-import-contract-audit`

Work on substance first: status-transition import replacement for timeout-quarantine rows keyed by `operationReplayKey`. Keep browser-light release evidence separate from Managed Chromium evidence, and do not claim provider cancellation, rollback, no-mutation-on-timeout, cross-browser OPFS/Web Locks, quota survival, crash durability, or production readiness.

---

# Historical agents note — rev0089

Historical revision: rev0089. Codename: OPFS Web Lock Quarantine Clearance Replay Key Receipt Integrity Proof. Current task: `browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof`. Receipt integrity and `operationReplayKeys` are current; browser-light release proof plus managed Chromium proof.

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

# BrowserRT agent notes — rev0084

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

Non-claims remain explicit: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, fsync behavior, crash safety, power-loss safety, quota survival, eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness.  Unverified restore is not silently trusted; corrupt restore blocks fail before decode/import/register. Browser-light release evidence remains separate from managed Chromium evidence.

---


Carried-forward quarantine sidecar audit keywords: row replay; status-rewritten; browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof; facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit; rejected-cleared-quarantine-row-replay. no-op clearance receipt; timed-out-quarantine-clear-noop; rejected-noop-clear. clearance receipt replay; rejected-cleared-quarantine-replay. receipt registration integrity; rejected-clearance-receipt-integrity. receipt provenance binding; rejected-clearance-receipt-provenance. restore backpressure binding; review binding; review scope; legacy clear binding; unsettled orphan review; multi-failure quarantine; late-failure-clear-review-required; late-failure-clear-scope-required. Browser-light and managed Chromium evidence stay separated.
browser-light release evidence remains explicit.
Review-scope sidecar visibility: browser:opfs-web-lock-quarantine-clearance-replay-guard-proof and browser:opfs-web-lock-quarantine-review-scope-proof remain carried-forward guardrails.
Receipt provenance sidecar visibility: browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof; facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit; registration provenance; bound provenance; browser-light.
Epoch/receipt sidecar visibility: browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof; facility:storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit; operationEpoch; same visible op ids; downgrade replay. Receipt registration integrity: browser:opfs-web-lock-quarantine-clearance-receipt-registration-integrity-proof; facility:storage-lane-quarantine-clearance-receipt-registration-integrity-contract-audit; direct receipt registration; forged receipt; rejected-clearance-receipt-integrity. Clearance receipt replay: browser:opfs-web-lock-quarantine-clearance-replay-guard-proof; facility:storage-lane-quarantine-clearance-replay-guard-contract-audit; clearance receipt; replay; clearanceReceipt.v1; rejected-cleared-quarantine-replay; browser-light.
No-op clearance sidecar visibility: browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof; facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit; zero-row clearance receipt; browser-light.


Carried-forward lane-binding sidecar visibility: `browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof`; `facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit`; `rejected-clearance-receipt-lane-binding`; row-lane mismatch; valid lane-bound receipt replay rejection. These remain guardrails while rev0084 focuses on lane-filtered import.


rev0086 audit anchor: browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof / facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit. The restore registration gate proves wrong-lane restore fails closed when registration rejects, valid restore remains lane-bound, and Managed Chromium verifies the OPFS/Web Locks handoff. This is not cryptographic attestation and not production readiness.
Receipt provenance binding sidecar: `browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`; `facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit`; registration provenance; bound provenance; blockVerified; browser-light.

Carried-forward quarantine evidence anchors: rev0091 browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit block integrity unverified restore WebLockGuardedBlockStore; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof facility:storage-lane-quarantine-clearance-replay-guard-contract-audit clearance receipt replay browser-light; browser:opfs-web-lock-quarantine-review-binding-proof quarantine review binding; browser:opfs-web-lock-quarantine-review-scope-proof quarantine-review-scope; browser:opfs-web-lock-quarantine-review-replay-key-scope-proof facility:storage-lane-quarantine-review-replay-key-scope-contract-audit operationReplayKey visible opId; browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof facility:storage-lane-quarantine-partial-clearance-replay-scope-contract-audit partial clearance uncleared row; browser:opfs-web-lock-quarantine-operation-replay-key-collision-proof facility:storage-lane-quarantine-operation-replay-key-collision-contract-audit; browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit lane-wide query-scope; browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit zero-row; browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit operationReplayKeys receipt integrity; browser:opfs-web-lock-quarantine-status-transition-import-proof facility:storage-lane-quarantine-status-transition-import-contract-audit browser-light; browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit quarantine-restore-backpressure; browser:opfs-web-lock-unsettled-orphan-review-proof facility:storage-lane-unsettled-orphan-review-contract-audit unsettled orphan review.
Carried-forward quarantine audit anchors for release compatibility: rev0091; browser:opfs-web-lock-quarantine-clearance-replay-guard-proof; facility:storage-lane-quarantine-clearance-replay-guard-contract-audit; browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof; facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit; block integrity; unverified restore; browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof; facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit; quarantine-restore-backpressure; operationReplayKey; visible opId; partialClear; exactAfterPartial; unclearedImport; lanewide query scope; unsettled orphan; BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED; quarantine review scope; browser-light.
