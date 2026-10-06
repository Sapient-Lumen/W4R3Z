import {
  REVISION,
  VERSION,
  boot,
  createKernelKitDemoPlan,
  validateKernelKitDemoPlan,
  detectCapabilities,
  digestBytesHex,
  validateOpfsStorageLaneAdapterSnapshot,
  KERNEL_KIT_DEMO_NON_CLAIMS
} from './browserrt.mjs';
export const KERNEL_KIT_BROWSER_RUNNER_SCHEMA = 1;
export function traceProjection(trace) {
  return trace.map((event) => {
    const out = { kind: event.kind };
    for (const key of ['label', 'op', 'opId', 'lane', 'priority', 'disposition', 'reason', 'code', 'stage', 'bytes', 'digest', 'duplicate', 'deleted', 'transferCount']) {
      if (Object.hasOwn(event, key)) out[key] = event[key];
    }
    return out;
  }).filter((event) => event.kind);
}
const KERNEL_KIT_POSTURED_GUARDED_STORAGE_BUDGET_POLICY = Object.freeze({
  requireEstimate: true,
  reserveRatio: 0,
  reserveFloorBytes: 0,
  reserveCapBytes: 0,
  maxUsageRatio: 1
});
function posturedGuardedStorageProof(posturedLaneOrGuarded = null) {
  const laneAdapterFactory = posturedLaneOrGuarded?.posturedGuarded ? posturedLaneOrGuarded : null;
  const posturedGuarded = laneAdapterFactory?.posturedGuarded || posturedLaneOrGuarded || null;
  const posture = posturedGuarded?.posture || {};
  const admissionPolicy = posturedGuarded?.admissionPolicy || {};
  const writeBudgetGuard = posturedGuarded?.writeBudgetGuard || {};
  const lockContentionPolicy = posturedGuarded?.lockContentionPolicy || {};
  const posturedGuardedFactoryUsed = posturedGuarded?.status === 'admitted-and-guarded'
    && writeBudgetGuard.source === 'browser-storage-posture-admission-policy'
    && lockContentionPolicy.source === 'postured-web-lock-guarded-opfs-factory';
  return Object.freeze({
    posturedGuardedFactoryUsed,
    posturedLaneAdapterFactoryUsed: laneAdapterFactory?.status === 'admitted-guarded-lane-adapter'
      && laneAdapterFactory.adapterFactorySource === 'postured-web-lock-guarded-storage-lane-adapter-factory'
      && posturedGuardedFactoryUsed,
    adapterFactorySource: laneAdapterFactory?.adapterFactorySource || null,
    postureStatus: posture.status || null,
    postureRiskLevel: posture.riskLevel || null,
    admissionStatus: admissionPolicy.status || null,
    writeBudgetGuardSource: writeBudgetGuard.source || null,
    writeBudgetGuardPolicySource: writeBudgetGuard.policySource || writeBudgetGuard.source || null,
    lockContentionPolicySource: lockContentionPolicy.source || null,
    lockContentionTimeoutMs: lockContentionPolicy.lockTimeoutMs ?? null
  });
}
export function compactKernelKitGuardedStorageSnapshot(snapshot = null, posturedGuarded = null) {
  const postureProof = posturedGuardedStorageProof(posturedGuarded);
  if (!snapshot || typeof snapshot !== 'object') {
    return Object.freeze({
      status: 'not-observed',
      source: 'kernel-kit-browser-runner',
      guardedProvider: false,
      webLocksAvailable: false,
      exclusiveMutationsObserved: false,
      sharedReadsObserved: false,
      lockAcquiredReleased: false,
      posturedGuardedFactoryUsed: postureProof.posturedGuardedFactoryUsed,
      posturedLaneAdapterFactoryUsed: postureProof.posturedLaneAdapterFactoryUsed,
      adapterFactorySource: postureProof.adapterFactorySource,
      postureStatus: postureProof.postureStatus,
      admissionStatus: postureProof.admissionStatus,
      writeBudgetGuardSource: postureProof.writeBudgetGuardSource,
      lockContentionPolicySource: postureProof.lockContentionPolicySource,
      noFairnessClaim: true
    });
  }
  const stats = snapshot.stats || {};
  const coordinatorStats = snapshot.coordinator?.stats || {};
  const provider = String(snapshot.provider || '');
  const proof = Object.freeze({
    guardedProvider: provider.startsWith('web-lock-guarded:'),
    webLocksAvailable: snapshot.available === true,
    exclusiveMutationsObserved: Number(stats.exclusiveOperations || 0) >= 1 && (Number(stats.puts || 0) + Number(stats.deletes || 0) + Number(stats.cleanupCalls || 0)) >= 1,
    sharedReadsObserved: Number(stats.sharedOperations || 0) >= 1 && (Number(stats.gets || 0) + Number(stats.has || 0) + Number(stats.verifies || 0) + Number(stats.estimates || 0)) >= 1,
    lockAcquiredReleased: Number(coordinatorStats.acquired || 0) >= 1 && Number(coordinatorStats.released || 0) >= 1 && Number(coordinatorStats.errors || 0) === 0,
    posturedGuardedFactoryUsed: postureProof.posturedGuardedFactoryUsed,
    posturedLaneAdapterFactoryUsed: postureProof.posturedLaneAdapterFactoryUsed,
    postureGuardPropagated: postureProof.posturedGuardedFactoryUsed && postureProof.admissionStatus === 'admit-with-guard' && postureProof.writeBudgetGuardSource === 'browser-storage-posture-admission-policy',
    boundedLockContentionPolicy: postureProof.lockContentionPolicySource === 'postured-web-lock-guarded-opfs-factory' && Number.isFinite(Number(postureProof.lockContentionTimeoutMs)),
    noFairnessClaim: true
  });
  const observed = proof.guardedProvider && proof.webLocksAvailable && proof.exclusiveMutationsObserved && proof.sharedReadsObserved && proof.lockAcquiredReleased && proof.posturedGuardedFactoryUsed && proof.posturedLaneAdapterFactoryUsed && proof.postureGuardPropagated && proof.boundedLockContentionPolicy && proof.noFairnessClaim;
  return Object.freeze({
    status: observed ? 'observed' : 'partial',
    source: 'kernel-kit-browser-runner',
    provider: snapshot.provider || null,
    prefix: snapshot.prefix || null,
    lockName: snapshot.lockName || null,
    readMode: snapshot.readMode || null,
    available: snapshot.available === true,
    lockTimeoutMs: snapshot.lockTimeoutMs ?? null,
    postureStatus: postureProof.postureStatus,
    postureRiskLevel: postureProof.postureRiskLevel,
    admissionStatus: postureProof.admissionStatus,
    writeBudgetGuardSource: postureProof.writeBudgetGuardSource,
    writeBudgetGuardPolicySource: postureProof.writeBudgetGuardPolicySource,
    lockContentionPolicySource: postureProof.lockContentionPolicySource,
    lockContentionTimeoutMs: postureProof.lockContentionTimeoutMs,
    posturedGuardedFactoryUsed: postureProof.posturedGuardedFactoryUsed,
    posturedLaneAdapterFactoryUsed: postureProof.posturedLaneAdapterFactoryUsed,
    adapterFactorySource: postureProof.adapterFactorySource,
    stats: Object.freeze({
      operations: Number(stats.operations || 0),
      exclusiveOperations: Number(stats.exclusiveOperations || 0),
      sharedOperations: Number(stats.sharedOperations || 0),
      puts: Number(stats.puts || 0),
      gets: Number(stats.gets || 0),
      has: Number(stats.has || 0),
      verifies: Number(stats.verifies || 0),
      deletes: Number(stats.deletes || 0),
      cleanupCalls: Number(stats.cleanupCalls || 0),
      errors: Number(stats.errors || 0)
    }),
    coordinatorStats: Object.freeze({
      requests: Number(coordinatorStats.requests || 0),
      acquired: Number(coordinatorStats.acquired || 0),
      released: Number(coordinatorStats.released || 0),
      exclusiveRequests: Number(coordinatorStats.exclusiveRequests || 0),
      sharedRequests: Number(coordinatorStats.sharedRequests || 0),
      errors: Number(coordinatorStats.errors || 0),
      timeouts: Number(coordinatorStats.timeouts || 0)
    }),
    proof
  });
}
async function createKernelKitPosturedGuardedStorage(rt, { prefix, label, lockPrefix, source = 'kernel-kit-browser-runner' } = {}) {
  const posturedLaneAdapter = await rt.opfsWebLockGuardedStorageLaneAdapterWithPosture({
    label,
    prefix,
    lockPrefix,
    lockName: 'storage-lane',
    lockContentionTimeoutMs: 1200,
    budgetPolicy: KERNEL_KIT_POSTURED_GUARDED_STORAGE_BUDGET_POLICY,
    storeConfig: {
      verifyExistingBlocksOnPut: true,
      verifyAfterWrite: true,
      verifyOnHas: true
    }
  });
  const posturedGuarded = posturedLaneAdapter.posturedGuarded;
  const guardedStore = posturedLaneAdapter.guardedStore || posturedLaneAdapter.store;
  const adapter = posturedLaneAdapter.adapter;
  return Object.freeze({
    source,
    posturedLaneAdapter,
    posturedGuarded,
    guardedStore,
    adapter,
    writeBudgetGuard: posturedLaneAdapter.writeBudgetGuard,
    storageAdmission: Object.freeze({
      status: posturedLaneAdapter.admissionPolicy?.status || null,
      postureStatus: posturedLaneAdapter.posture?.status || null,
      writeBudgetGuardSource: posturedLaneAdapter.writeBudgetGuard?.source || null,
      lockContentionPolicySource: posturedLaneAdapter.lockContentionPolicy?.source || null,
      lockContentionTimeoutMs: posturedLaneAdapter.lockContentionPolicy?.lockTimeoutMs ?? null,
      adapterFactorySource: posturedLaneAdapter.adapterFactorySource || null
    })
  });
}
export function createKernelKitBrowserRunnerInfo() {
  const plan = createKernelKitDemoPlan({ revision: REVISION });
  const validation = validateKernelKitDemoPlan(plan);
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: KERNEL_KIT_BROWSER_RUNNER_SCHEMA,
    runner: 'kernel-kit-demo-browser-runner',
    runnerPurpose: 'Reusable browser-side runner for the integrated Kernel Kit demo proof and demo page.',
    plan,
    validation,
    capabilities: detectCapabilities(globalThis),
    page: typeof location === 'object' ? { location: location.href, readyState: document?.readyState, crossOriginIsolated, isSecureContext } : null,
    nonClaims: [
      'Browser runner info is not a production runtime claim.',
      'Browser runner info does not prove OPFS durability, quota, eviction, crash recovery, browser restart, or cross-browser behavior.'
    ]
  });
}
export async function runKernelKitDemoWork(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/kernel-kit-demo`;
  const rt = await boot({
    telemetry: 'browser-cdp',
    proof: REVISION,
    kernelKitDemoProof: true,
    browserCdpHarness: true,
    browserWorkerAgentProbe: true,
    opfsStorageLaneAdapterProof: true
  });
  const plan = createKernelKitDemoPlan({ revision: REVISION });
  const planValidation = validateKernelKitDemoPlan(plan);
  const channel = rt.channel({ label: 'kernel-kit-demo-control', capacity: 1, overflow: 'fail' });
  await channel.send({ step: 'boot-runtime', revision: REVISION });
  const channelValue = await channel.receive();
  const agent = await rt.spawnAgent({ name: 'kernel-kit-demo-worker' });
  const ping = await agent.call('ping', { demo: 'kernel-kit' });
  const buffer = new ArrayBuffer(16);
  new Uint32Array(buffer).set([29, 31, 37, 41]);
  const transfer = rt.transferObject(buffer, { id: 'transfer:kernel-kit-demo-sum', label: 'kernel-kit-demo-sum' });
  const transferRefBefore = { id: transfer.ref.id, bytes: transfer.ref.bytes, ownership: transfer.ref.ownership };
  const sum = await agent.call('sum-u32', { buffer: transfer.buffer, ref: transfer.ref }, { transfer: transfer.transferList, priority: 'user-blocking', lane: 'cpu' });
  const transferDetached = transfer.buffer.byteLength === 0 && buffer.byteLength === 0;
  await agent.terminate('kernel-kit-demo-worker-complete');
  const admission = rt.admissionController({ label: 'kernel-kit-demo-admission', lowWatermarkBytes: 32, highWatermarkBytes: 256, hardLimitBytes: 1024 });
  const demoDocument = {
    kind: 'BrowserRT Kernel Kit Demo Artifact',
    revision: REVISION,
    workerSum: sum.sum,
    workerCount: sum.count,
    workerRef: sum.ref?.id,
    channelValue,
    planSteps: plan.steps.map((step) => step.id),
    createdAt: 'deterministic-demo'
  };
  const payload = new TextEncoder().encode(JSON.stringify(demoDocument));
  const admissionAccepted = admission.tryAdmit({ bytes: payload.byteLength, priority: 'user-visible', label: 'kernel-kit-demo-opfs-write' });
  const admissionRejected = admission.tryAdmit({ bytes: 4096, priority: 'background', label: 'kernel-kit-demo-oversize' });
  const posturedStorage = await createKernelKitPosturedGuardedStorage(rt, { label: `${REVISION}-kernel-kit-demo-guarded-store`, prefix, lockPrefix: `browserrt:${REVISION}:kernel-kit-demo` });
  const { guardedStore, adapter, writeBudgetGuard, storageAdmission } = posturedStorage;
  const put = admissionAccepted.admitted ? adapter.schedulePut(payload, { id: 'demo-put', priority: 'user-visible', label: 'kernel-kit-demo-artifact', putOptions: { writeBudgetGuard } }) : { accepted: false, reason: 'admission-rejected' };
  const verifyBefore = adapter.scheduleVerify('sha256:0000000000000000000000000000000000000000000000000000000000000000', { id: 'verify-missing', priority: 'background' });
  const drain = await adapter.drain({ maxSteps: 8 });
  const putResult = adapter.result('demo-put');
  const payloadDigest = `sha256:${await digestBytesHex(payload)}`;
  if (admissionAccepted.admitted) admission.release(admissionAccepted.leaseId, { outcome: 'storage-write-complete' });
  const snapshot = adapter.snapshot();
  const guardedStorage = compactKernelKitGuardedStorageSnapshot(guardedStore.snapshot(), posturedStorage.posturedLaneAdapter);
  const adapterValidation = validateOpfsStorageLaneAdapterSnapshot(snapshot);
  const admissionSnapshot = admission.snapshot();
  const abortBoundary = await rt.kernelKitOpfsAbortBoundary({ prefix: `${prefix}/abort-boundary` });
  const storagePosture = await rt.kernelKitStoragePosture({ label: 'kernel-kit-demo-work-storage-posture' });
  const webLockPosture = await rt.kernelKitWebLockPosture({ label: 'kernel-kit-demo-work-web-lock-posture' });
  const lifecycleCheckpoint = rt.kernelKitLifecycleCheckpoint({
    runner: 'kernel-kit-demo-browser-runner-work',
    proof: {
      storageWrite: putResult?.digest === payloadDigest,
      opfsAbortBoundary: abortBoundary.status === 'passed' && abortBoundary.proof?.nonMutationBoundary === true,
      storageAbortBoundary: abortBoundary.proof?.compositeAbortRejected === true && abortBoundary.proof?.noBlockPresent === true,
      guardedStorageLane: guardedStorage.status === 'observed' && guardedStorage.proof?.guardedProvider === true && guardedStorage.proof?.lockAcquiredReleased === true && guardedStorage.proof?.posturedGuardedFactoryUsed === true && guardedStorage.proof?.posturedLaneAdapterFactoryUsed === true && guardedStorage.proof?.postureGuardPropagated === true,
      storagePostureObserved: storagePosture.proof?.estimateChecked === true && storagePosture.proof?.persistenceNotRequestedByDefault === true,
      posturedGuardedFactoryUsed: guardedStorage.proof?.posturedGuardedFactoryUsed === true,
      postureGuardPropagated: guardedStorage.proof?.postureGuardPropagated === true,
      writeBudgetChecked: putResult?.budget?.checked === true || guardedStorage.writeBudgetGuardSource === 'browser-storage-posture-admission-policy',
      webLockPostureObserved: webLockPosture.proof?.exclusiveNoOverlap === true && webLockPosture.proof?.sharedCoHold === true && webLockPosture.proof?.drainedAfterUse === true
    },
    storagePosture,
    webLockPosture,
    guardedStorageLane: guardedStorage,
    abortBoundary,
    storage: { result: putResult },
    nonClaims: KERNEL_KIT_DEMO_NON_CLAIMS
  }, { source: 'browser-kernel-kit-work' });
  const trace = rt.close();
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    runner: 'kernel-kit-demo-browser-runner',
    page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext },
    plan,
    planValidation,
    capabilities: detectCapabilities(globalThis),
    worker: { pingPong: ping.pong === true, pingEnvelopeMagic: ping.envelope?.magic, sum, transferRefBefore, transferDetached },
    channel: { received: channelValue, emptySize: channel.size() },
    admission: { accepted: admissionAccepted, rejected: admissionRejected, snapshot: admissionSnapshot },
    storage: {
      put,
      verifyBefore,
      result: putResult,
      ref: putResult?.ref ?? null,
      digest: putResult?.digest ?? null,
      payloadDigest,
      payloadBytes: payload.byteLength,
      demoDocument,
      drain: drain.results.map((row) => ({ op: row.op, ok: row.ok, lane: row.lane, dispatched: row.dispatched })),
      snapshot,
      guarded: guardedStorage,
      storageAdmission,
      budgetChecked: putResult?.budget?.checked === true,
      budgetPolicySource: putResult?.budget?.guard?.policySource || null,
      adapterValidation
    },
    guardedStorage,
    abortBoundary,
    storagePosture,
    webLockPosture,
    lifecycleCheckpoint,
    proof: {
      opfsAbortBoundary: abortBoundary.status === 'passed' && abortBoundary.proof?.nonMutationBoundary === true,
      storageAbortBoundary: abortBoundary.proof?.compositeAbortRejected === true && abortBoundary.proof?.noBlockPresent === true,
      guardedStorageLane: guardedStorage.status === 'observed' && guardedStorage.proof?.guardedProvider === true && guardedStorage.proof?.lockAcquiredReleased === true && guardedStorage.proof?.posturedGuardedFactoryUsed === true && guardedStorage.proof?.posturedLaneAdapterFactoryUsed === true && guardedStorage.proof?.postureGuardPropagated === true,
      storagePostureObserved: storagePosture.proof?.estimateChecked === true && storagePosture.proof?.persistenceNotRequestedByDefault === true,
      webLockPostureObserved: webLockPosture.proof?.exclusiveNoOverlap === true && webLockPosture.proof?.sharedCoHold === true && webLockPosture.proof?.drainedAfterUse === true,
      lifecycleCheckpoint: lifecycleCheckpoint.status === 'risk-checkpoint-ready'
    },
    traceKinds: trace.map((event) => event.kind),
    normalizedTrace: traceProjection(trace)
  };
}
export async function runKernelKitDemoReload(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/kernel-kit-demo`;
  const ref = options.ref;
  const expectedDigest = options.expectedDigest;
  if (!ref) throw new Error('runKernelKitDemoReload requires ref');
  const rt = await boot({ telemetry: 'browser-cdp', proof: REVISION, kernelKitDemoProof: true, browserCdpHarness: true, opfsStorageLaneAdapterProof: true });
  const plan = createKernelKitDemoPlan({ revision: REVISION });
  const posturedStorage = await createKernelKitPosturedGuardedStorage(rt, { label: `${REVISION}-kernel-kit-demo-reload-guarded-store`, prefix, lockPrefix: `browserrt:${REVISION}:kernel-kit-demo` });
  const { guardedStore, adapter, storageAdmission } = posturedStorage;
  const has = adapter.scheduleHas(ref, { id: 'demo-has', priority: 'user-visible' });
  const get = adapter.scheduleGet(ref, { id: 'demo-get', priority: 'user-visible' });
  const verify = adapter.scheduleVerify(ref, { id: 'demo-verify', priority: 'user-visible' });
  const drainRead = await adapter.drain({ maxSteps: 8 });
  const readBytes = adapter.result('demo-get');
  const readText = new TextDecoder().decode(readBytes);
  const parsed = JSON.parse(readText);
  const readDigest = `sha256:${await digestBytesHex(readBytes)}`;
  const del = adapter.scheduleDelete(ref, { id: 'demo-delete', priority: 'maintenance' });
  const cleanup = adapter.scheduleCleanupForTest({ id: 'demo-cleanup' });
  const drainCleanup = await adapter.drain({ maxSteps: 8 });
  const snapshot = adapter.snapshot();
  const guardedStorage = compactKernelKitGuardedStorageSnapshot(guardedStore.snapshot(), posturedStorage.posturedLaneAdapter);
  const validation = validateOpfsStorageLaneAdapterSnapshot(snapshot);
  const storagePosture = await rt.kernelKitStoragePosture({ label: 'kernel-kit-demo-reload-storage-posture' });
  const webLockPosture = await rt.kernelKitWebLockPosture({ label: 'kernel-kit-demo-reload-web-lock-posture' });
  const lifecycleCheckpoint = rt.kernelKitLifecycleCheckpoint({
    runner: 'kernel-kit-demo-browser-runner-reload',
    proof: {
      storagePathEvidencePresent: true,
      reloadReadback: readDigest === expectedDigest && adapter.result('demo-verify')?.ok === true,
      guardedStorageLane: guardedStorage.status === 'observed' && guardedStorage.proof?.guardedProvider === true && guardedStorage.proof?.lockAcquiredReleased === true && guardedStorage.proof?.posturedGuardedFactoryUsed === true && guardedStorage.proof?.posturedLaneAdapterFactoryUsed === true && guardedStorage.proof?.postureGuardPropagated === true,
      storagePostureObserved: storagePosture.proof?.estimateChecked === true && storagePosture.proof?.persistenceNotRequestedByDefault === true,
      webLockPostureObserved: webLockPosture.proof?.exclusiveNoOverlap === true && webLockPosture.proof?.sharedCoHold === true && webLockPosture.proof?.drainedAfterUse === true
    },
    storagePosture,
    webLockPosture,
    guardedStorageLane: guardedStorage,
    read: { verify: adapter.result('demo-verify') },
    nonClaims: KERNEL_KIT_DEMO_NON_CLAIMS
  }, { source: 'browser-kernel-kit-reload' });
  const trace = rt.close();
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    runner: 'kernel-kit-demo-browser-runner',
    page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext },
    planStepCount: plan.steps.length,
    accepted: { has, get, verify, del, cleanup },
    read: { digest: readDigest, expectedDigest, bytes: readBytes.byteLength, parsed, has: adapter.result('demo-has'), verify: adapter.result('demo-verify'), deleteResult: adapter.result('demo-delete'), cleanup: adapter.result('demo-cleanup') },
    drain: {
      read: drainRead.results.map((row) => ({ op: row.op, ok: row.ok, lane: row.lane, dispatched: row.dispatched })),
      cleanup: drainCleanup.results.map((row) => ({ op: row.op, ok: row.ok, lane: row.lane, dispatched: row.dispatched }))
    },
    snapshot,
    guardedStorage,
    storageAdmission,
    validation,
    storagePosture,
    webLockPosture,
    lifecycleCheckpoint,
    proof: { guardedStorageLane: guardedStorage.status === 'observed' && guardedStorage.proof?.guardedProvider === true && guardedStorage.proof?.lockAcquiredReleased === true && guardedStorage.proof?.posturedGuardedFactoryUsed === true && guardedStorage.proof?.posturedLaneAdapterFactoryUsed === true && guardedStorage.proof?.postureGuardPropagated === true, storagePostureObserved: storagePosture.proof?.estimateChecked === true && storagePosture.proof?.persistenceNotRequestedByDefault === true, webLockPostureObserved: webLockPosture.proof?.exclusiveNoOverlap === true && webLockPosture.proof?.sharedCoHold === true && webLockPosture.proof?.drainedAfterUse === true, lifecycleCheckpoint: lifecycleCheckpoint.status === 'risk-checkpoint-ready' },
    traceKinds: trace.map((event) => event.kind),
    normalizedTrace: traceProjection(trace)
  };
}
if (typeof window === 'object') {
  window.BrowserRTKernelKitDemo = Object.freeze({
    createKernelKitBrowserRunnerInfo,
    runKernelKitDemoWork,
    runKernelKitDemoReload
  });
}
