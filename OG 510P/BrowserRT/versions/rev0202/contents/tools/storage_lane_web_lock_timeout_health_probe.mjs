#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot } from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-WEB-LOCK-TIMEOUT-HEALTH-PROBE.json`;
const TASK_ID = 'scheduler:storage-lane-web-lock-timeout-health-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function webLockTimeoutError(bytes) {
  const error = new Error('synthetic Web Lock acquisition timeout for storage-lane health policy');
  error.name = 'BrowserRTWebLockError';
  error.code = 'BRT_WEB_LOCK_TIMEOUT';
  error.detail = {
    code: 'BRT_WEB_LOCK_TIMEOUT',
    name: 'AbortError',
    message: 'The guarded provider could not acquire its Web Lock before timeout.',
    context: { store: 'synthetic-web-lock-guarded-store', bytes }
  };
  return error;
}

function makeSyntheticGuardedStore({ failFirst = true, trace = null } = {}) {
  const state = { fail: failFirst, puts: 0, failures: 0, bytes: 0, records: [] };
  return {
    name: 'synthetic-web-lock-guarded-store',
    provider: 'web-lock-guarded:opfs-async-block-store-v0',
    async put(payload, fields = {}) {
      const bytes = payload?.byteLength ?? payload?.length ?? 0;
      state.puts += 1;
      if (state.fail) {
        state.failures += 1;
        trace?.emit('synthetic-web-lock-guarded-store:timeout', { bytes, label: fields.label ?? null });
        throw webLockTimeoutError(bytes);
      }
      state.bytes += bytes;
      const ref = Object.freeze({ kind: 'block', id: `block:synthetic-web-lock:${state.puts}`, digest: `synthetic-web-lock:${state.puts}`, hash: `synthetic-web-lock-${state.puts}`, backend: this.provider, bytes, path: null });
      const row = Object.freeze({ ref, digest: ref.digest, hash: ref.hash, bytes, duplicate: false, path: null });
      state.records.push(row);
      trace?.emit('synthetic-web-lock-guarded-store:put', { bytes, digest: ref.digest, label: fields.label ?? null });
      return row;
    },
    async get(ref) { return new Uint8Array(Number(ref?.bytes || 0)); },
    async has() { return true; },
    async verify(ref) { return Object.freeze({ digest: ref?.digest || String(ref), present: true, ok: true, bytes: ref?.bytes ?? 0, path: null }); },
    async delete() { return true; },
    async estimate() { return Object.freeze({ quota: null, usage: state.bytes, usageDetails: { synthetic: state.bytes } }); },
    async cleanupForTest() { state.records.length = 0; state.bytes = 0; return true; },
    recover(reason = 'web-lock-holder-drained') { state.fail = false; trace?.emit('synthetic-web-lock-guarded-store:recover', { reason }); return { recovered: true, reason }; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, prefix: 'synthetic/web-lock-guarded', stats: { ...state, records: state.records.length } }); }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const scheduler = createCrossLaneScheduler({
    label: `${REVISION}-web-lock-timeout-health-scheduler`,
    trace,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const store = makeSyntheticGuardedStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-web-lock-timeout-health-adapter`, store, scheduler, trace, lane: 'storage' });

  const firstAccepted = adapter.schedulePut(new Uint8Array(128), { id: 'timed-out-guarded-put', label: 'synthetic-web-lock-timeout-put', priority: 'user-visible' });
  const firstDrain = await adapter.drain({ maxSteps: 2 });
  const firstResult = firstDrain.results.find((row) => row.opId === 'timed-out-guarded-put');
  const afterFailure = adapter.snapshot();
  const storageLaneAfterFailure = afterFailure.executor.scheduler.lanes.find((lane) => lane.id === 'storage');

  const rejectedAfterTimeout = adapter.schedulePut(new Uint8Array(16), { id: 'post-timeout-put', label: 'should-reject-while-lock-unhealthy' });
  const routedSnapshot = adapter.scheduleSnapshot({ id: 'fallback-snapshot-after-lock-timeout', fallbackLanes: ['maintenance'], priority: 'background' });
  const routeDrain = await adapter.drain({ maxSteps: 4 });
  const routeResult = routeDrain.results.find((row) => row.opId === 'fallback-snapshot-after-lock-timeout');

  store.recover('web-lock-holder-drained');
  const recoveryLane = adapter.markHealthy('storage', 'web-lock-holder-drained');
  const recoveredPut = adapter.schedulePut(new Uint8Array(32), { id: 'recovered-web-lock-put', label: 'post-lock-drain-write', priority: 'user-visible' });
  const recoveryDrain = await adapter.drain({ maxSteps: 4 });
  const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'recovered-web-lock-put');
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();

  assert.equal(firstAccepted.accepted, true);
  assert.equal(firstResult?.ok, false);
  assert.equal(firstResult?.error?.code, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(firstResult?.error?.storageDisposition, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(storageLaneAfterFailure?.healthy, false);
  assert.equal(storageLaneAfterFailure?.healthReason, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(afterFailure.executor.stats.laneHealthFailures, 1);
  assert.equal(rejectedAfterTimeout.accepted, false);
  assert.equal(rejectedAfterTimeout.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(rejectedAfterTimeout.scheduler.noMutation, true);
  assert.equal(routedSnapshot.accepted, true);
  assert.equal(routedSnapshot.scheduler.disposition, 'accepted-routed');
  assert.equal(routedSnapshot.scheduler.lane, 'maintenance');
  assert.equal(routeResult?.ok, true);
  assert.equal(recoveryLane.healthy, true);
  assert.equal(recoveredPut.accepted, true);
  assert.equal(recoveredResult?.ok, true);
  assert.equal(validation.ok, true);
  for (const kind of ['storage-lane:provider-unhealthy', 'crosslane:lane-unhealthy', 'crosslane:reject', 'crosslane:routed-enqueue', 'crosslane:lane-healthy', 'synthetic-web-lock-guarded-store:recover']) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-web-lock-timeout-health-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Fast release-tier proof that a WebLockGuardedBlockStore acquisition timeout is treated as storage-lane provider-health/backpressure: BRT_WEB_LOCK_TIMEOUT marks storage unhealthy, follow-on writes reject without mutation, maintenance fallback can still run, and explicit recovery reopens the lane.',
    observations: {
      firstAccepted,
      firstResult,
      storageLaneAfterFailure,
      rejectedAfterTimeout,
      routedSnapshot,
      routeResult,
      recoveryLane,
      recoveredPut,
      recoveredResult,
      finalSnapshot,
      validation,
      traceKinds,
      normalizedTrace: trace.snapshot().map((event) => ({ kind: event.kind, opId: event.opId, lane: event.lane, code: event.code, storageDisposition: event.storageDisposition, reason: event.reason, disposition: event.disposition, routeReason: event.routeReason })).filter((event) => event.kind)
    },
    claimsChecked: [
      'BRT_WEB_LOCK_TIMEOUT is now a storage-lane health failure when it escapes a guarded storage provider',
      'a guarded-provider timeout marks the requested storage lane unhealthy with the provider code as reason',
      'follow-on storage writes reject without queue mutation while the lane remains unhealthy',
      'maintenance fallback routing remains usable while the storage lane is unhealthy',
      'explicit recovery marks the storage lane healthy and permits a later write'
    ],
    nonClaims: [
      'Synthetic release-tier provider timeout proof only; browser Web Locks behavior is covered by explicit browser proofs.',
      'No automatic recovery, fairness, starvation-freedom, cross-browser, OPFS durability, quota, eviction, fsync, or production exactly-once claim.',
      'BRT_WEB_LOCK_ABORTED caller cancellation is not claimed as provider-health failure in this slice.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-web-lock-timeout-health-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed synthetic storage-lane Web Lock timeout proof is not a browser lifecycle claim.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_web_lock_timeout_health_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
