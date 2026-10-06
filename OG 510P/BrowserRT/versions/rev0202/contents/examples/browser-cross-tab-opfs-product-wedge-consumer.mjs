import * as defaultApi from '../src/public-api.mjs';

export const BROWSERRT_BROWSER_CROSS_TAB_OPFS_PRODUCT_WEDGE_FORMAT = 'browserrt.browser-cross-tab-opfs-product-wedge-receipt.v1';

const POSTURE_GUARD_SOURCE = 'browser-storage-posture-admission-policy';
const LOCK_POLICY_SOURCE = 'postured-web-lock-guarded-opfs-factory';
function posturedGuardedStorageOk(storage) {
  return storage?.posturedGuardedFactoryUsed === true && storage?.postureStatus === 'observed' && storage?.admissionStatus === 'admit-with-guard' && storage?.writeBudgetGuardSource === POSTURE_GUARD_SOURCE && storage?.lockContentionPolicy?.enabled === true && storage?.lockContentionPolicy?.source === LOCK_POLICY_SOURCE;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function assertBrowserCapabilities(api) {
  const capabilities = api.detectCapabilities();
  const unavailable = [];
  if (capabilities.opfs !== true) unavailable.push('opfs');
  if (capabilities.webLocks !== true) unavailable.push('webLocks');
  if (globalThis.isSecureContext !== true) unavailable.push('secureContext');
  if (unavailable.length) throw new Error(`Browser cross-tab OPFS wedge requires ${unavailable.join(', ')}`);
  return capabilities;
}

function describeError(error) {
  return Object.freeze({
    name: error?.name || 'Error',
    message: error?.message || String(error),
    code: error?.code ?? null,
    detail: error?.detail ?? null,
    storageDisposition: error?.storageDisposition ?? null
  });
}

function encodePayload(value) {
  return new TextEncoder().encode(JSON.stringify(value) + '\n');
}

function refDigest(ref) {
  if (typeof ref === 'string') return ref.startsWith('block:') ? ref.slice('block:'.length) : ref;
  return ref?.digest || ref?.hash || null;
}

function nowMs() {
  return Math.round((globalThis.performance?.now?.() ?? Date.now()) * 1000) / 1000;
}

function proofFromObserved(observed = {}) {
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true,
    twoTabsPrepared: observed.tabs?.preparedCount === 2 && observed.tabs?.tabIds?.includes('A') && observed.tabs?.tabIds?.includes('B'),
    browserCapabilitiesVisible: observed.environment?.hasOpfs === true && observed.environment?.hasWebLocks === true && observed.environment?.isSecureContext === true,
    namespacedFacadeUsed: observed.namespace?.storage === true && observed.namespace?.coordination === true,
    posturedGuardedFactoryUsed: posturedGuardedStorageOk(observed.storage),
    sameOriginSharedProfile: observed.environment?.sameOrigin === true && observed.environment?.samePrefix === true && observed.environment?.sameLockName === true,
    exclusiveHoldObserved: observed.contention?.holdAcquired === true && observed.contention?.holdReleased === true,
    queuedTabTimedOutBeforeAcquisition: observed.contention?.timedOutBeforeRelease === true && /TIMEOUT|AbortError|abort/i.test(String(observed.contention?.timeoutCode || observed.contention?.timeoutName || observed.contention?.timeoutMessage || '')),
    queuedWaiterAcquiredAfterRelease: observed.contention?.queuedWaiterPendingBeforeRelease === true && observed.contention?.queuedWaiterCompletedAfterRelease === true && observed.contention?.queuedWaiterDigestMatches === true && observed.contention?.queuedWaiterBudgetChecked === true,
    timedOutRequestDidNotMutateAfterRelease: observed.contention?.timedOutNoMutationAfterRelease === true && observed.contention?.timedOutDigestAbsentAfterRelease === true,
    recoveryWriteAfterRelease: observed.contention?.writeAfterReleaseOk === true,
    crossTabStorageVisible: observed.crossRead?.aReadBDigestMatches === true && observed.crossRead?.bReadADigestMatches === true,
    storageLaneUsed: observed.storage?.aAdapterSnapshotValid === true && observed.storage?.bAdapterSnapshotValid === true,
    locksSettled: observed.locks?.aSettled === true && observed.locks?.bSettled === true,
    cleanupAttempted: observed.cleanup?.accepted === true && observed.cleanup?.result === true,
    traceReceiptClosed: observed.trace?.aClosed === true && observed.trace?.bClosed === true
  });
}

export function createBrowserCrossTabOpfsProductWedgeReceipt({ api = defaultApi, generatedAt = 'deterministic-browser-cross-tab-opfs-product-wedge', source = 'examples/browser-cross-tab-opfs-product-wedge-consumer.mjs', observed = {}, nonClaims = [] } = {}) {
  const proof = proofFromObserved(observed);
  const missing = Object.entries(proof).filter(([, value]) => value !== true).map(([key]) => key);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    format: BROWSERRT_BROWSER_CROSS_TAB_OPFS_PRODUCT_WEDGE_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Two-tab OPFS/Web Locks wedge: queued timeout no ghost write, waiter acquires after release, recovery write succeeds.',
    proof,
    missing,
    observed,
    nonClaims: Object.freeze(nonClaims.length ? nonClaims : [
      'Chromium smoke only; no cross-browser/fairness/fsync/eviction/quota/crash/service-worker/production claim.',
      'Short pending-lock timeout proves pre-acquire cancellation; Web Locks do not cancel acquired callbacks.'
    ])
  });
}

export function validateBrowserCrossTabOpfsProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_BROWSER_CROSS_TAB_OPFS_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_BROWSER_CROSS_TAB_OPFS_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of [
    'publicApiImportOnly',
    'twoTabsPrepared',
    'browserCapabilitiesVisible',
    'namespacedFacadeUsed',
    'posturedGuardedFactoryUsed',
    'sameOriginSharedProfile',
    'exclusiveHoldObserved',
    'queuedTabTimedOutBeforeAcquisition',
    'queuedWaiterAcquiredAfterRelease',
    'timedOutRequestDidNotMutateAfterRelease',
    'recoveryWriteAfterRelease',
    'crossTabStorageVisible',
    'storageLaneUsed',
    'locksSettled',
    'cleanupAttempted',
    'traceReceiptClosed'
  ]) {
    if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /cross-browser|fsync|eviction|production/i.test(String(claim)))) errors.push('durability/cross-browser non-claims must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, proof });
}


export const BROWSERRT_BROWSER_TAB_CLOSE_OPFS_PRODUCT_WEDGE_FORMAT = 'browserrt.browser-tab-close-opfs-product-wedge-receipt.v1';

function tabCloseProofFromObserved(observed = {}) {
  return Object.freeze({
    publicApiImportOnly: observed.imports?.publicApiOnly === true && observed.imports?.importSpecifier === 'browserrt',
    twoTabsPrepared: observed.tabs?.preparedCount === 2 && observed.tabs?.holderTabId === 'A' && observed.tabs?.survivorTabId === 'B',
    browserCapabilitiesVisible: observed.environment?.hasOpfs === true && observed.environment?.hasWebLocks === true && observed.environment?.isSecureContext === true,
    namespacedFacadeUsed: observed.namespace?.storage === true && observed.namespace?.coordination === true,
    posturedGuardedFactoryUsed: posturedGuardedStorageOk(observed.storage),
    sameOriginSharedProfile: observed.environment?.sameOrigin === true && observed.environment?.samePrefix === true && observed.environment?.sameLockName === true,
    holderAcquiredAndWroteBeforeClose: observed.termination?.holderAcquired === true && observed.termination?.holderWriteVerified === true && observed.termination?.holderWriteBudgetChecked === true,
    survivorTimedOutBeforeTabClose: observed.termination?.survivorTimedOutBeforeClose === true && /TIMEOUT|AbortError|abort/i.test(String(observed.termination?.timeoutCode || observed.termination?.timeoutName || observed.termination?.timeoutMessage || '')),
    holderTargetClosed: observed.termination?.holderTargetClosed === true,
    survivorRecoveredAfterTabClose: observed.termination?.survivorWriteAfterCloseOk === true && observed.termination?.survivorSettledAfterClose === true,
    holderBlockStillReadable: observed.storage?.survivorReadHolderDigestMatches === true && observed.storage?.holderVerifyDigestMatches === true,
    storageLaneUsed: observed.storage?.survivorAdapterSnapshotValid === true,
    cleanupAttempted: observed.cleanup?.accepted === true && observed.cleanup?.result === true,
    survivorTraceClosed: observed.trace?.survivorClosed === true
  });
}

export function createBrowserTabCloseOpfsProductWedgeReceipt({ api = defaultApi, generatedAt = 'deterministic-browser-tab-close-opfs-product-wedge', source = 'examples/browser-cross-tab-opfs-product-wedge-consumer.mjs', observed = {}, nonClaims = [] } = {}) {
  const proof = tabCloseProofFromObserved(observed);
  const missing = Object.entries(proof).filter(([, value]) => value !== true).map(([key]) => key);
  return Object.freeze({
    project: 'BrowserRT',
    revision: api.REVISION,
    version: api.VERSION,
    schema: 1,
    format: BROWSERRT_BROWSER_TAB_CLOSE_OPFS_PRODUCT_WEDGE_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Tab-close wedge: same-origin Web Lock release and OPFS recovery after holder closes during write hold.',
    proof,
    missing,
    observed,
    nonClaims: Object.freeze(nonClaims.length ? nonClaims : [
      'Chromium/CDP tab-close proof only; no cross-browser/mobile/crash/power-loss/quota/eviction/production claim.',
      'Shows release on page close; no callback-cancellation-after-acquire claim.'
    ])
  });
}

export function validateBrowserTabCloseOpfsProductWedgeReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_BROWSER_TAB_CLOSE_OPFS_PRODUCT_WEDGE_FORMAT) errors.push(`format must be ${BROWSERRT_BROWSER_TAB_CLOSE_OPFS_PRODUCT_WEDGE_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of [
    'publicApiImportOnly',
    'twoTabsPrepared',
    'browserCapabilitiesVisible',
    'namespacedFacadeUsed',
    'posturedGuardedFactoryUsed',
    'sameOriginSharedProfile',
    'holderAcquiredAndWroteBeforeClose',
    'survivorTimedOutBeforeTabClose',
    'holderTargetClosed',
    'survivorRecoveredAfterTabClose',
    'holderBlockStillReadable',
    'storageLaneUsed',
    'cleanupAttempted',
    'survivorTraceClosed'
  ]) {
    if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /cross-browser|crash|power-loss|eviction|production/i.test(String(claim)))) errors.push('lifecycle/durability non-claims must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, proof });
}

export async function createBrowserCrossTabOpfsParticipantWithApi(api = defaultApi, {
  tabId = 'A',
  generatedAt = 'deterministic-browser-cross-tab-opfs-participant',
  source = 'examples/browser-cross-tab-opfs-product-wedge-consumer.mjs',
  importSpecifier = '../src/public-api.mjs',
  prefixSuffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
  lockTimeoutMs = 1200
} = {}) {
  const capabilities = assertBrowserCapabilities(api);
  const label = `browser-cross-tab-opfs-wedge:${tabId}`;
  const prefix = `browserrt/${api.REVISION}/browser-cross-tab-opfs-product-wedge/${prefixSuffix}`;
  const lockPrefix = `browserrt:${api.REVISION}:browser-cross-tab-opfs-product-wedge:${prefixSuffix}`;
  const lockName = 'shared-opfs-block-store';
  const rt = await api.boot({ telemetry: 'browser-cross-tab-opfs-product-wedge', proof: api.REVISION, browserCrossTabOpfsProductWedge: true, tabId });
  const namespace = Object.freeze({
    storage: typeof rt.storage?.opfsWebLockGuardedBlockStoreWithPosture === 'function' && typeof rt.storage?.blockStoreLaneAdapter === 'function',
    coordination: typeof rt.coordination?.crossLaneScheduler === 'function'
  });
  const posturedGuarded = await rt.storage.opfsWebLockGuardedBlockStoreWithPosture({
    label,
    prefix,
    lockName,
    lockPrefix,
    lockTimeoutMs,
    budgetPolicy: { requireEstimate: true, reserveRatio: 0, reserveFloorBytes: 0, reserveCapBytes: 0, maxUsageRatio: 1 },
    storeConfig: {
      verifyExistingBlocksOnPut: true,
      verifyAfterWrite: true,
      verifyOnHas: true
    }
  });
  const guardedStore = posturedGuarded.store;
  const posturedWriteBudgetGuard = posturedGuarded.writeBudgetGuard;
  const storagePosture = Object.freeze({
    posturedGuardedFactoryUsed: true,
    postureStatus: posturedGuarded.posture?.status || null,
    admissionStatus: posturedGuarded.admissionPolicy?.status || null,
    writeBudgetGuardSource: posturedWriteBudgetGuard?.source || null,
    lockContentionPolicy: posturedGuarded.lockContentionPolicy || null
  });
  const scheduler = rt.coordination.crossLaneScheduler({
    label: `${label}:scheduler`,
    lanes: [
      { id: 'storage', rank: 80, capacity: 1, quantum: 64, maxQueuedCost: 4096 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 256 }
    ]
  });
  const adapter = rt.storage.blockStoreLaneAdapter({ label: `${label}:adapter`, store: guardedStore, scheduler, lane: 'storage' });
  const state = { tabId, generatedAt, source, importSpecifier, prefixSuffix, prefix, lockPrefix, lockName: guardedStore.fullLockName, namespace, capabilities, storagePosture, posturedWriteBudgetGuard, rt, guardedStore, scheduler, adapter, hold: null, writes: {}, reads: {}, queuedPuts: {}, closed: false, traceKinds: [] };

  async function prepare() {
    const settled = await guardedStore.waitForSettled({ timeoutMs: 1000, intervalMs: 25 });
    return Object.freeze({
      tabId,
      revision: api.REVISION,
      version: api.VERSION,
      prefix,
      lockName: guardedStore.fullLockName,
      environment: {
        crossOriginIsolated: globalThis.crossOriginIsolated === true,
        isSecureContext: globalThis.isSecureContext === true,
        hasOpfs: capabilities.opfs === true,
        hasWebLocks: capabilities.webLocks === true,
        href: globalThis.location?.href || null,
        origin: globalThis.location?.origin || null
      },
      settled: settled.ok === true,
      provider: guardedStore.provider,
      namespace,
      storagePosture
    });
  }

  async function startExclusiveHold({ acquireTimeoutMs = 2000 } = {}) {
    if (state.hold?.pending) throw new Error('exclusive hold already pending');
    let releaseHold;
    let acquiredResolve;
    let acquiredReject;
    const acquired = new Promise((resolve, reject) => { acquiredResolve = resolve; acquiredReject = reject; });
    const release = new Promise((resolve) => { releaseHold = resolve; });
    state.releaseHold = releaseHold;
    const holdState = { pending: true, acquired: false, released: false, startedAt: nowMs(), acquiredAt: null, releasedAt: null, error: null };
    state.hold = holdState;
    holdState.promise = guardedStore.withExclusive(async () => {
      holdState.acquired = true;
      holdState.acquiredAt = nowMs();
      acquiredResolve(true);
      await release;
      holdState.released = true;
      holdState.releasedAt = nowMs();
      return Object.freeze({ tabId, released: true, heldMs: Math.max(0, holdState.releasedAt - holdState.acquiredAt) });
    }, { tabId, phase: 'cross-tab-exclusive-hold' }, { timeoutMs: acquireTimeoutMs }).then((result) => {
      holdState.pending = false;
      holdState.result = result;
      return result;
    }).catch((error) => {
      holdState.pending = false;
      holdState.error = describeError(error);
      acquiredReject(error);
      throw error;
    });
    const deadline = Date.now() + Math.max(1, acquireTimeoutMs);
    while (!holdState.acquired && !holdState.error && Date.now() < deadline) {
      await Promise.race([acquired.catch(() => false), sleep(10)]);
    }
    if (!holdState.acquired) throw new Error(`exclusive hold was not acquired within ${acquireTimeoutMs}ms`);
    return snapshot();
  }

  async function releaseExclusiveHold() {
    if (!state.hold) throw new Error('no exclusive hold exists');
    if (state.hold.released !== true && typeof state.releaseHold === 'function') state.releaseHold(true);
    const result = await state.hold.promise;
    return Object.freeze({ tabId, result, snapshot: snapshot() });
  }

  async function startExclusiveWriteHold({ acquireTimeoutMs = 2000, phase = 'tab-close-open-ended-write-hold' } = {}) {
    if (state.hold?.pending) throw new Error('exclusive hold already pending');
    let releaseHold;
    let acquiredResolve;
    let acquiredReject;
    const acquired = new Promise((resolve, reject) => { acquiredResolve = resolve; acquiredReject = reject; });
    const release = new Promise((resolve) => { releaseHold = resolve; });
    state.releaseHold = releaseHold;
    const holdState = { pending: true, acquired: false, released: false, startedAt: nowMs(), acquiredAt: null, releasedAt: null, error: null, write: null };
    state.hold = holdState;
    holdState.promise = guardedStore.withExclusive(async () => {
      holdState.acquiredAt = nowMs();
      const payload = encodePayload({ project: 'BrowserRT', revision: api.REVISION, tabId, source, importSpecifier, prefix, phase });
      const expectedDigest = `sha256:${await api.digestBytesHex(payload)}`;
      const put = await guardedStore.store.put(payload, { label: `${tabId}:${phase}` }, { writeBudgetGuard: posturedWriteBudgetGuard });
      const got = await guardedStore.store.get(put.ref);
      const readDigest = `sha256:${await api.digestBytesHex(got)}`;
      const verify = await guardedStore.store.verify(put.ref);
      holdState.write = Object.freeze({
        tabId,
        phase,
        digest: put?.digest || null,
        expectedDigest,
        readDigest,
        verifyDigest: verify?.digest || null,
        verifyOk: verify?.ok === true,
        readDigestMatches: readDigest === expectedDigest,
        ref: put?.ref || null,
        path: put?.path || null,
        bytes: got?.byteLength ?? null,
        budgetChecked: put?.budget?.checked === true
      });
      state.writes[`${tabId}:exclusive-write-hold`] = holdState.write;
      holdState.acquired = true;
      acquiredResolve(true);
      await release;
      holdState.released = true;
      holdState.releasedAt = nowMs();
      return Object.freeze({ tabId, released: true, heldMs: Math.max(0, holdState.releasedAt - holdState.acquiredAt), write: holdState.write });
    }, { tabId, phase: 'cross-tab-exclusive-write-hold' }, { timeoutMs: acquireTimeoutMs }).then((result) => {
      holdState.pending = false;
      holdState.result = result;
      return result;
    }).catch((error) => {
      holdState.pending = false;
      holdState.error = describeError(error);
      acquiredReject(error);
      throw error;
    });
    const deadline = Date.now() + Math.max(1, acquireTimeoutMs);
    while ((!holdState.acquired || !holdState.write?.ref) && !holdState.error && Date.now() < deadline) {
      await Promise.race([acquired.catch(() => false), sleep(10)]);
    }
    if (!holdState.acquired) throw new Error(`exclusive write hold was not acquired within ${acquireTimeoutMs}ms`);
    if (!holdState.write?.ref) throw new Error('exclusive write hold did not produce a readable block ref');
    return snapshot();
  }

  async function attemptTimedPutWhileLocked({ timeoutMs = 120, labelSuffix = 'contended-timeout' } = {}) {
    const payload = encodePayload({ project: 'BrowserRT', revision: api.REVISION, tabId, source, importSpecifier, prefix, phase: labelSuffix, timeoutMs });
    const expectedDigest = `sha256:${await api.digestBytesHex(payload)}`;
    try {
      const result = await guardedStore.put(payload, { label: `${tabId}:${labelSuffix}` }, { timeoutMs, writeBudgetGuard: posturedWriteBudgetGuard });
      return Object.freeze({ tabId, ok: true, timedOut: false, expectedDigest, result, snapshot: snapshot() });
    } catch (error) {
      return Object.freeze({ tabId, ok: false, timedOut: /TIMEOUT|AbortError|abort/i.test(String(error?.code || error?.name || error?.message || '')), expectedDigest, error: describeError(error), snapshot: snapshot() });
    }
  }

  async function startQueuedPutWhileLocked({ opId = `${tabId}:queued-waiter-after-release`, timeoutMs = 2500, labelSuffix = 'queued-waiter-after-release' } = {}) {
    if (state.queuedPuts[opId]?.pending) throw new Error(`queued put already pending for ${opId}`);
    const payload = encodePayload({ project: 'BrowserRT', revision: api.REVISION, tabId, source, importSpecifier, prefix, phase: labelSuffix, opId, timeoutMs });
    const expectedDigest = `sha256:${await api.digestBytesHex(payload)}`;
    const record = { tabId, opId, phase: labelSuffix, timeoutMs, expectedDigest, startedAt: nowMs(), pending: true, completedAt: null, row: null, error: null };
    state.queuedPuts[opId] = record;
    record.promise = guardedStore.put(payload, { label: `${tabId}:${labelSuffix}` }, { timeoutMs, writeBudgetGuard: posturedWriteBudgetGuard }).then(async (put) => {
      const got = await guardedStore.get(put.ref, { timeoutMs: lockTimeoutMs });
      const verify = await guardedStore.verify(put.ref, { timeoutMs: lockTimeoutMs });
      const readDigest = `sha256:${await api.digestBytesHex(got)}`;
      const row = Object.freeze({
        tabId,
        opId,
        phase: labelSuffix,
        ok: true,
        timedOut: false,
        pendingBeforeRelease: true,
        startedAt: record.startedAt,
        completedAt: nowMs(),
        digest: put?.digest || null,
        expectedDigest,
        readDigest,
        verifyDigest: verify?.digest || null,
        verifyOk: verify?.ok === true,
        digestMatches: readDigest === expectedDigest && verify?.digest === expectedDigest,
        ref: put?.ref || null,
        path: put?.path || null,
        bytes: got?.byteLength ?? null,
        budgetChecked: put?.budget?.checked === true
      });
      state.writes[opId] = row;
      return row;
    }).catch((error) => {
      const row = Object.freeze({ tabId, opId, phase: labelSuffix, ok: false, timedOut: /TIMEOUT|AbortError|abort/i.test(String(error?.code || error?.name || error?.message || '')), error: describeError(error), startedAt: record.startedAt, completedAt: nowMs() });
      throw Object.assign(error, { browserRtQueuedPutRow: row });
    }).finally(() => {
      record.pending = false;
      record.completedAt = nowMs();
    });
    record.promise.then((row) => { record.row = row; }, (error) => { record.error = error?.browserRtQueuedPutRow || describeError(error); });
    return Object.freeze({ tabId, opId, started: true, pending: true, expectedDigest, snapshot: snapshot() });
  }

  async function awaitQueuedPut({ opId = `${tabId}:queued-waiter-after-release` } = {}) {
    const record = state.queuedPuts[opId];
    if (!record) throw new Error(`no queued put exists for ${opId}`);
    try {
      const row = await record.promise;
      return Object.freeze({ tabId, opId, row, snapshot: snapshot() });
    } catch (error) {
      return Object.freeze({ tabId, opId, row: error?.browserRtQueuedPutRow || Object.freeze({ ok: false, error: describeError(error) }), snapshot: snapshot() });
    }
  }

  async function writeViaStorageLane({ opId = `${tabId}:write`, phase = 'after-release' } = {}) {
    const payload = encodePayload({ project: 'BrowserRT', revision: api.REVISION, tabId, source, importSpecifier, prefix, phase, opId });
    const expectedDigest = `sha256:${await api.digestBytesHex(payload)}`;
    const put = adapter.schedulePut(payload, {
      id: `${tabId}:${opId}:put`,
      priority: 'user-visible',
      label: `${tabId}:${phase}`,
      putOptions: { timeoutMs: lockTimeoutMs, writeBudgetGuard: posturedWriteBudgetGuard }
    });
    await adapter.drain({ maxSteps: 1 });
    const putResult = adapter.result(`${tabId}:${opId}:put`);
    const verify = adapter.scheduleVerify(putResult.ref, { id: `${tabId}:${opId}:verify`, verifyOptions: { timeoutMs: lockTimeoutMs } });
    const get = adapter.scheduleGet(putResult.ref, { id: `${tabId}:${opId}:get`, getOptions: { timeoutMs: lockTimeoutMs } });
    await adapter.drain({ maxSteps: 2 });
    const verifyResult = adapter.result(`${tabId}:${opId}:verify`);
    const readBytes = adapter.result(`${tabId}:${opId}:get`);
    const readDigest = `sha256:${await api.digestBytesHex(readBytes)}`;
    const row = Object.freeze({
      tabId,
      opId,
      phase,
      accepted: put.accepted === true && verify.accepted === true && get.accepted === true,
      digest: putResult?.digest || null,
      expectedDigest,
      readDigest,
      verifyDigest: verifyResult?.digest || null,
      verifyOk: verifyResult?.ok === true,
      ref: putResult?.ref || null,
      path: putResult?.path || null,
      bytes: readBytes?.byteLength ?? null,
      budgetChecked: putResult?.budget?.checked === true,
      adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(adapter.snapshot()).ok === true
    });
    state.writes[opId] = row;
    return row;
  }

  async function verifyDigestAbsentViaStorageLane(digest, { opId = `${tabId}:digest-absent-check` } = {}) {
    const has = adapter.scheduleHas(digest, { id: `${tabId}:${opId}:has`, hasOptions: { timeoutMs: lockTimeoutMs } });
    await adapter.drain({ maxSteps: 1 });
    const present = adapter.result(`${tabId}:${opId}:has`);
    const row = Object.freeze({
      tabId,
      opId,
      accepted: has.accepted === true,
      digest,
      present: present === true,
      absent: present === false,
      adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(adapter.snapshot()).ok === true
    });
    state.reads[opId] = row;
    return row;
  }

  async function readRefViaStorageLane(ref, { opId = `${tabId}:cross-read`, expectedDigest = null } = {}) {
    const get = adapter.scheduleGet(ref, { id: `${tabId}:${opId}:get`, getOptions: { timeoutMs: lockTimeoutMs } });
    const verify = adapter.scheduleVerify(ref, { id: `${tabId}:${opId}:verify`, verifyOptions: { timeoutMs: lockTimeoutMs } });
    await adapter.drain({ maxSteps: 2 });
    const readBytes = adapter.result(`${tabId}:${opId}:get`);
    const verifyResult = adapter.result(`${tabId}:${opId}:verify`);
    const readDigest = `sha256:${await api.digestBytesHex(readBytes)}`;
    const row = Object.freeze({
      tabId,
      opId,
      accepted: get.accepted === true && verify.accepted === true,
      expectedDigest: expectedDigest || refDigest(ref),
      readDigest,
      verifyDigest: verifyResult?.digest || null,
      verifyOk: verifyResult?.ok === true,
      digestMatches: expectedDigest ? readDigest === expectedDigest : readDigest === refDigest(ref),
      adapterSnapshotValid: api.validateBlockStoreLaneAdapterSnapshot(adapter.snapshot()).ok === true
    });
    state.reads[opId] = row;
    return row;
  }

  async function settled({ timeoutMs = 1500 } = {}) {
    const result = await guardedStore.waitForSettled({ timeoutMs, intervalMs: 25 });
    return Object.freeze({ tabId, ok: result.ok === true, result, snapshot: snapshot() });
  }

  async function queryLocks() {
    const result = await guardedStore.queryLocks();
    return Object.freeze({ tabId, result, snapshot: snapshot() });
  }

  async function cleanup() {
    const cleanupAccepted = true;
    const result = await guardedStore.cleanupForTest({ timeoutMs: lockTimeoutMs });
    return Object.freeze({ tabId, accepted: cleanupAccepted, result: result === true, snapshot: snapshot() });
  }

  function snapshot() {
    const guardSnapshot = guardedStore.snapshot();
    return Object.freeze({
      tabId,
      revision: api.REVISION,
      version: api.VERSION,
      prefix,
      lockPrefix,
      lockName: guardedStore.fullLockName,
      hold: state.hold ? { pending: state.hold.pending === true, acquired: state.hold.acquired === true, released: state.hold.released === true, error: state.hold.error || null, startedAt: state.hold.startedAt, acquiredAt: state.hold.acquiredAt, releasedAt: state.hold.releasedAt, write: state.hold.write || null } : null,
      namespace,
      store: { provider: guardedStore.provider, available: guardedStore.available === true, storagePosture, guard: guardSnapshot },
      writes: state.writes,
      reads: state.reads,
      queuedPuts: Object.fromEntries(Object.entries(state.queuedPuts).map(([key, value]) => [key, { tabId: value.tabId, opId: value.opId, phase: value.phase, pending: value.pending === true, startedAt: value.startedAt, completedAt: value.completedAt, expectedDigest: value.expectedDigest, row: value.row, error: value.error }])),
      closed: state.closed === true,
      traceKinds: state.traceKinds
    });
  }

  function close() {
    if (!state.closed) {
      const trace = rt.close();
      state.traceKinds = trace.map((event) => event.kind);
      state.closed = true;
    }
    return snapshot();
  }

  return Object.freeze({ prepare, startExclusiveHold, startExclusiveWriteHold, releaseExclusiveHold, attemptTimedPutWhileLocked, startQueuedPutWhileLocked, awaitQueuedPut, writeViaStorageLane, verifyDigestAbsentViaStorageLane, readRefViaStorageLane, settled, queryLocks, cleanup, snapshot, close });
}
