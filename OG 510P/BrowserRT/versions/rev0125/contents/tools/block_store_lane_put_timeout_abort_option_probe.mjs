#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'storage:block-store-lane-put-timeout-abort-option-proof';
const DEFAULT_OUT = `artifacts/validation/${PFX}-BLOCK-STORE-LANE-PUT-TIMEOUT-ABORT-OPTION-PROBE.json`;
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
    reasonCode: reason?.code || null,
    reasonMessage: reason?.message || (reason == null ? null : String(reason))
  });
}

function timeoutAbortObservedError(signal, stage) {
  const error = new Error(`put timeout abort observed at ${stage}`);
  error.name = 'BrowserRTPutTimeoutAbortOptionTestError';
  error.code = 'BRT_TEST_PUT_TIMEOUT_ABORT_OBSERVED';
  error.storageDisposition = 'BRT_TEST_PUT_TIMEOUT_ABORT_OBSERVED';
  error.detail = Object.freeze({ stage, signal: abortSummary(signal) });
  return error;
}

class PutTimeoutOptionRecordingStore {
  constructor({ trace = null, releaseDelayMs = 80 } = {}) {
    this.name = 'put-timeout-option-recording-store';
    this.provider = 'put-timeout-option-recorder-v0';
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
      optionKeys: Object.keys(options).filter((key) => key !== 'signal' && key !== 'abortSignal').sort(),
      operationTimeoutMs: options.operationTimeoutMs ?? null,
      start: abortSummary(signal)
    };
    this.calls.push(call);
    this.trace?.emit('put-timeout-option-store:put-start', call);
    if (signal?.aborted) throw timeoutAbortObservedError(signal, 'start');
    const result = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => resolve('completed'), this.releaseDelayMs);
      const onAbort = () => {
        clearTimeout(timer);
        const aborted = { ...call, abortedDuringWait: abortSummary(signal) };
        this.calls.push(aborted);
        this.trace?.emit('put-timeout-option-store:put-abort', aborted);
        reject(timeoutAbortObservedError(signal, 'wait'));
      };
      signal?.addEventListener?.('abort', onAbort, { once: true });
    });
    const done = { ...call, completed: true, end: abortSummary(signal) };
    this.calls.push(done);
    this.trace?.emit('put-timeout-option-store:put-complete', done);
    return Object.freeze({ digest: `sha256:${result}`, hash: result, bytes: String(value).length, ref: { digest: `sha256:${result}`, hash: result } });
  }
  async get() { return new Uint8Array(); }
  async has() { return false; }
  async verify(ref) { return Object.freeze({ ok: false, present: false, digest: String(ref), bytes: 0 }); }
  async delete() { return false; }
  snapshot() { return Object.freeze({ provider: this.provider, blockCount: 0, calls: this.calls.map((row) => ({ ...row })) }); }
}

async function runPutLevelOptInCase() {
  const trace = new TraceLog();
  const store = new PutTimeoutOptionRecordingStore({ trace, releaseDelayMs: 120 });
  const adapter = createBlockStoreLaneAdapter({
    label: `${REVISION}-put-timeout-abort-opt-in-adapter`,
    store,
    scheduler: makeScheduler(`${REVISION}-put-timeout-abort-opt-in-scheduler`, trace),
    trace,
    defaultOperationTimeoutMs: 0,
    abortProviderOnOperationTimeout: false
  });
  const scheduled = adapter.schedulePut('put-level opt-in should inject timeout AbortSignal', {
    id: 'put-level-timeout-abort-opt-in',
    label: 'put-timeout-abort-opt-in',
    operationTimeoutMs: 20,
    abortProviderOnOperationTimeout: true
  });
  const drain = await adapter.drain({ maxSteps: 2 });
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  return { scheduled, drain, settled, snapshot: adapter.snapshot(), calls: store.calls, traceKinds: trace.kinds(), trace: trace.snapshot() };
}

async function runPutLevelOptOutCase() {
  const trace = new TraceLog();
  const store = new PutTimeoutOptionRecordingStore({ trace, releaseDelayMs: 60 });
  const adapter = createBlockStoreLaneAdapter({
    label: `${REVISION}-put-timeout-abort-opt-out-adapter`,
    store,
    scheduler: makeScheduler(`${REVISION}-put-timeout-abort-opt-out-scheduler`, trace),
    trace,
    defaultOperationTimeoutMs: 0,
    abortProviderOnOperationTimeout: true
  });
  const scheduled = adapter.schedulePut('put-level opt-out should suppress default timeout AbortSignal', {
    id: 'put-level-timeout-abort-opt-out',
    label: 'put-timeout-abort-opt-out',
    operationTimeoutMs: 15,
    abortProviderOnOperationTimeout: false
  });
  const drain = await adapter.drain({ maxSteps: 2 });
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  return { scheduled, drain, settled, snapshot: adapter.snapshot(), calls: store.calls, traceKinds: trace.kinds(), trace: trace.snapshot() };
}

export async function runProbe() {
  const started = performance.now();
  const putLevelOptIn = await runPutLevelOptInCase();
  const putLevelOptOut = await runPutLevelOptOutCase();

  const optInRow = putLevelOptIn.drain.results.find((row) => row.opId === 'put-level-timeout-abort-opt-in');
  assert.equal(putLevelOptIn.scheduled.accepted, true);
  assert.equal(optInRow.ok, false, 'put-level opt-in timeout should reject caller-visible scheduled put');
  assert.equal(optInRow.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(optInRow.error.providerDetail?.providerAbortSignaled, true, 'put-level opt-in should signal provider abort on timeout');
  assert.equal(putLevelOptIn.snapshot.executor.stats.operationTimeouts, 1);
  assert.equal(putLevelOptIn.snapshot.executor.stats.providerTimeoutAborts, 1, 'put-level opt-in should increment providerTimeoutAborts even when adapter default is false');
  assert.equal(putLevelOptIn.settled.ok, true, 'late provider abort failure should settle the timed-out quarantine row');
  assert.equal(putLevelOptIn.snapshot.executor.stats.failedTimedOutOperations, 1);
  assert.equal(putLevelOptIn.calls[0].hasSignal, true, 'put-level opt-in must forward a timeout-owned AbortSignal into provider options');
  assert.equal(putLevelOptIn.calls[0].signalEqualsAbortSignal, true, 'provider should receive the same timeout signal on signal and abortSignal');
  assert.ok(putLevelOptIn.calls.some((row) => row.abortedDuringWait?.reasonCode === 'BRT_STORAGE_OPERATION_TIMEOUT_ABORT'), 'provider should observe timeout-owned abort reason');
  assert.equal(putLevelOptIn.calls[0].optionKeys.includes('abortProviderOnOperationTimeout'), false, 'scheduler control option must not leak as a provider option key');
  assert.equal(validateBlockStoreLaneAdapterSnapshot(putLevelOptIn.snapshot).ok, true);

  const optOutRow = putLevelOptOut.drain.results.find((row) => row.opId === 'put-level-timeout-abort-opt-out');
  assert.equal(putLevelOptOut.scheduled.accepted, true);
  assert.equal(optOutRow.ok, false, 'put-level opt-out should still time out caller-visible scheduled put');
  assert.equal(optOutRow.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(optOutRow.error.providerDetail?.providerAbortSignaled, false, 'put-level opt-out should suppress provider abort even when adapter default is true');
  assert.equal(putLevelOptOut.snapshot.executor.stats.operationTimeouts, 1);
  assert.equal(putLevelOptOut.snapshot.executor.stats.providerTimeoutAborts, 0, 'put-level opt-out should not count provider timeout aborts');
  assert.equal(putLevelOptOut.settled.ok, true, 'late provider success should settle quarantine');
  assert.equal(putLevelOptOut.snapshot.executor.stats.successfulTimedOutOperations, 1, 'non-aborted provider should complete late as success');
  assert.equal(putLevelOptOut.calls[0].hasSignal, false, 'put-level opt-out must not forward a timeout AbortSignal');
  assert.ok(putLevelOptOut.calls.some((row) => row.completed === true), 'provider should complete late when put-level opt-out suppresses timeout abort');
  assert.equal(putLevelOptOut.calls[0].optionKeys.includes('abortProviderOnOperationTimeout'), false, 'opt-out scheduler control must not leak as provider option');
  assert.equal(validateBlockStoreLaneAdapterSnapshot(putLevelOptOut.snapshot).ok, true);

  for (const kind of ['storage-lane:operation-timeout', 'storage-lane:late-provider-failure']) assert.ok(putLevelOptIn.traceKinds.includes(kind), `opt-in trace missing ${kind}`);
  for (const kind of ['storage-lane:operation-timeout', 'storage-lane:late-provider-success']) assert.ok(putLevelOptOut.traceKinds.includes(kind), `opt-out trace missing ${kind}`);

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-block-store-lane-put-timeout-abort-option-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier proof that BlockStoreLaneAdapter.schedulePut honors per-operation abortProviderOnOperationTimeout true/false instead of only the adapter default.',
    cases: { putLevelOptIn, putLevelOptOut },
    claimsChecked: [
      'schedulePut per-operation abortProviderOnOperationTimeout=true injects a timeout-owned provider AbortSignal when the adapter default is false',
      'schedulePut per-operation abortProviderOnOperationTimeout=false suppresses timeout-owned provider AbortSignal when the adapter default is true',
      'scheduler control option does not leak as a provider option key',
      'timed-out provider abort failures and late successes still enter the existing timed-out-operation quarantine model'
    ],
    nonClaims: [
      'Release proof uses a recording provider; managed browser proof supplies Chromium OPFS evidence.',
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-block-store-lane-put-timeout-abort-option-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[block_store_lane_put_timeout_abort_option_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
