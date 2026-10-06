// BrowserRT rev0036 storage-lane admission-history model oracle.
// Fake-provider/model proof only. No OPFS, browser Worker, production overload-governance, throughput, latency, durability, exactly-once, or formal verification claim.

const PRIORITY_RANK = new Map([
  ['maintenance', 0],
  ['background', 1],
  ['user-visible', 2],
  ['user-blocking', 3],
  ['critical', 4]
]);

function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function normalizePriority(priority) {
  const value = priority ?? 'background';
  if (!PRIORITY_RANK.has(value)) throw new Error(`Unsupported priority: ${value}`);
  return value;
}
function rank(priority) { return PRIORITY_RANK.get(normalizePriority(priority)); }
function nonNegInt(name, value, errors) {
  if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`);
}
function assertBytes(bytes) {
  if (!Number.isInteger(bytes) || bytes < 1) throw new Error('bytes must be an integer >= 1');
}
function finalOf(row) { return row?.final || row?.result?.final || null; }

export class StorageLaneAdmissionHistoryModelOracle {
  #held = new Map();
  #nextHeld = 1;
  #trace;
  constructor({
    label = 'storage-lane-admission-history-model-oracle',
    lowWatermarkBytes = 0,
    highWatermarkBytes = 20,
    hardLimitBytes = 64,
    criticalMinPriority = 'user-blocking',
    rejectMinPriorityWhileCongested = 'user-visible',
    trace = null
  } = {}) {
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
    this.providerHealthy = true;
    this.providerHealthReason = null;
    this.providerBlocks = 0;
    this.history = [];
    this.stats = {
      operations: 0,
      admitted: 0,
      rejectedByAdmission: 0,
      criticalBypass: 0,
      resilienceSuccesses: 0,
      resilienceFailures: 0,
      providerHealthRejected: 0,
      watermarkRejected: 0,
      hardLimitRejected: 0,
      noMutationRejects: 0,
      releases: 0,
      directHolds: 0,
      directReleases: 0,
      providerUnhealthyTransitions: 0,
      providerHealthyTransitions: 0
    };
    this.#trace = trace;
    this.#emit('storage-admission-model:create', { highWatermarkBytes, hardLimitBytes });
  }

  #emit(kind, detail = {}) { this.#trace?.emit(kind, { label: this.label, ...detail }); }
  #enterCongestion(projectedBytes, reason = 'high-watermark') {
    if (!this.congested) this.#emit('storage-admission-model:high-watermark', { inFlightBytes: this.inFlightBytes, projectedBytes, reason });
    this.congested = true;
  }
  #maybeRecover(reason = 'release') {
    if (this.congested && this.inFlightBytes <= this.lowWatermarkBytes) {
      this.congested = false;
      this.#emit('storage-admission-model:low-watermark', { inFlightBytes: this.inFlightBytes, reason });
    }
  }
  #predictGate({ bytes, priority = 'background', label = null } = {}) {
    assertBytes(bytes);
    const p = normalizePriority(priority);
    const projectedBytes = this.inFlightBytes + bytes;
    const reject = (disposition, reason) => Object.freeze({ admitted: false, disposition, reason, bytes, priority: p, projectedBytes, label });
    if (bytes > this.hardLimitBytes || projectedBytes > this.hardLimitBytes) return reject('rejected-hard-limit', 'hard-limit');
    if (!this.providerHealthy && rank(p) < rank(this.criticalMinPriority)) return reject('rejected-provider-health', this.providerHealthReason || 'provider-unhealthy');
    const lowPriority = rank(p) < rank(this.rejectMinPriorityWhileCongested);
    if ((this.congested || projectedBytes > this.highWatermarkBytes) && lowPriority) {
      if (projectedBytes > this.highWatermarkBytes) this.#enterCongestion(projectedBytes, 'projected-high-watermark');
      return reject('rejected-watermark', this.congested ? 'congested-low-priority' : 'projected-high-watermark');
    }
    const bypass = (this.congested || projectedBytes > this.highWatermarkBytes) && rank(p) >= rank(this.criticalMinPriority);
    return Object.freeze({ admitted: true, disposition: bypass ? 'admitted-critical-bypass' : 'admitted', bytes, priority: p, projectedBytes, label, bypass });
  }
  #applyGate(gate) {
    this.inFlightBytes = gate.projectedBytes;
    if (this.inFlightBytes >= this.highWatermarkBytes) this.#enterCongestion(this.inFlightBytes, 'admitted-high-watermark');
  }
  #releaseBytes(bytes, reason = 'release') {
    this.inFlightBytes = Math.max(0, this.inFlightBytes - bytes);
    this.#maybeRecover(reason);
  }

  holdLease(input = {}) {
    const gate = this.#predictGate(input);
    if (!gate.admitted) return Object.freeze({ held: false, gate });
    this.#applyGate(gate);
    const leaseId = `model-held:${this.#nextHeld++}`;
    this.#held.set(leaseId, { bytes: gate.bytes, priority: gate.priority });
    this.stats.directHolds += 1;
    this.#emit('storage-admission-model:hold', { leaseId, bytes: gate.bytes, priority: gate.priority, inFlightBytes: this.inFlightBytes });
    return Object.freeze({ held: true, leaseId, gate });
  }

  releaseHeld(leaseId, reason = 'model-held-release') {
    const held = this.#held.get(leaseId);
    if (!held) return Object.freeze({ released: false, leaseId, inFlightBytes: this.inFlightBytes });
    this.#held.delete(leaseId);
    this.#releaseBytes(held.bytes, reason);
    this.stats.directReleases += 1;
    this.#emit('storage-admission-model:release-held', { leaseId, bytes: held.bytes, inFlightBytes: this.inFlightBytes });
    return Object.freeze({ released: true, leaseId, bytes: held.bytes, inFlightBytes: this.inFlightBytes });
  }

  markProviderUnhealthy(reason = 'provider-unhealthy') {
    this.providerHealthy = false;
    this.providerHealthReason = reason;
    this.stats.providerUnhealthyTransitions += 1;
    this.#emit('storage-admission-model:provider-unhealthy', { reason });
  }

  markProviderHealthy(reason = 'provider-healthy') {
    this.providerHealthy = true;
    this.providerHealthReason = null;
    this.stats.providerHealthyTransitions += 1;
    this.#emit('storage-admission-model:provider-healthy', { reason });
  }

  predictAdmission(input = {}) { return this.#predictGate(input); }

  observeOperation(input = {}, row = {}, { providerBlocksBefore = this.providerBlocks, providerBlocksAfter = this.providerBlocks, expectedFinal = 'success' } = {}) {
    const bytes = Number.isInteger(input.bytes) ? input.bytes : 1;
    const priority = input.priority || 'user-visible';
    const gate = this.#predictGate({ bytes, priority, label: input.id || null });
    const final = finalOf(row) || {};
    const errors = [];
    this.stats.operations += 1;

    if (!gate.admitted) {
      this.stats.rejectedByAdmission += 1;
      if (gate.disposition === 'rejected-provider-health') this.stats.providerHealthRejected += 1;
      if (gate.disposition === 'rejected-watermark') this.stats.watermarkRejected += 1;
      if (gate.disposition === 'rejected-hard-limit') this.stats.hardLimitRejected += 1;
      if (final.noProviderMutation === true) this.stats.noMutationRejects += 1;
      if (final.ok !== false) errors.push('real final must be failed for model-predicted admission rejection');
      if (final.disposition !== gate.disposition) errors.push(`real disposition ${final.disposition} != model disposition ${gate.disposition}`);
      if (providerBlocksAfter !== providerBlocksBefore) errors.push('admission rejection must not mutate provider block count');
      if (final.noProviderMutation !== true) errors.push('admission rejection must report noProviderMutation');
      const expected = Object.freeze({ admitted: false, disposition: gate.disposition, providerBlocks: this.providerBlocks });
      this.history.push({ input: cloneJson(input), expected, final: cloneJson(final), errors: errors.slice() });
      this.#emit('storage-admission-model:observe-reject', { disposition: gate.disposition, errors });
      return Object.freeze({ ok: errors.length === 0, errors, expected });
    }

    this.#applyGate(gate);
    this.stats.admitted += 1;
    if (gate.bypass) this.stats.criticalBypass += 1;
    const shouldSucceed = expectedFinal === 'success' || expectedFinal === 'transient-success' || expectedFinal === 'critical-success';
    if (shouldSucceed && final.ok !== true) errors.push(`real final should succeed for ${expectedFinal}`);
    if (!shouldSucceed && final.ok !== false) errors.push(`real final should fail for ${expectedFinal}`);
    if (gate.bypass && row?.admission?.bypass !== true) errors.push('real admission gate should report bypass');
    if (row?.release?.released !== true) errors.push('admitted real operation must release admission lease');
    if (final.ok === true) {
      this.stats.resilienceSuccesses += 1;
      if (providerBlocksAfter < providerBlocksBefore) errors.push('provider block count cannot shrink on successful enqueue');
      if (providerBlocksAfter === providerBlocksBefore) errors.push('successful unique enqueue should add a provider block');
      this.providerBlocks = providerBlocksAfter;
    } else {
      this.stats.resilienceFailures += 1;
      if (providerBlocksAfter !== providerBlocksBefore) errors.push('failed admitted operation should not mutate provider block count in this model slice');
      this.providerBlocks = providerBlocksAfter;
    }
    this.stats.releases += 1;
    this.#releaseBytes(bytes, final.ok ? 'model-success-release' : 'model-failure-release');
    const expected = Object.freeze({ admitted: true, disposition: gate.disposition, finalOk: shouldSucceed, bypass: gate.bypass, providerBlocks: this.providerBlocks });
    this.history.push({ input: cloneJson(input), expected, final: cloneJson(final), errors: errors.slice() });
    this.#emit('storage-admission-model:observe-admitted', { disposition: gate.disposition, finalOk: final.ok === true, errors });
    return Object.freeze({ ok: errors.length === 0, errors, expected });
  }

  snapshot() {
    return Object.freeze({
      label: this.label,
      historyCount: this.history.length,
      heldLeaseCount: this.#held.size,
      inFlightBytes: this.inFlightBytes,
      congested: this.congested,
      providerHealthy: this.providerHealthy,
      providerHealthReason: this.providerHealthReason,
      providerBlocks: this.providerBlocks,
      lowWatermarkBytes: this.lowWatermarkBytes,
      highWatermarkBytes: this.highWatermarkBytes,
      hardLimitBytes: this.hardLimitBytes,
      stats: { ...this.stats }
    });
  }
}

export function compareStorageLaneAdmissionHistoryToModel(realSnapshot, modelSnapshot, { providerSnapshot = null } = {}) {
  const errors = [];
  const rs = realSnapshot?.stats || {};
  const ms = modelSnapshot?.stats || {};
  for (const key of ['operations', 'admitted', 'rejectedByAdmission', 'criticalBypass', 'resilienceSuccesses', 'resilienceFailures', 'providerHealthRejected', 'watermarkRejected', 'hardLimitRejected', 'noMutationRejects', 'releases']) {
    if (rs[key] !== ms[key]) errors.push(`stats.${key}: real ${rs[key]} != model ${ms[key]}`);
  }
  const admission = realSnapshot?.admission || {};
  if (admission.inFlightBytes !== modelSnapshot.inFlightBytes) errors.push(`admission.inFlightBytes: real ${admission.inFlightBytes} != model ${modelSnapshot.inFlightBytes}`);
  if (admission.leaseCount !== modelSnapshot.heldLeaseCount) errors.push(`admission.leaseCount: real ${admission.leaseCount} != model heldLeaseCount ${modelSnapshot.heldLeaseCount}`);
  if (admission.congested !== modelSnapshot.congested) errors.push(`admission.congested: real ${admission.congested} != model ${modelSnapshot.congested}`);
  if (admission.providerHealthy !== modelSnapshot.providerHealthy) errors.push(`admission.providerHealthy: real ${admission.providerHealthy} != model ${modelSnapshot.providerHealthy}`);
  if (providerSnapshot && providerSnapshot.blockCount !== modelSnapshot.providerBlocks) errors.push(`provider.blockCount: real ${providerSnapshot.blockCount} != model ${modelSnapshot.providerBlocks}`);
  if (realSnapshot?.historyCount !== modelSnapshot.historyCount) errors.push(`historyCount: real ${realSnapshot?.historyCount} != model ${modelSnapshot.historyCount}`);
  return Object.freeze({ ok: errors.length === 0, errors });
}

export function validateStorageLaneAdmissionHistoryModelSnapshot(snapshot) {
  const errors = [];
  const obj = snapshot && typeof snapshot === 'object';
  if (!obj) return Object.freeze({ ok: false, errors: ['snapshot must be an object'] });
  for (const key of ['historyCount', 'heldLeaseCount', 'inFlightBytes', 'providerBlocks']) nonNegInt(key, snapshot[key], errors);
  if (typeof snapshot.congested !== 'boolean') errors.push('congested must be boolean');
  if (typeof snapshot.providerHealthy !== 'boolean') errors.push('providerHealthy must be boolean');
  if (!snapshot.stats || typeof snapshot.stats !== 'object') errors.push('stats must be present');
  else {
    for (const key of ['operations', 'admitted', 'rejectedByAdmission', 'resilienceSuccesses', 'resilienceFailures', 'releases']) nonNegInt(`stats.${key}`, snapshot.stats[key], errors);
    if (snapshot.stats.operations !== snapshot.historyCount) errors.push('stats.operations must equal historyCount');
    if (snapshot.stats.operations !== snapshot.stats.admitted + snapshot.stats.rejectedByAdmission) errors.push('operations must equal admitted + rejectedByAdmission');
    if (snapshot.stats.admitted !== snapshot.stats.resilienceSuccesses + snapshot.stats.resilienceFailures) errors.push('admitted must equal resilienceSuccesses + resilienceFailures');
    if (snapshot.stats.releases !== snapshot.stats.admitted) errors.push('each admitted operation must release admission lease in model');
  }
  return Object.freeze({ ok: errors.length === 0, errors });
}

export function createStorageLaneAdmissionHistoryModelOracle(config = {}) {
  return new StorageLaneAdmissionHistoryModelOracle(config);
}
