#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, createOpfsAsyncBlockStore, validateBlockStoreLaneAdapterSnapshot } from '../src/browserrt.mjs';
import { createDirectoryMutationRecorder, fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'storage:composite-abort-signal-proof';
const DEFAULT_OUT = `artifacts/validation/${PFX}-STORAGE-LANE-COMPOSITE-ABORT-SIGNAL-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

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

function abortSummary(signal) {
  const reason = signal && 'reason' in signal ? signal.reason : null;
  return Object.freeze({
    aborted: signal?.aborted === true,
    reasonName: reason?.name || null,
    reasonMessage: reason?.message || (reason == null ? null : String(reason))
  });
}

function callerAbortError(signal, stage) {
  const error = new Error(`caller abort observed at ${stage}`);
  error.name = 'BrowserRTCompositeAbortSignalTestError';
  error.code = 'BRT_TEST_CALLER_ABORTED';
  error.storageDisposition = 'BRT_TEST_CALLER_ABORTED';
  error.detail = Object.freeze({ stage, signal: abortSummary(signal) });
  return error;
}

class SignalAwareStore {
  constructor({ trace = null, releaseDelayMs = 80 } = {}) {
    this.name = 'signal-aware-store';
    this.provider = 'signal-aware-test-provider-v0';
    this.trace = trace;
    this.releaseDelayMs = releaseDelayMs;
    this.calls = [];
  }
  async put(value, fields = {}, options = {}) {
    const signal = options.signal ?? options.abortSignal ?? null;
    const call = {
      method: 'put',
      label: fields.label ?? null,
      hasSignal: Boolean(signal),
      signalEqualsAbortSignal: signal === options.abortSignal,
      compositeAbortSignal: options.compositeAbortSignal === true,
      providerSignalComposed: options.providerSignalComposed === true,
      operationTimeoutMs: options.operationTimeoutMs ?? null,
      start: abortSummary(signal)
    };
    this.calls.push(call);
    this.trace?.emit('signal-aware-store:put-start', call);
    if (signal?.aborted) throw callerAbortError(signal, 'start');
    const result = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => resolve('completed'), this.releaseDelayMs);
      const onAbort = () => {
        clearTimeout(timer);
        const abortCall = { ...call, abortedDuringWait: abortSummary(signal) };
        this.calls.push(abortCall);
        this.trace?.emit('signal-aware-store:put-abort', abortCall);
        reject(callerAbortError(signal, 'wait'));
      };
      signal?.addEventListener?.('abort', onAbort, { once: true });
    });
    return Object.freeze({ digest: `sha256:${result}`, hash: result, bytes: String(value).length, ref: { digest: `sha256:${result}`, hash: result } });
  }
  async get(ref, options = {}) { return new Uint8Array(); }
  async has(ref, options = {}) { return false; }
  async verify(ref, options = {}) { return Object.freeze({ ok: false, present: false, digest: String(ref), bytes: 0 }); }
  async delete(ref, options = {}) { return false; }
  snapshot() { return Object.freeze({ provider: this.provider, blockCount: 0, calls: this.calls.map((row) => ({ ...row })) }); }
}

async function runPreAbortedCallerSignalCase() {
  const trace = new TraceLog();
  const recorder = createDirectoryMutationRecorder(`${REVISION}-composite-abort-preaborted-mutations`);
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-composite-preabort-opfs-store`, prefix: `browserrt/${REVISION}/composite-abort/preaborted`, trace, writeBudgetGuard: false });
    const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-composite-preabort-adapter`, store, scheduler: makeScheduler(`${REVISION}-composite-preabort-scheduler`, trace), trace, defaultOperationTimeoutMs: 1000, abortProviderOnOperationTimeout: true });
    const controller = new AbortController();
    controller.abort(new Error('caller-pre-aborted-before-scheduled-opfs-put'));
    const before = fakeTreeSummary(root);
    const schedule = adapter.schedulePut(new TextEncoder().encode(`BrowserRT ${REVISION} composite abort preaborted payload`), { id: 'preaborted-caller-signal-opfs-put', label: 'caller-preabort', providerOptions: { signal: controller.signal } });
    const drain = await adapter.drain({ maxSteps: 2 });
    const after = fakeTreeSummary(root);
    return { before, schedule, drain, after, snapshot: adapter.snapshot(), storeSnapshot: store.snapshot(), mutations: recorder.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks: recorder.hooks });
}

async function runCallerAbortBeforeTimeoutCase() {
  const trace = new TraceLog();
  const store = new SignalAwareStore({ trace, releaseDelayMs: 200 });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-composite-caller-abort-adapter`, store, scheduler: makeScheduler(`${REVISION}-composite-caller-abort-scheduler`, trace), trace, defaultOperationTimeoutMs: 500, abortProviderOnOperationTimeout: true });
  const controller = new AbortController();
  const schedule = adapter.schedulePut('caller abort should win before operation timeout', { id: 'caller-abort-before-timeout-put', label: 'caller-abort-before-timeout', providerOptions: { signal: controller.signal } });
  const abortTimer = setTimeout(() => controller.abort(new Error('caller-aborted-before-timeout-fired')), 20);
  const drain = await adapter.drain({ maxSteps: 2 });
  clearTimeout(abortTimer);
  return { schedule, drain, snapshot: adapter.snapshot(), calls: store.calls, traceKinds: trace.kinds(), trace: trace.snapshot() };
}

async function runDualCallerSignalCase() {
  const trace = new TraceLog();
  const store = new SignalAwareStore({ trace, releaseDelayMs: 200 });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-composite-dual-caller-signal-adapter`, store, scheduler: makeScheduler(`${REVISION}-composite-dual-caller-signal-scheduler`, trace), trace, defaultOperationTimeoutMs: 500, abortProviderOnOperationTimeout: true });
  const signalController = new AbortController();
  const abortSignalController = new AbortController();
  const schedule = adapter.schedulePut('abortSignal should compose alongside signal before operation timeout', { id: 'dual-caller-abort-signal-put', label: 'dual-caller-abort-signal', providerOptions: { signal: signalController.signal, abortSignal: abortSignalController.signal } });
  const abortTimer = setTimeout(() => abortSignalController.abort(new Error('caller-abortSignal-aborted-before-timeout-fired')), 20);
  const drain = await adapter.drain({ maxSteps: 2 });
  clearTimeout(abortTimer);
  return { schedule, drain, snapshot: adapter.snapshot(), calls: store.calls, traceKinds: trace.kinds(), trace: trace.snapshot() };
}

async function runTimeoutStillAbortsWithLiveCallerSignalCase() {
  const trace = new TraceLog();
  const store = new SignalAwareStore({ trace, releaseDelayMs: 200 });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-composite-timeout-adapter`, store, scheduler: makeScheduler(`${REVISION}-composite-timeout-scheduler`, trace), trace, defaultOperationTimeoutMs: 25, abortProviderOnOperationTimeout: true });
  const controller = new AbortController();
  const schedule = adapter.schedulePut('timeout should still abort provider when caller signal is live', { id: 'timeout-composite-live-caller-put', label: 'timeout-composite-live-caller', providerOptions: { signal: controller.signal } });
  const drain = await adapter.drain({ maxSteps: 2 });
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  return { schedule, drain, settled, snapshot: adapter.snapshot(), calls: store.calls, traceKinds: trace.kinds(), trace: trace.snapshot() };
}

export async function runProbe() {
  const started = performance.now();
  const preAborted = await runPreAbortedCallerSignalCase();
  const callerAbortBeforeTimeout = await runCallerAbortBeforeTimeoutCase();
  const dualCallerSignal = await runDualCallerSignalCase();
  const timeoutWithLiveCallerSignal = await runTimeoutStillAbortsWithLiveCallerSignalCase();

  const preAbortRow = preAborted.drain.results.find((row) => row.opId === 'preaborted-caller-signal-opfs-put');
  assert.equal(preAborted.schedule.accepted, true);
  assert.equal(preAbortRow.ok, false, 'pre-aborted caller signal should reject scheduled OPFS put');
  assert.equal(preAbortRow.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(preAbortRow.error.providerDetail?.stage, 'before-digest', 'caller pre-abort should be observed before OPFS digest/open/mutation');
  assert.equal(preAborted.after.fileCount, 0, 'pre-aborted scheduled OPFS put must leave no files');
  assert.equal(preAborted.after.dirCount, 0, 'pre-aborted scheduled OPFS put must leave no directories');
  assert.equal(preAborted.storeSnapshot.stats.opens, 0, 'pre-aborted scheduled OPFS put should not open OPFS');
  assert.equal(preAborted.snapshot.executor.stats.operationTimeouts, 0, 'caller pre-abort must not be converted into operation timeout');
  assert.equal(preAborted.snapshot.executor.stats.providerTimeoutAborts, 0, 'caller pre-abort must not count as timeout abort');
  assert.ok(preAborted.traceKinds.includes('storage:opfs-block-abort'));

  const callerAbortRow = callerAbortBeforeTimeout.drain.results.find((row) => row.opId === 'caller-abort-before-timeout-put');
  assert.equal(callerAbortBeforeTimeout.schedule.accepted, true);
  assert.equal(callerAbortRow.ok, false, 'caller abort before timeout should reject scheduled provider call');
  assert.equal(callerAbortRow.error.code, 'BRT_TEST_CALLER_ABORTED');
  assert.equal(callerAbortBeforeTimeout.snapshot.executor.stats.operationTimeouts, 0, 'caller abort before timeout must not enter timeout quarantine');
  assert.equal(callerAbortBeforeTimeout.snapshot.executor.stats.providerTimeoutAborts, 0, 'caller abort before timeout must not count as timeout abort');
  assert.equal(callerAbortBeforeTimeout.calls[0].providerSignalComposed, true, 'adapter should compose caller and timeout-owned signals when both are live');
  assert.equal(callerAbortBeforeTimeout.calls[0].signalEqualsAbortSignal, true, 'provider should receive one composed signal on signal and abortSignal');
  assert.equal(callerAbortBeforeTimeout.calls.some((row) => row.abortedDuringWait?.reasonMessage === 'caller-aborted-before-timeout-fired'), true, 'provider should observe caller abort reason');

  const dualSignalRow = dualCallerSignal.drain.results.find((row) => row.opId === 'dual-caller-abort-signal-put');
  assert.equal(dualCallerSignal.schedule.accepted, true);
  assert.equal(dualSignalRow.ok, false, 'caller abortSignal before timeout should reject scheduled provider call');
  assert.equal(dualSignalRow.error.code, 'BRT_TEST_CALLER_ABORTED');
  assert.equal(dualCallerSignal.snapshot.executor.stats.operationTimeouts, 0, 'caller abortSignal before timeout must not enter timeout quarantine');
  assert.equal(dualCallerSignal.snapshot.executor.stats.providerTimeoutAborts, 0, 'caller abortSignal before timeout must not count as timeout abort');
  assert.equal(dualCallerSignal.calls[0].providerSignalComposed, true, 'adapter should compose signal, abortSignal, and timeout-owned signal when all are live');
  assert.equal(dualCallerSignal.calls[0].signalEqualsAbortSignal, true, 'provider should receive one composed signal on both signal and abortSignal');
  assert.equal(dualCallerSignal.calls.some((row) => row.abortedDuringWait?.reasonMessage === 'caller-abortSignal-aborted-before-timeout-fired'), true, 'provider should observe caller abortSignal reason');

  const timeoutRow = timeoutWithLiveCallerSignal.drain.results.find((row) => row.opId === 'timeout-composite-live-caller-put');
  assert.equal(timeoutWithLiveCallerSignal.schedule.accepted, true);
  assert.equal(timeoutRow.ok, false, 'timeout should reject caller-visible scheduled call');
  assert.equal(timeoutRow.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(timeoutRow.error.providerDetail?.providerAbortSignaled, true);
  assert.equal(timeoutWithLiveCallerSignal.snapshot.executor.stats.operationTimeouts, 1);
  assert.equal(timeoutWithLiveCallerSignal.snapshot.executor.stats.providerTimeoutAborts, 1, 'timeout abort should still fire with a live caller signal composed in');
  assert.equal(timeoutWithLiveCallerSignal.settled.ok, true, 'late provider abort should settle quarantine');
  assert.equal(timeoutWithLiveCallerSignal.snapshot.executor.stats.failedTimedOutOperations, 1, 'timeout-owned abort should remain reviewed as late failure');
  assert.equal(timeoutWithLiveCallerSignal.calls[0].providerSignalComposed, true);
  assert.equal(timeoutWithLiveCallerSignal.calls.some((row) => row.abortedDuringWait?.reasonMessage?.includes('operation timeout aborted provider context')), true, 'provider should observe timeout abort reason');
  assert.equal(validateBlockStoreLaneAdapterSnapshot(timeoutWithLiveCallerSignal.snapshot).ok, true);
  for (const kind of ['storage-lane:operation-timeout', 'storage-lane:late-provider-failure']) assert.ok(timeoutWithLiveCallerSignal.traceKinds.includes(kind), `timeout composite trace missing ${kind}`);

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-composite-abort-signal-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier proof that scheduled provider cancellation composes caller AbortSignal and timeout-owned AbortSignal instead of masking one with the other.',
    cases: { preAborted, callerAbortBeforeTimeout, dualCallerSignal, timeoutWithLiveCallerSignal },
    claimsChecked: [
      'pre-aborted caller providerOptions.signal reaches scheduled OPFS put before digest/open/mutation even when abortProviderOnOperationTimeout is enabled',
      'caller abort before operation timeout rejects as caller/provider abort rather than timeout quarantine',
      'caller abortSignal composes alongside signal and can abort before operation timeout',
      'timeout-owned abort still fires when a live caller signal is also supplied',
      'providers receive one composed signal on both signal and abortSignal when both cancellation sources exist'
    ],
    nonClaims: [
      'Release proof uses fake OPFS/recording providers; managed browser proof supplies Chromium OPFS evidence.',
      'Abort remains cooperative; providers that ignore AbortSignal may still settle late and require quarantine review.',
      'This does not claim cross-browser conformance, quota reservation, eviction survival, fsync durability, crash/power-loss recovery, Web Locks fairness, or production readiness.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-composite-abort-signal-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[storage_lane_composite_abort_signal_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
