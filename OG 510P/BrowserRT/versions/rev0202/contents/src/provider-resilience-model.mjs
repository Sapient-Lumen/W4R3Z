const PRIORITY_ORDER = Object.freeze(['critical', 'user-blocking', 'user-visible', 'background', 'maintenance']);
const BYPASS_PRIORITIES = new Set(['critical']);
const DEFAULT_RETRYABLE_CODES = Object.freeze(['BRT_STORAGE_INJECTED_FAULT', 'BRT_STORAGE_QUOTA_TRANSIENT', 'BRT_STORAGE_PROVIDER_REJECTED']);
function assertInt(name, value, min = 0) {
  if (!Number.isInteger(value) || value < min) throw new Error(`${name} must be an integer >= ${min}`);
}
function assertPct(name, value) {
  if (!Number.isFinite(value) || value < 0 || value > 100) throw new Error(`${name} must be between 0 and 100`);
}
function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function normalizePriority(priority) { const p = String(priority || 'background'); return PRIORITY_ORDER.includes(p) ? p : 'background'; }
function deterministicId(prefix, n) { return `${prefix}:${String(n).padStart(4, '0')}`; }
function failureRate(total, failed) { return total > 0 ? (failed / total) * 100 : 0; }
function windowStats(window) {
  const total = window.length;
  const failed = window.filter((row) => row.failed).length;
  const slow = window.filter((row) => row.slow).length;
  return Object.freeze({ total, failed, slow, failureRate: failureRate(total, failed), slowRate: failureRate(total, slow) });
}
function shouldFault(faults, opCounts, op) {
  const count = (opCounts.get(op) || 0) + 1;
  opCounts.set(op, count);
  const index = faults.findIndex((fault) => fault && (fault.op === op || fault.op === '*') && (fault.at === count || fault.at === 'every'));
  if (index < 0) return null;
  const fault = faults[index];
  if (fault.at !== 'every') faults.splice(index, 1);
  return { code: fault.code || 'BRT_STORAGE_INJECTED_FAULT', message: fault.message || `Injected block-store fault for ${op}`, op, count };
}
function comparableFinal(row) {
  return Object.freeze({ ok: row?.final?.ok === true, reason: row?.final?.reason || null, attempts: row?.final?.attempts ?? 0, code: row?.final?.code || null });
}
class ModelProvider {
  constructor({ faults = [], quotaPuts = Number.POSITIVE_INFINITY } = {}) {
    this.faults = Array.isArray(faults) ? faults.map((fault) => ({ ...fault })) : [];
    this.opCounts = new Map();
    this.quotaPuts = quotaPuts;
    this.puts = 0;
    this.blockCount = 0;
    this.faultCount = 0;
  }
  put(payload) {
    const fault = shouldFault(this.faults, this.opCounts, 'put');
    if (fault) { this.faultCount += 1; return { ok: false, code: fault.code, noMutation: true }; }
    if (this.puts >= this.quotaPuts) return { ok: false, code: 'BRT_STORAGE_QUOTA_EXCEEDED', noMutation: true };
    this.puts += 1;
    this.blockCount += 1;
    return { ok: true, bytes: String(payload).length };
  }
  snapshot() { return { puts: this.puts, blockCount: this.blockCount, faultCount: this.faultCount }; }
}
class ModelRetryPolicy {
  constructor({ maxAttempts = 3, initialDelayTicks = 1, multiplier = 2, maxDelayTicks = 16, jitterTicks = 0, retryableCodes = DEFAULT_RETRYABLE_CODES, nonRetryableCodes = [] } = {}) {
    assertInt('maxAttempts', maxAttempts, 1);
    this.maxAttempts = maxAttempts;
    this.initialDelayTicks = initialDelayTicks;
    this.multiplier = multiplier;
    this.maxDelayTicks = maxDelayTicks;
    this.jitterTicks = jitterTicks;
    this.retryableCodes = [...new Set(retryableCodes.map(String))];
    this.nonRetryableCodes = [...new Set(nonRetryableCodes.map(String))];
  }
  shouldRetry({ attempt, code }) {
    const normalized = String(code || '');
    if (this.nonRetryableCodes.includes(normalized)) return { retry: false, reason: 'non-retryable-code' };
    if (attempt >= this.maxAttempts) return { retry: false, reason: 'max-attempts' };
    if (!this.retryableCodes.includes(normalized)) return { retry: false, reason: 'not-in-retryable-codes' };
    return { retry: true, reason: 'retryable-code' };
  }
  delayTicksForAttempt(attempt) {
    return Math.min(this.maxDelayTicks, Math.floor(this.initialDelayTicks * (this.multiplier ** Math.max(0, attempt - 1))));
  }
  snapshot() { return { maxAttempts: this.maxAttempts, retryableCodes: this.retryableCodes.slice(), nonRetryableCodes: this.nonRetryableCodes.slice() }; }
}
class ModelRetryBudget {
  constructor({ maxRetryCredits = 4, initialRetryCredits = 1, refillPerPrimarySuccess = 1, refillPerPrimaryFailure = 0, maxActiveRetries = 2, minRetryCredits = 0, allowCriticalBypass = true, requireIdempotent = true } = {}) {
    this.maxRetryCredits = maxRetryCredits;
    this.retryCredits = initialRetryCredits;
    this.refillPerPrimarySuccess = refillPerPrimarySuccess;
    this.refillPerPrimaryFailure = refillPerPrimaryFailure;
    this.maxActiveRetries = maxActiveRetries;
    this.minRetryCredits = minRetryCredits;
    this.allowCriticalBypass = Boolean(allowCriticalBypass);
    this.requireIdempotent = Boolean(requireIdempotent);
    this.activeRetries = 0;
    this.providerHealthy = true;
    this.sequence = 1;
    this.leases = new Set();
    this.stats = { primaryObserved: 0, retryAccepted: 0, retryRejected: 0, retryReleased: 0, criticalBypassAccepted: 0, exhaustedRejected: 0, nonIdempotentRejected: 0, activeLimitRejected: 0, providerHealthRejected: 0 };
  }
  observePrimary({ ok }) {
    this.stats.primaryObserved += 1;
    const delta = ok ? this.refillPerPrimarySuccess : this.refillPerPrimaryFailure;
    this.retryCredits = Math.min(this.maxRetryCredits, this.retryCredits + delta);
  }
  tryAcquireRetry({ priority = 'background', idempotent = true }) {
    const p = normalizePriority(priority);
    const bypass = this.allowCriticalBypass && BYPASS_PRIORITIES.has(p);
    const reject = (reason) => {
      this.stats.retryRejected += 1;
      if (reason === 'retry-budget-exhausted') this.stats.exhaustedRejected += 1;
      if (reason === 'non-idempotent') this.stats.nonIdempotentRejected += 1;
      if (reason === 'active-retry-limit') this.stats.activeLimitRejected += 1;
      if (reason === 'provider-unhealthy') this.stats.providerHealthRejected += 1;
      return { accepted: false, reason };
    };
    if (!this.providerHealthy) return reject('provider-unhealthy');
    if (this.requireIdempotent && idempotent === false) return reject('non-idempotent');
    if (this.activeRetries >= this.maxActiveRetries) return reject('active-retry-limit');
    if (!bypass && this.retryCredits <= this.minRetryCredits) return reject('retry-budget-exhausted');
    const leaseId = deterministicId('model-retry-lease', this.sequence++);
    if (!bypass) this.retryCredits -= 1;
    this.activeRetries += 1;
    this.leases.add(leaseId);
    this.stats.retryAccepted += 1;
    if (bypass) this.stats.criticalBypassAccepted += 1;
    return { accepted: true, reason: bypass ? 'critical-bypass' : 'budget-credit', leaseId };
  }
  releaseRetry(leaseId) {
    if (!leaseId || !this.leases.has(leaseId)) return { released: false, reason: 'unknown-lease' };
    this.leases.delete(leaseId);
    this.activeRetries = Math.max(0, this.activeRetries - 1);
    this.stats.retryReleased += 1;
    return { released: true };
  }
  snapshot() { return { retryCredits: this.retryCredits, activeRetries: this.activeRetries, leaseCount: this.leases.size, stats: { ...this.stats } }; }
}
class ModelBreaker {
  constructor({ maxConcurrent = 2, slidingWindowSize = 8, minimumCalls = 4, failureRateThreshold = 50, slowCallRateThreshold = 100, slowCallDurationTicks = 1000, openDurationTicks = 5, halfOpenMaxCalls = 1, countSlowCallsAsFailures = false } = {}) {
    assertInt('maxConcurrent', maxConcurrent, 1); assertInt('slidingWindowSize', slidingWindowSize, 1); assertInt('minimumCalls', minimumCalls, 1); assertPct('failureRateThreshold', failureRateThreshold); assertPct('slowCallRateThreshold', slowCallRateThreshold);
    this.maxConcurrent = maxConcurrent; this.slidingWindowSize = slidingWindowSize; this.minimumCalls = minimumCalls; this.failureRateThreshold = failureRateThreshold; this.slowCallRateThreshold = slowCallRateThreshold; this.slowCallDurationTicks = slowCallDurationTicks; this.openDurationTicks = openDurationTicks; this.halfOpenMaxCalls = halfOpenMaxCalls; this.countSlowCallsAsFailures = Boolean(countSlowCallsAsFailures);
    this.state = 'closed'; this.nowTick = 0; this.openUntilTick = null; this.active = 0; this.halfOpenInFlight = 0; this.halfOpenSuccesses = 0; this.sequence = 1; this.leases = new Map(); this.window = [];
    this.stats = { accepted: 0, rejected: 0, opened: 0, closed: 0, halfOpened: 0, bulkheadRejected: 0, circuitOpenRejected: 0, halfOpenLimitRejected: 0 };
  }
  transition(state, reason) {
    if (this.state === state && state !== 'open') return { transitioned: false, state: this.state, reason };
    this.state = state;
    if (state === 'open') { this.openUntilTick = this.nowTick + this.openDurationTicks; this.halfOpenInFlight = 0; this.halfOpenSuccesses = 0; this.stats.opened += 1; }
    if (state === 'half-open') { this.halfOpenInFlight = 0; this.halfOpenSuccesses = 0; this.stats.halfOpened += 1; }
    if (state === 'closed') { this.openUntilTick = null; this.halfOpenInFlight = 0; this.halfOpenSuccesses = 0; this.window = []; this.stats.closed += 1; }
    return { transitioned: true, state: this.state, reason };
  }
  maybeHalfOpen() { if (this.state === 'open' && this.openUntilTick !== null && this.nowTick >= this.openUntilTick) return this.transition('half-open', 'open-duration-elapsed'); return { transitioned: false, state: this.state }; }
  advanceTicks(ticks = 1) { this.nowTick += Math.max(0, ticks); return this.maybeHalfOpen(); }
  tryAcquire({ priority = 'user-visible', kind = 'storage-lane-enqueue' } = {}) {
    this.maybeHalfOpen();
    const reject = (reason) => { this.stats.rejected += 1; if (reason === 'bulkhead-full') this.stats.bulkheadRejected += 1; if (reason === 'circuit-open') this.stats.circuitOpenRejected += 1; if (reason === 'half-open-limit') this.stats.halfOpenLimitRejected += 1; return { accepted: false, reason, state: this.state }; };
    if (this.state === 'open') return reject('circuit-open');
    if (this.active >= this.maxConcurrent) return reject('bulkhead-full');
    if (this.state === 'half-open' && this.halfOpenInFlight >= this.halfOpenMaxCalls) return reject('half-open-limit');
    const leaseId = deterministicId('model-breaker-lease', this.sequence++);
    const lease = { leaseId, priority: normalizePriority(priority), kind, stateAtAcquire: this.state };
    this.leases.set(leaseId, lease); this.active += 1; if (this.state === 'half-open') this.halfOpenInFlight += 1; this.stats.accepted += 1;
    return { accepted: true, leaseId, state: lease.stateAtAcquire };
  }
  release(leaseId, { ok = true, durationTicks = 1 } = {}) {
    const lease = this.leases.get(leaseId);
    if (!lease) return { released: false, reason: 'unknown-lease' };
    this.leases.delete(leaseId); this.active = Math.max(0, this.active - 1); if (lease.stateAtAcquire === 'half-open') this.halfOpenInFlight = Math.max(0, this.halfOpenInFlight - 1);
    const slow = durationTicks >= this.slowCallDurationTicks && this.slowCallDurationTicks > 0;
    const failed = !ok || (this.countSlowCallsAsFailures && slow);
    if (lease.stateAtAcquire === 'half-open') {
      if (failed) this.transition('open', 'half-open-probe-failed');
      else { this.halfOpenSuccesses += 1; if (this.halfOpenSuccesses >= this.halfOpenMaxCalls) this.transition('closed', 'half-open-probes-succeeded'); }
    } else if (lease.stateAtAcquire === 'closed') {
      this.window.push({ failed, slow }); if (this.window.length > this.slidingWindowSize) this.window.shift();
      const stats = windowStats(this.window);
      if (stats.total >= this.minimumCalls && stats.failureRate >= this.failureRateThreshold) this.transition('open', 'failure-rate-threshold');
      else if (stats.total >= this.minimumCalls && stats.slowRate >= this.slowCallRateThreshold) this.transition('open', 'slow-call-rate-threshold');
    }
    return { released: true, state: this.state };
  }
  snapshot() { return { state: this.state, nowTick: this.nowTick, openUntilTick: this.openUntilTick, active: this.active, halfOpenInFlight: this.halfOpenInFlight, leaseCount: this.leases.size, window: windowStats(this.window), stats: { ...this.stats } }; }
}
export class ProviderResilienceModelOracle {
  constructor({ provider = {}, breaker = {}, retryBudget = {}, retryPolicy = {} } = {}) {
    this.provider = new ModelProvider(provider);
    this.breaker = new ModelBreaker(breaker);
    this.retryBudget = new ModelRetryBudget(retryBudget);
    this.retryPolicy = new ModelRetryPolicy(retryPolicy);
    this.history = [];
    this.stats = { operations: 0, successes: 0, failures: 0, attempts: 0, retryBudgetRejected: 0, breakerRejected: 0, providerFailures: 0, retriesAccepted: 0, noMutationRejects: 0 };
  }
  runMailboxEnqueue(input = {}) {
    const opId = String(input.id || `model-op:${this.stats.operations + 1}`);
    const priority = input.priority || 'user-visible';
    const payload = input.payload ?? `payload:${opId}`;
    const maxAttempts = Number.isInteger(input.maxAttempts) ? input.maxAttempts : this.retryPolicy.maxAttempts;
    const idempotent = input.idempotent !== false;
    const durationTicks = Number.isInteger(input.durationTicks) ? input.durationTicks : 1;
    const autoHealOnRetry = input.autoHealOnRetry !== false;
    const beforeBlocks = this.provider.blockCount;
    const row = { opId, priority, maxAttempts, idempotent, attempts: [], final: null };
    this.stats.operations += 1;
    let pendingRetryLeaseId = null;
    let lastCode = null;
    for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
      if (attempt > 1 && autoHealOnRetry) {
      }
      const breakerGate = this.breaker.tryAcquire({ priority, kind: 'storage-lane-enqueue' });
      if (!breakerGate.accepted) {
        if (pendingRetryLeaseId) { this.retryBudget.releaseRetry(pendingRetryLeaseId); pendingRetryLeaseId = null; }
        this.stats.breakerRejected += 1; this.stats.failures += 1;
        const noProviderMutation = this.provider.blockCount === beforeBlocks;
        if (noProviderMutation) this.stats.noMutationRejects += 1;
        row.final = { ok: false, reason: `breaker:${breakerGate.reason}`, attempts: attempt - 1, opId, noProviderMutation };
        this.history.push(cloneJson(row)); return cloneJson(row);
      }
      this.stats.attempts += 1;
      const put = this.provider.put(payload);
      const ok = put.ok === true;
      const code = ok ? null : put.code;
      lastCode = code;
      this.breaker.release(breakerGate.leaseId, { ok, durationTicks });
      if (pendingRetryLeaseId) { this.retryBudget.releaseRetry(pendingRetryLeaseId); pendingRetryLeaseId = null; }
      row.attempts.push({ attempt, ok, code, breakerState: this.breaker.snapshot().state });
      if (attempt === 1) this.retryBudget.observePrimary({ ok, code });
      if (ok) {
        this.stats.successes += 1;
        row.final = { ok: true, reason: attempt > 1 ? 'retry-success' : 'primary-success', attempts: attempt, opId };
        this.history.push(cloneJson(row)); return cloneJson(row);
      }
      this.stats.providerFailures += 1;
      const policyDecision = this.retryPolicy.shouldRetry({ attempt, code });
      const decision = attempt >= maxAttempts ? { retry: false, reason: 'max-attempts' } : policyDecision;
      if (!decision.retry) {
        this.stats.failures += 1;
        row.final = { ok: false, reason: decision.reason, code, attempts: attempt, opId };
        this.history.push(cloneJson(row)); return cloneJson(row);
      }
      const gate = this.retryBudget.tryAcquireRetry({ priority, idempotent, code });
      if (!gate.accepted) {
        this.stats.retryBudgetRejected += 1; this.stats.failures += 1;
        row.final = { ok: false, reason: `retry-budget:${gate.reason}`, code, attempts: attempt, opId };
        this.history.push(cloneJson(row)); return cloneJson(row);
      }
      this.stats.retriesAccepted += 1;
      pendingRetryLeaseId = gate.leaseId;
      this.breaker.advanceTicks(this.retryPolicy.delayTicksForAttempt(attempt));
    }
    this.stats.failures += 1;
    row.final = { ok: false, reason: 'max-attempts-loop-exhausted', code: lastCode, attempts: maxAttempts, opId };
    this.history.push(cloneJson(row)); return cloneJson(row);
  }
  snapshot() {
    return Object.freeze({ stats: { ...this.stats }, historyCount: this.history.length, provider: this.provider.snapshot(), breaker: this.breaker.snapshot(), retryBudget: this.retryBudget.snapshot(), retryPolicy: this.retryPolicy.snapshot() });
  }
}
export function compareProviderResilienceHistoryToModel(realRows, modelRows) {
  const errors = [];
  if (!Array.isArray(realRows) || !Array.isArray(modelRows)) return Object.freeze({ ok: false, errors: ['both histories must be arrays'] });
  if (realRows.length !== modelRows.length) errors.push(`history length mismatch real=${realRows.length} model=${modelRows.length}`);
  const n = Math.min(realRows.length, modelRows.length);
  for (let i = 0; i < n; i += 1) {
    const real = comparableFinal(realRows[i]);
    const model = comparableFinal(modelRows[i]);
    if (JSON.stringify(real) !== JSON.stringify(model)) errors.push(`row ${i} final mismatch real=${JSON.stringify(real)} model=${JSON.stringify(model)}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, compared: n });
}
export function validateProviderResilienceModelSnapshot(snapshot) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  const nonNeg = (name, value) => { if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`); };
  if (!isObj(snapshot)) return Object.freeze({ ok: false, errors: ['snapshot must be an object'] });
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  else {
    for (const key of ['operations', 'successes', 'failures', 'attempts', 'retryBudgetRejected', 'breakerRejected', 'providerFailures', 'retriesAccepted', 'noMutationRejects']) nonNeg(`stats.${key}`, snapshot.stats[key]);
    if (snapshot.stats.successes + snapshot.stats.failures !== snapshot.stats.operations) errors.push('successes + failures must equal operations');
  }
  nonNeg('historyCount', snapshot.historyCount);
  if (snapshot.stats && snapshot.historyCount !== snapshot.stats.operations) errors.push('historyCount must equal operations');
  if (!isObj(snapshot.provider)) errors.push('provider snapshot must be present');
  if (!isObj(snapshot.breaker)) errors.push('breaker snapshot must be present');
  if (!isObj(snapshot.retryBudget)) errors.push('retryBudget snapshot must be present');
  return Object.freeze({ ok: errors.length === 0, errors });
}
export function createProviderResilienceModelOracle(config = {}) {
  return new ProviderResilienceModelOracle(config);
}
