// Rev0106 composes signal/abortSignal for direct guarded lock acquisition and provider calls.
import { createWebLockCoordinator, WebLockCoordinator } from './web-lock-coordinator.mjs';
import { attachBrowserStorageRecoveryGuidance, createBrowserStorageRecoveryGuidance } from './browser-storage-recovery-guidance.mjs';
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
function makeGuardedError(code, message, detail = {}) {
  const error = new Error(message);
  error.name = 'BrowserRTWebLockGuardedBlockStoreError';
  error.code = code;
  error.detail = detail;
  return error;
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
function guardedAbortOptions(options = {}, extraSignals = []) {
  const out = { ...(options || {}) };
  const supplied = [];
  const signalSupplied = hasOwn(options, 'signal');
  const abortSignalSupplied = hasOwn(options, 'abortSignal');
  if (signalSupplied && options.signal !== null && options.signal !== undefined) supplied.push(options.signal);
  if (abortSignalSupplied && options.abortSignal !== null && options.abortSignal !== undefined) supplied.push(options.abortSignal);
  for (const signal of extraSignals || []) if (signal !== null && signal !== undefined) supplied.push(signal);
  const invalid = supplied.filter((signal) => !isAbortSignalObject(signal));
  if (invalid.length > 0) {
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
  #closeController = typeof AbortController === 'function' ? new AbortController() : null;
  constructor({ store, coordinator = null, locks = undefined, lockName = null, lockPrefix = 'browserrt:opfs-block-store', label = null, trace = null, readMode = 'shared', requireWebLocks = true, lockTimeoutMs = 0, ownStore = undefined, allowUnboundedLockTimeoutOverride = true } = {}) {
    if (!store) throw new Error('WebLockGuardedBlockStore requires a store');
    this.store = store;
    this.ownStore = ownStore === undefined ? false : ownStore !== false;
    this.trace = trace;
    this.label = label || `${store.name || 'opfs-block-store'}-web-lock-guard`;
    this.lockTimeoutMs = normalizeLockTimeoutMs(lockTimeoutMs);
    this.allowUnboundedLockTimeoutOverride = allowUnboundedLockTimeoutOverride !== false;
    this.coordinator = coordinator instanceof WebLockCoordinator ? coordinator : createWebLockCoordinator({ locks, prefix: lockPrefix, label: `${this.label}:coordinator`, trace, requireAvailable: requireWebLocks, defaultTimeoutMs: this.lockTimeoutMs });
    this.lockName = lockName || cleanLockNamePart(store.prefix || store.name || 'opfs-block-store');
    this.readMode = readMode === 'exclusive' ? 'exclusive' : 'shared';
    this.stats = { operations: 0, exclusiveOperations: 0, sharedOperations: 0, errors: 0, puts: 0, gets: 0, has: 0, deletes: 0, verifies: 0, estimates: 0, opens: 0, cleanupCalls: 0, stagedRecoveries: 0, abortSignalOperations: 0, compositeAbortSignals: 0, invalidAbortSignalsPreserved: 0, lockTimeoutOverrideRejects: 0, closeCalls: 0, closeAbortSignals: 0, closedOperationRejects: 0 };
    this.trace?.emit('storage:opfs-web-lock-guard-create', { label: this.label, store: this.name, provider: this.provider, lockName: this.fullLockName, available: this.available, readMode: this.readMode, lockTimeoutMs: this.lockTimeoutMs, allowUnboundedLockTimeoutOverride: this.allowUnboundedLockTimeoutOverride });
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
    this.stats.errors += 1;
    const error = new Error(`WebLockGuardedBlockStore ${this.label} is closed`);
    error.name = 'BrowserRTWebLockGuardedBlockStoreError';
    error.code = 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED';
    const context = { label: this.label, op, store: this.name, provider: this.provider, lockName: this.fullLockName };
    error.detail = context;
    attachBrowserStorageRecoveryGuidance(error, context);
    const recovery = error.browserStorageRecovery || error.detail?.recovery || null;
    this.trace?.emit('storage:opfs-web-lock-guard-closed-reject', { ...context, error: describeError(error), recovery });
    this.trace?.emit('storage:opfs-web-lock-guard-recovery-guidance', { ...context, recovery });
    throw error;
  }

  #assertBoundedLockTimeoutOverride(op = 'operation', options = {}) {
    if (this.allowUnboundedLockTimeoutOverride !== false || !hasOwn(options, 'timeoutMs')) return;
    const proposedTimeoutMs = normalizeLockTimeoutMs(options.timeoutMs);
    if (proposedTimeoutMs > 0) return;
    this.stats.lockTimeoutOverrideRejects += 1;
    this.stats.errors += 1;
    const message = 'Postured Web-Lock-guarded block store rejected unbounded per-operation lock timeout override';
    const detail = { label: this.label, op, store: this.name, provider: this.provider, lockName: this.fullLockName, defaultTimeoutMs: this.lockTimeoutMs, proposedTimeoutMs, allowUnboundedLockTimeoutOverride: false, overrideRejected: true, preMutationRejected: true };
    detail.recovery = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTWebLockGuardedBlockStoreError', code: 'BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED', message, detail }, { op, phase: 'lock-timeout-override', lockName: this.fullLockName, timeoutMs: this.lockTimeoutMs });
    this.trace?.emit('storage:opfs-web-lock-guard-timeout-override-rejected', detail);
    throw makeGuardedError('BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED', message, detail);
  }

  async #run(op, mode, callback, options = {}) {
    this.#throwIfClosed(op);
    this.stats.operations += 1;
    if (mode === 'exclusive') this.stats.exclusiveOperations += 1;
    else this.stats.sharedOperations += 1;
    this.#assertBoundedLockTimeoutOverride(op, options);
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    const abortOptions = guardedAbortOptions(options, [this.#closeController?.signal]);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.stats.abortSignalOperations += 1;
    if (abortOptions.composed) this.stats.compositeAbortSignals += 1;
    if (abortOptions.invalidSignalPreserved) this.stats.invalidAbortSignalsPreserved += 1;
    const metadata = { component: 'WebLockGuardedBlockStore', op, store: this.name, provider: this.provider, lockName: this.fullLockName, timeoutMs, hasSignal: abortOptions.signalSupplied, hasAbortSignal: abortOptions.abortSignalSupplied, compositeAbortSignal: abortOptions.composed === true, invalidAbortSignalPreserved: abortOptions.invalidSignalPreserved === true };
    this.trace?.emit('storage:opfs-web-lock-guard-op-start', metadata);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.trace?.emit('storage:opfs-web-lock-guard-abort-signal', metadata);
    this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-start`, metadata);
    try {
      const value = await this.coordinator.request(this.fullLockName, (lock) => { this.#throwIfClosed(op); return callback(lock, abortOptions.providerOptions); }, { mode, metadata, timeoutMs, signal: abortOptions.lockSignal });
      this.trace?.emit('storage:opfs-web-lock-guard-op-complete', { ...metadata, ok: true });
      this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-end`, { ...metadata, ok: true });
      return value;
    } catch (error) {
      this.stats.errors += 1;
      const recovery = createBrowserStorageRecoveryGuidance(error, { op, mode, store: this.name, provider: this.provider, lockName: this.fullLockName, timeoutMs });
      attachBrowserStorageRecoveryGuidance(error, { op, mode, store: this.name, provider: this.provider, lockName: this.fullLockName, timeoutMs });
      this.trace?.emit('storage:opfs-web-lock-guard-op-error', { ...metadata, error: describeError(error), recovery });
      this.trace?.emit('storage:opfs-web-lock-guard-recovery-guidance', { ...metadata, recovery });
      this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-end`, { ...metadata, ok: false, error: describeError(error), recovery });
      throw error;
    } finally {
      const cleanup = abortOptions.providerOptions?.[GUARDED_ABORT_CLEANUP] || abortOptions.cleanup;
      if (typeof cleanup === 'function') cleanup();
    }
  }
  #customLockError(op, mode, metadata, error) {
    this.stats.errors += 1;
    const recoveryContext = {
      op,
      mode,
      store: this.name,
      provider: this.provider,
      lockName: this.fullLockName,
      timeoutMs: metadata.timeoutMs,
      hasSignal: metadata.hasSignal === true,
      hasAbortSignal: metadata.hasAbortSignal === true
    };
    const recovery = createBrowserStorageRecoveryGuidance(error, recoveryContext);
    attachBrowserStorageRecoveryGuidance(error, recoveryContext);
    this.trace?.emit('storage:opfs-web-lock-guard-custom-error', { ...metadata, error: describeError(error), recovery });
    this.trace?.emit('storage:opfs-web-lock-guard-recovery-guidance', { ...metadata, recovery });
    this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-end`, { ...metadata, ok: false, error: describeError(error), recovery });
  }
  async withExclusive(callback, metadata = {}, options = {}) {
    this.#throwIfClosed('custom-exclusive');
    this.stats.operations += 1;
    this.stats.exclusiveOperations += 1;
    this.#assertBoundedLockTimeoutOverride('custom-exclusive', options);
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    const abortOptions = guardedAbortOptions(options, [this.#closeController?.signal]);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.stats.abortSignalOperations += 1;
    if (abortOptions.composed) this.stats.compositeAbortSignals += 1;
    if (abortOptions.invalidSignalPreserved) this.stats.invalidAbortSignalsPreserved += 1;
    const op = 'custom-exclusive';
    const traceMetadata = { component: 'WebLockGuardedBlockStore', op, store: this.name, provider: this.provider, lockName: this.fullLockName, timeoutMs, hasSignal: abortOptions.signalSupplied, hasAbortSignal: abortOptions.abortSignalSupplied, compositeAbortSignal: abortOptions.composed === true, invalidAbortSignalPreserved: abortOptions.invalidSignalPreserved === true, ...metadata };
    this.trace?.emit('storage:opfs-web-lock-guard-op-start', traceMetadata);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.trace?.emit('storage:opfs-web-lock-guard-abort-signal', traceMetadata);
    this.trace?.emit('storage:opfs-web-lock-guard-exclusive-start', traceMetadata);
    try {
      const value = await this.coordinator.exclusive(this.fullLockName, (lock) => { this.#throwIfClosed(op); return callback(lock); }, { metadata: traceMetadata, timeoutMs, signal: abortOptions.lockSignal });
      this.trace?.emit('storage:opfs-web-lock-guard-op-complete', { ...traceMetadata, ok: true });
      this.trace?.emit('storage:opfs-web-lock-guard-exclusive-end', { ...traceMetadata, ok: true });
      return value;
    } catch (error) {
      this.#customLockError(op, 'exclusive', traceMetadata, error);
      throw error;
    } finally {
      const cleanup = abortOptions.providerOptions?.[GUARDED_ABORT_CLEANUP] || abortOptions.cleanup;
      if (typeof cleanup === 'function') cleanup();
    }
  }
  async withShared(callback, metadata = {}, options = {}) {
    this.#throwIfClosed('custom-shared');
    this.stats.operations += 1;
    this.stats.sharedOperations += 1;
    this.#assertBoundedLockTimeoutOverride('custom-shared', options);
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    const abortOptions = guardedAbortOptions(options, [this.#closeController?.signal]);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.stats.abortSignalOperations += 1;
    if (abortOptions.composed) this.stats.compositeAbortSignals += 1;
    if (abortOptions.invalidSignalPreserved) this.stats.invalidAbortSignalsPreserved += 1;
    const op = 'custom-shared';
    const traceMetadata = { component: 'WebLockGuardedBlockStore', op, store: this.name, provider: this.provider, lockName: this.fullLockName, timeoutMs, hasSignal: abortOptions.signalSupplied, hasAbortSignal: abortOptions.abortSignalSupplied, compositeAbortSignal: abortOptions.composed === true, invalidAbortSignalPreserved: abortOptions.invalidSignalPreserved === true, ...metadata };
    this.trace?.emit('storage:opfs-web-lock-guard-op-start', traceMetadata);
    if (abortOptions.signalSupplied || abortOptions.abortSignalSupplied) this.trace?.emit('storage:opfs-web-lock-guard-abort-signal', traceMetadata);
    this.trace?.emit('storage:opfs-web-lock-guard-shared-start', traceMetadata);
    try {
      const value = await this.coordinator.shared(this.fullLockName, (lock) => { this.#throwIfClosed(op); return callback(lock); }, { metadata: traceMetadata, timeoutMs, signal: abortOptions.lockSignal });
      this.trace?.emit('storage:opfs-web-lock-guard-op-complete', { ...traceMetadata, ok: true });
      this.trace?.emit('storage:opfs-web-lock-guard-shared-end', { ...traceMetadata, ok: true });
      return value;
    } catch (error) {
      this.#customLockError(op, 'shared', traceMetadata, error);
      throw error;
    } finally {
      const cleanup = abortOptions.providerOptions?.[GUARDED_ABORT_CLEANUP] || abortOptions.cleanup;
      if (typeof cleanup === 'function') cleanup();
    }
  }
  async open(options = {}) {
    this.stats.opens += 1;
    return await this.#run('open', 'exclusive', async (_lock, providerOptions) => await this.store.open(providerOptions), options);
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
    let closeAbortReason = null;
    if (!wasClosed && this.#closeController && !this.#closeController.signal.aborted) {
      closeAbortReason = makeGuardedError('BRT_OPFS_WEB_LOCK_GUARD_CLOSED', `WebLockGuardedBlockStore ${this.label} closed`, { label: this.label, store: this.name, provider: this.provider, lockName: this.fullLockName, reason });
      try { this.#closeController.abort(closeAbortReason); } catch { this.#closeController.abort(); }
      this.stats.closeAbortSignals += 1;
    }
    let storeClose = null;
    if (!wasClosed && this.ownStore && this.store && typeof this.store.closeAsync === 'function') storeClose = await this.store.closeAsync({ reason });
    else if (!wasClosed && this.ownStore && this.store && typeof this.store.close === 'function') storeClose = this.store.close(reason);
    const report = Object.freeze({ disposition: wasClosed ? 'already-closed' : 'closed', label: this.label, name: this.name, provider: this.provider, lockName: this.fullLockName, ownStore: this.ownStore, storeClose, closeSignalAborted: this.#closeController?.signal?.aborted === true, closeAbortReason: closeAbortReason ? describeError(closeAbortReason) : null, reason });
    this.trace?.emit('storage:opfs-web-lock-guard-close', { label: this.label, provider: this.provider, lockName: this.fullLockName, disposition: report.disposition, ownStore: this.ownStore, storeClosed: Boolean(storeClose), closeSignalAborted: report.closeSignalAborted, reason });
    return report;
  }
  snapshot() {
    return Object.freeze({ label: this.label, name: this.name, provider: this.provider, prefix: this.prefix ?? null, lockName: this.fullLockName, available: this.available, readMode: this.readMode, lockTimeoutMs: this.lockTimeoutMs, allowUnboundedLockTimeoutOverride: this.allowUnboundedLockTimeoutOverride, closed: this.#closed, closeSignalAborted: this.#closeController?.signal?.aborted === true, ownStore: this.ownStore, stats: { ...this.stats }, coordinator: this.coordinator.snapshot(), store: typeof this.store.snapshot === 'function' ? this.store.snapshot() : null });
  }
}
export function createWebLockGuardedBlockStore(config = {}) {
  return new WebLockGuardedBlockStore(config);
}
