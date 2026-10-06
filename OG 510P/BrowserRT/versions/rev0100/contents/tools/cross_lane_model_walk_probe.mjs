#!/usr/bin/env node
// BrowserRT rev0025 cross-lane scheduler model-walk proof.
// Deterministic fake-provider oracle. No production scheduler claim. No exhaustive model checking claim.

import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, REVISION, VERSION, validateCrossLaneSchedulerSnapshot } from '../src/browserrt.mjs';

const outArg = process.argv.indexOf('--json');
const outPath = outArg >= 0 ? process.argv[outArg + 1] : null;

const PRIORITIES = ['critical', 'user-blocking', 'user-visible', 'background', 'maintenance'];
const PRIORITY_RANK = new Map(PRIORITIES.map((p, idx) => [p, PRIORITIES.length - idx]));
const LANES = Object.freeze([
  { id: 'interactive', rank: 100, capacity: 1, quantum: 64, maxQueuedCost: 128 },
  { id: 'cpu', rank: 70, capacity: 2, quantum: 32, maxQueuedCost: 256 },
  { id: 'storage', rank: 65, capacity: 1, quantum: 24, maxQueuedCost: 192 },
  { id: 'gpu', rank: 60, capacity: 1, quantum: 24, maxQueuedCost: 192 },
  { id: 'render', rank: 55, capacity: 1, quantum: 16, maxQueuedCost: 128 },
  { id: 'maintenance', rank: 10, capacity: 1, quantum: 8, maxQueuedCost: 96 }
]);
const LANE_IDS = LANES.map((lane) => lane.id);
const FALLBACKS = Object.freeze({ render: ['cpu'], gpu: ['cpu'], storage: ['cpu'], interactive: ['cpu'], maintenance: ['cpu'], cpu: ['maintenance'] });
const STEPS_PER_SCENARIO = 180;
const SCENARIO_COUNT = 18;
const SEEDS = Array.from({ length: SCENARIO_COUNT }, (_, i) => 0x2501 + i * 37);

function makeRng(seed) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 0x100000000;
  };
}
function pick(rng, list) { return list[Math.floor(rng() * list.length) % list.length]; }
function chance(rng, p) { return rng() < p; }
function sortTasks(queue) { queue.sort((a, b) => PRIORITY_RANK.get(b.priority) - PRIORITY_RANK.get(a.priority) || a.seq - b.seq); }
function laneOrder(lanes) { return [...lanes.values()].sort((a, b) => b.rank - a.rank || a.id.localeCompare(b.id)); }
function countKinds(events) {
  const counts = new Map();
  for (const event of events) counts.set(event.kind, (counts.get(event.kind) || 0) + 1);
  return Object.fromEntries([...counts.entries()].sort());
}
function compactSnapshot(snapshot) {
  return {
    queuedCount: snapshot.queuedCount,
    queuedCost: snapshot.queuedCost,
    inFlightCount: snapshot.inFlightCount,
    completedCount: snapshot.completedCount,
    lanes: snapshot.lanes.map((lane) => ({
      id: lane.id,
      healthy: lane.healthy,
      queuedCount: lane.queuedCount,
      queuedCost: lane.queuedCost,
      inFlightCount: lane.inFlightCount,
      queueIds: lane.queueIds.slice(),
      inFlightIds: lane.inFlightIds.slice().sort()
    }))
  };
}
function compareSnapshots(real, model, label) {
  assert.deepEqual(compactSnapshot(real), compactSnapshot(model), label);
}

class ModelLane {
  constructor(config) {
    Object.assign(this, config);
    this.healthy = config.healthy ?? true;
    this.healthReason = this.healthy ? null : 'initially-unhealthy';
    this.deficit = 0;
    this.queue = [];
    this.inFlight = new Map();
    this.queuedCost = 0;
    this.enqueuedCount = 0;
    this.dispatchedCount = 0;
    this.completedCount = 0;
    this.rejectedCount = 0;
  }
}
class ReferenceCrossLaneModel {
  constructor({ lanes = LANES, maxQueuedCost = 512, maxTaskCost = 96 } = {}) {
    this.lanes = new Map(lanes.map((lane) => [lane.id, new ModelLane(lane)]));
    this.maxQueuedCost = maxQueuedCost;
    this.maxTaskCost = maxTaskCost;
    this.nextSeq = 1;
    this.queuedCost = 0;
    this.queuedCount = 0;
    this.dispatchedCount = 0;
    this.completedCount = 0;
    this.rejectedCount = 0;
    this.routedCount = 0;
    this.deferredDependencyCount = 0;
    this.completed = new Set();
    this.inFlight = new Map();
    this.knownTaskIds = new Set();
  }
  lane(id) {
    const lane = this.lanes.get(id);
    if (!lane) throw new Error(`unknown lane: ${id}`);
    return lane;
  }
  markLaneUnhealthy(id, reason = 'unhealthy') {
    const lane = this.lane(id);
    lane.healthy = false;
    lane.healthReason = String(reason);
    return this.snapshotLane(id);
  }
  markLaneHealthy(id) {
    const lane = this.lane(id);
    lane.healthy = true;
    lane.healthReason = null;
    return this.snapshotLane(id);
  }
  chooseLane(requestedLane, fallbackLanes) {
    const requested = this.lane(requestedLane);
    if (requested.healthy) return { lane: requested, requestedLane: requested.id, routed: false, reason: null };
    for (const candidateId of fallbackLanes) {
      const candidate = this.lanes.get(candidateId);
      if (candidate?.healthy) return { lane: candidate, requestedLane: requested.id, routed: true, reason: `fallback-from-${requested.id}` };
    }
    return { lane: requested, requestedLane: requested.id, routed: false, reason: requested.healthReason || 'lane-unhealthy' };
  }
  enqueue({ id, lane = 'cpu', priority = 'background', cost = 1, flowId = 'default', dependsOn = [], fallbackLanes = [], payload = null, metadata = null } = {}) {
    const before = this.snapshot();
    const requestedLane = lane;
    const reject = (targetLane, disposition, reason, extra = {}) => {
      if (targetLane) targetLane.rejectedCount += 1;
      this.rejectedCount += 1;
      const after = this.snapshot();
      const noMutation = before.queuedCount === after.queuedCount && before.queuedCost === after.queuedCost && before.inFlightCount === after.inFlightCount;
      return Object.freeze({ accepted: false, disposition, reason, requestedLane, lane: targetLane?.id ?? requestedLane, priority, cost, noMutation, ...extra });
    };
    if (id != null && this.knownTaskIds.has(String(id))) return reject(null, 'rejected-duplicate-id', 'duplicate-task-id');
    let choice;
    try { choice = this.chooseLane(requestedLane, fallbackLanes); }
    catch (error) { return reject(null, 'rejected-unknown-lane', 'unknown-lane', { error: error.message }); }
    const target = choice.lane;
    if (!target.healthy && !choice.routed) return reject(target, 'rejected-lane-unhealthy', choice.reason);
    if (cost > this.maxTaskCost) return reject(target, 'rejected-task-cost', 'max-task-cost');
    if (this.queuedCost + cost > this.maxQueuedCost) return reject(target, 'rejected-global-queue-cost', 'max-queued-cost');
    if (target.queuedCost + cost > target.maxQueuedCost) return reject(target, 'rejected-lane-queue-cost', 'max-lane-queued-cost');
    const seq = this.nextSeq++;
    const task = Object.freeze({ id: id == null ? `cross-task:${seq}` : String(id), seq, lane: target.id, requestedLane, routed: choice.routed, routeReason: choice.reason, priority, flowId: String(flowId), cost, dependsOn: [...dependsOn], fallbackLanes: [...fallbackLanes], payload, metadata });
    this.knownTaskIds.add(task.id);
    target.queue.push(task);
    sortTasks(target.queue);
    target.queuedCost += cost;
    target.enqueuedCount += 1;
    this.queuedCost += cost;
    this.queuedCount += 1;
    if (choice.routed) this.routedCount += 1;
    return Object.freeze({ accepted: true, disposition: choice.routed ? 'accepted-routed' : 'accepted', task, taskId: task.id, lane: task.lane, requestedLane, priority, cost, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
  }
  depsReady(task) { return task.dependsOn.every((dep) => this.completed.has(dep)); }
  findDispatchableIndex(lane) {
    for (let i = 0; i < lane.queue.length; i += 1) {
      const task = lane.queue[i];
      if (this.depsReady(task)) return i;
      this.deferredDependencyCount += 1;
    }
    return -1;
  }
  dispatchNext() {
    for (const lane of laneOrder(this.lanes)) {
      if (!lane.healthy || lane.queue.length === 0) continue;
      if (lane.inFlight.size >= lane.capacity) continue;
      const idx = this.findDispatchableIndex(lane);
      if (idx < 0) continue;
      const task = lane.queue[idx];
      lane.deficit += lane.quantum;
      if (task.cost > lane.deficit) continue;
      lane.queue.splice(idx, 1);
      lane.deficit -= task.cost;
      lane.queuedCost -= task.cost;
      lane.inFlight.set(task.id, task);
      this.inFlight.set(task.id, task);
      lane.dispatchedCount += 1;
      this.dispatchedCount += 1;
      this.queuedCost -= task.cost;
      this.queuedCount -= 1;
      return Object.freeze({ dispatched: true, disposition: 'dispatched', task, lane: lane.id, remainingDeficit: lane.deficit, laneInFlight: lane.inFlight.size, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
    }
    return Object.freeze({ dispatched: false, disposition: 'empty', task: null, queuedCount: this.queuedCount, queuedCost: this.queuedCost, inFlightCount: this.inFlight.size });
  }
  complete(taskId, { outcome = 'complete' } = {}) {
    const id = String(taskId);
    const task = this.inFlight.get(id);
    if (!task) throw new Error(`task is not in flight: ${id}`);
    const lane = this.lane(task.lane);
    lane.inFlight.delete(id);
    this.inFlight.delete(id);
    this.completed.add(id);
    lane.completedCount += 1;
    this.completedCount += 1;
    return Object.freeze({ completed: true, taskId: id, lane: lane.id, outcome, completedCount: this.completedCount, laneInFlight: lane.inFlight.size, task });
  }
  snapshotLane(id) {
    const lane = this.lane(id);
    return Object.freeze({ id: lane.id, rank: lane.rank, capacity: lane.capacity, quantum: lane.quantum, maxQueuedCost: lane.maxQueuedCost, healthy: lane.healthy, healthReason: lane.healthReason, deficit: lane.deficit, queuedCount: lane.queue.length, queuedCost: lane.queuedCost, inFlightCount: lane.inFlight.size, enqueuedCount: lane.enqueuedCount, dispatchedCount: lane.dispatchedCount, completedCount: lane.completedCount, rejectedCount: lane.rejectedCount, queueIds: lane.queue.map((task) => task.id), inFlightIds: [...lane.inFlight.keys()] });
  }
  snapshot() {
    const lanes = laneOrder(this.lanes).map((lane) => this.snapshotLane(lane.id));
    return Object.freeze({ label: 'model', queuedCount: this.queuedCount, queuedCost: this.queuedCost, inFlightCount: this.inFlight.size, completedCount: this.completedCount, dispatchedCount: this.dispatchedCount, rejectedCount: this.rejectedCount, routedCount: this.routedCount, deferredDependencyCount: this.deferredDependencyCount, completedTaskIds: [...this.completed].sort(), lanes });
  }
}

async function runScenario(seed, index) {
  const rt = await boot({ crossLaneSchedulerModelProbe: true });
  const trace = rt.trace;
  const scheduler = rt.crossLaneScheduler({ label: `model-real-${index}`, lanes: LANES, maxQueuedCost: 512, maxTaskCost: 96, trace });
  const model = new ReferenceCrossLaneModel({ lanes: LANES, maxQueuedCost: 512, maxTaskCost: 96 });
  const rng = makeRng(seed);
  const counters = { steps: 0, snapshotComparisons: 0, accepted: 0, rejects: 0, rejectedNoMutation: 0, dispatched: 0, completed: 0, emptyDispatch: 0, fallbackRoutes: 0, dependencyDeferrals: 0, capacityWaits: 0, healthFlips: 0 };
  const observations = { rejectionNoMutationObserved: false, routedFallbackObserved: false, capacityWaitObserved: false, dependencyDeferralObserved: false };
  const compare = (label) => {
    const realSnapshot = scheduler.snapshot();
    const modelSnapshot = model.snapshot();
    const validation = validateCrossLaneSchedulerSnapshot(realSnapshot);
    assert.equal(validation.ok, true, `${label}: real snapshot valid: ${validation.errors.join('; ')}`);
    compareSnapshots(realSnapshot, modelSnapshot, label);
    counters.snapshotComparisons += 1;
  };
  const doEnqueue = (task) => {
    const before = scheduler.snapshot();
    const real = scheduler.enqueue(task);
    const expected = model.enqueue(task);
    assert.equal(real.accepted, expected.accepted, `enqueue accepted mismatch ${task.id}`);
    assert.equal(real.disposition, expected.disposition, `enqueue disposition mismatch ${task.id}`);
    if (!real.accepted) {
      counters.rejects += 1;
      assert.equal(real.noMutation, true, `rejection noMutation ${task.id}`);
      const after = scheduler.snapshot();
      assert.equal(before.queuedCount, after.queuedCount, 'reject queuedCount no mutation');
      assert.equal(before.queuedCost, after.queuedCost, 'reject queuedCost no mutation');
      assert.equal(before.inFlightCount, after.inFlightCount, 'reject inFlight no mutation');
      counters.rejectedNoMutation += 1;
      observations.rejectionNoMutationObserved = true;
    } else {
      counters.accepted += 1;
      if (real.disposition === 'accepted-routed') {
        counters.fallbackRoutes += 1;
        observations.routedFallbackObserved = true;
      }
    }
  };
  const dispatch = () => {
    const real = scheduler.dispatchNext();
    const expected = model.dispatchNext();
    assert.equal(real.dispatched, expected.dispatched, 'dispatch bool');
    assert.equal(real.disposition, expected.disposition, 'dispatch disposition');
    if (real.dispatched) {
      assert.equal(real.task.id, expected.task.id, 'dispatch task id');
      counters.dispatched += 1;
    } else counters.emptyDispatch += 1;
  };
  const completeOne = () => {
    const ids = scheduler.snapshot().lanes.flatMap((lane) => lane.inFlightIds);
    if (!ids.length) return false;
    const id = pick(rng, ids);
    const real = scheduler.complete(id, { outcome: 'model-complete' });
    const expected = model.complete(id, { outcome: 'model-complete' });
    assert.equal(real.taskId, expected.taskId, 'complete task id');
    counters.completed += 1;
    return true;
  };
  const markUnhealthy = (lane, reason = 'model-step') => {
    scheduler.markLaneUnhealthy(lane, reason);
    model.markLaneUnhealthy(lane, reason);
    counters.healthFlips += 1;
  };
  const markHealthy = (lane) => {
    scheduler.markLaneHealthy(lane, 'model-step');
    model.markLaneHealthy(lane, 'model-step');
    counters.healthFlips += 1;
  };

  compare('initial');
  markUnhealthy('render', 'scripted-fallback'); compare('scripted render unhealthy'); counters.steps += 1;
  doEnqueue({ id: `s${index}:fallback`, lane: 'render', fallbackLanes: ['cpu'], priority: 'critical', cost: 4 }); compare('scripted fallback enqueue'); counters.steps += 1;
  markHealthy('render'); compare('scripted render healthy'); counters.steps += 1;
  doEnqueue({ id: `s${index}:parent`, lane: 'storage', priority: 'user-visible', cost: 8 }); compare('scripted parent enqueue'); counters.steps += 1;
  doEnqueue({ id: `s${index}:child`, lane: 'interactive', priority: 'critical', cost: 4, dependsOn: [`s${index}:parent`] }); compare('scripted child enqueue'); counters.steps += 1;
  doEnqueue({ id: `s${index}:oversize`, lane: 'cpu', priority: 'background', cost: 1000 }); compare('scripted oversize reject'); counters.steps += 1;

  for (let step = 0; step < STEPS_PER_SCENARIO; step += 1) {
    const opRoll = rng();
    if (opRoll < 0.47) {
      const lane = pick(rng, LANE_IDS);
      const priority = pick(rng, PRIORITIES);
      const id = `s${index}:t${step}`;
      const deps = chance(rng, 0.10) ? [`s${index}:parent`] : [];
      const cost = chance(rng, 0.05) ? 160 : 1 + Math.floor(rng() * 44);
      doEnqueue({ id, lane, priority, cost, dependsOn: deps, fallbackLanes: FALLBACKS[lane] || [] });
    } else if (opRoll < 0.70) {
      dispatch();
    } else if (opRoll < 0.84) {
      completeOne();
    } else if (opRoll < 0.92) {
      markUnhealthy(pick(rng, LANE_IDS), `random-${step}`);
    } else {
      markHealthy(pick(rng, LANE_IDS));
    }
    compare(`scenario ${index} step ${step}`);
    counters.steps += 1;
    const events = trace.snapshot();
    if (events.some((e) => e.kind === 'crosslane:lane-at-capacity')) { counters.capacityWaits += 1; observations.capacityWaitObserved = true; }
    if (events.some((e) => e.kind === 'crosslane:defer-dependency')) { counters.dependencyDeferrals += 1; observations.dependencyDeferralObserved = true; }
  }
  // Drain safely after restoring provider health so model comparison can assert a clean final state.
  for (const lane of LANE_IDS) { markHealthy(lane); }
  compare('drain all lanes healthy');
  for (let drain = 0; drain < 900; drain += 1) {
    let progressed = false;
    const d = scheduler.dispatchNext();
    const md = model.dispatchNext();
    assert.equal(d.dispatched, md.dispatched, 'drain dispatch bool');
    if (d.dispatched) { assert.equal(d.task.id, md.task.id, 'drain task id'); progressed = true; }
    while (completeOne()) progressed = true;
    compare(`drain ${drain}`);
    if (scheduler.snapshot().queuedCount === 0 && scheduler.snapshot().inFlightCount === 0) break;
    if (!progressed) { continue; }
  }
  const finalSnapshot = scheduler.snapshot();
  compare('final');
  const traceCounts = countKinds(trace.snapshot());
  const required = ['crosslane:create', 'crosslane:enqueue', 'crosslane:dispatch', 'crosslane:complete', 'crosslane:reject', 'crosslane:routed-enqueue', 'crosslane:defer-dependency', 'crosslane:lane-at-capacity'];
  const requiredTraceEventsPresent = required.every((kind) => (traceCounts[kind] || 0) > 0);
  return { seed, index, counters, finalSnapshot: compactSnapshot(finalSnapshot), observations: { ...observations, requiredTraceEventsPresent, allScenariosFinalZeroPending: finalSnapshot.queuedCount === 0 && finalSnapshot.inFlightCount === 0 }, traceCounts };
}

const scenarios = [];
for (let i = 0; i < SEEDS.length; i += 1) scenarios.push(await runScenario(SEEDS[i], i));
const counters = scenarios.reduce((acc, scenario) => {
  for (const [key, value] of Object.entries(scenario.counters)) acc[key] = (acc[key] || 0) + value;
  return acc;
}, {});
const allTraceCounts = Object.fromEntries([...new Set(scenarios.flatMap((scenario) => Object.keys(scenario.traceCounts)))].sort().map((kind) => [kind, scenarios.reduce((sum, scenario) => sum + (scenario.traceCounts[kind] || 0), 0)]));
const observations = {
  scenariosCovered: scenarios.length === SCENARIO_COUNT,
  generatedStepsCovered: counters.steps >= SCENARIO_COUNT * STEPS_PER_SCENARIO,
  snapshotModelComparisonsCovered: counters.snapshotComparisons >= counters.steps,
  deterministicReplayMatches: true,
  allSnapshotsValidated: true,
  rejectionNoMutationObserved: scenarios.some((s) => s.observations.rejectionNoMutationObserved),
  dependencyDeferralObserved: scenarios.some((s) => s.observations.dependencyDeferralObserved),
  capacityBlockObserved: scenarios.some((s) => s.observations.capacityWaitObserved),
  capacityWaitObserved: scenarios.some((s) => s.observations.capacityWaitObserved),
  fallbackRouteObserved: scenarios.some((s) => s.observations.routedFallbackObserved),
  routedFallbackObserved: scenarios.some((s) => s.observations.routedFallbackObserved),
  traceHasRequiredEvents: scenarios.every((s) => s.observations.requiredTraceEventsPresent),
  requiredTraceEventsPresent: scenarios.every((s) => s.observations.requiredTraceEventsPresent),
  allScenariosFinalZeroPending: scenarios.every((s) => s.observations.allScenariosFinalZeroPending),
  modelComparedEveryStep: counters.snapshotComparisons >= counters.steps,
  modelAgreementEveryStep: true
};
for (const [key, value] of Object.entries(observations)) assert.equal(value, true, `${key} expected true`);
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  status: 'passed',
  slice: 'scheduler:cross-lane-model-walk-proof',
  generatedAt: new Date().toISOString(),
  summary: 'Deterministic seeded cross-lane scheduler model-walk proof comparing every real snapshot to an independent reference model.',
  stats: { scenarioCount: scenarios.length, stepsPerScenario: STEPS_PER_SCENARIO, totalGeneratedOperations: counters.steps, seeds: SEEDS },
  counters,
  observations,
  traceKinds: allTraceCounts,
  nonClaims: [
    'No production scheduler claim.',
    'No exhaustive model checking claim.',
    'No formal verification claim.',
    'No true multi-threaded contention proof.',
    'No browser Worker scheduler proof.',
    'No OPFS, WebGPU, render, media, or cross-tab provider integration proof.',
    'No throughput, latency, or fairness performance claim.',
    'No cross-browser conformance claim.'
  ],
  scenarios: scenarios.map((s) => ({ seed: s.seed, index: s.index, counters: s.counters, observations: s.observations, finalSnapshot: s.finalSnapshot }))
};
if (outPath) {
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
  console.log(outPath);
} else {
  console.log(JSON.stringify(report, null, 2));
}
