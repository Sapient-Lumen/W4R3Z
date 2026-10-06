#!/usr/bin/env node
// BrowserRT rev0031 storage-lane retry-budget/admission proof.
// Fake-provider/virtual-tick proof only; no OPFS/browser retry budget, wall-clock, SLO, or production retry-storm safety claim.

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
  createRetryBudgetAdmissionController,
  createStorageLaneExecutor,
  createStorageLaneRetryController,
  createStorageLaneRetryPolicy,
  validateCrossLaneSchedulerSnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-STORAGE-LANE-RETRY-BUDGET-PROBE.json`);
function hasKind(trace, kind) { return trace.some((event) => event.kind === kind); }
function kinds(trace) { return [...new Set(trace.map((event) => event.kind))].sort(); }
function opState(controller, id) { const op = controller.operation(id); assert.ok(op, `operation ${id} should exist`); return op; }
function lastEvent(op, name) { return [...op.history].reverse().find((row) => row.event === name); }

const rt = await boot({ storageLaneRetryBudgetProof: true });
const retryPolicy = createStorageLaneRetryPolicy({ maxAttempts: 3, initialDelayTicks: 1, multiplier: 2, maxDelayTicks: 4, jitterTicks: 0, retryableCodes: ['BRT_STORAGE_INJECTED_FAULT'], nonRetryableCodes: ['BRT_STORAGE_NON_RETRYABLE'] });

function makeHarness(label, budgetOptions = {}) {
  const provider = createMemoryBlockStore({ name: `${label}-store`, provider: `${label}-fake-provider-v0`, quotaBytes: 4096, trace: rt.trace });
  const mailbox = createPersistedSpillMailbox({ label: `${label}-mailbox`, provider, memoryCapacityBytes: 0, maxFrameBytes: 128, deleteBlockOnAck: false, trace: rt.trace });
  const scheduler = createCrossLaneScheduler({
    label: `${label}-scheduler`,
    maxQueuedCost: 256,
    maxTaskCost: 32,
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 160 },
      { id: 'maintenance', rank: 20, capacity: 1, quantum: 64, maxQueuedCost: 96 }
    ],
    trace: rt.trace
  });
  const executor = createStorageLaneExecutor({ label: `${label}-executor`, scheduler, mailbox, trace: rt.trace, markUnhealthyOnError: true });
  const budget = createRetryBudgetAdmissionController({ label: `${label}-budget`, trace: rt.trace, ...budgetOptions });
  const retrier = createStorageLaneRetryController({ label: `${label}-retry`, executor, policy: retryPolicy, retryBudget: budget, trace: rt.trace });
  return { provider, mailbox, scheduler, executor, budget, retrier };
}

// Scenario 1: a retry consumes a retry-budget credit, releases active retry accounting, and succeeds only after explicit provider recovery.
const okHarness = makeHarness('rev0031-budget-success', { maxRetryCredits: 2, initialRetryCredits: 1, maxActiveRetries: 1, refillPerPrimarySuccess: 0 });
okHarness.provider.injectFault({ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT', message: 'first write transient fault' });
assert.equal(okHarness.retrier.submitMailboxEnqueue(okHarness.mailbox, 'budget-success-payload', { id: 'budget-success', priority: 'user-visible', cost: 1, idempotent: true }).accepted, true);
await okHarness.retrier.drainReady({ maxSteps: 5 });
const okAfterFailure = opState(okHarness.retrier, 'budget-success');
assert.equal(okAfterFailure.state, 'retry-delayed');
assert.equal(okHarness.provider.snapshot().blockCount, 0);
assert.equal(okHarness.scheduler.snapshotLane('storage').healthy, false);
assert.equal(okHarness.retrier.advanceToNextRetry().advanced, true);
okHarness.executor.markHealthy('storage', 'rev0031 budget-success provider recovered');
await okHarness.retrier.drainReady({ maxSteps: 5 });
const okFinal = opState(okHarness.retrier, 'budget-success');
assert.equal(okFinal.state, 'succeeded');
assert.equal(okFinal.attempts, 2);
assert.equal(okHarness.budget.snapshot().activeRetries, 0);
assert.equal(okHarness.budget.snapshot().stats.retryAccepted, 1);
assert.equal(okHarness.budget.snapshot().stats.retryReleased, 1);
assert.equal(okHarness.budget.snapshot().retryCredits, 0);

// Scenario 2: a retryable failure is not retried when the retry budget is exhausted.
const exhaustedHarness = makeHarness('rev0031-budget-exhausted', { maxRetryCredits: 1, initialRetryCredits: 0, maxActiveRetries: 1, refillPerPrimarySuccess: 0 });
exhaustedHarness.provider.injectFault({ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT', message: 'budget exhausted transient fault' });
assert.equal(exhaustedHarness.retrier.submitMailboxEnqueue(exhaustedHarness.mailbox, 'budget-exhausted-payload', { id: 'budget-exhausted', priority: 'background', cost: 1, idempotent: true }).accepted, true);
await exhaustedHarness.retrier.drainReady({ maxSteps: 5 });
assert.equal(exhaustedHarness.retrier.advanceToNextRetry().advanced, true);
exhaustedHarness.executor.markHealthy('storage', 'rev0031 exhausted scenario provider recovered');
await exhaustedHarness.retrier.drainReady({ maxSteps: 5 });
const exhaustedFinal = opState(exhaustedHarness.retrier, 'budget-exhausted');
assert.equal(exhaustedFinal.state, 'failed');
assert.equal(exhaustedFinal.attempts, 1);
assert.equal(exhaustedFinal.lastError.decision.reason, 'retry-budget-exhausted');
assert.equal(exhaustedHarness.provider.snapshot().blockCount, 0);
assert.equal(exhaustedHarness.budget.snapshot().stats.exhaustedRejected, 1);

// Scenario 3: non-idempotent retryable work is failed by the retry-budget gate even when credits exist.
const nonIdempotentHarness = makeHarness('rev0031-budget-nonidempotent', { maxRetryCredits: 2, initialRetryCredits: 2, maxActiveRetries: 1, requireIdempotent: true });
nonIdempotentHarness.provider.injectFault({ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT', message: 'non-idempotent transient fault' });
assert.equal(nonIdempotentHarness.retrier.submitMailboxEnqueue(nonIdempotentHarness.mailbox, 'budget-nonidempotent-payload', { id: 'budget-nonidempotent', priority: 'user-visible', cost: 1, idempotent: false }).accepted, true);
await nonIdempotentHarness.retrier.drainReady({ maxSteps: 5 });
assert.equal(nonIdempotentHarness.retrier.advanceToNextRetry().advanced, true);
nonIdempotentHarness.executor.markHealthy('storage', 'rev0031 non-idempotent scenario provider recovered');
await nonIdempotentHarness.retrier.drainReady({ maxSteps: 5 });
const nonIdempotentFinal = opState(nonIdempotentHarness.retrier, 'budget-nonidempotent');
assert.equal(nonIdempotentFinal.state, 'failed');
assert.equal(nonIdempotentFinal.lastError.decision.reason, 'retry-budget-rejected');
assert.equal(lastEvent(nonIdempotentFinal, 'retry-budget-gate').gate.reason, 'non-idempotent');
assert.equal(nonIdempotentHarness.budget.snapshot().stats.nonIdempotentRejected, 1);

// Scenario 4: direct budget accounting demonstrates active limit, provider health rejection, refill, and critical bypass semantics without scheduling another storage op.
const directBudget = createRetryBudgetAdmissionController({ label: 'rev0031-budget-direct', maxRetryCredits: 2, initialRetryCredits: 1, maxActiveRetries: 1, refillPerPrimarySuccess: 1, allowCriticalBypass: true, trace: rt.trace });
const firstLease = directBudget.tryAcquireRetry({ opId: 'direct-one', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
assert.equal(firstLease.accepted, true);
const activeLimit = directBudget.tryAcquireRetry({ opId: 'direct-two', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
assert.equal(activeLimit.accepted, false);
assert.equal(activeLimit.reason, 'active-retry-limit');
assert.equal(directBudget.releaseRetry(firstLease.leaseId, { ok: true }).released, true);
directBudget.markProviderUnhealthy('rev0031 direct provider unhealthy');
const providerHealthReject = directBudget.tryAcquireRetry({ opId: 'direct-three', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
assert.equal(providerHealthReject.accepted, false);
assert.equal(providerHealthReject.reason, 'provider-unhealthy');
directBudget.markProviderHealthy('rev0031 direct provider healthy');
const refill = directBudget.observePrimary({ ok: true, opId: 'direct-primary' });
assert.equal(refill.observed, true);
const secondLease = directBudget.tryAcquireRetry({ opId: 'direct-four', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
assert.equal(secondLease.accepted, true);
assert.equal(directBudget.releaseRetry(secondLease.leaseId, { ok: false }).released, true);
// Drain remaining non-bypass credit, then prove critical can bypass credit exhaustion but still releases active accounting.
assert.equal(directBudget.snapshot().retryCredits, 0);
const criticalLease = directBudget.tryAcquireRetry({ opId: 'direct-critical', attempt: 2, priority: 'critical', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
assert.equal(criticalLease.accepted, true);
assert.equal(criticalLease.reason, 'critical-bypass');
assert.equal(criticalLease.spentCredit, 0);
assert.equal(directBudget.releaseRetry(criticalLease.leaseId, { ok: true }).released, true);

const trace = rt.close();
const traceKinds = kinds(trace);
const requiredTraceKinds = [
  'retry-budget:create',
  'retry-budget:acquire',
  'retry-budget:release',
  'retry-budget:reject',
  'retry-budget:provider-unhealthy',
  'retry-budget:provider-healthy',
  'retry-budget:primary-observed',
  'retry-budget:refill',
  'storage-retry:retry-budget-gate',
  'storage-retry:retry-budget-release',
  'storage-retry:fail-final',
  'storage-retry:complete',
  'storage-lane:provider-unhealthy',
  'storage-lane:provider-healthy'
];
const observations = {
  retryBudgetControllerCreated: hasKind(trace, 'retry-budget:create'),
  storageLaneRetryControllerIntegratesBudget: hasKind(trace, 'storage-retry:retry-budget-gate'),
  retryCreditConsumedAndReleased: okHarness.budget.snapshot().stats.retryAccepted === 1 && okHarness.budget.snapshot().stats.retryReleased === 1 && okHarness.budget.snapshot().retryCredits === 0,
  successfulRetryAfterExplicitProviderRecovery: okFinal.state === 'succeeded' && okFinal.attempts === 2 && okHarness.mailbox.snapshot().queueDepth === 1,
  exhaustedBudgetRejectsRetryWithoutSecondProviderMutation: exhaustedFinal.state === 'failed' && exhaustedFinal.attempts === 1 && exhaustedFinal.lastError.decision.reason === 'retry-budget-exhausted' && exhaustedHarness.provider.snapshot().blockCount === 0,
  nonIdempotentRetryRejectedByGate: nonIdempotentFinal.state === 'failed' && lastEvent(nonIdempotentFinal, 'retry-budget-gate').gate.reason === 'non-idempotent',
  activeRetryLimitRejectsSecondRetry: activeLimit.reason === 'active-retry-limit',
  providerUnhealthyRejectsRetry: providerHealthReject.reason === 'provider-unhealthy',
  primaryObservationRefillsCredits: refill.gained === 1,
  criticalBypassUnderCreditExhaustion: criticalLease.accepted === true && criticalLease.reason === 'critical-bypass' && criticalLease.spentCredit === 0,
  allBudgetLeasesReleased: okHarness.budget.snapshot().activeRetries === 0 && directBudget.snapshot().activeRetries === 0,
  finalSchedulerSnapshotsValid: [okHarness, exhaustedHarness, nonIdempotentHarness].every((h) => validateCrossLaneSchedulerSnapshot(h.scheduler.snapshot()).ok),
  finalSchedulerAccountingEmpty: [okHarness, exhaustedHarness, nonIdempotentHarness].every((h) => h.scheduler.snapshot().queuedCount === 0 && h.scheduler.snapshot().inFlightCount === 0),
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => traceKinds.includes(kind)),
  bootReportRecordsStorageLaneRetryBudgetProof: rt.report.executableProofs.storageLaneRetryBudgetProof === true
};
for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  status: 'passed',
  slice: 'scheduler:storage-lane-retry-budget-proof',
  generatedAt: new Date().toISOString(),
  purpose: 'Fake-provider proof that storage-lane retry policy is governed by an explicit retry-budget/admission controller before OPFS/browser spending.',
  observations,
  counts: {
    traceEvents: trace.length,
    retryBudgetControllers: 4,
    successfulRetryProviderBlocks: okHarness.provider.snapshot().blockCount,
    exhaustedProviderBlocks: exhaustedHarness.provider.snapshot().blockCount,
    nonIdempotentProviderBlocks: nonIdempotentHarness.provider.snapshot().blockCount,
    directBudgetAcceptedRetries: directBudget.snapshot().stats.retryAccepted,
    directBudgetRejectedRetries: directBudget.snapshot().stats.retryRejected
  },
  snapshots: {
    successfulRetry: { operation: okFinal, retryBudget: okHarness.budget.snapshot(), retrier: okHarness.retrier.snapshot(), scheduler: okHarness.scheduler.snapshot(), mailbox: okHarness.mailbox.snapshot() },
    exhaustedRetry: { operation: exhaustedFinal, retryBudget: exhaustedHarness.budget.snapshot(), retrier: exhaustedHarness.retrier.snapshot(), scheduler: exhaustedHarness.scheduler.snapshot(), mailbox: exhaustedHarness.mailbox.snapshot() },
    nonIdempotentRetry: { operation: nonIdempotentFinal, retryBudget: nonIdempotentHarness.budget.snapshot(), retrier: nonIdempotentHarness.retrier.snapshot(), scheduler: nonIdempotentHarness.scheduler.snapshot(), mailbox: nonIdempotentHarness.mailbox.snapshot() },
    directBudget: directBudget.snapshot()
  },
  traceKinds,
  requiredTraceKinds,
  nonClaims: [
    'No OPFS storage-lane retry-budget proof.',
    'No browser Worker storage-lane retry-budget proof.',
    'No retry-storm safety or production overload-governance claim.',
    'No wall-clock timer, throughput, latency, or SLO claim.',
    'No durability, fsync, quota, eviction, or crash-recovery claim.',
    'No exactly-once delivery claim.',
    'No cross-browser conformance claim.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
