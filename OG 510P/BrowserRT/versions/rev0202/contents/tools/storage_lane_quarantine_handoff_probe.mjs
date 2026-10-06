#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-handoff-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-HANDOFF-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (typeof value === 'string') return new TextEncoder().encode(value); if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticProviderError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }
function makeScheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }

function makeHandoffStore({ trace = null } = {}) {
  const records = new Map();
  const releases = { success: deferred(), failure: deferred() };
  const state = { puts: 0, lateSuccessPuts: 0, lateFailurePuts: 0, immediatePuts: 0, waitForSettledCalls: 0 };
  return {
    name: 'synthetic-quarantine-handoff-block-store',
    provider: 'synthetic-quarantine-handoff-provider-v0',
    releases,
    async put(payload, fields = {}) {
      const body = bytes(payload);
      const hash = await digestBytesHex(body);
      const digest = `sha256:${hash}`;
      const ref = Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null });
      records.set(digest, body);
      state.puts += 1;
      trace?.emit('synthetic-handoff-store:put-committed', { digest, bytes: body.byteLength, label: fields.label ?? null });
      if (fields.label === 'late-success') {
        state.lateSuccessPuts += 1;
        await releases.success.promise;
        trace?.emit('synthetic-handoff-store:late-success-release', { digest });
        return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, path: null, lateSuccessAfterTimeout: true });
      }
      if (fields.label === 'late-failure') {
        state.lateFailurePuts += 1;
        await releases.failure.promise;
        trace?.emit('synthetic-handoff-store:late-failure-release', { digest });
        throw codedError('BRT_SYNTHETIC_LATE_PROVIDER_FAILURE', 'synthetic provider failed after committing for quarantine handoff proof', { digest, bytes: body.byteLength });
      }
      state.immediatePuts += 1;
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, path: null });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing block ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); return Object.freeze({ digest, present: Boolean(row), ok: Boolean(row), bytes: row?.byteLength ?? 0, path: null }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: Array.from(records.values()).reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { state.waitForSettledCalls += 1; return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-store-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}

function combineLedgers(...ledgers) {
  return Object.freeze({
    schema: 'brt.storageLane.timedOutOperationQuarantine.v1',
    exportedAtMs: Date.now(),
    label: `${REVISION}-combined-quarantine-handoff-ledger`,
    reason: 'combined-late-success-and-late-failure-handoff',
    lane: 'storage',
    counts: Object.freeze({
      total: ledgers.reduce((sum, l) => sum + (l.counts?.total ?? 0), 0),
      unsettled: ledgers.reduce((sum, l) => sum + (l.unsettledTimedOutOperations?.length ?? 0), 0),
      successful: ledgers.reduce((sum, l) => sum + (l.successfulTimedOutOperations?.length ?? 0), 0),
      failed: ledgers.reduce((sum, l) => sum + (l.failedTimedOutOperations?.length ?? 0), 0)
    }),
    unsettledTimedOutOperations: Object.freeze(ledgers.flatMap((l) => l.unsettledTimedOutOperations ?? [])),
    successfulTimedOutOperations: Object.freeze(ledgers.flatMap((l) => l.successfulTimedOutOperations ?? [])),
    failedTimedOutOperations: Object.freeze(ledgers.flatMap((l) => l.failedTimedOutOperations ?? []))
  });
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeHandoffStore({ trace });
  const successAdapter = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-handoff-success-adapter`, store, scheduler: makeScheduler(`${REVISION}-quarantine-handoff-success-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 60 });
  const failureAdapter = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-handoff-failure-adapter`, store, scheduler: makeScheduler(`${REVISION}-quarantine-handoff-failure-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 60 });

  const successPayload = `BrowserRT ${REVISION} quarantine handoff late success payload`;
  const failurePayload = `BrowserRT ${REVISION} quarantine handoff late failure payload`;
  const successDigest = `sha256:${await digestBytesHex(bytes(successPayload))}`;
  const failureDigest = `sha256:${await digestBytesHex(bytes(failurePayload))}`;

  const successAccepted = successAdapter.schedulePut(successPayload, { id: 'handoff-late-success-put', priority: 'user-visible', label: 'late-success' });
  const successDrain = await successAdapter.drain({ maxSteps: 2 });
  const successTimeout = successDrain.results.find((row) => row.opId === 'handoff-late-success-put');
  const successPresentBeforeRelease = await store.has(successDigest);
  store.releases.success.resolve('release-late-success-for-handoff');
  const successSettled = await successAdapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const successVerify = await store.verify(successDigest);
  const successLedger = successAdapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'export-late-success-for-handoff' });

  const failureAccepted = failureAdapter.schedulePut(failurePayload, { id: 'handoff-late-failure-put', priority: 'user-visible', label: 'late-failure' });
  const failureDrain = await failureAdapter.drain({ maxSteps: 2 });
  const failureTimeout = failureDrain.results.find((row) => row.opId === 'handoff-late-failure-put');
  const failurePresentBeforeRelease = await store.has(failureDigest);
  store.releases.failure.resolve('release-late-failure-for-handoff');
  const failureSettled = await failureAdapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const failureVerify = await store.verify(failureDigest);
  const failureLedger = failureAdapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'export-late-failure-for-handoff' });

  const combinedLedger = combineLedgers(successLedger, failureLedger);
  const handoffAdapter = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-handoff-import-adapter`, store, scheduler: makeScheduler(`${REVISION}-quarantine-handoff-import-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const importResult = handoffAdapter.importTimedOutOperationQuarantine(combinedLedger, { lane: 'storage', reason: 'import-combined-quarantine-ledger', markUnhealthy: true });
  const importedSnapshot = handoffAdapter.snapshot();
  const storageLaneAfterImport = importedSnapshot.executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const rejectedAfterImport = handoffAdapter.schedulePut('must-not-queue-after-quarantine-import', { id: 'reject-after-quarantine-import', priority: 'user-visible' });
  const directMarkHealthyRejected = handoffAdapter.markHealthy('storage', 'unsafe-direct-reopen-before-quarantine-review');
  const blockedBySuccess = await handoffAdapter.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 5, reason: 'handoff-recovery-before-review' });
  const successReview = handoffAdapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opId: 'handoff-late-success-put', reviewer: 'legacy-compatible-release-probe', reviewToken: `${REVISION}-handoff-success-review`, reason: 'reviewed-late-success-from-imported-ledger' });
  const clearSuccess = handoffAdapter.clearSuccessfulTimedOutOperations({ reviewManifest: successReview, requireReviewFingerprint: true, reason: 'reviewed-late-success-from-imported-ledger' });
  const blockedByFailure = await handoffAdapter.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 5, reason: 'handoff-recovery-after-success-clear' });
  const failureReview = handoffAdapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: 'handoff-late-failure-put', reviewer: 'legacy-compatible-release-probe', reviewToken: `${REVISION}-handoff-failure-review`, reason: 'reviewed-late-failure-from-imported-ledger' });
  const clearFailure = handoffAdapter.clearFailedTimedOutOperations({ reviewManifest: failureReview, requireReviewFingerprint: true, reason: 'reviewed-late-failure-from-imported-ledger' });
  const recoveredAfterClears = await handoffAdapter.recoverWhenStoreSettled({ timeoutMs: 500, intervalMs: 5, reason: 'handoff-quarantine-reviewed-and-cleared' });
  const recoveredSchedule = handoffAdapter.schedulePut(`BrowserRT ${REVISION} quarantine handoff recovered write`, { id: 'handoff-recovered-put', priority: 'user-visible', label: 'recovered-after-quarantine-handoff' });
  const recoveredDrain = await handoffAdapter.drain({ maxSteps: 3 });
  const recoveredResult = recoveredDrain.results.find((row) => row.opId === 'handoff-recovered-put');
  const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const finalSnapshot = handoffAdapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();

  assert.equal(successAccepted.accepted, true);
  assert.equal(successTimeout?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(successPresentBeforeRelease, true);
  assert.equal(successSettled.ok, true);
  assert.equal(successVerify.ok, true);
  assert.equal(successLedger.successfulTimedOutOperations.length, 1);
  assert.equal(failureAccepted.accepted, true);
  assert.equal(failureTimeout?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(failurePresentBeforeRelease, true);
  assert.equal(failureSettled.ok, true);
  assert.equal(failureVerify.ok, true, 'late failure is not rollback: committed synthetic block remains present');
  assert.equal(failureLedger.failedTimedOutOperations.length, 1);
  assert.equal(combinedLedger.successfulTimedOutOperations.length, 1);
  assert.equal(combinedLedger.failedTimedOutOperations.length, 1);
  assert.equal(importResult.ok, true);
  assert.equal(importResult.importedCount, 2);
  assert.equal(storageLaneAfterImport?.healthy, false);
  assert.equal(storageLaneAfterImport?.healthReason, 'timed-out-operation-quarantine-imported');
  assert.equal(importedSnapshot.executor.successfulTimedOutOperationCount, 1);
  assert.equal(importedSnapshot.executor.failedTimedOutOperationCount, 1);
  assert.equal(rejectedAfterImport.accepted, false);
  assert.equal(rejectedAfterImport.scheduler.noMutation, true);
  assert.equal(directMarkHealthyRejected.healthy, false);
  assert.equal(directMarkHealthyRejected.disposition, 'rejected-timed-out-operation-quarantine');
  assert.equal(blockedBySuccess.recovered, false);
  assert.equal(blockedBySuccess.reason, 'timed-out-operation-late-success');
  assert.equal(clearSuccess.clearedCount, 1);
  assert.equal(blockedByFailure.recovered, false);
  assert.equal(blockedByFailure.reason, 'timed-out-operation-late-failure');
  assert.equal(clearFailure.clearedCount, 1);
  assert.equal(recoveredAfterClears.recovered, true);
  assert.equal(recoveredSchedule.accepted, true);
  assert.equal(recoveredResult?.ok, true);
  assert.equal(recoveredVerify?.ok, true);
  assert.equal(finalSnapshot.executor.successfulTimedOutOperationCount, 0);
  assert.equal(finalSnapshot.executor.failedTimedOutOperationCount, 0);
  assert.equal(validation.ok, true);
  for (const kind of ['storage-lane:timed-out-quarantine-export','storage-lane:timed-out-quarantine-import','storage-lane:provider-healthy-rejected','storage-lane:late-provider-success','storage-lane:late-provider-failure','block-store-lane:recover-timed-out-successes-blocked','block-store-lane:recover-timed-out-failures-blocked','block-store-lane:recover-settled']) assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-handoff-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that late-provider timeout quarantine can be exported, imported into a fresh storage-lane adapter, marks the imported lane unhealthy, blocks direct markHealthy bypass, and recovers only after reviewed/scoped success and failure clears.', observations: { successAccepted, successTimeout, successPresentBeforeRelease, successSettled, successVerify, successLedger, failureAccepted, failureTimeout, failurePresentBeforeRelease, failureSettled, failureVerify, failureLedger, combinedLedger, importResult, importedSnapshot, storageLaneAfterImport, rejectedAfterImport, directMarkHealthyRejected, blockedBySuccess, clearSuccess, blockedByFailure, clearFailure, recoveredAfterClears, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, traceKinds }, claimsChecked: ['Timed-out late success and late failure quarantine can be exported as a ledger', 'A fresh adapter importing the ledger marks the storage lane unhealthy', 'Direct markHealthy is rejected while imported timed-out-operation quarantine remains active', 'Recovery remains blocked by late-success then late-failure quarantine until each is reviewed and scoped', 'Recovered writes verify after reviewed quarantine clearing'], nonClaims: ['This is browser-light release evidence; browser OPFS/Web Locks handoff proof is separate.', 'Quarantine handoff is not automatic persistence, provider cancellation, rollback, no-mutation, exactly-once, durability, quota, eviction, cross-browser, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-handoff-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed quarantine handoff proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_handoff_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
