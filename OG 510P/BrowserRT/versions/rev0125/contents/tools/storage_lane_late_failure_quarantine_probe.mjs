#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-late-failure-quarantine-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-LATE-FAILURE-QUARANTINE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
}
function bytes(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value);
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  return new TextEncoder().encode(String(value));
}
function codedError(code, message, detail = {}) {
  const error = new Error(message);
  error.name = 'BrowserRTSyntheticLateProviderError';
  error.code = code;
  error.storageDisposition = code;
  error.detail = Object.freeze({ ...detail });
  return error;
}

function makeLateFailingStore({ trace = null } = {}) {
  const release = deferred();
  const records = new Map();
  const state = { puts: 0, committedBeforeSettle: 0, waitForSettledCalls: 0, released: false, lateFailures: 0, cleanupCalls: 0 };
  return {
    name: 'synthetic-late-failing-block-store',
    provider: 'synthetic-late-failing-provider-v0',
    release,
    state,
    async put(payload, fields = {}) {
      const body = bytes(payload);
      const hash = await digestBytesHex(body);
      const digest = `sha256:${hash}`;
      state.puts += 1;
      records.set(digest, body);
      state.committedBeforeSettle += 1;
      trace?.emit('synthetic-late-failing-store:committed-before-settle', { digest, bytes: body.byteLength, label: fields.label ?? null });
      if (fields?.label === 'late-provider-failure') {
        await release.promise;
        state.released = true;
        state.lateFailures += 1;
        trace?.emit('synthetic-late-failing-store:late-failure', { digest });
        throw codedError('BRT_OPFS_OPERATION_FAILED', 'synthetic late provider failure after timeout', { digest, label: fields.label });
      }
      const ref = Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null });
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, path: null, label: fields.label ?? null });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); return Object.freeze({ digest, present: Boolean(row), ok: Boolean(row), bytes: row?.byteLength ?? 0, path: null }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: Array.from(records.values()).reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { state.cleanupCalls += 1; const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { state.waitForSettledCalls += 1; return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-store-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const scheduler = createCrossLaneScheduler({
    label: `${REVISION}-late-failure-quarantine-scheduler`,
    trace,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const store = makeLateFailingStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-late-failure-quarantine-adapter`, store, scheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 120 });
  const payload = `BrowserRT ${REVISION} late-failure quarantine payload`;
  const timeoutDigest = `sha256:${await digestBytesHex(bytes(payload))}`;

  const accepted = adapter.schedulePut(payload, { id: 'late-failing-put-times-out', label: 'late-provider-failure', priority: 'user-visible' });
  const drain = await adapter.drain({ maxSteps: 2 });
  const timeoutResult = drain.results.find((row) => row.opId === 'late-failing-put-times-out');
  const snapshotAfterTimeout = adapter.snapshot();
  const storageLaneAfterTimeout = snapshotAfterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const committedButUnsettled = await store.has(timeoutDigest);
  const blockedWhileUnsettled = await adapter.recoverWhenStoreSettled({ timeoutMs: 45, intervalMs: 5, reason: 'late-provider-still-unsettled' });

  store.release.resolve('release-late-provider-to-fail');
  const settledWait = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const snapshotAfterLateFailure = adapter.snapshot();
  const failedTimedOutOperations = adapter.failedTimedOutOperations('storage');
  const verifyCommittedAfterLateFailure = await store.verify(timeoutDigest);
  const adapterResultAfterLateFailure = adapter.result('late-failing-put-times-out') ?? null;
  const blockedByLateFailure = await adapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'late-provider-failure-blocks-recovery' });
  const rejectedAfterLateFailure = adapter.schedulePut('must-not-queue-after-late-failure', { id: 'reject-after-late-failure' });

  const unscopedClearRejected = adapter.clearFailedTimedOutOperations({ lane: 'storage', reviewed: true, reviewToken: 'rev0073-late-failure-review-unscoped', reason: 'maintenance-reviewed-late-provider-failure-without-scope' });
  const clearReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: 'late-failing-put-times-out', reviewer: 'legacy-compatible-release-probe', reviewToken: 'rev0078-late-failure-review-scoped', reason: 'maintenance-reviewed-late-provider-failure' });
  const cleared = adapter.clearFailedTimedOutOperations({ reviewManifest: clearReview, requireReviewFingerprint: true, reason: 'maintenance-reviewed-late-provider-failure' });
  const recoveredAfterClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'late-provider-failure-reviewed-recovery' });
  const recoveredSchedule = adapter.schedulePut('BrowserRT late failure quarantine recovered write', { id: 'late-failure-recovered-put', priority: 'user-visible', label: 'recovered-after-late-failure' });
  const recoveryDrain = await adapter.drain({ maxSteps: 3 });
  const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'late-failure-recovered-put');
  const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();

  assert.equal(accepted.accepted, true, 'late-failing operation should schedule');
  assert.equal(timeoutResult?.ok, false, 'late-failing operation should time out first');
  assert.equal(timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(snapshotAfterTimeout.executor.unsettledTimedOutOperationCount, 1, 'timed-out provider operation should remain tracked as unsettled');
  assert.equal(snapshotAfterTimeout.executor.failedTimedOutOperationCount, 0, 'no failed late settlement before provider actually settles');
  assert.equal(storageLaneAfterTimeout?.healthy, false, 'storage lane should be unhealthy after operation timeout');
  assert.equal(storageLaneAfterTimeout?.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(committedButUnsettled, true, 'operation timeout is not a no-mutation guarantee');
  assert.equal(blockedWhileUnsettled.recovered, false, 'recovery should first block on unsettled provider work');
  assert.equal(blockedWhileUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(settledWait.ok, true, 'late provider failure still counts as provider settlement');
  assert.equal(settledWait.count, 0);
  assert.equal(snapshotAfterLateFailure.executor.unsettledTimedOutOperationCount, 0, 'unsettled provider work should drain after late failure');
  assert.equal(snapshotAfterLateFailure.executor.failedTimedOutOperationCount, 1, 'late failure should remain quarantined after settlement');
  assert.equal(snapshotAfterLateFailure.executor.stats.lateProviderSettlementFailures, 1);
  assert.equal(snapshotAfterLateFailure.executor.stats.failedTimedOutOperations, 1);
  assert.equal(failedTimedOutOperations.length, 1, 'adapter should expose failed timed-out operation quarantine');
  assert.equal(failedTimedOutOperations[0].error.code, 'BRT_OPFS_OPERATION_FAILED');
  assert.equal(verifyCommittedAfterLateFailure.ok, true, 'late provider failure can happen after mutation; recovery must not assume rollback');
  assert.equal(adapterResultAfterLateFailure, null, 'late failure must not publish a successful adapter result');
  assert.equal(blockedByLateFailure.recovered, false, 'recovery should block after late provider failure until reviewed');
  assert.equal(blockedByLateFailure.reason, 'timed-out-operation-late-failure');
  assert.equal(blockedByLateFailure.failedTimedOutOperations.length, 1);
  assert.equal(rejectedAfterLateFailure.accepted, false, 'lane should remain unhealthy while late failure is quarantined');
  assert.equal(rejectedAfterLateFailure.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(unscopedClearRejected.ok, false, 'maintenance clear without opId/all should be rejected');
  assert.equal(unscopedClearRejected.code, 'late-failure-clear-scope-required');
  assert.equal(cleared.clearedCount, 1, 'maintenance should explicitly clear reviewed late failure');
  assert.equal(recoveredAfterClear.recovered, true, 'recovery should succeed after late failure is explicitly reviewed/cleared');
  assert.equal(recoveredSchedule.accepted, true, 'new write should schedule after cleared recovery');
  assert.equal(recoveredResult?.ok, true, 'new write should complete after recovery');
  assert.equal(recoveredVerify?.ok, true, 'recovered block should verify');
  assert.equal(finalSnapshot.executor.failedTimedOutOperationCount, 0, 'no failed timed-out quarantine should remain');
  assert.equal(finalSnapshot.executor.stats.failedTimedOutOperationsCleared, 1);
  assert.equal(validation.ok, true, validation.errors.join('\n'));
  for (const kind of ['storage-lane:operation-timeout-unsettled', 'storage-lane:late-provider-failure', 'storage-lane:late-provider-settlement', 'block-store-lane:recover-timed-out-failures-blocked', 'storage-lane:late-provider-failures-cleared', 'block-store-lane:recover-settled']) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-late-failure-quarantine-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier proof that late provider rejection after BRT_STORAGE_OPERATION_TIMEOUT remains quarantined: BrowserRT tracks the late failure, blocks settled recovery even after provider settlement drains, keeps the lane unhealthy until explicit maintenance acknowledgement, and avoids retroactive adapter success.',
    observations: { accepted, timeoutResult, snapshotAfterTimeout, storageLaneAfterTimeout, committedButUnsettled, blockedWhileUnsettled, settledWait, snapshotAfterLateFailure, failedTimedOutOperations, verifyCommittedAfterLateFailure, adapterResultAfterLateFailure, blockedByLateFailure, rejectedAfterLateFailure, unscopedClearRejected, cleared, recoveredAfterClear, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, validation, traceKinds },
    claimsChecked: [
      'Late provider failure after storage-lane operation timeout is tracked separately from unsettled timed-out work',
      'recoverWhenStoreSettled blocks on timed-out-operation-late-failure after late rejection settles',
      'Late failure does not retroactively publish adapter success and does not imply rollback/no-mutation',
      'Maintenance must explicitly clear reviewed failed timed-out operations before recovery reopens the lane'
    ],
    nonClaims: [
      'Synthetic release-tier proof only; it does not launch a browser or prove OPFS/Web Locks behavior.',
      'Operation timeout and late failure quarantine do not prove cancellation, rollback, exactly-once behavior, or provider interruption.',
      'Explicit clearing is maintenance acknowledgement in this proof, not automatic correctness or production recovery.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-late-failure-quarantine-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed late-failure quarantine proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[storage_lane_late_failure_quarantine_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
