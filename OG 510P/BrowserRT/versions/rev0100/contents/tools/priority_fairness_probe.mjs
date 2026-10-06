#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, REVISION, VERSION, TraceLog } from '../src/browserrt.mjs';
import { createPriorityFairScheduler } from '../src/priority-fairness.mjs';

const DEFAULT_ARTIFACT = `artifacts/validation/REV${REVISION.slice(3)}-PRIORITY-FAIRNESS-PROBE.json`;

function parseArgs(argv) {
  const out = { json: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--json') out.json = argv[++i] || DEFAULT_ARTIFACT;
    else throw new Error(`Unknown option: ${argv[i]}`);
  }
  return out;
}

function enqueueMany(scheduler, { flowId, priority, count, cost, prefix }) {
  const rows = [];
  for (let i = 0; i < count; i += 1) {
    const result = scheduler.enqueue({ id: `${prefix}-${i}`, flowId, priority, cost, payload: { i } });
    assert.equal(result.accepted, true, `enqueue ${prefix}-${i}`);
    rows.push(result);
  }
  return rows;
}

async function runProof() {
  const trace = new TraceLog();
  const rt = await boot({ priorityFairnessProbe: true });
  const scheduler = createPriorityFairScheduler({
    label: 'rev0025-priority-fairness',
    priorityQuanta: { critical: 64, 'user-blocking': 32, 'user-visible': 16, background: 8, maintenance: 4 },
    maxQueuedCost: 400,
    maxFlowQueuedCost: 96,
    maxTaskCost: 64,
    trace
  });

  enqueueMany(scheduler, { flowId: 'noisy-neighbor', priority: 'background', count: 10, cost: 7, prefix: 'noisy' });
  enqueueMany(scheduler, { flowId: 'steady-peer-a', priority: 'background', count: 4, cost: 3, prefix: 'peer-a' });
  enqueueMany(scheduler, { flowId: 'steady-peer-b', priority: 'background', count: 4, cost: 3, prefix: 'peer-b' });
  const flowLimitBefore = scheduler.snapshot();
  const flowLimitReject = scheduler.enqueue({ id: 'noisy-over-flow-limit', flowId: 'noisy-neighbor', priority: 'background', cost: 40 });
  const flowLimitAfter = scheduler.snapshot();
  assert.equal(flowLimitReject.disposition, 'rejected-flow-queue-cost');

  const firstNine = scheduler.drain({ limit: 9 });
  assert.equal(firstNine.length, 9);
  const firstNineFlows = firstNine.map((task) => task.flowId);
  const peerAInFirstNine = firstNineFlows.filter((flow) => flow === 'steady-peer-a').length;
  const peerBInFirstNine = firstNineFlows.filter((flow) => flow === 'steady-peer-b').length;
  const noisyInFirstNine = firstNineFlows.filter((flow) => flow === 'noisy-neighbor').length;

  enqueueMany(scheduler, { flowId: 'interactive-user', priority: 'critical', count: 3, cost: 5, prefix: 'critical' });
  enqueueMany(scheduler, { flowId: 'visible-ui', priority: 'user-visible', count: 2, cost: 5, prefix: 'visible' });
  const priorityBurst = scheduler.drain({ limit: 5 });
  const priorityBurstPriorities = priorityBurst.map((task) => task.priority);
  const criticalPrefixProtected = priorityBurstPriorities.slice(0, 3).every((priority) => priority === 'critical');
  const visibleBeforeBackground = priorityBurstPriorities.slice(3, 5).every((priority) => priority === 'user-visible');

  const oversizeBefore = scheduler.snapshot();
  const oversizeReject = scheduler.enqueue({ id: 'oversize-task', flowId: 'bad-flow', priority: 'critical', cost: 65 });
  const oversizeAfter = scheduler.snapshot();
  assert.equal(oversizeReject.disposition, 'rejected-task-cost');

  const drainRest = scheduler.drain({ limit: 1000 });
  const finalSnapshot = scheduler.snapshot();
  const allDispatched = [...firstNine, ...priorityBurst, ...drainRest];
  const backgroundDispatches = allDispatched.filter((task) => task.priority === 'background');
  const countsByFlow = Object.fromEntries(['noisy-neighbor', 'steady-peer-a', 'steady-peer-b', 'interactive-user', 'visible-ui'].map((flow) => [flow, allDispatched.filter((task) => task.flowId === flow).length]));
  const eventKinds = trace.kinds();
  const requiredEvents = ['fair:create', 'fair:flow-create', 'fair:enqueue', 'fair:flow-activate', 'fair:deficit-add', 'fair:dispatch', 'fair:reject', 'fair:flow-empty', 'fair:dispatch-empty'];
  const missingEvents = requiredEvents.filter((kind) => !eventKinds.includes(kind));

  const observations = {
    runtimeBooted: rt.report.project === 'BrowserRT' && rt.report.revision === REVISION,
    noisyNeighborDidNotStarvePeers: peerAInFirstNine >= 3 && peerBInFirstNine >= 3 && noisyInFirstNine <= 3,
    samePriorityFairRotationObserved: firstNineFlows.join(',') === 'noisy-neighbor,steady-peer-a,steady-peer-b,noisy-neighbor,steady-peer-a,steady-peer-b,noisy-neighbor,steady-peer-a,steady-peer-b',
    variableCostAccountedByDeficit: trace.count('fair:deficit-add') >= allDispatched.length,
    priorityProtectionObserved: criticalPrefixProtected && visibleBeforeBackground,
    lowPriorityResumesAfterHighPriorityDrain: backgroundDispatches.length === 18,
    flowQueueLimitRejectObserved: flowLimitReject.noMutation && flowLimitBefore.queuedCost === flowLimitAfter.queuedCost,
    oversizeRejectObserved: oversizeReject.noMutation && oversizeBefore.queuedCost === oversizeAfter.queuedCost,
    noMutationOnReject: flowLimitReject.noMutation && oversizeReject.noMutation,
    allAcceptedTasksDispatched: allDispatched.length === 23,
    finalQueueEmpty: finalSnapshot.queuedCount === 0 && finalSnapshot.queuedCost === 0,
    countsMeaningful: countsByFlow['noisy-neighbor'] === 10 && countsByFlow['steady-peer-a'] === 4 && countsByFlow['steady-peer-b'] === 4 && countsByFlow['interactive-user'] === 3 && countsByFlow['visible-ui'] === 2,
    traceHasRequiredEvents: missingEvents.length === 0
  };
  for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    proof_id: 'scheduler:priority-fairness-proof',
    status: 'passed',
    generatedAt: new Date().toISOString(),
    observations,
    firstNineFlows,
    priorityBurstPriorities,
    countsByFlow,
    counts: {
      accepted: 23,
      dispatched: allDispatched.length,
      rejected: finalSnapshot.rejectedCount,
      eventKinds: eventKinds.length
    },
    snapshots: { flowLimitBefore, flowLimitAfter, oversizeBefore, oversizeAfter, finalSnapshot },
    requiredEventKinds: requiredEvents,
    eventKinds,
    missingEvents,
    trace: trace.snapshot(),
    runtimeExecutableProofs: rt.report.executableProofs,
    nonClaims: [
      'No production scheduler algorithm claim.',
      'No exact Kubernetes APF, DRR, Linux CFS, WFQ, or SRE load-shedding implementation claim.',
      'No browser Worker priority scheduler proof.',
      'No preemption, deadline, or cross-lane fairness proof.',
      'No multi-threaded scheduler contention proof.',
      'No throughput or latency performance claim.',
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
console.log(JSON.stringify({ status: report.status, proof_id: report.proof_id, dispatched: report.counts.dispatched, rejected: report.counts.rejected }, null, 2));
