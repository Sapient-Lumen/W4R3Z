#!/usr/bin/env node
// BrowserRT rev0028 storage-lane retry policy proof.
// Fake-provider/virtual-tick proof only; no OPFS, durability, exactly-once, retry-storm safety, or production retry scheduler claim.

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
  createStorageLaneRetryController,
  createStorageLaneRetryPolicy,
  validateCrossLaneSchedulerSnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-STORAGE-LANE-RETRY-POLICY-PROBE.json`);
function hasKind(trace, kind) { return trace.some((event) => event.kind === kind); }
function kinds(trace) { return [...new Set(trace.map((event) => event.kind))].sort(); }
function opState(controller, id) { const op = controller.operation(id); assert.ok(op, `operation ${id} should exist`); return op; }
function providerBlockCount(provider) { return provider.snapshot().blockCount; }

const rt = await boot({ storageLaneRetryPolicyProof: true });
const retryPolicy = createStorageLaneRetryPolicy({ maxAttempts: 3, initialDelayTicks: 2, multiplier: 2, maxDelayTicks: 8, jitterTicks: 1, jitterSeed: 28028, retryableCodes: ['BRT_STORAGE_INJECTED_FAULT'], nonRetryableCodes: ['BRT_STORAGE_NON_RETRYABLE'] });
const provider = createMemoryBlockStore({ name: 'rev0028-storage-retry-store', provider: 'memory-storage-retry-fake-provider-v0', quotaBytes: 4096, trace: rt.trace });
const mailbox = createPersistedSpillMailbox({ label: 'rev0028-storage-retry-mailbox', provider, memoryCapacityBytes: 0, maxFrameBytes: 128, deleteBlockOnAck: false, trace: rt.trace });
const scheduler = createCrossLaneScheduler({
  label: 'rev0028-storage-retry-scheduler',
  maxQueuedCost: 256,
  maxTaskCost: 32,
  lanes: [
    { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 160 },
    { id: 'maintenance', rank: 20, capacity: 1, quantum: 64, maxQueuedCost: 96 }
  ],
  trace: rt.trace
});
const executor = createStorageLaneExecutor({ label: 'rev0028-storage-retry-executor', scheduler, mailbox, trace: rt.trace, markUnhealthyOnError: true });
const retrier = createStorageLaneRetryController({ label: 'rev0028-storage-retry-controller', executor, policy: retryPolicy, trace: rt.trace });

// Scenario 1: one transient provider write failure; no mailbox/provider mutation on failed attempt; lane health gates retry until explicit recovery.
provider.injectFault({ op: 'put', at: 1, code: 'BRT_STORAGE_INJECTED_FAULT', message: 'first write transient fault' });
const transientSubmit = retrier.submitMailboxEnqueue(mailbox, 'transient-payload', { id: 'transient-enqueue', priority: 'user-visible', cost: 1 });
assert.equal(transientSubmit.accepted, true);
const firstTransientDrain = await retrier.drainReady({ maxSteps: 5 });
const transientAfterFailure = opState(retrier, 'transient-enqueue');
assert.equal(transientAfterFailure.state, 'retry-delayed');
assert.equal(transientAfterFailure.attempts, 1);
assert.equal(providerBlockCount(provider), 0);
assert.equal(mailbox.snapshot().queueDepth, 0);
const providerBlockCountAfterFirstFailure = provider.snapshot().blockCount;
assert.equal(providerBlockCountAfterFirstFailure, 0);
assert.equal(scheduler.snapshotLane('storage').healthy, false);
const delayedRetryCountAfterFailure = retrier.snapshot().delayedCount;
assert.equal(delayedRetryCountAfterFailure, 1);
const advanced = retrier.advanceToNextRetry();
assert.equal(advanced.advanced, true);
executor.markHealthy('storage', 'rev0028 transient provider recovered');
const secondTransientDrain = await retrier.drainReady({ maxSteps: 5 });
const transientDone = opState(retrier, 'transient-enqueue');
assert.equal(transientDone.state, 'succeeded');
assert.equal(transientDone.attempts, 2);
assert.equal(providerBlockCount(provider), 1);
assert.equal(mailbox.snapshot().queueDepth, 1);

// Scenario 2: non-retryable provider error fails once and does not schedule a retry.
provider.injectFault({ op: 'put', at: 3, code: 'BRT_STORAGE_NON_RETRYABLE', message: 'logical storage error is not retryable' });
const nonRetryableSubmit = retrier.submitMailboxEnqueue(mailbox, 'non-retryable-payload', { id: 'non-retryable-enqueue', priority: 'user-visible', cost: 1 });
assert.equal(nonRetryableSubmit.accepted, true);
const nonRetryableDrain = await retrier.drainReady({ maxSteps: 5 });
const nonRetryableState = opState(retrier, 'non-retryable-enqueue');
assert.equal(nonRetryableState.state, 'failed');
assert.equal(nonRetryableState.attempts, 1);
assert.equal(nonRetryableState.lastError.decision.reason, 'non-retryable-code');
assert.equal(retrier.snapshot().delayed.some((row) => row.opId === 'non-retryable-enqueue'), false);
executor.markHealthy('storage', 'rev0028 nonretryable scenario reset');

// Scenario 3: retryable error with maxAttempts=2 eventually fails without unbounded scheduling.
provider.injectFault({ op: 'put', at: 'every', code: 'BRT_STORAGE_INJECTED_FAULT', message: 'persistent transient-looking failure' });
const maxSubmit = retrier.submitMailboxEnqueue(mailbox, 'max-attempts-payload', { id: 'max-attempts-enqueue', priority: 'background', cost: 1, maxAttempts: 2 });
assert.equal(maxSubmit.accepted, true);
const maxFirstDrain = await retrier.drainReady({ maxSteps: 5 });
const maxAfterFirst = opState(retrier, 'max-attempts-enqueue');
assert.equal(maxAfterFirst.state, 'retry-delayed');
executor.markHealthy('storage', 'rev0028 max-attempts first reset');
assert.equal(retrier.advanceToNextRetry().advanced, true);
const maxSecondDrain = await retrier.drainReady({ maxSteps: 5 });
const maxFinal = opState(retrier, 'max-attempts-enqueue');
assert.equal(maxFinal.state, 'failed');
assert.equal(maxFinal.attempts, 2);
assert.equal(maxFinal.lastError.decision.reason, 'max-attempts');
assert.equal(retrier.snapshot().delayed.some((row) => row.opId === 'max-attempts-enqueue'), false);
executor.markHealthy('storage', 'rev0028 cleanup reset');

const trace = rt.close();
const traceKinds = kinds(trace);
const retrierSnapshot = retrier.snapshot();
const schedulerSnapshot = scheduler.snapshot();
const mailboxSnapshot = mailbox.snapshot();
const providerSnapshot = provider.snapshot();
const requiredTraceKinds = [
  'storage-retry:create',
  'storage-retry:submit',
  'storage-retry:attempt-schedule',
  'storage-retry:attempt-result',
  'storage-retry:schedule-delay',
  'storage-retry:ready',
  'storage-retry:complete',
  'storage-retry:fail-final',
  'storage-retry:tick-advance',
  'storage-lane:error',
  'storage-lane:provider-unhealthy',
  'storage-lane:provider-healthy',
  'mailbox:persisted-enqueue',
  'storage:block-fault',
  'storage:block-put'
];
const observations = {
  retryControllerCreated: hasKind(trace, 'storage-retry:create'),
  policyExponentialBackoffWithDeterministicJitter: retryPolicy.delayTicksForAttempt(2, 'transient-enqueue') >= retryPolicy.delayTicksForAttempt(1, 'transient-enqueue'),
  transientFailureNoProviderMutation: firstTransientDrain.snapshot.executor.mailbox.queueDepth === 0 && providerBlockCountAfterFirstFailure === 0,
  transientFailureScheduledDelayedRetry: delayedRetryCountAfterFailure === 1 && transientAfterFailure.state === 'retry-delayed',
  laneMarkedUnhealthyOnTransientFailure: hasKind(trace, 'storage-lane:provider-unhealthy'),
  explicitHealthRecoveryBeforeRetry: hasKind(trace, 'storage-lane:provider-healthy'),
  retrySucceededOnSecondAttempt: transientDone.state === 'succeeded' && transientDone.attempts === 2,
  exactlyOneProviderBlockForSuccessfulTransientOperation: providerSnapshot.blockCount === 1,
  nonRetryableFailsWithoutRetry: nonRetryableState.state === 'failed' && nonRetryableState.attempts === 1 && nonRetryableState.lastError.decision.reason === 'non-retryable-code',
  maxAttemptsStopsRetryLoop: maxFinal.state === 'failed' && maxFinal.attempts === 2 && maxFinal.lastError.decision.reason === 'max-attempts',
  noDelayedRetriesRemain: retrierSnapshot.delayedCount === 0,
  finalSchedulerSnapshotValid: validateCrossLaneSchedulerSnapshot(schedulerSnapshot).ok === true,
  finalSchedulerAccountingEmpty: schedulerSnapshot.queuedCount === 0 && schedulerSnapshot.inFlightCount === 0,
  successfulMailboxEntryRemainsReady: mailboxSnapshot.queueDepth === 1 && mailboxSnapshot.pendingCount === 0,
  retryStatsRecorded: retrierSnapshot.stats.retryScheduled >= 2 && retrierSnapshot.stats.finalFailures === 2 && retrierSnapshot.stats.successes === 1,
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => traceKinds.includes(kind)),
  bootReportRecordsStorageLaneRetryPolicyProof: rt.report.executableProofs.storageLaneRetryPolicyProof === true
};
for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  status: 'passed',
  slice: 'scheduler:storage-lane-retry-policy-proof',
  generatedAt: new Date().toISOString(),
  purpose: 'Fake-provider proof that storage-lane retry policy uses bounded attempts, virtual backoff ticks, explicit health recovery, non-retryable codes, no-mutation failed attempts, and trace evidence without OPFS/browser spending.',
  observations,
  counts: {
    traceEvents: trace.length,
    retryOperations: retrierSnapshot.operations.length,
    delayedRetriesRemaining: retrierSnapshot.delayedCount,
    providerBlocks: providerSnapshot.blockCount,
    mailboxQueueDepth: mailboxSnapshot.queueDepth
  },
  retryPolicy: retryPolicy.snapshot(),
  operations: {
    transient: transientDone,
    nonRetryable: nonRetryableState,
    maxAttempts: maxFinal
  },
  drainSummaries: {
    firstTransientDrain: firstTransientDrain.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok ?? null, opId: row.opId ?? null, disposition: row.disposition ?? null, error: row.error ?? null })),
    secondTransientDrain: secondTransientDrain.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok ?? null, opId: row.opId ?? null, disposition: row.disposition ?? null })),
    nonRetryableDrain: nonRetryableDrain.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok ?? null, opId: row.opId ?? null, error: row.error ?? null })),
    maxFirstDrain: maxFirstDrain.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok ?? null, opId: row.opId ?? null, error: row.error ?? null })),
    maxSecondDrain: maxSecondDrain.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok ?? null, opId: row.opId ?? null, error: row.error ?? null }))
  },
  retrierSnapshot,
  schedulerSnapshot,
  mailboxSnapshot,
  providerSnapshot,
  traceKinds,
  requiredTraceKinds,
  nonClaims: [
    'No OPFS storage-lane retry proof.',
    'No browser Worker storage-lane retry proof.',
    'No durability, fsync, quota, eviction, or crash-recovery claim.',
    'No exactly-once delivery claim.',
    'No retry-storm safety or production retry algorithm claim.',
    'No wall-clock timer, throughput, latency, or SLO claim.',
    'No cross-browser conformance claim.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
