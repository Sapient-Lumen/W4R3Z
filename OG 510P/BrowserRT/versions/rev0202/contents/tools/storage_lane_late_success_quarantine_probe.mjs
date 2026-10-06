#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-late-success-quarantine-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-LATE-SUCCESS-QUARANTINE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
async function waitUntil(fn, { timeoutMs = 500, intervalMs = 5 } = {}) { const start = performance.now(); let last = null; while (performance.now() - start <= timeoutMs) { last = await fn(); if (last) return true; await new Promise((r) => setTimeout(r, intervalMs)); } return Boolean(last); }
function bytes(value) { if (typeof value === 'string') return new TextEncoder().encode(value); if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function makeLateSuccessfulStore({ trace = null } = {}) {
  const release = deferred();
  const records = new Map();
  const state = { puts: 0, committedBeforeSettle: 0, waitForSettledCalls: 0, released: false, lateSuccesses: 0 };
  return {
    name: 'synthetic-late-success-block-store', provider: 'synthetic-late-success-provider-v0', release, state,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`;
      state.puts += 1; records.set(digest, body); state.committedBeforeSettle += 1;
      trace?.emit('synthetic-late-success-store:committed-before-settle', { digest, bytes: body.byteLength, label: fields.label ?? null });
      if (fields?.label === 'late-success-op') { const reason = await release.promise; state.released = true; state.lateSuccesses += 1; trace?.emit('synthetic-late-success-store:late-success', { digest, reason }); }
      const ref = Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null });
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, path: null, label: fields.label ?? null });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); return Object.freeze({ digest, present: Boolean(row), ok: Boolean(row), bytes: row?.byteLength ?? 0, path: null }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: Array.from(records.values()).reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { state.waitForSettledCalls += 1; return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-store-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}
export async function runProbe() {
  const started = performance.now(); const trace = new TraceLog();
  const scheduler = createCrossLaneScheduler({ label: `${REVISION}-late-success-quarantine-scheduler`, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
  const store = makeLateSuccessfulStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-late-success-quarantine-adapter`, store, scheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 120 });
  const payload = `BrowserRT ${REVISION} late-success quarantine payload`; const timeoutDigest = `sha256:${await digestBytesHex(bytes(payload))}`;
  const accepted = adapter.schedulePut(payload, { id: 'late-success-put-times-out', label: 'late-success-op', priority: 'user-visible' });
  const drain = await adapter.drain({ maxSteps: 2 }); const timeoutResult = drain.results.find((row) => row.opId === 'late-success-put-times-out');
  const snapshotAfterTimeout = adapter.snapshot(); const storageLaneAfterTimeout = snapshotAfterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const committedButUnsettled = await waitUntil(() => store.has(timeoutDigest), { timeoutMs: 500, intervalMs: 5 });
  const rejectedWhileUnhealthy = adapter.schedulePut('must-not-queue-before-late-success-review', { id: 'reject-while-late-success-unhealthy' });
  const blockedWhileUnsettled = await adapter.recoverWhenStoreSettled({ timeoutMs: 45, intervalMs: 5, reason: 'late-success-still-unsettled' });
  store.release.resolve('release-late-success-after-timeout');
  const settledWait = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const verifyAfterLateSuccess = await store.verify(timeoutDigest); const adapterResultAfterLateSuccess = adapter.result('late-success-put-times-out') ?? null; const snapshotAfterLateSuccess = adapter.snapshot();
  const blockedByLateSuccess = await adapter.recoverWhenStoreSettled({ timeoutMs: 500, intervalMs: 5, reason: 'late-success-reviewed-recovery-not-yet-cleared' });
  const stillRejectedAfterLateSuccess = adapter.schedulePut('must-not-queue-before-success-clear', { id: 'reject-before-late-success-clear' });
  const unreviewedClearRejected = adapter.clearSuccessfulTimedOutOperations({ lane: 'storage', reason: 'operator-unreviewed-late-success-clear' });
  const unscopedClearRejected = adapter.clearSuccessfulTimedOutOperations({ lane: 'storage', reviewed: true, reviewToken: 'rev0073-late-success-review-unscoped', reason: 'operator-reviewed-late-success-without-scope' });
  const clearReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opId: 'late-success-put-times-out', reviewer: 'legacy-compatible-release-probe', reviewToken: 'rev0078-late-success-review-scoped', reason: 'operator-reviewed-late-success-commit' });
  const cleared = adapter.clearSuccessfulTimedOutOperations({ reviewManifest: clearReview, requireReviewFingerprint: true, reason: 'operator-reviewed-late-success-commit' });
  const recoveredAfterClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 500, intervalMs: 5, reason: 'late-success-reviewed-and-cleared' });
  const recoveredSchedule = adapter.schedulePut('BrowserRT late success quarantine recovered write', { id: 'late-success-recovered-put', priority: 'user-visible', label: 'recovered-after-late-success-clear', operationTimeoutMs: 1000 });
  const recoveryDrain = await adapter.drain({ maxSteps: 3 }); const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'late-success-recovered-put'); const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const finalSnapshot = adapter.snapshot(); const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot); const traceKinds = trace.kinds();
  assert.equal(accepted.accepted, true); assert.equal(timeoutResult?.ok, false); assert.equal(timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(snapshotAfterTimeout.executor.unsettledTimedOutOperationCount, 1); assert.equal(storageLaneAfterTimeout?.healthy, false); assert.equal(storageLaneAfterTimeout?.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(committedButUnsettled, true, 'operation timeout is not a provider cancellation/no-mutation guarantee');
  assert.equal(rejectedWhileUnhealthy.accepted, false); assert.equal(rejectedWhileUnhealthy.scheduler.disposition, 'rejected-lane-unhealthy'); assert.equal(rejectedWhileUnhealthy.scheduler.noMutation, true); assert.equal(blockedWhileUnsettled.recovered, false); assert.equal(blockedWhileUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(settledWait.ok, true); assert.equal(verifyAfterLateSuccess.ok, true); assert.equal(adapterResultAfterLateSuccess, null); assert.equal(snapshotAfterLateSuccess.executor.unsettledTimedOutOperationCount, 0); assert.equal(snapshotAfterLateSuccess.executor.successfulTimedOutOperationCount, 1); assert.equal(snapshotAfterLateSuccess.executor.failedTimedOutOperationCount, 0); assert.equal(snapshotAfterLateSuccess.executor.stats.lateProviderSettlementSuccesses, 1);
  assert.equal(blockedByLateSuccess.recovered, false); assert.equal(blockedByLateSuccess.reason, 'timed-out-operation-late-success'); assert.equal(stillRejectedAfterLateSuccess.accepted, false); assert.equal(stillRejectedAfterLateSuccess.scheduler.noMutation, true); assert.equal(unreviewedClearRejected.ok, false); assert.equal(unreviewedClearRejected.code, 'late-success-clear-review-required'); assert.equal(unscopedClearRejected.ok, false); assert.equal(unscopedClearRejected.code, 'late-success-clear-scope-required'); assert.equal(cleared.clearedCount, 1); assert.equal(recoveredAfterClear.recovered, true); assert.equal(recoveredSchedule.accepted, true); assert.equal(recoveredResult?.ok, true); assert.equal(recoveredVerify?.ok, true); assert.equal(finalSnapshot.executor.successfulTimedOutOperationCount, 0); assert.equal(finalSnapshot.executor.failedTimedOutOperationCount, 0); assert.equal(finalSnapshot.executor.stats.successfulTimedOutOperationsCleared, 1); assert.equal(validation.ok, true);
  for (const kind of ['storage-lane:operation-timeout-unsettled','storage-lane:operation-timeout','storage-lane:late-provider-success','storage-lane:late-provider-settlement','block-store-lane:recover-timed-out-successes-blocked','storage-lane:late-provider-successes-clear-rejected','storage-lane:late-provider-successes-cleared','block-store-lane:recover-settled']) assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-late-success-quarantine-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that late successful provider settlement after BRT_STORAGE_OPERATION_TIMEOUT is quarantined until explicit reviewed, scoped maintenance clear.', observations: { accepted, timeoutResult, snapshotAfterTimeout, storageLaneAfterTimeout, committedButUnsettled, rejectedWhileUnhealthy, blockedWhileUnsettled, settledWait, verifyAfterLateSuccess, adapterResultAfterLateSuccess, snapshotAfterLateSuccess, blockedByLateSuccess, stillRejectedAfterLateSuccess, unreviewedClearRejected, unscopedClearRejected, cleared, recoveredAfterClear, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, traceKinds }, claimsChecked: ['Late provider success after operation timeout is tracked separately from unsettled and failed timed-out operations','Successful late provider settlement does not publish a normal adapter result for the timed-out scheduler operation','recoverWhenStoreSettled blocks on timed-out-operation-late-success until reviewed, scoped maintenance clears the success','follow-on writes remain rejected with noMutation while the late-success quarantine is active'], nonClaims: ['Late-success quarantine is not provider cancellation, rollback, no-mutation, exactly-once, or durability evidence.','Synthetic release-tier proof only; browser OPFS/Web Locks proof is separate.','No automatic recovery, cross-browser behavior, quota, eviction, persistent-retention, throughput, latency, SLO, or production-readiness claim.'] };
}
const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-late-success-quarantine-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed late-success quarantine proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_late_success_quarantine_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
// Audit phrase: successful late provider settlement does not publish a normal adapter result.
// late provider success must not retroactively publish success
