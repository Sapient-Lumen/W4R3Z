#!/usr/bin/env node
// BrowserRT rev0036 storage-lane admission-history model-walk proof.
// Fake-provider/model proof only: no OPFS, browser Worker, production overload-governance, throughput, durability, exactly-once, or formal verification claim.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  boot,
  createMemoryBlockStore,
  createPersistedSpillMailbox,
  createCrossLaneScheduler,
  createStorageLaneExecutor,
  createCircuitBreakerBulkheadController,
  createRetryBudgetAdmissionController,
  createProviderResilienceHistoryRunner,
  createStorageLaneAdmissionHistoryRunner,
  createWatermarkAdmissionController,
  validateStorageLaneAdmissionHistorySnapshot,
  createStorageLaneAdmissionHistoryModelOracle,
  compareStorageLaneAdmissionHistoryToModel,
  validateStorageLaneAdmissionHistoryModelSnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-STORAGE-LANE-ADMISSION-MODEL-PROBE.json`);

function makeRng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 0x100000000;
  };
}
function pick(rng, values) { return values[Math.floor(rng() * values.length)]; }
function hasKind(trace, kind) { return trace.some((row) => row.kind === kind); }
function kinds(trace) { return [...new Set(trace.map((row) => row.kind))].sort(); }
function stripLabels(value) {
  if (Array.isArray(value)) return value.map(stripLabels);
  if (value && typeof value === 'object') {
    const out = {};
    for (const [key, child] of Object.entries(value)) {
      if (key === 'label') continue;
      out[key] = stripLabels(child);
    }
    return out;
  }
  return value;
}
function scenarioDigest(summary) {
  return JSON.stringify({ seed: summary.seed, counters: summary.counters, observations: summary.observations, finalModel: stripLabels(summary.finalModel), finalReal: stripLabels(summary.finalReal) });
}

const admissionOptions = Object.freeze({ lowWatermarkBytes: 0, highWatermarkBytes: 20, hardLimitBytes: 64, criticalMinPriority: 'user-blocking', rejectMinPriorityWhileCongested: 'user-visible' });

function makeHarness(rt, seed, scenarioIndex) {
  const label = `rev0036-admission-model-${scenarioIndex}-${seed}`;
  const provider = createMemoryBlockStore({ name: `${label}:provider`, provider: 'memory-storage-admission-model-v0', quotaBytes: 256 * 1024, trace: rt.trace });
  const mailbox = createPersistedSpillMailbox({ label: `${label}:mailbox`, provider, trace: rt.trace, deleteBlockOnAck: false, memoryCapacityBytes: 0, maxFrameBytes: 512 });
  const scheduler = createCrossLaneScheduler({ label: `${label}:scheduler`, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 4096 }] });
  const executor = createStorageLaneExecutor({ label: `${label}:executor`, mailbox, scheduler, trace: rt.trace, markUnhealthyOnError: false });
  const breaker = createCircuitBreakerBulkheadController({ label: `${label}:breaker`, trace: rt.trace, maxConcurrent: 4, slidingWindowSize: 1024, minimumCalls: 999, failureRateThreshold: 100, openDurationTicks: 2, halfOpenMaxCalls: 1 });
  const retryBudget = createRetryBudgetAdmissionController({ label: `${label}:retry-budget`, trace: rt.trace, maxRetryCredits: 256, initialRetryCredits: 128, maxActiveRetries: 4, refillPerPrimarySuccess: 1 });
  const resilienceRunner = createProviderResilienceHistoryRunner({ label: `${label}:resilience`, executor, mailbox, breaker, retryBudget, retryPolicy: { maxAttempts: 3, initialDelayTicks: 1, maxDelayTicks: 2, jitterTicks: 0 }, trace: rt.trace });
  const admission = createWatermarkAdmissionController({ label: `${label}:admission`, ...admissionOptions, trace: rt.trace });
  const runner = createStorageLaneAdmissionHistoryRunner({ label, admission, resilienceRunner, mailbox, trace: rt.trace });
  const model = createStorageLaneAdmissionHistoryModelOracle({ label: `${label}:model`, ...admissionOptions, trace: rt.trace });
  return { label, provider, mailbox, scheduler, executor, breaker, retryBudget, resilienceRunner, admission, runner, model, held: [] };
}

function compareRig(rig, label) {
  const real = rig.runner.snapshot();
  const model = rig.model.snapshot();
  const realValidation = validateStorageLaneAdmissionHistorySnapshot(real);
  const modelValidation = validateStorageLaneAdmissionHistoryModelSnapshot(model);
  assert.equal(realValidation.ok, true, `${label}: real snapshot invalid: ${realValidation.errors.join('; ')}`);
  assert.equal(modelValidation.ok, true, `${label}: model snapshot invalid: ${modelValidation.errors.join('; ')}`);
  const cmp = compareStorageLaneAdmissionHistoryToModel(real, model, { providerSnapshot: rig.provider.snapshot() });
  assert.equal(cmp.ok, true, `${label}: model comparison failed: ${cmp.errors.join('; ')}`);
  return { realValidation, modelValidation, comparison: cmp, real, model };
}

function modelPredictsAdmission(rig, input) {
  return rig.model.predictAdmission(input).admitted === true;
}

async function runEnqueue(rig, counters, observations, input, expectedFinal = 'success') {
  const before = rig.provider.snapshot().blockCount;
  if (expectedFinal === 'transient-success' && modelPredictsAdmission(rig, input)) {
    rig.provider.failNextPutForTest(`admission model transient ${input.id}`);
  }
  const row = await rig.runner.runMailboxEnqueue(input);
  const after = rig.provider.snapshot().blockCount;
  const observed = rig.model.observeOperation(input, row, { providerBlocksBefore: before, providerBlocksAfter: after, expectedFinal });
  assert.equal(observed.ok, true, `model observation failed for ${input.id}: ${observed.errors.join('; ')}`);
  counters.operations += 1;
  if (row.admission?.admitted === true || row.admission?.disposition?.startsWith?.('admitted')) counters.admitted += 1;
  else counters.rejected += 1;
  if (row.final?.ok === true) counters.successes += 1;
  if (row.final?.ok === false) counters.failures += 1;
  if (row.final?.disposition === 'rejected-watermark') observations.watermarkRejectObserved = true;
  if (row.final?.disposition === 'rejected-provider-health') observations.providerHealthRejectObserved = true;
  if (row.final?.disposition === 'rejected-hard-limit') observations.hardLimitRejectObserved = true;
  if (row.admission?.bypass === true) observations.criticalBypassObserved = true;
  if (row.final?.reason === 'retry-success') observations.transientRetryObserved = true;
  if (row.final?.noProviderMutation === true) observations.noMutationRejectObserved = true;
  if (row.final?.ok === true) observations.successObserved = true;
  return row;
}

function holdCongestion(rig, counters, observations, bytes = admissionOptions.highWatermarkBytes) {
  const real = rig.admission.tryAdmit({ bytes, priority: 'critical', label: `held-${counters.holds}` });
  const model = rig.model.holdLease({ bytes, priority: 'critical', label: `held-${counters.holds}` });
  assert.equal(real.admitted, model.held, 'real/model held-admit result must match');
  if (real.admitted) {
    rig.held.push({ realLeaseId: real.leaseId, modelLeaseId: model.leaseId });
    counters.holds += 1;
    observations.heldLeaseObserved = true;
  }
}
function releaseHeld(rig, counters, observations) {
  const held = rig.held.shift();
  if (!held) return false;
  const real = rig.admission.release(held.realLeaseId, { outcome: 'model-release-held' });
  const model = rig.model.releaseHeld(held.modelLeaseId, 'model-release-held');
  assert.equal(real.released, model.released, 'real/model held release result must match');
  counters.releases += 1;
  observations.heldReleaseObserved = true;
  return true;
}
function setProviderHealth(rig, healthy, counters, observations) {
  if (healthy) {
    rig.runner.markAdmissionProviderHealthy('model-health-up');
    rig.model.markProviderHealthy('model-health-up');
    counters.healthTransitions += 1;
    observations.providerHealthRecoveryObserved = true;
  } else {
    rig.runner.markAdmissionProviderUnhealthy('model-health-down');
    rig.model.markProviderUnhealthy('model-health-down');
    counters.healthTransitions += 1;
    observations.providerHealthDownObserved = true;
  }
}

async function applyCommand(rig, seed, step, command, counters, observations) {
  if (command === 'hold') holdCongestion(rig, counters, observations, admissionOptions.highWatermarkBytes);
  else if (command === 'release') releaseHeld(rig, counters, observations);
  else if (command === 'health-down') setProviderHealth(rig, false, counters, observations);
  else if (command === 'health-up') setProviderHealth(rig, true, counters, observations);
  else if (command === 'hard') await runEnqueue(rig, counters, observations, { id: `s${seed}-${step}-hard`, payload: `hard:${seed}:${step}`, priority: 'critical', bytes: admissionOptions.hardLimitBytes + 1, maxAttempts: 1 }, 'admission-reject');
  else if (command === 'transient') await runEnqueue(rig, counters, observations, { id: `s${seed}-${step}-transient`, payload: `transient:${seed}:${step}`, priority: 'user-visible', bytes: 4, idempotent: true, maxAttempts: 3 }, 'transient-success');
  else if (command === 'critical') await runEnqueue(rig, counters, observations, { id: `s${seed}-${step}-critical`, payload: `critical:${seed}:${step}`, priority: 'critical', bytes: 4, maxAttempts: 2 }, 'critical-success');
  else await runEnqueue(rig, counters, observations, { id: `s${seed}-${step}-success`, payload: `success:${seed}:${step}:${command}`, priority: command === 'background' ? 'background' : 'user-visible', bytes: command === 'background' ? 3 : 4, maxAttempts: 2 }, 'success');
  counters.steps += 1;
  compareRig(rig, `${rig.label}:${step}:${command}`);
}

async function runScenario(rt, seed, scenarioIndex, { targeted = false } = {}) {
  const rng = makeRng(seed);
  const rig = makeHarness(rt, seed, scenarioIndex);
  const counters = { steps: 0, operations: 0, admitted: 0, rejected: 0, successes: 0, failures: 0, holds: 0, releases: 0, healthTransitions: 0, comparisons: 0 };
  const observations = { successObserved: false, transientRetryObserved: false, watermarkRejectObserved: false, criticalBypassObserved: false, providerHealthDownObserved: false, providerHealthRejectObserved: false, providerHealthRecoveryObserved: false, hardLimitRejectObserved: false, noMutationRejectObserved: false, heldLeaseObserved: false, heldReleaseObserved: false };
  compareRig(rig, `${rig.label}:initial`);

  const commands = targeted ? [
    'success', 'transient', 'hold', 'background', 'critical', 'release', 'health-down', 'background', 'critical', 'health-up', 'background', 'hard'
  ] : null;
  const steps = targeted ? commands.length : 84;
  for (let step = 0; step < steps; step += 1) {
    let command;
    if (targeted) command = commands[step];
    else {
      const choices = ['success', 'background', 'critical', 'transient', 'hard', 'hold', 'release', 'health-down', 'health-up'];
      command = pick(rng, choices);
      if (command === 'hold' && rig.held.length >= 2) command = 'background';
      if (command === 'release' && rig.held.length === 0) command = 'success';
    }
    await applyCommand(rig, seed, step, command, counters, observations);
    counters.comparisons += 1;
  }
  while (rig.held.length) {
    releaseHeld(rig, counters, observations);
    compareRig(rig, `${rig.label}:final-release`);
    counters.comparisons += 1;
  }
  if (!rig.model.snapshot().providerHealthy) {
    setProviderHealth(rig, true, counters, observations);
    compareRig(rig, `${rig.label}:final-health`);
    counters.comparisons += 1;
  }
  const finalCompare = compareRig(rig, `${rig.label}:final`);
  const finalReal = finalCompare.real;
  const finalModel = finalCompare.model;
  assert.equal(finalReal.admission.leaseCount, 0, 'admission leases must be empty at scenario end');
  assert.equal(finalReal.admission.inFlightBytes, 0, 'admission bytes must be empty at scenario end');
  return { seed, scenarioIndex, targeted, counters, observations, finalReal: { historyCount: finalReal.historyCount, stats: finalReal.stats, admission: finalReal.admission, providerBlocks: rig.provider.snapshot().blockCount }, finalModel };
}

const rt = await boot({ storageLaneAdmissionHistoryModelProof: true, storageLaneAdmissionHistoryProof: true, providerResilienceHistoryProof: true, retryBudgetAdmissionProof: true });
const summaries = [];
summaries.push(await runScenario(rt, 0xA11CE, 0, { targeted: true }));
const seeds = Array.from({ length: 18 }, (_, i) => 0x5A17 + i * 97);
for (const [i, seed] of seeds.entries()) summaries.push(await runScenario(rt, seed, i + 1));
// Deterministic replay of the first generated seed.
const replay = await runScenario(rt, seeds[0], 100, { targeted: false });
assert.equal(scenarioDigest(summaries[1]), scenarioDigest(replay), 'deterministic replay of seed 1 should match');

const trace = rt.close();
const aggregate = summaries.reduce((acc, s) => {
  for (const [key, value] of Object.entries(s.counters)) acc[key] = (acc[key] || 0) + value;
  for (const [key, value] of Object.entries(s.observations)) acc.observations[key] = acc.observations[key] || Boolean(value);
  return acc;
}, { observations: {} });
const requiredTraceKinds = [
  'storage-admission-model:create',
  'storage-admission-model:observe-admitted',
  'storage-admission-model:observe-reject',
  'storage-admission-history:operation-start',
  'storage-admission-history:operation-final',
  'admission:admit',
  'admission:reject',
  'provider-resilience:operation-final'
];
const observations = {
  scenarioCount: summaries.length,
  generatedScenarioCount: summaries.length - 1,
  totalSteps: aggregate.steps,
  deterministicReplayMatches: scenarioDigest(summaries[1]) === scenarioDigest(replay),
  modelAgreementEveryStep: true,
  snapshotsValidate: true,
  successObserved: aggregate.observations.successObserved === true,
  transientRetryObserved: aggregate.observations.transientRetryObserved === true,
  watermarkRejectObserved: aggregate.observations.watermarkRejectObserved === true,
  criticalBypassObserved: aggregate.observations.criticalBypassObserved === true,
  providerHealthRejectObserved: aggregate.observations.providerHealthRejectObserved === true,
  providerHealthRecoveryObserved: aggregate.observations.providerHealthRecoveryObserved === true,
  hardLimitRejectObserved: aggregate.observations.hardLimitRejectObserved === true,
  noMutationRejectObserved: aggregate.observations.noMutationRejectObserved === true,
  heldLeaseAndReleaseObserved: aggregate.observations.heldLeaseObserved === true && aggregate.observations.heldReleaseObserved === true,
  finalAccountingEmpty: summaries.every((s) => s.finalReal.admission.leaseCount === 0 && s.finalReal.admission.inFlightBytes === 0),
  bootReportRecordsStorageLaneAdmissionModelProof: rt.report.executableProofs.storageLaneAdmissionHistoryModelProof === true,
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => hasKind(trace, kind))
};
for (const [key, value] of Object.entries(observations)) {
  if (typeof value === 'boolean') assert.equal(value, true, `${key} should be true`);
}

const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed', generatedAt: new Date().toISOString(),
  slice: 'scheduler:storage-lane-admission-model-proof',
  purpose: 'Run targeted and generated fake-provider storage-lane admission histories, comparing StorageLaneAdmissionHistoryRunner snapshots against an independent reference model after every command.',
  observations,
  aggregate: { ...aggregate, observations: undefined },
  summaries: summaries.map((s) => ({ seed: s.seed, targeted: s.targeted, counters: s.counters, observations: s.observations, finalReal: s.finalReal, finalModel: s.finalModel })),
  trace: { count: trace.length, kinds: kinds(trace), requiredTraceKinds },
  nonClaims: [
    'No OPFS storage-lane admission-history model proof.',
    'No browser Worker storage-lane admission-history model proof.',
    'No production overload-governance, admission-control, retry-storm, circuit-breaker, bulkhead, retry-budget, storage-lane, or fairness claim.',
    'No exhaustive model checking, formal verification, true concurrent interleaving, or linearizability claim.',
    'No wall-clock timer, throughput, latency, SLO, durability, fsync, quota, eviction, crash-recovery, or exactly-once delivery claim.',
    'No cross-browser conformance claim.',
    'No WebGPU proof.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
