#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, createWebLockGuardedBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'opfs:block-store-guarded-staged-recovery-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-GUARDED-STAGED-RECOVERY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

function makeAbortError(message = 'Fake Web Lock request aborted before acquisition') {
  if (typeof DOMException === 'function') return new DOMException(message, 'AbortError');
  const error = new Error(message);
  error.name = 'AbortError';
  return error;
}

class QueuedFakeWebLocks {
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
    req.reject(makeAbortError());
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
    this.events.push({ event: 'acquire', name, mode: req.mode, label: req.label, counts: this._counts(row), queued: row.queue.length });
    const lock = Object.freeze({ name, mode: req.mode });
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
      if (signal?.aborted) { reject(makeAbortError('Fake Web Lock request already aborted')); return; }
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

function deferred(label = 'deferred') {
  let settled = false;
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return {
    label,
    promise,
    resolve(value) { if (!settled) { settled = true; resolve(value); } },
    reject(error) { if (!settled) { settled = true; reject(error); } },
    get settled() { return settled; }
  };
}

function payloadOf(label, size = 4096) {
  const bytes = new Uint8Array(size);
  const header = new TextEncoder().encode(`BrowserRT ${REVISION} guarded staged recovery proof ${label}`);
  bytes.set(header);
  for (let i = header.length; i < bytes.length; i += 1) bytes[i] = (label.charCodeAt(i % label.length) + i * 23 + (i >>> 3)) & 255;
  return bytes;
}

function makeStagedCloseGate({ releaseAfter = 1 } = {}) {
  const stagedCloses = [];
  const closed = deferred('staged-close-count');
  const release = deferred('release-staged-close');
  const hooks = {
    async onClose({ file, bytes }) {
      if (!String(file?.name || '').includes('.brt-stage-')) return;
      stagedCloses.push(Object.freeze({ name: file.name, path: file.path, bytes: bytes.byteLength }));
      if (stagedCloses.length >= releaseAfter) closed.resolve(Object.freeze([...stagedCloses]));
      await release.promise;
    }
  };
  return { hooks, stagedCloses, closed: closed.promise, release: release.resolve };
}

async function waitFor(predicate, { timeoutMs = 1000, intervalMs = 5, label = 'condition' } = {}) {
  const deadline = performance.now() + timeoutMs;
  while (performance.now() <= deadline) {
    if (await predicate()) return true;
    await sleep(intervalMs);
  }
  throw new Error(`timed out waiting for ${label}`);
}

function tmpFiles(tree) { return tree.files.filter((row) => row.path.endsWith('.tmp')); }
function blkFiles(tree) { return tree.files.filter((row) => row.path.endsWith('.blk')); }

async function runUnguardedRecoveryRaceCase() {
  const payload = payloadOf('unguarded-race', 5632);
  const prefix = `browserrt/${REVISION}/fake-guarded-staged-recovery/unguarded-race`;
  const traceA = new TraceLog({ maxEvents: 8192 });
  const traceB = new TraceLog({ maxEvents: 8192 });
  const gate = makeStagedCloseGate({ releaseAfter: 1 });
  return await withFakeNavigator(async (root) => {
    const writer = createOpfsAsyncBlockStore({ name: `${REVISION}-unguarded-writer`, prefix, trace: traceA });
    const recoveryStore = createOpfsAsyncBlockStore({ name: `${REVISION}-unguarded-recovery`, prefix, trace: traceB });
    const putPromise = writer.put(payload, { label: 'unguarded-live-put' });
    await gate.closed;
    const stagedTree = fakeTreeSummary(root);
    const recoveryWhileLive = await recoveryStore.recoverStagedWrites({ reason: 'probe-unguarded-race' });
    const afterRecoveryTree = fakeTreeSummary(root);
    gate.release();
    let putError = null;
    try { await putPromise; }
    catch (error) { putError = captureError(error); }
    const finalTree = fakeTreeSummary(root);
    return Object.freeze({ stagedTree, recoveryWhileLive, afterRecoveryTree, finalTree, putError, writerSnapshot: writer.snapshot(), recoverySnapshot: recoveryStore.snapshot(), writerTraceKinds: traceA.kinds(), recoveryTraceKinds: traceB.kinds() });
  }, { hooks: gate.hooks });
}

async function runGuardedRecoverySerializationCase() {
  const payload = payloadOf('guarded-serialized-recovery', 6144);
  const prefix = `browserrt/${REVISION}/fake-guarded-staged-recovery/guarded-serialized`;
  const traceA = new TraceLog({ maxEvents: 8192 });
  const traceB = new TraceLog({ maxEvents: 8192 });
  const locks = new QueuedFakeWebLocks();
  const gate = makeStagedCloseGate({ releaseAfter: 1 });
  return await withFakeNavigator(async (root) => {
    const rawWriter = createOpfsAsyncBlockStore({ name: `${REVISION}-guarded-writer-raw`, prefix, trace: traceA });
    const rawRecovery = createOpfsAsyncBlockStore({ name: `${REVISION}-guarded-recovery-raw`, prefix, trace: traceB });
    const guardA = createWebLockGuardedBlockStore({ store: rawWriter, locks, lockPrefix: 'browserrt:test-guarded-staged-recovery', lockName: `${REVISION}-same-prefix`, label: `${REVISION}-guarded-writer`, trace: traceA });
    const guardB = createWebLockGuardedBlockStore({ store: rawRecovery, locks, lockPrefix: 'browserrt:test-guarded-staged-recovery', lockName: `${REVISION}-same-prefix`, label: `${REVISION}-guarded-recovery`, trace: traceB });
    const putPromise = guardA.put(payload, { label: 'guarded-live-put' });
    await gate.closed;
    const stagedTree = fakeTreeSummary(root);
    assert.equal(tmpFiles(stagedTree).length, 1, 'guarded writer should expose one staged temp while held');
    assert.equal(blkFiles(stagedTree).length, 0, 'guarded writer must not publish final before staged gate release');
    const recoveryPromise = guardB.recoverStagedWrites({ reason: 'probe-guarded-recovery-waits' });
    await waitFor(async () => {
      const q = await locks.query();
      return q.pending.length > 0;
    }, { label: 'guarded recovery pending behind put lock' });
    const whileRecoveryPendingTree = fakeTreeSummary(root);
    assert.equal(tmpFiles(whileRecoveryPendingTree).length, 1, 'queued guarded recovery must not delete live staged temp before lock acquisition');
    gate.release();
    const committed = await putPromise;
    const recoveryAfterPut = await recoveryPromise;
    const afterTree = fakeTreeSummary(root);
    const readBack = await guardB.get(committed.ref);
    const lockEvents = Object.freeze([...locks.events]);
    const exclusiveEvents = lockEvents.map((row, idx) => ({ row, idx })).filter(({ row }) => row.mode === 'exclusive');
    const exclusiveRequests = exclusiveEvents.filter(({ row }) => row.event === 'request').map(({ idx }) => idx);
    const exclusiveAcquires = exclusiveEvents.filter(({ row }) => row.event === 'acquire').map(({ idx }) => idx);
    const exclusiveReleases = exclusiveEvents.filter(({ row }) => row.event === 'release').map(({ idx }) => idx);
    const putAcquireIdx = exclusiveAcquires[0] ?? -1;
    const recoveryRequestIdx = exclusiveRequests[1] ?? -1;
    const putReleaseIdx = exclusiveReleases[0] ?? -1;
    const recoveryAcquireIdx = exclusiveAcquires[1] ?? -1;
    const recoveryReleaseIdx = exclusiveReleases[1] ?? -1;
    return Object.freeze({ committed, stagedTree, whileRecoveryPendingTree, recoveryAfterPut, afterTree, readBackDigest: `sha256:${await digestBytesHex(readBack)}`, guardASnapshot: guardA.snapshot(), guardBSnapshot: guardB.snapshot(), rawWriterSnapshot: rawWriter.snapshot(), rawRecoverySnapshot: rawRecovery.snapshot(), lockEvents, lockOrder: { putAcquireIdx, recoveryRequestIdx, putReleaseIdx, recoveryAcquireIdx, recoveryReleaseIdx }, traceKindsA: traceA.kinds(), traceKindsB: traceB.kinds() });
  }, { hooks: gate.hooks });
}

export async function runProbe() {
  const started = performance.now();
  const unguardedRace = await runUnguardedRecoveryRaceCase();
  const guardedSerialization = await runGuardedRecoverySerializationCase();

  assert.equal(tmpFiles(unguardedRace.stagedTree).length, 1, 'unguarded setup should expose one staged temp while writer is held');
  assert.equal(unguardedRace.recoveryWhileLive.deleted, 1, 'unguarded second provider recovery demonstrates the race by deleting the live staged temp');
  assert.ok(unguardedRace.putError, 'unguarded writer should fail after another provider deletes its staged temp');
  assert.notEqual(unguardedRace.putError.code, null, 'unguarded failure should be classified');
  assert.equal(blkFiles(unguardedRace.finalTree).length, 0, 'unguarded failed live put must not leave a final canonical block');

  assert.equal(tmpFiles(guardedSerialization.stagedTree).length, 1, 'guarded setup should expose one staged temp while writer is held');
  assert.equal(tmpFiles(guardedSerialization.whileRecoveryPendingTree).length, 1, 'guarded queued recovery must leave staged temp untouched before lock acquisition');
  assert.equal(guardedSerialization.recoveryAfterPut.deleted, 0, 'guarded recovery runs after put cleanup and should have no staged temp to delete');
  assert.equal(guardedSerialization.recoveryAfterPut.candidates, 0, 'guarded recovery should see no staged candidates after put cleanup');
  assert.equal(tmpFiles(guardedSerialization.afterTree).length, 0, 'guarded path must not leak staged temps');
  assert.equal(blkFiles(guardedSerialization.afterTree).length, 1, 'guarded path should publish exactly one canonical block');
  assert.equal(guardedSerialization.readBackDigest, guardedSerialization.committed.digest, 'guarded committed block must read back through the recovery guard');
  assert.ok(guardedSerialization.lockOrder.putAcquireIdx >= 0, 'put lock acquisition missing');
  assert.ok(guardedSerialization.lockOrder.recoveryRequestIdx > guardedSerialization.lockOrder.putAcquireIdx, 'recovery should request while put lock is held');
  assert.ok(guardedSerialization.lockOrder.putReleaseIdx > guardedSerialization.lockOrder.recoveryRequestIdx, 'put should release after queued recovery request');
  assert.ok(guardedSerialization.lockOrder.recoveryAcquireIdx > guardedSerialization.lockOrder.putReleaseIdx, 'recovery must acquire only after put releases');
  assert.ok(guardedSerialization.guardBSnapshot.stats.stagedRecoveries >= 1, 'guarded recovery stat missing');
  assert.ok(guardedSerialization.traceKindsB.includes('storage:opfs-web-lock-guard-exclusive-start'), 'guarded recovery exclusive trace missing');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-guarded-staged-recovery-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS/fake-Web-Locks proof that staged recovery is unsafe across provider instances without coordination and that WebLockGuardedBlockStore.recoverStagedWrites serializes recovery behind guarded puts for the same prefix lock.',
    observations: { unguardedRace, guardedSerialization },
    claimsChecked: [
      'a second unguarded provider can delete a live staged temp owned by another provider instance and make the writer fail before final publish',
      'WebLockGuardedBlockStore exposes recoverStagedWrites and routes it through the same exclusive lock as put/delete/cleanupForTest',
      'guarded staged recovery queues behind an active guarded staged put instead of deleting its temp file',
      'after the guarded put releases and cleans its staged temp, guarded recovery sees no candidates and the canonical block remains readable'
    ],
    nonClaims: [
      'Fake OPFS and fake Web Locks only; no real browser matrix, power-loss, fsync, quota/eviction, or atomic rename claim.',
      'The guard works only when all provider instances use the same Web Lock name/prefix; direct raw providers remain intentionally uncoordinated.',
      'Web Locks aborts cancel pending acquisition, not arbitrary work after acquisition; provider operations still need their own cooperative abort checkpoints.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-guarded-staged-recovery-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: captureError(error) };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_guarded_staged_recovery_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
