#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-WEB-LOCK-GUARDED-BLOCK-STORE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

class FakeWebLocks {
  constructor() {
    this.state = new Map();
    this.events = [];
    this.maxExclusiveActive = 0;
    this.maxSharedActive = 0;
    this.overlap = false;
  }
  _row(name) {
    if (!this.state.has(name)) this.state.set(name, { active: [], queue: [] });
    return this.state.get(name);
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
  _activeCounts(row) {
    return {
      exclusive: row.active.filter((entry) => entry.mode === 'exclusive').length,
      shared: row.active.filter((entry) => entry.mode === 'shared').length
    };
  }
  _acquire(name, row, request) {
    const lock = Object.freeze({ name, mode: request.mode });
    row.active.push(request);
    const counts = this._activeCounts(row);
    this.maxExclusiveActive = Math.max(this.maxExclusiveActive, counts.exclusive);
    this.maxSharedActive = Math.max(this.maxSharedActive, counts.shared);
    if (counts.exclusive > 1 || (counts.exclusive === 1 && counts.shared > 0)) this.overlap = true;
    this.events.push({ event: 'acquire', name, mode: request.mode, label: request.label, active: counts });
    Promise.resolve()
      .then(() => request.callback(lock))
      .then(request.resolve, request.reject)
      .finally(() => {
        const idx = row.active.indexOf(request);
        if (idx >= 0) row.active.splice(idx, 1);
        this.events.push({ event: 'release', name, mode: request.mode, label: request.label, active: this._activeCounts(row) });
        this._pump(name);
      });
  }
  request(name, options, callback) {
    if (typeof options === 'function') { callback = options; options = {}; }
    const mode = options?.mode || 'exclusive';
    const label = options?.metadata?.op || options?.metadata?.label || mode;
    const row = this._row(name);
    this.events.push({ event: 'request', name, mode, label, active: this._activeCounts(row), queued: row.queue.length });
    return new Promise((resolve, reject) => {
      const request = { mode, label, callback, resolve, reject };
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
  const locks = new FakeWebLocks();
  const rt = await boot({ blockStoreProbe: true });
  const store = rt.blockStore({ name: `${REVISION}-fake-lock-guard-store` });
  const guard = rt.opfsWebLockGuardedBlockStore({
    store,
    locks,
    lockPrefix: 'browserrt:test-web-lock-guard',
    lockName: `${REVISION}-contention`,
    label: `${REVISION}-fake-web-lock-guard`
  });

  const events = [];
  const record = (event, fields = {}) => events.push({ event, t: Date.now(), ...fields });
  let activeExclusive = 0;
  let maxActiveExclusive = 0;
  let exclusiveOverlap = false;

  const slow = guard.withExclusive(async () => {
    activeExclusive += 1;
    maxActiveExclusive = Math.max(maxActiveExclusive, activeExclusive);
    if (activeExclusive > 1) exclusiveOverlap = true;
    record('slow-enter');
    await sleep(8);
    const put = await store.put('slow-web-lock-guarded-block', { label: 'slow-direct-under-lock' });
    await sleep(8);
    record('slow-exit', { digest: put.digest });
    activeExclusive -= 1;
    return put;
  }, { op: 'slow-held-put' });
  await sleep(1);
  const fast = guard.put('fast-web-lock-guarded-block', { label: 'fast-guarded-put' }).then((put) => { record('fast-done', { digest: put.digest }); return put; });
  const [slowPut, fastPut] = await Promise.all([slow, fast]);

  let activeShared = 0;
  let maxActiveShared = 0;
  let releaseShared;
  const sharedRelease = new Promise((resolve) => { releaseShared = resolve; });
  const sharedA = guard.withShared(async () => {
    activeShared += 1;
    maxActiveShared = Math.max(maxActiveShared, activeShared);
    if (activeShared >= 2) releaseShared();
    await Promise.race([sharedRelease, sleep(40)]);
    activeShared -= 1;
    return 'shared-a';
  }, { op: 'shared-a' });
  const sharedB = guard.withShared(async () => {
    activeShared += 1;
    maxActiveShared = Math.max(maxActiveShared, activeShared);
    if (activeShared >= 2) releaseShared();
    await Promise.race([sharedRelease, sleep(40)]);
    activeShared -= 1;
    return 'shared-b';
  }, { op: 'shared-b' });
  const sharedResults = await Promise.all([sharedA, sharedB]);

  const fastGet = await guard.get(fastPut.ref);
  const slowVerify = await guard.verify(slowPut.ref);
  const query = await guard.coordinator.query();
  const normalizedQuery = await guard.coordinator.queryLocks(guard.fullLockName);
  const settled = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 200, intervalMs: 5 });
  const snapshot = guard.snapshot();
  const trace = rt.trace.snapshot();
  const closeTrace = rt.close();

  const acquisitionLabels = locks.events.filter((row) => row.event === 'acquire').map((row) => row.label);
  const exclusiveAcquireCount = locks.events.filter((row) => row.event === 'acquire' && row.mode === 'exclusive').length;
  const slowExit = events.find((row) => row.event === 'slow-exit');
  const fastDone = events.find((row) => row.event === 'fast-done');
  assert.equal(guard.available, true);
  assert.equal(exclusiveOverlap, false);
  assert.equal(maxActiveExclusive, 1);
  assert.equal(locks.maxExclusiveActive, 1);
  assert.equal(locks.overlap, false);
  assert.ok(exclusiveAcquireCount >= 2, 'slow custom hold and guarded put should both acquire exclusive locks');
  assert.ok(slowExit && fastDone && fastDone.t >= slowExit.t, 'guarded put should complete only after slow held lock exits');
  assert.ok(maxActiveShared >= 2, 'shared guard calls should co-hold');
  assert.equal(fastGet.byteLength, 'fast-web-lock-guarded-block'.length);
  assert.equal(slowVerify.ok, true);
  assert.equal(query.held.length, 0);
  assert.equal(query.pending.length, 0);
  assert.equal(normalizedQuery.heldCount, 0);
  assert.equal(normalizedQuery.pendingCount, 0);
  assert.equal(settled.ok, true);
  for (const kind of ['coord:web-lock-request', 'coord:web-lock-acquired', 'coord:web-lock-release', 'coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete', 'storage:opfs-web-lock-guard-create', 'storage:opfs-web-lock-guard-op-start', 'storage:opfs-web-lock-guard-op-complete']) {
    assert.ok(trace.some((event) => event.kind === kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-web-lock-guarded-block-store-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Release-tier fake-lock proof for WebLockGuardedBlockStore: exclusive mutation calls serialize, shared read-like calls can co-hold, lock trace evidence is emitted, and the wrapper remains testable without launching Chromium.',
    observations: {
      slowPut: { digest: slowPut.digest, bytes: slowPut.bytes },
      fastPut: { digest: fastPut.digest, bytes: fastPut.bytes },
      fastGetBytes: fastGet.byteLength,
      slowVerify,
      exclusive: { maxActiveExclusive, exclusiveOverlap, fakeMaxExclusiveActive: locks.maxExclusiveActive, acquisitionLabels, exclusiveAcquireCount },
      shared: { maxActiveShared, sharedResults },
      query,
      normalizedQuery,
      settled,
      events,
      fakeLockEvents: locks.events,
      snapshot,
      traceKinds: trace.map((event) => event.kind),
      closeTraceKinds: closeTrace.map((event) => event.kind)
    },
    claimsChecked: [
      'WebLockGuardedBlockStore emits lock/operation trace evidence',
      'exclusive guarded calls for one lock name do not overlap',
      'a guarded put waits behind an already-held exclusive lock',
      'shared guarded calls can co-hold when no exclusive mutation is active',
      'read/verify paths still reach the wrapped block-store provider'
    ],
    nonClaims: [
      'Fake-lock release proof only; browser Web Locks behavior is proved by explicit browser tier.',
      'No OPFS durability, fsync, quota, eviction, crash, background-lifecycle, fairness, or cross-browser claim.',
      'No multi-tab production exactly-once claim; this is a wrapper/coordination contract guard.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-web-lock-guarded-block-store-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed fake-lock guarded-store probe is not a browser storage claim.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[web_lock_guarded_block_store_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
