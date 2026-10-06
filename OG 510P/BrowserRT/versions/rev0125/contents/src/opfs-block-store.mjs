// BrowserRT OPFS async block-store provider.
// This is intentionally a narrow async browser-window provider proof surface:
// content-addressed put/get/has/delete/verify using navigator.storage.getDirectory().
// Rev0057 adds quota/error classification for writes so browser quota failures are explicit artifacts instead of opaque DOMException strings.
// Rev0058 adds best-effort rollback of failed writes so content-addressed failed puts do not leave partial block files behind.
// Rev0059 adds an abrupt-kill browser proof around acknowledged writes plus one intentionally unclosed stream candidate.
// Rev0061 verifies existing content-addressed files before dedupe and repairs corrupt final-hash files before acknowledging a put.
// Rev0095 honors explicit caller AbortSignal/abortSignal options at provider checkpoints and rolls back aborted puts.
// Rev0096 adds an opt-in StorageManager.estimate() write-budget preflight guard before OPFS file mutation.
// Rev0097 makes failed-put rollback ownership-aware so duplicate/idempotent puts cannot delete pre-existing valid blocks.
// Rev0098 resets a failed cached OPFS open promise so transient root/prefix open failures do not permanently poison the provider.
// Rev0099 makes the write-budget guard duplicate-aware: verified no-op duplicate puts bypass budget checks,
// while new writes and corrupt-block repairs still check budget before OPFS mutation.
// Rev0100 preserves already-valid content-addressed final blocks during failed-put rollback instead of deleting
// valid bytes after late abort/observer failure; invalid or missing owned files are still best-effort removed.
// Rev0101 keeps read-only miss paths no-create: get/has/verify and delete misses no longer create empty
// OPFS prefix/bucket directories just to discover NotFound.
// Rev0107 composes raw provider signal and abortSignal options so direct OPFS calls do not
// silently ignore one caller-owned abort source when both are supplied.
// Rev0121 makes closeAsync an aborting lifecycle fence for in-flight operations
// and lets rollback clean up owned partial writes even after the store is closed.
// Rev0122 stages new puts in a same-bucket temporary block, verifies the staged bytes,
// publishes the final content-addressed path only after staging succeeds, and cleans staged files on success/failure.
// Rev0123 adds an explicit staged-temp recovery sweep for abandoned same-bucket temp files
// while preserving canonical .blk blocks and rejecting staged names outside the expected digest bucket.
// Rev0124 makes staged temp names provider-instance unique and makes same-runtime recovery skip
// active staged writes so recovery cannot self-sabotage an in-flight put.
// It does not claim fsync durability, organic eviction behavior, general crash recovery, multi-tab safety, or sync-handle behavior.

const DEFAULT_PROVIDER = 'opfs-async-block-store-v0';

function storageError(code, message, detail = {}) {
  const error = new Error(message);
  error.name = 'BrowserRTOpfsBlockStoreError';
  error.code = code;
  error.detail = detail;
  return error;
}

function summarizeAbortReason(reason) {
  if (reason == null) return null;
  if (typeof reason === 'string') return reason;
  if (typeof reason === 'number' || typeof reason === 'boolean') return String(reason);
  return { name: reason?.name || null, message: reason?.message || String(reason) };
}

const OPFS_COMPOSITE_ABORT_CLEANUP = Symbol('BrowserRT.opfsCompositeAbortCleanup');

function isAbortSignalLike(value) {
  return value && typeof value === 'object' && typeof value.aborted === 'boolean' && typeof value.addEventListener === 'function' && typeof value.removeEventListener === 'function';
}

function abortReason(signal, fallback = null) {
  try { return signal?.reason ?? fallback; } catch { return fallback; }
}

function composeAbortSignals(signals = []) {
  const uniqueSignals = [];
  const seen = new Set();
  for (const signal of signals) {
    if (!isAbortSignalLike(signal) || seen.has(signal)) continue;
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
  const abortFrom = (sourceSignal) => {
    if (controller.signal.aborted) return;
    try { controller.abort(abortReason(sourceSignal, new Error('BrowserRT OPFS provider signal aborted'))); } catch { controller.abort(); }
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

function abortSignalFromOptions(options = {}) {
  const signalOptionSupplied = Object.prototype.hasOwnProperty.call(options || {}, 'signal');
  const abortSignalOptionSupplied = Object.prototype.hasOwnProperty.call(options || {}, 'abortSignal');
  const signalSupplied = signalOptionSupplied && options.signal !== null && options.signal !== undefined;
  const abortSignalSupplied = abortSignalOptionSupplied && options.abortSignal !== null && options.abortSignal !== undefined;
  const supplied = [];
  if (signalSupplied) supplied.push({ key: 'signal', value: options.signal });
  if (abortSignalSupplied) supplied.push({ key: 'abortSignal', value: options.abortSignal });
  for (const row of supplied) {
    if (!isAbortSignalLike(row.value)) {
      throw storageError('BRT_OPFS_ABORT_SIGNAL_INVALID', 'OPFS block-store signal/abortSignal must be AbortSignal-compatible objects or null', { signalType: row.value === null ? 'null' : typeof row.value, option: row.key, signalOptionSupplied, abortSignalOptionSupplied, signalSupplied, abortSignalSupplied });
    }
  }
  const composition = composeAbortSignals(supplied.map((row) => row.value));
  return Object.freeze({ ...composition, signalSupplied, abortSignalSupplied, signalOptionSupplied, abortSignalOptionSupplied });
}


function finiteNonNegativeNumber(value, label) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < 0) throw storageError('BRT_OPFS_WRITE_BUDGET_INVALID', `${label} must be a non-negative finite number`, { label, value });
  return n;
}

function normalizeWriteBudgetGuard(value = null, source = 'writeBudgetGuard') {
  if (value === undefined || value === null || value === false) {
    return Object.freeze({ enabled: false, requireEstimate: false, minFreeBytes: 0, maxUsageRatio: 1, source, reason: 'disabled' });
  }
  if (value === true) {
    return Object.freeze({ enabled: true, requireEstimate: true, minFreeBytes: 0, maxUsageRatio: 1, source, reason: 'require-estimate' });
  }
  if (typeof value !== 'object') {
    throw storageError('BRT_OPFS_WRITE_BUDGET_INVALID', 'OPFS writeBudgetGuard must be an object, true, false, null, or undefined', { source, actualType: typeof value });
  }
  const minFreeBytes = finiteNonNegativeNumber(value.minFreeBytes ?? value.reserveBytes ?? value.minAvailableBytes ?? 0, `${source}.minFreeBytes`);
  const rawRatio = value.maxUsageRatio ?? value.maxProjectedUsageRatio ?? 1;
  const maxUsageRatio = Number(rawRatio);
  if (!Number.isFinite(maxUsageRatio) || maxUsageRatio <= 0 || maxUsageRatio > 1) {
    throw storageError('BRT_OPFS_WRITE_BUDGET_INVALID', `${source}.maxUsageRatio must be > 0 and <= 1`, { source, maxUsageRatio: rawRatio });
  }
  const requireEstimate = Boolean(value.requireEstimate ?? value.requireStorageEstimate ?? false);
  const enabled = value.enabled === false ? false : Boolean(requireEstimate || minFreeBytes > 0 || maxUsageRatio < 1);
  return Object.freeze({ enabled, requireEstimate, minFreeBytes, maxUsageRatio, source, reason: enabled ? 'configured' : 'no-threshold' });
}

function writeBudgetGuardFromConfig({ writeBudgetGuard = null, minFreeBytesForPut = undefined, maxUsageRatioForPut = undefined, requireStorageEstimateForPut = undefined } = {}) {
  if (writeBudgetGuard !== null && writeBudgetGuard !== undefined) return normalizeWriteBudgetGuard(writeBudgetGuard, 'constructor.writeBudgetGuard');
  if (minFreeBytesForPut !== undefined || maxUsageRatioForPut !== undefined || requireStorageEstimateForPut !== undefined) {
    return normalizeWriteBudgetGuard({ minFreeBytes: minFreeBytesForPut ?? 0, maxUsageRatio: maxUsageRatioForPut ?? 1, requireEstimate: requireStorageEstimateForPut === true }, 'constructor.writeBudgetGuard');
  }
  return normalizeWriteBudgetGuard(null, 'constructor.writeBudgetGuard');
}

function writeBudgetGuardForPut(defaultGuard, options = {}) {
  if (Object.prototype.hasOwnProperty.call(options || {}, 'writeBudgetGuard')) {
    return normalizeWriteBudgetGuard(options.writeBudgetGuard, 'put.writeBudgetGuard');
  }
  if (Object.prototype.hasOwnProperty.call(options || {}, 'minFreeBytesForPut')
    || Object.prototype.hasOwnProperty.call(options || {}, 'maxUsageRatioForPut')
    || Object.prototype.hasOwnProperty.call(options || {}, 'requireStorageEstimateForPut')) {
    return normalizeWriteBudgetGuard({ minFreeBytes: options.minFreeBytesForPut ?? 0, maxUsageRatio: options.maxUsageRatioForPut ?? 1, requireEstimate: options.requireStorageEstimateForPut === true }, 'put.writeBudgetGuard');
  }
  return defaultGuard;
}

function finiteEstimateNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) && n >= 0 ? n : null;
}

export function classifyOpfsBlockStoreError(error, context = {}) {
  const name = error?.name || 'Error';
  const message = error?.message || String(error);
  const explicitCode = typeof error?.code === 'string' && error.code.startsWith('BRT_OPFS_') ? error.code : null;
  const domCode = Number.isFinite(error?.code) ? error.code : null;
  const quotaLike = name === 'QuotaExceededError' || /quota|exceed/i.test(message);
  const code = explicitCode || (quotaLike ? 'BRT_OPFS_QUOTA_EXCEEDED'
    : name === 'NotFoundError' ? 'BRT_OPFS_NOT_FOUND'
    : name === 'SecurityError' ? 'BRT_OPFS_SECURITY_ERROR'
    : name === 'InvalidStateError' ? 'BRT_OPFS_INVALID_STATE'
    : name === 'NoModificationAllowedError' ? 'BRT_OPFS_WRITE_LOCK_UNAVAILABLE'
    : 'BRT_OPFS_OPERATION_FAILED');
  return Object.freeze({ code, name, message, domCode, context: Object.freeze({ ...context }) });
}

function wrapOpfsPutError(error, context = {}, rollback = null) {
  const classified = classifyOpfsBlockStoreError(error, context);
  const originalDetail = error?.detail && typeof error.detail === 'object' ? error.detail : null;
  const detail = { ...classified, originalName: classified.name, rollback };
  if (originalDetail) {
    detail.originalDetail = originalDetail;
    for (const key of ['reasons', 'reason', 'quota', 'usage', 'freeBefore', 'projectedUsage', 'projectedFreeBytes', 'projectedUsageRatio', 'guard', 'requestedBytes', 'digest', 'hash', 'path', 'source']) {
      if (originalDetail[key] !== undefined && detail[key] === undefined) detail[key] = originalDetail[key];
    }
  }
  return storageError(classified.code, `OPFS block put failed: ${classified.message}`, detail);
}

function toOwnedUint8Array(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value);
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  throw new Error('OPFS block-store bytes must be a string, ArrayBuffer, Uint8Array, or ArrayBuffer view');
}

function bytesToHex(bytes) {
  return Array.from(new Uint8Array(bytes)).map((x) => x.toString(16).padStart(2, '0')).join('');
}

async function digestBytesHexLocal(value) {
  const bytes = toOwnedUint8Array(value);
  if (globalThis.crypto?.subtle?.digest) {
    const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return bytesToHex(digest);
  }
  throw new Error('OPFS block store requires crypto.subtle.digest for sha256 block refs');
}

function blockKeyFromRef(refOrDigest) {
  if (typeof refOrDigest === 'string') {
    if (refOrDigest.startsWith('block:sha256:')) return refOrDigest.slice('block:sha256:'.length);
    if (refOrDigest.startsWith('sha256:')) return refOrDigest.slice('sha256:'.length);
    if (/^[0-9a-f]{64}$/.test(refOrDigest)) return refOrDigest;
  }
  if (refOrDigest && typeof refOrDigest === 'object') {
    if (typeof refOrDigest.hash === 'string') return blockKeyFromRef(refOrDigest.hash);
    if (typeof refOrDigest.digest === 'string') return blockKeyFromRef(refOrDigest.digest);
    if (typeof refOrDigest.id === 'string') return blockKeyFromRef(refOrDigest.id);
  }
  throw new Error('OPFS block ref must be sha256 digest string or block object ref');
}

function cleanPathPart(part) {
  if (typeof part !== 'string' || !part.length || part === '.' || part === '..' || /[\\/]/.test(part)) {
    throw new Error(`Invalid OPFS path segment: ${part}`);
  }
  return part;
}

function cleanPrefix(prefix) {
  const parts = String(prefix || '').split('/').filter(Boolean).map(cleanPathPart);
  if (!parts.length) throw new Error('OPFS block-store prefix must contain at least one path segment');
  return parts;
}

function createStageSessionId() {
  try {
    const crypto = globalThis.crypto;
    if (typeof crypto?.getRandomValues === 'function') {
      const words = new Uint32Array(2);
      crypto.getRandomValues(words);
      return `${words[0].toString(36)}${words[1].toString(36)}`.slice(0, 16) || 'stage0';
    }
  } catch {}
  const time = Date.now().toString(36);
  const random = Math.floor(Math.random() * 0xffffffff).toString(36);
  return `${time}${random}`.slice(0, 16) || 'stage0';
}

function createBlockRef(hash, fields = {}) {
  if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) {
    throw new Error('OPFS block ref requires lowercase 64-character sha256 hash');
  }
  return Object.freeze({
    kind: 'block',
    id: fields.id ?? `block:sha256:${hash}`,
    digest: `sha256:${hash}`,
    hash,
    algorithm: 'sha256',
    backend: fields.backend ?? DEFAULT_PROVIDER,
    path: fields.path ?? null,
    bytes: fields.bytes ?? 0,
    label: fields.label ?? null,
    ownership: fields.ownership ?? 'origin-private-content-addressed-provider',
    createdAt: fields.createdAt ?? Date.now()
  });
}

async function missingAsFalse(fn) {
  try { await fn(); return true; } catch (error) {
    if (error?.name === 'NotFoundError') return false;
    throw error;
  }
}

async function openWritable(fileHandle, { exclusive = true } = {}) {
  if (!exclusive) return Object.freeze({ writable: await fileHandle.createWritable(), mode: 'default', fallback: false });
  try {
    return Object.freeze({ writable: await fileHandle.createWritable({ mode: 'exclusive' }), mode: 'exclusive', fallback: false });
  } catch (error) {
    // Older implementations may not understand the mode option. Fall back only
    // for option-shape errors; contention/security/quota errors must remain real failures.
    if (error?.name === 'TypeError') {
      return Object.freeze({ writable: await fileHandle.createWritable(), mode: 'default', fallback: true });
    }
    throw error;
  }
}

export class OpfsAsyncBlockStore {
  #trace;
  #rootPromise = null;
  #opened = false;
  #closed = false;
  #closeController = typeof AbortController === 'function' ? new AbortController() : null;
  #inFlightOperations = 0;
  #operationSeq = 0;
  #stageSessionId = createStageSessionId();
  #activeStagedWrites = new Map();

  constructor({ name = 'opfs-async-block-store', prefix = 'browserrt/blocks', provider = DEFAULT_PROVIDER, trace = null, verifyExistingBlocksOnPut = true, verifyAfterWrite = true, verifyOnHas = true, repairCorruptOnPut = true, exclusiveWriters = true, writeBudgetGuard = null, minFreeBytesForPut = undefined, maxUsageRatioForPut = undefined, requireStorageEstimateForPut = undefined } = {}) {
    this.name = name;
    this.provider = provider;
    this.prefix = cleanPrefix(prefix).join('/');
    this.verifyExistingBlocksOnPut = verifyExistingBlocksOnPut !== false;
    this.verifyAfterWrite = verifyAfterWrite !== false;
    this.verifyOnHas = verifyOnHas !== false;
    this.repairCorruptOnPut = repairCorruptOnPut !== false;
    this.exclusiveWriters = exclusiveWriters !== false;
    this.writeBudgetGuard = writeBudgetGuardFromConfig({ writeBudgetGuard, minFreeBytesForPut, maxUsageRatioForPut, requireStorageEstimateForPut });
    this.#trace = trace;
    this.stats = {
      opens: 0,
      openFailures: 0,
      openRetryResets: 0,
      puts: 0,
      putFailures: 0,
      quotaRejects: 0,
      duplicatePuts: 0,
      gets: 0,
      has: 0,
      deletes: 0,
      verifies: 0,
      checksumFailures: 0,
      estimateCalls: 0,
      cleanupCalls: 0,
      rollbackAttempts: 0,
      rollbackDeletes: 0,
      rollbackMisses: 0,
      rollbackFailures: 0,
      integrityChecks: 0,
      corruptBlocksDetected: 0,
      corruptDeletes: 0,
      corruptRepairs: 0,
      postWriteVerifications: 0,
      exclusiveWriterFallbacks: 0,
      abortRejects: 0,
      invalidAbortSignals: 0,
      compositeAbortSignals: 0,
      abortSignalOptionPairs: 0,
      writeBudgetChecks: 0,
      writeBudgetRejects: 0,
      writeBudgetDuplicateBypasses: 0,
      writeBudgetEstimateUnavailable: 0,
      writeBudgetEstimateFailures: 0,
      rollbackOwnershipSkips: 0,
      rollbackValidBlockPreserves: 0,
      rollbackIntegrityChecks: 0,
      rollbackIntegrityCheckFailures: 0,
      noCreateMisses: 0,
      closeCalls: 0,
      closedOperationRejects: 0,
      closeAbortSignals: 0,
      closeAbortRejects: 0,
      operationsStarted: 0,
      operationsSettled: 0,
      stagedPuts: 0,
      stagedWriteVerifications: 0,
      stagedPublishWrites: 0,
      stagedTempDeletes: 0,
      stagedTempDeleteMisses: 0,
      stagedTempDeleteFailures: 0,
      stagedVerifyFailures: 0,
      stagedRecoverySweeps: 0,
      stagedRecoveryDirectoriesScanned: 0,
      stagedRecoveryFilesScanned: 0,
      stagedRecoveryCandidates: 0,
      stagedRecoveryDeletes: 0,
      stagedRecoveryMisses: 0,
      stagedRecoverySkips: 0,
      stagedRecoveryActiveSkips: 0,
      stagedRecoveryFailures: 0,
      stagedActiveWritesStarted: 0,
      stagedActiveWritesSettled: 0,
      stagedActiveWritesHighWater: 0
    };
    this.#trace?.emit('storage:opfs-blockstore-create', { name: this.name, provider: this.provider, prefix: this.prefix, verifyExistingBlocksOnPut: this.verifyExistingBlocksOnPut, verifyAfterWrite: this.verifyAfterWrite, verifyOnHas: this.verifyOnHas, repairCorruptOnPut: this.repairCorruptOnPut, exclusiveWriters: this.exclusiveWriters, explicitAbortSignals: true, writeBudgetGuard: this.writeBudgetGuard, stageSessionId: this.#stageSessionId });
  }

  get available() {
    return typeof globalThis.navigator?.storage?.getDirectory === 'function';
  }

  #throwIfClosed(op = 'operation') {
    if (!this.#closed) return;
    this.stats.closedOperationRejects += 1;
    const detail = { store: this.name, prefix: this.prefix, op, closed: true };
    this.#trace?.emit('storage:opfs-blockstore-closed-reject', detail);
    throw storageError('BRT_OPFS_STORE_CLOSED', `OPFS block-store ${this.name} is closed`, detail);
  }

  async open() {
    this.#throwIfClosed('open');
    if (!this.available) {
      throw storageError('BRT_OPFS_UNAVAILABLE', 'navigator.storage.getDirectory is unavailable for OPFS async block store', { store: this.name });
    }
    if (!this.#rootPromise) {
      let guardedRootPromise = null;
      const rootPromise = (async () => {
        const originRoot = await globalThis.navigator.storage.getDirectory();
        let dir = originRoot;
        for (const part of this.prefix.split('/')) dir = await dir.getDirectoryHandle(part, { create: true });
        this.stats.opens += 1;
        this.#opened = true;
        this.#trace?.emit('storage:opfs-blockstore-open', { store: this.name, prefix: this.prefix });
        return dir;
      })();
      guardedRootPromise = rootPromise.catch((error) => {
        const classified = classifyOpfsBlockStoreError(error, { store: this.name, prefix: this.prefix, op: 'open' });
        const rootPromiseReset = this.#rootPromise === guardedRootPromise;
        this.stats.openFailures += 1;
        if (rootPromiseReset) {
          this.#rootPromise = null;
          this.stats.openRetryResets += 1;
        }
        this.#opened = false;
        this.#trace?.emit('storage:opfs-blockstore-open-error', { store: this.name, prefix: this.prefix, error: classified, rootPromiseReset });
        throw error;
      });
      this.#rootPromise = guardedRootPromise;
    }
    return await this.#rootPromise;
  }

  blockPath(hash) {
    if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) throw new Error('blockPath requires sha256 hex hash');
    return `${this.prefix}/${hash.slice(0, 2)}/${hash.slice(2, 4)}/${hash}.blk`;
  }

  #stagedFileName(hash, opSeq = 0) {
    if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) throw new Error('stagedFileName requires sha256 hex hash');
    const seq = Number.isFinite(opSeq) ? Math.max(0, Number(opSeq)) : 0;
    return `${hash}.brt-stage-${this.#stageSessionId}-${seq.toString(36)}.tmp`;
  }

  #stagedBlockPath(hash, fileName) {
    if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) throw new Error('stagedBlockPath requires sha256 hex hash');
    if (typeof fileName !== 'string' || !fileName.startsWith(`${hash}.brt-stage-`) || !fileName.endsWith('.tmp') || /[\/]/.test(fileName)) {
      throw new Error('stagedBlockPath requires a same-bucket BrowserRT staged filename');
    }
    return `${this.prefix}/${hash.slice(0, 2)}/${hash.slice(2, 4)}/${fileName}`;
  }

  #stagedHashFromFileName(fileName) {
    if (typeof fileName !== 'string') return null;
    const match = /^([0-9a-f]{64})\.brt-stage-[0-9a-z]+(?:-[0-9a-z]+)*\.tmp$/.exec(fileName);
    return match ? match[1] : null;
  }

  #isStagedFileInExpectedBucket(fileName, firstBucket, secondBucket) {
    const hash = this.#stagedHashFromFileName(fileName);
    if (!hash) return Object.freeze({ match: false, reason: 'not-browserrt-staged-name', hash: null });
    if (hash.slice(0, 2) !== firstBucket || hash.slice(2, 4) !== secondBucket) {
      return Object.freeze({ match: false, reason: 'staged-name-outside-digest-bucket', hash });
    }
    return Object.freeze({ match: true, reason: 'same-bucket-staged-temp', hash });
  }

  #activeStagedKey(hash, fileName) {
    return `${hash}/${fileName}`;
  }

  #markActiveStagedWrite(hash, fileName, path, opSeq) {
    const key = this.#activeStagedKey(hash, fileName);
    const row = Object.freeze({ hash, fileName, path, opSeq, startedAt: Date.now() });
    this.#activeStagedWrites.set(key, row);
    this.stats.stagedActiveWritesStarted += 1;
    this.stats.stagedActiveWritesHighWater = Math.max(this.stats.stagedActiveWritesHighWater, this.#activeStagedWrites.size);
    this.#trace?.emit('storage:opfs-block-staged-active-start', { store: this.name, prefix: this.prefix, digest: `sha256:${hash}`, hash, path, fileName, opSeq, activeStagedWrites: this.#activeStagedWrites.size });
    return key;
  }

  #clearActiveStagedWrite(key, outcome = 'settled') {
    const row = this.#activeStagedWrites.get(key);
    if (!row) return false;
    this.#activeStagedWrites.delete(key);
    this.stats.stagedActiveWritesSettled += 1;
    this.#trace?.emit('storage:opfs-block-staged-active-settle', { store: this.name, prefix: this.prefix, digest: `sha256:${row.hash}`, hash: row.hash, path: row.path, fileName: row.fileName, opSeq: row.opSeq, outcome, activeStagedWrites: this.#activeStagedWrites.size });
    return true;
  }

  #isActiveStagedWrite(hash, fileName) {
    return this.#activeStagedWrites.has(this.#activeStagedKey(hash, fileName));
  }

  async #directoryEntries(dir, { signal = null, op = 'directory-entries', path = null } = {}) {
    this.#throwIfAborted(signal, { op, stage: 'before-directory-entries', path });
    const iterator = typeof dir?.entries === 'function' ? dir.entries() : (typeof dir?.[Symbol.asyncIterator] === 'function' ? dir[Symbol.asyncIterator]() : null);
    if (!iterator) {
      throw storageError('BRT_OPFS_DIRECTORY_ITERATION_UNAVAILABLE', 'OPFS staged recovery requires iterable FileSystemDirectoryHandle entries()', { store: this.name, prefix: this.prefix, op, path });
    }
    const rows = [];
    for await (const [name, handle] of iterator) {
      this.#throwIfAborted(signal, { op, stage: 'during-directory-entries', path, name });
      rows.push([name, handle]);
    }
    return rows;
  }

  async #bucket(hash, create = true) {
    const root = await this.open();
    const a = await root.getDirectoryHandle(hash.slice(0, 2), { create });
    return await a.getDirectoryHandle(hash.slice(2, 4), { create });
  }

  #recordNoCreateMiss(hash, { op = 'read', stage = 'not-found', reason = 'not-found-no-create' } = {}) {
    const digest = `sha256:${hash}`;
    const path = this.blockPath(hash);
    this.stats.noCreateMisses += 1;
    this.#trace?.emit('storage:opfs-block-no-create-miss', { store: this.name, digest, hash, path, op, stage, reason, created: false });
  }

  async #readBlockBytes(hash, { signal = null, op = 'read', existingOnly = false, ignoreClosed = false } = {}) {
    try {
      this.#throwIfAborted(signal, { op, stage: 'before-open-bucket', hash });
      const bucket = existingOnly ? await this.#existingBucket(hash, { signal, op, ignoreClosed }) : await this.#bucket(hash, false);
      this.#throwIfAborted(signal, { op, stage: 'before-open-file', hash });
      const file = await bucket.getFileHandle(`${hash}.blk`, { create: false });
      this.#throwIfAborted(signal, { op, stage: 'before-read-file', hash });
      const bytes = new Uint8Array(await (await file.getFile()).arrayBuffer());
      this.#throwIfAborted(signal, { op, stage: 'after-read-file', hash });
      return bytes;
    } catch (error) {
      if (existingOnly && error?.name === 'NotFoundError') this.#recordNoCreateMiss(hash, { op, stage: 'read-block-bytes' });
      throw error;
    }
  }

  async #readNamedBlockBytes(bucket, fileName, { signal = null, op = 'read-named-block', hash = null, digest = null, path = null, stage = 'read-named-file' } = {}) {
    this.#throwIfAborted(signal, { op, stage: `before-open-${stage}`, hash, digest, path, fileName });
    const file = await bucket.getFileHandle(fileName, { create: false });
    this.#throwIfAborted(signal, { op, stage: `before-read-${stage}`, hash, digest, path, fileName });
    const bytes = new Uint8Array(await (await file.getFile()).arrayBuffer());
    this.#throwIfAborted(signal, { op, stage: `after-read-${stage}`, hash, digest, path, fileName });
    return bytes;
  }

  async #inspectExistingBlock(hash, { source = 'integrity-check', emitValid = false, signal = null, existingOnly = false, ignoreClosed = false } = {}) {
    const digest = `sha256:${hash}`;
    const path = this.blockPath(hash);
    try {
      const bytes = await this.#readBlockBytes(hash, { signal, op: source, existingOnly, ignoreClosed });
      this.#throwIfAborted(signal, { op: source, stage: 'before-integrity-digest', hash });
      const actualHash = await digestBytesHexLocal(bytes);
      this.#throwIfAborted(signal, { op: source, stage: 'after-integrity-digest', hash });
      const actualDigest = `sha256:${actualHash}`;
      const ok = actualHash === hash;
      this.stats.integrityChecks += 1;
      const result = Object.freeze({ present: true, ok, digest, hash, actualDigest, actualHash, bytes: bytes.byteLength, path, source });
      if (ok && emitValid) this.#trace?.emit('storage:opfs-block-integrity-ok', { store: this.name, digest, hash, bytes: bytes.byteLength, path, source });
      if (!ok) {
        this.stats.checksumFailures += 1;
        this.stats.corruptBlocksDetected += 1;
        this.#trace?.emit('storage:opfs-block-corrupt', { store: this.name, digest, hash, actualDigest, bytes: bytes.byteLength, path, source });
      }
      return result;
    } catch (error) {
      if (error?.name === 'NotFoundError') return Object.freeze({ present: false, ok: false, digest, hash, actualDigest: null, actualHash: null, bytes: 0, path, source });
      throw error;
    }
  }

  #abortContextFromOptions(options = {}, op = 'operation') {
    try {
      const context = abortSignalFromOptions(options);
      if (context.composed) {
        this.stats.compositeAbortSignals += 1;
        this.#trace?.emit('storage:opfs-block-composite-abort-signal', { store: this.name, op, signalSupplied: context.signalSupplied, abortSignalSupplied: context.abortSignalSupplied, nativeAny: context.nativeAny === true, degraded: context.degraded === true });
      }
      if (context.signalSupplied && context.abortSignalSupplied) this.stats.abortSignalOptionPairs += 1;
      return context;
    } catch (error) {
      this.stats.invalidAbortSignals += 1;
      this.#trace?.emit('storage:opfs-block-abort-signal-invalid', { store: this.name, op, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null } });
      throw error;
    }
  }

  #signalFromOptions(options = {}, op = 'operation') {
    return this.#beginOperation(options, op).signal;
  }

  #cleanupAbortContext(context) {
    const cleanup = context?.cleanup || context?.[OPFS_COMPOSITE_ABORT_CLEANUP];
    if (typeof cleanup === 'function') cleanup();
  }

  #beginOperation(options = {}, op = 'operation') {
    this.#throwIfClosed(op);
    const userContext = this.#abortContextFromOptions(options, op);
    const closeSignal = this.#closeController?.signal ?? null;
    const lifecycleComposition = closeSignal ? composeAbortSignals([userContext.signal, closeSignal]) : Object.freeze({ signal: userContext.signal, cleanup: null, composed: false });
    if (lifecycleComposition.composed) {
      this.#trace?.emit('storage:opfs-block-lifecycle-abort-signal', { store: this.name, op, signalSupplied: userContext.signalSupplied, abortSignalSupplied: userContext.abortSignalSupplied, closeSignalSupplied: true, nativeAny: lifecycleComposition.nativeAny === true, degraded: lifecycleComposition.degraded === true });
    }
    const opSeq = ++this.#operationSeq;
    this.#inFlightOperations += 1;
    this.stats.operationsStarted += 1;
    this.#trace?.emit('storage:opfs-block-operation-start', { store: this.name, op, opSeq, inFlightOperations: this.#inFlightOperations });
    const cleanup = () => {
      this.#cleanupAbortContext(lifecycleComposition);
      this.#cleanupAbortContext(userContext);
    };
    return Object.freeze({ ...userContext, signal: lifecycleComposition.signal, cleanup, op, opSeq, closeSignalSupplied: closeSignal !== null });
  }

  #endOperation(context) {
    try { this.#cleanupAbortContext(context); }
    finally {
      if (Number.isFinite(context?.opSeq)) {
        this.#inFlightOperations = Math.max(0, this.#inFlightOperations - 1);
        this.stats.operationsSettled += 1;
        this.#trace?.emit('storage:opfs-block-operation-settle', { store: this.name, op: context.op, opSeq: context.opSeq, inFlightOperations: this.#inFlightOperations });
      }
    }
  }

  #throwIfAborted(signal, context = {}) {
    if (!signal?.aborted) return;
    this.stats.abortRejects += 1;
    const reasonCode = typeof signal.reason?.code === 'string' ? signal.reason.code : null;
    if (reasonCode === 'BRT_OPFS_STORE_CLOSED') this.stats.closeAbortRejects += 1;
    const detail = { store: this.name, prefix: this.prefix, ...context, closeAbort: reasonCode === 'BRT_OPFS_STORE_CLOSED', reason: summarizeAbortReason(signal.reason) };
    this.#trace?.emit('storage:opfs-block-abort', detail);
    throw storageError('BRT_OPFS_OPERATION_ABORTED', `OPFS block-store ${context.op || 'operation'} aborted before provider mutation completed`, detail);
  }

  async #checkWriteBudgetBeforePut(bytes, guard, signal = null, context = {}) {
    if (!guard?.enabled) return Object.freeze({ checked: false, enabled: false, reason: guard?.reason || 'disabled' });
    this.#throwIfAborted(signal, { op: 'put', stage: 'before-write-budget-estimate', requestedBytes: bytes.byteLength });
    if (typeof globalThis.navigator?.storage?.estimate !== 'function') {
      this.stats.writeBudgetEstimateUnavailable += 1;
      const detail = { store: this.name, prefix: this.prefix, requestedBytes: bytes.byteLength, ...context, guard, reason: 'estimate-unavailable' };
      this.#trace?.emit('storage:opfs-block-write-budget-estimate-unavailable', detail);
      if (guard.requireEstimate) throw storageError('BRT_OPFS_ESTIMATE_UNAVAILABLE', 'OPFS write budget guard requires navigator.storage.estimate()', detail);
      return Object.freeze({ checked: false, enabled: true, reason: 'estimate-unavailable', guard });
    }
    let estimate;
    try {
      estimate = await globalThis.navigator.storage.estimate();
    } catch (error) {
      this.stats.writeBudgetEstimateFailures += 1;
      const detail = { store: this.name, prefix: this.prefix, requestedBytes: bytes.byteLength, ...context, guard, reason: 'estimate-failed', error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null } };
      this.#trace?.emit('storage:opfs-block-write-budget-estimate-error', detail);
      if (guard.requireEstimate) throw storageError('BRT_OPFS_ESTIMATE_UNAVAILABLE', 'OPFS write budget guard could not obtain navigator.storage.estimate()', detail);
      return Object.freeze({ checked: false, enabled: true, reason: 'estimate-failed', guard });
    }
    this.#throwIfAborted(signal, { op: 'put', stage: 'after-write-budget-estimate', requestedBytes: bytes.byteLength });
    const quota = finiteEstimateNumber(estimate?.quota);
    const usage = finiteEstimateNumber(estimate?.usage);
    if (quota === null || usage === null || quota <= 0) {
      this.stats.writeBudgetEstimateUnavailable += 1;
      const detail = { store: this.name, prefix: this.prefix, requestedBytes: bytes.byteLength, quota: estimate?.quota ?? null, usage: estimate?.usage ?? null, ...context, guard, reason: 'estimate-incomplete' };
      this.#trace?.emit('storage:opfs-block-write-budget-estimate-unavailable', detail);
      if (guard.requireEstimate) throw storageError('BRT_OPFS_ESTIMATE_UNAVAILABLE', 'OPFS write budget guard requires numeric quota and usage estimate values', detail);
      return Object.freeze({ checked: false, enabled: true, reason: 'estimate-incomplete', guard });
    }
    this.stats.writeBudgetChecks += 1;
    const requestedBytes = bytes.byteLength;
    const projectedUsage = usage + requestedBytes;
    const freeBefore = Math.max(0, quota - usage);
    const projectedFreeBytes = quota - projectedUsage;
    const projectedUsageRatio = projectedUsage / quota;
    const reasons = [];
    if (projectedFreeBytes < guard.minFreeBytes) reasons.push('min-free-bytes');
    if (projectedUsageRatio > guard.maxUsageRatio) reasons.push('max-usage-ratio');
    const detail = Object.freeze({ store: this.name, prefix: this.prefix, requestedBytes, quota, usage, freeBefore, projectedUsage, projectedFreeBytes, projectedUsageRatio, ...context, guard });
    this.#trace?.emit('storage:opfs-block-write-budget-check', detail);
    if (reasons.length) {
      this.stats.writeBudgetRejects += 1;
      const rejectDetail = { ...detail, reasons };
      this.#trace?.emit('storage:opfs-block-write-budget-reject', rejectDetail);
      throw storageError('BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'OPFS block-store write budget guard rejected put before OPFS file mutation', rejectDetail);
    }
    return Object.freeze({ checked: true, ok: true, ...detail });
  }

  #bypassWriteBudgetForDuplicate(bytes, guard, { digest = null, hash = null, path = null, source = 'duplicate-put' } = {}) {
    if (!guard?.enabled) return Object.freeze({ checked: false, enabled: false, bypassed: false, reason: guard?.reason || 'disabled' });
    this.stats.writeBudgetDuplicateBypasses += 1;
    const detail = Object.freeze({ store: this.name, prefix: this.prefix, requestedBytes: bytes.byteLength, digest, hash, path, source, guard, reason: 'verified-duplicate-no-op-put' });
    this.#trace?.emit('storage:opfs-block-write-budget-duplicate-bypass', detail);
    return Object.freeze({ checked: false, enabled: true, bypassed: true, ok: true, ...detail });
  }

  async #openExistingPrefix({ signal = null, op = 'existing-prefix-open', hash = null, ignoreClosed = false } = {}) {
    if (!ignoreClosed) this.#throwIfClosed(op);
    if (!this.available) {
      throw storageError('BRT_OPFS_UNAVAILABLE', 'navigator.storage.getDirectory is unavailable for OPFS async block store', { store: this.name });
    }
    try {
      this.#throwIfAborted(signal, { op, stage: 'before-open-existing-root', hash });
      const originRoot = await globalThis.navigator.storage.getDirectory();
      let dir = originRoot;
      for (const part of this.prefix.split('/')) {
        this.#throwIfAborted(signal, { op, stage: 'before-open-existing-prefix-part', hash, part });
        dir = await dir.getDirectoryHandle(part, { create: false });
      }
      return dir;
    } catch (error) {
      if (error?.name === 'NotFoundError') throw error;
      const classified = classifyOpfsBlockStoreError(error, { store: this.name, prefix: this.prefix, op, hash, existingOnly: true });
      this.stats.openFailures += 1;
      this.#opened = false;
      this.#trace?.emit('storage:opfs-blockstore-open-error', { store: this.name, prefix: this.prefix, op, hash, existingOnly: true, error: classified, rootPromiseReset: false });
      throw error;
    }
  }

  async #existingBucket(hash, { signal = null, op = 'existing-bucket-open', ignoreClosed = false } = {}) {
    const root = await this.#openExistingPrefix({ signal, op, hash, ignoreClosed });
    this.#throwIfAborted(signal, { op, stage: 'before-open-existing-first-bucket', hash });
    const a = await root.getDirectoryHandle(hash.slice(0, 2), { create: false });
    this.#throwIfAborted(signal, { op, stage: 'before-open-existing-second-bucket', hash });
    return await a.getDirectoryHandle(hash.slice(2, 4), { create: false });
  }

  async #deleteBlockFile(hash, { reason = 'delete', signal = null, op = 'delete', ignoreClosed = false } = {}) {
    const digest = `sha256:${hash}`;
    const path = this.blockPath(hash);
    try {
      this.#throwIfAborted(signal, { op, stage: 'before-open-bucket', hash, digest, path, reason });
      const bucket = await this.#existingBucket(hash, { signal, op, ignoreClosed });
      this.#throwIfAborted(signal, { op, stage: 'before-remove-entry', hash, digest, path, reason });
      await bucket.removeEntry(`${hash}.blk`);
      this.#trace?.emit('storage:opfs-block-delete-file', { store: this.name, digest, hash, deleted: true, path, reason });
      return true;
    } catch (error) {
      if (error?.name === 'NotFoundError') {
        this.#recordNoCreateMiss(hash, { op, stage: 'delete-block-file', reason });
        this.#trace?.emit('storage:opfs-block-delete-file', { store: this.name, digest, hash, deleted: false, path, reason });
        return false;
      }
      throw error;
    }
  }

  async #deleteNamedBlockFile(hash, fileName, { reason = 'delete-named-block', signal = null, op = 'delete-named-block', ignoreClosed = false, path = null } = {}) {
    const digest = `sha256:${hash}`;
    const blockPath = path || (fileName === `${hash}.blk` ? this.blockPath(hash) : this.#stagedBlockPath(hash, fileName));
    try {
      this.#throwIfAborted(signal, { op, stage: 'before-open-bucket', hash, digest, path: blockPath, reason, fileName });
      const bucket = await this.#existingBucket(hash, { signal, op, ignoreClosed });
      this.#throwIfAborted(signal, { op, stage: 'before-remove-entry', hash, digest, path: blockPath, reason, fileName });
      await bucket.removeEntry(fileName);
      this.#trace?.emit('storage:opfs-block-delete-file', { store: this.name, digest, hash, deleted: true, path: blockPath, reason, fileName });
      return true;
    } catch (error) {
      if (error?.name === 'NotFoundError') {
        this.#recordNoCreateMiss(hash, { op, stage: 'delete-named-block-file', reason });
        this.#trace?.emit('storage:opfs-block-delete-file', { store: this.name, digest, hash, deleted: false, path: blockPath, reason, fileName });
        return false;
      }
      throw error;
    }
  }

  async #cleanupStagedWrite(hash, fileName, { reason = 'staged-put-cleanup', ignoreClosed = true } = {}) {
    if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash) || typeof fileName !== 'string') {
      return Object.freeze({ attempted: false, deleted: false, missed: false, error: null, reason: 'missing-staged-file' });
    }
    const path = this.#stagedBlockPath(hash, fileName);
    try {
      const deleted = await this.#deleteNamedBlockFile(hash, fileName, { reason, op: 'staged-put-cleanup', ignoreClosed, path });
      if (deleted) this.stats.stagedTempDeletes += 1;
      else this.stats.stagedTempDeleteMisses += 1;
      const result = Object.freeze({ attempted: true, deleted, missed: !deleted, error: null, reason, path, fileName });
      this.#trace?.emit('storage:opfs-block-staged-cleanup', { store: this.name, digest: `sha256:${hash}`, hash, path, fileName, deleted, missed: !deleted, reason });
      return result;
    } catch (error) {
      this.stats.stagedTempDeleteFailures += 1;
      const detail = classifyOpfsBlockStoreError(error, { store: this.name, prefix: this.prefix, digest: `sha256:${hash}`, hash, path, fileName, stagedCleanup: true, reason });
      const result = Object.freeze({ attempted: true, deleted: false, missed: false, error: detail, reason, path, fileName });
      this.#trace?.emit('storage:opfs-block-staged-cleanup-error', { store: this.name, digest: `sha256:${hash}`, hash, path, fileName, error: detail, reason });
      return result;
    }
  }

  async #rollbackFailedPut(hash, { allowed = false, reason = 'unowned-final-block', rollbackDigest = null, path = null } = {}) {
    if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) {
      return Object.freeze({ attempted: false, deleted: false, missed: false, skipped: true, reason: 'missing-or-invalid-hash', error: null });
    }
    const blockDigest = rollbackDigest || `sha256:${hash}`;
    const blockPath = path || this.blockPath(hash);
    if (!allowed) {
      this.stats.rollbackOwnershipSkips += 1;
      const result = Object.freeze({ attempted: false, deleted: false, missed: false, skipped: true, reason, error: null, digest: blockDigest, path: blockPath });
      this.#trace?.emit('storage:opfs-block-put-rollback-skipped', { store: this.name, digest: blockDigest, hash, path: blockPath, reason });
      return result;
    }
    this.stats.rollbackAttempts += 1;
    const digest = blockDigest;
    let integrity = null;
    try {
      integrity = await this.#inspectExistingBlock(hash, { source: 'failed-put-rollback-preserve-check', existingOnly: true, ignoreClosed: true });
      this.stats.rollbackIntegrityChecks += 1;
      if (integrity.present && integrity.ok) {
        this.stats.rollbackValidBlockPreserves += 1;
        const result = Object.freeze({ attempted: true, deleted: false, missed: false, skipped: true, preserved: true, reason: 'valid-final-block-preserved', error: null, digest, path: blockPath, integrity });
        this.#trace?.emit('storage:opfs-block-put-rollback-preserved', { store: this.name, digest, hash, path: blockPath, reason: result.reason, bytes: integrity.bytes, actualDigest: integrity.actualDigest });
        return result;
      }
    } catch (inspectError) {
      this.stats.rollbackIntegrityCheckFailures += 1;
      const inspectDetail = classifyOpfsBlockStoreError(inspectError, { store: this.name, prefix: this.prefix, digest, hash, path: blockPath, rollback: true, preserveCheck: true });
      integrity = Object.freeze({ present: null, ok: false, error: inspectDetail });
      this.#trace?.emit('storage:opfs-block-put-rollback-preserve-check-error', { store: this.name, digest, hash, path: blockPath, error: inspectDetail });
    }
    try {
      const deleted = await this.#deleteBlockFile(hash, { reason: 'failed-put-rollback', ignoreClosed: true });
      if (deleted) this.stats.rollbackDeletes += 1;
      else this.stats.rollbackMisses += 1;
      const result = Object.freeze({ attempted: true, deleted, missed: !deleted, skipped: false, preserved: false, error: null, digest, path: blockPath, integrity });
      this.#trace?.emit('storage:opfs-block-put-rollback', { store: this.name, digest, hash, path: result.path, deleted, missed: !deleted, integrityOk: integrity?.ok ?? null, integrityPresent: integrity?.present ?? null });
      return result;
    } catch (error) {
      this.stats.rollbackFailures += 1;
      const detail = classifyOpfsBlockStoreError(error, { store: this.name, prefix: this.prefix, digest, hash, path: this.blockPath(hash), rollback: true });
      const result = Object.freeze({ attempted: true, deleted: false, missed: false, skipped: false, preserved: false, error: detail, digest, path: blockPath, integrity });
      this.#trace?.emit('storage:opfs-block-put-rollback-error', { store: this.name, digest, hash, path: result.path, error: detail, integrityOk: integrity?.ok ?? null, integrityPresent: integrity?.present ?? null });
      return result;
    }
  }

  async #writeBlockBytes(bucket, fileName, bytes, { digest, hash, label, signal = null, purpose = 'final', path = null }) {
    this.#throwIfAborted(signal, { op: 'put', stage: 'before-create-file', hash, digest });
    const file = await bucket.getFileHandle(fileName, { create: true });
    this.#throwIfAborted(signal, { op: 'put', stage: 'before-create-writable', hash, digest });
    const writer = await openWritable(file, { exclusive: this.exclusiveWriters });
    if (writer.fallback) this.stats.exclusiveWriterFallbacks += 1;
    let closed = false;
    try {
      this.#throwIfAborted(signal, { op: 'put', stage: 'before-write', hash, digest });
      await writer.writable.write(bytes);
      this.#throwIfAborted(signal, { op: 'put', stage: 'before-close', hash, digest });
      await writer.writable.close();
      closed = true;
      this.#throwIfAborted(signal, { op: 'put', stage: 'after-close', hash, digest });
    } catch (error) {
      if (!closed && typeof writer.writable?.abort === 'function') await writer.writable.abort().catch(() => {});
      throw error;
    }
    this.#trace?.emit('storage:opfs-block-write-close', { store: this.name, digest, hash, bytes: bytes.byteLength, writerMode: writer.mode, exclusiveWriterFallback: writer.fallback, label, fileName, purpose, path: path || (fileName === `${hash}.blk` ? this.blockPath(hash) : this.#stagedBlockPath(hash, fileName)) });
    return writer;
  }

  async put(value, fields = {}, options = {}) {
    const abortContext = this.#beginOperation(options, 'put');
    const signal = abortContext.signal;
    let bytes = new Uint8Array();
    let hash = null;
    let digest = null;
    let path = null;
    let budget = null;
    let repairedCorrupt = false;
    let repair = null;
    let rollbackOwnsFinalBlock = false;
    let duplicate = false;
    let staging = null;
    let activeStagedKey = null;
    try {
      this.#throwIfAborted(signal, { op: 'put', stage: 'before-digest' });
      bytes = toOwnedUint8Array(value);
      const writeBudgetGuard = writeBudgetGuardForPut(this.writeBudgetGuard, options);
      let writer = null;
      try {
        hash = await digestBytesHexLocal(bytes);
        digest = `sha256:${hash}`;
        path = this.blockPath(hash);
        this.#throwIfAborted(signal, { op: 'put', stage: 'before-duplicate-check', hash, digest, path, bytes: bytes.byteLength });
        let bucket = null;
        const fileName = `${hash}.blk`;
        duplicate = false;
        if (this.verifyExistingBlocksOnPut) {
          const existing = await this.#inspectExistingBlock(hash, { source: 'put-duplicate-check', signal, existingOnly: true });
          if (existing.present && existing.ok) {
            duplicate = true;
            budget = this.#bypassWriteBudgetForDuplicate(bytes, writeBudgetGuard, { digest, hash, path, source: 'verified-existing-block' });
          } else if (existing.present && !existing.ok) {
            if (!this.repairCorruptOnPut) {
              throw storageError('BRT_OPFS_CORRUPT_BLOCK', 'OPFS block file exists at content-addressed path but checksum does not match', { store: this.name, prefix: this.prefix, digest, hash, path, existing });
            }
            budget = await this.#checkWriteBudgetBeforePut(bytes, writeBudgetGuard, signal, { digest, hash, path, source: 'corrupt-block-repair-put' });
            this.#throwIfAborted(signal, { op: 'put', stage: 'before-corrupt-repair-delete', hash, digest, path, bytes: bytes.byteLength });
            const deleted = await this.#deleteBlockFile(hash, { reason: 'corrupt-repair-before-put', signal, op: 'put' });
            rollbackOwnsFinalBlock = true;
            this.stats.corruptDeletes += deleted ? 1 : 0;
            this.stats.corruptRepairs += 1;
            repairedCorrupt = true;
            repair = Object.freeze({ deleted, existing });
            this.#trace?.emit('storage:opfs-block-repair', { store: this.name, digest, hash, path, deleted, actualDigest: existing.actualDigest, bytes: existing.bytes, source: 'put-duplicate-check' });
          }
        } else {
          this.#throwIfAborted(signal, { op: 'put', stage: 'before-duplicate-file-check', hash, digest, path, bytes: bytes.byteLength });
          duplicate = await missingAsFalse(async () => { const existingBucket = await this.#existingBucket(hash, { signal, op: 'put-duplicate-file-check' }); await existingBucket.getFileHandle(fileName, { create: false }); });
          if (duplicate) budget = this.#bypassWriteBudgetForDuplicate(bytes, writeBudgetGuard, { digest, hash, path, source: 'existing-file-duplicate-check' });
        }
        if (!duplicate) {
          if (!budget) budget = await this.#checkWriteBudgetBeforePut(bytes, writeBudgetGuard, signal, { digest, hash, path, source: repairedCorrupt ? 'corrupt-block-repair-put' : 'new-block-put' });
          this.#throwIfAborted(signal, { op: 'put', stage: 'before-open-mutable-bucket', hash, digest, path, bytes: bytes.byteLength });
          bucket = await this.#bucket(hash, true);
          this.#throwIfAborted(signal, { op: 'put', stage: 'before-stage-write', hash, digest, path, bytes: bytes.byteLength });
          const stagedFileName = this.#stagedFileName(hash, abortContext.opSeq);
          const stagedPath = this.#stagedBlockPath(hash, stagedFileName);
          staging = { staged: true, fileName: stagedFileName, path: stagedPath, finalPath: path, verified: false, published: false, cleanup: null, stageSessionId: this.#stageSessionId };
          activeStagedKey = this.#markActiveStagedWrite(hash, stagedFileName, stagedPath, abortContext.opSeq);
          this.stats.stagedPuts += 1;
          this.#trace?.emit('storage:opfs-block-staged-write-start', { store: this.name, digest, hash, stagedPath, finalPath: path, fileName: stagedFileName, bytes: bytes.byteLength });
          writer = await this.#writeBlockBytes(bucket, stagedFileName, bytes, { digest, hash, label: fields.label ?? null, signal, purpose: 'stage', path: stagedPath });
          const stagedBytes = await this.#readNamedBlockBytes(bucket, stagedFileName, { signal, op: 'put', hash, digest, path: stagedPath, stage: 'staged-block' });
          this.#throwIfAborted(signal, { op: 'put', stage: 'before-staged-digest', hash, digest, path: stagedPath, bytes: stagedBytes.byteLength });
          const stagedHash = await digestBytesHexLocal(stagedBytes);
          this.#throwIfAborted(signal, { op: 'put', stage: 'after-staged-digest', hash, digest, path: stagedPath, bytes: stagedBytes.byteLength });
          this.stats.stagedWriteVerifications += 1;
          if (stagedHash !== hash || stagedBytes.byteLength !== bytes.byteLength) {
            this.stats.stagedVerifyFailures += 1;
            throw storageError('BRT_OPFS_STAGED_WRITE_VERIFY_FAILED', 'OPFS staged block write did not match the target content-addressed digest before publish', { store: this.name, prefix: this.prefix, digest, hash, stagedDigest: `sha256:${stagedHash}`, stagedPath, path, stagedBytes: stagedBytes.byteLength, expectedBytes: bytes.byteLength });
          }
          staging.verified = true;
          this.#trace?.emit('storage:opfs-block-staged-write-verified', { store: this.name, digest, hash, stagedPath, finalPath: path, fileName: stagedFileName, bytes: stagedBytes.byteLength });
          this.#throwIfAborted(signal, { op: 'put', stage: 'before-final-publish', hash, digest, path, stagedPath, bytes: stagedBytes.byteLength });
          rollbackOwnsFinalBlock = true;
          writer = await this.#writeBlockBytes(bucket, fileName, stagedBytes, { digest, hash, label: fields.label ?? null, signal, purpose: 'publish-final', path });
          this.stats.stagedPublishWrites += 1;
          staging.published = true;
          this.#trace?.emit('storage:opfs-block-staged-publish', { store: this.name, digest, hash, stagedPath, finalPath: path, fileName: stagedFileName, bytes: stagedBytes.byteLength });
          if (this.verifyAfterWrite) {
            const final = await this.#inspectExistingBlock(hash, { source: 'post-put-verify', emitValid: true, signal });
            this.stats.postWriteVerifications += 1;
            if (!final.ok) {
              throw storageError('BRT_OPFS_POST_WRITE_VERIFY_FAILED', 'OPFS block post-write checksum verification failed', { store: this.name, prefix: this.prefix, digest, hash, path, final, staging: { ...staging } });
            }
          }
          staging.cleanup = await this.#cleanupStagedWrite(hash, stagedFileName, { reason: 'staged-put-published' });
          if (activeStagedKey) { this.#clearActiveStagedWrite(activeStagedKey, 'put-published'); activeStagedKey = null; }
        }
        this.stats.puts += 1;
        if (duplicate) this.stats.duplicatePuts += 1;
        const ref = createBlockRef(hash, { bytes: bytes.byteLength, backend: this.provider, path, label: fields.label ?? null });
        const stagingReceipt = staging ? Object.freeze({ ...staging, cleanup: staging.cleanup ? Object.freeze({ ...staging.cleanup }) : null }) : null;
        this.#trace?.emit('storage:opfs-block-put', { store: this.name, digest, hash, bytes: bytes.byteLength, duplicate, repairedCorrupt, repair, budget, path, label: ref.label, writerMode: writer?.mode ?? null, exclusiveWriterFallback: writer?.fallback ?? false, verifiedAfterWrite: !duplicate && this.verifyAfterWrite, staging: stagingReceipt });
        return Object.freeze({ ref, digest, hash, bytes: bytes.byteLength, duplicate, repairedCorrupt, repair, budget, path, staging: stagingReceipt });
      } catch (error) {
        let stagingCleanup = null;
        if (staging?.fileName) {
          stagingCleanup = await this.#cleanupStagedWrite(hash, staging.fileName, { reason: 'failed-staged-put-cleanup', ignoreClosed: true });
          staging.cleanup = stagingCleanup;
        }
        const rollback = await this.#rollbackFailedPut(hash, { allowed: rollbackOwnsFinalBlock, reason: duplicate ? 'pre-existing-duplicate-block-not-owned-by-put' : 'final-block-not-created-by-put', rollbackDigest: digest, path });
        const stagingReceipt = staging ? Object.freeze({ ...staging, cleanup: stagingCleanup ? Object.freeze({ ...stagingCleanup }) : (staging.cleanup ? Object.freeze({ ...staging.cleanup }) : null) }) : null;
        if (activeStagedKey) { this.#clearActiveStagedWrite(activeStagedKey, 'put-failed'); activeStagedKey = null; }
        const wrapped = wrapOpfsPutError(error, { store: this.name, prefix: this.prefix, digest, hash, path, bytes: bytes.byteLength, label: fields.label ?? null, repairedCorrupt, budget, rollbackOwnsFinalBlock, staging: stagingReceipt }, rollback);
        this.stats.putFailures += 1;
        if (wrapped.code === 'BRT_OPFS_QUOTA_EXCEEDED') this.stats.quotaRejects += 1;
        this.#trace?.emit('storage:opfs-block-put-error', { store: this.name, prefix: this.prefix, digest, hash, bytes: bytes.byteLength, path, error: wrapped.detail });
        throw wrapped;
      }
    } finally {
      if (activeStagedKey) this.#clearActiveStagedWrite(activeStagedKey, 'put-finally');
      this.#endOperation(abortContext);
    }
  }

  async get(refOrDigest, options = {}) {
    const abortContext = this.#beginOperation(options, 'get');
    const signal = abortContext.signal;
    try {
      this.#throwIfAborted(signal, { op: 'get', stage: 'before-ref-parse' });
      const hash = blockKeyFromRef(refOrDigest);
      const digest = `sha256:${hash}`;
      const stored = await this.#readBlockBytes(hash, { signal, op: 'get', existingOnly: true });
      this.#throwIfAborted(signal, { op: 'get', stage: 'before-digest', hash, digest });
      const actualHash = await digestBytesHexLocal(stored);
      this.#throwIfAborted(signal, { op: 'get', stage: 'after-digest', hash, digest });
      if (actualHash !== hash) {
        this.stats.checksumFailures += 1;
        this.stats.corruptBlocksDetected += 1;
        this.#trace?.emit('storage:opfs-block-checksum-error', { store: this.name, digest, actualDigest: `sha256:${actualHash}`, bytes: stored.byteLength, path: this.blockPath(hash) });
        throw storageError('BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'OPFS block checksum mismatch', { store: this.name, digest, actualDigest: `sha256:${actualHash}`, bytes: stored.byteLength, path: this.blockPath(hash) });
      }
      this.stats.gets += 1;
      this.#trace?.emit('storage:opfs-block-get', { store: this.name, digest, bytes: stored.byteLength, path: this.blockPath(hash) });
      return stored;
    } finally {
      this.#endOperation(abortContext);
    }
  }

  async has(refOrDigest, options = {}) {
    const abortContext = this.#beginOperation(options, 'has');
    const signal = abortContext.signal;
    try {
      this.#throwIfAborted(signal, { op: 'has', stage: 'before-ref-parse' });
      const hash = blockKeyFromRef(refOrDigest);
      this.stats.has += 1;
      let present;
      let ok = null;
      let actualDigest = null;
      let bytes = 0;
      if (this.verifyOnHas) {
        const inspection = await this.#inspectExistingBlock(hash, { source: 'has', signal, existingOnly: true });
        present = inspection.present && inspection.ok;
        ok = inspection.ok;
        actualDigest = inspection.actualDigest;
        bytes = inspection.bytes;
      } else {
        try {
          this.#throwIfAborted(signal, { op: 'has', stage: 'before-open-bucket', hash });
          const bucket = await this.#existingBucket(hash, { signal, op: 'has' });
          this.#throwIfAborted(signal, { op: 'has', stage: 'before-get-file-handle', hash });
          await bucket.getFileHandle(`${hash}.blk`, { create: false });
          present = true;
        } catch (error) {
          if (error?.name !== 'NotFoundError') throw error;
          this.#recordNoCreateMiss(hash, { op: 'has', stage: 'file-exists' });
          present = false;
        }
      }
      this.#trace?.emit('storage:opfs-block-has', { store: this.name, digest: `sha256:${hash}`, present, ok, actualDigest, bytes, verified: this.verifyOnHas });
      return present;
    } finally {
      this.#endOperation(abortContext);
    }
  }

  async delete(refOrDigest, options = {}) {
    const abortContext = this.#beginOperation(options, 'delete');
    const signal = abortContext.signal;
    try {
      this.#throwIfAborted(signal, { op: 'delete', stage: 'before-ref-parse' });
      const hash = blockKeyFromRef(refOrDigest);
      const digest = `sha256:${hash}`;
      const deleted = await this.#deleteBlockFile(hash, { reason: 'delete', signal, op: 'delete' });
      this.stats.deletes += 1;
      this.#trace?.emit('storage:opfs-block-delete', { store: this.name, digest, deleted, path: this.blockPath(hash) });
      return deleted;
    } finally {
      this.#endOperation(abortContext);
    }
  }

  async verify(refOrDigest, options = {}) {
    const abortContext = this.#beginOperation(options, 'verify');
    const signal = abortContext.signal;
    try {
      this.#throwIfAborted(signal, { op: 'verify', stage: 'before-ref-parse' });
      const hash = blockKeyFromRef(refOrDigest);
      const inspection = await this.#inspectExistingBlock(hash, { source: 'verify', signal, existingOnly: true });
      this.stats.verifies += 1;
      return Object.freeze({ digest: `sha256:${hash}`, present: inspection.present, ok: inspection.present && inspection.ok, bytes: inspection.bytes, path: this.blockPath(hash), actualDigest: inspection.actualDigest, reason: inspection.present && !inspection.ok ? 'checksum-mismatch' : null });
    } finally {
      this.#endOperation(abortContext);
    }
  }


  async recoverStagedWrites(options = {}) {
    const abortContext = this.#beginOperation(options, 'recoverStagedWrites');
    const signal = abortContext.signal;
    const reason = typeof options?.reason === 'string' && options.reason.length ? options.reason : 'recover-staged-writes';
    const failOnError = options?.failOnError !== false;
    const maxDeletes = options?.maxDeletes === undefined || options?.maxDeletes === null ? Infinity : Number(options.maxDeletes);
    if (!(maxDeletes === Infinity || (Number.isFinite(maxDeletes) && maxDeletes >= 0))) {
      this.#endOperation(abortContext);
      throw storageError('BRT_OPFS_STAGED_RECOVERY_INVALID', 'OPFS staged recovery maxDeletes must be a non-negative finite number or omitted', { store: this.name, prefix: this.prefix, maxDeletes: options?.maxDeletes });
    }
    const report = {
      store: this.name,
      provider: this.provider,
      prefix: this.prefix,
      reason,
      prefixMissing: false,
      truncated: false,
      directoriesScanned: 0,
      filesScanned: 0,
      candidates: 0,
      deleted: 0,
      misses: 0,
      skipped: 0,
      activeSkipped: 0,
      failures: 0,
      deletedPaths: [],
      skippedPaths: [],
      errors: []
    };
    const pushSkip = (path, fileName, skipReason, hash = null) => {
      report.skipped += 1;
      this.stats.stagedRecoverySkips += 1;
      report.skippedPaths.push(Object.freeze({ path, fileName, reason: skipReason, hash }));
      this.#trace?.emit('storage:opfs-block-staged-recovery-skip', { store: this.name, prefix: this.prefix, path, fileName, reason: skipReason, hash });
    };
    try {
      this.#throwIfAborted(signal, { op: 'recoverStagedWrites', stage: 'before-open-prefix' });
      let prefixRoot;
      try {
        prefixRoot = await this.#openExistingPrefix({ signal, op: 'recoverStagedWrites' });
      } catch (error) {
        if (error?.name === 'NotFoundError') {
          report.prefixMissing = true;
          this.stats.stagedRecoverySweeps += 1;
          this.#trace?.emit('storage:opfs-block-staged-recovery', { store: this.name, prefix: this.prefix, ...report });
          return Object.freeze({ ...report, deletedPaths: Object.freeze(report.deletedPaths), skippedPaths: Object.freeze(report.skippedPaths), errors: Object.freeze(report.errors) });
        }
        throw error;
      }
      const firstLevel = await this.#directoryEntries(prefixRoot, { signal, op: 'recoverStagedWrites', path: this.prefix });
      report.directoriesScanned += 1;
      this.stats.stagedRecoveryDirectoriesScanned += 1;
      for (const [firstName, firstHandle] of firstLevel) {
        if (!/^[0-9a-f]{2}$/.test(firstName) || firstHandle?.kind === 'file') {
          pushSkip(`${this.prefix}/${firstName}`, firstName, firstHandle?.kind === 'file' ? 'top-level-file' : 'non-hash-first-bucket');
          continue;
        }
        const firstPath = `${this.prefix}/${firstName}`;
        const secondLevel = await this.#directoryEntries(firstHandle, { signal, op: 'recoverStagedWrites', path: firstPath });
        report.directoriesScanned += 1;
        this.stats.stagedRecoveryDirectoriesScanned += 1;
        for (const [secondName, secondHandle] of secondLevel) {
          if (!/^[0-9a-f]{2}$/.test(secondName) || secondHandle?.kind === 'file') {
            pushSkip(`${firstPath}/${secondName}`, secondName, secondHandle?.kind === 'file' ? 'first-bucket-file' : 'non-hash-second-bucket');
            continue;
          }
          const bucketPath = `${firstPath}/${secondName}`;
          const fileRows = await this.#directoryEntries(secondHandle, { signal, op: 'recoverStagedWrites', path: bucketPath });
          report.directoriesScanned += 1;
          this.stats.stagedRecoveryDirectoriesScanned += 1;
          for (const [fileName, fileHandle] of fileRows) {
            const path = `${bucketPath}/${fileName}`;
            if (fileHandle?.kind && fileHandle.kind !== 'file') {
              pushSkip(path, fileName, 'nested-directory-in-block-bucket');
              continue;
            }
            report.filesScanned += 1;
            this.stats.stagedRecoveryFilesScanned += 1;
            const match = this.#isStagedFileInExpectedBucket(fileName, firstName, secondName);
            if (!match.match) {
              if (match.hash) pushSkip(path, fileName, match.reason, match.hash);
              continue;
            }
            report.candidates += 1;
            this.stats.stagedRecoveryCandidates += 1;
            if (this.#isActiveStagedWrite(match.hash, fileName)) {
              report.activeSkipped += 1;
              this.stats.stagedRecoveryActiveSkips += 1;
              pushSkip(path, fileName, 'active-staged-write', match.hash);
              continue;
            }
            if (report.deleted >= maxDeletes) {
              report.truncated = true;
              pushSkip(path, fileName, 'max-deletes-reached', match.hash);
              continue;
            }
            try {
              this.#throwIfAborted(signal, { op: 'recoverStagedWrites', stage: 'before-remove-staged-temp', hash: match.hash, path, fileName, reason });
              await secondHandle.removeEntry(fileName);
              report.deleted += 1;
              this.stats.stagedRecoveryDeletes += 1;
              report.deletedPaths.push(Object.freeze({ path, fileName, hash: match.hash }));
              this.#trace?.emit('storage:opfs-block-staged-recovery-delete', { store: this.name, prefix: this.prefix, digest: `sha256:${match.hash}`, hash: match.hash, path, fileName, reason });
            } catch (error) {
              if (error?.name === 'NotFoundError') {
                report.misses += 1;
                this.stats.stagedRecoveryMisses += 1;
                this.#trace?.emit('storage:opfs-block-staged-recovery-miss', { store: this.name, prefix: this.prefix, digest: `sha256:${match.hash}`, hash: match.hash, path, fileName, reason });
                continue;
              }
              const detail = classifyOpfsBlockStoreError(error, { store: this.name, prefix: this.prefix, digest: `sha256:${match.hash}`, hash: match.hash, path, fileName, stagedRecovery: true, reason });
              report.failures += 1;
              this.stats.stagedRecoveryFailures += 1;
              report.errors.push(Object.freeze({ path, fileName, hash: match.hash, error: detail }));
              this.#trace?.emit('storage:opfs-block-staged-recovery-error', { store: this.name, prefix: this.prefix, digest: `sha256:${match.hash}`, hash: match.hash, path, fileName, error: detail, reason });
              if (failOnError) throw storageError('BRT_OPFS_STAGED_RECOVERY_FAILED', 'OPFS staged recovery failed while deleting an orphan staged temp file', { store: this.name, prefix: this.prefix, reason, report: { ...report, deletedPaths: [...report.deletedPaths], skippedPaths: [...report.skippedPaths], errors: [...report.errors] } });
            }
          }
        }
      }
      this.stats.stagedRecoverySweeps += 1;
      const frozen = Object.freeze({ ...report, deletedPaths: Object.freeze(report.deletedPaths), skippedPaths: Object.freeze(report.skippedPaths), errors: Object.freeze(report.errors) });
      this.#trace?.emit('storage:opfs-block-staged-recovery', { store: this.name, prefix: this.prefix, ...frozen });
      return frozen;
    } finally {
      this.#endOperation(abortContext);
    }
  }

  async estimate(options = {}) {
    const abortContext = this.#beginOperation(options, 'estimate');
    const signal = abortContext.signal;
    try {
      this.#throwIfAborted(signal, { op: 'estimate', stage: 'before-estimate' });
      this.stats.estimateCalls += 1;
      if (typeof globalThis.navigator?.storage?.estimate !== 'function') return Object.freeze({ quota: null, usage: null, usageDetails: null });
      const estimate = await globalThis.navigator.storage.estimate();
      this.#throwIfAborted(signal, { op: 'estimate', stage: 'after-estimate' });
      this.#trace?.emit('storage:opfs-block-estimate', { store: this.name, quota: estimate.quota ?? null, usage: estimate.usage ?? null, usageDetails: estimate.usageDetails ?? null });
      return Object.freeze({ quota: estimate.quota ?? null, usage: estimate.usage ?? null, usageDetails: estimate.usageDetails ?? null });
    } finally {
      this.#endOperation(abortContext);
    }
  }

  async cleanupForTest(options = {}) {
    const abortContext = this.#beginOperation(options, 'cleanupForTest');
    const signal = abortContext.signal;
    try {
      this.#throwIfAborted(signal, { op: 'cleanupForTest', stage: 'before-cleanup' });
      this.stats.cleanupCalls += 1;
      try {
        const originRoot = await globalThis.navigator.storage.getDirectory();
        const parts = this.prefix.split('/');
        let dir = originRoot;
        for (const part of parts.slice(0, -1)) {
          this.#throwIfAborted(signal, { op: 'cleanupForTest', stage: 'before-open-parent', part });
          dir = await dir.getDirectoryHandle(part, { create: false });
        }
        this.#throwIfAborted(signal, { op: 'cleanupForTest', stage: 'before-remove-prefix' });
        await dir.removeEntry(parts.at(-1), { recursive: true });
        this.#rootPromise = null;
        this.#opened = false;
        this.#trace?.emit('storage:opfs-block-cleanup', { store: this.name, prefix: this.prefix, deleted: true, reopenedRequired: true });
        return true;
      } catch (error) {
        if (error?.name === 'NotFoundError') {
          this.#rootPromise = null;
          this.#opened = false;
          this.#trace?.emit('storage:opfs-block-cleanup', { store: this.name, prefix: this.prefix, deleted: false, reopenedRequired: true });
          return false;
        }
        throw error;
      }
    } finally {
      this.#endOperation(abortContext);
    }
  }

  close(reason = 'opfs-block-store-close') {
    void this.closeAsync({ reason });
    return this.snapshot();
  }

  async closeAsync({ reason = 'opfs-block-store-close' } = {}) {
    this.stats.closeCalls += 1;
    const wasClosed = this.#closed;
    const wasOpened = this.#opened;
    const inFlightAtClose = this.#inFlightOperations;
    if (!wasClosed && this.#closeController && !this.#closeController.signal.aborted) {
      this.stats.closeAbortSignals += 1;
      try {
        this.#closeController.abort(storageError('BRT_OPFS_STORE_CLOSED', `OPFS block-store ${this.name} closed while operations may be in flight`, { store: this.name, prefix: this.prefix, reason, inFlightAtClose }));
      } catch {
        this.#closeController.abort();
      }
    }
    this.#closed = true;
    this.#rootPromise = null;
    this.#opened = false;
    const report = Object.freeze({
      disposition: wasClosed ? 'already-closed' : 'closed',
      store: this.name,
      provider: this.provider,
      prefix: this.prefix,
      openedBeforeClose: wasOpened,
      inFlightAtClose,
      inFlightAfterClose: this.#inFlightOperations,
      available: this.available,
      reason,
      stats: { ...this.stats }
    });
    this.#trace?.emit('storage:opfs-blockstore-close', { store: this.name, provider: this.provider, prefix: this.prefix, disposition: report.disposition, openedBeforeClose: wasOpened, inFlightAtClose, reason });
    return report;
  }

  snapshot() {
    return Object.freeze({
      name: this.name,
      provider: this.provider,
      prefix: this.prefix,
      opened: this.#opened,
      closed: this.#closed,
      inFlightOperations: this.#inFlightOperations,
      activeStagedWrites: this.#activeStagedWrites.size,
      stageSessionId: this.#stageSessionId,
      available: this.available,
      verifyExistingBlocksOnPut: this.verifyExistingBlocksOnPut,
      verifyAfterWrite: this.verifyAfterWrite,
      verifyOnHas: this.verifyOnHas,
      repairCorruptOnPut: this.repairCorruptOnPut,
      exclusiveWriters: this.exclusiveWriters,
      writeBudgetGuard: this.writeBudgetGuard,
      stats: { ...this.stats }
    });
  }
}

export function createOpfsAsyncBlockStore(config = {}) {
  return new OpfsAsyncBlockStore(config);
}
