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

const TASK_ID = 'scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-CLEARANCE-LANEWIDE-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  return {
    name: 'synthetic-clearance-lanewide-scope-store', provider: 'synthetic-clearance-lanewide-scope-provider-v1',
    async put(payload, fields = {}) { const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; records.set(digest, body); trace?.emit('synthetic-clearance-lanewide-scope:put', { digest, bytes: body.byteLength, label: fields.label ?? null }); return Object.freeze({ ref: Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength }), digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null }); },
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
function makeLedger({ suffix = 'primary', lane = 'storage', epoch = `${REVISION}-lanewide-scope-epoch` } = {}) {
  const now = Date.now();
  const success = Object.freeze({ opId: `${REVISION}-${suffix}-late-success`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-${suffix}-late-success`, timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: `sha256:${suffix}-success`, bytes: 32, disposition: 'synthetic-late-success' } });
  const failed = Object.freeze({ opId: `${REVISION}-${suffix}-late-failure`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-${suffix}-late-failure`, timeoutMs: 25, timedOutAtMs: now + 2, settledAtMs: now + 3, error: { name: 'SyntheticLateFailure', message: 'synthetic late failure for lane-wide scope proof', code: 'BRT_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_SYNTHETIC_LATE_FAILURE' } });
  const base = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, exportedAtMs: now + 4, label: `${REVISION}-lanewide-scope-ledger`, reason: 'synthetic-lanewide-scope-ledger', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failed]) });
  const fingerprint = timedOutQuarantineFingerprint(base);
  return Object.freeze({ ...base, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint });
}
function selfConsistentReceipt(base) { const draft = { ...base }; draft.receiptFingerprint = timedOutOperationQuarantineClearanceReceiptFingerprint(draft); return Object.freeze(draft); }
function registrationProvenance(adapter, receipt) { return Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: receipt.lane ?? adapter.lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: adapter.label, store: adapter.storeName, provider: adapter.providerName }); }

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const producer = makeAdapter(`${REVISION}-lanewide-scope-producer`, store, trace);
  const staleLedger = makeLedger();
  const importOriginal = producer.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'import-before-lanewide-scope-clear', markUnhealthy: false });
  assert.equal(importOriginal.ok, true); assert.equal(importOriginal.markUnhealthyForced, true);
  const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0085-release-probe', reviewToken: 'lanewide-scope-review-token', reason: 'review-before-lanewide-scope-clear' });
  const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-for-lanewide-scope-receipt' });
  assert.equal(clearResult.ok, true); assert.equal(clearResult.clearedCount, 2); assert.equal(clearResult.allowLaneWide, true);
  const validReceipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0085-release-probe', label: 'release-lanewide-scope-valid-receipt' });
  const validValidation = validateTimedOutOperationQuarantineClearanceReceipt(validReceipt);
  assert.equal(validValidation.ok, true); assert.equal(validReceipt.lane, 'storage'); assert.equal(validReceipt.allowLaneWide, true);

  const ambiguousLaneWideReceipt = selfConsistentReceipt({ ...validReceipt, lane: null, allowLaneWide: true });
  const ambiguousValidation = validateTimedOutOperationQuarantineClearanceReceipt(ambiguousLaneWideReceipt);
  assert.equal(ambiguousValidation.ok, false);
  assert.ok(ambiguousValidation.errors.some((message) => String(message).includes('lane-wide receipts are lane-scoped')), JSON.stringify(ambiguousValidation.errors));

  const wrongAdapter = makeAdapter(`${REVISION}-lanewide-scope-ambiguous-register`, store, trace);
  const ambiguousRegister = wrongAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(ambiguousLaneWideReceipt, { lane: 'maintenance', reason: 'direct-register-lane-ambiguous-lanewide-receipt', provenance: registrationProvenance(wrongAdapter, ambiguousLaneWideReceipt) });
  assert.equal(ambiguousRegister.ok, false);
  assert.equal(ambiguousRegister.disposition, 'rejected-clearance-receipt-integrity');
  const importAfterAmbiguousReject = wrongAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'import-after-lane-ambiguous-receipt-rejection', markUnhealthy: false });
  assert.equal(importAfterAmbiguousReject.ok, true); assert.equal(importAfterAmbiguousReject.markUnhealthyForced, true);
  const wrongLaneState = wrongAdapter.scheduler.snapshotLane('storage');
  assert.equal(wrongLaneState.healthy, false); assert.equal(wrongAdapter.timedOutOperationQuarantine('storage').totalCount, 2);

  const validAdapter = makeAdapter(`${REVISION}-lanewide-scope-valid-register`, store, trace);
  const validRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'direct-register-valid-lanewide-receipt', provenance: registrationProvenance(validAdapter, validReceipt) });
  assert.equal(validRegister.ok, true); assert.equal(validRegister.lane, 'storage'); assert.equal(validRegister.allowLaneWide, true);
  const replayAfterValid = validAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'replay-after-valid-lanewide-receipt', markUnhealthy: false });
  assert.equal(replayAfterValid.ok, false); assert.equal(replayAfterValid.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(validAdapter.scheduler.snapshotLane('storage').healthy, true); assert.equal(validAdapter.timedOutOperationQuarantine('storage').totalCount, 0);
  validAdapter.schedulePut(`${REVISION}:lanewide-scope-recovery`, { id: `${REVISION}-lanewide-scope-recovery-put`, label: 'lanewide-scope-recovery-put' });
  const recoveryDispatch = validAdapter.scheduler.dispatchNext();
  const recovery = await validAdapter.executor.executeDispatched(recoveryDispatch);
  assert.equal(recovery.ok, true);
  const recoveryVerify = await store.verify(recovery.result.ref || recovery.result);
  assert.equal(recoveryVerify.ok, true);
  const events = trace.snapshot().map((event) => event.kind);
  for (const kind of ['storage-lane:timed-out-quarantine-clearance-receipt-rejected', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'storage-lane:timed-out-quarantine-clearance-receipt-registered', 'storage-lane:timed-out-quarantine-import-replay-rejected']) assert.ok(events.includes(kind), `missing trace ${kind}`);
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-lanewide-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Browser-light proof that timeout-quarantine clearance receipts treat lane-wide as lane-scoped and reject lane-ambiguous receipts before they can suppress stale quarantine replay.', observations: { staleLedger, importOriginal, reviewManifest, clearResult, validReceipt, validValidation, ambiguousLaneWideReceipt, ambiguousValidation, ambiguousRegister, importAfterAmbiguousReject, wrongLaneState, validRegister, replayAfterValid, recoveryVerify, stats: { producer: producer.executor.snapshot().stats, wrong: wrongAdapter.executor.snapshot().stats, valid: validAdapter.executor.snapshot().stats }, traceKinds: events }, claimsChecked: ['lane-wide clearance receipt creation remains valid when it is lane-scoped', 'self-consistent lane-ambiguous lane-wide receipts fail validation and direct registration', 'rejected lane-ambiguous receipt registration does not suppress stale quarantine import/backpressure', 'valid lane-scoped receipt registration still rejects stale replay and permits later write'], nonClaims: ['Browser-light synthetic storage only; no OPFS/Web Locks/cross-browser claim.', 'Receipt fingerprints are deterministic integrity checks, not cryptographic attestation or tamper-proof storage.', 'No provider cancellation, rollback, durability, eviction, SLO, or production-readiness claim.'] });
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-lanewide-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed lane-wide scope proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_clearance_lanewide_scope_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
