#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot } from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-OPFS-ERROR-HEALTH-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function opfsQuotaError(bytes) {
  const error = new Error('synthetic OPFS quota exceeded for storage-lane health policy');
  error.name = 'BrowserRTOpfsBlockStoreError';
  error.code = 'BRT_OPFS_QUOTA_EXCEEDED';
  error.detail = {
    code: 'BRT_OPFS_QUOTA_EXCEEDED',
    name: 'QuotaExceededError',
    message: 'The origin quota was exceeded while writing an OPFS block.',
    domCode: null,
    context: { store: 'synthetic-opfs-store', bytes }
  };
  return error;
}

function makeSyntheticOpfsStore({ failFirst = true, trace = null } = {}) {
  const state = { fail: failFirst, puts: 0, failures: 0, bytes: 0, records: [] };
  return {
    name: 'synthetic-opfs-store',
    provider: 'opfs-async-block-store-v0',
    async put(payload, fields = {}) {
      const bytes = payload?.byteLength ?? payload?.length ?? 0;
      state.puts += 1;
      if (state.fail) {
        state.failures += 1;
        trace?.emit('synthetic-opfs-store:quota-error', { bytes, label: fields.label ?? null });
        throw opfsQuotaError(bytes);
      }
      state.bytes += bytes;
      const ref = Object.freeze({ kind: 'block', id: `block:synthetic:${state.puts}`, digest: `synthetic:${state.puts}`, hash: `synthetic-${state.puts}`, backend: this.provider, bytes, path: null });
      const row = Object.freeze({ ref, digest: ref.digest, hash: ref.hash, bytes, duplicate: false, path: null });
      state.records.push(row);
      trace?.emit('synthetic-opfs-store:put', { bytes, digest: ref.digest, label: fields.label ?? null });
      return row;
    },
    async get(ref) { return new Uint8Array(Number(ref?.bytes || 0)); },
    async has() { return true; },
    async verify(ref) { return Object.freeze({ digest: ref?.digest || String(ref), present: true, ok: true, bytes: ref?.bytes ?? 0, path: null }); },
    async delete() { return true; },
    async estimate() { return Object.freeze({ quota: 786432, usage: state.bytes, usageDetails: { synthetic: state.bytes } }); },
    async cleanupForTest() { state.records.length = 0; state.bytes = 0; return true; },
    recover(reason = 'synthetic-cleanup-complete') { state.fail = false; trace?.emit('synthetic-opfs-store:recover', { reason }); return { recovered: true, reason }; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, prefix: 'synthetic/opfs', stats: { ...state, records: state.records.length } }); }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const scheduler = createCrossLaneScheduler({
    label: `${REVISION}-opfs-error-health-scheduler`,
    trace,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const store = makeSyntheticOpfsStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-opfs-error-health-adapter`, store, scheduler, trace, lane: 'storage' });

  const rejectedPayload = new Uint8Array(64 * 1024);
  const firstAccepted = adapter.schedulePut(rejectedPayload, { id: 'quota-put', label: 'synthetic-quota-put', priority: 'user-visible' });
  const firstDrain = await adapter.drain({ maxSteps: 2 });
  const firstResult = firstDrain.results.find((row) => row.opId === 'quota-put');
  const afterFailure = adapter.snapshot();
  const storageLaneAfterFailure = afterFailure.executor.scheduler.lanes.find((lane) => lane.id === 'storage');

  const rejectedAfterUnhealthy = adapter.schedulePut(new Uint8Array(16), { id: 'post-quota-put', label: 'should-reject-while-unhealthy' });
  const routedSnapshot = adapter.scheduleSnapshot({ id: 'fallback-snapshot', fallbackLanes: ['maintenance'], priority: 'background' });
  const routeDrain = await adapter.drain({ maxSteps: 4 });
  const routeResult = routeDrain.results.find((row) => row.opId === 'fallback-snapshot');

  store.recover('quota-space-reclaimed');
  const recoveryLane = adapter.markHealthy('storage', 'quota-space-reclaimed');
  const recoveredPut = adapter.schedulePut(new Uint8Array(32), { id: 'recovered-put', label: 'post-cleanup-write', priority: 'user-visible' });
  const recoveryDrain = await adapter.drain({ maxSteps: 4 });
  const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'recovered-put');
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();

  assert.equal(firstAccepted.accepted, true);
  assert.equal(firstResult?.ok, false);
  assert.equal(firstResult?.error?.code, 'BRT_OPFS_QUOTA_EXCEEDED');
  assert.equal(firstResult?.error?.storageDisposition, 'BRT_OPFS_QUOTA_EXCEEDED');
  assert.equal(storageLaneAfterFailure?.healthy, false);
  assert.equal(storageLaneAfterFailure?.healthReason, 'BRT_OPFS_QUOTA_EXCEEDED');
  assert.equal(afterFailure.executor.stats.laneHealthFailures, 1);
  assert.equal(rejectedAfterUnhealthy.accepted, false);
  assert.equal(rejectedAfterUnhealthy.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(rejectedAfterUnhealthy.scheduler.noMutation, true);
  assert.equal(routedSnapshot.accepted, true);
  assert.equal(routedSnapshot.scheduler.disposition, 'accepted-routed');
  assert.equal(routedSnapshot.scheduler.lane, 'maintenance');
  assert.equal(routeResult?.ok, true);
  assert.equal(recoveryLane.healthy, true);
  assert.equal(recoveredPut.accepted, true);
  assert.equal(recoveredResult?.ok, true);
  assert.equal(validation.ok, true);
  for (const kind of ['storage-lane:provider-unhealthy', 'crosslane:lane-unhealthy', 'crosslane:reject', 'crosslane:routed-enqueue', 'crosslane:lane-healthy', 'synthetic-opfs-store:recover']) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-storage-lane-opfs-error-health-proof`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    durationMs: Math.round(performance.now() - started),
    purpose: 'Fast release-tier proof that OPFS provider error codes are treated as storage-lane health failures: quota error marks the storage lane unhealthy, new storage writes reject without mutation, maintenance fallback can still run, and explicit recovery reopens the lane.',
    observations: {
      firstAccepted,
      firstResult,
      storageLaneAfterFailure,
      rejectedAfterUnhealthy,
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
      'BRT_OPFS_QUOTA_EXCEEDED is now a storage-lane health failure, not merely an opaque provider error',
      'a quota failure marks the requested storage lane unhealthy with the provider code as reason',
      'follow-on storage writes reject without queue mutation while the lane remains unhealthy',
      'maintenance fallback routing remains usable while the storage lane is unhealthy',
      'explicit recovery marks the storage lane healthy and permits a later write'
    ],
    nonClaims: [
      'Synthetic release-tier provider error proof only; it does not exercise browser OPFS or CDP quota pressure.',
      'No durability, organic eviction, quota-size, or throughput claim.',
      'Recovery is explicit/manual in this slice; no automatic browser storage reclamation claim.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-opfs-error-health-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_opfs_error_health_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
