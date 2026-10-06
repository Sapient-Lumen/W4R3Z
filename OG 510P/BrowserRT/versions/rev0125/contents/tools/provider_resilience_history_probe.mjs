#!/usr/bin/env node
// BrowserRT rev0033 provider-integrated resilience history proof.
// Fake-provider/virtual-tick only: no OPFS/browser/durability/performance/SLO/production resilience claim.

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
  validateProviderResilienceHistorySnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-PROVIDER-RESILIENCE-HISTORY-PROBE.json`);
function kinds(trace) { return [...new Set(trace.map((event) => event.kind))].sort(); }
function hasKind(trace, kind) { return trace.some((event) => event.kind === kind); }

function makeHarness(rt, label, { faults = [], breaker = {}, budget = {}, policy = {}, memoryCapacityBytes = 8 } = {}) {
  const provider = createMemoryBlockStore({ name: `${label}:provider`, provider: 'provider-resilience-memory-fake-v0', faults, trace: rt.trace });
  const mailbox = createPersistedSpillMailbox({ label: `${label}:mailbox`, provider, trace: rt.trace, memoryCapacityBytes, deleteBlockOnAck: false });
  const scheduler = createCrossLaneScheduler({ label: `${label}:scheduler`, trace: rt.trace, lanes: [
    { id: 'storage', rank: 80, capacity: 1, quantum: 64, maxQueuedCost: 256 },
    { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
  ]});
  const executor = createStorageLaneExecutor({ label: `${label}:executor`, scheduler, mailbox, trace: rt.trace });
  const breakerCtl = createCircuitBreakerBulkheadController({ label: `${label}:breaker`, maxConcurrent: 1, slidingWindowSize: 4, minimumCalls: 4, failureRateThreshold: 75, slowCallRateThreshold: 100, openDurationTicks: 2, halfOpenMaxCalls: 1, trace: rt.trace, ...breaker });
  const retryBudget = createRetryBudgetAdmissionController({ label: `${label}:retry-budget`, maxRetryCredits: 8, initialRetryCredits: 2, maxActiveRetries: 1, refillPerPrimarySuccess: 1, refillPerPrimaryFailure: 0, requireIdempotent: true, trace: rt.trace, ...budget });
  const runner = createProviderResilienceHistoryRunner({ label: `${label}:runner`, executor, mailbox, breaker: breakerCtl, retryBudget, retryPolicy: { maxAttempts: 3, initialDelayTicks: 1, maxDelayTicks: 2, jitterTicks: 0, ...policy }, trace: rt.trace });
  return { provider, mailbox, scheduler, executor, breaker: breakerCtl, retryBudget, runner };
}

const rt = await boot({ providerResilienceHistoryProof: true, storageLaneRetryBudgetProof: true, circuitBreakerBulkheadProof: true });

// Scenario 1: transient provider failure, retry-budget acquisition, retry success.
const transient = makeHarness(rt, 'rev0033-transient', { faults: [{ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT', message: 'first transient write failure' }], breaker: { minimumCalls: 3, failureRateThreshold: 100, openDurationTicks: 1 }, budget: { initialRetryCredits: 2 } });
const transientHistory = await transient.runner.runMailboxEnqueue({ id: 'transient-retry-success', payload: 'transient payload', priority: 'user-visible' });
assert.equal(transientHistory.final.ok, true);
assert.equal(transientHistory.final.reason, 'retry-success');
assert.equal(transientHistory.attempts.length, 2);
assert.equal(transient.runner.snapshot().stats.retriesAccepted, 1);

// Scenario 2: failures open the circuit; open circuit rejects without provider mutation; virtual tick allows half-open success.
const breakerHarness = makeHarness(rt, 'rev0033-breaker', { faults: [
  { op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT' }
], breaker: { slidingWindowSize: 2, minimumCalls: 2, failureRateThreshold: 50, openDurationTicks: 2, halfOpenMaxCalls: 1 }, budget: { initialRetryCredits: 0 }, policy: { maxAttempts: 1 } });
const failA = await breakerHarness.runner.runMailboxEnqueue({ id: 'breaker-fail-a', payload: 'a', maxAttempts: 1 });
const failB = await breakerHarness.runner.runMailboxEnqueue({ id: 'breaker-fail-b', payload: 'b', maxAttempts: 1 });
assert.equal(failA.final.ok, false);
assert.equal(failB.final.ok, false);
assert.equal(breakerHarness.breaker.snapshot().state, 'open');
const beforeOpenRejectProviderBlocks = breakerHarness.provider.snapshot().blockCount;
const openReject = await breakerHarness.runner.runMailboxEnqueue({ id: 'breaker-open-reject', payload: 'c', maxAttempts: 1 });
assert.equal(openReject.final.ok, false);
assert.equal(openReject.final.reason, 'breaker:circuit-open');
const afterOpenRejectProviderBlocks = breakerHarness.provider.snapshot().blockCount;
assert.equal(afterOpenRejectProviderBlocks, beforeOpenRejectProviderBlocks);
breakerHarness.breaker.advanceTicks(2);
breakerHarness.executor.markHealthy('storage', 'rev0033-half-open-recovery');
const halfOpenRecovery = await breakerHarness.runner.runMailboxEnqueue({ id: 'breaker-half-open-recovery', payload: 'd', maxAttempts: 1 });
assert.equal(halfOpenRecovery.final.ok, true);
assert.equal(breakerHarness.breaker.snapshot().state, 'closed');

// Scenario 3: retry budget rejection stops retries without a second provider mutation.
const budgetHarness = makeHarness(rt, 'rev0033-budget', { faults: [{ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT' }], breaker: { minimumCalls: 3, failureRateThreshold: 100 }, budget: { maxRetryCredits: 0, initialRetryCredits: 0, maxActiveRetries: 1 }, policy: { maxAttempts: 3 } });
const budgetBefore = budgetHarness.provider.snapshot();
const budgetRejected = await budgetHarness.runner.runMailboxEnqueue({ id: 'budget-rejects-retry', payload: 'budget', priority: 'background' });
assert.equal(budgetRejected.final.ok, false);
assert.equal(budgetRejected.final.reason, 'retry-budget:retry-budget-exhausted');
assert.equal(budgetHarness.provider.snapshot().stats.puts, budgetBefore.stats.puts);
assert.equal(budgetHarness.runner.snapshot().stats.retryBudgetRejected, 1);

// Scenario 4: bulkhead capacity rejection has no provider mutation.
const bulkheadHarness = makeHarness(rt, 'rev0033-bulkhead', { breaker: { maxConcurrent: 1, minimumCalls: 2, slidingWindowSize: 2 } });
const manualLease = bulkheadHarness.breaker.tryAcquire({ opId: 'manual-held-lease', priority: 'user-visible', kind: 'test-hold' });
assert.equal(manualLease.accepted, true);
const bulkheadBefore = bulkheadHarness.provider.snapshot().blockCount;
const bulkheadRejected = await bulkheadHarness.runner.runMailboxEnqueue({ id: 'bulkhead-rejects', payload: 'bulkhead', priority: 'background' });
assert.equal(bulkheadRejected.final.reason, 'breaker:bulkhead-full');
assert.equal(bulkheadHarness.provider.snapshot().blockCount, bulkheadBefore);
bulkheadHarness.breaker.release(manualLease.leaseId, { ok: true, durationTicks: 1 });

// Generated histories: deterministic seeds combining faults, retries, budget, and circuit state.
const generated = [];
for (let seed = 1; seed <= 12; seed += 1) {
  const firstFault = seed % 2 === 0;
  const secondFault = seed % 5 === 0;
  const faults = [];
  if (firstFault) faults.push({ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT' });
  if (secondFault) faults.push({ op: 'put', at: 2, code: 'BRT_STORAGE_INJECTED_FAULT' });
  const h = makeHarness(rt, `rev0033-generated-${seed}`, {
    faults,
    breaker: { slidingWindowSize: 3, minimumCalls: 3, failureRateThreshold: 100, openDurationTicks: 1 },
    budget: { initialRetryCredits: seed % 3 === 0 ? 0 : 2, maxRetryCredits: 4 },
    policy: { maxAttempts: seed % 3 === 0 ? 2 : 3 }
  });
  const row = await h.runner.runMailboxEnqueue({ id: `generated-${seed}`, payload: `payload-${seed}`, priority: seed % 4 === 0 ? 'critical' : 'user-visible', idempotent: seed % 7 !== 0 });
  const snapshot = h.runner.snapshot();
  assert.equal(validateProviderResilienceHistorySnapshot(snapshot).ok, true);
  generated.push({ seed, final: row.final, attempts: row.attempts.length, snapshot: { stats: snapshot.stats, breakerState: snapshot.breaker.state, providerBlocks: snapshot.mailbox.providerSnapshot.blockCount, retryCredits: snapshot.retryBudget.retryCredits } });
}

const allRunners = [transient, breakerHarness, budgetHarness, bulkheadHarness].map((h) => h.runner);
const validations = allRunners.map((runner) => validateProviderResilienceHistorySnapshot(runner.snapshot()));
validations.forEach((v) => assert.equal(v.ok, true, v.errors.join('; ')));
const trace = rt.close();
const traceKinds = kinds(trace);
const requiredTraceKinds = [
  'provider-resilience:create',
  'provider-resilience:operation-start',
  'provider-resilience:attempt',
  'provider-resilience:retry-budget-gate',
  'provider-resilience:breaker-reject',
  'provider-resilience:operation-final',
  'storage-lane:dispatch',
  'storage-lane:complete',
  'storage-lane:error',
  'retry-budget:acquire',
  'retry-budget:reject',
  'resilience:state-transition'
];
const observations = {
  runnerCreated: true,
  transientRetrySucceeded: transientHistory.final.ok === true && transientHistory.attempts.length === 2,
  retryBudgetAcquiredBeforeRetry: transient.runner.snapshot().stats.retriesAccepted >= 1,
  providerFailureObserved: transient.runner.snapshot().stats.providerFailures >= 1,
  circuitOpenedAfterFailures: failA.final.ok === false && failB.final.ok === false && openReject.final.reason === 'breaker:circuit-open',
  openCircuitCausedNoProviderMutation: openReject.final.noProviderMutation === true && afterOpenRejectProviderBlocks === beforeOpenRejectProviderBlocks,
  halfOpenRecoveryClosedCircuit: halfOpenRecovery.final.ok === true && breakerHarness.breaker.snapshot().state === 'closed',
  retryBudgetRejectionStopsRetry: budgetRejected.final.reason === 'retry-budget:retry-budget-exhausted' && budgetHarness.runner.snapshot().stats.retryBudgetRejected === 1,
  bulkheadRejectionCausedNoProviderMutation: bulkheadRejected.final.noProviderMutation === true && bulkheadHarness.provider.snapshot().blockCount === bulkheadBefore,
  generatedHistoryCount: generated.length,
  generatedHistoriesIncludeSuccess: generated.some((row) => row.final.ok === true),
  generatedHistoriesIncludeFailure: generated.some((row) => row.final.ok === false),
  snapshotsValidate: validations.every((v) => v.ok),
  finalLeaseAccountingEmpty: allRunners.every((runner) => runner.snapshot().breaker.leaseCount === 0 && runner.snapshot().retryBudget.leaseCount === 0),
  bootReportRecordsProviderResilienceHistoryProof: rt.report.executableProofs.providerResilienceHistoryProof === true,
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => hasKind(trace, kind))
};
Object.entries(observations).forEach(([name, value]) => {
  if (name === 'generatedHistoryCount') assert.equal(value, 12);
  else assert.equal(value, true, `${name} should be true`);
});

const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed', generatedAt: new Date().toISOString(),
  slice: 'scheduler:provider-resilience-history-proof',
  purpose: 'Compose storage-lane scheduling, fake persisted-spill provider behavior, retry policy, retry-budget admission, and circuit-breaker/bulkhead semantics under deterministic fake-provider histories.',
  observations,
  histories: {
    transient: transientHistory,
    breaker: { failA, failB, openReject, halfOpenRecovery },
    budgetRejected,
    bulkheadRejected,
    generated
  },
  snapshots: {
    transient: transient.runner.snapshot(),
    breaker: breakerHarness.runner.snapshot(),
    budget: budgetHarness.runner.snapshot(),
    bulkhead: bulkheadHarness.runner.snapshot()
  },
  trace: { count: trace.length, kinds: traceKinds, requiredTraceKinds },
  nonClaims: [
    'No OPFS provider-resilience proof.',
    'No browser Worker provider-resilience proof.',
    'No production resilience, retry-storm, circuit-breaker, bulkhead, retry-budget, storage-lane, or overload-governance claim.',
    'No wall-clock timer, throughput, latency, fairness, SLO, durability, fsync, quota, eviction, crash-recovery, or exactly-once delivery claim.',
    'No exhaustive model checking or formal verification claim.',
    'No cross-browser conformance claim.',
    'No WebGPU proof.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
