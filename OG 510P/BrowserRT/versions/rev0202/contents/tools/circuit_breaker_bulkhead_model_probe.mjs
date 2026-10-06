#!/usr/bin/env node
// BrowserRT rev0033 circuit-breaker/bulkhead deterministic model proof.
// Fake-provider/model slice only: no OPFS, browser, wall-clock timer, production resilience, or formal verification claim.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, boot, createCircuitBreakerBulkheadController, validateCircuitBreakerBulkheadSnapshot } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-CIRCUIT-BREAKER-BULKHEAD-MODEL-PROBE.json`);

const PRIORITIES = Object.freeze(['critical', 'user-blocking', 'user-visible', 'background', 'maintenance']);
const STATES = Object.freeze(['closed', 'open', 'half-open', 'forced-open', 'disabled', 'metrics-only']);

function lcg(seed) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 0x100000000;
  };
}
function pick(rnd, values) { return values[Math.floor(rnd() * values.length) % values.length]; }
function deterministicId(prefix, n) { return `${prefix}:${String(n).padStart(4, '0')}`; }
function normalizePriority(priority) { const p = String(priority || 'background'); return PRIORITIES.includes(p) ? p : 'background'; }
function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function failureRateFrom(total, failed) { return total > 0 ? Math.round((failed / total) * 10000) / 100 : 0; }
function windowStats(window) {
  const total = window.length;
  const failed = window.filter((row) => row.failed).length;
  const slow = window.filter((row) => row.slow).length;
  return { total, failed, slow, failureRate: failureRateFrom(total, failed), slowRate: failureRateFrom(total, slow) };
}
function comparableSnapshot(snapshot) {
  return {
    state: snapshot.state,
    nowTick: snapshot.nowTick,
    openUntilTick: snapshot.openUntilTick,
    active: snapshot.active,
    halfOpenInFlight: snapshot.halfOpenInFlight,
    halfOpenSuccesses: snapshot.halfOpenSuccesses,
    leaseCount: snapshot.leaseCount,
    leases: snapshot.leases.map((lease) => ({ leaseId: lease.leaseId, opId: lease.opId, priority: lease.priority, kind: lease.kind, stateAtAcquire: lease.stateAtAcquire, acquiredTick: lease.acquiredTick })).sort((a, b) => a.leaseId.localeCompare(b.leaseId)),
    window: cloneJson(snapshot.window),
    stats: cloneJson(snapshot.stats)
  };
}

class CircuitBreakerBulkheadModel {
  constructor(config = {}) {
    this.label = config.label || 'circuit-breaker-bulkhead-model';
    this.maxConcurrent = config.maxConcurrent ?? 2;
    this.slidingWindowSize = config.slidingWindowSize ?? 8;
    this.minimumCalls = config.minimumCalls ?? 4;
    this.failureRateThreshold = config.failureRateThreshold ?? 50;
    this.slowCallRateThreshold = config.slowCallRateThreshold ?? 100;
    this.slowCallDurationTicks = config.slowCallDurationTicks ?? 1000;
    this.openDurationTicks = config.openDurationTicks ?? 5;
    this.halfOpenMaxCalls = config.halfOpenMaxCalls ?? 1;
    this.countSlowCallsAsFailures = Boolean(config.countSlowCallsAsFailures);
    this.state = 'closed';
    this.nowTick = 0;
    this.openUntilTick = null;
    this.active = 0;
    this.halfOpenInFlight = 0;
    this.halfOpenSuccesses = 0;
    this.sequence = 1;
    this.leases = new Map();
    this.window = [];
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
  }
  transition(nextState, reason) {
    if (!STATES.includes(nextState)) throw new Error(`Unsupported state ${nextState}`);
    if (this.state === nextState && nextState !== 'open') return { transitioned: false, state: this.state, reason };
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
      this.window = [];
      this.stats.closed += 1;
    } else if (nextState === 'forced-open') {
      this.openUntilTick = null;
      this.stats.forcedOpen += 1;
    } else if (nextState === 'disabled') {
      this.openUntilTick = null;
      this.stats.disabled += 1;
    }
    return { transitioned: true, state: this.state, reason, openUntilTick: this.openUntilTick };
  }
  maybeHalfOpen() {
    if (this.state === 'open' && this.openUntilTick !== null && this.nowTick >= this.openUntilTick) return this.transition('half-open', 'open-duration-elapsed');
    return { transitioned: false, state: this.state };
  }
  recordClosedOutcome(outcome) {
    this.window.push(outcome);
    if (this.window.length > this.slidingWindowSize) this.window.shift();
    const stats = windowStats(this.window);
    if (stats.total >= this.minimumCalls && stats.failureRate >= this.failureRateThreshold) return this.transition('open', 'failure-rate-threshold');
    if (stats.total >= this.minimumCalls && stats.slowRate >= this.slowCallRateThreshold) return this.transition('open', 'slow-call-rate-threshold');
    return { transitioned: false, state: this.state, window: stats };
  }
  advanceTicks(ticks = 1) {
    this.nowTick += ticks;
    return { advanced: true, ticks, nowTick: this.nowTick, transition: this.maybeHalfOpen() };
  }
  forceOpen(reason = 'manual-force-open') { return this.transition('forced-open', reason); }
  close(reason = 'manual-close') { return this.transition('closed', reason); }
  tryAcquire(input = {}) {
    this.maybeHalfOpen();
    const opId = String(input.opId || input.id || deterministicId('resilience-op', this.sequence));
    const priority = normalizePriority(input.priority);
    const kind = String(input.kind || 'operation');
    const reject = (reason) => {
      this.stats.rejected += 1;
      if (reason === 'bulkhead-full') this.stats.bulkheadRejected += 1;
      if (reason === 'circuit-open' || reason === 'forced-open') this.stats.circuitOpenRejected += 1;
      if (reason === 'half-open-limit') this.stats.halfOpenLimitRejected += 1;
      return { accepted: false, reason, opId, priority, kind, active: this.active, halfOpenInFlight: this.halfOpenInFlight, state: this.state };
    };
    if (this.state === 'forced-open') return reject('forced-open');
    if (this.state === 'open') return reject('circuit-open');
    if (this.active >= this.maxConcurrent) return reject('bulkhead-full');
    if (this.state === 'half-open' && this.halfOpenInFlight >= this.halfOpenMaxCalls) return reject('half-open-limit');
    const leaseId = deterministicId('resilience-lease', this.sequence++);
    const lease = { leaseId, opId, priority, kind, stateAtAcquire: this.state, acquiredTick: this.nowTick };
    this.leases.set(leaseId, lease);
    this.active += 1;
    if (this.state === 'half-open') this.halfOpenInFlight += 1;
    this.stats.accepted += 1;
    return { accepted: true, leaseId, opId, priority, kind, state: this.state, active: this.active, halfOpenInFlight: this.halfOpenInFlight };
  }
  release(leaseOrId, result = {}) {
    const leaseId = typeof leaseOrId === 'string' ? leaseOrId : leaseOrId?.leaseId;
    if (!leaseId || !this.leases.has(leaseId)) return { released: false, reason: 'unknown-lease', leaseId: leaseId || null, active: this.active, state: this.state };
    const lease = this.leases.get(leaseId);
    this.leases.delete(leaseId);
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
    const outcome = { opId: lease.opId, ok, failed, slow, durationTicks, stateAtAcquire: lease.stateAtAcquire };
    let transition = { transitioned: false, state: this.state };
    if (lease.stateAtAcquire === 'half-open') {
      if (!ok || failed) transition = this.transition('open', 'half-open-probe-failed');
      else {
        this.halfOpenSuccesses += 1;
        if (this.halfOpenSuccesses >= this.halfOpenMaxCalls) transition = this.transition('closed', 'half-open-probes-succeeded');
      }
    } else if (lease.stateAtAcquire === 'closed' || lease.stateAtAcquire === 'metrics-only') {
      transition = this.recordClosedOutcome(outcome);
    }
    return { released: true, leaseId, opId: lease.opId, ok, failed, slow, durationTicks, active: this.active, state: this.state, transition };
  }
  snapshot() {
    return {
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
      leaseCount: this.leases.size,
      leases: [...this.leases.values()].map(cloneJson),
      window: windowStats(this.window),
      stats: { ...this.stats }
    };
  }
}

function compare(real, model, context) {
  const validation = validateCircuitBreakerBulkheadSnapshot(real.snapshot());
  assert.equal(validation.ok, true, `${context}: invalid real snapshot: ${validation.errors.join('; ')}`);
  assert.deepEqual(comparableSnapshot(real.snapshot()), comparableSnapshot(model.snapshot()), `${context}: real/model mismatch`);
}
function snapshotAccounting(snapshot) {
  return { active: snapshot.active, leaseCount: snapshot.leaseCount, state: snapshot.state, halfOpenInFlight: snapshot.halfOpenInFlight };
}
function checkNoLeaseGrowth(before, after) {
  return after.active === before.active && after.leaseCount === before.leaseCount && after.halfOpenInFlight === before.halfOpenInFlight;
}

function forceTargetedObservations(obs, trace) {
  const t = { emit(kind, detail) { trace.push({ kind, ...detail }); } };
  // Bulkhead no-mutation.
  {
    const cfg = { label: 'rev0033-target-bulkhead', maxConcurrent: 1, slidingWindowSize: 4, minimumCalls: 2, trace: t };
    const real = createCircuitBreakerBulkheadController(cfg);
    const model = new CircuitBreakerBulkheadModel(cfg);
    compare(real, model, 'target:bulkhead:init');
    const a = real.tryAcquire({ opId: 'target:bulkhead:hold' });
    const ma = model.tryAcquire({ opId: 'target:bulkhead:hold' });
    assert.equal(a.accepted, ma.accepted);
    compare(real, model, 'target:bulkhead:first-acquire');
    const before = snapshotAccounting(real.snapshot());
    const r = real.tryAcquire({ opId: 'target:bulkhead:reject' });
    const m = model.tryAcquire({ opId: 'target:bulkhead:reject' });
    assert.equal(r.reason, m.reason);
    compare(real, model, 'target:bulkhead:reject');
    obs.bulkheadRejectObserved ||= r.reason === 'bulkhead-full';
    obs.rejectionNoLeaseGrowthObserved ||= checkNoLeaseGrowth(before, real.snapshot());
    real.release(a.leaseId, { ok: true, durationTicks: 1 });
    model.release(ma.leaseId, { ok: true, durationTicks: 1 });
    compare(real, model, 'target:bulkhead:release');
  }
  // Failure threshold, open rejection, half-open success close, unknown release.
  {
    const cfg = { label: 'rev0033-target-failure', maxConcurrent: 3, slidingWindowSize: 4, minimumCalls: 3, failureRateThreshold: 50, slowCallRateThreshold: 100, openDurationTicks: 3, halfOpenMaxCalls: 1, trace: t };
    const real = createCircuitBreakerBulkheadController(cfg);
    const model = new CircuitBreakerBulkheadModel(cfg);
    for (const [i, ok] of [false, true, false].entries()) {
      const a = real.tryAcquire({ opId: `target:failure:${i}` });
      const ma = model.tryAcquire({ opId: `target:failure:${i}` });
      real.release(a.leaseId, { ok, durationTicks: 1 });
      model.release(ma.leaseId, { ok, durationTicks: 1 });
      compare(real, model, `target:failure:${i}:release`);
    }
    obs.failureThresholdOpenObserved ||= real.snapshot().state === 'open';
    const before = snapshotAccounting(real.snapshot());
    const r = real.tryAcquire({ opId: 'target:failure:open-reject' });
    const m = model.tryAcquire({ opId: 'target:failure:open-reject' });
    assert.equal(r.reason, m.reason);
    compare(real, model, 'target:failure:open-reject');
    obs.openRejectObserved ||= r.reason === 'circuit-open';
    obs.rejectionNoLeaseGrowthObserved ||= checkNoLeaseGrowth(before, real.snapshot());
    real.advanceTicks(3); model.advanceTicks(3); compare(real, model, 'target:failure:half-open');
    obs.halfOpenTransitionObserved ||= real.snapshot().state === 'half-open';
    const probe = real.tryAcquire({ opId: 'target:failure:probe-success' });
    const mprobe = model.tryAcquire({ opId: 'target:failure:probe-success' });
    real.release(probe.leaseId, { ok: true, durationTicks: 1 });
    model.release(mprobe.leaseId, { ok: true, durationTicks: 1 });
    compare(real, model, 'target:failure:probe-success-close');
    obs.halfOpenSuccessCloseObserved ||= real.snapshot().state === 'closed';
    const miss = real.release('missing-lease', { ok: false });
    const mmiss = model.release('missing-lease', { ok: false });
    assert.equal(miss.reason, mmiss.reason);
    obs.unknownReleaseObserved ||= miss.reason === 'unknown-lease';
  }
  // Half-open failure reopens.
  {
    const cfg = { label: 'rev0033-target-half-open-failure', maxConcurrent: 2, slidingWindowSize: 2, minimumCalls: 2, failureRateThreshold: 50, openDurationTicks: 2, halfOpenMaxCalls: 1, trace: t };
    const real = createCircuitBreakerBulkheadController(cfg);
    const model = new CircuitBreakerBulkheadModel(cfg);
    for (let i = 0; i < 2; i += 1) {
      const a = real.tryAcquire({ opId: `target:half-open-fail:${i}` });
      const ma = model.tryAcquire({ opId: `target:half-open-fail:${i}` });
      real.release(a.leaseId, { ok: false, durationTicks: 1 });
      model.release(ma.leaseId, { ok: false, durationTicks: 1 });
      compare(real, model, `target:half-open-fail:${i}`);
    }
    real.advanceTicks(2); model.advanceTicks(2); compare(real, model, 'target:half-open-fail:half-open');
    const probe = real.tryAcquire({ opId: 'target:half-open-fail:probe' });
    const mprobe = model.tryAcquire({ opId: 'target:half-open-fail:probe' });
    real.release(probe.leaseId, { ok: false, durationTicks: 1 });
    model.release(mprobe.leaseId, { ok: false, durationTicks: 1 });
    compare(real, model, 'target:half-open-fail:reopen');
    obs.halfOpenFailureReopensObserved ||= real.snapshot().state === 'open';
  }
  // Slow threshold.
  {
    const cfg = { label: 'rev0033-target-slow', maxConcurrent: 2, slidingWindowSize: 3, minimumCalls: 2, failureRateThreshold: 100, slowCallRateThreshold: 50, slowCallDurationTicks: 5, openDurationTicks: 3, trace: t };
    const real = createCircuitBreakerBulkheadController(cfg);
    const model = new CircuitBreakerBulkheadModel(cfg);
    for (let i = 0; i < 2; i += 1) {
      const a = real.tryAcquire({ opId: `target:slow:${i}` });
      const ma = model.tryAcquire({ opId: `target:slow:${i}` });
      real.release(a.leaseId, { ok: true, durationTicks: 5 });
      model.release(ma.leaseId, { ok: true, durationTicks: 5 });
      compare(real, model, `target:slow:${i}`);
    }
    obs.slowThresholdOpenObserved ||= real.snapshot().state === 'open';
  }
  // Forced-open rejection then manual close.
  {
    const cfg = { label: 'rev0033-target-force', maxConcurrent: 1, trace: t };
    const real = createCircuitBreakerBulkheadController(cfg);
    const model = new CircuitBreakerBulkheadModel(cfg);
    real.forceOpen('target-force'); model.forceOpen('target-force'); compare(real, model, 'target:force-open');
    const before = snapshotAccounting(real.snapshot());
    const r = real.tryAcquire({ opId: 'target:force:reject' });
    const m = model.tryAcquire({ opId: 'target:force:reject' });
    assert.equal(r.reason, m.reason); compare(real, model, 'target:force-reject');
    obs.forcedOpenRejectObserved ||= r.reason === 'forced-open';
    obs.rejectionNoLeaseGrowthObserved ||= checkNoLeaseGrowth(before, real.snapshot());
    real.close('target-close'); model.close('target-close'); compare(real, model, 'target:force-close');
    obs.manualCloseObserved ||= real.snapshot().state === 'closed';
  }
}

function generatedWalk({ seed, scenarioIndex, steps, trace }) {
  const config = {
    label: `rev0033-circuit-model-${scenarioIndex}`,
    maxConcurrent: 1 + (scenarioIndex % 3),
    slidingWindowSize: 3 + (scenarioIndex % 5),
    minimumCalls: 2 + (scenarioIndex % 2),
    failureRateThreshold: [40, 50, 67, 75][scenarioIndex % 4],
    slowCallRateThreshold: [50, 67, 100][scenarioIndex % 3],
    slowCallDurationTicks: 3 + (scenarioIndex % 4),
    openDurationTicks: 1 + (scenarioIndex % 5),
    halfOpenMaxCalls: 1 + (scenarioIndex % 2),
    countSlowCallsAsFailures: scenarioIndex % 7 === 0,
    trace: { emit(kind, detail) { trace.push({ scenarioIndex, kind, ...detail }); } }
  };
  if (config.minimumCalls > config.slidingWindowSize) config.minimumCalls = config.slidingWindowSize;
  const real = createCircuitBreakerBulkheadController(config);
  const model = new CircuitBreakerBulkheadModel(config);
  const rnd = lcg(seed);
  const obs = {
    acceptedObserved: false,
    rejectionObserved: false,
    openObserved: false,
    halfOpenObserved: false,
    closeObserved: false,
    bulkheadRejectObserved: false,
    circuitRejectObserved: false,
    forcedOpenRejectObserved: false,
    unknownReleaseObserved: false,
    noMutationRejectObserved: false,
    slowObserved: false,
    failureObserved: false
  };
  let agreements = 0;
  for (let step = 0; step < steps; step += 1) {
    const snap = real.snapshot();
    const activeLease = snap.leases.length ? pick(rnd, snap.leases).leaseId : null;
    let choice = Math.floor(rnd() * 12);
    if (snap.leaseCount === 0 && choice <= 3) choice = 4;
    if (choice <= 2) {
      const before = snapshotAccounting(real.snapshot());
      const op = { opId: `scenario:${scenarioIndex}:op:${step}`, priority: pick(rnd, PRIORITIES), kind: pick(rnd, ['storage-write', 'render', 'retry', 'maintenance']) };
      const r = real.tryAcquire(op);
      const m = model.tryAcquire(op);
      assert.equal(r.accepted, m.accepted, `scenario ${scenarioIndex} step ${step} accept mismatch`);
      if (!r.accepted) {
        assert.equal(r.reason, m.reason, `scenario ${scenarioIndex} step ${step} reject reason mismatch`);
        obs.rejectionObserved = true;
        obs.noMutationRejectObserved ||= checkNoLeaseGrowth(before, real.snapshot());
        obs.bulkheadRejectObserved ||= r.reason === 'bulkhead-full';
        obs.circuitRejectObserved ||= r.reason === 'circuit-open';
        obs.forcedOpenRejectObserved ||= r.reason === 'forced-open';
      } else obs.acceptedObserved = true;
    } else if (choice <= 5 && activeLease) {
      const ok = rnd() >= 0.35;
      const durationTicks = Math.floor(rnd() * (config.slowCallDurationTicks + 4));
      const r = real.release(activeLease, { ok, durationTicks });
      const m = model.release(activeLease, { ok, durationTicks });
      assert.equal(r.released, m.released, `scenario ${scenarioIndex} step ${step} release mismatch`);
      obs.slowObserved ||= r.slow;
      obs.failureObserved ||= r.failed;
    } else if (choice <= 7) {
      const ticks = Math.floor(rnd() * 4);
      real.advanceTicks(ticks);
      model.advanceTicks(ticks);
    } else if (choice === 8) {
      const r = real.release(`missing:${scenarioIndex}:${step}`, { ok: false, durationTicks: 0 });
      const m = model.release(`missing:${scenarioIndex}:${step}`, { ok: false, durationTicks: 0 });
      assert.equal(r.reason, m.reason);
      obs.unknownReleaseObserved ||= r.reason === 'unknown-lease';
    } else if (choice === 9 && real.snapshot().leaseCount === 0) {
      real.forceOpen(`scenario-${scenarioIndex}-${step}`);
      model.forceOpen(`scenario-${scenarioIndex}-${step}`);
    } else if (choice === 10 && real.snapshot().leaseCount === 0) {
      real.close(`scenario-${scenarioIndex}-${step}`);
      model.close(`scenario-${scenarioIndex}-${step}`);
      obs.closeObserved = true;
    } else {
      const op = { opId: `scenario:${scenarioIndex}:fallback:${step}`, priority: 'background', kind: 'fallback-acquire' };
      const r = real.tryAcquire(op);
      const m = model.tryAcquire(op);
      assert.equal(r.accepted, m.accepted);
    }
    const state = real.snapshot().state;
    obs.openObserved ||= state === 'open';
    obs.halfOpenObserved ||= state === 'half-open';
    obs.closeObserved ||= state === 'closed';
    compare(real, model, `scenario:${scenarioIndex}:step:${step}`);
    agreements += 1;
  }
  // Drain any leases to keep final accounting easy to audit.
  for (const lease of [...real.snapshot().leases]) {
    real.release(lease.leaseId, { ok: true, durationTicks: 1 });
    model.release(lease.leaseId, { ok: true, durationTicks: 1 });
    compare(real, model, `scenario:${scenarioIndex}:drain:${lease.leaseId}`);
    agreements += 1;
  }
  return { scenarioIndex, seed, steps, agreements, observations: obs, finalSnapshot: real.snapshot() };
}

const trace = [];
const targeted = {
  bulkheadRejectObserved: false,
  rejectionNoLeaseGrowthObserved: false,
  failureThresholdOpenObserved: false,
  openRejectObserved: false,
  halfOpenTransitionObserved: false,
  halfOpenSuccessCloseObserved: false,
  halfOpenFailureReopensObserved: false,
  slowThresholdOpenObserved: false,
  forcedOpenRejectObserved: false,
  manualCloseObserved: false,
  unknownReleaseObserved: false
};
forceTargetedObservations(targeted, trace);

const scenarioCount = 28;
const stepsPerScenario = 120;
const scenarios = [];
let agreements = 0;
for (let i = 0; i < scenarioCount; i += 1) {
  const scenario = generatedWalk({ seed: 0xB0A500 + i * 7919, scenarioIndex: i, steps: stepsPerScenario, trace });
  scenarios.push(scenario);
  agreements += scenario.agreements;
}
const replayA = generatedWalk({ seed: 0xC1A0BEEF, scenarioIndex: 997, steps: 80, trace: [] });
const replayB = generatedWalk({ seed: 0xC1A0BEEF, scenarioIndex: 997, steps: 80, trace: [] });
const bootReport = await boot({ circuitBreakerBulkheadModelProof: true });

const traceKinds = [...new Set(trace.map((event) => event.kind))].sort();
const requiredTraceKinds = ['resilience:create', 'resilience:acquire', 'resilience:reject', 'resilience:release', 'resilience:state-transition', 'resilience:window-record', 'resilience:tick'];
const combinedScenarioObs = scenarios.reduce((acc, scenario) => {
  for (const [key, value] of Object.entries(scenario.observations)) acc[key] ||= Boolean(value);
  return acc;
}, {});
const finalSnapshotsValidated = scenarios.every((scenario) => validateCircuitBreakerBulkheadSnapshot(scenario.finalSnapshot).ok);
const finalAccountingEmpty = scenarios.every((scenario) => scenario.finalSnapshot.active === 0 && scenario.finalSnapshot.leaseCount === 0);
const observations = {
  targetedObservationsHold: Object.values(targeted).every(Boolean),
  deterministicReplayMatches: JSON.stringify(comparableSnapshot(replayA.finalSnapshot)) === JSON.stringify(comparableSnapshot(replayB.finalSnapshot)) && replayA.agreements === replayB.agreements,
  realModelAgreementEveryStep: true,
  finalSnapshotsValidated,
  finalAccountingEmpty,
  generatedOpenObserved: Boolean(combinedScenarioObs.openObserved),
  generatedHalfOpenObserved: Boolean(combinedScenarioObs.halfOpenObserved),
  generatedBulkheadRejectObserved: Boolean(combinedScenarioObs.bulkheadRejectObserved || targeted.bulkheadRejectObserved),
  generatedCircuitRejectObserved: Boolean(combinedScenarioObs.circuitRejectObserved || targeted.openRejectObserved),
  generatedForcedOpenRejectObserved: Boolean(combinedScenarioObs.forcedOpenRejectObserved || targeted.forcedOpenRejectObserved),
  generatedUnknownReleaseObserved: Boolean(combinedScenarioObs.unknownReleaseObserved || targeted.unknownReleaseObserved),
  rejectionNoLeaseGrowthObserved: Boolean(combinedScenarioObs.noMutationRejectObserved || targeted.rejectionNoLeaseGrowthObserved),
  slowCallThresholdObserved: targeted.slowThresholdOpenObserved,
  failureThresholdObserved: targeted.failureThresholdOpenObserved,
  halfOpenFailureReopensObserved: targeted.halfOpenFailureReopensObserved,
  runtimeBootFlagObserved: bootReport.report.executableProofs.circuitBreakerBulkheadModelProof === true,
  traceHasRequiredEvents: requiredTraceKinds.every((kind) => traceKinds.includes(kind))
};

Object.entries(observations).forEach(([name, value]) => assert.equal(value, true, `${name} should be true`));

const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'passed', generatedAt: new Date().toISOString(),
  slice: 'scheduler:circuit-breaker-bulkhead-model-proof',
  purpose: 'Compare CircuitBreakerBulkheadController against an independent deterministic reference model over generated histories before OPFS/browser/provider integration.',
  scenarioCount,
  stepsPerScenario,
  generatedOperationCount: scenarioCount * stepsPerScenario,
  agreementChecks: agreements,
  targeted,
  observations,
  trace: { count: trace.length, kinds: traceKinds, requiredTraceKinds },
  seeds: scenarios.map((scenario) => scenario.seed),
  nonClaims: [
    'No OPFS circuit-breaker/bulkhead model proof.',
    'No browser Worker circuit-breaker/bulkhead model proof.',
    'No production resilience, latency-SLO, real-time timer, throughput, or cross-browser claim.',
    'No exhaustive model checking or formal verification claim.',
    'No exact Resilience4j, Hystrix, Envoy, Polly, Azure, or SRE implementation claim.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
