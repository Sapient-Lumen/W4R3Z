#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, digestBytesHex } from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-clearance-restore-registration-gate-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-CLEARANCE-RESTORE-REGISTRATION-GATE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function bytes(value) {
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  return new TextEncoder().encode(String(value));
}

function makeStore({ trace = null } = {}) {
  const records = new Map();
  return {
    name: 'synthetic-clearance-restore-registration-gate-store',
    provider: 'synthetic-clearance-restore-registration-gate-provider-v0',
    async put(payload, fields = {}) {
      const body = bytes(payload);
      const hash = await digestBytesHex(body);
      const digest = `sha256:${hash}`;
      records.set(digest, body);
      trace?.emit('synthetic-clearance-restore-registration-gate:put', { digest, bytes: body.byteLength, label: fields.label ?? null, purpose: fields.purpose ?? null });
      const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength });
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null });
    },
    async get(ref) {
      const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest ?? ref?.hash ?? ref?.id;
      const row = records.get(digest);
      if (!row) throw new Error(`missing block ${digest}`);
      return new Uint8Array(row);
    },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest ?? ref?.hash ?? ref?.id; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest ?? ref?.hash ?? ref?.id; const row = records.get(digest); return Object.freeze({ ok: Boolean(row), present: Boolean(row), digest, bytes: row?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest ?? ref?.hash ?? ref?.id; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: [...records.values()].reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size }); }
  };
}

function scheduler(label, trace) {
  return createCrossLaneScheduler({ label, trace, lanes: [
    { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 },
    { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
  ] });
}
function adapter(label, store, trace, lane = 'storage') {
  return createBlockStoreLaneAdapter({ label, store, scheduler: scheduler(`${label}:scheduler`, trace), trace, lane, defaultOperationTimeoutMs: 1000 });
}

function makeLedger({ lane = 'storage', suffix = 'restore-registration-gate', epoch = `${REVISION}-restore-registration-gate-epoch` } = {}) {
  const now = Date.now();
  const success = Object.freeze({ opId: `${REVISION}-${suffix}-late-success`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-${suffix}-late-success`, timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: `sha256:${suffix}-success`, bytes: 64, disposition: 'synthetic-late-success' } });
  const failed = Object.freeze({ opId: `${REVISION}-${suffix}-late-failure`, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: `operation:${lane}:put:${epoch}:${REVISION}-${suffix}-late-failure`, timeoutMs: 25, timedOutAtMs: now + 2, settledAtMs: now + 3, error: { name: 'SyntheticLateFailure', message: 'synthetic late failure for restore registration gate proof', code: 'BRT_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_SYNTHETIC_LATE_FAILURE' } });
  const base = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, exportedAtMs: now + 4, label: `${REVISION}-${suffix}-ledger`, reason: 'synthetic-restore-registration-gate-ledger', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failed]) });
  const fingerprint = timedOutQuarantineFingerprint(base);
  return Object.freeze({ ...base, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint });
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const staleLedger = makeLedger();
  const producer = adapter(`${REVISION}-restore-registration-gate-producer`, store, trace, 'storage');
  const imported = producer.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', markUnhealthy: false, reason: 'import-before-clear-for-restore-registration-gate' });
  assert.equal(imported.ok, true);
  assert.equal(imported.markUnhealthyForced, true);
  const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0086-release-probe', reviewToken: 'restore-registration-gate-review-token', reason: 'review-for-restore-registration-gate' });
  const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-for-restore-registration-gate-receipt' });
  assert.equal(clearResult.ok, true);
  assert.equal(clearResult.clearedCount, 2);
  const receipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0086-release-probe', label: 'restore-registration-gate-receipt' });
  const persisted = await producer.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label: 'restore-registration-gate-persisted-receipt' });
  assert.equal(persisted.ok, true);
  const persistedVerify = await store.verify(persisted.ref);
  assert.equal(persistedVerify.ok, true);

  const wrongLaneAdapter = adapter(`${REVISION}-restore-registration-gate-wrong-lane`, store, trace, 'maintenance');
  const wrongLaneRestore = await wrongLaneAdapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane: 'maintenance', reason: 'restore-storage-receipt-into-maintenance-lane' });
  assert.equal(wrongLaneRestore.ok, false);
  assert.equal(wrongLaneRestore.disposition, 'rejected-clearance-receipt-lane-binding');
  assert.equal(wrongLaneRestore.registration?.ok, false);
  assert.equal(wrongLaneAdapter.clearedTimedOutOperationQuarantineClearanceReceipts('storage').length, 0);
  const importAfterRejectedRestore = wrongLaneAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', markUnhealthy: false, reason: 'import-after-rejected-restore-registration' });
  assert.equal(importAfterRejectedRestore.ok, true);
  assert.equal(importAfterRejectedRestore.markUnhealthyForced, true);
  assert.equal(wrongLaneAdapter.scheduler.snapshotLane('storage').healthy, false);
  assert.equal(wrongLaneAdapter.timedOutOperationQuarantine('storage').totalCount, 2);

  const validRestoreAdapter = adapter(`${REVISION}-restore-registration-gate-valid`, store, trace, 'storage');
  const validRestore = await validRestoreAdapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane: 'storage', reason: 'restore-storage-receipt-into-storage-lane' });
  assert.equal(validRestore.ok, true);
  assert.equal(validRestore.registration?.ok, true);
  assert.equal(validRestore.registration?.registrationSource, 'block-store-restore-clearance-receipt');
  const replayAfterValidRestore = validRestoreAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', markUnhealthy: false, reason: 'replay-after-valid-restore-registration' });
  assert.equal(replayAfterValidRestore.ok, false);
  assert.equal(replayAfterValidRestore.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(validRestoreAdapter.scheduler.snapshotLane('storage').healthy, true);
  assert.equal(validRestoreAdapter.timedOutOperationQuarantine('storage').totalCount, 0);
  validRestoreAdapter.schedulePut(`${REVISION}:restore-registration-gate-recovery`, { id: `${REVISION}-restore-registration-gate-recovery-put`, label: 'restore-registration-gate-recovery-put' });
  const dispatched = validRestoreAdapter.scheduler.dispatchNext();
  const recovery = await validRestoreAdapter.executor.executeDispatched(dispatched);
  assert.equal(recovery.ok, true);
  const recoveryVerify = await store.verify(recovery.result.ref || recovery.result);
  assert.equal(recoveryVerify.ok, true);

  const events = trace.snapshot().map((event) => event.kind);
  for (const kind of ['block-store-lane:quarantine-clearance-receipt-restore-rejected', 'block-store-lane:quarantine-clearance-receipt-restored', 'storage-lane:timed-out-quarantine-import-replay-rejected']) assert.ok(events.includes(kind), `missing trace ${kind}`);
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-restore-registration-gate-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Browser-light proof that restoring a timeout-quarantine clearance receipt fails closed when registration rejects, and only a valid lane/provenance-bound restore suppresses stale replay.', observations: { staleLedger, imported, reviewManifest, clearResult, receipt, persisted, persistedVerify, wrongLaneRestore, importAfterRejectedRestore, wrongLane: wrongLaneAdapter.scheduler.snapshotLane('storage'), validRestore, replayAfterValidRestore, recoveryVerify, stats: { producer: producer.snapshot().stats, wrongLane: wrongLaneAdapter.snapshot().stats, validRestore: validRestoreAdapter.snapshot().stats }, traceKinds: events }, claimsChecked: ['receipt restore no longer reports ok when registration rejects', 'wrong-lane restored receipt does not install stale replay guard state', 'stale ledger import still forces backpressure after rejected restore', 'valid block-store restore has bound provenance and rejects stale replay', 'later storage write verifies after valid restore'], nonClaims: ['Browser-light synthetic storage only; no OPFS/Web Locks/cross-browser claim.', 'Receipt fingerprints/provenance are deterministic integrity bindings, not cryptographic attestation or tamper-proof storage.', 'No provider cancellation, rollback, durability, eviction, SLO, or production-readiness claim.'] });
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-restore-registration-gate-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed restore registration gate proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_clearance_restore_registration_gate_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
