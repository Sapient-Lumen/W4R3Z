import * as defaultApi from '../src/public-api.mjs';

export async function runProductWedgeWithApi(api = defaultApi, { generatedAt = 'deterministic-product-wedge', source = 'examples/product-wedge-consumer.mjs', importSpecifier = '../src/public-api.mjs' } = {}) {
  const {
    REVISION,
    VERSION,
    boot,
    digestBytesHex,
    createBrowserRtProductWedgeReceipt,
    validateBrowserRtProductWedgeReceipt,
    BROWSERRT_PUBLIC_API_EXPORTS,
    validateBlockStoreLaneAdapterSnapshot
  } = api;
  const rt = await boot({ telemetry: 'public-api-product-wedge', proof: REVISION, publicApiProductWedge: true });
  const channel = rt.core.channel({ label: 'product-wedge-channel', capacity: 1, overflow: 'fail' });
  await channel.send({ job: 'current-work' });
  let overflowDisposition = 'not-observed';
  try { await channel.send({ job: 'overflow' }); } catch { overflowDisposition = 'failed-full'; }
  const received = await channel.receive();

  const agent = await rt.core.spawnAgent({ name: 'product-wedge-agent' });
  const ping = await agent.call('ping', { source: 'product-wedge' });
  const buffer = new ArrayBuffer(16);
  new Uint32Array(buffer).set([5, 7, 11, 13]);
  const transfer = rt.core.transferObject(buffer, { id: 'transfer:product-wedge-sum', label: 'product-wedge-sum' });
  const sum = await agent.call('sum-u32', { ref: transfer.ref, buffer: transfer.buffer }, { transfer: transfer.transferList, lane: 'cpu', priority: 'user-visible' });
  const transferDetached = buffer.byteLength === 0 && transfer.buffer.byteLength === 0;
  await agent.terminate('product-wedge-agent-complete');

  const admission = rt.coordination.admissionController({ label: 'product-wedge-admission', lowWatermarkBytes: 0, highWatermarkBytes: 128, hardLimitBytes: 512 });
  const payload = new TextEncoder().encode(JSON.stringify({ project: 'BrowserRT', revision: REVISION, sum: sum.sum, job: received.job }));
  const accepted = admission.tryAdmit({ bytes: payload.byteLength, priority: 'user-visible', label: 'product-wedge-payload' });
  const rejected = admission.tryAdmit({ bytes: 4096, priority: 'background', label: 'product-wedge-too-large' });

  const store = rt.storage.blockStore({ name: 'product-wedge-store', provider: 'product-wedge-memory-provider-v1' });
  const scheduler = rt.coordination.crossLaneScheduler({ label: 'product-wedge-scheduler', lanes: [{ id: 'storage', rank: 50, capacity: 1, quantum: 64, maxQueuedCost: 512 }] });
  const adapter = rt.storage.blockStoreLaneAdapter({ label: 'product-wedge-storage-lane', store, scheduler });
  const put = adapter.schedulePut(payload, { id: 'product-wedge-put', priority: 'user-visible' });
  await adapter.drain({ maxSteps: 4 });
  const putResult = adapter.result('product-wedge-put');
  const verify = adapter.scheduleVerify(putResult.ref, { id: 'product-wedge-verify' });
  const get = adapter.scheduleGet(putResult.ref, { id: 'product-wedge-get' });
  await adapter.drain({ maxSteps: 4 });
  const verifyResult = adapter.result('product-wedge-verify');
  const readBytes = adapter.result('product-wedge-get');
  const expectedDigest = await digestBytesHex(payload);
  const readDigest = await digestBytesHex(readBytes);
  if (accepted.admitted) admission.release(accepted.leaseId, { outcome: 'product-wedge-stored' });
  const adapterValidation = validateBlockStoreLaneAdapterSnapshot(adapter.snapshot());
  const trace = rt.close();
  const traceKinds = trace.map((event) => event.kind);

  const observed = Object.freeze({
    imports: { publicApiOnly: true, importSpecifier, supportedExports: BROWSERRT_PUBLIC_API_EXPORTS.slice() },
    runtime: { revision: REVISION, version: VERSION, revisionMatches: rt.revision === REVISION, versionMatches: rt.version === VERSION },
    channel: { overflowDisposition, receivedCurrentWork: received.job === 'current-work' },
    worker: { pingPong: ping.pong === true, sum: sum.sum, count: sum.count, transferDetached },
    admission: { accepted: accepted.admitted === true, rejectedNoMutation: rejected.admitted === false && rejected.noMutation === true },
    storage: { putAccepted: put.accepted === true, verifyAccepted: verify.accepted === true, getAccepted: get.accepted === true, verifyOk: verifyResult.ok === true, expectedDigest: `sha256:${expectedDigest}`, readDigest: `sha256:${readDigest}`, readDigestMatches: expectedDigest === readDigest, adapterSnapshotValid: adapterValidation.ok === true },
    trace: { count: trace.length, kinds: traceKinds }
  });
  const receipt = createBrowserRtProductWedgeReceipt({ revision: REVISION, version: VERSION, observed, traceKinds, generatedAt, source });
  const validation = validateBrowserRtProductWedgeReceipt(receipt);
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: validation.ok ? 'passed' : 'failed', probe_id: `${REVISION}-public-api-product-wedge`, receipt, validation, nonClaims: receipt.nonClaims });
}

export async function runProductWedgeConsumer(options = {}) {
  return runProductWedgeWithApi(defaultApi, { source: 'examples/product-wedge-consumer.mjs', importSpecifier: '../src/public-api.mjs', ...options });
}

if (typeof process !== 'undefined' && process.argv && import.meta.url === `file://${process.argv[1]}`) {
  console.log(JSON.stringify(await runProductWedgeConsumer(), null, 2));
}
