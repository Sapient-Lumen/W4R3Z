// BrowserRT Kernel Kit browser runner.
// This keeps the explicit browser/CDP proof out of giant inline Runtime.evaluate
// strings and makes the demo page reusable by humans and probes.
import {
  REVISION,
  VERSION,
  boot,
  createKernelKitDemoPlan,
  validateKernelKitDemoPlan,
  detectCapabilities,
  digestBytesHex,
  validateOpfsStorageLaneAdapterSnapshot
} from './browserrt.mjs';

export const KERNEL_KIT_BROWSER_RUNNER_SCHEMA = 1;

export function traceProjection(trace) {
  return trace.map((event) => {
    const out = { kind: event.kind };
    for (const key of ['label', 'op', 'opId', 'lane', 'priority', 'disposition', 'reason', 'bytes', 'digest', 'duplicate', 'deleted', 'transferCount']) {
      if (Object.hasOwn(event, key)) out[key] = event[key];
    }
    return out;
  }).filter((event) => event.kind);
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
  const adapter = rt.opfsBlockStoreStorageLaneAdapter({ label: `${REVISION}-kernel-kit-demo`, prefix });
  const put = admissionAccepted.admitted ? adapter.schedulePut(payload, { id: 'demo-put', priority: 'user-visible', label: 'kernel-kit-demo-artifact' }) : { accepted: false, reason: 'admission-rejected' };
  const verifyBefore = adapter.scheduleVerify('sha256:0000000000000000000000000000000000000000000000000000000000000000', { id: 'verify-missing', priority: 'background' });
  const drain = await adapter.drain({ maxSteps: 8 });
  const putResult = adapter.result('demo-put');
  if (admissionAccepted.admitted) admission.release(admissionAccepted.leaseId, { outcome: 'storage-write-complete' });
  const snapshot = adapter.snapshot();
  const adapterValidation = validateOpfsStorageLaneAdapterSnapshot(snapshot);
  const admissionSnapshot = admission.snapshot();
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
      payloadDigest: `sha256:${await digestBytesHex(payload)}`,
      payloadBytes: payload.byteLength,
      demoDocument,
      drain: drain.results.map((row) => ({ op: row.op, ok: row.ok, lane: row.lane, dispatched: row.dispatched })),
      snapshot,
      adapterValidation
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
  const adapter = rt.opfsBlockStoreStorageLaneAdapter({ label: `${REVISION}-kernel-kit-demo-reload`, prefix });
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
  const validation = validateOpfsStorageLaneAdapterSnapshot(snapshot);
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
    validation,
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
