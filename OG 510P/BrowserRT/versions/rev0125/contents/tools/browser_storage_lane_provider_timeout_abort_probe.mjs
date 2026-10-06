#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const BROWSER_TASK = 'browser:provider-timeout-abort-proof';
const DEFAULT_OUT = `artifacts/validation/${PFX}-BROWSER-STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, lockPrefix, payloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      storageEstimate: typeof navigator.storage?.estimate === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      fileSystemFileHandle: typeof FileSystemFileHandle === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ storageLaneProviderTimeoutAbortProof: true, opfsAsyncBlockStoreProof: true, opfsWebLocksProof: true, browserCdpHarness: true });
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const prefixParts = String(${JSON.stringify(prefix)}).split('/').filter(Boolean);
    const openPrefix = async (create = false) => {
      let dir = await navigator.storage.getDirectory();
      for (const part of prefixParts) dir = await dir.getDirectoryHandle(part, { create });
      return dir;
    };
    const prefixExists = async () => {
      try { await openPrefix(false); return true; }
      catch (error) { if (error?.name === 'NotFoundError') return false; throw error; }
    };
    const treeSummary = async () => {
      try {
        const dir = await openPrefix(false);
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
    const makeScheduler = (label) => mod.createCrossLaneScheduler({
      label: label + ':scheduler', trace: rt.trace,
      lanes: [
        { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
        { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
      ]
    });
    const store = rt.opfsAsyncBlockStore({ name: 'browser-provider-timeout-abort-store', prefix: ${JSON.stringify(prefix)}, writeBudgetGuard: false });
    const cleanupBefore = await store.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const prefixBefore = await prefixExists();
    const originalCreateWritable = FileSystemFileHandle.prototype.createWritable;
    const patchStats = { createWritableCalls: 0, delayedCreateWritableReturns: 0, abortCalls: 0, writeCalls: 0, closeCalls: 0 };
    FileSystemFileHandle.prototype.createWritable = async function patchedCreateWritable(options = {}) {
      patchStats.createWritableCalls += 1;
      const writable = await originalCreateWritable.call(this, options);
      await sleep(350);
      patchStats.delayedCreateWritableReturns += 1;
      return {
        async write(value) { patchStats.writeCalls += 1; return await writable.write(value); },
        async close() { patchStats.closeCalls += 1; return await writable.close(); },
        async abort(reason) { patchStats.abortCalls += 1; return await writable.abort(reason); },
        async seek(position) { return typeof writable.seek === 'function' ? await writable.seek(position) : undefined; },
        async truncate(size) { return typeof writable.truncate === 'function' ? await writable.truncate(size) : undefined; }
      };
    };
    let abortPhase;
    try {
      const adapter = mod.createBlockStoreLaneAdapter({
        label: 'browser-provider-timeout-abort-adapter',
        store,
        scheduler: makeScheduler('browser-provider-timeout-abort'),
        trace: rt.trace,
        defaultOperationTimeoutMs: 120,
        abortProviderOnOperationTimeout: true
      });
      const schedule = adapter.schedulePut(payload, { id: 'browser-opfs-put-aborted-by-operation-timeout', label: 'browser-provider-timeout-abort' });
      const drain = await adapter.drain({ maxSteps: 2 });
      const afterTimeout = adapter.snapshot();
      const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 10 });
      const afterSettledTree = await treeSummary();
      const quarantine = adapter.timedOutOperationQuarantine('storage');
      const review = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: 'browser-opfs-put-aborted-by-operation-timeout', reviewer: 'browser-provider-timeout-abort-proof', reason: 'browser provider timeout abort reviewed', reviewToken: '${REVISION}-browser-provider-timeout-abort-review' });
      const cleared = adapter.clearFailedTimedOutOperations({ reviewManifest: review, requireReviewFingerprint: true, reason: 'browser-provider-timeout-abort-proof-cleared' });
      const healthy = adapter.markHealthy('storage', 'browser-provider-timeout-abort-reviewed');
      abortPhase = { schedule, drain, afterTimeout, settled, afterSettledTree, quarantine, review, cleared, healthy, adapterSnapshot: adapter.snapshot(), storeSnapshot: store.snapshot() };
    } finally {
      FileSystemFileHandle.prototype.createWritable = originalCreateWritable;
    }

    const recoveryAdapter = mod.createBlockStoreLaneAdapter({ label: 'browser-provider-timeout-abort-recovery-adapter', store, scheduler: makeScheduler('browser-provider-timeout-abort-recovery'), trace: rt.trace, defaultOperationTimeoutMs: 500, abortProviderOnOperationTimeout: true });
    const recoverySchedule = recoveryAdapter.schedulePut(new TextEncoder().encode('BrowserRT browser provider timeout abort recovered write'), { id: 'browser-provider-timeout-abort-recovered-put', label: 'browser-provider-timeout-abort-recovered', providerOptions: { writeBudgetGuard: false } });
    const recoveryDrain = await recoveryAdapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryAdapter.result('browser-provider-timeout-abort-recovered-put');
    const recoveredVerify = recoveredResult?.ref ? await store.verify(recoveredResult.ref, { timeoutMs: 500 }) : null;
    const recoveredRead = recoveredResult?.ref ? await store.get(recoveredResult.ref, { timeoutMs: 500 }) : null;
    const cleanupAfter = await store.cleanupForTest({ timeoutMs: 500 }).catch(() => false);

    const guardedPrefix = ${JSON.stringify(prefix)} + '/guarded-smoke';
    const guarded = rt.opfsWebLockGuardedBlockStore({
      prefix: guardedPrefix,
      label: 'browser-provider-timeout-abort-guarded-smoke',
      lockPrefix: ${JSON.stringify(lockPrefix)},
      lockName: 'provider-timeout-abort-lock',
      lockTimeoutMs: 500,
      storeConfig: { writeBudgetGuard: false }
    });
    const guardedCleanupBefore = await guarded.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const guardedPayload = new TextEncoder().encode('BrowserRT guarded smoke provider timeout abort path');
    const guardedPut = await guarded.put(guardedPayload, { label: 'browser-provider-timeout-abort-guarded-smoke' }, { timeoutMs: 500, writeBudgetGuard: false });
    const guardedVerify = await guarded.verify(guardedPut.ref, { timeoutMs: 500 });
    const guardedRead = await guarded.get(guardedPut.ref, { timeoutMs: 500 });
    const guardedCleanupAfter = await guarded.cleanupForTest({ timeoutMs: 500 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const trace = rt.trace.snapshot();
    const traceKinds = trace.map((row) => row.kind);
    const normalizedTrace = trace.map((row) => ({ kind: row.kind, label: row.label, op: row.op, store: row.store, provider: row.provider, cancellation: row.cancellation, abortProviderOnOperationTimeout: row.abortProviderOnOperationTimeout, code: row.error?.code || row.code || null, reason: row.reason, digest: row.digest, path: row.path })).filter((row) => row.kind);
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, cleanupBefore, prefixBefore, patchStats, abortPhase, recoverySchedule, recoveryDrain, recoveredResult: recoveredResult ? { digest: recoveredResult.digest, bytes: recoveredResult.bytes, duplicate: recoveredResult.duplicate, ref: recoveredResult.ref } : null, recoveredVerify, recoveredReadSameBytes: recoveredRead ? recoveredRead.byteLength > 0 : false, cleanupAfter, guardedCleanupBefore, guardedPut: guardedPut ? { digest: guardedPut.digest, bytes: guardedPut.bytes, duplicate: guardedPut.duplicate, ref: guardedPut.ref } : null, guardedVerify, guardedReadSameBytes: guardedRead ? sameBytes(guardedRead, guardedPayload) : false, guardedCleanupAfter, lockSettled, locksAfter: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/provider-timeout-abort-proof/${Date.now()}`;
  const lockPrefix = options.lockPrefix || `browserrt:${REVISION}:provider-timeout-abort`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser provider timeout abort payload ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 25000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/storage-lane-provider-timeout-abort-probe.html',
    pageTitle: 'BrowserRT storage lane provider timeout abort probe',
    profilePrefix: 'browserrt-provider-timeout-abort-',
    stderrTerms: ['opfs', 'storage', 'locks', 'timeout-abort']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, lockPrefix, payloadText), timeoutMs);
    mark('browser-storage-lane-provider-timeout-abort-eval', started);
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
  assert.equal(observed.capabilities.fileSystemFileHandle, true, 'FileSystemFileHandle must be patchable for deterministic delay');
  assert.equal(observed.prefixBefore, false, 'proof prefix should start absent');

  const abortRow = observed.abortPhase.drain.results.find((row) => row.opId === 'browser-opfs-put-aborted-by-operation-timeout');
  assert.equal(abortRow.ok, false, 'scheduled browser OPFS put should time out');
  assert.equal(abortRow.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(abortRow.error.providerDetail?.abortProviderOnTimeout, true);
  assert.equal(abortRow.error.providerDetail?.providerAbortSignaled, true);
  assert.equal(observed.patchStats.createWritableCalls >= 1, true, 'patch should delay createWritable inside real OPFS');
  assert.equal(observed.patchStats.abortCalls >= 1, true, 'timeout-owned abort should call writable.abort');
  assert.equal(observed.abortPhase.afterTimeout.executor.stats.providerTimeoutAborts, 1);
  assert.equal(observed.abortPhase.settled.ok, true, 'browser provider abort should settle timed-out operation');
  assert.equal(observed.abortPhase.quarantine.failedTimedOutOperationCount, 1, 'browser provider abort should be late-failure quarantined');
  assert.equal(observed.abortPhase.afterSettledTree.fileCount, 0, 'aborted browser OPFS put should leave no block files');
  assert.equal(observed.abortPhase.afterSettledTree.byteCount, 0, 'aborted browser OPFS put should leave no block bytes');
  assert.equal(observed.abortPhase.storeSnapshot.stats.abortRejects > 0, true, 'browser OPFS store should observe timeout-owned abort signal');
  assert.equal(observed.abortPhase.cleared.clearedCount, 1);
  assert.equal(observed.abortPhase.healthy.healthy, true);

  const recoveredRow = observed.recoveryDrain.results.find((row) => row.opId === 'browser-provider-timeout-abort-recovered-put');
  assert.equal(recoveredRow.ok, true, 'recovery put should succeed after failed-abort quarantine review');
  assert.equal(observed.recoveredVerify.ok, true);
  assert.equal(observed.recoveredReadSameBytes, true);
  assert.equal(observed.cleanupAfter, true);
  assert.equal(observed.guardedVerify.ok, true);
  assert.equal(observed.guardedReadSameBytes, true);
  assert.equal(observed.lockSettled.ok, true, 'guarded lock should settle');
  assert.equal(observed.locksAfter?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksAfter?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');
  for (const kind of ['storage-lane:operation-timeout', 'storage:opfs-block-abort', 'storage:opfs-block-put-rollback', 'storage-lane:late-provider-failures-cleared', 'storage:opfs-web-lock-guard-op-complete']) {
    assert.ok(observed.traceKinds.includes(kind), `browser trace missing ${kind}`);
  }

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-storage-lane-provider-timeout-abort-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that abortProviderOnOperationTimeout injects a timeout-owned AbortSignal into a scheduled OPFS put, aborts the real OPFS writer, rolls back the block path, and still allows reviewed recovery plus guarded Web Locks smoke.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'real OPFS scheduled put receives timeout-owned provider AbortSignal when abortProviderOnOperationTimeout is enabled',
      'operation timeout calls writable.abort and rolls back the unacknowledged block file',
      'late provider abort is quarantined as a failed timed-out operation until reviewed and cleared',
      'after review/clear, scheduled OPFS writes and guarded OPFS/Web Locks smoke still succeed and drain locks'
    ],
    nonClaims: [
      'Managed Chromium only; no Firefox/Safari/cross-browser conformance claim.',
      'Provider abort on timeout remains cooperative and opt-in; providers that ignore AbortSignal can still settle late.',
      'This does not prove quota reservation, eviction survival, fsync durability, crash/power-loss recovery, Web Locks fairness, multi-tab atomicity, or production readiness.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', 25000)), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-storage-lane-provider-timeout-abort-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_storage_lane_provider_timeout_abort_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
