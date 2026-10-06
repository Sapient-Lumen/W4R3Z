import * as defaultApi from '../src/public-api.mjs';

export const BROWSERRT_BROWSER_OPFS_ABORT_PRODUCT_WEDGE_FORMAT = 'browserrt.browser-opfs-abort-product-wedge-receipt.v1';

function hasTraceKind(observed, ...kinds) {
  const seen = new Set(Array.isArray(observed.trace?.kinds) ? observed.trace.kinds : []);
  return kinds.some((kind) => seen.has(kind));
}

function proofFromObserved(observed = {}) {
  const finalRollbackVisible = observed.abort?.rollbackAttempts >= 1 && observed.abort?.rollbackDeletes >= 1;
  const stagedRollbackVisible = observed.abort?.stagedCleanupAttempts >= 1 && (observed.abort?.stagedCleanupDeletes >= 1 || observed.abort?.stagedCleanupMisses >= 1) && hasTraceKind(observed, 'storage:opfs-block-staged-cleanup');
  const rollbackTraceVisible = hasTraceKind(observed, 'storage:opfs-block-put-rollback', 'storage:opfs-block-put-rollback-skipped') || hasTraceKind(observed, 'storage:opfs-block-staged-cleanup');
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true,
    browserCapabilitiesVisible: observed.environment?.hasOpfs === true && observed.environment?.hasWebLocks === true && observed.environment?.isSecureContext === true,
    runtimeBooted: observed.runtime?.revisionMatches === true && observed.runtime?.versionMatches === true,
    namespacedFacadeUsed: observed.namespace?.storage === true && observed.namespace?.coordination === true,
    posturedGuardedFactoryUsed: observed.storage?.posturedGuardedFactoryUsed === true && observed.storage?.postureStatus === 'observed' && observed.storage?.admissionStatus === 'admit-with-guard' && observed.storage?.writeBudgetGuardSource === 'browser-storage-posture-admission-policy' && observed.storage?.lockContentionPolicy?.enabled === true,
    guardedStoreAvailable: observed.storage?.guardedAvailable === true && /^web-lock-guarded:opfs-async-block-store/.test(String(observed.storage?.provider || '')),
    timeoutAbortObserved: observed.abort?.putAccepted === true && observed.abort?.drainOk === false && observed.abort?.errorCode === 'BRT_STORAGE_OPERATION_TIMEOUT' && observed.abort?.providerAbortSignaled === true && observed.abort?.executorProviderTimeoutAborts >= 1,
    providerAbortSettled: observed.abort?.settled === true && observed.abort?.failedTimedOutOperationCount >= 1 && observed.abort?.lateFailureCode === 'BRT_OPFS_OPERATION_ABORTED',
    abortedWriteDidNotCommit: observed.abort?.expectedDigest && observed.abort?.hasAfterAbort === false && observed.abort?.verifyPresentAfterAbort === false,
    rollbackVisible: observed.abort?.writerAbortCalls >= 1 && (finalRollbackVisible || stagedRollbackVisible),
    quarantineVisibleBeforeOverride: observed.recovery?.quarantineBeforeOverrideCount >= 1 && observed.recovery?.laneHealthOverride === true,
    recoveryBlockedBeforeOverride: observed.recovery?.preOverrideRecoveryRejected === true && observed.recovery?.preOverrideNoMutation === true && observed.recovery?.preOverrideHasAfterReject === false && observed.recovery?.preOverrideVerifyPresentAfterReject === false,
    storageLaneRecoveredAfterAbort: observed.recovery?.putAccepted === true && observed.recovery?.verifyOk === true && observed.recovery?.readDigestMatches === true && observed.recovery?.readTextMatches === true,
    locksSettled: observed.locks?.beforeSettled === true && observed.locks?.afterSettled === true,
    cleanupAttempted: observed.cleanup?.accepted === true && observed.cleanup?.result === true,
    traceReceiptClosed: observed.trace?.closed === true && hasTraceKind(observed, 'storage-lane:operation-timeout') && rollbackTraceVisible && hasTraceKind(observed, 'runtime:close')
  });
}

export function createBrowserOpfsAbortProductWedgeReceipt({ api = defaultApi, generatedAt = 'deterministic-browser-opfs-abort-product-wedge', source = 'examples/browser-opfs-abort-product-wedge-consumer.mjs', observed = {}, nonClaims = [] } = {}) {
  const proof = proofFromObserved(observed);
  const missing = Object.entries(proof).filter(([, value]) => value !== true).map(([key]) => key);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    format: BROWSERRT_BROWSER_OPFS_ABORT_PRODUCT_WEDGE_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Installed-browser public API wedge proving a storage-lane operation timeout can abort an in-progress guarded OPFS put, leave no committed digest, surface staged rollback cleanup or final-block rollback evidence, keep timed-out-operation quarantine visible, and recover only after an explicit health override plus successful write/read.',
    proof,
    missing,
    observed,
    nonClaims: Object.freeze(nonClaims.length ? nonClaims : [
      'Managed Chromium installed-package abort proof only; it patches createWritable to force a deterministic storage-lane timeout and provider abort. It does not prove arbitrary renderer crashes, browser process death during an unacknowledged write, power-loss safety, fsync durability, cross-browser behavior, quota/eviction survival, or production readiness.',
      'The recovery step uses an explicit lane health override while timed-out-operation quarantine remains visible; it does not claim automatic safe recovery from every interrupted write.'
    ])
  });
}

export function validateBrowserOpfsAbortProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_BROWSER_OPFS_ABORT_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_BROWSER_OPFS_ABORT_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of [
    'publicApiImportOnly',
    'browserCapabilitiesVisible',
    'runtimeBooted',
    'namespacedFacadeUsed',
    'posturedGuardedFactoryUsed',
    'guardedStoreAvailable',
    'timeoutAbortObserved',
    'providerAbortSettled',
    'abortedWriteDidNotCommit',
    'rollbackVisible',
    'quarantineVisibleBeforeOverride',
    'recoveryBlockedBeforeOverride',
    'storageLaneRecoveredAfterAbort',
    'locksSettled',
    'cleanupAttempted',
    'traceReceiptClosed'
  ]) {
    if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /crash|fsync|cross-browser|production/i.test(String(claim)))) errors.push('crash/durability/cross-browser/production non-claims must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, proof });
}

function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }

async function waitForFailedTimeout(adapter, { timeoutMs = 2500, intervalMs = 25 } = {}) {
  const started = performance.now();
  let snapshot = adapter.snapshot();
  while (performance.now() - started < timeoutMs) {
    snapshot = adapter.snapshot();
    if ((snapshot.executor?.failedTimedOutOperationCount || 0) > 0) {
      return Object.freeze({ ok: true, elapsedMs: Math.round(performance.now() - started), snapshot });
    }
    await sleep(intervalMs);
  }
  return Object.freeze({ ok: false, elapsedMs: Math.round(performance.now() - started), snapshot });
}

function installCreateWritableDelayPatch({ delayMs = 180 } = {}) {
  if (typeof FileSystemFileHandle === 'undefined' || typeof FileSystemFileHandle.prototype?.createWritable !== 'function') {
    throw new Error('FileSystemFileHandle.createWritable is unavailable for OPFS abort wedge');
  }
  const originalCreateWritable = FileSystemFileHandle.prototype.createWritable;
  const stats = { createWritableCalls: 0, delayedCalls: 0, writeCalls: 0, closeCalls: 0, abortCalls: 0, delayMs };
  FileSystemFileHandle.prototype.createWritable = async function patchedCreateWritable(options = {}) {
    stats.createWritableCalls += 1;
    const writable = await originalCreateWritable.call(this, options);
    stats.delayedCalls += 1;
    await sleep(delayMs);
    return {
      async write(value) { stats.writeCalls += 1; return await writable.write(value); },
      async close() { stats.closeCalls += 1; return await writable.close(); },
      async abort(reason) { stats.abortCalls += 1; return typeof writable.abort === 'function' ? await writable.abort(reason) : undefined; },
      async seek(position) { return typeof writable.seek === 'function' ? await writable.seek(position) : undefined; },
      async truncate(size) { return typeof writable.truncate === 'function' ? await writable.truncate(size) : undefined; }
    };
  };
  return Object.freeze({ stats, restore() { FileSystemFileHandle.prototype.createWritable = originalCreateWritable; } });
}

export async function runBrowserOpfsAbortProductWedgeWithApi(api = defaultApi, {
  generatedAt = 'deterministic-browser-opfs-abort-product-wedge',
  source = 'examples/browser-opfs-abort-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
} = {}) {
  const capabilities = api.detectCapabilities();
  const unavailable = [];
  if (capabilities.opfs !== true) unavailable.push('opfs');
  if (capabilities.webLocks !== true) unavailable.push('webLocks');
  if (globalThis.isSecureContext !== true) unavailable.push('secureContext');
  if (unavailable.length) throw new Error(`Browser OPFS abort product wedge requires ${unavailable.join(', ')}`);

  const rt = await api.boot({ telemetry: 'browser-opfs-abort-product-wedge', proof: api.REVISION, browserOpfsAbortProductWedge: true });
  const namespace = Object.freeze({
    storage: typeof rt.storage?.opfsWebLockGuardedBlockStoreWithPosture === 'function' && typeof rt.storage?.blockStoreLaneAdapter === 'function',
    coordination: typeof rt.coordination?.crossLaneScheduler === 'function'
  });
  const prefix = `browserrt/${api.REVISION}/browser-opfs-abort-product-wedge/${prefixSuffix}`;
  const label = 'browser-opfs-abort-product-wedge';
  const posturedGuarded = await rt.storage.opfsWebLockGuardedBlockStoreWithPosture({
    label,
    prefix,
    lockPrefix: `browserrt:${api.REVISION}:browser-opfs-abort-product-wedge`,
    lockContentionTimeoutMs: 2000,
    budgetPolicy: { requireEstimate: true, minFreeBytes: 0, maxUsageRatio: 1 },
    storeConfig: {
      verifyExistingBlocksOnPut: true,
      verifyAfterWrite: true,
      verifyOnHas: true,
      repairCorruptOnPut: true
    }
  });
  const guardedStore = posturedGuarded.store;
  const writeBudgetGuard = posturedGuarded.writeBudgetGuard;
  const scheduler = rt.coordination.crossLaneScheduler({
    label: `${label}:scheduler`,
    lanes: [
      { id: 'storage', rank: 80, capacity: 1, quantum: 64, maxQueuedCost: 2048 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 256 }
    ]
  });
  const adapter = rt.storage.blockStoreLaneAdapter({ label: `${label}:adapter`, store: guardedStore, scheduler, lane: 'storage' });
  const beforeSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
  const encoder = new TextEncoder();
  const decoder = new TextDecoder();
  const abortedPayloadText = JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, source, importSpecifier, prefix, scenario: 'storage-lane-timeout-aborts-guarded-opfs-put' }) + '\n';
  const abortedPayload = encoder.encode(abortedPayloadText);
  const abortedDigest = `sha256:${await api.digestBytesHex(abortedPayload)}`;
  const preOverridePayloadText = JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, source, importSpecifier, prefix, scenario: 'pre-override-recovery-must-be-blocked-by-quarantine' }) + '\n';
  const preOverridePayload = encoder.encode(preOverridePayloadText);
  const preOverrideDigest = `sha256:${await api.digestBytesHex(preOverridePayload)}`;
  const recoveryPayloadText = JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, source, importSpecifier, prefix, scenario: 'post-timeout-abort-recovery-write' }) + '\n';
  const recoveryPayload = encoder.encode(recoveryPayloadText);
  const recoveryDigest = `sha256:${await api.digestBytesHex(recoveryPayload)}`;

  let cleanupAccepted = null;
  let cleanupResult = null;
  let patch = null;
  try {
    patch = installCreateWritableDelayPatch({ delayMs: 180 });
    const timeoutPut = adapter.schedulePut(abortedPayload, {
      id: 'browser-opfs-abort-wedge-timeout-put',
      priority: 'user-visible',
      label: 'browser-opfs-abort-wedge-timeout-payload',
      operationTimeoutMs: 45,
      abortProviderOnOperationTimeout: true,
      putOptions: { timeoutMs: 2000, writeBudgetGuard }
    });
    const timeoutDrain = await adapter.drain({ maxSteps: 1 });
    patch.restore();
    const timeoutRow = timeoutDrain.results[0] || {};
    const settlement = await waitForFailedTimeout(adapter, { timeoutMs: 2500, intervalMs: 25 });
    const settledSnapshot = settlement.snapshot;
    const failedRows = settledSnapshot.executor?.failedTimedOutOperations || [];
    const failedRow = failedRows[0] || null;
    const guardAfterAbort = guardedStore.snapshot();
    const hasAfterAbort = await guardedStore.has(abortedDigest, { timeoutMs: 2000 });
    const verifyAfterAbort = await guardedStore.verify(abortedDigest, { timeoutMs: 2000 });
    const quarantineBeforeOverride = adapter.timedOutOperationQuarantine?.('storage') || settledSnapshot.executor?.timedOutOperationQuarantine || null;
    const preOverridePut = adapter.schedulePut(preOverridePayload, {
      id: 'browser-opfs-abort-wedge-pre-override-put',
      priority: 'user-visible',
      label: 'browser-opfs-abort-wedge-pre-override-payload',
      putOptions: { timeoutMs: 2000, writeBudgetGuard }
    });
    const preOverrideHasAfterReject = await guardedStore.has(preOverrideDigest, { timeoutMs: 2000 });
    const preOverrideVerifyAfterReject = await guardedStore.verify(preOverrideDigest, { timeoutMs: 2000 });
    const markHealthy = adapter.markHealthy('storage', 'reviewed-provider-abort-after-storage-lane-timeout', { allowWithTimedOutQuarantine: true, reviewToken: 'browser-opfs-abort-product-wedge-reviewed-timeout' });

    const recoveryPut = adapter.schedulePut(recoveryPayload, {
      id: 'browser-opfs-abort-wedge-recovery-put',
      priority: 'user-visible',
      label: 'browser-opfs-abort-wedge-recovery-payload',
      putOptions: { timeoutMs: 2000, writeBudgetGuard }
    });
    await adapter.drain({ maxSteps: 1 });
    const recoveryPutResult = adapter.result('browser-opfs-abort-wedge-recovery-put');
    const recoveryVerify = adapter.scheduleVerify(recoveryPutResult.ref, { id: 'browser-opfs-abort-wedge-recovery-verify', verifyOptions: { timeoutMs: 2000 } });
    const recoveryGet = adapter.scheduleGet(recoveryPutResult.ref, { id: 'browser-opfs-abort-wedge-recovery-get', getOptions: { timeoutMs: 2000 } });
    await adapter.drain({ maxSteps: 2 });
    const recoveryVerifyResult = adapter.result('browser-opfs-abort-wedge-recovery-verify');
    const recoveryReadBytes = adapter.result('browser-opfs-abort-wedge-recovery-get');
    const recoveryReadDigest = `sha256:${await api.digestBytesHex(recoveryReadBytes)}`;
    const recoveryReadText = decoder.decode(recoveryReadBytes);

    const cleanup = adapter.scheduleCleanupForTest({ id: 'browser-opfs-abort-wedge-cleanup', cleanupOptions: { timeoutMs: 2000 } });
    cleanupAccepted = cleanup.accepted === true;
    await adapter.drain({ maxSteps: 1 });
    cleanupResult = adapter.result('browser-opfs-abort-wedge-cleanup');
    const afterSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
    const finalAdapterSnapshot = adapter.snapshot();
    const finalGuardSnapshot = guardedStore.snapshot();
    const trace = rt.close();
    const traceKinds = trace.map((event) => event.kind);
    const observed = Object.freeze({
      imports: { publicApiOnly: true, importSpecifier },
      environment: {
        crossOriginIsolated: globalThis.crossOriginIsolated === true,
        isSecureContext: globalThis.isSecureContext === true,
        hasOpfs: capabilities.opfs === true,
        hasWebLocks: capabilities.webLocks === true,
        hasWorker: typeof Worker === 'function',
        href: globalThis.location?.href || null,
        origin: globalThis.location?.origin || null
      },
      runtime: { revision: api.REVISION, version: api.VERSION, revisionMatches: rt.revision === api.REVISION, versionMatches: rt.version === api.VERSION },
      namespace,
      storage: {
        prefix,
        provider: finalGuardSnapshot.provider,
        guardedAvailable: guardedStore.available === true,
        posturedGuardedFactoryUsed: true,
        postureStatus: posturedGuarded.posture?.status || null,
        admissionStatus: posturedGuarded.admissionPolicy?.status || null,
        writeBudgetGuardSource: posturedGuarded.writeBudgetGuard?.source || null,
        lockContentionPolicy: posturedGuarded.lockContentionPolicy || null,
        adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(finalAdapterSnapshot).ok === true
      },
      abort: {
        putAccepted: timeoutPut.accepted === true,
        expectedDigest: abortedDigest,
        drainOk: timeoutRow.ok === true,
        errorCode: timeoutRow.error?.code || null,
        providerAbortSignaled: timeoutRow.error?.detail?.providerAbortSignaled === true || (settledSnapshot.executor?.stats?.providerTimeoutAborts || 0) >= 1,
        operationTimeoutMs: timeoutRow.error?.detail?.timeoutMs ?? null,
        settled: settlement.ok === true,
        failedTimedOutOperationCount: settledSnapshot.executor?.failedTimedOutOperationCount || 0,
        lateFailureCode: failedRow?.error?.code || null,
        lateFailureName: failedRow?.error?.name || null,
        hasAfterAbort,
        verifyPresentAfterAbort: verifyAfterAbort?.present === true,
        verifyOkAfterAbort: verifyAfterAbort?.ok === true,
        rollbackAttempts: guardAfterAbort.store?.stats?.rollbackAttempts || 0,
        rollbackDeletes: guardAfterAbort.store?.stats?.rollbackDeletes || 0,
        rollbackOwnershipSkips: guardAfterAbort.store?.stats?.rollbackOwnershipSkips || 0,
        stagedCleanupAttempts: (guardAfterAbort.store?.stats?.stagedTempDeletes || 0) + (guardAfterAbort.store?.stats?.stagedTempDeleteMisses || 0) + (guardAfterAbort.store?.stats?.stagedTempDeleteFailures || 0),
        stagedCleanupDeletes: guardAfterAbort.store?.stats?.stagedTempDeletes || 0,
        stagedCleanupMisses: guardAfterAbort.store?.stats?.stagedTempDeleteMisses || 0,
        stagedCleanupFailures: guardAfterAbort.store?.stats?.stagedTempDeleteFailures || 0,
        putFailures: guardAfterAbort.store?.stats?.putFailures || 0,
        abortRejects: guardAfterAbort.store?.stats?.abortRejects || 0,
        writerCreateWritableCalls: patch.stats.createWritableCalls,
        writerDelayedCalls: patch.stats.delayedCalls,
        writerWriteCalls: patch.stats.writeCalls,
        writerCloseCalls: patch.stats.closeCalls,
        writerAbortCalls: patch.stats.abortCalls,
        executorOperationTimeouts: settledSnapshot.executor?.stats?.operationTimeouts || 0,
        executorProviderTimeoutAborts: settledSnapshot.executor?.stats?.providerTimeoutAborts || 0
      },
      recovery: {
        quarantineBeforeOverrideCount: quarantineBeforeOverride?.totalCount ?? finalAdapterSnapshot.timedOutOperationQuarantineCount ?? null,
        preOverrideRecoveryRejected: preOverridePut.accepted === false && preOverridePut.scheduler?.disposition === 'rejected-lane-unhealthy',
        preOverrideDisposition: preOverridePut.scheduler?.disposition || preOverridePut.disposition || null,
        preOverrideReason: preOverridePut.scheduler?.reason || preOverridePut.reason || null,
        preOverrideNoMutation: preOverridePut.scheduler?.noMutation === true || preOverridePut.noMutation === true,
        preOverrideExpectedDigest: preOverrideDigest,
        preOverrideHasAfterReject,
        preOverrideVerifyPresentAfterReject: preOverrideVerifyAfterReject?.present === true,
        laneHealthOverride: markHealthy?.healthy === true,
        laneHealthOverrideReason: markHealthy?.reason || null,
        putAccepted: recoveryPut.accepted === true,
        digest: recoveryPutResult?.digest || null,
        expectedDigest: recoveryDigest,
        verifyAccepted: recoveryVerify.accepted === true,
        getAccepted: recoveryGet.accepted === true,
        verifyDigest: recoveryVerifyResult?.digest || null,
        verifyOk: recoveryVerifyResult?.ok === true,
        readDigest: recoveryReadDigest,
        readDigestMatches: recoveryReadDigest === recoveryDigest,
        readTextMatches: recoveryReadText === recoveryPayloadText,
        budgetChecked: recoveryPutResult?.budget?.checked === true
      },
      locks: {
        beforeSettled: beforeSettled.ok === true,
        afterSettled: afterSettled.ok === true,
        lockName: finalGuardSnapshot.lockName,
        exclusiveOperations: finalGuardSnapshot.stats?.exclusiveOperations || 0,
        sharedOperations: finalGuardSnapshot.stats?.sharedOperations || 0,
        errors: finalGuardSnapshot.stats?.errors || 0
      },
      cleanup: { accepted: cleanupAccepted, result: cleanupResult === true },
      trace: { closed: traceKinds.includes('runtime:close'), count: trace.length, kinds: traceKinds }
    });
    const receipt = createBrowserOpfsAbortProductWedgeReceipt({ api, observed, generatedAt, source });
    return Object.freeze({ project: 'BrowserRT', revision: api.REVISION, version: api.VERSION, schema: 1, status: receipt.status, receipt, validation: validateBrowserOpfsAbortProductWedgeReceipt(receipt) });
  } catch (error) {
    try { patch?.restore?.(); } catch {}
    if (cleanupAccepted !== true) {
      try {
        adapter.markHealthy('storage', 'cleanup-after-abort-product-wedge-error', { allowWithTimedOutQuarantine: true, reviewToken: 'cleanup-after-abort-error' });
        const cleanup = adapter.scheduleCleanupForTest({ id: 'browser-opfs-abort-wedge-cleanup-after-error', cleanupOptions: { timeoutMs: 2000 } });
        cleanupAccepted = cleanup.accepted === true;
        await adapter.drain({ maxSteps: 1 });
        cleanupResult = adapter.result('browser-opfs-abort-wedge-cleanup-after-error');
      } catch {}
    }
    try { rt.close(); } catch {}
    throw error;
  }
}
