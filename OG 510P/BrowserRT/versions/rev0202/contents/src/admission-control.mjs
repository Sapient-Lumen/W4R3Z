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
function normalizePriority(priority) {
  const value = priority ?? 'background';
  if (!PRIORITY_RANK.has(value)) throw new Error(`Unsupported priority: ${value}`);
  return value;
}
function priorityRank(priority) {
  return PRIORITY_RANK.get(normalizePriority(priority));
}
function nowMs() { return Date.now(); }
function normalizeAbortSignal(name, value) {
  if (value === undefined || value === null || value === false) return null;
  const t = typeof value;
  if ((t !== 'object' && t !== 'function') || typeof value.aborted !== 'boolean') {
    throw new Error(`${name} must be an AbortSignal-like object with an aborted boolean`);
  }
  if (value.aborted !== true && typeof value.addEventListener !== 'function') {
    throw new Error(`${name} must expose addEventListener when not already aborted`);
  }
  return value;
}
function uniqueAbortSignals(signal, abortSignal) {
  const signals = [];
  const a = normalizeAbortSignal('signal', signal);
  const b = normalizeAbortSignal('abortSignal', abortSignal);
  for (const candidate of [a, b]) if (candidate && !signals.includes(candidate)) signals.push(candidate);
  return signals;
}
function abortReasonOf(signal) {
  if (!signal) return 'abort-signal';
  if (signal.reason instanceof Error) return signal.reason.name || signal.reason.message || 'AbortError';
  if (signal.reason != null) return String(signal.reason);
  return 'abort-signal';
}
export class WatermarkAdmissionController {
  #leases = new Map();
  #abortCleanups = new Map();
  #nextLease = 1;
  #trace;
  #providerHealthy = true;
  #providerHealthReason = null;
  constructor({
    label = 'watermark-admission-controller',
    lowWatermarkBytes = 0,
    highWatermarkBytes = 1024,
    hardLimitBytes = 2048,
    criticalMinPriority = 'user-blocking',
    rejectMinPriorityWhileCongested = 'user-visible',
    trace = null
  } = {}) {
    assertInteger('lowWatermarkBytes', lowWatermarkBytes);
    assertInteger('highWatermarkBytes', highWatermarkBytes, 1);
    assertInteger('hardLimitBytes', hardLimitBytes, 1);
    if (lowWatermarkBytes > highWatermarkBytes) throw new Error('lowWatermarkBytes must be <= highWatermarkBytes');
    if (highWatermarkBytes > hardLimitBytes) throw new Error('highWatermarkBytes must be <= hardLimitBytes');
    this.label = label;
    this.lowWatermarkBytes = lowWatermarkBytes;
    this.highWatermarkBytes = highWatermarkBytes;
    this.hardLimitBytes = hardLimitBytes;
    this.criticalMinPriority = normalizePriority(criticalMinPriority);
    this.rejectMinPriorityWhileCongested = normalizePriority(rejectMinPriorityWhileCongested);
    this.inFlightBytes = 0;
    this.congested = false;
    this.#trace = trace;
    this.stats = {
      admitted: 0,
      rejected: 0,
      watermarkRejected: 0,
      hardLimitRejected: 0,
      providerHealthRejected: 0,
      abortSignalRejected: 0,
      abortSignalBindings: 0,
      abortSignalReleased: 0,
      released: 0,
      highWatermarkCrossings: 0,
      lowWatermarkRecoveries: 0,
      criticalBypassAdmits: 0,
      noMutationRejects: 0
    };
    this.#trace?.emit('admission:create', {
      label: this.label,
      lowWatermarkBytes: this.lowWatermarkBytes,
      highWatermarkBytes: this.highWatermarkBytes,
      hardLimitBytes: this.hardLimitBytes,
      criticalMinPriority: this.criticalMinPriority,
      rejectMinPriorityWhileCongested: this.rejectMinPriorityWhileCongested
    });
  }
  #emit(kind, payload = {}) { this.#trace?.emit(kind, { label: this.label, ...payload }); }
  #enterCongestion(projectedBytes, reason = 'high-watermark') {
    if (!this.congested) {
      this.congested = true;
      this.stats.highWatermarkCrossings += 1;
      this.#emit('admission:high-watermark', { inFlightBytes: this.inFlightBytes, projectedBytes, highWatermarkBytes: this.highWatermarkBytes, reason });
    }
  }
  #maybeRecover(reason = 'release') {
    if (this.congested && this.inFlightBytes <= this.lowWatermarkBytes) {
      this.congested = false;
      this.stats.lowWatermarkRecoveries += 1;
      this.#emit('admission:low-watermark', { inFlightBytes: this.inFlightBytes, lowWatermarkBytes: this.lowWatermarkBytes, reason });
    }
  }
  tryAdmit({ bytes, priority = 'background', label = null, metadata = null, signal = null, abortSignal = null } = {}) {
    assertInteger('bytes', bytes, 1);
    const p = normalizePriority(priority);
    const abortSignals = uniqueAbortSignals(signal, abortSignal);
    const beforeBytes = this.inFlightBytes;
    const beforeLeaseCount = this.#leases.size;
    const projectedBytes = beforeBytes + bytes;
    const reject = (disposition, reason) => {
      const noMutation = beforeBytes === this.inFlightBytes && beforeLeaseCount === this.#leases.size;
      this.stats.rejected += 1;
      if (disposition === 'rejected-hard-limit') this.stats.hardLimitRejected += 1;
      if (disposition === 'rejected-watermark') this.stats.watermarkRejected += 1;
      if (disposition === 'rejected-provider-health') this.stats.providerHealthRejected += 1;
      if (disposition === 'rejected-aborted') this.stats.abortSignalRejected += 1;
      if (noMutation) this.stats.noMutationRejects += 1;
      this.#emit('admission:reject', { disposition, reason, bytes, priority: p, inFlightBytes: this.inFlightBytes, projectedBytes, hardLimitBytes: this.hardLimitBytes, congested: this.congested, providerHealthy: this.#providerHealthy, noMutation });
      return Object.freeze({ admitted: false, disposition, reason, bytes, priority: p, inFlightBytes: this.inFlightBytes, projectedBytes, noMutation });
    };
    if (abortSignals.some((candidate) => candidate.aborted === true)) return reject('rejected-aborted', `pre-aborted:${abortReasonOf(abortSignals.find((candidate) => candidate.aborted === true))}`);
    if (bytes > this.hardLimitBytes || projectedBytes > this.hardLimitBytes) return reject('rejected-hard-limit', 'hard-limit');
    if (!this.#providerHealthy && priorityRank(p) < priorityRank(this.criticalMinPriority)) return reject('rejected-provider-health', this.#providerHealthReason || 'provider-unhealthy');
    const lowPriority = priorityRank(p) < priorityRank(this.rejectMinPriorityWhileCongested);
    if ((this.congested || projectedBytes > this.highWatermarkBytes) && lowPriority) {
      if (projectedBytes > this.highWatermarkBytes) this.#enterCongestion(projectedBytes, 'projected-high-watermark');
      return reject('rejected-watermark', this.congested ? 'congested-low-priority' : 'projected-high-watermark');
    }
    const bypass = (this.congested || projectedBytes > this.highWatermarkBytes) && priorityRank(p) >= priorityRank(this.criticalMinPriority);
    const leaseId = `admit:${this.#nextLease++}`;
    const lease = Object.freeze({ leaseId, bytes, priority: p, label, metadata, admittedAt: nowMs(), bypass });
    this.#leases.set(leaseId, lease);
    this.inFlightBytes = projectedBytes;
    this.stats.admitted += 1;
    if (this.inFlightBytes >= this.highWatermarkBytes) this.#enterCongestion(this.inFlightBytes);
    if (bypass) this.stats.criticalBypassAdmits += 1;
    if (abortSignals.length > 0) {
      const cleanups = [];
      const releaseFromAbort = (source) => {
        const release = this.release(leaseId, { outcome: 'aborted' });
        if (release.released) {
          this.stats.abortSignalReleased += 1;
          this.#emit('admission:abort-release', { leaseId, bytes, priority: p, label, reason: abortReasonOf(source), inFlightBytes: this.inFlightBytes, leaseCount: this.#leases.size });
        }
      };
      for (const source of abortSignals) {
        const onAbort = () => releaseFromAbort(source);
        if (source.aborted === true) onAbort();
        else {
          source.addEventListener('abort', onAbort, { once: true });
          if (typeof source.removeEventListener === 'function') cleanups.push(() => source.removeEventListener('abort', onAbort));
        }
      }
      if (cleanups.length > 0 && this.#leases.has(leaseId)) {
        this.#abortCleanups.set(leaseId, () => { for (const cleanup of cleanups.splice(0)) cleanup(); });
        this.stats.abortSignalBindings += abortSignals.length;
      }
    }
    this.#emit('admission:admit', { leaseId, bytes, priority: p, label, inFlightBytes: this.inFlightBytes, leaseCount: this.#leases.size, congested: this.congested, bypass, abortSignalBound: this.#abortCleanups.has(leaseId) });
    return Object.freeze({ admitted: true, disposition: bypass ? 'admitted-critical-bypass' : 'admitted', leaseId, bytes, priority: p, label, inFlightBytes: this.inFlightBytes, congested: this.congested, bypass, abortSignalBound: this.#abortCleanups.has(leaseId) });
  }
  release(leaseId, { outcome = 'complete' } = {}) {
    const lease = this.#leases.get(leaseId);
    if (!lease) {
      this.#emit('admission:release-miss', { leaseId });
      return Object.freeze({ released: false, disposition: 'release-miss', leaseId, inFlightBytes: this.inFlightBytes });
    }
    const cleanup = this.#abortCleanups.get(leaseId);
    if (cleanup) { try { cleanup(); } finally { this.#abortCleanups.delete(leaseId); } }
    this.#leases.delete(leaseId);
    this.inFlightBytes -= lease.bytes;
    if (this.inFlightBytes < 0) this.inFlightBytes = 0;
    this.stats.released += 1;
    this.#emit('admission:release', { leaseId, bytes: lease.bytes, priority: lease.priority, outcome, inFlightBytes: this.inFlightBytes, leaseCount: this.#leases.size });
    this.#maybeRecover(outcome);
    return Object.freeze({ released: true, disposition: 'released', leaseId, bytes: lease.bytes, priority: lease.priority, outcome, inFlightBytes: this.inFlightBytes, congested: this.congested });
  }
  markProviderUnhealthy(reason = 'provider-unhealthy') {
    this.#providerHealthy = false;
    this.#providerHealthReason = reason;
    this.#emit('admission:provider-unhealthy', { reason, inFlightBytes: this.inFlightBytes });
  }
  markProviderHealthy(reason = 'provider-healthy') {
    this.#providerHealthy = true;
    this.#providerHealthReason = null;
    this.#emit('admission:provider-healthy', { reason, inFlightBytes: this.inFlightBytes });
  }
  snapshot() {
    return Object.freeze({
      label: this.label,
      lowWatermarkBytes: this.lowWatermarkBytes,
      highWatermarkBytes: this.highWatermarkBytes,
      hardLimitBytes: this.hardLimitBytes,
      inFlightBytes: this.inFlightBytes,
      leaseCount: this.#leases.size,
      boundAbortLeaseCount: this.#abortCleanups.size,
      congested: this.congested,
      providerHealthy: this.#providerHealthy,
      providerHealthReason: this.#providerHealthReason,
      stats: { ...this.stats }
    });
  }
}
export function createWatermarkAdmissionController(config = {}) {
  return new WatermarkAdmissionController(config);
}
