const PRIORITY_RANK = new Map([
  ['maintenance', 0],
  ['background', 1],
  ['user-visible', 2],
  ['user-blocking', 3],
  ['critical', 4]
]);
function assertInteger(name, value, min = 0) {
  if (!Number.isInteger(value) || value < min) throw new Error(`${name} must be an integer >= ${min}`);
}
function assertFinite(name, value, min = 0) {
  if (!Number.isFinite(value) || value < min) throw new Error(`${name} must be a finite number >= ${min}`);
}
function normalizePriority(priority) {
  const value = priority ?? 'background';
  if (!PRIORITY_RANK.has(value)) throw new Error(`Unsupported priority: ${value}`);
  return value;
}
function priorityRank(priority) { return PRIORITY_RANK.get(normalizePriority(priority)); }
function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
function percentile(values, p) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const idx = Math.min(sorted.length - 1, Math.max(0, Math.ceil((p / 100) * sorted.length) - 1));
  return sorted[idx];
}
function ewma(previous, next, alpha) { return !Number.isFinite(previous) || previous <= 0 ? next : previous * (1 - alpha) + next * alpha; }
function nowMs() { return Date.now(); }
export class AdaptiveConcurrencyController {
  #leases = new Map();
  #nextLease = 1;
  #trace;
  #providerHealthy = true;
  #providerHealthReason = null;
  #windowSamples = [];
  #minRttMs = null;
  #smoothedRttMs = null;
  constructor({
    label = 'adaptive-concurrency-controller',
    minLimit = 1,
    maxLimit = 64,
    initialLimit = 4,
    queueTargetMs = 8,
    additiveIncrease = 1,
    multiplicativeDecrease = 0.5,
    smoothing = 0.25,
    probeEveryWindows = 0,
    criticalMinPriority = 'user-blocking',
    rejectMinPriorityWhileLimited = 'user-visible',
    trace = null
  } = {}) {
    assertInteger('minLimit', minLimit, 1);
    assertInteger('maxLimit', maxLimit, minLimit);
    assertInteger('initialLimit', initialLimit, minLimit);
    assertFinite('queueTargetMs', queueTargetMs, 0);
    assertFinite('additiveIncrease', additiveIncrease, 0);
    assertFinite('multiplicativeDecrease', multiplicativeDecrease, 0.01);
    if (multiplicativeDecrease >= 1) throw new Error('multiplicativeDecrease must be < 1');
    assertFinite('smoothing', smoothing, 0);
    if (smoothing > 1) throw new Error('smoothing must be <= 1');
    assertInteger('probeEveryWindows', probeEveryWindows, 0);
    this.label = label;
    this.minLimit = minLimit;
    this.maxLimit = maxLimit;
    this.limit = clamp(initialLimit, minLimit, maxLimit);
    this.queueTargetMs = queueTargetMs;
    this.additiveIncrease = additiveIncrease;
    this.multiplicativeDecrease = multiplicativeDecrease;
    this.smoothing = smoothing;
    this.probeEveryWindows = probeEveryWindows;
    this.criticalMinPriority = normalizePriority(criticalMinPriority);
    this.rejectMinPriorityWhileLimited = normalizePriority(rejectMinPriorityWhileLimited);
    this.inFlight = 0;
    this.windowIndex = 0;
    this.#trace = trace;
    this.stats = {
      admitted: 0, rejected: 0, limitRejected: 0, hardLimitRejected: 0, providerHealthRejected: 0,
      criticalBypassAdmits: 0, completed: 0, failures: 0, timeouts: 0,
      increases: 0, decreases: 0, probes: 0, noMutationRejects: 0
    };
    this.#emit('adaptive:create', { minLimit, maxLimit, initialLimit: this.limit, queueTargetMs, additiveIncrease, multiplicativeDecrease });
  }
  #emit(kind, payload = {}) { this.#trace?.emit(kind, { label: this.label, ...payload }); }
  tryAcquire({ priority = 'background', weight = 1, label = null, metadata = null } = {}) {
    assertInteger('weight', weight, 1);
    const p = normalizePriority(priority);
    const beforeInFlight = this.inFlight;
    const beforeLeaseCount = this.#leases.size;
    const projected = this.inFlight + weight;
    const highPriority = priorityRank(p) >= priorityRank(this.criticalMinPriority);
    const reject = (disposition, reason) => {
      const noMutation = beforeInFlight === this.inFlight && beforeLeaseCount === this.#leases.size;
      this.stats.rejected += 1;
      if (disposition === 'rejected-limit') this.stats.limitRejected += 1;
      if (disposition === 'rejected-hard-limit') this.stats.hardLimitRejected += 1;
      if (disposition === 'rejected-provider-health') this.stats.providerHealthRejected += 1;
      if (noMutation) this.stats.noMutationRejects += 1;
      this.#emit('adaptive:reject', { disposition, reason, priority: p, weight, inFlight: this.inFlight, projected, limit: this.limit, providerHealthy: this.#providerHealthy, noMutation });
      return Object.freeze({ admitted: false, disposition, reason, priority: p, weight, inFlight: this.inFlight, projected, limit: this.limit, noMutation });
    };
    if (!this.#providerHealthy && !highPriority) return reject('rejected-provider-health', this.#providerHealthReason || 'provider-unhealthy');
    if (weight > this.maxLimit || projected > this.maxLimit) return reject('rejected-hard-limit', 'max-limit');
    if (projected > this.limit && priorityRank(p) < priorityRank(this.rejectMinPriorityWhileLimited)) return reject('rejected-limit', 'adaptive-limit');
    const bypass = projected > this.limit && highPriority;
    const leaseId = `adaptive:${this.#nextLease++}`;
    const lease = Object.freeze({ leaseId, priority: p, weight, label, metadata, admittedAt: nowMs(), bypass });
    this.#leases.set(leaseId, lease);
    this.inFlight = projected;
    this.stats.admitted += 1;
    if (bypass) this.stats.criticalBypassAdmits += 1;
    this.#emit('adaptive:admit', { leaseId, priority: p, weight, label, inFlight: this.inFlight, limit: this.limit, bypass });
    return Object.freeze({ admitted: true, disposition: bypass ? 'admitted-critical-bypass' : 'admitted', leaseId, priority: p, weight, label, inFlight: this.inFlight, limit: this.limit, bypass });
  }
  release(leaseId, { latencyMs, outcome = 'complete' } = {}) {
    const lease = this.#leases.get(leaseId);
    if (!lease) {
      this.#emit('adaptive:release-miss', { leaseId });
      return Object.freeze({ released: false, disposition: 'release-miss', leaseId, inFlight: this.inFlight, limit: this.limit });
    }
    if (latencyMs !== undefined) assertFinite('latencyMs', latencyMs, 0);
    this.#leases.delete(leaseId);
    this.inFlight = Math.max(0, this.inFlight - lease.weight);
    const sample = { latencyMs: latencyMs ?? 0, outcome, weight: lease.weight, bypass: lease.bypass, priority: lease.priority };
    this.#windowSamples.push(sample);
    this.stats.completed += 1;
    if (outcome === 'timeout') this.stats.timeouts += 1;
    if (outcome === 'error' || outcome === 'timeout') this.stats.failures += 1;
    this.#emit('adaptive:release', { leaseId, outcome, latencyMs: sample.latencyMs, inFlight: this.inFlight, limit: this.limit });
    return Object.freeze({ released: true, disposition: 'released', leaseId, outcome, latencyMs: sample.latencyMs, inFlight: this.inFlight, limit: this.limit });
  }
  observeWindow({ forceProbe = false } = {}) {
    const samples = this.#windowSamples.splice(0);
    const beforeLimit = this.limit;
    this.windowIndex += 1;
    const latencySamples = samples.filter((s) => Number.isFinite(s.latencyMs) && s.latencyMs > 0).map((s) => s.latencyMs);
    const timeoutCount = samples.filter((s) => s.outcome === 'timeout').length;
    const errorCount = samples.filter((s) => s.outcome === 'error').length;
    const sampleCount = samples.length;
    const p50 = percentile(latencySamples, 50);
    const p90 = percentile(latencySamples, 90);
    if (latencySamples.length) {
      const observedMin = Math.min(...latencySamples);
      this.#minRttMs = this.#minRttMs == null ? observedMin : Math.min(this.#minRttMs, observedMin);
      this.#smoothedRttMs = ewma(this.#smoothedRttMs, p50, this.smoothing);
    }
    const baseline = this.#minRttMs ?? p50 ?? 0;
    const queueDelay = Math.max(0, (this.#smoothedRttMs || p50 || 0) - baseline);
    const shouldProbe = forceProbe || (this.probeEveryWindows > 0 && this.windowIndex % this.probeEveryWindows === 0);
    let decision = 'hold';
    let nextLimit = beforeLimit;
    let reason = 'insufficient-samples';
    if (shouldProbe) {
      this.stats.probes += 1;
      nextLimit = this.minLimit;
      decision = 'probe-min-limit';
      reason = 'scheduled-min-rtt-probe';
      this.#emit('adaptive:probe', { beforeLimit, nextLimit, windowIndex: this.windowIndex });
    } else if (timeoutCount > 0 || errorCount > 0) {
      nextLimit = Math.max(this.minLimit, Math.floor(beforeLimit * this.multiplicativeDecrease));
      decision = 'decrease';
      reason = timeoutCount > 0 ? 'timeout' : 'error';
    } else if (sampleCount > 0 && queueDelay <= this.queueTargetMs) {
      nextLimit = Math.min(this.maxLimit, beforeLimit + this.additiveIncrease);
      decision = nextLimit > beforeLimit ? 'increase' : 'hold';
      reason = 'latency-within-target';
    } else if (sampleCount > 0 && queueDelay > this.queueTargetMs) {
      nextLimit = Math.max(this.minLimit, Math.floor(beforeLimit * this.multiplicativeDecrease));
      decision = nextLimit < beforeLimit ? 'decrease' : 'hold';
      reason = 'queue-delay-above-target';
    }
    this.limit = clamp(Math.trunc(nextLimit), this.minLimit, this.maxLimit);
    if (this.limit > beforeLimit) this.stats.increases += 1;
    if (this.limit < beforeLimit) this.stats.decreases += 1;
    const result = Object.freeze({ windowIndex: this.windowIndex, sampleCount, timeoutCount, errorCount, p50, p90, minRttMs: this.#minRttMs, smoothedRttMs: this.#smoothedRttMs, queueDelayMs: queueDelay, beforeLimit, nextLimit: this.limit, decision, reason });
    this.#emit('adaptive:window', result);
    if (this.limit > beforeLimit) this.#emit('adaptive:limit-increase', result);
    if (this.limit < beforeLimit) this.#emit('adaptive:limit-decrease', result);
    return result;
  }
  markProviderUnhealthy(reason = 'provider-unhealthy') {
    this.#providerHealthy = false;
    this.#providerHealthReason = reason;
    this.#emit('adaptive:provider-unhealthy', { reason, inFlight: this.inFlight, limit: this.limit });
  }
  markProviderHealthy(reason = 'provider-healthy') {
    this.#providerHealthy = true;
    this.#providerHealthReason = null;
    this.#emit('adaptive:provider-healthy', { reason, inFlight: this.inFlight, limit: this.limit });
  }
  snapshot() {
    return Object.freeze({ label: this.label, minLimit: this.minLimit, maxLimit: this.maxLimit, limit: this.limit, inFlight: this.inFlight, leaseCount: this.#leases.size, queueTargetMs: this.queueTargetMs, minRttMs: this.#minRttMs, smoothedRttMs: this.#smoothedRttMs, pendingSamples: this.#windowSamples.length, providerHealthy: this.#providerHealthy, providerHealthReason: this.#providerHealthReason, stats: { ...this.stats } });
  }
}
export function createAdaptiveConcurrencyController(config = {}) { return new AdaptiveConcurrencyController(config); }
