// BrowserRT rev0031 retry-budget admission scaffold.
// Non-claim: No OPFS retry-budget proof, browser retry-budget proof, or production retry-storm safety claim.
// Fake-provider policy only. No OPFS, browser, wall-clock, SLO, or production retry-storm safety claim.

const PRIORITY_ORDER = Object.freeze(['critical', 'user-blocking', 'user-visible', 'background', 'maintenance']);
const BYPASS_PRIORITIES = new Set(['critical']);

function assertInt(name, value, min = 0) {
  if (!Number.isInteger(value) || value < min) throw new Error(`${name} must be an integer >= ${min}`);
}
function normalizePriority(priority) {
  const p = String(priority || 'background');
  return PRIORITY_ORDER.includes(p) ? p : 'background';
}
function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}
function deterministicId(prefix, n) {
  return `${prefix}:${String(n).padStart(4, '0')}`;
}

export class RetryBudgetAdmissionController {
  #trace;
  #sequence = 1;
  #leases = new Map();

  constructor({
    label = 'retry-budget-admission',
    maxRetryCredits = 4,
    initialRetryCredits = 1,
    refillPerPrimarySuccess = 1,
    refillPerPrimaryFailure = 0,
    maxActiveRetries = 2,
    minRetryCredits = 0,
    allowCriticalBypass = true,
    requireIdempotent = true,
    trace = null
  } = {}) {
    assertInt('maxRetryCredits', maxRetryCredits, 0);
    assertInt('initialRetryCredits', initialRetryCredits, 0);
    assertInt('refillPerPrimarySuccess', refillPerPrimarySuccess, 0);
    assertInt('refillPerPrimaryFailure', refillPerPrimaryFailure, 0);
    assertInt('maxActiveRetries', maxActiveRetries, 0);
    assertInt('minRetryCredits', minRetryCredits, 0);
    if (initialRetryCredits > maxRetryCredits) throw new Error('initialRetryCredits must be <= maxRetryCredits');
    if (minRetryCredits > maxRetryCredits) throw new Error('minRetryCredits must be <= maxRetryCredits');
    this.label = label;
    this.maxRetryCredits = maxRetryCredits;
    this.initialRetryCredits = initialRetryCredits;
    this.refillPerPrimarySuccess = refillPerPrimarySuccess;
    this.refillPerPrimaryFailure = refillPerPrimaryFailure;
    this.maxActiveRetries = maxActiveRetries;
    this.minRetryCredits = minRetryCredits;
    this.allowCriticalBypass = Boolean(allowCriticalBypass);
    this.requireIdempotent = Boolean(requireIdempotent);
    this.retryCredits = initialRetryCredits;
    this.activeRetries = 0;
    this.providerHealthy = true;
    this.stats = {
      primaryObserved: 0,
      primarySuccesses: 0,
      primaryFailures: 0,
      creditsRefilled: 0,
      retryAccepted: 0,
      retryRejected: 0,
      retryReleased: 0,
      criticalBypassAccepted: 0,
      nonIdempotentRejected: 0,
      exhaustedRejected: 0,
      activeLimitRejected: 0,
      providerHealthRejected: 0
    };
    this.#trace = trace;
    this.#emit('retry-budget:create', { snapshot: this.snapshot() });
  }

  #emit(kind, detail = {}) {
    this.#trace?.emit(kind, { label: this.label, ...detail });
  }

  observePrimary(result = {}) {
    const ok = result.ok !== false;
    const delta = ok ? this.refillPerPrimarySuccess : this.refillPerPrimaryFailure;
    const before = this.retryCredits;
    this.retryCredits = Math.min(this.maxRetryCredits, this.retryCredits + delta);
    const gained = this.retryCredits - before;
    this.stats.primaryObserved += 1;
    if (ok) this.stats.primarySuccesses += 1;
    else this.stats.primaryFailures += 1;
    this.stats.creditsRefilled += gained;
    const row = Object.freeze({ observed: true, ok, before, after: this.retryCredits, gained, reason: ok ? 'primary-success' : 'primary-failure' });
    this.#emit('retry-budget:primary-observed', row);
    if (gained > 0) this.#emit('retry-budget:refill', row);
    return row;
  }

  tryAcquireRetry(input = {}) {
    const priority = normalizePriority(input.priority);
    const idempotent = input.idempotent !== false;
    const opId = String(input.opId || input.id || deterministicId('retry-budget-op', this.#sequence));
    const attempt = Number.isInteger(input.attempt) ? input.attempt : Number.isInteger(input.nextAttempt) ? input.nextAttempt : null;
    const code = input.code || null;
    const isBypass = this.allowCriticalBypass && BYPASS_PRIORITIES.has(priority);
    const reject = (reason, extra = {}) => {
      this.stats.retryRejected += 1;
      if (reason === 'non-idempotent') this.stats.nonIdempotentRejected += 1;
      if (reason === 'retry-budget-exhausted') this.stats.exhaustedRejected += 1;
      if (reason === 'active-retry-limit') this.stats.activeLimitRejected += 1;
      if (reason === 'provider-unhealthy') this.stats.providerHealthRejected += 1;
      const row = Object.freeze({ accepted: false, reason, opId, attempt, priority, idempotent, code, retryCredits: this.retryCredits, activeRetries: this.activeRetries, ...extra });
      this.#emit('retry-budget:reject', row);
      return row;
    };

    if (!this.providerHealthy) return reject('provider-unhealthy');
    if (this.requireIdempotent && !idempotent) return reject('non-idempotent');
    if (this.activeRetries >= this.maxActiveRetries) return reject('active-retry-limit');
    if (!isBypass && this.retryCredits <= this.minRetryCredits) return reject('retry-budget-exhausted');

    const leaseId = deterministicId('retry-budget-lease', this.#sequence++);
    const spentCredit = isBypass ? 0 : 1;
    if (spentCredit) this.retryCredits -= spentCredit;
    this.activeRetries += 1;
    this.stats.retryAccepted += 1;
    if (isBypass) this.stats.criticalBypassAccepted += 1;
    const lease = Object.freeze({ leaseId, opId, attempt, priority, idempotent, code, spentCredit, bypass: isBypass, acquiredAtSequence: this.#sequence - 1 });
    this.#leases.set(leaseId, lease);
    const row = Object.freeze({ accepted: true, reason: isBypass ? 'critical-bypass' : 'budget-credit', leaseId, opId, attempt, priority, idempotent, spentCredit, retryCredits: this.retryCredits, activeRetries: this.activeRetries });
    this.#emit('retry-budget:acquire', row);
    return row;
  }

  releaseRetry(leaseOrId, result = {}) {
    const leaseId = typeof leaseOrId === 'string' ? leaseOrId : leaseOrId?.leaseId;
    if (!leaseId || !this.#leases.has(leaseId)) {
      const row = Object.freeze({ released: false, reason: 'unknown-lease', leaseId: leaseId || null });
      this.#emit('retry-budget:release-missing', row);
      return row;
    }
    const lease = this.#leases.get(leaseId);
    this.#leases.delete(leaseId);
    this.activeRetries = Math.max(0, this.activeRetries - 1);
    this.stats.retryReleased += 1;
    const row = Object.freeze({ released: true, leaseId, opId: lease.opId, attempt: lease.attempt, ok: result.ok === true, activeRetries: this.activeRetries, retryCredits: this.retryCredits });
    this.#emit('retry-budget:release', row);
    return row;
  }

  markProviderUnhealthy(reason = 'manual-unhealthy') {
    this.providerHealthy = false;
    this.#emit('retry-budget:provider-unhealthy', { reason, activeRetries: this.activeRetries, retryCredits: this.retryCredits });
  }

  markProviderHealthy(reason = 'manual-healthy') {
    this.providerHealthy = true;
    this.#emit('retry-budget:provider-healthy', { reason, activeRetries: this.activeRetries, retryCredits: this.retryCredits });
  }

  snapshot() {
    return Object.freeze({
      label: this.label,
      maxRetryCredits: this.maxRetryCredits,
      initialRetryCredits: this.initialRetryCredits,
      retryCredits: this.retryCredits,
      minRetryCredits: this.minRetryCredits,
      refillPerPrimarySuccess: this.refillPerPrimarySuccess,
      refillPerPrimaryFailure: this.refillPerPrimaryFailure,
      maxActiveRetries: this.maxActiveRetries,
      activeRetries: this.activeRetries,
      providerHealthy: this.providerHealthy,
      allowCriticalBypass: this.allowCriticalBypass,
      requireIdempotent: this.requireIdempotent,
      leaseCount: this.#leases.size,
      leases: [...this.#leases.values()].map(cloneJson),
      stats: { ...this.stats }
    });
  }
}


export function validateRetryBudgetAdmissionSnapshot(snapshot) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  const nonNeg = (name, value) => {
    if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`);
  };
  if (!isObj(snapshot)) {
    return Object.freeze({ ok: false, errors: ['snapshot must be an object'], retryCredits: 0, activeRetries: 0, leaseCount: 0 });
  }
  for (const key of ['maxRetryCredits', 'initialRetryCredits', 'retryCredits', 'minRetryCredits', 'maxActiveRetries', 'activeRetries', 'leaseCount']) nonNeg(key, snapshot[key]);
  if (snapshot.initialRetryCredits > snapshot.maxRetryCredits) errors.push('initialRetryCredits must be <= maxRetryCredits');
  if (snapshot.minRetryCredits > snapshot.maxRetryCredits) errors.push('minRetryCredits must be <= maxRetryCredits');
  if (snapshot.retryCredits > snapshot.maxRetryCredits) errors.push('retryCredits must be <= maxRetryCredits');
  if (snapshot.retryCredits < snapshot.minRetryCredits) errors.push('retryCredits must not fall below minRetryCredits');
  if (snapshot.activeRetries > snapshot.maxActiveRetries) errors.push('activeRetries must be <= maxActiveRetries');
  if (snapshot.leaseCount !== snapshot.activeRetries) errors.push('leaseCount must equal activeRetries');
  if (!Array.isArray(snapshot.leases)) errors.push('leases must be an array');
  else {
    if (snapshot.leases.length !== snapshot.leaseCount) errors.push('leases.length must equal leaseCount');
    const leaseIds = new Set();
    for (const lease of snapshot.leases) {
      if (!lease || typeof lease !== 'object') errors.push('every lease must be an object');
      else if (!lease.leaseId) errors.push('every lease must have leaseId');
      else if (leaseIds.has(lease.leaseId)) errors.push(`duplicate leaseId ${lease.leaseId}`);
      else leaseIds.add(lease.leaseId);
    }
  }
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  else {
    for (const key of ['primaryObserved', 'primarySuccesses', 'primaryFailures', 'retryAccepted', 'retryRejected', 'retryReleased']) nonNeg(`stats.${key}`, snapshot.stats[key]);
    if ((snapshot.stats.primarySuccesses || 0) + (snapshot.stats.primaryFailures || 0) !== (snapshot.stats.primaryObserved || 0)) errors.push('primary success/failure counts must sum to primaryObserved');
    if ((snapshot.stats.retryReleased || 0) > (snapshot.stats.retryAccepted || 0)) errors.push('retryReleased must be <= retryAccepted');
  }
  if (typeof snapshot.providerHealthy !== 'boolean') errors.push('providerHealthy must be boolean');
  if (typeof snapshot.allowCriticalBypass !== 'boolean') errors.push('allowCriticalBypass must be boolean');
  if (typeof snapshot.requireIdempotent !== 'boolean') errors.push('requireIdempotent must be boolean');
  return Object.freeze({ ok: errors.length === 0, errors, retryCredits: snapshot.retryCredits || 0, activeRetries: snapshot.activeRetries || 0, leaseCount: snapshot.leaseCount || 0 });
}

export function createRetryBudgetAdmissionController(config = {}) {
  return new RetryBudgetAdmissionController(config);
}
