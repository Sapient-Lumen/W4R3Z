#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const BROWSER_TASK = 'browser:composite-abort-signal-proof';
const DEFAULT_OUT = `artifacts/validation/${PFX}-BROWSER-STORAGE-LANE-COMPOSITE-ABORT-SIGNAL-PROBE.json`;
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
      abortSignalAny: typeof AbortSignal?.any === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ storageLaneCompositeAbortSignalProof: true, storageLaneProviderTimeoutAbortProof: true, opfsAsyncBlockStoreProof: true, opfsWebLocksProof: true, browserCdpHarness: true });
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

    const store = rt.opfsAsyncBlockStore({ name: 'browser-composite-abort-signal-store', prefix: ${JSON.stringify(prefix)}, writeBudgetGuard: false });
    const cleanupBefore = await store.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const prefixBefore = await prefixExists();

    const preAbortAdapter = mod.createBlockStoreLaneAdapter({ label: 'browser-composite-preabort-adapter', store, scheduler: makeScheduler('browser-composite-preabort'), trace: rt.trace, defaultOperationTimeoutMs: 1000, abortProviderOnOperationTimeout: true });
    const controller = new AbortController();
    controller.abort(new Error('browser-caller-pre-aborted-before-scheduled-opfs-put'));
    const preAbortSchedule = preAbortAdapter.schedulePut(payload, { id: 'browser-preaborted-caller-signal-opfs-put', label: 'browser-caller-preabort', providerOptions: { signal: controller.signal } });
    const preAbortDrain = await preAbortAdapter.drain({ maxSteps: 2 });
    const preAbortTree = await treeSummary();
    const preAbortSnapshot = preAbortAdapter.snapshot();

    const liveSignalAdapter = mod.createBlockStoreLaneAdapter({ label: 'browser-composite-live-signal-adapter', store, scheduler: makeScheduler('browser-composite-live-signal'), trace: rt.trace, defaultOperationTimeoutMs: 1000, abortProviderOnOperationTimeout: true });
    const liveController = new AbortController();
    const liveSchedule = liveSignalAdapter.schedulePut(new TextEncoder().encode('BrowserRT browser composite abort live signal write'), { id: 'browser-composite-live-signal-put', label: 'browser-composite-live-signal', providerOptions: { signal: liveController.signal, writeBudgetGuard: false } });
    const liveDrain = await liveSignalAdapter.drain({ maxSteps: 3 });
    const liveResult = liveSignalAdapter.result('browser-composite-live-signal-put');
    const liveVerify = liveResult?.ref ? await store.verify(liveResult.ref, { timeoutMs: 500 }) : null;
    const liveRead = liveResult?.ref ? await store.get(liveResult.ref, { timeoutMs: 500 }) : null;
    const liveTree = await treeSummary();
    const cleanupAfterLive = await store.cleanupForTest({ timeoutMs: 500 }).catch(() => false);

    const guardedPrefix = ${JSON.stringify(prefix)} + '/guarded-smoke';
    const guarded = rt.opfsWebLockGuardedBlockStore({
      prefix: guardedPrefix,
      label: 'browser-composite-abort-signal-guarded-smoke',
      lockPrefix: ${JSON.stringify(lockPrefix)},
      lockName: 'composite-abort-signal-lock',
      lockTimeoutMs: 500,
      storeConfig: { writeBudgetGuard: false }
    });
    const guardedCleanupBefore = await guarded.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const guardedPayload = new TextEncoder().encode('BrowserRT guarded smoke composite abort signal path');
    const guardedPut = await guarded.put(guardedPayload, { label: 'browser-composite-abort-signal-guarded-smoke' }, { timeoutMs: 500, writeBudgetGuard: false });
    const guardedVerify = await guarded.verify(guardedPut.ref, { timeoutMs: 500 });
    const guardedRead = await guarded.get(guardedPut.ref, { timeoutMs: 500 });
    const guardedCleanupAfter = await guarded.cleanupForTest({ timeoutMs: 500 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const trace = rt.trace.snapshot();
    const traceKinds = trace.map((row) => row.kind);
    const normalizedTrace = trace.map((row) => ({ kind: row.kind, label: row.label, op: row.op, store: row.store, provider: row.provider, code: row.error?.code || row.code || null, reason: row.reason, stage: row.stage, path: row.path })).filter((row) => row.kind);
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, cleanupBefore, prefixBefore, preAbortSchedule, preAbortDrain, preAbortTree, preAbortSnapshot, liveSchedule, liveDrain, liveResult: liveResult ? { digest: liveResult.digest, bytes: liveResult.bytes, duplicate: liveResult.duplicate, ref: liveResult.ref } : null, liveVerify, liveReadSameBytes: liveRead ? liveRead.byteLength > 0 : false, liveTree, cleanupAfterLive, guardedCleanupBefore, guardedPut: guardedPut ? { digest: guardedPut.digest, bytes: guardedPut.bytes, duplicate: guardedPut.duplicate, ref: guardedPut.ref } : null, guardedVerify, guardedReadSameBytes: guardedRead ? sameBytes(guardedRead, guardedPayload) : false, guardedCleanupAfter, lockSettled, locksAfter: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/composite-abort-signal-proof/${Date.now()}`;
  const lockPrefix = options.lockPrefix || `browserrt:${REVISION}:composite-abort-signal`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser composite abort signal payload ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 22000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/storage-lane-composite-abort-signal-probe.html',
    pageTitle: 'BrowserRT storage lane composite abort signal probe',
    profilePrefix: 'browserrt-composite-abort-signal-',
    stderrTerms: ['opfs', 'storage', 'locks', 'composite-abort']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, lockPrefix, payloadText), timeoutMs);
    mark('browser-storage-lane-composite-abort-signal-eval', started);
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
  assert.equal(observed.prefixBefore, false, 'proof prefix should start absent');

  const preAbortRow = observed.preAbortDrain.results.find((row) => row.opId === 'browser-preaborted-caller-signal-opfs-put');
  assert.equal(observed.preAbortSchedule.accepted, true);
  assert.equal(preAbortRow.ok, false, 'pre-aborted caller signal should reject browser scheduled OPFS put');
  assert.equal(preAbortRow.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(preAbortRow.error.providerDetail?.stage, 'before-digest', 'browser OPFS should see caller pre-abort before digest/open/mutation');
  assert.equal(observed.preAbortTree.fileCount, 0, 'pre-aborted browser OPFS put must leave no files');
  assert.equal(observed.preAbortTree.dirCount, 0, 'pre-aborted browser OPFS put must leave no directories');
  assert.equal(observed.preAbortSnapshot.store.stats.opens, 0, 'pre-aborted browser OPFS put should not open OPFS');
  assert.equal(observed.preAbortSnapshot.executor.stats.operationTimeouts, 0, 'caller pre-abort must not be counted as timeout');
  assert.equal(observed.preAbortSnapshot.executor.stats.providerTimeoutAborts, 0, 'caller pre-abort must not be counted as timeout abort');

  const liveRow = observed.liveDrain.results.find((row) => row.opId === 'browser-composite-live-signal-put');
  assert.equal(observed.liveSchedule.accepted, true);
  assert.equal(liveRow.ok, true, 'live caller signal composed with timeout signal should still allow a normal scheduled write');
  assert.equal(observed.liveVerify.ok, true);
  assert.equal(observed.liveReadSameBytes, true);
  assert.equal(observed.liveTree.fileCount >= 1, true, 'successful live-signal write should produce a block before cleanup');
  assert.equal(observed.cleanupAfterLive, true);

  assert.equal(observed.guardedVerify.ok, true);
  assert.equal(observed.guardedReadSameBytes, true);
  assert.equal(observed.lockSettled.ok, true, 'guarded lock should settle');
  assert.equal(observed.locksAfter?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksAfter?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');
  for (const kind of ['storage:opfs-block-abort', 'storage:opfs-block-put', 'storage:opfs-web-lock-guard-op-complete']) assert.ok(observed.traceKinds.includes(kind), `browser trace missing ${kind}`);

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-storage-lane-composite-abort-signal-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that a caller-supplied provider AbortSignal is not masked by timeout-owned cancellation in scheduled OPFS calls, and that live caller-signal composition still allows guarded writes and drains Web Locks.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'pre-aborted caller providerOptions.signal reaches real OPFS before digest/open/mutation while abortProviderOnOperationTimeout is enabled',
      'caller pre-abort does not enter storage-lane timeout quarantine or timeout-abort counters',
      'a live caller AbortSignal composed with timeout-owned cancellation still allows normal scheduled OPFS writes',
      'guarded OPFS/Web Locks smoke still verifies and drains locks after the composite signal path'
    ],
    nonClaims: [
      'Managed Chromium only; no Firefox/Safari/cross-browser conformance claim.',
      'Abort remains cooperative; providers that ignore AbortSignal may still settle late and require quarantine review.',
      'This does not prove quota reservation, eviction survival, fsync durability, crash/power-loss recovery, Web Locks fairness, multi-tab atomicity, or production readiness.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ chromium: argValue(argv, '--chromium'), timeoutMs: Number(argValue(argv, '--timeout-ms', '22000')), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-storage-lane-composite-abort-signal-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_storage_lane_composite_abort_signal_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
