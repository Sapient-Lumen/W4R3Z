// BrowserRT rev0039 block-store lane adapter.
// Generic fake/browser provider bridge: schedules block-store operations through
// CrossLaneScheduler/StorageLaneExecutor without claiming durability, quota, OPFS
// crash recovery, throughput, or production storage scheduling.

import { createStorageLaneExecutor, validateStorageLaneExecutorSnapshot } from './storage-lane-scheduler.mjs';

const BLOCK_STORE_OPS = Object.freeze(['put', 'get', 'has', 'verify', 'delete', 'estimate', 'snapshot', 'cleanup']);
const BLOCK_STORE_OP_SET = new Set(BLOCK_STORE_OPS);

function assertScheduler(scheduler) {
  if (!scheduler || typeof scheduler.enqueue !== 'function' || typeof scheduler.dispatchNext !== 'function' || typeof scheduler.complete !== 'function') {
    throw new Error('BlockStoreLaneAdapter requires a CrossLaneScheduler-like scheduler when no executor is supplied');
  }
}

function assertStore(store, methods = ['put', 'get', 'has', 'verify', 'delete', 'snapshot']) {
  for (const method of methods) {
    if (!store || typeof store[method] !== 'function') throw new Error(`BlockStoreLaneAdapter requires a store with ${method}()`);
  }
}

function payloadBytes(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value).byteLength;
  if (value instanceof ArrayBuffer) return value.byteLength;
  if (ArrayBuffer.isView(value)) return value.byteLength;
  if (value && typeof value === 'object' && Number.isFinite(value.bytes)) return Number(value.bytes);
  return 1;
}

function summarize(value) {
  if (value instanceof Uint8Array) return { kind: 'Uint8Array', bytes: value.byteLength };
  if (value instanceof ArrayBuffer) return { kind: 'ArrayBuffer', bytes: value.byteLength };
  if (value == null || typeof value !== 'object') return { value };
  const out = {};
  for (const key of ['digest', 'hash', 'bytes', 'duplicate', 'present', 'ok', 'deleted', 'quota', 'usage', 'path', 'provider', 'blockCount', 'opened', 'available']) {
    if (Object.hasOwn(value, key)) out[key] = value[key];
  }
  if (value.ref && typeof value.ref === 'object') out.ref = { id: value.ref.id, digest: value.ref.digest, hash: value.ref.hash, backend: value.ref.backend, bytes: value.ref.bytes, path: value.ref.path };
  return out;
}

export class BlockStoreLaneAdapter {
  #trace;
  #store;
  #executor;
  #results = new Map();
  #nextOpSeq = 1;

  constructor({ label = 'block-store-lane-adapter', store, executor = null, scheduler = null, lane = 'storage', trace = null, markUnhealthyOnError = true } = {}) {
    assertStore(store, ['put', 'get', 'has', 'verify', 'delete', 'snapshot']);
    if (!executor) assertScheduler(scheduler);
    this.label = label;
    this.lane = lane;
    this.#store = store;
    this.#executor = executor || createStorageLaneExecutor({ label: `${label}:executor`, scheduler, mailbox: null, lane, trace, markUnhealthyOnError });
    this.#trace = trace;
    this.stats = { scheduled: 0, rejected: 0, completed: 0, failed: 0, emptyDispatches: 0 };
    this.#emit('block-store-lane:create', { store: this.storeName, provider: this.providerName, lane });
  }

  get store() { return this.#store; }
  get executor() { return this.#executor; }
  get scheduler() { return this.#executor.scheduler; }
  get storeName() { return this.#store.name || this.#store.label || 'unnamed-block-store'; }
  get providerName() { return this.#store.provider || this.#store.name || 'unknown-block-provider'; }

  #emit(kind, payload = {}) { this.#trace?.emit(kind, { label: this.label, lane: this.lane, ...payload }); }
  #opId(kind, id) { return id || `${this.label}:${kind}:${this.#nextOpSeq++}`; }

  schedule(kind, run, { id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], metadata = null } = {}) {
    if (!BLOCK_STORE_OP_SET.has(kind)) throw new Error(`Unsupported block-store lane op: ${kind}`);
    const opId = this.#opId(kind, id);
    const accepted = this.#executor.scheduleOperation({
      id: opId,
      kind: `block-${kind}`,
      lane,
      fallbackLanes,
      priority,
      cost,
      dependsOn,
      flowId: 'block-store',
      metadata: { component: 'BlockStoreLaneAdapter', blockStoreOp: kind, store: this.storeName, provider: this.providerName, ...(metadata || {}) },
      run: async () => {
        this.#emit('block-store-lane:op-start', { opId, op: kind, store: this.storeName, provider: this.providerName });
        const value = await run();
        this.#results.set(opId, value);
        this.stats.completed += 1;
        this.#emit('block-store-lane:op-complete', { opId, op: kind, result: summarize(value) });
        return value;
      }
    });
    if (!accepted.accepted) {
      this.stats.rejected += 1;
      this.#emit('block-store-lane:reject', { opId, op: kind, reason: accepted.scheduler?.reason, disposition: accepted.scheduler?.disposition, noMutation: accepted.scheduler?.noMutation === true });
      return Object.freeze({ ...accepted, adapterOp: kind });
    }
    this.stats.scheduled += 1;
    this.#emit('block-store-lane:schedule', { opId, op: kind, priority, cost, dependsOn, lane, fallbackLanes });
    return Object.freeze({ ...accepted, adapterOp: kind });
  }

  schedulePut(payload, { id = null, priority = 'user-visible', cost = null, dependsOn = [], lane = this.lane, fallbackLanes = [], label = null, fields = {} } = {}) {
    const bytes = payloadBytes(payload);
    return this.schedule('put', () => this.#store.put(payload, { label, ...fields }), { id, priority, cost: cost ?? Math.max(1, Math.ceil(bytes / 16)), dependsOn, lane, fallbackLanes, metadata: { bytes, label } });
  }

  scheduleGet(ref, options = {}) { return this.schedule('get', () => this.#store.get(ref), { priority: 'user-visible', cost: 1, ...options, metadata: { refDigest: ref?.digest || ref?.id || String(ref) } }); }
  scheduleHas(ref, options = {}) { return this.schedule('has', () => this.#store.has(ref), { priority: 'user-visible', cost: 1, ...options, metadata: { refDigest: ref?.digest || ref?.id || String(ref) } }); }
  scheduleVerify(ref, options = {}) { return this.schedule('verify', () => this.#store.verify(ref), { priority: 'user-visible', cost: 1, ...options, metadata: { refDigest: ref?.digest || ref?.id || String(ref) } }); }
  scheduleDelete(ref, options = {}) { return this.schedule('delete', () => this.#store.delete(ref), { priority: 'user-visible', cost: 1, ...options, metadata: { refDigest: ref?.digest || ref?.id || String(ref) } }); }
  scheduleEstimate(options = {}) {
    const run = typeof this.#store.estimate === 'function' ? () => this.#store.estimate() : async () => ({ quota: null, usage: null, unavailable: true });
    return this.schedule('estimate', run, { priority: 'background', cost: 1, ...options });
  }
  scheduleSnapshot(options = {}) { return this.schedule('snapshot', () => this.#store.snapshot(), { priority: 'background', cost: 1, ...options }); }
  scheduleCleanupForTest(options = {}) {
    if (typeof this.#store.cleanupForTest !== 'function') throw new Error('block-store cleanupForTest is unavailable');
    return this.schedule('cleanup', () => this.#store.cleanupForTest(), { priority: 'maintenance', cost: 1, lane: 'maintenance', ...options });
  }

  submit(op, args = {}, options = {}) {
    if (op === 'put' || op === 'block-put') return this.schedulePut(args.payload ?? args.bytes ?? '', options);
    if (op === 'get' || op === 'block-get') return this.scheduleGet(args.ref ?? args.digest, options);
    if (op === 'has' || op === 'block-has') return this.scheduleHas(args.ref ?? args.digest, options);
    if (op === 'verify' || op === 'block-verify') return this.scheduleVerify(args.ref ?? args.digest, options);
    if (op === 'delete' || op === 'block-delete') return this.scheduleDelete(args.ref ?? args.digest, options);
    if (op === 'estimate' || op === 'block-estimate') return this.scheduleEstimate(options);
    if (op === 'snapshot' || op === 'block-snapshot') return this.scheduleSnapshot(options);
    if (op === 'cleanup' || op === 'cleanupForTest' || op === 'block-cleanup') return this.scheduleCleanupForTest(options);
    throw new Error(`Unsupported block-store lane submit op: ${op}`);
  }

  async drain(options = {}) {
    const drained = await this.#executor.drain(options);
    for (const row of drained.results) {
      if (row.dispatched === false) this.stats.emptyDispatches += 1;
      if (row.dispatched && row.ok === false) this.stats.failed += 1;
    }
    return drained;
  }

  async executeNext() { const drained = await this.drain({ maxSteps: 1 }); return drained.results[0] || Object.freeze({ dispatched: false, disposition: 'empty' }); }
  result(opId) { return this.#results.get(String(opId)) ?? this.#executor.result?.(opId); }
  resultSummary(opId) { return summarize(this.result(opId)); }
  markHealthy(lane = this.lane, reason = 'manual-recovery') { return this.#executor.markHealthy(lane, reason); }
  markUnhealthy(lane = this.lane, reason = 'manual-unhealthy') { return this.#executor.markUnhealthy(lane, reason); }

  snapshot() {
    const executor = this.#executor.snapshot();
    const store = this.#store.snapshot();
    return Object.freeze({ label: this.label, lane: this.lane, storeName: this.storeName, provider: this.providerName, stats: { ...this.stats }, resultCount: this.#results.size, store, executor, executorValidation: validateStorageLaneExecutorSnapshot(executor, { requireMailbox: false }) });
  }
}

export function validateBlockStoreLaneAdapterSnapshot(snapshot) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  if (!isObj(snapshot)) return Object.freeze({ ok: false, errors: ['snapshot must be an object'], resultCount: 0 });
  if (typeof snapshot.label !== 'string' || !snapshot.label) errors.push('label must be non-empty string');
  if (typeof snapshot.provider !== 'string' || !snapshot.provider) errors.push('provider must be non-empty string');
  if (!isObj(snapshot.store)) errors.push('store snapshot must be present');
  if (!isObj(snapshot.executor)) errors.push('executor snapshot must be present');
  if (!isObj(snapshot.executorValidation) || snapshot.executorValidation.ok !== true) errors.push('executorValidation.ok must be true');
  if (!Number.isInteger(snapshot.resultCount) || snapshot.resultCount < 0) errors.push('resultCount must be non-negative integer');
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  return Object.freeze({ ok: errors.length === 0, errors, resultCount: snapshot.resultCount || 0 });
}

export function createBlockStoreLaneAdapter(config = {}) { return new BlockStoreLaneAdapter(config); }
export const BLOCK_STORE_LANE_ADAPTER_OPS = BLOCK_STORE_OPS;
