const BLOCK_STORE_OPS = Object.freeze(['put', 'get', 'has', 'verify', 'delete', 'estimate', 'snapshot', 'cleanup']);
const RUNTIME_CORE_BLOCK_STORE_FLOW_ID = 'runtime-core-block-store';
const RUNTIME_CORE_BLOCK_STORE_COMPONENT = 'RuntimeCoreBlockStoreLaneAdapter';
const BLOCK_STORE_OP_SET = new Set(BLOCK_STORE_OPS);
function assertScheduler(scheduler) {
  if (!scheduler || typeof scheduler.enqueue !== 'function' || typeof scheduler.dispatchNext !== 'function' || typeof scheduler.complete !== 'function' || typeof scheduler.cancelQueued !== 'function') {
    throw new Error('RuntimeCoreBlockStoreLaneAdapter requires a CrossLaneScheduler-like scheduler with cancelQueued()');
  }
}
function assertStore(store, methods = ['put', 'get', 'has', 'verify', 'delete', 'snapshot']) {
  for (const method of methods) {
    if (!store || typeof store[method] !== 'function') throw new Error(`RuntimeCoreBlockStoreLaneAdapter requires a store with ${method}()`);
  }
}
function payloadBytes(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value).byteLength;
  if (value instanceof ArrayBuffer) return value.byteLength;
  if (ArrayBuffer.isView(value)) return value.byteLength;
  if (value && typeof value === 'object' && Number.isFinite(value.bytes)) return Number(value.bytes);
  return 1;
}
function finiteNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  const n = Number(value);
  return Number.isFinite(n) && n >= 0 ? n : null;
}
function captureBudgetError(error) {
  return Object.freeze({ name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null });
}
function storePutGrowthEstimate(store, payload, requestedBytes, providerOptions = {}) {
  const normalizedRequestedBytes = Math.max(0, Math.floor(Number(requestedBytes) || 0));
  if (!store || typeof store.estimatePutGrowth !== 'function') {
    return Object.freeze({ available: false, checked: false, duplicate: false, reason: 'store-put-growth-estimate-unavailable', requestedBytes: normalizedRequestedBytes, growthBytes: normalizedRequestedBytes });
  }
  try {
    const estimate = store.estimatePutGrowth(payload, { ...providerOptions, requestedBytes: normalizedRequestedBytes });
    if (estimate && typeof estimate.then === 'function') {
      return Object.freeze({ available: true, checked: false, duplicate: false, reason: 'store-put-growth-estimate-async-skipped', requestedBytes: normalizedRequestedBytes, growthBytes: normalizedRequestedBytes });
    }
    const growthBytes = Math.max(0, Math.floor(Number(estimate?.growthBytes ?? normalizedRequestedBytes) || 0));
    return Object.freeze({
      available: true,
      checked: estimate?.checked === true,
      duplicate: estimate?.duplicate === true,
      reason: typeof estimate?.reason === 'string' ? estimate.reason : (estimate?.duplicate === true ? 'known-duplicate' : 'duplicate-unknown'),
      requestedBytes: normalizedRequestedBytes,
      growthBytes,
      digest: typeof estimate?.digest === 'string' ? estimate.digest : null
    });
  } catch (error) {
    return Object.freeze({ available: true, checked: false, duplicate: false, reason: 'store-put-growth-estimate-failed', requestedBytes: normalizedRequestedBytes, growthBytes: normalizedRequestedBytes, error: captureBudgetError(error) });
  }
}
function storeBudgetPreflight(store, growthBytes, { pendingBytes = 0, requestedBytes = growthBytes, growthEstimate = null, requireSynchronousEstimate = true } = {}) {
  const reservedBytes = Math.max(0, Math.floor(Number(pendingBytes) || 0));
  const normalizedRequestedBytes = Math.max(0, Math.floor(Number(requestedBytes) || 0));
  const normalizedGrowthBytes = Math.max(0, Math.floor(Number(growthBytes) || 0));
  const duplicate = growthEstimate?.duplicate === true;
  if (!store || typeof store.estimate !== 'function') return Object.freeze({ available: false, checked: false, reason: 'store-estimate-unavailable', requestedBytes: normalizedRequestedBytes, growthBytes: normalizedGrowthBytes, reservedBytes, duplicate, growthEstimate });
  try {
    const estimate = store.estimate();
    if (estimate && typeof estimate.then === 'function') {
      return Object.freeze({ available: true, checked: false, reason: requireSynchronousEstimate ? 'store-estimate-async-skipped' : 'store-estimate-async', requestedBytes: normalizedRequestedBytes, growthBytes: normalizedGrowthBytes, reservedBytes, duplicate, growthEstimate });
    }
    const quota = finiteNumber(estimate?.quota);
    const usage = finiteNumber(estimate?.usage);
    if (quota === null || usage === null) return Object.freeze({ available: true, checked: false, reason: 'store-estimate-incomplete', requestedBytes: normalizedRequestedBytes, growthBytes: normalizedGrowthBytes, reservedBytes, duplicate, growthEstimate, quota, usage });
    const freeBytes = Math.max(0, Math.floor(quota - usage));
    const unreservedFreeBytes = Math.max(0, freeBytes - reservedBytes);
    const projectedUsage = usage + reservedBytes + normalizedGrowthBytes;
    const fits = normalizedGrowthBytes <= unreservedFreeBytes;
    return Object.freeze({
      available: true,
      checked: true,
      reason: fits ? (reservedBytes > 0 ? 'fits-reserved-store-budget' : 'fits-current-store-budget') : (reservedBytes > 0 ? 'exceeds-reserved-store-budget' : 'exceeds-current-store-budget'),
      quota,
      usage,
      freeBytes,
      reservedBytes,
      unreservedFreeBytes,
      requestedBytes: normalizedRequestedBytes,
      growthBytes: normalizedGrowthBytes,
      duplicate,
      growthEstimate,
      projectedUsage,
      projectedFreeBytes: Math.max(0, freeBytes - reservedBytes - normalizedGrowthBytes),
      fits
    });
  } catch (error) {
    return Object.freeze({ available: true, checked: false, reason: 'store-estimate-failed', requestedBytes: normalizedRequestedBytes, growthBytes: normalizedGrowthBytes, reservedBytes, duplicate, growthEstimate, error: captureBudgetError(error) });
  }
}
function summarize(value) {
  if (value instanceof Uint8Array) return Object.freeze({ kind: 'Uint8Array', bytes: value.byteLength });
  if (value instanceof ArrayBuffer) return Object.freeze({ kind: 'ArrayBuffer', bytes: value.byteLength });
  if (value == null || typeof value !== 'object') return Object.freeze({ value });
  const out = {};
  for (const key of ['digest', 'hash', 'bytes', 'duplicate', 'present', 'ok', 'deleted', 'quota', 'usage', 'blockCount', 'provider', 'duplicateHintsCleared']) {
    if (Object.hasOwn(value, key)) out[key] = value[key];
  }
  if (value.ref && typeof value.ref === 'object') out.ref = { id: value.ref.id, digest: value.ref.digest, hash: value.ref.hash, backend: value.ref.backend, bytes: value.ref.bytes };
  return Object.freeze(out);
}
function optionBag(value, label) {
  if (value === undefined || value === null) return {};
  if (typeof value !== 'object' || Array.isArray(value)) throw new Error(`${label} must be an object when supplied`);
  return { ...value };
}
function scheduledProviderOptions(options = {}, op = 'operation') {
  const providerOptions = optionBag(options.providerOptions, 'providerOptions');
  const storeOptions = optionBag(options.storeOptions, 'storeOptions');
  const namedOptions = optionBag(options[`${op}Options`], `${op}Options`);
  return Object.freeze({ ...providerOptions, ...storeOptions, ...namedOptions });
}
function isAbortSignalLike(value) {
  return value && typeof value === 'object' && typeof value.aborted === 'boolean' && typeof value.addEventListener === 'function';
}
function abortSignalFromProviderOptions(providerOptions = {}) {
  const signal = providerOptions?.signal ?? providerOptions?.abortSignal ?? null;
  return isAbortSignalLike(signal) ? signal : null;
}
function abortSummary(signal, fallbackMessage = 'Runtime-core scheduled operation aborted') {
  const reason = signal && 'reason' in signal ? signal.reason : null;
  const name = reason?.name || 'AbortError';
  const message = reason?.message || (reason == null ? fallbackMessage : String(reason));
  const code = reason?.code ?? 'BRT_RUNTIME_CORE_SCHEDULE_ABORTED';
  return Object.freeze({ name, message, code });
}
function withRuntimeCoreScheduledOptions(providerOptions = {}, context = {}) {
  const out = { ...(providerOptions || {}) };
  const contextSignal = context?.signal ?? context?.abortSignal ?? null;
  if (!Object.hasOwn(out, 'signal') && !Object.hasOwn(out, 'abortSignal') && contextSignal) {
    out.signal = contextSignal;
    out.abortSignal = contextSignal;
  }
  out.runtimeCoreLightLane = true;
  return out;
}
async function callStore(providerOptions, context, call) {
  return call(withRuntimeCoreScheduledOptions(providerOptions, context));
}
export class RuntimeCoreBlockStoreLaneAdapter {
  #trace;
  #store;
  #scheduler;
  #results = new Map();
  #errors = new Map();
  #nextOpSeq = 1;
  #queuedAbortListeners = new Map();
  #ownedQueuedTaskIds = new Set();
  #ownedInFlightTaskIds = new Set();
  #putReservations = new Map();
  #reservedPutBytes = 0;
  #lastDispatch = null;
  #blockedDispatches = new Map();
  #closed = false;
  constructor({ label = 'runtime-core-block-store-lane-adapter', store, scheduler, lane = 'storage', trace = null } = {}) {
    assertStore(store, ['put', 'get', 'has', 'verify', 'delete', 'snapshot']);
    assertScheduler(scheduler);
    this.label = label;
    this.lane = lane;
    this.#store = store;
    this.#scheduler = scheduler;
    this.#trace = trace;
    this.stats = { scheduled: 0, rejected: 0, dispatched: 0, completed: 0, failed: 0, cancelled: 0, queuedAbortCancels: 0, externalQueuedCancelsReconciled: 0, preAbortedRejects: 0, quotaPreflightRejects: 0, quotaReservationRejects: 0, emptyDispatches: 0, filteredHeadBlocks: 0, blockedDispatchesTracked: 0, blockedDispatchReobserved: 0, blockedDispatchPruned: 0, closedOperationRejects: 0, closeCalls: 0 };
    this.#emit('runtime-core-block-store-lane:create', { store: this.storeName, provider: this.providerName, lane });
  }
  get store() { return this.#store; }
  get scheduler() { return this.#scheduler; }
  get storeName() { return this.#store.name || this.#store.label || 'unnamed-runtime-core-block-store'; }
  get providerName() { return this.#store.provider || this.#store.name || 'runtime-core-memory-provider'; }
  get closed() { return this.#closed; }
  #emit(kind, payload = {}) { this.#trace?.emit(kind, { label: this.label, lane: this.lane, ...payload }); }
  #opId(kind, id) { return id || `${this.label}:${kind}:${this.#nextOpSeq++}`; }
  #summarizeFilterHeadBlocks(blocks = []) {
    return Object.freeze((Array.isArray(blocks) ? blocks : []).map((block) => Object.freeze({
      taskId: block?.taskId ?? null,
      lane: block?.lane ?? null,
      flowId: block?.flowId ?? null,
      component: block?.component ?? null,
      priority: block?.priority ?? null
    })));
  }
  #rememberDispatch(report) {
    this.#lastDispatch = Object.freeze(report);
    return this.#lastDispatch;
  }
  #recordBlockedDispatches(blocks = []) {
    if (!Array.isArray(blocks) || blocks.length === 0) return Object.freeze([]);
    const rows = [];
    for (const block of blocks) {
      const id = String(block?.taskId ?? 'unknown-blocked-task');
      const previous = this.#blockedDispatches.get(id);
      const row = Object.freeze({ taskId: id, lane: block?.lane ?? null, flowId: block?.flowId ?? null, component: block?.component ?? null, priority: block?.priority ?? null, blockedCount: (previous?.blockedCount || 0) + 1 });
      if (previous) this.stats.blockedDispatchReobserved += 1;
      else this.stats.blockedDispatchesTracked += 1;
      this.#blockedDispatches.set(id, row);
      rows.push(row);
    }
    return Object.freeze(rows);
  }
  #pruneBlockedDispatches(reason = 'snapshot') {
    if (this.#blockedDispatches.size === 0) return 0;
    const { queued, inFlight } = this.#activeSchedulerTaskIds();
    let pruned = 0;
    for (const id of [...this.#blockedDispatches.keys()]) {
      if (queued.has(id) || inFlight.has(id)) continue;
      this.#blockedDispatches.delete(id);
      pruned += 1;
    }
    if (pruned > 0) this.#emit('runtime-core-block-store-lane:blocked-dispatch-prune', { reason, pruned, blockedDispatchCount: this.#blockedDispatches.size });
    this.stats.blockedDispatchPruned += pruned;
    return pruned;
  }
  #blockedDispatchSnapshot() {
    this.#pruneBlockedDispatches('snapshot');
    return Object.freeze([...this.#blockedDispatches.values()].sort((a, b) => String(a.taskId).localeCompare(String(b.taskId))));
  }
  #throwIfClosed(op = 'operation') {
    if (!this.#closed) return;
    this.stats.closedOperationRejects += 1;
    const error = new Error(`RuntimeCoreBlockStoreLaneAdapter ${this.label} is closed`);
    error.name = 'BrowserRTRuntimeCoreLaneAdapterError';
    error.code = 'BRT_RUNTIME_CORE_LANE_ADAPTER_CLOSED';
    error.detail = { label: this.label, lane: this.lane, op, store: this.storeName, provider: this.providerName };
    this.#emit('runtime-core-block-store-lane:closed-reject', error.detail);
    throw error;
  }
  #clearQueuedAbortListener(opId) {
    const entry = this.#queuedAbortListeners.get(String(opId));
    if (!entry) return false;
    entry.signal.removeEventListener('abort', entry.onAbort);
    this.#queuedAbortListeners.delete(String(opId));
    return true;
  }
  #reservePutBytes(opId, bytes) {
    const id = String(opId);
    if (this.#putReservations.has(id)) return this.#putReservations.get(id);
    const n = Math.max(0, Math.floor(Number(bytes) || 0));
    if (n <= 0) return 0;
    this.#putReservations.set(id, n);
    this.#reservedPutBytes += n;
    this.#emit('runtime-core-block-store-lane:put-reserve', { opId: id, bytes: n, reservedPutBytes: this.#reservedPutBytes });
    return n;
  }
  #releasePutReservation(opId) {
    const id = String(opId);
    if (!this.#putReservations.has(id)) return 0;
    const bytes = this.#putReservations.get(id);
    this.#putReservations.delete(id);
    this.#reservedPutBytes = Math.max(0, this.#reservedPutBytes - bytes);
    this.#emit('runtime-core-block-store-lane:put-reservation-release', { opId: id, bytes, reservedPutBytes: this.#reservedPutBytes });
    return bytes;
  }
  #recordAbortError(opId, signal, fallbackMessage) {
    const summary = abortSummary(signal, fallbackMessage);
    this.#errors.set(String(opId), summary);
    return summary;
  }
  #activeSchedulerTaskIds() {
    const snapshot = this.#scheduler.snapshot();
    const queued = new Set();
    const inFlight = new Set();
    for (const lane of snapshot?.lanes || []) {
      for (const id of lane?.queueIds || []) queued.add(String(id));
      for (const id of lane?.inFlightIds || []) inFlight.add(String(id));
    }
    return { queued, inFlight, snapshot };
  }
  #reconcileExternallyCancelledQueued(reason = 'runtime-core-owned-queue-reconcile') {
    if (this.#ownedQueuedTaskIds.size === 0) return Object.freeze({ reconciled: 0, releasedReservationBytes: 0 });
    const { queued, inFlight, snapshot } = this.#activeSchedulerTaskIds();
    let reconciled = 0;
    let releasedReservationBytes = 0;
    for (const opId of [...this.#ownedQueuedTaskIds]) {
      const id = String(opId);
      if (queued.has(id) || inFlight.has(id)) continue;
      this.#clearQueuedAbortListener(id);
      this.#ownedQueuedTaskIds.delete(id);
      const released = this.#releasePutReservation(id);
      releasedReservationBytes += released;
      reconciled += 1;
      this.stats.cancelled += 1;
      this.stats.externalQueuedCancelsReconciled += 1;
      const error = Object.freeze({ name: 'BrowserRTRuntimeCoreLaneAdapterError', message: `Scheduled ${id} left the scheduler queue before adapter dispatch`, code: 'BRT_RUNTIME_CORE_EXTERNAL_QUEUED_CANCELLED' });
      this.#errors.set(id, error);
      this.#emit('runtime-core-block-store-lane:external-queued-cancel-reconcile', { opId: id, reason, error, releasedReservationBytes: released, queuedCount: snapshot.queuedCount, queuedCost: snapshot.queuedCost });
    }
    return Object.freeze({ reconciled, releasedReservationBytes });
  }
  #registerQueuedAbortCancel(opId, op, signal) {
    if (!isAbortSignalLike(signal)) return false;
    const onAbort = () => {
      const cancelled = this.#scheduler.cancelQueued(opId, {
        reason: 'abort-signal-before-dispatch',
        disposition: 'cancelled-aborted-before-dispatch',
        metadata: { component: 'RuntimeCoreBlockStoreLaneAdapter', op, store: this.storeName, provider: this.providerName }
      });
      if (!cancelled.cancelled) return;
      this.#queuedAbortListeners.delete(String(opId));
      this.#ownedQueuedTaskIds.delete(String(opId));
      this.#ownedInFlightTaskIds.delete(String(opId));
      const releasedReservationBytes = this.#releasePutReservation(opId);
      this.stats.cancelled += 1;
      this.stats.queuedAbortCancels += 1;
      const error = this.#recordAbortError(opId, signal, `Scheduled ${op} aborted before dispatch in ${this.label}`);
      this.#emit('runtime-core-block-store-lane:queued-abort-cancel', { opId, op, reason: cancelled.reason, disposition: cancelled.disposition, error, queuedCount: cancelled.queuedCount, queuedCost: cancelled.queuedCost, releasedReservationBytes });
    };
    signal.addEventListener('abort', onAbort, { once: true });
    this.#queuedAbortListeners.set(String(opId), { signal, onAbort });
    if (signal.aborted) onAbort();
    return true;
  }
  schedule(kind, run, { id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], metadata = null, signal = null, reservationBytes = 0 } = {}) {
    this.#throwIfClosed(kind);
    if (!BLOCK_STORE_OP_SET.has(kind)) throw new Error(`Unsupported runtime-core block-store lane op: ${kind}`);
    this.#reconcileExternallyCancelledQueued('pre-schedule');
    const opId = this.#opId(kind, id);
    if (isAbortSignalLike(signal) && signal.aborted) {
      this.stats.rejected += 1;
      this.stats.preAbortedRejects += 1;
      const error = this.#recordAbortError(opId, signal, `Scheduled ${kind} rejected before enqueue in ${this.label}`);
      const rejected = Object.freeze({ accepted: false, disposition: 'rejected-aborted-before-schedule', reason: 'abort-signal-already-aborted', taskId: opId, lane, requestedLane: lane, priority, cost, noMutation: true, error, adapterOp: kind });
      this.#emit('runtime-core-block-store-lane:reject-pre-aborted', { opId, op: kind, reason: rejected.reason, disposition: rejected.disposition, noMutation: true, error });
      return rejected;
    }
    const accepted = this.#scheduler.enqueue({
      id: opId,
      lane,
      fallbackLanes,
      priority,
      cost,
      dependsOn,
      flowId: RUNTIME_CORE_BLOCK_STORE_FLOW_ID,
      metadata: { component: RUNTIME_CORE_BLOCK_STORE_COMPONENT, blockStoreOp: kind, store: this.storeName, provider: this.providerName, ...(metadata || {}) },
      payload: Object.freeze({ kind, run })
    });
    if (!accepted.accepted) {
      this.stats.rejected += 1;
      this.#emit('runtime-core-block-store-lane:reject', { opId, op: kind, reason: accepted.reason, disposition: accepted.disposition, noMutation: accepted.noMutation === true });
      return Object.freeze({ ...accepted, adapterOp: kind });
    }
    this.stats.scheduled += 1;
    const reservedBytes = kind === 'put' ? this.#reservePutBytes(opId, reservationBytes) : 0;
    this.#ownedQueuedTaskIds.add(String(opId));
    this.#registerQueuedAbortCancel(opId, kind, signal);
    this.#emit('runtime-core-block-store-lane:schedule', { opId, op: kind, priority, cost, dependsOn, lane, fallbackLanes, abortableQueued: isAbortSignalLike(signal), reservedBytes, reservedPutBytes: this.#reservedPutBytes });
    return Object.freeze({ ...accepted, adapterOp: kind, reservedBytes, reservedPutBytes: this.#reservedPutBytes });
  }
  schedulePut(payload, { id = null, priority = 'user-visible', cost = null, dependsOn = [], lane = this.lane, fallbackLanes = [], label = null, fields = {}, ...options } = {}) {
    this.#throwIfClosed('put');
    this.#reconcileExternallyCancelledQueued('pre-schedule-put-budget');
    const bytes = payloadBytes(payload);
    const providerOptions = scheduledProviderOptions(options, 'put');
    const signal = abortSignalFromProviderOptions(providerOptions);
    const opId = this.#opId('put', id);
    let growth = null;
    let budget = null;
    if (!(isAbortSignalLike(signal) && signal.aborted)) {
      growth = storePutGrowthEstimate(this.#store, payload, bytes, providerOptions);
      budget = storeBudgetPreflight(this.#store, growth.growthBytes, { pendingBytes: this.#reservedPutBytes, requestedBytes: bytes, growthEstimate: growth });
      if (budget.checked === true && budget.fits === false) {
        this.stats.rejected += 1;
        this.stats.quotaPreflightRejects += 1;
        if (budget.reservedBytes > 0) this.stats.quotaReservationRejects += 1;
        const rejected = Object.freeze({
          accepted: false,
          disposition: 'rejected-store-budget-before-schedule',
          reason: 'store-quota-preflight',
          taskId: opId,
          lane,
          requestedLane: lane,
          priority,
          cost: cost ?? Math.max(1, Math.ceil(bytes / 16)),
          noMutation: true,
          budget,
          adapterOp: 'put'
        });
        this.#emit('runtime-core-block-store-lane:reject-quota-preflight', { opId, op: 'put', reason: rejected.reason, disposition: rejected.disposition, noMutation: true, budget });
        return rejected;
      }
    }
    if (!growth) growth = storePutGrowthEstimate(this.#store, payload, bytes, providerOptions);
    if (!budget) budget = storeBudgetPreflight(this.#store, growth.growthBytes, { pendingBytes: this.#reservedPutBytes, requestedBytes: bytes, growthEstimate: growth });
    const scheduled = this.schedule('put', (context = {}) => callStore(providerOptions, context, (scheduledOptions) => this.#store.put(payload, { label, ...fields, ...scheduledOptions })), { id: opId, priority, cost: cost ?? Math.max(1, Math.ceil(bytes / 16)), dependsOn, lane, fallbackLanes, metadata: { bytes, growthBytes: growth.growthBytes, duplicateBudget: growth.duplicate === true }, signal, reservationBytes: growth.growthBytes });
    return Object.freeze({ ...scheduled, budget, growth });
  }
  scheduleGet(ref, { id = null, priority = 'user-visible', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], ...options } = {}) {
    const providerOptions = scheduledProviderOptions(options, 'get');
    return this.schedule('get', (context = {}) => callStore(providerOptions, context, (scheduledOptions) => this.#store.get(ref, scheduledOptions)), { id, priority, cost, dependsOn, lane, fallbackLanes, metadata: { ref: summarize(ref) }, signal: abortSignalFromProviderOptions(providerOptions) });
  }
  scheduleHas(ref, { id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], ...options } = {}) {
    const providerOptions = scheduledProviderOptions(options, 'has');
    return this.schedule('has', (context = {}) => callStore(providerOptions, context, (scheduledOptions) => this.#store.has(ref, scheduledOptions)), { id, priority, cost, dependsOn, lane, fallbackLanes, metadata: { ref: summarize(ref) }, signal: abortSignalFromProviderOptions(providerOptions) });
  }
  scheduleVerify(ref, { id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], ...options } = {}) {
    const providerOptions = scheduledProviderOptions(options, 'verify');
    return this.schedule('verify', (context = {}) => callStore(providerOptions, context, (scheduledOptions) => this.#store.verify(ref, scheduledOptions)), { id, priority, cost, dependsOn, lane, fallbackLanes, metadata: { ref: summarize(ref) }, signal: abortSignalFromProviderOptions(providerOptions) });
  }
  scheduleDelete(ref, { id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], ...options } = {}) {
    const providerOptions = scheduledProviderOptions(options, 'delete');
    return this.schedule('delete', (context = {}) => callStore(providerOptions, context, (scheduledOptions) => this.#store.delete(ref, scheduledOptions)), { id, priority, cost, dependsOn, lane, fallbackLanes, metadata: { ref: summarize(ref) }, signal: abortSignalFromProviderOptions(providerOptions) });
  }
  scheduleEstimate({ id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], ...options } = {}) {
    const providerOptions = scheduledProviderOptions(options, 'estimate');
    const run = typeof this.#store.estimate === 'function'
      ? (context = {}) => callStore(providerOptions, context, (scheduledOptions) => this.#store.estimate(scheduledOptions))
      : async () => Object.freeze({ quota: null, usage: null, unavailable: true });
    return this.schedule('estimate', run, { id, priority, cost, dependsOn, lane, fallbackLanes, metadata: { telemetry: 'estimate' }, signal: abortSignalFromProviderOptions(providerOptions) });
  }
  scheduleSnapshot({ id = null, priority = 'background', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], ...options } = {}) {
    const providerOptions = scheduledProviderOptions(options, 'snapshot');
    return this.schedule('snapshot', (context = {}) => callStore(providerOptions, context, (scheduledOptions) => this.#store.snapshot(scheduledOptions)), { id, priority, cost, dependsOn, lane, fallbackLanes, metadata: { telemetry: 'snapshot' }, signal: abortSignalFromProviderOptions(providerOptions) });
  }
  scheduleCleanupForTest({ id = null, priority = 'maintenance', cost = 1, dependsOn = [], lane = this.lane, fallbackLanes = [], ...options } = {}) {
    if (typeof this.#store.cleanupForTest !== 'function') throw new Error('runtime-core block-store cleanupForTest is unavailable');
    const providerOptions = scheduledProviderOptions(options, 'cleanup');
    return this.schedule('cleanup', (context = {}) => callStore(providerOptions, context, (scheduledOptions) => this.#store.cleanupForTest(scheduledOptions)), { id, priority, cost, dependsOn, lane, fallbackLanes, metadata: { telemetry: 'cleanupForTest' }, signal: abortSignalFromProviderOptions(providerOptions) });
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
    throw new Error(`Unsupported runtime-core block-store lane submit op: ${op}`);
  }
  result(opId) { return this.#results.get(String(opId)); }
  error(opId) { return this.#errors.get(String(opId)); }
  async dispatchOne(context = {}) {
    if (this.#closed) {
      this.stats.emptyDispatches += 1;
      const lastDispatch = this.#rememberDispatch({ dispatched: false, disposition: 'closed', closed: true, queuedOwnedCount: this.#ownedQueuedTaskIds.size, inFlightOwnedCount: this.#ownedInFlightTaskIds.size });
      this.#emit('runtime-core-block-store-lane:dispatch-closed', { queuedOwnedCount: this.#ownedQueuedTaskIds.size, inFlightOwnedCount: this.#ownedInFlightTaskIds.size });
      return Object.freeze({ dispatched: false, disposition: 'closed', lastDispatch });
    }
    const dispatched = this.#scheduler.dispatchNext({ flowId: RUNTIME_CORE_BLOCK_STORE_FLOW_ID, metadataComponent: RUNTIME_CORE_BLOCK_STORE_COMPONENT, preserveFilteredLaneHead: true });
    if (!dispatched.dispatched) {
      this.stats.emptyDispatches += 1;
      if (dispatched.filterHeadBlocked) this.stats.filteredHeadBlocks += 1;
      const disposition = dispatched.filterHeadBlocked ? 'foreign-head-blocked' : 'empty';
      const filterHeadBlocks = this.#summarizeFilterHeadBlocks(dispatched.filterHeadBlocks || []);
      const blockedDispatches = dispatched.filterHeadBlocked === true ? this.#recordBlockedDispatches(filterHeadBlocks) : Object.freeze([]);
      const lastDispatch = this.#rememberDispatch({ dispatched: false, disposition, filterHeadBlocked: dispatched.filterHeadBlocked === true, filterHeadBlocks, blockedDispatches, queuedCount: dispatched.queuedCount, inFlightCount: dispatched.inFlightCount });
      this.#emit('runtime-core-block-store-lane:dispatch-empty', { queuedCount: dispatched.queuedCount, inFlightCount: dispatched.inFlightCount, disposition, filterHeadBlocked: dispatched.filterHeadBlocked === true, filterHeadBlocks, blockedDispatches });
      return Object.freeze({ dispatched: false, disposition, filterHeadBlocked: dispatched.filterHeadBlocked === true, filterHeadBlocks, blockedDispatches, lastDispatch });
    }
    this.stats.dispatched += 1;
    const { task } = dispatched;
    this.#clearQueuedAbortListener(task?.id);
    this.#ownedQueuedTaskIds.delete(String(task?.id));
    this.#ownedInFlightTaskIds.add(String(task?.id));
    const op = task?.metadata?.blockStoreOp ?? 'operation';
    const run = task?.payload?.run;
    if (typeof run !== 'function') throw new Error(`RuntimeCoreBlockStoreLaneAdapter dispatched task without run(): ${task?.id}`);
    this.#rememberDispatch({ dispatched: true, disposition: 'dispatched', status: 'running', taskId: task.id, op, lane: task.lane });
    this.#emit('runtime-core-block-store-lane:op-start', { opId: task.id, op, store: this.storeName, provider: this.providerName });
    try {
      const value = await run({ ...context, task, lane: task.lane });
      this.#results.set(task.id, value);
      const releasedReservationBytes = this.#releasePutReservation(task.id);
      this.#scheduler.complete(task.id, { outcome: 'complete', metadata: { op, result: summarize(value), releasedReservationBytes } });
      this.#ownedInFlightTaskIds.delete(String(task.id));
      this.stats.completed += 1;
      const lastDispatch = this.#rememberDispatch({ dispatched: true, disposition: 'dispatched', status: 'completed', taskId: task.id, op, lane: task.lane, releasedReservationBytes });
      this.#emit('runtime-core-block-store-lane:op-complete', { opId: task.id, op, result: summarize(value), releasedReservationBytes });
      return Object.freeze({ dispatched: true, status: 'completed', taskId: task.id, op, result: value, releasedReservationBytes, lastDispatch });
    } catch (error) {
      const summary = Object.freeze({ name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null });
      this.#errors.set(task.id, summary);
      const releasedReservationBytes = this.#releasePutReservation(task.id);
      this.#scheduler.complete(task.id, { outcome: 'failed', metadata: { op, error: summary, releasedReservationBytes } });
      this.#ownedInFlightTaskIds.delete(String(task.id));
      this.stats.failed += 1;
      const lastDispatch = this.#rememberDispatch({ dispatched: true, disposition: 'dispatched', status: 'failed', taskId: task.id, op, lane: task.lane, releasedReservationBytes, error: summary });
      this.#emit('runtime-core-block-store-lane:op-failed', { opId: task.id, op, error: summary, releasedReservationBytes });
      return Object.freeze({ dispatched: true, status: 'failed', taskId: task.id, op, error: summary, releasedReservationBytes, lastDispatch });
    }
  }
  async drain({ maxSteps = 32, context = {} } = {}) {
    const steps = [];
    for (let i = 0; i < maxSteps; i += 1) {
      const step = await this.dispatchOne(context);
      steps.push(step);
      if (!step.dispatched) break;
    }
    return Object.freeze({ steps: Object.freeze(steps), completed: this.stats.completed, failed: this.stats.failed, emptyDispatches: this.stats.emptyDispatches });
  }
  close(reason = 'runtime-core-block-store-lane-adapter-close') {
    this.stats.closeCalls += 1;
    this.#reconcileExternallyCancelledQueued('pre-close');
    const wasClosed = this.#closed;
    this.#closed = true;
    let closeCancelledQueued = 0;
    for (const opId of [...this.#ownedQueuedTaskIds]) {
      this.#clearQueuedAbortListener(opId);
      const cancelled = this.#scheduler.cancelQueued(opId, {
        reason: 'adapter-close-before-dispatch',
        disposition: 'cancelled-close-before-dispatch',
        metadata: { component: 'RuntimeCoreBlockStoreLaneAdapter', store: this.storeName, provider: this.providerName }
      });
      this.#ownedQueuedTaskIds.delete(String(opId));
      const releasedReservationBytes = this.#releasePutReservation(opId);
      if (cancelled.cancelled) {
        closeCancelledQueued += 1;
        this.stats.cancelled += 1;
      }
      if (releasedReservationBytes > 0) this.#emit('runtime-core-block-store-lane:close-release-reservation', { opId, releasedReservationBytes, reservedPutBytes: this.#reservedPutBytes });
    }
    for (const opId of [...this.#queuedAbortListeners.keys()]) this.#clearQueuedAbortListener(opId);
    const report = Object.freeze({ disposition: wasClosed ? 'already-closed' : 'closed', label: this.label, lane: this.lane, store: this.storeName, provider: this.providerName, reason, closeCancelledQueued, inFlightOwnedCount: this.#ownedInFlightTaskIds.size });
    this.#emit('runtime-core-block-store-lane:close', report);
    return report;
  }
  snapshot() {
    this.#reconcileExternallyCancelledQueued('snapshot');
    const scheduler = this.#scheduler.snapshot();
    const store = this.#store.snapshot();
    const blockedDispatches = this.#blockedDispatchSnapshot();
    return Object.freeze({
      label: this.label,
      lane: this.lane,
      storeName: this.storeName,
      provider: this.providerName,
      closed: this.#closed,
      light: true,
      runtimeCoreLightLane: true,
      stats: { ...this.stats },
      resultCount: this.#results.size,
      errorCount: this.#errors.size,
      ownedQueuedCount: this.#ownedQueuedTaskIds.size,
      ownedInFlightCount: this.#ownedInFlightTaskIds.size,
      reservedPutCount: this.#putReservations.size,
      reservedPutBytes: this.#reservedPutBytes,
      lastDispatch: this.#lastDispatch,
      blockedDispatches,
      store,
      scheduler
    });
  }
}
export function validateRuntimeCoreBlockStoreLaneAdapterSnapshot(snapshot) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  if (!isObj(snapshot)) return Object.freeze({ ok: false, errors: Object.freeze(['snapshot must be an object']), resultCount: 0 });
  if (typeof snapshot.label !== 'string' || !snapshot.label) errors.push('label must be non-empty string');
  if (typeof snapshot.provider !== 'string' || !snapshot.provider) errors.push('provider must be non-empty string');
  if (!isObj(snapshot.store)) errors.push('store snapshot must be present');
  if (!isObj(snapshot.scheduler)) errors.push('scheduler snapshot must be present');
  if (snapshot.runtimeCoreLightLane !== true) errors.push('runtimeCoreLightLane must be true');
  if (!Number.isInteger(snapshot.resultCount) || snapshot.resultCount < 0) errors.push('resultCount must be non-negative integer');
  if (snapshot.errorCount !== undefined && (!Number.isInteger(snapshot.errorCount) || snapshot.errorCount < 0)) errors.push('errorCount must be non-negative integer');
  if (snapshot.ownedQueuedCount !== undefined && (!Number.isInteger(snapshot.ownedQueuedCount) || snapshot.ownedQueuedCount < 0)) errors.push('ownedQueuedCount must be non-negative integer');
  if (snapshot.ownedInFlightCount !== undefined && (!Number.isInteger(snapshot.ownedInFlightCount) || snapshot.ownedInFlightCount < 0)) errors.push('ownedInFlightCount must be non-negative integer');
  if (snapshot.reservedPutCount !== undefined && (!Number.isInteger(snapshot.reservedPutCount) || snapshot.reservedPutCount < 0)) errors.push('reservedPutCount must be non-negative integer');
  if (snapshot.reservedPutBytes !== undefined && (!Number.isInteger(snapshot.reservedPutBytes) || snapshot.reservedPutBytes < 0)) errors.push('reservedPutBytes must be non-negative integer');
  if (snapshot.lastDispatch !== undefined && snapshot.lastDispatch !== null && !isObj(snapshot.lastDispatch)) errors.push('lastDispatch must be null or object');
  if (isObj(snapshot.lastDispatch) && snapshot.lastDispatch.filterHeadBlocked === true && !Array.isArray(snapshot.lastDispatch.filterHeadBlocks)) errors.push('lastDispatch.filterHeadBlocks must be an array when filterHeadBlocked is true');
  if (snapshot.blockedDispatches !== undefined && !Array.isArray(snapshot.blockedDispatches)) errors.push('blockedDispatches must be an array when present');
  if (Array.isArray(snapshot.blockedDispatches)) {
    for (const block of snapshot.blockedDispatches) {
      if (!isObj(block)) errors.push('blockedDispatches entries must be objects');
      else if (!Number.isInteger(block.blockedCount) || block.blockedCount < 1) errors.push('blockedDispatches.blockedCount must be a positive integer');
    }
  }
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  return Object.freeze({ ok: errors.length === 0, errors: Object.freeze(errors), resultCount: snapshot.resultCount || 0, errorCount: snapshot.errorCount || 0, light: snapshot.runtimeCoreLightLane === true });
}
export function createRuntimeCoreBlockStoreLaneAdapter(config = {}) { return new RuntimeCoreBlockStoreLaneAdapter(config); }
export const RUNTIME_CORE_BLOCK_STORE_LANE_ADAPTER_OPS = BLOCK_STORE_OPS;
