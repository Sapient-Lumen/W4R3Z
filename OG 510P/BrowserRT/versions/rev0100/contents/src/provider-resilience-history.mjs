// BrowserRT rev0033 provider-integrated resilience history scaffold.
// Fake-provider/virtual-tick proof only. No OPFS, browser, durability, performance, SLO, or production resilience claim.

import { createStorageLaneRetryPolicy, StorageLaneRetryPolicy } from './storage-lane-retry.mjs';
import { validateStorageLaneExecutorSnapshot } from './storage-lane-scheduler.mjs';
import { validateRetryBudgetAdmissionSnapshot } from './retry-budget-admission.mjs';
import { validateCircuitBreakerBulkheadSnapshot } from './circuit-breaker-bulkhead.mjs';

function assertProvider(label, value, method) {
  if (!value || typeof value[method] !== 'function') throw new Error(`${label} must provide ${method}()`);
}
function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function errorCodeFromResult(result) {
  return result?.error?.code || result?.error?.name || result?.result?.reason || result?.reason || null;
}
function summarizeDispatch(row) {
  if (!row || typeof row !== 'object') return row;
  return Object.freeze({
    dispatched: Boolean(row.dispatched),
    ok: row.ok === true,
    opId: row.opId ?? null,
    taskId: row.taskId ?? null,
    op: row.op ?? null,
    lane: row.lane ?? null,
    disposition: row.disposition ?? null,
    errorCode: errorCodeFromResult(row),
    resultDisposition: row.result?.disposition ?? null,
    seq: row.result?.seq ?? null,
    bytes: row.result?.bytes ?? null
  });
}

export class ProviderResilienceHistoryRunner {
  #trace;
  #history = [];
  #sequence = 1;

  constructor({
    label = 'provider-resilience-history-runner',
    executor,
    mailbox,
    breaker,
    retryBudget,
    retryPolicy = {},
    trace = null
  } = {}) {
    assertProvider('ProviderResilienceHistoryRunner executor', executor, 'scheduleMailboxEnqueue');
    assertProvider('ProviderResilienceHistoryRunner executor', executor, 'drain');
    assertProvider('ProviderResilienceHistoryRunner executor', executor, 'snapshot');
    assertProvider('ProviderResilienceHistoryRunner mailbox', mailbox, 'snapshot');
    assertProvider('ProviderResilienceHistoryRunner breaker', breaker, 'tryAcquire');
    assertProvider('ProviderResilienceHistoryRunner breaker', breaker, 'release');
    assertProvider('ProviderResilienceHistoryRunner breaker', breaker, 'snapshot');
    assertProvider('ProviderResilienceHistoryRunner retryBudget', retryBudget, 'tryAcquireRetry');
    assertProvider('ProviderResilienceHistoryRunner retryBudget', retryBudget, 'observePrimary');
    assertProvider('ProviderResilienceHistoryRunner retryBudget', retryBudget, 'snapshot');
    this.label = label;
    this.executor = executor;
    this.mailbox = mailbox;
    this.breaker = breaker;
    this.retryBudget = retryBudget;
    this.retryPolicy = retryPolicy instanceof StorageLaneRetryPolicy ? retryPolicy : createStorageLaneRetryPolicy(retryPolicy);
    this.#trace = trace;
    this.stats = {
      operations: 0,
      successes: 0,
      failures: 0,
      attempts: 0,
      retryAttempts: 0,
      retriesAccepted: 0,
      retryBudgetRejected: 0,
      breakerRejected: 0,
      schedulerRejected: 0,
      providerFailures: 0,
      primaryObserved: 0,
      noMutationRejects: 0
    };
    this.#emit('provider-resilience:create', { policy: this.retryPolicy.snapshot() });
  }

  #emit(kind, detail = {}) {
    this.#trace?.emit(kind, { label: this.label, ...detail });
  }

  #record(row) {
    const frozen = Object.freeze(cloneJson(row));
    this.#history.push(frozen);
    return frozen;
  }

  async runMailboxEnqueue(input = {}) {
    const opId = String(input.id || `provider-resilience-op:${this.#sequence++}`);
    const priority = input.priority || 'user-visible';
    const payload = input.payload ?? `payload:${opId}`;
    const maxAttempts = Number.isInteger(input.maxAttempts) ? input.maxAttempts : this.retryPolicy.maxAttempts;
    const idempotent = input.idempotent !== false;
    const durationTicks = Number.isInteger(input.durationTicks) ? input.durationTicks : 1;
    const lane = input.lane || this.executor.lane || 'storage';
    const autoHealOnRetry = input.autoHealOnRetry !== false;
    const fallbackLanes = input.fallbackLanes || [];
    const cost = Number.isInteger(input.cost) ? input.cost : 1;
    const beforeProvider = this.mailbox.snapshot().providerSnapshot;
    const op = { opId, priority, maxAttempts, idempotent, attempts: [], final: null };
    this.stats.operations += 1;
    this.#emit('provider-resilience:operation-start', { opId, priority, maxAttempts, idempotent, lane });

    let pendingRetryLeaseId = null;
    let lastCode = null;
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      if (attempt > 1) {
        this.stats.retryAttempts += 1;
        if (autoHealOnRetry && typeof this.executor.markHealthy === 'function') this.executor.markHealthy(lane, 'provider-resilience-retry-ready');
      }
      const breakerGate = this.breaker.tryAcquire({ opId: `${opId}:attempt:${attempt}`, priority, kind: 'storage-lane-enqueue' });
      if (!breakerGate.accepted) {
        if (pendingRetryLeaseId) {
          this.retryBudget.releaseRetry(pendingRetryLeaseId, { ok: false, opId, attempt });
          pendingRetryLeaseId = null;
        }
        this.stats.breakerRejected += 1;
        this.stats.failures += 1;
        const final = Object.freeze({ ok: false, reason: `breaker:${breakerGate.reason}`, attempts: attempt - 1, opId, noProviderMutation: this.mailbox.snapshot().providerSnapshot.blockCount === beforeProvider.blockCount });
        if (final.noProviderMutation) this.stats.noMutationRejects += 1;
        op.final = final;
        this.#emit('provider-resilience:breaker-reject', { opId, attempt, gate: breakerGate, noProviderMutation: final.noProviderMutation });
        this.#emit('provider-resilience:operation-final', final);
        return this.#record(op);
      }

      const scheduled = this.executor.scheduleMailboxEnqueue(this.mailbox, payload, {
        id: `${opId}:attempt:${attempt}`,
        priority,
        cost,
        lane,
        fallbackLanes,
        enqueue: { label: opId }
      });
      if (!scheduled.accepted) {
        this.breaker.release(breakerGate.leaseId, { ok: false, durationTicks });
        if (pendingRetryLeaseId) this.retryBudget.releaseRetry(pendingRetryLeaseId, { ok: false, opId, attempt });
        this.stats.schedulerRejected += 1;
        this.stats.failures += 1;
        const final = Object.freeze({ ok: false, reason: `scheduler:${scheduled.reason || scheduled.disposition || 'rejected'}`, attempts: attempt - 1, opId });
        op.final = final;
        this.#emit('provider-resilience:scheduler-reject', { opId, attempt, scheduled });
        this.#emit('provider-resilience:operation-final', final);
        return this.#record(op);
      }

      this.stats.attempts += 1;
      const drained = await this.executor.drain({ maxSteps: 1 });
      const dispatch = drained.results.find((row) => row?.dispatched) || drained.results[0] || null;
      const summary = summarizeDispatch(dispatch);
      const ok = summary?.ok === true;
      const code = ok ? null : (summary?.errorCode || 'BRT_STORAGE_UNKNOWN');
      lastCode = code;
      const breakerRelease = this.breaker.release(breakerGate.leaseId, { ok, durationTicks });
      if (pendingRetryLeaseId) {
        this.retryBudget.releaseRetry(pendingRetryLeaseId, { ok, opId, attempt });
        pendingRetryLeaseId = null;
      }
      const attemptRow = Object.freeze({ attempt, scheduled: { accepted: scheduled.accepted, taskId: scheduled.taskId || scheduled.id || `${opId}:attempt:${attempt}`, lane: scheduled.lane }, dispatch: summary, breakerRelease });
      op.attempts.push(cloneJson(attemptRow));
      this.#emit('provider-resilience:attempt', { opId, attempt, ok, code, dispatch: summary, breakerState: this.breaker.snapshot().state });

      if (attempt === 1) {
        this.retryBudget.observePrimary({ ok, opId, attempt, kind: 'mailbox-enqueue', code });
        this.stats.primaryObserved += 1;
      }
      if (ok) {
        this.stats.successes += 1;
        const final = Object.freeze({ ok: true, reason: attempt > 1 ? 'retry-success' : 'primary-success', attempts: attempt, opId });
        op.final = final;
        this.#emit('provider-resilience:operation-final', final);
        return this.#record(op);
      }

      this.stats.providerFailures += 1;
      const policyDecision = this.retryPolicy.shouldRetry({ attempt, code });
      const decision = attempt >= maxAttempts ? { retry: false, reason: 'max-attempts' } : policyDecision;
      if (!decision.retry) {
        this.stats.failures += 1;
        const final = Object.freeze({ ok: false, reason: decision.reason, code, attempts: attempt, opId });
        op.final = final;
        this.#emit('provider-resilience:operation-final', final);
        return this.#record(op);
      }

      const gate = this.retryBudget.tryAcquireRetry({ opId, attempt: attempt + 1, priority, idempotent, code });
      this.#emit('provider-resilience:retry-budget-gate', { opId, attempt: attempt + 1, gate });
      if (!gate.accepted) {
        this.stats.retryBudgetRejected += 1;
        this.stats.failures += 1;
        const final = Object.freeze({ ok: false, reason: `retry-budget:${gate.reason}`, code, attempts: attempt, opId });
        op.final = final;
        this.#emit('provider-resilience:operation-final', final);
        return this.#record(op);
      }
      this.stats.retriesAccepted += 1;
      pendingRetryLeaseId = gate.leaseId;
      const delay = this.retryPolicy.delayTicksForAttempt(attempt, opId);
      if (delay > 0 && typeof this.breaker.advanceTicks === 'function') this.breaker.advanceTicks(delay);
    }

    this.stats.failures += 1;
    const final = Object.freeze({ ok: false, reason: 'max-attempts-loop-exhausted', code: lastCode, attempts: maxAttempts, opId });
    op.final = final;
    this.#emit('provider-resilience:operation-final', final);
    return this.#record(op);
  }

  history() {
    return this.#history.map(cloneJson);
  }

  snapshot() {
    return Object.freeze({
      label: this.label,
      stats: { ...this.stats },
      historyCount: this.#history.length,
      executor: this.executor.snapshot(),
      mailbox: this.mailbox.snapshot(),
      breaker: this.breaker.snapshot(),
      retryBudget: this.retryBudget.snapshot(),
      retryPolicy: this.retryPolicy.snapshot()
    });
  }
}

export function validateProviderResilienceHistorySnapshot(snapshot) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  const nonNeg = (name, value) => { if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`); };
  if (!isObj(snapshot)) return Object.freeze({ ok: false, errors: ['snapshot must be an object'] });
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  else for (const key of ['operations', 'successes', 'failures', 'attempts', 'retryAttempts', 'retriesAccepted', 'retryBudgetRejected', 'breakerRejected', 'schedulerRejected', 'providerFailures', 'primaryObserved', 'noMutationRejects']) nonNeg(`stats.${key}`, snapshot.stats[key]);
  nonNeg('historyCount', snapshot.historyCount);
  const executorValidation = validateStorageLaneExecutorSnapshot(snapshot.executor, { requireMailbox: true });
  if (!executorValidation.ok) errors.push(...executorValidation.errors.map((e) => `executor.${e}`));
  const breakerValidation = validateCircuitBreakerBulkheadSnapshot(snapshot.breaker);
  if (!breakerValidation.ok) errors.push(...breakerValidation.errors.map((e) => `breaker.${e}`));
  const budgetValidation = validateRetryBudgetAdmissionSnapshot(snapshot.retryBudget);
  if (!budgetValidation.ok) errors.push(...budgetValidation.errors.map((e) => `retryBudget.${e}`));
  if (snapshot.stats && snapshot.stats.successes + snapshot.stats.failures !== snapshot.stats.operations) errors.push('successes + failures must equal operations');
  if (snapshot.stats && snapshot.stats.retryBudgetRejected > snapshot.stats.providerFailures) errors.push('retryBudgetRejected cannot exceed providerFailures in this baby proof');
  return Object.freeze({ ok: errors.length === 0, errors, executorValidation, breakerValidation, budgetValidation });
}

export function createProviderResilienceHistoryRunner(config = {}) {
  return new ProviderResilienceHistoryRunner(config);
}
