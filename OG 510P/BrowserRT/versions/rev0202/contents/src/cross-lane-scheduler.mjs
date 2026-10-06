const PRIORITY_ORDER = Object.freeze(['critical', 'user-blocking', 'user-visible', 'background', 'maintenance']);
const PRIORITY_RANK = new Map(PRIORITY_ORDER.map((priority, idx) => [priority, PRIORITY_ORDER.length - idx]));
const DEFAULT_LANES = Object.freeze([
  { id: 'interactive', rank: 100, capacity: 1, quantum: 64, maxQueuedCost: 128 },
  { id: 'cpu', rank: 70, capacity: 2, quantum: 32, maxQueuedCost: 256 },
  { id: 'storage', rank: 65, capacity: 1, quantum: 24, maxQueuedCost: 192 },
  { id: 'gpu', rank: 60, capacity: 1, quantum: 24, maxQueuedCost: 192 },
  { id: 'render', rank: 55, capacity: 1, quantum: 16, maxQueuedCost: 128 },
  { id: 'maintenance', rank: 10, capacity: 1, quantum: 8, maxQueuedCost: 96 }
]);
function assertInteger(name, value, min = 0) {
  if (!Number.isInteger(value) || value < min) throw new Error(`${name} must be an integer >= ${min}`);
}
function assertFinite(name, value, min = 0) {
  if (value !== Number.POSITIVE_INFINITY && (!Number.isFinite(value) || value < min)) throw new Error(`${name} must be a finite number >= ${min}`);
}
function normalizePriority(priority = 'background') {
  if (!PRIORITY_RANK.has(priority)) throw new Error(`Unsupported priority: ${priority}`);
  return priority;
}
function normalizeLaneId(lane) {
  if (typeof lane !== 'string' || lane.length === 0) throw new Error('lane must be a non-empty string');
  return lane;
}
function normalizeDeps(dependsOn = []) {
  if (dependsOn == null) return [];
  const list = Array.isArray(dependsOn) ? dependsOn : [dependsOn];
  return list.map((value) => String(value)).filter(Boolean);
}
function deepFreezeTask(task) {
  return Object.freeze({ ...task, dependsOn: Object.freeze(task.dependsOn.slice()), fallbackLanes: Object.freeze(task.fallbackLanes.slice()) });
}
class LaneState {
  constructor(config) {
    this.id = normalizeLaneId(config.id);
    this.rank = config.rank ?? 0;
    this.capacity = config.capacity ?? 1;
    this.quantum = config.quantum ?? 1;
    this.maxQueuedCost = config.maxQueuedCost ?? Number.MAX_SAFE_INTEGER;
    this.healthy = config.healthy ?? true;
    this.healthReason = this.healthy ? null : 'initially-unhealthy';
    this.deficit = 0;
    this.queue = [];
    this.inFlight = new Map();
    this.queuedCost = 0;
    this.enqueuedCount = 0;
    this.dispatchedCount = 0;
    this.completedCount = 0;
    this.cancelledCount = 0;
    this.rejectedCount = 0;
    assertFinite(`lane.${this.id}.rank`, this.rank, -1000000);
    assertInteger(`lane.${this.id}.capacity`, this.capacity, 1);
    assertFinite(`lane.${this.id}.quantum`, this.quantum, 0.000001);
    assertFinite(`lane.${this.id}.maxQueuedCost`, this.maxQueuedCost, 1);
  }
}
export class CrossLaneScheduler {
  #trace;
  #lanes = new Map();
  #nextSeq = 1;
  #completed = new Set();
  #cancelled = new Set();
  #inFlight = new Map();
  #knownTaskIds = new Set();
  constructor({ label = 'cross-lane-scheduler', lanes = DEFAULT_LANES, maxQueuedCost = Number.MAX_SAFE_INTEGER, maxTaskCost = Number.MAX_SAFE_INTEGER, trace = null } = {}) {
    this.label = label;
    this.maxQueuedCost = maxQueuedCost;
    this.maxTaskCost = maxTaskCost;
    this.queuedCost = 0;
    this.queuedCount = 0;
    this.dispatchedCount = 0;
    this.completedCount = 0;
    this.cancelledCount = 0;
    this.rejectedCount = 0;
    this.routedCount = 0;
    this.deferredDependencyCount = 0;
    this.filteredDispatchBlockedCount = 0;
    this.#trace = trace;
    assertFinite('maxQueuedCost', maxQueuedCost, 1);
    assertFinite('maxTaskCost', maxTaskCost, 1);
    const laneList = Array.isArray(lanes) ? lanes : Object.entries(lanes).map(([id, config]) => ({ id, ...config }));
    for (const config of laneList) this.addLane(config);
    this.#emit('crosslane:create', { laneCount: this.#lanes.size, maxQueuedCost, maxTaskCost });
  }
  #emit(kind, payload = {}) { this.#trace?.emit(kind, { label: this.label, ...payload }); }
  #laneOrder() { return [...this.#lanes.values()].sort((a, b) => b.rank - a.rank || a.id.localeCompare(b.id)); }
  #sortLaneQueue(lane) { lane.queue.sort((a, b) => PRIORITY_RANK.get(b.priority) - PRIORITY_RANK.get(a.priority) || a.seq - b.seq); }
  addLane(config = {}) {
    const lane = new LaneState(config);
    if (this.#lanes.has(lane.id)) throw new Error(`lane already exists: ${lane.id}`);
    this.#lanes.set(lane.id, lane);
    this.#emit('crosslane:lane-create', { lane: lane.id, rank: lane.rank, capacity: lane.capacity, quantum: lane.quantum, maxQueuedCost: lane.maxQueuedCost, healthy: lane.healthy });
    return this.snapshotLane(lane.id);
  }
  #requireLane(laneId) {
    const id = normalizeLaneId(laneId);
    const lane = this.#lanes.get(id);
    if (!lane) throw new Error(`unknown lane: ${id}`);
    return lane;
  }
  markLaneUnhealthy(laneId, reason = 'unhealthy') {
    const lane = this.#requireLane(laneId);
    lane.healthy = false;
    lane.healthReason = String(reason);
    this.#emit('crosslane:lane-unhealthy', { lane: lane.id, reason: lane.healthReason, queuedCount: lane.queue.length, inFlight: lane.inFlight.size });
    return this.snapshotLane(lane.id);
  }
  markLaneHealthy(laneId, reason = 'healthy') {
    const lane = this.#requireLane(laneId);
    lane.healthy = true;
    lane.healthReason = null;
    this.#emit('crosslane:lane-healthy', { lane: lane.id, reason, queuedCount: lane.queue.length, inFlight: lane.inFlight.size });
    return this.snapshotLane(lane.id);
  }
  #chooseLane(requestedLane, fallbackLanes) {
    const requested = this.#requireLane(requestedLane);
    if (requested.healthy) return { lane: requested, requestedLane: requested.id, routed: false, reason: null };
    for (const candidateId of fallbackLanes) {
      const candidate = this.#lanes.get(candidateId);
      if (candidate?.healthy) return { lane: candidate, requestedLane: requested.id, routed: true, reason: `fallback-from-${requested.id}` };
    }
    return { lane: requested, requestedLane: requested.id, routed: false, reason: requested.healthReason || 'lane-unhealthy' };
  }
  enqueue({ id, lane = 'cpu', priority = 'background', cost = 1, flowId = 'default', dependsOn = [], fallbackLanes = [], payload = null, metadata = null } = {}) {
    const p = normalizePriority(priority);
    assertInteger('cost', cost, 1);
    const requestedLane = normalizeLaneId(lane);
    const normalizedFallbacks = fallbackLanes.map(normalizeLaneId);
    const before = this.snapshot();
    const reject = (targetLane, disposition, reason, extra = {}) => {
      if (targetLane) targetLane.rejectedCount += 1;
      this.rejectedCount += 1;
      const after = this.snapshot();
      const noMutation = before.queuedCount === after.queuedCount && before.queuedCost === after.queuedCost && before.inFlightCount === after.inFlightCount;
      this.#emit('crosslane:reject', { disposition, reason, requestedLane, lane: targetLane?.id ?? requestedLane, priority: p, cost, noMutation, ...extra });
      return Object.freeze({ accepted: false, disposition, reason, requestedLane, lane: targetLane?.id ?? requestedLane, priority: p, cost, noMutation, ...extra });
    };
    if (id != null && this.#knownTaskIds.has(String(id))) return reject(null, 'rejected-duplicate-id', 'duplicate-task-id');
    let choice;
    try { choice = this.#chooseLane(requestedLane, normalizedFallbacks); }
    catch (error) { return reject(null, 'rejected-unknown-lane', 'unknown-lane', { error: error.message }); }
    const target = choice.lane;
    if (!target.healthy && !choice.routed) return reject(target, 'rejected-lane-unhealthy', choice.reason);
    if (cost > this.maxTaskCost) return reject(target, 'rejected-task-cost', 'max-task-cost');
    if (this.queuedCost + cost > this.maxQueuedCost) return reject(target, 'rejected-global-queue-cost', 'max-queued-cost');
    if (target.queuedCost + cost > target.maxQueuedCost) return reject(target, 'rejected-lane-queue-cost', 'max-lane-queued-cost');
    const seq = this.#nextSeq++;
    const task = deepFreezeTask({ id: id == null ? `cross-task:${seq}` : String(id), seq, lane: target.id, requestedLane, routed: choice.routed, routeReason: choice.reason, priority: p, flowId: String(flowId), cost, dependsOn: normalizeDeps(dependsOn), fallbackLanes: normalizedFallbacks, payload, metadata });
    this.#knownTaskIds.add(task.id);
    target.queue.push(task);
    this.#sortLaneQueue(target);
    target.queuedCost += cost;
    target.enqueuedCount += 1;
    this.queuedCost += cost;
    this.queuedCount += 1;
    if (choice.routed) this.routedCount += 1;
    this.#emit(choice.routed ? 'crosslane:routed-enqueue' : 'crosslane:enqueue', { taskId: task.id, lane: task.lane, requestedLane, routeReason: choice.reason, priority: p, cost, dependsOn: task.dependsOn, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
    return Object.freeze({ accepted: true, disposition: choice.routed ? 'accepted-routed' : 'accepted', task, taskId: task.id, lane: task.lane, requestedLane, priority: p, cost, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
  }
  #depsReady(task) { return task.dependsOn.every((dep) => this.#completed.has(dep)); }
  #dispatchFilter({ flowId = null, metadataComponent = null } = {}) {
    const normalizedFlowId = flowId == null ? null : String(flowId);
    const normalizedComponent = metadataComponent == null ? null : String(metadataComponent);
    if (normalizedFlowId == null && normalizedComponent == null) return () => true;
    return (task) => {
      if (normalizedFlowId != null && task.flowId !== normalizedFlowId) return false;
      if (normalizedComponent != null && task.metadata?.component !== normalizedComponent) return false;
      return true;
    };
  }
  #findDispatchableIndex(lane, matches = () => true, { preserveFilteredLaneHead = false } = {}) {
    for (let i = 0; i < lane.queue.length; i += 1) {
      const task = lane.queue[i];
      if (!matches(task)) {
        const atLaneHead = i === 0;
        this.#emit('crosslane:skip-dispatch-filter', { taskId: task.id, lane: lane.id, flowId: task.flowId, component: task.metadata?.component ?? null, atLaneHead, preserveFilteredLaneHead });
        if (preserveFilteredLaneHead && atLaneHead) {
          this.filteredDispatchBlockedCount += 1;
          this.#emit('crosslane:blocked-dispatch-filter-head', { taskId: task.id, lane: lane.id, flowId: task.flowId, component: task.metadata?.component ?? null, queuedCount: lane.queue.length });
          return Object.freeze({ index: -1, blockedByFilterHead: task });
        }
        continue;
      }
      if (this.#depsReady(task)) return Object.freeze({ index: i, blockedByFilterHead: null });
      this.deferredDependencyCount += 1;
      this.#emit('crosslane:defer-dependency', { taskId: task.id, lane: lane.id, waitingFor: task.dependsOn.filter((dep) => !this.#completed.has(dep)), completedCount: this.#completed.size });
    }
    return Object.freeze({ index: -1, blockedByFilterHead: null });
  }
  cancelQueued(taskId, { reason = 'cancelled', disposition = 'cancelled-queued', metadata = null } = {}) {
    const id = String(taskId);
    for (const lane of this.#lanes.values()) {
      const idx = lane.queue.findIndex((task) => task.id === id);
      if (idx < 0) continue;
      const [task] = lane.queue.splice(idx, 1);
      lane.queuedCost -= task.cost;
      lane.cancelledCount += 1;
      this.queuedCost -= task.cost;
      this.queuedCount -= 1;
      this.cancelledCount += 1;
      this.#cancelled.add(id);
      this.#emit('crosslane:cancel-queued', { taskId: id, lane: lane.id, requestedLane: task.requestedLane, priority: task.priority, cost: task.cost, reason, disposition, queuedCount: this.queuedCount, queuedCost: this.queuedCost, metadata });
      return Object.freeze({ cancelled: true, disposition, taskId: id, lane: lane.id, reason, queuedCount: this.queuedCount, queuedCost: this.queuedCost, task });
    }
    const inFlight = this.#inFlight.has(id);
    const completed = this.#completed.has(id);
    const cancelled = this.#cancelled.has(id);
    const status = inFlight ? 'in-flight' : completed ? 'completed' : cancelled ? 'already-cancelled' : 'not-found';
    this.#emit('crosslane:cancel-queued-miss', { taskId: id, reason, status, queuedCount: this.queuedCount, inFlightCount: this.#inFlight.size });
    return Object.freeze({ cancelled: false, disposition: `not-cancelled-${status}`, taskId: id, reason, queuedCount: this.queuedCount, queuedCost: this.queuedCost, inFlight, completed, alreadyCancelled: cancelled });
  }
  dispatchNext(options = {}) {
    const matches = this.#dispatchFilter(options);
    const preserveFilteredLaneHead = options?.preserveFilteredLaneHead === true;
    const filterHeadBlocks = [];
    for (const lane of this.#laneOrder()) {
      if (!lane.healthy) {
        if (lane.queue.length) {
          const head = lane.queue[0];
          this.#emit('crosslane:skip-unhealthy-lane', { lane: lane.id, reason: lane.healthReason || 'unhealthy', queuedCount: lane.queue.length, headTaskId: head?.id ?? null, headPriority: head?.priority ?? null });
          this.#emit('crosslane:priority-blocked-but-skipped', { lane: lane.id, reason: 'unhealthy-lane', queuedCount: lane.queue.length, headTaskId: head?.id ?? null, headPriority: head?.priority ?? null });
        }
        continue;
      }
      if (lane.queue.length === 0) continue;
      if (lane.inFlight.size >= lane.capacity) {
        this.#emit('crosslane:lane-at-capacity', { lane: lane.id, capacity: lane.capacity, inFlight: lane.inFlight.size, queuedCount: lane.queue.length });
        continue;
      }
      const candidate = this.#findDispatchableIndex(lane, matches, { preserveFilteredLaneHead });
      if (candidate.blockedByFilterHead) {
        filterHeadBlocks.push(Object.freeze({ taskId: candidate.blockedByFilterHead.id, lane: lane.id, flowId: candidate.blockedByFilterHead.flowId, component: candidate.blockedByFilterHead.metadata?.component ?? null, priority: candidate.blockedByFilterHead.priority }));
        continue;
      }
      const idx = candidate.index;
      if (idx < 0) continue;
      const task = lane.queue[idx];
      lane.deficit += lane.quantum;
      this.#emit('crosslane:deficit-add', { lane: lane.id, quantum: lane.quantum, deficit: lane.deficit, headTaskId: task.id, headCost: task.cost });
      if (task.cost > lane.deficit) {
        this.#emit('crosslane:skip-insufficient-deficit', { taskId: task.id, lane: lane.id, cost: task.cost, deficit: lane.deficit });
        continue;
      }
      lane.queue.splice(idx, 1);
      lane.deficit -= task.cost;
      lane.queuedCost -= task.cost;
      lane.inFlight.set(task.id, task);
      this.#inFlight.set(task.id, task);
      lane.dispatchedCount += 1;
      this.dispatchedCount += 1;
      this.queuedCost -= task.cost;
      this.queuedCount -= 1;
      const out = Object.freeze({ dispatched: true, disposition: 'dispatched', task, lane: lane.id, remainingDeficit: lane.deficit, laneInFlight: lane.inFlight.size, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
      this.#emit('crosslane:dispatch', { taskId: task.id, lane: lane.id, requestedLane: task.requestedLane, priority: task.priority, cost: task.cost, laneInFlight: lane.inFlight.size, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
      return out;
    }
    const filtered = options?.flowId != null || options?.metadataComponent != null;
    const filterHeadBlocked = filterHeadBlocks.length > 0;
    const disposition = filterHeadBlocked ? 'empty-filtered-head-blocked' : (filtered ? 'empty-filtered' : 'empty');
    this.#emit('crosslane:dispatch-empty', { queuedCount: this.queuedCount, queuedCost: this.queuedCost, inFlightCount: this.#inFlight.size, filtered, preserveFilteredLaneHead, filterHeadBlocked, filterHeadBlocks, flowId: options?.flowId ?? null, metadataComponent: options?.metadataComponent ?? null });
    return Object.freeze({ dispatched: false, disposition, task: null, queuedCount: this.queuedCount, queuedCost: this.queuedCost, inFlightCount: this.#inFlight.size, filtered, preserveFilteredLaneHead, filterHeadBlocked, filterHeadBlocks: Object.freeze(filterHeadBlocks), flowId: options?.flowId ?? null, metadataComponent: options?.metadataComponent ?? null });
  }
  complete(taskId, { outcome = 'complete', metadata = null } = {}) {
    const id = String(taskId);
    const task = this.#inFlight.get(id);
    if (!task) throw new Error(`task is not in flight: ${id}`);
    const lane = this.#requireLane(task.lane);
    lane.inFlight.delete(id);
    this.#inFlight.delete(id);
    this.#completed.add(id);
    lane.completedCount += 1;
    this.completedCount += 1;
    this.#emit('crosslane:complete', { taskId: id, lane: lane.id, outcome, completedCount: this.completedCount, laneInFlight: lane.inFlight.size, metadata });
    return Object.freeze({ completed: true, taskId: id, lane: lane.id, outcome, completedCount: this.completedCount, laneInFlight: lane.inFlight.size, task });
  }
  markCompleted(taskId, { reason = 'external' } = {}) {
    const id = String(taskId);
    this.#completed.add(id);
    this.#emit('crosslane:mark-completed', { taskId: id, reason, completedCount: this.#completed.size });
    return Object.freeze({ completed: true, taskId: id, reason, completedCount: this.#completed.size });
  }
  snapshotLane(laneId) {
    const lane = this.#requireLane(laneId);
    return Object.freeze({ id: lane.id, rank: lane.rank, capacity: lane.capacity, quantum: lane.quantum, maxQueuedCost: lane.maxQueuedCost, healthy: lane.healthy, healthReason: lane.healthReason, deficit: lane.deficit, queuedCount: lane.queue.length, queuedCost: lane.queuedCost, inFlightCount: lane.inFlight.size, enqueuedCount: lane.enqueuedCount, dispatchedCount: lane.dispatchedCount, completedCount: lane.completedCount, cancelledCount: lane.cancelledCount, rejectedCount: lane.rejectedCount, queueIds: lane.queue.map((task) => task.id), inFlightIds: [...lane.inFlight.keys()] });
  }
  snapshot() {
    const lanes = this.#laneOrder().map((lane) => this.snapshotLane(lane.id));
    return Object.freeze({ label: this.label, queuedCount: this.queuedCount, queuedCost: this.queuedCost, inFlightCount: this.#inFlight.size, completedCount: this.completedCount, cancelledCount: this.cancelledCount, dispatchedCount: this.dispatchedCount, rejectedCount: this.rejectedCount, routedCount: this.routedCount, deferredDependencyCount: this.deferredDependencyCount, filteredDispatchBlockedCount: this.filteredDispatchBlockedCount, completedTaskIds: [...this.#completed].sort(), cancelledTaskIds: [...this.#cancelled].sort(), lanes });
  }
}
export function validateCrossLaneSchedulerSnapshot(snapshot, { requireSortedCompleted = true } = {}) {
  if (!snapshot || typeof snapshot !== 'object') throw new Error('snapshot must be an object');
  const lanes = Array.isArray(snapshot.lanes) ? snapshot.lanes : [];
  const errors = [];
  const queuedIds = new Set();
  const inFlightIds = new Set();
  let queuedCount = 0;
  let queuedCost = 0;
  let inFlightCount = 0;
  for (const lane of lanes) {
    if (!lane || typeof lane !== 'object') {
      errors.push('lane entry is not an object');
      continue;
    }
    const q = Array.isArray(lane.queueIds) ? lane.queueIds : [];
    const f = Array.isArray(lane.inFlightIds) ? lane.inFlightIds : [];
    queuedCount += q.length;
    queuedCost += Number(lane.queuedCost || 0);
    inFlightCount += f.length;
    if (q.length !== Number(lane.queuedCount || 0)) errors.push(`lane ${lane.id} queuedCount mismatch`);
    if (f.length !== Number(lane.inFlightCount || 0)) errors.push(`lane ${lane.id} inFlightCount mismatch`);
    if (Number(lane.inFlightCount || 0) > Number(lane.capacity || 0)) errors.push(`lane ${lane.id} exceeds capacity`);
    if (Number(lane.queuedCost || 0) < 0) errors.push(`lane ${lane.id} negative queuedCost`);
    if (Number(lane.deficit || 0) < 0) errors.push(`lane ${lane.id} negative deficit`);
    for (const id of q) {
      if (queuedIds.has(id)) errors.push(`duplicate queued task ${id}`);
      queuedIds.add(id);
    }
    for (const id of f) {
      if (inFlightIds.has(id)) errors.push(`duplicate in-flight task ${id}`);
      inFlightIds.add(id);
    }
  }
  for (const id of queuedIds) if (inFlightIds.has(id)) errors.push(`task appears queued and in-flight: ${id}`);
  if (queuedCount !== Number(snapshot.queuedCount || 0)) errors.push(`global queuedCount mismatch ${snapshot.queuedCount} != ${queuedCount}`);
  if (queuedCost !== Number(snapshot.queuedCost || 0)) errors.push(`global queuedCost mismatch ${snapshot.queuedCost} != ${queuedCost}`);
  if (inFlightCount !== Number(snapshot.inFlightCount || 0)) errors.push(`global inFlightCount mismatch ${snapshot.inFlightCount} != ${inFlightCount}`);
  const completed = Array.isArray(snapshot.completedTaskIds) ? snapshot.completedTaskIds : [];
  const cancelled = Array.isArray(snapshot.cancelledTaskIds) ? snapshot.cancelledTaskIds : [];
  if (completed.length !== new Set(completed).size) errors.push('duplicate completed task id');
  if (cancelled.length !== new Set(cancelled).size) errors.push('duplicate cancelled task id');
  for (const id of cancelled) if (queuedIds.has(id) || inFlightIds.has(id)) errors.push(`cancelled task still active: ${id}`);
  if (requireSortedCompleted && completed.join('\u0000') !== completed.slice().sort().join('\u0000')) errors.push('completedTaskIds not sorted');
  if (requireSortedCompleted && cancelled.join('\u0000') !== cancelled.slice().sort().join('\u0000')) errors.push('cancelledTaskIds not sorted');
  return Object.freeze({ ok: errors.length === 0, errors, queuedCount, queuedCost, inFlightCount, laneCount: lanes.length, completedCount: completed.length, cancelledCount: cancelled.length });
}
export function createCrossLaneScheduler(options = {}) { return new CrossLaneScheduler(options); }
export const CROSS_LANE_DEFAULT_LANES = DEFAULT_LANES;
export const CROSS_LANE_PRIORITY_ORDER = PRIORITY_ORDER;
