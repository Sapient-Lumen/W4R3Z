#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, createOpfsAsyncBlockStore, validateBlockStoreLaneAdapterSnapshot } from '../src/browserrt.mjs';
import { createDirectoryMutationRecorder, fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'storage:provider-timeout-abort-proof';
const DEFAULT_OUT = `artifacts/validation/${PFX}-STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-PROBE.json`;
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

class TimeoutContextRecordingStore {
  constructor({ trace = null, releaseDelayMs = 25 } = {}) {
    this.name = 'timeout-context-recording-store';
    this.provider = 'timeout-context-recorder-v0';
    this.trace = trace;
    this.releaseDelayMs = releaseDelayMs;
    this.calls = [];
  }
  async put(value, fields = {}, options = {}) {
    this.calls.push({ method: 'put', hasSignal: Boolean(options.signal), signalAbortedAtStart: options.signal?.aborted === true, operationTimeoutMs: options.operationTimeoutMs ?? null, abortProviderOnOperationTimeout: options.abortProviderOnOperationTimeout === true, label: fields.label ?? null });
    this.trace?.emit('timeout-context-recording-store:put-start', this.calls.at(-1));
    await sleep(this.releaseDelayMs);
    this.trace?.emit('timeout-context-recording-store:put-complete', { signalAbortedAtEnd: options.signal?.aborted === true });
    return Object.freeze({ digest: 'sha256:context-recorder', hash: 'context-recorder', bytes: String(value).length, ref: { digest: 'sha256:context-recorder', hash: 'context-recorder' } });
  }
  async get() { return new Uint8Array(); }
  async has() { return false; }
  async verify() { return { ok: false, present: false, digest: 'sha256:context-recorder', bytes: 0 }; }
  async delete() { return false; }
  snapshot() { return { provider: this.provider, blockCount: 0, calls: this.calls.map((row) => ({ ...row })) }; }
}

async function runDefaultNonCancellationCase() {
  const trace = new TraceLog();
  const store = new TimeoutContextRecordingStore({ trace, releaseDelayMs: 30 });
  const adapter = createBlockStoreLaneAdapter({
    label: `${REVISION}-provider-timeout-default-noncancel-adapter`,
    store,
    scheduler: makeScheduler(`${REVISION}-provider-timeout-default-noncancel-scheduler`, trace),
    trace,
    defaultOperationTimeoutMs: 5
  });
  const scheduled = adapter.schedulePut('default timeout does not synthesize provider AbortSignal', { id: 'default-noncancel-timeout-put', label: 'default-noncancel-timeout' });
  const drain = await adapter.drain({ maxSteps: 2 });
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  return { scheduled, drain, settled, calls: store.calls, snapshot: adapter.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
}

async function runOptInOpfsAbortCase() {
  const trace = new TraceLog();
  const recorder = createDirectoryMutationRecorder(`${REVISION}-provider-timeout-abort-mutations`);
  const writeEvents = [];
  const hooks = {
    ...recorder.hooks,
    async onWrite({ file, bytes }) {
      writeEvents.push(Object.freeze({ event: 'onWrite-start', path: file.path, bytes: bytes.byteLength, at: Date.now() }));
      await sleep(70);
      writeEvents.push(Object.freeze({ event: 'onWrite-end', path: file.path, bytes: bytes.byteLength, at: Date.now() }));
    },
    async onAbort({ file }) {
      writeEvents.push(Object.freeze({ event: 'writer-abort', path: file.path, at: Date.now() }));
    }
  };
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-provider-timeout-abort-opfs-store`, prefix: `browserrt/${REVISION}/provider-timeout-abort`, trace, writeBudgetGuard: false });
    const adapter = createBlockStoreLaneAdapter({
      label: `${REVISION}-provider-timeout-abort-adapter`,
      store,
      scheduler: makeScheduler(`${REVISION}-provider-timeout-abort-scheduler`, trace),
      trace,
      defaultOperationTimeoutMs: 20,
      abortProviderOnOperationTimeout: true
    });
    const before = fakeTreeSummary(root);
    const scheduled = adapter.schedulePut(new TextEncoder().encode(`BrowserRT ${REVISION} provider timeout abort payload`), { id: 'opfs-put-aborted-by-operation-timeout', label: 'provider-timeout-abort' });
    const drain = await adapter.drain({ maxSteps: 2 });
    const afterTimeout = adapter.snapshot();
    const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
    const afterSettled = fakeTreeSummary(root);
    const quarantine = adapter.timedOutOperationQuarantine('storage');
    const review = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: 'opfs-put-aborted-by-operation-timeout', reviewer: 'provider-timeout-abort-proof', reason: 'provider abort after operation timeout reviewed', reviewToken: `${REVISION}-provider-timeout-abort-review` });
    const cleared = adapter.clearFailedTimedOutOperations({ reviewManifest: review, requireReviewFingerprint: true, reason: 'provider-timeout-abort-proof-cleared-failed-abort' });
    const healthy = adapter.markHealthy('storage', 'provider-timeout-abort-reviewed');
    const recoveredSchedule = adapter.schedulePut('BrowserRT provider timeout abort recovered write', { id: 'provider-timeout-abort-recovered-put', label: 'provider-timeout-abort-recovered', operationTimeoutMs: 250, providerOptions: { writeBudgetGuard: false } });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 });
    const recoveredResult = adapter.result('provider-timeout-abort-recovered-put');
    const recoveredVerify = recoveredResult?.ref ? await store.verify(recoveredResult.ref) : null;
    const finalSnapshot = adapter.snapshot();
    return { before, scheduled, drain, afterTimeout, settled, afterSettled, quarantine, review, cleared, healthy, recoveredSchedule, recoveryDrain, recoveredResult, recoveredVerify, finalSnapshot, storeSnapshot: store.snapshot(), mutations: recorder.snapshot(), writeEvents, traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks });
}

export async function runProbe() {
  const started = performance.now();
  const defaultNonCancellation = await runDefaultNonCancellationCase();
  const optInOpfsAbort = await runOptInOpfsAbortCase();

  const defaultRow = defaultNonCancellation.drain.results.find((row) => row.opId === 'default-noncancel-timeout-put');
  assert.equal(defaultNonCancellation.scheduled.accepted, true);
  assert.equal(defaultRow.ok, false);
  assert.equal(defaultRow.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(defaultNonCancellation.calls[0].hasSignal, false, 'default timeout must not synthesize provider AbortSignal');
  assert.equal(defaultNonCancellation.snapshot.executor.stats.providerTimeoutAborts, 0, 'default timeout remains non-cancelling');
  assert.equal(defaultNonCancellation.settled.ok, true, 'default late completion should settle quarantine state');
  assert.ok(defaultNonCancellation.traceKinds.includes('storage-lane:operation-timeout'));

  const timeoutRow = optInOpfsAbort.drain.results.find((row) => row.opId === 'opfs-put-aborted-by-operation-timeout');
  assert.equal(optInOpfsAbort.scheduled.accepted, true);
  assert.equal(timeoutRow.ok, false);
  assert.equal(timeoutRow.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(timeoutRow.error.providerDetail?.abortProviderOnTimeout, true);
  assert.equal(timeoutRow.error.providerDetail?.providerAbortSignaled, true);
  assert.equal(optInOpfsAbort.afterTimeout.executor.stats.operationTimeouts, 1);
  assert.equal(optInOpfsAbort.afterTimeout.executor.stats.providerTimeoutAborts, 1);
  assert.equal(optInOpfsAbort.settled.ok, true, 'provider abort should settle the timed-out operation');
  assert.equal(optInOpfsAbort.quarantine.failedTimedOutOperationCount, 1, 'provider abort should be late-failure quarantined');
  assert.equal(optInOpfsAbort.afterSettled.fileCount, 0, 'OPFS aborted timed-out put should leave no block files');
  assert.equal(optInOpfsAbort.afterSettled.byteCount, 0, 'OPFS aborted timed-out put should leave no block bytes');
  assert.equal(optInOpfsAbort.storeSnapshot.stats.abortRejects > 0, true, 'underlying OPFS store should observe timeout-owned abort signal');
  const rollbackOrPreCreateAbort = optInOpfsAbort.storeSnapshot.stats.rollbackDeletes >= 1 || optInOpfsAbort.storeSnapshot.stats.rollbackMisses >= 1 || (optInOpfsAbort.afterSettled.fileCount === 0 && optInOpfsAbort.writeEvents.some((row) => row.event === 'writer-abort'));
  assert.equal(rollbackOrPreCreateAbort, true, 'aborted write should either run rollback cleanup or abort before any durable block file is created');
  assert.ok(optInOpfsAbort.writeEvents.some((row) => row.event === 'writer-abort'), 'fake writer abort should be called before close');
  assert.equal(optInOpfsAbort.cleared.clearedCount, 1);
  assert.equal(optInOpfsAbort.healthy.healthy, true);
  const recoveredRow = optInOpfsAbort.recoveryDrain.results.find((row) => row.opId === 'provider-timeout-abort-recovered-put');
  assert.equal(recoveredRow.ok, true, 'lane should recover after failed-abort quarantine is reviewed and cleared');
  assert.equal(optInOpfsAbort.recoveredVerify.ok, true);
  assert.equal(validateBlockStoreLaneAdapterSnapshot(optInOpfsAbort.finalSnapshot).ok, true);
  for (const kind of ['storage-lane:operation-timeout', 'storage:opfs-block-abort', 'storage-lane:late-provider-failures-cleared']) {
    assert.ok(optInOpfsAbort.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }
  assert.ok(optInOpfsAbort.traceKinds.includes('storage:opfs-block-put-rollback') || optInOpfsAbort.traceKinds.includes('storage:opfs-block-staged-cleanup'), 'missing rollback or staged cleanup trace kind');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-provider-timeout-abort-proof`, task_id: RELEASE_TASK,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release proof that storage-lane operation timeouts can optionally abort provider work through a timeout-owned AbortSignal, and that scheduled OPFS puts then roll back instead of continuing as wasteful late mutation.',
    observations: { defaultNonCancellation, optInOpfsAbort },
    claimsChecked: [
      'operation timeout remains non-cancelling by default for compatibility',
      'abortProviderOnOperationTimeout=true injects a timeout-owned AbortSignal into scheduled provider options',
      'OPFS put observes BRT_OPFS_OPERATION_ABORTED from the timeout-owned abort signal, aborts the writer, rolls back, and leaves no block bytes',
      'late provider abort is quarantined as a failed timed-out operation and can be reviewed/cleared before lane recovery'
    ],
    nonClaims: [
      'Provider timeout abort is opt-in; BrowserRT still does not claim universal cancellation for all scheduled storage work.',
      'AbortSignal cancellation is cooperative: providers that ignore the signal can still settle late and require quarantine review.',
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-provider-timeout-abort-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_provider_timeout_abort_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
