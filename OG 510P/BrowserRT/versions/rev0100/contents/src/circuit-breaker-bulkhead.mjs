// BrowserRT rev0031 circuit-breaker/bulkhead scaffold.
// Fake-provider/virtual-tick proof only. No OPFS, browser, real time, SLO, or production resilience claim.

const DEFAULT_PRIORITIES = Object.freeze(['critical', 'user-blocking', 'user-visible', 'background', 'maintenance']);
const STATES = Object.freeze(['closed', 'open', 'half-open', 'forced-open', 'disabled', 'metrics-only']);

function assertInt(name, value, min = 0) {
  if (!Number.isInteger(value) || value < min) throw new Error(`${name} must be an integer >= ${min}`);
}
function assertPct(name, value) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > 100) throw new Error(`${name} must be a finite percentage from 0 to 100`);
}
function normalizePriority(priority) {
  const p = String(priority || 'background');
  return DEFAULT_PRIORITIES.includes(p) ? p : 'background';
}
function deterministicId(prefix, n) {
  return `${prefix}:${String(n).padStart(4, '0')}`;
}
function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}
function failureRateFrom(total, failed) {
  return total > 0 ? Math.round((failed / total) * 10000) / 100 : 0;
}

export class CircuitBreakerBulkheadController {
  #trace;
  #sequence = 1;
  #leases = new Map();
  #window = [];

  constructor({
    label = 'circuit-breaker-bulkhead',
    maxConcurrent = 2,
    slidingWindowSize = 8,
    minimumCalls = 4,
    failureRateThreshold = 50,
    slowCallRateThreshold = 100,
    slowCallDurationTicks = 1000,
    openDurationTicks = 5,
    halfOpenMaxCalls = 1,
    countSlowCallsAsFailures = false,
    trace = null
  } = {}) {
    assertInt('maxConcurrent', maxConcurrent, 1);
    assertInt('slidingWindowSize', slidingWindowSize, 1);
    assertInt('minimumCalls', minimumCalls, 1);
    assertInt('openDurationTicks', openDurationTicks, 1);
    assertInt('halfOpenMaxCalls', halfOpenMaxCalls, 1);
    assertPct('failureRateThreshold', failureRateThreshold);
    assertPct('slowCallRateThreshold', slowCallRateThreshold);
    assertInt('slowCallDurationTicks', slowCallDurationTicks, 0);
    if (minimumCalls > slidingWindowSize) throw new Error('minimumCalls must be <= slidingWindowSize');
    this.label = label;
    this.maxConcurrent = maxConcurrent;
    this.slidingWindowSize = slidingWindowSize;
    this.minimumCalls = minimumCalls;
    this.failureRateThreshold = failureRateThreshold;
    this.slowCallRateThreshold = slowCallRateThreshold;
    this.slowCallDurationTicks = slowCallDurationTicks;
    this.openDurationTicks = openDurationTicks;
    this.halfOpenMaxCalls = halfOpenMaxCalls;
    this.countSlowCallsAsFailures = Boolean(countSlowCallsAsFailures);
    this.state = 'closed';
    this.nowTick = 0;
    this.openUntilTick = null;
    this.active = 0;
    this.halfOpenInFlight = 0;
    this.halfOpenSuccesses = 0;
    this.stats = {
      accepted: 0,
      rejected: 0,
      bulkheadRejected: 0,
      circuitOpenRejected: 0,
      halfOpenLimitRejected: 0,
      released: 0,
      successes: 0,
      failures: 0,
      slowCalls: 0,
      opened: 0,
      halfOpened: 0,
      closed: 0,
      forcedOpen: 0,
      disabled: 0
    };
    this.#trace = trace;
    this.#emit('resilience:create', { snapshot: this.snapshot() });
  }

  #emit(kind, detail = {}) {
    if (!this.#trace) return;
    const safe = { ...detail };
    if (Object.prototype.hasOwnProperty.call(safe, 'kind')) {
      safe.operationKind = safe.kind;
      delete safe.kind;
    }
    this.#trace.emit(kind, { ...safe, label: this.label, controllerState: this.state, tick: this.nowTick });
  }

  #windowStats() {
    const total = this.#window.length;
    const failed = this.#window.filter((row) => row.failed).length;
    const slow = this.#window.filter((row) => row.slow).length;
    return Object.freeze({ total, failed, slow, failureRate: failureRateFrom(total, failed), slowRate: failureRateFrom(total, slow) });
  }

  #transition(nextState, reason, extra = {}) {
    const previousState = this.state;
    if (!STATES.includes(nextState)) throw new Error(`Unsupported resilience state: ${nextState}`);
    if (previousState === nextState && nextState !== 'open') return Object.freeze({ transitioned: false, state: this.state, reason });
    this.state = nextState;
    if (nextState === 'open') {
      this.openUntilTick = this.nowTick + this.openDurationTicks;
      this.halfOpenInFlight = 0;
      this.halfOpenSuccesses = 0;
      this.stats.opened += 1;
    } else if (nextState === 'half-open') {
      this.halfOpenInFlight = 0;
      this.halfOpenSuccesses = 0;
      this.stats.halfOpened += 1;
    } else if (nextState === 'closed') {
      this.openUntilTick = null;
      this.halfOpenInFlight = 0;
      this.halfOpenSuccesses = 0;
      this.#window = [];
      this.stats.closed += 1;
    } else if (nextState === 'forced-open') {
      this.openUntilTick = null;
      this.stats.forcedOpen += 1;
    } else if (nextState === 'disabled') {
      this.openUntilTick = null;
      this.stats.disabled += 1;
    }
    const row = Object.freeze({ transitioned: true, previousState, state: this.state, reason, openUntilTick: this.openUntilTick, ...extra });
    this.#emit('resilience:state-transition', row);
    return row;
  }

  #maybeHalfOpen() {
    if (this.state === 'open' && this.openUntilTick !== null && this.nowTick >= this.openUntilTick) {
      return this.#transition('half-open', 'open-duration-elapsed');
    }
    return Object.freeze({ transitioned: false, state: this.state });
  }

  #recordClosedOutcome(outcome) {
    this.#window.push(outcome);
    if (this.#window.length > this.slidingWindowSize) this.#window.shift();
    const stats = this.#windowStats();
    this.#emit('resilience:window-record', { outcome, window: stats });
    if (stats.total >= this.minimumCalls && stats.failureRate >= this.failureRateThreshold) {
      return this.#transition('open', 'failure-rate-threshold', { window: stats });
    }
    if (stats.total >= this.minimumCalls && stats.slowRate >= this.slowCallRateThreshold) {
      return this.#transition('open', 'slow-call-rate-threshold', { window: stats });
    }
    return Object.freeze({ transitioned: false, state: this.state, window: stats });
  }

  advanceTicks(ticks = 1) {
    assertInt('ticks', ticks, 0);
    this.nowTick += ticks;
    const transition = this.#maybeHalfOpen();
    const row = Object.freeze({ advanced: true, ticks, nowTick: this.nowTick, transition });
    this.#emit('resilience:tick', row);
    return row;
  }

  forceOpen(reason = 'manual-force-open') {
    return this.#transition('forced-open', reason);
  }

  close(reason = 'manual-close') {
    return this.#transition('closed', reason);
  }

  tryAcquire(input = {}) {
    this.#maybeHalfOpen();
    const opId = String(input.opId || input.id || deterministicId('resilience-op', this.#sequence));
    const priority = normalizePriority(input.priority);
    const kind = String(input.kind || 'operation');
    const reject = (reason, extra = {}) => {
      this.stats.rejected += 1;
      if (reason === 'bulkhead-full') this.stats.bulkheadRejected += 1;
      if (reason === 'circuit-open' || reason === 'forced-open') this.stats.circuitOpenRejected += 1;
      if (reason === 'half-open-limit') this.stats.halfOpenLimitRejected += 1;
      const row = Object.freeze({ accepted: false, reason, opId, priority, kind, active: this.active, halfOpenInFlight: this.halfOpenInFlight, state: this.state, ...extra });
      this.#emit('resilience:reject', row);
      return row;
    };

    if (this.state === 'forced-open') return reject('forced-open');
    if (this.state === 'open') return reject('circuit-open', { openUntilTick: this.openUntilTick });
    if (this.active >= this.maxConcurrent) return reject('bulkhead-full', { maxConcurrent: this.maxConcurrent });
    if (this.state === 'half-open' && this.halfOpenInFlight >= this.halfOpenMaxCalls) return reject('half-open-limit', { halfOpenMaxCalls: this.halfOpenMaxCalls });

    const leaseId = deterministicId('resilience-lease', this.#sequence++);
    const lease = Object.freeze({ leaseId, opId, priority, kind, stateAtAcquire: this.state, acquiredTick: this.nowTick });
    this.#leases.set(leaseId, lease);
    this.active += 1;
    if (this.state === 'half-open') this.halfOpenInFlight += 1;
    this.stats.accepted += 1;
    const row = Object.freeze({ accepted: true, leaseId, opId, priority, kind, state: this.state, active: this.active, halfOpenInFlight: this.halfOpenInFlight });
    this.#emit('resilience:acquire', row);
    return row;
  }

  release(leaseOrId, result = {}) {
    const leaseId = typeof leaseOrId === 'string' ? leaseOrId : leaseOrId?.leaseId;
    if (!leaseId || !this.#leases.has(leaseId)) {
      const row = Object.freeze({ released: false, reason: 'unknown-lease', leaseId: leaseId || null, active: this.active, state: this.state });
      this.#emit('resilience:release-missing', row);
      return row;
    }
    const lease = this.#leases.get(leaseId);
    this.#leases.delete(leaseId);
    this.active = Math.max(0, this.active - 1);
    if (lease.stateAtAcquire === 'half-open') this.halfOpenInFlight = Math.max(0, this.halfOpenInFlight - 1);
    const ok = result.ok !== false;
    const durationTicks = Number.isInteger(result.durationTicks) ? result.durationTicks : 0;
    const slow = durationTicks >= this.slowCallDurationTicks && this.slowCallDurationTicks > 0;
    const failed = !ok || (this.countSlowCallsAsFailures && slow);
    this.stats.released += 1;
    if (ok) this.stats.successes += 1;
    else this.stats.failures += 1;
    if (slow) this.stats.slowCalls += 1;
    const outcome = Object.freeze({ opId: lease.opId, ok, failed, slow, durationTicks, stateAtAcquire: lease.stateAtAcquire });

    let transition = Object.freeze({ transitioned: false, state: this.state });
    if (lease.stateAtAcquire === 'half-open') {
      if (!ok || failed) transition = this.#transition('open', 'half-open-probe-failed', { outcome });
      else {
        this.halfOpenSuccesses += 1;
        this.#emit('resilience:half-open-probe-success', { opId: lease.opId, halfOpenSuccesses: this.halfOpenSuccesses, halfOpenMaxCalls: this.halfOpenMaxCalls });
        if (this.halfOpenSuccesses >= this.halfOpenMaxCalls) transition = this.#transition('closed', 'half-open-probes-succeeded', { outcome });
      }
    } else if (lease.stateAtAcquire === 'closed' || lease.stateAtAcquire === 'metrics-only') {
      transition = this.#recordClosedOutcome(outcome);
    }

    const row = Object.freeze({ released: true, leaseId, opId: lease.opId, ok, failed, slow, durationTicks, active: this.active, state: this.state, transition });
    this.#emit('resilience:release', row);
    return row;
  }

  snapshot() {
    const window = this.#windowStats();
    return Object.freeze({
      label: this.label,
      state: this.state,
      nowTick: this.nowTick,
      openUntilTick: this.openUntilTick,
      maxConcurrent: this.maxConcurrent,
      active: this.active,
      slidingWindowSize: this.slidingWindowSize,
      minimumCalls: this.minimumCalls,
      failureRateThreshold: this.failureRateThreshold,
      slowCallRateThreshold: this.slowCallRateThreshold,
      slowCallDurationTicks: this.slowCallDurationTicks,
      openDurationTicks: this.openDurationTicks,
      halfOpenMaxCalls: this.halfOpenMaxCalls,
      halfOpenInFlight: this.halfOpenInFlight,
      halfOpenSuccesses: this.halfOpenSuccesses,
      leaseCount: this.#leases.size,
      leases: [...this.#leases.values()].map(cloneJson),
      window,
      stats: { ...this.stats }
    });
  }
}

export function validateCircuitBreakerBulkheadSnapshot(snapshot) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  const nonNeg = (name, value) => { if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`); };
  if (!isObj(snapshot)) return Object.freeze({ ok: false, errors: ['snapshot must be an object'], state: null, active: 0, leaseCount: 0 });
  if (!STATES.includes(snapshot.state)) errors.push(`state must be one of ${STATES.join(', ')}`);
  for (const key of ['nowTick', 'maxConcurrent', 'active', 'slidingWindowSize', 'minimumCalls', 'openDurationTicks', 'halfOpenMaxCalls', 'halfOpenInFlight', 'halfOpenSuccesses', 'leaseCount']) nonNeg(key, snapshot[key]);
  if (snapshot.active > snapshot.maxConcurrent) errors.push('active must not exceed maxConcurrent');
  if (snapshot.leaseCount !== snapshot.active) errors.push('leaseCount must equal active');
  if (snapshot.minimumCalls > snapshot.slidingWindowSize) errors.push('minimumCalls must be <= slidingWindowSize');
  if (snapshot.halfOpenInFlight > snapshot.halfOpenMaxCalls) errors.push('halfOpenInFlight must not exceed halfOpenMaxCalls');
  if (!Array.isArray(snapshot.leases)) errors.push('leases must be an array');
  else if (snapshot.leases.length !== snapshot.leaseCount) errors.push('leases.length must equal leaseCount');
  if (!isObj(snapshot.window)) errors.push('window stats must be present');
  else {
    for (const key of ['total', 'failed', 'slow']) nonNeg(`window.${key}`, snapshot.window[key]);
    if (snapshot.window.total > snapshot.slidingWindowSize) errors.push('window.total must not exceed slidingWindowSize');
    if (snapshot.window.failed > snapshot.window.total) errors.push('window.failed must not exceed total');
    if (snapshot.window.slow > snapshot.window.total) errors.push('window.slow must not exceed total');
  }
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  return Object.freeze({ ok: errors.length === 0, errors, state: snapshot.state, active: snapshot.active || 0, leaseCount: snapshot.leaseCount || 0, windowTotal: snapshot.window?.total || 0 });
}

export function createCircuitBreakerBulkheadController(config = {}) {
  return new CircuitBreakerBulkheadController(config);
}
