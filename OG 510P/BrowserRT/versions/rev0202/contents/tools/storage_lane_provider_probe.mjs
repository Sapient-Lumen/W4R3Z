#!/usr/bin/env node
// BrowserRT rev0027 storage-lane provider integration proof.
// Fake-provider composition only; no OPFS, durability, throughput, or production scheduler claim.

import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  boot,
  createCrossLaneScheduler,
  createMemoryBlockStore,
  createPersistedSpillMailbox,
  createStorageLaneExecutor,
  validateCrossLaneSchedulerSnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-STORAGE-LANE-PROVIDER-PROBE.json`);
function hasKind(trace, kind) { return trace.some((event) => event.kind === kind); }
function summarize(value) {
  if (value == null) return null;
  if (value instanceof Uint8Array) return { kind: 'Uint8Array', bytes: value.byteLength };
  if (typeof value !== 'object') return value;
  const out = {};
  for (const key of ['disposition', 'seq', 'bytes', 'checksum32', 'pendingId', 'consumerId', 'deliveryCount', 'dryRun', 'candidateCount', 'deleted', 'deleteMisses', 'kind', 'version', 'opSeq', 'checksum']) if (key in value) out[key] = value[key];
  if ('payload' in value) out.payload = summarize(value.payload);
  if ('ref' in value) out.ref = value.ref;
  if ('candidates' in value) out.candidates = value.candidates;
  return out;
}

const rt = await boot({ storageLaneProviderProof: true });
const provider = createMemoryBlockStore({ name: 'rev0027-storage-lane-provider-store', provider: 'memory-block-storage-lane-provider-v0', quotaBytes: 4096, trace: rt.trace });
const mailbox = createPersistedSpillMailbox({ label: 'rev0027-storage-lane-mailbox', provider, memoryCapacityBytes: 12, maxFrameBytes: 128, deleteBlockOnAck: false, trace: rt.trace });
const scheduler = createCrossLaneScheduler({
  label: 'rev0027-storage-lane-scheduler',
  maxQueuedCost: 256,
  maxTaskCost: 32,
  lanes: [
    { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 160 },
    { id: 'maintenance', rank: 20, capacity: 1, quantum: 64, maxQueuedCost: 96 },
    { id: 'cpu', rank: 40, capacity: 1, quantum: 64, maxQueuedCost: 96 }
  ],
  trace: rt.trace
});
const executor = createStorageLaneExecutor({ label: 'rev0027-storage-lane-executor', scheduler, mailbox, trace: rt.trace });
const runtimeExecutor = rt.storageLaneExecutor({ label: 'rev0027-runtime-factory-executor' });

const capacityHold = executor.submit('snapshot', {}, { id: 'capacity-hold-snapshot', priority: 'user-visible', cost: 1 });
const capacityWait = executor.submit('snapshot', {}, { id: 'capacity-wait-snapshot', priority: 'user-visible', cost: 1 });
assert.equal(capacityHold.accepted && capacityWait.accepted, true);
const heldDispatch = scheduler.dispatchNext();
assert.equal(heldDispatch.dispatched, true);
const capacityBlockedDispatch = scheduler.dispatchNext();
assert.equal(capacityBlockedDispatch.dispatched, false);
const heldSnapshotRun = await executor.executeDispatched(heldDispatch);
assert.equal(heldSnapshotRun.ok, true);
const waitedSnapshotRun = await executor.executeNext();
assert.equal(waitedSnapshotRun.ok, true);

executor.markUnhealthy('storage', 'fixture-provider-down-before-submit');
const rejectedWhileUnhealthy = executor.submit('enqueue', { payload: 'should-not-enter-mailbox', label: 'reject' }, { id: 'reject-while-unhealthy', priority: 'user-visible', cost: 1 });
assert.equal(rejectedWhileUnhealthy.accepted, false);
assert.equal(rejectedWhileUnhealthy.scheduler.noMutation, true);
executor.markHealthy('storage', 'fixture-provider-restored');

const writeA = executor.submit('enqueue', { payload: 'alpha-one', label: 'alpha' }, { id: 'enqueue-alpha', priority: 'user-visible', cost: 1 });
const writeB = executor.submit('enqueue', { payload: 'bravo-bravo-bravo-bravo', label: 'bravo' }, { id: 'enqueue-bravo', priority: 'user-visible', cost: 2 });
const writeC = executor.submit('enqueue', { payload: 'charlie-charlie-charlie', label: 'charlie' }, { id: 'enqueue-charlie', priority: 'background', cost: 2 });
for (const row of [writeA, writeB, writeC]) assert.equal(row.accepted, true);
const enqueueDrain = await executor.drain({ maxSteps: 4 });
assert.equal(enqueueDrain.results.filter((row) => row.ok).length, 3);
assert.equal(mailbox.snapshot().queueDepth, 3);

const deqA = executor.submit('dequeue', { consumerId: 'consumer-a' }, { id: 'dequeue-alpha', priority: 'user-blocking', cost: 1 });
assert.equal(deqA.accepted, true);
const deliveryA = await executor.executeNext();
assert.equal(deliveryA.ok, true);
assert.ok(deliveryA.result.pendingId);
const ackA = executor.submit('ack', { pendingId: deliveryA.result.pendingId, deleteBlock: false }, { id: 'ack-alpha', priority: 'user-visible', cost: 1, dependsOn: ['dequeue-alpha'] });
const checkpointBlocked = executor.submit('checkpoint', { label: 'after-ack' }, { id: 'checkpoint-after-ack', priority: 'critical', cost: 1, dependsOn: ['ack-alpha'] });
assert.equal(ackA.accepted && checkpointBlocked.accepted, true);
const ackRun = await executor.executeNext();
assert.equal(ackRun.ok, true);
const checkpointRun = await executor.executeNext();
assert.equal(checkpointRun.ok, true);
assert.equal(checkpointRun.result.kind, 'persisted-spill-mailbox-manifest');

const compactDry = executor.submit('compact', { dryRun: true, reason: 'after-ack-dry' }, { id: 'compact-dry', lane: 'maintenance', priority: 'maintenance', cost: 1, dependsOn: ['checkpoint-after-ack'] });
assert.equal(compactDry.accepted, true);
const compactDryRun = await executor.executeNext();
assert.equal(compactDryRun.ok, true);
assert.equal(compactDryRun.result.dryRun, true);
assert.equal(compactDryRun.result.candidateCount, 1);
assert.equal(compactDryRun.result.deleted, 0);
const compactReal = executor.submit('compact', { dryRun: false, reason: 'after-ack-real' }, { id: 'compact-real', lane: 'maintenance', priority: 'maintenance', cost: 1, dependsOn: ['compact-dry'] });
assert.equal(compactReal.accepted, true);
const compactRealRun = await executor.executeNext();
assert.equal(compactRealRun.ok, true);
assert.equal(compactRealRun.result.deleted, 1);
const postRealCompactionMailboxSnapshot = mailbox.snapshot();
const postRealCompactionProviderSnapshot = provider.snapshot();

provider.failNextPutForTest('rev0027 simulated provider write failure');
const failTask = executor.submit('enqueue', { payload: 'delta-fail', label: 'fail' }, { id: 'enqueue-provider-fail', priority: 'critical', cost: 1 });
assert.equal(failTask.accepted, true);
const failed = await executor.executeNext();
assert.equal(failed.ok, false);
assert.equal(scheduler.snapshotLane('storage').healthy, false);
const rejectedDuringUnhealthy = executor.submit('enqueue', { payload: 'echo-held' }, { id: 'enqueue-during-unhealthy', priority: 'user-visible', cost: 1 });
assert.equal(rejectedDuringUnhealthy.accepted, false);
assert.equal(rejectedDuringUnhealthy.scheduler.noMutation, true);
executor.markHealthy('storage', 'fixture-provider-restored-after-fault');
const restored = executor.submit('enqueue', { payload: 'echo-restored', label: 'restored' }, { id: 'enqueue-restored', priority: 'user-visible', cost: 1 });
assert.equal(restored.accepted, true);
const restoredRun = await executor.executeNext();
assert.equal(restoredRun.ok, true);

const finalDeliveries = [];
for (const id of ['bravo', 'charlie', 'restored']) {
  const deq = executor.submit('dequeue', { consumerId: 'final-consumer' }, { id: `dequeue-${id}`, priority: 'background', cost: 1 });
  assert.equal(deq.accepted, true);
  const delivery = await executor.executeNext();
  assert.equal(delivery.ok, true);
  finalDeliveries.push(delivery.result);
  const ack = executor.submit('ack', { pendingId: delivery.result.pendingId, deleteBlock: false }, { id: `ack-${id}`, priority: 'background', cost: 1, dependsOn: [`dequeue-${id}`] });
  assert.equal(ack.accepted, true);
  assert.equal((await executor.executeNext()).ok, true);
}
const finalCompact = executor.submit('compact', { dryRun: false, reason: 'final-cleanup' }, { id: 'compact-final', lane: 'maintenance', priority: 'maintenance', cost: 1 });
assert.equal(finalCompact.accepted, true);
const finalCompactRun = await executor.executeNext();
assert.equal(finalCompactRun.ok, true);
assert.equal(finalCompactRun.result.deleted >= 3, true);

const snapshot = executor.snapshot();
const providerSnapshot = provider.snapshot();
const trace = rt.close();
const traceKinds = [...new Set(trace.map((event) => event.kind))].sort();
const requiredTraceKinds = [
  'storage-lane:create',
  'storage-lane:schedule',
  'storage-lane:reject',
  'storage-lane:dispatch',
  'storage-lane:complete',
  'storage-lane:error',
  'storage-lane:provider-unhealthy',
  'storage-lane:provider-healthy',
  'crosslane:enqueue',
  'crosslane:reject',
  'crosslane:dispatch',
  'crosslane:defer-dependency',
  'crosslane:lane-at-capacity',
  'mailbox:persisted-enqueue',
  'mailbox:persisted-deliver',
  'mailbox:persisted-ack',
  'mailbox:persisted-checkpoint',
  'mailbox:persisted-compact',
  'storage:block-put',
  'storage:block-delete'
];
const observations = {
  storageLaneExecutorCreated: hasKind(trace, 'storage-lane:create'),
  runtimeFactoryIntegration: runtimeExecutor.snapshot().label === 'rev0027-runtime-factory-executor',
  capacityBlockObserved: capacityBlockedDispatch.dispatched === false && hasKind(trace, 'crosslane:lane-at-capacity'),
  healthRejectNoMutation: rejectedWhileUnhealthy.accepted === false && rejectedWhileUnhealthy.scheduler.noMutation === true,
  enqueuesExecutedViaScheduler: enqueueDrain.results.filter((row) => row.ok).length === 3,
  dequeueAndAckExecutedViaScheduler: deliveryA.ok === true && ackRun.ok === true,
  dependencyDeferralObserved: hasKind(trace, 'crosslane:defer-dependency') && checkpointRun.ok === true,
  maintenanceLaneCompactionObserved: compactDryRun.lane === 'maintenance' && compactRealRun.lane === 'maintenance',
  checkpointExecutedViaStorageLane: checkpointRun.lane === 'storage' && checkpointRun.result.kind === 'persisted-spill-mailbox-manifest',
  snapshotExecutedViaStorageLane: heldSnapshotRun.lane === 'storage' && waitedSnapshotRun.lane === 'storage',
  dryRunDidNotDelete: compactDryRun.result.deleted === 0,
  realCompactDeletedAckedOnly: compactRealRun.result.deleted === 1,
  pendingAndReadyProtected: postRealCompactionMailboxSnapshot.queueDepth >= 2 && postRealCompactionMailboxSnapshot.pendingCount === 0,
  providerBlocksRemainForLiveMessages: postRealCompactionProviderSnapshot.blockCount >= 2,
  providerFailureMarksStorageUnhealthy: failed.ok === false && hasKind(trace, 'storage-lane:provider-unhealthy'),
  unhealthyLaneRejectsWithoutMutation: rejectedDuringUnhealthy.accepted === false && rejectedDuringUnhealthy.scheduler.noMutation === true,
  providerRecoveryRestoresScheduling: restoredRun.ok === true && hasKind(trace, 'storage-lane:provider-healthy'),
  finalDeliveriesObserved: finalDeliveries.length === 3 && finalDeliveries.every((row) => row?.payload?.byteLength > 0),
  finalCompactionReclaimsRemainingBlocks: finalCompactRun.result.deleted >= 3,
  schedulerSnapshotValid: validateCrossLaneSchedulerSnapshot(snapshot.scheduler).ok === true,
  finalAccountingEmpty: snapshot.pendingOperationCount === 0 && snapshot.scheduler.queuedCount === 0 && snapshot.scheduler.inFlightCount === 0 && snapshot.mailbox.queueDepth === 0 && snapshot.mailbox.pendingCount === 0,
  providerEmptyAfterFinalCompaction: providerSnapshot.blockCount === 0,
  runtimeFactoryStorageLaneProofFlag: rt.report.executableProofs.storageLaneProviderProof === true,
  bootReportRecordsStorageLaneProviderProof: rt.report.executableProofs.storageLaneProviderProof === true,
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => traceKinds.includes(kind))
};
for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  status: 'passed',
  slice: 'scheduler:storage-lane-provider-proof',
  generatedAt: new Date().toISOString(),
  purpose: 'Fake-provider proof that CrossLaneScheduler can drive PersistedSpillMailbox through StorageLaneExecutor with storage/maintenance lanes, dependency deferral, provider health transitions, compaction, and trace evidence.',
  observations,
  counts: {
    enqueueDispatches: enqueueDrain.results.filter((row) => row.ok).length,
    finalDeliveries: finalDeliveries.length,
    traceEvents: trace.length,
    providerBlocks: providerSnapshot.blockCount
  },
  results: {
    deliveryA: summarize(deliveryA.result),
    checkpoint: summarize(checkpointRun.result),
    compactDry: summarize(compactDryRun.result),
    compactReal: summarize(compactRealRun.result),
    failed: summarize(failed.error),
    finalCompact: summarize(finalCompactRun.result)
  },
  schedulerSnapshot: snapshot.scheduler,
  mailboxSnapshot: snapshot.mailbox,
  providerSnapshot,
  traceKinds,
  requiredTraceKinds,
  nonClaims: [
    'No OPFS storage-lane provider proof.',
    'No browser Worker storage-lane provider proof.',
    'No durability, fsync, quota, eviction, or crash-recovery claim.',
    'No production scheduler/provider integration claim.',
    'No exactly-once delivery claim.',
    'No throughput or latency claim.',
    'No cross-browser conformance claim.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
