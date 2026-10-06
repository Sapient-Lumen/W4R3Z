const DEFAULT_RETRYABLE_CODES = Object.freeze(['BRT_STORAGE_INJECTED_FAULT', 'BRT_STORAGE_QUOTA_TRANSIENT', 'BRT_STORAGE_PROVIDER_REJECTED']);
function assertInt(name, value, min = 0) {
  if (!Number.isInteger(value) || value < min) throw new Error(`${name} must be an integer >= ${min}`);
}
function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function errorCodeFromResult(result) {
  return result?.error?.code || result?.error?.name || result?.result?.reason || null;
}
function summarizeResult(result) {
  if (!result || typeof result !== 'object') return result;
  return {
    dispatched: Boolean(result.dispatched),
    ok: result.ok === true,
    opId: result.opId ?? null,
    op: result.op ?? null,
    lane: result.lane ?? null,
    disposition: result.disposition ?? null,
    errorCode: errorCodeFromResult(result),
    resultDisposition: result.result?.disposition ?? null,
    resultSeq: result.result?.seq ?? null,
    resultBytes: result.result?.bytes ?? null
  };
}
function deterministicJitter({ seed, attempt, id, span }) {
  if (span <= 0) return 0;
  let h = (Number(seed) >>> 0) || 0x9e3779b9;
  const text = `${id}:${attempt}`;
  for (let i = 0; i < text.length; i += 1) h = Math.imul(h ^ text.charCodeAt(i), 16777619) >>> 0;
  return h % (span + 1);
}
export class StorageLaneRetryPolicy {
  constructor({ maxAttempts = 3, initialDelayTicks = 1, multiplier = 2, maxDelayTicks = 16, jitterTicks = 0, jitterSeed = 0, retryableCodes = DEFAULT_RETRYABLE_CODES, nonRetryableCodes = [] } = {}) {
    assertInt('maxAttempts', maxAttempts, 1);
    assertInt('initialDelayTicks', initialDelayTicks, 0);
    assertInt('maxDelayTicks', maxDelayTicks, 0);
    assertInt('jitterTicks', jitterTicks, 0);
    if (!Number.isFinite(multiplier) || multiplier < 1) throw new Error('multiplier must be finite and >= 1');
    this.maxAttempts = maxAttempts;
    this.initialDelayTicks = initialDelayTicks;
    this.multiplier = multiplier;
    this.maxDelayTicks = maxDelayTicks;
    this.jitterTicks = jitterTicks;
    this.jitterSeed = jitterSeed;
    this.retryableCodes = Object.freeze([...new Set(retryableCodes.map(String))]);
    this.nonRetryableCodes = Object.freeze([...new Set(nonRetryableCodes.map(String))]);
  }
  delayTicksForAttempt(attempt, id = 'operation') {
    assertInt('attempt', attempt, 1);
    const base = Math.min(this.maxDelayTicks, Math.floor(this.initialDelayTicks * (this.multiplier ** Math.max(0, attempt - 1))));
    return base + deterministicJitter({ seed: this.jitterSeed, attempt, id, span: this.jitterTicks });
  }
  shouldRetry({ attempt, code }) {
    const normalized = String(code || '');
    if (this.nonRetryableCodes.includes(normalized)) return Object.freeze({ retry: false, reason: 'non-retryable-code' });
    if (attempt >= this.maxAttempts) return Object.freeze({ retry: false, reason: 'max-attempts' });
    if (!this.retryableCodes.includes(normalized)) return Object.freeze({ retry: false, reason: 'not-in-retryable-codes' });
    return Object.freeze({ retry: true, reason: 'retryable-code' });
  }
  snapshot() {
    return Object.freeze({ maxAttempts: this.maxAttempts, initialDelayTicks: this.initialDelayTicks, multiplier: this.multiplier, maxDelayTicks: this.maxDelayTicks, jitterTicks: this.jitterTicks, jitterSeed: this.jitterSeed, retryableCodes: this.retryableCodes.slice(), nonRetryableCodes: this.nonRetryableCodes.slice() });
  }
}
export class StorageLaneRetryController {
  #trace;
  #ops = new Map();
  #delayed = [];
  #sequence = 1;
  constructor({ label = 'storage-lane-retry-controller', executor, policy = {}, retryBudget = null, trace = null } = {}) {
    if (!executor || typeof executor.scheduleOperation !== 'function' || typeof executor.drain !== 'function') throw new Error('StorageLaneRetryController requires a StorageLaneExecutor-like executor');
    this.label = label;
    this.executor = executor;
    this.policy = policy instanceof StorageLaneRetryPolicy ? policy : new StorageLaneRetryPolicy(policy);
    this.retryBudget = retryBudget;
    this.nowTick = 0;
    this.stats = { submitted: 0, attemptScheduled: 0, schedulerRejected: 0, successes: 0, retryScheduled: 0, retryBudgetAccepted: 0, retryBudgetRejected: 0, retryBudgetReleased: 0, finalFailures: 0, nonRetryableFailures: 0, maxAttemptFailures: 0, retryBudgetFailures: 0, attempts: 0, delayedReady: 0 };
    this.#trace = trace;
    this.#emit('storage-retry:create', { policy: this.policy.snapshot() });
  }
  #emit(kind, payload = {}) {
    const detail = { ...payload };
    if (Object.hasOwn(detail, 'kind')) {
      detail.opKind = detail.kind;
      delete detail.kind;
    }
    this.#trace?.emit(kind, { label: this.label, tick: this.nowTick, ...detail });
  }
  submitMailboxEnqueue(mailbox, payload, options = {}) {
    const id = String(options.id || `storage-retry-op:${this.#sequence++}`);
    if (this.#ops.has(id)) throw new Error(`retry operation already exists: ${id}`);
    const op = {
      id,
      kind: 'mailbox-enqueue',
      attempts: 0,
      state: 'submitted',
      payload,
      mailbox,
      priority: options.priority || 'background',
      cost: options.cost,
      dependsOn: options.dependsOn || [],
      lane: options.lane || this.executor.lane || 'storage',
      fallbackLanes: options.fallbackLanes || [],
      enqueue: options.enqueue || {},
      maxAttempts: options.maxAttempts || this.policy.maxAttempts,
      idempotent: options.idempotent !== false,
      retryBudgetLeaseId: null,
      result: null,
      lastError: null,
      history: []
    };
    this.#ops.set(id, op);
    this.stats.submitted += 1;
    this.#emit('storage-retry:submit', { opId: id, kind: op.kind, maxAttempts: op.maxAttempts, lane: op.lane, priority: op.priority });
    this.#scheduleAttempt(op, 'initial');
    return Object.freeze({ accepted: true, opId: id, state: op.state, attempt: op.attempts });
  }
  #scheduleAttempt(op, reason) {
    op.attempts += 1;
    const attempt = op.attempts;
    const attemptId = `${op.id}:attempt:${attempt}`;
    const scheduled = this.executor.scheduleMailboxEnqueue(op.mailbox, op.payload, {
      id: attemptId,
      priority: op.priority,
      cost: op.cost,
      dependsOn: op.dependsOn,
      lane: op.lane,
      fallbackLanes: op.fallbackLanes,
      enqueue: { ...op.enqueue, label: op.enqueue.label || op.id }
    });
    this.stats.attempts += 1;
    if (!scheduled.accepted) {
      op.state = 'scheduler-rejected';
      op.lastError = { code: scheduled.scheduler?.reason || 'scheduler-rejected', disposition: scheduled.scheduler?.disposition || 'scheduler-rejected' };
      op.history.push({ tick: this.nowTick, event: 'scheduler-rejected', attempt, detail: cloneJson(op.lastError) });
      this.stats.schedulerRejected += 1;
      this.#emit('storage-retry:scheduler-reject', { opId: op.id, attempt, attemptId, reason: op.lastError.code, disposition: op.lastError.disposition });
      return scheduled;
    }
    op.state = 'attempt-scheduled';
    op.history.push({ tick: this.nowTick, event: 'attempt-scheduled', attempt, attemptId, reason });
    this.stats.attemptScheduled += 1;
    this.#emit('storage-retry:attempt-schedule', { opId: op.id, attempt, attemptId, reason, lane: scheduled.lane, priority: op.priority });
    return scheduled;
  }
  #scheduleDelayedRetry(op, code, decision) {
    const delayTicks = Math.max(0, this.policy.delayTicksForAttempt(op.attempts, op.id));
    const readyAt = this.nowTick + delayTicks;
    op.state = 'retry-delayed';
    op.lastError = { code, decision };
    op.history.push({ tick: this.nowTick, event: 'retry-delayed', attempt: op.attempts, code, readyAt, delayTicks });
    this.#delayed.push({ opId: op.id, readyAt });
    this.#delayed.sort((a, b) => a.readyAt - b.readyAt || a.opId.localeCompare(b.opId));
    this.stats.retryScheduled += 1;
    this.#emit('storage-retry:schedule-delay', { opId: op.id, attempt: op.attempts, code, readyAt, delayTicks, reason: decision.reason });
  }
  #markFinalFailure(op, code, decision) {
    op.state = 'failed';
    op.lastError = { code, decision };
    op.history.push({ tick: this.nowTick, event: 'failed', attempt: op.attempts, code, reason: decision.reason });
    this.stats.finalFailures += 1;
    if (decision.reason === 'max-attempts') this.stats.maxAttemptFailures += 1;
    if (decision.reason === 'retry-budget-exhausted' || decision.reason === 'retry-budget-rejected') this.stats.retryBudgetFailures += 1;
    if (decision.reason === 'non-retryable-code' || decision.reason === 'not-in-retryable-codes') this.stats.nonRetryableFailures += 1;
    if (op.attempts === 1) this.retryBudget?.observePrimary?.({ ok: false, opId: op.id, code, reason: decision.reason, kind: op.kind });
    this.#emit('storage-retry:fail-final', { opId: op.id, attempt: op.attempts, code, reason: decision.reason });
  }
  #handleDispatchResult(result) {
    if (!result?.dispatched || !result.opId) return;
    const match = String(result.opId).match(/^(.*):attempt:(\d+)$/);
    if (!match) return;
    const opId = match[1];
    const attempt = Number(match[2]);
    const op = this.#ops.get(opId);
    if (!op) return;
    op.history.push({ tick: this.nowTick, event: 'attempt-result', attempt, ok: result.ok === true, code: errorCodeFromResult(result) });
    this.#emit('storage-retry:attempt-result', { opId, attempt, result: summarizeResult(result) });
    if (attempt > 1 && this.retryBudget && op.retryBudgetLeaseId) {
      const release = this.retryBudget.releaseRetry(op.retryBudgetLeaseId, { ok: result.ok === true, opId, attempt });
      op.history.push({ tick: this.nowTick, event: 'retry-budget-release', attempt, release: cloneJson(release) });
      op.retryBudgetLeaseId = null;
      this.stats.retryBudgetReleased += release.released ? 1 : 0;
      this.#emit('storage-retry:retry-budget-release', { opId, attempt, release });
    }
    if (result.ok) {
      op.state = 'succeeded';
      op.result = result.result;
      this.stats.successes += 1;
      if (attempt === 1) this.retryBudget?.observePrimary?.({ ok: true, opId, attempt, kind: op.kind });
      this.#emit('storage-retry:complete', { opId, attempt, result: summarizeResult(result) });
      return;
    }
    const code = errorCodeFromResult(result) || 'BRT_STORAGE_UNKNOWN';
    const effectivePolicy = op.maxAttempts === this.policy.maxAttempts ? this.policy : new StorageLaneRetryPolicy({ ...this.policy.snapshot(), maxAttempts: op.maxAttempts });
    const decision = effectivePolicy.shouldRetry({ attempt: op.attempts, code });
    if (decision.retry) this.#scheduleDelayedRetry(op, code, decision);
    else this.#markFinalFailure(op, code, decision);
  }
  scheduleDueRetries() {
    const ready = [];
    const waiting = [];
    for (const row of this.#delayed) (row.readyAt <= this.nowTick ? ready : waiting).push(row);
    this.#delayed = waiting;
    for (const row of ready) {
      const op = this.#ops.get(row.opId);
      if (!op || op.state !== 'retry-delayed') continue;
      this.stats.delayedReady += 1;
      this.#emit('storage-retry:ready', { opId: op.id, readyAt: row.readyAt, attempt: op.attempts + 1 });
      if (this.retryBudget) {
        const gate = this.retryBudget.tryAcquireRetry({ opId: op.id, attempt: op.attempts + 1, priority: op.priority, idempotent: op.idempotent, code: op.lastError?.code });
        op.history.push({ tick: this.nowTick, event: 'retry-budget-gate', attempt: op.attempts + 1, gate: cloneJson(gate) });
        this.#emit('storage-retry:retry-budget-gate', { opId: op.id, attempt: op.attempts + 1, gate });
        if (!gate.accepted) {
          this.stats.retryBudgetRejected += 1;
          this.#markFinalFailure(op, op.lastError?.code || gate.reason || 'BRT_RETRY_BUDGET_REJECTED', { retry: false, reason: gate.reason === 'retry-budget-exhausted' ? 'retry-budget-exhausted' : 'retry-budget-rejected', gate: cloneJson(gate) });
          continue;
        }
        this.stats.retryBudgetAccepted += 1;
        op.retryBudgetLeaseId = gate.leaseId;
      }
      this.#scheduleAttempt(op, 'retry-ready');
    }
    return ready.length;
  }
  async drainReady({ maxSteps = 100 } = {}) {
    const results = [];
    let steps = 0;
    this.scheduleDueRetries();
    while (steps < maxSteps) {
      steps += 1;
      const drained = await this.executor.drain({ maxSteps: 1 });
      const row = drained.results[0];
      if (!row || !row.dispatched) { results.push(row || { dispatched: false, disposition: 'empty' }); break; }
      results.push(row);
      this.#handleDispatchResult(row);
      this.scheduleDueRetries();
    }
    return Object.freeze({ tick: this.nowTick, results, snapshot: this.snapshot() });
  }
  advanceToNextRetry() {
    if (!this.#delayed.length) return Object.freeze({ advanced: false, tick: this.nowTick });
    const next = this.#delayed[0].readyAt;
    this.nowTick = Math.max(this.nowTick, next);
    this.#emit('storage-retry:tick-advance', { nextRetryAt: next, delayedCount: this.#delayed.length });
    return Object.freeze({ advanced: true, tick: this.nowTick });
  }
  operation(id) {
    const op = this.#ops.get(String(id));
    if (!op) return null;
    return Object.freeze({ id: op.id, kind: op.kind, attempts: op.attempts, state: op.state, idempotent: op.idempotent, retryBudgetLeaseId: op.retryBudgetLeaseId, lastError: op.lastError ? cloneJson(op.lastError) : null, result: op.result ? cloneJson(op.result) : null, history: op.history.map(cloneJson) });
  }
  snapshot() {
    const ops = [...this.#ops.values()].map((op) => this.operation(op.id));
    return Object.freeze({ label: this.label, tick: this.nowTick, policy: this.policy.snapshot(), retryBudget: this.retryBudget?.snapshot?.() ?? null, stats: { ...this.stats }, delayedCount: this.#delayed.length, delayed: this.#delayed.map(cloneJson), operations: ops, executor: this.executor.snapshot() });
  }
}
export function createStorageLaneRetryPolicy(options = {}) { return new StorageLaneRetryPolicy(options); }
export function createStorageLaneRetryController(options = {}) { return new StorageLaneRetryController(options); }
