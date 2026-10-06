#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import {
  REVISION,
  VERSION,
  TraceLog,
  createCrossLaneScheduler,
  createBlockStoreLaneAdapter,
  digestBytesHex,
  validateTimedOutOperationQuarantineClearanceReceipt,
  timedOutOperationQuarantineClearanceReceiptFingerprint
} from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-partial-clearance-replay-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-PARTIAL-CLEARANCE-REPLAY-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  return {
    name: 'synthetic-partial-clearance-replay-scope-store', provider: 'synthetic-partial-clearance-replay-scope-provider-v1',
    async put(payload, fields = {}) { const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; records.set(digest, body); trace?.emit('synthetic-partial-clearance:put', { digest, bytes: body.byteLength, label: fields.label ?? null }); return Object.freeze({ ref: Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength }), digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null }); },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing block ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); return Object.freeze({ ok: Boolean(row), present: Boolean(row), digest, bytes: row?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: [...records.values()].reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size }); }
  };
}
function makeAdapter(label, store, trace) { return createBlockStoreLaneAdapter({ label, store, scheduler: scheduler(`${label}:scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 }); }
function withFingerprint(ledger) { const fingerprint = timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint }); }
function makeLedger({ suffix = 'partial-scope', lane = 'storage', epoch = `${REVISION}-partial-clearance-epoch` } = {}) {
  const now = Date.now();
  const success = Object.freeze({ opId: `${REVISION}-${suffix}-late-success`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-${suffix}-late-success`, timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: `sha256:${suffix}-success`, bytes: 32, disposition: 'synthetic-late-success' } });
  const failed = Object.freeze({ opId: `${REVISION}-${suffix}-late-failure`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-${suffix}-late-failure`, timeoutMs: 25, timedOutAtMs: now + 2, settledAtMs: now + 3, error: { name: 'SyntheticLateFailure', message: 'synthetic late failure for partial clearance replay scope proof', code: 'BRT_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_SYNTHETIC_LATE_FAILURE' } });
  const base = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, exportedAtMs: now + 4, label: `${REVISION}-partial-clearance-replay-scope-ledger`, reason: 'synthetic-partial-clearance-replay-scope-ledger', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failed]) });
  return withFingerprint(base);
}
function failedOnlyLedger(staleLedger) {
  return withFingerprint({ ...staleLedger, label: `${REVISION}-partial-clearance-uncleared-only-ledger`, reason: 'uncleared-row-only-after-partial-clearance', counts: Object.freeze({ total: 1, unsettled: 0, successful: 0, failed: 1 }), successfulTimedOutOperations: Object.freeze([]), failedTimedOutOperations: Object.freeze([staleLedger.failedTimedOutOperations[0]]) });
}
function selfConsistentReceipt(base) { const draft = { ...base }; draft.receiptFingerprint = timedOutOperationQuarantineClearanceReceiptFingerprint(draft); return Object.freeze(draft); }
function forgedFullCountReceiptFrom(partialReceipt, staleLedger) {
  const lane = partialReceipt.lane || 'storage'; const epoch = `${REVISION}-forged-partial-clearance-replay-scope-epoch`;
  const fakeSuccess = Object.freeze({ opId: `${REVISION}-forged-cleared-success`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-forged-cleared-success`, disposition: 'forged-success' });
  const fakeFailed = Object.freeze({ opId: `${REVISION}-forged-cleared-failure`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-forged-cleared-failure`, disposition: 'forged-failure', error: { code: 'BRT_FORGED_FAILURE', storageDisposition: 'BRT_FORGED_FAILURE' } });
  return selfConsistentReceipt({ ...partialReceipt, label: `${REVISION}-forged-full-count-partial-clearance-receipt`, preClearanceFingerprint: staleLedger.quarantineFingerprint, reviewFingerprint: staleLedger.reviewFingerprint, clearedCount: 2, successfulClearedCount: 1, failedClearedCount: 1, counts: Object.freeze({ total: 2, successful: 1, failed: 1 }), opIds: Object.freeze([fakeSuccess.opId, fakeFailed.opId]), categories: Object.freeze(['all']), cleared: Object.freeze({ successful: Object.freeze([fakeSuccess]), failed: Object.freeze([fakeFailed]) }) });
}
function registrationProvenance(adapter, receipt) { return Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: receipt.lane ?? adapter.lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: adapter.label, store: adapter.storeName, provider: adapter.providerName }); }

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const staleLedger = makeLedger();
  const unclearedLedger = failedOnlyLedger(staleLedger);

  const producer = makeAdapter(`${REVISION}-partial-clearance-producer`, store, trace);
  const importOriginal = producer.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'import-before-partial-clearance-scope-proof', markUnhealthy: false });
  assert.equal(importOriginal.ok, true); assert.equal(importOriginal.importedCount, 2); assert.equal(importOriginal.markUnhealthyForced, true);
  const successOpId = staleLedger.successfulTimedOutOperations[0].opId;
  const failedOpId = staleLedger.failedTimedOutOperations[0].opId;
  const partialReview = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opId: successOpId, reviewer: 'rev0087-release-probe', reviewToken: 'partial-clearance-review-token', reason: 'review-success-row-only' });
  const partialClear = producer.clearTimedOutOperationQuarantine({ reviewManifest: partialReview, requireReviewFingerprint: true, reason: 'clear-only-success-row-for-partial-clearance-scope-proof' });
  assert.equal(partialClear.ok, true); assert.equal(partialClear.clearedCount, 1); assert.equal(partialClear.successfulClearedCount, 1); assert.equal(partialClear.failedClearedCount, 0);
  const partialReceipt = producer.createTimedOutOperationQuarantineClearanceReceipt(partialClear, { reviewer: 'rev0087-release-probe', label: 'partial-clearance-receipt' });
  assert.equal(validateTimedOutOperationQuarantineClearanceReceipt(partialReceipt).ok, true);

  const partialAdapter = makeAdapter(`${REVISION}-partial-clearance-fresh`, store, trace);
  const partialRegister = partialAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(partialReceipt, { lane: 'storage', reason: 'register-partial-clearance-receipt', provenance: registrationProvenance(partialAdapter, partialReceipt) });
  assert.equal(partialRegister.ok, true); assert.equal(partialRegister.clearedCount, 1);
  const exactAfterPartial = partialAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'exact-stale-ledger-after-partial-clearance', markUnhealthy: false });
  assert.equal(exactAfterPartial.ok, false); assert.equal(exactAfterPartial.disposition, 'rejected-cleared-quarantine-row-replay'); assert.equal(exactAfterPartial.matchedRows.length, 1);
  assert.equal(partialAdapter.scheduler.snapshotLane('storage').healthy, true); assert.equal(partialAdapter.timedOutOperationQuarantine('storage').totalCount, 0);

  const unclearedImport = partialAdapter.importTimedOutOperationQuarantine(unclearedLedger, { lane: 'storage', reason: 'uncleared-row-only-after-partial-clearance', markUnhealthy: false });
  assert.equal(unclearedImport.ok, true); assert.equal(unclearedImport.importedCount, 1); assert.equal(unclearedImport.failedCount, 1); assert.equal(unclearedImport.markUnhealthyForced, true); assert.equal(partialAdapter.scheduler.snapshotLane('storage').healthy, false); assert.equal(partialAdapter.timedOutOperationQuarantine('storage').failedTimedOutOperationCount, 1);
  const failedReview = partialAdapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: failedOpId, reviewer: 'rev0087-release-probe', reviewToken: 'partial-clearance-uncleared-row-review-token', reason: 'review-uncleared-failed-row' });
  const failedClear = partialAdapter.clearTimedOutOperationQuarantine({ reviewManifest: failedReview, requireReviewFingerprint: true, reason: 'clear-uncleared-row-after-partial-clearance-scope-proof' });
  assert.equal(failedClear.ok, true); assert.equal(failedClear.clearedCount, 1); assert.equal(partialAdapter.recoverWhenStoreSettled ? typeof partialAdapter.recoverWhenStoreSettled : 'function', 'function');
  const healthy = partialAdapter.executor.markHealthy('storage', 'release-partial-clearance-recovery');
  assert.equal(healthy.healthy, true);

  const forgedAdapter = makeAdapter(`${REVISION}-partial-clearance-forged-full-count`, store, trace);
  const forgedReceipt = forgedFullCountReceiptFrom(partialReceipt, staleLedger);
  const forgedValidation = validateTimedOutOperationQuarantineClearanceReceipt(forgedReceipt);
  assert.equal(forgedValidation.ok, false); assert.ok(forgedValidation.errors.some((e) => e.includes('operationReplayKeys must match')));
  const forgedRegister = forgedAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(forgedReceipt, { lane: 'storage', reason: 'register-forged-full-count-receipt', provenance: registrationProvenance(forgedAdapter, forgedReceipt) });
  assert.equal(forgedRegister.ok, false); assert.equal(forgedRegister.disposition, 'rejected-clearance-receipt-integrity');
  const importAfterForgedFullCount = forgedAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'import-after-forged-full-count-receipt-with-wrong-rows', markUnhealthy: false });
  assert.equal(importAfterForgedFullCount.ok, true); assert.equal(importAfterForgedFullCount.importedCount, 2); assert.equal(importAfterForgedFullCount.markUnhealthyForced, true);

  const fullProducer = makeAdapter(`${REVISION}-full-clearance-producer`, store, trace);
  assert.equal(fullProducer.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'import-before-full-clearance-control', markUnhealthy: false }).ok, true);
  const fullReview = fullProducer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0087-release-probe', reviewToken: 'full-clearance-control-review-token', reason: 'review-full-clearance-control' });
  const fullClear = fullProducer.clearTimedOutOperationQuarantine({ reviewManifest: fullReview, requireReviewFingerprint: true, reason: 'clear-full-control' });
  assert.equal(fullClear.ok, true); assert.equal(fullClear.clearedCount, 2);
  const fullReceipt = fullProducer.createTimedOutOperationQuarantineClearanceReceipt(fullClear, { reviewer: 'rev0087-release-probe', label: 'full-clearance-control-receipt' });
  const fullAdapter = makeAdapter(`${REVISION}-full-clearance-fresh`, store, trace);
  assert.equal(fullAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(fullReceipt, { lane: 'storage', reason: 'register-full-clearance-control-receipt', provenance: registrationProvenance(fullAdapter, fullReceipt) }).ok, true);
  const exactAfterFull = fullAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'exact-stale-ledger-after-full-clearance-control', markUnhealthy: false });
  assert.equal(exactAfterFull.ok, false); assert.equal(exactAfterFull.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(exactAfterFull.matchedRows.length, 2);

  fullAdapter.schedulePut(`${REVISION}:partial-clearance-scope-recovery`, { id: `${REVISION}-partial-clearance-scope-recovery-put`, label: 'partial-clearance-scope-recovery-put' });
  const recovery = await fullAdapter.executor.executeDispatched(fullAdapter.scheduler.dispatchNext());
  assert.equal(recovery.ok, true);
  const writeVerify = await store.verify(recovery.result.ref);
  assert.equal(writeVerify.ok, true);
  const traceKinds = trace.kinds();
  for (const kind of ['storage-lane:timed-out-quarantine-import-row-replay-rejected', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'storage-lane:timed-out-quarantine-clearance-receipt-registered']) assert.ok(traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-partial-clearance-replay-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that partial timeout-quarantine clearance receipts cannot suppress still-uncleared rows through full-fingerprint replay rejection.', observations: { staleLedger, unclearedLedger, importOriginal, partialReview, partialClear, partialReceipt, partialRegister, exactAfterPartial, unclearedImport, failedReview, failedClear, forgedReceipt, forgedValidation, forgedRegister, importAfterForgedFullCount, fullClear, fullReceipt, exactAfterFull, recovery, writeVerify, traceKinds }, claimsChecked: ['partial clearance receipt does not turn full pre-clearance fingerprint into a full replay suppressor', 'full stale ledger after partial clear is rejected by row-replay guard, not exact-replay guard', 'uncleared row-only ledger still imports/backpressures for review', 'self-consistent full-count receipt with wrong rows does not suppress exact stale ledger import', 'genuine full clearance still rejects exact stale replay'], nonClaims: ['Browser-light synthetic provider only; no OPFS, Web Locks, cross-browser, durability, quota, or eviction claim.', 'No cryptographic attestation or tamper-proof storage claim.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, SLO, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-partial-clearance-replay-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed partial clearance replay scope proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_partial_clearance_replay_scope_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
