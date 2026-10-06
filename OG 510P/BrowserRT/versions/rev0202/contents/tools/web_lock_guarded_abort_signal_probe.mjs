#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { createWebLockGuardedBlockStore, REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'coord:web-lock-guarded-abort-signal-proof';
const DEFAULT_OUT = `artifacts/validation/${PFX}-WEB-LOCK-GUARDED-ABORT-SIGNAL-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function abortError() {
  const err = new Error('Fake Web Lock request aborted');
  err.name = 'AbortError';
  return err;
}

class AbortableQueuedLocks {
  constructor() {
    this.rows = new Map();
    this.events = [];
    this.requestCalls = 0;
    this.abortRejects = 0;
  }
  _row(name) {
    if (!this.rows.has(name)) this.rows.set(name, { active: [], queue: [] });
    return this.rows.get(name);
  }
  _counts(row) {
    return { held: row.active.length, pending: row.queue.length };
  }
  _canAcquire(row, mode) {
    if (mode === 'exclusive') return row.active.length === 0;
    return !row.active.some((item) => item.mode === 'exclusive');
  }
  _pump(name) {
    const row = this._row(name);
    while (row.queue.length > 0) {
      const next = row.queue[0];
      if (!this._canAcquire(row, next.mode)) return;
      row.queue.shift();
      this._acquire(name, row, next);
      if (next.mode === 'exclusive') return;
    }
  }
  _removeQueued(name, row, request) {
    const idx = row.queue.indexOf(request);
    if (idx >= 0) row.queue.splice(idx, 1);
    if (request.cleanup) request.cleanup();
    return idx >= 0;
  }
  _acquire(name, row, request) {
    if (request.cleanup) request.cleanup();
    const lock = Object.freeze({ name, mode: request.mode });
    row.active.push(request);
    this.events.push({ event: 'acquire', name, mode: request.mode, label: request.label, ...this._counts(row) });
    Promise.resolve()
      .then(() => request.callback(lock))
      .then(request.resolve, request.reject)
      .finally(() => {
        const idx = row.active.indexOf(request);
        if (idx >= 0) row.active.splice(idx, 1);
        this.events.push({ event: 'release', name, mode: request.mode, label: request.label, ...this._counts(row) });
        this._pump(name);
      });
  }
  request(name, options, callback) {
    if (typeof options === 'function') { callback = options; options = {}; }
    this.requestCalls += 1;
    const mode = options?.mode || 'exclusive';
    const label = options?.metadata?.op || options?.metadata?.label || mode;
    const row = this._row(name);
    this.events.push({ event: 'request', name, mode, label, hasSignal: Boolean(options?.signal), signalAborted: options?.signal?.aborted === true, ...this._counts(row) });
    return new Promise((resolve, reject) => {
      if (options?.signal?.aborted) {
        this.abortRejects += 1;
        this.events.push({ event: 'abort-before-queue', name, mode, label });
        reject(abortError());
        return;
      }
      const request = { name, mode, label, callback, resolve, reject, cleanup: null };
      if (options?.signal && typeof options.signal.addEventListener === 'function') {
        const onAbort = () => {
          if (this._removeQueued(name, row, request)) {
            this.abortRejects += 1;
            this.events.push({ event: 'abort-queued', name, mode, label, ...this._counts(row) });
            reject(abortError());
            this._pump(name);
          }
        };
        options.signal.addEventListener('abort', onAbort, { once: true });
        request.cleanup = () => { try { options.signal.removeEventListener('abort', onAbort); } catch {} };
      }
      row.queue.push(request);
      this._pump(name);
    });
  }
  async query() {
    const held = [];
    const pending = [];
    for (const [name, row] of this.rows.entries()) {
      held.push(...row.active.map((item) => ({ name, mode: item.mode, clientId: item.label })));
      pending.push(...row.queue.map((item) => ({ name, mode: item.mode, clientId: item.label })));
    }
    return { held, pending };
  }
}

class RecordingBlockStore {
  constructor(name = `${REVISION}-recording-guarded-abort-store`) {
    this.name = name;
    this.provider = 'recording-block-store';
    this.prefix = `${REVISION}/recording-guarded-abort`;
    this.calls = [];
    this.blocks = new Map();
    this.stats = { puts: 0, gets: 0, has: 0, deletes: 0, verifies: 0, estimates: 0, cleanupCalls: 0, providerAbortRejects: 0 };
    this.waitForAbortOnPut = false;
    this.lastPutEntered = null;
  }
  _signal(options = {}) { return options?.signal ?? options?.abortSignal ?? null; }
  _providerAbortError(signal) {
    const error = new Error('recording provider observed AbortSignal before mutation');
    error.name = 'RecordingProviderAbortError';
    error.code = 'BRT_FAKE_PROVIDER_ABORTED';
    error.detail = { signalAborted: signal?.aborted === true, reasonName: signal?.reason?.name || null, reasonMessage: signal?.reason?.message || String(signal?.reason ?? '') };
    return error;
  }
  async put(value, fields = {}, options = {}) {
    this.stats.puts += 1;
    const signal = this._signal(options);
    const call = { op: 'put', signalAborted: signal?.aborted === true, sameSignalFields: options.signal && options.signal === options.abortSignal, composite: options.guardedAbortSignalComposed === true || options.compositeAbortSignal === true, label: fields.label ?? null };
    this.calls.push(call);
    if (signal?.aborted) { this.stats.providerAbortRejects += 1; throw this._providerAbortError(signal); }
    if (this.waitForAbortOnPut) {
      let enteredResolve;
      this.lastPutEntered = new Promise((resolve) => { enteredResolve = resolve; });
      enteredResolve(call);
      await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('recording provider did not receive composed AbortSignal')), 500);
        signal?.addEventListener('abort', () => {
          clearTimeout(timer);
          this.stats.providerAbortRejects += 1;
          reject(this._providerAbortError(signal));
        }, { once: true });
      });
    }
    const bytes = typeof value === 'string' ? new TextEncoder().encode(value).byteLength : value?.byteLength ?? 1;
    const digest = `sha256:${String(this.stats.puts).padStart(64, '0')}`;
    this.blocks.set(digest, { bytes, value });
    return Object.freeze({ ref: { id: digest, digest, hash: digest.slice(7), bytes, backend: this.provider, kind: 'block' }, digest, hash: digest.slice(7), bytes, duplicate: false, path: `${this.prefix}/${digest}.blk` });
  }
  async get(ref, options = {}) { this.stats.gets += 1; this.calls.push({ op: 'get', signalAborted: this._signal(options)?.aborted === true }); return new Uint8Array(0); }
  async has(ref, options = {}) { this.stats.has += 1; this.calls.push({ op: 'has', signalAborted: this._signal(options)?.aborted === true }); return this.blocks.has(String(ref?.digest || ref)); }
  async delete(ref, options = {}) { this.stats.deletes += 1; this.calls.push({ op: 'delete', signalAborted: this._signal(options)?.aborted === true }); return this.blocks.delete(String(ref?.digest || ref)); }
  async verify(ref, options = {}) { this.stats.verifies += 1; this.calls.push({ op: 'verify', signalAborted: this._signal(options)?.aborted === true }); return Object.freeze({ present: false, ok: false, digest: String(ref?.digest || ref), bytes: 0 }); }
  async estimate(options = {}) { this.stats.estimates += 1; this.calls.push({ op: 'estimate', signalAborted: this._signal(options)?.aborted === true }); return Object.freeze({ quota: null, usage: null, usageDetails: null }); }
  async cleanupForTest(options = {}) { this.stats.cleanupCalls += 1; this.calls.push({ op: 'cleanupForTest', signalAborted: this._signal(options)?.aborted === true }); this.blocks.clear(); return true; }
  snapshot() { return Object.freeze({ name: this.name, provider: this.provider, prefix: this.prefix, stats: { ...this.stats }, callCount: this.calls.length }); }
}

async function waitForPredicate(label, fn, { timeoutMs = 500, intervalMs = 5 } = {}) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const value = await fn();
    if (value) return value;
    await sleep(intervalMs);
  }
  throw new Error(`timed out waiting for ${label}`);
}

function summarizeError(error) {
  const detail = error?.detail || null;
  const recovery = error?.browserStorageRecovery || detail?.recovery || null;
  return Object.freeze({
    name: error?.name || 'Error',
    message: error?.message || String(error),
    code: error?.code ?? null,
    detail: detail ? Object.freeze({
      name: detail.name ?? null,
      label: detail.label ?? null,
      lockName: detail.lockName ?? detail.name ?? null,
      mode: detail.mode ?? null,
      timeoutMs: detail.timeoutMs ?? null,
      causeName: detail.causeName ?? null,
      acquired: detail.acquired ?? null,
      preMutationRejected: detail.preMutationRejected === true,
      recovery: recovery ? Object.freeze({
        code: recovery.code,
        category: recovery.category,
        phase: recovery.phase,
        action: recovery.action,
        preMutationRejected: recovery.preMutationRejected,
        mutationAttempted: recovery.mutationAttempted,
        shouldQueryLocks: recovery.shouldQueryLocks,
        mutationCommitted: recovery.mutationCommitted,
        op: recovery.op
      }) : null
    }) : null
  });
}

async function capture(label, fn) {
  try {
    return { label, ok: true, value: await fn() };
  } catch (error) {
    return { label, ok: false, error: summarizeError(error) };
  }
}

export async function runProbe() {
  const started = performance.now();
  const locks = new AbortableQueuedLocks();
  const store = new RecordingBlockStore();
  const traceEvents = [];
  const trace = { emit(kind, fields = {}) { traceEvents.push({ kind, ...fields }); }, snapshot() { return traceEvents.slice(); } };
  const guard = createWebLockGuardedBlockStore({ store, locks, lockPrefix: `browserrt:${REVISION}:guarded-abort`, lockName: `${REVISION}-guarded-abort`, label: `${REVISION}-guarded-abort-signal`, trace, lockTimeoutMs: 0 });

  let releaseHolder;
  const holder = guard.withExclusive(async () => {
    await new Promise((resolve) => { releaseHolder = resolve; });
    return 'holder-released';
  }, { op: 'abortSignal-holder' });
  await waitForPredicate('exclusive holder', async () => (await locks.query()).held.length === 1);

  const queuedAbort = new AbortController();
  const queuedPutPromise = capture('queued-put-abortSignal-only', () => guard.put('must-not-enter-store', { label: 'queued-put-abortSignal-only' }, { abortSignal: queuedAbort.signal }));
  await waitForPredicate('queued put pending lock', async () => (await locks.query()).pending.length === 1);
  queuedAbort.abort(new Error('operator-cancelled-pending-guarded-put'));
  const queuedPut = await queuedPutPromise;
  const whileHeldAfterAbort = await locks.query();
  assert.equal(queuedPut.ok, false, 'queued abortSignal-only guarded put should reject');
  assert.equal(queuedPut.error.code, 'BRT_WEB_LOCK_ABORTED', 'abortSignal-only pending guarded put should reject at Web Lock boundary');
  assert.equal(store.stats.puts, 0, 'pending abortSignal-only guarded put must not enter provider');
  assert.equal(whileHeldAfterAbort.held.length, 1, 'holder should still be held when queued abort drains');
  assert.equal(whileHeldAfterAbort.pending.length, 0, 'abortSignal-only queued put should be removed while holder remains active');
  releaseHolder();
  assert.equal(await holder, 'holder-released');

  let releaseSharedHolder;
  const sharedHolder = guard.withExclusive(async () => {
    await new Promise((resolve) => { releaseSharedHolder = resolve; });
  }, { op: 'custom-holder' });
  await waitForPredicate('custom holder', async () => (await locks.query()).held.length === 1);
  let customCallbackEntered = false;
  const customAbort = new AbortController();
  const customPromise = capture('withShared-abortSignal-only', () => guard.withShared(async () => { customCallbackEntered = true; return 'bad'; }, { op: 'queued-custom-shared' }, { abortSignal: customAbort.signal }));
  await waitForPredicate('queued custom shared pending lock', async () => (await locks.query()).pending.length === 1);
  customAbort.abort(new Error('operator-cancelled-pending-custom-shared'));
  const custom = await customPromise;
  assert.equal(custom.ok, false, 'withShared abortSignal-only should reject while pending');
  assert.equal(custom.error.code, 'BRT_WEB_LOCK_ABORTED');
  assert.equal(custom.error.detail?.recovery?.code, 'BRT_WEB_LOCK_ABORTED', 'custom withShared abort must carry attached recovery guidance');
  assert.equal(custom.error.detail?.recovery?.category, 'lock-abort', 'custom withShared abort recovery must classify lock-abort');
  assert.equal(custom.error.detail?.preMutationRejected, true, 'custom withShared abort recovery must preserve pre-mutation rejection');
  assert.equal(customCallbackEntered, false, 'custom callback must not run after abortSignal-only pending cancellation');
  releaseSharedHolder();
  await sharedHolder;

  store.waitForAbortOnPut = true;
  const liveSignal = new AbortController();
  const abortSignal = new AbortController();
  const providerAbortPromise = capture('dual-signal-provider-abort', () => guard.put('provider-composite-abort', { label: 'dual-signal-provider-abort' }, { signal: liveSignal.signal, abortSignal: abortSignal.signal }));
  await store.lastPutEntered;
  abortSignal.abort(new Error('abortSignal-aborted-after-lock-acquired'));
  const providerAbort = await providerAbortPromise;
  assert.equal(providerAbort.ok, false, 'abortSignal should abort provider even when signal is live');
  assert.equal(providerAbort.error.code, 'BRT_FAKE_PROVIDER_ABORTED');
  const providerCall = store.calls.find((row) => row.label === 'dual-signal-provider-abort');
  assert.equal(providerCall.sameSignalFields, true, 'provider should receive composed signal as signal and abortSignal');
  assert.equal(providerCall.composite, true, 'provider options should mark guarded abort composition');
  store.waitForAbortOnPut = false;

  const requestCallsBeforeInvalid = locks.requestCalls;
  const invalid = await capture('invalid-abortSignal-shape', () => guard.has('sha256:' + '0'.repeat(64), { abortSignal: { aborted: false, addEventListener() {}, removeEventListener() {} } }));
  assert.equal(invalid.ok, false, 'invalid abortSignal shape should reject');
  assert.equal(invalid.error.code, 'BRT_WEB_LOCK_SIGNAL_INVALID');
  assert.equal(locks.requestCalls, requestCallsBeforeInvalid, 'invalid abortSignal must reject before locks.request is called');

  const success = await guard.put('normal-guarded-success', { label: 'normal-guarded-success' });
  assert.equal(success.duplicate, false);
  const settled = await guard.waitForSettled({ timeoutMs: 200, intervalMs: 5 });
  assert.equal(settled.ok, true);

  const requestCallsBeforeCloseReject = locks.requestCalls;
  await guard.closeAsync({ reason: 'rev0167-closed-recovery-preflight' });
  const closedPut = await capture('closed-guard-put', () => guard.put('after-close-must-not-enter-store', { label: 'closed-guard-put' }));
  assert.equal(closedPut.ok, false, 'closed guarded store should reject put');
  assert.equal(closedPut.error.code, 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED');
  assert.equal(closedPut.error.detail?.recovery?.category, 'guard-lifecycle-closed', 'closed guard recovery must classify lifecycle close');
  assert.equal(closedPut.error.detail?.recovery?.preMutationRejected, true, 'closed guard recovery must be pre-mutation');
  assert.equal(closedPut.error.detail?.recovery?.mutationAttempted, false, 'closed guard recovery must not claim provider mutation');
  assert.equal(closedPut.error.detail?.recovery?.mutationCommitted, false, 'closed guard recovery must not claim mutation commit');
  assert.equal(closedPut.error.detail?.recovery?.op, 'put', 'closed guard recovery must carry rejected op');
  assert.equal(locks.requestCalls, requestCallsBeforeCloseReject, 'closed guard reject must not call locks.request');

  const snapshot = guard.snapshot();
  const traceSnapshot = trace.snapshot();
  const traceKinds = traceSnapshot.map((row) => row.kind);
  assert.ok(traceKinds.includes('storage:opfs-web-lock-guard-abort-signal'), 'guard should trace abort-signal aware operations');
  assert.ok(traceKinds.includes('coord:web-lock-aborted'), 'coordinator should trace pending abort');
  assert.ok(traceKinds.includes('storage:opfs-web-lock-guard-custom-error'), 'custom withExclusive/withShared failures should emit a guarded custom error trace');
  assert.ok(traceSnapshot.some((row) => row.kind === 'storage:opfs-web-lock-guard-recovery-guidance' && row.recovery?.op === 'custom-shared' && row.recovery?.code === 'BRT_WEB_LOCK_ABORTED'), 'custom withShared abort should emit recovery guidance trace');
  assert.ok(traceSnapshot.some((row) => row.kind === 'storage:opfs-web-lock-guard-closed-reject' && row.recovery?.code === 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED'), 'closed guard reject should emit recovery guidance on the closed-reject trace');
  assert.ok(traceSnapshot.some((row) => row.kind === 'storage:opfs-web-lock-guard-recovery-guidance' && row.recovery?.category === 'guard-lifecycle-closed'), 'closed guard reject should emit the shared recovery guidance trace');
  assert.ok(snapshot.stats.abortSignalOperations >= 4, 'guard should count abort-signal operations');
  assert.ok(snapshot.stats.compositeAbortSignals >= 1, 'guard should count composite direct signal/abortSignal operations');
  assert.ok(snapshot.stats.invalidAbortSignalsPreserved >= 1, 'guard should preserve invalid abortSignal shape for coordinator validation');
  assert.equal(snapshot.coordinator.stats.aborted >= 2, true, 'coordinator should count pending aborts');
  assert.equal(snapshot.coordinator.stats.optionRejected >= 1, true, 'coordinator should count invalid abortSignal option rejection');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-web-lock-guarded-abort-signal-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake Web Locks proof that direct WebLockGuardedBlockStore operations compose signal/abortSignal for lock acquisition/provider calls, pending aborts cancel before provider mutation, custom withExclusive/withShared failures carry recovery guidance, and closed guards reject locally before locks.request.',
    observations: { queuedPut, whileHeldAfterAbort, custom, providerAbort, invalid, success: { digest: success.digest, bytes: success.bytes }, closedPut, storeCalls: store.calls, fakeLockEvents: locks.events, snapshot, traceKinds, settled },
    claimsChecked: [
      'abortSignal-only guarded put cancels while pending on the Web Lock and does not enter the provider',
      'abortSignal-only withShared custom callback cancels while pending, does not run the callback, and carries recovery guidance',
      'custom withExclusive/withShared failures emit guarded recovery traces rather than becoming invisible raw coordinator failures',
      'dual signal + abortSignal direct guarded put composes both sources and forwards the composed signal to provider options',
      'invalid abortSignal shapes are not masked by a sibling signal and reject before locks.request',
      'closed guarded store operations reject before locks.request/provider mutation with structured recovery guidance',
      'normal guarded put remains usable after abort/error paths until the guard lifecycle is closed'
    ],
    nonClaims: [
      'Release-tier fake-lock proof only; browser Web Locks and real OPFS behavior are covered by the managed Chromium proof.',
      'Abort remains cooperative after lock acquisition; providers that ignore AbortSignal can still mutate or settle late.',
      'No cross-browser conformance, OPFS durability, quota/eviction survival, fsync, crash recovery, Web Locks fairness, or production-readiness claim.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-web-lock-guarded-abort-signal-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, code: error?.code ?? null, detail: error?.detail ?? null }, nonClaims: ['Failed guarded abortSignal proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[web_lock_guarded_abort_signal_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
