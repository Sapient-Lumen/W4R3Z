import assert from 'node:assert/strict';
import {
  BoundedChannel,
  LANES,
  PRIORITIES,
  REVISION,
  VERSION,
  availableCapabilityTierNames,
  boot,
  capabilityTierNames,
  createEnvelope,
  createBlockObjectRef,
  createMemoryBlockStore,
  createOpfsAsyncBlockStore,
  createWebLockCoordinator,
  createWebLockGuardedBlockStore,
  createJournaledMemoryBlockStore,
  createSharedFrameRing,
  createSpillFrameMailbox,
  createPersistedSpillMailbox,
  recoverPersistedSpillMailbox,
  createWatermarkAdmissionController,
  createAdaptiveConcurrencyController,
  createPriorityFairScheduler,
  createCrossLaneScheduler,
  createObjectRef,
  createOpfsObjectRef,
  createOpfsSyncObjectRef,
  createTransferObject,
  createTransferObjectRef,
  detectCapabilities,
  createRetryBudgetAdmissionController,
  createCircuitBreakerBulkheadController,
  validateCircuitBreakerBulkheadSnapshot,
  createProviderResilienceHistoryRunner,
  validateProviderResilienceHistorySnapshot,
  createProviderResilienceModelOracle,
  validateProviderResilienceModelSnapshot,
  createStorageLaneAdmissionHistoryRunner,
  validateStorageLaneAdmissionHistorySnapshot,
  createStorageLaneAdmissionHistoryModelOracle,
  compareStorageLaneAdmissionHistoryToModel,
  validateStorageLaneAdmissionHistoryModelSnapshot,
  spawnWorkerAgent,
  createKernelKitDemoPlan,
  validateKernelKitDemoReport,
  KERNEL_KIT_DEMO_NON_CLAIMS
} from '../src/browserrt.mjs';

assert.equal(REVISION, 'rev0100');
assert.equal(VERSION, '0.0.100');
assert.ok(LANES.includes('storage'));
assert.ok(LANES.includes('gpu'));
assert.ok(LANES.includes('plugin'));
assert.ok(PRIORITIES.includes('user-blocking'));
assert.ok(capabilityTierNames().includes('mesh'));

const caps = detectCapabilities();
assert.equal(typeof caps.sharedArrayBuffer, 'boolean');
assert.equal(typeof caps.transferableArrayBuffer, 'boolean');
assert.equal(typeof caps.opfs, 'boolean');
assert.equal(typeof caps.webLocks, 'boolean');
assert.equal(typeof caps.measureMemory, 'boolean');
assert.ok(availableCapabilityTierNames(caps).includes('basic'));

const ref = createObjectRef('opfs', { id: 'opfs:demo-block', bytes: 128, block: 'demo-block' });
assert.deepEqual({ kind: ref.kind, id: ref.id, bytes: ref.bytes, block: ref.block }, { kind: 'opfs', id: 'opfs:demo-block', bytes: 128, block: 'demo-block' });
const opfsRef = createOpfsObjectRef('browserrt/rev0098/demo.bin', { bytes: 64 });
assert.equal(opfsRef.kind, 'opfs');
assert.equal(opfsRef.backend, 'opfs-async');
assert.equal(opfsRef.path, 'browserrt/rev0098/demo.bin');
const opfsSyncRef = createOpfsSyncObjectRef('browserrt/rev0098/sync-demo.bin', { bytes: 65 });
const opfsBlockStore = createOpfsAsyncBlockStore({ name: 'smoke-opfs-block-store', prefix: 'browserrt/rev0098/smoke-blocks' });
assert.equal(opfsBlockStore.provider, 'opfs-async-block-store-v0');
assert.equal(opfsBlockStore.snapshot().available, caps.opfs);
assert.equal(typeof createWebLockCoordinator, 'function');
assert.equal(typeof createWebLockGuardedBlockStore, 'function');
assert.equal(opfsSyncRef.kind, 'opfs');
assert.equal(opfsSyncRef.backend, 'opfs-sync-access-handle');
assert.equal(opfsSyncRef.ownership, 'origin-private-worker-exclusive');
assert.throws(() => createObjectRef('bogus', { bytes: 1 }), /Unsupported object ref kind/);
assert.throws(() => createObjectRef('inline', { bytes: -1 }), /non-negative/);
const blockRef = createBlockObjectRef('0'.repeat(64), { bytes: 0, label: 'empty-block' });
assert.equal(blockRef.kind, 'block');
assert.equal(blockRef.digest, `sha256:${'0'.repeat(64)}`);
assert.throws(() => createBlockObjectRef('bad-hash'), /sha256/);

const transferRef = createTransferObjectRef(new ArrayBuffer(8), { id: 'transfer:ref-only' });
assert.equal(transferRef.kind, 'transfer');
assert.equal(transferRef.bytes, 8);
const env = createEnvelope('demo-op', { lane: 'cpu', priority: 'user-visible', payloadRef: transferRef });
assert.equal(env.magic, 'BRT1');
assert.equal(env.payloadRef.id, 'transfer:ref-only');

const rt = await boot({ telemetry: 'always', proof: REVISION, blockStoreProbe: true, priorityFairnessProbe: true, persistedSpillRecoveryProbe: true, persistedSpillCompactionProbe: true, crossLaneSchedulerProbe: true, storageLaneRetryPolicyProof: true, storageLaneRetryBudgetProof: true });
assert.equal(rt.revision, REVISION);
assert.equal(rt.report.executableProofs.workerAgent, true);
assert.equal(rt.report.executableProofs.storageLaneRetryPolicyProof, true);

const demoPlan = createKernelKitDemoPlan({ revision: REVISION });
assert.equal(demoPlan.posture, 'usefulness-wedge-not-production-runtime');
const demoValidation = validateKernelKitDemoReport({ project: 'BrowserRT', revision: REVISION, schema: 1, demo_id: 'kernel-kit-smoke', components: { runtimeBoot: true, workerAgent: true, transferObjectRef: true, admissionGovernor: true, opfsStorageLane: true, traceReport: true }, worker: { sum: 136, detachedAfter: true }, admission: { lowPriorityRejected: true, criticalBypass: true, finalLeaseCount: 0 }, storage: { readbackDigest: 'abc', storedRef: { hash: 'abc' }, verifyOk: true, deleteOk: true, hasAfterDelete: false }, traceKinds: ['runtime:boot','channel:create','channel:send','channel:receive','agent:spawn','agent:result','object:transfer-ref','admission:reject','storage:opfs-block-put','storage-lane:dispatch','block-store-lane:op-complete','storage:opfs-block-get','storage:opfs-block-delete','runtime:close'], nonClaims: KERNEL_KIT_DEMO_NON_CLAIMS.slice() });
assert.equal(demoValidation.ok, true);

const smokeResilience = createCircuitBreakerBulkheadController({ label: 'smoke-circuit-breaker-bulkhead', maxConcurrent: 1, slidingWindowSize: 2, minimumCalls: 2, failureRateThreshold: 50, openDurationTicks: 1, halfOpenMaxCalls: 1, trace: rt.trace });
const smokeResilienceLeaseA = smokeResilience.tryAcquire({ opId: 'smoke-resilience-a' });
assert.equal(smokeResilienceLeaseA.accepted, true);
const smokeResilienceReject = smokeResilience.tryAcquire({ opId: 'smoke-resilience-b' });
assert.equal(smokeResilienceReject.reason, 'bulkhead-full');
smokeResilience.release(smokeResilienceLeaseA, { ok: false, durationTicks: 1 });
const smokeResilienceLeaseB = smokeResilience.tryAcquire({ opId: 'smoke-resilience-c' });
smokeResilience.release(smokeResilienceLeaseB, { ok: true, durationTicks: 1 });
assert.equal(smokeResilience.snapshot().state, 'open');
smokeResilience.advanceTicks(1);
const smokeProbe = smokeResilience.tryAcquire({ opId: 'smoke-resilience-probe' });
smokeResilience.release(smokeProbe, { ok: true, durationTicks: 1 });
assert.equal(smokeResilience.snapshot().state, 'closed');
assert.equal(validateCircuitBreakerBulkheadSnapshot(smokeResilience.snapshot()).ok, true);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'resilience:state-transition'));

const smokeRuntimeResilience = rt.circuitBreakerBulkheadController({ label: 'smoke-runtime-resilience', maxConcurrent: 1, slidingWindowSize: 2, minimumCalls: 2 });
assert.equal(validateCircuitBreakerBulkheadSnapshot(smokeRuntimeResilience.snapshot()).ok, true);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:circuit-breaker-bulkhead-controller-ref'));

const smokeRetryBudget = createRetryBudgetAdmissionController({ label: 'smoke-retry-budget', maxRetryCredits: 1, initialRetryCredits: 1, trace: rt.trace });
const smokeRetryLease = smokeRetryBudget.tryAcquireRetry({ opId: 'smoke-budget', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
assert.equal(smokeRetryLease.accepted, true);
assert.equal(smokeRetryBudget.releaseRetry(smokeRetryLease.leaseId, { ok: true }).released, true);
assert.equal(smokeRetryBudget.snapshot().activeRetries, 0);
const smokeProviderRunner = rt.providerResilienceHistoryRunner({ label: 'smoke-provider-resilience', breakerOptions: { maxConcurrent: 1, slidingWindowSize: 2, minimumCalls: 2 }, retryBudgetOptions: { initialRetryCredits: 1, maxRetryCredits: 2 } });
assert.equal(validateProviderResilienceHistorySnapshot(smokeProviderRunner.snapshot()).ok, true);
assert.equal(typeof createProviderResilienceHistoryRunner, 'function');
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:provider-resilience-history-runner-ref'));
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'runtime:boot'));

const admissionModel = createStorageLaneAdmissionHistoryModelOracle({ label: 'smoke-admission-model', highWatermarkBytes: 8, hardLimitBytes: 16, trace: rt.trace });
const modelGate = admissionModel.predictAdmission({ bytes: 4, priority: 'user-visible', label: 'smoke-model' });
assert.equal(modelGate.admitted, true);
assert.equal(validateStorageLaneAdmissionHistoryModelSnapshot(admissionModel.snapshot()).ok, true);
assert.equal(typeof compareStorageLaneAdmissionHistoryToModel, 'function');
const runtimeAdmissionModel = rt.storageLaneAdmissionHistoryModelOracle({ label: 'smoke-runtime-admission-model', highWatermarkBytes: 8, hardLimitBytes: 16 });
assert.equal(validateStorageLaneAdmissionHistoryModelSnapshot(runtimeAdmissionModel.snapshot()).ok, true);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:storage-lane-admission-history-model-oracle-ref'));


const directStore = createMemoryBlockStore({ name: 'smoke-direct-block-store', trace: rt.trace });
const runtimeStore = rt.blockStore({ name: 'smoke-runtime-block-store' });
const smokeFakeLocks = { request: async (name, options, callback) => callback({ name, mode: options?.mode || 'exclusive' }), query: async () => ({ held: [], pending: [] }) };
const runtimeGuardedStore = rt.opfsWebLockGuardedBlockStore({ store: rt.blockStore({ name: 'smoke-runtime-guarded-block-store' }), locks: smokeFakeLocks, lockName: 'smoke-runtime-guard', label: 'smoke-runtime-guard' });
const guardedPut = await runtimeGuardedStore.put('hello guarded store', { label: 'smoke-guarded' });
assert.equal((await runtimeGuardedStore.verify(guardedPut.ref)).ok, true);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'coord:web-lock-acquired'));
const blockPut = await runtimeStore.put('hello block store', { label: 'smoke' });
const blockDuplicate = await runtimeStore.put(new TextEncoder().encode('hello block store'), { label: 'smoke-duplicate' });
assert.equal(blockPut.digest, blockDuplicate.digest);
assert.equal(blockDuplicate.duplicate, true);
assert.equal(await runtimeStore.has(blockPut.ref), true);
assert.equal(new TextDecoder().decode(await runtimeStore.get(blockPut.digest)), 'hello block store');
assert.equal((await runtimeStore.verify(blockPut.ref)).ok, true);
assert.equal(runtimeStore.snapshot().blockCount, 1);
const directBlockPut = await directStore.put(new Uint8Array([9, 8, 7]), { label: 'direct' });
assert.equal((await directStore.verify(directBlockPut.ref)).ok, true);
assert.equal(rt.trace.count('storage:block-put') >= 2, true);

const journalStore = createJournaledMemoryBlockStore({ name: 'smoke-journal-store', trace: rt.trace });
const journalPut = await journalStore.put('journal smoke', { label: 'journal-smoke' });
const journalCheckpoint = await journalStore.checkpoint({ label: 'smoke-checkpoint' });
const journalRecovered = await rt.recoverJournaledBlockStore({ manifest: journalCheckpoint, journal: journalStore.exportJournal(), name: 'smoke-journal-recovered' });
assert.equal(new TextDecoder().decode(await journalRecovered.store.get(journalPut.ref)), 'journal smoke');
assert.equal(journalRecovered.recovery.appliedJournalRecords, 0);
assert.equal(rt.trace.count('storage:manifest-checkpoint') >= 1, true);


const frameRing = createSharedFrameRing({ capacityBytes: 64, label: 'smoke-frame-ring', trace: rt.trace });
assert.equal(frameRing.tryPushFrame(new Uint8Array([1, 2, 3]), { seq: 1 }), true);
const framePop = frameRing.popFrame();
assert.equal(framePop.done, false);
assert.equal(framePop.frame.seq, 1);
assert.deepEqual(Array.from(framePop.frame.payload), [1, 2, 3]);
frameRing.close();
assert.equal(frameRing.snapshot().closed, true);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'ipc:sab-frame-ring-push'));

const spillProvider = createMemoryBlockStore({ name: 'smoke-spill-provider', trace: rt.trace });
const spillMailbox = createSpillFrameMailbox({ label: 'smoke-spill-mailbox', provider: spillProvider, memoryCapacityBytes: 4, trace: rt.trace });
const spillMemory = await spillMailbox.enqueue(new Uint8Array([1, 2, 3, 4]), { seq: 1 });
const spillCold = await spillMailbox.enqueue(new Uint8Array([5, 6, 7, 8, 9]), { seq: 2 });
assert.equal(spillMemory.disposition, 'memory');
assert.equal(spillCold.disposition, 'spilled');
const spillFirst = await spillMailbox.dequeue({ consumerId: 'smoke-consumer' });
assert.equal(spillFirst.seq, 1);
await spillMailbox.ack(spillFirst.pendingId);
const spillSecond = await spillMailbox.dequeue({ consumerId: 'smoke-consumer' });
assert.equal(spillSecond.seq, 2);
await spillMailbox.ack(spillSecond.pendingId);
assert.equal(spillMailbox.snapshot().providerSnapshot.blockCount, 0);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'mailbox:spill-write'));


const persistedProvider = createJournaledMemoryBlockStore({ name: 'smoke-persisted-spill-provider', trace: rt.trace });
const persistedMailbox = createPersistedSpillMailbox({ label: 'smoke-persisted-spill', provider: persistedProvider, trace: rt.trace, maxFrameBytes: 64 });
await persistedMailbox.enqueue(new Uint8Array([10, 11, 12]), { label: 'persisted-a' });
await persistedMailbox.enqueue(new Uint8Array([13, 14, 15, 16]), { label: 'persisted-b' });
const persistedDelivery = await persistedMailbox.dequeue({ consumerId: 'smoke-persisted-consumer' });
assert.equal(persistedDelivery.seq, 1);
await persistedMailbox.ack(persistedDelivery.pendingId);
const persistedCheckpoint = await persistedMailbox.checkpoint({ label: 'smoke-persisted-checkpoint' });
const persistedRecovered = await recoverPersistedSpillMailbox({ manifest: persistedCheckpoint, journal: persistedMailbox.exportJournal(), provider: persistedProvider, trace: rt.trace, label: 'smoke-persisted-recovered' });
assert.deepEqual(persistedRecovered.mailbox.snapshot().queueSeqs, [2]);
assert.equal((await persistedRecovered.mailbox.dequeue({ consumerId: 'smoke-recovered-consumer' })).seq, 2);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'mailbox:persisted-recover'));


const admission = createWatermarkAdmissionController({ label: 'smoke-admission', lowWatermarkBytes: 4, highWatermarkBytes: 8, hardLimitBytes: 12, trace: rt.trace });
const admittedA = admission.tryAdmit({ bytes: 4, priority: 'background', label: 'a' });
const admittedB = admission.tryAdmit({ bytes: 4, priority: 'background', label: 'b' });
const rejectedLow = admission.tryAdmit({ bytes: 1, priority: 'background', label: 'c' });
assert.equal(admittedA.admitted, true);
assert.equal(admittedB.admitted, true);
assert.equal(rejectedLow.disposition, 'rejected-watermark');
admission.release(admittedA.leaseId, { outcome: 'smoke' });
admission.release(admittedB.leaseId, { outcome: 'smoke' });
assert.equal(admission.snapshot().congested, false);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'admission:high-watermark'));


const adaptive = createAdaptiveConcurrencyController({ label: 'smoke-adaptive', initialLimit: 2, minLimit: 1, maxLimit: 5, windowSize: 2, targetRttMs: 30, overloadRttMs: 80, trace: rt.trace });
const adaptiveA = adaptive.tryAcquire({ priority: 'background', label: 'a' });
const adaptiveB = adaptive.tryAcquire({ priority: 'background', label: 'b' });
const adaptiveReject = adaptive.tryAcquire({ priority: 'background', label: 'reject' });
assert.equal(adaptiveA.admitted, true);
assert.equal(adaptiveB.admitted, true);
assert.equal(adaptiveReject.disposition, 'rejected-limit');
adaptive.release(adaptiveA.leaseId, { latencyMs: 20, outcome: 'complete' });
adaptive.release(adaptiveB.leaseId, { latencyMs: 22, outcome: 'complete' });
const adaptiveWindow = adaptive.observeWindow();
assert.equal(adaptiveWindow.decision, 'increase');
assert.equal(adaptive.snapshot().limit, 3);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'adaptive:limit-increase'));



const fair = createPriorityFairScheduler({ label: 'smoke-priority-fair', maxQueuedCost: 100, maxFlowQueuedCost: 40, maxTaskCost: 20, trace: rt.trace });
fair.enqueue({ id: 'fair-noisy-0', flowId: 'noisy', priority: 'background', cost: 7 });
fair.enqueue({ id: 'fair-peer-0', flowId: 'peer', priority: 'background', cost: 3 });
fair.enqueue({ id: 'fair-critical-0', flowId: 'ui', priority: 'critical', cost: 2 });
const fairDispatch = [fair.dispatchNext().task, fair.dispatchNext().task, fair.dispatchNext().task];
assert.equal(fairDispatch[0].priority, 'critical');
assert.deepEqual(fairDispatch.slice(1).map((task) => task.flowId), ['noisy', 'peer']);
const fairReject = fair.enqueue({ id: 'fair-oversize', flowId: 'ui', priority: 'critical', cost: 21 });
assert.equal(fairReject.disposition, 'rejected-task-cost');
assert.equal(fair.snapshot().queuedCount, 0);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'fair:dispatch'));



const cross = createCrossLaneScheduler({ label: 'smoke-cross-lane', maxQueuedCost: 32, maxTaskCost: 4, lanes: [
  { id: 'interactive', rank: 100, capacity: 1, quantum: 16, maxQueuedCost: 16 },
  { id: 'cpu', rank: 50, capacity: 1, quantum: 16, maxQueuedCost: 16 },
  { id: 'storage', rank: 40, capacity: 1, quantum: 16, maxQueuedCost: 16 }
], trace: rt.trace });
cross.enqueue({ id: 'smoke-interactive', lane: 'interactive', priority: 'critical', cost: 1 });
cross.enqueue({ id: 'smoke-cpu', lane: 'cpu', priority: 'background', cost: 1 });
const crossFirst = cross.dispatchNext();
assert.equal(crossFirst.task.id, 'smoke-interactive');
cross.complete(crossFirst.task.id);
const crossSecond = cross.dispatchNext();
assert.equal(crossSecond.task.id, 'smoke-cpu');
cross.complete(crossSecond.task.id);
assert.equal(cross.snapshot().queuedCount, 0);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'crosslane:dispatch'));

const runtimeCross = rt.crossLaneScheduler({ label: 'smoke-runtime-cross-lane', lanes: [{ id: 'cpu', rank: 1, capacity: 1, quantum: 8, maxQueuedCost: 8 }] });
assert.equal(runtimeCross.snapshot().lanes.length, 1);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:cross-lane-scheduler-ref'));


const runtimeRetry = rt.storageLaneRetryController({ label: 'smoke-storage-lane-retry' });
assert.equal(runtimeRetry.policy.snapshot().maxAttempts, 3);
assert.equal(runtimeRetry.snapshot().delayedCount, 0);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:storage-lane-retry-controller-ref'));

const tracedTransfer = rt.transferObject(new Uint8Array([1, 2, 3, 4]).buffer, { id: 'transfer:object' });
assert.equal(tracedTransfer.ref.bytes, 4);
assert.equal(tracedTransfer.transferList.length, 1);
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:transfer-ref'));
const tracedOpfsRef = rt.opfsObjectRef('browserrt/rev0067/traced.bin', { bytes: 7 });
assert.equal(tracedOpfsRef.backend, 'opfs-async');
const tracedOpfsSyncRef = rt.opfsSyncObjectRef('browserrt/rev0067/traced-sync.bin', { bytes: 8 });
assert.equal(tracedOpfsSyncRef.backend, 'opfs-sync-access-handle');
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:opfs-ref'));
assert.ok(rt.trace.snapshot().some((event) => event.kind === 'object:opfs-sync-ref')); 

const ch = rt.channel({ capacity: 2, overflow: 'drop-newest', label: 'proof-channel' });
const channelReceipts = [await ch.send('a'), await ch.send('b'), await ch.send('c')];
assert.deepEqual(channelReceipts, [
  { disposition: 'queued' },
  { disposition: 'queued' },
  { disposition: 'dropped-newest' }
]);
assert.equal(await ch.receive(), 'a');
assert.equal(await ch.receive(), 'b');

const directChannel = new BoundedChannel({ capacity: 1, overflow: 'drop-oldest', label: 'direct-smoke' });
assert.deepEqual(await directChannel.send('a'), { disposition: 'queued' });
assert.deepEqual(await directChannel.send('b'), { disposition: 'dropped-oldest' });
assert.equal(await directChannel.receive(), 'b');

const waiting = rt.channel({ capacity: 1, overflow: 'wait', label: 'wait-smoke' });
await waiting.send(1);
const sendPromise = waiting.send(2);
assert.equal(waiting.size(), 1);
assert.equal(await waiting.receive(), 1);
assert.deepEqual(await sendPromise, { disposition: 'queued-after-wait' });
assert.equal(await waiting.receive(), 2);
assert.ok(rt.trace.count('channel:create') >= 1);

const agent = await spawnWorkerAgent({ name: 'smoke-agent', trace: rt.trace });
const ping = await agent.call('ping', { value: 'hello' });
assert.equal(ping.pong, true);
assert.equal(ping.protocol, 1);
assert.equal(ping.payload.value, 'hello');
assert.equal(ping.envelope.magic, 'BRT1');

const sumBuffer = new ArrayBuffer(16);
new Uint32Array(sumBuffer).set([1, 2, 3, 4]);
const transferObject = createTransferObject(sumBuffer, { id: 'transfer:sum-u32' });
const sumResult = await agent.call('sum-u32', { buffer: transferObject.buffer, ref: transferObject.ref }, { transfer: transferObject.transferList, priority: 'user-blocking' });
assert.equal(sumResult.sum, 10);
assert.equal(sumResult.count, 4);
assert.equal(sumResult.bytes, 16);
assert.equal(sumResult.ref.id, 'transfer:sum-u32');
assert.equal(transferObject.buffer.byteLength, 0, 'transferred ArrayBuffer should detach in sender');
await agent.terminate('smoke-agent-complete');

const supervisor = rt.supervisor({ name: 'smoke-supervisor', restartLimit: 1 });
await supervisor.start();
const supervisorPingBefore = await supervisor.call('ping', { phase: 'before-crash' });
assert.equal(supervisorPingBefore.pong, true);
await assert.rejects(() => supervisor.call('crash-now', {}, { timeoutMs: 1000 }), /exited|terminated|call timed out/);
const supervisorPingAfter = await supervisor.call('ping', { phase: 'after-crash' });
assert.equal(supervisorPingAfter.pong, true);
assert.equal(supervisor.snapshot().restartCount, 1);
await supervisor.close();

const closeTrace = rt.close();
const eventKinds = rt.trace.kinds();
for (const required of ['runtime:boot', 'runtime:boot-report', 'storage:blockstore-create', 'storage:block-put', 'storage:block-verify', 'mailbox:spill-write', 'mailbox:ack', 'mailbox:persisted-recover', 'adaptive:limit-increase', 'fair:dispatch', 'crosslane:dispatch', 'object:storage-lane-retry-controller-ref', 'resilience:state-transition', 'object:circuit-breaker-bulkhead-controller-ref', 'channel:send', 'channel:receive', 'agent:spawn', 'agent:ready', 'agent:call', 'agent:result', 'agent:exit', 'supervisor:spawn-request', 'supervisor:observed-exit', 'runtime:close']) {
  assert.ok(eventKinds.includes(required), `missing trace event ${required}`);
}
assert.ok(closeTrace.length >= 20);
console.log('BrowserRT smoke test passed');
