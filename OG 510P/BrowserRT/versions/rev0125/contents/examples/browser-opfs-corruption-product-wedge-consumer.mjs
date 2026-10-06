import * as defaultApi from '../src/public-api.mjs';

export const BROWSERRT_BROWSER_OPFS_CORRUPTION_PRODUCT_WEDGE_FORMAT = 'browserrt.browser-opfs-corruption-product-wedge-receipt.v1';

function proofFromObserved(observed = {}) {
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true,
    browserCapabilitiesVisible: observed.environment?.hasOpfs === true && observed.environment?.hasWebLocks === true && observed.environment?.isSecureContext === true,
    runtimeBooted: observed.runtime?.revisionMatches === true && observed.runtime?.versionMatches === true,
    guardedStoreAvailable: observed.storage?.guardedAvailable === true && /^web-lock-guarded:opfs-async-block-store/.test(String(observed.storage?.provider || '')),
    initialWriteVerified: observed.initial?.putAccepted === true && observed.initial?.verifyOk === true && observed.initial?.readDigestMatches === true,
    corruptionInjected: observed.corruption?.injected === true && observed.corruption?.corruptDigest !== observed.initial?.expectedDigest,
    corruptVerifyRejected: observed.corruption?.verifyAccepted === true && observed.corruption?.verifyOk === false && observed.corruption?.verifyReason === 'checksum-mismatch',
    corruptReadRejected: observed.corruption?.getAccepted === true && observed.corruption?.getDrainOk === false && observed.corruption?.getErrorCode === 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH',
    repairPutObserved: observed.repair?.putAccepted === true && observed.repair?.digestStable === true && observed.repair?.repairedCorrupt === true && observed.repair?.repairDeleted === true,
    repairedReadVerified: observed.repair?.verifyOk === true && observed.repair?.readDigestMatches === true && observed.repair?.readTextMatches === true,
    locksSettled: observed.locks?.beforeSettled === true && observed.locks?.afterSettled === true,
    cleanupAttempted: observed.cleanup?.accepted === true && observed.cleanup?.result === true,
    traceReceiptClosed: observed.trace?.closed === true && Array.isArray(observed.trace?.kinds) && observed.trace.kinds.includes('storage:opfs-block-corrupt') && observed.trace.kinds.includes('storage:opfs-block-repair') && observed.trace.kinds.includes('runtime:close')
  });
}

export function createBrowserOpfsCorruptionProductWedgeReceipt({ api = defaultApi, generatedAt = 'deterministic-browser-opfs-corruption-product-wedge', source = 'examples/browser-opfs-corruption-product-wedge-consumer.mjs', observed = {}, nonClaims = [] } = {}) {
  const proof = proofFromObserved(observed);
  const missing = Object.entries(proof).filter(([, value]) => value !== true).map(([key]) => key);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    format: BROWSERRT_BROWSER_OPFS_CORRUPTION_PRODUCT_WEDGE_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Installed-browser public API wedge proving content-addressed OPFS corruption is detected on verify/get, not served to callers, and repaired by a subsequent guarded storage-lane put of the original payload.',
    proof,
    missing,
    observed,
    nonClaims: Object.freeze(nonClaims.length ? nonClaims : [
      'Managed Chromium installed-package corruption proof only; it intentionally tampers with the OPFS block file and does not prove organic disk corruption rates, malicious same-origin isolation, cross-browser behavior, fsync durability, power-loss safety, quota/eviction survival, or production readiness.',
      'The repair step proves a re-put of the original payload replaces a corrupt content-addressed block after detection; it does not prove automatic background repair or recovery without caller intent.'
    ])
  });
}

export function validateBrowserOpfsCorruptionProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_BROWSER_OPFS_CORRUPTION_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_BROWSER_OPFS_CORRUPTION_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of [
    'publicApiImportOnly',
    'browserCapabilitiesVisible',
    'runtimeBooted',
    'guardedStoreAvailable',
    'initialWriteVerified',
    'corruptionInjected',
    'corruptVerifyRejected',
    'corruptReadRejected',
    'repairPutObserved',
    'repairedReadVerified',
    'locksSettled',
    'cleanupAttempted',
    'traceReceiptClosed'
  ]) {
    if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /corruption|cross-browser|fsync|production/i.test(String(claim)))) errors.push('corruption/durability/cross-browser/production non-claims must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, proof });
}

async function openOpfsFileAtPath(path) {
  const parts = String(path || '').split('/').filter(Boolean);
  if (parts.length < 2 || parts.some((part) => part === '..')) throw new Error(`unsafe OPFS block path: ${path}`);
  const fileName = parts.pop();
  let dir = await globalThis.navigator.storage.getDirectory();
  for (const part of parts) dir = await dir.getDirectoryHandle(part, { create: false });
  return await dir.getFileHandle(fileName, { create: false });
}

async function overwriteOpfsFile(path, bytes) {
  const handle = await openOpfsFileAtPath(path);
  const writer = await handle.createWritable();
  try {
    await writer.write(bytes);
    await writer.close();
  } catch (error) {
    try { await writer.abort(); } catch {}
    throw error;
  }
  return Object.freeze({ path, bytes: bytes.byteLength });
}

export async function runBrowserOpfsCorruptionProductWedgeWithApi(api = defaultApi, {
  generatedAt = 'deterministic-browser-opfs-corruption-product-wedge',
  source = 'examples/browser-opfs-corruption-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
} = {}) {
  const capabilities = api.detectCapabilities();
  const unavailable = [];
  if (capabilities.opfs !== true) unavailable.push('opfs');
  if (capabilities.webLocks !== true) unavailable.push('webLocks');
  if (globalThis.isSecureContext !== true) unavailable.push('secureContext');
  if (unavailable.length) throw new Error(`Browser OPFS corruption product wedge requires ${unavailable.join(', ')}`);

  const rt = await api.boot({ telemetry: 'browser-opfs-corruption-product-wedge', proof: api.REVISION, browserOpfsCorruptionProductWedge: true });
  const namespace = Object.freeze({
    storage: typeof rt.storage?.opfsWebLockGuardedBlockStore === 'function' && typeof rt.storage?.blockStoreLaneAdapter === 'function',
    coordination: typeof rt.coordination?.crossLaneScheduler === 'function'
  });
  const prefix = `browserrt/${api.REVISION}/browser-opfs-corruption-product-wedge/${prefixSuffix}`;
  const label = 'browser-opfs-corruption-product-wedge';
  const guardedStore = rt.storage.opfsWebLockGuardedBlockStore({
    label,
    prefix,
    lockPrefix: `browserrt:${api.REVISION}:browser-opfs-corruption-product-wedge`,
    lockTimeoutMs: 2000,
    storeConfig: {
      verifyExistingBlocksOnPut: true,
      verifyAfterWrite: true,
      verifyOnHas: true,
      repairCorruptOnPut: true,
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
  const decoder = new TextDecoder();
  const payloadText = JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, source, importSpecifier, prefix, scenario: 'opfs-corruption-detection-and-repair' }) + '\n';
  const payload = encoder.encode(payloadText);
  const expectedDigest = `sha256:${await api.digestBytesHex(payload)}`;
  const corruptBytes = encoder.encode(JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, scenario: 'intentional-corruption', prefix, nonce: prefixSuffix }) + '\n');
  const corruptDigest = `sha256:${await api.digestBytesHex(corruptBytes)}`;

  let cleanupAccepted = null;
  let cleanupResult = null;
  try {
    const put = adapter.schedulePut(payload, {
      id: 'browser-opfs-corruption-wedge-initial-put',
      priority: 'user-visible',
      label: 'browser-opfs-corruption-wedge-payload',
      putOptions: { timeoutMs: 2000, writeBudgetGuard: { requireEstimate: true, minFreeBytes: 0, maxUsageRatio: 1 } }
    });
    await adapter.drain({ maxSteps: 1 });
    const putResult = adapter.result('browser-opfs-corruption-wedge-initial-put');
    const initialVerify = adapter.scheduleVerify(putResult.ref, { id: 'browser-opfs-corruption-wedge-initial-verify', verifyOptions: { timeoutMs: 2000 } });
    const initialGet = adapter.scheduleGet(putResult.ref, { id: 'browser-opfs-corruption-wedge-initial-get', getOptions: { timeoutMs: 2000 } });
    await adapter.drain({ maxSteps: 2 });
    const initialVerifyResult = adapter.result('browser-opfs-corruption-wedge-initial-verify');
    const initialReadBytes = adapter.result('browser-opfs-corruption-wedge-initial-get');
    const initialReadDigest = `sha256:${await api.digestBytesHex(initialReadBytes)}`;

    const tamper = await overwriteOpfsFile(putResult.path, corruptBytes);
    const corruptVerify = adapter.scheduleVerify(putResult.ref, { id: 'browser-opfs-corruption-wedge-corrupt-verify', verifyOptions: { timeoutMs: 2000 } });
    await adapter.drain({ maxSteps: 1 });
    const corruptVerifyResult = adapter.result('browser-opfs-corruption-wedge-corrupt-verify');
    const corruptGet = adapter.scheduleGet(putResult.ref, { id: 'browser-opfs-corruption-wedge-corrupt-get', getOptions: { timeoutMs: 2000 } });
    const corruptGetDrain = await adapter.drain({ maxSteps: 1 });
    const corruptGetRow = corruptGetDrain.results[0] || {};

    const repairPut = adapter.schedulePut(payload, {
      id: 'browser-opfs-corruption-wedge-repair-put',
      priority: 'user-visible',
      label: 'browser-opfs-corruption-wedge-repair-payload',
      putOptions: { timeoutMs: 2000, writeBudgetGuard: { requireEstimate: true, minFreeBytes: 0, maxUsageRatio: 1 } }
    });
    await adapter.drain({ maxSteps: 1 });
    const repairPutResult = adapter.result('browser-opfs-corruption-wedge-repair-put');
    const repairVerify = adapter.scheduleVerify(repairPutResult.ref, { id: 'browser-opfs-corruption-wedge-repair-verify', verifyOptions: { timeoutMs: 2000 } });
    const repairGet = adapter.scheduleGet(repairPutResult.ref, { id: 'browser-opfs-corruption-wedge-repair-get', getOptions: { timeoutMs: 2000 } });
    await adapter.drain({ maxSteps: 2 });
    const repairVerifyResult = adapter.result('browser-opfs-corruption-wedge-repair-verify');
    const repairReadBytes = adapter.result('browser-opfs-corruption-wedge-repair-get');
    const repairReadDigest = `sha256:${await api.digestBytesHex(repairReadBytes)}`;
    const repairReadText = decoder.decode(repairReadBytes);

    const cleanup = adapter.scheduleCleanupForTest({ id: 'browser-opfs-corruption-wedge-cleanup', cleanupOptions: { timeoutMs: 2000 } });
    cleanupAccepted = cleanup.accepted === true;
    await adapter.drain({ maxSteps: 1 });
    cleanupResult = adapter.result('browser-opfs-corruption-wedge-cleanup');
    const afterSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
    const adapterSnapshot = adapter.snapshot();
    const guardSnapshot = guardedStore.snapshot();
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
      storage: { prefix, provider: guardSnapshot.provider, guardedAvailable: guardedStore.available === true, adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(adapterSnapshot).ok === true },
      initial: {
        putAccepted: put.accepted === true,
        verifyAccepted: initialVerify.accepted === true,
        getAccepted: initialGet.accepted === true,
        digest: putResult?.digest || null,
        path: putResult?.path || null,
        expectedDigest,
        verifyDigest: initialVerifyResult?.digest || null,
        verifyOk: initialVerifyResult?.ok === true,
        readDigest: initialReadDigest,
        readDigestMatches: initialReadDigest === expectedDigest,
        budgetChecked: putResult?.budget?.checked === true
      },
      corruption: {
        injected: tamper.bytes === corruptBytes.byteLength,
        corruptDigest,
        tamperPath: tamper.path,
        verifyAccepted: corruptVerify.accepted === true,
        verifyOk: corruptVerifyResult?.ok === true,
        verifyReason: corruptVerifyResult?.reason || null,
        verifyActualDigest: corruptVerifyResult?.actualDigest || null,
        getAccepted: corruptGet.accepted === true,
        getDrainOk: corruptGetRow.ok === true,
        getErrorCode: corruptGetRow.error?.code || null,
        getErrorName: corruptGetRow.error?.name || null
      },
      repair: {
        putAccepted: repairPut.accepted === true,
        digest: repairPutResult?.digest || null,
        digestStable: repairPutResult?.digest === expectedDigest && putResult?.digest === expectedDigest,
        path: repairPutResult?.path || null,
        repairedCorrupt: repairPutResult?.repairedCorrupt === true,
        repairDeleted: repairPutResult?.repair?.deleted === true,
        repairExistingOk: repairPutResult?.repair?.existing?.ok === true,
        repairActualDigest: repairPutResult?.repair?.existing?.actualDigest || null,
        verifyDigest: repairVerifyResult?.digest || null,
        verifyOk: repairVerifyResult?.ok === true,
        readDigest: repairReadDigest,
        readDigestMatches: repairReadDigest === expectedDigest,
        readTextMatches: repairReadText === payloadText
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
    const receipt = createBrowserOpfsCorruptionProductWedgeReceipt({ api, observed, generatedAt, source });
    return Object.freeze({ project: 'BrowserRT', revision: api.REVISION, version: api.VERSION, schema: 1, status: receipt.status, receipt, validation: validateBrowserOpfsCorruptionProductWedgeReceipt(receipt) });
  } catch (error) {
    if (cleanupAccepted !== true) {
      try {
        const cleanup = adapter.scheduleCleanupForTest({ id: 'browser-opfs-corruption-wedge-cleanup-after-error', cleanupOptions: { timeoutMs: 2000 } });
        cleanupAccepted = cleanup.accepted === true;
        await adapter.drain({ maxSteps: 1 });
        cleanupResult = adapter.result('browser-opfs-corruption-wedge-cleanup-after-error');
      } catch {}
    }
    try { rt.close(); } catch {}
    throw error;
  }
}
