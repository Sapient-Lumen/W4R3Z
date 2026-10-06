#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-mixed-outcome-quarantine-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-MIXED-OUTCOME-QUARANTINE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (typeof value === 'string') return new TextEncoder().encode(value); if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const error = new Error(message); error.name = 'BrowserRTSyntheticMixedOutcomeError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; }

function makeMixedOutcomeStore({ trace = null } = {}) {
  const records = new Map();
  const releases = new Map([['success', deferred()], ['failure', deferred()]]);
  const state = { puts: 0, committedBeforeSettle: 0, lateSuccesses: 0, lateFailures: 0, waitForSettledCalls: 0 };
  const labelKind = (label) => String(label || '').includes('failure') ? 'failure' : (String(label || '').includes('success') ? 'success' : 'normal');
  return {
    name: 'synthetic-mixed-outcome-block-store', provider: 'synthetic-mixed-outcome-provider-v0', releases, state,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; const kind = labelKind(fields.label);
      state.puts += 1; records.set(digest, body); state.committedBeforeSettle += 1;
      trace?.emit('synthetic-mixed-outcome-store:committed-before-settle', { digest, bytes: body.byteLength, label: fields.label ?? null, kind });
      if (kind === 'success') { const reason = await releases.get('success').promise; state.lateSuccesses += 1; trace?.emit('synthetic-mixed-outcome-store:late-success', { digest, reason }); }
      if (kind === 'failure') { const reason = await releases.get('failure').promise; state.lateFailures += 1; trace?.emit('synthetic-mixed-outcome-store:late-failure', { digest, reason }); throw codedError('BRT_SYNTHETIC_LATE_FAILURE', 'synthetic late failure after committed timed-out write', { digest, reason }); }
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
  const scheduler = createCrossLaneScheduler({ label: `${REVISION}-mixed-outcome-quarantine-scheduler`, trace, lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
  const store = makeMixedOutcomeStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-mixed-outcome-quarantine-adapter`, store, scheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 120 });
  const successPayload = `BrowserRT ${REVISION} mixed late success payload`; const failurePayload = `BrowserRT ${REVISION} mixed late failure payload`;
  const successDigest = `sha256:${await digestBytesHex(bytes(successPayload))}`; const failureDigest = `sha256:${await digestBytesHex(bytes(failurePayload))}`;

  const acceptedSuccess = adapter.schedulePut(successPayload, { id: 'mixed-late-success-put', label: 'mixed-late-success', priority: 'user-visible' });
  const acceptedFailure = adapter.schedulePut(failurePayload, { id: 'mixed-late-failure-put', label: 'mixed-late-failure', priority: 'user-visible' });
  const dispatchSuccess = scheduler.dispatchNext(); const dispatchFailure = scheduler.dispatchNext();
  const [timeoutSuccess, timeoutFailure] = await Promise.all([adapter.executor.executeDispatched(dispatchSuccess), adapter.executor.executeDispatched(dispatchFailure)]);
  const snapshotAfterTimeouts = adapter.snapshot(); const laneAfterTimeouts = snapshotAfterTimeouts.executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const successCommitted = await store.has(successDigest); const failureCommitted = await store.has(failureDigest);
  const quarantineAfterTimeouts = adapter.timedOutOperationQuarantine('storage');
  const missingCategoryClear = adapter.clearTimedOutOperationQuarantine({ lane: 'storage', reviewed: true, reviewToken: 'missing-category-review', reason: 'reviewed-but-category-missing' });
  const blockedWhileUnsettled = await adapter.recoverWhenStoreSettled({ timeoutMs: 45, intervalMs: 5, reason: 'mixed-outcome-still-unsettled' });

  store.releases.get('success').resolve('release-mixed-late-success'); store.releases.get('failure').resolve('release-mixed-late-failure');
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 600, intervalMs: 5 });
  const quarantineAfterSettlement = adapter.timedOutOperationQuarantine('storage');
  const verifySuccessAfterLate = await store.verify(successDigest); const verifyFailureAfterLate = await store.verify(failureDigest);
  const blockedBySuccess = await adapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'mixed-late-success-still-quarantined' });
  const rejectedAfterMixedSettlement = adapter.schedulePut('must-not-queue-after-mixed-late-outcome', { id: 'reject-after-mixed-late-outcome' });
  const unreviewedSuccessClear = adapter.clearTimedOutOperationQuarantine({ category: 'success', lane: 'storage', opId: 'mixed-late-success-put', reason: 'unreviewed-success-clear' });
  const clearSuccess = adapter.clearTimedOutOperationQuarantine({ category: 'success', lane: 'storage', opId: 'mixed-late-success-put', reviewed: true, reviewToken: `${REVISION}-mixed-success-reviewed`, reason: 'reviewed-success-clear' });
  const blockedByFailure = await adapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'mixed-late-failure-still-quarantined' });
  const unscopedFailureClear = adapter.clearTimedOutOperationQuarantine({ category: 'failure', lane: 'storage', reviewed: true, reviewToken: `${REVISION}-unscoped-failure`, reason: 'reviewed-failure-clear-without-scope' });
  const clearFailure = adapter.clearTimedOutOperationQuarantine({ category: 'failure', lane: 'storage', opId: 'mixed-late-failure-put', reviewed: true, reviewToken: `${REVISION}-mixed-failure-reviewed`, reason: 'reviewed-failure-clear' });
  const recoveredAfterBothClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'mixed-late-outcomes-reviewed-recovery' });
  const recoveredSchedule = adapter.schedulePut('BrowserRT mixed late outcome quarantine recovered write', { id: 'mixed-outcome-recovered-put', priority: 'user-visible', label: 'recovered-after-mixed-late-outcomes' });
  const recoveryDrain = await adapter.drain({ maxSteps: 3 }); const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'mixed-outcome-recovered-put'); const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const finalSnapshot = adapter.snapshot(); const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot); const traceKinds = trace.kinds();

  assert.equal(acceptedSuccess.accepted, true); assert.equal(acceptedFailure.accepted, true);
  assert.equal(dispatchSuccess.dispatched, true); assert.equal(dispatchFailure.dispatched, true);
  assert.equal(timeoutSuccess.ok, false); assert.equal(timeoutFailure.ok, false);
  assert.equal(timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(snapshotAfterTimeouts.executor.unsettledTimedOutOperationCount, 2); assert.equal(laneAfterTimeouts.healthy, false); assert.equal(laneAfterTimeouts.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(successCommitted, true); assert.equal(failureCommitted, true);
  assert.equal(quarantineAfterTimeouts.totalCount, 2); assert.equal(quarantineAfterTimeouts.unsettledCount, 2); assert.deepEqual(quarantineAfterTimeouts.blockedReasons, ['timed-out-operation-still-unsettled']);
  assert.equal(missingCategoryClear.ok, false); assert.equal(missingCategoryClear.code, 'timed-out-quarantine-clear-scope-required');
  assert.equal(blockedWhileUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(settled.ok, true); assert.equal(settled.count, 0);
  assert.equal(quarantineAfterSettlement.totalCount, 2); assert.equal(quarantineAfterSettlement.successfulCount, 1); assert.equal(quarantineAfterSettlement.failedCount, 1); assert.deepEqual(quarantineAfterSettlement.blockedReasons, ['timed-out-operation-late-success', 'timed-out-operation-late-failure']);
  assert.equal(verifySuccessAfterLate.ok, true); assert.equal(verifyFailureAfterLate.ok, true);
  assert.ok(adapter.result('mixed-late-success-put') == null); assert.ok(adapter.result('mixed-late-failure-put') == null);
  assert.equal(blockedBySuccess.reason, 'timed-out-operation-late-success'); assert.equal(blockedBySuccess.quarantine.totalCount, 2);
  assert.equal(rejectedAfterMixedSettlement.accepted, false); assert.equal(rejectedAfterMixedSettlement.scheduler.noMutation, true);
  assert.equal(unreviewedSuccessClear.ok, false); assert.equal(unreviewedSuccessClear.code, 'timed-out-quarantine-clear-review-required');
  assert.equal(clearSuccess.ok, true); assert.equal(clearSuccess.clearedCount, 1);
  assert.equal(blockedByFailure.reason, 'timed-out-operation-late-failure'); assert.equal(blockedByFailure.quarantine.failedCount, 1);
  assert.equal(unscopedFailureClear.ok, false); assert.equal(unscopedFailureClear.code, 'timed-out-quarantine-clear-scope-required');
  assert.equal(clearFailure.ok, true); assert.equal(clearFailure.clearedCount, 1);
  assert.equal(recoveredAfterBothClear.recovered, true); assert.equal(recoveredSchedule.accepted, true); assert.equal(recoveredResult?.ok, true); assert.equal(recoveredVerify?.ok, true);
  assert.equal(finalSnapshot.executor.timedOutOperationQuarantineCount, 0); assert.equal(finalSnapshot.executor.stats.reviewedLateProviderSuccesses, 1); assert.equal(finalSnapshot.executor.stats.reviewedLateProviderFailures, 1); assert.equal(finalSnapshot.executor.stats.timedOutOperationQuarantineClearRejected, 3);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  for (const kind of ['storage-lane:operation-timeout-unsettled', 'storage-lane:late-provider-success', 'storage-lane:late-provider-failure', 'storage-lane:timed-out-quarantine-clear-rejected', 'storage-lane:timed-out-quarantine-cleared', 'block-store-lane:recover-timed-out-successes-blocked', 'block-store-lane:recover-timed-out-failures-blocked', 'block-store-lane:recover-settled']) assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-mixed-outcome-quarantine-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that mixed late provider success and late provider failure after operation timeout remain visible as separate reviewed/scoped quarantine categories before storage-lane recovery.', observations: { timeoutSuccess, timeoutFailure, snapshotAfterTimeouts, successCommitted, failureCommitted, quarantineAfterTimeouts, missingCategoryClear, blockedWhileUnsettled, settled, quarantineAfterSettlement, verifySuccessAfterLate, verifyFailureAfterLate, blockedBySuccess, rejectedAfterMixedSettlement, unreviewedSuccessClear, clearSuccess, blockedByFailure, unscopedFailureClear, clearFailure, recoveredAfterBothClear, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, traceKinds }, claimsChecked: ['mixed late success and late failure remain in separate quarantine categories', 'unified clear requires explicit category plus reviewed scope', 'clearing the success category does not hide the failure category', 'lane recovery succeeds only after both quarantined outcomes are reviewed/scoped and cleared'], nonClaims: ['This is browser-light release evidence only.', 'Timeouts and late outcomes are not cancellation, rollback, no-mutation, exactly-once, durability, cross-browser, quota, eviction, crash, or production readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-mixed-outcome-quarantine-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed mixed-outcome quarantine proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_mixed_outcome_quarantine_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
