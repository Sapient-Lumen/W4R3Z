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

const TASK_ID = 'scheduler:storage-lane-quarantine-clearance-receipt-lane-binding-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-CLEARANCE-RECEIPT-LANE-BINDING-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticReceiptLaneBindingError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  const releaseSuccess = deferred();
  const releaseFailure = deferred();
  const state = { puts: 0, lateSuccesses: 0, lateFailures: 0 };
  return {
    name: 'synthetic-clearance-receipt-lane-binding-store', provider: 'synthetic-clearance-receipt-lane-binding-provider-v1', releaseSuccess, releaseFailure, state,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`;
      records.set(digest, body); state.puts += 1;
      trace?.emit('synthetic-clearance-receipt-lane-binding:put', { digest, bytes: body.byteLength, label: fields.label ?? null, purpose: fields.purpose ?? null });
      const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength });
      if (fields.label === 'receipt-lane-binding-late-success') { await releaseSuccess.promise; state.lateSuccesses += 1; }
      if (fields.label === 'receipt-lane-binding-late-failure') { await releaseFailure.promise; state.lateFailures += 1; throw codedError('BRT_SYNTHETIC_RECEIPT_LANE_BINDING_LATE_FAILURE', 'synthetic late failure after committed block', { digest }); }
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing block ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); return Object.freeze({ ok: Boolean(row), present: Boolean(row), digest, bytes: row?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: [...records.values()].reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}
function makeAdapter(label, store, trace, timeoutMs = 1000) {
  return createBlockStoreLaneAdapter({ label, store, scheduler: scheduler(`${label}:scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: timeoutMs });
}
function selfConsistentReceipt(base) {
  const draft = { ...base };
  draft.receiptFingerprint = timedOutOperationQuarantineClearanceReceiptFingerprint(draft);
  return Object.freeze(draft);
}

function registrationProvenance(adapter, receipt, source = 'adapter-create-clearance-receipt') {
  return Object.freeze({
    schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1',
    source,
    lane: receipt.lane ?? adapter.lane,
    receiptFingerprint: receipt.receiptFingerprint,
    preClearanceFingerprint: receipt.preClearanceFingerprint,
    reviewFingerprint: receipt.reviewFingerprint,
    adapterLabel: adapter.label,
    store: adapter.storeName,
    provider: adapter.providerName,
    refDigest: source === 'block-store-restore-clearance-receipt' ? 'sha256:synthetic-lane-binding' : undefined,
    bytes: source === 'block-store-restore-clearance-receipt' ? 512 : undefined
  });
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const producer = makeAdapter(`${REVISION}-receipt-lane-binding-producer`, store, trace, 80);
  producer.schedulePut(`${REVISION}:receipt-lane-binding-success`, { id: 'receipt-lane-binding-success-timeout', label: 'receipt-lane-binding-late-success' });
  producer.schedulePut(`${REVISION}:receipt-lane-binding-failure`, { id: 'receipt-lane-binding-failure-timeout', label: 'receipt-lane-binding-late-failure' });
  const d1 = producer.scheduler.dispatchNext(); const d2 = producer.scheduler.dispatchNext();
  const [t1, t2] = await Promise.all([producer.executor.executeDispatched(d1), producer.executor.executeDispatched(d2)]);
  assert.equal(t1.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(t2.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  store.releaseSuccess.resolve('release-success'); store.releaseFailure.resolve('release-failure');
  const settled = await producer.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  assert.equal(settled.ok, true);
  const before = producer.timedOutOperationQuarantine('storage');
  assert.equal(before.successfulTimedOutOperationCount, 1); assert.equal(before.failedTimedOutOperationCount, 1);
  const staleLedger = producer.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'receipt-lane-binding-export-before-clear' });
  const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0084-release-probe', reviewToken: 'receipt-lane-binding-review-token', reason: 'review-before-receipt-lane-binding' });
  const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-for-receipt-lane-binding' });
  assert.equal(clearResult.ok, true); assert.equal(clearResult.clearedCount, 2);
  const validReceipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0084-release-probe', label: 'release-receipt-lane-binding-valid-receipt' });
  const validValidation = validateTimedOutOperationQuarantineClearanceReceipt(validReceipt);
  assert.equal(validValidation.ok, true);

  const rowLaneMismatchReceipt = selfConsistentReceipt({ ...validReceipt, lane: 'maintenance' });
  const rowLaneMismatchValidation = validateTimedOutOperationQuarantineClearanceReceipt(rowLaneMismatchReceipt);
  assert.equal(rowLaneMismatchValidation.ok, false);
  assert.ok(rowLaneMismatchValidation.errors.some((message) => String(message).includes('cleared row lane storage must match receipt lane maintenance')));

  const wrongLaneAdapter = makeAdapter(`${REVISION}-receipt-lane-binding-wrong-lane`, store, trace, 1000);
  const wrongLaneRegister = wrongLaneAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'maintenance', reason: 'direct-register-valid-receipt-wrong-lane' });
  assert.equal(wrongLaneRegister.ok, false);
  assert.equal(wrongLaneRegister.disposition, 'rejected-clearance-receipt-lane-binding');
  const rowLaneMismatchRegister = wrongLaneAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(rowLaneMismatchReceipt, { lane: 'maintenance', reason: 'direct-register-row-lane-mismatched-receipt' });
  assert.equal(rowLaneMismatchRegister.ok, false);
  assert.equal(rowLaneMismatchRegister.disposition, 'rejected-clearance-receipt-integrity');
  const importAfterWrongLane = wrongLaneAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'import-after-wrong-lane-register-rejections', markUnhealthy: false });
  assert.equal(importAfterWrongLane.ok, true);
  assert.equal(importAfterWrongLane.markUnhealthyForced, true);
  const wrongLaneState = wrongLaneAdapter.scheduler.snapshotLane('storage');
  assert.equal(wrongLaneState.healthy, false);
  assert.equal(wrongLaneAdapter.timedOutOperationQuarantine('storage').totalCount, 2);

  const validAdapter = makeAdapter(`${REVISION}-receipt-lane-binding-valid`, store, trace, 1000);
  const validDirectRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'direct-register-valid-receipt-correct-lane', provenance: registrationProvenance(validAdapter, validReceipt) });
  assert.equal(validDirectRegister.ok, true);
  assert.equal(validDirectRegister.lane, 'storage');
  const replayAfterValid = validAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'stale-ledger-replay-after-valid-lane-bound-register', markUnhealthy: false });
  assert.equal(replayAfterValid.ok, false);
  assert.equal(replayAfterValid.disposition, 'rejected-cleared-quarantine-replay');
  const laneAfterReplay = validAdapter.scheduler.snapshotLane('storage');
  assert.equal(laneAfterReplay.healthy, true);
  assert.equal(validAdapter.timedOutOperationQuarantine('storage').totalCount, 0);

  const write = validAdapter.schedulePut(`${REVISION}:receipt-lane-binding-after-valid-register`, { id: 'receipt-lane-binding-after-valid-register-put', label: 'receipt-lane-binding-after-valid-register', operationTimeoutMs: 1000 });
  assert.equal(write.accepted, true);
  const drain = await validAdapter.drain({ maxSteps: 3 });
  const writeResult = drain.results.find((row) => row.opId === 'receipt-lane-binding-after-valid-register-put');
  assert.equal(writeResult?.ok, true);
  const writeVerify = await store.verify(writeResult.result.ref);
  assert.equal(writeVerify.ok, true);
  const traceKinds = trace.kinds();
  for (const kind of ['storage-lane:timed-out-quarantine-clearance-receipt-rejected', 'storage-lane:timed-out-quarantine-clearance-receipt-registered', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'storage-lane:timed-out-quarantine-import-replay-rejected']) assert.ok(traceKinds.includes(kind), `missing trace ${kind}`);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-receipt-lane-binding-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that timeout-quarantine clearance receipts cannot be directly registered under a lane different from their bound receipt lane, and row lanes must match receipt lane.', observations: { timeoutResults: [t1, t2], settled, before, staleLedger, reviewManifest, clearResult, validReceipt, validValidation, rowLaneMismatchReceipt, rowLaneMismatchValidation, wrongLaneRegister, rowLaneMismatchRegister, importAfterWrongLane, wrongLaneState, validDirectRegister, replayAfterValid, laneAfterReplay, writeResult, writeVerify, stats: validAdapter.snapshot().stats, executorStats: validAdapter.snapshot().executor.stats, traceKinds }, claimsChecked: ['receipt row lane mismatch fails receipt validation', 'direct registration cannot override a valid receipt into a different lane', 'rejected wrong-lane registration does not suppress stale quarantine import', 'valid lane-bound registration still rejects stale replay without poisoning lane health', 'later storage-lane write verifies'], nonClaims: ['Browser-light synthetic provider only; no OPFS, Web Locks, cross-browser, durability, quota, or eviction claim.', 'Receipt fingerprint and lane binding are deterministic integrity checks, not cryptographic attestation or tamper-proof storage.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, SLO, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-receipt-lane-binding-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed receipt lane-binding proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_clearance_receipt_lane_binding_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
