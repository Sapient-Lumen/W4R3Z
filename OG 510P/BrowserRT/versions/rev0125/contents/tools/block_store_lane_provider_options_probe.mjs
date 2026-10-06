#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { createDirectoryMutationRecorder, createStorageEstimateRecorder, fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'storage:block-store-lane-provider-options-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BLOCK-STORE-LANE-PROVIDER-OPTIONS-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

function makeScheduler(label, trace) {
  return createCrossLaneScheduler({
    label,
    trace,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
}

function payload(label) {
  return new TextEncoder().encode(`BrowserRT ${REVISION} block-store lane provider options proof ${label}`);
}

function refForHash(hash, bytes = 0, path = null) {
  return Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest: `sha256:${hash}`, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes, path });
}

async function runProviderBudgetRejectCase() {
  const bytes = payload('provider-budget-reject');
  const prefix = `browserrt/${REVISION}/fake-lane-provider-options/provider-budget-reject`;
  const recorder = createDirectoryMutationRecorder('provider-budget-reject');
  const estimate = createStorageEstimateRecorder({ quota: 100, usage: 0, usageDetails: { fake: true, case: 'provider-budget-reject' } });
  return await withFakeNavigator(async (root) => {
    const trace = new TraceLog();
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-lane-provider-options-budget-reject`, prefix, trace });
    const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-lane-provider-options-budget-reject-adapter`, store, scheduler: makeScheduler(`${REVISION}-lane-provider-options-budget-reject-scheduler`, trace), trace });
    const scheduled = adapter.schedulePut(bytes, { id: 'provider-budget-reject-put', providerOptions: { writeBudgetGuard: { maxUsageRatio: 0.0001, requireEstimate: true } }, label: 'provider-budget-reject' });
    const before = fakeTreeSummary(root);
    const drain = await adapter.drain({ maxSteps: 2 });
    const after = fakeTreeSummary(root);
    return { scheduled, before, drain, after, estimate: estimate.snapshot(), mutations: recorder.snapshot(), storeSnapshot: store.snapshot(), adapterSnapshot: adapter.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks: recorder.hooks, estimate: estimate.estimate });
}

async function runNamedPutOptionsOverrideCase() {
  const bytes = payload('named-put-options-override');
  const prefix = `browserrt/${REVISION}/fake-lane-provider-options/named-put-options-override`;
  const recorder = createDirectoryMutationRecorder('named-put-options-override');
  const estimate = createStorageEstimateRecorder({ quota: 100, usage: 0, usageDetails: { fake: true, case: 'named-put-options-override' } });
  return await withFakeNavigator(async (root) => {
    const trace = new TraceLog();
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-lane-provider-options-override`, prefix, trace });
    const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-lane-provider-options-override-adapter`, store, scheduler: makeScheduler(`${REVISION}-lane-provider-options-override-scheduler`, trace), trace });
    const scheduled = adapter.schedulePut(bytes, {
      id: 'named-put-options-override-put',
      providerOptions: { writeBudgetGuard: { maxUsageRatio: 0.0001, requireEstimate: true } },
      putOptions: { writeBudgetGuard: false },
      label: 'named-put-options-override'
    });
    const drain = await adapter.drain({ maxSteps: 2 });
    const result = adapter.result('named-put-options-override-put');
    const verify = result?.ref ? await store.verify(result.ref) : null;
    const after = fakeTreeSummary(root);
    return { scheduled, drain, result: result ? { digest: result.digest, bytes: result.bytes, duplicate: result.duplicate, budget: result.budget, ref: result.ref } : null, verify, after, estimate: estimate.snapshot(), mutations: recorder.snapshot(), storeSnapshot: store.snapshot(), adapterSnapshot: adapter.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks: recorder.hooks, estimate: estimate.estimate });
}

async function runProviderAbortReadCase() {
  const bytes = payload('provider-abort-read');
  const prefix = `browserrt/${REVISION}/fake-lane-provider-options/provider-abort-read`;
  const recorder = createDirectoryMutationRecorder('provider-abort-read');
  return await withFakeNavigator(async (root) => {
    const trace = new TraceLog();
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-lane-provider-options-abort-read`, prefix, trace });
    const seed = await store.put(bytes, { label: 'provider-abort-read-seed' });
    const controller = new AbortController();
    controller.abort('rev0102-provider-options-read-abort');
    const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-lane-provider-options-abort-read-adapter`, store, scheduler: makeScheduler(`${REVISION}-lane-provider-options-abort-read-scheduler`, trace), trace });
    const scheduled = adapter.scheduleGet(seed.ref, { id: 'provider-aborted-get', providerOptions: { signal: controller.signal } });
    const drain = await adapter.drain({ maxSteps: 2 });
    const directAfterAbort = await store.get(seed.ref);
    return { scheduled, drain, seed: { digest: seed.digest, bytes: seed.bytes, ref: seed.ref }, directAfterAbortBytes: directAfterAbort.byteLength, after: fakeTreeSummary(root), mutations: recorder.snapshot(), storeSnapshot: store.snapshot(), adapterSnapshot: adapter.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks: recorder.hooks });
}

class RecordingStore {
  constructor() { this.name = 'recording-block-store'; this.provider = 'recording-provider-v0'; this.calls = []; }
  #call(method, options) { const row = { method, options: { ...(options || {}) } }; this.calls.push(row); return row; }
  async put(value, fields = {}, options = {}) { const row = this.#call('put', options); row.fields = { ...fields }; return { digest: 'sha256:recording', hash: 'recording', bytes: value?.byteLength ?? String(value).length, ref: { digest: 'sha256:recording', hash: 'recording' }, duplicate: false, observedOptions: row.options }; }
  async get(ref, options = {}) { this.#call('get', options); return new Uint8Array([1, 2, 3]); }
  async has(ref, options = {}) { this.#call('has', options); return options.namedHas === true; }
  async verify(ref, options = {}) { this.#call('verify', options); return { ok: options.namedVerify === true, present: true, digest: ref?.digest || String(ref), bytes: 3 }; }
  async delete(ref, options = {}) { this.#call('delete', options); return options.namedDelete === true; }
  async estimate(options = {}) { this.#call('estimate', options); return { quota: 10, usage: 1 }; }
  async cleanupForTest(options = {}) { this.#call('cleanup', options); return options.namedCleanup === true; }
  snapshot() { return { provider: this.provider, blockCount: 0, calls: this.calls.map((row) => ({ method: row.method, fields: row.fields || null, optionKeys: Object.keys(row.options).sort(), options: row.options })) }; }
}

async function runNamedOptionBagsCase() {
  const trace = new TraceLog();
  const store = new RecordingStore();
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-lane-provider-options-recording-adapter`, store, scheduler: makeScheduler(`${REVISION}-lane-provider-options-recording-scheduler`, trace), trace });
  adapter.schedulePut(new Uint8Array([7, 8, 9]), { id: 'record-put', providerOptions: { inherited: 'provider', overridden: 'provider' }, storeOptions: { storeOnly: true, overridden: 'store' }, putOptions: { namedPut: true, overridden: 'put' }, fields: { purpose: 'option-bag-proof' } });
  adapter.scheduleHas('sha256:recording', { id: 'record-has', providerOptions: { inherited: 'provider' }, hasOptions: { namedHas: true } });
  adapter.scheduleVerify('sha256:recording', { id: 'record-verify', providerOptions: { inherited: 'provider' }, verifyOptions: { namedVerify: true } });
  adapter.scheduleDelete('sha256:recording', { id: 'record-delete', providerOptions: { inherited: 'provider' }, deleteOptions: { namedDelete: true } });
  adapter.scheduleEstimate({ id: 'record-estimate', providerOptions: { inherited: 'provider' }, estimateOptions: { namedEstimate: true } });
  adapter.scheduleCleanupForTest({ id: 'record-cleanup', providerOptions: { inherited: 'provider' }, cleanupOptions: { namedCleanup: true } });
  const drain = await adapter.drain({ maxSteps: 10 });
  return { drain, calls: store.calls, snapshot: adapter.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
}

export async function runProbe() {
  const started = performance.now();
  const providerBudgetReject = await runProviderBudgetRejectCase();
  const namedPutOptionsOverride = await runNamedPutOptionsOverrideCase();
  const providerAbortRead = await runProviderAbortReadCase();
  const namedOptionBags = await runNamedOptionBagsCase();

  const rejectRow = providerBudgetReject.drain.results.find((row) => row.opId === 'provider-budget-reject-put');
  assert.equal(rejectRow.ok, false, 'scheduled provider budget guard should reject the put');
  assert.equal(rejectRow.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.equal(providerBudgetReject.before.dirCount, 0);
  assert.equal(providerBudgetReject.after.dirCount, 0, 'budget rejection through lane adapter must happen before OPFS directory mutation');
  assert.equal(providerBudgetReject.after.fileCount, 0, 'budget rejection through lane adapter must not create a block file');
  assert.equal(providerBudgetReject.estimate.callCount, 1, 'scheduled provider budget guard should call estimate once');
  assert.equal(providerBudgetReject.mutations.byKind['create-directory'] || 0, 0, 'budget rejection should create zero directories');
  assert.equal(providerBudgetReject.storeSnapshot.stats.writeBudgetRejects, 1, 'underlying OPFS store should see the provider budget guard');
  assert.ok(providerBudgetReject.traceKinds.includes('storage:opfs-block-write-budget-reject'));

  const overrideRow = namedPutOptionsOverride.drain.results.find((row) => row.opId === 'named-put-options-override-put');
  assert.equal(overrideRow.ok, true, 'named putOptions should override the inherited impossible provider budget');
  assert.equal(namedPutOptionsOverride.result.budget.enabled, false, 'putOptions.writeBudgetGuard=false should reach the store');
  assert.equal(namedPutOptionsOverride.verify.ok, true);
  assert.equal(namedPutOptionsOverride.after.fileCount, 1, 'override case should write one block file');
  assert.equal(namedPutOptionsOverride.estimate.callCount, 0, 'disabled named putOptions budget should avoid estimate calls');
  assert.ok(namedPutOptionsOverride.mutations.byKind['create-file'] >= 1, 'override case should create a block file');

  const abortRow = providerAbortRead.drain.results.find((row) => row.opId === 'provider-aborted-get');
  assert.equal(abortRow.ok, false, 'providerOptions.signal should abort a scheduled read');
  assert.equal(abortRow.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(providerAbortRead.directAfterAbortBytes, providerAbortRead.seed.bytes, 'aborted scheduled read must not corrupt the seeded block');
  assert.equal(providerAbortRead.storeSnapshot.stats.abortRejects, 1, 'underlying OPFS store should observe the provider abort signal');
  assert.ok(providerAbortRead.traceKinds.includes('storage:opfs-block-abort'));

  const callsByMethod = new Map(namedOptionBags.calls.map((row) => [row.method, row]));
  assert.equal(callsByMethod.get('put').options.inherited, 'provider');
  assert.equal(callsByMethod.get('put').options.storeOnly, true);
  assert.equal(callsByMethod.get('put').options.namedPut, true);
  assert.equal(callsByMethod.get('put').options.overridden, 'put', 'named putOptions should win over store/provider bags');
  assert.equal(callsByMethod.get('has').options.namedHas, true);
  assert.equal(callsByMethod.get('verify').options.namedVerify, true);
  assert.equal(callsByMethod.get('delete').options.namedDelete, true);
  assert.equal(callsByMethod.get('estimate').options.namedEstimate, true);
  assert.equal(callsByMethod.get('cleanup').options.namedCleanup, true);
  assert.ok(namedOptionBags.traceKinds.includes('block-store-lane:schedule'));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-block-store-lane-provider-options-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release proof that BlockStoreLaneAdapter preserves explicit providerOptions/storeOptions/named operation option bags when scheduled operations reach the underlying block store.',
    observations: { providerBudgetReject, namedPutOptionsOverride, providerAbortRead, namedOptionBags },
    claimsChecked: [
      'providerOptions.writeBudgetGuard reaches OpfsAsyncBlockStore through schedulePut and rejects before OPFS mutation',
      'named putOptions can intentionally override inherited providerOptions/storeOptions for a scheduled put',
      'providerOptions.signal reaches read-like scheduled operations and aborts at the underlying store boundary',
      'named has/verify/delete/estimate/cleanup option bags are preserved through the lane adapter'
    ],
    nonClaims: [
      'This is a provider-option pass-through proof, not a new scheduler fairness, throughput, durability, quota reservation, or crash-recovery claim.',
      'Fake OPFS release coverage is paired with a focused managed Chromium proof; neither claims cross-browser behavior, fsync durability, organic eviction survival, or production readiness.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-block-store-lane-provider-options-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[block_store_lane_provider_options_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
