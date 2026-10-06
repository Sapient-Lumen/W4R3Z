import * as defaultApi from '../src/public-api.mjs';

export const BROWSERRT_GOLDEN_WORKLOAD_FORMAT = 'browserrt.golden-workload-receipt.v1';

const REQUIRED_PROOF = Object.freeze([
  'namespacedFacadeUsed',
  'boundedChannelBackpressure',
  'admissionRejectNoMutation',
  'workerTransformedChunks',
  'storageLaneCommittedChunks',
  'abortCancelledBeforeCommit',
  'quarantineReviewedAndCleared',
  'recoveryWriteAfterAbort',
  'adapterSnapshotValid',
  'traceClosed'
]);

const encoder = new TextEncoder();

function encodeJson(value) { return encoder.encode(JSON.stringify(value)); }

function bool(value) { return value === true; }

function shortError(error) {
  return Object.freeze({
    name: error?.name || 'Error',
    message: error?.message || String(error),
    code: error?.code ?? error?.storageDisposition ?? null,
    storageDisposition: error?.storageDisposition ?? error?.code ?? null
  });
}

function abortableDelay(ms, signal = null) {
  if (signal?.aborted) return Promise.reject(signal.reason || new Error('aborted'));
  return new Promise((resolve, reject) => {
    let settled = false;
    const cleanup = () => {
      if (signal && typeof signal.removeEventListener === 'function') signal.removeEventListener('abort', onAbort);
    };
    const timer = setTimeout(() => {
      settled = true;
      cleanup();
      resolve();
    }, ms);
    const onAbort = () => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      cleanup();
      reject(signal?.reason || new Error('aborted'));
    };
    if (signal && typeof signal.addEventListener === 'function') signal.addEventListener('abort', onAbort, { once: true });
  });
}

function proofFromObserved(observed = {}) {
  return Object.freeze({
    namespacedFacadeUsed: observed.namespace?.core === true && observed.namespace?.storage === true && observed.namespace?.coordination === true,
    boundedChannelBackpressure: observed.channel?.overflowDisposition === 'failed-full' && observed.channel?.receivedCount === 2,
    admissionRejectNoMutation: observed.admission?.accepted === true && observed.admission?.rejectedNoMutation === true && observed.admission?.released === true,
    workerTransformedChunks: observed.worker?.chunkCount === 2 && observed.worker?.allSumsMatch === true && observed.worker?.allTransfersDetached === true,
    storageLaneCommittedChunks: observed.storage?.putCount === 2 && observed.storage?.allReadsMatch === true && observed.storage?.allVerifiesOk === true,
    abortCancelledBeforeCommit: observed.abort?.timeoutCode === 'BRT_STORAGE_OPERATION_TIMEOUT' && observed.abort?.lateFailureCode === 'BRT_STORAGE_OPERATION_TIMEOUT_ABORT' && observed.abort?.abortedWritePresent === false,
    quarantineReviewedAndCleared: observed.abort?.reviewCreated === true && observed.abort?.clearOk === true && observed.abort?.clearanceReceiptValid === true && observed.abort?.postClearQuarantineCount === 0,
    recoveryWriteAfterAbort: observed.recovery?.putOk === true && observed.recovery?.verifyOk === true && observed.recovery?.readDigestMatches === true && observed.recovery?.laneHealthy === true,
    adapterSnapshotValid: observed.storage?.adapterSnapshotValid === true,
    traceClosed: Array.isArray(observed.trace?.kinds) && observed.trace.kinds.includes('runtime:boot') && observed.trace.kinds.includes('runtime:close')
  });
}

export function createGoldenWorkloadReceipt({ revision, version, observed, generatedAt = new Date().toISOString(), source = 'golden-workload-consumer' } = {}) {
  const proof = proofFromObserved(observed);
  const missing = REQUIRED_PROOF.filter((key) => !bool(proof[key]));
  return Object.freeze({
    project: 'BrowserRT',
    revision,
    version,
    schema: 1,
    format: BROWSERRT_GOLDEN_WORKLOAD_FORMAT,
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    purpose: 'Consumer-facing golden workload through the product namespaces: bounded queue admission, Worker transform, storage-lane commit/read/verify, timeout-driven provider abort with no commit, reviewed quarantine clearance, and recovery write after abort.',
    workload: Object.freeze({ name: 'bounded-local-transform-and-store', chunkCount: observed?.worker?.chunkCount ?? 0, storageProvider: observed?.storage?.provider ?? null }),
    proof,
    missing,
    observed,
    nonClaims: Object.freeze([
      'Golden workload uses the package public API and a memory-backed block store; browser OPFS, Web Locks, quota, eviction, fsync, tab close, process kill, and cross-browser claims remain in explicit browser tasks.',
      'Timeout cancellation is cooperative and proves the provider honored BrowserRT\'s abort signal before commit in this workload, not that every browser filesystem operation is preemptible.',
      'The receipt reports trace event kinds and digests only; it is not a telemetry, privacy, anonymization, or production benchmark claim.'
    ])
  });
}

export function validateGoldenWorkloadReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object') errors.push('receipt must be an object');
  if (receipt?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (receipt?.format !== BROWSERRT_GOLDEN_WORKLOAD_FORMAT) errors.push(`format must be ${BROWSERRT_GOLDEN_WORKLOAD_FORMAT}`);
  if (receipt?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(receipt?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(receipt?.version || ''))) errors.push('version must be x.y.z');
  const proof = receipt?.proof && typeof receipt.proof === 'object' ? receipt.proof : {};
  for (const key of REQUIRED_PROOF) if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  if (!Array.isArray(receipt?.nonClaims) || !receipt.nonClaims.some((claim) => /OPFS/.test(claim) && /cross-browser/.test(claim))) errors.push('OPFS/cross-browser non-claim must be visible');
  if (receipt?.status !== (errors.length ? 'failed' : 'passed')) errors.push('status does not match validation result');
  return Object.freeze({ ok: errors.length === 0, errors, requiredProof: REQUIRED_PROOF.slice(), proof });
}

export async function runGoldenWorkloadWithApi(api = defaultApi, { generatedAt = 'deterministic-golden-workload', source = 'examples/golden-workload-consumer.mjs', importSpecifier = '../src/public-api.mjs' } = {}) {
  const { REVISION, VERSION, boot, digestBytesHex, validateBlockStoreLaneAdapterSnapshot } = api;
  const rt = await boot({ telemetry: 'golden-workload', goldenWorkload: true, proof: REVISION });
  const namespace = Object.freeze({
    core: typeof rt.core?.channel === 'function' && typeof rt.core?.spawnAgent === 'function',
    storage: typeof rt.storage?.blockStore === 'function' && typeof rt.storage?.blockStoreLaneAdapter === 'function',
    coordination: typeof rt.coordination?.admissionController === 'function' && typeof rt.coordination?.crossLaneScheduler === 'function',
    diagnostics: typeof rt.diagnostics?.kernelKitTraceExport === 'function',
    experimental: typeof rt.experimental?.providerResilienceModelOracle === 'function'
  });

  const channel = rt.core.channel({ label: 'golden-workload-channel', capacity: 2, overflow: 'fail' });
  await channel.send({ id: 'chunk-0' });
  await channel.send({ id: 'chunk-1' });
  let overflowDisposition = 'not-observed';
  try { await channel.send({ id: 'chunk-overflow' }); } catch { overflowDisposition = 'failed-full'; }
  const queuedJobs = [await channel.receive(), await channel.receive()];

  const agent = await rt.core.spawnAgent({ name: 'golden-workload-agent' });
  const chunks = [
    { id: queuedJobs[0].id, values: [3, 5, 8, 13] },
    { id: queuedJobs[1].id, values: [21, 34, 55, 89] }
  ];
  const transformed = [];
  let allTransfersDetached = true;
  for (const chunk of chunks) {
    const array = new Uint32Array(chunk.values);
    const originalBuffer = array.buffer.slice(0);
    const transfer = rt.core.transferObject(originalBuffer, { id: `golden-workload-transfer:${chunk.id}`, label: chunk.id });
    const sum = await agent.call('sum-u32', { ref: transfer.ref, buffer: transfer.buffer }, { transfer: transfer.transferList, lane: 'cpu', priority: 'user-visible' });
    allTransfersDetached = allTransfersDetached && originalBuffer.byteLength === 0 && transfer.buffer.byteLength === 0;
    transformed.push(Object.freeze({ id: chunk.id, values: chunk.values, expectedSum: chunk.values.reduce((a, b) => a + b, 0), sum: sum.sum, count: sum.count, bytes: sum.bytes }));
  }
  await agent.terminate('golden-workload-complete');

  const admission = rt.coordination.admissionController({ label: 'golden-workload-admission', lowWatermarkBytes: 0, highWatermarkBytes: 96, hardLimitBytes: 192 });
  const admitted = admission.tryAdmit({ bytes: 64, priority: 'user-visible', label: 'golden-workload-batch' });
  const rejected = admission.tryAdmit({ bytes: 4096, priority: 'background', label: 'golden-workload-over-budget' });

  const store = rt.storage.blockStore({ name: 'golden-workload-store', provider: 'memory-block-golden-workload-provider-v1' });
  const scheduler = rt.coordination.crossLaneScheduler({
    label: 'golden-workload-scheduler',
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
      { id: 'maintenance', rank: 20, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const adapter = rt.storage.blockStoreLaneAdapter({ label: 'golden-workload-storage-lane', store, scheduler, abortProviderOnOperationTimeout: true });

  const payloads = transformed.map((row) => encodeJson({ project: 'BrowserRT', revision: REVISION, workload: 'golden', chunk: row.id, sum: row.sum, count: row.count }));
  for (const [index, payload] of payloads.entries()) {
    adapter.schedulePut(payload, { id: `golden-put-${index}`, priority: 'user-visible', fields: { workload: 'golden', chunkIndex: index } });
  }
  await adapter.drain({ maxSteps: 8 });
  const putResults = payloads.map((_, index) => adapter.result(`golden-put-${index}`));
  for (const [index, putResult] of putResults.entries()) {
    adapter.scheduleVerify(putResult.ref, { id: `golden-verify-${index}` });
    adapter.scheduleGet(putResult.ref, { id: `golden-get-${index}` });
  }
  await adapter.drain({ maxSteps: 8 });
  const readChecks = [];
  for (const [index, payload] of payloads.entries()) {
    const readBytes = adapter.result(`golden-get-${index}`);
    const expectedDigest = await digestBytesHex(payload);
    const readDigest = await digestBytesHex(readBytes);
    const verifyResult = adapter.result(`golden-verify-${index}`);
    readChecks.push(Object.freeze({ index, verifyOk: verifyResult?.ok === true, expectedDigest: `sha256:${expectedDigest}`, readDigest: `sha256:${readDigest}`, readDigestMatches: expectedDigest === readDigest }));
  }

  const abortedPayload = encodeJson({ project: 'BrowserRT', revision: REVISION, workload: 'golden', chunk: 'aborted-before-commit' });
  const abortedDigest = `sha256:${await digestBytesHex(abortedPayload)}`;
  adapter.schedule('put', async (context = {}) => {
    await abortableDelay(50, context.abortSignal || context.signal || null);
    if (context.timedOut === true || (typeof context.isTimedOut === 'function' && context.isTimedOut())) throw new Error('golden workload refused late commit after timeout');
    return store.put(abortedPayload, { label: 'golden-aborted-put-should-not-commit' });
  }, { id: 'golden-aborted-put', priority: 'user-visible', cost: 1, operationTimeoutMs: 1, abortProviderOnOperationTimeout: true, metadata: { workload: 'golden', abortBoundary: true } });
  const timeoutDrain = await adapter.drain({ maxSteps: 1 });
  await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const failedTimedOut = adapter.failedTimedOutOperations('storage');
  const abortedWritePresent = await store.has(abortedDigest);
  const timeoutError = timeoutDrain.results.find((row) => row.opId === 'golden-aborted-put')?.error || null;
  const review = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', reviewer: 'golden-workload', reason: 'golden-workload-reviewed-provider-abort', category: 'failed', all: true, allowLaneWide: true });
  const clearFailed = adapter.clearFailedTimedOutOperations({ lane: 'storage', reviewManifest: review, reason: 'golden-workload-cleared-provider-abort' });
  const clearanceReceipt = clearFailed?.ok ? adapter.createTimedOutOperationQuarantineClearanceReceipt(clearFailed, { reviewer: 'golden-workload', label: 'golden-workload-provider-abort-clearance' }) : null;
  const postClearQuarantine = adapter.timedOutOperationQuarantine('storage');
  const recoveryHealth = adapter.markHealthy('storage', 'golden-workload-recovered-after-reviewed-abort');

  const recoveryPayload = encodeJson({ project: 'BrowserRT', revision: REVISION, workload: 'golden', recoveredAfterAbort: true });
  adapter.schedulePut(recoveryPayload, { id: 'golden-recovery-put', priority: 'user-visible', fields: { workload: 'golden', recovery: true } });
  await adapter.drain({ maxSteps: 4 });
  const recoveryPut = adapter.result('golden-recovery-put');
  adapter.scheduleVerify(recoveryPut.ref, { id: 'golden-recovery-verify' });
  adapter.scheduleGet(recoveryPut.ref, { id: 'golden-recovery-get' });
  await adapter.drain({ maxSteps: 4 });
  const recoveryRead = adapter.result('golden-recovery-get');
  const recoveryExpectedDigest = await digestBytesHex(recoveryPayload);
  const recoveryReadDigest = await digestBytesHex(recoveryRead);
  const recoveryVerify = adapter.result('golden-recovery-verify');

  const release = admitted.admitted ? admission.release(admitted.leaseId, { outcome: 'golden-workload-complete' }) : Object.freeze({ released: false });
  const adapterValidation = validateBlockStoreLaneAdapterSnapshot(adapter.snapshot(), { requireStore: true });
  const trace = rt.close();
  const traceKinds = trace.map((event) => event.kind);

  const observed = Object.freeze({
    imports: { publicApiOnly: true, importSpecifier },
    runtime: { revision: REVISION, version: VERSION, revisionMatches: rt.revision === REVISION, versionMatches: rt.version === VERSION },
    namespace,
    channel: { overflowDisposition, receivedCount: queuedJobs.length, receivedIds: queuedJobs.map((job) => job.id) },
    admission: { accepted: admitted.admitted === true, rejectedNoMutation: rejected.admitted === false && rejected.noMutation === true, released: release.released === true, inFlightBytesAfterRelease: release.inFlightBytes ?? admission.snapshot().inFlightBytes },
    worker: { chunkCount: transformed.length, allSumsMatch: transformed.every((row) => row.sum === row.expectedSum), allTransfersDetached, rows: transformed.map((row) => ({ id: row.id, sum: row.sum, count: row.count, bytes: row.bytes })) },
    storage: { provider: store.provider, putCount: putResults.filter(Boolean).length, allVerifiesOk: readChecks.every((row) => row.verifyOk), allReadsMatch: readChecks.every((row) => row.readDigestMatches), readChecks, adapterSnapshotValid: adapterValidation.ok === true, adapterValidation },
    abort: { scheduled: true, timeoutCode: timeoutError?.code ?? timeoutError?.storageDisposition ?? null, lateFailureCode: failedTimedOut[0]?.error?.code ?? failedTimedOut[0]?.error?.storageDisposition ?? null, failedTimedOutCount: failedTimedOut.length, abortedDigest, abortedWritePresent, reviewCreated: Boolean(review?.reviewFingerprint), clearOk: clearFailed?.ok === true, clearanceReceiptValid: Boolean(clearanceReceipt?.receiptFingerprint), postClearQuarantineCount: postClearQuarantine.totalCount },
    recovery: { laneHealthy: recoveryHealth?.healthy === true, putOk: Boolean(recoveryPut?.ref), verifyOk: recoveryVerify?.ok === true, expectedDigest: `sha256:${recoveryExpectedDigest}`, readDigest: `sha256:${recoveryReadDigest}`, readDigestMatches: recoveryExpectedDigest === recoveryReadDigest },
    trace: { count: trace.length, kinds: traceKinds }
  });
  const receipt = createGoldenWorkloadReceipt({ revision: REVISION, version: VERSION, observed, generatedAt, source });
  const validation = validateGoldenWorkloadReceipt(receipt);
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: validation.ok ? 'passed' : 'failed', probe_id: `${REVISION}-golden-workload`, receipt, validation, nonClaims: receipt.nonClaims });
}

export async function runGoldenWorkloadConsumer(options = {}) {
  return runGoldenWorkloadWithApi(defaultApi, { source: 'examples/golden-workload-consumer.mjs', importSpecifier: '../src/public-api.mjs', ...options });
}

if (typeof process !== 'undefined' && process.argv && import.meta.url === `file://${process.argv[1]}`) {
  console.log(JSON.stringify(await runGoldenWorkloadConsumer(), null, 2));
}
