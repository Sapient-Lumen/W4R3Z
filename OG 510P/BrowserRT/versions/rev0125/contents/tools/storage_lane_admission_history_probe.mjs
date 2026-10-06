#!/usr/bin/env node
// BrowserRT rev0035 storage-lane admission-history proof.
// Fake-provider/release-tier proof only: no OPFS, browser Worker, wall-clock, durability, production overload-governance, or exactly-once claim.
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
  validateStorageLaneAdmissionHistorySnapshot,
  createWatermarkAdmissionController
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-STORAGE-LANE-ADMISSION-HISTORY-PROBE.json`);

function hasKind(trace, kind) { return trace.some((row) => row.kind === kind); }
function kinds(trace) { return [...new Set(trace.map((row) => row.kind))].sort(); }
function makeHarness(rt, label, cfg = {}) {
  const provider = createMemoryBlockStore({ name: `${label}:provider`, provider: 'memory-storage-admission-history-v0', faults: cfg.provider?.faults || [], quotaBytes: cfg.provider?.quotaBytes ?? Number.POSITIVE_INFINITY, trace: rt.trace });
  const mailbox = createPersistedSpillMailbox({ label: `${label}:mailbox`, provider, trace: rt.trace, deleteBlockOnAck: false, memoryCapacityBytes: 0, maxFrameBytes: cfg.mailbox?.maxFrameBytes ?? 512 });
  const scheduler = createCrossLaneScheduler({ label: `${label}:scheduler`, trace: rt.trace, lanes: cfg.lanes || [{ id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 2048 }] });
  const executor = createStorageLaneExecutor({ label: `${label}:executor`, mailbox, scheduler, trace: rt.trace, markUnhealthyOnError: false });
  const breaker = createCircuitBreakerBulkheadController({ label: `${label}:breaker`, trace: rt.trace, maxConcurrent: 2, slidingWindowSize: 4, minimumCalls: 3, failureRateThreshold: 67, openDurationTicks: 2, halfOpenMaxCalls: 1, ...(cfg.breaker || {}) });
  const retryBudget = createRetryBudgetAdmissionController({ label: `${label}:retry-budget`, trace: rt.trace, maxRetryCredits: 4, initialRetryCredits: 2, maxActiveRetries: 2, refillPerPrimarySuccess: 1, ...(cfg.retryBudget || {}) });
  const resilienceRunner = createProviderResilienceHistoryRunner({ label: `${label}:resilience`, executor, mailbox, breaker, retryBudget, retryPolicy: { maxAttempts: 3, initialDelayTicks: 1, maxDelayTicks: 2, jitterTicks: 0, ...(cfg.retryPolicy || {}) }, trace: rt.trace });
  const admission = createWatermarkAdmissionController({ label: `${label}:admission`, lowWatermarkBytes: cfg.admission?.lowWatermarkBytes ?? 0, highWatermarkBytes: cfg.admission?.highWatermarkBytes ?? 8, hardLimitBytes: cfg.admission?.hardLimitBytes ?? 24, criticalMinPriority: 'user-blocking', rejectMinPriorityWhileCongested: 'user-visible', trace: rt.trace });
  const runner = createStorageLaneAdmissionHistoryRunner({ label, admission, resilienceRunner, mailbox, trace: rt.trace });
  return { provider, mailbox, scheduler, executor, breaker, retryBudget, resilienceRunner, admission, runner };
}

const rt = await boot({ storageLaneAdmissionHistoryProof: true, providerResilienceHistoryProof: true, retryBudgetAdmissionProof: true });

// Targeted success and transient retry under admission lease.
const success = makeHarness(rt, 'rev0035-success');
const successRow = await success.runner.runMailboxEnqueue({ id: 'success', payload: 'ok-payload', priority: 'user-visible', bytes: 4, maxAttempts: 2 });
assert.equal(successRow.final.ok, true);
const transient = makeHarness(rt, 'rev0035-transient', { provider: { faults: [{ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT' }] }, breaker: { minimumCalls: 3, failureRateThreshold: 100 }, retryBudget: { initialRetryCredits: 2 } });
const transientRow = await transient.runner.runMailboxEnqueue({ id: 'transient', payload: 'retry-payload', priority: 'user-visible', bytes: 5, idempotent: true, maxAttempts: 3 });
assert.equal(transientRow.final.ok, true);
assert.equal(transientRow.final.reason, 'retry-success');

// Watermark rejection: hold a critical lease to make the admission controller congested, then verify low-priority no-mutation rejection.
const watermark = makeHarness(rt, 'rev0035-watermark');
const held = watermark.admission.tryAdmit({ bytes: 8, priority: 'critical', label: 'held-congestion' });
assert.equal(held.admitted, true);
const beforeWatermarkBlocks = watermark.provider.snapshot().blockCount;
const watermarkReject = await watermark.runner.runMailboxEnqueue({ id: 'watermark-reject', payload: 'should-not-store', priority: 'background', bytes: 2, maxAttempts: 1 });
assert.equal(watermarkReject.final.ok, false);
assert.equal(watermarkReject.final.disposition, 'rejected-watermark');
assert.equal(watermarkReject.final.noProviderMutation, true);
assert.equal(watermark.provider.snapshot().blockCount, beforeWatermarkBlocks);
watermark.admission.release(held.leaseId, { outcome: 'test-held-release' });

// Critical bypass while congested must admit and execute, then release the admission lease.
const bypassHeld = watermark.admission.tryAdmit({ bytes: 8, priority: 'critical', label: 'held-bypass' });
assert.equal(bypassHeld.admitted, true);
const criticalBypass = await watermark.runner.runMailboxEnqueue({ id: 'critical-bypass', payload: 'critical-goes-through', priority: 'critical', bytes: 2, maxAttempts: 1 });
assert.equal(criticalBypass.admission.bypass, true);
assert.equal(criticalBypass.final.ok, true);
watermark.admission.release(bypassHeld.leaseId, { outcome: 'test-held-release-2' });
assert.equal(watermark.admission.snapshot().leaseCount, 0);

// Provider-health gate at admission layer, then recovery.
const health = makeHarness(rt, 'rev0035-health');
health.runner.markAdmissionProviderUnhealthy('simulated-storage-unhealthy');
const beforeHealthBlocks = health.provider.snapshot().blockCount;
const healthReject = await health.runner.runMailboxEnqueue({ id: 'health-reject', payload: 'blocked', priority: 'background', bytes: 3, maxAttempts: 1 });
assert.equal(healthReject.final.disposition, 'rejected-provider-health');
assert.equal(healthReject.final.noProviderMutation, true);
assert.equal(health.provider.snapshot().blockCount, beforeHealthBlocks);
health.runner.markAdmissionProviderHealthy('simulated-storage-recovered');
const healthRecovery = await health.runner.runMailboxEnqueue({ id: 'health-recovery', payload: 'after-health', priority: 'background', bytes: 3, maxAttempts: 1 });
assert.equal(healthRecovery.final.ok, true);

// Hard limit rejection must be explicit and no-mutation.
const hardLimit = makeHarness(rt, 'rev0035-hard-limit', { admission: { highWatermarkBytes: 8, hardLimitBytes: 12 } });
const beforeHardBlocks = hardLimit.provider.snapshot().blockCount;
const hardReject = await hardLimit.runner.runMailboxEnqueue({ id: 'hard-reject', payload: 'too-large', priority: 'critical', bytes: 13, maxAttempts: 1 });
assert.equal(hardReject.final.disposition, 'rejected-hard-limit');
assert.equal(hardReject.final.noProviderMutation, true);
assert.equal(hardLimit.provider.snapshot().blockCount, beforeHardBlocks);

const snapshots = [success, transient, watermark, health, hardLimit].map((h) => h.runner.snapshot());
const validations = snapshots.map((snapshot) => validateStorageLaneAdmissionHistorySnapshot(snapshot));
validations.forEach((validation) => assert.equal(validation.ok, true, validation.errors.join('; ')));
const finalLeaseAccountingEmpty = [success, transient, watermark, health, hardLimit].every((h) => h.admission.snapshot().leaseCount === 0 && h.breaker.snapshot().leaseCount === 0 && h.retryBudget.snapshot().leaseCount === 0);
assert.equal(finalLeaseAccountingEmpty, true);

const trace = rt.close();
const requiredTraceKinds = [
  'storage-admission-history:create',
  'storage-admission-history:operation-start',
  'storage-admission-history:admitted',
  'storage-admission-history:admission-reject',
  'storage-admission-history:release',
  'storage-admission-history:operation-final',
  'admission:admit',
  'admission:reject',
  'admission:release',
  'provider-resilience:operation-start',
  'provider-resilience:operation-final'
];
const observations = {
  successUnderAdmission: successRow.final.ok === true && successRow.release.released === true,
  transientRetryUnderAdmission: transientRow.final.reason === 'retry-success' && transientRow.release.released === true,
  watermarkRejectionNoMutation: watermarkReject.final.disposition === 'rejected-watermark' && watermarkReject.final.noProviderMutation === true,
  criticalBypassUnderCongestion: criticalBypass.admission.bypass === true && criticalBypass.final.ok === true,
  providerHealthRejectionNoMutation: healthReject.final.disposition === 'rejected-provider-health' && healthReject.final.noProviderMutation === true,
  providerHealthRecoveryAdmits: healthRecovery.final.ok === true,
  hardLimitRejectionNoMutation: hardReject.final.disposition === 'rejected-hard-limit' && hardReject.final.noProviderMutation === true,
  snapshotsValidate: validations.every((v) => v.ok),
  finalLeaseAccountingEmpty,
  bootReportRecordsStorageLaneAdmissionHistoryProof: rt.report.executableProofs.storageLaneAdmissionHistoryProof === true,
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => hasKind(trace, kind))
};
Object.entries(observations).forEach(([name, value]) => assert.equal(value, true, `${name} should be true`));
const aggregate = snapshots.reduce((acc, snapshot) => {
  acc.operations += snapshot.stats.operations;
  acc.admitted += snapshot.stats.admitted;
  acc.rejectedByAdmission += snapshot.stats.rejectedByAdmission;
  acc.criticalBypass += snapshot.stats.criticalBypass;
  acc.noMutationRejects += snapshot.stats.noMutationRejects;
  return acc;
}, { operations: 0, admitted: 0, rejectedByAdmission: 0, criticalBypass: 0, noMutationRejects: 0 });
assert.equal(aggregate.operations, 7);
assert.equal(aggregate.rejectedByAdmission, 3);

const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed', generatedAt: new Date().toISOString(),
  slice: 'scheduler:storage-lane-admission-history-proof',
  purpose: 'Compose watermark admission, provider-health gates, provider-resilience history runner, storage-lane executor, persisted-spill mailbox, retry-budget, and circuit-breaker/bulkhead behavior under deterministic fake-provider histories.',
  observations,
  aggregate,
  snapshots: snapshots.map((snapshot) => ({ stats: snapshot.stats, admission: { inFlightBytes: snapshot.admission.inFlightBytes, leaseCount: snapshot.admission.leaseCount, congested: snapshot.admission.congested, providerHealthy: snapshot.admission.providerHealthy }, resilience: { stats: snapshot.resilience.stats, breakerState: snapshot.resilience.breaker.state, retryCredits: snapshot.resilience.retryBudget.retryCredits }, mailbox: { queueDepth: snapshot.mailbox.queueDepth, pendingCount: snapshot.mailbox.pendingCount, providerBlocks: snapshot.mailbox.providerSnapshot.blockCount } })),
  trace: { count: trace.length, kinds: kinds(trace), requiredTraceKinds },
  nonClaims: [
    'No OPFS storage-lane admission-history proof.',
    'No browser Worker storage-lane admission-history proof.',
    'No production overload-governance, admission-control, retry-storm, circuit-breaker, bulkhead, retry-budget, or storage-lane claim.',
    'No wall-clock timer, throughput, latency, fairness, SLO, durability, fsync, quota, eviction, crash-recovery, or exactly-once delivery claim.',
    'No exhaustive model checking or formal verification claim.',
    'No cross-browser conformance claim.',
    'No WebGPU proof.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
