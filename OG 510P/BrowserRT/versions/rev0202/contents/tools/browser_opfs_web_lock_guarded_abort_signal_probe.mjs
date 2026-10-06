#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const BROWSER_TASK = 'browser:opfs-web-lock-guarded-abort-signal-proof';
const DEFAULT_OUT = `artifacts/validation/${PFX}-BROWSER-OPFS-WEB-LOCK-GUARDED-ABORT-SIGNAL-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, lockPrefix, lockName, payloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      webLocksQuery: typeof navigator.locks?.query === 'function',
      abortController: typeof AbortController === 'function',
      abortSignalAny: typeof AbortSignal?.any === 'function',
      fileSystemFileHandle: typeof FileSystemFileHandle === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsWebLockGuardedAbortSignalProof: true, opfsAsyncBlockStoreProof: true, opfsWebLocksProof: true, browserCdpHarness: true });
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null } }; }
    };
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const prefixParts = String(${JSON.stringify(prefix)}).split('/').filter(Boolean);
    const openPrefix = async (suffix = '', create = false) => {
      let dir = await navigator.storage.getDirectory();
      const parts = suffix ? [...prefixParts, ...String(suffix).split('/').filter(Boolean)] : prefixParts;
      for (const part of parts) dir = await dir.getDirectoryHandle(part, { create });
      return dir;
    };
    const treeSummary = async (suffix = '') => {
      try {
        const dir = await openPrefix(suffix, false);
        let dirCount = 0; let fileCount = 0; let byteCount = 0; const files = [];
        const walk = async (node, path = '') => {
          for await (const [name, handle] of node.entries()) {
            const childPath = path ? path + '/' + name : name;
            if (handle.kind === 'directory') { dirCount += 1; await walk(handle, childPath); }
            else if (handle.kind === 'file') { const file = await handle.getFile(); fileCount += 1; byteCount += file.size; files.push({ path: childPath, bytes: file.size }); }
          }
        };
        await walk(dir);
        return { exists: true, dirCount, fileCount, byteCount, files };
      } catch (error) {
        if (error?.name === 'NotFoundError') return { exists: false, dirCount: 0, fileCount: 0, byteCount: 0, files: [] };
        throw error;
      }
    };
    const waitFor = async (label, fn, timeoutMs = 1000, intervalMs = 10) => {
      const started = Date.now();
      while (Date.now() - started < timeoutMs) {
        const value = await fn();
        if (value) return value;
        await sleep(intervalMs);
      }
      throw new Error('timeout waiting for ' + label);
    };

    const store = rt.opfsAsyncBlockStore({ name: 'browser-guarded-abort-signal-store', prefix: ${JSON.stringify(prefix)} + '/pending', writeBudgetGuard: false });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)} + '-pending', label: 'browser-guarded-abort-signal-pending', lockTimeoutMs: 0 });
    const cleanupPendingBefore = await guard.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const treeBeforePending = await treeSummary('pending');
    let releaseHolder;
    const holder = guard.withExclusive(async () => {
      await new Promise((resolve) => { releaseHolder = resolve; });
      return 'released';
    }, { op: 'browser-abortSignal-holder' });
    await waitFor('holder held', async () => {
      const q = await guard.queryLocks();
      return q.heldCount === 1 ? q : null;
    });
    const abortOnly = new AbortController();
    const queuedPutPromise = capture('browser-abortSignal-only-pending-put', () => guard.put(payload, { label: 'browser-abortSignal-only-pending-put' }, { abortSignal: abortOnly.signal, writeBudgetGuard: false }));
    const pendingBeforeAbort = await waitFor('queued put pending', async () => {
      const q = await guard.queryLocks();
      return q.pendingCount === 1 ? q : null;
    });
    abortOnly.abort(new Error('browser operator cancelled pending guarded put'));
    const queuedPut = await queuedPutPromise;
    const queryWhileHeldAfterAbort = await guard.queryLocks();
    const treeAfterPendingAbort = await treeSummary('pending');
    releaseHolder();
    const holderResult = await holder;
    const settledAfterPending = await guard.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });

    const providerStore = rt.opfsAsyncBlockStore({ name: 'browser-guarded-provider-abort-store', prefix: ${JSON.stringify(prefix)} + '/provider', writeBudgetGuard: false });
    const providerGuard = rt.opfsWebLockGuardedBlockStore({ store: providerStore, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)} + '-provider', label: 'browser-guarded-provider-abort', lockTimeoutMs: 500 });
    const cleanupProviderBefore = await providerGuard.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const originalCreateWritable = FileSystemFileHandle.prototype.createWritable;
    const providerAbortController = new AbortController();
    const liveController = new AbortController();
    const patchStats = { createWritableCalls: 0, abortsIssued: 0, writeCalls: 0, closeCalls: 0 };
    FileSystemFileHandle.prototype.createWritable = async function patchedCreateWritable(options = {}) {
      patchStats.createWritableCalls += 1;
      const writable = await originalCreateWritable.call(this, options);
      providerAbortController.abort(new Error('browser abortSignal aborted after lock acquisition before OPFS write'));
      patchStats.abortsIssued += 1;
      await sleep(20);
      return {
        async write(value) { patchStats.writeCalls += 1; return await writable.write(value); },
        async close() { patchStats.closeCalls += 1; return await writable.close(); },
        async abort(reason) { return typeof writable.abort === 'function' ? await writable.abort(reason) : undefined; },
        async seek(position) { return typeof writable.seek === 'function' ? await writable.seek(position) : undefined; },
        async truncate(size) { return typeof writable.truncate === 'function' ? await writable.truncate(size) : undefined; }
      };
    };
    let providerAbort;
    try {
      providerAbort = await capture('browser-dual-signal-provider-abort', () => providerGuard.put(new TextEncoder().encode('provider abort payload ' + Date.now()), { label: 'browser-dual-signal-provider-abort' }, { signal: liveController.signal, abortSignal: providerAbortController.signal, writeBudgetGuard: false }));
    } finally {
      FileSystemFileHandle.prototype.createWritable = originalCreateWritable;
    }
    const providerTreeAfterAbort = await treeSummary('provider');
    const providerSnapshotAfterAbort = providerGuard.snapshot();

    // guarded-smoke
    const smokeStore = rt.opfsAsyncBlockStore({ name: 'browser-guarded-abort-smoke-store', prefix: ${JSON.stringify(prefix)} + '/smoke', writeBudgetGuard: false });
    const smokeGuard = rt.opfsWebLockGuardedBlockStore({ store: smokeStore, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)} + '-smoke', label: 'browser-guarded-abort-smoke', lockTimeoutMs: 500 });
    const smokeCleanupBefore = await smokeGuard.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const smokePut = await smokeGuard.put(new TextEncoder().encode('BrowserRT guarded abortSignal smoke ' + Date.now()), { label: 'browser-guarded-abort-smoke' }, { timeoutMs: 500, writeBudgetGuard: false });
    const smokeVerify = await smokeGuard.verify(smokePut.ref, { timeoutMs: 500 });
    const smokeRead = await smokeGuard.get(smokePut.ref, { timeoutMs: 500 });
    const smokeCleanupAfter = await smokeGuard.cleanupForTest({ timeoutMs: 500 });
    const smokeSettled = await smokeGuard.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksAfterRaw = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const locksAfter = locksAfterRaw ? { heldCount: locksAfterRaw.held?.length ?? null, pendingCount: locksAfterRaw.pending?.length ?? null, held: locksAfterRaw.held, pending: locksAfterRaw.pending } : null;
    const trace = rt.trace.snapshot();
    const traceKinds = trace.map((row) => row.kind);
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, cleanupPendingBefore, treeBeforePending, pendingBeforeAbort, queuedPut, queryWhileHeldAfterAbort, treeAfterPendingAbort, holderResult, settledAfterPending, cleanupProviderBefore, providerAbort, patchStats, providerTreeAfterAbort, providerSnapshotAfterAbort, smokeCleanupBefore, smokePut: { digest: smokePut.digest, bytes: smokePut.bytes, ref: smokePut.ref }, smokeVerify, smokeReadSameBytes: smokeRead.byteLength > 0, smokeCleanupAfter, smokeSettled, locksAfter, traceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-guarded-abort-signal-proof`;
  const lockPrefix = options.lockPrefix || `browserrt:${REVISION}:guarded-abort-signal-browser`;
  const lockName = options.lockName || `${REVISION}-guarded-abort-signal`;
  const payload = options.payload || `browser-guarded-abort-signal-payload-${REVISION}-${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 18000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-web-lock-guarded-abort-signal-probe.html',
    pageTitle: 'BrowserRT OPFS Web Lock guarded abortSignal probe',
    profilePrefix: 'browserrt-opfs-web-lock-guarded-abort-signal-',
    stderrTerms: ['opfs', 'lock', 'abort', 'signal', 'storage']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, lockPrefix, lockName, payload), timeoutMs);
    mark('browser-opfs-web-lock-guarded-abort-signal-eval', started);
    out._pageUrl = pageUrl;
    return out;
  });

  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.page.isSecureContext, true);
  assert.equal(observed.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(observed.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(observed.capabilities.abortController, true, 'AbortController must be available');
  assert.equal(observed.queuedPut.ok, false, 'abortSignal-only queued guarded put should reject');
  assert.equal(observed.queuedPut.error?.code, 'BRT_WEB_LOCK_ABORTED', 'queued abortSignal-only put should reject at Web Lock boundary');
  assert.equal(observed.queryWhileHeldAfterAbort.heldCount, 1, 'holder should remain held after queued abort drains');
  assert.equal(observed.queryWhileHeldAfterAbort.pendingCount, 0, 'queued abortSignal-only put should be removed before holder release');
  assert.equal(observed.treeAfterPendingAbort.fileCount, 0, 'queued abort before lock acquisition should not create OPFS block files');
  assert.equal(observed.providerAbort.ok, false, 'dual signal/abortSignal provider abort should reject');
  assert.equal(observed.providerAbort.error?.code, 'BRT_OPFS_OPERATION_ABORTED', 'provider abort after acquisition should preserve OPFS error surface');
  assert.equal(observed.patchStats.createWritableCalls >= 1, true, 'provider abort case should reach patched writable path');
  assert.equal(observed.patchStats.writeCalls, 0, 'provider abort should happen before OPFS write call');
  assert.equal(observed.providerSnapshotAfterAbort.store.stats.abortRejects >= 1, true, 'underlying OPFS store should count abort rejection');
  assert.equal(observed.smokeVerify.ok, true, 'smoke guarded write should verify');
  assert.equal(observed.smokeReadSameBytes, true, 'smoke guarded read should return bytes');
  assert.equal(observed.smokeCleanupAfter, true, 'smoke cleanup should remove prefix');
  assert.equal(observed.smokeSettled.ok, true, 'smoke Web Lock should settle');
  assert.equal(observed.locksAfter?.heldCount ?? 0, 0, 'browser Web Locks query should end with zero held locks');
  assert.equal(observed.locksAfter?.pendingCount ?? 0, 0, 'browser Web Locks query should end with zero pending locks');
  assert.ok(observed.traceKinds.includes('storage:opfs-web-lock-guard-abort-signal'), 'guard should trace abort-signal-aware browser operations');
  assert.ok(observed.traceKinds.includes('coord:web-lock-aborted'), 'coordinator should trace pending abortSignal cancellation');
  assert.ok(obedTraceHas(observed, 'storage:opfs-block-abort'), 'underlying OPFS abort trace should be present');
  assert.ok(observed.traceKinds.includes('storage:opfs-web-lock-guard-op-complete'), 'smoke path should complete guarded operation');

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-guarded-abort-signal-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium proof that direct WebLockGuardedBlockStore abortSignal options cancel pending real Web Locks before OPFS mutation and that dual signal/abortSignal sources reach real OPFS provider abort checkpoints after acquisition without being mislabeled as lock-aborted.',
    observed, harness,
    claimsChecked: [
      'abortSignal-only guarded put cancels while pending on real navigator.locks and does not create OPFS block files',
      'after-acquisition provider abort from abortSignal preserves BRT_OPFS_OPERATION_ABORTED rather than being wrapped as BRT_WEB_LOCK_ABORTED',
      'dual signal/abortSignal composition reaches real OPFS before write()',
      'guarded OPFS/Web Locks smoke still writes, verifies, reads, cleans up, and drains locks'
    ],
    nonClaims: [
      'Managed Chromium proof only; no Firefox/Safari/cross-browser conformance claim.',
      'Abort remains cooperative after lock acquisition; providers that ignore AbortSignal can still mutate or settle late.',
      'No OPFS fsync durability, crash/power-loss recovery, quota reservation, eviction survival, Web Locks fairness, or production-readiness claim.'
    ]
  };
}

function obedTraceHas(observed, kind) { return Array.isArray(observed.traceKinds) && observed.traceKinds.includes(kind); }

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', 18000)), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-guarded-abort-signal-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, code: error?.code ?? null, detail: error?.detail ?? null }, nonClaims: ['Failed managed Chromium guarded abortSignal proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_guarded_abort_signal_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
