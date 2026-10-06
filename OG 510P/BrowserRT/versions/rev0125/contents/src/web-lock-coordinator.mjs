// BrowserRT Web Locks coordinator.
// Narrow helper around navigator.locks.request/query so mesh/storage code can
// prove actual browser coordination without baking raw Web Locks calls into
// every provider. This helper does not claim fairness, background lifecycle
// behavior, cross-browser conformance, or storage durability. Rev0106 only classifies external AbortSignal as lock-aborted before acquisition.

function coordinatorError(code, message, detail = {}) {
  const error = new Error(message);
  error.name = 'BrowserRTWebLockCoordinatorError';
  error.code = code;
  error.detail = detail;
  return error;
}

function defaultLocks() {
  return globalThis.navigator?.locks ?? null;
}

function cleanLockName(name) {
  if (typeof name !== 'string' || !name.trim()) throw coordinatorError('BRT_WEB_LOCK_NAME_INVALID', 'Web lock name must be a non-empty string', { actualType: name === null ? 'null' : typeof name });
  if (name.includes('\0')) throw coordinatorError('BRT_WEB_LOCK_NAME_INVALID', 'Web lock name must not contain NUL', { name });
  return name.trim();
}

function cleanMode(mode) {
  const normalized = mode === undefined || mode === null ? 'exclusive' : mode;
  if (normalized !== 'exclusive' && normalized !== 'shared') throw coordinatorError('BRT_WEB_LOCK_MODE_INVALID', `Unsupported Web Lock mode: ${normalized}`, { mode: normalized });
  return normalized;
}

function normalizeTimeoutMs(timeoutMs) {
  if (timeoutMs === undefined || timeoutMs === null || timeoutMs === false) return 0;
  const n = Number(timeoutMs);
  if (!Number.isFinite(n) || n < 0) throw coordinatorError('BRT_WEB_LOCK_TIMEOUT_INVALID', `Web lock timeoutMs must be a non-negative finite number: ${timeoutMs}`, { timeoutMs });
  return Math.floor(n);
}

function cleanOptionalBooleanOption(optionName, value, detail = {}) {
  if (value === undefined) return undefined;
  if (typeof value !== 'boolean') {
    throw coordinatorError('BRT_WEB_LOCK_OPTION_TYPE', `Web Lock option ${optionName} must be boolean when supplied`, { ...detail, option: optionName, actualType: value === null ? 'null' : typeof value, actualValue: value });
  }
  return value;
}

function cleanAbortSignalOption(signal, detail = {}) {
  if (signal === undefined || signal === null) return undefined;
  const looksLikeObject = signal !== null && (typeof signal === 'object' || typeof signal === 'function');
  const AbortSignalCtor = globalThis.AbortSignal;
  const sameRealmSignal = typeof AbortSignalCtor === 'function' ? signal instanceof AbortSignalCtor : true;
  const structuralSignal = looksLikeObject && typeof signal.aborted === 'boolean' && typeof signal.addEventListener === 'function' && typeof signal.removeEventListener === 'function';
  if (!sameRealmSignal || !structuralSignal) {
    throw coordinatorError('BRT_WEB_LOCK_SIGNAL_INVALID', 'Web Lock signal option must be an AbortSignal', { ...detail, actualType: signal === null ? 'null' : typeof signal });
  }
  return signal;
}

function validateLockOptionCombinations({ mode, ifAvailable, steal, signal, timeoutMs, detail = {} } = {}) {
  if (ifAvailable === true && steal === true) {
    throw coordinatorError('BRT_WEB_LOCK_OPTION_CONFLICT', 'Web Lock ifAvailable and steal cannot both be true in BrowserRT coordinator', { ...detail, mode, ifAvailable, steal, hasSignal: Boolean(signal), timeoutMs });
  }
  if (steal === true && mode !== 'exclusive') {
    throw coordinatorError('BRT_WEB_LOCK_OPTION_CONFLICT', 'Web Lock steal requires exclusive mode in BrowserRT coordinator', { ...detail, mode, ifAvailable, steal, hasSignal: Boolean(signal), timeoutMs });
  }
  if ((timeoutMs > 0 || signal) && (ifAvailable === true || steal === true)) {
    throw coordinatorError('BRT_WEB_LOCK_SIGNAL_OPTION_CONFLICT', 'Web Lock cancellation signal cannot be combined with ifAvailable or steal in BrowserRT coordinator', { ...detail, mode, timeoutMs, ifAvailable: ifAvailable === true, steal: steal === true, hasSignal: Boolean(signal) });
  }
}

function lockRequestOptions({ mode, ifAvailable, steal, signal } = {}) {
  const options = { mode: cleanMode(mode) };
  if (ifAvailable !== undefined) options.ifAvailable = ifAvailable;
  if (steal !== undefined) options.steal = steal;
  if (signal !== undefined) options.signal = signal;
  return options;
}

function serializeLock(lock) {
  if (!lock) return null;
  return { name: lock.name ?? null, mode: lock.mode ?? null };
}

function abortReason(signal) {
  try { return signal?.reason ?? null; } catch { return null; }
}

function makeAbortProxy({ signal = null, timeoutMs = 0, detail = {}, trace = null, traceBase = {} } = {}) {
  const normalizedTimeoutMs = normalizeTimeoutMs(timeoutMs);
  if (!signal && normalizedTimeoutMs <= 0) {
    return { signal: undefined, timeoutMs: 0, timedOut: false, externalAborted: false, markAcquired() {}, cleanup() {}, snapshot() { return { timeoutMs: 0, timedOut: false, externalAborted: false }; } };
  }
  if (typeof AbortController !== 'function') {
    throw coordinatorError('BRT_WEB_LOCK_ABORT_UNSUPPORTED', 'AbortController is unavailable for Web Lock cancellation', detail);
  }
  const controller = new AbortController();
  let timedOut = false;
  let externalAborted = false;
  let acquired = false;
  let timeoutId = null;
  const cleanupFns = [];
  const abort = (kind, reason) => {
    if (controller.signal.aborted) return;
    if (kind === 'timeout') timedOut = true;
    if (kind === 'external') externalAborted = true;
    try { controller.abort(reason); } catch { controller.abort(); }
  };
  if (signal) {
    if (signal.aborted) {
      abort('external', abortReason(signal));
    } else if (typeof signal.addEventListener === 'function') {
      const onAbort = () => abort('external', abortReason(signal));
      signal.addEventListener('abort', onAbort, { once: true });
      cleanupFns.push(() => { try { signal.removeEventListener('abort', onAbort); } catch {} });
    }
  }
  if (normalizedTimeoutMs > 0) {
    trace?.emit('coord:web-lock-timeout-arm', { ...traceBase, timeoutMs: normalizedTimeoutMs });
    timeoutId = setTimeout(() => {
      if (acquired || controller.signal.aborted) return;
      trace?.emit('coord:web-lock-timeout-fired', { ...traceBase, timeoutMs: normalizedTimeoutMs });
      abort('timeout', coordinatorError('BRT_WEB_LOCK_TIMEOUT', `Web Lock request timed out after ${normalizedTimeoutMs}ms`, { ...detail, timeoutMs: normalizedTimeoutMs }));
    }, normalizedTimeoutMs);
    cleanupFns.push(() => clearTimeout(timeoutId));
  }
  return {
    signal: controller.signal,
    timeoutMs: normalizedTimeoutMs,
    get timedOut() { return timedOut; },
    get externalAborted() { return externalAborted; },
    markAcquired() {
      acquired = true;
      if (timeoutId !== null) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
    },
    cleanup() {
      for (const fn of cleanupFns.splice(0)) fn();
    },
    snapshot() { return { timeoutMs: normalizedTimeoutMs, timedOut, externalAborted, acquired }; }
  };
}

export class WebLockCoordinator {
  constructor({ locks = defaultLocks(), prefix = 'browserrt', trace = null, label = 'web-lock-coordinator', requireAvailable = true, defaultTimeoutMs = 0 } = {}) {
    this.locks = locks;
    this.prefix = cleanLockName(prefix);
    this.label = label;
    this.requireAvailable = Boolean(requireAvailable);
    this.defaultTimeoutMs = normalizeTimeoutMs(defaultTimeoutMs);
    this.trace = trace;
    this.stats = { requests: 0, acquired: 0, released: 0, unavailable: 0, errors: 0, exclusiveRequests: 0, sharedRequests: 0, notAcquired: 0, queries: 0, queryLocks: 0, waitsForSettled: 0, waitSettledTimeouts: 0, timeouts: 0, aborted: 0, optionRejected: 0 };
    this.trace?.emit('coord:web-lock-coordinator-create', { label: this.label, prefix: this.prefix, available: this.available, defaultTimeoutMs: this.defaultTimeoutMs });
  }

  get available() {
    return typeof this.locks?.request === 'function';
  }

  lockName(name) {
    return `${this.prefix}:${cleanLockName(name)}`;
  }

  async request(name, callback, options = {}) {
    if (typeof callback !== 'function') throw new Error('WebLockCoordinator.request requires callback');
    let fullName = null;
    let mode = 'exclusive';
    let timeoutMs = 0;
    let metadata = null;
    let ifAvailable;
    let steal;
    let signal;
    try {
      const baseName = cleanLockName(name);
      fullName = cleanLockName(baseName.includes(':') ? baseName : this.lockName(baseName));
      mode = cleanMode(options.mode);
      timeoutMs = options.timeoutMs === undefined ? this.defaultTimeoutMs : normalizeTimeoutMs(options.timeoutMs);
      metadata = options.metadata || null;
      const detail = { label: this.label, name: fullName, mode, timeoutMs, metadata };
      ifAvailable = cleanOptionalBooleanOption('ifAvailable', options.ifAvailable, detail);
      steal = cleanOptionalBooleanOption('steal', options.steal, detail);
      signal = cleanAbortSignalOption(options.signal, detail);
      validateLockOptionCombinations({ mode, ifAvailable, steal, signal, timeoutMs, detail });
    } catch (error) {
      if (error?.name === 'BrowserRTWebLockCoordinatorError') {
        this.stats.optionRejected += 1;
        this.stats.errors += 1;
        this.trace?.emit('coord:web-lock-option-rejected', { label: this.label, name: fullName, mode, timeoutMs, metadata, error: { name: error.name, message: error.message, code: error.code ?? null, detail: error.detail ?? null } });
      }
      throw error;
    }
    const traceBase = { label: this.label, name: fullName, mode, timeoutMs, metadata };
    const abortProxy = makeAbortProxy({ signal, timeoutMs, detail: traceBase, trace: this.trace, traceBase });
    const requestOptions = lockRequestOptions({ mode, ifAvailable, steal, signal: abortProxy.signal });
    this.stats.requests += 1;
    if (mode === 'exclusive') this.stats.exclusiveRequests += 1;
    else this.stats.sharedRequests += 1;
    this.trace?.emit('coord:web-lock-request', { label: this.label, name: fullName, mode, ifAvailable: requestOptions.ifAvailable === true, steal: requestOptions.steal === true, timeoutMs, hasSignal: Boolean(requestOptions.signal), metadata });
    if (!this.available) {
      abortProxy.cleanup();
      this.stats.unavailable += 1;
      this.trace?.emit('coord:web-lock-unavailable', { label: this.label, name: fullName, mode, timeoutMs, metadata });
      if (this.requireAvailable) throw coordinatorError('BRT_WEB_LOCKS_UNAVAILABLE', 'navigator.locks.request is unavailable', { label: this.label, name: fullName, mode, timeoutMs, metadata });
      return await callback(null);
    }
    try {
      return await this.locks.request(fullName, requestOptions, async (lock) => {
        abortProxy.markAcquired();
        if (!lock) {
          this.stats.notAcquired += 1;
          this.trace?.emit('coord:web-lock-not-acquired', { label: this.label, name: fullName, mode, timeoutMs, metadata });
          return await callback(null);
        }
        this.stats.acquired += 1;
        this.trace?.emit('coord:web-lock-acquired', { label: this.label, name: fullName, mode, timeoutMs, lock: serializeLock(lock), metadata });
        try {
          return await callback(lock);
        } finally {
          this.stats.released += 1;
          this.trace?.emit('coord:web-lock-release', { label: this.label, name: fullName, mode, timeoutMs, lock: serializeLock(lock), metadata });
          this.trace?.emit('coord:web-lock-released', { label: this.label, name: fullName, mode, timeoutMs, lock: serializeLock(lock), metadata });
        }
      });
    } catch (error) {
      const abortState = abortProxy.snapshot();
      if (abortState.timedOut) {
        this.stats.timeouts += 1;
        this.stats.errors += 1;
        const wrapped = coordinatorError('BRT_WEB_LOCK_TIMEOUT', `Web Lock request timed out after ${timeoutMs}ms`, { label: this.label, name: fullName, mode, timeoutMs, metadata, causeName: error?.name || 'Error', causeMessage: error?.message || String(error) });
        this.trace?.emit('coord:web-lock-timeout', { label: this.label, name: fullName, mode, timeoutMs, metadata, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null } });
        throw wrapped;
      }
      if ((abortState.externalAborted || (error?.name === 'AbortError' && options.signal?.aborted)) && !abortState.acquired) {
        this.stats.aborted += 1;
        this.stats.errors += 1;
        const wrapped = coordinatorError('BRT_WEB_LOCK_ABORTED', 'Web Lock request aborted before acquisition', { label: this.label, name: fullName, mode, timeoutMs, metadata, causeName: error?.name || 'Error', causeMessage: error?.message || String(error), acquired: abortState.acquired === true });
        this.trace?.emit('coord:web-lock-aborted', { label: this.label, name: fullName, mode, timeoutMs, metadata, acquired: abortState.acquired === true, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null } });
        throw wrapped;
      }
      this.stats.errors += 1;
      this.trace?.emit('coord:web-lock-error', { label: this.label, name: fullName, mode, timeoutMs, metadata, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null } });
      throw error;
    } finally {
      abortProxy.cleanup();
    }
  }

  async exclusive(name, callback, options = {}) {
    return await this.request(name, callback, { ...options, mode: 'exclusive' });
  }

  async shared(name, callback, options = {}) {
    return await this.request(name, callback, { ...options, mode: 'shared' });
  }

  async query() {
    if (typeof this.locks?.query !== 'function') return null;
    this.stats.queries += 1;
    const result = await this.locks.query();
    this.trace?.emit('coord:web-lock-query', { label: this.label, heldCount: result?.held?.length ?? null, pendingCount: result?.pending?.length ?? null });
    return result;
  }

  normalizeQueryResult(result, name = null) {
    const fullName = name ? cleanLockName(String(name).includes(':') ? String(name) : this.lockName(String(name))) : null;
    const held = Array.isArray(result?.held) ? result.held : [];
    const pending = Array.isArray(result?.pending) ? result.pending : [];
    const keep = (row) => !fullName || row?.name === fullName;
    return Object.freeze({
      name: fullName,
      held: held.filter(keep).map((row) => ({ name: row.name ?? null, mode: row.mode ?? null, clientId: row.clientId ?? null })),
      pending: pending.filter(keep).map((row) => ({ name: row.name ?? null, mode: row.mode ?? null, clientId: row.clientId ?? null }))
    });
  }

  async queryLocks(name = null) {
    this.stats.queryLocks += 1;
    const raw = await this.query();
    if (!raw) {
      const unavailable = Object.freeze({ available: false, name: name ? cleanLockName(String(name).includes(':') ? String(name) : this.lockName(String(name))) : null, held: [], pending: [], heldCount: null, pendingCount: null, raw: null });
      this.trace?.emit('coord:web-lock-query-normalized', { label: this.label, available: false, name: unavailable.name, heldCount: null, pendingCount: null });
      return unavailable;
    }
    const normalized = this.normalizeQueryResult(raw, name);
    const result = Object.freeze({ available: true, name: normalized.name, held: normalized.held, pending: normalized.pending, heldCount: normalized.held.length, pendingCount: normalized.pending.length, raw });
    this.trace?.emit('coord:web-lock-query-normalized', { label: this.label, available: true, name: result.name, heldCount: result.heldCount, pendingCount: result.pendingCount });
    return result;
  }

  async waitForSettled(name = null, { timeoutMs = 1000, intervalMs = 25 } = {}) {
    this.stats.waitsForSettled += 1;
    const startedAt = Date.now();
    const deadline = startedAt + Math.max(0, timeoutMs);
    const fullName = name ? cleanLockName(String(name).includes(':') ? String(name) : this.lockName(String(name))) : null;
    this.trace?.emit('coord:web-lock-wait-settled-start', { label: this.label, name: fullName, timeoutMs, intervalMs });
    let last = await this.queryLocks(fullName);
    while (last.available && (last.heldCount > 0 || last.pendingCount > 0) && Date.now() < deadline) {
      await new Promise((resolve) => setTimeout(resolve, Math.max(1, intervalMs)));
      last = await this.queryLocks(fullName);
    }
    const elapsedMs = Date.now() - startedAt;
    const ok = Boolean(last.available && last.heldCount === 0 && last.pendingCount === 0);
    if (!ok) this.stats.waitSettledTimeouts += 1;
    const result = Object.freeze({ ok, elapsedMs, timeoutMs, name: fullName, last });
    this.trace?.emit(ok ? 'coord:web-lock-wait-settled-complete' : 'coord:web-lock-wait-settled-timeout', { label: this.label, name: fullName, elapsedMs, timeoutMs, heldCount: last.heldCount, pendingCount: last.pendingCount, available: last.available });
    return result;
  }

  snapshot() {
    return Object.freeze({ label: this.label, prefix: this.prefix, available: this.available, requireAvailable: this.requireAvailable, defaultTimeoutMs: this.defaultTimeoutMs, stats: { ...this.stats } });
  }
}

export function createWebLockCoordinator(config = {}) {
  return new WebLockCoordinator(config);
}
