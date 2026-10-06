#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, boot, diagnoseBrowserStoragePosture, createBrowserStorageRecoveryGuidance, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT, digestBytesHex } from '../src/public-api.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-STORAGE-POSTURE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function fakeBrowserGlobal({ persisted = false, grant = false } = {}) {
  const calls = { estimate: 0, persisted: 0, persist: 0 };
  return {
    calls,
    globalThis: {
      navigator: {
        storage: {
          getDirectory() { return {}; },
          async estimate() { calls.estimate += 1; return { quota: 1000, usage: 400, usageDetails: { fileSystem: 400 } }; },
          async persisted() { calls.persisted += 1; return persisted; },
          async persist() { calls.persist += 1; return grant; }
        },
        locks: {
          async request(_name, callback) { return await callback({ name: _name, mode: 'exclusive' }); },
          async query() { return { held: [], pending: [] }; }
        }
      }
    }
  };
}


function fakeAbortError(message = 'Fake Web Lock request aborted before acquisition') {
  if (typeof DOMException === 'function') return new DOMException(message, 'AbortError');
  const error = new Error(message);
  error.name = 'AbortError';
  return error;
}

function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }

function fakeContentionWebLocks() {
  const state = new Map();
  const events = [];
  const rowFor = (name) => {
    if (!state.has(name)) state.set(name, { active: [], queue: [] });
    return state.get(name);
  };
  const counts = (row) => Object.freeze({ held: row.active.length, pending: row.queue.length });
  const canAcquire = (row, mode) => mode === 'exclusive' ? row.active.length === 0 : !row.active.some((entry) => entry.mode === 'exclusive');
  const removeAbortListener = (entry) => {
    if (entry.signal && entry.onAbort && typeof entry.signal.removeEventListener === 'function') {
      try { entry.signal.removeEventListener('abort', entry.onAbort); } catch {}
    }
    entry.onAbort = null;
  };
  const pump = (name) => {
    const row = rowFor(name);
    while (row.queue.length > 0) {
      const next = row.queue[0];
      if (!canAcquire(row, next.mode)) return;
      row.queue.shift();
      acquire(name, row, next);
      if (next.mode === 'exclusive') return;
    }
  };
  const abortQueued = (name, entry) => {
    const row = rowFor(name);
    const idx = row.queue.indexOf(entry);
    if (idx >= 0) row.queue.splice(idx, 1);
    removeAbortListener(entry);
    events.push({ event: 'abort-queued', name, mode: entry.mode, label: entry.label, ...counts(row) });
    entry.reject(fakeAbortError());
    pump(name);
  };
  function acquire(name, row, entry) {
    removeAbortListener(entry);
    row.active.push(entry);
    events.push({ event: 'acquire', name, mode: entry.mode, label: entry.label, ...counts(row) });
    Promise.resolve()
      .then(() => entry.callback(Object.freeze({ name, mode: entry.mode })))
      .then(entry.resolve, entry.reject)
      .finally(() => {
        const idx = row.active.indexOf(entry);
        if (idx >= 0) row.active.splice(idx, 1);
        events.push({ event: 'release', name, mode: entry.mode, label: entry.label, ...counts(row) });
        pump(name);
      });
  }
  return Object.freeze({
    events,
    request(name, options, callback) {
      if (typeof options === 'function') { callback = options; options = {}; }
      const mode = options?.mode || 'exclusive';
      const label = options?.metadata?.op || options?.metadata?.label || mode;
      const signal = options?.signal || null;
      const row = rowFor(name);
      events.push({ event: 'request', name, mode, label, hasSignal: Boolean(signal), signalAborted: signal?.aborted === true, ...counts(row) });
      return new Promise((resolve, reject) => {
        const entry = { mode, label, callback, resolve, reject, signal, onAbort: null };
        if (signal?.aborted) { events.push({ event: 'abort-before-queue', name, mode, label, ...counts(row) }); reject(fakeAbortError('Fake Web Lock request already aborted')); return; }
        if (signal && typeof signal.addEventListener === 'function') {
          entry.onAbort = () => abortQueued(name, entry);
          signal.addEventListener('abort', entry.onAbort, { once: true });
        }
        row.queue.push(entry);
        pump(name);
      });
    },
    async query() {
      const held = [];
      const pending = [];
      for (const [name, row] of state.entries()) {
        held.push(...row.active.map((entry) => ({ name, mode: entry.mode, clientId: entry.label })));
        pending.push(...row.queue.map((entry) => ({ name, mode: entry.mode, clientId: entry.label })));
      }
      return { held, pending };
    }
  });
}

async function waitForPredicate(label, fn, { timeoutMs = 500, intervalMs = 5 } = {}) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const value = await fn();
    if (value) return value;
    await sleep(intervalMs);
  }
  throw new Error(`timed out waiting for ${label}`);
}

function fakeWebLocks() {
  const requests = [];
  return Object.freeze({
    requests,
    async request(name, options, callback) {
      if (typeof options === 'function') { callback = options; options = {}; }
      const mode = options?.mode || 'exclusive';
      requests.push(Object.freeze({ name, mode, ifAvailable: options?.ifAvailable === true, steal: options?.steal === true, hasSignal: Boolean(options?.signal) }));
      if (options?.ifAvailable === true) return await callback({ name, mode });
      return await callback({ name, mode });
    },
    async query() { return { held: [], pending: [] }; }
  });
}

export async function runProbe() {
  const bestEffort = fakeBrowserGlobal({ persisted: false, grant: false });
  const report = await diagnoseBrowserStoragePosture({ globalThis: bestEffort.globalThis, revision: REVISION, version: VERSION, generatedAt: 'deterministic-browser-storage-posture-probe' });
  assert.equal(report.format, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT);
  assert.equal(report.status, 'observed');
  assert.equal(report.riskLevel, 'needs-product-policy');
  assert.equal(report.capabilities.opfs, true);
  assert.equal(report.capabilities.webLocks, true);
  assert.equal(report.estimate.ok, true);
  assert.equal(report.estimate.quota, 1000);
  assert.equal(report.estimate.usage, 400);
  assert.equal(report.persisted.ok, true);
  assert.equal(report.persisted.persisted, false);
  assert.equal(report.persistRequest.requested, false);
  assert.equal(report.proof.persistenceNotRequestedByDefault, true);
  assert.equal(report.admissionPolicy.format, 'browserrt.browser-storage-admission-policy.v1');
  assert.equal(report.admissionPolicy.status, 'admit-with-guard');
  assert.equal(report.admissionPolicy.writeBudgetGuard.enabled, true);
  assert.equal(report.admissionPolicy.writeBudgetGuard.transientWriteMultiplier, 2);
  assert.equal(report.admissionPolicy.storagePrivacyPolicy.enabled, true);
  assert.equal(report.admissionPolicy.storagePrivacyPolicy.storageTimingSideChannelReview, false);
  assert.equal(report.opfsPostureReceipt.storagePrivacy.status, 'no-planned-large-opfs-write-observed');
  assert.equal(report.proof.storageTimingPrivacyReviewVisible, true);
  assert.equal(report.proof.noStorageTimingMitigationClaim, true);
  assert.equal(report.writeBudgetGuard.source, 'browser-storage-posture-admission-policy');
  assert.equal(report.proof.admissionPolicyDerived, true);
  assert.equal(report.proof.mutationGuardActionable, true);
  assert.equal(report.opfsPostureReceipt.format, 'browserrt.browser-storage-posture-receipt.v1');
  assert.equal(report.opfsPostureReceipt.quota.source, 'StorageManager.estimate()');
  assert.equal(report.opfsPostureReceipt.internalByteLedger.provided, false);
  assert.equal(report.opfsPostureReceipt.persistence.persisted, false);
  assert.equal(report.opfsPostureReceipt.coordination.webLocksAvailable, true);
  assert.equal(report.opfsPostureReceipt.lastMutationReceipt, null);
  assert.equal(report.opfsPostureReceipt.proof.noQuotaReservationClaim, true);
  assert.equal(report.opfsPostureReceipt.proof.noEvictionSurvivalClaim, true);
  assert.equal(report.opfsPostureReceipt.proof.noPrivacySideChannelClaim, true);
  assert.equal(bestEffort.calls.persist, 0, 'diagnostic must not call persist() by default');
  assert.ok(report.warnings.some((row) => row.id === 'best-effort-storage'), 'best-effort storage warning must be visible');
  assert.ok(report.nonClaims.some((claim) => /eviction survival|fsync|cross-browser/i.test(claim)), 'non-claims must name durability/browser limits');

  const plannedFake = fakeBrowserGlobal({ persisted: true, grant: true });
  const plannedReport = await diagnoseBrowserStoragePosture({
    globalThis: plannedFake.globalThis,
    generatedAt: 'deterministic-browser-storage-posture-planned-write-probe',
    budgetPolicy: { plannedWriteBytes: 600, maxUsageRatio: 0.9, reserveRatio: 0.05 }
  });
  assert.equal(plannedReport.admissionPolicy.projectedWritableBytes, 500);
  assert.equal(plannedReport.admissionPolicy.plannedWriteBytes, 600);
  assert.equal(plannedReport.admissionPolicy.plannedBudgetedBytes, 1200);
  assert.equal(plannedReport.admissionPolicy.transientWriteMultiplier, 2);
  assert.equal(plannedReport.admissionPolicy.plannedWriteFits, false);
  assert.equal(plannedReport.admissionPolicy.status, 'reject-planned-write-over-budget');
  assert.equal(plannedReport.opfsPostureReceipt.admission.plannedWriteFits, false);
  assert.equal(plannedReport.opfsPostureReceipt.admission.plannedBudgetedBytes, 1200);
  assert.ok(plannedReport.warnings.some((row) => row.id === 'storage-admission-planned-write-over-budget'), 'planned write over budget warning must be visible');

  const privacyReviewReport = await diagnoseBrowserStoragePosture({
    globalThis: { navigator: {
      storage: { getDirectory() { return {}; }, async estimate() { return { quota: 10 * 1024 * 1024 * 1024, usage: 0, usageDetails: { fileSystem: 0 } }; }, async persisted() { return true; } },
      locks: fakeWebLocks()
    } },
    generatedAt: 'deterministic-browser-storage-posture-storage-timing-privacy-probe',
    budgetPolicy: { plannedWriteBytes: 700 * 1024 * 1024, transientWriteMultiplier: 1 }
  });
  assert.equal(privacyReviewReport.admissionPolicy.status, 'admit-with-guard');
  assert.equal(privacyReviewReport.admissionPolicy.storagePrivacyPolicy.storageTimingSideChannelReview, true);
  assert.equal(privacyReviewReport.admissionPolicy.storagePrivacyPolicy.absoluteRisk, true);
  assert.equal(privacyReviewReport.opfsPostureReceipt.storagePrivacy.manualReviewRequired, true);
  assert.ok(privacyReviewReport.warnings.some((row) => row.id === 'storage-timing-side-channel-review'), 'large planned OPFS writes must surface a storage-timing privacy review warning');

  const ledgerFake = fakeBrowserGlobal({ persisted: true, grant: true });
  const ledgerReport = await diagnoseBrowserStoragePosture({
    globalThis: ledgerFake.globalThis,
    generatedAt: 'deterministic-browser-storage-posture-byte-ledger-probe',
    internalByteLedger: { bytes: 512, blockCount: 3, exact: true, source: 'browserrt-opfs-block-ledger', lastMutationReceipt: { id: 'mut-1', op: 'put', digest: 'sha256:test', bytes: 128, committed: true } },
    lastMutationReceipt: { id: 'mut-2', op: 'delete', digest: 'sha256:old', committed: true, source: 'caller' }
  });
  assert.equal(ledgerReport.opfsPostureReceipt.internalByteLedger.provided, true);
  assert.equal(ledgerReport.opfsPostureReceipt.internalByteLedger.bytes, 512);
  assert.equal(ledgerReport.opfsPostureReceipt.internalByteLedger.blockCount, 3);
  assert.equal(ledgerReport.opfsPostureReceipt.internalByteLedger.exact, true);
  assert.equal(ledgerReport.opfsPostureReceipt.lastMutationReceipt.id, 'mut-2');
  assert.equal(ledgerReport.opfsPostureReceipt.persistence.persisted, true);

  const request = fakeBrowserGlobal({ persisted: false, grant: false });
  const requested = await diagnoseBrowserStoragePosture({ globalThis: request.globalThis, revision: REVISION, version: VERSION, requestPersistentStorage: true, generatedAt: 'deterministic-browser-storage-posture-persist-request-probe' });
  assert.equal(request.calls.persist, 1, 'persist() must only be called when explicitly requested');
  assert.equal(requested.persistRequest.requested, true);
  assert.equal(requested.persistRequest.granted, false);
  assert.ok(requested.warnings.some((row) => row.id === 'persistent-storage-denied'), 'denied persist() warning must be visible');

  const runtimeFake = fakeBrowserGlobal({ persisted: false, grant: false });
  const rt = await boot({ telemetry: 'browser-storage-posture-probe' });
  const runtimeReport = await rt.storage.browserStoragePosture({ globalThis: runtimeFake.globalThis, generatedAt: 'deterministic-runtime-storage-posture-probe' });
  const kernelReport = await rt.storage.kernelKitStoragePosture({ globalThis: runtimeFake.globalThis, generatedAt: 'deterministic-kernel-storage-posture-probe' });
  await rt.closeAsync({ reason: 'browser-storage-posture-probe-complete' });
  assert.equal(runtimeReport.format, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT);
  assert.equal(runtimeReport.proof.persistenceNotRequestedByDefault, true);
  assert.equal(kernelReport.browserStoragePosture.format, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT);
  assert.equal(kernelReport.proof.browserStoragePostureDiagnostic, true);
  assert.equal(kernelReport.proof.admissionPolicyDerived, true);
  assert.equal(kernelReport.proof.mutationGuardActionable, true);

  const directRecoveryGuidance = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTWebLockCoordinatorError', code: 'BRT_WEB_LOCK_TIMEOUT', message: 'timed out', detail: { name: 'browserrt:test-lock', mode: 'exclusive', timeoutMs: 25 } }, { op: 'put' });
  assert.equal(directRecoveryGuidance.format, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT);
  assert.equal(directRecoveryGuidance.category, 'lock-contention');
  assert.equal(directRecoveryGuidance.preMutationRejected, true);
  assert.equal(directRecoveryGuidance.shouldQueryLocks, true);

  const serviceWorkerWaitUntilGuidance = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTServiceWorkerLifecycleError', code: 'BRT_SW_WAITUNTIL_LATE_FAILURE', message: 'redacted waitUntil late failure', detail: { op: 'service-worker-waituntil', stage: 'post-response-waituntil', name: 'browserrt:redacted-sw-lock', mode: 'exclusive', timeoutMs: 15000 } }, { source: 'browser-storage-posture-probe' });
  assert.equal(serviceWorkerWaitUntilGuidance.category, 'service-worker-lifecycle');
  assert.equal(serviceWorkerWaitUntilGuidance.phase, 'service-worker-waituntil-post-response');
  assert.equal(serviceWorkerWaitUntilGuidance.mutationAttempted, true);
  assert.equal(serviceWorkerWaitUntilGuidance.preMutationRejected, false);
  assert.equal(serviceWorkerWaitUntilGuidance.shouldQueryLocks, true);
  assert.equal(serviceWorkerWaitUntilGuidance.shouldVerifyDigestBeforeRetry, true);
  assert.equal(serviceWorkerWaitUntilGuidance.retryHint.serviceWorkerSettlementRequired, true);
  assert.equal(serviceWorkerWaitUntilGuidance.shouldRetryAutomatically, false);

  const guardedAdmission = await withFakeNavigator(async (root) => {
    const pressureReport = await diagnoseBrowserStoragePosture({ globalThis, revision: REVISION, version: VERSION, generatedAt: 'deterministic-storage-admission-pressure-probe', budgetPolicy: { maxUsageRatio: 0.9, reserveRatio: 0.05 } });
    assert.equal(pressureReport.admissionPolicy.status, 'reject-until-storage-freed');
    assert.ok(pressureReport.warnings.some((row) => row.id === 'storage-admission-rejecting-new-writes'), 'admission rejecting warning must be visible under quota pressure');
    const pressureRuntime = await boot({ telemetry: 'browser-storage-posture-guarded-admission' });
    let factoryRejection = null;
    try {
      await pressureRuntime.storage.opfsAsyncBlockStoreWithPosture({ name: 'posture-admission-rejected-store', prefix: 'browserrt/posture-admission-rejected-store', budgetPolicy: { maxUsageRatio: 0.9, reserveRatio: 0.05 } });
    } catch (error) {
      factoryRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    assert.equal(factoryRejection?.code, 'BRT_BROWSER_STORAGE_ADMISSION_REJECTED', 'postured factory must reject before creating a store under quota pressure');
    assert.equal(factoryRejection?.detail?.recovery?.format, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT, 'postured factory rejection must carry recovery guidance');
    assert.equal(factoryRejection?.detail?.recovery?.preMutationRejected, true, 'postured factory rejection guidance must be pre-mutation');
    const store = pressureRuntime.storage.opfsAsyncBlockStore({ name: 'posture-admission-guard-store', prefix: 'browserrt/posture-admission-guard', writeBudgetGuard: pressureReport.writeBudgetGuard });
    let rejection = null;
    try {
      await store.put(new Uint8Array(32), { label: 'quota-pressure-guarded-put' });
    } catch (error) {
      rejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    await pressureRuntime.closeAsync({ reason: 'browser-storage-posture-guarded-admission-complete' });
    assert.equal(rejection?.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'derived writeBudgetGuard must reject before OPFS mutation when current posture has no writable budget');
    assert.equal(rejection?.detail?.recovery?.format, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT, 'write budget rejection must carry recovery guidance');
    assert.equal(rejection?.detail?.recovery?.preMutationRejected, true, 'write budget recovery guidance must classify the rejection as pre-mutation');
    const tree = fakeTreeSummary(root);
    assert.equal(tree.fileCount, 0, 'postured factory plus derived guard must reject before creating OPFS files');
    return { pressureStatus: pressureReport.admissionPolicy.status, projectedWritableBytes: pressureReport.admissionPolicy.projectedWritableBytes, factoryRejection, rejection, tree };
  }, { estimate: { quota: 1000, usage: 950, usageDetails: { fileSystem: 950 } } });

  const plannedWriteAdmission = await withFakeNavigator(async (root) => {
    const plannedRuntime = await boot({ telemetry: 'browser-storage-posture-planned-write-admission' });
    let factoryRejection = null;
    try {
      await plannedRuntime.storage.opfsAsyncBlockStoreWithPosture({
        name: 'posture-planned-write-rejected-store',
        prefix: 'browserrt/posture-planned-write-rejected-store',
        budgetPolicy: { plannedWriteBytes: 600, maxUsageRatio: 0.9, reserveRatio: 0.05 }
      });
    } catch (error) {
      factoryRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    await plannedRuntime.closeAsync({ reason: 'browser-storage-posture-planned-write-admission-complete' });
    assert.equal(factoryRejection?.code, 'BRT_BROWSER_STORAGE_ADMISSION_REJECTED', 'postured factory must reject before creating a store when plannedWriteBytes exceeds projected writable budget');
    assert.equal(factoryRejection?.detail?.status, 'reject-planned-write-over-budget');
    assert.equal(factoryRejection?.detail?.plannedWriteBytes, 600);
    assert.equal(factoryRejection?.detail?.plannedBudgetedBytes, 1200);
    assert.equal(factoryRejection?.detail?.transientWriteMultiplier, 2);
    assert.equal(factoryRejection?.detail?.plannedWriteFits, false);
    assert.equal(factoryRejection?.detail?.recovery?.preMutationRejected, true);
    const tree = fakeTreeSummary(root);
    assert.equal(tree.fileCount, 0, 'planned-write admission rejection must not create OPFS files');
    return { factoryRejection, tree };
  }, { estimate: { quota: 1000, usage: 400, usageDetails: { fileSystem: 400 } } });



  const posturedGuardOverrideRejection = await withFakeNavigator(async (root) => {
    const overrideRuntime = await boot({ telemetry: 'browser-storage-posture-guard-override' });
    const attempts = [];
    for (const attempt of [
      { label: 'top-level-disabled', config: { writeBudgetGuard: false }, expectedSource: 'config.writeBudgetGuard' },
      { label: 'store-config-disabled', config: { storeConfig: { writeBudgetGuard: false } }, expectedSource: 'storeConfig.writeBudgetGuard' }
    ]) {
      let factoryRejection = null;
      try {
        await overrideRuntime.storage.opfsAsyncBlockStoreWithPosture({
          name: `posture-guard-override-rejected-store-${attempt.label}`,
          prefix: `browserrt/posture-guard-override-rejected-store-${attempt.label}`,
          budgetPolicy: { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0 },
          ...attempt.config
        });
      } catch (error) {
        factoryRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
      }
      assert.equal(factoryRejection?.code, 'BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED', 'postured factory must reject explicit writeBudgetGuard override by default');
      assert.equal(factoryRejection?.detail?.preMutationRejected, true, 'postured guard override rejection must be pre-mutation');
      assert.equal(factoryRejection?.detail?.recovery?.format, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT, 'guard override rejection must carry recovery guidance');
      assert.equal(factoryRejection?.detail?.source, attempt.expectedSource, 'guard override rejection must name the override source');
      assert.equal(factoryRejection?.detail?.disabled, true, 'guard override rejection must flag disabled guard attempts');
      assert.equal(factoryRejection?.detail?.postureGuardPolicy?.format, 'browserrt.postured-write-budget-guard-policy.v1');
      assert.equal(factoryRejection?.detail?.postureGuardPolicy?.enforced, true);
      attempts.push(Object.freeze({ label: attempt.label, factoryRejection }));
    }
    await overrideRuntime.closeAsync({ reason: 'browser-storage-posture-guard-override-complete' });
    const tree = fakeTreeSummary(root);
    assert.equal(tree.fileCount, 0, 'postured guard override rejection must not create OPFS files');
    return { attempts, tree };
  }, { estimate: { quota: 1000, usage: 100, usageDetails: { fileSystem: 100 } } });

  const posturedStoreAdmission = await withFakeNavigator(async (root) => {
    const posturedRuntime = await boot({ telemetry: 'browser-storage-posture-postured-store-admission' });
    const postured = await posturedRuntime.storage.opfsAsyncBlockStoreWithPosture({
      name: 'posture-admitted-store',
      prefix: 'browserrt/posture-admitted-store',
      budgetPolicy: { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0 }
    });
    assert.equal(postured.status, 'admitted');
    assert.equal(postured.admissionPolicy.status, 'admit-with-guard');
    assert.equal(postured.writeBudgetGuard.enabled, true);
    assert.equal(postured.writeBudgetGuard.source, 'browser-storage-posture-admission-policy');
    assert.equal(postured.postureGuardPolicy.format, 'browserrt.postured-write-budget-guard-policy.v1');
    assert.equal(postured.postureGuardPolicy.enforced, true);
    assert.equal(postured.postureGuardPolicy.suppliedOverride, false);
    assert.equal(postured.store.writeBudgetGuard.source, 'constructor.writeBudgetGuard');
    assert.equal(postured.store.writeBudgetGuard.policySource, 'browser-storage-posture-admission-policy');
    const put = await postured.store.put(new Uint8Array([1, 2, 3, 4]), { label: 'postured-store-admitted-put' });
    const verify = await postured.store.verify(put.ref);
    const cleanup = await postured.store.cleanupForTest();
    const overridePayload = new Uint8Array([9, 9, 9, 9]);
    const overrideDigest = `sha256:${await digestBytesHex(overridePayload)}`;
    let putOverrideRejection = null;
    try {
      await postured.store.put(overridePayload, { label: 'postured-store-per-put-override-rejected' }, { writeBudgetGuard: false });
    } catch (error) {
      putOverrideRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    const overridePresent = await postured.store.has(overrideDigest);
    const tree = fakeTreeSummary(root);
    await posturedRuntime.closeAsync({ reason: 'browser-storage-posture-postured-store-admission-complete' });
    assert.equal(verify.ok, true, 'admitted postured store should verify a guarded fake-OPFS write');
    assert.equal(cleanup, true);
    assert.equal(putOverrideRejection?.code, 'BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED', 'postured store must reject per-put writeBudgetGuard override attempts');
    assert.equal(putOverrideRejection?.detail?.preMutationRejected, true, 'postured per-put override rejection must be pre-mutation');
    assert.equal(putOverrideRejection?.detail?.overrideRejected, true, 'postured per-put override rejection must be explicit');
    assert.deepEqual(putOverrideRejection?.detail?.overrideKeys, ['writeBudgetGuard'], 'postured per-put override rejection must name the override key');
    assert.equal(overridePresent, false, 'postured per-put override rejection must not create the target block');
    assert.equal(tree.fileCount, 0, 'admitted postured store proof must clean fake OPFS files and reject override before mutation');
    return { status: postured.status, admissionStatus: postured.admissionPolicy.status, allowWriteBudgetGuardOverride: postured.store.allowWriteBudgetGuardOverride, put: { digest: put.digest, bytes: put.bytes, budget: put.budget }, verify, cleanup, putOverrideRejection, overridePresent, tree };
  }, { estimate: { quota: 1000, usage: 100, usageDetails: { fileSystem: 100 } } });

  const posturedWebLockLocks = fakeWebLocks();
  const posturedWebLockStoreAdmission = await withFakeNavigator(async (root) => {
    const locks = posturedWebLockLocks;
    const guardedRuntime = await boot({ telemetry: 'browser-storage-posture-postured-web-lock-store-admission' });
    const postured = await guardedRuntime.storage.opfsWebLockGuardedBlockStoreWithPosture({
      label: 'posture-admitted-web-lock-guarded-store',
      prefix: 'browserrt/posture-admitted-web-lock-guarded-store',
      lockPrefix: 'browserrt:posture-admitted-web-lock-guarded-store',
      lockName: 'shared-local-state',
      budgetPolicy: { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0 }
    });
    assert.equal(postured.status, 'admitted-and-guarded');
    assert.equal(postured.admissionPolicy.status, 'admit-with-guard');
    assert.equal(postured.writeBudgetGuard.source, 'browser-storage-posture-admission-policy');
    assert.equal(postured.postureGuardPolicy.format, 'browserrt.postured-write-budget-guard-policy.v1');
    assert.equal(postured.postureGuardPolicy.enforced, true);
    assert.equal(postured.store.available, true);
    assert.match(postured.store.provider, /^web-lock-guarded:opfs-async-block-store/);
    assert.equal(postured.lockContentionPolicy.source, 'postured-web-lock-guarded-opfs-factory');
    assert.equal(postured.lockFallbackPolicy.singleOwnerFallbackRequested, false);
    assert.equal(postured.lockFallbackPolicy.lockAvailable, true);
    assert.equal(postured.lockContentionPolicy.defaulted, true);
    assert.ok(postured.lockContentionPolicy.lockTimeoutMs > 0, 'postured Web-Lock-guarded factory must install a bounded lock wait by default');
    const before = await postured.store.waitForSettled({ timeoutMs: 100, intervalMs: 5 });
    const put = await postured.store.put(new Uint8Array([5, 6, 7, 8]), { label: 'postured-web-lock-store-admitted-put' });
    const verify = await postured.store.verify(put.ref);
    const cleanup = await postured.store.cleanupForTest();
    const guardedOverridePayload = new Uint8Array([8, 7, 6, 5]);
    const guardedOverrideDigest = `sha256:${await digestBytesHex(guardedOverridePayload)}`;
    let putOverrideRejection = null;
    try {
      await postured.store.put(guardedOverridePayload, { label: 'postured-web-lock-store-per-put-override-rejected' }, { writeBudgetGuard: false });
    } catch (error) {
      putOverrideRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    const timeoutOverridePayload = new Uint8Array([4, 3, 2, 1]);
    const timeoutOverrideDigest = `sha256:${await digestBytesHex(timeoutOverridePayload)}`;
    let timeoutOverrideRejection = null;
    try {
      await postured.store.put(timeoutOverridePayload, { label: 'postured-web-lock-store-unbounded-timeout-override-rejected' }, { timeoutMs: 0 });
    } catch (error) {
      timeoutOverrideRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    const guardedOverridePresent = await postured.store.has(guardedOverrideDigest, { timeoutMs: 100 });
    const timeoutOverridePresent = await postured.store.has(timeoutOverrideDigest, { timeoutMs: 100 });
    const after = await postured.store.waitForSettled({ timeoutMs: 100, intervalMs: 5 });
    const snapshot = postured.store.snapshot();
    const tree = fakeTreeSummary(root);
    await guardedRuntime.closeAsync({ reason: 'browser-storage-posture-postured-web-lock-store-admission-complete' });
    assert.equal(before.ok, true, 'postured Web-Lock-guarded store should start settled');
    assert.equal(verify.ok, true, 'postured Web-Lock-guarded store should verify a guarded fake-OPFS write');
    assert.equal(put.budget.checked, true, 'postured Web-Lock-guarded store should run the derived budget guard before mutation');
    assert.equal(put.budget.guard.policySource, 'browser-storage-posture-admission-policy', 'postured Web-Lock-guarded put should preserve the posture policy source after guard normalization');
    assert.equal(cleanup, true);
    assert.equal(putOverrideRejection?.code, 'BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED', 'postured Web-Lock-guarded store must reject per-put writeBudgetGuard override attempts');
    assert.equal(putOverrideRejection?.detail?.preMutationRejected, true, 'postured guarded per-put override rejection must be pre-mutation');
    assert.equal(timeoutOverrideRejection?.code, 'BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED', 'postured Web-Lock-guarded store must reject unbounded per-operation lock timeout overrides');
    assert.equal(timeoutOverrideRejection?.detail?.preMutationRejected, true, 'postured unbounded lock timeout override rejection must be pre-mutation');
    assert.equal(timeoutOverrideRejection?.detail?.recovery?.shouldQueryLocks, true, 'timeout override recovery should preserve lock-inspection guidance');
    assert.equal(guardedOverridePresent, false, 'postured guarded per-put override rejection must not create the target block');
    assert.equal(timeoutOverridePresent, false, 'postured unbounded timeout override rejection must not create the target block');
    assert.equal(after.ok, true, 'postured Web-Lock-guarded store should settle after cleanup and override rejection');
    assert.equal(tree.fileCount, 0, 'postured Web-Lock-guarded store proof must clean fake OPFS files and reject override before mutation');
    return { status: postured.status, admissionStatus: postured.admissionPolicy.status, lockName: postured.lockName, lockContentionPolicy: postured.lockContentionPolicy, lockFallbackPolicy: postured.lockFallbackPolicy, put: { digest: put.digest, bytes: put.bytes, budget: put.budget }, verify, cleanup, putOverrideRejection, timeoutOverrideRejection, guardedOverridePresent, timeoutOverridePresent, before, after, snapshot, tree, lockRequests: locks.requests };
  }, { estimate: { quota: 1000, usage: 100, usageDetails: { fileSystem: 100 } }, navigatorExtras: { locks: posturedWebLockLocks } });

  const posturedWebLockUnboundedFactoryRejection = await withFakeNavigator(async (root) => {
    const runtime = await boot({ telemetry: 'browser-storage-posture-postured-web-lock-unbounded-factory-rejection' });
    let factoryRejection = null;
    try {
      await runtime.storage.opfsWebLockGuardedBlockStoreWithPosture({
        label: 'posture-unbounded-web-lock-timeout-rejected',
        prefix: 'browserrt/posture-unbounded-web-lock-timeout-rejected',
        lockTimeoutMs: 0,
        budgetPolicy: { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0 }
      });
    } catch (error) {
      factoryRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    await runtime.closeAsync({ reason: 'browser-storage-posture-postured-web-lock-unbounded-factory-rejection-complete' });
    const tree = fakeTreeSummary(root);
    assert.equal(factoryRejection?.code, 'BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED', 'postured guarded factory must reject lockTimeoutMs:0 before store creation');
    assert.equal(factoryRejection?.detail?.preMutationRejected, true, 'postured guarded unbounded factory rejection must be pre-mutation');
    assert.equal(factoryRejection?.detail?.recovery?.shouldQueryLocks, true, 'unbounded factory rejection recovery should preserve lock inspection guidance');
    assert.equal(tree.fileCount, 0, 'unbounded timeout factory rejection must not create OPFS files');
    return { factoryRejection, tree };
  }, { estimate: { quota: 1000, usage: 100, usageDetails: { fileSystem: 100 } }, navigatorExtras: { locks: fakeWebLocks() } });

  const posturedWebLockSingleOwnerFallbackRejection = await withFakeNavigator(async (root) => {
    const runtime = await boot({ telemetry: 'browser-storage-posture-postured-web-lock-single-owner-fallback-rejection' });
    let fallbackRejection = null;
    try {
      await runtime.storage.opfsWebLockGuardedBlockStoreWithPosture({
        label: 'posture-web-lock-single-owner-fallback-rejected',
        prefix: 'browserrt/posture-web-lock-single-owner-fallback-rejected',
        requireWebLocks: false,
        budgetPolicy: { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0 }
      });
    } catch (error) {
      fallbackRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    await runtime.closeAsync({ reason: 'browser-storage-posture-postured-web-lock-single-owner-fallback-rejection-complete' });
    const tree = fakeTreeSummary(root);
    assert.equal(fallbackRejection?.code, 'BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED', 'postured guarded factory must require an explicit unsafe opt-in for unlocked fallback');
    assert.equal(fallbackRejection?.detail?.preMutationRejected, true, 'single-owner fallback rejection must be pre-mutation');
    assert.equal(fallbackRejection?.detail?.fallbackPolicy?.singleOwnerFallbackRequested, true, 'fallback policy must mark the requested unlocked fallback');
    assert.equal(fallbackRejection?.detail?.fallbackPolicy?.allowUnsafeSingleOwnerFallback, false, 'fallback policy must record missing unsafe opt-in');
    assert.equal(fallbackRejection?.detail?.recovery?.category, 'coordination-fallback-policy', 'fallback rejection must carry recovery guidance');
    assert.equal(tree.fileCount, 0, 'single-owner fallback rejection must not create OPFS files');
    return { fallbackRejection, tree };
  }, { estimate: { quota: 1000, usage: 100, usageDetails: { fileSystem: 100 } } });

  const posturedWebLockSingleOwnerFallbackAdmission = await withFakeNavigator(async (root) => {
    const runtime = await boot({ telemetry: 'browser-storage-posture-postured-web-lock-single-owner-fallback-admission' });
    const postured = await runtime.storage.opfsWebLockGuardedBlockStoreWithPosture({
      label: 'posture-web-lock-single-owner-fallback-admitted',
      prefix: 'browserrt/posture-web-lock-single-owner-fallback-admitted',
      requireWebLocks: false,
      allowUnsafeSingleOwnerFallback: true,
      budgetPolicy: { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0 }
    });
    assert.equal(postured.status, 'admitted-single-owner-fallback');
    assert.equal(postured.lockFallbackPolicy.singleOwnerFallbackRequested, true);
    assert.equal(postured.lockFallbackPolicy.allowUnsafeSingleOwnerFallback, true);
    assert.equal(postured.store.snapshot().available, false);
    const put = await postured.store.put(new Uint8Array([9, 8, 7, 6]), { label: 'postured-single-owner-fallback-put' });
    const verify = await postured.store.verify(put.ref);
    const cleanup = await postured.store.cleanupForTest();
    const snapshot = postured.store.snapshot();
    await runtime.closeAsync({ reason: 'browser-storage-posture-postured-web-lock-single-owner-fallback-admission-complete' });
    const tree = fakeTreeSummary(root);
    assert.equal(verify.ok, true, 'explicit unsafe single-owner fallback should still use the postured store and verify locally');
    assert.equal(put.budget.checked, true, 'explicit unsafe single-owner fallback must keep the storage budget guard');
    assert.equal(cleanup, true);
    assert.equal(tree.fileCount, 0, 'explicit unsafe single-owner fallback proof must clean fake OPFS files');
    return { status: postured.status, lockFallbackPolicy: postured.lockFallbackPolicy, put: { digest: put.digest, bytes: put.bytes, budget: put.budget }, verify, cleanup, snapshot, tree };
  }, { estimate: { quota: 1000, usage: 100, usageDetails: { fileSystem: 100 } } });

  const posturedLaneAdapterLocks = fakeWebLocks();
  const posturedLaneAdapterAdmission = await withFakeNavigator(async (root) => {
    const laneRuntime = await boot({ telemetry: 'browser-storage-posture-postured-lane-adapter-admission' });
    const posturedLane = await laneRuntime.storage.opfsWebLockGuardedStorageLaneAdapterWithPosture({
      label: 'posture-admitted-web-lock-guarded-lane-adapter',
      prefix: 'browserrt/posture-admitted-web-lock-guarded-lane-adapter',
      lockPrefix: 'browserrt:posture-admitted-web-lock-guarded-lane-adapter',
      lockName: 'shared-local-state',
      budgetPolicy: { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0 },
      storeConfig: { verifyAfterWrite: true, verifyOnHas: true }
    });
    assert.equal(posturedLane.status, 'admitted-guarded-lane-adapter');
    assert.equal(posturedLane.adapterFactorySource, 'postured-web-lock-guarded-storage-lane-adapter-factory');
    assert.equal(posturedLane.posturedGuarded.status, 'admitted-and-guarded');
    assert.equal(posturedLane.admissionPolicy.status, 'admit-with-guard');
    assert.equal(posturedLane.writeBudgetGuard.source, 'browser-storage-posture-admission-policy');
    assert.equal(posturedLane.postureGuardPolicy.format, 'browserrt.postured-write-budget-guard-policy.v1');
    assert.equal(posturedLane.postureGuardPolicy.enforced, true);
    assert.equal(posturedLane.lockContentionPolicy.source, 'postured-web-lock-guarded-opfs-factory');
    const payload = new TextEncoder().encode('postured guarded storage lane adapter proof');
    const scheduledPut = posturedLane.adapter.schedulePut(payload, {
      id: 'postured-lane-adapter-put',
      priority: 'user-visible',
      label: 'postured-lane-adapter-put',
      putOptions: { writeBudgetGuard: posturedLane.writeBudgetGuard }
    });
    assert.equal(scheduledPut.accepted, true, 'postured guarded storage-lane adapter should accept an admitted put');
    const drainPut = await posturedLane.adapter.drain({ maxSteps: 4 });
    const put = posturedLane.adapter.result('postured-lane-adapter-put');
    assert.equal(put?.budget?.checked, true, 'postured guarded storage-lane adapter put should run a budget guard before mutation');
    assert.equal(put?.budget?.guard?.policySource, 'browser-storage-posture-admission-policy', 'storage-lane adapter put should preserve posture policy source');
    posturedLane.adapter.scheduleVerify(put.ref, { id: 'postured-lane-adapter-verify', priority: 'user-visible' });
    posturedLane.adapter.scheduleCleanupForTest({ id: 'postured-lane-adapter-cleanup' });
    const drainVerifyCleanup = await posturedLane.adapter.drain({ maxSteps: 4 });
    const verify = posturedLane.adapter.result('postured-lane-adapter-verify');
    const settled = await posturedLane.guardedStore.waitForSettled({ timeoutMs: 100, intervalMs: 5 });
    const adapterSnapshot = posturedLane.adapter.snapshot();
    const storeSnapshot = posturedLane.guardedStore.snapshot();
    const tree = fakeTreeSummary(root);
    await laneRuntime.closeAsync({ reason: 'browser-storage-posture-postured-lane-adapter-admission-complete' });
    assert.equal(verify?.ok, true, 'postured guarded storage-lane adapter should verify through the guarded provider');
    assert.equal(settled.ok, true, 'postured guarded storage-lane adapter should settle its Web Lock after scheduled work');
    assert.equal(tree.fileCount, 0, 'postured guarded storage-lane adapter proof must clean fake OPFS files');
    return { status: posturedLane.status, adapterFactorySource: posturedLane.adapterFactorySource, admissionStatus: posturedLane.admissionPolicy.status, lockContentionPolicy: posturedLane.lockContentionPolicy, scheduledPut: { accepted: scheduledPut.accepted, id: scheduledPut.id ?? scheduledPut.task?.id ?? null }, drainPut: drainPut.results.map((row) => ({ op: row.op, ok: row.ok, dispatched: row.dispatched })), drainVerifyCleanup: drainVerifyCleanup.results.map((row) => ({ op: row.op, ok: row.ok, dispatched: row.dispatched })), put: { digest: put.digest, bytes: put.bytes, budget: put.budget }, verify, settled, adapterSnapshot, storeSnapshot, tree, lockRequests: posturedLaneAdapterLocks.requests };
  }, { estimate: { quota: 1000, usage: 100, usageDetails: { fileSystem: 100 } }, navigatorExtras: { locks: posturedLaneAdapterLocks } });

  const contentionLocks = fakeContentionWebLocks();
  const posturedWebLockContention = await withFakeNavigator(async (root) => {
    const contentionRuntime = await boot({ telemetry: 'browser-storage-posture-postured-web-lock-contention' });
    const postured = await contentionRuntime.storage.opfsWebLockGuardedBlockStoreWithPosture({
      label: 'posture-contention-web-lock-guarded-store',
      prefix: 'browserrt/posture-contention-web-lock-guarded-store',
      lockPrefix: 'browserrt:posture-contention-web-lock-guarded-store',
      lockName: 'shared-local-state',
      lockTimeoutMs: 25,
      budgetPolicy: { maxUsageRatio: 0.99, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0 }
    });
    let releaseHolder;
    const holderReleased = new Promise((resolve) => { releaseHolder = resolve; });
    const holder = postured.store.withExclusive(async () => {
      await holderReleased;
      return 'holder-released';
    }, { op: 'postured-contention-holder' });
    await waitForPredicate('exclusive lock holder to acquire', async () => {
      const q = await postured.store.queryLocks();
      return q.heldCount === 1 ? q : null;
    });
    const payload = new TextEncoder().encode('postured-lock-contention-should-not-write');
    const digest = `sha256:${await digestBytesHex(payload)}`;
    let timeoutRejection = null;
    try {
      await postured.store.put(payload, { label: 'postured-lock-contention-timeout-put' });
    } catch (error) {
      timeoutRejection = { name: error?.name || 'Error', code: error?.code || null, message: error?.message || String(error), detail: error?.detail || null };
    }
    assert.equal(timeoutRejection?.code, 'BRT_WEB_LOCK_TIMEOUT', 'postured guarded store must timeout queued lock acquisition before mutation');
    assert.equal(timeoutRejection?.detail?.recovery?.format, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT, 'lock timeout must carry recovery guidance');
    assert.equal(timeoutRejection?.detail?.recovery?.shouldQueryLocks, true, 'lock timeout recovery guidance must tell callers to inspect held/pending locks');
    const runtimeGuidance = contentionRuntime.storage.browserStorageRecoveryGuidance(timeoutRejection, { op: 'put' });
    assert.equal(runtimeGuidance.category, 'lock-contention', 'runtime storage namespace must classify lock timeout recovery guidance');
    releaseHolder();
    const holderResult = await holder;
    const timedOutPresent = await postured.store.has(digest, { timeoutMs: 100 });
    const recoveryPut = await postured.store.put(new Uint8Array([9, 10, 11]), { label: 'postured-lock-contention-recovery-put' }, { timeoutMs: 100 });
    const recoveryVerify = await postured.store.verify(recoveryPut.ref, { timeoutMs: 100 });
    const cleanup = await postured.store.cleanupForTest({ timeoutMs: 100 });
    const settled = await postured.store.waitForSettled({ timeoutMs: 100, intervalMs: 5 });
    const snapshot = postured.store.snapshot();
    const tree = fakeTreeSummary(root);
    await contentionRuntime.closeAsync({ reason: 'browser-storage-posture-postured-web-lock-contention-complete' });
    assert.equal(holderResult, 'holder-released');
    assert.equal(timedOutPresent, false, 'timed-out lock acquisition must not publish the payload digest');
    assert.equal(recoveryVerify.ok, true, 'postured guarded store should recover after lock-acquisition timeout');
    assert.equal(cleanup, true);
    assert.equal(settled.ok, true);
    assert.equal(tree.fileCount, 0, 'postured lock-contention proof must clean fake OPFS files');
    return { status: postured.status, lockContentionPolicy: postured.lockContentionPolicy, timeoutRejection, digest, timedOutPresent, recoveryPut: { digest: recoveryPut.digest, bytes: recoveryPut.bytes }, recoveryVerify, cleanup, settled, snapshot, tree, fakeLockEvents: contentionLocks.events };
  }, { estimate: { quota: 1000, usage: 100, usageDetails: { fileSystem: 100 } }, navigatorExtras: { locks: contentionLocks } });

  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    status: 'passed',
    probe_id: `${REVISION}-browser-storage-posture`,
    purpose: 'Product-facing BrowserRT storage posture diagnostic: OPFS/quota/persistence/Web Locks are reported without hidden persist() calls, with explicit best-effort warnings and non-claims.',
    proof: {
      directDiagnosticObserved: report.status === 'observed',
      directRecoveryGuidanceExported: directRecoveryGuidance.format === BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT && directRecoveryGuidance.preMutationRejected === true,
      serviceWorkerWaitUntilGuidanceClassified: serviceWorkerWaitUntilGuidance.category === 'service-worker-lifecycle' && serviceWorkerWaitUntilGuidance.shouldQueryLocks === true && serviceWorkerWaitUntilGuidance.shouldVerifyDigestBeforeRetry === true && serviceWorkerWaitUntilGuidance.shouldRetryAutomatically === false,
      opfsCapabilityObserved: report.capabilities.opfs === true,
      quotaEstimateObserved: report.estimate.ok === true,
      webLocksObserved: report.capabilities.webLocks === true,
      admissionPolicyDerived: report.proof.admissionPolicyDerived === true,
      derivedWriteBudgetGuardActionable: report.admissionPolicy.writeBudgetGuard.enabled === true,
      opfsPostureReceiptNamesQuotaLedgerPersistenceLocksAndNonClaims: report.opfsPostureReceipt.format === 'browserrt.browser-storage-posture-receipt.v1' && report.opfsPostureReceipt.quota.ok === true && report.opfsPostureReceipt.internalByteLedger.provided === false && report.opfsPostureReceipt.persistence.persisted === false && report.opfsPostureReceipt.coordination.webLocksAvailable === true && report.opfsPostureReceipt.proof.noPrivacySideChannelClaim === true,
      internalByteLedgerReceiptObserved: ledgerReport.opfsPostureReceipt.internalByteLedger.provided === true && ledgerReport.opfsPostureReceipt.internalByteLedger.bytes === 512 && ledgerReport.opfsPostureReceipt.lastMutationReceipt?.id === 'mut-2',
      plannedWriteAdmissionRejectsBeforeStoreCreation: plannedReport.admissionPolicy.status === 'reject-planned-write-over-budget' && plannedReport.admissionPolicy.plannedWriteFits === false && plannedReport.admissionPolicy.plannedBudgetedBytes === 1200 && plannedWriteAdmission.factoryRejection?.detail?.status === 'reject-planned-write-over-budget' && plannedWriteAdmission.tree.fileCount === 0,
      posturedGuardOverrideRejectedBeforeStoreCreation: posturedGuardOverrideRejection.attempts.every((attempt) => attempt.factoryRejection?.code === 'BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED' && attempt.factoryRejection?.detail?.preMutationRejected === true) && posturedGuardOverrideRejection.tree.fileCount === 0,
      posturedFactoryRejectsBeforeStoreCreation: guardedAdmission.factoryRejection?.code === 'BRT_BROWSER_STORAGE_ADMISSION_REJECTED' && guardedAdmission.tree.fileCount === 0,
      pressureAdmissionRejectsBeforeMutation: guardedAdmission.rejection?.code === 'BRT_OPFS_WRITE_BUDGET_EXCEEDED' && guardedAdmission.rejection?.detail?.recovery?.preMutationRejected === true && guardedAdmission.tree.fileCount === 0,
      posturedFactoryAdmitsAndAppliesGuard: posturedStoreAdmission.status === 'admitted' && posturedStoreAdmission.put?.budget?.checked === true && posturedStoreAdmission.verify?.ok === true,
      posturedStoreRejectsPerPutGuardOverrideBeforeMutation: posturedStoreAdmission.allowWriteBudgetGuardOverride === false && posturedStoreAdmission.putOverrideRejection?.code === 'BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED' && posturedStoreAdmission.overridePresent === false && posturedStoreAdmission.tree.fileCount === 0,
      posturedWebLockFactoryAdmitsAppliesGuardAndSettles: posturedWebLockStoreAdmission.status === 'admitted-and-guarded' && posturedWebLockStoreAdmission.put?.budget?.checked === true && posturedWebLockStoreAdmission.verify?.ok === true && posturedWebLockStoreAdmission.after?.ok === true,
      posturedWebLockFactoryRejectsPerPutGuardOverrideBeforeMutation: posturedWebLockStoreAdmission.putOverrideRejection?.code === 'BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED' && posturedWebLockStoreAdmission.guardedOverridePresent === false && posturedWebLockStoreAdmission.tree.fileCount === 0,
      posturedWebLockFactoryDefaultsBoundedLockWait: posturedWebLockStoreAdmission.lockContentionPolicy?.defaulted === true && posturedWebLockStoreAdmission.snapshot?.lockTimeoutMs > 0 && posturedWebLockStoreAdmission.snapshot?.allowUnboundedLockTimeoutOverride === false,
      posturedWebLockFactoryRejectsUnboundedFactoryTimeoutBeforeStoreCreation: posturedWebLockUnboundedFactoryRejection.factoryRejection?.code === 'BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED' && posturedWebLockUnboundedFactoryRejection.tree.fileCount === 0,
      posturedWebLockFactoryRequiresExplicitUnsafeSingleOwnerFallbackOptIn: posturedWebLockSingleOwnerFallbackRejection.fallbackRejection?.code === 'BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED' && posturedWebLockSingleOwnerFallbackRejection.tree.fileCount === 0,
      posturedWebLockFactoryLabelsExplicitUnsafeSingleOwnerFallback: posturedWebLockSingleOwnerFallbackAdmission.status === 'admitted-single-owner-fallback' && posturedWebLockSingleOwnerFallbackAdmission.lockFallbackPolicy?.allowUnsafeSingleOwnerFallback === true && posturedWebLockSingleOwnerFallbackAdmission.put?.budget?.checked === true,
      posturedWebLockFactoryRejectsUnboundedPerOperationTimeoutBeforeMutation: posturedWebLockStoreAdmission.timeoutOverrideRejection?.code === 'BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED' && posturedWebLockStoreAdmission.timeoutOverridePresent === false && posturedWebLockStoreAdmission.tree.fileCount === 0,
      posturedGuardedStorageLaneAdapterFactoryAdmitsAppliesGuardAndSettles: posturedLaneAdapterAdmission.status === 'admitted-guarded-lane-adapter' && posturedLaneAdapterAdmission.adapterFactorySource === 'postured-web-lock-guarded-storage-lane-adapter-factory' && posturedLaneAdapterAdmission.put?.budget?.checked === true && posturedLaneAdapterAdmission.put?.budget?.guard?.policySource === 'browser-storage-posture-admission-policy' && posturedLaneAdapterAdmission.verify?.ok === true && posturedLaneAdapterAdmission.settled?.ok === true,
      posturedWebLockContentionRejectsBeforeMutationAndRecovers: posturedWebLockContention.timeoutRejection?.code === 'BRT_WEB_LOCK_TIMEOUT' && posturedWebLockContention.timeoutRejection?.detail?.recovery?.shouldQueryLocks === true && posturedWebLockContention.timedOutPresent === false && posturedWebLockContention.recoveryVerify?.ok === true && posturedWebLockContention.settled?.ok === true,
      bestEffortWarningVisible: report.warnings.some((row) => row.id === 'best-effort-storage'),
      persistNotCalledByDefault: bestEffort.calls.persist === 0,
      explicitPersistRequestOnly: request.calls.persist === 1 && requested.persistRequest.requested === true,
      runtimeNamespaceExposesDiagnostic: runtimeReport.format === BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT,
      kernelKitPostureRefactoredThroughDiagnostic: kernelReport.proof.browserStoragePostureDiagnostic === true
    },
    direct: report,
    directRecoveryGuidance,
    ledgerReport,
    plannedReport,
    requested,
    guardedAdmission,
    plannedWriteAdmission,
    posturedGuardOverrideRejection,
    posturedStoreAdmission,
    posturedWebLockStoreAdmission,
    posturedWebLockUnboundedFactoryRejection,
    posturedWebLockSingleOwnerFallbackRejection,
    posturedWebLockSingleOwnerFallbackAdmission,
    posturedLaneAdapterAdmission,
    posturedWebLockContention,
    runtime: { status: runtimeReport.status, riskLevel: runtimeReport.riskLevel, warnings: runtimeReport.warnings },
    kernelKit: { status: kernelReport.status, schema: kernelReport.schema, warnings: kernelReport.warnings, proof: kernelReport.proof, admissionPolicy: kernelReport.admissionPolicy },
    nonClaims: report.nonClaims
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runProbe();
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
}
