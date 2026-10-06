import { createWatermarkAdmissionController } from './admission-control.mjs';
import { createCrossLaneScheduler } from './cross-lane-scheduler.mjs';
import { createRuntimeCoreBlockStoreLaneAdapter, validateRuntimeCoreBlockStoreLaneAdapterSnapshot } from './runtime-core-lane-adapter.mjs';
import { diagnoseBrowserStoragePosture, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT } from './browser-storage-posture.mjs';
import { createBrowserStorageRecoveryGuidance, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT } from './browser-storage-recovery-guidance.mjs';
export const VERSION = '0.0.125';
export const REVISION = 'rev0125';
export const BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT = 'browserrt.runtime-core-entry.v1';
export const BROWSERRT_RUNTIME_CORE_EXPORTS = Object.freeze([
  'VERSION',
  'REVISION',
  'BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT',
  'BROWSERRT_RUNTIME_CORE_EXPORTS',
  'detectCapabilities',
  'availableCapabilityTierNames',
  'boot',
  'bootRuntimeCore',
  'createObjectRef',
  'createTransferObjectRef',
  'createTransferObject',
  'createBlockObjectRef',
  'createEnvelope',
  'digestBytesHex',
  'createMemoryBlockStore',
  'TraceLog',
  'diagnoseBrowserStoragePosture',
  'createBrowserStorageRecoveryGuidance',
  'BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT',
  'BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT',
  'validateBlockStoreLaneAdapterSnapshot'
]);
export {
  BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT,
  BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT,
  diagnoseBrowserStoragePosture,
  createBrowserStorageRecoveryGuidance
};
export const validateBlockStoreLaneAdapterSnapshot = validateRuntimeCoreBlockStoreLaneAdapterSnapshot;
const CAPABILITY_TIERS = Object.freeze([
  { id: 0, name: 'basic', meaning: 'main thread plus structured clone fallback' },
  { id: 1, name: 'workered', meaning: 'dedicated workers and transferables' },
  { id: 2, name: 'isolated', meaning: 'SharedArrayBuffer and Atomics in cross-origin-isolated contexts' },
  { id: 3, name: 'persistent', meaning: 'OPFS block store and storage worker paths' },
  { id: 4, name: 'accelerated', meaning: 'WebGPU and other accelerated adapter paths' },
  { id: 5, name: 'mesh', meaning: 'cross-tab coordination through same-origin primitives' }
]);
const OBJECT_REF_KINDS = new Set(['inline', 'transfer', 'shared', 'opfs', 'stream', 'gpu', 'block']);
let NEXT_ID = 1;
function nextId(prefix) {
  const id = NEXT_ID++;
  return `${prefix}:${id.toString(36)}`;
}
function environmentName(g = globalThis) {
  if (typeof g.window === 'object' && g.window === g) return 'browser-window';
  if (g.process?.versions?.node) return 'node';
  return 'worker-or-unknown';
}
function toOwnedUint8Array(value) {
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  if (typeof value === 'string') return new TextEncoder().encode(value);
  return new TextEncoder().encode(JSON.stringify(value));
}
function blockKeyFromRef(refOrDigest) {
  if (typeof refOrDigest === 'string') {
    if (/^[0-9a-f]{64}$/.test(refOrDigest)) return `sha256:${refOrDigest}`;
    if (/^sha256:[0-9a-f]{64}$/.test(refOrDigest)) return refOrDigest;
  }
  if (refOrDigest && typeof refOrDigest === 'object') {
    if (typeof refOrDigest.digest === 'string') return blockKeyFromRef(refOrDigest.digest);
    if (typeof refOrDigest.hash === 'string') return blockKeyFromRef(refOrDigest.hash);
    if (typeof refOrDigest.id === 'string') return blockKeyFromRef(refOrDigest.id.replace(/^block:/, ''));
  }
  throw new Error('Block ref must be a sha256 digest string or block object ref');
}
function storageError(code, message, detail = {}) {
  const error = new Error(message);
  error.name = 'BrowserRTStorageError';
  error.code = code;
  error.detail = detail;
  return error;
}
function isAbortSignalLike(value) {
  return value && typeof value === 'object' && typeof value.aborted === 'boolean' && typeof value.addEventListener === 'function';
}
function abortSignalFromOptions(options = {}) {
  if (!options || typeof options !== 'object') return null;
  return options.signal ?? options.abortSignal ?? null;
}
function abortErrorFromSignal(signal, fallbackMessage = 'BrowserRT runtime-core operation aborted') {
  if (!isAbortSignalLike(signal)) return null;
  if (!signal.aborted) return null;
  if (typeof signal.throwIfAborted === 'function') {
    try { signal.throwIfAborted(); } catch (error) { return error; }
  }
  const reason = 'reason' in signal ? signal.reason : null;
  if (reason instanceof Error || (typeof DOMException !== 'undefined' && reason instanceof DOMException)) return reason;
  const error = storageError('BRT_RUNTIME_CORE_ABORTED', fallbackMessage, { reason: reason == null ? null : String(reason) });
  error.name = 'AbortError';
  return error;
}
function throwIfRuntimeCoreAborted(options = {}, fallbackMessage = 'BrowserRT runtime-core operation aborted') {
  const signal = abortSignalFromOptions(options);
  const error = abortErrorFromSignal(signal, fallbackMessage);
  if (error) throw error;
}
export function detectCapabilities(g = globalThis) {
  const nav = g.navigator || {};
  const storage = nav.storage || {};
  const scheduler = g.scheduler || {};
  const nodeLike = Boolean(g.process?.versions?.node);
  return Object.freeze({
    environment: environmentName(g),
    workers: typeof g.Worker === 'function' || nodeLike,
    moduleWorkers: typeof g.Worker === 'function' || nodeLike,
    transferableArrayBuffer: typeof g.ArrayBuffer === 'function',
    sharedArrayBuffer: typeof g.SharedArrayBuffer === 'function',
    atomics: typeof g.Atomics === 'object',
    crossOriginIsolated: Boolean(g.crossOriginIsolated),
    opfs: typeof storage.getDirectory === 'function',
    storageEstimate: typeof storage.estimate === 'function',
    storagePersisted: typeof storage.persisted === 'function',
    storagePersist: typeof storage.persist === 'function',
    webgpu: Boolean(nav.gpu),
    webnn: Boolean(nav.ml),
    offscreenCanvas: typeof g.OffscreenCanvas === 'function',
    webcodecs: typeof g.VideoEncoder === 'function' || typeof g.VideoDecoder === 'function',
    videoFrameTransfer: typeof g.VideoFrame === 'function',
    broadcastChannel: typeof g.BroadcastChannel === 'function',
    messageChannel: typeof g.MessageChannel === 'function',
    sharedWorker: typeof g.SharedWorker === 'function',
    serviceWorker: Boolean(nav.serviceWorker),
    webLocks: Boolean(nav.locks),
    schedulerPostTask: typeof scheduler.postTask === 'function',
    schedulerYield: typeof scheduler.yield === 'function',
    performanceObserver: typeof g.PerformanceObserver === 'function',
    measureMemory: Boolean(g.performance && typeof g.performance.measureUserAgentSpecificMemory === 'function')
  });
}
export function availableCapabilityTierNames(capabilities = detectCapabilities()) {
  const names = ['basic'];
  if (capabilities.workers && capabilities.transferableArrayBuffer) names.push('workered');
  if (capabilities.sharedArrayBuffer && capabilities.atomics && capabilities.crossOriginIsolated) names.push('isolated');
  if (capabilities.opfs) names.push('persistent');
  if (capabilities.webgpu) names.push('accelerated');
  if (capabilities.broadcastChannel && capabilities.webLocks) names.push('mesh');
  return names;
}
export function createObjectRef(kind, fields = {}) {
  if (!OBJECT_REF_KINDS.has(kind)) throw new Error(`Unsupported object ref kind: ${kind}`);
  const bytes = fields.bytes ?? fields.length ?? 0;
  if (!Number.isFinite(bytes) || bytes < 0) throw new Error('Object ref bytes/length must be a non-negative finite number');
  return Object.freeze({
    ...fields,
    kind,
    id: fields.id ?? nextId(kind),
    bytes,
    ownership: fields.ownership ?? (kind === 'transfer' ? 'owned-main' : 'unspecified'),
    createdAt: fields.createdAt ?? Date.now()
  });
}
export function createTransferObjectRef(buffer, fields = {}) {
  if (!(buffer instanceof ArrayBuffer)) throw new Error('createTransferObjectRef requires an ArrayBuffer');
  return createObjectRef('transfer', {
    ...fields,
    id: fields.id ?? nextId('transfer'),
    bytes: buffer.byteLength,
    transferType: 'ArrayBuffer',
    ownership: 'owned-main'
  });
}
export function createTransferObject(buffer, fields = {}) {
  const ref = createTransferObjectRef(buffer, fields);
  return Object.freeze({ ref, buffer, transferList: [buffer] });
}
export function createBlockObjectRef(hash, fields = {}) {
  if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) throw new Error('createBlockObjectRef requires a lowercase 64-character sha256 hex hash');
  return createObjectRef('block', {
    ...fields,
    id: fields.id ?? `block:sha256:${hash}`,
    digest: `sha256:${hash}`,
    hash,
    algorithm: 'sha256',
    backend: fields.backend ?? 'memory-block-store',
    ownership: fields.ownership ?? 'content-addressed-provider'
  });
}
export async function digestBytesHex(bytes) {
  const body = bytes instanceof ArrayBuffer ? bytes : toOwnedUint8Array(bytes);
  if (!globalThis.crypto?.subtle?.digest) throw new Error('BrowserRT runtime-core digest requires crypto.subtle.digest');
  const digest = await globalThis.crypto.subtle.digest('SHA-256', body);
  return Array.from(new Uint8Array(digest)).map((x) => x.toString(16).padStart(2, '0')).join('');
}
export function createEnvelope(op, fields = {}) {
  if (typeof op !== 'string' || op.length === 0) throw new Error('Envelope op must be a non-empty string');
  return Object.freeze({
    magic: 'BRT1',
    version: 1,
    id: fields.id ?? nextId('env'),
    parentId: fields.parentId ?? null,
    traceId: fields.traceId ?? null,
    op,
    lane: fields.lane ?? 'cpu',
    priority: fields.priority ?? 'user-visible',
    deadlineMs: fields.deadlineMs ?? 0,
    flags: fields.flags ?? 0,
    payloadRef: fields.payloadRef ?? null
  });
}
export class TraceLog {
  #events = [];
  #nextSeq = 1;
  #capacity;
  #droppedCount = 0;
  constructor({ capacity = 4096 } = {}) {
    if (!Number.isInteger(capacity) || capacity < 1) throw new Error('TraceLog capacity must be a positive integer');
    this.#capacity = capacity;
  }
  get capacity() { return this.#capacity; }
  get droppedCount() { return this.#droppedCount; }
  emit(kind, detail = {}) {
    if (typeof kind !== 'string' || kind.length === 0) throw new Error('TraceLog kind must be a non-empty string');
    if (!detail || typeof detail !== 'object' || Array.isArray(detail)) throw new Error('TraceLog detail must be an object');
    const event = Object.freeze({ ...detail, seq: this.#nextSeq++, t: Date.now(), kind });
    if (this.#events.length >= this.#capacity) {
      this.#events.shift();
      this.#droppedCount += 1;
    }
    this.#events.push(event);
    return event;
  }
  snapshot() { return this.#events.slice(); }
  find(kind) { return this.#events.filter((event) => event.kind === kind); }
  count(kind) { return this.find(kind).length; }
  kinds() { return [...new Set(this.#events.map((event) => event.kind))]; }
}
class BoundedChannel {
  #queue = [];
  #waiting = [];
  #closed = false;
  #trace;
  #droppedCount = 0;
  constructor({ label = 'runtime-core-channel', capacity = 16, overflow = 'fail', trace = null } = {}) {
    if (!Number.isInteger(capacity) || capacity < 1) throw new Error('channel capacity must be a positive integer');
    if (!['fail', 'drop-oldest', 'drop-newest'].includes(overflow)) throw new Error('channel overflow must be fail, drop-oldest, or drop-newest');
    this.label = label;
    this.capacity = capacity;
    this.overflow = overflow;
    this.#trace = trace;
    this.#trace?.emit('channel:create', { label, capacity, overflow });
  }
  async send(value) {
    if (this.#closed) throw new Error(`channel is closed: ${this.label}`);
    if (this.#waiting.length) {
      const resolve = this.#waiting.shift();
      resolve(value);
      this.#trace?.emit('channel:deliver', { label: this.label, queued: this.#queue.length });
      return Object.freeze({ accepted: true, disposition: 'delivered' });
    }
    if (this.#queue.length >= this.capacity) {
      if (this.overflow === 'drop-oldest') {
        this.#queue.shift();
        this.#droppedCount += 1;
        this.#trace?.emit('channel:drop-oldest', { label: this.label, droppedCount: this.#droppedCount });
      } else if (this.overflow === 'drop-newest') {
        this.#droppedCount += 1;
        this.#trace?.emit('channel:drop-newest', { label: this.label, droppedCount: this.#droppedCount });
        return Object.freeze({ accepted: false, disposition: 'dropped-newest', droppedCount: this.#droppedCount });
      } else throw new Error(`channel full: ${this.label}`);
    }
    this.#queue.push(value);
    this.#trace?.emit('channel:enqueue', { label: this.label, queued: this.#queue.length });
    return Object.freeze({ accepted: true, disposition: 'queued' });
  }
  async receive() {
    if (this.#queue.length) {
      const value = this.#queue.shift();
      this.#trace?.emit('channel:receive', { label: this.label, queued: this.#queue.length });
      return value;
    }
    if (this.#closed) return undefined;
    return new Promise((resolve) => this.#waiting.push(resolve));
  }
  close() {
    this.#closed = true;
    while (this.#waiting.length) this.#waiting.shift()(undefined);
    this.#trace?.emit('channel:close', { label: this.label, queued: this.#queue.length });
  }
  snapshot() { return Object.freeze({ label: this.label, capacity: this.capacity, queued: this.#queue.length, closed: this.#closed, droppedCount: this.#droppedCount }); }
}
class MemoryBlockStore {
  #blocks = new Map();
  #trace;
  #stringPayloadDigestHints = new Map();
  #duplicateHintLimit;
  constructor({ name = 'runtime-core-memory-block-store', provider = 'runtime-core-memory-provider-v1', quotaBytes = Number.POSITIVE_INFINITY, duplicateHintLimit = 256, trace = null } = {}) {
    const normalizedQuotaBytes = quotaBytes === Number.POSITIVE_INFINITY ? Number.POSITIVE_INFINITY : Number(quotaBytes);
    const normalizedDuplicateHintLimit = Number(duplicateHintLimit);
    if (normalizedQuotaBytes !== Number.POSITIVE_INFINITY && (!Number.isFinite(normalizedQuotaBytes) || normalizedQuotaBytes < 0)) throw new Error('MemoryBlockStore quotaBytes must be a non-negative finite number or Infinity');
    if (!Number.isInteger(normalizedDuplicateHintLimit) || normalizedDuplicateHintLimit < 0) throw new Error('MemoryBlockStore duplicateHintLimit must be an integer >= 0');
    this.name = name;
    this.provider = provider;
    this.quotaBytes = normalizedQuotaBytes;
    this.duplicateHintLimit = normalizedDuplicateHintLimit;
    this.#duplicateHintLimit = normalizedDuplicateHintLimit;
    this.createdAt = Date.now();
    this.#trace = trace;
    this.stats = { puts: 0, duplicatePuts: 0, gets: 0, has: 0, deletes: 0, verifies: 0, quotaRejects: 0, duplicateBudgetHits: 0, duplicateHintsCleared: 0 };
    this.#trace?.emit('storage:blockstore-create', { name, provider, quotaBytes, duplicateHintLimit: normalizedDuplicateHintLimit });
  }
  bytesUsed() {
    let total = 0;
    for (const entry of this.#blocks.values()) total += entry.bytes.byteLength;
    return total;
  }
  #rememberStringPayloadDigest(value, key) {
    if (typeof value !== 'string' || this.#duplicateHintLimit <= 0) return false;
    if (this.#stringPayloadDigestHints.has(value)) this.#stringPayloadDigestHints.delete(value);
    while (this.#stringPayloadDigestHints.size >= this.#duplicateHintLimit) {
      const oldest = this.#stringPayloadDigestHints.keys().next().value;
      this.#stringPayloadDigestHints.delete(oldest);
    }
    this.#stringPayloadDigestHints.set(value, key);
    return true;
  }
  #knownStringPayloadDigest(value) {
    if (typeof value !== 'string') return null;
    const key = this.#stringPayloadDigestHints.get(value) || null;
    return key && this.#blocks.has(key) ? key : null;
  }
  #forgetDuplicateHintsForDigest(key) {
    let cleared = 0;
    for (const [value, hintedKey] of [...this.#stringPayloadDigestHints.entries()]) {
      if (hintedKey !== key) continue;
      this.#stringPayloadDigestHints.delete(value);
      cleared += 1;
    }
    if (cleared > 0) this.stats.duplicateHintsCleared += cleared;
    return cleared;
  }
  estimatePutGrowth(value, options = {}) {
    throwIfRuntimeCoreAborted(options, `Block store put growth estimate aborted in ${this.name}`);
    const requestedBytes = Number.isFinite(options.requestedBytes) && Number(options.requestedBytes) >= 0
      ? Math.floor(Number(options.requestedBytes))
      : toOwnedUint8Array(value).byteLength;
    const duplicateDigest = this.#knownStringPayloadDigest(value);
    const duplicate = Boolean(duplicateDigest);
    if (duplicate) this.stats.duplicateBudgetHits += 1;
    return Object.freeze({
      available: true,
      checked: duplicate,
      duplicate,
      digest: duplicateDigest,
      requestedBytes,
      growthBytes: duplicate ? 0 : requestedBytes,
      reason: duplicate ? 'known-string-payload-duplicate' : 'duplicate-unknown'
    });
  }
  async put(value, fields = {}) {
    throwIfRuntimeCoreAborted(fields, `Block store put aborted in ${this.name}`);
    const bytes = toOwnedUint8Array(value);
    const hash = await digestBytesHex(bytes);
    throwIfRuntimeCoreAborted(fields, `Block store put aborted in ${this.name}`);
    const key = `sha256:${hash}`;
    const duplicate = this.#blocks.has(key);
    if (!duplicate && this.bytesUsed() + bytes.byteLength > this.quotaBytes) {
      this.stats.quotaRejects += 1;
      throw storageError('BRT_STORAGE_QUOTA_EXCEEDED', `Block store quota exceeded in ${this.name}`, { store: this.name, requestedBytes: bytes.byteLength, bytesUsed: this.bytesUsed(), quotaBytes: this.quotaBytes });
    }
    if (!duplicate) this.#blocks.set(key, { bytes: new Uint8Array(bytes), labels: fields.label ? [String(fields.label)] : [], createdAt: Date.now() });
    else if (fields.label) this.#blocks.get(key).labels.push(String(fields.label));
    this.#rememberStringPayloadDigest(value, key);
    this.stats.puts += 1;
    if (duplicate) this.stats.duplicatePuts += 1;
    const ref = createBlockObjectRef(hash, { bytes: bytes.byteLength, backend: this.provider, label: fields.label ?? null });
    this.#trace?.emit('storage:block-put', { store: this.name, digest: ref.digest, bytes: ref.bytes, duplicate });
    return Object.freeze({ ref, digest: ref.digest, hash, bytes: bytes.byteLength, duplicate });
  }
  async get(refOrDigest, options = {}) {
    throwIfRuntimeCoreAborted(options, `Block store get aborted in ${this.name}`);
    const key = blockKeyFromRef(refOrDigest);
    const entry = this.#blocks.get(key);
    if (!entry) throw storageError('BRT_STORAGE_NOT_FOUND', `Block not found: ${key}`, { store: this.name, digest: key });
    this.stats.gets += 1;
    return new Uint8Array(entry.bytes);
  }
  async has(refOrDigest, options = {}) {
    throwIfRuntimeCoreAborted(options, `Block store has aborted in ${this.name}`);
    const present = this.#blocks.has(blockKeyFromRef(refOrDigest));
    this.stats.has += 1;
    return present;
  }
  async verify(refOrDigest, options = {}) {
    throwIfRuntimeCoreAborted(options, `Block store verify aborted in ${this.name}`);
    const key = blockKeyFromRef(refOrDigest);
    const entry = this.#blocks.get(key);
    if (!entry) {
      this.stats.verifies += 1;
      return Object.freeze({ ok: false, present: false, digest: key, reason: 'missing' });
    }
    const actualDigest = `sha256:${await digestBytesHex(entry.bytes)}`;
    throwIfRuntimeCoreAborted(options, `Block store verify aborted in ${this.name}`);
    this.stats.verifies += 1;
    return Object.freeze({ ok: actualDigest === key, present: true, digest: key, actualDigest, bytes: entry.bytes.byteLength, reason: actualDigest === key ? null : 'checksum-mismatch' });
  }
  async delete(refOrDigest, options = {}) {
    throwIfRuntimeCoreAborted(options, `Block store delete aborted in ${this.name}`);
    const key = blockKeyFromRef(refOrDigest);
    const deleted = this.#blocks.delete(key);
    const duplicateHintsCleared = deleted ? this.#forgetDuplicateHintsForDigest(key) : 0;
    this.stats.deletes += 1;
    return Object.freeze({ deleted, digest: key, duplicateHintsCleared });
  }
  estimate(options = {}) {
    throwIfRuntimeCoreAborted(options, `Block store estimate aborted in ${this.name}`);
    return Object.freeze({ quota: Number.isFinite(this.quotaBytes) ? this.quotaBytes : null, usage: this.bytesUsed(), blockCount: this.#blocks.size });
  }
  snapshot(options = {}) {
    throwIfRuntimeCoreAborted(options, `Block store snapshot aborted in ${this.name}`);
    return Object.freeze({ name: this.name, provider: this.provider, blockCount: this.#blocks.size, bytes: this.bytesUsed(), duplicateHintCount: this.#stringPayloadDigestHints.size, duplicateHintLimit: this.duplicateHintLimit, stats: { ...this.stats } });
  }
  async cleanupForTest(options = {}) {
    throwIfRuntimeCoreAborted(options, `Block store cleanup aborted in ${this.name}`);
    const count = this.#blocks.size;
    const duplicateHintsCleared = this.#stringPayloadDigestHints.size;
    this.#blocks.clear();
    this.#stringPayloadDigestHints.clear();
    if (duplicateHintsCleared > 0) this.stats.duplicateHintsCleared += duplicateHintsCleared;
    return Object.freeze({ deleted: count, duplicateHintsCleared });
  }
}
export function createMemoryBlockStore(config = {}) { return new MemoryBlockStore(config); }
export function bootRuntimeCore(options = {}) {
  const trace = options.trace instanceof TraceLog ? options.trace : new TraceLog({ capacity: options.traceCapacity ?? 4096 });
  trace.emit('runtime:boot', { revision: REVISION, version: VERSION, entry: 'runtime-core', telemetry: options.telemetry ?? null });
  const runtime = {
    revision: REVISION,
    version: VERSION,
    entry: BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT,
    trace,
    capabilities: detectCapabilities(options.globalThis || globalThis),
    core: Object.freeze({
      channel: (config = {}) => new BoundedChannel({ trace, ...config }),
      transferObject: createTransferObject,
      objectRef: createObjectRef,
      blockRef: createBlockObjectRef,
      envelope: createEnvelope
    }),
    storage: Object.freeze({
      blockStore: (config = {}) => createMemoryBlockStore({ trace, ...config }),
      blockStoreLaneAdapter: (config = {}) => createRuntimeCoreBlockStoreLaneAdapter({ trace, ...config }),
      browserStoragePosture: (config = {}) => diagnoseBrowserStoragePosture(config),
      browserStorageRecoveryGuidance: (error, context = {}) => createBrowserStorageRecoveryGuidance(error, context)
    }),
    coordination: Object.freeze({
      admissionController: (config = {}) => createWatermarkAdmissionController({ trace, ...config }),
      crossLaneScheduler: (config = {}) => createCrossLaneScheduler({ trace, ...config })
    }),
    close(reason = 'runtime-core-close') {
      trace.emit('runtime:close', { revision: REVISION, version: VERSION, entry: 'runtime-core', reason });
      return trace.snapshot();
    }
  };
  return Object.freeze(runtime);
}
export const boot = bootRuntimeCore;
