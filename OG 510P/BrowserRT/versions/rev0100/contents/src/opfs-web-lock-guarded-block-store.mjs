// BrowserRT Web-Lock-guarded block-store wrapper.
// This wrapper serializes mutating provider calls through one same-origin Web
// Lock and routes read-like calls through shared locks where supported. It is a
// coordination boundary only: no OPFS durability, fsync, eviction, quota, crash,
// Trace event aliases include storage:opfs-web-lock-guard-exclusive-start and storage:opfs-web-lock-guard-shared-end for auditability.
// fairness, or cross-browser claim is implied.

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

export class WebLockGuardedBlockStore {
  constructor({ store, coordinator = null, locks = undefined, lockName = null, lockPrefix = 'browserrt:opfs-block-store', label = null, trace = null, readMode = 'shared', requireWebLocks = true, lockTimeoutMs = 0 } = {}) {
    if (!store) throw new Error('WebLockGuardedBlockStore requires a store');
    this.store = store;
    this.trace = trace;
    this.label = label || `${store.name || 'opfs-block-store'}-web-lock-guard`;
    this.lockTimeoutMs = normalizeLockTimeoutMs(lockTimeoutMs);
    this.coordinator = coordinator instanceof WebLockCoordinator ? coordinator : createWebLockCoordinator({ locks, prefix: lockPrefix, label: `${this.label}:coordinator`, trace, requireAvailable: requireWebLocks, defaultTimeoutMs: this.lockTimeoutMs });
    this.lockName = lockName || cleanLockNamePart(store.prefix || store.name || 'opfs-block-store');
    this.readMode = readMode === 'exclusive' ? 'exclusive' : 'shared';
    this.stats = { operations: 0, exclusiveOperations: 0, sharedOperations: 0, errors: 0, puts: 0, gets: 0, has: 0, deletes: 0, verifies: 0, estimates: 0, opens: 0, cleanupCalls: 0 };
    this.trace?.emit('storage:opfs-web-lock-guard-create', { label: this.label, store: this.name, provider: this.provider, lockName: this.fullLockName, available: this.available, readMode: this.readMode, lockTimeoutMs: this.lockTimeoutMs });
  }

  get name() { return this.store.name || this.label; }
  get provider() { return `web-lock-guarded:${this.store.provider || this.store.name || 'block-store'}`; }
  get prefix() { return this.store.prefix; }
  get available() { return this.coordinator.available; }
  get fullLockName() { return this.lockName.includes(':') ? this.lockName : this.coordinator.lockName(this.lockName); }

  async #run(op, mode, callback, options = {}) {
    this.stats.operations += 1;
    if (mode === 'exclusive') this.stats.exclusiveOperations += 1;
    else this.stats.sharedOperations += 1;
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    const metadata = { component: 'WebLockGuardedBlockStore', op, store: this.name, provider: this.provider, lockName: this.fullLockName, timeoutMs };
    this.trace?.emit('storage:opfs-web-lock-guard-op-start', metadata);
    this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-start`, metadata);
    try {
      const value = await this.coordinator.request(this.fullLockName, callback, { mode, metadata, timeoutMs, signal: options.signal });
      this.trace?.emit('storage:opfs-web-lock-guard-op-complete', { ...metadata, ok: true });
      this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-end`, { ...metadata, ok: true });
      return value;
    } catch (error) {
      this.stats.errors += 1;
      this.trace?.emit('storage:opfs-web-lock-guard-op-error', { ...metadata, error: describeError(error) });
      this.trace?.emit(`storage:opfs-web-lock-guard-${mode}-end`, { ...metadata, ok: false, error: describeError(error) });
      throw error;
    }
  }

  async withExclusive(callback, metadata = {}, options = {}) {
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    return await this.coordinator.exclusive(this.fullLockName, callback, { metadata: { component: 'WebLockGuardedBlockStore', op: 'custom-exclusive', store: this.name, provider: this.provider, timeoutMs, ...metadata }, timeoutMs, signal: options.signal });
  }

  async withShared(callback, metadata = {}, options = {}) {
    const timeoutMs = options.timeoutMs === undefined ? this.lockTimeoutMs : normalizeLockTimeoutMs(options.timeoutMs);
    return await this.coordinator.shared(this.fullLockName, callback, { metadata: { component: 'WebLockGuardedBlockStore', op: 'custom-shared', store: this.name, provider: this.provider, timeoutMs, ...metadata }, timeoutMs, signal: options.signal });
  }

  async open() {
    this.stats.opens += 1;
    return await this.#run('open', 'exclusive', async () => await this.store.open());
  }

  async put(value, fields = {}, options = {}) {
    this.stats.puts += 1;
    return await this.#run('put', 'exclusive', async () => await this.store.put(value, fields, options), options);
  }

  async get(refOrDigest, options = {}) {
    this.stats.gets += 1;
    return await this.#run('get', this.readMode, async () => await this.store.get(refOrDigest, options), options);
  }

  async has(refOrDigest, options = {}) {
    this.stats.has += 1;
    return await this.#run('has', this.readMode, async () => await this.store.has(refOrDigest, options), options);
  }

  async delete(refOrDigest, options = {}) {
    this.stats.deletes += 1;
    return await this.#run('delete', 'exclusive', async () => await this.store.delete(refOrDigest, options), options);
  }

  async verify(refOrDigest, options = {}) {
    this.stats.verifies += 1;
    return await this.#run('verify', this.readMode, async () => await this.store.verify(refOrDigest, options), options);
  }

  async estimate(options = {}) {
    this.stats.estimates += 1;
    return await this.#run('estimate', this.readMode, async () => await this.store.estimate(options), options);
  }

  async cleanupForTest(options = {}) {
    this.stats.cleanupCalls += 1;
    if (typeof this.store.cleanupForTest !== 'function') throw new Error('guarded store cleanupForTest is unavailable');
    return await this.#run('cleanupForTest', 'exclusive', async () => await this.store.cleanupForTest(options), options);
  }

  async queryLocks() {
    if (typeof this.coordinator.queryLocks !== 'function') {
      return Object.freeze({ available: false, name: this.fullLockName, held: [], pending: [], heldCount: null, pendingCount: null, raw: null, reason: 'queryLocks-unavailable' });
    }
    const result = await this.coordinator.queryLocks(this.fullLockName);
    this.trace?.emit('storage:opfs-web-lock-guard-query', { label: this.label, lockName: this.fullLockName, available: result.available, heldCount: result.heldCount, pendingCount: result.pendingCount });
    return result;
  }

  async waitForSettled({ timeoutMs = 1000, intervalMs = 25 } = {}) {
    if (typeof this.coordinator.waitForSettled !== 'function') {
      return Object.freeze({ ok: false, available: false, name: this.fullLockName, elapsedMs: 0, timeoutMs, last: null, reason: 'waitForSettled-unavailable' });
    }
    const result = await this.coordinator.waitForSettled(this.fullLockName, { timeoutMs, intervalMs });
    this.trace?.emit(result.ok ? 'storage:opfs-web-lock-guard-settled' : 'storage:opfs-web-lock-guard-still-contended', { label: this.label, lockName: this.fullLockName, ok: result.ok, elapsedMs: result.elapsedMs, timeoutMs, heldCount: result.last?.heldCount ?? null, pendingCount: result.last?.pendingCount ?? null, available: result.last?.available ?? null });
    return result;
  }

  snapshot() {
    return Object.freeze({ label: this.label, name: this.name, provider: this.provider, prefix: this.prefix ?? null, lockName: this.fullLockName, available: this.available, readMode: this.readMode, lockTimeoutMs: this.lockTimeoutMs, stats: { ...this.stats }, coordinator: this.coordinator.snapshot(), store: typeof this.store.snapshot === 'function' ? this.store.snapshot() : null });
  }
}

export function createWebLockGuardedBlockStore(config = {}) {
  return new WebLockGuardedBlockStore(config);
}
