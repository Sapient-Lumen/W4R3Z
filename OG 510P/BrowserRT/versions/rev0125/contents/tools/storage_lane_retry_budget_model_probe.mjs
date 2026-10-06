#!/usr/bin/env node
// BrowserRT rev0033 retry-budget model/history proof.
// Fake-provider/model slice only: no OPFS, browser, wall-clock, production retry-storm safety, or formal verification claim.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  boot,
  createRetryBudgetAdmissionController,
  validateRetryBudgetAdmissionSnapshot
} from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/validation/${PREFIX}-STORAGE-LANE-RETRY-BUDGET-MODEL-PROBE.json`);

const PRIORITY_ORDER = Object.freeze(['critical', 'user-blocking', 'user-visible', 'background', 'maintenance']);
const BYPASS_PRIORITIES = new Set(['critical']);

function lcg(seed) {
  let state = seed >>> 0;
  return () => {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 0x100000000;
  };
}
function pick(rnd, values) { return values[Math.floor(rnd() * values.length) % values.length]; }
function deterministicId(prefix, n) { return `${prefix}:${String(n).padStart(4, '0')}`; }
function normalizePriority(priority) { const p = String(priority || 'background'); return PRIORITY_ORDER.includes(p) ? p : 'background'; }
function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function comparableSnapshot(snapshot) {
  return {
    retryCredits: snapshot.retryCredits,
    activeRetries: snapshot.activeRetries,
    providerHealthy: snapshot.providerHealthy,
    leaseCount: snapshot.leaseCount,
    leases: snapshot.leases.map((lease) => ({ leaseId: lease.leaseId, opId: lease.opId, attempt: lease.attempt, priority: lease.priority, idempotent: lease.idempotent, code: lease.code, spentCredit: lease.spentCredit, bypass: lease.bypass })).sort((a, b) => a.leaseId.localeCompare(b.leaseId)),
    stats: cloneJson(snapshot.stats)
  };
}

class RetryBudgetModel {
  constructor(config = {}) {
    this.label = config.label || 'retry-budget-model';
    this.maxRetryCredits = config.maxRetryCredits ?? 4;
    this.initialRetryCredits = config.initialRetryCredits ?? 1;
    this.refillPerPrimarySuccess = config.refillPerPrimarySuccess ?? 1;
    this.refillPerPrimaryFailure = config.refillPerPrimaryFailure ?? 0;
    this.maxActiveRetries = config.maxActiveRetries ?? 2;
    this.minRetryCredits = config.minRetryCredits ?? 0;
    this.allowCriticalBypass = config.allowCriticalBypass !== false;
    this.requireIdempotent = config.requireIdempotent !== false;
    this.retryCredits = this.initialRetryCredits;
    this.activeRetries = 0;
    this.providerHealthy = true;
    this.sequence = 1;
    this.leases = new Map();
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
    return { observed: true, ok, before, after: this.retryCredits, gained, reason: ok ? 'primary-success' : 'primary-failure' };
  }
  tryAcquireRetry(input = {}) {
    const priority = normalizePriority(input.priority);
    const idempotent = input.idempotent !== false;
    const opId = String(input.opId || input.id || deterministicId('retry-budget-op', this.sequence));
    const attempt = Number.isInteger(input.attempt) ? input.attempt : Number.isInteger(input.nextAttempt) ? input.nextAttempt : null;
    const code = input.code || null;
    const isBypass = this.allowCriticalBypass && BYPASS_PRIORITIES.has(priority);
    const reject = (reason) => {
      this.stats.retryRejected += 1;
      if (reason === 'non-idempotent') this.stats.nonIdempotentRejected += 1;
      if (reason === 'retry-budget-exhausted') this.stats.exhaustedRejected += 1;
      if (reason === 'active-retry-limit') this.stats.activeLimitRejected += 1;
      if (reason === 'provider-unhealthy') this.stats.providerHealthRejected += 1;
      return { accepted: false, reason, opId, attempt, priority, idempotent, code, retryCredits: this.retryCredits, activeRetries: this.activeRetries };
    };
    if (!this.providerHealthy) return reject('provider-unhealthy');
    if (this.requireIdempotent && !idempotent) return reject('non-idempotent');
    if (this.activeRetries >= this.maxActiveRetries) return reject('active-retry-limit');
    if (!isBypass && this.retryCredits <= this.minRetryCredits) return reject('retry-budget-exhausted');
    const leaseId = deterministicId('retry-budget-lease', this.sequence++);
    const spentCredit = isBypass ? 0 : 1;
    if (spentCredit) this.retryCredits -= spentCredit;
    this.activeRetries += 1;
    this.stats.retryAccepted += 1;
    if (isBypass) this.stats.criticalBypassAccepted += 1;
    const lease = { leaseId, opId, attempt, priority, idempotent, code, spentCredit, bypass: isBypass, acquiredAtSequence: this.sequence - 1 };
    this.leases.set(leaseId, lease);
    return { accepted: true, reason: isBypass ? 'critical-bypass' : 'budget-credit', leaseId, opId, attempt, priority, idempotent, spentCredit, retryCredits: this.retryCredits, activeRetries: this.activeRetries };
  }
  releaseRetry(leaseOrId, result = {}) {
    const leaseId = typeof leaseOrId === 'string' ? leaseOrId : leaseOrId?.leaseId;
    if (!leaseId || !this.leases.has(leaseId)) return { released: false, reason: 'unknown-lease', leaseId: leaseId || null };
    const lease = this.leases.get(leaseId);
    this.leases.delete(leaseId);
    this.activeRetries = Math.max(0, this.activeRetries - 1);
    this.stats.retryReleased += 1;
    return { released: true, leaseId, opId: lease.opId, attempt: lease.attempt, ok: result.ok === true, activeRetries: this.activeRetries, retryCredits: this.retryCredits };
  }
  markProviderUnhealthy() { this.providerHealthy = false; }
  markProviderHealthy() { this.providerHealthy = true; }
  snapshot() {
    return {
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
      leaseCount: this.leases.size,
      leases: [...this.leases.values()].map(cloneJson),
      stats: { ...this.stats }
    };
  }
}

function compare(real, model, context) {
  const validation = validateRetryBudgetAdmissionSnapshot(real.snapshot());
  assert.equal(validation.ok, true, `${context}: real snapshot invalid: ${validation.errors.join('; ')}`);
  assert.deepEqual(comparableSnapshot(real.snapshot()), comparableSnapshot(model.snapshot()), `${context}: real/model snapshot mismatch`);
}

function forceObservations(real, model, obs) {
  const step = (name, fn) => { fn(); compare(real, model, `targeted:${name}`); };
  step('first-acquire', () => {
    const r = real.tryAcquireRetry({ opId: 'target:first', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    const m = model.tryAcquireRetry({ opId: 'target:first', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    assert.deepEqual(r.accepted, m.accepted); obs.acceptedObserved ||= r.accepted;
  });
  step('active-limit', () => {
    const r = real.tryAcquireRetry({ opId: 'target:active-limit', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    const m = model.tryAcquireRetry({ opId: 'target:active-limit', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    assert.equal(r.reason, m.reason); obs.activeLimitRejectObserved ||= r.reason === 'active-retry-limit';
  });
  const lease = real.snapshot().leases[0]?.leaseId;
  step('release-first', () => {
    const r = real.releaseRetry(lease, { ok: true });
    const m = model.releaseRetry(lease, { ok: true });
    assert.equal(r.released, m.released); obs.releaseObserved ||= r.released;
  });
  step('budget-exhausted', () => {
    const r = real.tryAcquireRetry({ opId: 'target:exhausted', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    const m = model.tryAcquireRetry({ opId: 'target:exhausted', attempt: 2, priority: 'background', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    assert.equal(r.reason, m.reason); obs.budgetExhaustRejectObserved ||= r.reason === 'retry-budget-exhausted';
  });
  step('critical-bypass', () => {
    const r = real.tryAcquireRetry({ opId: 'target:critical', attempt: 2, priority: 'critical', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    const m = model.tryAcquireRetry({ opId: 'target:critical', attempt: 2, priority: 'critical', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    assert.equal(r.reason, m.reason); obs.criticalBypassObserved ||= r.accepted && r.reason === 'critical-bypass' && r.spentCredit === 0;
  });
  const criticalLease = real.snapshot().leases[0]?.leaseId;
  step('release-critical', () => { real.releaseRetry(criticalLease, { ok: true }); model.releaseRetry(criticalLease, { ok: true }); });
  step('provider-unhealthy', () => { real.markProviderUnhealthy('target'); model.markProviderUnhealthy('target'); obs.providerUnhealthyTransitionObserved = true; });
  step('provider-unhealthy-reject', () => {
    const r = real.tryAcquireRetry({ opId: 'target:unhealthy', attempt: 2, priority: 'critical', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    const m = model.tryAcquireRetry({ opId: 'target:unhealthy', attempt: 2, priority: 'critical', idempotent: true, code: 'BRT_STORAGE_INJECTED_FAULT' });
    assert.equal(r.reason, m.reason); obs.providerUnhealthyRejectObserved ||= r.reason === 'provider-unhealthy';
  });
  step('provider-healthy', () => { real.markProviderHealthy('target'); model.markProviderHealthy('target'); obs.providerHealthRecoveryObserved = true; });
  step('non-idempotent', () => {
    const r = real.tryAcquireRetry({ opId: 'target:non-idempotent', attempt: 2, priority: 'background', idempotent: false, code: 'BRT_STORAGE_INJECTED_FAULT' });
    const m = model.tryAcquireRetry({ opId: 'target:non-idempotent', attempt: 2, priority: 'background', idempotent: false, code: 'BRT_STORAGE_INJECTED_FAULT' });
    assert.equal(r.reason, m.reason); obs.nonIdempotentRejectObserved ||= r.reason === 'non-idempotent';
  });
  step('primary-refill', () => {
    const r = real.observePrimary({ ok: true });
    const m = model.observePrimary({ ok: true });
    assert.equal(r.gained, m.gained); obs.primaryRefillObserved ||= r.gained > 0;
  });
  step('unknown-release', () => {
    const r = real.releaseRetry('missing-lease', { ok: false });
    const m = model.releaseRetry('missing-lease', { ok: false });
    assert.equal(r.reason, m.reason); obs.unknownReleaseObserved ||= r.reason === 'unknown-lease';
  });
}

function generatedWalk({ seed, scenarioIndex, steps }) {
  const config = {
    label: `rev0033-budget-model-${scenarioIndex}`,
    maxRetryCredits: 2 + (scenarioIndex % 4),
    initialRetryCredits: scenarioIndex % 3,
    refillPerPrimarySuccess: 1 + (scenarioIndex % 2),
    refillPerPrimaryFailure: scenarioIndex % 2,
    maxActiveRetries: 1 + (scenarioIndex % 3),
    minRetryCredits: 0,
    allowCriticalBypass: true,
    requireIdempotent: scenarioIndex % 5 !== 0
  };
  if (config.initialRetryCredits > config.maxRetryCredits) config.initialRetryCredits = config.maxRetryCredits;
  const real = createRetryBudgetAdmissionController(config);
  const model = new RetryBudgetModel(config);
  const rnd = lcg(seed);
  const obs = {
    acceptedObserved: false,
    activeLimitRejectObserved: false,
    budgetExhaustRejectObserved: false,
    nonIdempotentRejectObserved: false,
    providerUnhealthyRejectObserved: false,
    providerUnhealthyTransitionObserved: false,
    providerHealthRecoveryObserved: false,
    criticalBypassObserved: false,
    primaryRefillObserved: false,
    unknownReleaseObserved: false,
    rejectionNoLeaseGrowthObserved: false
  };
  if (scenarioIndex === 0) {
    const targetedReal = createRetryBudgetAdmissionController({ label: 'rev0033-targeted-budget-model', maxRetryCredits: 2, initialRetryCredits: 1, refillPerPrimarySuccess: 1, refillPerPrimaryFailure: 0, maxActiveRetries: 1, allowCriticalBypass: true, requireIdempotent: true });
    const targetedModel = new RetryBudgetModel({ label: 'rev0033-targeted-budget-model', maxRetryCredits: 2, initialRetryCredits: 1, refillPerPrimarySuccess: 1, refillPerPrimaryFailure: 0, maxActiveRetries: 1, allowCriticalBypass: true, requireIdempotent: true });
    forceObservations(targetedReal, targetedModel, obs);
  }
  let agreements = 0;
  for (let step = 0; step < steps; step += 1) {
    const choice = Math.floor(rnd() * 10);
    if (choice <= 2) {
      const ok = rnd() >= 0.3;
      const r = real.observePrimary({ ok, opId: `scenario:${scenarioIndex}:primary:${step}` });
      const m = model.observePrimary({ ok, opId: `scenario:${scenarioIndex}:primary:${step}` });
      assert.equal(r.gained, m.gained, `scenario ${scenarioIndex} step ${step} primary gain mismatch`);
      obs.primaryRefillObserved ||= r.gained > 0;
    } else if (choice === 3) {
      real.markProviderUnhealthy(`scenario-${scenarioIndex}-step-${step}`);
      model.markProviderUnhealthy(`scenario-${scenarioIndex}-step-${step}`);
      obs.providerUnhealthyTransitionObserved = true;
    } else if (choice === 4) {
      real.markProviderHealthy(`scenario-${scenarioIndex}-step-${step}`);
      model.markProviderHealthy(`scenario-${scenarioIndex}-step-${step}`);
      obs.providerHealthRecoveryObserved = true;
    } else if (choice <= 8) {
      const beforeLeaseCount = real.snapshot().leaseCount;
      const input = {
        opId: `scenario:${scenarioIndex}:op:${step}`,
        attempt: 2 + (step % 4),
        priority: pick(rnd, PRIORITY_ORDER),
        idempotent: rnd() >= 0.2,
        code: pick(rnd, ['BRT_STORAGE_INJECTED_FAULT', 'BRT_STORAGE_QUOTA_TRANSIENT', 'BRT_STORAGE_PROVIDER_REJECTED'])
      };
      const r = real.tryAcquireRetry(input);
      const m = model.tryAcquireRetry(input);
      assert.equal(r.accepted, m.accepted, `scenario ${scenarioIndex} step ${step} acquire acceptance mismatch`);
      assert.equal(r.reason, m.reason, `scenario ${scenarioIndex} step ${step} acquire reason mismatch`);
      if (r.accepted) {
        obs.acceptedObserved = true;
        obs.criticalBypassObserved ||= r.reason === 'critical-bypass' && r.spentCredit === 0;
      } else {
        obs.activeLimitRejectObserved ||= r.reason === 'active-retry-limit';
        obs.budgetExhaustRejectObserved ||= r.reason === 'retry-budget-exhausted';
        obs.nonIdempotentRejectObserved ||= r.reason === 'non-idempotent';
        obs.providerUnhealthyRejectObserved ||= r.reason === 'provider-unhealthy';
        obs.rejectionNoLeaseGrowthObserved ||= real.snapshot().leaseCount === beforeLeaseCount;
      }
    } else {
      const leases = real.snapshot().leases;
      if (leases.length && rnd() >= 0.2) {
        const leaseId = pick(rnd, leases).leaseId;
        const ok = rnd() >= 0.4;
        const r = real.releaseRetry(leaseId, { ok });
        const m = model.releaseRetry(leaseId, { ok });
        assert.equal(r.released, m.released, `scenario ${scenarioIndex} step ${step} release mismatch`);
      } else {
        const r = real.releaseRetry(`unknown:${scenarioIndex}:${step}`, { ok: false });
        const m = model.releaseRetry(`unknown:${scenarioIndex}:${step}`, { ok: false });
        assert.equal(r.reason, m.reason, `scenario ${scenarioIndex} step ${step} unknown release mismatch`);
        obs.unknownReleaseObserved ||= r.reason === 'unknown-lease';
      }
    }
    compare(real, model, `scenario:${scenarioIndex}:step:${step}`);
    agreements += 1;
  }
  // Drain accepted leases so final accounting is empty and compare again.
  for (const lease of real.snapshot().leases.slice()) {
    real.releaseRetry(lease.leaseId, { ok: true });
    model.releaseRetry(lease.leaseId, { ok: true });
    compare(real, model, `scenario:${scenarioIndex}:drain:${lease.leaseId}`);
    agreements += 1;
  }
  const finalValidation = validateRetryBudgetAdmissionSnapshot(real.snapshot());
  assert.equal(finalValidation.ok, true, `scenario ${scenarioIndex} final snapshot invalid`);
  return { scenarioIndex, seed, steps, agreements, observations: obs, snapshot: real.snapshot() };
}

const rt = await boot({ telemetry: 'always', proof: REVISION, storageLaneRetryBudgetProof: true, storageLaneRetryBudgetModelProof: true });
assert.match(REVISION, /^rev\d{4}$/);
assert.match(VERSION, /^0\.0\.\d+$/);
assert.equal(validateRetryBudgetAdmissionSnapshot(rt.retryBudgetAdmissionController({ label: 'validator-smoke' }).snapshot()).ok, true);

const scenarioCount = 32;
const stepsPerScenario = 96;
const scenarios = [];
for (let i = 0; i < scenarioCount; i += 1) scenarios.push(generatedWalk({ seed: 0xB00B1E + i * 104729, scenarioIndex: i, steps: stepsPerScenario }));

const aggregate = scenarios.reduce((acc, scenario) => {
  acc.totalSteps += scenario.steps;
  acc.totalAgreements += scenario.agreements;
  for (const [key, value] of Object.entries(scenario.observations)) acc[key] ||= Boolean(value);
  acc.finalActiveRetries += scenario.snapshot.activeRetries;
  acc.finalLeaseCount += scenario.snapshot.leaseCount;
  acc.totalAccepted += scenario.snapshot.stats.retryAccepted;
  acc.totalRejected += scenario.snapshot.stats.retryRejected;
  return acc;
}, { totalSteps: 0, totalAgreements: 0, finalActiveRetries: 0, finalLeaseCount: 0, totalAccepted: 0, totalRejected: 0 });

const trace = rt.close();
const traceKinds = [...new Set(trace.map((event) => event.kind))];
const observations = {
  retryBudgetModelWalkCreated: true,
  snapshotValidatorExported: typeof validateRetryBudgetAdmissionSnapshot === 'function',
  scenarioCount: scenarioCount === 32,
  generatedSteps: aggregate.totalSteps === scenarioCount * stepsPerScenario,
  realModelAgreementEveryStep: aggregate.totalAgreements >= aggregate.totalSteps,
  deterministicReplaySeedsRecorded: scenarios.every((s, i) => s.seed === 0xB00B1E + i * 104729),
  acceptedObserved: aggregate.acceptedObserved === true,
  activeLimitRejectObserved: aggregate.activeLimitRejectObserved === true,
  budgetExhaustRejectObserved: aggregate.budgetExhaustRejectObserved === true,
  nonIdempotentRejectObserved: aggregate.nonIdempotentRejectObserved === true,
  providerUnhealthyRejectObserved: aggregate.providerUnhealthyRejectObserved === true,
  providerHealthRecoveryObserved: aggregate.providerHealthRecoveryObserved === true,
  criticalBypassObserved: aggregate.criticalBypassObserved === true,
  primaryRefillObserved: aggregate.primaryRefillObserved === true,
  unknownReleaseObserved: aggregate.unknownReleaseObserved === true,
  rejectionNoLeaseGrowthObserved: aggregate.rejectionNoLeaseGrowthObserved === true,
  finalAccountingEmpty: aggregate.finalActiveRetries === 0 && aggregate.finalLeaseCount === 0,
  finalSnapshotsValidated: scenarios.every((s) => validateRetryBudgetAdmissionSnapshot(s.snapshot).ok === true),
  bootReportRecordsRetryBudgetModelProof: rt.report.executableProofs.storageLaneRetryBudgetModelProof === true,
  traceHasRequiredEvents: ['runtime:boot', 'runtime:close'].every((kind) => traceKinds.includes(kind))
};
for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  status: 'passed',
  slice: 'scheduler:storage-lane-retry-budget-model-proof',
  generatedAt: new Date().toISOString(),
  purpose: 'Deterministic fake-provider/model-walk proof for retry-budget admission semantics before OPFS/browser spending.',
  observations,
  counts: {
    scenarioCount,
    stepsPerScenario,
    totalGeneratedSteps: aggregate.totalSteps,
    totalAgreementChecks: aggregate.totalAgreements,
    totalAcceptedRetries: aggregate.totalAccepted,
    totalRejectedRetries: aggregate.totalRejected,
    traceEvents: trace.length
  },
  scenarioSummaries: scenarios.map((scenario) => ({ scenarioIndex: scenario.scenarioIndex, seed: scenario.seed, steps: scenario.steps, agreements: scenario.agreements, stats: scenario.snapshot.stats, retryCredits: scenario.snapshot.retryCredits })),
  traceKinds,
  nonClaims: [
    'No OPFS retry-budget model proof.',
    'No browser Worker retry-budget model proof.',
    'No production retry-storm safety claim.',
    'No exhaustive model checking or formal verification claim.',
    'No wall-clock timer, throughput, latency, fairness, or SLO claim.',
    'No exactly-once delivery claim.',
    'No durability, fsync, quota, eviction, or crash-recovery claim.',
    'No cross-browser conformance claim.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
