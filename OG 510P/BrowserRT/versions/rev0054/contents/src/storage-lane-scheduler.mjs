// BrowserRT rev0028 storage-lane scheduler integration scaffold.
// Fake-provider composition only. No OPFS, durability, throughput, or production scheduler claim. No production scheduler claim.

import { validateCrossLaneSchedulerSnapshot } from './cross-lane-scheduler.mjs';

const SUPPORTED_OPS = Object.freeze(['operation', 'enqueue', 'dequeue', 'ack', 'checkpoint', 'compact', 'snapshot']);
const SUPPORTED_OP_SET = new Set(SUPPORTED_OPS);

function summarizeResult(value) {
  if (value == null) return null;
  if (value instanceof Uint8Array) return { kind: 'Uint8Array', bytes: value.byteLength };
  if (typeof value !== 'object') return { value };
  const out = {};
  for (const key of ['disposition', 'seq', 'bytes', 'checksum32', 'pendingId', 'consumerId', 'deliveryCount', 'dryRun', 'candidateCount', 'deleted', 'deleteMisses', 'kind', 'version', 'opSeq', 'checksum']) if (key in value) out[key] = value[key];
  return out;
}
function describeError(error) {
  if (!error || typeof error !== 'object') return { name: 'Error', message: String(error), code: null };
  return { name: error.name || 'Error', message: error.message || String(error), code: error.code || error.storageDisposition || null };
}

export class StorageLaneExecutor {
  #trace;
  #ops = new Map();
  #results = new Map();
  #nextTaskSeq = 1;

  constructor({ label = 'storage-lane-executor', scheduler, mailbox = null, lane = 'storage', trace = null, markUnhealthyOnError = true } = {}) {
    if (!scheduler || typeof scheduler.enqueue !== 'function' || typeof scheduler.dispatchNext !== 'function' || typeof scheduler.complete !== 'function') throw new Error('StorageLaneExecutor requires a CrossLaneScheduler-like scheduler');
    this.label = label; this.scheduler = scheduler; this.mailbox = mailbox; this.lane = lane; this.markUnhealthyOnError = Boolean(markUnhealthyOnError); this.#trace = trace;
    this.stats = { scheduled: 0, rejected: 0, dispatched: 0, completed: 0, failed: 0, emptyDispatches: 0, laneHealthFailures: 0 };
    this.#emit('storage-lane:create', { lane, markUnhealthyOnError: this.markUnhealthyOnError });
  }
  #emit(kind, payload = {}) {
    const detail = { ...payload };
    if (Object.hasOwn(detail, 'kind')) {
      detail.opKind = detail.kind;
      delete detail.kind;
    }
    this.#trace?.emit(kind, { label: this.label, lane: this.lane, ...detail });
  }

  scheduleOperation({ id = null, kind = 'operation', lane = this.lane, fallbackLanes = [], priority = 'background', cost = 1, dependsOn = [], flowId = null, run, metadata = null } = {}) {
    if (typeof run !== 'function') throw new Error('scheduleOperation requires run()');
    const opId = id || `${this.label}:${kind}:${this.#nextTaskSeq++}`;
    const scheduler = this.scheduler.enqueue({ id: opId, lane, fallbackLanes, priority, cost, dependsOn, flowId: flowId || kind, payload: { component: 'StorageLaneExecutor', opId, kind }, metadata: { component: 'StorageLaneExecutor', kind, ...metadata } });
    if (!scheduler.accepted) {
      this.stats.rejected += 1;
      this.#emit('storage-lane:reject', { opId, kind, disposition: scheduler.disposition, reason: scheduler.reason, lane, noMutation: scheduler.noMutation === true });
      return Object.freeze({ accepted: false, opId, kind, scheduler });
    }
    this.stats.scheduled += 1;
    this.#ops.set(opId, { opId, kind, run });
    this.#emit('storage-lane:schedule', { opId, kind, lane: scheduler.lane, requestedLane: scheduler.requestedLane, priority, cost, dependsOn, fallbackLanes });
    return Object.freeze({ accepted: true, opId, kind, scheduler });
  }

  scheduleMailboxEnqueue(mailbox, payload, { id = null, priority = 'background', cost = null, dependsOn = [], lane = this.lane, fallbackLanes = [], enqueue = {} } = {}) {
    const bytes = typeof payload === 'string' ? new TextEncoder().encode(payload).byteLength : (payload?.byteLength ?? payload?.length ?? 1);
    return this.scheduleOperation({ id, kind: 'mailbox-enqueue', lane, fallbackLanes, priority, cost: cost ?? Math.max(1, Math.ceil(bytes / 16)), dependsOn, run: async () => mailbox.enqueue(payload, enqueue) });
  }
  scheduleMailboxDequeue(mailbox, { id = null, priority = 'user-visible', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], consumerId = 'storage-lane-consumer' } = {}) {
    return this.scheduleOperation({ id, kind: 'mailbox-dequeue', lane, fallbackLanes, priority, cost, dependsOn, run: async () => mailbox.dequeue({ consumerId }) });
  }
  scheduleMailboxCheckpoint(mailbox, { id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], label = null } = {}) {
    return this.scheduleOperation({ id, kind: 'mailbox-checkpoint', lane, fallbackLanes, priority, cost, dependsOn, run: async () => mailbox.checkpoint({ label }) });
  }
  scheduleMailboxCompact(mailbox, { id = null, priority = 'maintenance', cost = 2, dependsOn = [], lane = 'maintenance', fallbackLanes = [], dryRun = false, reason = 'storage-lane' } = {}) {
    return this.scheduleOperation({ id, kind: 'mailbox-compact', lane, fallbackLanes, priority, cost, dependsOn, run: async () => mailbox.compact({ dryRun, reason }) });
  }

  // Compatibility with the simpler submit/executeNext API used by the runtime object factory.
  submit(op, args = {}, options = {}) {
    if (!SUPPORTED_OP_SET.has(op)) throw new Error(`Unsupported storage lane op: ${op}`);
    const mailbox = this.mailbox;
    if (!mailbox) throw new Error('submit() requires the executor to be constructed with mailbox');
    if (op === 'enqueue') return this.scheduleMailboxEnqueue(mailbox, args.payload ?? args.bytes ?? '', { id: options.id, priority: options.priority, cost: options.cost, dependsOn: options.dependsOn, lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes, enqueue: { seq: args.seq ?? null, label: args.label ?? null } });
    if (op === 'dequeue') return this.scheduleMailboxDequeue(mailbox, { id: options.id, priority: options.priority, cost: options.cost, dependsOn: options.dependsOn, lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes, consumerId: args.consumerId });
    if (op === 'checkpoint') return this.scheduleMailboxCheckpoint(mailbox, { id: options.id, priority: options.priority, cost: options.cost, dependsOn: options.dependsOn, lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes, label: args.label });
    if (op === 'compact') return this.scheduleMailboxCompact(mailbox, { id: options.id, priority: options.priority, cost: options.cost, dependsOn: options.dependsOn, lane: options.lane || 'maintenance', fallbackLanes: options.fallbackLanes, dryRun: args.dryRun, reason: args.reason });
    if (op === 'ack') return this.scheduleOperation({ id: options.id, kind: 'mailbox-ack', lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes || [], priority: options.priority || 'user-visible', cost: options.cost || 1, dependsOn: options.dependsOn || [], run: async () => mailbox.ack(args.pendingId, { deleteBlock: args.deleteBlock }) });
    if (op === 'snapshot') return this.scheduleOperation({ id: options.id, kind: 'mailbox-snapshot', lane: options.lane || this.lane, fallbackLanes: options.fallbackLanes || [], priority: options.priority || 'background', cost: options.cost || 1, dependsOn: options.dependsOn || [], run: async () => mailbox.snapshot() });
  }

  async executeNext() { const drained = await this.drain({ maxSteps: 1 }); return drained.results[0] || Object.freeze({ dispatched: false, disposition: 'empty' }); }
  async executeDispatched(dispatched) { if (!dispatched?.task) throw new Error('executeDispatched requires a scheduler dispatch result'); return this.#runDispatched(dispatched); }

  async drain({ maxSteps = 100 } = {}) {
    const results = [];
    for (let i = 0; i < maxSteps; i += 1) {
      const dispatch = this.scheduler.dispatchNext();
      if (!dispatch.dispatched) { this.stats.emptyDispatches += 1; this.#emit('storage-lane:dispatch-empty', { disposition: dispatch.disposition || 'empty', queuedCount: dispatch.queuedCount, inFlightCount: dispatch.inFlightCount }); results.push(Object.freeze({ dispatched: false, disposition: dispatch.disposition || 'empty', scheduler: dispatch })); break; }
      results.push(await this.#runDispatched(dispatch));
    }
    return Object.freeze({ results, snapshot: this.snapshot() });
  }

  async #runDispatched(dispatch) {
    this.stats.dispatched += 1;
    const task = dispatch.task; const op = this.#ops.get(task.id);
    this.#emit('storage-lane:dispatch', { opId: task.id, kind: op?.kind || task.payload?.kind || 'unknown', lane: dispatch.lane, priority: task.priority, cost: task.cost });
    if (!op) { this.stats.failed += 1; this.scheduler.complete(task.id, { outcome: 'storage-lane:missing-op' }); return Object.freeze({ dispatched: true, ok: false, opId: task.id, lane: dispatch.lane, error: 'missing-operation' }); }
    try {
      const result = await op.run();
      if (String(result?.disposition || '').startsWith('rejected-provider')) { const err = new Error(`provider rejected ${op.kind}: ${result.reason}`); err.name = 'BrowserRTStorageLaneProviderError'; err.code = result.reason || 'BRT_STORAGE_PROVIDER_REJECTED'; throw err; }
      this.#results.set(op.opId, result); this.#ops.delete(op.opId); this.scheduler.complete(task.id, { outcome: `storage-lane:${op.kind}:complete`, metadata: summarizeResult(result) });
      this.stats.completed += 1; this.#emit('storage-lane:complete', { opId: op.opId, kind: op.kind, lane: dispatch.lane, result: summarizeResult(result) });
      return Object.freeze({ dispatched: true, ok: true, opId: op.opId, taskId: op.opId, op: op.kind, lane: dispatch.lane, result });
    } catch (error) {
      const detail = describeError(error);
      this.#ops.delete(op.opId); this.stats.failed += 1;
      if (this.markUnhealthyOnError && detail.code && String(detail.code).startsWith('BRT_STORAGE')) { this.scheduler.markLaneUnhealthy(dispatch.lane, detail.code); this.stats.laneHealthFailures += 1; this.#emit('storage-lane:provider-unhealthy', { opId: op.opId, lane: dispatch.lane, code: detail.code }); }
      this.scheduler.complete(task.id, { outcome: `storage-lane:${op.kind}:error`, metadata: detail });
      this.#emit('storage-lane:error', { opId: op.opId, kind: op.kind, lane: dispatch.lane, error: detail });
      return Object.freeze({ dispatched: true, ok: false, opId: op.opId, taskId: op.opId, op: op.kind, lane: dispatch.lane, error: detail });
    }
  }

  markHealthy(lane = this.lane, reason = 'manual-recovery') { const row = this.scheduler.markLaneHealthy(lane, reason); this.#emit('storage-lane:provider-healthy', { lane, reason, queuedCount: row.queuedCount, inFlightCount: row.inFlightCount }); return row; }
  markUnhealthy(lane = this.lane, reason = 'manual-unhealthy') { const row = this.scheduler.markLaneUnhealthy(lane, reason); this.#emit('storage-lane:provider-unhealthy', { lane, reason, queuedCount: row.queuedCount, inFlightCount: row.inFlightCount }); return row; }
  result(opId) { return this.#results.get(String(opId)); }
  resultMap() { return new Map(this.#results); }
  snapshot() { const scheduler = this.scheduler.snapshot(); return Object.freeze({ label: this.label, pendingOperationCount: this.#ops.size, resultCount: this.#results.size, stats: { ...this.stats }, schedulerValidation: validateCrossLaneSchedulerSnapshot(scheduler), scheduler, mailbox: this.mailbox?.snapshot?.() ?? null }); }
}

export function validateStorageLaneExecutorSnapshot(snapshot, { requireMailbox = true } = {}) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  if (!isObj(snapshot)) {
    return Object.freeze({ ok: false, errors: ['snapshot must be an object'], pendingOperationCount: 0, resultCount: 0, queuedCount: 0, inFlightCount: 0, mailboxQueueDepth: 0, mailboxPendingCount: 0 });
  }
  const nonNeg = (name, value) => { if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`); };
  nonNeg('pendingOperationCount', snapshot.pendingOperationCount);
  nonNeg('resultCount', snapshot.resultCount);
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  const scheduler = snapshot.scheduler;
  if (!isObj(scheduler)) errors.push('scheduler snapshot must be present');
  const schedulerValidation = snapshot.schedulerValidation;
  if (!isObj(schedulerValidation) || schedulerValidation.ok !== true) errors.push('schedulerValidation.ok must be true');
  const queuedCount = Number.isInteger(scheduler?.queuedCount) ? scheduler.queuedCount : 0;
  const inFlightCount = Number.isInteger(scheduler?.inFlightCount) ? scheduler.inFlightCount : 0;
  if (scheduler && Array.isArray(scheduler.lanes)) {
    const laneQueued = scheduler.lanes.reduce((sum, lane) => sum + (Number.isInteger(lane.queuedCount) ? lane.queuedCount : 0), 0);
    const laneInFlight = scheduler.lanes.reduce((sum, lane) => sum + (Number.isInteger(lane.inFlightCount) ? lane.inFlightCount : 0), 0);
    if (laneQueued !== queuedCount) errors.push(`scheduler queuedCount mismatch: lanes=${laneQueued} global=${queuedCount}`);
    if (laneInFlight !== inFlightCount) errors.push(`scheduler inFlightCount mismatch: lanes=${laneInFlight} global=${inFlightCount}`);
  } else if (scheduler) errors.push('scheduler.lanes must be an array');

  const mailbox = snapshot.mailbox;
  if (requireMailbox && !isObj(mailbox)) errors.push('mailbox snapshot must be present');
  let mailboxQueueDepth = 0;
  let mailboxPendingCount = 0;
  if (isObj(mailbox)) {
    mailboxQueueDepth = mailbox.queueDepth;
    mailboxPendingCount = mailbox.pendingCount;
    nonNeg('mailbox.queueDepth', mailboxQueueDepth);
    nonNeg('mailbox.pendingCount', mailboxPendingCount);
    if (Array.isArray(mailbox.queueSeqs) && mailbox.queueSeqs.length !== mailboxQueueDepth) errors.push('mailbox queueSeqs length must match queueDepth');
    if (Array.isArray(mailbox.pendingSeqs) && mailbox.pendingSeqs.length !== mailboxPendingCount) errors.push('mailbox pendingSeqs length must match pendingCount');
    if (Number.isInteger(mailbox.retainedBlockCount) && Array.isArray(mailbox.liveBlockDigests) && mailbox.retainedBlockCount < mailbox.liveBlockDigests.length) errors.push('retainedBlockCount must cover liveBlockDigests');
    const provider = mailbox.providerSnapshot;
    if (isObj(provider) && Number.isInteger(provider.blockCount) && provider.blockCount < mailbox.liveBlockDigests?.length) errors.push('provider blockCount must cover liveBlockDigests');
  }
  return Object.freeze({ ok: errors.length === 0, errors, pendingOperationCount: snapshot.pendingOperationCount || 0, resultCount: snapshot.resultCount || 0, queuedCount, inFlightCount, mailboxQueueDepth, mailboxPendingCount });
}

export function createStorageLaneExecutor(config = {}) { return new StorageLaneExecutor(config); }
export const STORAGE_LANE_EXECUTOR_SUPPORTED_OPS = SUPPORTED_OPS;
