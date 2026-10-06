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
  validateTimedOutOperationQuarantineClearanceReceipt
} from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-clearance-replay-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-CLEARANCE-REPLAY-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticClearanceReplayGuardError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  const releaseSuccess = deferred();
  const releaseFailure = deferred();
  const state = { puts: 0, lateSuccesses: 0, lateFailures: 0, waitForSettledCalls: 0 };
  return {
    name: 'synthetic-clearance-replay-guard-store', provider: 'synthetic-clearance-replay-guard-provider-v0', releaseSuccess, releaseFailure, state,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`;
      records.set(digest, body); state.puts += 1;
      trace?.emit('synthetic-clearance-replay-guard:put', { digest, bytes: body.byteLength, label: fields.label ?? null, purpose: fields.purpose ?? null });
      const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength });
      if (fields.label === 'clearance-replay-late-success') { await releaseSuccess.promise; state.lateSuccesses += 1; }
      if (fields.label === 'clearance-replay-late-failure') { await releaseFailure.promise; state.lateFailures += 1; throw codedError('BRT_SYNTHETIC_CLEARANCE_REPLAY_LATE_FAILURE', 'synthetic late failure after committed block', { digest }); }
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing block ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); return Object.freeze({ ok: Boolean(row), present: Boolean(row), digest, bytes: row?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: [...records.values()].reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { state.waitForSettledCalls += 1; return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-clearance-replay`, store, scheduler: scheduler(`${REVISION}-clearance-replay-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 80 });
  adapter.schedulePut(`${REVISION}:clearance-replay-success`, { id: 'clearance-replay-success-timeout', label: 'clearance-replay-late-success' });
  adapter.schedulePut(`${REVISION}:clearance-replay-failure`, { id: 'clearance-replay-failure-timeout', label: 'clearance-replay-late-failure' });
  const d1 = adapter.scheduler.dispatchNext(); const d2 = adapter.scheduler.dispatchNext();
  const [t1, t2] = await Promise.all([adapter.executor.executeDispatched(d1), adapter.executor.executeDispatched(d2)]);
  assert.equal(t1.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(t2.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  store.releaseSuccess.resolve('release-success'); store.releaseFailure.resolve('release-failure');
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  assert.equal(settled.ok, true);
  const before = adapter.timedOutOperationQuarantine('storage');
  assert.equal(before.successfulTimedOutOperationCount, 1); assert.equal(before.failedTimedOutOperationCount, 1);
  const staleLedger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'export-before-clearance-receipt' });
  const reviewManifest = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0079-release-probe', reviewToken: 'clearance-replay-review-token', reason: 'review-before-clearance-replay-guard' });
  const clearResult = adapter.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-for-clearance-replay-guard' });
  assert.equal(clearResult.ok, true); assert.equal(clearResult.clearedCount, 2);
  const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0079-release-probe', label: 'release-clearance-replay-receipt' });
  const validation = validateTimedOutOperationQuarantineClearanceReceipt(receipt);
  assert.equal(validation.ok, true);
  const sameAdapterReplay = adapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'same-adapter-stale-replay', markUnhealthy: false });
  assert.equal(sameAdapterReplay.ok, false);
  assert.equal(sameAdapterReplay.disposition, 'rejected-cleared-quarantine-replay');
  const persisted = await adapter.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label: 'release-clearance-replay-receipt-persisted' });
  assert.equal(persisted.ok, true);

  const fresh = createBlockStoreLaneAdapter({ label: `${REVISION}-clearance-replay-fresh`, store, scheduler: scheduler(`${REVISION}-clearance-replay-fresh-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const restored = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane: 'storage' });
  assert.equal(restored.ok, true); assert.equal(restored.receiptFingerprint, receipt.receiptFingerprint); assert.equal(restored.registration.ok, true);
  const replay = fresh.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'fresh-adapter-stale-ledger-replay', markUnhealthy: false });
  assert.equal(replay.ok, false); assert.equal(replay.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(fresh.timedOutOperationQuarantine('storage').totalCount, 0);
  const laneAfterReplay = fresh.scheduler.snapshotLane('storage');
  assert.equal(laneAfterReplay.healthy, true);
  const write = fresh.schedulePut(`${REVISION}:clearance-replay-after-guard`, { id: 'clearance-replay-after-guard-put', label: 'clearance-replay-after-guard', operationTimeoutMs: 1000 });
  assert.equal(write.accepted, true);
  const drain = await fresh.drain({ maxSteps: 3 });
  const writeResult = drain.results.find((row) => row.opId === 'clearance-replay-after-guard-put');
  assert.equal(writeResult?.ok, true);
  const writeVerify = await store.verify(writeResult.result.ref);
  assert.equal(writeVerify.ok, true);
  const traceKinds = trace.kinds();
  for (const kind of ['block-store-lane:quarantine-clearance-receipt-created', 'block-store-lane:quarantine-clearance-receipt-persisted', 'block-store-lane:quarantine-clearance-receipt-restored', 'storage-lane:timed-out-quarantine-import-replay-rejected']) assert.ok(traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-replay-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that reviewed/fingerprint-bound timeout-quarantine clearance receipts can be persisted/restored and then block stale cleared quarantine-ledger replay into a fresh adapter without poisoning lane health.', observations: { timeoutResults: [t1, t2], settled, before, staleLedger, reviewManifest, clearResult, receipt, validation, sameAdapterReplay, persisted, restored, replay, laneAfterReplay, writeResult, writeVerify, stats: fresh.snapshot().stats, executorStats: fresh.executor.snapshot().stats, traceKinds }, claimsChecked: ['clearance receipt registers the cleared quarantine fingerprint', 'same-adapter stale ledger replay is rejected', 'restored clearance receipt registers into a fresh adapter', 'fresh-adapter stale ledger replay is rejected without mutation or backpressure', 'later writes still verify after replay rejection'], nonClaims: ['Synthetic provider only; not a browser OPFS/Web Locks proof.', 'Receipt fingerprint is deterministic binding, not cryptographic attestation or tamper-proof storage.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-replay-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed clearance replay guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_clearance_replay_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
