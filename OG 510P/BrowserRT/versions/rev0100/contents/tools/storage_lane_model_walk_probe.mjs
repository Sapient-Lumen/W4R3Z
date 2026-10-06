#!/usr/bin/env node
// BrowserRT rev0028 storage-lane provider model-walk proof.
// Fake-provider only. No OPFS storage-lane model proof. No durability, throughput, formal verification, or production scheduler claim.

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
  validateStorageLaneExecutorSnapshot,
  checksumPersistedSpillPayload32
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-STORAGE-LANE-MODEL-WALK-PROBE.json`);
const encoder = new TextEncoder();

function makeRng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 0x100000000;
  };
}
function pick(rng, items) { return items[Math.floor(rng() * items.length)]; }
function payloadFor(seed, seq) { return encoder.encode(`storage-lane-model:${seed}:${seq}:${'x'.repeat((seq % 7) + 1)}`); }
function checksum32(bytes) { return checksumPersistedSpillPayload32(bytes); }
function hasKind(trace, kind) { return trace.some((event) => event.kind === kind); }
function scenarioDigest(summary) {
  return JSON.stringify({
    seed: summary.seed,
    counters: summary.counters,
    observations: summary.observations,
    finalModel: summary.finalModel,
    finalExecutor: summary.finalExecutor
  });
}

class LogicalMailboxModel {
  constructor() {
    this.nextSeq = 1;
    this.ready = [];
    this.pending = new Map();
    this.acked = [];
    this.delivered = [];
    this.payloadChecksums = new Map();
  }
  enqueue(seq, payload) {
    this.nextSeq = Math.max(this.nextSeq, seq + 1);
    this.ready.push(seq);
    this.payloadChecksums.set(seq, checksum32(payload));
  }
  dequeue(delivery) {
    const expectedSeq = this.ready.shift();
    if (expectedSeq == null) return null;
    assert.equal(delivery.seq, expectedSeq, 'dequeue seq must match logical FIFO head');
    assert.equal(delivery.checksum32, this.payloadChecksums.get(expectedSeq), 'dequeue checksum must match logical payload');
    this.pending.set(delivery.pendingId, expectedSeq);
    this.delivered.push(expectedSeq);
    return expectedSeq;
  }
  ack(pendingId) {
    const seq = this.pending.get(pendingId);
    assert.notEqual(seq, undefined, `model must know pending id ${pendingId}`);
    this.pending.delete(pendingId);
    this.acked.push(seq);
    return seq;
  }
  snapshot() {
    return Object.freeze({ ready: this.ready.slice(), pending: [...this.pending.values()], pendingIds: [...this.pending.keys()], acked: this.acked.slice(), delivered: this.delivered.slice(), nextSeq: this.nextSeq });
  }
}

function makeRig(seed, scenarioIndex) {
  return boot({ storageLaneModelWalkProof: true }).then((rt) => {
    const provider = createMemoryBlockStore({ name: `rev0028-storage-lane-model-provider-${scenarioIndex}`, provider: 'memory-block-storage-lane-model-provider-v0', quotaBytes: 32 * 1024, trace: rt.trace });
    const mailbox = createPersistedSpillMailbox({ label: `rev0028-storage-lane-model-mailbox-${scenarioIndex}`, provider, memoryCapacityBytes: 64, maxFrameBytes: 256, deleteBlockOnAck: false, trace: rt.trace });
    const scheduler = createCrossLaneScheduler({
      label: `rev0028-storage-lane-model-scheduler-${scenarioIndex}`,
      maxQueuedCost: 512,
      maxTaskCost: 64,
      lanes: [
        { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 256 },
        { id: 'maintenance', rank: 20, capacity: 1, quantum: 64, maxQueuedCost: 128 },
        { id: 'cpu', rank: 40, capacity: 1, quantum: 64, maxQueuedCost: 128 }
      ],
      trace: rt.trace
    });
    const executor = createStorageLaneExecutor({ label: `rev0028-storage-lane-model-executor-${scenarioIndex}`, scheduler, mailbox, trace: rt.trace });
    return { rt, provider, mailbox, scheduler, executor, model: new LogicalMailboxModel(), rng: makeRng(seed) };
  });
}

function compareModelToExecutor(rig, label) {
  const snapshot = rig.executor.snapshot();
  const validation = validateStorageLaneExecutorSnapshot(snapshot);
  assert.equal(validation.ok, true, `${label}: storage-lane snapshot valid: ${validation.errors.join('; ')}`);
  const model = rig.model.snapshot();
  const mailbox = snapshot.mailbox;
  assert.deepEqual(mailbox.queueSeqs, model.ready, `${label}: ready queue must match model`);
  assert.deepEqual(mailbox.pendingSeqs, model.pending, `${label}: pending seqs must match model`);
  assert.equal(snapshot.schedulerValidation.ok, true, `${label}: scheduler snapshot valid`);
  return { validation, model, executor: { queuedCount: snapshot.scheduler.queuedCount, inFlightCount: snapshot.scheduler.inFlightCount, queueDepth: mailbox.queueDepth, pendingCount: mailbox.pendingCount, providerBlockCount: mailbox.providerSnapshot.blockCount, retainedBlockCount: mailbox.retainedBlockCount } };
}

async function submitAndExecute(rig, op, args = {}, options = {}) {
  const scheduled = rig.executor.submit(op, args, options);
  if (!scheduled.accepted) return { scheduled, run: null };
  const run = await rig.executor.executeNext();
  return { scheduled, run };
}

async function opEnqueue(rig, counters, observations, seed, step) {
  const seq = rig.model.nextSeq;
  const payload = payloadFor(seed, seq);
  const { scheduled, run } = await submitAndExecute(rig, 'enqueue', { payload, seq, label: `seq-${seq}` }, { id: `s${seed}-${step}-enqueue-${seq}`, priority: pick(rig.rng, ['user-visible', 'background']), cost: Math.max(1, Math.ceil(payload.byteLength / 16)) });
  assert.equal(scheduled.accepted, true, 'enqueue should schedule in normal path');
  assert.equal(run.ok, true, 'enqueue should execute in normal path');
  rig.model.enqueue(seq, payload);
  counters.enqueues += 1;
  if (run.result.disposition === 'spilled-persisted') observations.spillPathObserved = true;
  else observations.hotPathObserved = true;
}

async function opDequeue(rig, counters, observations, seed, step) {
  const beforeReady = rig.model.ready.length;
  const { scheduled, run } = await submitAndExecute(rig, 'dequeue', { consumerId: `consumer-${seed}` }, { id: `s${seed}-${step}-dequeue`, priority: 'user-visible', cost: 1 });
  assert.equal(scheduled.accepted, true, 'dequeue should schedule');
  assert.equal(run.ok, true, 'dequeue should execute');
  counters.dequeues += 1;
  if (beforeReady === 0) {
    assert.equal(run.result, null, 'empty model must produce empty dequeue');
    observations.emptyDequeueObserved = true;
  } else {
    rig.model.dequeue(run.result);
    observations.deliveryObserved = true;
  }
}

async function opAck(rig, counters, observations, seed, step) {
  const pendingIds = [...rig.model.pending.keys()];
  if (!pendingIds.length) return false;
  const pendingId = pick(rig.rng, pendingIds);
  const { scheduled, run } = await submitAndExecute(rig, 'ack', { pendingId, deleteBlock: false }, { id: `s${seed}-${step}-ack-${pendingId.replace(':', '-')}`, priority: 'background', cost: 1 });
  assert.equal(scheduled.accepted, true, 'ack should schedule');
  assert.equal(run.ok, true, 'ack should execute');
  assert.equal(run.result, true, 'ack result true');
  rig.model.ack(pendingId);
  counters.acks += 1;
  observations.ackObserved = true;
  return true;
}

async function opCheckpoint(rig, counters, observations, seed, step) {
  const { scheduled, run } = await submitAndExecute(rig, 'checkpoint', { label: `model-${seed}-${step}` }, { id: `s${seed}-${step}-checkpoint`, priority: 'background', cost: 1 });
  assert.equal(scheduled.accepted, true, 'checkpoint should schedule');
  assert.equal(run.ok, true, 'checkpoint should execute');
  assert.equal(run.result.kind, 'persisted-spill-mailbox-manifest', 'checkpoint returns manifest');
  counters.checkpoints += 1;
  observations.checkpointObserved = true;
}

async function opCompact(rig, counters, observations, seed, step) {
  const dry = rig.rng() < 0.55;
  const before = rig.model.snapshot();
  const { scheduled, run } = await submitAndExecute(rig, 'compact', { dryRun: dry, reason: `model-${seed}-${step}` }, { id: `s${seed}-${step}-compact-${dry ? 'dry' : 'real'}`, lane: 'maintenance', priority: 'maintenance', cost: 1 });
  assert.equal(scheduled.accepted, true, 'compact should schedule');
  assert.equal(run.ok, true, 'compact should execute');
  assert.deepEqual(rig.model.snapshot(), before, 'compaction must not mutate logical delivery model');
  counters.compactions += 1;
  observations.compactionNoLogicalMutation = true;
  if (run.result.dryRun) observations.dryRunCompactionObserved = true;
  else observations.realCompactionObserved = true;
}

async function opHealthReject(rig, counters, observations, seed, step) {
  const before = rig.executor.snapshot();
  rig.executor.markUnhealthy('storage', `model-health-down-${seed}-${step}`);
  const payload = payloadFor(seed, rig.model.nextSeq);
  const scheduled = rig.executor.submit('enqueue', { payload, seq: rig.model.nextSeq, label: 'health-reject' }, { id: `s${seed}-${step}-health-reject`, priority: 'critical', cost: 1 });
  assert.equal(scheduled.accepted, false, 'unhealthy storage lane should reject enqueue without fallback');
  assert.equal(scheduled.scheduler.noMutation, true, 'health rejection must report no mutation');
  const after = rig.executor.snapshot();
  assert.equal(before.scheduler.queuedCount, after.scheduler.queuedCount, 'health reject queuedCount no mutation');
  assert.equal(before.mailbox.queueDepth, after.mailbox.queueDepth, 'health reject queueDepth no mutation');
  rig.executor.markHealthy('storage', `model-health-up-${seed}-${step}`);
  counters.healthRejects += 1;
  observations.healthRejectNoMutation = true;
}

async function opProviderFailure(rig, counters, observations, seed, step) {
  const before = rig.model.snapshot();
  const seq = rig.model.nextSeq;
  rig.provider.failNextPutForTest(`model provider failure ${seed}/${step}`);
  const scheduled = rig.executor.submit('enqueue', { payload: payloadFor(seed, seq), seq, label: 'provider-fail' }, { id: `s${seed}-${step}-provider-fail`, priority: 'critical', cost: 1 });
  assert.equal(scheduled.accepted, true, 'provider failure task should enter scheduler');
  const run = await rig.executor.executeNext();
  assert.equal(run.ok, false, 'provider failure should fail during execution');
  assert.equal(rig.scheduler.snapshotLane('storage').healthy, false, 'storage lane should be unhealthy after storage provider failure');
  assert.deepEqual(rig.model.snapshot(), before, 'provider failure must not mutate logical model');
  rig.executor.markHealthy('storage', `provider-restored-${seed}-${step}`);
  counters.providerFailures += 1;
  observations.providerFailureObserved = true;
}

async function opCapacityBlock(rig, counters, observations, seed, step) {
  const first = rig.executor.submit('snapshot', {}, { id: `s${seed}-${step}-capacity-hold`, priority: 'critical', cost: 1 });
  const second = rig.executor.submit('snapshot', {}, { id: `s${seed}-${step}-capacity-wait`, priority: 'critical', cost: 1 });
  assert.equal(first.accepted && second.accepted, true, 'capacity setup should schedule two snapshots');
  const held = rig.scheduler.dispatchNext();
  assert.equal(held.dispatched, true, 'first snapshot dispatches');
  const blocked = rig.scheduler.dispatchNext();
  assert.equal(blocked.dispatched, false, 'second snapshot blocked by lane capacity');
  assert.equal(blocked.disposition, 'empty', 'capacity block still reports empty dispatch result');
  assert.equal((await rig.executor.executeDispatched(held)).ok, true, 'held snapshot executes');
  assert.equal((await rig.executor.executeNext()).ok, true, 'waiting snapshot executes after capacity frees');
  counters.capacityBlocks += 1;
  observations.capacityBlockObserved = true;
}

async function opDependencyDeferral(rig, counters, observations, seed, step) {
  if (!rig.model.pending.size) return false;
  const [pendingId] = rig.model.pending.keys();
  const ackId = `s${seed}-${step}-dep-ack`;
  const checkpoint = rig.executor.submit('checkpoint', { label: `blocked-${seed}-${step}` }, { id: `s${seed}-${step}-dep-checkpoint`, priority: 'critical', cost: 1, dependsOn: [ackId] });
  const ack = rig.executor.submit('ack', { pendingId, deleteBlock: false }, { id: ackId, priority: 'background', cost: 1 });
  assert.equal(checkpoint.accepted && ack.accepted, true, 'dependency setup should schedule checkpoint and ack');
  const ackRun = await rig.executor.executeNext();
  assert.equal(ackRun.ok, true, 'dependency ack should execute first after deferral');
  rig.model.ack(pendingId);
  const checkpointRun = await rig.executor.executeNext();
  assert.equal(checkpointRun.ok, true, 'dependency checkpoint should execute after ack completes');
  counters.dependencyDeferrals += 1;
  observations.dependencyDeferralObserved = true;
  return true;
}

async function drainFinal(rig, counters, seed) {
  for (const pendingId of [...rig.model.pending.keys()]) {
    const { run } = await submitAndExecute(rig, 'ack', { pendingId, deleteBlock: false }, { id: `s${seed}-final-ack-${pendingId.replace(':', '-')}`, priority: 'background', cost: 1 });
    assert.equal(run.ok, true);
    rig.model.ack(pendingId);
  }
  while (rig.model.ready.length) {
    const deq = await submitAndExecute(rig, 'dequeue', { consumerId: `final-${seed}` }, { id: `s${seed}-final-dequeue-${rig.model.ready[0]}`, priority: 'user-visible', cost: 1 });
    assert.equal(deq.run.ok, true);
    rig.model.dequeue(deq.run.result);
    const ack = await submitAndExecute(rig, 'ack', { pendingId: deq.run.result.pendingId, deleteBlock: false }, { id: `s${seed}-final-ack-${deq.run.result.pendingId.replace(':', '-')}`, priority: 'background', cost: 1 });
    assert.equal(ack.run.ok, true);
    rig.model.ack(deq.run.result.pendingId);
  }
  const compact = await submitAndExecute(rig, 'compact', { dryRun: false, reason: `final-${seed}` }, { id: `s${seed}-final-compact`, lane: 'maintenance', priority: 'maintenance', cost: 1 });
  assert.equal(compact.run.ok, true);
  counters.finalDrains += 1;
}

async function runScenario(seed, scenarioIndex, { replay = false } = {}) {
  const rig = await makeRig(seed, scenarioIndex);
  const counters = { steps: 0, enqueues: 0, dequeues: 0, acks: 0, checkpoints: 0, compactions: 0, healthRejects: 0, providerFailures: 0, capacityBlocks: 0, dependencyDeferrals: 0, finalDrains: 0, snapshotComparisons: 0 };
  const observations = { hotPathObserved: false, spillPathObserved: false, emptyDequeueObserved: false, deliveryObserved: false, ackObserved: false, checkpointObserved: false, compactionNoLogicalMutation: false, dryRunCompactionObserved: false, realCompactionObserved: false, healthRejectNoMutation: false, providerFailureObserved: false, capacityBlockObserved: false, dependencyDeferralObserved: false };
  compareModelToExecutor(rig, 'initial');
  const steps = 96;
  for (let step = 0; step < steps; step += 1) {
    counters.steps += 1;
    const choices = ['enqueue', 'dequeue', 'ack', 'checkpoint', 'compact', 'health', 'provider', 'capacity', 'dependency'];
    const choice = pick(rig.rng, choices);
    if (choice === 'enqueue') await opEnqueue(rig, counters, observations, seed, step);
    else if (choice === 'dequeue') await opDequeue(rig, counters, observations, seed, step);
    else if (choice === 'ack') await opAck(rig, counters, observations, seed, step);
    else if (choice === 'checkpoint') await opCheckpoint(rig, counters, observations, seed, step);
    else if (choice === 'compact') await opCompact(rig, counters, observations, seed, step);
    else if (choice === 'health') await opHealthReject(rig, counters, observations, seed, step);
    else if (choice === 'provider') await opProviderFailure(rig, counters, observations, seed, step);
    else if (choice === 'capacity') await opCapacityBlock(rig, counters, observations, seed, step);
    else if (choice === 'dependency') await opDependencyDeferral(rig, counters, observations, seed, step);
    compareModelToExecutor(rig, `scenario ${scenarioIndex} step ${step}`);
    counters.snapshotComparisons += 1;
  }
  await drainFinal(rig, counters, seed);
  const final = compareModelToExecutor(rig, `scenario ${scenarioIndex} final`);
  const executorSnapshot = rig.executor.snapshot();
  assert.equal(final.model.ready.length, 0, 'final model ready empty');
  assert.equal(final.model.pending.length, 0, 'final model pending empty');
  assert.equal(executorSnapshot.pendingOperationCount, 0, 'final executor pending ops empty');
  assert.equal(executorSnapshot.scheduler.queuedCount, 0, 'final scheduler queue empty');
  assert.equal(executorSnapshot.scheduler.inFlightCount, 0, 'final scheduler inFlight empty');
  const trace = rig.rt.close();
  const traceKinds = [...new Set(trace.map((event) => event.kind))].sort();
  const requiredTraceKinds = [
    'storage-lane:create',
    'storage-lane:schedule',
    'storage-lane:dispatch',
    'storage-lane:complete',
    'storage-lane:reject',
    'storage-lane:error',
    'storage-lane:provider-unhealthy',
    'storage-lane:provider-healthy',
    'crosslane:enqueue',
    'crosslane:dispatch',
    'crosslane:lane-at-capacity',
    'crosslane:defer-dependency',
    'mailbox:persisted-enqueue',
    'mailbox:persisted-deliver',
    'mailbox:persisted-ack',
    'mailbox:persisted-compact',
    'storage:block-put'
  ];
  const summary = {
    seed,
    scenarioIndex,
    replay,
    counters,
    observations: {
      ...observations,
      snapshotsValidated: true,
      modelAgreementEveryStep: true,
      finalAccountingEmpty: executorSnapshot.pendingOperationCount === 0 && executorSnapshot.scheduler.queuedCount === 0 && executorSnapshot.scheduler.inFlightCount === 0 && final.model.ready.length === 0 && final.model.pending.length === 0,
      traceHasRequiredEvents: requiredTraceKinds.every((kind) => hasKind(trace, kind))
    },
    finalModel: final.model,
    finalExecutor: final.executor,
    traceKinds
  };
  if (!summary.observations.traceHasRequiredEvents) {
    const missing = requiredTraceKinds.filter((kind) => !hasKind(trace, kind));
    throw new Error(`missing required trace kinds: ${missing.join(', ')}`);
  }
  return summary;
}

const seeds = Array.from({ length: 12 }, (_, i) => 0xB0870028 + i * 7919);
const scenarioSummaries = [];
for (let i = 0; i < seeds.length; i += 1) scenarioSummaries.push(await runScenario(seeds[i], i));
const replayA = await runScenario(seeds[3], 1003, { replay: true });
const replayB = await runScenario(seeds[3], 1003, { replay: true });
const deterministicReplayMatches = scenarioDigest(replayA) === scenarioDigest(replayB);
assert.equal(deterministicReplayMatches, true, 'deterministic replay summaries must match');

const totals = scenarioSummaries.reduce((acc, row) => {
  for (const [key, value] of Object.entries(row.counters)) acc[key] = (acc[key] || 0) + value;
  return acc;
}, {});
const observations = {
  deterministicReplayMatches,
  scenarioCount: scenarioSummaries.length,
  totalGeneratedSteps: totals.steps,
  snapshotsValidated: scenarioSummaries.every((row) => row.observations.snapshotsValidated),
  modelAgreementEveryStep: scenarioSummaries.every((row) => row.observations.modelAgreementEveryStep),
  finalAccountingEmpty: scenarioSummaries.every((row) => row.observations.finalAccountingEmpty),
  hotPathObserved: scenarioSummaries.some((row) => row.observations.hotPathObserved),
  spillPathObserved: scenarioSummaries.some((row) => row.observations.spillPathObserved),
  emptyDequeueObserved: scenarioSummaries.some((row) => row.observations.emptyDequeueObserved),
  deliveryObserved: scenarioSummaries.some((row) => row.observations.deliveryObserved),
  ackObserved: scenarioSummaries.some((row) => row.observations.ackObserved),
  checkpointObserved: scenarioSummaries.some((row) => row.observations.checkpointObserved),
  compactionNoLogicalMutation: scenarioSummaries.some((row) => row.observations.compactionNoLogicalMutation),
  healthRejectNoMutation: scenarioSummaries.some((row) => row.observations.healthRejectNoMutation),
  providerFailureObserved: scenarioSummaries.some((row) => row.observations.providerFailureObserved),
  capacityBlockObserved: scenarioSummaries.some((row) => row.observations.capacityBlockObserved),
  dependencyDeferralObserved: scenarioSummaries.some((row) => row.observations.dependencyDeferralObserved),
  traceHasRequiredEvents: scenarioSummaries.every((row) => row.observations.traceHasRequiredEvents)
};
for (const [key, value] of Object.entries(observations)) {
  if (key !== 'scenarioCount' && key !== 'totalGeneratedSteps') assert.equal(value, true, `observation must be true: ${key}`);
}

const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  status: 'passed',
  generatedAt: new Date().toISOString(),
  slice: 'scheduler:storage-lane-model-walk-proof',
  codename: 'Storage Lane Model Oracle',
  purpose: 'Deterministic fake-provider model walks for StorageLaneExecutor + CrossLaneScheduler + PersistedSpillMailbox composition.',
  nonClaims: [
    'No OPFS storage-lane model proof.',
    'No browser Worker storage-lane provider proof.',
    'No fsync, flush, quota, eviction, or durability claim.',
    'No production storage scheduler claim.',
    'No exhaustive model checking, formal verification, or true concurrent interleaving proof.',
    'No throughput or latency claim.',
    'No exactly-once delivery claim.'
  ],
  seeds,
  totals,
  observations,
  scenarioSummaries: scenarioSummaries.map((row) => ({ seed: row.seed, counters: row.counters, observations: row.observations, finalModel: row.finalModel, finalExecutor: row.finalExecutor }))
};

await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ status: report.status, revision: REVISION, slice: report.slice, outPath, observations }, null, 2));
