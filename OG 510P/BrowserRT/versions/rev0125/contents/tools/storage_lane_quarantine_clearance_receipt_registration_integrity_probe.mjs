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

const TASK_ID = 'scheduler:storage-lane-quarantine-clearance-receipt-registration-integrity-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-CLEARANCE-RECEIPT-REGISTRATION-INTEGRITY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticReceiptRegistrationIntegrityError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  const releaseSuccess = deferred();
  const releaseFailure = deferred();
  const state = { puts: 0, lateSuccesses: 0, lateFailures: 0 };
  return {
    name: 'synthetic-clearance-receipt-registration-integrity-store', provider: 'synthetic-clearance-receipt-registration-integrity-provider-v0', releaseSuccess, releaseFailure, state,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`;
      records.set(digest, body); state.puts += 1;
      trace?.emit('synthetic-clearance-receipt-registration-integrity:put', { digest, bytes: body.byteLength, label: fields.label ?? null });
      const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength });
      if (fields.label === 'registration-integrity-late-success') { await releaseSuccess.promise; state.lateSuccesses += 1; }
      if (fields.label === 'registration-integrity-late-failure') { await releaseFailure.promise; state.lateFailures += 1; throw codedError('BRT_SYNTHETIC_RECEIPT_REGISTRATION_LATE_FAILURE', 'synthetic late failure after committed block', { digest }); }
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
function makeSelfConsistentReceipt(base) {
  const draft = { ...base };
  draft.receiptFingerprint = timedOutOperationQuarantineClearanceReceiptFingerprint(draft);
  return draft;
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const producer = makeAdapter(`${REVISION}-receipt-registration-integrity-producer`, store, trace, 80);
  producer.schedulePut(`${REVISION}:registration-integrity-success`, { id: 'registration-integrity-success-timeout', label: 'registration-integrity-late-success' });
  producer.schedulePut(`${REVISION}:registration-integrity-failure`, { id: 'registration-integrity-failure-timeout', label: 'registration-integrity-late-failure' });
  const d1 = producer.scheduler.dispatchNext(); const d2 = producer.scheduler.dispatchNext();
  const [t1, t2] = await Promise.all([producer.executor.executeDispatched(d1), producer.executor.executeDispatched(d2)]);
  assert.equal(t1.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(t2.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  store.releaseSuccess.resolve('release-success'); store.releaseFailure.resolve('release-failure');
  const settled = await producer.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  assert.equal(settled.ok, true);
  const before = producer.timedOutOperationQuarantine('storage');
  assert.equal(before.successfulTimedOutOperationCount, 1); assert.equal(before.failedTimedOutOperationCount, 1);
  const staleLedger = producer.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'registration-integrity-export-before-clear' });
  const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0080-release-probe', reviewToken: 'registration-integrity-review-token', reason: 'review-before-registration-integrity' });
  const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-for-registration-integrity-valid-receipt' });
  assert.equal(clearResult.ok, true); assert.equal(clearResult.clearedCount, 2);
  const validReceipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0080-release-probe', label: 'registration-integrity-valid-receipt' });
  const validValidation = validateTimedOutOperationQuarantineClearanceReceipt(validReceipt);
  assert.equal(validValidation.ok, true);

  const wrongFingerprintReceipt = { ...validReceipt, receiptFingerprint: 'brt-qclear-v1:forged000000000000' };
  const badOpIdsReceipt = makeSelfConsistentReceipt({ ...validReceipt, opIds: ['not-the-cleared-op-id'] });
  const preReviewMismatchReceipt = makeSelfConsistentReceipt({ ...validReceipt, preClearanceFingerprint: 'brt-qfp-v1:stale-review-mismatch' });

  const forgedAdapter = makeAdapter(`${REVISION}-receipt-registration-integrity-forged`, store, trace, 1000);
  const wrongFingerprintRegister = forgedAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(wrongFingerprintReceipt, { lane: 'storage', reason: 'direct-register-wrong-fingerprint' });
  const badOpIdsRegister = forgedAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(badOpIdsReceipt, { lane: 'storage', reason: 'direct-register-opid-mismatch' });
  const preReviewMismatchRegister = forgedAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(preReviewMismatchReceipt, { lane: 'storage', reason: 'direct-register-pre-review-mismatch' });
  for (const result of [wrongFingerprintRegister, badOpIdsRegister, preReviewMismatchRegister]) {
    assert.equal(result.ok, false);
    assert.equal(result.disposition, 'rejected-clearance-receipt-integrity');
  }
  const importAfterForgedRegisters = forgedAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'import-after-forged-direct-registers', markUnhealthy: false });
  assert.equal(importAfterForgedRegisters.ok, true);
  assert.equal(importAfterForgedRegisters.markUnhealthyForced, true);
  const forgedLane = forgedAdapter.scheduler.snapshotLane('storage');
  assert.equal(forgedLane.healthy, false);
  assert.equal(forgedAdapter.timedOutOperationQuarantine('storage').totalCount, 2);

  const receiptAdapter = makeAdapter(`${REVISION}-receipt-registration-integrity-valid`, store, trace, 1000);
  const bareValidDirectRegister = receiptAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'direct-register-valid-receipt-without-provenance' });
  assert.equal(bareValidDirectRegister.ok, false);
  assert.equal(bareValidDirectRegister.disposition, 'rejected-clearance-receipt-provenance');
  const mismatchedProvenanceRegister = receiptAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'direct-register-valid-receipt-with-mismatched-provenance', provenance: { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: 'brt-qclear-v1:not-the-receipt', preClearanceFingerprint: validReceipt.preClearanceFingerprint, adapterLabel: 'manual', store: 'manual', provider: 'manual' } });
  assert.equal(mismatchedProvenanceRegister.ok, false);
  assert.equal(mismatchedProvenanceRegister.disposition, 'rejected-clearance-receipt-provenance');
  const validDirectRegister = receiptAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'direct-register-valid-receipt-with-bound-provenance', provenance: { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: validReceipt.receiptFingerprint, preClearanceFingerprint: validReceipt.preClearanceFingerprint, reviewFingerprint: validReceipt.reviewFingerprint, adapterLabel: 'registration-integrity-valid-adapter', store: store.name, provider: store.provider } });
  assert.equal(validDirectRegister.ok, true);
  const replayAfterValidReceipt = receiptAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'replay-after-valid-direct-register', markUnhealthy: false });
  assert.equal(replayAfterValidReceipt.ok, false);
  assert.equal(replayAfterValidReceipt.disposition, 'rejected-cleared-quarantine-replay');
  const laneAfterReplay = receiptAdapter.scheduler.snapshotLane('storage');
  assert.equal(laneAfterReplay.healthy, true);
  assert.equal(receiptAdapter.timedOutOperationQuarantine('storage').totalCount, 0);
  const write = receiptAdapter.schedulePut(`${REVISION}:registration-integrity-after-valid-register`, { id: 'registration-integrity-after-valid-register-put', label: 'registration-integrity-after-valid-register', operationTimeoutMs: 1000 });
  assert.equal(write.accepted, true);
  const drain = await receiptAdapter.drain({ maxSteps: 3 });
  const writeResult = drain.results.find((row) => row.opId === 'registration-integrity-after-valid-register-put');
  assert.equal(writeResult?.ok, true);
  const writeVerify = await store.verify(writeResult.result.ref);
  assert.equal(writeVerify.ok, true);
  const traceKinds = trace.kinds();
  for (const kind of ['storage-lane:timed-out-quarantine-clearance-receipt-rejected', 'storage-lane:timed-out-quarantine-clearance-receipt-registered', 'storage-lane:timed-out-quarantine-import-replay-rejected']) assert.ok(traceKinds.includes(kind), `missing trace ${kind}`);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-receipt-registration-integrity-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that direct timeout-quarantine clearance-receipt registration validates receipt integrity before installing replay guard state.', observations: { timeoutResults: [t1, t2], settled, before, staleLedger, reviewManifest, clearResult, validReceipt, validValidation, wrongFingerprintRegister, badOpIdsRegister, preReviewMismatchRegister, importAfterForgedRegisters, forgedLane, bareValidDirectRegister, mismatchedProvenanceRegister, validDirectRegister, replayAfterValidReceipt, laneAfterReplay, writeResult, writeVerify, forgedExecutorStats: forgedAdapter.executor.snapshot().stats, validExecutorStats: receiptAdapter.executor.snapshot().stats, traceKinds }, claimsChecked: ['direct receipt registration rejects wrong receipt fingerprints', 'direct receipt registration rejects self-consistent but mismatched opId scopes', 'direct receipt registration rejects pre-clearance/review fingerprint mismatch', 'forged rejected receipts do not install replay guard state', 'valid directly registered receipts require bound registration provenance before blocking stale quarantine ledger replay without backpressuring the lane'], nonClaims: ['Synthetic provider only; not a browser OPFS/Web Locks proof.', 'Receipt fingerprint is deterministic integrity/review binding, not cryptographic attestation or tamper-proof storage.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-receipt-registration-integrity-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed clearance receipt registration integrity proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_clearance_receipt_registration_integrity_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
