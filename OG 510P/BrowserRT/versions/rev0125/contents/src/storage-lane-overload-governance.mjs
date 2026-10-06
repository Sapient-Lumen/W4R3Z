// BrowserRT rev0039 storage-lane overload-governance model scaffold.
// Fake-provider/model proof only. No OPFS, browser Worker, production overload-governance,
// throughput, latency, durability, exactly-once, or formal verification claim.

function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function finalOf(row) { return row?.final || row?.result?.final || null; }
function nonNeg(name, value, errors) {
  if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`);
}
function classify(row = {}) {
  const final = finalOf(row) || {};
  const classes = new Set();
  if (final.ok === true) classes.add('success');
  if (final.reason === 'retry-success') classes.add('retry-success');
  if (row?.admission?.bypass === true) classes.add('critical-bypass');
  if (final.disposition === 'rejected-watermark') classes.add('admission-watermark');
  if (final.disposition === 'rejected-provider-health') classes.add('admission-health');
  if (final.disposition === 'rejected-hard-limit') classes.add('admission-hard-limit');
  if (String(final.reason || '').startsWith('retry-budget:')) classes.add('retry-budget-reject');
  if (final.reason === 'retry-budget:retry-budget-exhausted') classes.add('retry-budget-exhausted');
  if (final.reason === 'retry-budget:non-idempotent') classes.add('retry-budget-non-idempotent');
  if (String(final.reason || '').startsWith('breaker:')) classes.add('breaker-reject');
  if (final.reason === 'breaker:bulkhead-full') classes.add('breaker-bulkhead');
  if (final.reason === 'breaker:circuit-open') classes.add('breaker-open');
  return classes;
}

export class StorageLaneOverloadGovernanceModelOracle {
  #trace;
  #history = [];
  constructor({ label = 'storage-lane-overload-governance-model-oracle', trace = null } = {}) {
    this.label = label;
    this.#trace = trace;
    this.stats = {
      operations: 0,
      successes: 0,
      failures: 0,
      admissionRejected: 0,
      resilienceFailures: 0,
      retrySuccesses: 0,
      retryBudgetRejected: 0,
      retryBudgetExhausted: 0,
      nonIdempotentRejected: 0,
      breakerRejected: 0,
      bulkheadRejected: 0,
      circuitOpenRejected: 0,
      providerHealthRejected: 0,
      watermarkRejected: 0,
      hardLimitRejected: 0,
      criticalBypass: 0,
      noMutationRejects: 0,
      providerMutationsOnRejectedFinal: 0,
      admissionReleaseFailures: 0,
      expectedClassMismatches: 0,
      snapshotChecks: 0,
      snapshotFailures: 0
    };
    this.#emit('storage-overload-model:create', { snapshot: this.snapshot() });
  }

  #emit(kind, detail = {}) { this.#trace?.emit(kind, { label: this.label, ...detail }); }
  #record(row) {
    const frozen = Object.freeze(cloneJson(row));
    this.#history.push(frozen);
    return frozen;
  }

  observeOperation({ label = null, input = {}, row = {}, beforeProviderBlocks = 0, afterProviderBlocks = 0, expectedClasses = [], expectNoProviderMutation = null } = {}) {
    const final = finalOf(row) || {};
    const classes = classify(row);
    const errors = [];
    const admitted = row?.admission?.admitted === true || String(row?.admission?.disposition || '').startsWith('admitted');
    const rejected = final.ok === false;
    const providerDelta = afterProviderBlocks - beforeProviderBlocks;
    this.stats.operations += 1;
    if (final.ok === true) this.stats.successes += 1;
    else this.stats.failures += 1;
    if (!admitted) this.stats.admissionRejected += 1;
    else if (final.ok === false) this.stats.resilienceFailures += 1;
    if (classes.has('retry-success')) this.stats.retrySuccesses += 1;
    if (classes.has('retry-budget-reject')) this.stats.retryBudgetRejected += 1;
    if (classes.has('retry-budget-exhausted')) this.stats.retryBudgetExhausted += 1;
    if (classes.has('retry-budget-non-idempotent')) this.stats.nonIdempotentRejected += 1;
    if (classes.has('breaker-reject')) this.stats.breakerRejected += 1;
    if (classes.has('breaker-bulkhead')) this.stats.bulkheadRejected += 1;
    if (classes.has('breaker-open')) this.stats.circuitOpenRejected += 1;
    if (classes.has('admission-health')) this.stats.providerHealthRejected += 1;
    if (classes.has('admission-watermark')) this.stats.watermarkRejected += 1;
    if (classes.has('admission-hard-limit')) this.stats.hardLimitRejected += 1;
    if (classes.has('critical-bypass')) this.stats.criticalBypass += 1;
    if (rejected && (final.noProviderMutation === true || providerDelta === 0)) this.stats.noMutationRejects += 1;
    if (rejected && providerDelta !== 0) this.stats.providerMutationsOnRejectedFinal += 1;
    if (admitted && row?.release?.released !== true) {
      this.stats.admissionReleaseFailures += 1;
      errors.push('admitted operation did not release admission lease');
    }
    for (const expected of expectedClasses) {
      if (!classes.has(expected)) errors.push(`expected class ${expected} not observed`);
    }
    if (expectNoProviderMutation === true && providerDelta !== 0) errors.push('expected no provider mutation but provider block count changed');
    if (expectNoProviderMutation === false && providerDelta <= 0) errors.push('expected provider mutation but provider block count did not increase');
    if (errors.length) this.stats.expectedClassMismatches += 1;
    const observation = { label, input: cloneJson(input), final: cloneJson(final), admitted, providerBlocks: { before: beforeProviderBlocks, after: afterProviderBlocks, delta: providerDelta }, classes: [...classes].sort(), expectedClasses: expectedClasses.slice(), errors };
    this.#emit(errors.length ? 'storage-overload-model:observe-error' : 'storage-overload-model:observe', observation);
    return this.#record(observation);
  }

  observeSnapshot({ label = null, admission = null, resilience = null, breaker = null, retryBudget = null } = {}) {
    const errors = [];
    this.stats.snapshotChecks += 1;
    const admissionSnap = admission?.snapshot ? admission.snapshot() : admission;
    const resilienceSnap = resilience?.snapshot ? resilience.snapshot() : resilience;
    const breakerSnap = breaker?.snapshot ? breaker.snapshot() : breaker;
    const retryBudgetSnap = retryBudget?.snapshot ? retryBudget.snapshot() : retryBudget;
    if (admissionSnap && (admissionSnap.leaseCount || 0) < 0) errors.push('admission leaseCount must not be negative');
    if (breakerSnap && (breakerSnap.leaseCount || 0) < 0) errors.push('breaker leaseCount must not be negative');
    if (retryBudgetSnap && (retryBudgetSnap.leaseCount || 0) < 0) errors.push('retry budget leaseCount must not be negative');
    if (resilienceSnap?.stats && (resilienceSnap.stats.successes || 0) + (resilienceSnap.stats.failures || 0) > (resilienceSnap.stats.operations || 0)) errors.push('resilience success/failure count exceeds operations');
    if (errors.length) this.stats.snapshotFailures += 1;
    const row = { label, kind: 'snapshot', errors, admission: admissionSnap ? { leaseCount: admissionSnap.leaseCount, inFlightBytes: admissionSnap.inFlightBytes, providerHealthy: admissionSnap.providerHealthy, congested: admissionSnap.congested } : null, breaker: breakerSnap ? { state: breakerSnap.state, leaseCount: breakerSnap.leaseCount, active: breakerSnap.active } : null, retryBudget: retryBudgetSnap ? { retryCredits: retryBudgetSnap.retryCredits, activeRetries: retryBudgetSnap.activeRetries, leaseCount: retryBudgetSnap.leaseCount, providerHealthy: retryBudgetSnap.providerHealthy } : null };
    this.#emit(errors.length ? 'storage-overload-model:snapshot-error' : 'storage-overload-model:snapshot', row);
    return this.#record(row);
  }

  history() { return this.#history.map(cloneJson); }
  snapshot() {
    return Object.freeze({ label: this.label, historyCount: this.#history.length, stats: { ...this.stats } });
  }
}

export function validateStorageLaneOverloadGovernanceSnapshot(snapshot) {
  const errors = [];
  if (!snapshot || typeof snapshot !== 'object') return Object.freeze({ ok: false, errors: ['snapshot must be an object'] });
  nonNeg('historyCount', snapshot.historyCount, errors);
  if (!snapshot.stats || typeof snapshot.stats !== 'object') errors.push('stats must be present');
  else {
    for (const key of ['operations', 'successes', 'failures', 'admissionRejected', 'resilienceFailures', 'retrySuccesses', 'retryBudgetRejected', 'retryBudgetExhausted', 'nonIdempotentRejected', 'breakerRejected', 'bulkheadRejected', 'circuitOpenRejected', 'providerHealthRejected', 'watermarkRejected', 'hardLimitRejected', 'criticalBypass', 'noMutationRejects', 'providerMutationsOnRejectedFinal', 'admissionReleaseFailures', 'expectedClassMismatches', 'snapshotChecks', 'snapshotFailures']) nonNeg(`stats.${key}`, snapshot.stats[key], errors);
    if ((snapshot.stats.successes || 0) + (snapshot.stats.failures || 0) !== (snapshot.stats.operations || 0)) errors.push('successes + failures must equal operations');
    if ((snapshot.stats.admissionRejected || 0) + (snapshot.stats.resilienceFailures || 0) > (snapshot.stats.failures || 0)) errors.push('admissionRejected + resilienceFailures must not exceed failures');
    if ((snapshot.stats.bulkheadRejected || 0) + (snapshot.stats.circuitOpenRejected || 0) > (snapshot.stats.breakerRejected || 0)) errors.push('breaker rejection subcounts must not exceed breakerRejected');
  }
  return Object.freeze({ ok: errors.length === 0, errors });
}

export function compareStorageLaneOverloadGovernanceToRuntime(governanceSnapshot, runtimeSnapshot = {}) {
  const errors = [];
  const validation = validateStorageLaneOverloadGovernanceSnapshot(governanceSnapshot);
  if (!validation.ok) errors.push(...validation.errors);
  const stats = governanceSnapshot?.stats || {};
  if ((stats.providerMutationsOnRejectedFinal || 0) !== 0) errors.push('rejected finals must not mutate provider block count in this slice');
  if ((stats.admissionReleaseFailures || 0) !== 0) errors.push('admitted operations must release admission leases');
  if ((stats.expectedClassMismatches || 0) !== 0) errors.push('expected classes must match observations');
  if ((stats.snapshotFailures || 0) !== 0) errors.push('snapshot checks must not fail');
  if (runtimeSnapshot.admission && (runtimeSnapshot.admission.leaseCount || 0) !== 0) errors.push('final admission leaseCount must be zero');
  if (runtimeSnapshot.breaker && (runtimeSnapshot.breaker.leaseCount || 0) !== 0) errors.push('final breaker leaseCount must be zero');
  if (runtimeSnapshot.retryBudget && (runtimeSnapshot.retryBudget.leaseCount || 0) !== 0) errors.push('final retry-budget leaseCount must be zero');
  return Object.freeze({ ok: errors.length === 0, errors, stats: { ...stats } });
}

export function createStorageLaneOverloadGovernanceModelOracle(config = {}) {
  return new StorageLaneOverloadGovernanceModelOracle(config);
}
