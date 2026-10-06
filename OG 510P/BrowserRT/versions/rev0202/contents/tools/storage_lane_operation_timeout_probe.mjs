#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-operation-timeout-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-OPERATION-TIMEOUT-PROBE.json`;
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

function makeSlowCommittingStore({ trace = null } = {}) {
  const release = deferred();
  const records = new Map();
  const state = { puts: 0, committedBeforeRelease: 0, released: false, releaseReason: null, lateCompletions: 0 };
  return {
    name: 'synthetic-slow-committing-block-store',
    provider: 'synthetic-slow-commit-provider-v0',
    release,
    state,
    async put(payload, fields = {}) {
      const body = bytes(payload);
      const hash = await digestBytesHex(body);
      const digest = `sha256:${hash}`;
      state.puts += 1;
      records.set(digest, body);
      state.committedBeforeRelease += 1;
      trace?.emit('synthetic-slow-store:committed-before-release', { digest, bytes: body.byteLength, label: fields.label ?? null });
      const reason = await release.promise;
      state.released = true;
      state.releaseReason = reason || 'released';
      state.lateCompletions += 1;
      const ref = Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null });
      trace?.emit('synthetic-slow-store:resolved-after-release', { digest, bytes: body.byteLength, reason });
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, path: null, releasedAfterTimeout: true });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); return Object.freeze({ digest, present: Boolean(row), ok: Boolean(row), bytes: row?.byteLength ?? 0, path: null }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: Array.from(records.values()).reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const scheduler = createCrossLaneScheduler({
    label: `${REVISION}-operation-timeout-scheduler`,
    trace,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const store = makeSlowCommittingStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-operation-timeout-adapter`, store, scheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 120 });
  const payload = `BrowserRT ${REVISION} storage lane operation timeout payload`;
  const timeoutDigest = `sha256:${await digestBytesHex(bytes(payload))}`;

  const accepted = adapter.schedulePut(payload, { id: 'slow-put-times-out-after-provider-commit', label: 'slow-provider-op', priority: 'user-visible' });
  const drain = await adapter.drain({ maxSteps: 2 });
  const timeoutResult = drain.results.find((row) => row.opId === 'slow-put-times-out-after-provider-commit');
  const afterTimeout = adapter.snapshot();
  const storageLane = afterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const committedButUnreturned = await store.has(timeoutDigest);
  const adapterResultAfterTimeout = adapter.result('slow-put-times-out-after-provider-commit') ?? null;

  const rejectedWhileUnhealthy = adapter.schedulePut('must-not-queue-while-unhealthy', { id: 'reject-while-operation-timeout-unhealthy' });
  const maintenanceSnapshot = adapter.scheduleSnapshot({ id: 'maintenance-snapshot-after-operation-timeout', fallbackLanes: ['maintenance'], priority: 'background' });
  const maintenanceDrain = await adapter.drain({ maxSteps: 3 });
  const maintenanceResult = maintenanceDrain.results.find((row) => row.opId === 'maintenance-snapshot-after-operation-timeout');

  store.release.resolve('test-release-after-timeout');
  const settledAfterLateRelease = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const verifyAfterLateRelease = await store.verify(timeoutDigest);
  const quarantineAfterLateRelease = adapter.timedOutOperationQuarantine('storage');
  const healthyRejectedBeforeClear = adapter.markHealthy('storage', 'operation-timeout-investigated-before-quarantine-review');
  const lateSuccessReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opId: 'slow-put-times-out-after-provider-commit', reviewer: 'legacy-compatible-release-probe', reviewToken: `${REVISION}-operation-timeout-late-success-review`, reason: 'operation-timeout-proof-reviewed-late-success' });
  const clearedLateSuccess = adapter.clearSuccessfulTimedOutOperations({ reviewManifest: lateSuccessReview, requireReviewFingerprint: true, reason: 'operation-timeout-proof-reviewed-late-success' });
  const healthy = adapter.markHealthy('storage', 'operation-timeout-investigated');
  const recoveredSchedule = adapter.schedulePut('BrowserRT operation timeout recovered write', { id: 'operation-timeout-recovered-put', priority: 'user-visible', label: 'recovered-after-timeout' });
  const recoveryDrain = await adapter.drain({ maxSteps: 3 });
  const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'operation-timeout-recovered-put');
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();

  assert.equal(accepted.accepted, true);
  assert.equal(timeoutResult?.ok, false);
  assert.equal(timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(timeoutResult?.error?.storageDisposition, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(afterTimeout.executor.stats.operationTimeouts, 1);
  assert.equal(storageLane?.healthy, false);
  assert.equal(storageLane?.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(committedButUnreturned, true, 'operation timeout is not a provider cancellation/no-mutation guarantee');
  assert.equal(adapterResultAfterTimeout, null, 'timed-out operation should not publish an adapter result');
  assert.equal(rejectedWhileUnhealthy.accepted, false);
  assert.equal(rejectedWhileUnhealthy.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(rejectedWhileUnhealthy.scheduler.noMutation, true);
  assert.equal(maintenanceSnapshot.accepted, true);
  assert.equal(maintenanceSnapshot.scheduler.lane, 'maintenance');
  assert.equal(maintenanceResult?.ok, true);
  assert.equal(settledAfterLateRelease.ok, true);
  assert.equal(verifyAfterLateRelease.ok, true);
  assert.equal(quarantineAfterLateRelease.successfulTimedOutOperationCount, 1, 'late success after operation timeout should be quarantined before reopening');
  assert.equal(healthyRejectedBeforeClear.healthy, false, 'direct markHealthy should not bypass late-success quarantine');
  assert.equal(healthyRejectedBeforeClear.disposition, 'rejected-timed-out-operation-quarantine');
  assert.equal(clearedLateSuccess.clearedCount, 1);
  assert.equal(healthy.healthy, true);
  assert.equal(recoveredSchedule.accepted, true);
  assert.equal(recoveredResult?.ok, true);
  assert.equal(validation.ok, true);
  for (const kind of ['storage-lane:operation-timeout-arm', 'storage-lane:operation-timeout', 'storage-lane:provider-unhealthy', 'crosslane:lane-unhealthy', 'crosslane:reject', 'crosslane:routed-enqueue', 'crosslane:lane-healthy']) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-operation-timeout-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier proof that dispatched storage-lane work can be bounded by an operation timeout: the executor returns BRT_STORAGE_OPERATION_TIMEOUT, marks the lane unhealthy, rejects follow-on writes without queue mutation, still allows maintenance fallback, and later explicit recovery permits new work. It also proves the non-claim that operation timeout is not provider cancellation.',
    observations: { accepted, timeoutResult, storageLane, committedButUnreturned, timeoutDigest, adapterResultAfterTimeout, rejectedWhileUnhealthy, maintenanceSnapshot, maintenanceResult, settledAfterLateRelease, verifyAfterLateRelease, quarantineAfterLateRelease, healthyRejectedBeforeClear, clearedLateSuccess, healthy, recoveredSchedule, recoveredResult, finalSnapshot, validation, traceKinds, normalizedTrace: trace.snapshot().map((event) => ({ kind: event.kind, opId: event.opId, lane: event.lane, code: event.code, reason: event.reason, disposition: event.disposition, timeoutMs: event.timeoutMs, cancellation: event.cancellation })).filter((event) => event.kind) },
    claimsChecked: [
      'StorageLaneExecutor supports a bounded dispatched-operation timeout',
      'BRT_STORAGE_OPERATION_TIMEOUT is a storage-lane health failure that marks the lane unhealthy',
      'timed-out operations do not publish a successful adapter result',
      'follow-on writes reject without queue mutation while the lane is unhealthy',
      'maintenance fallback remains routable while the storage lane is unhealthy',
      'operation timeout is not claimed to cancel or roll back provider work'
    ],
    nonClaims: [
      'Synthetic release-tier provider proof only; browser OPFS/Web Locks coverage is handled by explicit browser proofs.',
      'Operation timeout is not cancellation, rollback, no-mutation, exactly-once, or provider interruption evidence.',
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-operation-timeout-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed operation-timeout proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_operation_timeout_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
