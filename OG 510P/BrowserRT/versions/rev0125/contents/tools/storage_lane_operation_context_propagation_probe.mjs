#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, createWebLockGuardedBlockStore, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-operation-context-propagation-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-OPERATION-CONTEXT-PROPAGATION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const bytes = (value) => value instanceof Uint8Array ? new Uint8Array(value) : new TextEncoder().encode(String(value));

function makeImmediateLocks() {
  const calls = [];
  return {
    calls,
    async request(name, options, callback) {
      calls.push({ name, mode: options?.mode ?? 'exclusive', timeoutMs: options?.signal ? 'signal-present' : null, hasSignal: Boolean(options?.signal) });
      return await callback({ name, mode: options?.mode ?? 'exclusive' });
    },
    async query() { return { held: [], pending: [] }; }
  };
}

function makeRecordingStore() {
  const records = new Map();
  const calls = [];
  const record = (method, options) => calls.push({ method, operationTimeoutMs: options?.operationTimeoutMs ?? null, hasSignal: Boolean(options?.signal || options?.abortSignal), optionKeys: Object.keys(options || {}).sort() });
  return {
    name: 'synthetic-context-recording-store', provider: 'synthetic-context-provider-v0', prefix: 'synthetic/context', calls,
    async put(payload, fields = {}, options = {}) {
      record('put', options);
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`;
      records.set(digest, body);
      return Object.freeze({ ref: Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null, label: fields.label ?? null }), digest, hash, bytes: body.byteLength, duplicate: false, path: null });
    },
    async get(ref, options = {}) { record('get', options); const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing ${digest}`); return new Uint8Array(row); },
    async has(ref, options = {}) { record('has', options); const digest = typeof ref === 'string' ? ref : ref?.digest; return records.has(digest); },
    async verify(ref, options = {}) { record('verify', options); const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); return Object.freeze({ digest, present: Boolean(row), ok: Boolean(row), bytes: row?.byteLength ?? 0, path: null }); },
    async delete(ref, options = {}) { record('delete', options); const digest = typeof ref === 'string' ? ref : ref?.digest; return records.delete(digest); },
    async estimate(options = {}) { record('estimate', options); return Object.freeze({ quota: null, usage: Array.from(records.values()).reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest(options = {}) { record('cleanupForTest', options); const had = records.size > 0; records.clear(); return had; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, prefix: this.prefix, blockCount: records.size, callCount: calls.length, calls: calls.slice() }); }
  };
}

function callMap(calls) {
  const out = new Map();
  for (const call of calls) out.set(call.method, call);
  return out;
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const locks = makeImmediateLocks();
  const recordingStore = makeRecordingStore();
  const guarded = createWebLockGuardedBlockStore({ store: recordingStore, locks, lockPrefix: `${REVISION}:context`, lockName: 'operation-context', label: `${REVISION}-context-guard`, trace, lockTimeoutMs: 77 });
  const scheduler = createCrossLaneScheduler({ label: `${REVISION}-context-propagation-scheduler`, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-context-propagation-adapter`, store: guarded, scheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 111 });

  const schedulePut = adapter.schedulePut(`BrowserRT ${REVISION} context propagation payload`, { id: 'ctx-put', label: 'ctx-put', operationTimeoutMs: 222 });
  const putDrain = await adapter.drain({ maxSteps: 2 });
  const putResult = putDrain.results.find((row) => row.opId === 'ctx-put');
  const ref = putResult?.result?.ref;
  const scheduled = [
    schedulePut,
    adapter.scheduleGet(ref, { id: 'ctx-get', operationTimeoutMs: 333 }),
    adapter.scheduleHas(ref, { id: 'ctx-has', operationTimeoutMs: 444 }),
    adapter.scheduleVerify(ref, { id: 'ctx-verify', operationTimeoutMs: 555 }),
    adapter.scheduleEstimate({ id: 'ctx-estimate', operationTimeoutMs: 666 }),
    adapter.scheduleDelete(ref, { id: 'ctx-delete', operationTimeoutMs: 777 }),
    adapter.scheduleCleanupForTest({ id: 'ctx-cleanup', operationTimeoutMs: 888 })
  ];
  const remainingDrain = await adapter.drain({ maxSteps: 10 });
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const callsByMethod = callMap(recordingStore.calls);
  const expectedTimeouts = { put: 222, get: 333, has: 444, verify: 555, estimate: 666, delete: 777, cleanupForTest: 888 };
  const observedTimeouts = Object.fromEntries([...callsByMethod.entries()].map(([method, call]) => [method, call.operationTimeoutMs]));
  for (const [method, expected] of Object.entries(expectedTimeouts)) assert.equal(observedTimeouts[method], expected, `${method} operationTimeoutMs should propagate`);
  for (const accepted of scheduled) assert.equal(accepted.accepted, true, `${accepted.opId || accepted.adapterOp} should be accepted`);
  assert.equal(putResult?.ok, true);
  assert.equal(validation.ok, true);
  assert.ok(locks.calls.length >= Object.keys(expectedTimeouts).length, 'Web Lock wrapper should run every store operation through a lock');
  const traceKinds = trace.kinds();
  for (const kind of ['block-store-lane:op-start', 'block-store-lane:op-complete', 'storage:opfs-web-lock-guard-op-start', 'storage:opfs-web-lock-guard-op-complete']) assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-operation-context-propagation-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier proof that BlockStoreLaneAdapter passes storage-lane operation context into WebLockGuardedBlockStore and then into provider calls.',
    observations: { putResult, remainingDrain, expectedTimeouts, observedTimeouts, recordingCalls: recordingStore.calls, lockCalls: locks.calls, finalSnapshot, traceKinds },
    claimsChecked: ['BlockStoreLaneAdapter forwards the executor context to the scheduled provider callback.', 'WebLockGuardedBlockStore forwards provider options to put/get/has/verify/estimate/delete/cleanupForTest.', 'operationTimeoutMs reaches the provider; operation timeout remains separate from Web Lock acquisition timeout.'],
    nonClaims: ['This release-tier proof uses synthetic locks and a synthetic provider; browser OPFS/Web Locks proof is separate.', 'Context propagation is not provider cancellation, rollback, durability, quota, eviction, throughput, latency, SLO, or production-readiness evidence.']
  };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-operation-context-propagation-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed context-propagation proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_operation_context_propagation_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
