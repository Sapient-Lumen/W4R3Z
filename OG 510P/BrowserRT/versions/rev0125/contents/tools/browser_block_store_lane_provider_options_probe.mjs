#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-BLOCK-STORE-LANE-PROVIDER-OPTIONS-PROBE.json`;
const BROWSER_TASK = 'browser:block-store-lane-provider-options-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, lockPrefix, payloadText, secondPayloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      storageEstimate: typeof navigator.storage?.estimate === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      textEncoder: typeof TextEncoder === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ blockStoreLaneProviderOptionsProof: true, opfsAsyncBlockStoreProof: true, opfsWebLocksProof: true, browserCdpHarness: true });
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const secondPayload = new TextEncoder().encode(${JSON.stringify(secondPayloadText)});
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const prefixExists = async (candidatePrefix) => {
      try {
        let dir = await navigator.storage.getDirectory();
        for (const part of String(candidatePrefix).split('/').filter(Boolean)) dir = await dir.getDirectoryHandle(part, { create: false });
        return true;
      } catch (error) {
        if (error?.name === 'NotFoundError') return false;
        throw error;
      }
    };
    const newAdapter = (label, guard) => {
      const scheduler = mod.createCrossLaneScheduler({
        label: label + ':scheduler',
        trace: rt.trace,
        lanes: [
          { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
          { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
        ]
      });
      return mod.createBlockStoreLaneAdapter({ label, store: guard, scheduler, trace: rt.trace });
    };

    const baselineEstimate = await navigator.storage.estimate().catch(() => ({ quota: 1000000000, usage: 0 }));
    const impossibleReserve = Number.isFinite(Number(baselineEstimate?.quota)) ? Math.floor(Number(baselineEstimate.quota)) + 1 : Number.MAX_SAFE_INTEGER;
    const store = rt.opfsAsyncBlockStore({
      name: 'browser-lane-provider-options-store',
      prefix: ${JSON.stringify(prefix)},
      writeBudgetGuard: false
    });
    const cleanupBefore = await store.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const prefixBefore = await prefixExists(${JSON.stringify(prefix)});

    const rejectAdapter = newAdapter('browser-lane-provider-options-reject-adapter', store);
    const rejectSchedule = rejectAdapter.schedulePut(payload, {
      id: 'browser-provider-budget-reject-put',
      providerOptions: { timeoutMs: 500, writeBudgetGuard: { maxUsageRatio: 1e-30, requireEstimate: true } },
      label: 'browser-provider-budget-reject'
    });
    const rejectDrain = await rejectAdapter.drain({ maxSteps: 2 });
    const prefixAfterReject = await prefixExists(${JSON.stringify(prefix)});
    const rejectSnapshot = rejectAdapter.snapshot();

    const overrideAdapter = newAdapter('browser-lane-provider-options-override-adapter', store);
    const overrideSchedule = overrideAdapter.schedulePut(payload, {
      id: 'browser-provider-budget-override-put',
      providerOptions: { timeoutMs: 500, writeBudgetGuard: { maxUsageRatio: 1e-30, requireEstimate: true } },
      putOptions: { timeoutMs: 500, writeBudgetGuard: false },
      label: 'browser-provider-budget-override'
    });
    const overrideDrain = await overrideAdapter.drain({ maxSteps: 2 });
    const overrideResult = overrideAdapter.result('browser-provider-budget-override-put');
    const overrideVerify = overrideResult?.ref ? await store.verify(overrideResult.ref, { timeoutMs: 500 }) : null;
    const overrideRead = overrideResult?.ref ? await store.get(overrideResult.ref, { timeoutMs: 500 }) : null;
    const prefixAfterOverride = await prefixExists(${JSON.stringify(prefix)});
    const overrideSnapshot = overrideAdapter.snapshot();

    const abortController = new AbortController();
    abortController.abort('browser-provider-options-scheduled-get-abort');
    const abortAdapter = newAdapter('browser-lane-provider-options-abort-adapter', store);
    const abortSchedule = abortAdapter.scheduleGet(overrideResult.ref, { id: 'browser-provider-aborted-get', providerOptions: { signal: abortController.signal } });
    const abortDrain = await abortAdapter.drain({ maxSteps: 2 });
    const postAbortVerify = await store.verify(overrideResult.ref, { timeoutMs: 500 });
    const abortSnapshot = abortAdapter.snapshot();

    const secondAdapter = newAdapter('browser-lane-provider-options-second-adapter', store);
    const secondSchedule = secondAdapter.schedulePut(secondPayload, { id: 'browser-provider-second-put', storeOptions: { timeoutMs: 500, writeBudgetGuard: false }, label: 'browser-provider-second-put' });
    const secondDrain = await secondAdapter.drain({ maxSteps: 2 });
    const secondResult = secondAdapter.result('browser-provider-second-put');
    const secondVerify = secondResult?.ref ? await store.verify(secondResult.ref, { timeoutMs: 500 }) : null;
    const cleanupAfter = await store.cleanupForTest({ timeoutMs: 500 });

    const guardedPrefix = ${JSON.stringify(prefix)} + '/guarded-smoke';
    const guarded = rt.opfsWebLockGuardedBlockStore({
      prefix: guardedPrefix,
      label: 'browser-lane-provider-options-guarded-smoke',
      lockPrefix: ${JSON.stringify(lockPrefix)},
      lockName: 'provider-options-lock',
      lockTimeoutMs: 500,
      storeConfig: { writeBudgetGuard: false }
    });
    const guardedCleanupBefore = await guarded.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const guardedPayload = new TextEncoder().encode('BrowserRT guarded smoke provider options path');
    const guardedPut = await guarded.put(guardedPayload, { label: 'browser-provider-options-guarded-smoke' }, { timeoutMs: 500, writeBudgetGuard: false });
    const guardedVerify = await guarded.verify(guardedPut.ref, { timeoutMs: 500 });
    const guardedRead = await guarded.get(guardedPut.ref, { timeoutMs: 500 });
    const guardedCleanupAfter = await guarded.cleanupForTest({ timeoutMs: 500 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;

    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const normalizedTrace = rt.trace.snapshot().map((row) => ({ kind: row.kind, label: row.label, op: row.op, store: row.store, provider: row.provider, lockName: row.lockName, providerOptionKeys: row.providerOptionKeys, code: row.error?.code || row.code || null, reason: row.reason, reasons: row.reasons, digest: row.digest, path: row.path })).filter((row) => row.kind);
    const guardedSnapshot = guarded.snapshot();
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, baselineEstimate, impossibleReserve, cleanupBefore, prefixBefore, rejectSchedule, rejectDrain, prefixAfterReject, rejectSnapshot, overrideSchedule, overrideDrain, overrideResult: overrideResult ? { digest: overrideResult.digest, bytes: overrideResult.bytes, duplicate: overrideResult.duplicate, budget: overrideResult.budget, ref: overrideResult.ref } : null, overrideVerify, overrideReadSameBytes: overrideRead ? sameBytes(overrideRead, payload) : false, prefixAfterOverride, overrideSnapshot, abortSchedule, abortDrain, postAbortVerify, abortSnapshot, secondSchedule, secondDrain, secondResult: secondResult ? { digest: secondResult.digest, bytes: secondResult.bytes, duplicate: secondResult.duplicate, budget: secondResult.budget, ref: secondResult.ref } : null, secondVerify, cleanupAfter, guardedCleanupBefore, guardedPut: guardedPut ? { digest: guardedPut.digest, bytes: guardedPut.bytes, duplicate: guardedPut.duplicate, budget: guardedPut.budget, ref: guardedPut.ref } : null, guardedVerify, guardedReadSameBytes: guardedRead ? sameBytes(guardedRead, guardedPayload) : false, guardedCleanupAfter, lockSettled, locksAfter: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, guardedSnapshot, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/block-store-lane-provider-options-proof/${Date.now()}`;
  const lockPrefix = options.lockPrefix || `browserrt:${REVISION}:lane-provider-options`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser block-store lane provider options payload ${Date.now()}`;
  const secondPayloadText = options.secondPayloadText || `BrowserRT ${REVISION} browser block-store lane provider options second payload ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 25000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/block-store-lane-provider-options-probe.html',
    pageTitle: 'BrowserRT block-store lane provider options probe',
    profilePrefix: 'browserrt-lane-provider-options-',
    stderrTerms: ['opfs', 'storage', 'locks', 'provider-options']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, lockPrefix, payloadText, secondPayloadText), timeoutMs);
    mark('browser-block-store-lane-provider-options-eval', started);
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
  assert.equal(observed.capabilities.storageEstimate, true, 'StorageManager.estimate must be available for browser budget proof');

  assert.equal(observed.prefixBefore, false, 'proof prefix should start absent');
  const rejectRow = observed.rejectDrain.results.find((row) => row.opId === 'browser-provider-budget-reject-put');
  assert.equal(rejectRow.ok, false, 'providerOptions.writeBudgetGuard should reject scheduled browser put');
  assert.equal(rejectRow.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.equal(observed.prefixAfterReject, false, 'providerOptions budget reject should happen before OPFS prefix creation');
  assert.ok(observed.rejectSchedule.scheduler.task.metadata.providerOptionKeys.includes('writeBudgetGuard'), 'schedule metadata should expose provider option keys');

  const overrideRow = observed.overrideDrain.results.find((row) => row.opId === 'browser-provider-budget-override-put');
  assert.equal(overrideRow.ok, true, 'putOptions.writeBudgetGuard=false should override inherited impossible provider budget in browser path');
  assert.equal(observed.overrideResult.budget.enabled, false);
  assert.equal(observed.overrideVerify.ok, true);
  assert.equal(observed.overrideReadSameBytes, true);
  assert.equal(observed.prefixAfterOverride, true, 'successful override put should create prefix');

  const abortRow = observed.abortDrain.results.find((row) => row.opId === 'browser-provider-aborted-get');
  assert.equal(abortRow.ok, false, 'providerOptions.signal should abort the scheduled OPFS read');
  assert.ok(['BRT_WEB_LOCK_ABORTED', 'BRT_OPFS_OPERATION_ABORTED'].includes(abortRow.error.code), `unexpected abort code ${abortRow.error.code}`);
  assert.equal(observed.postAbortVerify.ok, true, 'aborted scheduled read must not corrupt the block');

  const secondRow = observed.secondDrain.results.find((row) => row.opId === 'browser-provider-second-put');
  assert.equal(secondRow.ok, true, 'storeOptions should reach a second scheduled browser put');
  assert.equal(observed.secondVerify.ok, true);
  assert.equal(observed.cleanupAfter, true, 'browser prefix should clean up at end');
  assert.equal(observed.lockSettled.ok, true, 'guarded lock should settle');
  assert.equal(observed.locksAfter?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksAfter?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');
  for (const kind of ['block-store-lane:schedule', 'storage:opfs-block-write-budget-reject', 'storage:opfs-web-lock-guard-op-complete']) {
    assert.ok(observed.traceKinds.includes(kind), `browser trace missing ${kind}`);
  }

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-block-store-lane-provider-options-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that scheduled block-store providerOptions/storeOptions survive through BlockStoreLaneAdapter into the OPFS path, with a separate Web Lock guarded smoke path.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'providerOptions.writeBudgetGuard rejects a scheduled OPFS put before prefix creation',
      'named putOptions can override inherited providerOptions in the scheduled browser OPFS path',
      'providerOptions.signal reaches the scheduled OPFS read path and aborts without corrupting the block',
      'storeOptions reach a scheduled OPFS put and the Web Lock drains afterward'
    ],
    nonClaims: [
      'Managed Chromium only; no Firefox/Safari/cross-browser conformance claim.',
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-block-store-lane-provider-options-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_block_store_lane_provider_options_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
