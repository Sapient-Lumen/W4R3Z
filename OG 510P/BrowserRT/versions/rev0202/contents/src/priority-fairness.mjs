const PRIORITY_ORDER = Object.freeze(['critical', 'user-blocking', 'user-visible', 'background', 'maintenance']);
const PRIORITY_RANK = new Map(PRIORITY_ORDER.map((p, idx) => [p, PRIORITY_ORDER.length - idx]));
const DEFAULT_PRIORITY_QUANTA = Object.freeze({
  critical: 64,
  'user-blocking': 32,
  'user-visible': 16,
  background: 8,
  maintenance: 4
});
function assertInteger(name, value, min = 0) {
  if (!Number.isInteger(value) || value < min) throw new Error(`${name} must be an integer >= ${min}`);
}
function assertFinite(name, value, min = 0) {
  if (!Number.isFinite(value) || value < min) throw new Error(`${name} must be a finite number >= ${min}`);
}
function normalizePriority(priority) {
  const p = priority ?? 'background';
  if (!PRIORITY_RANK.has(p)) throw new Error(`Unsupported priority: ${p}`);
  return p;
}
function taskIdFrom(fields, next) {
  return fields.id ?? `fair-task:${next}`;
}
class FairFlow {
  constructor({ flowId, priority, weight = 1 }) {
    assertFinite('weight', weight, 0.000001);
    this.flowId = String(flowId);
    this.priority = normalizePriority(priority);
    this.weight = weight;
    this.deficit = 0;
    this.queue = [];
    this.queuedCost = 0;
    this.enqueuedCount = 0;
    this.dispatchedCount = 0;
    this.dispatchedCost = 0;
    this.rejectedCount = 0;
  }
}
export class PriorityFairScheduler {
  #trace;
  #flows = new Map();
  #states = new Map();
  #nextTask = 1;
  constructor({
    label = 'priority-fair-scheduler',
    priorityQuanta = {},
    maxQueuedCost = Number.POSITIVE_INFINITY,
    maxFlowQueuedCost = Number.POSITIVE_INFINITY,
    maxTaskCost = Number.POSITIVE_INFINITY,
    trace = null
  } = {}) {
    this.label = label;
    this.priorityQuanta = Object.freeze({ ...DEFAULT_PRIORITY_QUANTA, ...priorityQuanta });
    for (const [priority, quantum] of Object.entries(this.priorityQuanta)) {
      normalizePriority(priority);
      assertFinite(`priorityQuanta.${priority}`, quantum, 0.000001);
    }
    assertFinite('maxQueuedCost', maxQueuedCost, 1);
    assertFinite('maxFlowQueuedCost', maxFlowQueuedCost, 1);
    assertFinite('maxTaskCost', maxTaskCost, 1);
    this.maxQueuedCost = maxQueuedCost;
    this.maxFlowQueuedCost = maxFlowQueuedCost;
    this.maxTaskCost = maxTaskCost;
    this.queuedCost = 0;
    this.queuedCount = 0;
    this.dispatchedCount = 0;
    this.dispatchedCost = 0;
    this.rejectedCount = 0;
    this.#trace = trace;
    for (const priority of PRIORITY_ORDER) this.#states.set(priority, { order: [], cursor: 0 });
    this.#emit('fair:create', { priorityQuanta: this.priorityQuanta, maxQueuedCost, maxFlowQueuedCost, maxTaskCost });
  }
  #emit(kind, payload = {}) { this.#trace?.emit(kind, { label: this.label, ...payload }); }
  #flowKey(priority, flowId) { return `${priority}\u0000${flowId}`; }
  #getFlow(priority, flowId, weight = 1) {
    const key = this.#flowKey(priority, flowId);
    let flow = this.#flows.get(key);
    if (!flow) {
      flow = new FairFlow({ priority, flowId, weight });
      this.#flows.set(key, flow);
      this.#emit('fair:flow-create', { priority, flowId: flow.flowId, weight: flow.weight });
    }
    return flow;
  }
  #activate(flow) {
    const state = this.#states.get(flow.priority);
    if (!state.order.includes(flow.flowId)) {
      state.order.push(flow.flowId);
      this.#emit('fair:flow-activate', { priority: flow.priority, flowId: flow.flowId, activeFlowCount: state.order.length });
    }
  }
  #deactivateIfEmpty(flow) {
    if (flow.queue.length > 0) return;
    const state = this.#states.get(flow.priority);
    const idx = state.order.indexOf(flow.flowId);
    if (idx >= 0) {
      state.order.splice(idx, 1);
      if (state.cursor > idx) state.cursor -= 1;
      if (state.cursor >= state.order.length) state.cursor = 0;
      this.#emit('fair:flow-empty', { priority: flow.priority, flowId: flow.flowId, activeFlowCount: state.order.length });
    }
  }
  enqueue({ id, flowId, priority = 'background', cost = 1, weight = 1, payload = null, metadata = null } = {}) {
    const p = normalizePriority(priority);
    if (flowId == null || flowId === '') throw new Error('flowId is required');
    assertInteger('cost', cost, 1);
    assertFinite('weight', weight, 0.000001);
    const flow = this.#getFlow(p, String(flowId), weight);
    const before = this.snapshot();
    const reject = (disposition, reason) => {
      flow.rejectedCount += 1;
      this.rejectedCount += 1;
      const after = this.snapshot();
      const noMutation = before.queuedCost === after.queuedCost && before.queuedCount === after.queuedCount;
      this.#emit('fair:reject', { disposition, reason, priority: p, flowId: flow.flowId, cost, queuedCost: this.queuedCost, flowQueuedCost: flow.queuedCost, noMutation });
      return Object.freeze({ accepted: false, disposition, reason, priority: p, flowId: flow.flowId, cost, noMutation });
    };
    if (cost > this.maxTaskCost) return reject('rejected-task-cost', 'max-task-cost');
    if (this.queuedCost + cost > this.maxQueuedCost) return reject('rejected-global-queue-cost', 'max-queued-cost');
    if (flow.queuedCost + cost > this.maxFlowQueuedCost) return reject('rejected-flow-queue-cost', 'max-flow-queued-cost');
    const task = Object.freeze({ id: taskIdFrom({ id }, this.#nextTask++), flowId: flow.flowId, priority: p, cost, payload, metadata, enqueuedSeq: this.#nextTask });
    flow.queue.push(task);
    flow.queuedCost += cost;
    flow.enqueuedCount += 1;
    this.queuedCost += cost;
    this.queuedCount += 1;
    this.#activate(flow);
    this.#emit('fair:enqueue', { taskId: task.id, priority: p, flowId: flow.flowId, cost, queuedCost: this.queuedCost, flowQueuedCost: flow.queuedCost });
    return Object.freeze({ accepted: true, disposition: 'accepted', taskId: task.id, task, priority: p, flowId: flow.flowId, cost, queuedCost: this.queuedCost, flowQueuedCost: flow.queuedCost });
  }
  dispatchNext() {
    for (const priority of PRIORITY_ORDER) {
      const dispatched = this.#dispatchFromPriority(priority);
      if (dispatched) return dispatched;
    }
    this.#emit('fair:dispatch-empty', { queuedCount: this.queuedCount, queuedCost: this.queuedCost });
    return Object.freeze({ dispatched: false, disposition: 'empty', task: null, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
  }
  #dispatchFromPriority(priority) {
    const state = this.#states.get(priority);
    if (!state.order.length) return null;
    const maxScans = Math.max(1, state.order.length * 4);
    for (let scan = 0; scan < maxScans && state.order.length; scan += 1) {
      if (state.cursor >= state.order.length) state.cursor = 0;
      const flowId = state.order[state.cursor];
      const flow = this.#flows.get(this.#flowKey(priority, flowId));
      if (!flow || flow.queue.length === 0) {
        if (flow) this.#deactivateIfEmpty(flow);
        else state.order.splice(state.cursor, 1);
        continue;
      }
      const quantum = this.priorityQuanta[priority] * flow.weight;
      flow.deficit += quantum;
      this.#emit('fair:deficit-add', { priority, flowId, quantum, deficit: flow.deficit });
      const head = flow.queue[0];
      if (head.cost <= flow.deficit) {
        flow.queue.shift();
        flow.deficit -= head.cost;
        flow.queuedCost -= head.cost;
        flow.dispatchedCount += 1;
        flow.dispatchedCost += head.cost;
        this.queuedCost -= head.cost;
        this.queuedCount -= 1;
        this.dispatchedCount += 1;
        this.dispatchedCost += head.cost;
        const out = Object.freeze({ dispatched: true, disposition: 'dispatched', task: head, priority, flowId, remainingDeficit: flow.deficit, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
        this.#emit('fair:dispatch', { taskId: head.id, priority, flowId, cost: head.cost, remainingDeficit: flow.deficit, queuedCount: this.queuedCount, queuedCost: this.queuedCost });
        if (flow.queue.length === 0) this.#deactivateIfEmpty(flow);
        else state.cursor = (state.cursor + 1) % state.order.length;
        return out;
      }
      this.#emit('fair:skip-insufficient-deficit', { priority, flowId, headCost: head.cost, deficit: flow.deficit });
      state.cursor = (state.cursor + 1) % state.order.length;
    }
    return null;
  }
  drain({ limit = Number.POSITIVE_INFINITY } = {}) {
    if (limit !== Number.POSITIVE_INFINITY) assertInteger('limit', limit, 1);
    const rows = [];
    while (rows.length < limit) {
      const next = this.dispatchNext();
      if (!next.dispatched) break;
      rows.push(next.task);
    }
    return rows;
  }
  snapshot() {
    const flows = [];
    for (const flow of this.#flows.values()) {
      flows.push({
        flowId: flow.flowId,
        priority: flow.priority,
        weight: flow.weight,
        deficit: flow.deficit,
        queuedCount: flow.queue.length,
        queuedCost: flow.queuedCost,
        enqueuedCount: flow.enqueuedCount,
        dispatchedCount: flow.dispatchedCount,
        dispatchedCost: flow.dispatchedCost,
        rejectedCount: flow.rejectedCount
      });
    }
    flows.sort((a, b) => a.priority.localeCompare(b.priority) || a.flowId.localeCompare(b.flowId));
    return Object.freeze({
      label: this.label,
      queuedCount: this.queuedCount,
      queuedCost: this.queuedCost,
      dispatchedCount: this.dispatchedCount,
      dispatchedCost: this.dispatchedCost,
      rejectedCount: this.rejectedCount,
      activeFlows: Object.fromEntries(PRIORITY_ORDER.map((p) => [p, this.#states.get(p).order.slice()])),
      flows
    });
  }
}
export function createPriorityFairScheduler(options = {}) {
  return new PriorityFairScheduler(options);
}
export const PRIORITY_FAIRNESS_ORDER = PRIORITY_ORDER;
