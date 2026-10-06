#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-WRITE-BUDGET-GUARD-PROBE.json`;
const BROWSER_TASK = 'browser:opfs-block-store-write-budget-guard-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, guardedPrefix, payloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      storageEstimate: typeof navigator.storage?.estimate === 'function',
      storagePersisted: typeof navigator.storage?.persisted === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      textEncoder: typeof TextEncoder === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, opfsWriteBudgetGuardProof: true, browserCdpHarness: true });
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const baselineEstimate = await navigator.storage.estimate();
    const persistedBefore = navigator.storage.persisted ? await navigator.storage.persisted().catch((error) => ({ error: String(error?.message || error) })) : null;

    const rejectStore = rt.opfsAsyncBlockStore({ name: 'browser-opfs-budget-reject-store', prefix: ${JSON.stringify(prefix + '/reject')}, writeBudgetGuard: { maxUsageRatio: Number.MIN_VALUE, requireEstimate: true } });
    const budgetReject = await capture('raw-write-budget-reject-before-open', () => rejectStore.put(payload, { label: 'raw-write-budget-reject-before-open' }));
    const budgetRejectSnapshot = rejectStore.snapshot();

    const perPutStore = rt.opfsAsyncBlockStore({ name: 'browser-opfs-budget-per-put-store', prefix: ${JSON.stringify(prefix + '/per-put')} });
    const perPutReject = await capture('raw-per-put-write-budget-reject-before-open', () => perPutStore.put(payload, { label: 'raw-per-put-write-budget-reject-before-open' }, { writeBudgetGuard: { maxUsageRatio: Number.MIN_VALUE, requireEstimate: true } }));
    const perPutRejectSnapshot = perPutStore.snapshot();

    const passStore = rt.opfsAsyncBlockStore({ name: 'browser-opfs-budget-pass-store', prefix: ${JSON.stringify(prefix + '/pass')}, writeBudgetGuard: { requireEstimate: true, maxUsageRatio: 1 } });
    const cleanupBeforePass = await passStore.cleanupForTest().catch(() => false);
    const passPut = await passStore.put(payload, { label: 'raw-write-budget-pass' });
    const passVerify = await passStore.verify(passPut.ref);
    const passEstimate = await passStore.estimate();
    const cleanupAfterPass = await passStore.cleanupForTest();

    const guarded = rt.opfsWebLockGuardedBlockStore({ prefix: ${JSON.stringify(guardedPrefix)}, label: 'browser-opfs-budget-guarded', lockPrefix: 'browserrt:${REVISION}:opfs-budget', lockName: '${REVISION}-opfs-budget-lock', lockTimeoutMs: 250, storeConfig: { writeBudgetGuard: { requireEstimate: true, maxUsageRatio: 1 } } });
    const cleanupBeforeGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 }).catch(() => false);
    const guardedPut = await guarded.put(payload, { label: 'guarded-write-budget-pass' }, { signal: null, timeoutMs: 300 });
    const guardedVerify = await guarded.verify(guardedPut.ref, { signal: null, timeoutMs: 300 });
    const cleanupAfterGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const locksAfterGuarded = locksQuery;
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const normalizedTrace = rt.trace.snapshot().map((row) => ({ kind: row.kind, store: row.store, prefix: row.prefix, requestedBytes: row.requestedBytes, quota: row.quota, usage: row.usage, projectedFreeBytes: row.projectedFreeBytes, projectedUsageRatio: row.projectedUsageRatio, reasons: row.reasons, error: row.error, lockName: row.lockName, op: row.op })).filter((row) => row.kind);
    const snapshots = { reject: budgetRejectSnapshot, perPut: perPutRejectSnapshot, pass: passStore.snapshot(), guarded: guarded.snapshot() };
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, baselineEstimate, persistedBefore, budgetReject, budgetRejectSnapshot, perPutReject, perPutRejectSnapshot, cleanupBeforePass, passPut: { digest: passPut.digest, bytes: passPut.bytes, path: passPut.path, ref: passPut.ref }, passVerify, passEstimate, cleanupAfterPass, cleanupBeforeGuarded, guardedPut: { digest: guardedPut.digest, bytes: guardedPut.bytes, path: guardedPut.path, ref: guardedPut.ref }, guardedVerify, cleanupAfterGuarded, lockSettled, locksAfterGuarded: locksAfterGuarded ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, snapshots, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-write-budget-guard-proof`;
  const guardedPrefix = options.guardedPrefix || `browserrt/${REVISION}/opfs-block-store-write-budget-guarded-proof`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser OPFS write budget guard proof ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 18000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-write-budget-guard-probe.html',
    pageTitle: 'BrowserRT OPFS block-store write budget guard probe',
    profilePrefix: 'browserrt-opfs-write-budget-guard-',
    stderrTerms: ['opfs', 'storage', 'quota', 'estimate', 'budget']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, guardedPrefix, payloadText), timeoutMs);
    mark('browser-opfs-block-store-write-budget-guard-eval', started);
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
  assert.equal(observed.capabilities.storageEstimate, true, 'StorageManager.estimate must be available for browser budget proof');
  assert.equal(observed.budgetReject.ok, false, 'browser raw budget reject must reject');
  assert.equal(observed.budgetReject.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.ok(observed.budgetReject.error.detail.reasons.includes('max-usage-ratio'), 'browser reject must include max-usage-ratio reason');
  assert.equal(observed.budgetRejectSnapshot.opened, false, 'browser raw budget reject must not open OPFS');
  assert.equal(observed.perPutReject.ok, false, 'browser per-put budget reject must reject');
  assert.equal(observed.perPutReject.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.equal(observed.perPutRejectSnapshot.opened, false, 'browser per-put budget reject must not open OPFS');
  assert.equal(observed.passVerify.ok, true, 'browser passing write budget guard should allow raw put/verify');
  assert.equal(observed.cleanupAfterPass, true, 'browser pass prefix should clean up');
  assert.equal(observed.guardedVerify.ok, true, 'guarded OPFS/Web Locks path should write/verify with passing budget guard');
  assert.equal(observed.cleanupAfterGuarded, true, 'guarded prefix should clean up');
  assert.equal(observed.lockSettled.ok, true, 'guarded lock should settle after budget proof');
  assert.equal(observed.locksAfterGuarded?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksAfterGuarded?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');
  assert.ok(Number.isFinite(observed.baselineEstimate?.quota), 'baseline estimate should include numeric quota');
  assert.ok(Number.isFinite(observed.baselineEstimate?.usage), 'baseline estimate should include numeric usage');
  for (const kind of ['storage:opfs-block-write-budget-check', 'storage:opfs-block-write-budget-reject', 'storage:opfs-block-put', 'storage:opfs-web-lock-guard-op-complete']) {
    assert.ok(observed.traceKinds.includes(kind), `browser trace missing ${kind}`);
  }

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-write-budget-guard-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that OpfsAsyncBlockStore writeBudgetGuard uses real navigator.storage.estimate() in the browser realm: impossible projected-usage thresholds reject before OPFS open, while passing raw and Web-Lock-guarded writes still verify and drain locks.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'real navigator.storage.estimate() returns quota/usage data for the proof origin',
      'constructor writeBudgetGuard impossible projected-usage ratio rejects before raw OPFS provider open',
      'per-put writeBudgetGuard projected usage threshold rejects before raw OPFS provider open',
      'passing raw OPFS writeBudgetGuard put/verify succeeds and cleans up',
      'Web-Lock-guarded OPFS store still writes/verifies with a passing budget guard and drains locks'
    ],
    nonClaims: [
      'Managed Chromium only; no cross-browser, production-readiness, durability, fsync, organic eviction, crash/power-loss, quota-policy, or capacity guarantee.',
      'StorageManager.estimate values are approximate and the guard is not a true storage reservation.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', 18000)), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-block-store-write-budget-guard-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_block_store_write_budget_guard_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
