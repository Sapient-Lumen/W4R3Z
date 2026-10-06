#!/usr/bin/env node
// BrowserRT rev0039 storage-lane overload-governance model proof.
// Fake-provider/release-tier proof only: no OPFS, browser Worker, wall-clock, durability,
// throughput, exactly-once, or production overload-governance claim.
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
  createStorageLaneOverloadGovernanceModelOracle,
  compareStorageLaneOverloadGovernanceToRuntime,
  validateStorageLaneOverloadGovernanceSnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-STORAGE-LANE-OVERLOAD-GOVERNANCE-PROBE.json`);

function hasKind(trace, kind) { return trace.some((row) => row.kind === kind); }
function kinds(trace) { return [...new Set(trace.map((row) => row.kind))].sort(); }
function makeRng(seed) {
  let s = seed >>> 0;
  return () => { s = (Math.imul(s, 1103515245) + 12345) >>> 0; return s / 0x100000000; };
}
function pick(rng, values) { return values[Math.floor(rng() * values.length)]; }

function makeHarness(rt, label, cfg = {}) {
  const provider = createMemoryBlockStore({ name: `${label}:provider`, provider: 'memory-storage-overload-governance-v0', quotaBytes: 512 * 1024, trace: rt.trace, ...(cfg.provider || {}) });
  const mailbox = createPersistedSpillMailbox({ label: `${label}:mailbox`, provider, trace: rt.trace, deleteBlockOnAck: false, memoryCapacityBytes: 0, maxFrameBytes: 512, ...(cfg.mailbox || {}) });
  const scheduler = createCrossLaneScheduler({ label: `${label}:scheduler`, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 4096 }], ...(cfg.scheduler || {}) });
  const executor = createStorageLaneExecutor({ label: `${label}:executor`, mailbox, scheduler, trace: rt.trace, markUnhealthyOnError: false, ...(cfg.executor || {}) });
  const breaker = createCircuitBreakerBulkheadController({ label: `${label}:breaker`, trace: rt.trace, maxConcurrent: 2, slidingWindowSize: 4, minimumCalls: 3, failureRateThreshold: 67, openDurationTicks: 2, halfOpenMaxCalls: 1, ...(cfg.breaker || {}) });
  const retryBudget = createRetryBudgetAdmissionController({ label: `${label}:retry-budget`, trace: rt.trace, maxRetryCredits: 4, initialRetryCredits: 2, maxActiveRetries: 2, refillPerPrimarySuccess: 1, ...(cfg.retryBudget || {}) });
  const resilienceRunner = createProviderResilienceHistoryRunner({ label: `${label}:resilience`, executor, mailbox, breaker, retryBudget, retryPolicy: { maxAttempts: 3, initialDelayTicks: 1, maxDelayTicks: 2, jitterTicks: 0, ...(cfg.retryPolicy || {}) }, trace: rt.trace });
  const admission = createWatermarkAdmissionController({ label: `${label}:admission`, lowWatermarkBytes: 0, highWatermarkBytes: 10, hardLimitBytes: 32, criticalMinPriority: 'user-blocking', rejectMinPriorityWhileCongested: 'user-visible', trace: rt.trace, ...(cfg.admission || {}) });
  const runner = createStorageLaneAdmissionHistoryRunner({ label, admission, resilienceRunner, mailbox, trace: rt.trace });
  const oracle = createStorageLaneOverloadGovernanceModelOracle({ label: `${label}:oracle`, trace: rt.trace });
  return { provider, mailbox, scheduler, executor, breaker, retryBudget, resilienceRunner, admission, runner, oracle, label };
}

async function observeRun(h, input, expectedClasses = [], options = {}) {
  const before = h.provider.snapshot().blockCount;
  if (options.failNextPut) h.provider.failNextPutForTest(`${h.label}:${input.id}:fail-next-put`);
  const row = await h.runner.runMailboxEnqueue(input);
  const after = h.provider.snapshot().blockCount;
  const observed = h.oracle.observeOperation({ label: input.id, input, row, beforeProviderBlocks: before, afterProviderBlocks: after, expectedClasses, expectNoProviderMutation: options.expectNoProviderMutation ?? null });
  assert.equal(observed.errors.length, 0, `${h.label}:${input.id}: ${observed.errors.join('; ')}`);
  h.oracle.observeSnapshot({ label: `${input.id}:snapshot`, admission: h.admission.snapshot(), resilience: h.resilienceRunner.snapshot(), breaker: h.breaker.snapshot(), retryBudget: h.retryBudget.snapshot() });
  return row;
}

async function targetedScenarios(rt) {
  const summaries = [];

  const success = makeHarness(rt, 'rev0039-success', { breaker: { slidingWindowSize: 128, minimumCalls: 99 } });
  const successRow = await observeRun(success, { id: 'success', payload: 'success', priority: 'user-visible', bytes: 4, maxAttempts: 2 }, ['success'], { expectNoProviderMutation: false });
  assert.equal(successRow.final.ok, true);
  summaries.push({ name: 'success', snapshot: success.oracle.snapshot(), final: successRow.final });

  const retry = makeHarness(rt, 'rev0039-retry-success', { breaker: { slidingWindowSize: 128, minimumCalls: 99 }, retryBudget: { initialRetryCredits: 2 } });
  const retryRow = await observeRun(retry, { id: 'retry-success', payload: 'retry-success', priority: 'user-visible', bytes: 4, maxAttempts: 3, idempotent: true }, ['success', 'retry-success'], { failNextPut: true, expectNoProviderMutation: false });
  assert.equal(retryRow.final.reason, 'retry-success');
  summaries.push({ name: 'retry-success', snapshot: retry.oracle.snapshot(), final: retryRow.final });

  const budget = makeHarness(rt, 'rev0039-budget-exhausted', { breaker: { slidingWindowSize: 128, minimumCalls: 99 }, retryBudget: { initialRetryCredits: 0, minRetryCredits: 0 } });
  const budgetRow = await observeRun(budget, { id: 'retry-budget-exhausted', payload: 'budget', priority: 'user-visible', bytes: 4, maxAttempts: 3, idempotent: true }, ['retry-budget-exhausted'], { failNextPut: true, expectNoProviderMutation: true });
  assert.equal(budgetRow.final.reason, 'retry-budget:retry-budget-exhausted');
  summaries.push({ name: 'retry-budget-exhausted', snapshot: budget.oracle.snapshot(), final: budgetRow.final });

  const nonIdem = makeHarness(rt, 'rev0039-non-idempotent', { breaker: { slidingWindowSize: 128, minimumCalls: 99 }, retryBudget: { initialRetryCredits: 2 } });
  const nonIdemRow = await observeRun(nonIdem, { id: 'non-idempotent', payload: 'non-idempotent', priority: 'user-visible', bytes: 4, maxAttempts: 3, idempotent: false }, ['retry-budget-non-idempotent'], { failNextPut: true, expectNoProviderMutation: true });
  assert.equal(nonIdemRow.final.reason, 'retry-budget:non-idempotent');
  summaries.push({ name: 'non-idempotent', snapshot: nonIdem.oracle.snapshot(), final: nonIdemRow.final });

  const bulkhead = makeHarness(rt, 'rev0039-bulkhead', { breaker: { maxConcurrent: 1, slidingWindowSize: 128, minimumCalls: 99 } });
  const held = bulkhead.breaker.tryAcquire({ opId: 'held-bulkhead', priority: 'critical', kind: 'test-held' });
  assert.equal(held.accepted, true);
  const bulkheadRow = await observeRun(bulkhead, { id: 'bulkhead', payload: 'bulkhead', priority: 'user-visible', bytes: 4, maxAttempts: 1 }, ['breaker-bulkhead'], { expectNoProviderMutation: true });
  bulkhead.breaker.release(held.leaseId, { ok: true });
  assert.equal(bulkheadRow.final.reason, 'breaker:bulkhead-full');
  summaries.push({ name: 'bulkhead', snapshot: bulkhead.oracle.snapshot(), final: bulkheadRow.final });

  const circuit = makeHarness(rt, 'rev0039-open-circuit', { breaker: { maxConcurrent: 2, slidingWindowSize: 2, minimumCalls: 1, failureRateThreshold: 100, openDurationTicks: 3 }, retryBudget: { initialRetryCredits: 0 } });
  const failRow = await observeRun(circuit, { id: 'open-primer', payload: 'open-primer', priority: 'user-visible', bytes: 4, maxAttempts: 1, autoHealOnRetry: false }, [], { failNextPut: true, expectNoProviderMutation: true });
  assert.equal(failRow.final.ok, false);
  const openRow = await observeRun(circuit, { id: 'open-reject', payload: 'open-reject', priority: 'user-visible', bytes: 4, maxAttempts: 1 }, ['breaker-open'], { expectNoProviderMutation: true });
  assert.equal(openRow.final.reason, 'breaker:circuit-open');
  summaries.push({ name: 'open-circuit', snapshot: circuit.oracle.snapshot(), final: openRow.final });

  const admission = makeHarness(rt, 'rev0039-admission', { breaker: { slidingWindowSize: 128, minimumCalls: 99 } });
  const heldAdmission = admission.admission.tryAdmit({ bytes: 10, priority: 'critical', label: 'held-admission' });
  assert.equal(heldAdmission.admitted, true);
  const watermarkRow = await observeRun(admission, { id: 'watermark', payload: 'watermark', priority: 'background', bytes: 2, maxAttempts: 1 }, ['admission-watermark'], { expectNoProviderMutation: true });
  const bypassRow = await observeRun(admission, { id: 'critical-bypass', payload: 'critical-bypass', priority: 'critical', bytes: 2, maxAttempts: 1 }, ['success', 'critical-bypass'], { expectNoProviderMutation: false });
  admission.admission.release(heldAdmission.leaseId, { outcome: 'test-release' });
  assert.equal(watermarkRow.final.disposition, 'rejected-watermark');
  assert.equal(bypassRow.admission.bypass, true);
  summaries.push({ name: 'admission-watermark-bypass', snapshot: admission.oracle.snapshot(), finals: [watermarkRow.final, bypassRow.final] });

  const health = makeHarness(rt, 'rev0039-admission-health', { breaker: { slidingWindowSize: 128, minimumCalls: 99 } });
  health.runner.markAdmissionProviderUnhealthy('test-health-down');
  const healthReject = await observeRun(health, { id: 'health-reject', payload: 'health', priority: 'background', bytes: 3, maxAttempts: 1 }, ['admission-health'], { expectNoProviderMutation: true });
  health.runner.markAdmissionProviderHealthy('test-health-up');
  const healthRecover = await observeRun(health, { id: 'health-recover', payload: 'health-recover', priority: 'background', bytes: 3, maxAttempts: 1 }, ['success'], { expectNoProviderMutation: false });
  assert.equal(healthReject.final.disposition, 'rejected-provider-health');
  assert.equal(healthRecover.final.ok, true);
  summaries.push({ name: 'admission-health', snapshot: health.oracle.snapshot(), finals: [healthReject.final, healthRecover.final] });

  const hard = makeHarness(rt, 'rev0039-hard-limit', { admission: { hardLimitBytes: 12, highWatermarkBytes: 8 }, breaker: { slidingWindowSize: 128, minimumCalls: 99 } });
  const hardRow = await observeRun(hard, { id: 'hard-limit', payload: 'hard', priority: 'critical', bytes: 13, maxAttempts: 1 }, ['admission-hard-limit'], { expectNoProviderMutation: true });
  assert.equal(hardRow.final.disposition, 'rejected-hard-limit');
  summaries.push({ name: 'hard-limit', snapshot: hard.oracle.snapshot(), final: hardRow.final });

  return summaries;
}

async function generatedGovernanceHistories(rt) {
  const summaries = [];
  for (let scenario = 0; scenario < 12; scenario += 1) {
    const seed = 0xB007 + scenario * 131;
    const rng = makeRng(seed);
    const h = makeHarness(rt, `rev0039-generated-${scenario}`, { breaker: { slidingWindowSize: 128, minimumCalls: 99 }, retryBudget: { initialRetryCredits: 3 } });
    const held = [];
    const counts = { commands: 0, success: 0, rejected: 0 };
    for (let step = 0; step < 64; step += 1) {
      let command = pick(rng, ['success', 'transient', 'hold', 'release', 'health-down', 'health-up', 'hard', 'background', 'critical']);
      if (command === 'hold' && held.length >= 2) command = 'success';
      if (command === 'release' && held.length === 0) command = 'success';
      if (command === 'hold') {
        const gate = h.admission.tryAdmit({ bytes: 10, priority: 'critical', label: `generated-held-${step}` });
        if (gate.admitted) held.push(gate.leaseId);
        h.oracle.observeSnapshot({ label: `generated-${step}-hold`, admission: h.admission.snapshot(), resilience: h.resilienceRunner.snapshot(), breaker: h.breaker.snapshot(), retryBudget: h.retryBudget.snapshot() });
      } else if (command === 'release') {
        const id = held.shift();
        if (id) h.admission.release(id, { outcome: 'generated-release' });
        h.oracle.observeSnapshot({ label: `generated-${step}-release`, admission: h.admission.snapshot(), resilience: h.resilienceRunner.snapshot(), breaker: h.breaker.snapshot(), retryBudget: h.retryBudget.snapshot() });
      } else if (command === 'health-down') {
        h.runner.markAdmissionProviderUnhealthy('generated-health-down');
        h.oracle.observeSnapshot({ label: `generated-${step}-health-down`, admission: h.admission.snapshot(), resilience: h.resilienceRunner.snapshot(), breaker: h.breaker.snapshot(), retryBudget: h.retryBudget.snapshot() });
      } else if (command === 'health-up') {
        h.runner.markAdmissionProviderHealthy('generated-health-up');
        h.oracle.observeSnapshot({ label: `generated-${step}-health-up`, admission: h.admission.snapshot(), resilience: h.resilienceRunner.snapshot(), breaker: h.breaker.snapshot(), retryBudget: h.retryBudget.snapshot() });
      } else {
        const expected = [];
        const input = { id: `g${scenario}-${step}-${command}`, payload: `generated:${scenario}:${step}:${command}`, priority: command === 'background' ? 'background' : command === 'critical' ? 'critical' : 'user-visible', bytes: command === 'hard' ? 33 : command === 'background' ? 3 : 4, maxAttempts: command === 'transient' ? 3 : 2, idempotent: true };
        if (command === 'hard') expected.push('admission-hard-limit');
        // Generated histories intentionally avoid hard expected success classes because
        // admission health/congestion commands may legitimately reject before the resilience layer.
        const row = await observeRun(h, input, expected, { failNextPut: command === 'transient', expectNoProviderMutation: command === 'hard' ? true : null });
        if (row.final?.ok === true) counts.success += 1; else counts.rejected += 1;
      }
      counts.commands += 1;
    }
    while (held.length) h.admission.release(held.shift(), { outcome: 'generated-final-release' });
    if (!h.admission.snapshot().providerHealthy) h.runner.markAdmissionProviderHealthy('generated-final-health-up');
    const oracleSnapshot = h.oracle.snapshot();
    const validation = validateStorageLaneOverloadGovernanceSnapshot(oracleSnapshot);
    assert.equal(validation.ok, true, validation.errors.join('; '));
    const comparison = compareStorageLaneOverloadGovernanceToRuntime(oracleSnapshot, { admission: h.admission.snapshot(), breaker: h.breaker.snapshot(), retryBudget: h.retryBudget.snapshot() });
    assert.equal(comparison.ok, true, comparison.errors.join('; '));
    summaries.push({ seed, counts, stats: oracleSnapshot.stats });
  }
  return summaries;
}

// This generated-history proof intentionally emits more than the runtime's
// default trace budget. Keep the larger proof budget explicit instead of
// silently returning to an unbounded trace.
const rt = await boot({ traceCapacity: 32768, storageLaneOverloadGovernanceModelProof: true, storageLaneAdmissionHistoryModelProof: true, providerResilienceHistoryProof: true, retryBudgetAdmissionProof: true, circuitBreakerBulkheadProof: true });
const targeted = await targetedScenarios(rt);
const generated = await generatedGovernanceHistories(rt);
const trace = rt.close();

const aggregate = targeted.concat(generated).reduce((acc, row) => {
  const stats = row.snapshot?.stats || row.stats || {};
  for (const [key, value] of Object.entries(stats)) acc[key] = (acc[key] || 0) + value;
  return acc;
}, {});
const requiredTraceKinds = [
  'storage-overload-model:create',
  'storage-overload-model:observe',
  'storage-admission-history:operation-start',
  'storage-admission-history:operation-final',
  'provider-resilience:operation-final',
  'admission:admit',
  'admission:reject',
  'retry-budget:reject',
  'resilience:reject'
];
const observations = {
  targetedScenarioCount: targeted.length,
  generatedScenarioCount: generated.length,
  totalObservedOperations: aggregate.operations,
  successObserved: aggregate.successes > 0,
  retrySuccessObserved: aggregate.retrySuccesses > 0,
  retryBudgetExhaustionObserved: aggregate.retryBudgetExhausted > 0,
  nonIdempotentRetryRejectObserved: aggregate.nonIdempotentRejected > 0,
  breakerBulkheadRejectObserved: aggregate.bulkheadRejected > 0,
  breakerOpenRejectObserved: aggregate.circuitOpenRejected > 0,
  watermarkRejectObserved: aggregate.watermarkRejected > 0,
  providerHealthRejectObserved: aggregate.providerHealthRejected > 0,
  hardLimitRejectObserved: aggregate.hardLimitRejected > 0,
  criticalBypassObserved: aggregate.criticalBypass > 0,
  noProviderMutationOnRejectedFinals: aggregate.providerMutationsOnRejectedFinal === 0,
  admissionLeasesReleased: aggregate.admissionReleaseFailures === 0,
  expectedClassesMatched: aggregate.expectedClassMismatches === 0,
  snapshotsValidated: aggregate.snapshotFailures === 0,
  bootReportRecordsOverloadGovernanceProof: rt.report.executableProofs.storageLaneOverloadGovernanceModelProof === true,
  bootReportCarriesAdmissionHistoryModelProof: rt.report.executableProofs.storageLaneAdmissionHistoryModelProof === true,
  missingTraceKinds: requiredTraceKinds.filter((kind) => !hasKind(trace, kind)),
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => hasKind(trace, kind))
};
Object.entries(observations).forEach(([key, value]) => { if (typeof value === 'boolean') assert.equal(value, true, `${key} should be true`); });

const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed', generatedAt: new Date().toISOString(),
  slice: 'scheduler:storage-lane-overload-governance-model-proof',
  purpose: 'Compose storage-lane admission, provider-resilience, retry-budget, circuit-breaker/bulkhead, and fake-provider histories under a model oracle that checks rejection order, no-mutation boundaries, release accounting, and trace evidence before OPFS/browser spending.',
  observations,
  aggregate,
  targeted: targeted.map((row) => ({ name: row.name, final: row.final || row.finals || null, stats: row.snapshot.stats })),
  generated,
  trace: { count: trace.length, kinds: kinds(trace), requiredTraceKinds },
  nonClaims: [
    'No OPFS storage-lane overload-governance model proof.',
    'No browser Worker storage-lane overload-governance model proof.',
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
