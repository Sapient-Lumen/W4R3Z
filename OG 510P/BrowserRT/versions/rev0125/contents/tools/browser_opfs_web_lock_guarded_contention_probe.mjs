#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-GUARDED-CONTENTION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function workerSource() {
  return `
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const bytesFor = (text) => new TextEncoder().encode(text);
    self.onmessage = async (event) => {
      const cfg = event.data || {};
      const post = (eventName, fields = {}) => self.postMessage({ event: eventName, role: cfg.role, t: Math.round(performance.now() * 1000) / 1000, ...fields });
      try {
        post('worker-start');
        const mod = await import(cfg.browserRtUrl);
        const rt = await mod.boot({ opfsAsyncBlockStoreProof: true });
        const trace = rt.trace;
        const store = rt.opfsAsyncBlockStore({ name: cfg.role + '-opfs-store', prefix: cfg.prefix });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: cfg.lockPrefix, lockName: cfg.lockName, label: cfg.role + '-guard' });
        post('guard-ready', { available: guard.available, lockName: guard.fullLockName });
        const payload = bytesFor(cfg.payload);
        const put = await guard.withExclusive(async () => {
          post('acquired');
          if (cfg.holdBeforeMs) await sleep(cfg.holdBeforeMs);
          const result = await store.put(payload, { label: cfg.role });
          post('wrote', { digest: result.digest, bytes: result.bytes });
          if (cfg.holdAfterMs) await sleep(cfg.holdAfterMs);
          post('releasing', { digest: result.digest });
          return result;
        }, { op: cfg.role + '-exclusive-opfs-put', role: cfg.role });
        const verify = await guard.verify(put.ref);
        const snapshot = guard.snapshot();
        const traceSnapshot = trace.snapshot();
        rt.close();
        post('done', {
          put: { digest: put.digest, hash: put.hash, bytes: put.bytes, duplicate: put.duplicate, path: put.path, ref: put.ref },
          verify,
          snapshot,
          traceKinds: traceSnapshot.map((row) => row.kind),
          normalizedTrace: traceSnapshot.map((row) => ({ kind: row.kind, name: row.name, mode: row.mode, op: row.op, lockName: row.lockName, store: row.store, digest: row.digest, bytes: row.bytes, metadata: row.metadata })).filter((row) => row.kind)
        });
      } catch (error) {
        post('error', { error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack || null } });
      }
    };
  `;
}

function exprForPage(prefix, lockPrefix, lockName, slowHoldBeforeMs, slowHoldAfterMs) {
  const source = workerSource();
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const now = () => Math.round(performance.now() * 1000) / 1000;
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      webLocksQuery: typeof navigator.locks?.query === 'function',
      worker: typeof Worker === 'function',
      moduleWorker: typeof Worker === 'function',
      blob: typeof Blob === 'function',
      createObjectURL: typeof URL?.createObjectURL === 'function'
    };
    const mod = await import(browserRtUrl);
    const prepRt = await mod.boot({ opfsAsyncBlockStoreProof: true });
    const prepStore = prepRt.opfsAsyncBlockStore({ name: 'prep-main-store', prefix: ${JSON.stringify(prefix)} });
    const prepGuard = prepRt.opfsWebLockGuardedBlockStore({ store: prepStore, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'prep-main-guard' });
    const cleanupBefore = await prepGuard.cleanupForTest();
    const prepTrace = prepRt.trace.snapshot();
    prepRt.close();

    function createRunner(role, payload, holdBeforeMs, holdAfterMs) {
      const url = URL.createObjectURL(new Blob([${JSON.stringify(source)}], { type: 'text/javascript' }));
      const worker = new Worker(url, { type: 'module', name: 'browserrt-' + role + '-opfs-web-lock-worker' });
      const messages = [];
      const waiters = [];
      let doneResolve;
      let doneReject;
      const done = new Promise((resolve, reject) => { doneResolve = resolve; doneReject = reject; });
      function notify(row) {
        for (let i = waiters.length - 1; i >= 0; i -= 1) {
          const waiter = waiters[i];
          if (waiter.pred(row)) {
            waiters.splice(i, 1);
            clearTimeout(waiter.timer);
            waiter.resolve(row);
          }
        }
      }
      worker.onmessage = (event) => {
        const row = { ...event.data, receivedAt: now() };
        messages.push(row);
        notify(row);
        if (row.event === 'done') doneResolve(row);
        if (row.event === 'error') doneReject(new Error(row.error?.message || 'worker error'));
      };
      worker.onerror = (event) => doneReject(new Error(event.message || 'worker error'));
      const waitFor = (pred, timeoutMs = 2000) => new Promise((resolve, reject) => {
        for (const row of messages) if (pred(row)) return resolve(row);
        const timer = setTimeout(() => reject(new Error('timeout waiting for worker ' + role)), timeoutMs);
        waiters.push({ pred, resolve, reject, timer });
      });
      const start = () => worker.postMessage({ role, prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, browserRtUrl, payload, holdBeforeMs, holdAfterMs });
      const terminate = () => { try { worker.terminate(); } catch {} try { URL.revokeObjectURL(url); } catch {} };
      return { role, worker, messages, done, waitFor, start, terminate };
    }

    const slow = createRunner('slow', 'slow-worker-opfs-web-lock-contention-' + Math.random(), ${JSON.stringify(slowHoldBeforeMs)}, ${JSON.stringify(slowHoldAfterMs)});
    slow.start();
    const slowAcquired = await slow.waitFor((row) => row.event === 'acquired', 2500);
    const fast = createRunner('fast', 'fast-worker-opfs-web-lock-contention-' + Math.random(), 0, 0);
    fast.start();
    await sleep(Math.max(20, Math.min(${JSON.stringify(slowHoldBeforeMs)}, 80)));
    const fastAcquiredDuringSlowHold = fast.messages.some((row) => row.event === 'acquired');
    const slowReleasing = await slow.waitFor((row) => row.event === 'releasing', 2500);
    const fastAcquired = await fast.waitFor((row) => row.event === 'acquired', 2500);
    const [slowDone, fastDone] = await Promise.all([slow.done, fast.done]);
    slow.terminate();
    fast.terminate();

    const verifyRt = await mod.boot({ opfsAsyncBlockStoreProof: true });
    const verifyStore = verifyRt.opfsAsyncBlockStore({ name: 'verify-main-store', prefix: ${JSON.stringify(prefix)} });
    const verifyGuard = verifyRt.opfsWebLockGuardedBlockStore({ store: verifyStore, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'verify-main-guard' });
    const slowVerify = await verifyGuard.verify(slowDone.put.ref);
    const fastVerify = await verifyGuard.verify(fastDone.put.ref);
    const mainPut = await verifyGuard.put(new TextEncoder().encode('main-post-contention-guarded-put'), { label: 'main-post-contention' });
    const mainVerify = await verifyGuard.verify(mainPut.ref);
    const cleanupAfter = await verifyGuard.cleanupForTest();
    const verifySnapshot = verifyGuard.snapshot();
    const verifyTrace = verifyRt.trace.snapshot();
    const query = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    verifyRt.close();

    return JSON.stringify({
      project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities,
      prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, fullLockName: verifyGuard.fullLockName,
      cleanupBefore, slowAcquired, slowReleasing, fastAcquired, fastAcquiredDuringSlowHold,
      slow: { messages: slow.messages, done: slowDone },
      fast: { messages: fast.messages, done: fastDone },
      verification: { slowVerify, fastVerify, mainPut: { digest: mainPut.digest, bytes: mainPut.bytes, duplicate: mainPut.duplicate, path: mainPut.path, ref: mainPut.ref }, mainVerify, cleanupAfter, verifySnapshot },
      query: query ? { heldCount: query.held?.length ?? null, pendingCount: query.pending?.length ?? null } : null,
      traces: { prepKinds: prepTrace.map((row) => row.kind), verifyKinds: verifyTrace.map((row) => row.kind), slowKinds: slowDone.traceKinds, fastKinds: fastDone.traceKinds, verifyNormalized: verifyTrace.map((row) => ({ kind: row.kind, name: row.name, mode: row.mode, op: row.op, lockName: row.lockName, store: row.store, digest: row.digest, bytes: row.bytes, metadata: row.metadata })).filter((row) => row.kind) }
    });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-guarded-contention-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-guarded-contention';
  const lockName = options.lockName || `${REVISION}-shared-opfs-mutation-lock`;
  const slowHoldBeforeMs = Number(options.slowHoldBeforeMs || 140);
  const slowHoldAfterMs = Number(options.slowHoldAfterMs || 35);
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-web-lock-guarded-contention-probe.html',
    pageTitle: 'BrowserRT OPFS Web Lock guarded contention probe',
    profilePrefix: 'browserrt-opfs-web-lock-guard-',
    stderrTerms: ['opfs', 'lock', 'worker', 'storage']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, lockPrefix, lockName, slowHoldBeforeMs, slowHoldAfterMs), timeoutMs);
    mark('browser-opfs-web-lock-guarded-contention-eval', started);
    out._pageUrl = pageUrl;
    return out;
  });

  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.page.isSecureContext, true);
  assert.equal(observed.capabilities.opfs, true, 'OPFS must be available for guarded contention proof');
  assert.equal(observed.capabilities.webLocks, true, 'Web Locks must be available for guarded contention proof');
  assert.equal(observed.capabilities.worker, true, 'Dedicated workers must be available');
  assert.equal(typeof observed.cleanupBefore, 'boolean');
  assert.equal(observed.slowAcquired.event, 'acquired');
  assert.equal(observed.fastAcquiredDuringSlowHold, false, 'fast worker must not acquire while slow worker holds the same lock');
  assert.equal(observed.slowReleasing.event, 'releasing');
  assert.equal(observed.fastAcquired.event, 'acquired');
  assert.ok(observed.fastAcquired.receivedAt >= observed.slowReleasing.receivedAt, 'fast lock acquisition should happen after slow releases/starts releasing');
  assert.equal(observed.slow.done.verify.ok, true);
  assert.equal(observed.fast.done.verify.ok, true);
  assert.equal(observed.verification.slowVerify.ok, true);
  assert.equal(observed.verification.fastVerify.ok, true);
  assert.equal(observed.verification.mainVerify.ok, true);
  assert.equal(observed.verification.cleanupAfter, true);
  assert.equal(observed.query?.heldCount ?? 0, 0);
  assert.equal(observed.query?.pendingCount ?? 0, 0);
  for (const kinds of [observed.traces.slowKinds, observed.traces.fastKinds, observed.traces.verifyKinds]) {
    for (const kind of ['coord:web-lock-request', 'coord:web-lock-acquired', 'coord:web-lock-release', 'storage:opfs-web-lock-guard-create']) {
      assert.ok(kinds.includes(kind), `missing guarded lock trace kind ${kind}`);
    }
  }
  assert.ok(observed.traces.verifyKinds.includes('storage:opfs-block-put'), 'main guarded put should reach OPFS block put');
  assert.ok(observed.traces.verifyKinds.includes('storage:opfs-block-cleanup'), 'final cleanup should run under guard');

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-guarded-contention-proof`, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium proof that BrowserRT WebLockGuardedBlockStore can serialize same-origin worker OPFS mutations: a fast worker waits while a slow worker holds the same exclusive Web Lock, both acknowledged content-addressed OPFS blocks verify from the main page, a normal guarded put still reaches OPFS, and cleanup leaves no held/pending locks.',
    observations: observed,
    harness,
    claimsChecked: [
      'navigator.locks and async OPFS are available in the managed Chromium page and dedicated workers',
      'two same-origin workers use one BrowserRT WebLockGuardedBlockStore lock name around OPFS writes',
      'the fast worker does not acquire the lock during the slow worker hold window',
      'both worker-written content-addressed OPFS blocks verify from a main-page guarded store',
      'a standard guarded put reaches OPFS after contention',
      'final guarded cleanup succeeds and navigator.locks.query reports no held/pending locks'
    ],
    nonClaims: [
      'Chromium-in-cloudtainer browser proof only; not cross-browser Web Locks or OPFS conformance.',
      'Exclusive lock serialization is not a fairness, starvation-freedom, exactly-once, multi-tab lifecycle, or background-throttling claim.',
      'This does not prove OPFS durability, fsync behavior, power-loss safety, organic low-disk eviction survival, persistent-storage retention, or quota behavior.',
      'The proof coordinates two dedicated workers plus a main page on one local origin; it is not a production distributed-lock claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '60000'));
const chromium = argValue(argv, '--chromium', null);
const prefix = argValue(argv, '--prefix', null);
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');
try {
  const report = await runProbe({ timeoutMs, chromium, prefix, relaxPolicy });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-guarded-contention-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser OPFS/Web Locks contention proof is not silently skipped; run it by explicit id while debugging.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_guarded_contention_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
