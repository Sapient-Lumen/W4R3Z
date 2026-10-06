// BrowserRT rev0035 storage-lane admission-history scaffold.
// Fake-provider/virtual-history proof only. No OPFS, browser Worker, wall-clock, durability, performance, or production overload-governance claim.

function assertProvider(label, value, method) {
  if (!value || typeof value[method] !== 'function') throw new Error(`${label} must provide ${method}()`);
}
function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function payloadByteLength(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value).byteLength;
  if (value instanceof Uint8Array) return value.byteLength;
  if (value instanceof ArrayBuffer) return value.byteLength;
  if (ArrayBuffer.isView(value)) return value.byteLength;
  return new TextEncoder().encode(JSON.stringify(value ?? null)).byteLength;
}
function finalOf(row) { return row?.final || row?.result?.final || null; }

export class StorageLaneAdmissionHistoryRunner {
  #trace;
  #history = [];
  #sequence = 1;

  constructor({
    label = 'storage-lane-admission-history-runner',
    admission,
    resilienceRunner,
    mailbox,
    trace = null
  } = {}) {
    assertProvider('StorageLaneAdmissionHistoryRunner admission', admission, 'tryAdmit');
    assertProvider('StorageLaneAdmissionHistoryRunner admission', admission, 'release');
    assertProvider('StorageLaneAdmissionHistoryRunner admission', admission, 'snapshot');
    assertProvider('StorageLaneAdmissionHistoryRunner resilienceRunner', resilienceRunner, 'runMailboxEnqueue');
    assertProvider('StorageLaneAdmissionHistoryRunner resilienceRunner', resilienceRunner, 'snapshot');
    assertProvider('StorageLaneAdmissionHistoryRunner mailbox', mailbox, 'snapshot');
    this.label = label;
    this.admission = admission;
    this.resilienceRunner = resilienceRunner;
    this.mailbox = mailbox;
    this.#trace = trace;
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
      releases: 0
    };
    this.#emit('storage-admission-history:create', { admission: admission.snapshot?.(), resilience: resilienceRunner.snapshot?.() });
  }

  #emit(kind, detail = {}) { this.#trace?.emit(kind, { label: this.label, ...detail }); }
  #record(row) {
    const frozen = Object.freeze(cloneJson(row));
    this.#history.push(frozen);
    return frozen;
  }

  markAdmissionProviderUnhealthy(reason = 'provider-unhealthy') {
    assertProvider('StorageLaneAdmissionHistoryRunner admission', this.admission, 'markProviderUnhealthy');
    this.admission.markProviderUnhealthy(reason);
    this.#emit('storage-admission-history:provider-unhealthy', { reason });
  }

  markAdmissionProviderHealthy(reason = 'provider-healthy') {
    assertProvider('StorageLaneAdmissionHistoryRunner admission', this.admission, 'markProviderHealthy');
    this.admission.markProviderHealthy(reason);
    this.#emit('storage-admission-history:provider-healthy', { reason });
  }

  async runMailboxEnqueue(input = {}) {
    const opId = String(input.id || `storage-admission-op:${this.#sequence++}`);
    const payload = input.payload ?? `payload:${opId}`;
    const bytes = Number.isInteger(input.bytes) ? input.bytes : payloadByteLength(payload);
    const priority = input.priority || 'user-visible';
    const beforeProvider = this.mailbox.snapshot().providerSnapshot?.blockCount ?? 0;
    this.stats.operations += 1;
    this.#emit('storage-admission-history:operation-start', { opId, priority, bytes });

    const gate = this.admission.tryAdmit({ bytes, priority, label: opId, metadata: { opId, kind: 'mailbox-enqueue' } });
    if (!gate.admitted) {
      this.stats.rejectedByAdmission += 1;
      if (gate.disposition === 'rejected-provider-health') this.stats.providerHealthRejected += 1;
      if (gate.disposition === 'rejected-watermark') this.stats.watermarkRejected += 1;
      if (gate.disposition === 'rejected-hard-limit') this.stats.hardLimitRejected += 1;
      const noProviderMutation = (this.mailbox.snapshot().providerSnapshot?.blockCount ?? 0) === beforeProvider;
      if (noProviderMutation) this.stats.noMutationRejects += 1;
      const row = {
        opId,
        priority,
        bytes,
        admission: gate,
        final: { ok: false, reason: `admission:${gate.reason}`, disposition: gate.disposition, attempts: 0, opId, noProviderMutation }
      };
      this.#emit('storage-admission-history:admission-reject', { opId, gate, noProviderMutation });
      this.#emit('storage-admission-history:operation-final', row.final);
      return this.#record(row);
    }

    this.stats.admitted += 1;
    if (gate.bypass) this.stats.criticalBypass += 1;
    this.#emit('storage-admission-history:admitted', { opId, gate });
    let resilienceRow;
    let release;
    try {
      resilienceRow = await this.resilienceRunner.runMailboxEnqueue({ ...input, id: opId, payload, priority });
      const final = finalOf(resilienceRow);
      if (final?.ok === true) this.stats.resilienceSuccesses += 1;
      else this.stats.resilienceFailures += 1;
      release = this.admission.release(gate.leaseId, { outcome: final?.ok ? 'resilience-success' : 'resilience-failure' });
      this.stats.releases += release.released ? 1 : 0;
      const row = { opId, priority, bytes, admission: gate, release, resilience: resilienceRow, final };
      this.#emit('storage-admission-history:release', { opId, release, final });
      this.#emit('storage-admission-history:operation-final', { ...final, admissionReleased: release.released });
      return this.#record(row);
    } catch (error) {
      release = this.admission.release(gate.leaseId, { outcome: 'resilience-throw' });
      this.stats.releases += release.released ? 1 : 0;
      const final = { ok: false, reason: 'resilience-throw', code: error?.code || error?.name || 'BRT_RESILIENCE_THROW', message: error?.message || String(error), opId };
      this.stats.resilienceFailures += 1;
      this.#emit('storage-admission-history:error', { opId, error: final, release });
      this.#emit('storage-admission-history:operation-final', { ...final, admissionReleased: release.released });
      return this.#record({ opId, priority, bytes, admission: gate, release, final });
    }
  }

  history() { return this.#history.map(cloneJson); }

  snapshot() {
    return Object.freeze({
      label: this.label,
      historyCount: this.#history.length,
      stats: { ...this.stats },
      admission: this.admission.snapshot(),
      resilience: this.resilienceRunner.snapshot(),
      mailbox: this.mailbox.snapshot()
    });
  }
}

export function validateStorageLaneAdmissionHistorySnapshot(snapshot) {
  const errors = [];
  const isObj = (value) => value && typeof value === 'object';
  const nonNeg = (name, value) => { if (!Number.isInteger(value) || value < 0) errors.push(`${name} must be a non-negative integer`); };
  if (!isObj(snapshot)) return Object.freeze({ ok: false, errors: ['snapshot must be an object'] });
  nonNeg('historyCount', snapshot.historyCount);
  if (!isObj(snapshot.stats)) errors.push('stats must be present');
  else {
    for (const key of ['operations', 'admitted', 'rejectedByAdmission', 'criticalBypass', 'resilienceSuccesses', 'resilienceFailures', 'providerHealthRejected', 'watermarkRejected', 'hardLimitRejected', 'noMutationRejects', 'releases']) nonNeg(`stats.${key}`, snapshot.stats[key]);
    if (snapshot.stats.operations !== snapshot.historyCount) errors.push('stats.operations must equal historyCount');
    if (snapshot.stats.operations !== snapshot.stats.admitted + snapshot.stats.rejectedByAdmission) errors.push('operations must equal admitted + rejectedByAdmission');
    if (snapshot.stats.admitted !== snapshot.stats.resilienceSuccesses + snapshot.stats.resilienceFailures) errors.push('admitted must equal resilienceSuccesses + resilienceFailures');
    if (snapshot.stats.releases !== snapshot.stats.admitted) errors.push('every admitted operation must release its admission lease');
  }
  if (!isObj(snapshot.admission)) errors.push('admission snapshot must be present');
  else {
    nonNeg('admission.inFlightBytes', snapshot.admission.inFlightBytes);
    nonNeg('admission.leaseCount', snapshot.admission.leaseCount);
  }
  if (!isObj(snapshot.resilience)) errors.push('resilience snapshot must be present');
  if (!isObj(snapshot.mailbox)) errors.push('mailbox snapshot must be present');
  return Object.freeze({ ok: errors.length === 0, errors });
}

export function createStorageLaneAdmissionHistoryRunner(config = {}) {
  return new StorageLaneAdmissionHistoryRunner(config);
}
