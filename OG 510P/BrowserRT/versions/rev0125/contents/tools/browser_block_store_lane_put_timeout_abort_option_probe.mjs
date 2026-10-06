#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const BROWSER_TASK = 'browser:block-store-lane-put-timeout-abort-option-proof';
const DEFAULT_OUT = `artifacts/validation/${PFX}-BROWSER-BLOCK-STORE-LANE-PUT-TIMEOUT-ABORT-OPTION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, lockPrefix, payloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      abortController: typeof AbortController === 'function',
      fileSystemFileHandle: typeof FileSystemFileHandle === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ blockStoreLanePutTimeoutAbortOptionProof: true, storageLaneProviderTimeoutAbortProof: true, opfsAsyncBlockStoreProof: true, opfsWebLocksProof: true, browserCdpHarness: true });
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const optOutPayload = new TextEncoder().encode(${JSON.stringify(payloadText + ' opt-out')});
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
    const makeScheduler = (label) => mod.createCrossLaneScheduler({
      label: label + ':scheduler', trace: rt.trace,
      lanes: [
        { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
        { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
      ]
    });

    const optInStore = rt.opfsAsyncBlockStore({ name: 'browser-put-timeout-abort-opt-in-store', prefix: ${JSON.stringify(prefix)} + '/opt-in', writeBudgetGuard: false });
    const optOutStore = rt.opfsAsyncBlockStore({ name: 'browser-put-timeout-abort-opt-out-store', prefix: ${JSON.stringify(prefix)} + '/opt-out', writeBudgetGuard: false });
    const cleanupBefore = {
      optIn: await optInStore.cleanupForTest({ timeoutMs: 500 }).catch(() => false),
      optOut: await optOutStore.cleanupForTest({ timeoutMs: 500 }).catch(() => false)
    };
    const beforeTrees = { optIn: await treeSummary('opt-in'), optOut: await treeSummary('opt-out') };

    const originalCreateWritable = FileSystemFileHandle.prototype.createWritable;
    const patchStats = { createWritableCalls: 0, abortCalls: 0, writeCalls: 0, closeCalls: 0, delayedReturns: 0 };
    FileSystemFileHandle.prototype.createWritable = async function patchedCreateWritable(options = {}) {
      patchStats.createWritableCalls += 1;
      const writable = await originalCreateWritable.call(this, options);
      await sleep(180);
      patchStats.delayedReturns += 1;
      return {
        async write(value) { patchStats.writeCalls += 1; return await writable.write(value); },
        async close() { patchStats.closeCalls += 1; return await writable.close(); },
        async abort(reason) { patchStats.abortCalls += 1; return await writable.abort(reason); },
        async seek(position) { return typeof writable.seek === 'function' ? await writable.seek(position) : undefined; },
        async truncate(size) { return typeof writable.truncate === 'function' ? await writable.truncate(size) : undefined; }
      };
    };
    let optIn;
    let optOut;
    try {
      const optInAdapter = mod.createBlockStoreLaneAdapter({ label: 'browser-put-timeout-abort-opt-in-adapter', store: optInStore, scheduler: makeScheduler('browser-put-timeout-abort-opt-in'), trace: rt.trace, defaultOperationTimeoutMs: 0, abortProviderOnOperationTimeout: false });
      const optInSchedule = optInAdapter.schedulePut(payload, { id: 'browser-put-timeout-abort-opt-in', label: 'browser-put-timeout-abort-opt-in', operationTimeoutMs: 70, abortProviderOnOperationTimeout: true });
      const optInDrain = await optInAdapter.drain({ maxSteps: 2 });
      const optInSettled = await optInAdapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 10 });
      const optInTree = await treeSummary('opt-in');
      optIn = { schedule: optInSchedule, drain: optInDrain, settled: optInSettled, tree: optInTree, snapshot: optInAdapter.snapshot(), storeSnapshot: optInStore.snapshot() };

      const optOutAdapter = mod.createBlockStoreLaneAdapter({ label: 'browser-put-timeout-abort-opt-out-adapter', store: optOutStore, scheduler: makeScheduler('browser-put-timeout-abort-opt-out'), trace: rt.trace, defaultOperationTimeoutMs: 0, abortProviderOnOperationTimeout: true });
      const optOutSchedule = optOutAdapter.schedulePut(optOutPayload, { id: 'browser-put-timeout-abort-opt-out', label: 'browser-put-timeout-abort-opt-out', operationTimeoutMs: 70, abortProviderOnOperationTimeout: false });
      const optOutDrain = await optOutAdapter.drain({ maxSteps: 2 });
      const optOutSettled = await optOutAdapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 10 });
      const optOutResult = optOutAdapter.lateResult('browser-put-timeout-abort-opt-out')?.summary ?? null;
      const optOutTree = await treeSummary('opt-out');
      optOut = { schedule: optOutSchedule, drain: optOutDrain, settled: optOutSettled, lateSummary: optOutResult, tree: optOutTree, snapshot: optOutAdapter.snapshot(), storeSnapshot: optOutStore.snapshot() };
    } finally {
      FileSystemFileHandle.prototype.createWritable = originalCreateWritable;
    }

    const cleanupAfter = {
      optIn: await optInStore.cleanupForTest({ timeoutMs: 500 }).catch(() => false),
      optOut: await optOutStore.cleanupForTest({ timeoutMs: 500 }).catch(() => false)
    };

    const guardedPrefix = ${JSON.stringify(prefix)} + '/guarded-smoke';
    const guarded = rt.opfsWebLockGuardedBlockStore({
      prefix: guardedPrefix,
      label: 'browser-put-timeout-abort-option-guarded-smoke',
      lockPrefix: ${JSON.stringify(lockPrefix)},
      lockName: 'put-timeout-abort-option-lock',
      lockTimeoutMs: 500,
      storeConfig: { writeBudgetGuard: false }
    });
    const guardedCleanupBefore = await guarded.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const guardedPayload = new TextEncoder().encode('BrowserRT guarded smoke put timeout abort option path');
    const guardedPut = await guarded.put(guardedPayload, { label: 'browser-put-timeout-abort-option-guarded-smoke' }, { timeoutMs: 500, writeBudgetGuard: false });
    const guardedVerify = await guarded.verify(guardedPut.ref, { timeoutMs: 500 });
    const guardedRead = await guarded.get(guardedPut.ref, { timeoutMs: 500 });
    const guardedCleanupAfter = await guarded.cleanupForTest({ timeoutMs: 500 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const trace = rt.trace.snapshot();
    const traceKinds = trace.map((row) => row.kind);
    const normalizedTrace = trace.map((row) => ({ kind: row.kind, label: row.label, op: row.op, store: row.store, provider: row.provider, cancellation: row.cancellation, abortProviderOnOperationTimeout: row.abortProviderOnOperationTimeout, code: row.error?.code || row.code || null, reason: row.reason, digest: row.digest, path: row.path })).filter((row) => row.kind);
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, cleanupBefore, beforeTrees, optIn, optOut, patchStats, cleanupAfter, guardedCleanupBefore, guardedPut: guardedPut ? { digest: guardedPut.digest, bytes: guardedPut.bytes, duplicate: guardedPut.duplicate, ref: guardedPut.ref } : null, guardedVerify, guardedReadSameBytes: guardedRead ? sameBytes(guardedRead, guardedPayload) : false, guardedCleanupAfter, lockSettled, locksAfter: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/put-timeout-abort-option-proof/${Date.now()}`;
  const lockPrefix = options.lockPrefix || `browserrt:${REVISION}:put-timeout-abort-option`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser put timeout abort option payload ${Date.now()}`;
  const { result: report, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 24000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/block-store-lane-put-timeout-abort-option-probe.html',
    pageTitle: 'BrowserRT block store lane put timeout abort option probe',
    profilePrefix: 'browserrt-put-timeout-abort-option-',
    stderrTerms: ['opfs', 'storage', 'locks', 'put-timeout-abort']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, lockPrefix, payloadText), timeoutMs);
    mark('browser-block-store-lane-put-timeout-abort-option-eval', started);
    out._pageUrl = pageUrl;
    return out;
  });

  assert.equal(report.project, 'BrowserRT');
  assert.equal(report.revision, REVISION);
  assert.equal(report.capabilities.opfs, true, 'OPFS must be available in managed Chromium proof');
  assert.equal(report.capabilities.webLocks, true, 'Web Locks must be available in managed Chromium proof');
  assert.equal(report.capabilities.abortController, true, 'AbortController must be available in managed Chromium proof');

  const optInRow = report.optIn.drain.results.find((row) => row.opId === 'browser-put-timeout-abort-opt-in');
  assert.equal(report.optIn.schedule.accepted, true);
  assert.equal(optInRow.ok, false, 'per-put opt-in should time out caller-visible real OPFS put');
  assert.equal(optInRow.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(optInRow.error.providerDetail?.providerAbortSignaled, true, 'per-put opt-in should signal provider abort');
  assert.equal(report.optIn.snapshot.executor.stats.providerTimeoutAborts, 1, 'per-put opt-in should count provider timeout abort with adapter default false');
  assert.equal(report.optIn.snapshot.executor.stats.failedTimedOutOperations, 1, 'real OPFS abort should settle as late failure');
  assert.equal(report.optIn.settled.ok, true);
  assert.equal(report.optIn.tree.fileCount, 0, 'real OPFS per-put opt-in abort should not leave a final block file');
  assert.equal(report.optIn.storeSnapshot.stats.rollbackDeletes >= 0, true);

  const optOutRow = report.optOut.drain.results.find((row) => row.opId === 'browser-put-timeout-abort-opt-out');
  assert.equal(report.optOut.schedule.accepted, true);
  assert.equal(optOutRow.ok, false, 'per-put opt-out should still time out caller-visible real OPFS put');
  assert.equal(optOutRow.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(optOutRow.error.providerDetail?.providerAbortSignaled, false, 'per-put opt-out should suppress provider abort with adapter default true');
  assert.equal(report.optOut.snapshot.executor.stats.providerTimeoutAborts, 0, 'per-put opt-out should not count provider timeout abort');
  assert.equal(report.optOut.snapshot.executor.stats.successfulTimedOutOperations, 1, 'non-aborted real OPFS write should settle as late success');
  assert.equal(report.optOut.settled.ok, true);
  assert.equal(report.optOut.tree.fileCount, 1, 'real OPFS per-put opt-out should allow late acknowledged block file to appear before cleanup');
  assert.equal(report.patchStats.abortCalls >= 1, true, 'opt-in real OPFS writer should see abort');
  assert.equal(report.patchStats.writeCalls >= 1, true, 'opt-out real OPFS writer should write after caller-visible timeout');
  assert.equal(report.cleanupAfter.optOut, true, 'proof should clean up the opt-out late block path');

  assert.equal(report.guardedVerify.ok, true, 'guarded OPFS/Web Locks smoke verify should pass');
  assert.equal(report.guardedReadSameBytes, true, 'guarded OPFS/Web Locks smoke read should match');
  assert.equal(report.lockSettled.ok, true, 'Web Locks guarded smoke should settle');
  if (report.locksAfter) {
    assert.equal(report.locksAfter.heldCount, 0, 'no held locks after guarded smoke');
    assert.equal(report.locksAfter.pendingCount, 0, 'no pending locks after guarded smoke');
  }
  for (const kind of ['storage-lane:operation-timeout', 'storage-lane:late-provider-failure', 'storage-lane:late-provider-success', 'storage:opfs-block-put']) {
    assert.ok(report.traceKinds.includes(kind), `browser trace missing ${kind}`);
  }

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-block-store-lane-put-timeout-abort-option-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium proof that BlockStoreLaneAdapter.schedulePut honors per-operation abortProviderOnOperationTimeout true/false with real OPFS and still drains guarded Web Locks.',
    capabilities: report.capabilities,
    page: report.page,
    harness,
    observed: report,
    claimsChecked: [
      'schedulePut per-operation abortProviderOnOperationTimeout=true injects a timeout-owned AbortSignal into real OPFS even when the adapter default is false',
      'schedulePut per-operation abortProviderOnOperationTimeout=false suppresses timeout-owned provider AbortSignal even when the adapter default is true',
      'real OPFS opt-in abort leaves no final block file; real OPFS opt-out can complete late and enters successful timed-out-operation quarantine',
      'guarded OPFS/Web Locks smoke still writes, verifies, reads, cleans up, and drains locks'
    ],
    nonClaims: [
      'Managed Chromium only; no Firefox/Safari/cross-browser conformance claim.',
      'Abort remains cooperative; providers that ignore AbortSignal may still settle late and require quarantine review.',
      'No exact quota prediction, quota reservation, organic eviction survival, persistent-storage retention, fsync durability, crash/power-loss recovery, Web Locks fairness, multi-tab atomicity, or production-readiness claim.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ chromium: argValue(argv, '--chromium', undefined), timeoutMs: Number(argValue(argv, '--timeout-ms', '24000')), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-block-store-lane-put-timeout-abort-option-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_block_store_lane_put_timeout_abort_option_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
