#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-TIMEOUT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function holderWorkerSource() {
  return `
    let releaseHold = null;
    let releasePromise = null;
    self.onmessage = async (event) => {
      const msg = event.data || {};
      if (msg.op === 'release') {
        if (releaseHold) releaseHold();
        return;
      }
      const cfg = msg;
      const post = (eventName, fields = {}) => self.postMessage({ event: eventName, t: Math.round(performance.now() * 1000) / 1000, ...fields });
      try {
        releasePromise = new Promise((resolve) => { releaseHold = resolve; });
        const mod = await import(cfg.browserRtUrl);
        const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockTimeoutProof: true });
        const store = rt.opfsAsyncBlockStore({ name: 'browser-timeout-holder-store', prefix: cfg.prefix });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: cfg.lockPrefix, lockName: cfg.lockName, label: 'browser-timeout-holder-guard', lockTimeoutMs: 0 });
        post('guard-ready', { available: guard.available, lockName: guard.fullLockName });
        const put = await guard.withExclusive(async () => {
          post('acquired', { lockName: guard.fullLockName });
          const result = await store.put(new TextEncoder().encode(cfg.holderPayload), { label: 'browser-timeout-holder' });
          const verify = await store.verify(result.ref);
          post('holder-wrote', { digest: result.digest, bytes: result.bytes, verify });
          await releasePromise;
          post('releasing', { digest: result.digest });
          return { result, verify };
        }, { op: 'browser-timeout-holder-exclusive' });
        const traceSnapshot = rt.trace.snapshot();
        const snapshot = guard.snapshot();
        rt.close();
        post('done', {
          put: { digest: put.result.digest, hash: put.result.hash, bytes: put.result.bytes, duplicate: put.result.duplicate, path: put.result.path, ref: put.result.ref },
          verify: put.verify,
          snapshot,
          traceKinds: traceSnapshot.map((row) => row.kind)
        });
      } catch (error) {
        post('error', { error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack || null } });
      }
    };
  `;
}

function exprForPage(prefix, lockPrefix, lockName, lockTimeoutMs, holderPayload, timeoutPayload, recoveryPayload) {
  const source = holderWorkerSource();
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
      blob: typeof Blob === 'function',
      createObjectURL: typeof URL?.createObjectURL === 'function',
      abortController: typeof AbortController === 'function',
      subtleDigest: typeof crypto?.subtle?.digest === 'function'
    };
    const digestHex = async (text) => {
      const bytes = new TextEncoder().encode(text);
      const hash = await crypto.subtle.digest('SHA-256', bytes);
      return 'sha256:' + Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, '0')).join('');
    };
    const mod = await import(browserRtUrl);
    const prepRt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockTimeoutProof: true });
    const prepStore = prepRt.opfsAsyncBlockStore({ name: 'browser-timeout-prep-store', prefix: ${JSON.stringify(prefix)} });
    const prepGuard = prepRt.opfsWebLockGuardedBlockStore({ store: prepStore, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'browser-timeout-prep-guard', lockTimeoutMs: 200 });
    const cleanupBefore = await prepGuard.cleanupForTest();
    const prepTrace = prepRt.trace.snapshot();
    prepRt.close();

    const workerUrl = URL.createObjectURL(new Blob([${JSON.stringify(source)}], { type: 'text/javascript' }));
    const worker = new Worker(workerUrl, { type: 'module', name: 'browserrt-opfs-web-lock-timeout-holder' });
    const workerMessages = [];
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
      workerMessages.push(row);
      notify(row);
      if (row.event === 'done') doneResolve(row);
      if (row.event === 'error') doneReject(new Error(row.error?.message || 'worker error'));
    };
    worker.onerror = (event) => doneReject(new Error(event.message || 'worker error'));
    const waitFor = (pred, timeoutMs = 3000) => new Promise((resolve, reject) => {
      for (const row of workerMessages) if (pred(row)) return resolve(row);
      const timer = setTimeout(() => reject(new Error('timeout waiting for worker event')), timeoutMs);
      waiters.push({ pred, resolve, reject, timer });
    });
    worker.postMessage({ prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, browserRtUrl, holderPayload: ${JSON.stringify(holderPayload)} });
    const workerAcquired = await waitFor((row) => row.event === 'acquired', 3000);
    const workerWrote = await waitFor((row) => row.event === 'holder-wrote', 3000);

    const timeoutDigest = await digestHex(${JSON.stringify(timeoutPayload)});
    const timeoutRt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockTimeoutProof: true });
    const timeoutStore = timeoutRt.opfsAsyncBlockStore({ name: 'browser-timeout-main-store', prefix: ${JSON.stringify(prefix)} });
    const timeoutGuard = timeoutRt.opfsWebLockGuardedBlockStore({ store: timeoutStore, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'browser-timeout-main-guard', lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} });
    let timeoutError = null;
    try {
      await timeoutGuard.put(new TextEncoder().encode(${JSON.stringify(timeoutPayload)}), { label: 'browser-timeout-candidate' });
    } catch (error) {
      timeoutError = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null };
    }
    const traceAfterTimeout = timeoutRt.trace.snapshot();
    const snapshotAfterTimeout = timeoutGuard.snapshot();
    timeoutRt.close();

    worker.postMessage({ op: 'release' });
    const workerDone = await done;
    try { worker.terminate(); } catch {}
    try { URL.revokeObjectURL(workerUrl); } catch {}

    const verifyRt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockTimeoutProof: true });
    const verifyStore = verifyRt.opfsAsyncBlockStore({ name: 'browser-timeout-verify-store', prefix: ${JSON.stringify(prefix)} });
    const verifyGuard = verifyRt.opfsWebLockGuardedBlockStore({ store: verifyStore, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'browser-timeout-verify-guard', lockTimeoutMs: 250 });
    const timeoutPresentAfterRelease = await verifyGuard.has(timeoutDigest);
    const holderVerify = await verifyGuard.verify(workerDone.put.ref);
    const recoveryPut = await verifyGuard.put(new TextEncoder().encode(${JSON.stringify(recoveryPayload)}), { label: 'browser-timeout-recovery' });
    const recoveryVerify = await verifyGuard.verify(recoveryPut.ref);
    const cleanupAfter = await verifyGuard.cleanupForTest();
    const query = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const verifyTrace = verifyRt.trace.snapshot();
    const verifySnapshot = verifyGuard.snapshot();
    verifyRt.close();

    return JSON.stringify({
      project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities,
      prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)},
      cleanupBefore, workerAcquired, workerWrote, workerDone, workerMessages,
      timeoutDigest, timeoutError, timeoutPresentAfterRelease,
      holderVerify, recoveryPut: { digest: recoveryPut.digest, bytes: recoveryPut.bytes, duplicate: recoveryPut.duplicate, path: recoveryPut.path, ref: recoveryPut.ref }, recoveryVerify, cleanupAfter,
      query: query ? { heldCount: query.held?.length ?? null, pendingCount: query.pending?.length ?? null, held: query.held, pending: query.pending } : null,
      snapshots: { afterTimeout: snapshotAfterTimeout, verify: verifySnapshot },
      traces: {
        prepKinds: prepTrace.map((row) => row.kind),
        timeoutKinds: traceAfterTimeout.map((row) => row.kind),
        verifyKinds: verifyTrace.map((row) => row.kind),
        workerKinds: workerDone.traceKinds,
        timeoutNormalized: traceAfterTimeout.map((row) => ({ kind: row.kind, name: row.name, mode: row.mode, op: row.op, lockName: row.lockName, metadata: row.metadata, timeoutMs: row.timeoutMs, error: row.error })).filter((row) => row.kind)
      }
    });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-timeout-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-timeout';
  const lockName = options.lockName || `${REVISION}-bounded-opfs-mutation-lock`;
  const lockTimeoutMs = Number(options.lockTimeoutMs || 45);
  const holderPayload = options.holderPayload || `holder-block-${REVISION}-${Date.now()}`;
  const timeoutPayload = options.timeoutPayload || `timeout-block-should-not-write-${REVISION}-${Date.now()}`;
  const recoveryPayload = options.recoveryPayload || `recovery-block-after-timeout-${REVISION}-${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-web-lock-timeout-probe.html',
    pageTitle: 'BrowserRT OPFS Web Lock timeout probe',
    profilePrefix: 'browserrt-opfs-web-lock-timeout-',
    stderrTerms: ['opfs', 'lock', 'abort', 'timeout', 'worker', 'storage']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, lockPrefix, lockName, lockTimeoutMs, holderPayload, timeoutPayload, recoveryPayload), timeoutMs);
    mark('browser-opfs-web-lock-timeout-eval', started);
    out._pageUrl = pageUrl;
    return out;
  });

  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.page.isSecureContext, true);
  assert.equal(observed.capabilities.opfs, true, 'OPFS must be available for Web Lock timeout proof');
  assert.equal(observed.capabilities.webLocks, true, 'Web Locks must be available for Web Lock timeout proof');
  assert.equal(observed.capabilities.worker, true, 'Dedicated workers must be available');
  assert.equal(observed.capabilities.abortController, true, 'AbortController must be available');
  assert.equal(observed.workerAcquired.event, 'acquired');
  assert.equal(observed.workerWrote.event, 'holder-wrote');
  assert.equal(observed.timeoutError?.code, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(observed.timeoutPresentAfterRelease, false, 'timed-out OPFS guarded put must not write a block');
  assert.equal(observed.holderVerify.ok, true, 'holder block should verify after release');
  assert.equal(observed.recoveryVerify.ok, true, 'post-timeout guarded write should succeed');
  assert.equal(observed.cleanupAfter, true);
  assert.equal(observed.query?.heldCount ?? 0, 0);
  assert.equal(observed.query?.pendingCount ?? 0, 0);
  assert.equal(observed.snapshots.afterTimeout.coordinator.stats.timeouts, 1);
  assert.equal(observed.snapshots.afterTimeout.stats.errors, 1);
  for (const kind of ['coord:web-lock-timeout-arm', 'coord:web-lock-timeout-fired', 'coord:web-lock-timeout', 'storage:opfs-web-lock-guard-op-error']) {
    assert.ok(observed.traces.timeoutKinds.includes(kind), `missing browser timeout trace kind ${kind}`);
  }
  assert.ok(observed.traces.workerKinds.includes('coord:web-lock-acquired'), 'worker must acquire actual Web Lock');
  assert.ok(observed.traces.verifyKinds.includes('storage:opfs-block-put'), 'recovery write should reach OPFS');

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-timeout-proof`, task_id: 'browser:opfs-web-lock-timeout-proof', status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium proof that a BrowserRT WebLockGuardedBlockStore OPFS mutation pending behind a worker-held exclusive Web Lock aborts via AbortSignal timeout as BRT_WEB_LOCK_TIMEOUT, does not mutate OPFS, leaves no pending lock, and later recovers for a normal guarded OPFS write.',
    observations: observed,
    harness,
    claimsChecked: [
      'a dedicated worker can hold the BrowserRT OPFS guarded-store exclusive Web Lock while writing a verified holder block',
      'a main-page guarded OPFS put pending on the same lock aborts with BRT_WEB_LOCK_TIMEOUT',
      'the timed-out payload digest is absent after the worker releases the lock',
      'a subsequent guarded OPFS put succeeds and verifies',
      'navigator.locks.query reports no held/pending locks after cleanup'
    ],
    nonClaims: [
      'Managed Chromium browser proof only; not a cross-browser Web Locks or OPFS conformance claim.',
      'Timeout is an acquisition backstop only; it does not cancel work after a lock has already been granted.',
      'No fairness, starvation-freedom, background/mobile lifecycle, exactly-once, service-worker, Storage Buckets, OPFS durability, fsync, quota, eviction, or power-loss claim.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-timeout-proof`, task_id: 'browser:opfs-web-lock-timeout-proof', status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser OPFS/Web Locks timeout proof is not silently skipped; run it by explicit id while debugging.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_timeout_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
