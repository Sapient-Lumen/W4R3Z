#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, REVISION, TraceLog, VERSION } from '../src/browserrt.mjs';
import { createAdaptiveConcurrencyController } from '../src/adaptive-concurrency.mjs';

const DEFAULT_ARTIFACT = `artifacts/validation/REV${REVISION.slice(3)}-ADAPTIVE-CONCURRENCY-PROBE.json`;

function parseArgs(argv) {
  const out = { json: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--json') out.json = argv[++i] || DEFAULT_ARTIFACT;
    else throw new Error(`Unknown option: ${argv[i]}`);
  }
  return out;
}

function acquireMany(controller, count, priority = 'background', label = 'task') {
  const rows = [];
  for (let i = 0; i < count; i += 1) {
    const admission = controller.tryAcquire({ priority, label: `${label}-${i}` });
    rows.push(admission);
    assert.equal(admission.admitted, true, `${label}-${i} should admit`);
  }
  return rows;
}

function releaseMany(controller, leases, latencyMs, outcome = 'complete') {
  return leases.map((lease) => {
    const released = controller.release(lease.leaseId, { latencyMs, outcome });
    assert.equal(released.released, true, `release ${lease.leaseId}`);
    return released;
  });
}

async function runProof() {
  const trace = new TraceLog();
  const rt = await boot({ adaptiveConcurrencyProbe: true });
  const controller = createAdaptiveConcurrencyController({
    label: 'rev0025-adaptive-controller',
    minLimit: 1,
    maxLimit: 12,
    initialLimit: 4,
    queueTargetMs: 10,
    additiveIncrease: 1,
    multiplicativeDecrease: 0.5,
    smoothing: 1,
    criticalMinPriority: 'user-blocking',
    rejectMinPriorityWhileLimited: 'user-visible',
    trace
  });

  const initial = controller.snapshot();

  const lowWindowA = acquireMany(controller, 4, 'background', 'low-a');
  const overInitialBefore = controller.snapshot();
  const overInitial = controller.tryAcquire({ priority: 'background', label: 'over-initial' });
  const overInitialAfter = controller.snapshot();
  assert.equal(overInitial.disposition, 'rejected-limit');
  releaseMany(controller, lowWindowA, 20);
  const lowUpdateA = controller.observeWindow();
  assert.equal(lowUpdateA.decision, 'increase');
  assert.equal(lowUpdateA.nextLimit, 5);

  const lowWindowB = acquireMany(controller, 5, 'background', 'low-b');
  releaseMany(controller, lowWindowB, 22);
  const lowUpdateB = controller.observeWindow();
  assert.equal(lowUpdateB.decision, 'increase');
  assert.equal(lowUpdateB.nextLimit, 6);

  const highWindow = acquireMany(controller, 6, 'background', 'high');
  const overSixBefore = controller.snapshot();
  const overSix = controller.tryAcquire({ priority: 'background', label: 'over-six' });
  const overSixAfter = controller.snapshot();
  assert.equal(overSix.disposition, 'rejected-limit');
  const criticalBypass = controller.tryAcquire({ priority: 'critical', label: 'critical-bypass' });
  assert.equal(criticalBypass.disposition, 'admitted-critical-bypass');
  const hardReject = controller.tryAcquire({ priority: 'critical', weight: 20, label: 'hard-reject' });
  assert.equal(hardReject.disposition, 'rejected-hard-limit');
  releaseMany(controller, [...highWindow, criticalBypass], 125);
  const highUpdate = controller.observeWindow();
  assert.equal(highUpdate.decision, 'decrease');
  assert.equal(highUpdate.nextLimit, 3);

  controller.markProviderUnhealthy('scripted-provider-pressure');
  const providerRejectBefore = controller.snapshot();
  const providerReject = controller.tryAcquire({ priority: 'background', label: 'provider-reject' });
  const providerRejectAfter = controller.snapshot();
  assert.equal(providerReject.disposition, 'rejected-provider-health');
  const providerCritical = controller.tryAcquire({ priority: 'critical', label: 'provider-critical' });
  assert.equal(providerCritical.admitted, true);
  controller.release(providerCritical.leaseId, { latencyMs: 24, outcome: 'complete' });
  controller.markProviderHealthy('scripted-provider-recovery');
  const providerRecoveryUpdate = controller.observeWindow();
  assert.equal(providerRecoveryUpdate.decision, 'increase');
  assert.equal(providerRecoveryUpdate.nextLimit, 4);

  const timeoutWindow = acquireMany(controller, 2, 'background', 'timeout');
  releaseMany(controller, timeoutWindow, 220, 'timeout');
  const timeoutUpdate = controller.observeWindow();
  assert.equal(timeoutUpdate.decision, 'decrease');
  assert.equal(timeoutUpdate.reason, 'timeout');

  const forceProbe = controller.observeWindow({ forceProbe: true });
  assert.equal(forceProbe.decision, 'probe-min-limit');
  assert.equal(forceProbe.nextLimit, 1);

  const recoveredLease = controller.tryAcquire({ priority: 'background', label: 'post-probe-background' });
  assert.equal(recoveredLease.admitted, true);
  const postProbeReject = controller.tryAcquire({ priority: 'background', label: 'post-probe-over-limit' });
  assert.equal(postProbeReject.disposition, 'rejected-limit');
  controller.release(recoveredLease.leaseId, { latencyMs: 21, outcome: 'complete' });
  const finalUpdate = controller.observeWindow();
  assert.equal(finalUpdate.decision, 'increase');

  const finalSnapshot = controller.snapshot();
  const eventKinds = trace.kinds();
  const requiredEvents = [
    'adaptive:create',
    'adaptive:admit',
    'adaptive:reject',
    'adaptive:release',
    'adaptive:window',
    'adaptive:limit-increase',
    'adaptive:limit-decrease',
    'adaptive:provider-unhealthy',
    'adaptive:provider-healthy',
    'adaptive:probe'
  ];
  const missingEvents = requiredEvents.filter((kind) => !eventKinds.includes(kind));

  const observations = {
    initialLimitObserved: initial.limit === 4,
    initialLimitIsFour: initial.limit === 4,
    lowPriorityRejectedAtLimit: overInitial.disposition === 'rejected-limit' && overSix.disposition === 'rejected-limit',
    noMutationOnReject: overInitial.noMutation && overInitialBefore.inFlight === overInitialAfter.inFlight && overSix.noMutation && overSixBefore.inFlight === overSixAfter.inFlight && providerReject.noMutation && providerRejectBefore.inFlight === providerRejectAfter.inFlight,
    criticalBypassObserved: criticalBypass.disposition === 'admitted-critical-bypass',
    criticalBypassUnderDynamicLimit: criticalBypass.disposition === 'admitted-critical-bypass',
    hardLimitRejected: hardReject.disposition === 'rejected-hard-limit',
    hardLimitRejectsOversizedWeight: hardReject.disposition === 'rejected-hard-limit',
    limitIncreaseObserved: lowUpdateA.nextLimit === 5 && lowUpdateB.nextLimit === 6 && providerRecoveryUpdate.nextLimit === 4,
    lowLatencyIncreasesLimitTwice: lowUpdateA.nextLimit === 5 && lowUpdateB.nextLimit === 6,
    limitDecreaseObserved: highUpdate.nextLimit === 3 && highUpdate.reason === 'queue-delay-above-target',
    highLatencyDecreasesLimit: highUpdate.nextLimit === 3 && highUpdate.reason === 'queue-delay-above-target',
    timeoutDecreaseObserved: timeoutUpdate.decision === 'decrease' && timeoutUpdate.reason === 'timeout',
    providerHealthRejectionObserved: providerReject.disposition === 'rejected-provider-health' && providerReject.noMutation,
    providerHealthRejectsLowPriority: providerReject.disposition === 'rejected-provider-health' && providerReject.noMutation && providerRejectBefore.inFlight === providerRejectAfter.inFlight,
    providerHealthRecoveryObserved: providerCritical.admitted && providerRecoveryUpdate.nextLimit === 4 && recoveredLease.admitted,
    providerRecoveryAllowsCriticalAndThenBackground: providerCritical.admitted && providerRecoveryUpdate.nextLimit === 4 && recoveredLease.admitted,
    probeMinLimitObserved: forceProbe.nextLimit === 1,
    forcedProbeDropsToMinLimit: forceProbe.nextLimit === 1,
    postProbeLimitStillProtectsBackground: postProbeReject.disposition === 'rejected-limit',
    finalNoLeases: finalSnapshot.inFlight === 0 && finalSnapshot.leaseCount === 0,
    finalControllerEmpty: finalSnapshot.inFlight === 0 && finalSnapshot.leaseCount === 0,
    statsMeaningful: finalSnapshot.stats.admitted >= 10 && finalSnapshot.stats.rejected >= 3 && finalSnapshot.stats.increases >= 1 && finalSnapshot.stats.decreases >= 1,
    statsCapturedIncreasesAndDecreases: finalSnapshot.stats.increases >= 3 && finalSnapshot.stats.decreases >= 2,
    traceHasRequiredEvents: missingEvents.length === 0
  };
  for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    proof_id: 'scheduler:adaptive-concurrency-proof',
    status: 'passed',
    generatedAt: new Date().toISOString(),
    observations,
    counts: {
      admitted: finalSnapshot.stats.admitted,
      rejected: finalSnapshot.stats.rejected,
      increases: finalSnapshot.stats.increases,
      decreases: finalSnapshot.stats.decreases,
      probes: finalSnapshot.stats.probes
    },
    updates: { lowUpdateA, lowUpdateB, highUpdate, providerRecoveryUpdate, timeoutUpdate, forceProbe, finalUpdate },
    snapshots: { initial, overInitialBefore, overInitialAfter, overSixBefore, overSixAfter, providerRejectBefore, providerRejectAfter, finalSnapshot },
    requiredEventKinds: requiredEvents,
    eventKinds,
    missingEvents,
    trace: trace.snapshot(),
    runtimeExecutableProofs: rt.report.executableProofs,
    nonClaims: [
      'No production auto-tuning claim.',
      'No browser Worker adaptive-concurrency proof.',
      'No multi-producer fairness proof.',
      'No latency or throughput performance claim.',
      'No claim that this AIMD-like policy is stable for arbitrary workloads.',
      'No cross-browser conformance claim.'
    ]
  };
}

const args = parseArgs(process.argv.slice(2));
const report = await runProof();
if (args.json) {
  await mkdir(dirname(args.json), { recursive: true });
  await writeFile(args.json, `${JSON.stringify(report, null, 2)}\n`);
}
console.log(JSON.stringify({ status: report.status, proof_id: report.proof_id, finalLimit: report.snapshots.finalSnapshot.limit, increases: report.snapshots.finalSnapshot.stats.increases, decreases: report.snapshots.finalSnapshot.stats.decreases }, null, 2));
