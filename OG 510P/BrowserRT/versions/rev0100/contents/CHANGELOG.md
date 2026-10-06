## rev0100 — 2026-06-10 — OPFS Block Store Rollback Valid Block Preserve

- Hardened `OpfsAsyncBlockStore.put()` failed-put rollback with a valid-block preserve check before deleting an owned final content-addressed path.
- Preserves valid committed `.blk` bytes after late trace/observer failures and after explicit aborts that occur after close/commit; invalid or missing owned files still roll back through best-effort delete.
- Added `rollbackIntegrityChecks`, `rollbackValidBlockPreserves`, `rollbackIntegrityCheckFailures`, trace event `storage:opfs-block-put-rollback-preserved`, and reason `valid-final-block-preserved`.
- Added release proof `opfs:block-store-rollback-valid-block-preserve-proof`, managed Chromium proof `browser:opfs-block-store-rollback-valid-block-preserve-proof`, and contract audit `facility:opfs-block-store-rollback-valid-block-preserve-contract-audit`.
- Current-office routing moved to `opfs-block-store-rollback-valid-block-preserve-current-proof` while rev0099 duplicate-aware write-budget evidence remains carried forward.
- Non-claims remain explicit: no cross-browser conformance, quota survival, eviction survival, crash/power-loss durability, OPFS fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness.

## rev0099 — 2026-06-09 — OPFS Block Store Write Budget Duplicate Bypass

- Made `OpfsAsyncBlockStore.put()` duplicate-aware under `writeBudgetGuard`: existing valid content-addressed blocks now bypass budget estimation because the call performs no write.
- Added read-only existing-prefix/bucket helpers so duplicate discovery does not create OPFS directories merely to decide whether a budget check is needed.
- Kept new writes and corrupt-block repairs fail-closed: budget checks still run before OPFS creation, deletion, or repair mutation.
- Added `writeBudgetDuplicateBypasses`, `storage:opfs-block-write-budget-duplicate-bypass`, and budget result/error detail for this decision.
- Added release proof `opfs:block-store-write-budget-duplicate-bypass-proof`, managed Chromium proof `browser:opfs-block-store-write-budget-duplicate-bypass-proof`, and contract audit `facility:opfs-block-store-write-budget-duplicate-bypass-contract-audit` with current-office routing to `opfs-block-store-write-budget-duplicate-bypass-current-proof`.
- Refactored `tools/lib/fake_opfs_harness.mjs` with `createStorageEstimateRecorder(...)` so OPFS budget proofs can track estimate calls and tree state without cloning storage doubles.
- Non-claims remain explicit: not a storage reservation, no cross-browser conformance, quota survival, eviction survival, crash/power-loss durability, OPFS fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness.

## rev0098 — 2026-06-09 — OPFS Block Store Open Failure Recovery

- Hardened `OpfsAsyncBlockStore.open()` so a failed cached OPFS root/prefix open promise is cleared instead of permanently poisoning the provider instance.
- Added `openFailures`, `openRetryResets`, and `storage:opfs-blockstore-open-error` evidence for transient open failure recovery.
- Added release proof `opfs:block-store-open-failure-recovery-proof` covering first-open failure, same-store open retry, idempotent successful open reuse, and `put()` retry after an open failure.
- Added managed Chromium proof `browser:opfs-block-store-open-failure-recovery-proof` using a fail-once `navigator.storage.getDirectory()` patch plus real OPFS/Web Locks guarded write/verify and lock-drain checks.
- Added contract audit `facility:opfs-block-store-open-failure-recovery-contract-audit` and moved current-office package/Makefile/check-cube routing to `opfs-block-store-open-failure-recovery-current-proof`.
- Refactored the fake OPFS harness with a reusable fail-once directory-open hook for future transient-provider failure proofs.
- Non-claims remain explicit: no retry loop/backoff policy, no cross-browser conformance, quota survival, eviction survival, crash/power-loss durability, fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness.

## rev0097 — 2026-06-09

- Hardened `OpfsAsyncBlockStore.put()` rollback ownership. Duplicate/idempotent puts that only inspect a pre-existing valid block no longer delete that block if a later trace, abort, or inspection error occurs.
- Added `rollbackOwnershipSkips` and `storage:opfs-block-put-rollback-skipped` evidence, with failure reasons including `pre-existing-duplicate-block-not-owned-by-put` and `final-block-not-created-by-put`.
- Added release proof `opfs:block-store-owned-rollback-guard-proof` covering duplicate trace failure preservation, duplicate abort during inspection preservation, and owned failed-write rollback.
- Added managed Chromium proof `browser:opfs-block-store-owned-rollback-guard-proof` covering real OPFS duplicate failure preservation plus real Web Locks drain after a guarded write/verify.
- Added contract audit `facility:opfs-block-store-owned-rollback-guard-contract-audit` and moved current-office package/Makefile/check-cube routing to `opfs-block-store-owned-rollback-guard-current-proof`.
- Refactored this OPFS edge proof onto the shared fake-opfs harness rather than adding another bespoke filesystem double.
- Non-claims remain explicit: no cross-browser conformance, quota survival, eviction survival, crash/power-loss durability, fsync durability, Web Locks fairness, cryptographic attestation, multi-tab atomicity, or production readiness.

## rev0096 — 2026-06-09 — OPFS Block Store Write Budget Guard

- Added an opt-in `writeBudgetGuard` to `OpfsAsyncBlockStore` so raw OPFS `put()` can reject projected storage-budget violations before OPFS open/file mutation.
- The guard supports `minFreeBytes`, `maxUsageRatio`, and explicit `requireEstimate` policy, plus per-put overrides and legacy constructor shorthands.
- Added `BRT_OPFS_WRITE_BUDGET_EXCEEDED`, `BRT_OPFS_WRITE_BUDGET_INVALID`, and `BRT_OPFS_ESTIMATE_UNAVAILABLE` error paths, trace events, and stats.
- Refactored `tools/lib/fake_opfs_harness.mjs` so deterministic proofs can inject StorageManager-estimate-shaped quota/usage data.
- Added `opfs:block-store-write-budget-guard-proof`, `browser:opfs-block-store-write-budget-guard-proof`, and `facility:opfs-block-store-write-budget-guard-contract-audit` with docs and current-office routing.
- Carried forward rev0095 AbortSignal/rollback evidence without claiming provider cancellation, quota reservation, cross-browser behavior, eviction survival, crash durability, OPFS fsync durability, Web Locks fairness, cryptographic attestation, or production readiness.

## rev0095 — 2026-06-09 — OPFS Block Store AbortSignal Guard and Fake OPFS Harness Refactor

- Hardened `OpfsAsyncBlockStore` so explicit caller `signal` / `abortSignal` options are checked before provider checkpoints, including put/get/has/delete/verify/estimate/cleanup paths.
- Added `BRT_OPFS_OPERATION_ABORTED` and `BRT_OPFS_ABORT_SIGNAL_INVALID` to the raw OPFS error surface, with trace events for abort rejection and invalid signal shape.
- Added deterministic release proof `opfs:block-store-abort-signal-proof` covering pre-aborted operations, invalid signal values, mid-write abort rollback, and after-close rollback of a committed final block.
- Added managed Chromium proof `browser:opfs-block-store-abort-signal-proof` for real OPFS pre-abort/invalid-signal behavior and guarded OPFS/Web Locks compatibility with `signal: null`.
- Refactored the fake OPFS test double into `tools/lib/fake_opfs_harness.mjs` and moved the corrupt-block repair probe onto that shared harness.
- Added contract audit `facility:opfs-block-store-abort-signal-contract-audit` plus current-office routing for package scripts and Makefile.
- Non-claims remain explicit: this does not turn storage-lane operation timeouts into provider cancellation and does not prove cross-browser behavior, OPFS quota/eviction retention, crash/power-loss durability, fsync, Web Locks fairness, cryptographic attestation, or production readiness.

## rev0094 — 2026-06-09

- Hardened `src/web-lock-coordinator.mjs`: lock names and modes are normalized before any `.includes()` or native request path, `ifAvailable`/`steal` now require booleans, string values such as `"false"` reject instead of becoming truthy, invalid Web Locks option combinations fail closed locally, and invalid signal shapes reject with a BrowserRT code.
- Added `tools/web_lock_strict_option_guard_probe.mjs`, a release-tier fake-LockManager proof that invalid names/options do not call native `locks.request` and that explicit `ifAvailable: false` / `steal: false` values are preserved.
- Added `tools/browser_opfs_web_lock_strict_option_guard_probe.mjs`, a managed Chromium proof for real `navigator.locks` plus an OPFS Web Lock guarded block-store write/verify using adapter-compatible `signal: null`.
- Current task ids: `browser:opfs-web-lock-strict-option-guard-proof`, `coord:web-lock-strict-option-guard-proof`, and `facility:web-lock-strict-option-guard-contract-audit`.
- Added `tools/web_lock_strict_option_guard_contract_audit.mjs` and moved current-office commands/package metadata/manifest routing to the new strict option slice.
- Carried-forward audit anchors remain visible in the current head: `browser:opfs-web-lock-multi-failure-quarantine-proof`, `facility:storage-lane-multi-failure-quarantine-contract-audit`, `late-failure-clear-review-required`, and `late-failure-clear-scope-required`; status-transition, receipt-integrity, expected-fingerprint, and replay-guard sidecars remain historical replay evidence, not current-office aliases.
- Non-claims remain explicit: no fairness, starvation-freedom, cross-browser conformance, OPFS durability, quota survival, eviction survival, crash recovery, cryptographic attestation, or production-readiness claim.

## rev0093 — 2026-06-09

- Hardened `BlockStoreLaneAdapter` restore paths: blank expected-fingerprint strings now reject with `timed-out-quarantine-restore-expected-fingerprint-blank` or `timed-out-quarantine-clearance-receipt-restore-expected-fingerprint-blank` before restore decode/import/registration, instead of silently disabling the expected-fingerprint pin.
- Refactored the expected-fingerprint release/browser proof assertions into `tools/lib/quarantine_restore_expected_fingerprint_harness.mjs`; both Node and managed Chromium proof paths now check blank intent, valid-but-wrong ledger restore, valid-but-wrong receipt restore, wrong pre-clearance fingerprint, successful pinned restore, and stale replay rejection.
- Added `tools/current_office_audit.mjs` and wired it into package-time validation so primary current npm scripts, Makefile targets, central metadata, package slug, and manifest output prefixes fail fast on drift.
- Renamed historical `*current*` npm shortcuts to explicit `replay:*` aliases to keep current-office commands from masquerading as old proof slices.
- Carried-forward audit anchors remain visible in the current head: `browser:opfs-web-lock-multi-failure-quarantine-proof`, `facility:storage-lane-multi-failure-quarantine-contract-audit`, `late-failure-clear-review-required`, and `late-failure-clear-scope-required`; status-transition, receipt-integrity, expected-fingerprint, and replay-guard sidecars remain historical replay evidence, not current-office aliases.
- Non-claims remain explicit: expected fingerprint binding is operator/handoff intent checking, not cryptographic attestation or tamper-proof storage; no provider cancellation, rollback, durability, quota/eviction, cross-browser, throughput, or production-readiness claim.

## rev0092 — 2026-06-05

### OPFS Web Lock Quarantine Restore Expected Fingerprint Proof
Carried-forward audit anchors: browser:opfs-web-lock-multi-failure-quarantine-proof facility:storage-lane-multi-failure-quarantine-contract-audit late-failure-clear-review-required late-failure-clear-scope-required; browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit block integrity unverified restore; browser:opfs-web-lock-quarantine-status-transition-import-proof facility:storage-lane-quarantine-status-transition-import-contract-audit; browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit operationReplayKeys receipt.
Carried-forward quarantine compatibility anchors: browser:opfs-web-lock-multi-failure-quarantine-proof; facility:storage-lane-multi-failure-quarantine-contract-audit; late-failure-clear-review-required; late-failure-clear-scope-required; browser:opfs-web-lock-quarantine-review-replay-key-scope-proof; facility:storage-lane-quarantine-review-replay-key-scope-contract-audit; operationReplayKey; visible opId; browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof; facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit.


blockVerified restore provenance sidecar: `browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`; `facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit`; registration provenance rejects as `rejected-clearance-receipt-provenance`.
- Current task: `browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof`.
- Current release proof: `scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof`.
- Current audit: `facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit`.
- Runtime hardening: provider-backed timeout-quarantine ledger and clearance-receipt restore can now require caller-supplied expected fingerprints, so valid-but-wrong restore blocks fail closed before quarantine import or receipt registration.
- Proofs: release-light and Managed Chromium OPFS/Web Locks probes reject wrong expected quarantine, receipt, pre-clearance, or post-clearance fingerprints, while correct expected fingerprints still allow restore, stale replay rejection, explicit recovery, and later guarded OPFS writes.
- Carried-forward sidecar: clearance receipt provenance binding remains visible as historical evidence, but the rev0092 current office is expected-fingerprint restore binding.
- Non-claims: no cryptographic attestation, tamper-proof storage, provider cancellation, rollback, no-mutation-on-timeout, cross-browser OPFS/Web Locks, durability, quota/eviction survival, latency SLO, or production-readiness claim.

## rev0091 — 2026-06-05

### OPFS Web Lock Quarantine Receipt Restore Integrity Proof

- Current task: `browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof`.
- Current release proof: `scheduler:storage-lane-quarantine-receipt-restore-integrity-proof`.
- Current audit: `facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit`.
- Runtime hardening: `BlockStoreLaneAdapter` now verifies provider-backed block refs before restoring persisted timeout-quarantine ledgers or clearance receipts, rejecting corrupt restore blocks before `get()`, decode, import, or registration.
- Branch continuity: rev0090 `browser:opfs-web-lock-quarantine-status-transition-import-proof` remains carried forward so status-transition import replacement by `operationReplayKey` is not lost.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, quota/eviction survival, latency SLOs, or production readiness. Browser-light release evidence remains separate from managed Chromium evidence.

## rev0090 — 2026-06-05
Carried-forward multi-failure quarantine audit anchor: `browser:opfs-web-lock-multi-failure-quarantine-proof` and `facility:storage-lane-multi-failure-quarantine-contract-audit` remain protected with `late-failure-clear-review-required` and `late-failure-clear-scope-required`.


### OPFS Web Lock Quarantine Status Transition Import Proof

- Current task: `browser:opfs-web-lock-quarantine-status-transition-import-proof`.
- Current release proof: `scheduler:storage-lane-quarantine-status-transition-import-proof`.
- Current audit: `facility:storage-lane-quarantine-status-transition-import-contract-audit`.
- Runtime hardening: timeout-quarantine import now removes existing rows by `operationReplayKey` across unsettled/successful/failed buckets before installing a status-updated row.
- Added `statusTransitionReplacementCount`, `quarantineLedgerStatusTransitionReplacements`, and `storage-lane:timed-out-quarantine-import-status-transition-replaced` evidence.
- Browser evidence: managed Chromium exercises real OPFS/Web Locks via `WebLockGuardedBlockStore`, status-transition import replacement, stale replay rejection, recovery, and a later verified guarded write.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, cryptographic attestation, cross-browser OPFS/Web Locks behavior, OPFS durability, quota/eviction survival, SLOs, or production readiness.

## rev0089 — 2026-06-05

### OPFS Web Lock Quarantine Clearance Replay Key Receipt Integrity Proof

- Current task: `browser:opfs-web-lock-quarantine-clearance-replay-key-receipt-integrity-proof`.
- Current audit: `facility:storage-lane-quarantine-clearance-replay-key-receipt-integrity-contract-audit`.
- Added `scheduler:storage-lane-quarantine-clearance-replay-key-receipt-integrity-proof` and managed Chromium browser proof.
- Clearance receipts now reject missing/extra `operationReplayKeys` and cleared row operationReplayKey mismatch before stale timeout-quarantine replay suppression.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, quota/eviction survival, latency SLOs, or production readiness.

## rev0088 — 2026-06-05

### OPFS Web Lock Quarantine Review Replay Key Scope Proof

- Added `browser:opfs-web-lock-quarantine-review-replay-key-scope-proof` and `scheduler:storage-lane-quarantine-review-replay-key-scope-proof` to prove timeout-quarantine review/clearance must scope same-visible-opId rows by `operationReplayKey`.
- Runtime now rejects ambiguous opId-only timeout-quarantine clear/finalize with `timed-out-quarantine-clear-opid-ambiguous` / `rejected-ambiguous-opid-scope` unless review is lane-wide or replay-key scoped.
- Clearance receipts now carry `operationReplayKeys`, so partial review suppresses stale replay only for rows actually reviewed.
- Added `facility:storage-lane-quarantine-review-replay-key-scope-contract-audit` plus docs and surface wiring for the replay-key-scope boundary.
- Carried-forward multi-failure quarantine anchors remain visible: `browser:opfs-web-lock-multi-failure-quarantine-proof`, `facility:storage-lane-multi-failure-quarantine-contract-audit`, `late-failure-clear-review-required`, and `late-failure-clear-scope-required`.

Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, cryptographic attestation, cross-browser OPFS/Web Locks behavior, OPFS durability, quota/eviction survival, SLOs, or production readiness.

## rev0087 — 2026-06-05

### OPFS Web Lock Quarantine Operation Replay Key Collision Proof

- Current task: `browser:opfs-web-lock-quarantine-operation-replay-key-collision-proof`.
- Current release proof: `scheduler:storage-lane-quarantine-operation-replay-key-collision-proof`.
- Current audit: `facility:storage-lane-quarantine-operation-replay-key-collision-contract-audit`.
- Runtime hardening: timeout-quarantine ledgers now preserve distinct rows by `operationReplayKey` when visible opId / visible `opId` is reused, preventing import/clearance collapse.
- Sidecar hardening: partial clearance receipts must cover every imported row before exact stale-ledger replay suppression can fire; uncleared rows still import/backpressure.
- Carried sidecar: `browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof` / `facility:storage-lane-quarantine-partial-clearance-replay-scope-contract-audit` keeps partial clearance and uncleared row replay-scope evidence current.
- Browser evidence: managed Chromium exercises real guarded OPFS/Web Locks with duplicate visible op ids, duplicate replay-key rejection, clearance replay guard behavior, and a later verified guarded write.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, quota/eviction survival, throughput/latency SLO, or production readiness claim.


Carried sidecar: `browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof` / `facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit` keeps lane-wide query-scope evidence current without moving the package office.
## rev0086 — 2026-06-05

rev0086 carried-forward multi-failure audit anchor: browser:opfs-web-lock-multi-failure-quarantine-proof facility:storage-lane-multi-failure-quarantine-contract-audit late-failure-clear-review-required late-failure-clear-scope-required.
rev0086 audit phrase anchor: restore registration gate wrong-lane valid restore Managed Chromium not cryptographic attestation.

### OPFS Web Lock Quarantine Clearance Restore Registration Gate Proof

- Current task: `browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof`.
- Current release proof: `scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof`.
- Current audit: `facility:storage-lane-quarantine-clearance-restore-registration-gate-contract-audit`.
- Runtime hardening: clearance receipt restore now fails closed when registration rejects; wrong-lane block-store restore no longer reports `ok: true` or installs stale timeout-quarantine replay guard state.
- Browser evidence: managed Chromium persists a clearance receipt as a guarded OPFS content-addressed block, relaunches the same profile/origin, rejects wrong-lane restore, verifies stale import still backpressures, then validates provenance-bound storage-lane restore, stale replay rejection, and recovery write verification.
- Carried-forward guards remain visible: lane-wide clearance receipts are lane-scoped, lane-filtered imports do not silently drop rows, row/epoch replay guards remain active, and no-op clearance receipts remain rejected.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, quota/eviction survival, throughput/latency SLO, or production readiness claim.

## rev0085 — 2026-06-05

- Current task: `browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof`.
- Current release proof: `scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof`.
- Current audit: `facility:storage-lane-quarantine-clearance-lanewide-scope-contract-audit`.
- Runtime hardening: lane-wide clearance receipts are now lane-scoped.  `allowLaneWide: true` timeout-quarantine clearance receipts are now lane-scoped, not lane-ambiguous; a self-consistent receipt with no concrete `lane` fails validation/registration and cannot suppress stale quarantine import/backpressure.
- Carried forward: rev0084 lane-filter import guard remains wired so wrong-lane and accidental partial timeout-quarantine imports still fail closed unless partial import is explicit.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, automatic recovery, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, fsync/crash/power-loss safety, quota/eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness.

## rev0084 — 2026-06-05

### OPFS Web Lock Quarantine Lane Filter Import Guard Proof

- Current task: `browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof`.
- Current release proof: `scheduler:storage-lane-quarantine-lane-filter-import-guard-proof`.
- Current audit: `facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit`.
- Keyword anchor: lane-filtered import.
- Runtime hardening: lane-wide clearance receipts are now lane-scoped.  lane-filtered timeout-quarantine import now rejects wrong-lane non-empty ledgers as `rejected-lane-filter-empty-import` and rejects mixed-lane partial imports by default as `rejected-lane-filter-partial-import`.
- Explicit `allowPartialImport: true` remains available for reviewed handoff cases, but it forces storage-lane backpressure, rejects follow-on writes without mutation, and requires reviewed/scoped clearing plus explicit recovery.
- Carried-forward audit anchors: `browser:opfs-web-lock-multi-failure-quarantine-proof`, `facility:storage-lane-multi-failure-quarantine-contract-audit`, `late-failure-clear-review-required`, `late-failure-clear-scope-required`; `browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof`, `facility:storage-lane-quarantine-clearance-receipt-lane-binding-contract-audit`, `rejected-clearance-receipt-lane-binding`; `browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof`, `facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit`, `rejected-cleared-quarantine-row-replay`; `browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof`, `facility:storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit`, `operationEpoch`; `browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof`, `facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit`, `timed-out-quarantine-clear-noop`; `browser:opfs-web-lock-quarantine-clearance-replay-guard-proof`, `facility:storage-lane-quarantine-clearance-replay-guard-contract-audit`, `rejected-cleared-quarantine-replay`; `browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`, `facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit`, `rejected-clearance-receipt-provenance`; `browser:opfs-web-lock-unsettled-orphan-review-proof`, `facility:storage-lane-unsettled-orphan-review-contract-audit`, `BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED`.
- Branch continuity: the linked rev0083 clearance-receipt lane-binding work remains carried-forward evidence (`rejected-clearance-receipt-lane-binding`, row-lane mismatch, valid lane-bound receipt replay rejection) rather than being overwritten by the lane-filter branch.
- Non-claims preserved: no provider cancellation, rollback, no-mutation-on-timeout, cross-browser OPFS/Web Locks behavior, quota/eviction survival, crash/power-loss durability, cryptographic attestation, throughput/latency SLO, or production readiness claim.

## rev0082 — 2026-06-05

### OPFS Web Lock Quarantine Clearance Epoch Replay Guard Proof

- Current task: `browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof`.
- Current release proof: `scheduler:storage-lane-quarantine-clearance-epoch-replay-guard-proof`.
- Current audit: `facility:storage-lane-quarantine-clearance-epoch-replay-guard-contract-audit`.
- Runtime hardening: lane-wide clearance receipts are now lane-scoped.  timeout-quarantine clearance row replay guard state is now operation-epoch scoped through `operationEpoch` and `operationReplayKey`.
- Stale exact cleared-ledger replay still rejects, status-rewritten stale rows with the original epoch reject as cleared-row replay, and epoch-stripped downgrade replay rejects as `rejected-cleared-quarantine-row-replay-downgrade`.
- Fresh same visible op ids / opId collision from a different operation epoch imports normally, forces backpressure, and still requires reviewed/scoped clearing before explicit recovery.
- Carried-forward multi-failure quarantine guard remains visible in rev0082: `browser:opfs-web-lock-multi-failure-quarantine-proof`, `facility:storage-lane-multi-failure-quarantine-contract-audit`, `late-failure-clear-review-required`, and `late-failure-clear-scope-required`.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, cryptographic attestation, tamper-proof storage, cross-browser OPFS/Web Locks behavior, OPFS durability, quota/eviction survival, throughput/latency SLO, or production readiness claim.

Carried-forward sidecar note: `browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof` and `facility:storage-lane-quarantine-clearance-receipt-provenance-binding-contract-audit` remain visible; registration provenance and bound provenance checks continue to reject as `rejected-clearance-receipt-provenance`.

## rev0081 — 2026-06-05

### OPFS Web Lock Quarantine Clearance Row Replay Guard Proof

- Current task: `browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof`.
- Current audit: `facility:storage-lane-quarantine-clearance-row-replay-guard-contract-audit`.
- Runtime hardening: lane-wide clearance receipts are now lane-scoped.  clearance receipts now carry cleared row, operation, and replay keys so modified stale ledgers cannot reintroduce already-cleared timeout-quarantine rows after exact fingerprint clearance.
- Proofs: `scheduler:storage-lane-quarantine-clearance-row-replay-guard-proof` and `browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof` cover exact stale replay, modified cleared-row replay, and status-rewritten operation replay as `rejected-cleared-quarantine-row-replay` / `timed-out-quarantine-import-rejected-cleared-row` while keeping the lane healthy and quarantine-empty after rejection.
- Carried-forward multi-failure quarantine guard remains visible: `browser:opfs-web-lock-multi-failure-quarantine-proof`, `facility:storage-lane-multi-failure-quarantine-contract-audit`, `late-failure-clear-review-required`, and `late-failure-clear-scope-required`.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, cryptographic attestation, cross-browser OPFS/Web Locks behavior, durability, quota/eviction survival, latency SLO, or production readiness claim.

## rev0080 — 2026-06-05

### OPFS Web Lock Quarantine Noop Clearance Receipt Guard Proof

Current task: `browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof`
Current audit: `facility:storage-lane-quarantine-noop-clearance-receipt-guard-contract-audit`
Current release proof: `scheduler:storage-lane-quarantine-noop-clearance-receipt-guard-proof`

- Hardened timeout-quarantine maintenance so reviewed/scoped clears that match zero rows reject as `timed-out-quarantine-clear-noop` / `rejected-noop-clear`.
- Blocked creation and validation of zero-cleared `clearanceReceipt.v1` objects so stale pre-clearance ledger replay cannot be guarded by a receipt that cleared nothing.
- Added release-light and managed-Chromium proofs using `BlockStoreLaneAdapter`, `WebLockGuardedBlockStore`, real OPFS/Web Locks, stale-ledger replay rejection, explicit recovery, and guarded OPFS verification.
- Carried-forward multi-failure quarantine guard remains visible: `browser:opfs-web-lock-multi-failure-quarantine-proof`, `facility:storage-lane-multi-failure-quarantine-contract-audit`, `late-failure-clear-review-required`, and `late-failure-clear-scope-required`.
- Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, cross-browser OPFS/Web Locks, quota/eviction survival, crash/power-loss durability, throughput/latency SLO, or production readiness claim.


Carried-forward sidecar evidence retained in rev0080: `browser:opfs-web-lock-quarantine-clearance-replay-guard-proof`, `facility:storage-lane-quarantine-clearance-replay-guard-contract-audit`, `browser:opfs-web-lock-multi-failure-quarantine-proof`, `facility:storage-lane-multi-failure-quarantine-contract-audit`, `browser:opfs-web-lock-quarantine-legacy-clear-binding-proof`, `browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof`, `browser:opfs-web-lock-quarantine-review-scope-proof`, `browser:opfs-web-lock-unsettled-orphan-review-proof`, and `browser:opfs-web-lock-quarantine-clearance-receipt-registration-integrity-proof`. These are carried-forward checks, not the current office. direct receipt registration, forged receipt rejection, `rejected-clearance-receipt-integrity`, `clearanceReceipt.v1`, `late-failure-clear-review-required`, and `late-failure-clear-scope-required` remain visible as sidecar guardrails while rev0080 focuses on `timed-out-quarantine-clear-noop`.

Registration-integrity sidecar audit retained: `facility:storage-lane-quarantine-clearance-receipt-registration-integrity-contract-audit`; direct receipt registration and `rejected-clearance-receipt-integrity` remain carried-forward guardrails.

## rev0079 — 2026-06-05

- Current slice then: `browser:opfs-web-lock-quarantine-clearance-replay-guard-proof`.
- Added clearance receipt runtime registration so restored `clearanceReceipt.v1` data rejects stale cleared timeout-quarantine ledger replay as `rejected-cleared-quarantine-replay`.
- Added release-light and managed Chromium OPFS/Web Lock proofs plus `facility:storage-lane-quarantine-clearance-replay-guard-contract-audit`.
- Preserved non-claims: no provider cancellation, rollback, no-mutation-on-timeout, cryptographic attestation, tamper-proof storage, cross-browser behavior, OPFS durability, quota/eviction survival, or production readiness.
