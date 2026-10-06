#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-WEB-LOCK-QUERY-SETTLED-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

class FakeWebLocksQueryable {
  constructor() {
    this.state = new Map();
    this.events = [];
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
  _counts(row) {
    return { held: row.active.length, pending: row.queue.length };
  }
  _acquire(name, row, request) {
    row.active.push(request);
    this.events.push({ event: 'acquire', name, mode: request.mode, clientId: request.clientId, ...this._counts(row) });
    Promise.resolve()
      .then(() => request.callback(Object.freeze({ name, mode: request.mode })))
      .then(request.resolve, request.reject)
      .finally(() => {
        const idx = row.active.indexOf(request);
        if (idx >= 0) row.active.splice(idx, 1);
        this.events.push({ event: 'release', name, mode: request.mode, clientId: request.clientId, ...this._counts(row) });
        this._pump(name);
      });
  }
  request(name, options, callback) {
    if (typeof options === 'function') { callback = options; options = {}; }
    const row = this._row(name);
    const mode = options?.mode || 'exclusive';
    const clientId = options?.metadata?.op || options?.metadata?.label || mode;
    this.events.push({ event: 'request', name, mode, clientId, ...this._counts(row) });
    return new Promise((resolve, reject) => {
      row.queue.push({ mode, clientId, callback, resolve, reject });
      this._pump(name);
    });
  }
  async query() {
    const held = [];
    const pending = [];
    for (const [name, row] of this.state.entries()) {
      held.push(...row.active.map((entry) => ({ name, mode: entry.mode, clientId: entry.clientId })));
      pending.push(...row.queue.map((entry) => ({ name, mode: entry.mode, clientId: entry.clientId })));
    }
    this.events.push({ event: 'query', held: held.length, pending: pending.length });
    return { held, pending };
  }
}

export async function runProbe() {
  const locks = new FakeWebLocksQueryable();
  const rt = await boot({ webLockQuerySettledProof: true });
  const coordinator = rt.webLockCoordinator({ locks, prefix: 'browserrt:test-web-lock-query-settled', label: `${REVISION}-query-settled-coordinator` });
  const logicalName = `${REVISION}-query-settled-lock`;
  const fullName = coordinator.lockName(logicalName);

  let releaseHolder;
  const holderReleased = new Promise((resolve) => { releaseHolder = resolve; });
  let holderEntered = false;
  const holder = coordinator.exclusive(logicalName, async () => {
    holderEntered = true;
    await holderReleased;
    return 'holder-released';
  }, { metadata: { op: 'query-settled-holder' } });

  const deadline = Date.now() + 250;
  while (!holderEntered && Date.now() < deadline) await sleep(1);
  assert.equal(holderEntered, true, 'holder should acquire before waiter is queued');

  let waiterEntered = false;
  const waiter = coordinator.exclusive(logicalName, async () => {
    waiterEntered = true;
    return 'waiter-ran';
  }, { metadata: { op: 'query-settled-waiter' } });

  await sleep(4);
  const during = await coordinator.queryLocks(logicalName);
  const settledDuringHold = await coordinator.waitForSettled(logicalName, { timeoutMs: 8, intervalMs: 2 });
  assert.equal(during.available, true);
  assert.equal(during.name, fullName);
  assert.equal(during.heldCount, 1);
  assert.equal(during.pendingCount, 1);
  assert.equal(during.held[0].mode, 'exclusive');
  assert.equal(during.pending[0].mode, 'exclusive');
  assert.equal(settledDuringHold.ok, false, 'waitForSettled should time out while holder remains active and waiter pending');
  assert.equal(waiterEntered, false, 'waiter must not enter before holder release');

  releaseHolder();
  const [holderResult, waiterResult] = await Promise.all([holder, waiter]);
  const settledAfterRelease = await coordinator.waitForSettled(fullName, { timeoutMs: 250, intervalMs: 2 });
  const finalQuery = await coordinator.queryLocks(fullName);
  const snapshot = coordinator.snapshot();
  const trace = rt.trace.snapshot();
  const closeTrace = rt.close();

  assert.equal(holderResult, 'holder-released');
  assert.equal(waiterResult, 'waiter-ran');
  assert.equal(waiterEntered, true);
  assert.equal(settledAfterRelease.ok, true);
  assert.equal(finalQuery.heldCount, 0);
  assert.equal(finalQuery.pendingCount, 0);
  assert.equal(snapshot.stats.waitSettledTimeouts, 1);
  for (const kind of ['coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-start', 'coord:web-lock-wait-settled-timeout', 'coord:web-lock-wait-settled-complete']) {
    assert.ok(trace.some((event) => event.kind === kind), `missing query/settled trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-web-lock-query-settled-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Release-tier fake-lock proof that WebLockCoordinator queryLocks()/waitForSettled() normalize held/pending rows, time out while a lock remains busy, and report empty state after release.',
    observations: { fullName, during, settledDuringHold, settledAfterRelease, finalQuery, holderResult, waiterResult, fakeLockEvents: locks.events, snapshot, traceKinds: trace.map((event) => event.kind), closeTraceKinds: closeTrace.map((event) => event.kind) },
    claimsChecked: [
      'queryLocks filters and normalizes held/pending Web Lock rows for one BrowserRT lock name',
      'waitForSettled returns a bounded timeout while a lock is held and another request is pending',
      'waitForSettled returns ok after the holder releases and queued waiter drains',
      'query/settled helper trace events are emitted for auditability'
    ],
    nonClaims: [
      'Release-tier fake-lock query proof only; browser lifecycle release is covered by the explicit Chromium tab-termination proof.',
      'No cross-browser Web Locks behavior, fairness, starvation freedom, mobile/background lifecycle, service-worker coordination, or distributed-lock claim.',
      'No OPFS durability, fsync, quota, eviction, crash recovery, persistent-storage retention, or production readiness claim.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-web-lock-query-settled-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed fake-lock query-settled proof is not browser lifecycle evidence.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[web_lock_query_settled_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
