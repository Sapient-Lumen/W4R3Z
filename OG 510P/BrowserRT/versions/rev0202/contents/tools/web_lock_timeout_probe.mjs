#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, digestBytesHex, REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-WEB-LOCK-TIMEOUT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function makeAbortError(message = 'The operation was aborted.') {
  if (typeof DOMException === 'function') return new DOMException(message, 'AbortError');
  const error = new Error(message);
  error.name = 'AbortError';
  return error;
}

class FakeWebLocksWithAbort {
  constructor() {
    this.state = new Map();
    this.events = [];
    this.maxExclusiveActive = 0;
    this.overlap = false;
  }
  _row(name) {
    if (!this.state.has(name)) this.state.set(name, { active: [], queue: [] });
    return this.state.get(name);
  }
  _activeCounts(row) {
    return {
      exclusive: row.active.filter((entry) => entry.mode === 'exclusive').length,
      shared: row.active.filter((entry) => entry.mode === 'shared').length
    };
  }
  _canAcquire(row, mode) {
    if (mode === 'exclusive') return row.active.length === 0;
    return !row.active.some((entry) => entry.mode === 'exclusive');
  }
  _pump(name) {
    const row = this._row(name);
    while (row.queue.length) {
      const next = row.queue[0];
      if (!this._canAcquire(row, next.mode)) return;
      row.queue.shift();
      this._acquire(name, row, next);
      if (next.mode === 'exclusive') return;
    }
  }
  _removeAbortListener(request) {
    if (request.signal && request.onAbort && typeof request.signal.removeEventListener === 'function') {
      try { request.signal.removeEventListener('abort', request.onAbort); } catch {}
    }
    request.onAbort = null;
  }
  _abortQueued(name, request) {
    const row = this._row(name);
    const idx = row.queue.indexOf(request);
    if (idx >= 0) row.queue.splice(idx, 1);
    this._removeAbortListener(request);
    this.events.push({ event: 'abort', name, mode: request.mode, label: request.label, active: this._activeCounts(row), queued: row.queue.length });
    request.reject(makeAbortError('Fake Web Lock request aborted before acquisition'));
  }
  _acquire(name, row, request) {
    this._removeAbortListener(request);
    const lock = Object.freeze({ name, mode: request.mode });
    row.active.push(request);
    const counts = this._activeCounts(row);
    this.maxExclusiveActive = Math.max(this.maxExclusiveActive, counts.exclusive);
    if (counts.exclusive > 1 || (counts.exclusive === 1 && counts.shared > 0)) this.overlap = true;
    this.events.push({ event: 'acquire', name, mode: request.mode, label: request.label, active: counts, queued: row.queue.length });
    Promise.resolve()
      .then(() => request.callback(lock))
      .then(request.resolve, request.reject)
      .finally(() => {
        const idx = row.active.indexOf(request);
        if (idx >= 0) row.active.splice(idx, 1);
        this.events.push({ event: 'release', name, mode: request.mode, label: request.label, active: this._activeCounts(row), queued: row.queue.length });
        this._pump(name);
      });
  }
  request(name, options, callback) {
    if (typeof options === 'function') { callback = options; options = {}; }
    const mode = options?.mode || 'exclusive';
    const label = options?.metadata?.op || options?.metadata?.label || mode;
    const signal = options?.signal || null;
    const row = this._row(name);
    this.events.push({ event: 'request', name, mode, label, active: this._activeCounts(row), queued: row.queue.length, hasSignal: Boolean(signal) });
    return new Promise((resolve, reject) => {
      const request = { mode, label, callback, resolve, reject, signal, onAbort: null };
      if (signal?.aborted) {
        this.events.push({ event: 'abort-before-queue', name, mode, label, active: this._activeCounts(row), queued: row.queue.length });
        reject(makeAbortError('Fake Web Lock request was already aborted'));
        return;
      }
      if (signal && typeof signal.addEventListener === 'function') {
        request.onAbort = () => this._abortQueued(name, request);
        signal.addEventListener('abort', request.onAbort, { once: true });
      }
      row.queue.push(request);
      this._pump(name);
    });
  }
  async query() {
    const held = [];
    const pending = [];
    for (const [name, row] of this.state.entries()) {
      held.push(...row.active.map((entry) => ({ name, mode: entry.mode, clientId: entry.label })));
      pending.push(...row.queue.map((entry) => ({ name, mode: entry.mode, clientId: entry.label })));
    }
    return { held, pending };
  }
}

export async function runProbe() {
  const locks = new FakeWebLocksWithAbort();
  const rt = await boot({ webLockTimeoutProof: true });
  const store = rt.blockStore({ name: `${REVISION}-fake-timeout-lock-store` });
  const guard = rt.opfsWebLockGuardedBlockStore({
    store,
    locks,
    lockPrefix: 'browserrt:test-web-lock-timeout',
    lockName: `${REVISION}-bounded-wait`,
    label: `${REVISION}-fake-web-lock-timeout-guard`,
    lockTimeoutMs: 18
  });

  const events = [];
  const record = (event, fields = {}) => events.push({ event, t: Date.now(), ...fields });
  let releaseHold;
  const holdReleased = new Promise((resolve) => { releaseHold = resolve; });
  let holderEntered = false;
  const holder = guard.withExclusive(async () => {
    holderEntered = true;
    record('holder-enter');
    await holdReleased;
    record('holder-exit');
    return 'released';
  }, { op: 'timeout-holder' });

  const deadline = Date.now() + 250;
  while (!holderEntered && Date.now() < deadline) await sleep(1);
  assert.equal(holderEntered, true, 'holder lock should enter before timeout candidate is queued');

  const timeoutPayload = 'timeout-candidate-should-not-write';
  const timeoutHash = await digestBytesHex(new TextEncoder().encode(timeoutPayload));
  let timeoutError = null;
  try {
    await guard.put(timeoutPayload, { label: 'timeout-candidate' });
  } catch (error) {
    timeoutError = error;
    record('timeout-error', { name: error.name, code: error.code, message: error.message });
  }
  assert.equal(timeoutError?.code, 'BRT_WEB_LOCK_TIMEOUT');
  releaseHold();
  const holderResult = await holder;

  const timeoutPresent = await guard.has(`sha256:${timeoutHash}`);
  const recoveryPut = await guard.put('post-timeout-recovery-write', { label: 'post-timeout-recovery' }, { timeoutMs: 100 });
  const recoveryVerify = await guard.verify(recoveryPut.ref, { timeoutMs: 100 });
  const query = await guard.coordinator.query();
  const normalizedQuery = await guard.coordinator.queryLocks(guard.fullLockName);
  const settled = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 100, intervalMs: 5 });
  const snapshot = guard.snapshot();
  const trace = rt.trace.snapshot();
  const closeTrace = rt.close();

  assert.equal(holderResult, 'released');
  assert.equal(timeoutPresent, false, 'timed-out put callback must not have mutated the store');
  assert.equal(recoveryVerify.ok, true, 'guarded store should recover after a queued request timeout');
  assert.equal(query.held.length, 0);
  assert.equal(query.pending.length, 0);
  assert.equal(normalizedQuery.heldCount, 0);
  assert.equal(normalizedQuery.pendingCount, 0);
  assert.equal(settled.ok, true);
  assert.equal(snapshot.coordinator.stats.timeouts, 1);
  assert.equal(snapshot.stats.errors, 1);
  for (const kind of ['coord:web-lock-timeout-arm', 'coord:web-lock-timeout-fired', 'coord:web-lock-timeout', 'storage:opfs-web-lock-guard-op-error']) {
    assert.ok(trace.some((event) => event.kind === kind), `missing timeout trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-web-lock-timeout-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Release-tier fake-lock proof that WebLockCoordinator/WebLockGuardedBlockStore bound pending Web Lock waits with AbortSignal-backed timeout behavior, reject with BRT_WEB_LOCK_TIMEOUT before mutation, clear pending state, and recover for later guarded writes.',
    observations: {
      timeoutMs: guard.lockTimeoutMs,
      timeoutError: { name: timeoutError.name, code: timeoutError.code, message: timeoutError.message, detail: timeoutError.detail },
      timeoutHash: `sha256:${timeoutHash}`,
      timeoutPresent,
      recoveryPut: { digest: recoveryPut.digest, bytes: recoveryPut.bytes },
      recoveryVerify,
      query,
      normalizedQuery,
      settled,
      holderResult,
      events,
      fakeLockEvents: locks.events,
      snapshot,
      traceKinds: trace.map((event) => event.kind),
      closeTraceKinds: closeTrace.map((event) => event.kind)
    },
    claimsChecked: [
      'a pending guarded mutation waits behind an already-held exclusive Web Lock',
      'the pending request aborts with BRT_WEB_LOCK_TIMEOUT before entering the mutation callback',
      'the timed-out payload is absent from the wrapped block store',
      'held/pending fake lock state is empty after the holder releases and normalized query/wait-settled helpers agree',
      'a subsequent guarded write succeeds after the timeout'
    ],
    nonClaims: [
      'Release-tier fake-lock timeout proof only; browser AbortSignal/Web Locks behavior is covered by the explicit browser timeout proof.',
      'Timeout bounds lock acquisition only; it does not cancel a callback after the lock has already been granted.',
      'No fairness, starvation-freedom, multi-tab lifecycle, cross-browser, OPFS durability, quota, eviction, fsync, or production exactly-once claim.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-web-lock-timeout-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed fake-lock timeout proof is not a browser Web Locks or OPFS claim.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[web_lock_timeout_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
