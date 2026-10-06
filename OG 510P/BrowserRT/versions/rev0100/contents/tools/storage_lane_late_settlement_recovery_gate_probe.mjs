#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-late-settlement-recovery-gate-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-LATE-SETTLEMENT-RECOVERY-GATE-PROBE.json`;
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

function makeLateSettlingStore({ trace = null } = {}) {
  const release = deferred();
  const records = new Map();
  const state = { puts: 0, committedBeforeSettle: 0, waitForSettledCalls: 0, released: false, lateCompletions: 0 };
  return {
    name: 'synthetic-late-settling-block-store',
    provider: 'synthetic-late-settle-provider-v0',
    release,
    state,
    async put(payload, fields = {}) {
      const body = bytes(payload);
      const hash = await digestBytesHex(body);
      const digest = `sha256:${hash}`;
      state.puts += 1;
      records.set(digest, body);
      state.committedBeforeSettle += 1;
      trace?.emit('synthetic-late-store:committed-before-settle', { digest, bytes: body.byteLength, label: fields.label ?? null });
      if (fields?.label === 'late-provider-op') {
        const reason = await release.promise;
        state.released = true;
        state.lateCompletions += 1;
        trace?.emit('synthetic-late-store:late-settled', { digest, reason });
      }
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
  const started = performance.now();
  const trace = new TraceLog();
  const scheduler = createCrossLaneScheduler({
    label: `${REVISION}-late-settlement-gate-scheduler`,
    trace,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const store = makeLateSettlingStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-late-settlement-gate-adapter`, store, scheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 35 });
  const payload = `BrowserRT ${REVISION} late-settlement recovery gate payload`;
  const timeoutDigest = `sha256:${await digestBytesHex(bytes(payload))}`;

  const accepted = adapter.schedulePut(payload, { id: 'late-settling-put-times-out', label: 'late-provider-op', priority: 'user-visible' });
  const drain = await adapter.drain({ maxSteps: 2 });
  const timeoutResult = drain.results.find((row) => row.opId === 'late-settling-put-times-out');
  const snapshotAfterTimeout = adapter.snapshot();
  const storageLaneAfterTimeout = snapshotAfterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const committedButUnsettled = await store.has(timeoutDigest);
  const adapterResultAfterTimeout = adapter.result('late-settling-put-times-out') ?? null;

  const rejectedWhileUnhealthy = adapter.schedulePut('must-not-queue-before-settlement', { id: 'reject-while-late-settlement-unhealthy' });
  const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 45, intervalMs: 5, reason: 'late-provider-still-unsettled' });
  const snapshotAfterBlockedRecovery = adapter.snapshot();

  store.release.resolve('release-late-provider-after-blocked-recovery');
  const settledWait = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const verifyAfterLateSettlement = await store.verify(timeoutDigest);
  const adapterResultAfterLateSettlement = adapter.result('late-settling-put-times-out') ?? null;
  const blockedByLateSuccess = await adapter.recoverWhenStoreSettled({ timeoutMs: 500, intervalMs: 5, reason: 'late-provider-success-quarantine' });
  const successfulTimedOutOperations = adapter.successfulTimedOutOperations('storage');
  const successReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opId: 'late-settling-put-times-out', reviewer: 'legacy-compatible-release-probe', reviewToken: 'rev0078-late-settlement-success-review-scoped', reason: 'late-settlement-proof-scoped-success-clear' });
  const clearedSuccessful = adapter.clearSuccessfulTimedOutOperations({ reviewManifest: successReview, requireReviewFingerprint: true, reason: 'late-settlement-proof-scoped-success-clear' });
  const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 500, intervalMs: 5, reason: 'late-provider-settled-recovery-after-scoped-clear' });
  const recoveredSchedule = adapter.schedulePut('BrowserRT late settlement recovered write', { id: 'late-settlement-recovered-put', priority: 'user-visible', label: 'recovered-after-late-settlement' });
  const recoveryDrain = await adapter.drain({ maxSteps: 3 });
  const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'late-settlement-recovered-put');
  const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();

  assert.equal(accepted.accepted, true, 'late-settling operation should schedule');
  assert.equal(timeoutResult?.ok, false, 'late-settling operation should time out');
  assert.equal(timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(snapshotAfterTimeout.executor.unsettledTimedOutOperationCount, 1, 'timed-out provider operation should remain tracked as unsettled');
  assert.equal(snapshotAfterTimeout.executor.stats.unsettledTimedOutOperations, 1);
  assert.equal(snapshotAfterTimeout.executor.stats.operationTimeouts, 1);
  assert.equal(storageLaneAfterTimeout?.healthy, false, 'storage lane should be unhealthy after operation timeout');
  assert.equal(storageLaneAfterTimeout?.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(committedButUnsettled, true, 'operation timeout is not a provider cancellation/no-mutation guarantee');
  assert.equal(adapterResultAfterTimeout, null, 'timed-out operation must not publish a successful adapter result while unsettled');
  assert.equal(rejectedWhileUnhealthy.accepted, false, 'follow-on write should reject while lane unhealthy');
  assert.equal(rejectedWhileUnhealthy.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(rejectedWhileUnhealthy.scheduler.noMutation, true);
  assert.equal(blockedRecovery.recovered, false, 'recovery must block while a timed-out provider operation remains unsettled');
  assert.equal(blockedRecovery.reason, 'timed-out-operation-still-unsettled');
  assert.equal(blockedRecovery.settled.ok, true, 'store coordination itself reports settled; the block must come from late provider settlement');
  assert.equal(blockedRecovery.timeoutSettled.count, 1);
  assert.equal(snapshotAfterBlockedRecovery.executor.unsettledTimedOutOperationCount, 1);
  assert.equal(settledWait.ok, true, 'late provider should settle after explicit release');
  assert.equal(settledWait.count, 0);
  assert.equal(verifyAfterLateSettlement.ok, true, 'provider data written before timeout should verify after late settlement');
  assert.equal(adapterResultAfterLateSettlement, null, 'late provider settlement must not retroactively publish a successful adapter result for the failed scheduler op');
  assert.equal(blockedByLateSuccess.recovered, false, 'rev0073 recovery should block while late provider success remains quarantined');
  assert.equal(blockedByLateSuccess.reason, 'timed-out-operation-late-success');
  assert.equal(successfulTimedOutOperations.length, 1, 'late provider success should be retained until scoped maintenance clear');
  assert.equal(clearedSuccessful.ok, true, 'scoped clear should permit maintenance review to reopen lane');
  assert.equal(clearedSuccessful.clearedCount, 1);
  assert.equal(settledRecovery.recovered, true, 'recovery should succeed after late provider settlement drains and scoped success quarantine is cleared');
  assert.equal(recoveredSchedule.accepted, true, 'new write should schedule after recovery');
  assert.equal(recoveredResult?.ok, true, 'new write should complete after recovery');
  assert.equal(recoveredVerify?.ok, true, 'new write should verify after recovery');
  assert.equal(finalSnapshot.executor.unsettledTimedOutOperationCount, 0);
  assert.equal(finalSnapshot.executor.successfulTimedOutOperationCount, 0);
  assert.equal(finalSnapshot.executor.stats.lateProviderSettlements, 1);
  assert.equal(finalSnapshot.executor.stats.lateProviderSettlementSuccesses, 1);
  assert.equal(validation.ok, true);
  for (const kind of ['storage-lane:operation-timeout-unsettled', 'storage-lane:operation-timeout', 'block-store-lane:recover-timed-out-ops-blocked', 'storage-lane:late-provider-settlement', 'block-store-lane:recover-timed-out-successes-blocked', 'storage-lane:late-provider-successes-cleared', 'block-store-lane:recover-timed-out-ops-settled', 'block-store-lane:recover-settled']) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-late-settlement-recovery-gate-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier proof that a storage-lane operation which times out after provider mutation remains tracked as an unsettled late provider operation: explicit recovery is blocked even when the store coordination surface reports settled, late settlement is recorded, the timed-out operation is not retroactively published as success, and recovery succeeds only after the late provider operation settles.',
    observations: { accepted, timeoutResult, storageLaneAfterTimeout, committedButUnsettled, timeoutDigest, adapterResultAfterTimeout, rejectedWhileUnhealthy, blockedRecovery, snapshotAfterBlockedRecovery, settledWait, verifyAfterLateSettlement, adapterResultAfterLateSettlement, blockedByLateSuccess, successfulTimedOutOperations, clearedSuccessful, settledRecovery, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, validation, traceKinds, normalizedTrace: trace.snapshot().map((event) => ({ kind: event.kind, opId: event.opId, lane: event.lane, code: event.code, reason: event.reason, disposition: event.disposition, timeoutMs: event.timeoutMs, cancellation: event.cancellation, unsettledTimedOutOperationCount: event.unsettledTimedOutOperationCount })).filter((event) => event.kind) },
    claimsChecked: [
      'StorageLaneExecutor tracks timed-out provider operations until late settlement',
      'recoverWhenStoreSettled refuses to reopen the storage lane while timed-out provider work is still unresolved',
      'late provider settlement is traced and, as of rev0073, late success remains quarantined until a scoped maintenance clear',
      'timed-out provider success is not retroactively published as a successful adapter result',
      'later writes can complete after explicit recovery'
    ],
    nonClaims: [
      'Synthetic release-tier provider proof only; managed Chromium OPFS/Web Locks coverage is handled by the browser proof.',
      'Operation timeout remains not cancellation, rollback, no-mutation, exactly-once, or provider interruption evidence.',
      'No automatic recovery, fairness, starvation-freedom, cross-browser behavior, OPFS durability, quota, eviction, fsync, persistent-retention, throughput, latency, SLO, or production-readiness claim.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-late-settlement-recovery-gate-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed late-settlement recovery-gate proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_late_settlement_recovery_gate_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
