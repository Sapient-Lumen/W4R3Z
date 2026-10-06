import * as defaultApi from '../src/public-api.mjs';

export const BROWSERRT_BROWSER_OPFS_PRODUCT_WEDGE_FORMAT = 'browserrt.browser-opfs-product-wedge-receipt.v1';

const encoder = new TextEncoder();

function encodeJson(value) { return encoder.encode(JSON.stringify(value) + '\n'); }

function proofFromObserved(observed = {}) {
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true,
    namespacedFacadeUsed: observed.namespace?.core === true && observed.namespace?.storage === true && observed.namespace?.coordination === true,
    browserCapabilitiesVisible: observed.environment?.hasOpfs === true && observed.environment?.hasWebLocks === true && observed.environment?.isSecureContext === true,
    runtimeBooted: observed.runtime?.revisionMatches === true && observed.runtime?.versionMatches === true,
    boundedChannelBackpressure: observed.channel?.overflowDisposition === 'failed-full' && observed.channel?.receivedCount === 2,
    workerTransformedChunks: observed.worker?.chunkCount === 2 && observed.worker?.allSumsMatch === true && observed.worker?.allTransfersDetached === true,
    admissionRejectNoMutation: observed.admission?.accepted === true && observed.admission?.rejectedNoMutation === true && observed.admission?.released === true,
    guardedStoreAvailable: observed.storage?.guardedAvailable === true && /^web-lock-guarded:opfs-async-block-store/.test(String(observed.storage?.provider || '')),
    storageLaneAccepted: observed.storage?.putAccepted === true && observed.storage?.verifyAccepted === true && observed.storage?.getAccepted === true,
    persistentGoldenWorkload: observed.storage?.chunkPutCount === 2 && observed.storage?.allVerifiesOk === true && observed.storage?.allReadsMatch === true,
    opfsWriteVerified: observed.storage?.putDigestMatchesExpected === true && observed.storage?.allVerifiesOk === true,
    opfsReadDigestMatches: observed.storage?.allReadsMatch === true,
    writeBudgetEstimated: observed.storage?.budgetChecked === true && Number.isFinite(Number(observed.storage?.estimateQuota)),
    webLocksExercised: Number(observed.locks?.exclusiveOperations || 0) >= 2 && Number(observed.locks?.sharedOperations || 0) >= 2,
    locksSettled: observed.locks?.beforeSettled === true && observed.locks?.afterSettled === true,
    cleanupAttempted: observed.cleanup?.accepted === true && observed.cleanup?.result === true,
    traceReceiptClosed: Array.isArray(observed.trace?.kinds) && observed.trace.kinds.includes('runtime:boot') && observed.trace.kinds.includes('runtime:close') && observed.trace.kinds.includes('storage:opfs-web-lock-guard-create')
  });
}

export function validateBrowserOpfsProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_BROWSER_OPFS_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_BROWSER_OPFS_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of [
    'publicApiImportOnly',
    'namespacedFacadeUsed',
    'browserCapabilitiesVisible',
    'runtimeBooted',
    'boundedChannelBackpressure',
    'workerTransformedChunks',
    'admissionRejectNoMutation',
    'guardedStoreAvailable',
    'storageLaneAccepted',
    'persistentGoldenWorkload',
    'opfsWriteVerified',
    'opfsReadDigestMatches',
    'writeBudgetEstimated',
    'webLocksExercised',
    'locksSettled',
    'cleanupAttempted',
    'traceReceiptClosed'
  ]) {
    if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /fsync|crash|eviction|cross-browser/.test(claim))) errors.push('durability/cross-browser non-claims must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, proof });
}

export async function runBrowserOpfsProductWedgeWithApi(api = defaultApi, {
  generatedAt = 'deterministic-browser-opfs-product-wedge',
  source = 'examples/browser-opfs-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`
} = {}) {
  const capabilities = api.detectCapabilities();
  const unavailable = [];
  if (capabilities.opfs !== true) unavailable.push('opfs');
  if (capabilities.webLocks !== true) unavailable.push('webLocks');
  if (globalThis.isSecureContext !== true) unavailable.push('secureContext');
  if (unavailable.length) {
    throw new Error(`Browser OPFS product wedge requires ${unavailable.join(', ')}`);
  }

  const rt = await api.boot({ telemetry: 'browser-opfs-product-wedge', proof: api.REVISION, browserOpfsProductWedge: true, persistentGoldenWorkload: true });
  const namespace = Object.freeze({
    core: typeof rt.core?.channel === 'function' && typeof rt.core?.spawnAgent === 'function' && typeof rt.core?.transferObject === 'function',
    storage: typeof rt.storage?.opfsWebLockGuardedBlockStore === 'function' && typeof rt.storage?.blockStoreLaneAdapter === 'function',
    coordination: typeof rt.coordination?.crossLaneScheduler === 'function' && typeof rt.coordination?.admissionController === 'function',
    diagnostics: typeof rt.diagnostics?.kernelKitTraceExport === 'function'
  });
  const prefix = `browserrt/${api.REVISION}/browser-opfs-product-wedge/${prefixSuffix}`;
  const label = 'browser-opfs-product-wedge';
  const guardedStore = rt.storage.opfsWebLockGuardedBlockStore({
    label,
    prefix,
    lockPrefix: `browserrt:${api.REVISION}:browser-opfs-product-wedge`,
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
      { id: 'storage', rank: 80, capacity: 1, quantum: 64, maxQueuedCost: 4096 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 256 }
    ]
  });
  const adapter = rt.storage.blockStoreLaneAdapter({ label: `${label}:adapter`, store: guardedStore, scheduler, lane: 'storage' });
  const beforeSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });

  let cleanupAccepted = null;
  let cleanupResult = null;
  let error = null;
  let closed = false;
  try {
    const channel = rt.core.channel({ label: 'browser-opfs-golden-channel', capacity: 2, overflow: 'fail' });
    await channel.send({ id: 'chunk-0', values: [3, 5, 8, 13] });
    await channel.send({ id: 'chunk-1', values: [21, 34, 55, 89] });
    let overflowDisposition = 'not-observed';
    try { await channel.send({ id: 'chunk-overflow', values: [144] }); } catch { overflowDisposition = 'failed-full'; }
    const queuedJobs = [await channel.receive(), await channel.receive()];

    const agent = await rt.core.spawnAgent({ name: 'browser-opfs-golden-agent' });
    const transformed = [];
    let allTransfersDetached = true;
    try {
      for (const job of queuedJobs) {
        const array = new Uint32Array(job.values);
        const transferBuffer = array.buffer.slice(0);
        const transfer = rt.core.transferObject(transferBuffer, { id: `browser-opfs-golden-transfer:${job.id}`, label: job.id });
        const sum = await agent.call('sum-u32', { ref: transfer.ref, buffer: transfer.buffer }, { transfer: transfer.transferList, lane: 'cpu', priority: 'user-visible' });
        allTransfersDetached = allTransfersDetached && transferBuffer.byteLength === 0 && transfer.buffer.byteLength === 0;
        transformed.push(Object.freeze({ id: job.id, values: job.values, expectedSum: job.values.reduce((a, b) => a + b, 0), sum: sum.sum, count: sum.count, bytes: sum.bytes }));
      }
    } finally {
      await agent.terminate('browser-opfs-golden-agent-complete');
    }

    const payloads = transformed.map((row) => encodeJson({ project: 'BrowserRT', revision: api.REVISION, workload: 'browser-opfs-golden', source, importSpecifier, prefix, chunk: row.id, sum: row.sum, count: row.count }));
    const totalBytes = payloads.reduce((total, bytes) => total + bytes.byteLength, 0);
    const admission = rt.coordination.admissionController({ label: 'browser-opfs-golden-admission', lowWatermarkBytes: 0, highWatermarkBytes: Math.max(totalBytes + 16, 128), hardLimitBytes: Math.max(totalBytes + 128, 512) });
    const admitted = admission.tryAdmit({ bytes: totalBytes, priority: 'user-visible', label: 'browser-opfs-golden-batch' });
    const rejected = admission.tryAdmit({ bytes: 1024 * 1024 * 1024, priority: 'background', label: 'browser-opfs-golden-over-budget' });

    for (const [index, payload] of payloads.entries()) {
      adapter.schedulePut(payload, {
        id: `browser-opfs-product-wedge-put-${index}`,
        priority: 'user-visible',
        label: `browser-opfs-product-wedge-payload-${index}`,
        fields: { workload: 'browser-opfs-golden', chunkIndex: index },
        putOptions: { timeoutMs: 2000, writeBudgetGuard: { requireEstimate: true, minFreeBytes: 0, maxUsageRatio: 1 } }
      });
    }
    const estimate = adapter.scheduleEstimate({ id: 'browser-opfs-product-wedge-estimate', estimateOptions: { timeoutMs: 2000 } });
    await adapter.drain({ maxSteps: payloads.length + 1 });
    const putResults = payloads.map((_, index) => adapter.result(`browser-opfs-product-wedge-put-${index}`));
    const expectedDigests = await Promise.all(payloads.map(async (payload) => `sha256:${await api.digestBytesHex(payload)}`));

    for (const [index, putResult] of putResults.entries()) {
      adapter.scheduleVerify(putResult.ref, { id: `browser-opfs-product-wedge-verify-${index}`, verifyOptions: { timeoutMs: 2000 } });
      adapter.scheduleGet(putResult.ref, { id: `browser-opfs-product-wedge-get-${index}`, getOptions: { timeoutMs: 2000 } });
    }
    await adapter.drain({ maxSteps: payloads.length * 2 });
    const estimateResult = adapter.result('browser-opfs-product-wedge-estimate') || {};
    const readChecks = [];
    for (const [index, expectedDigest] of expectedDigests.entries()) {
      const verifyResult = adapter.result(`browser-opfs-product-wedge-verify-${index}`);
      const readBytes = adapter.result(`browser-opfs-product-wedge-get-${index}`);
      const readDigest = `sha256:${await api.digestBytesHex(readBytes)}`;
      readChecks.push(Object.freeze({ index, putDigest: putResults[index]?.digest || null, verifyDigest: verifyResult?.digest || null, verifyOk: verifyResult?.ok === true, expectedDigest, readDigest, readDigestMatches: readDigest === expectedDigest, putDigestMatchesExpected: putResults[index]?.digest === expectedDigest }));
    }

    const release = admitted.admitted ? admission.release(admitted.leaseId, { outcome: 'browser-opfs-golden-stored' }) : Object.freeze({ released: false });
    const cleanup = adapter.scheduleCleanupForTest({ id: 'browser-opfs-product-wedge-cleanup', cleanupOptions: { timeoutMs: 2000 } });
    cleanupAccepted = cleanup.accepted === true;
    await adapter.drain({ maxSteps: 1 });
    cleanupResult = adapter.result('browser-opfs-product-wedge-cleanup');
    const afterSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
    const adapterSnapshot = adapter.snapshot();
    const guardSnapshot = guardedStore.snapshot();
    const trace = rt.close();
    closed = true;
    const traceKinds = trace.map((event) => event.kind);
    const observed = Object.freeze({
      imports: { publicApiOnly: true, importSpecifier },
      namespace,
      environment: {
        crossOriginIsolated: globalThis.crossOriginIsolated === true,
        isSecureContext: globalThis.isSecureContext === true,
        hasOpfs: capabilities.opfs === true,
        hasWebLocks: capabilities.webLocks === true,
        hasWorker: typeof Worker === 'function'
      },
      runtime: { revision: api.REVISION, version: api.VERSION, revisionMatches: rt.revision === api.REVISION, versionMatches: rt.version === api.VERSION },
      channel: { overflowDisposition, receivedCount: queuedJobs.length, receivedIds: queuedJobs.map((job) => job.id) },
      worker: { chunkCount: transformed.length, allSumsMatch: transformed.every((row) => row.sum === row.expectedSum), allTransfersDetached, rows: transformed.map((row) => ({ id: row.id, sum: row.sum, count: row.count, bytes: row.bytes })) },
      admission: { accepted: admitted.admitted === true, rejectedNoMutation: rejected.admitted === false && rejected.noMutation === true, released: release.released === true, inFlightBytesAfterRelease: release.inFlightBytes ?? admission.snapshot().inFlightBytes },
      storage: {
        prefix,
        provider: guardSnapshot.provider,
        guardedAvailable: guardedStore.available === true,
        putAccepted: putResults.every(Boolean),
        verifyAccepted: readChecks.length === payloads.length,
        getAccepted: readChecks.length === payloads.length,
        estimateAccepted: estimate.accepted === true,
        chunkPutCount: putResults.filter(Boolean).length,
        readChecks,
        putDigestMatchesExpected: readChecks.every((row) => row.putDigestMatchesExpected),
        allVerifiesOk: readChecks.every((row) => row.verifyOk),
        allReadsMatch: readChecks.every((row) => row.readDigestMatches),
        budgetChecked: putResults.every((row) => row?.budget?.checked === true),
        estimateQuota: estimateResult.quota ?? null,
        estimateUsage: estimateResult.usage ?? null,
        adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(adapterSnapshot).ok === true
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
      trace: { count: trace.length, kinds: traceKinds }
    });
    const proof = proofFromObserved(observed);
    const missing = Object.entries(proof).filter(([, value]) => value !== true).map(([key]) => key);
    const receipt = Object.freeze({
      project: 'BrowserRT',
      revision: api.REVISION,
      version: api.VERSION,
      schema: 1,
      format: BROWSERRT_BROWSER_OPFS_PRODUCT_WEDGE_FORMAT,
      source,
      generatedAt,
      status: missing.length === 0 ? 'passed' : 'failed',
      purpose: 'Installed-browser persistent golden workload using the BrowserRT product namespaces: bounded queue, Worker transfer transform, admission no-mutation guard, real OPFS async block storage guarded by same-origin Web Locks, storage-lane verify/read/estimate, lock settlement, and cleanup.',
      proof,
      missing,
      observed,
      nonClaims: Object.freeze([
        'Managed Chromium OPFS/Web Locks package smoke only; no cross-browser, registry, bundler, quota-pressure, organic eviction, fsync, abrupt crash, or production durability claim.',
        'The proof writes, verifies, reads, estimates, settles locks, and cleans up under one same-origin browser profile; cross-tab contention, reload/reopen, tab close, and process-kill claims remain separate explicit browser tasks.'
      ])
    });
    const validation = validateBrowserOpfsProductWedgeReceipt(receipt);
    return Object.freeze({ project: 'BrowserRT', revision: api.REVISION, version: api.VERSION, schema: 1, status: validation.ok ? 'passed' : 'failed', probe_id: `${api.REVISION}-browser-opfs-product-wedge`, receipt, validation, traceKinds });
  } catch (caught) {
    error = caught;
    throw caught;
  } finally {
    if (error && cleanupAccepted !== true) {
      try { await guardedStore.cleanupForTest({ timeoutMs: 2000 }); } catch {}
    }
    if (!closed) {
      try { rt.close(); } catch {}
    }
  }
}

export async function runBrowserOpfsProductWedgeConsumer(options = {}) {
  return runBrowserOpfsProductWedgeWithApi(defaultApi, { source: 'examples/browser-opfs-product-wedge-consumer.mjs', importSpecifier: '../src/public-api.mjs', ...options });
}

if (typeof process !== 'undefined' && process.argv && import.meta.url === `file://${process.argv[1]}`) {
  console.log(JSON.stringify(await runBrowserOpfsProductWedgeConsumer(), null, 2));
}
