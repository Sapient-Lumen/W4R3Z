#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-WRITE-BUDGET-DUPLICATE-BYPASS-PROBE.json`;
const BROWSER_TASK = 'browser:opfs-block-store-write-budget-duplicate-bypass-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, guardedPrefix, payloadText, newPayloadText) {
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
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, opfsWriteBudgetGuardProof: true, opfsWriteBudgetDuplicateBypassProof: true, browserCdpHarness: true });
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const newPayload = new TextEncoder().encode(${JSON.stringify(newPayloadText)});
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const baselineEstimate = await navigator.storage.estimate();

    const storage = navigator.storage;
    const ownDescriptor = Object.getOwnPropertyDescriptor(storage, 'estimate');
    const prototypeDescriptor = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(storage), 'estimate');
    const originalEstimate = storage.estimate.bind(storage);
    let patchInstalled = false;
    let patchMode = null;
    let estimateMode = 'impossible';
    const estimateCalls = [];
    const patchedEstimate = async function patchedBrowserRtStorageEstimate() {
      estimateCalls.push({ call: estimateCalls.length + 1, mode: estimateMode });
      if (estimateMode === 'generous') return { quota: 100000000, usage: 0, usageDetails: { browserrt: 'generous' } };
      return { quota: 10000, usage: 9900, usageDetails: { browserrt: 'impossible' } };
    };
    try {
      Object.defineProperty(storage, 'estimate', { configurable: true, value: patchedEstimate });
      patchInstalled = storage.estimate === patchedEstimate;
      patchMode = 'defineProperty';
    } catch (defineError) {
      try {
        storage.estimate = patchedEstimate;
        patchInstalled = storage.estimate === patchedEstimate;
        patchMode = 'assignment';
      } catch (assignmentError) {
        patchMode = 'failed:' + (defineError?.name || 'define') + ':' + (assignmentError?.name || 'assign');
      }
    }
    const restoreEstimate = () => {
      try {
        if (ownDescriptor) Object.defineProperty(storage, 'estimate', ownDescriptor);
        else if (prototypeDescriptor) delete storage.estimate;
        else storage.estimate = originalEstimate;
      } catch {}
    };

    const duplicatePrefix = ${JSON.stringify(prefix + '/duplicate')};
    const duplicateSeeder = rt.opfsAsyncBlockStore({ name: 'browser-budget-duplicate-seed-store', prefix: duplicatePrefix });
    const cleanupBeforeDuplicate = await duplicateSeeder.cleanupForTest().catch(() => false);
    const seedPut = await duplicateSeeder.put(payload, { label: 'browser-budget-duplicate-seed' });
    const callsBeforeDuplicate = estimateCalls.length;
    const duplicateStore = rt.opfsAsyncBlockStore({ name: 'browser-budget-duplicate-guarded-store', prefix: duplicatePrefix, writeBudgetGuard: { minFreeBytes: 1000, maxUsageRatio: 0.5, requireEstimate: true } });
    estimateMode = 'impossible';
    const duplicatePut = await capture('browser-duplicate-put-bypasses-impossible-budget', () => duplicateStore.put(payload, { label: 'browser-duplicate-put-bypasses-impossible-budget' }));
    const callsAfterDuplicate = estimateCalls.length;
    const duplicateRead = duplicatePut.ok ? await duplicateStore.get(duplicatePut.value.ref) : null;
    const duplicateVerify = duplicatePut.ok ? await duplicateStore.verify(duplicatePut.value.ref) : null;
    const duplicateSnapshot = duplicateStore.snapshot();

    const rejectPrefix = ${JSON.stringify(prefix + '/new-reject')};
    const rejectStore = rt.opfsAsyncBlockStore({ name: 'browser-budget-new-write-reject-store', prefix: rejectPrefix, writeBudgetGuard: { minFreeBytes: 1000, maxUsageRatio: 0.5, requireEstimate: true } });
    const cleanupBeforeReject = await rejectStore.cleanupForTest().catch(() => false);
    estimateMode = 'impossible';
    const callsBeforeReject = estimateCalls.length;
    const newWriteReject = await capture('browser-new-write-still-rejects-before-mutation', () => rejectStore.put(newPayload, { label: 'browser-new-write-still-rejects-before-mutation' }));
    const callsAfterReject = estimateCalls.length;
    const rejectSnapshot = rejectStore.snapshot();

    const passPrefix = ${JSON.stringify(prefix + '/pass')};
    const passStore = rt.opfsAsyncBlockStore({ name: 'browser-budget-duplicate-pass-store', prefix: passPrefix, writeBudgetGuard: { requireEstimate: true, maxUsageRatio: 1 } });
    const cleanupBeforePass = await passStore.cleanupForTest().catch(() => false);
    estimateMode = 'generous';
    const passPut = await passStore.put(newPayload, { label: 'browser-budget-pass-after-duplicate-bypass' });
    const passVerify = await passStore.verify(passPut.ref);
    const cleanupAfterPass = await passStore.cleanupForTest();

    const guarded = rt.opfsWebLockGuardedBlockStore({ prefix: ${JSON.stringify(guardedPrefix)}, label: 'browser-budget-duplicate-bypass-guarded', lockPrefix: 'browserrt:${REVISION}:budget-duplicate-bypass', lockName: '${REVISION}-budget-duplicate-bypass-lock', lockTimeoutMs: 250, storeConfig: { writeBudgetGuard: { requireEstimate: true, maxUsageRatio: 1 } } });
    const cleanupBeforeGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 }).catch(() => false);
    estimateMode = 'generous';
    const guardedPut = await guarded.put(payload, { label: 'guarded-budget-duplicate-bypass-pass' }, { signal: null, timeoutMs: 300 });
    const guardedVerify = await guarded.verify(guardedPut.ref, { signal: null, timeoutMs: 300 });
    const cleanupAfterGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;

    restoreEstimate();
    const cleanupAfterDuplicate = await duplicateStore.cleanupForTest().catch(() => false);
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const normalizedTrace = rt.trace.snapshot().map((row) => ({ kind: row.kind, store: row.store, prefix: row.prefix, requestedBytes: row.requestedBytes, digest: row.digest, duplicate: row.duplicate, budget: row.budget, reason: row.reason, reasons: row.reasons, source: row.source, lockName: row.lockName, op: row.op })).filter((row) => row.kind);
    const snapshots = { duplicate: duplicateSnapshot, reject: rejectSnapshot, pass: passStore.snapshot(), guarded: guarded.snapshot() };
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, baselineEstimate, patchInstalled, patchMode, cleanupBeforeDuplicate, seedPut: { digest: seedPut.digest, bytes: seedPut.bytes, path: seedPut.path, ref: seedPut.ref }, callsBeforeDuplicate, duplicatePut: duplicatePut.ok ? { label: duplicatePut.label, ok: true, digest: duplicatePut.value.digest, bytes: duplicatePut.value.bytes, duplicate: duplicatePut.value.duplicate, budget: duplicatePut.value.budget, ref: duplicatePut.value.ref } : duplicatePut, callsAfterDuplicate, duplicateEstimateCallsDuringPut: callsAfterDuplicate - callsBeforeDuplicate, duplicateBytesPreserved: duplicateRead ? sameBytes(duplicateRead, payload) : false, duplicateVerify, duplicateSnapshot, cleanupBeforeReject, newWriteReject, callsBeforeReject, callsAfterReject, rejectEstimateCallsDuringPut: callsAfterReject - callsBeforeReject, rejectSnapshot, cleanupBeforePass, passPut: { digest: passPut.digest, bytes: passPut.bytes, duplicate: passPut.duplicate, ref: passPut.ref }, passVerify, cleanupAfterPass, cleanupBeforeGuarded, guardedPut: { digest: guardedPut.digest, bytes: guardedPut.bytes, ref: guardedPut.ref }, guardedVerify, cleanupAfterGuarded, lockSettled, locksAfterGuarded: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, cleanupAfterDuplicate, estimateCalls, snapshots, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-write-budget-duplicate-bypass-proof`;
  const guardedPrefix = options.guardedPrefix || `browserrt/${REVISION}/opfs-block-store-write-budget-duplicate-bypass-guarded-proof`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser OPFS write budget duplicate bypass proof ${Date.now()}`;
  const newPayloadText = options.newPayloadText || `BrowserRT ${REVISION} browser OPFS new write budget reject proof ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 20000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-write-budget-duplicate-bypass-probe.html',
    pageTitle: 'BrowserRT OPFS block-store write budget duplicate bypass probe',
    profilePrefix: 'browserrt-opfs-budget-duplicate-bypass-',
    stderrTerms: ['opfs', 'storage', 'quota', 'estimate', 'budget', 'duplicate']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, guardedPrefix, payloadText, newPayloadText), timeoutMs);
    mark('browser-opfs-block-store-write-budget-duplicate-bypass-eval', started);
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
  assert.equal(observed.capabilities.storageEstimate, true, 'StorageManager.estimate must be available');
  assert.equal(observed.capabilities.webLocks, true, 'Web Locks must be available for guarded smoke path');
  assert.equal(observed.patchInstalled, true, `navigator.storage.estimate patch must install for this browser proof (${observed.patchMode})`);
  assert.equal(observed.duplicatePut.ok, true, 'browser duplicate put should succeed under impossible budget');
  assert.equal(observed.duplicatePut.duplicate, true, 'browser duplicate put should be marked duplicate');
  assert.equal(observed.duplicatePut.budget.bypassed, true, 'browser duplicate put should bypass budget');
  assert.equal(observed.duplicateEstimateCallsDuringPut, 0, 'browser duplicate bypass should not call patched estimate');
  assert.equal(observed.duplicateBytesPreserved, true, 'browser duplicate bytes should read back');
  assert.equal(observed.duplicateVerify.ok, true, 'browser duplicate should verify');
  assert.equal(observed.duplicateSnapshot.stats.writeBudgetDuplicateBypasses, 1, 'browser duplicate bypass stat should increment');
  assert.equal(observed.duplicateSnapshot.stats.writeBudgetChecks, 0, 'browser duplicate bypass should not record budget check');
  assert.equal(observed.newWriteReject.ok, false, 'browser new write should still reject under impossible budget');
  assert.equal(observed.newWriteReject.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.equal(observed.rejectEstimateCallsDuringPut, 1, 'browser new write reject should call patched estimate once');
  assert.equal(observed.rejectSnapshot.opened, false, 'browser new write reject should not open mutable OPFS prefix');
  assert.equal(observed.rejectSnapshot.stats.writeBudgetRejects, 1, 'browser new write reject stat should increment');
  assert.equal(observed.passVerify.ok, true, 'browser passing raw budget write should verify');
  assert.equal(observed.cleanupAfterPass, true, 'browser pass prefix should clean up');
  assert.equal(observed.guardedVerify.ok, true, 'guarded OPFS/Web Locks path should verify');
  assert.equal(observed.cleanupAfterGuarded, true, 'guarded prefix should clean up');
  assert.equal(observed.lockSettled.ok, true, 'guarded lock should settle');
  assert.equal(observed.locksAfterGuarded?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksAfterGuarded?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');
  for (const kind of ['storage:opfs-block-write-budget-duplicate-bypass', 'storage:opfs-block-write-budget-reject', 'storage:opfs-block-put', 'storage:opfs-web-lock-guard-op-complete']) {
    assert.ok(observed.traceKinds.includes(kind), `browser trace missing ${kind}`);
  }

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-write-budget-duplicate-bypass-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that OpfsAsyncBlockStore writeBudgetGuard is duplicate-aware in a real browser: a seeded valid duplicate put bypasses an impossible patched estimate without calling estimate, while a new write still rejects before mutable OPFS open and guarded OPFS/Web Locks writes still verify under a passing estimate.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'valid duplicate put bypasses writeBudgetGuard without calling navigator.storage.estimate',
      'new non-duplicate put still rejects under impossible projected-usage budget before mutable OPFS open',
      'passing raw budget write verifies',
      'Web-Lock-guarded OPFS store still writes/verifies and leaves no held/pending locks'
    ],
    nonClaims: [
      'Managed Chromium only; no Firefox/Safari/cross-browser conformance claim.',
      'Patched estimate proves control-flow boundaries, not quota reservation, eviction survival, fsync durability, crash/power-loss recovery, tamper-proof storage, multi-tab atomicity, or production readiness.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', 20000)), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-block-store-write-budget-duplicate-bypass-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_block_store_write_budget_duplicate_bypass_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
