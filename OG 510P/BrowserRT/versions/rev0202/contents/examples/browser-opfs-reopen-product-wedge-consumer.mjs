import * as defaultApi from '../src/public-api.mjs';

export const BROWSERRT_BROWSER_OPFS_REOPEN_PRODUCT_WEDGE_FORMAT = 'browserrt.browser-opfs-reopen-product-wedge-receipt.v1';

const POSTURE_GUARD_SOURCE = 'browser-storage-posture-admission-policy';
const LOCK_POLICY_SOURCE = 'postured-web-lock-guarded-opfs-factory';
function posturedGuardedStorageOk(storage, { lockPolicy = false } = {}) {
  return storage?.posturedGuardedFactoryUsed === true && storage?.postureStatus === 'observed' && storage?.admissionStatus === 'admit-with-guard' && storage?.writeBudgetGuardSource === POSTURE_GUARD_SOURCE && (lockPolicy !== true || storage?.lockContentionPolicy?.source === LOCK_POLICY_SOURCE);
}
function verifiedWithPostureBudget(storage) {
  return storage?.readDigestMatches === true && storage?.verifyDigestMatches === true && storage?.budgetChecked === true && storage?.budgetPolicySource === POSTURE_GUARD_SOURCE;
}

function assertBrowserCapabilities(api) {
  const capabilities = api.detectCapabilities();
  const unavailable = [];
  if (capabilities.opfs !== true) unavailable.push('opfs');
  if (capabilities.webLocks !== true) unavailable.push('webLocks');
  if (globalThis.isSecureContext !== true) unavailable.push('secureContext');
  if (unavailable.length) throw new Error(`Browser OPFS reopen wedge requires ${unavailable.join(', ')}`);
  return capabilities;
}

function encodePayload(value) {
  return new TextEncoder().encode(JSON.stringify(value) + '\n');
}

function refDigest(ref) {
  if (typeof ref === 'string') return ref.startsWith('block:') ? ref.slice('block:'.length) : ref;
  return ref?.digest || ref?.hash || null;
}

function namespaceProof(rt) {
  return Object.freeze({
    core: typeof rt.core?.channel === 'function' && typeof rt.core?.spawnAgent === 'function',
    storage: typeof rt.storage?.opfsWebLockGuardedBlockStoreWithPosture === 'function' && typeof rt.storage?.blockStoreLaneAdapter === 'function',
    coordination: typeof rt.coordination?.crossLaneScheduler === 'function',
    diagnostics: typeof rt.diagnostics?.kernelKitTraceExport === 'function'
  });
}

function storagePostureProof(posturedGuarded) {
  return Object.freeze({
    posturedGuardedFactoryUsed: true,
    postureStatus: posturedGuarded.posture?.status || null,
    postureRiskLevel: posturedGuarded.posture?.riskLevel || null,
    admissionStatus: posturedGuarded.admissionPolicy?.status || null,
    writeBudgetGuardSource: posturedGuarded.writeBudgetGuard?.source || null,
    lockContentionPolicy: posturedGuarded.lockContentionPolicy || null,
    lockContentionPolicySource: posturedGuarded.lockContentionPolicy?.source || null,
    lockContentionTimeoutMs: posturedGuarded.lockContentionPolicy?.lockTimeoutMs ?? null
  });
}

async function createRuntimeObjects(api, { prefixSuffix, lockTimeoutMs = 2000, labelSuffix = 'session' } = {}) {
  const prefix = `browserrt/${api.REVISION}/browser-opfs-reopen-product-wedge/${prefixSuffix}`;
  const lockPrefix = `browserrt:${api.REVISION}:browser-opfs-reopen-product-wedge:${prefixSuffix}`;
  const rt = await api.boot({ telemetry: 'browser-opfs-reopen-product-wedge', proof: api.REVISION, browserOpfsReopenProductWedge: true, labelSuffix });
  const namespace = namespaceProof(rt);
  const label = `browser-opfs-reopen-product-wedge:${labelSuffix}`;
  const posturedGuarded = await rt.storage.opfsWebLockGuardedBlockStoreWithPosture({
    label,
    prefix,
    lockPrefix,
    lockName: 'reopen-opfs-block-store',
    lockTimeoutMs,
    budgetPolicy: { requireEstimate: true, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0, maxUsageRatio: 1 },
    storeConfig: {
      verifyExistingBlocksOnPut: true,
      verifyAfterWrite: true,
      verifyOnHas: true
    }
  });
  const guardedStore = posturedGuarded.guardedStore || posturedGuarded.store;
  const scheduler = rt.coordination.crossLaneScheduler({
    label: `${label}:scheduler`,
    lanes: [
      { id: 'storage', rank: 80, capacity: 1, quantum: 64, maxQueuedCost: 2048 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 256 }
    ]
  });
  const adapter = rt.storage.blockStoreLaneAdapter({ label: `${label}:adapter`, store: guardedStore, scheduler, lane: 'storage' });
  return { rt, namespace, guardedStore, scheduler, adapter, prefix, lockPrefix, lockName: guardedStore.fullLockName, posturedGuarded, storagePosture: storagePostureProof(posturedGuarded), posturedWriteBudgetGuard: posturedGuarded.writeBudgetGuard };
}

export async function writeBrowserOpfsReopenBlockWithApi(api = defaultApi, {
  generatedAt = 'deterministic-browser-opfs-reopen-write',
  source = 'examples/browser-opfs-reopen-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
  lockTimeoutMs = 2000,
  pageLoadId = globalThis.__BROWSERRT_PAGE_LOAD_ID || null
} = {}) {
  const capabilities = assertBrowserCapabilities(api);
  const { rt, namespace, guardedStore, adapter, prefix, lockPrefix, lockName, storagePosture, posturedWriteBudgetGuard } = await createRuntimeObjects(api, { prefixSuffix, lockTimeoutMs, labelSuffix: 'write-session' });
  const beforeSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
  const payload = encodePayload({ project: 'BrowserRT', revision: api.REVISION, source, importSpecifier, prefix, lockName, pageLoadId, phase: 'write-before-page-reload' });
  const expectedDigest = `sha256:${await api.digestBytesHex(payload)}`;
  const put = adapter.schedulePut(payload, {
    id: 'browser-opfs-reopen-write-put',
    priority: 'user-visible',
    label: 'browser-opfs-reopen-write-payload',
    putOptions: { timeoutMs: lockTimeoutMs, writeBudgetGuard: posturedWriteBudgetGuard }
  });
  await adapter.drain({ maxSteps: 1 });
  const putResult = adapter.result('browser-opfs-reopen-write-put');
  const verify = adapter.scheduleVerify(putResult.ref, { id: 'browser-opfs-reopen-write-verify', verifyOptions: { timeoutMs: lockTimeoutMs } });
  const get = adapter.scheduleGet(putResult.ref, { id: 'browser-opfs-reopen-write-get', getOptions: { timeoutMs: lockTimeoutMs } });
  const estimate = adapter.scheduleEstimate({ id: 'browser-opfs-reopen-write-estimate', estimateOptions: { timeoutMs: lockTimeoutMs } });
  await adapter.drain({ maxSteps: 3 });
  const verifyResult = adapter.result('browser-opfs-reopen-write-verify');
  const readBytes = adapter.result('browser-opfs-reopen-write-get');
  const estimateResult = adapter.result('browser-opfs-reopen-write-estimate') || {};
  const readDigest = `sha256:${await api.digestBytesHex(readBytes)}`;
  const afterSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
  const adapterSnapshot = adapter.snapshot();
  const guardSnapshot = guardedStore.snapshot();
  const trace = rt.close();
  const traceKinds = trace.map((event) => event.kind);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    phase: 'write-before-page-reload',
    generatedAt,
    source,
    importSpecifier,
    pageLoadId,
    prefixSuffix,
    prefix,
    lockPrefix,
    lockName,
    environment: {
      crossOriginIsolated: globalThis.crossOriginIsolated === true,
      isSecureContext: globalThis.isSecureContext === true,
      hasOpfs: capabilities.opfs === true,
      hasWebLocks: capabilities.webLocks === true,
      href: globalThis.location?.href || null,
      origin: globalThis.location?.origin || null
    },
    runtime: { revisionMatches: rt.revision === api.REVISION, versionMatches: rt.version === api.VERSION },
    namespace,
    storage: {
      provider: guardSnapshot.provider,
      guardedAvailable: guardedStore.available === true,
      putAccepted: put.accepted === true,
      verifyAccepted: verify.accepted === true,
      getAccepted: get.accepted === true,
      estimateAccepted: estimate.accepted === true,
      ref: putResult?.ref || null,
      path: putResult?.path || null,
      digest: putResult?.digest || null,
      expectedDigest,
      verifyDigest: verifyResult?.digest || null,
      verifyOk: verifyResult?.ok === true,
      readDigest,
      readDigestMatches: readDigest === expectedDigest,
      verifyDigestMatches: verifyResult?.digest === expectedDigest,
      budgetChecked: putResult?.budget?.checked === true,
      estimateQuota: estimateResult.quota ?? null,
      estimateUsage: estimateResult.usage ?? null,
      adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(adapterSnapshot).ok === true,
      ...storagePosture,
      budgetPolicySource: putResult?.budget?.guard?.policySource || null
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
    trace: { closed: traceKinds.includes('runtime:close'), kinds: traceKinds }
  });
}

export async function readBrowserOpfsReopenBlockWithApi(api = defaultApi, {
  ref,
  expectedDigest = refDigest(ref),
  generatedAt = 'deterministic-browser-opfs-reopen-read',
  source = 'examples/browser-opfs-reopen-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix,
  lockTimeoutMs = 2000,
  pageLoadId = globalThis.__BROWSERRT_PAGE_LOAD_ID || null,
  cleanup = true
} = {}) {
  if (!ref) throw new Error('readBrowserOpfsReopenBlockWithApi requires ref');
  if (!prefixSuffix) throw new Error('readBrowserOpfsReopenBlockWithApi requires prefixSuffix');
  const capabilities = assertBrowserCapabilities(api);
  const { rt, namespace, guardedStore, adapter, prefix, lockPrefix, lockName, storagePosture } = await createRuntimeObjects(api, { prefixSuffix, lockTimeoutMs, labelSuffix: 'read-session' });
  const beforeSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
  const verify = adapter.scheduleVerify(ref, { id: 'browser-opfs-reopen-read-verify', verifyOptions: { timeoutMs: lockTimeoutMs } });
  const get = adapter.scheduleGet(ref, { id: 'browser-opfs-reopen-read-get', getOptions: { timeoutMs: lockTimeoutMs } });
  const estimate = adapter.scheduleEstimate({ id: 'browser-opfs-reopen-read-estimate', estimateOptions: { timeoutMs: lockTimeoutMs } });
  await adapter.drain({ maxSteps: 3 });
  const verifyResult = adapter.result('browser-opfs-reopen-read-verify');
  const readBytes = adapter.result('browser-opfs-reopen-read-get');
  const estimateResult = adapter.result('browser-opfs-reopen-read-estimate') || {};
  const readDigest = `sha256:${await api.digestBytesHex(readBytes)}`;
  let cleanupAccepted = null;
  let cleanupResult = null;
  if (cleanup) {
    const cleanupTask = adapter.scheduleCleanupForTest({ id: 'browser-opfs-reopen-read-cleanup', cleanupOptions: { timeoutMs: lockTimeoutMs } });
    cleanupAccepted = cleanupTask.accepted === true;
    await adapter.drain({ maxSteps: 1 });
    cleanupResult = adapter.result('browser-opfs-reopen-read-cleanup');
  }
  const afterSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
  const adapterSnapshot = adapter.snapshot();
  const guardSnapshot = guardedStore.snapshot();
  const trace = rt.close();
  const traceKinds = trace.map((event) => event.kind);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    phase: 'read-after-page-reload',
    generatedAt,
    source,
    importSpecifier,
    pageLoadId,
    prefixSuffix,
    prefix,
    lockPrefix,
    lockName,
    environment: {
      crossOriginIsolated: globalThis.crossOriginIsolated === true,
      isSecureContext: globalThis.isSecureContext === true,
      hasOpfs: capabilities.opfs === true,
      hasWebLocks: capabilities.webLocks === true,
      href: globalThis.location?.href || null,
      origin: globalThis.location?.origin || null
    },
    runtime: { revisionMatches: rt.revision === api.REVISION, versionMatches: rt.version === api.VERSION },
    namespace,
    storage: {
      ref,
      expectedDigest,
      verifyDigest: verifyResult?.digest || null,
      verifyOk: verifyResult?.ok === true,
      readDigest,
      readDigestMatches: readDigest === expectedDigest,
      verifyDigestMatches: verifyResult?.digest === expectedDigest,
      estimateAccepted: estimate.accepted === true,
      estimateQuota: estimateResult.quota ?? null,
      estimateUsage: estimateResult.usage ?? null,
      adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(adapterSnapshot).ok === true,
      ...storagePosture
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
    cleanup: { accepted: cleanupAccepted, result: cleanup ? cleanupResult === true : null },
    trace: { closed: traceKinds.includes('runtime:close'), kinds: traceKinds }
  });
}


function safeError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

async function openPrefixDirectory(prefix, { create = true } = {}) {
  const root = await navigator.storage.getDirectory();
  let dir = root;
  for (const part of String(prefix || '').split('/').filter(Boolean)) {
    dir = await dir.getDirectoryHandle(part, { create });
  }
  return dir;
}

function blockPathFor(prefix, hash) {
  return `${prefix}/${hash.slice(0, 2)}/${hash.slice(2, 4)}/${hash}.blk`;
}

function interruptedCandidatePayloadForApi(api, { source, importSpecifier, prefix, pageLoadId, totalBytes }) {
  const total = Math.max(4096, Number(totalBytes) || 0);
  const payload = new Uint8Array(total);
  for (let i = 0; i < payload.length; i += 1) payload[i] = (i * 31 + api.REVISION.charCodeAt(api.REVISION.length - 1) * 17 + 91) & 255;
  const marker = new TextEncoder().encode(JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, source, importSpecifier, prefix, pageLoadId, phase: 'interrupted-unclosed-write-candidate' }) + '\n');
  payload.set(marker.slice(0, Math.min(marker.length, payload.length)));
  return payload;
}

async function digestForBytes(api, bytes) {
  const hash = await api.digestBytesHex(bytes);
  return Object.freeze({ hash, digest: `sha256:${hash}` });
}

export async function createBrowserOpfsInterruptedCandidateWithApi(api = defaultApi, {
  generatedAt = 'deterministic-browser-opfs-interrupted-candidate',
  source = 'examples/browser-opfs-reopen-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix,
  totalBytes = 512 * 1024,
  firstChunkBytes = 64 * 1024,
  pageLoadId = globalThis.__BROWSERRT_PAGE_LOAD_ID || null
} = {}) {
  if (!prefixSuffix) throw new Error('createBrowserOpfsInterruptedCandidateWithApi requires prefixSuffix');
  const capabilities = assertBrowserCapabilities(api);
  const total = Math.max(4096, Number(totalBytes) || 0);
  const first = Math.max(1, Math.min(total - 1, Number(firstChunkBytes) || 1));
  const prefix = `browserrt/${api.REVISION}/browser-opfs-reopen-product-wedge/${prefixSuffix}`;
  const payload = interruptedCandidatePayloadForApi(api, { source, importSpecifier, prefix, pageLoadId, totalBytes: total });
  const { hash, digest } = await digestForBytes(api, payload);
  const path = blockPathFor(prefix, hash);
  let dir = await openPrefixDirectory(prefix, { create: true });
  dir = await dir.getDirectoryHandle(hash.slice(0, 2), { create: true });
  dir = await dir.getDirectoryHandle(hash.slice(2, 4), { create: true });
  const file = await dir.getFileHandle(`${hash}.blk`, { create: true });
  const writable = await file.createWritable();
  const firstChunk = payload.slice(0, first);
  let writeSettled = false;
  let writeError = null;
  const writePromise = writable.write(firstChunk).then(() => { writeSettled = true; return 'fulfilled'; }).catch((error) => { writeSettled = true; writeError = safeError(error); return 'rejected'; });
  const firstWriteRace = await Promise.race([writePromise, new Promise((resolve) => setTimeout(() => resolve('pending-after-250ms'), 250))]);
  globalThis.__BROWSERRT_UNCLOSED_OPFS_CANDIDATE_WRITABLE = writable;
  globalThis.__BROWSERRT_UNCLOSED_OPFS_CANDIDATE_WRITE_PROMISE = writePromise;
  globalThis.__BROWSERRT_UNCLOSED_OPFS_CANDIDATE_PAYLOAD = payload;
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    generatedAt,
    source,
    importSpecifier,
    pageLoadId,
    prefixSuffix,
    prefix,
    digest,
    hash,
    path,
    bytes: payload.byteLength,
    firstChunkBytes: firstChunk.byteLength,
    writeCallIssued: true,
    firstWriteRace,
    firstWriteSettled: writeSettled,
    firstWriteError: writeError,
    closeCalled: false,
    environment: {
      crossOriginIsolated: globalThis.crossOriginIsolated === true,
      isSecureContext: globalThis.isSecureContext === true,
      hasOpfs: capabilities.opfs === true,
      hasWebLocks: capabilities.webLocks === true,
      href: globalThis.location?.href || null,
      origin: globalThis.location?.origin || null
    }
  });
}

export async function inspectBrowserOpfsInterruptedCandidateWithApi(api = defaultApi, {
  candidate,
  generatedAt = 'deterministic-browser-opfs-interrupted-candidate-inspection',
  source = 'examples/browser-opfs-reopen-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix = candidate?.prefixSuffix,
  lockTimeoutMs = 2000,
  cleanup = false,
  repairFullCandidate = false,
  pageLoadId = globalThis.__BROWSERRT_PAGE_LOAD_ID || null
} = {}) {
  if (!candidate?.hash || !candidate?.digest || !candidate?.path) throw new Error('inspectBrowserOpfsInterruptedCandidateWithApi requires candidate hash/digest/path');
  if (!prefixSuffix) throw new Error('inspectBrowserOpfsInterruptedCandidateWithApi requires prefixSuffix');
  const capabilities = assertBrowserCapabilities(api);
  const { rt, namespace, guardedStore, adapter, prefix, lockPrefix, lockName, storagePosture, posturedWriteBudgetGuard } = await createRuntimeObjects(api, { prefixSuffix, lockTimeoutMs, labelSuffix: 'interrupted-candidate-inspection' });
  const ref = Object.freeze({ kind: 'block', id: `block:${candidate.digest}`, digest: candidate.digest, hash: candidate.hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', path: candidate.path, bytes: candidate.bytes, label: 'interrupted-unclosed-write-candidate' });
  const beforeSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
  const inspection = { has: null, verify: null, get: null, delete: null, disposition: null, error: null };
  try {
    inspection.has = await guardedStore.has(ref, { timeoutMs: lockTimeoutMs });
    inspection.verify = await guardedStore.verify(ref, { timeoutMs: lockTimeoutMs });
    if (inspection.verify?.present !== true) {
      inspection.disposition = 'absent-after-unclosed-interrupted-write';
    } else if (inspection.verify?.ok !== true || inspection.verify?.reason === 'checksum-mismatch') {
      inspection.disposition = 'present-but-checksum-rejected-after-unclosed-interrupted-write';
    } else {
      try {
        const got = await guardedStore.get(ref, { timeoutMs: lockTimeoutMs });
        const readDigest = `sha256:${await api.digestBytesHex(got)}`;
        inspection.get = { ok: true, bytes: got.byteLength, readDigest, digestMatches: readDigest === candidate.digest, fullLength: got.byteLength === candidate.bytes };
        inspection.disposition = inspection.get.digestMatches && inspection.get.fullLength ? 'complete-valid-after-unclosed-interrupted-write' : 'readable-but-digest-or-size-mismatch-after-unclosed-interrupted-write';
      } catch (error) {
        inspection.get = { ok: false, error: safeError(error) };
        inspection.disposition = /CHECKSUM|MISMATCH|CORRUPT/i.test(`${error?.code || ''} ${error?.message || ''}`) ? 'present-but-checksum-rejected-after-unclosed-interrupted-write' : 'present-but-read-rejected-after-unclosed-interrupted-write';
      }
    }
  } catch (error) {
    inspection.error = safeError(error);
    inspection.disposition = 'inspection-error';
  }
  if (inspection.verify?.present === true || inspection.has === true) {
    try { inspection.delete = await guardedStore.delete(ref, { timeoutMs: lockTimeoutMs }); } catch (error) { inspection.delete = { error: safeError(error) }; }
  }
  let repairResult = null;
  if (repairFullCandidate) {
    repairResult = { requested: true, accepted: null, payloadMatchesCandidate: null, putDigestMatchesCandidate: null, verifyOk: null, readDigestMatchesCandidate: null, deleteAfterRepair: null, verifyAfterDeletePresent: null, error: null };
    try {
      const payload = interruptedCandidatePayloadForApi(api, { source: candidate.source || source, importSpecifier: candidate.importSpecifier || importSpecifier, prefix, pageLoadId: candidate.pageLoadId ?? pageLoadId, totalBytes: candidate.bytes });
      const payloadDigest = await digestForBytes(api, payload);
      repairResult.payloadDigest = payloadDigest.digest;
      repairResult.payloadMatchesCandidate = payloadDigest.digest === candidate.digest && payload.byteLength === candidate.bytes;
      if (!repairResult.payloadMatchesCandidate) throw new Error(`interrupted candidate repair payload mismatch: ${payloadDigest.digest} != ${candidate.digest}`);
      const putTask = adapter.schedulePut(payload, {
        id: 'browser-opfs-interrupted-candidate-repair-put',
        priority: 'user-visible',
        cost: 1,
        label: 'interrupted-candidate-full-payload-repair-retry',
        putOptions: { timeoutMs: lockTimeoutMs, writeBudgetGuard: posturedWriteBudgetGuard }
      });
      repairResult.accepted = putTask.accepted === true;
      await adapter.drain({ maxSteps: 4 });
      const putResult = adapter.result('browser-opfs-interrupted-candidate-repair-put');
      repairResult.putDigest = putResult?.digest || null;
      repairResult.putDigestMatchesCandidate = putResult?.digest === candidate.digest;
      repairResult.budgetChecked = putResult?.budget?.checked === true;
      repairResult.budgetPolicySource = putResult?.budget?.guard?.policySource || null;
      const verifyTask = adapter.scheduleVerify(putResult.ref, { id: 'browser-opfs-interrupted-candidate-repair-verify', verifyOptions: { timeoutMs: lockTimeoutMs } });
      const getTask = adapter.scheduleGet(putResult.ref, { id: 'browser-opfs-interrupted-candidate-repair-get', getOptions: { timeoutMs: lockTimeoutMs } });
      await adapter.drain({ maxSteps: 4 });
      const verifyResult = adapter.result('browser-opfs-interrupted-candidate-repair-verify');
      const got = adapter.result('browser-opfs-interrupted-candidate-repair-get');
      const readDigest = `sha256:${await api.digestBytesHex(got)}`;
      repairResult.verifyAccepted = verifyTask.accepted === true;
      repairResult.getAccepted = getTask.accepted === true;
      repairResult.verifyOk = verifyResult?.ok === true;
      repairResult.verifyDigest = verifyResult?.digest || null;
      repairResult.readDigest = readDigest;
      repairResult.readBytes = got?.byteLength ?? null;
      repairResult.readDigestMatchesCandidate = readDigest === candidate.digest;
      repairResult.readFullLength = got?.byteLength === candidate.bytes;
      const deleteTask = adapter.scheduleDelete(putResult.ref, { id: 'browser-opfs-interrupted-candidate-repair-delete', deleteOptions: { timeoutMs: lockTimeoutMs } });
      await adapter.drain({ maxSteps: 4 });
      repairResult.deleteAccepted = deleteTask.accepted === true;
      repairResult.deleteAfterRepair = adapter.result('browser-opfs-interrupted-candidate-repair-delete') === true;
      const afterDeleteVerify = await guardedStore.verify(ref, { timeoutMs: lockTimeoutMs });
      repairResult.verifyAfterDeletePresent = afterDeleteVerify.present === true;
      repairResult.verifyAfterDelete = afterDeleteVerify;
    } catch (error) {
      repairResult.error = safeError(error);
    }
    repairResult.ok = repairResult.error === null && repairResult.accepted === true && repairResult.payloadMatchesCandidate === true && repairResult.putDigestMatchesCandidate === true && repairResult.verifyOk === true && repairResult.readDigestMatchesCandidate === true && repairResult.readFullLength === true && repairResult.deleteAfterRepair === true && repairResult.verifyAfterDeletePresent === false;
  }
  let cleanupResult = null;
  if (cleanup) {
    try { cleanupResult = await guardedStore.cleanupForTest({ timeoutMs: lockTimeoutMs }); } catch (error) { cleanupResult = { error: safeError(error) }; }
  }
  const afterSettled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
  const guardSnapshot = guardedStore.snapshot();
  const trace = rt.close();
  const traceKinds = trace.map((event) => event.kind);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    generatedAt,
    source,
    importSpecifier,
    pageLoadId,
    prefixSuffix,
    prefix,
    lockPrefix,
    lockName,
    candidate,
    ref,
    namespace,
    environment: {
      crossOriginIsolated: globalThis.crossOriginIsolated === true,
      isSecureContext: globalThis.isSecureContext === true,
      hasOpfs: capabilities.opfs === true,
      hasWebLocks: capabilities.webLocks === true,
      href: globalThis.location?.href || null,
      origin: globalThis.location?.origin || null
    },
    runtime: { revisionMatches: rt.revision === api.REVISION, versionMatches: rt.version === api.VERSION },
    storage: {
      provider: guardSnapshot.provider,
      guardedAvailable: guardedStore.available === true,
      ...storagePosture
    },
    inspection,
    repair: repairResult || { requested: repairFullCandidate === true, ok: false },
    cleanup: { requested: cleanup === true, result: cleanupResult },
    locks: {
      beforeSettled: beforeSettled.ok === true,
      afterSettled: afterSettled.ok === true,
      available: guardSnapshot.available === true,
      lockName: guardSnapshot.lockName,
      exclusiveOperations: guardSnapshot.stats?.exclusiveOperations || 0,
      sharedOperations: guardSnapshot.stats?.sharedOperations || 0,
      errors: guardSnapshot.stats?.errors || 0
    },
    trace: { closed: traceKinds.includes('runtime:close'), kinds: traceKinds }
  });
}

function proofFromObserved(observed = {}) {
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true,
    browserCapabilitiesVisible: observed.environment?.hasOpfs === true && observed.environment?.hasWebLocks === true && observed.environment?.isSecureContext === true,
    packageRootImportedInBothSessions: observed.imports?.writeImportSpecifier === 'browserrt' && observed.imports?.readImportSpecifier === 'browserrt',
    firstRuntimeBooted: observed.write?.runtime?.revisionMatches === true && observed.write?.runtime?.versionMatches === true,
    namespacedFacadeUsedAcrossSessions: observed.write?.namespace?.storage === true && observed.write?.namespace?.coordination === true && observed.read?.namespace?.storage === true && observed.read?.namespace?.coordination === true,
    posturedGuardedFactoryUsedAcrossSessions: posturedGuardedStorageOk(observed.write?.storage, { lockPolicy: true }) && posturedGuardedStorageOk(observed.read?.storage, { lockPolicy: true }),
    firstWriteVerified: verifiedWithPostureBudget(observed.write?.storage),
    firstTraceClosed: observed.write?.trace?.closed === true,
    pageReloadObserved: Boolean(observed.reload?.beforePageLoadId) && Boolean(observed.reload?.afterPageLoadId) && observed.reload.beforePageLoadId !== observed.reload.afterPageLoadId,
    secondRuntimeReopened: observed.read?.runtime?.revisionMatches === true && observed.read?.runtime?.versionMatches === true,
    prefixStableAcrossReload: observed.write?.prefix === observed.read?.prefix && observed.write?.prefixSuffix === observed.read?.prefixSuffix,
    lockNameStableAcrossReload: observed.write?.lockName === observed.read?.lockName,
    reopenedReadDigestMatches: observed.read?.storage?.readDigestMatches === true && observed.read?.storage?.readDigest === observed.write?.storage?.expectedDigest,
    reopenedVerifyDigestMatches: observed.read?.storage?.verifyDigestMatches === true && observed.read?.storage?.verifyDigest === observed.write?.storage?.expectedDigest,
    locksSettledAcrossSessions: observed.write?.locks?.afterSettled === true && observed.read?.locks?.afterSettled === true,
    cleanupAttempted: (observed.read?.cleanup?.accepted === true && observed.read?.cleanup?.result === true) || observed.interruptedInspection?.cleanup?.result === true,
    secondTraceClosed: observed.read?.trace?.closed === true
  });
}

export function createBrowserOpfsReopenProductWedgeReceipt({ api = defaultApi, generatedAt = 'deterministic-browser-opfs-reopen-product-wedge', source = 'examples/browser-opfs-reopen-product-wedge-consumer.mjs', observed = {}, nonClaims = [] } = {}) {
  const proof = proofFromObserved(observed);
  const missing = Object.entries(proof).filter(([, value]) => value !== true).map(([key]) => key);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    format: BROWSERRT_BROWSER_OPFS_REOPEN_PRODUCT_WEDGE_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Reload wedge: Web-Lock-guarded OPFS write remains readable by a newly booted runtime.',
    proof,
    missing,
    observed,
    nonClaims: Object.freeze(nonClaims.length ? nonClaims : [
      'Chromium reload proof only; no cross-browser/fsync/quota/eviction/crash/service-worker/registry/production claim.',
      'Runtime closes before reload; no profile-kill or power-cycle claim.'
    ])
  });
}

export function validateBrowserOpfsReopenProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_BROWSER_OPFS_REOPEN_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_BROWSER_OPFS_REOPEN_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of [
    'publicApiImportOnly',
    'browserCapabilitiesVisible',
    'packageRootImportedInBothSessions',
    'firstRuntimeBooted',
    'namespacedFacadeUsedAcrossSessions',
    'posturedGuardedFactoryUsedAcrossSessions',
    'firstWriteVerified',
    'firstTraceClosed',
    'pageReloadObserved',
    'secondRuntimeReopened',
    'prefixStableAcrossReload',
    'lockNameStableAcrossReload',
    'reopenedReadDigestMatches',
    'reopenedVerifyDigestMatches',
    'locksSettledAcrossSessions',
    'cleanupAttempted',
    'secondTraceClosed'
  ]) {
    if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /fsync|eviction|crash|cross-browser/i.test(String(claim)))) errors.push('durability/cross-browser/crash non-claims must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, proof });
}

export async function runBrowserOpfsReopenProductWedgeWithApi(api = defaultApi, options = {}) {
  const write = await writeBrowserOpfsReopenBlockWithApi(api, options);
  const read = await readBrowserOpfsReopenBlockWithApi(api, { ...options, ref: write.storage.ref, expectedDigest: write.storage.expectedDigest, pageLoadId: options.pageLoadId });
  const observed = Object.freeze({
    imports: { publicApiOnly: true, writeImportSpecifier: options.importSpecifier || '../src/public-api.mjs', readImportSpecifier: options.importSpecifier || '../src/public-api.mjs' },
    environment: write.environment,
    reload: { beforePageLoadId: options.pageLoadId || write.pageLoadId, afterPageLoadId: options.pageLoadId || read.pageLoadId, note: 'single-context helper does not perform a page reload; use tools/package_installed_browser_reopen_opfs_consumer_probe.mjs for reload proof' },
    write,
    read
  });
  const receipt = createBrowserOpfsReopenProductWedgeReceipt({ api, observed, generatedAt: options.generatedAt, source: options.source });
  return Object.freeze({ project: 'BrowserRT', revision: api.REVISION, version: api.VERSION, schema: 1, status: receipt.status, receipt, validation: validateBrowserOpfsReopenProductWedgeReceipt(receipt) });
}


export const BROWSERRT_BROWSER_OPFS_ABRUPT_KILL_PRODUCT_WEDGE_FORMAT = 'browserrt.browser-opfs-abrupt-kill-product-wedge-receipt.v1';

function abruptKillProofFromObserved(observed = {}) {
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true,
    browserCapabilitiesVisible: observed.environment?.hasOpfs === true && observed.environment?.hasWebLocks === true && observed.environment?.isSecureContext === true,
    packageRootImportedInBothLaunches: observed.imports?.writeImportSpecifier === 'browserrt' && observed.imports?.readImportSpecifier === 'browserrt',
    sameOriginProfileRelaunch: observed.lifecycle?.sameOriginPage === true && observed.lifecycle?.profileReused === true,
    firstRuntimeBooted: observed.write?.runtime?.revisionMatches === true && observed.write?.runtime?.versionMatches === true,
    namespacedFacadeUsedAcrossProcessRelaunch: observed.write?.namespace?.storage === true && observed.write?.namespace?.coordination === true && observed.read?.namespace?.storage === true && observed.read?.namespace?.coordination === true && observed.interruptedInspection?.namespace?.storage === true,
    posturedGuardedFactoryUsedAcrossProcessRelaunch: posturedGuardedStorageOk(observed.write?.storage) && posturedGuardedStorageOk(observed.read?.storage) && posturedGuardedStorageOk(observed.interruptedInspection?.storage),
    acknowledgedWriteVerifiedBeforeKill: verifiedWithPostureBudget(observed.write?.storage),
    firstTraceClosedBeforeKill: observed.write?.trace?.closed === true,
    browserProcessSigkillObserved: observed.lifecycle?.firstBrowserProcessSigkilled === true && observed.lifecycle?.firstProcessTimedOut !== true,
    secondRuntimeReopened: observed.read?.runtime?.revisionMatches === true && observed.read?.runtime?.versionMatches === true,
    prefixStableAcrossProcessRelaunch: observed.write?.prefix === observed.read?.prefix && observed.write?.prefixSuffix === observed.read?.prefixSuffix,
    lockNameStableAcrossProcessRelaunch: observed.write?.lockName === observed.read?.lockName,
    relaunchedReadDigestMatches: observed.read?.storage?.readDigestMatches === true && observed.read?.storage?.readDigest === observed.write?.storage?.expectedDigest,
    relaunchedVerifyDigestMatches: observed.read?.storage?.verifyDigestMatches === true && observed.read?.storage?.verifyDigest === observed.write?.storage?.expectedDigest,
    interruptedCandidateCreatedBeforeKill: observed.interruptedCandidate?.writeCallIssued === true && observed.interruptedCandidate?.closeCalled === false && Number(observed.interruptedCandidate?.firstChunkBytes || 0) > 0 && Number(observed.interruptedCandidate?.firstChunkBytes || 0) < Number(observed.interruptedCandidate?.bytes || 0),
    interruptedCandidateNotSilentlyAccepted: ['absent-after-unclosed-interrupted-write', 'present-but-checksum-rejected-after-unclosed-interrupted-write', 'present-but-read-rejected-after-unclosed-interrupted-write'].includes(observed.interruptedInspection?.inspection?.disposition),
    interruptedCandidateCleanedOrAbsent: observed.interruptedInspection?.inspection?.verify?.present !== true || observed.interruptedInspection?.inspection?.delete === true || observed.interruptedInspection?.inspection?.delete?.deleted === true,
    interruptedCandidateRepairRetryVerified: observed.interruptedInspection?.repair?.ok === true && observed.interruptedInspection?.repair?.payloadMatchesCandidate === true && observed.interruptedInspection?.repair?.putDigestMatchesCandidate === true && observed.interruptedInspection?.repair?.readDigestMatchesCandidate === true && observed.interruptedInspection?.repair?.verifyAfterDeletePresent === false && observed.interruptedInspection?.repair?.budgetChecked === true && observed.interruptedInspection?.repair?.budgetPolicySource === POSTURE_GUARD_SOURCE,
    locksSettledAcrossProcessRelaunch: observed.write?.locks?.afterSettled === true && observed.read?.locks?.afterSettled === true,
    cleanupAttempted: (observed.read?.cleanup?.accepted === true && observed.read?.cleanup?.result === true) || observed.interruptedInspection?.cleanup?.result === true,
    secondTraceClosed: observed.read?.trace?.closed === true
  });
}

export function createBrowserOpfsAbruptKillProductWedgeReceipt({ api = defaultApi, generatedAt = 'deterministic-browser-opfs-abrupt-kill-product-wedge', source = 'examples/browser-opfs-reopen-product-wedge-consumer.mjs', observed = {}, nonClaims = [] } = {}) {
  const proof = abruptKillProofFromObserved(observed);
  const missing = Object.entries(proof).filter(([, value]) => value !== true).map(([key]) => key);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    format: BROWSERRT_BROWSER_OPFS_ABRUPT_KILL_PRODUCT_WEDGE_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Process-kill wedge: acknowledged digest survives relaunch; unclosed partial is absent/rejected, then guarded repair verifies.',
    proof,
    missing,
    observed,
    nonClaims: Object.freeze(nonClaims.length ? nonClaims : [
      'Chromium process-kill proof only; no cross-browser/crash-semantics/fsync/power-loss/quota/eviction/service-worker/production claim.',
      'Only acknowledged closed writes are positive evidence; no arbitrary in-flight recovery/fsync/power-loss claim.'
    ])
  });
}

export function validateBrowserOpfsAbruptKillProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_BROWSER_OPFS_ABRUPT_KILL_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_BROWSER_OPFS_ABRUPT_KILL_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of [
    'publicApiImportOnly',
    'browserCapabilitiesVisible',
    'packageRootImportedInBothLaunches',
    'sameOriginProfileRelaunch',
    'firstRuntimeBooted',
    'namespacedFacadeUsedAcrossProcessRelaunch',
    'posturedGuardedFactoryUsedAcrossProcessRelaunch',
    'acknowledgedWriteVerifiedBeforeKill',
    'firstTraceClosedBeforeKill',
    'browserProcessSigkillObserved',
    'secondRuntimeReopened',
    'prefixStableAcrossProcessRelaunch',
    'lockNameStableAcrossProcessRelaunch',
    'relaunchedReadDigestMatches',
    'relaunchedVerifyDigestMatches',
    'interruptedCandidateCreatedBeforeKill',
    'interruptedCandidateNotSilentlyAccepted',
    'interruptedCandidateCleanedOrAbsent',
    'interruptedCandidateRepairRetryVerified',
    'locksSettledAcrossProcessRelaunch',
    'cleanupAttempted',
    'secondTraceClosed'
  ]) {
    if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /fsync|power-loss|in-flight|cross-browser|eviction/i.test(String(claim)))) errors.push('durability/crash non-claims must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, proof });
}

if (typeof process !== 'undefined' && process.argv && import.meta.url === `file://${process.argv[1]}`) {
  console.log(JSON.stringify(await runBrowserOpfsReopenProductWedgeWithApi(defaultApi), null, 2));
}
