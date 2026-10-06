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

function abortSignalFromOptions(options = {}) {
  const signal = options?.signal ?? options?.abortSignal ?? null;
  if (signal == null) return null;
  if (typeof signal !== 'object' || typeof signal.aborted !== 'boolean') {
    throw storageError('BRT_OPFS_ABORT_SIGNAL_INVALID', 'OPFS block-store signal must be an AbortSignal-compatible object or null', { signalType: typeof signal });
  }
  return signal;
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
      writeBudgetChecks: 0,
      writeBudgetRejects: 0,
      writeBudgetDuplicateBypasses: 0,
      writeBudgetEstimateUnavailable: 0,
      writeBudgetEstimateFailures: 0,
      rollbackOwnershipSkips: 0,
      rollbackValidBlockPreserves: 0,
      rollbackIntegrityChecks: 0,
      rollbackIntegrityCheckFailures: 0
    };
    this.#trace?.emit('storage:opfs-blockstore-create', { name: this.name, provider: this.provider, prefix: this.prefix, verifyExistingBlocksOnPut: this.verifyExistingBlocksOnPut, verifyAfterWrite: this.verifyAfterWrite, verifyOnHas: this.verifyOnHas, repairCorruptOnPut: this.repairCorruptOnPut, exclusiveWriters: this.exclusiveWriters, explicitAbortSignals: true, writeBudgetGuard: this.writeBudgetGuard });
  }

  get available() {
    return typeof globalThis.navigator?.storage?.getDirectory === 'function';
  }

  async open() {
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

  async #bucket(hash, create = true) {
    const root = await this.open();
    const a = await root.getDirectoryHandle(hash.slice(0, 2), { create });
    return await a.getDirectoryHandle(hash.slice(2, 4), { create });
  }

  async #readBlockBytes(hash, { signal = null, op = 'read', existingOnly = false } = {}) {
    this.#throwIfAborted(signal, { op, stage: 'before-open-bucket', hash });
    const bucket = existingOnly ? await this.#existingBucket(hash, { signal, op }) : await this.#bucket(hash, false);
    this.#throwIfAborted(signal, { op, stage: 'before-open-file', hash });
    const file = await bucket.getFileHandle(`${hash}.blk`, { create: false });
    this.#throwIfAborted(signal, { op, stage: 'before-read-file', hash });
    const bytes = new Uint8Array(await (await file.getFile()).arrayBuffer());
    this.#throwIfAborted(signal, { op, stage: 'after-read-file', hash });
    return bytes;
  }

  async #inspectExistingBlock(hash, { source = 'integrity-check', emitValid = false, signal = null, existingOnly = false } = {}) {
    const digest = `sha256:${hash}`;
    const path = this.blockPath(hash);
    try {
      const bytes = await this.#readBlockBytes(hash, { signal, op: source, existingOnly });
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

  #signalFromOptions(options = {}, op = 'operation') {
    try {
      return abortSignalFromOptions(options);
    } catch (error) {
      this.stats.invalidAbortSignals += 1;
      this.#trace?.emit('storage:opfs-block-abort-signal-invalid', { store: this.name, op, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null } });
      throw error;
    }
  }

  #throwIfAborted(signal, context = {}) {
    if (!signal?.aborted) return;
    this.stats.abortRejects += 1;
    const detail = { store: this.name, prefix: this.prefix, ...context, reason: summarizeAbortReason(signal.reason) };
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

  async #openExistingPrefix({ signal = null, op = 'existing-prefix-open', hash = null } = {}) {
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

  async #existingBucket(hash, { signal = null, op = 'existing-bucket-open' } = {}) {
    const root = await this.#openExistingPrefix({ signal, op, hash });
    this.#throwIfAborted(signal, { op, stage: 'before-open-existing-first-bucket', hash });
    const a = await root.getDirectoryHandle(hash.slice(0, 2), { create: false });
    this.#throwIfAborted(signal, { op, stage: 'before-open-existing-second-bucket', hash });
    return await a.getDirectoryHandle(hash.slice(2, 4), { create: false });
  }

  async #deleteBlockFile(hash, { reason = 'delete', signal = null, op = 'delete' } = {}) {
    const digest = `sha256:${hash}`;
    const path = this.blockPath(hash);
    try {
      this.#throwIfAborted(signal, { op, stage: 'before-open-bucket', hash, digest, path, reason });
      const bucket = await this.#bucket(hash, false);
      this.#throwIfAborted(signal, { op, stage: 'before-remove-entry', hash, digest, path, reason });
      await bucket.removeEntry(`${hash}.blk`);
      this.#trace?.emit('storage:opfs-block-delete-file', { store: this.name, digest, hash, deleted: true, path, reason });
      return true;
    } catch (error) {
      if (error?.name === 'NotFoundError') {
        this.#trace?.emit('storage:opfs-block-delete-file', { store: this.name, digest, hash, deleted: false, path, reason });
        return false;
      }
      throw error;
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
      integrity = await this.#inspectExistingBlock(hash, { source: 'failed-put-rollback-preserve-check', existingOnly: true });
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
      const deleted = await this.#deleteBlockFile(hash, { reason: 'failed-put-rollback' });
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

  async #writeBlockBytes(bucket, fileName, bytes, { digest, hash, label, signal = null }) {
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
    this.#trace?.emit('storage:opfs-block-write-close', { store: this.name, digest, hash, bytes: bytes.byteLength, writerMode: writer.mode, exclusiveWriterFallback: writer.fallback, label });
    return writer;
  }

  async put(value, fields = {}, options = {}) {
    const signal = this.#signalFromOptions(options, 'put');
    this.#throwIfAborted(signal, { op: 'put', stage: 'before-digest' });
    const bytes = toOwnedUint8Array(value);
    const writeBudgetGuard = writeBudgetGuardForPut(this.writeBudgetGuard, options);
    let hash = null;
    let digest = null;
    let path = null;
    let budget = null;
    let repairedCorrupt = false;
    let repair = null;
    let writer = null;
    let rollbackOwnsFinalBlock = false;
    let duplicate = false;
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
        rollbackOwnsFinalBlock = true;
        writer = await this.#writeBlockBytes(bucket, fileName, bytes, { digest, hash, label: fields.label ?? null, signal });
        if (this.verifyAfterWrite) {
          const final = await this.#inspectExistingBlock(hash, { source: 'post-put-verify', emitValid: true, signal });
          this.stats.postWriteVerifications += 1;
          if (!final.ok) {
            throw storageError('BRT_OPFS_POST_WRITE_VERIFY_FAILED', 'OPFS block post-write checksum verification failed', { store: this.name, prefix: this.prefix, digest, hash, path, final });
          }
        }
      }
      this.stats.puts += 1;
      if (duplicate) this.stats.duplicatePuts += 1;
      const ref = createBlockRef(hash, { bytes: bytes.byteLength, backend: this.provider, path, label: fields.label ?? null });
      this.#trace?.emit('storage:opfs-block-put', { store: this.name, digest, hash, bytes: bytes.byteLength, duplicate, repairedCorrupt, repair, budget, path, label: ref.label, writerMode: writer?.mode ?? null, exclusiveWriterFallback: writer?.fallback ?? false, verifiedAfterWrite: !duplicate && this.verifyAfterWrite });
      return Object.freeze({ ref, digest, hash, bytes: bytes.byteLength, duplicate, repairedCorrupt, repair, budget, path });
    } catch (error) {
      const rollback = await this.#rollbackFailedPut(hash, { allowed: rollbackOwnsFinalBlock, reason: duplicate ? 'pre-existing-duplicate-block-not-owned-by-put' : 'final-block-not-created-by-put', rollbackDigest: digest, path });
      const wrapped = wrapOpfsPutError(error, { store: this.name, prefix: this.prefix, digest, hash, path, bytes: bytes.byteLength, label: fields.label ?? null, repairedCorrupt, budget, rollbackOwnsFinalBlock }, rollback);
      this.stats.putFailures += 1;
      if (wrapped.code === 'BRT_OPFS_QUOTA_EXCEEDED') this.stats.quotaRejects += 1;
      this.#trace?.emit('storage:opfs-block-put-error', { store: this.name, prefix: this.prefix, digest, hash, bytes: bytes.byteLength, path, error: wrapped.detail });
      throw wrapped;
    }
  }

  async get(refOrDigest, options = {}) {
    const signal = this.#signalFromOptions(options, 'get');
    this.#throwIfAborted(signal, { op: 'get', stage: 'before-ref-parse' });
    const hash = blockKeyFromRef(refOrDigest);
    const digest = `sha256:${hash}`;
    const stored = await this.#readBlockBytes(hash, { signal, op: 'get' });
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
  }

  async has(refOrDigest, options = {}) {
    const signal = this.#signalFromOptions(options, 'has');
    this.#throwIfAborted(signal, { op: 'has', stage: 'before-ref-parse' });
    const hash = blockKeyFromRef(refOrDigest);
    this.stats.has += 1;
    let present;
    let ok = null;
    let actualDigest = null;
    let bytes = 0;
    if (this.verifyOnHas) {
      const inspection = await this.#inspectExistingBlock(hash, { source: 'has', signal });
      present = inspection.present && inspection.ok;
      ok = inspection.ok;
      actualDigest = inspection.actualDigest;
      bytes = inspection.bytes;
    } else {
      present = await missingAsFalse(async () => {
        this.#throwIfAborted(signal, { op: 'has', stage: 'before-open-bucket', hash });
        const bucket = await this.#bucket(hash, false);
        this.#throwIfAborted(signal, { op: 'has', stage: 'before-get-file-handle', hash });
        await bucket.getFileHandle(`${hash}.blk`, { create: false });
      });
    }
    this.#trace?.emit('storage:opfs-block-has', { store: this.name, digest: `sha256:${hash}`, present, ok, actualDigest, bytes, verified: this.verifyOnHas });
    return present;
  }

  async delete(refOrDigest, options = {}) {
    const signal = this.#signalFromOptions(options, 'delete');
    this.#throwIfAborted(signal, { op: 'delete', stage: 'before-ref-parse' });
    const hash = blockKeyFromRef(refOrDigest);
    const digest = `sha256:${hash}`;
    const deleted = await this.#deleteBlockFile(hash, { reason: 'delete', signal, op: 'delete' });
    this.stats.deletes += 1;
    this.#trace?.emit('storage:opfs-block-delete', { store: this.name, digest, deleted, path: this.blockPath(hash) });
    return deleted;
  }

  async verify(refOrDigest, options = {}) {
    const signal = this.#signalFromOptions(options, 'verify');
    this.#throwIfAborted(signal, { op: 'verify', stage: 'before-ref-parse' });
    const hash = blockKeyFromRef(refOrDigest);
    const inspection = await this.#inspectExistingBlock(hash, { source: 'verify', signal });
    this.stats.verifies += 1;
    return Object.freeze({ digest: `sha256:${hash}`, present: inspection.present, ok: inspection.present && inspection.ok, bytes: inspection.bytes, path: this.blockPath(hash), actualDigest: inspection.actualDigest, reason: inspection.present && !inspection.ok ? 'checksum-mismatch' : null });
  }

  async estimate(options = {}) {
    const signal = this.#signalFromOptions(options, 'estimate');
    this.#throwIfAborted(signal, { op: 'estimate', stage: 'before-estimate' });
    this.stats.estimateCalls += 1;
    if (typeof globalThis.navigator?.storage?.estimate !== 'function') return Object.freeze({ quota: null, usage: null, usageDetails: null });
    const estimate = await globalThis.navigator.storage.estimate();
    this.#throwIfAborted(signal, { op: 'estimate', stage: 'after-estimate' });
    this.#trace?.emit('storage:opfs-block-estimate', { store: this.name, quota: estimate.quota ?? null, usage: estimate.usage ?? null, usageDetails: estimate.usageDetails ?? null });
    return Object.freeze({ quota: estimate.quota ?? null, usage: estimate.usage ?? null, usageDetails: estimate.usageDetails ?? null });
  }

  async cleanupForTest(options = {}) {
    const signal = this.#signalFromOptions(options, 'cleanupForTest');
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
  }

  snapshot() {
    return Object.freeze({
      name: this.name,
      provider: this.provider,
      prefix: this.prefix,
      opened: this.#opened,
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
