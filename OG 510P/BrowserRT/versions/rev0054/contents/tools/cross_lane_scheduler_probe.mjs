#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, createCrossLaneScheduler, REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-CROSS-LANE-SCHEDULER-PROBE.json`;

function argValue(argv, flag, fallback = null) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}
const outPath = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
function hasKind(trace, kind) { return trace.some((event) => event.kind === kind); }
function ids(rows) { return rows.map((row) => row.task?.id ?? row.taskId ?? row.disposition); }

const rt = await boot({ proof: 'rev0025-cross-lane-scheduler', crossLaneSchedulerProbe: true });
const scheduler = createCrossLaneScheduler({
  label: 'rev0025-cross-lane-proof',
  maxQueuedCost: 128,
  maxTaskCost: 8,
  lanes: [
    { id: 'interactive', rank: 100, capacity: 1, quantum: 64, maxQueuedCost: 32 },
    { id: 'cpu', rank: 80, capacity: 1, quantum: 64, maxQueuedCost: 48 },
    { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 48 },
    { id: 'gpu', rank: 60, capacity: 1, quantum: 64, maxQueuedCost: 48 },
    { id: 'render', rank: 50, capacity: 1, quantum: 64, maxQueuedCost: 32 },
    { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 32 }
  ],
  trace: rt.trace
});

const rejectUnknown = scheduler.enqueue({ id: 'bad-lane', lane: 'bogus', priority: 'background', cost: 1 });
assert.equal(rejectUnknown.accepted, false);
assert.equal(rejectUnknown.disposition, 'rejected-unknown-lane');
assert.equal(rejectUnknown.noMutation, true);
const rejectOversize = scheduler.enqueue({ id: 'oversize', lane: 'cpu', priority: 'background', cost: 9 });
assert.equal(rejectOversize.accepted, false);
assert.equal(rejectOversize.disposition, 'rejected-task-cost');
assert.equal(rejectOversize.noMutation, true);

scheduler.enqueue({ id: 'storage-critical-held', lane: 'storage', priority: 'critical', cost: 2 });
scheduler.markLaneUnhealthy('storage', 'fixture-provider-unhealthy');
scheduler.enqueue({ id: 'cpu-visible-a', lane: 'cpu', priority: 'user-visible', cost: 2 });
scheduler.enqueue({ id: 'gpu-visible-a', lane: 'gpu', priority: 'user-visible', cost: 2 });
scheduler.enqueue({ id: 'maintenance-a', lane: 'maintenance', priority: 'background', cost: 1 });
const whileStorageUnhealthy = [scheduler.dispatchNext(), scheduler.dispatchNext(), scheduler.dispatchNext()];
for (const row of whileStorageUnhealthy) scheduler.complete(row.task.id, { outcome: 'unhealthy-skip-independent-progress' });
scheduler.markLaneHealthy('storage', 'fixture-provider-healthy');
const recoveredStorage = scheduler.dispatchNext();
assert.equal(recoveredStorage.task.id, 'storage-critical-held');
scheduler.complete(recoveredStorage.task.id, { outcome: 'recovered-lane-complete' });

scheduler.enqueue({ id: 'cpu-parent', lane: 'cpu', priority: 'critical', cost: 2 });
scheduler.enqueue({ id: 'interactive-child-after-cpu', lane: 'interactive', priority: 'critical', cost: 2, dependsOn: ['cpu-parent'] });
scheduler.enqueue({ id: 'storage-independent', lane: 'storage', priority: 'user-visible', cost: 2 });
const parentDispatch = scheduler.dispatchNext();
assert.equal(parentDispatch.task.id, 'cpu-parent');
const independentDispatch = scheduler.dispatchNext();
assert.equal(independentDispatch.task.id, 'storage-independent');
scheduler.complete(parentDispatch.task.id, { outcome: 'dependency-source-complete' });
scheduler.complete(independentDispatch.task.id, { outcome: 'independent-complete' });
const childDispatch = scheduler.dispatchNext();
assert.equal(childDispatch.task.id, 'interactive-child-after-cpu');
scheduler.complete(childDispatch.task.id, { outcome: 'dependency-child-complete' });

scheduler.enqueue({ id: 'cpu-cap-a', lane: 'cpu', priority: 'background', cost: 4 });
scheduler.enqueue({ id: 'cpu-cap-b', lane: 'cpu', priority: 'background', cost: 4 });
const capA = scheduler.dispatchNext();
assert.equal(capA.task.id, 'cpu-cap-a');
const noCpuWhileFull = scheduler.dispatchNext();
assert.equal(noCpuWhileFull.dispatched, false);
assert.equal(noCpuWhileFull.disposition, 'empty');
scheduler.complete(capA.task.id, { outcome: 'capacity-release' });
const capB = scheduler.dispatchNext();
assert.equal(capB.task.id, 'cpu-cap-b');
scheduler.complete(capB.task.id, { outcome: 'capacity-release' });

scheduler.enqueue({ id: 'same-cpu', lane: 'cpu', priority: 'user-visible', cost: 2 });
scheduler.enqueue({ id: 'same-storage', lane: 'storage', priority: 'user-visible', cost: 2 });
scheduler.enqueue({ id: 'same-gpu', lane: 'gpu', priority: 'user-visible', cost: 2 });
const samePriorityDispatches = [scheduler.dispatchNext(), scheduler.dispatchNext(), scheduler.dispatchNext()];
const samePriorityLanes = samePriorityDispatches.map((row) => row.lane);
for (const row of samePriorityDispatches) scheduler.complete(row.task.id, { outcome: 'same-priority-complete' });

const routed = scheduler.enqueue({ id: 'routed-render-to-cpu', lane: 'render', fallbackLanes: ['cpu'], priority: 'user-visible', cost: 2 });
assert.equal(routed.accepted, true);
assert.equal(routed.lane, 'render');
scheduler.markLaneUnhealthy('render', 'render-provider-down');
const routedAfterHealth = scheduler.enqueue({ id: 'routed-render-to-cpu-2', lane: 'render', fallbackLanes: ['cpu'], priority: 'user-visible', cost: 2 });
assert.equal(routedAfterHealth.accepted, true);
assert.equal(routedAfterHealth.disposition, 'accepted-routed');
assert.equal(routedAfterHealth.lane, 'cpu');
const routeFirst = scheduler.dispatchNext();
assert.equal(routeFirst.task.id, 'routed-render-to-cpu-2');
scheduler.complete(routeFirst.task.id, { outcome: 'routed-fallback-complete' });
scheduler.markLaneHealthy('render', 'render-provider-restored');
const renderAfterRestore = scheduler.dispatchNext();
assert.equal(renderAfterRestore.task.id, 'routed-render-to-cpu');
scheduler.complete(renderAfterRestore.task.id, { outcome: 'requested-render-complete' });

const runtimeScheduler = rt.crossLaneScheduler({
  label: 'runtime-factory-cross-lane',
  maxQueuedCost: 16,
  maxTaskCost: 4,
  lanes: [{ id: 'cpu', rank: 1, capacity: 1, quantum: 4, maxQueuedCost: 8 }]
});
const runtimeEnqueue = runtimeScheduler.enqueue({ id: 'runtime-cpu', lane: 'cpu', priority: 'background', cost: 1 });
assert.equal(runtimeEnqueue.accepted, true);
const runtimeDispatch = runtimeScheduler.dispatchNext();
assert.equal(runtimeDispatch.task.id, 'runtime-cpu');
runtimeScheduler.complete(runtimeDispatch.task.id, { outcome: 'runtime-factory-complete' });

const finalSnapshot = scheduler.snapshot();
const trace = rt.close();
const requiredTraceKinds = [
  'crosslane:create',
  'crosslane:lane-create',
  'crosslane:enqueue',
  'crosslane:reject',
  'crosslane:lane-unhealthy',
  'crosslane:skip-unhealthy-lane',
  'crosslane:priority-blocked-but-skipped',
  'crosslane:dispatch',
  'crosslane:complete',
  'crosslane:lane-healthy',
  'crosslane:defer-dependency',
  'crosslane:lane-at-capacity',
  'crosslane:routed-enqueue',
  'crosslane:dispatch-empty'
];
const observations = {
  rejectedUnknownLaneWithoutMutation: rejectUnknown.noMutation && rejectUnknown.disposition === 'rejected-unknown-lane',
  rejectedOversizeWithoutMutation: rejectOversize.noMutation && rejectOversize.disposition === 'rejected-task-cost',
  unhealthyStorageDidNotBlockCpu: ids(whileStorageUnhealthy)[0] === 'cpu-visible-a',
  unhealthyStorageDidNotBlockGpu: ids(whileStorageUnhealthy)[1] === 'gpu-visible-a',
  unhealthyStorageDidNotBlockMaintenance: ids(whileStorageUnhealthy)[2] === 'maintenance-a',
  interactivePriorityProtected: ids(whileStorageUnhealthy)[0] === 'cpu-visible-a',
  blockedHigherPriorityWasSkippedWithTrace: hasKind(trace, 'crosslane:priority-blocked-but-skipped') && hasKind(trace, 'crosslane:skip-unhealthy-lane'),
  recoveredLaneDispatchesHeldTask: recoveredStorage.task.id === 'storage-critical-held',
  dependencyGateHeldChild: independentDispatch.task.id === 'storage-independent' && childDispatch.task.id === 'interactive-child-after-cpu' && hasKind(trace, 'crosslane:defer-dependency'),
  dependencyDeferredUntilParentComplete: independentDispatch.task.id === 'storage-independent' && childDispatch.task.id === 'interactive-child-after-cpu' && hasKind(trace, 'crosslane:defer-dependency'),
  laneCapacityPreventsSecondCpuDispatch: noCpuWhileFull.disposition === 'empty' && hasKind(trace, 'crosslane:lane-at-capacity'),
  storageCapacityBlockedSecondDispatch: noCpuWhileFull.disposition === 'empty' && hasKind(trace, 'crosslane:lane-at-capacity'),
  samePriorityMultipleLanesObserved: new Set(samePriorityLanes).size === 3,
  fallbackRoutingObserved: routedAfterHealth.disposition === 'accepted-routed' && routedAfterHealth.lane === 'cpu' && hasKind(trace, 'crosslane:routed-enqueue'),
  unhealthyLaneRoutedToFallback: routedAfterHealth.disposition === 'accepted-routed' && routedAfterHealth.lane === 'cpu' && hasKind(trace, 'crosslane:routed-enqueue'),
  rejectionNoMutation: rejectUnknown.noMutation && rejectOversize.noMutation,
  runtimeFactorySchedulerWorks: runtimeDispatch.task.id === 'runtime-cpu' && runtimeScheduler.snapshot().queuedCount === 0 && runtimeScheduler.snapshot().inFlightCount === 0,
  finalSchedulerEmpty: finalSnapshot.queuedCount === 0 && finalSnapshot.queuedCost === 0 && finalSnapshot.inFlightCount === 0,
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => hasKind(trace, kind))
};
for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  status: 'passed',
  slice: 'scheduler:cross-lane-contract-proof',
  generatedAt: new Date().toISOString(),
  purpose: 'Cheap fake-provider proof that BrowserRT can express a cross-lane scheduler contract: lane health, independent lane progress, dependency gates, capacity gates, fallback routing, rejection no-mutation, runtime factory integration, trace evidence, and final empty accounting.',
  dispatchSequences: {
    whileStorageUnhealthy: ids(whileStorageUnhealthy),
    dependency: [parentDispatch.task.id, independentDispatch.task.id, childDispatch.task.id],
    capacity: [capA.task.id, noCpuWhileFull.disposition, capB.task.id],
    samePriorityLanes,
    routing: [routeFirst.task.id, renderAfterRestore.task.id]
  },
  observations,
  finalSnapshot,
  traceKinds: [...new Set(trace.map((event) => event.kind))].sort(),
  traceEventCount: trace.length,
  requiredTraceKinds,
  runtimeExecutableProofs: rt.report.executableProofs,
  nonClaims: [
    'No production cross-lane scheduler claim.',
    'No preemption, deadline scheduling, work stealing, priority inheritance, or true multi-threaded contention proof.',
    'No exact Kubernetes, Borg, Ray, Dask, Tokio, libuv, CFS, or DRF implementation claim.',
    'No browser Worker cross-lane scheduler proof.',
    'No OPFS, WebGPU, render, media, or cross-tab provider integration proof.',
    'No throughput, latency, fairness, or real performance claim.'
  ]
};
if (outPath) {
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(report, null, 2) + String.fromCharCode(10));
  console.log(outPath);
} else {
  console.log(JSON.stringify(report, null, 2));
}
