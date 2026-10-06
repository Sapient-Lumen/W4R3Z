// BrowserRT Web-Lock-guarded block-store wrapper.
// This wrapper serializes mutating provider calls through one same-origin Web
// Lock and routes read-like calls through shared locks where supported. It is a
// coordination boundary only: no OPFS durability, fsync, eviction, quota, crash,
// Trace event aliases include storage:opfs-web-lock-guard-exclusive-start and storage:opfs-web-lock-guard-shared-end for auditability.
// fairness, or cross-browser claim is implied. Rev0106 composes signal/abortSignal for direct guarded lock acquisition and provider calls.
// Rev0125 exposes recoverStagedWrites through the same exclusive Web Lock so staged-temp cleanup cannot race guarded puts across provider instances/tabs.

import { createWebLockCoordinator, WebLockCoordinator } from './web-lock-coordinator.mjs';

function cleanLockNamePart(part) {
  const cleaned = String(part || '').replace(/[^a-zA-Z0-9_.:-]+/g, '-').replace(/^-+|-+$/g, '');
  return cleaned || 'opfs-block-store';
}

function describeError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null };
}

function normalizeLockTimeoutMs(timeoutMs) {
  if (timeoutMs === undefined || timeoutMs === null || timeoutMs === false) return 0;
  const n = Number(timeoutMs);
  if (!Number.isFinite(n) || n < 0) throw new Error(`lockTimeoutMs must be a non-negative finite number: ${timeoutMs}`);
  return Math.floor(n);
}


const GUARDED_ABORT_CLEANUP = Symbol('BrowserRT.WebLockGuardedBlockStore.abortCleanup');

function hasOwn(value, key) {
  return Object.prototype.hasOwnProperty.call(value || {}, key);
}

function isAbortSignalObject(value) {
  if (value == null || (typeof value !== 'object' && typeof value !== 'function')) return false;
  const structural = typeof value.aborted === 'boolean' && typeof value.addEventListener === 'function' && typeof value.removeEventListener === 'function';
  if (!structural) return false;
  const AbortSignalCtor = globalThis.AbortSignal;
  return typeof AbortSignalCtor !== 'function' || value instanceof AbortSignalCtor;
}

function guardedAbortReason(signal, fallback) {
  try { return signal?.reason ?? fallback; } catch { return fallback; }
}

function composeGuardedAbortSignals(signals = []) {
  const uniqueSignals = [];
  const seen = new Set();
  for (const signal of signals) {
    if (!isAbortSignalObject(signal) || seen.has(signal)) continue;
    seen.add(signal);
    uniqueSignals.push(signal);
  }
  if (uniqueSignals.length === 0) return Object.freeze({ signal: null, cleanup: null, composed: false });
  if (uniqueSignals.length === 1) return Object.freeze({ signal: uniqueSignals[0], cleanup: null, composed: false });
  if (typeof AbortSignal === 'function' && typeof AbortSignal.any === 'function') {
    return Object.freeze({ signal: AbortSignal.any(uniqueSignals), cleanup: null, composed: true, nativeAny: true });
  }
  if (typeof AbortController !== 'function') return Object.freeze({ signal: uniqueSignals[0], cleanup: null, composed: false, degraded: true });
  const controller = new AbortController();
  const listeners = [];
  const abortFrom = (signal) => {
    if (controller.signal.aborted) return;
    try { controller.abort(guardedAbortReason(signal, new Error('BrowserRT guarded block-store abortSignal aborted'))); } catch { controller.abort(); }
  };
  for (const signal of uniqueSignals) {
    if (signal.aborted) { abortFrom(signal); continue; }
    const listener = () => abortFrom(signal);
    signal.addEventListener('abort', listener, { once: true });
    listeners.push([signal, listener]);
  }
  const cleanup = () => {
    for (const [signal, listener] of listeners.splice(0)) {
      try { signal.removeEventListener('abort', listener); } catch {}
    }
  };
  return Object.freeze({ signal: controller.signal, cleanup, composed: true, nativeAny: false });
}

function guardedAbortOptions(options = {}) {
  const out = { ...(options || {}) };
  const supplied = [];
  const signalSupplied = hasOwn(options, 'signal');
  const abortSignalSupplied = hasOwn(options, 'abortSignal');
  if (signalSupplied && options.signal !== null && options.signal !== undefined) supplied.push(options.signal);
  if (abortSignalSupplied && options.abortSignal !== null && options.abortSignal !== undefined) supplied.push(options.abortSignal);
  const invalid = supplied.filter((signal) => !isAbortSignalObject(signal));
  if (invalid.length > 0) {
    // Preserve the caller's invalid shape for WebLockCoordinator / provider validation; never mask it with a valid sibling signal.
    const lockSignal = signalSupplied && options.signal !== null && options.signal !== undefined ? options.signal : options.abortSignal;
    return Object.freeze({ providerOptions: out, lockSignal, cleanup: null, composed: false, invalidSignalPreserved: true, signalSupplied, abortSignalSupplied });
  }
  const composition = composeGuardedAbortSignals(supplied);
  if (composition.signal) {
    out.signal = composition.signal;
    out.abortSignal = composition.signal;
    if (composition.composed) {
      out.compositeAbortSignal = true;
      out.guardedAbortSignalComposed = true;
    }
  }
  if (composition.cleanup) Object.defineProperty(out, GUARDED_ABORT_CLEANUP, { value: composition.cleanup, enumerable: false });
  return Object.freeze({ providerOptions: out, lockSignal: composition.signal ?? (signalSupplied ? options.signal : abortSignalSupplied ? options.abortSignal : undefined), cleanup: composition.cleanup, composed: composition.composed === true, signalSupplied, abortSignalSupplied });
}

export class WebLockGuardedBlockStore {
  #closed = false;

  constructor({ store, coordinator = null, locks = undefined, lockName = null, lockPrefix = 'browserrt:opfs-block-store', label = null, trace = null, readMode = 'shared', requireWebLocks = true, lockTimeoutMs = 0, ownStore = undefined } = {}) {
    if (!store) throw new Error('WebLockGuardedBlockStore requires a store');
    this.store = store;
    this.ownStore = ownStore === undefined ? false : ownStore !== false;
    this.trace = trace;
    this.label = label || `${store.name || 'opfs-block-store'}-web-lock-guard`;
    this.lockTimeoutMs = normalizeLockTimeoutMs(lockTimeoutMs);
    this.coordinator = coordinator instanceof WebLockCoordinator ? coordinator : createWebLockCoordinator({ locks, prefix: lockPrefix, label: `${this.label}:coordinator`, trace, requireAvailable: requireWebLocks, defaultTimeoutMs: this.lockTimeoutMs });
    this.lockName = lockName || cleanLockNamePart(store.prefix || store.name || 'opfs-block-store');
    this.readMode = readMode === 'exclusive' ? 'exclusive' : 'shared';
    this.stats = { operations: 0, exclusiveOperations: 0, sharedOperations: 0, errors: 0, puts: 0, gets: 0, has: 0, deletes: 0, verifies: 0, estimates: 0, opens: 0, cleanupCalls: 0, stagedRecoveries: 0, abortSignalOperations: 0, compositeAbortSignals: 0, invalidAbortSignalsPreserved: 0, closeCalls: 0, closedOperationRejects: 0 };
    this.trace?.emit('storage:opfs-web-lock-guard-create', { label: this.label, store: this.name, provider: this.provider, lockName: this.fullLockName, available: this.available, readMode: this.readMode, lockTimeoutMs: this.lockTimeoutMs });
  }

  get name() { return this.store.name || this.label; }
  get provider() { return `web-lock-guarded:${this.store.provider || this.store.name || 'block-store'}`; }
  get prefix() { return this.store.prefix; }
  get available() { return this.coordinator.available; }
  get fullLockName() { return this.lockName.includes(':') ? this.lockName : this.coordinator.lockName(this.lockName); }
  get closed() { return this.#closed; }

  #throwIfClosed(op = 'operation') {
    if (!this.#closed) return;
    this.stats.closedOperationRejects += 1;
    const error = new Error(`WebLockGuardedBlockStore ${this.label} is closed`);
    error.name = 'BrowserRTWebLockGuardedBlockStoreError';
    error.code = 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED';
    error.detail = { label: this.label, op, lockName: this.fullLockName };
    this.trace?.emit('storage:opfs-web-lock-guard-closed-reject', error.detail);
    throw error;
  }

  async #run(op, mode, callback, options = {}) {
    this.#throwIfClosed(op);
    this.stats.operations += 1;
    if (mode === 'exclusive') this.stats.exclusiveOperations += 1;
    else this.stats.sharedOperations += 1;
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    const abortOptions = guardedAbortOptions(options);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.stats.abortSignalOperations += 1;
    if (abortOptions.composed) this.stats.compositeAbortSignals += 1;
    if (abortOptions.invalidSignalPreserved) this.stats.invalidAbortSignalsPreserved += 1;
    const metadata = { component: 'WebLockGuardedBlockStore', op, store: this.name, provider: this.provider, lockName: this.fullLockName, timeoutMs, hasSignal: abortOptions.signalSupplied, hasAbortSignal: abortOptions.abortSignalSupplied, compositeAbortSignal: abortOptions.composed === true, invalidAbortSignalPreserved: abortOptions.invalidSignalPreserved === true };
    this.trace?.emit('storage:opfs-web-lock-guard-op-start', metadata);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.trace?.emit('storage:opfs-web-lock-guard-abort-signal', metadata);
    this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-start`, metadata);
    try {
      const value = await this.coordinator.request(this.fullLockName, (lock) => callback(lock, abortOptions.providerOptions), { mode, metadata, timeoutMs, signal: abortOptions.lockSignal });
      this.trace?.emit('storage:opfs-web-lock-guard-op-complete', { ...metadata, ok: true });
      this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-end`, { ...metadata, ok: true });
      return value;
    } catch (error) {
      this.stats.errors += 1;
      this.trace?.emit('storage:opfs-web-lock-guard-op-error', { ...metadata, error: describeError(error) });
      this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-end`, { ...metadata, ok: false, error: describeError(error) });
      throw error;
    } finally {
      const cleanup = abortOptions.providerOptions?.[GUARDED_ABORT_CLEANUP] || abortOptions.cleanup;
      if (typeof cleanup === 'function') cleanup();
    }
  }

  async withExclusive(callback, metadata = {}, options = {}) {
    this.#throwIfClosed('custom-exclusive');
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    const abortOptions = guardedAbortOptions(options);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.stats.abortSignalOperations += 1;
    if (abortOptions.composed) this.stats.compositeAbortSignals += 1;
    if (abortOptions.invalidSignalPreserved) this.stats.invalidAbortSignalsPreserved += 1;
    try {
      return await this.coordinator.exclusive(this.fullLockName, callback, { metadata: { component: 'WebLockGuardedBlockStore', op: 'custom-exclusive', store: this.name, provider: this.provider, timeoutMs, hasSignal: abortOptions.signalSupplied, hasAbortSignal: abortOptions.abortSignalSupplied, compositeAbortSignal: abortOptions.composed === true, ...metadata }, timeoutMs, signal: abortOptions.lockSignal });
    } finally {
      const cleanup = abortOptions.providerOptions?.[GUARDED_ABORT_CLEANUP] || abortOptions.cleanup;
      if (typeof cleanup === 'function') cleanup();
    }
  }

  async withShared(callback, metadata = {}, options = {}) {
    this.#throwIfClosed('custom-shared');
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    const abortOptions = guardedAbortOptions(options);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.stats.abortSignalOperations += 1;
    if (abortOptions.composed) this.stats.compositeAbortSignals += 1;
    if (abortOptions.invalidSignalPreserved) this.stats.invalidAbortSignalsPreserved += 1;
    try {
      return await this.coordinator.shared(this.fullLockName, callback, { metadata: { component: 'WebLockGuardedBlockStore', op: 'custom-shared', store: this.name, provider: this.provider, timeoutMs, hasSignal: abortOptions.signalSupplied, hasAbortSignal: abortOptions.abortSignalSupplied, compositeAbortSignal: abortOptions.composed === true, ...metadata }, timeoutMs, signal: abortOptions.lockSignal });
    } finally {
      const cleanup = abortOptions.providerOptions?.[GUARDED_ABORT_CLEANUP] || abortOptions.cleanup;
      if (typeof cleanup === 'function') cleanup();
    }
  }

  async open() {
    this.stats.opens += 1;
    return await this.#run('open', 'exclusive', async () => await this.store.open());
  }

  async put(value, fields = {}, options = {}) {
    this.stats.puts += 1;
    return await this.#run('put', 'exclusive', async (_lock, providerOptions) => await this.store.put(value, fields, providerOptions), options);
  }

  async get(refOrDigest, options = {}) {
    this.stats.gets += 1;
    return await this.#run('get', this.readMode, async (_lock, providerOptions) => await this.store.get(refOrDigest, providerOptions), options);
  }

  async has(refOrDigest, options = {}) {
    this.stats.has += 1;
    return await this.#run('has', this.readMode, async (_lock, providerOptions) => await this.store.has(refOrDigest, providerOptions), options);
  }

  async delete(refOrDigest, options = {}) {
    this.stats.deletes += 1;
    return await this.#run('delete', 'exclusive', async (_lock, providerOptions) => await this.store.delete(refOrDigest, providerOptions), options);
  }

  async verify(refOrDigest, options = {}) {
    this.stats.verifies += 1;
    return await this.#run('verify', this.readMode, async (_lock, providerOptions) => await this.store.verify(refOrDigest, providerOptions), options);
  }

  async estimate(options = {}) {
    this.stats.estimates += 1;
    return await this.#run('estimate', this.readMode, async (_lock, providerOptions) => await this.store.estimate(providerOptions), options);
  }

  async cleanupForTest(options = {}) {
    this.stats.cleanupCalls += 1;
    if (typeof this.store.cleanupForTest !== 'function') throw new Error('guarded store cleanupForTest is unavailable');
    return await this.#run('cleanupForTest', 'exclusive', async (_lock, providerOptions) => await this.store.cleanupForTest(providerOptions), options);
  }

  async recoverStagedWrites(options = {}) {
    this.stats.stagedRecoveries += 1;
    if (typeof this.store.recoverStagedWrites !== 'function') throw new Error('guarded store recoverStagedWrites is unavailable');
    return await this.#run('recoverStagedWrites', 'exclusive', async (_lock, providerOptions) => await this.store.recoverStagedWrites(providerOptions), options);
  }

  async queryLocks() {
    this.#throwIfClosed('queryLocks');
    if (typeof this.coordinator.queryLocks !== 'function') {
      return Object.freeze({ available: false, name: this.fullLockName, held: [], pending: [], heldCount: null, pendingCount: null, raw: null, reason: 'queryLocks-unavailable' });
    }
    const result = await this.coordinator.queryLocks(this.fullLockName);
    this.trace?.emit('storage:opfs-web-lock-guard-query', { label: this.label, lockName: this.fullLockName, available: result.available, heldCount: result.heldCount, pendingCount: result.pendingCount });
    return result;
  }

  async waitForSettled({ timeoutMs = 1000, intervalMs = 25 } = {}) {
    this.#throwIfClosed('waitForSettled');
    if (typeof this.coordinator.waitForSettled !== 'function') {
      return Object.freeze({ ok: false, available: false, name: this.fullLockName, elapsedMs: 0, timeoutMs, last: null, reason: 'waitForSettled-unavailable' });
    }
    const result = await this.coordinator.waitForSettled(this.fullLockName, { timeoutMs, intervalMs });
    this.trace?.emit(result.ok ? 'storage:opfs-web-lock-guard-settled' : 'storage:opfs-web-lock-guard-still-contended', { label: this.label, lockName: this.fullLockName, ok: result.ok, elapsedMs: result.elapsedMs, timeoutMs, heldCount: result.last?.heldCount ?? null, pendingCount: result.last?.pendingCount ?? null, available: result.last?.available ?? null });
    return result;
  }

  close(reason = 'opfs-web-lock-guard-close') {
    void this.closeAsync({ reason });
    return this.snapshot();
  }

  async closeAsync({ reason = 'opfs-web-lock-guard-close' } = {}) {
    this.stats.closeCalls += 1;
    const wasClosed = this.#closed;
    this.#closed = true;
    let storeClose = null;
    if (!wasClosed && this.ownStore && this.store && typeof this.store.closeAsync === 'function') storeClose = await this.store.closeAsync({ reason });
    else if (!wasClosed && this.ownStore && this.store && typeof this.store.close === 'function') storeClose = this.store.close(reason);
    const report = Object.freeze({ disposition: wasClosed ? 'already-closed' : 'closed', label: this.label, name: this.name, provider: this.provider, lockName: this.fullLockName, ownStore: this.ownStore, storeClose, reason });
    this.trace?.emit('storage:opfs-web-lock-guard-close', { label: this.label, provider: this.provider, lockName: this.fullLockName, disposition: report.disposition, ownStore: this.ownStore, storeClosed: Boolean(storeClose), reason });
    return report;
  }

  snapshot() {
    return Object.freeze({ label: this.label, name: this.name, provider: this.provider, prefix: this.prefix ?? null, lockName: this.fullLockName, available: this.available, readMode: this.readMode, lockTimeoutMs: this.lockTimeoutMs, closed: this.#closed, ownStore: this.ownStore, stats: { ...this.stats }, coordinator: this.coordinator.snapshot(), store: typeof this.store.snapshot === 'function' ? this.store.snapshot() : null });
  }
}

export function createWebLockGuardedBlockStore(config = {}) {
  return new WebLockGuardedBlockStore(config);
}
