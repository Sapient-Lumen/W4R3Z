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
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-clearance-row-replay-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-CLEARANCE-ROW-REPLAY-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticClearanceRowReplayGuardError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  const releaseSuccess = deferred();
  const releaseFailure = deferred();
  const state = { puts: 0, lateSuccesses: 0, lateFailures: 0 };
  return {
    name: 'synthetic-clearance-row-replay-guard-store', provider: 'synthetic-clearance-row-replay-guard-provider-v1', releaseSuccess, releaseFailure, state,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`;
      records.set(digest, body); state.puts += 1;
      trace?.emit('synthetic-clearance-row-replay-guard:put', { digest, bytes: body.byteLength, label: fields.label ?? null, purpose: fields.purpose ?? null });
      const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength });
      if (fields.label === 'clearance-row-replay-late-success') { await releaseSuccess.promise; state.lateSuccesses += 1; }
      if (fields.label === 'clearance-row-replay-late-failure') { await releaseFailure.promise; state.lateFailures += 1; throw codedError('BRT_SYNTHETIC_CLEARANCE_ROW_REPLAY_LATE_FAILURE', 'synthetic late failure after committed block', { digest }); }
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
function withFingerprint(ledger) {
  const quarantineFingerprint = timedOutQuarantineFingerprint(ledger);
  return Object.freeze({ ...ledger, quarantineFingerprint, reviewFingerprint: quarantineFingerprint });
}
function modifiedLedgerWithClearedRowsAndFreshRow(staleLedger) {
  const freshRow = Object.freeze({
    opId: 'clearance-row-replay-fresh-extra-success-timeout',
    kind: 'put', lane: 'storage', timeoutMs: 80, timedOutAtMs: Date.now() + 17, imported: false, settledAtMs: Date.now() + 19,
    result: Object.freeze({ digest: 'sha256:clearance-row-replay-fresh-extra', bytes: 19, disposition: 'synthetic-extra-success' })
  });
  const successfulTimedOutOperations = Object.freeze([...(staleLedger.successfulTimedOutOperations || []), freshRow]);
  const failedTimedOutOperations = Object.freeze([...(staleLedger.failedTimedOutOperations || [])]);
  const unsettledTimedOutOperations = Object.freeze([...(staleLedger.unsettledTimedOutOperations || [])]);
  return withFingerprint({
    ...staleLedger,
    reason: 'modified-stale-ledger-with-cleared-rows-plus-fresh-row',
    counts: Object.freeze({ total: successfulTimedOutOperations.length + failedTimedOutOperations.length + unsettledTimedOutOperations.length, successful: successfulTimedOutOperations.length, failed: failedTimedOutOperations.length, unsettled: unsettledTimedOutOperations.length }),
    unsettledTimedOutOperations,
    successfulTimedOutOperations,
    failedTimedOutOperations
  });
}
function modifiedLedgerWithClearedRowStatusRewrite(staleLedger) {
  const source = (staleLedger.failedTimedOutOperations || [])[0] || (staleLedger.successfulTimedOutOperations || [])[0];
  if (!source) throw new Error('status rewrite proof requires at least one cleared stale row');
  const rewritten = Object.freeze({
    opId: source.opId,
    kind: source.kind || 'put',
    lane: source.lane || 'storage',
    operationEpoch: source.operationEpoch ?? null,
    operationReplayKey: source.operationReplayKey ?? null,
    timeoutMs: Number(source.timeoutMs || 80),
    timedOutAtMs: Number(source.timedOutAtMs || Date.now()),
    imported: false,
    settledAtMs: Date.now() + 23,
    result: Object.freeze({ digest: 'sha256:clearance-row-replay-status-rewrite', bytes: 31, disposition: 'synthetic-status-rewrite-success' })
  });
  return withFingerprint({
    ...staleLedger,
    reason: 'modified-stale-ledger-with-cleared-row-status-rewrite',
    counts: Object.freeze({ total: 1, successful: 1, failed: 0, unsettled: 0 }),
    unsettledTimedOutOperations: Object.freeze([]),
    successfulTimedOutOperations: Object.freeze([rewritten]),
    failedTimedOutOperations: Object.freeze([])
  });
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-clearance-row-replay`, store, scheduler: scheduler(`${REVISION}-clearance-row-replay-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 80 });
  adapter.schedulePut(`${REVISION}:clearance-row-replay-success`, { id: 'clearance-row-replay-success-timeout', label: 'clearance-row-replay-late-success' });
  adapter.schedulePut(`${REVISION}:clearance-row-replay-failure`, { id: 'clearance-row-replay-failure-timeout', label: 'clearance-row-replay-late-failure' });
  const d1 = adapter.scheduler.dispatchNext(); const d2 = adapter.scheduler.dispatchNext();
  const [t1, t2] = await Promise.all([adapter.executor.executeDispatched(d1), adapter.executor.executeDispatched(d2)]);
  assert.equal(t1.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(t2.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  store.releaseSuccess.resolve('release-success'); store.releaseFailure.resolve('release-failure');
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  assert.equal(settled.ok, true);
  const before = adapter.timedOutOperationQuarantine('storage');
  assert.equal(before.successfulTimedOutOperationCount, 1); assert.equal(before.failedTimedOutOperationCount, 1);
  const staleLedger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'export-before-clearance-row-replay-guard' });
  const modifiedLedger = modifiedLedgerWithClearedRowsAndFreshRow(staleLedger);
  const statusRewriteLedger = modifiedLedgerWithClearedRowStatusRewrite(staleLedger);
  const reviewManifest = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0081-release-probe', reviewToken: 'clearance-row-replay-review-token', reason: 'review-before-clearance-row-replay-guard' });
  const clearResult = adapter.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-for-clearance-row-replay-guard' });
  assert.equal(clearResult.ok, true); assert.equal(clearResult.clearedCount, 2);
  const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0081-release-probe', label: 'release-clearance-row-replay-receipt' });
  const validation = validateTimedOutOperationQuarantineClearanceReceipt(receipt);
  assert.equal(validation.ok, true);
  const forged = { ...receipt, counts: { ...receipt.counts, total: receipt.counts.total + 1 } };
  const forgedRegistration = adapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(forged, { lane: 'storage', reason: 'direct-forged-receipt-registration-attempt' });
  assert.equal(forgedRegistration.ok, false);
  assert.equal(forgedRegistration.disposition, 'rejected-clearance-receipt-integrity');
  const persisted = await adapter.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label: 'release-clearance-row-replay-receipt-persisted' });
  assert.equal(persisted.ok, true);
  const fresh = createBlockStoreLaneAdapter({ label: `${REVISION}-clearance-row-replay-fresh`, store, scheduler: scheduler(`${REVISION}-clearance-row-replay-fresh-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const restored = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane: 'storage' });
  assert.equal(restored.ok, true); assert.equal(restored.registration.ok, true);
  assert.ok(restored.registration.clearedRowKeys.length >= 2);
  assert.ok(restored.registration.clearedOperationKeys.length >= 2);
  const exactReplay = fresh.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'fresh-adapter-exact-stale-ledger-replay', markUnhealthy: false });
  assert.equal(exactReplay.ok, false); assert.equal(exactReplay.disposition, 'rejected-cleared-quarantine-replay');
  const rowReplay = fresh.importTimedOutOperationQuarantine(modifiedLedger, { lane: 'storage', reason: 'fresh-adapter-modified-row-replay-ledger', markUnhealthy: false });
  assert.equal(rowReplay.ok, false); assert.equal(rowReplay.disposition, 'rejected-cleared-quarantine-row-replay'); assert.ok(rowReplay.matchedRows.length >= 1);
  const statusRewriteReplay = fresh.importTimedOutOperationQuarantine(statusRewriteLedger, { lane: 'storage', reason: 'fresh-adapter-status-rewritten-row-replay-ledger', markUnhealthy: false });
  assert.equal(statusRewriteReplay.ok, false); assert.equal(statusRewriteReplay.disposition, 'rejected-cleared-quarantine-row-replay'); assert.ok(statusRewriteReplay.matchedRows.some((row) => row.operationKey && row.statusKey), 'status rewrite replay should match by operation key even when status key differs');
  const quarantineAfterReplay = fresh.timedOutOperationQuarantine('storage');
  assert.equal(quarantineAfterReplay.totalCount, 0);
  const laneAfterReplay = fresh.scheduler.snapshotLane('storage');
  assert.equal(laneAfterReplay.healthy, true);
  const write = fresh.schedulePut(`${REVISION}:clearance-row-replay-after-guard`, { id: 'clearance-row-replay-after-guard-put', label: 'clearance-row-replay-after-guard', operationTimeoutMs: 1000 });
  assert.equal(write.accepted, true);
  const drain = await fresh.drain({ maxSteps: 3 });
  const writeResult = drain.results.find((row) => row.opId === 'clearance-row-replay-after-guard-put');
  assert.equal(writeResult?.ok, true);
  const writeVerify = await store.verify(writeResult.result.ref);
  assert.equal(writeVerify.ok, true);
  const traceKinds = trace.kinds();
  for (const kind of ['storage-lane:timed-out-quarantine-clearance-receipt-rejected', 'storage-lane:timed-out-quarantine-import-row-replay-rejected', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'block-store-lane:quarantine-clearance-receipt-restored']) assert.ok(traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-row-replay-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that clearance receipts reject direct forged registration, exact stale-ledger replay, modified row replay, and status-rewritten row replay without poisoning a fresh lane.', observations: { timeoutResults: [t1, t2], settled, before, staleLedger, modifiedLedger, statusRewriteLedger, reviewManifest, clearResult, receipt, validation, forgedRegistration, persisted, restored, exactReplay, rowReplay, statusRewriteReplay, quarantineAfterReplay, laneAfterReplay, writeResult, writeVerify, stats: fresh.snapshot().stats, executorStats: fresh.snapshot().executor.stats, traceKinds }, claimsChecked: ['direct receipt registration validates receipt integrity before registering a replay guard', 'exact stale ledger replay remains rejected', 'modified ledger replay containing previously cleared rows is rejected atomically', 'status-rewritten cleared operation rows are rejected by operation identity rather than status-specific row key alone', 'row replay rejection leaves the fresh lane healthy and quarantine-empty', 'later storage-lane write verifies'], nonClaims: ['Browser-light synthetic provider only; no OPFS, Web Locks, cross-browser, durability, quota, or eviction claim.', 'No cryptographic attestation or tamper-proof storage claim.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, SLO, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-row-replay-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed row replay guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_clearance_row_replay_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
