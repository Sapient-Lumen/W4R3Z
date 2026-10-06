#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { boot, createCrossLaneScheduler, digestBytesHex, REVISION, VERSION, validateBlockStoreLaneAdapterSnapshot } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-STORAGE-LANE-WEB-LOCK-SETTLED-RECOVERY-PROBE.json`;
const TASK_ID = 'scheduler:storage-lane-web-lock-settled-recovery-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function makeAbortError(message = 'The operation was aborted.') {
  if (typeof DOMException === 'function') return new DOMException(message, 'AbortError');
  const error = new Error(message);
  error.name = 'AbortError';
  return error;
}

class FakeWebLocksWithQuery {
  constructor() { this.state = new Map(); this.events = []; }
  _row(name) {
    if (!this.state.has(name)) this.state.set(name, { active: [], queue: [] });
    return this.state.get(name);
  }
  _counts(row) {
    return { exclusive: row.active.filter((entry) => entry.mode === 'exclusive').length, shared: row.active.filter((entry) => entry.mode === 'shared').length };
  }
  _canAcquire(row, mode) {
    if (mode === 'exclusive') return row.active.length === 0;
    return !row.active.some((entry) => entry.mode === 'exclusive');
  }
  _removeAbortListener(req) {
    if (req.signal && req.onAbort && typeof req.signal.removeEventListener === 'function') {
      try { req.signal.removeEventListener('abort', req.onAbort); } catch {}
    }
    req.onAbort = null;
  }
  _abortQueued(name, req) {
    const row = this._row(name);
    const idx = row.queue.indexOf(req);
    if (idx >= 0) row.queue.splice(idx, 1);
    this._removeAbortListener(req);
    this.events.push({ event: 'abort', name, mode: req.mode, label: req.label, counts: this._counts(row), queued: row.queue.length });
    req.reject(makeAbortError('Fake Web Lock request aborted before acquisition'));
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
  _acquire(name, row, req) {
    this._removeAbortListener(req);
    row.active.push(req);
    const lock = Object.freeze({ name, mode: req.mode });
    this.events.push({ event: 'acquire', name, mode: req.mode, label: req.label, counts: this._counts(row), queued: row.queue.length });
    Promise.resolve()
      .then(() => req.callback(lock))
      .then(req.resolve, req.reject)
      .finally(() => {
        const idx = row.active.indexOf(req);
        if (idx >= 0) row.active.splice(idx, 1);
        this.events.push({ event: 'release', name, mode: req.mode, label: req.label, counts: this._counts(row), queued: row.queue.length });
        this._pump(name);
      });
  }
  request(name, options, callback) {
    if (typeof options === 'function') { callback = options; options = {}; }
    const mode = options?.mode || 'exclusive';
    const label = options?.metadata?.op || options?.metadata?.label || mode;
    const signal = options?.signal || null;
    const row = this._row(name);
    this.events.push({ event: 'request', name, mode, label, counts: this._counts(row), queued: row.queue.length, hasSignal: Boolean(signal) });
    return new Promise((resolve, reject) => {
      const req = { mode, label, callback, resolve, reject, signal, onAbort: null };
      if (signal?.aborted) { reject(makeAbortError('Fake Web Lock already aborted')); return; }
      if (signal && typeof signal.addEventListener === 'function') {
        req.onAbort = () => this._abortQueued(name, req);
        signal.addEventListener('abort', req.onAbort, { once: true });
      }
      row.queue.push(req);
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
  const started = performance.now();
  const locks = new FakeWebLocksWithQuery();
  const rt = await boot({ webLockSettledRecoveryProof: true });
  const trace = rt.trace;
  const scheduler = createCrossLaneScheduler({
    label: `${REVISION}-settled-recovery-scheduler`,
    trace,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const rawStore = rt.blockStore({ name: `${REVISION}-settled-recovery-store` });
  const guard = rt.opfsWebLockGuardedBlockStore({
    store: rawStore,
    locks,
    lockPrefix: 'browserrt:test-web-lock-settled-recovery',
    lockName: `${REVISION}-guarded-lane-lock`,
    label: `${REVISION}-settled-recovery-guard`,
    lockTimeoutMs: 18
  });
  const adapter = rt.blockStoreLaneAdapter({ label: `${REVISION}-settled-recovery-adapter`, store: guard, scheduler, lane: 'storage' });

  let releaseHold;
  const holdReleased = new Promise((resolve) => { releaseHold = resolve; });
  let holderEntered = false;
  const holder = guard.withExclusive(async () => {
    holderEntered = true;
    trace.emit('test:settled-recovery-holder-enter');
    await holdReleased;
    trace.emit('test:settled-recovery-holder-exit');
    return 'released';
  }, { op: 'settled-recovery-holder' });

  const deadline = Date.now() + 250;
  while (!holderEntered && Date.now() < deadline) await sleep(1);
  assert.equal(holderEntered, true, 'holder must enter before scheduled put drains');

  const timeoutPayload = 'settled-recovery-timeout-candidate';
  const timeoutDigest = `sha256:${await digestBytesHex(new TextEncoder().encode(timeoutPayload))}`;
  const scheduledTimeout = adapter.schedulePut(timeoutPayload, { id: 'settled-recovery-timeout-put', priority: 'user-visible', label: 'timeout-behind-holder' });
  const timeoutDrain = await adapter.drain({ maxSteps: 2 });
  const timeoutResult = timeoutDrain.results.find((row) => row.opId === 'settled-recovery-timeout-put');
  const afterTimeout = adapter.snapshot();
  const unhealthyLane = afterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const rejectWhileUnhealthy = adapter.schedulePut('should-not-queue-before-settle-recovery', { id: 'reject-while-unhealthy', priority: 'user-visible' });
  const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 35, intervalMs: 5, reason: 'fake-holder-still-active' });

  releaseHold();
  const holderResult = await holder;
  const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 250, intervalMs: 5, reason: 'web-lock-settled-maintenance-recovery' });
  const recoveredSchedule = adapter.schedulePut('settled-recovery-success', { id: 'settled-recovery-success-put', priority: 'user-visible', label: 'after-settled-recovery' });
  const recoveryDrain = await adapter.drain({ maxSteps: 3 });
  const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'settled-recovery-success-put');
  const recoveredVerify = await guard.verify(recoveredResult.result.ref, { timeoutMs: 100 });
  const timeoutPresent = await guard.has(timeoutDigest, { timeoutMs: 100 });
  const finalLocks = await guard.queryLocks();
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.kinds();
  rt.close();

  assert.equal(scheduledTimeout.accepted, true);
  assert.equal(timeoutResult?.ok, false);
  assert.equal(timeoutResult?.error?.code, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(unhealthyLane?.healthy, false);
  assert.equal(unhealthyLane?.healthReason, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(rejectWhileUnhealthy.accepted, false);
  assert.equal(rejectWhileUnhealthy.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(rejectWhileUnhealthy.scheduler.noMutation, true);
  assert.equal(blockedRecovery.recovered, false);
  assert.equal(blockedRecovery.reason, 'store-coordination-still-contended');
  assert.equal(holderResult, 'released');
  assert.equal(settledRecovery.recovered, true);
  assert.equal(settledRecovery.recovery.healthy, true);
  assert.equal(recoveredSchedule.accepted, true);
  assert.equal(recoveredResult?.ok, true);
  assert.equal(recoveredVerify.ok, true);
  assert.equal(timeoutPresent, false);
  assert.equal(finalLocks.heldCount, 0);
  assert.equal(finalLocks.pendingCount, 0);
  assert.equal(validation.ok, true);
  for (const kind of ['block-store-lane:recover-settled-blocked', 'block-store-lane:recover-settled', 'storage:opfs-web-lock-guard-still-contended', 'storage:opfs-web-lock-guard-settled', 'crosslane:lane-healthy']) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-web-lock-settled-recovery-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-lock proof that a storage lane made unhealthy by BRT_WEB_LOCK_TIMEOUT does not reopen while the guarded Web Lock is still held, then reopens through an explicit settle-check maintenance recovery once the lock manager reports zero held/pending rows.',
    observations: { scheduledTimeout, timeoutResult, unhealthyLane, rejectWhileUnhealthy, blockedRecovery, holderResult, settledRecovery, recoveredSchedule, recoveredResult, recoveredVerify, timeoutDigest, timeoutPresent, finalLocks, finalSnapshot, validation, fakeLockEvents: locks.events, traceKinds },
    claimsChecked: [
      'BRT_WEB_LOCK_TIMEOUT still marks the storage lane unhealthy',
      'recoverWhenStoreSettled refuses recovery while the guarded store lock is held',
      'recoverWhenStoreSettled marks the lane healthy only after the guarded store reports zero held/pending lock rows',
      'a later scheduled put succeeds after explicit settled-lock maintenance recovery',
      'the timed-out candidate digest remains absent'
    ],
    nonClaims: [
      'Release-tier fake-lock proof only; browser same-origin tab lifecycle is covered by explicit managed Chromium proofs.',
      'Recovery is explicit/maintenance-driven, not an autonomous daemon or production liveness theorem.',
      'No fairness, starvation-freedom, cross-browser, OPFS durability, quota, eviction, fsync, or exactly-once production claim.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-web-lock-settled-recovery-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed fake-lock settled recovery proof is not a browser lifecycle or OPFS durability claim.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[storage_lane_web_lock_settled_recovery_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
