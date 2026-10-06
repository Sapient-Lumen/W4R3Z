#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PFX}-BROWSER-STORAGE-POSTURE-MANAGED-PROBE.json`;
const TASK_ID = 'browser:storage-posture-managed-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, origin: location.origin };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      storageEstimate: typeof navigator.storage?.estimate === 'function',
      storagePersisted: typeof navigator.storage?.persisted === 'function',
      storagePersist: typeof navigator.storage?.persist === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      webLocksQuery: typeof navigator.locks?.query === 'function'
    };
    const rt = await mod.boot({ telemetry: 'browser-storage-posture-managed-proof', browserCdpHarness: true });
    const budgetPolicy = { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0, requireEstimate: true };
    const direct = await mod.diagnoseBrowserStoragePosture({ globalThis, revision: mod.REVISION, version: mod.VERSION, generatedAt: 'managed-browser-storage-posture-direct', budgetPolicy });
    const runtime = await rt.storage.browserStoragePosture({ generatedAt: 'managed-browser-storage-posture-runtime', budgetPolicy });
    const payload = new TextEncoder().encode('BrowserRT ${REVISION} managed browser storage posture guard proof');
    const guarded = { attempted: direct.admissionPolicy.status === 'admit-with-guard', status: direct.admissionPolicy.status };
    if (guarded.attempted) {
      const postured = await rt.storage.opfsAsyncBlockStoreWithPosture({
        name: 'managed-storage-posture-derived-guard-store',
        prefix: ${JSON.stringify(prefix)},
        budgetPolicy,
        postureLabel: 'managed-storage-posture-postured-factory'
      });
      const store = postured.store;
      const cleanupBefore = await store.cleanupForTest().catch((error) => ({ error: String(error?.message || error) }));
      const put = await store.put(payload, { label: 'managed-storage-posture-derived-guard-put' });
      const verify = await store.verify(put.ref);
      const estimateAfterPut = await store.estimate().catch((error) => ({ error: String(error?.message || error) }));
      const cleanupAfter = await store.cleanupForTest();
      Object.assign(guarded, { postured: { status: postured.status, admissionStatus: postured.admissionPolicy.status, postureFormat: postured.posture.format, writeBudgetGuard: postured.writeBudgetGuard }, cleanupBefore, put: { digest: put.digest, bytes: put.bytes, path: put.path, budget: put.budget }, verify, estimateAfterPut, cleanupAfter, snapshot: store.snapshot() });
      const guardedPostured = await rt.storage.opfsWebLockGuardedBlockStoreWithPosture({
        label: 'managed-storage-posture-web-lock-guarded-store',
        prefix: ${JSON.stringify(prefix + '-web-lock-guarded')},
        lockPrefix: 'browserrt:${REVISION}:managed-storage-posture-web-lock-guarded',
        lockName: 'storage-posture-shared-state',
        lockTimeoutMs: 500,
        budgetPolicy,
        postureLabel: 'managed-storage-posture-web-lock-guarded-factory'
      });
      const guardedStore = guardedPostured.store;
      const guardedSettledBefore = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
      const guardedPut = await guardedStore.put(payload, { label: 'managed-storage-posture-web-lock-derived-guard-put' }, { timeoutMs: 1000 });
      const guardedVerify = await guardedStore.verify(guardedPut.ref, { timeoutMs: 1000 });
      const guardedCleanup = await guardedStore.cleanupForTest({ timeoutMs: 1000 });
      const guardedSettledAfter = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
      guarded.webLockPostured = { status: guardedPostured.status, admissionStatus: guardedPostured.admissionPolicy.status, postureFormat: guardedPostured.posture.format, writeBudgetGuard: guardedPostured.writeBudgetGuard, lockName: guardedPostured.lockName, provider: guardedStore.provider, available: guardedStore.available, settledBefore: guardedSettledBefore, put: { digest: guardedPut.digest, bytes: guardedPut.bytes, path: guardedPut.path, budget: guardedPut.budget }, verify: guardedVerify, cleanup: guardedCleanup, settledAfter: guardedSettledAfter, snapshot: guardedStore.snapshot() };
    }
    const trace = rt.close();
    const locksAfter = capabilities.webLocksQuery ? await navigator.locks.query().catch((error) => ({ error: String(error?.message || error) })) : null;
    return JSON.stringify({ project: 'BrowserRT', revision: mod.REVISION, version: mod.VERSION, page, capabilities, direct, runtime, guarded, locksAfter, traceKinds: trace.map((row) => row.kind), normalizedTrace: trace.map((row) => ({ kind: row.kind, label: row.label, status: row.status, riskLevel: row.riskLevel, warningIds: row.warningIds, requestPersistentStorage: row.requestPersistentStorage, projectedUsageRatio: row.projectedUsageRatio, projectedFreeBytes: row.projectedFreeBytes, reasons: row.reasons, store: row.store, prefix: row.prefix })).filter((row) => row.kind) });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/storage-posture-managed-proof`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 18000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/browser-storage-posture-managed-probe.html',
    pageTitle: 'BrowserRT browser storage posture managed probe',
    profilePrefix: 'browserrt-storage-posture-managed-',
    stderrTerms: ['opfs', 'storage', 'estimate', 'persist', 'quota', 'locks']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix), timeoutMs);
    mark('browser-storage-posture-managed-eval', started);
    out._pageUrl = pageUrl;
    return out;
  });

  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.page.isSecureContext, true);
  assert.equal(observed.capabilities.opfs, true, 'managed browser must expose OPFS for this proof');
  assert.equal(observed.capabilities.storageEstimate, true, 'managed browser must expose StorageManager.estimate() for this proof');
  assert.equal(observed.direct.format, 'browserrt.browser-storage-posture.v1');
  assert.equal(observed.runtime.format, 'browserrt.browser-storage-posture.v1');
  assert.equal(observed.direct.requestPersistentStorage, false, 'managed diagnostic must not call persist() by default');
  assert.equal(observed.direct.persistRequest.skipped, true, 'persist request must be skipped by default in managed browser');
  assert.equal(observed.direct.proof.persistenceNotRequestedByDefault, true);
  assert.equal(observed.direct.proof.admissionPolicyDerived, true);
  assert.equal(observed.direct.proof.mutationGuardActionable, true);
  assert.equal(observed.direct.admissionPolicy.format, 'browserrt.browser-storage-admission-policy.v1');
  assert.equal(observed.direct.admissionPolicy.writeBudgetGuard.enabled, true);
  assert.equal(observed.direct.admissionPolicy.status, 'admit-with-guard', 'fresh managed Chromium profile should admit a tiny guarded write under derived posture policy');
  assert.equal(observed.guarded.attempted, true);
  assert.equal(observed.guarded.postured.status, 'admitted', 'managed proof must use the postured OPFS factory');
  assert.equal(observed.guarded.postured.admissionStatus, 'admit-with-guard');
  assert.equal(observed.guarded.webLockPostured.status, 'admitted-and-guarded', 'managed proof must use the postured Web-Lock-guarded OPFS factory');
  assert.equal(observed.guarded.webLockPostured.admissionStatus, 'admit-with-guard');
  assert.match(observed.guarded.webLockPostured.provider, /^web-lock-guarded:opfs-async-block-store/);
  assert.equal(observed.guarded.webLockPostured.settledBefore.ok, true);
  assert.equal(observed.guarded.webLockPostured.settledAfter.ok, true);
  assert.equal(observed.guarded.verify.ok, true, 'derived managed-browser guard should allow and verify a tiny OPFS write');
  assert.equal(observed.guarded.put.budget.checked, true, 'derived guard must run StorageManager.estimate() before the OPFS mutation');
  assert.equal(observed.guarded.cleanupAfter, true, 'managed proof must clean OPFS prefix after guarded write');
  assert.equal(observed.guarded.webLockPostured.verify.ok, true, 'postured Web-Lock-guarded managed-browser store should verify a tiny OPFS write');
  assert.equal(observed.guarded.webLockPostured.put.budget.checked, true, 'postured Web-Lock-guarded factory must preserve the derived budget guard');
  assert.equal(observed.guarded.webLockPostured.cleanup, true, 'postured Web-Lock-guarded managed-browser store should clean its OPFS prefix');
  assert.ok(Number.isFinite(observed.direct.estimate.quota), 'direct posture estimate must include numeric quota');
  assert.ok(Number.isFinite(observed.direct.estimate.usage), 'direct posture estimate must include numeric usage');
  assert.ok(observed.traceKinds.includes('runtime:browser-storage-posture'), 'runtime storage posture trace must be emitted');
  assert.ok(observed.traceKinds.includes('object:opfs-async-block-store-with-posture-ref'), 'postured OPFS factory trace must be emitted');
  assert.ok(observed.traceKinds.includes('object:opfs-web-lock-guarded-block-store-with-posture-ref'), 'postured Web-Lock-guarded OPFS factory trace must be emitted');
  assert.ok(observed.traceKinds.includes('storage:opfs-web-lock-guard-op-start'), 'postured Web-Lock-guarded store must exercise Web Lock guarded operations');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-write-budget-check'), 'derived guard must emit OPFS budget-check trace');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-put'), 'derived guard tiny write must emit OPFS put trace');
  assert.equal(observed.locksAfter?.held?.length ?? 0, 0, 'managed browser should not leave held Web Locks after storage posture proof');
  assert.equal(observed.locksAfter?.pending?.length ?? 0, 0, 'managed browser should not leave pending Web Locks after storage posture proof');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID,
    probe_id: `${REVISION}-browser-storage-posture-managed-proof`, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that BrowserRT storage posture observes real OPFS/quota/persistence/Web Locks APIs without a hidden persist() call, derives an actionable writeBudgetGuard, and can apply that guard before a tiny OPFS mutation.',
    observations: observed,
    harness,
    claimsChecked: [
      'real managed Chromium OPFS and StorageManager.estimate() are visible',
      'diagnoseBrowserStoragePosture() and runtime.storage.browserStoragePosture() emit posture reports without calling persist() by default',
      'posture derives browser-storage-admission-policy.v1 and an enabled writeBudgetGuard',
      'the postured OPFS factory applies the derived guard before returning a store',
      'the postured Web-Lock-guarded OPFS factory combines quota admission with same-origin Web Lock serialization',
      'the derived guard runs a budget check before a tiny OPFS put and the prefix is cleaned',
      'no Web Locks are left held or pending after the proof'
    ],
    nonClaims: [
      'Managed Chromium/cloudtainer proof only; no cross-browser posture matrix or organic eviction behavior claim.',
      'StorageManager.estimate() is advisory posture evidence, not a quota reservation.',
      'No persistent-storage grant is requested, no fsync/power-loss durability is claimed, and this is not a throughput or storage-timing benchmark.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '18000'));
const chromium = argValue(argv, '--chromium', null);
const prefix = argValue(argv, '--prefix', null);
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');
try {
  const report = await runProbe({ timeoutMs, chromium, prefix, relaxPolicy });
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID, probe_id: `${REVISION}-browser-storage-posture-managed-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.error(out);
  console.error(`[browser_storage_posture_managed_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
