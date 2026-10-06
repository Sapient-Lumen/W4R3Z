#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot } from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-WEB-LOCK-READ-TIMEOUT-NONPOISON-PROBE.json`;
const TASK_ID = 'scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function webLockReadTimeoutError(op = 'verify') {
  const error = new Error(`synthetic Web Lock acquisition timeout for read-only ${op}`);
  error.name = 'BrowserRTWebLockError';
  error.code = 'BRT_WEB_LOCK_TIMEOUT';
  error.detail = {
    label: 'synthetic-read-timeout-guard:coordinator',
    name: 'browserrt:read-timeout-nonpoison:lock',
    mode: 'shared',
    timeoutMs: 25,
    metadata: {
      component: 'WebLockGuardedBlockStore',
      op,
      store: 'synthetic-web-lock-read-timeout-store',
      provider: 'web-lock-guarded:synthetic-opfs-block-store',
      lockName: 'browserrt:read-timeout-nonpoison:lock',
      timeoutMs: 25
    },
    causeName: 'AbortError',
    causeMessage: 'The guarded provider could not acquire its shared Web Lock before timeout.'
  };
  return error;
}

function makeSyntheticReadTimeoutStore({ trace = null } = {}) {
  const state = { verifyShouldTimeout: true, verifies: 0, puts: 0, bytes: 0, records: new Map() };
  return {
    name: 'synthetic-web-lock-read-timeout-store',
    provider: 'web-lock-guarded:synthetic-opfs-block-store',
    async put(payload, fields = {}) {
      const bytes = payload?.byteLength ?? payload?.length ?? 0;
      state.puts += 1;
      state.bytes += bytes;
      const digest = `synthetic-read-timeout:${state.puts}:${bytes}`;
      const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash: digest, backend: this.provider, bytes, path: null });
      const row = Object.freeze({ ref, digest, hash: digest, bytes, duplicate: false, path: null, label: fields.label ?? null });
      state.records.set(digest, row);
      trace?.emit('synthetic-web-lock-read-timeout-store:put', { digest, bytes, label: fields.label ?? null });
      return row;
    },
    async get(ref) { const digest = ref?.digest || String(ref); return new Uint8Array(Number(state.records.get(digest)?.bytes || 0)); },
    async has(ref) { return state.records.has(ref?.digest || String(ref)); },
    async verify(ref) {
      const digest = ref?.digest || String(ref);
      state.verifies += 1;
      if (state.verifyShouldTimeout) {
        state.verifyShouldTimeout = false;
        trace?.emit('synthetic-web-lock-read-timeout-store:verify-timeout', { digest });
        throw webLockReadTimeoutError('verify');
      }
      const row = state.records.get(digest);
      trace?.emit('synthetic-web-lock-read-timeout-store:verify', { digest, present: Boolean(row) });
      return Object.freeze({ digest, present: Boolean(row), ok: Boolean(row), bytes: row?.bytes ?? 0, path: null });
    },
    async delete(ref) { const digest = ref?.digest || String(ref); const deleted = state.records.delete(digest); return Object.freeze({ deleted, digest }); },
    async estimate() { return Object.freeze({ quota: null, usage: state.bytes, usageDetails: { synthetic: state.bytes } }); },
    async cleanupForTest() { state.records.clear(); state.bytes = 0; return true; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, prefix: 'synthetic/read-timeout-nonpoison', stats: { puts: state.puts, verifies: state.verifies, bytes: state.bytes, records: state.records.size, verifyShouldTimeout: state.verifyShouldTimeout } }); }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const scheduler = createCrossLaneScheduler({
    label: `${REVISION}-read-timeout-nonpoison-scheduler`,
    trace,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const store = makeSyntheticReadTimeoutStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-read-timeout-nonpoison-adapter`, store, scheduler, trace, lane: 'storage' });

  const seedAccepted = adapter.schedulePut(new Uint8Array(64), { id: 'seed-block-put', label: 'seed-before-read-timeout', priority: 'user-visible' });
  const seedDrain = await adapter.drain({ maxSteps: 3 });
  const seedResult = seedDrain.results.find((row) => row.opId === 'seed-block-put');
  const ref = seedResult?.result?.ref;

  const verifyAccepted = adapter.scheduleVerify(ref, { id: 'shared-verify-timeout', priority: 'user-visible' });
  const verifyDrain = await adapter.drain({ maxSteps: 3 });
  const verifyResult = verifyDrain.results.find((row) => row.opId === 'shared-verify-timeout');
  const afterReadTimeout = adapter.snapshot();
  const laneAfterReadTimeout = afterReadTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage');

  const followOnAccepted = adapter.schedulePut(new Uint8Array(32), { id: 'follow-on-write-after-read-timeout', label: 'should-still-accept', priority: 'user-visible' });
  const followOnDrain = await adapter.drain({ maxSteps: 4 });
  const followOnResult = followOnDrain.results.find((row) => row.opId === 'follow-on-write-after-read-timeout');

  const verifyAgainAccepted = adapter.scheduleVerify(ref, { id: 'verify-after-nonpoison', priority: 'user-visible' });
  const verifyAgainDrain = await adapter.drain({ maxSteps: 3 });
  const verifyAgainResult = verifyAgainDrain.results.find((row) => row.opId === 'verify-after-nonpoison');
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();

  assert.equal(seedAccepted.accepted, true);
  assert.equal(seedResult?.ok, true);
  assert.ok(ref?.digest, 'seed ref must have digest');
  assert.equal(verifyAccepted.accepted, true);
  assert.equal(verifyResult?.ok, false);
  assert.equal(verifyResult?.error?.code, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(laneAfterReadTimeout?.healthy, true, 'read-only Web Lock timeout must not poison storage lane');
  assert.equal(afterReadTimeout.executor.stats.laneHealthFailures, 0, 'read timeout should not increment laneHealthFailures');
  assert.equal(followOnAccepted.accepted, true, 'follow-on write should still be admitted after read timeout');
  assert.equal(followOnResult?.ok, true);
  assert.equal(verifyAgainAccepted.accepted, true);
  assert.equal(verifyAgainResult?.ok, true);
  assert.equal(validation.ok, true);
  for (const kind of ['synthetic-web-lock-read-timeout-store:verify-timeout', 'storage-lane:error', 'synthetic-web-lock-read-timeout-store:put', 'storage-lane:complete']) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }
  assert.equal(traceKinds.includes('storage-lane:provider-unhealthy'), false, 'read timeout should not emit provider-unhealthy');

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-web-lock-read-timeout-nonpoison-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Fast release-tier proof that a shared/read-only WebLockGuardedBlockStore timeout is a visible operation failure but does not poison the storage lane or block later admitted mutations.',
    observations: { seedAccepted, seedResult, verifyAccepted, verifyResult, laneAfterReadTimeout, followOnAccepted, followOnResult, verifyAgainAccepted, verifyAgainResult, finalSnapshot, validation, traceKinds, normalizedTrace: trace.snapshot().map((event) => ({ kind: event.kind, opId: event.opId, lane: event.lane, opKind: event.opKind, code: event.code, storageDisposition: event.storageDisposition, reason: event.reason, disposition: event.disposition })).filter((event) => event.kind) },
    claimsChecked: [
      'BRT_WEB_LOCK_TIMEOUT from WebLockGuardedBlockStore.verify() remains a failed operation with code evidence',
      'read-only/shared Web Lock timeouts do not mark the storage lane unhealthy',
      'laneHealthFailures does not increment for read-only Web Lock timeouts',
      'follow-on writes remain admissible and executable after read-only lock timeout',
      'later reads can verify once the synthetic contention clears'
    ],
    nonClaims: [
      'Synthetic release-tier proof only; managed Chromium OPFS/Web Locks behavior is covered by browser:opfs-web-lock-read-timeout-nonpoison-proof.',
      'No fairness, starvation-freedom, cross-browser, OPFS durability, quota, eviction, fsync, or production-readiness claim.',
      'Mutating Web Lock timeouts still remain provider-health/backpressure failures in separate storage-lane proofs.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-web-lock-read-timeout-nonpoison-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed synthetic read-timeout nonpoison proof is not a browser lifecycle claim.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_web_lock_read_timeout_nonpoison_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
