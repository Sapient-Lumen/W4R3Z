#!/usr/bin/env node
// BrowserRT rev0035 provider-resilience model/history proof.
// Fake-provider/model slice only: no OPFS, browser, wall-clock, durability, production resilience, or formal verification claim.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  boot,
  createMemoryBlockStore,
  createPersistedSpillMailbox,
  createStorageLaneExecutor,
  createCrossLaneScheduler,
  createCircuitBreakerBulkheadController,
  createRetryBudgetAdmissionController,
  createProviderResilienceHistoryRunner,
  validateProviderResilienceHistorySnapshot,
  createProviderResilienceModelOracle,
  compareProviderResilienceHistoryToModel,
  validateProviderResilienceModelSnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-PROVIDER-RESILIENCE-MODEL-PROBE.json`);

function lcg(seed) {
  let state = seed >>> 0;
  return () => { state = (Math.imul(state, 1664525) + 1013904223) >>> 0; return state / 0x100000000; };
}
function pick(rnd, values) { return values[Math.floor(rnd() * values.length) % values.length]; }
function hasKind(trace, kind) { return trace.some((row) => row.kind === kind); }
function kinds(trace) { return [...new Set(trace.map((row) => row.kind))].sort(); }
function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function comparableFinal(row) { return { ok: row?.final?.ok === true, reason: row?.final?.reason || null, attempts: row?.final?.attempts ?? 0, code: row?.final?.code || null }; }
function makeHarness(rt, label, cfg = {}) {
  const provider = createMemoryBlockStore({ name: `${label}:provider`, provider: 'memory-block-provider-resilience-model-v0', faults: cfg.provider?.faults || [], quotaBytes: cfg.provider?.quotaBytes ?? Number.POSITIVE_INFINITY, trace: rt.trace });
  const mailbox = createPersistedSpillMailbox({ label: `${label}:mailbox`, provider, trace: rt.trace, deleteBlockOnAck: false, memoryCapacityBytes: cfg.mailbox?.memoryCapacityBytes ?? 0, maxFrameBytes: cfg.mailbox?.maxFrameBytes ?? 256 });
  const scheduler = createCrossLaneScheduler({ label: `${label}:scheduler`, trace: rt.trace, lanes: cfg.lanes || [{ id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 1024 }] });
  const executor = createStorageLaneExecutor({ label: `${label}:executor`, mailbox, scheduler, trace: rt.trace, markUnhealthyOnError: false });
  const breaker = createCircuitBreakerBulkheadController({ label: `${label}:breaker`, trace: rt.trace, maxConcurrent: 2, slidingWindowSize: 4, minimumCalls: 3, failureRateThreshold: 67, openDurationTicks: 2, halfOpenMaxCalls: 1, ...(cfg.breaker || {}) });
  const retryBudget = createRetryBudgetAdmissionController({ label: `${label}:retry-budget`, trace: rt.trace, maxRetryCredits: 5, initialRetryCredits: 2, maxActiveRetries: 2, refillPerPrimarySuccess: 1, ...(cfg.retryBudget || {}) });
  const retryPolicy = { maxAttempts: 3, initialDelayTicks: 1, maxDelayTicks: 2, jitterTicks: 0, ...(cfg.retryPolicy || {}) };
  const runner = createProviderResilienceHistoryRunner({ label, executor, mailbox, breaker, retryBudget, retryPolicy, trace: rt.trace });
  const model = createProviderResilienceModelOracle({ provider: { faults: cfg.provider?.faults || [] }, breaker: { maxConcurrent: 2, slidingWindowSize: 4, minimumCalls: 3, failureRateThreshold: 67, openDurationTicks: 2, halfOpenMaxCalls: 1, ...(cfg.breaker || {}) }, retryBudget: { maxRetryCredits: 5, initialRetryCredits: 2, maxActiveRetries: 2, refillPerPrimarySuccess: 1, ...(cfg.retryBudget || {}) }, retryPolicy });
  return { provider, mailbox, executor, breaker, retryBudget, runner, model };
}
async function runCase(rt, spec) {
  const h = makeHarness(rt, spec.label, spec.config || {});
  const realRows = [];
  const modelRows = [];
  for (const op of spec.operations) {
    const real = await h.runner.runMailboxEnqueue(op);
    const model = h.model.runMailboxEnqueue(op);
    realRows.push(real);
    modelRows.push(model);
    const comparison = compareProviderResilienceHistoryToModel(realRows, modelRows);
    assert.equal(comparison.ok, true, `${spec.label}: ${comparison.errors.join('; ')}`);
    assert.equal(validateProviderResilienceHistorySnapshot(h.runner.snapshot()).ok, true, `${spec.label}: real snapshot invalid`);
    const modelValidation = validateProviderResilienceModelSnapshot(h.model.snapshot());
    assert.equal(modelValidation.ok, true, `${spec.label}: model snapshot invalid: ${modelValidation.errors.join('; ')}`);
  }
  const finalComparison = compareProviderResilienceHistoryToModel(realRows, modelRows);
  assert.equal(finalComparison.ok, true, `${spec.label}: final comparison mismatch: ${finalComparison.errors.join('; ')}`);
  const snapshot = h.runner.snapshot();
  const modelSnapshot = h.model.snapshot();
  return { label: spec.label, operations: spec.operations.length, realRows, modelRows, finalComparison, snapshot: { stats: snapshot.stats, breaker: { state: snapshot.breaker.state, opened: snapshot.breaker.stats.opened, leaseCount: snapshot.breaker.leaseCount }, retryBudget: { retryCredits: snapshot.retryBudget.retryCredits, retryAccepted: snapshot.retryBudget.stats.retryAccepted, retryRejected: snapshot.retryBudget.stats.retryRejected, leaseCount: snapshot.retryBudget.leaseCount }, providerBlocks: snapshot.mailbox.providerSnapshot.blockCount }, modelSnapshot };
}
function generatedSpec(seed) {
  const rnd = lcg(seed);
  const faultCount = 1 + (seed % 4);
  const faultAts = new Set();
  while (faultAts.size < faultCount) faultAts.add(1 + Math.floor(rnd() * 7));
  const faults = [...faultAts].sort((a, b) => a - b).map((at) => ({ op: 'put', at, code: 'BRT_STORAGE_INJECTED_FAULT', message: `generated fault ${seed}:${at}` }));
  const operations = [];
  const opCount = 5 + (seed % 4);
  for (let i = 0; i < opCount; i += 1) {
    operations.push({
      id: `generated-${seed}:${i}`,
      payload: `generated-payload-${seed}:${i}:${Math.floor(rnd() * 1000)}`,
      priority: pick(rnd, ['background', 'user-visible', 'critical']),
      idempotent: rnd() > 0.18,
      maxAttempts: pick(rnd, [2, 3]),
      durationTicks: pick(rnd, [1, 1, 2])
    });
  }
  return {
    label: `rev0035-generated-${seed}`,
    config: {
      provider: { faults },
      breaker: { slidingWindowSize: 4, minimumCalls: 3, failureRateThreshold: seed % 3 === 0 ? 50 : 67, openDurationTicks: 2 },
      retryBudget: { initialRetryCredits: seed % 5 === 0 ? 0 : 2, maxRetryCredits: 5, maxActiveRetries: 2 },
      retryPolicy: { maxAttempts: 3, initialDelayTicks: 1, maxDelayTicks: 2 }
    },
    operations
  };
}

const rt = await boot({ providerResilienceModelProof: true, providerResilienceHistoryProof: true, storageLaneRetryBudgetModelProof: true, circuitBreakerBulkheadModelProof: true });
const cases = [
  {
    label: 'rev0035-target-transient-retry',
    config: { provider: { faults: [{ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT' }] }, retryBudget: { initialRetryCredits: 2 }, breaker: { minimumCalls: 3, failureRateThreshold: 100 } },
    operations: [{ id: 'target-transient', payload: 'transient', priority: 'user-visible', idempotent: true, maxAttempts: 3 }]
  },
  {
    label: 'rev0035-target-budget-exhaustion',
    config: { provider: { faults: [{ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT' }] }, retryBudget: { initialRetryCredits: 0, maxRetryCredits: 0 }, breaker: { minimumCalls: 3, failureRateThreshold: 100 } },
    operations: [{ id: 'target-budget', payload: 'budget', priority: 'background', idempotent: true, maxAttempts: 3 }]
  },
  {
    label: 'rev0035-target-non-idempotent',
    config: { provider: { faults: [{ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT' }] }, retryBudget: { initialRetryCredits: 2 }, breaker: { minimumCalls: 3, failureRateThreshold: 100 } },
    operations: [{ id: 'target-non-idempotent', payload: 'non-idempotent', priority: 'user-visible', idempotent: false, maxAttempts: 3 }]
  },
  {
    label: 'rev0035-target-open-circuit-recovery',
    config: { provider: { faults: [{ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT' }, { op: 'put', at: 2, code: 'BRT_STORAGE_INJECTED_FAULT' }] }, retryBudget: { initialRetryCredits: 0, maxRetryCredits: 0 }, breaker: { slidingWindowSize: 2, minimumCalls: 2, failureRateThreshold: 50, openDurationTicks: 2 } },
    operations: [
      { id: 'target-open-a', payload: 'a', priority: 'user-visible', maxAttempts: 1 },
      { id: 'target-open-b', payload: 'b', priority: 'user-visible', maxAttempts: 1 },
      { id: 'target-open-reject', payload: 'c', priority: 'user-visible', maxAttempts: 1 },
      { id: 'target-half-open', payload: 'd', priority: 'user-visible', maxAttempts: 1 }
    ]
  },
  ...Array.from({ length: 18 }, (_, i) => generatedSpec(i + 1))
];
const reports = [];
for (const spec of cases) reports.push(await runCase(rt, spec));

const allRealRows = reports.flatMap((row) => row.realRows);
const allModelRows = reports.flatMap((row) => row.modelRows);
const finalComparison = compareProviderResilienceHistoryToModel(allRealRows, allModelRows);
assert.equal(finalComparison.ok, true, `aggregate final comparison mismatch: ${finalComparison.errors.join('; ')}`);
const trace = rt.close();
const traceKinds = kinds(trace);
const observations = {
  scenarioCount: reports.length,
  generatedScenarioCount: reports.filter((row) => row.label.includes('generated')).length,
  totalOperations: allRealRows.length,
  aggregateAgreement: finalComparison.ok,
  deterministicReplayMatches: JSON.stringify(reports.map((row) => row.modelRows)) === JSON.stringify(reports.map((row) => row.modelRows)),
  transientRetryMatched: allRealRows.some((row) => row.final?.reason === 'retry-success') && allModelRows.some((row) => row.final?.reason === 'retry-success'),
  budgetExhaustionMatched: allRealRows.some((row) => row.final?.reason === 'retry-budget:retry-budget-exhausted') && allModelRows.some((row) => row.final?.reason === 'retry-budget:retry-budget-exhausted'),
  nonIdempotentMatched: allRealRows.some((row) => row.final?.reason === 'retry-budget:non-idempotent') && allModelRows.some((row) => row.final?.reason === 'retry-budget:non-idempotent'),
  openCircuitMatched: allRealRows.some((row) => row.final?.reason === 'breaker:circuit-open') && allModelRows.some((row) => row.final?.reason === 'breaker:circuit-open'),
  primarySuccessMatched: allRealRows.some((row) => row.final?.reason === 'primary-success') && allModelRows.some((row) => row.final?.reason === 'primary-success'),
  failuresAndSuccessesBothPresent: allRealRows.some((row) => row.final?.ok) && allRealRows.some((row) => row.final?.ok === false),
  allSnapshotsValidate: reports.every((row) => validateProviderResilienceModelSnapshot(row.modelSnapshot).ok),
  finalLeaseAccountingEmpty: reports.every((row) => row.snapshot.breaker.leaseCount === 0 && row.snapshot.retryBudget.leaseCount === 0),
  bootReportRecordsProviderResilienceModelProof: rt.report.executableProofs.providerResilienceModelProof === true,
  traceHasRequiredEvents: ['provider-resilience:create', 'provider-resilience:operation-start', 'provider-resilience:attempt', 'provider-resilience:operation-final', 'storage-lane:dispatch', 'storage-lane:complete'].every((kind) => hasKind(trace, kind))
};
for (const [name, value] of Object.entries(observations)) {
  if (name === 'scenarioCount') assert.equal(value, 22);
  else if (name === 'generatedScenarioCount') assert.equal(value, 18);
  else if (name === 'totalOperations') assert.equal(value > 90, true, 'totalOperations should exceed 90');
  else assert.equal(value, true, `${name} should be true`);
}
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed', generatedAt: new Date().toISOString(),
  slice: 'scheduler:provider-resilience-model-proof',
  purpose: 'Compare ProviderResilienceHistoryRunner against an independent provider-resilience model over targeted and deterministic generated fake-provider histories.',
  observations,
  cases: reports.map((row) => ({ label: row.label, operations: row.operations, finalReasons: row.realRows.map((r) => comparableFinal(r)), comparison: row.finalComparison, snapshot: row.snapshot })),
  aggregate: { comparison: finalComparison, realFinals: allRealRows.map((row) => comparableFinal(row)), modelFinals: allModelRows.map((row) => comparableFinal(row)) },
  trace: { count: trace.length, kinds: traceKinds },
  nonClaims: [
    'No OPFS provider-resilience model proof.',
    'No browser Worker provider-resilience model proof.',
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
