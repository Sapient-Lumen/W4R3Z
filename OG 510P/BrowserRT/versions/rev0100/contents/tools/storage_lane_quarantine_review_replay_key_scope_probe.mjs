#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateTimedOutOperationQuarantineClearanceReceipt } from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-review-replay-key-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-REVIEW-REPLAY-KEY-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function bytes(value) { return value instanceof Uint8Array ? value : new TextEncoder().encode(String(value)); }
function makeStore() {
  const records = new Map();
  return {
    name: 'synthetic-quarantine-review-replay-key-scope-store',
    provider: 'synthetic-quarantine-review-replay-key-scope-provider-v0',
    async put(payload, fields = {}) { const body = bytes(payload); const digest = `sha256:${fields.digestSuffix || records.size + 1}`; records.set(digest, body); return Object.freeze({ ref: { digest, backend: this.provider, bytes: body.byteLength }, digest, bytes: body.byteLength, duplicate: false }); },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing ${digest}`); return row; },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return Object.freeze({ ok: records.has(digest), present: records.has(digest), digest, bytes: records.get(digest)?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, blockCount: records.size }); }
  };
}
function makeScheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeAdapter(label, store, trace) { return createBlockStoreLaneAdapter({ label, store, scheduler: makeScheduler(`${label}:scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 }); }
function withFingerprint(ledger) { const fingerprint = timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint }); }
function successRow({ epoch, opId = 'shared-visible-review-scope-op', suffix, offset = 0 }) {
  const now = Date.now() + offset;
  return Object.freeze({ opId, kind: 'put', lane: 'storage', operationEpoch: epoch, operationReplayKey: `operation:storage:put:${epoch}:${opId}`, timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: Object.freeze({ digest: `sha256:${suffix}`, bytes: 32, disposition: 'synthetic-late-success' }) });
}
function twoRowLedger() {
  const first = successRow({ epoch: `${REVISION}:review-scope-epoch-a`, suffix: 'review-replay-key-scope-a', offset: 1 });
  const second = successRow({ epoch: `${REVISION}:review-scope-epoch-b`, suffix: 'review-replay-key-scope-b', offset: 3 });
  return withFingerprint({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', exportedAtMs: Date.now() + 5, label: `${REVISION}-quarantine-review-replay-key-scope-ledger`, reason: 'synthetic-merged-ledger-with-same-visible-opid-for-review-scope', counts: Object.freeze({ total: 2, unsettled: 0, successful: 2, failed: 0 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([first, second]), failedTimedOutOperations: Object.freeze([]) });
}
function oneRowLedger(row, label) { return withFingerprint({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', exportedAtMs: Date.now() + 7, label, reason: 'single-row-replay-key-scope-ledger', counts: Object.freeze({ total: 1, unsettled: 0, successful: 1, failed: 0 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([row]), failedTimedOutOperations: Object.freeze([]) }); }

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore();
  const ledger = twoRowLedger();
  const [first, second] = ledger.successfulTimedOutOperations;
  assert.equal(first.opId, second.opId);
  assert.notEqual(first.operationReplayKey, second.operationReplayKey);

  const adapter = makeAdapter(`${REVISION}-review-replay-key-scope-importer`, store, trace);
  const importResult = adapter.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'release-import-review-replay-key-scope-ledger', markUnhealthy: false });
  assert.equal(importResult.ok, true);
  assert.equal(importResult.importedCount, 2);
  assert.equal(importResult.markUnhealthyForced, true);

  const ambiguousReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opIds: [first.opId], reviewer: 'rev0088-release-probe', reviewToken: 'review-replay-key-scope-ambiguous-opid', reason: 'opid-only-review-should-be-ambiguous' });
  const ambiguousClear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: ambiguousReview, requireReviewFingerprint: true, reason: 'release-opid-only-clear-should-fail' });
  assert.equal(ambiguousClear.ok, false);
  assert.equal(ambiguousClear.code, 'timed-out-quarantine-clear-opid-ambiguous');
  assert.equal(adapter.timedOutOperationQuarantine('storage').totalCount, 2);

  const firstReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', operationReplayKeys: [first.operationReplayKey], reviewer: 'rev0088-release-probe', reviewToken: 'review-replay-key-scope-first', reason: 'operation-replay-key-scoped-first-clear' });
  const firstClear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: firstReview, requireReviewFingerprint: true, reason: 'release-clear-first-by-operation-replay-key' });
  assert.equal(firstClear.ok, true);
  assert.equal(firstClear.clearedCount, 1);
  assert.equal(firstClear.cleared.successful[0].operationReplayKey, first.operationReplayKey);
  assert.deepEqual(firstClear.operationReplayKeys, [first.operationReplayKey]);
  const quarantineAfterFirstClear = adapter.timedOutOperationQuarantine('storage');
  assert.equal(quarantineAfterFirstClear.totalCount, 1);
  assert.equal(quarantineAfterFirstClear.successfulTimedOutOperations[0].operationReplayKey, second.operationReplayKey);

  const blockedRecovery = adapter.markHealthy('storage', 'release-recovery-before-second-clear');
  assert.equal(blockedRecovery.healthy, false);
  assert.equal(blockedRecovery.reason, 'timed-out-operation-quarantine-active');

  const firstReceipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(firstClear, { reviewer: 'rev0088-release-probe', label: 'review-replay-key-scope-first-receipt' });
  const firstReceiptValidation = validateTimedOutOperationQuarantineClearanceReceipt(firstReceipt);
  assert.equal(firstReceiptValidation.ok, true);
  assert.deepEqual(firstReceipt.operationReplayKeys, [first.operationReplayKey]);
  const fresh = makeAdapter(`${REVISION}-review-replay-key-scope-fresh`, store, trace);
  const provenance = { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: firstReceipt.receiptFingerprint, preClearanceFingerprint: firstReceipt.preClearanceFingerprint, reviewFingerprint: firstReceipt.reviewFingerprint, adapterLabel: fresh.label, store: fresh.storeName, provider: fresh.providerName };
  const register = fresh.executor.registerTimedOutOperationQuarantineClearanceReceipt(firstReceipt, { lane: 'storage', reason: 'release-register-first-replay-key-scoped-receipt', provenance });
  assert.equal(register.ok, true);
  const firstReplay = fresh.importTimedOutOperationQuarantine(oneRowLedger(first, `${REVISION}-first-row-stale-replay`), { lane: 'storage', reason: 'release-first-row-stale-replay', markUnhealthy: false });
  assert.equal(firstReplay.ok, false);
  assert.equal(firstReplay.disposition, 'rejected-cleared-quarantine-row-replay');
  const secondStillImportable = fresh.importTimedOutOperationQuarantine(oneRowLedger(second, `${REVISION}-second-row-still-active`), { lane: 'storage', reason: 'release-second-row-not-cleared-yet', markUnhealthy: false });
  assert.equal(secondStillImportable.ok, true);
  assert.equal(secondStillImportable.importedCount, 1);
  assert.equal(secondStillImportable.markUnhealthyForced, true);

  const secondReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', operationReplayKeys: [second.operationReplayKey], reviewer: 'rev0088-release-probe', reviewToken: 'review-replay-key-scope-second', reason: 'operation-replay-key-scoped-second-clear' });
  const secondClear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: secondReview, requireReviewFingerprint: true, reason: 'release-clear-second-by-operation-replay-key' });
  assert.equal(secondClear.ok, true);
  assert.equal(secondClear.clearedCount, 1);
  assert.equal(adapter.timedOutOperationQuarantine('storage').totalCount, 0);
  const recovery = adapter.markHealthy('storage', 'release-recovery-after-replay-key-scoped-clears');
  assert.equal(recovery.healthy, true);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-review-replay-key-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that timeout-quarantine review and clearance can scope by operationReplayKey and rejects ambiguous visible-opId-only clearing.', observations: { ledger, importResult, ambiguousReview, ambiguousClear, firstReview, firstClear, quarantineAfterFirstClear, blockedRecovery, firstReceipt, firstReceiptValidation, register, firstReplay, secondStillImportable, secondReview, secondClear, recovery, traceKinds: trace.kinds() }, claimsChecked: ['opId-only review clear rejects when one visible opId maps to multiple operationReplayKeys', 'operationReplayKey-scoped review clears exactly one timed-out provider row', 'partial replay-key clearance does not suppress an uncleared same-opId row', 'lane recovery remains blocked until remaining timeout quarantine is reviewed and cleared'], nonClaims: ['Release-tier proof uses synthetic timeout quarantine rows; it is not browser storage durability evidence.', 'Operation replay keys are deterministic review scope metadata, not cryptographic attestation or a security boundary.', 'No provider cancellation, rollback, no-mutation-on-timeout, exactly-once, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-review-replay-key-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed review replay-key scope proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_review_replay_key_scope_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
// rev0088/deep-audit carry-forward anchor: same visible opId duplicateOperationKeyLedger rejected-ledger-integrity remain covered by the carried operationReplayKey collision proof while this proof narrows review scope.
