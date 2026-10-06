import * as defaultApi from '../src/public-api.mjs';

export const BROWSERRT_BROWSER_OPFS_BUDGET_PRODUCT_WEDGE_FORMAT = 'browserrt.browser-opfs-budget-product-wedge-receipt.v1';

function proofFromObserved(observed = {}) {
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true,
    browserCapabilitiesVisible: observed.environment?.hasOpfs === true && observed.environment?.hasWebLocks === true && observed.environment?.isSecureContext === true,
    runtimeBooted: observed.runtime?.revisionMatches === true && observed.runtime?.versionMatches === true,
    guardedStoreAvailable: observed.storage?.guardedAvailable === true && /^web-lock-guarded:opfs-async-block-store/.test(String(observed.storage?.provider || '')),
    writeBudgetRejectObserved: observed.rejection?.putAccepted === true && observed.rejection?.drainOk === false && observed.rejection?.errorCode === 'BRT_OPFS_WRITE_BUDGET_EXCEEDED',
    rejectionExplainedByEstimate: observed.rejection?.traceRejectObserved === true && observed.rejection?.traceRejectReasonMinFreeBytes === true && Number.isFinite(Number(observed.rejection?.traceQuota)) && Number.isFinite(Number(observed.rejection?.traceUsage)),
    rejectedWriteDidNotCommit: observed.rejection?.hasAccepted === true && observed.rejection?.hasResult === false,
    storageLaneRecoveredAfterRejection: observed.recovery?.putAccepted === true && observed.recovery?.verifyAccepted === true && observed.recovery?.getAccepted === true && observed.recovery?.readDigestMatches === true && observed.recovery?.verifyDigestMatches === true,
    writeBudgetPassObserved: observed.recovery?.budgetChecked === true && Number.isFinite(Number(observed.recovery?.estimateQuota)),
    locksSettled: observed.locks?.beforeSettled === true && observed.locks?.afterSettled === true,
    cleanupAttempted: observed.cleanup?.accepted === true && observed.cleanup?.result === true,
    traceReceiptClosed: observed.trace?.closed === true && Array.isArray(observed.trace?.kinds) && observed.trace.kinds.includes('storage:opfs-block-write-budget-reject') && observed.trace.kinds.includes('runtime:close')
  });
}

export function createBrowserOpfsBudgetProductWedgeReceipt({ api = defaultApi, generatedAt = 'deterministic-browser-opfs-budget-product-wedge', source = 'examples/browser-opfs-budget-product-wedge-consumer.mjs', observed = {}, nonClaims = [] } = {}) {
  const proof = proofFromObserved(observed);
  const missing = Object.entries(proof).filter(([, value]) => value !== true).map(([key]) => key);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    format: BROWSERRT_BROWSER_OPFS_BUDGET_PRODUCT_WEDGE_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Installed-browser public API wedge proving OPFS write-budget rejection is explicit, pre-mutation, non-poisoning, and followed by a successful storage-lane write/read recovery.',
    proof,
    missing,
    observed,
    nonClaims: Object.freeze(nonClaims.length ? nonClaims : [
      'Managed Chromium installed-package write-budget proof only; it does not prove organic quota pressure, browser eviction policy, persistent-storage grants, cross-browser behavior, fsync durability, power-loss safety, arbitrary in-flight write survival, or production readiness.',
      'The rejected write is forced by an intentionally impossible minFreeBytes guard and proves explicit no-commit/recovery behavior, not real disk-full behavior.'
    ])
  });
}

export function validateBrowserOpfsBudgetProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_BROWSER_OPFS_BUDGET_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_BROWSER_OPFS_BUDGET_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of [
    'publicApiImportOnly',
    'browserCapabilitiesVisible',
    'runtimeBooted',
    'guardedStoreAvailable',
    'writeBudgetRejectObserved',
    'rejectionExplainedByEstimate',
    'rejectedWriteDidNotCommit',
    'storageLaneRecoveredAfterRejection',
    'writeBudgetPassObserved',
    'locksSettled',
    'cleanupAttempted',
    'traceReceiptClosed'
  ]) {
    if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /quota|eviction|cross-browser|fsync/i.test(String(claim)))) errors.push('quota/eviction/durability/cross-browser non-claims must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, proof });
}

export async function runBrowserOpfsBudgetProductWedgeWithApi(api = defaultApi, {
  generatedAt = 'deterministic-browser-opfs-budget-product-wedge',
  source = 'examples/browser-opfs-budget-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
} = {}) {
  const capabilities = api.detectCapabilities();
  const unavailable = [];
  if (capabilities.opfs !== true) unavailable.push('opfs');
  if (capabilities.webLocks !== true) unavailable.push('webLocks');
  if (globalThis.isSecureContext !== true) unavailable.push('secureContext');
  if (unavailable.length) throw new Error(`Browser OPFS budget product wedge requires ${unavailable.join(', ')}`);

  const rt = await api.boot({ telemetry: 'browser-opfs-budget-product-wedge', proof: api.REVISION, browserOpfsBudgetProductWedge: true });
  const namespace = Object.freeze({
    storage: typeof rt.storage?.opfsWebLockGuardedBlockStore === 'function' && typeof rt.storage?.blockStoreLaneAdapter === 'function',
    coordination: typeof rt.coordination?.crossLaneScheduler === 'function'
  });
  const prefix = `browserrt/${api.REVISION}/browser-opfs-budget-product-wedge/${prefixSuffix}`;
  const label = 'browser-opfs-budget-product-wedge';
  const guardedStore = rt.storage.opfsWebLockGuardedBlockStore({
    label,
    prefix,
    lockPrefix: `browserrt:${api.REVISION}:browser-opfs-budget-product-wedge`,
    lockTimeoutMs: 2000,
    storeConfig: {
      verifyExistingBlocksOnPut: true,
      verifyAfterWrite: true,
      verifyOnHas: true,
      writeBudgetGuard: { requireEstimate: true, minFreeBytes: 0, maxUsageRatio: 1 }
    }
  });
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
  const rejectPayload = encoder.encode(JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, source, importSpecifier, prefix, scenario: 'forced-write-budget-reject' }) + '\n');
  const rejectDigest = `sha256:${await api.digestBytesHex(rejectPayload)}`;
  const recoveryPayload = encoder.encode(JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, source, importSpecifier, prefix, scenario: 'post-budget-reject-recovery' }) + '\n');
  const recoveryExpectedDigest = `sha256:${await api.digestBytesHex(recoveryPayload)}`;

  let cleanupAccepted = null;
  let cleanupResult = null;
  try {
    const rejectingPut = adapter.schedulePut(rejectPayload, {
      id: 'browser-opfs-budget-wedge-rejected-put',
      priority: 'user-visible',
      label: 'browser-opfs-budget-wedge-rejected-payload',
      putOptions: { timeoutMs: 2000, writeBudgetGuard: { requireEstimate: true, minFreeBytes: 1e20, maxUsageRatio: 1 } }
    });
    const rejectDrain = await adapter.drain({ maxSteps: 1 });
    const rejectRow = rejectDrain.results[0] || {};
    const rejectedHas = adapter.scheduleHas(rejectDigest, { id: 'browser-opfs-budget-wedge-rejected-has', hasOptions: { timeoutMs: 2000 } });
    await adapter.drain({ maxSteps: 1 });
    const rejectedHasResult = adapter.result('browser-opfs-budget-wedge-rejected-has');

    const recoveryPut = adapter.schedulePut(recoveryPayload, {
      id: 'browser-opfs-budget-wedge-recovery-put',
      priority: 'user-visible',
      label: 'browser-opfs-budget-wedge-recovery-payload',
      putOptions: { timeoutMs: 2000, writeBudgetGuard: { requireEstimate: true, minFreeBytes: 0, maxUsageRatio: 1 } }
    });
    await adapter.drain({ maxSteps: 1 });
    const putResult = adapter.result('browser-opfs-budget-wedge-recovery-put');
    const verify = adapter.scheduleVerify(putResult.ref, { id: 'browser-opfs-budget-wedge-recovery-verify', verifyOptions: { timeoutMs: 2000 } });
    const get = adapter.scheduleGet(putResult.ref, { id: 'browser-opfs-budget-wedge-recovery-get', getOptions: { timeoutMs: 2000 } });
    const estimate = adapter.scheduleEstimate({ id: 'browser-opfs-budget-wedge-estimate', estimateOptions: { timeoutMs: 2000 } });
    await adapter.drain({ maxSteps: 3 });
    const verifyResult = adapter.result('browser-opfs-budget-wedge-recovery-verify');
    const readBytes = adapter.result('browser-opfs-budget-wedge-recovery-get');
    const estimateResult = adapter.result('browser-opfs-budget-wedge-estimate') || {};
    const recoveryReadDigest = `sha256:${await api.digestBytesHex(readBytes)}`;
    const cleanup = adapter.scheduleCleanupForTest({ id: 'browser-opfs-budget-wedge-cleanup', cleanupOptions: { timeoutMs: 2000 } });
    cleanupAccepted = cleanup.accepted === true;
    await adapter.drain({ maxSteps: 1 });
    cleanupResult = adapter.result('browser-opfs-budget-wedge-cleanup');
    const afterSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
    const adapterSnapshot = adapter.snapshot();
    const guardSnapshot = guardedStore.snapshot();
    const trace = rt.close();
    const traceKinds = trace.map((event) => event.kind);
    const rejectTrace = trace.find((event) => event.kind === 'storage:opfs-block-write-budget-reject')?.detail || trace.find((event) => event.kind === 'storage:opfs-block-write-budget-reject') || {};
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
      storage: { prefix, provider: guardSnapshot.provider, guardedAvailable: guardedStore.available === true, adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(adapterSnapshot).ok === true },
      rejection: {
        putAccepted: rejectingPut.accepted === true,
        drainOk: rejectRow.ok === true,
        errorCode: rejectRow.error?.code || null,
        errorName: rejectRow.error?.name || null,
        rejectDigest,
        hasAccepted: rejectedHas.accepted === true,
        hasResult: rejectedHasResult === true,
        traceRejectObserved: traceKinds.includes('storage:opfs-block-write-budget-reject'),
        traceRejectReasonMinFreeBytes: Array.isArray(rejectTrace.reasons) && rejectTrace.reasons.includes('min-free-bytes'),
        traceQuota: rejectTrace.quota ?? null,
        traceUsage: rejectTrace.usage ?? null,
        traceRequestedBytes: rejectTrace.requestedBytes ?? null
      },
      recovery: {
        putAccepted: recoveryPut.accepted === true,
        verifyAccepted: verify.accepted === true,
        getAccepted: get.accepted === true,
        estimateAccepted: estimate.accepted === true,
        digest: putResult?.digest || null,
        path: putResult?.path || null,
        expectedDigest: recoveryExpectedDigest,
        verifyDigest: verifyResult?.digest || null,
        verifyOk: verifyResult?.ok === true,
        verifyDigestMatches: verifyResult?.digest === recoveryExpectedDigest,
        readDigest: recoveryReadDigest,
        readDigestMatches: recoveryReadDigest === recoveryExpectedDigest,
        budgetChecked: putResult?.budget?.checked === true,
        estimateQuota: estimateResult.quota ?? null,
        estimateUsage: estimateResult.usage ?? null
      },
      locks: {
        beforeSettled: beforeSettled.ok === true,
        afterSettled: afterSettled.ok === true,
        available: guardSnapshot.available === true,
        lockName: guardSnapshot.lockName,
        exclusiveOperations: guardSnapshot.stats?.exclusiveOperations || 0,
        sharedOperations: guardSnapshot.stats?.sharedOperations || 0,
        errors: guardSnapshot.stats?.errors || 0
      },
      cleanup: { accepted: cleanupAccepted, result: cleanupResult === true },
      trace: { closed: traceKinds.includes('runtime:close'), count: trace.length, kinds: traceKinds }
    });
    const receipt = createBrowserOpfsBudgetProductWedgeReceipt({ api, observed, generatedAt, source });
    return Object.freeze({ project: 'BrowserRT', revision: api.REVISION, version: api.VERSION, schema: 1, status: receipt.status, receipt, validation: validateBrowserOpfsBudgetProductWedgeReceipt(receipt) });
  } catch (error) {
    if (cleanupAccepted !== true) {
      try {
        const cleanup = adapter.scheduleCleanupForTest({ id: 'browser-opfs-budget-wedge-cleanup-after-error', cleanupOptions: { timeoutMs: 2000 } });
        cleanupAccepted = cleanup.accepted === true;
        await adapter.drain({ maxSteps: 1 });
        cleanupResult = adapter.result('browser-opfs-budget-wedge-cleanup-after-error');
      } catch {}
    }
    try { rt.close(); } catch {}
    throw error;
  }
}
