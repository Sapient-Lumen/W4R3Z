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
  digestBytesHex
} from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-clearance-lanewide-query-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-CLEARANCE-LANEWIDE-QUERY-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  return {
    name: 'synthetic-clearance-lanewide-query-scope-store', provider: 'synthetic-clearance-lanewide-query-scope-provider-v1',
    async put(payload, fields = {}) { const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; records.set(digest, body); trace?.emit('synthetic-clearance-lanewide-query-scope:put', { digest, bytes: body.byteLength, label: fields.label ?? null }); return Object.freeze({ ref: Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength }), digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null }); },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing block ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); return Object.freeze({ ok: Boolean(row), present: Boolean(row), digest, bytes: row?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: [...records.values()].reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size }); }
  };
}
function makeAdapter(label, store, trace, lane = 'storage') { return createBlockStoreLaneAdapter({ label, store, scheduler: scheduler(`${label}:scheduler`, trace), trace, lane, defaultOperationTimeoutMs: 1000 }); }
function makeLedger({ suffix = 'primary', lane = 'storage', opSuffix = suffix, epoch = `${REVISION}-lanewide-query-scope-epoch` } = {}) {
  const now = Date.now();
  const success = Object.freeze({ opId: `${REVISION}-${opSuffix}-late-success`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-${opSuffix}-late-success`, timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: `sha256:${suffix}-success`, bytes: 32, disposition: 'synthetic-late-success' } });
  const failed = Object.freeze({ opId: `${REVISION}-${opSuffix}-late-failure`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-${opSuffix}-late-failure`, timeoutMs: 25, timedOutAtMs: now + 2, settledAtMs: now + 3, error: { name: 'SyntheticLateFailure', message: 'synthetic late failure for lane-wide query scope proof', code: 'BRT_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_SYNTHETIC_LATE_FAILURE' } });
  const base = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, exportedAtMs: now + 4, label: `${REVISION}-lanewide-query-scope-ledger:${lane}`, reason: 'synthetic-lanewide-query-scope-ledger', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failed]) });
  const fingerprint = timedOutQuarantineFingerprint(base);
  return Object.freeze({ ...base, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint });
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const producer = makeAdapter(`${REVISION}-lanewide-query-scope-producer`, store, trace, 'storage');
  const storageLedger = makeLedger({ lane: 'storage', suffix: 'storage', opSuffix: 'same-visible-op' });
  const importOriginal = producer.importTimedOutOperationQuarantine(storageLedger, { lane: 'storage', reason: 'import-before-lanewide-query-scope-clear', markUnhealthy: false });
  assert.equal(importOriginal.ok, true); assert.equal(importOriginal.markUnhealthyForced, true);
  const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0087-release-probe', reviewToken: 'lanewide-query-scope-review-token', reason: 'review-before-lanewide-query-scope-clear' });
  const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-for-lanewide-query-scope-receipt' });
  assert.equal(clearResult.ok, true); assert.equal(clearResult.allowLaneWide, true); assert.equal(clearResult.clearedCount, 2);
  const receipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0087-release-probe', label: 'release-lanewide-query-scope-receipt' });
  assert.equal(receipt.lane, 'storage'); assert.equal(receipt.allowLaneWide, true);

  const fresh = makeAdapter(`${REVISION}-lanewide-query-scope-fresh`, store, trace, 'storage');
  const register = fresh.executor.registerTimedOutOperationQuarantineClearanceReceipt(receipt, { lane: 'storage', reason: 'register-lanewide-query-scope-receipt', provenance: { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: fresh.label, store: fresh.storeName, provider: fresh.providerName } });
  assert.equal(register.ok, true);

  const allReceipts = fresh.executor.clearedTimedOutOperationQuarantineClearanceReceipts(null);
  const storageReceipts = fresh.clearedTimedOutOperationQuarantineClearanceReceipts('storage');
  const maintenanceReceipts = fresh.clearedTimedOutOperationQuarantineClearanceReceipts('maintenance');
  assert.equal(allReceipts.length, 1);
  assert.equal(storageReceipts.length, 1);
  assert.equal(maintenanceReceipts.length, 0, 'lane-wide storage receipt must not be visible as a maintenance-lane receipt');

  const storageReplay = fresh.importTimedOutOperationQuarantine(storageLedger, { lane: 'storage', reason: 'storage-replay-after-storage-receipt', markUnhealthy: false });
  assert.equal(storageReplay.ok, false); assert.equal(storageReplay.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(fresh.scheduler.snapshotLane('storage').healthy, true);

  const maintenanceLedger = makeLedger({ lane: 'maintenance', suffix: 'maintenance', opSuffix: 'same-visible-op', epoch: `${REVISION}-lanewide-query-scope-maintenance-epoch` });
  const maintenanceImport = fresh.importTimedOutOperationQuarantine(maintenanceLedger, { lane: 'maintenance', reason: 'maintenance-import-must-not-be-suppressed-by-storage-lanewide-receipt', markUnhealthy: false });
  assert.equal(maintenanceImport.ok, true);
  assert.equal(maintenanceImport.markUnhealthyForced, true);
  assert.equal(fresh.scheduler.snapshotLane('maintenance').healthy, false);
  assert.equal(fresh.timedOutOperationQuarantine('maintenance').totalCount, 2);

  const storageReceiptsAfterMaintenance = fresh.clearedTimedOutOperationQuarantineClearanceReceipts('storage');
  const maintenanceReceiptsAfterMaintenance = fresh.clearedTimedOutOperationQuarantineClearanceReceipts('maintenance');
  assert.equal(storageReceiptsAfterMaintenance.length, 1);
  assert.equal(maintenanceReceiptsAfterMaintenance.length, 0);

  fresh.schedulePut(`${REVISION}:lanewide-query-scope-recovery`, { id: `${REVISION}-lanewide-query-scope-recovery-put`, label: 'lanewide-query-scope-recovery-put', lane: 'storage' });
  const recoveryDispatch = fresh.scheduler.dispatchNext();
  const recovery = await fresh.executor.executeDispatched(recoveryDispatch);
  assert.equal(recovery.ok, true);
  const verify = await store.verify(recovery.result.ref);
  assert.equal(verify.ok, true);

  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-quarantine-clearance-lanewide-query-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-light proof that lane-wide timeout-quarantine clearance receipts remain query/replay scoped to their concrete lane.',
    observations: { importOriginal, clearResult, receipt: { lane: receipt.lane, allowLaneWide: receipt.allowLaneWide, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint }, register, allReceiptCount: allReceipts.length, storageReceiptCount: storageReceipts.length, maintenanceReceiptCount: maintenanceReceipts.length, storageReceiptFromStorageQuery: storageReceipts[0] || null, storageReceiptFromMaintenanceQuery: maintenanceReceipts[0] || null, maintenanceReceiptFromMaintenanceQuery: maintenanceReceiptsAfterMaintenance[0] || null, storageReplay, maintenanceImport, importAfterWrongLaneRegistration: maintenanceImport, maintenanceLane: fresh.scheduler.snapshotLane('maintenance'), storageReceiptsAfterMaintenance: storageReceiptsAfterMaintenance.length, maintenanceReceiptsAfterMaintenance: maintenanceReceiptsAfterMaintenance.length, recovery: { ok: recovery.ok, result: recovery.result }, verify, traceKinds: trace.kinds() },
    claimsChecked: ['lane-specific receipt queries do not return lane-wide receipts from other lanes', 'storage stale replay remains rejected by the storage receipt', 'maintenance quarantine with the same visible op ids imports/backpressures rather than being suppressed by the storage receipt', 'later storage-lane write still verifies'],
    nonClaims: ['Release-light synthetic block-store proof only; no Chromium, cross-browser, OPFS durability, quota/eviction, cancellation, rollback, exactly-once, cryptographic attestation, or production-readiness claim.']
  };
  return report;
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-lanewide-query-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed lane-wide query-scope proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_clearance_lanewide_query_scope_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
