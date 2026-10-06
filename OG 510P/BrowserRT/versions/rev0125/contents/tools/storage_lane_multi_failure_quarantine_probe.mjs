#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-multi-failure-quarantine-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-MULTI-FAILURE-QUARANTINE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (typeof value === 'string') return new TextEncoder().encode(value); if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticMultiLateProviderError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }

function makeMultiLateFailingStore({ trace = null } = {}) {
  const releases = new Map([['a', deferred()], ['b', deferred()]]);
  const records = new Map();
  const refs = new Map();
  const state = { puts: 0, committedBeforeSettle: 0, lateFailures: 0, cleanupCalls: 0, waitForSettledCalls: 0 };
  return {
    name: 'synthetic-multi-late-failing-block-store', provider: 'synthetic-multi-late-failing-provider-v1', releases, refs, state,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; const label = fields.label || 'unlabeled';
      state.puts += 1; state.committedBeforeSettle += 1; records.set(digest, body);
      const ref = Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null });
      refs.set(label, ref);
      trace?.emit('synthetic-multi-late-failing-store:committed-before-settle', { digest, label, bytes: body.byteLength });
      if (label === 'multi-late-failure-a' || label === 'multi-late-failure-b') {
        const key = label.endsWith('-a') ? 'a' : 'b';
        await releases.get(key).promise;
        state.lateFailures += 1;
        trace?.emit('synthetic-multi-late-failing-store:late-failure', { digest, label });
        throw codedError('BRT_OPFS_OPERATION_FAILED', 'synthetic late provider failure after timeout', { digest, label });
      }
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); return Object.freeze({ digest, present: Boolean(row), ok: Boolean(row), bytes: row?.byteLength ?? 0, path: null }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: Array.from(records.values()).reduce((n, row) => n + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { state.cleanupCalls += 1; const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { state.waitForSettledCalls += 1; return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-store-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const scheduler = createCrossLaneScheduler({ label: `${REVISION}-multi-failure-quarantine-scheduler`, trace, lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
  const store = makeMultiLateFailingStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-multi-failure-quarantine-adapter`, store, scheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 120 });
  const payloadA = `BrowserRT ${REVISION} multi late failure quarantine payload A`;
  const payloadB = `BrowserRT ${REVISION} multi late failure quarantine payload B`;
  const digestA = `sha256:${await digestBytesHex(bytes(payloadA))}`;
  const digestB = `sha256:${await digestBytesHex(bytes(payloadB))}`;

  const acceptedA = adapter.schedulePut(payloadA, { id: 'multi-late-failing-put-a', label: 'multi-late-failure-a', priority: 'user-visible' });
  const acceptedB = adapter.schedulePut(payloadB, { id: 'multi-late-failing-put-b', label: 'multi-late-failure-b', priority: 'user-visible' });
  const dispatchA = scheduler.dispatchNext();
  const dispatchB = scheduler.dispatchNext();
  const [timeoutA, timeoutB] = await Promise.all([adapter.executor.executeDispatched(dispatchA), adapter.executor.executeDispatched(dispatchB)]);
  const snapshotAfterTimeouts = adapter.snapshot();
  const laneAfterTimeouts = snapshotAfterTimeouts.executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const committedA = await store.has(digestA);
  const committedB = await store.has(digestB);
  const blockedWhileUnsettled = await adapter.recoverWhenStoreSettled({ timeoutMs: 45, intervalMs: 5, reason: 'multi-late-provider-still-unsettled' });
  const unsafeClear = adapter.clearFailedTimedOutOperations({ lane: 'storage', reason: 'unsafe-unreviewed-clear' });
  const ambiguousClear = adapter.clearFailedTimedOutOperations({ lane: 'storage', reviewed: true, reviewToken: 'ambiguous-review-without-op-id', reason: 'ambiguous-reviewed-clear' });
  const remainingAfterRejectedClears = adapter.failedTimedOutOperations('storage');

  store.releases.get('a').resolve('release-a');
  store.releases.get('b').resolve('release-b');
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const failedAfterLate = adapter.failedTimedOutOperations('storage');
  const verifyAAfterLate = await store.verify(digestA);
  const verifyBAfterLate = await store.verify(digestB);
  const blockedByTwoFailures = await adapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'multi-late-provider-failures-block-recovery' });
  const rejectedAfterLate = adapter.schedulePut('must-not-queue-after-multi-late-failure', { id: 'reject-after-multi-late-failure' });
  const clearReviewA = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: 'multi-late-failing-put-a', reviewer: 'legacy-compatible-release-probe', reviewToken: 'rev0078-reviewed-clear-a', reason: 'maintenance-reviewed-first-late-provider-failure' });
  const clearA = adapter.clearFailedTimedOutOperations({ reviewManifest: clearReviewA, requireReviewFingerprint: true, reason: 'maintenance-reviewed-first-late-provider-failure' });
  const blockedAfterOneClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'one-late-provider-failure-still-quarantined' });
  const clearReviewB = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: 'multi-late-failing-put-b', reviewer: 'legacy-compatible-release-probe', reviewToken: 'rev0078-reviewed-clear-b', reason: 'maintenance-reviewed-second-late-provider-failure' });
  const clearB = adapter.clearFailedTimedOutOperations({ reviewManifest: clearReviewB, requireReviewFingerprint: true, reason: 'maintenance-reviewed-second-late-provider-failure' });
  const recoveredAfterBothClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'multi-late-provider-failures-reviewed-recovery' });
  const recoveredSchedule = adapter.schedulePut('BrowserRT multi late failure quarantine recovered write', { id: 'multi-failure-recovered-put', priority: 'user-visible', label: 'recovered-after-multi-late-failure' });
  const recoveryDrain = await adapter.drain({ maxSteps: 3 });
  const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'multi-failure-recovered-put');
  const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();

  assert.equal(acceptedA.accepted, true); assert.equal(acceptedB.accepted, true);
  assert.equal(dispatchA.dispatched, true); assert.equal(dispatchB.dispatched, true);
  assert.equal(timeoutA.ok, false); assert.equal(timeoutB.ok, false);
  assert.equal(timeoutA.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(timeoutB.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(snapshotAfterTimeouts.executor.unsettledTimedOutOperationCount, 2, 'both timed-out provider operations should remain unsettled');
  assert.equal(laneAfterTimeouts.healthy, false); assert.equal(laneAfterTimeouts.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(committedA, true); assert.equal(committedB, true);
  assert.equal(blockedWhileUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(unsafeClear.ok, false); assert.equal(unsafeClear.code, 'late-failure-clear-review-required');
  assert.equal(ambiguousClear.ok, false); assert.equal(ambiguousClear.code, 'late-failure-clear-scope-required');
  assert.equal(remainingAfterRejectedClears.length, 0, 'rejected clears before late settlement must not invent failures');
  assert.equal(settled.ok, true); assert.equal(settled.count, 0);
  assert.equal(failedAfterLate.length, 2, 'both failed timed-out operations must remain quarantined');
  assert.deepEqual(failedAfterLate.map((row) => row.opId).sort(), ['multi-late-failing-put-a','multi-late-failing-put-b']);
  assert.equal(verifyAAfterLate.ok, true); assert.equal(verifyBAfterLate.ok, true);
  assert.ok(adapter.result('multi-late-failing-put-a') == null); assert.ok(adapter.result('multi-late-failing-put-b') == null);
  assert.equal(blockedByTwoFailures.recovered, false); assert.equal(blockedByTwoFailures.reason, 'timed-out-operation-late-failure');
  assert.equal(rejectedAfterLate.accepted, false); assert.equal(rejectedAfterLate.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(clearA.ok, true); assert.equal(clearA.clearedCount, 1); assert.equal(blockedAfterOneClear.reason, 'timed-out-operation-late-failure');
  assert.equal(clearB.ok, true); assert.equal(clearB.clearedCount, 1); assert.equal(recoveredAfterBothClear.recovered, true);
  assert.equal(recoveredSchedule.accepted, true); assert.equal(recoveredResult.ok, true); assert.equal(recoveredVerify.ok, true);
  assert.equal(finalSnapshot.executor.failedTimedOutOperationCount, 0); assert.equal(finalSnapshot.executor.stats.lateProviderFailureClearRejected, 2); assert.equal(finalSnapshot.executor.stats.reviewedLateProviderFailures, 2);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  for (const kind of ['storage-lane:operation-timeout-unsettled', 'storage-lane:operation-timeout', 'storage-lane:late-provider-failure', 'storage-lane:late-provider-failure-clear-rejected', 'storage-lane:late-provider-failures-cleared', 'block-store-lane:recover-timed-out-failures-blocked', 'block-store-lane:recover-settled']) assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-multi-failure-quarantine-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that multiple late provider failures after operation timeout require reviewed, scoped clearing before storage-lane recovery.', observations: { timeoutA, timeoutB, snapshotAfterTimeouts, committedA, committedB, blockedWhileUnsettled, unsafeClear, ambiguousClear, remainingAfterRejectedClears, settled, failedAfterLate, verifyAAfterLate, verifyBAfterLate, blockedByTwoFailures, rejectedAfterLate, clearA, blockedAfterOneClear, clearB, recoveredAfterBothClear, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, traceKinds }, claimsChecked: ['multiple late provider failures remain separate quarantine items', 'unreviewed clears are rejected', 'reviewed but unscoped clears are rejected', 'clearing one failure does not reopen recovery while another failure remains', 'explicit reviewed scoped clearing of both failures permits recovery'], nonClaims: ['This is browser-light release evidence only.', 'Timeouts and late failures are not cancellation, rollback, no-mutation, exactly-once, provider interruption, durability, cross-browser, quota, eviction, crash, or production readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-multi-failure-quarantine-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed multi-failure quarantine proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_multi_failure_quarantine_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
