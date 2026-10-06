import { createSharedInt32Ring, openSharedInt32Ring, SharedInt32Ring } from './sab-ring.mjs';
import { createSharedFrameRing, openSharedFrameRing, SharedFrameRing } from './sab-frame-ring.mjs';
import { createSpillFrameMailbox, SpillFrameMailbox } from './spill-mailbox.mjs';
import { createPersistedSpillMailbox, recoverPersistedSpillMailbox, PersistedSpillMailbox } from './persisted-spill-mailbox.mjs'; // PersistedSpillMailbox.compact() retained-ref compaction
import { createWatermarkAdmissionController, WatermarkAdmissionController } from './admission-control.mjs';
import { createAdaptiveConcurrencyController, AdaptiveConcurrencyController } from './adaptive-concurrency.mjs';
import { createPriorityFairScheduler, PriorityFairScheduler, PRIORITY_FAIRNESS_ORDER } from './priority-fairness.mjs';
import { createCrossLaneScheduler, CrossLaneScheduler, CROSS_LANE_PRIORITY_ORDER, validateCrossLaneSchedulerSnapshot } from './cross-lane-scheduler.mjs';
import { createStorageLaneExecutor, StorageLaneExecutor, STORAGE_LANE_EXECUTOR_SUPPORTED_OPS, validateStorageLaneExecutorSnapshot } from './storage-lane-scheduler.mjs';
import { BlockStoreLaneAdapter, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, BLOCK_STORE_LANE_ADAPTER_OPS } from './block-store-lane-adapter.mjs';
import { createStorageLaneRetryPolicy, createStorageLaneRetryController, StorageLaneRetryPolicy, StorageLaneRetryController } from './storage-lane-retry.mjs';
import { createRetryBudgetAdmissionController, RetryBudgetAdmissionController, validateRetryBudgetAdmissionSnapshot } from './retry-budget-admission.mjs';
import { createCircuitBreakerBulkheadController, CircuitBreakerBulkheadController, validateCircuitBreakerBulkheadSnapshot } from './circuit-breaker-bulkhead.mjs';
import { createProviderResilienceHistoryRunner, ProviderResilienceHistoryRunner, validateProviderResilienceHistorySnapshot } from './provider-resilience-history.mjs';
import { createProviderResilienceModelOracle, ProviderResilienceModelOracle, compareProviderResilienceHistoryToModel, validateProviderResilienceModelSnapshot } from './provider-resilience-model.mjs';
import { createStorageLaneAdmissionHistoryRunner, StorageLaneAdmissionHistoryRunner, validateStorageLaneAdmissionHistorySnapshot } from './storage-lane-admission-history.mjs';
import { createStorageLaneAdmissionHistoryModelOracle, StorageLaneAdmissionHistoryModelOracle, compareStorageLaneAdmissionHistoryToModel, validateStorageLaneAdmissionHistoryModelSnapshot } from './storage-lane-admission-model.mjs';
import { createStorageLaneOverloadGovernanceModelOracle, StorageLaneOverloadGovernanceModelOracle, compareStorageLaneOverloadGovernanceToRuntime, validateStorageLaneOverloadGovernanceSnapshot } from './storage-lane-overload-governance.mjs';
import { createOpfsAsyncBlockStore, OpfsAsyncBlockStore } from './opfs-block-store.mjs';
import { createOpfsBlockStoreStorageLaneAdapter, OpfsBlockStoreStorageLaneAdapter, validateOpfsStorageLaneAdapterSnapshot, OPFS_STORAGE_LANE_ADAPTER_SUPPORTED_OPS } from './opfs-storage-lane-adapter.mjs';
import { createDreamBoundaryMap, validateDreamBoundaryMap, DREAM_BOUNDARY_CATEGORIES, DREAM_BOUNDARY_AREAS } from './dream-boundary.mjs';
import { createProjectContinuationAssessment, validateProjectContinuationAssessment, PROJECT_ASSESSMENT_AUDIENCES, PROJECT_ASSESSMENT_POSTURES } from './project-assessment.mjs';
import { createKernelKitDemoPlan, validateKernelKitDemoPlan, validateKernelKitDemoProof, validateKernelKitDemoReport, summarizeKernelKitDemoTrace, scoreKernelKitDemoUsefulness, createKernelKitDemoTranscript, validateKernelKitDemoTranscript, createKernelKitTraceExport, validateKernelKitTraceExport, createKernelKitDemoHandoff, validateKernelKitDemoHandoff, KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY, KERNEL_KIT_DEMO_HANDOFF_REQUIRED_KEYS, KERNEL_KIT_DEMO_EXPORT_FORMATS, KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS, KERNEL_KIT_DEMO_FAILURE_MODES, KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT, KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS, createKernelKitDemoExportBundle, validateKernelKitDemoExportBundle, createKernelKitFailureModeReport, validateKernelKitFailureModeReport, createKernelKitTraceComparison, validateKernelKitTraceComparison, createKernelKitDiagnosticRunbook, validateKernelKitDiagnosticRunbook, createKernelKitSupportBundle, validateKernelKitSupportBundle, createKernelKitSupportBundleImportReport, validateKernelKitSupportBundleImportReport, createKernelKitSupportBundleDiff, validateKernelKitSupportBundleDiff, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_NON_CLAIMS, KERNEL_KIT_TRACE_COMPARISON_FORMAT, KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS, createKernelKitGuidedTour, validateKernelKitGuidedTour, createKernelKitGuidedTourReceipt, validateKernelKitGuidedTourReceipt, KERNEL_KIT_GUIDED_TOUR_FORMAT, KERNEL_KIT_GUIDED_TOUR_STEPS, KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS, KERNEL_KIT_DEMO_CODENAME, KERNEL_KIT_DEMO_STEPS, KERNEL_KIT_DEMO_REQUIRED_STEPS, KERNEL_KIT_DEMO_STAGE_LABELS, KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS, KERNEL_KIT_DEMO_NON_CLAIMS } from './kernel-kit-demo.mjs';
import { createKernelKitDemoObservatoryReport, validateKernelKitDemoObservatoryReport, KERNEL_KIT_OBSERVATORY_CODENAME, KERNEL_KIT_OBSERVATORY_REQUIRED_SECTIONS, KERNEL_KIT_OBSERVATORY_NON_CLAIMS } from './kernel-kit-demo-observatory.mjs';
import { createKernelKitHandoffMarkdown, validateKernelKitHandoffMarkdown, KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT, KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS } from './kernel-kit-handoff-markdown.mjs';
import { createKernelKitHandoffMarkdownImportReport, validateKernelKitHandoffMarkdownImportReport, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS, KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS } from './kernel-kit-handoff-reader.mjs';
import { createKernelKitReadinessGate, validateKernelKitReadinessGate, KERNEL_KIT_READINESS_GATE_FORMAT, KERNEL_KIT_READINESS_GATE_NON_CLAIMS, KERNEL_KIT_READINESS_GATE_REQUIRED_GATES, KERNEL_KIT_READINESS_GATE_PERSONAS } from './kernel-kit-readiness-gate.mjs';
import { createKernelKitReadinessContrast, validateKernelKitReadinessContrast, createDegradedKernelKitReadinessGate, KERNEL_KIT_READINESS_CONTRAST_FORMAT, KERNEL_KIT_READINESS_CONTRAST_NON_CLAIMS, KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES } from './kernel-kit-readiness-contrast.mjs';
import { createKernelKitDemoUsefulnessReport, validateKernelKitDemoUsefulnessReport, KERNEL_KIT_USEFULNESS_CODENAME, KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS, KERNEL_KIT_USEFULNESS_AUDIENCES, KERNEL_KIT_USEFULNESS_NON_CLAIMS } from './kernel-kit-demo-usefulness.mjs';

export const VERSION = '0.0.54';
export const REVISION = 'rev0054';

export const LANES = Object.freeze([
  'main',
  'interactive',
  'cpu',
  'storage',
  'gpu',
  'render',
  'media',
  'audio',
  'ml',
  'network',
  'cross-tab',
  'plugin',
  'maintenance'
]);

export const PRIORITIES = Object.freeze([
  'critical',
  'user-blocking',
  'user-visible',
  'background',
  'maintenance'
]);

export const CAPABILITY_TIERS = Object.freeze([
  { id: 0, name: 'basic', meaning: 'main thread plus structured clone fallback' },
  { id: 1, name: 'workered', meaning: 'dedicated workers and transferables' },
  { id: 2, name: 'isolated', meaning: 'SharedArrayBuffer and Atomics in cross-origin-isolated contexts' },
  { id: 3, name: 'persistent', meaning: 'OPFS block store and storage worker paths' },
  { id: 4, name: 'accelerated', meaning: 'WebGPU and other accelerated adapter paths' },
  { id: 5, name: 'mesh', meaning: 'cross-tab coordination through same-origin primitives' }
]);

const OBJECT_REF_KINDS = new Set(['inline', 'transfer', 'shared', 'opfs', 'stream', 'gpu', 'block']);
const CHANNEL_OVERFLOWS = new Set(['wait', 'drop-oldest', 'drop-newest', 'fail']);
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

function describeError(error) {
  if (!error || typeof error !== 'object') return { name: 'Error', message: String(error) };
  return {
    name: error.name || 'Error',
    message: error.message || String(error),
    stack: error.stack
  };
}

function reviveError(errorLike) {
  const err = new Error(errorLike?.message || 'Unknown BrowserRT worker error');
  err.name = errorLike?.name || 'BrowserRTWorkerError';
  if (errorLike?.stack) err.stack = errorLike.stack;
  return err;
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

export function capabilityTierNames() {
  return CAPABILITY_TIERS.map((tier) => tier.name);
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
  if (!Number.isFinite(bytes) || bytes < 0) {
    throw new Error('Object ref bytes/length must be a non-negative finite number');
  }
  return Object.freeze({
    kind,
    id: fields.id ?? nextId(kind),
    bytes,
    ownership: fields.ownership ?? (kind === 'transfer' ? 'owned-main' : 'unspecified'),
    createdAt: fields.createdAt ?? Date.now(),
    ...fields
  });
}

export function createTransferObjectRef(buffer, fields = {}) {
  if (!(buffer instanceof ArrayBuffer)) throw new Error('createTransferObjectRef requires an ArrayBuffer');
  return createObjectRef('transfer', {
    id: fields.id ?? nextId('transfer'),
    bytes: buffer.byteLength,
    transferType: 'ArrayBuffer',
    ownership: 'owned-main',
    ...fields
  });
}

export function createTransferObject(buffer, fields = {}) {
  const ref = createTransferObjectRef(buffer, fields);
  return Object.freeze({ ref, buffer, transferList: [buffer] });
}


export function createOpfsObjectRef(path, fields = {}) {
  if (typeof path !== 'string' || !path.length || path.includes('..')) {
    throw new Error('createOpfsObjectRef requires a non-empty relative OPFS path without parent traversal');
  }
  return createObjectRef('opfs', {
    id: fields.id ?? `opfs:${path}`,
    path,
    backend: fields.backend ?? 'opfs-async',
    ownership: fields.ownership ?? 'origin-private',
    ...fields
  });
}

export function createOpfsSyncObjectRef(path, fields = {}) {
  return createOpfsObjectRef(path, {
    id: fields.id ?? `opfs-sync:${path}`,
    backend: 'opfs-sync-access-handle',
    ownership: 'origin-private-worker-exclusive',
    ...fields
  });
}


function toOwnedUint8Array(value) {
  if (typeof value === 'string') return new TextEncoder().encode(value);
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  throw new Error('BlockStore bytes must be a string, ArrayBuffer, Uint8Array, or ArrayBuffer view');
}

function blockKeyFromRef(refOrDigest) {
  if (typeof refOrDigest === 'string') {
    if (refOrDigest.startsWith('block:sha256:')) return refOrDigest.slice('block:'.length);
    if (refOrDigest.startsWith('sha256:')) return refOrDigest;
    if (/^[0-9a-f]{64}$/.test(refOrDigest)) return `sha256:${refOrDigest}`;
  }
  if (refOrDigest && typeof refOrDigest === 'object') {
    if (typeof refOrDigest.digest === 'string') return blockKeyFromRef(refOrDigest.digest);
    if (typeof refOrDigest.hash === 'string') return `sha256:${refOrDigest.hash}`;
    if (typeof refOrDigest.id === 'string') return blockKeyFromRef(refOrDigest.id);
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

export function createBlockObjectRef(hash, fields = {}) {
  if (typeof hash !== 'string' || !/^[0-9a-f]{64}$/.test(hash)) {
    throw new Error('createBlockObjectRef requires a lowercase 64-character sha256 hex hash');
  }
  return createObjectRef('block', {
    id: fields.id ?? `block:sha256:${hash}`,
    digest: `sha256:${hash}`,
    hash,
    algorithm: 'sha256',
    backend: fields.backend ?? 'memory-block-store',
    ownership: fields.ownership ?? 'content-addressed-provider',
    ...fields
  });
}

export class MemoryBlockStore {
  #blocks = new Map();
  #trace;
  #failNextPut = null;
  #faults;
  #opCounts = new Map();

  constructor({ name = 'memory-block-store', trace = null, provider = 'memory-block-store-v0', quotaBytes = Number.POSITIVE_INFINITY, faults = [] } = {}) {
    this.name = name;
    this.provider = provider;
    this.quotaBytes = quotaBytes;
    this.#trace = trace;
    this.#faults = Array.isArray(faults) ? faults.slice() : [];
    this.createdAt = Date.now();
    this.stats = { puts: 0, duplicatePuts: 0, gets: 0, has: 0, deletes: 0, verifies: 0, corruptions: 0, faults: 0, quotaRejects: 0 };
    this.#trace?.emit('storage:blockstore-create', { name: this.name, provider: this.provider, quotaBytes: this.quotaBytes });
  }

  async put(value, fields = {}) {
    this.#maybeFault('put');
    if (this.#failNextPut) {
      const reason = this.#failNextPut;
      this.#failNextPut = null;
      this.stats.faults += 1;
      this.#trace?.emit('storage:block-fault', { store: this.name, op: 'put', code: 'BRT_STORAGE_INJECTED_FAULT', reason });
      throw storageError('BRT_STORAGE_INJECTED_FAULT', reason, { store: this.name, op: 'put' });
    }
    const bytes = toOwnedUint8Array(value);
    const hash = await digestBytesHex(bytes);
    const key = `sha256:${hash}`;
    const duplicate = this.#blocks.has(key);
    if (!duplicate && this.bytesUsed() + bytes.byteLength > this.quotaBytes) {
      this.stats.quotaRejects += 1;
      this.#trace?.emit('storage:block-quota-reject', { store: this.name, requestedBytes: bytes.byteLength, bytesUsed: this.bytesUsed(), quotaBytes: this.quotaBytes });
      throw storageError('BRT_STORAGE_QUOTA_EXCEEDED', `Block store quota exceeded in ${this.name}`, { store: this.name, requestedBytes: bytes.byteLength, bytesUsed: this.bytesUsed(), quotaBytes: this.quotaBytes });
    }
    if (!duplicate) {
      this.#blocks.set(key, { bytes: new Uint8Array(bytes), createdAt: Date.now(), labels: fields.label ? [String(fields.label)] : [] });
    } else if (fields.label) {
      this.#blocks.get(key).labels.push(String(fields.label));
    }
    this.stats.puts += 1;
    if (duplicate) this.stats.duplicatePuts += 1;
    const ref = createBlockObjectRef(hash, { bytes: bytes.byteLength, backend: this.provider, label: fields.label ?? null });
    this.#trace?.emit('storage:block-put', { store: this.name, digest: ref.digest, bytes: ref.bytes, duplicate, label: ref.label });
    return Object.freeze({ ref, digest: ref.digest, hash, bytes: bytes.byteLength, duplicate });
  }

  async get(refOrDigest) {
    this.#maybeFault('get');
    const key = blockKeyFromRef(refOrDigest);
    const entry = this.#blocks.get(key);
    if (!entry) {
      this.#trace?.emit('storage:block-get-miss', { store: this.name, digest: key });
      throw storageError('BRT_STORAGE_NOT_FOUND', `Block not found: ${key}`, { store: this.name, digest: key });
    }
    const hash = await digestBytesHex(entry.bytes);
    const actualDigest = `sha256:${hash}`;
    if (actualDigest !== key) {
      this.#trace?.emit('storage:block-get-error', { store: this.name, digest: key, actualDigest, reason: 'checksum mismatch' });
      throw storageError('BRT_STORAGE_CHECKSUM_MISMATCH', `Block checksum mismatch: ${key} != ${actualDigest}`, { store: this.name, digest: key, actualDigest });
    }
    this.stats.gets += 1;
    this.#trace?.emit('storage:block-get', { store: this.name, digest: key, bytes: entry.bytes.byteLength });
    return new Uint8Array(entry.bytes);
  }

  async has(refOrDigest) {
    this.#maybeFault('has');
    const key = blockKeyFromRef(refOrDigest);
    this.stats.has += 1;
    const present = this.#blocks.has(key);
    this.#trace?.emit('storage:block-has', { store: this.name, digest: key, present });
    return present;
  }

  failNextPutForTest(reason = 'injected failure') {
    this.#failNextPut = String(reason);
    this.#trace?.emit('storage:block-fail-next-put-for-test', { store: this.name, reason: this.#failNextPut });
  }

  corruptForTest(refOrDigest, mutator = null) {
    const key = blockKeyFromRef(refOrDigest);
    const entry = this.#blocks.get(key);
    if (!entry) throw new Error(`Block not found: ${key}`);
    const corrupted = new Uint8Array(entry.bytes);
    if (typeof mutator === 'function') mutator(corrupted);
    else if (corrupted.byteLength) corrupted[0] ^= 0xff;
    else entry.labels.push('corrupted-empty-block');
    entry.bytes = corrupted;
    this.#trace?.emit('storage:block-corrupt-for-test', { store: this.name, digest: key, bytes: corrupted.byteLength });
    return true;
  }

  async delete(refOrDigest) {
    this.#maybeFault('delete');
    const key = blockKeyFromRef(refOrDigest);
    const deleted = this.#blocks.delete(key);
    this.stats.deletes += 1;
    this.#trace?.emit('storage:block-delete', { store: this.name, digest: key, deleted });
    return deleted;
  }

  async verify(refOrDigest) {
    this.#maybeFault('verify');
    const key = blockKeyFromRef(refOrDigest);
    const entry = this.#blocks.get(key);
    if (!entry) return Object.freeze({ digest: key, present: false, ok: false });
    const hash = await digestBytesHex(entry.bytes);
    const ok = key === `sha256:${hash}`;
    this.stats.verifies += 1;
    this.#trace?.emit('storage:block-verify', { store: this.name, digest: key, ok, actualDigest: `sha256:${hash}` });
    return Object.freeze({ digest: key, actualDigest: `sha256:${hash}`, present: true, ok, bytes: entry.bytes.byteLength });
  }

  corrupt(refOrDigest, { mode = 'flip-first-byte' } = {}) {
    const key = blockKeyFromRef(refOrDigest);
    const entry = this.#blocks.get(key);
    if (!entry) throw storageError('BRT_STORAGE_NOT_FOUND', `Cannot corrupt missing block: ${key}`, { store: this.name, digest: key });
    if (!entry.bytes.byteLength) throw storageError('BRT_STORAGE_EMPTY_BLOCK', `Cannot corrupt empty block: ${key}`, { store: this.name, digest: key });
    if (mode === 'flip-first-byte') entry.bytes[0] ^= 0xff;
    else if (mode === 'truncate') entry.bytes = entry.bytes.slice(0, Math.max(0, entry.bytes.byteLength - 1));
    else throw new Error(`Unsupported corruption mode: ${mode}`);
    this.stats.corruptions += 1;
    this.#trace?.emit('storage:block-corrupt', { store: this.name, digest: key, mode });
    return Object.freeze({ digest: key, mode });
  }

  injectFault(fault) {
    this.#faults.push({ ...fault });
    this.#trace?.emit('storage:block-fault-inject', { store: this.name, fault: { ...fault } });
  }

  bytesUsed() {
    let bytes = 0;
    for (const entry of this.#blocks.values()) bytes += entry.bytes.byteLength;
    return bytes;
  }

  snapshot() {
    return Object.freeze({ name: this.name, provider: this.provider, blockCount: this.#blocks.size, bytes: this.bytesUsed(), quotaBytes: this.quotaBytes, stats: { ...this.stats } });
  }

  manifest() {
    const blocks = [];
    for (const [digest, entry] of this.#blocks.entries()) {
      blocks.push({ digest, bytes: entry.bytes.byteLength, createdAt: entry.createdAt, labels: entry.labels.slice() });
    }
    blocks.sort((a, b) => a.digest.localeCompare(b.digest));
    return Object.freeze({ kind: 'memory-block-store-manifest', name: this.name, provider: this.provider, blockCount: blocks.length, blocks });
  }

  #maybeFault(op) {
    const count = (this.#opCounts.get(op) || 0) + 1;
    this.#opCounts.set(op, count);
    const index = this.#faults.findIndex((fault) => fault && (fault.op === op || fault.op === '*') && (fault.at === count || fault.at === 'every'));
    if (index < 0) return;
    const fault = this.#faults[index];
    if (fault.at !== 'every') this.#faults.splice(index, 1);
    this.stats.faults += 1;
    const code = fault.code || 'BRT_STORAGE_INJECTED_FAULT';
    this.#trace?.emit('storage:block-fault', { store: this.name, op, count, code });
    throw storageError(code, fault.message || `Injected block-store fault for ${op}`, { store: this.name, op, count });
  }
}


function bytesToHex(bytes) {
  return Array.from(new Uint8Array(bytes)).map((x) => x.toString(16).padStart(2, '0')).join('');
}

function hexToBytes(hex) {
  if (typeof hex !== 'string' || hex.length % 2 !== 0 || /[^0-9a-f]/i.test(hex)) {
    throw new Error('Invalid hex byte string');
  }
  const out = new Uint8Array(hex.length / 2);
  for (let i = 0; i < out.length; i += 1) out[i] = Number.parseInt(hex.slice(i * 2, i * 2 + 2), 16);
  return out;
}

function canonicalJson(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value));
}

async function checksumPayload(payload) {
  return `sha256:${await digestBytesHex(new TextEncoder().encode(canonicalJson(payload)))}`;
}

export class JournaledMemoryBlockStore {
  #blocks = new Map();
  #journal = [];
  #seq = 0;
  #trace;

  constructor({ name = 'journaled-memory-block-store', provider = 'journaled-memory-fake-provider-v0', trace = null } = {}) {
    this.name = name;
    this.provider = provider;
    this.#trace = trace;
    this.stats = { puts: 0, duplicatePuts: 0, deletes: 0, checkpoints: 0, recoveries: 0, tornRecordsIgnored: 0 };
    this.#trace?.emit('storage:journaled-blockstore-create', { name: this.name, provider: this.provider });
  }

  async put(value, fields = {}) {
    const bytes = toOwnedUint8Array(value);
    const hash = await digestBytesHex(bytes);
    const digest = `sha256:${hash}`;
    const duplicate = this.#blocks.has(digest);
    if (!duplicate) this.#blocks.set(digest, { bytes: new Uint8Array(bytes), labels: [], createdAt: Date.now() });
    if (fields.label) this.#blocks.get(digest).labels.push(String(fields.label));
    this.stats.puts += 1;
    if (duplicate) this.stats.duplicatePuts += 1;
    await this.#append('put', { digest, bytesHex: bytesToHex(bytes), bytes: bytes.byteLength, label: fields.label ?? null, duplicate });
    const ref = createBlockObjectRef(hash, { bytes: bytes.byteLength, backend: this.provider, label: fields.label ?? null });
    this.#trace?.emit('storage:block-put', { store: this.name, digest, bytes: bytes.byteLength, duplicate, journaled: true });
    return Object.freeze({ ref, digest, hash, bytes: bytes.byteLength, duplicate, seq: this.#seq });
  }

  async get(refOrDigest) {
    const key = blockKeyFromRef(refOrDigest);
    const entry = this.#blocks.get(key);
    if (!entry) throw storageError('BRT_STORAGE_NOT_FOUND', `Journaled block not found: ${key}`, { store: this.name, digest: key });
    const hash = await digestBytesHex(entry.bytes);
    if (`sha256:${hash}` !== key) throw storageError('BRT_STORAGE_CHECKSUM_MISMATCH', `Journaled block checksum mismatch: ${key}`, { store: this.name, digest: key, actualDigest: `sha256:${hash}` });
    return new Uint8Array(entry.bytes);
  }

  async has(refOrDigest) {
    return this.#blocks.has(blockKeyFromRef(refOrDigest));
  }

  async delete(refOrDigest) {
    const digest = blockKeyFromRef(refOrDigest);
    const deleted = this.#blocks.delete(digest);
    this.stats.deletes += 1;
    await this.#append('delete', { digest, deleted });
    this.#trace?.emit('storage:block-delete', { store: this.name, digest, deleted, journaled: true });
    return deleted;
  }

  async checkpoint(fields = {}) {
    const blocks = [];
    for (const [digest, entry] of this.#blocks.entries()) {
      blocks.push({ digest, bytes: entry.bytes.byteLength, bytesHex: bytesToHex(entry.bytes), labels: entry.labels.slice(), createdAt: entry.createdAt });
    }
    blocks.sort((a, b) => a.digest.localeCompare(b.digest));
    const payload = { kind: 'journaled-memory-block-store-manifest-payload', name: this.name, provider: this.provider, seq: this.#seq, blockCount: blocks.length, blocks, label: fields.label ?? null };
    const manifest = Object.freeze({ kind: 'journaled-memory-block-store-manifest', version: 1, seq: this.#seq, checksum: await checksumPayload(payload), payload });
    this.stats.checkpoints += 1;
    this.#trace?.emit('storage:manifest-checkpoint', { store: this.name, seq: manifest.seq, blockCount: blocks.length, checksum: manifest.checksum, label: fields.label ?? null });
    return manifest;
  }

  exportJournal() {
    return this.#journal.map(cloneJson);
  }

  tornRecordForTest(fields = {}) {
    return { seq: this.#seq + 1, op: fields.op || 'put', payload: { digest: 'sha256:torn-tail-record', bytesHex: '00', bytes: 1 }, checksum: 'sha256:bad-tail-checksum' };
  }

  snapshot() {
    return Object.freeze({ name: this.name, provider: this.provider, seq: this.#seq, blockCount: this.#blocks.size, stats: { ...this.stats } });
  }

  manifestView() {
    const blocks = [];
    for (const [digest, entry] of this.#blocks.entries()) blocks.push({ digest, bytes: entry.bytes.byteLength, labels: entry.labels.slice() });
    blocks.sort((a, b) => a.digest.localeCompare(b.digest));
    return Object.freeze({ kind: 'journaled-memory-block-store-view', name: this.name, provider: this.provider, seq: this.#seq, blockCount: blocks.length, blocks });
  }

  async #append(op, payload) {
    const record = { seq: this.#seq + 1, op, payload: cloneJson(payload) };
    record.checksum = await checksumPayload({ seq: record.seq, op: record.op, payload: record.payload });
    this.#seq = record.seq;
    this.#journal.push(record);
    this.#trace?.emit('storage:journal-append', { store: this.name, seq: record.seq, op, digest: payload.digest ?? null });
    return record;
  }

  static async recover({ manifest, journal = [], trace = null, name = null, provider = null, strictTail = false } = {}) {
    if (!manifest || manifest.kind !== 'journaled-memory-block-store-manifest') {
      trace?.emit('storage:manifest-recover-error', { reason: 'missing-or-unsupported-manifest' });
      throw storageError('BRT_STORAGE_BAD_MANIFEST', 'Missing or unsupported journaled memory manifest', { manifestKind: manifest?.kind });
    }
    const expected = await checksumPayload(manifest.payload);
    if (expected !== manifest.checksum) {
      trace?.emit('storage:manifest-recover-error', { reason: 'checksum-mismatch', expected, actual: manifest.checksum, seq: manifest.seq });
      throw storageError('BRT_STORAGE_BAD_MANIFEST_CHECKSUM', 'Journaled memory manifest checksum mismatch', { expected, actual: manifest.checksum, seq: manifest.seq });
    }
    const store = new JournaledMemoryBlockStore({ name: name || manifest.payload.name || 'recovered-journaled-memory-block-store', provider: provider || manifest.payload.provider || 'journaled-memory-fake-provider-v0', trace });
    store.#seq = manifest.payload.seq || 0;
    for (const block of manifest.payload.blocks || []) {
      store.#blocks.set(block.digest, { bytes: hexToBytes(block.bytesHex || ''), labels: Array.isArray(block.labels) ? block.labels.slice() : [], createdAt: block.createdAt || Date.now() });
    }
    trace?.emit('storage:manifest-recover', { store: store.name, seq: store.#seq, blockCount: store.#blocks.size, checksum: manifest.checksum });
    let ignoredTailRecords = 0;
    const appliedJournalSeqs = [];
    const sorted = journal.map(cloneJson).sort((a, b) => (a.seq || 0) - (b.seq || 0));
    for (const record of sorted) {
      if ((record.seq || 0) <= store.#seq) continue;
      const recordExpected = await checksumPayload({ seq: record.seq, op: record.op, payload: record.payload });
      if (recordExpected !== record.checksum) {
        ignoredTailRecords += 1;
        store.stats.tornRecordsIgnored += 1;
        trace?.emit('storage:journal-torn-record-ignored', { store: store.name, seq: record.seq, op: record.op, expected: recordExpected, actual: record.checksum });
        if (strictTail) throw storageError('BRT_STORAGE_BAD_JOURNAL_RECORD', 'Journal record checksum mismatch', { seq: record.seq });
        break;
      }
      if (record.op === 'put') {
        store.#blocks.set(record.payload.digest, { bytes: hexToBytes(record.payload.bytesHex), labels: record.payload.label ? [String(record.payload.label)] : [], createdAt: Date.now() });
      } else if (record.op === 'delete') {
        store.#blocks.delete(record.payload.digest);
      } else {
        trace?.emit('storage:journal-torn-record-ignored', { store: store.name, seq: record.seq, op: record.op, reason: 'unknown-op' });
        ignoredTailRecords += 1;
        break;
      }
      store.#seq = record.seq;
      store.#journal.push(record);
      appliedJournalSeqs.push(record.seq);
      trace?.emit('storage:journal-replay-apply', { store: store.name, seq: record.seq, op: record.op, digest: record.payload.digest ?? null });
    }
    store.stats.recoveries += 1;
    const recovery = Object.freeze({ checkpointSeq: manifest.payload.seq || 0, finalSeq: store.#seq, appliedJournalRecords: appliedJournalSeqs.length, appliedJournalSeqs, ignoredTailRecords, blockCount: store.#blocks.size });
    trace?.emit('storage:journal-recover', { store: store.name, ...recovery });
    return Object.freeze({ store, recovery });
  }
}

export function createJournaledMemoryBlockStore(config = {}) {
  return new JournaledMemoryBlockStore(config);
}

export async function recoverJournaledMemoryBlockStore(config = {}) {
  return JournaledMemoryBlockStore.recover(config);
}

export function createMemoryBlockStore(config = {}) {
  return new MemoryBlockStore(config);
}

export async function digestBytesHex(bytes) {
  if (globalThis.crypto?.subtle?.digest) {
    const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(digest)).map((x) => x.toString(16).padStart(2, '0')).join('');
  }
  let hash = 2166136261;
  for (const byte of new Uint8Array(bytes)) {
    hash ^= byte;
    hash = Math.imul(hash, 16777619) >>> 0;
  }
  return `fnv32:${hash.toString(16).padStart(8, '0')}`;
}

export async function opfsAsyncWriteReadProbe({ path = 'browserrt/rev0025/opfs-async-proof.bin', bytes = null, text = null, cleanup = true } = {}) {
  const nav = globalThis.navigator;
  if (!nav?.storage || typeof nav.storage.getDirectory !== 'function') {
    throw new Error('OPFS is unavailable: navigator.storage.getDirectory is missing');
  }
  const inputBytes = bytes instanceof Uint8Array
    ? bytes
    : new TextEncoder().encode(text ?? `BrowserRT ${REVISION} OPFS async write/read proof`);
  const root = await nav.storage.getDirectory();
  const parts = path.split('/').filter(Boolean);
  if (!parts.length || parts.some((part) => part === '..')) throw new Error('OPFS probe path must be relative and non-empty');
  let dir = root;
  for (const part of parts.slice(0, -1)) {
    dir = await dir.getDirectoryHandle(part, { create: true });
  }
  const fileName = parts.at(-1);
  const file = await dir.getFileHandle(fileName, { create: true });
  const writable = await file.createWritable();
  await writable.write(inputBytes);
  await writable.close();
  const storedFile = await file.getFile();
  const storedBytes = new Uint8Array(await storedFile.arrayBuffer());
  const same = storedBytes.length === inputBytes.length && storedBytes.every((value, i) => value === inputBytes[i]);
  const result = Object.freeze({
    ref: createOpfsObjectRef(path, { bytes: storedBytes.byteLength }),
    bytesWritten: inputBytes.byteLength,
    bytesRead: storedBytes.byteLength,
    same,
    digest: await digestBytesHex(storedBytes),
    fileName,
    path,
    cleanup
  });
  if (cleanup && typeof dir.removeEntry === 'function') {
    await dir.removeEntry(fileName).catch(() => {});
  }
  return result;
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




export function createPriorityFairSchedulerObjectRef(id = 'priority-fairness-controller', fields = {}) {
  return createObjectRef('inline', {
    id: fields.id ?? `scheduler:priority-fairness:${id}`,
    schedulerType: 'priority-fairness-drr',
    ownership: 'runtime-scheduler-provider',
    ...fields
  });
}

export function createStorageLaneExecutorObjectRef(id = 'storage-lane-executor', fields = {}) {
  return createObjectRef('inline', {
    id: fields.id ?? `scheduler:storage-lane:${id}`,
    ownership: 'runtime-scheduler-provider',
    ...fields
  });
}


export class TraceLog {
  #events = [];
  #nextSeq = 1;

  emit(kind, detail = {}) {
    const event = Object.freeze({ seq: this.#nextSeq++, t: Date.now(), kind, ...detail });
    this.#events.push(event);
    return event;
  }

  snapshot() {
    return this.#events.slice();
  }

  find(kind) {
    return this.#events.filter((event) => event.kind === kind);
  }

  count(kind) {
    return this.find(kind).length;
  }

  kinds() {
    return [...new Set(this.#events.map((event) => event.kind))];
  }
}

export class BoundedChannel {
  constructor({ capacity = 1, overflow = 'wait', label = 'channel', trace = null } = {}) {
    if (!Number.isInteger(capacity) || capacity < 1) throw new Error('BoundedChannel capacity must be a positive integer');
    if (!CHANNEL_OVERFLOWS.has(overflow)) throw new Error(`Unsupported overflow policy: ${overflow}`);
    this.capacity = capacity;
    this.overflow = overflow;
    this.label = label;
    this.queue = [];
    this.waitingReceivers = [];
    this.waitingSenders = [];
    this.trace = trace;
    this.trace?.emit('channel:create', { label: this.label, capacity: this.capacity, overflow: this.overflow });
  }

  async send(value) {
    if (this.waitingReceivers.length) {
      const resolve = this.waitingReceivers.shift();
      resolve(value);
      this.trace?.emit('channel:send', { label: this.label, disposition: 'delivered', size: this.size() });
      return { disposition: 'delivered' };
    }
    if (this.queue.length < this.capacity) {
      this.queue.push(value);
      this.trace?.emit('channel:send', { label: this.label, disposition: 'queued', size: this.size() });
      return { disposition: 'queued' };
    }
    if (this.overflow === 'drop-oldest') {
      this.queue.shift();
      this.queue.push(value);
      this.trace?.emit('channel:send', { label: this.label, disposition: 'dropped-oldest', size: this.size() });
      return { disposition: 'dropped-oldest' };
    }
    if (this.overflow === 'drop-newest') {
      this.trace?.emit('channel:send', { label: this.label, disposition: 'dropped-newest', size: this.size() });
      return { disposition: 'dropped-newest' };
    }
    if (this.overflow === 'fail') {
      this.trace?.emit('channel:send', { label: this.label, disposition: 'failed-full', size: this.size() });
      throw new Error(`BoundedChannel ${this.label} is full`);
    }
    this.trace?.emit('channel:send', { label: this.label, disposition: 'waiting', size: this.size() });
    return await new Promise((resolve) => this.waitingSenders.push({ value, resolve }));
  }

  async receive() {
    if (this.queue.length) {
      const value = this.queue.shift();
      if (this.waitingSenders.length) {
        const sender = this.waitingSenders.shift();
        this.queue.push(sender.value);
        sender.resolve({ disposition: 'queued-after-wait' });
      }
      this.trace?.emit('channel:receive', { label: this.label, size: this.size() });
      return value;
    }
    this.trace?.emit('channel:receive-wait', { label: this.label, size: this.size() });
    return await new Promise((resolve) => this.waitingReceivers.push(resolve));
  }

  size() {
    return this.queue.length;
  }
}

export class WorkerAgent {
  #worker;
  #trace;
  #pending = new Map();
  #readyResolve;
  #readyReject;
  #exitCallbacks = new Set();
  #closed = false;
  #failed = false;
  #exitNotified = false;

  constructor({ worker, name = 'agent', trace = new TraceLog() }) {
    this.name = name;
    this.id = nextId('agent');
    this.#worker = worker;
    this.#trace = trace;
    this.ready = new Promise((resolve, reject) => {
      this.#readyResolve = resolve;
      this.#readyReject = reject;
    });
    this.#wireWorker(worker);
    this.#trace.emit('agent:spawn', { agentId: this.id, name: this.name });
  }

  get closed() { return this.#closed; }
  get failed() { return this.#failed; }
  get trace() { return this.#trace; }

  onExit(callback) {
    this.#exitCallbacks.add(callback);
    return () => this.#exitCallbacks.delete(callback);
  }

  async call(op, payload = {}, { transfer = [], timeoutMs = 0, lane = 'cpu', priority = 'user-visible' } = {}) {
    if (this.#closed) throw new Error(`WorkerAgent ${this.name} is closed`);
    await this.ready;
    const id = nextId('call');
    const envelope = createEnvelope(op, { lane, priority, payloadRef: payload.objectRef || payload.ref || null });
    const message = { type: 'agent:call', id, envelope, op, payload };
    this.#trace.emit('agent:call', { agentId: this.id, callId: id, op, transferCount: transfer.length, lane, priority });
    return await new Promise((resolve, reject) => {
      let timer = null;
      if (timeoutMs > 0) {
        timer = setTimeout(() => {
          this.#pending.delete(id);
          const err = new Error(`WorkerAgent call timed out: ${op}`);
          this.#trace.emit('agent:call-timeout', { agentId: this.id, callId: id, op, timeoutMs });
          reject(err);
        }, timeoutMs);
      }
      this.#pending.set(id, { resolve, reject, timer, op });
      try {
        if (transfer.length) this.#worker.postMessage(message, transfer);
        else this.#worker.postMessage(message);
      } catch (error) {
        this.#pending.delete(id);
        if (timer) clearTimeout(timer);
        this.#trace.emit('agent:post-error', { agentId: this.id, callId: id, op, error: describeError(error) });
        reject(error);
      }
    });
  }

  async terminate(reason = 'caller-terminate') {
    if (this.#closed) return { disposition: 'already-closed' };
    this.#trace.emit('agent:terminate', { agentId: this.id, name: this.name, reason });
    this.#closed = true;
    this.#rejectPending(new Error(`WorkerAgent terminated: ${reason}`));
    const result = this.#worker.terminate?.();
    if (result && typeof result.then === 'function') await result;
    return { disposition: 'terminated' };
  }

  #wireWorker(worker) {
    if (typeof worker.on === 'function') {
      worker.on('message', (message) => this.#handleMessage(message));
      worker.on('error', (error) => this.#handleError(error));
      worker.on('exit', (code) => this.#handleExit({ code }));
      return;
    }
    worker.addEventListener('message', (event) => this.#handleMessage(event.data));
    worker.addEventListener('error', (event) => this.#handleError(event.error || event.message || event));
  }

  #handleMessage(message) {
    if (!message || typeof message !== 'object') return;
    if (message.type === 'agent:ready') {
      this.#trace.emit('agent:ready', { agentId: this.id, name: this.name, detail: message.detail || {} });
      this.#readyResolve?.(this);
      return;
    }
    if (message.type === 'agent:trace') {
      this.#trace.emit(message.kind || 'agent:trace', { agentId: this.id, ...(message.detail || {}) });
      return;
    }
    if (message.type === 'agent:result' || message.type === 'agent:error') {
      const pending = this.#pending.get(message.id);
      if (!pending) return;
      this.#pending.delete(message.id);
      if (pending.timer) clearTimeout(pending.timer);
      if (message.type === 'agent:result') {
        this.#trace.emit('agent:result', { agentId: this.id, callId: message.id, op: pending.op });
        pending.resolve(message.result);
      } else {
        const err = reviveError(message.error);
        this.#trace.emit('agent:call-error', { agentId: this.id, callId: message.id, op: pending.op, error: describeError(err) });
        pending.reject(err);
      }
    }
  }

  #handleError(error) {
    const err = error instanceof Error ? error : new Error(String(error));
    this.#failed = true;
    this.#closed = true;
    this.#trace.emit('agent:error', { agentId: this.id, name: this.name, error: describeError(err) });
    this.#readyReject?.(err);
    this.#rejectPending(err);
    this.#notifyExit({ code: null, error: err });
  }

  #handleExit({ code = null } = {}) {
    const err = new Error(`WorkerAgent ${this.name} exited with code ${code}`);
    this.#closed = true;
    this.#trace.emit('agent:exit', { agentId: this.id, name: this.name, code });
    this.#readyReject?.(err);
    this.#rejectPending(err);
    this.#notifyExit({ code, error: err });
  }

  #notifyExit({ code, error }) {
    if (this.#exitNotified) return;
    this.#exitNotified = true;
    for (const callback of this.#exitCallbacks) callback({ agent: this, code, error });
  }

  #rejectPending(error) {
    for (const [id, pending] of this.#pending) {
      if (pending.timer) clearTimeout(pending.timer);
      pending.reject(error);
      this.#trace.emit('agent:pending-reject', { agentId: this.id, callId: id, op: pending.op, error: describeError(error) });
    }
    this.#pending.clear();
  }
}

export async function spawnWorkerAgent({ workerURL = null, name = 'browserrt-agent', trace = new TraceLog(), workerOptions = {} } = {}) {
  let worker;
  if (typeof globalThis.Worker === 'function' && environmentName() === 'browser-window') {
    const url = workerURL || new URL('./browser-agent-worker.mjs', import.meta.url);
    worker = new globalThis.Worker(url, { type: 'module', name, ...workerOptions });
  } else {
    const { Worker } = await import('node:worker_threads');
    const url = workerURL || new URL('./node-agent-worker.mjs', import.meta.url);
    worker = new Worker(url, { name, ...workerOptions });
  }
  const agent = new WorkerAgent({ worker, name, trace });
  await agent.ready;
  return agent;
}

export class Supervisor {
  constructor({ name = 'supervisor', workerURL = null, trace = new TraceLog(), restartLimit = 1 } = {}) {
    if (!Number.isInteger(restartLimit) || restartLimit < 0) throw new Error('Supervisor restartLimit must be a non-negative integer');
    this.name = name;
    this.workerURL = workerURL;
    this.trace = trace;
    this.restartLimit = restartLimit;
    this.restartCount = 0;
    this.agent = null;
    this.closed = false;
  }

  async start() {
    await this.#ensureAgent('start');
    return this;
  }

  async call(op, payload = {}, options = {}) {
    const agent = await this.#ensureAgent('call');
    try {
      return await agent.call(op, payload, options);
    } catch (error) {
      if (agent.closed || agent.failed) this.agent = null;
      this.trace.emit('supervisor:call-error', { supervisor: this.name, op, error: describeError(error) });
      throw error;
    }
  }

  snapshot() {
    return Object.freeze({
      name: this.name,
      restartCount: this.restartCount,
      restartLimit: this.restartLimit,
      agentId: this.agent?.id ?? null,
      agentAlive: Boolean(this.agent && !this.agent.closed)
    });
  }

  async close() {
    this.closed = true;
    this.trace.emit('supervisor:close', { supervisor: this.name, restartCount: this.restartCount });
    if (this.agent && !this.agent.closed) await this.agent.terminate('supervisor-close');
    return this.snapshot();
  }

  async #ensureAgent(reason) {
    if (this.closed) throw new Error(`Supervisor ${this.name} is closed`);
    if (this.agent && !this.agent.closed) return this.agent;
    if (this.agent?.closed) this.agent = null;
    if (this.restartCount >= this.restartLimit && reason !== 'start') {
      throw new Error(`Supervisor ${this.name} restart limit reached`);
    }
    if (reason !== 'start') {
      this.restartCount += 1;
      this.trace.emit('supervisor:restart', { supervisor: this.name, reason, restartCount: this.restartCount });
    }
    this.trace.emit('supervisor:spawn-request', { supervisor: this.name, reason, restartCount: this.restartCount });
    const agent = await spawnWorkerAgent({ workerURL: this.workerURL, name: `${this.name}-agent-${this.restartCount}`, trace: this.trace });
    agent.onExit(({ code }) => {
      this.trace.emit('supervisor:observed-exit', { supervisor: this.name, code, restartCount: this.restartCount });
      if (this.agent === agent) this.agent = null;
    });
    this.agent = agent;
    this.trace.emit('supervisor:agent-ready', { supervisor: this.name, agentId: agent.id, reason });
    return agent;
  }
}

export function createSupervisor(config = {}) {
  return new Supervisor(config);
}

export function createBootReport({ capabilities = detectCapabilities(), options = {} } = {}) {
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    environment: capabilities.environment,
    createdAt: new Date().toISOString(),
    options: Object.freeze({ ...options }),
    capabilities,
    availableTierNames: availableCapabilityTierNames(capabilities),
    lanes: LANES.slice(),
    priorities: PRIORITIES.slice(),
    capabilityTiers: CAPABILITY_TIERS.map((tier) => ({ ...tier })),
    executableProofs: Object.freeze({
      traceLog: true,
      boundedChannel: true,
      transferableObjectRef: true,
      workerAgent: true,
      supervisorRestart: true,
      kernelKitDemoProof: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof),
      browserKernelKitDemoProof: Boolean(options.browserKernelKitDemoProof),
      storageLane: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof || options.opfsStorageLaneAdapterProof || options.opfsAsyncBlockStoreProof || options.opfsAsyncProbe || options.opfsSyncWorkerProbe || options.browserOpfsSyncWorkerProbe || options.blockStoreProbe || options.journalRecoveryProbe || options.journaledBlockStoreProbe || options.spillMailboxProbe || options.persistedSpillRecoveryProbe || options.persistedSpillCompactionProbe || options.storageLaneRetryPolicyProof || options.storageLaneRetryBudgetProof || options.storageLaneRetryBudgetModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof),
      memoryBlockStore: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof || options.opfsAsyncBlockStoreProof || options.blockStoreProbe || options.journalRecoveryProbe || options.journaledBlockStoreProbe || options.spillMailboxProbe || options.persistedSpillRecoveryProbe || options.persistedSpillCompactionProbe || options.storageLaneRetryPolicyProof || options.storageLaneRetryBudgetProof || options.storageLaneRetryBudgetModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof),
      journaledBlockStore: Boolean(options.journalRecoveryProbe || options.journaledBlockStoreProbe),
      sabRing: Boolean(options.sabRingProbe || options.sharedMemoryRingProbe || options.browserSabRingWorkerProbe || options.browserSabFrameRingWorkerProbe || options.sabFrameRingProbe || options.sabFrameModelProbe),
      sabFrameRing: Boolean(options.sabFrameRingProbe || options.sabFrameModelProbe || options.browserSabFrameRingWorkerProbe),
      spillMailboxProbe: Boolean(options.spillMailboxProbe),
      persistedSpillRecoveryProbe: Boolean(options.persistedSpillRecoveryProbe),
      persistedSpillCompactionProbe: Boolean(options.persistedSpillCompactionProbe),
      storageLaneProviderProbe: Boolean(options.storageLaneProviderProbe),
      adaptiveConcurrencyProbe: Boolean(options.adaptiveConcurrencyProbe),
      priorityFairnessProbe: Boolean(options.priorityFairnessProbe),
      crossLaneSchedulerProbe: Boolean(options.crossLaneSchedulerProbe),
      crossLaneSchedulerModelProbe: Boolean(options.crossLaneSchedulerModelProbe || options.crossLaneModelWalkProbe),
      storageLaneSchedulerProbe: Boolean(options.storageLaneSchedulerProbe || options.storageLaneProviderProof),
      storageLaneProviderProof: Boolean(options.storageLaneProviderProof),
      storageLaneRetryPolicyProof: Boolean(options.storageLaneRetryPolicyProof),
      storageLaneRetryBudgetProof: Boolean(options.storageLaneRetryBudgetProof),
      storageLaneRetryBudgetModelProof: Boolean(options.storageLaneRetryBudgetModelProof),
      providerResilienceHistoryProof: Boolean(options.providerResilienceHistoryProof || options.storageLaneOverloadGovernanceModelProof),
      providerResilienceModelProof: Boolean(options.providerResilienceModelProof),
      storageLaneAdmissionHistoryProof: Boolean(options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof),
      storageLaneAdmissionHistoryModelProof: Boolean(options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof),
      storageLaneOverloadGovernanceModelProof: Boolean(options.storageLaneOverloadGovernanceModelProof),
      sabFrameModelProbe: Boolean(options.sabFrameModelProbe),
      browserSabRingWorkerProbe: Boolean(options.browserSabRingWorkerProbe),
      browserSabFrameRingWorkerProbe: Boolean(options.browserSabFrameRingWorkerProbe),
      sharedMemoryLane: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof || options.sabRingProbe || options.sharedMemoryRingProbe || options.browserSabRingWorkerProbe || options.browserSabFrameRingWorkerProbe || options.sabFrameRingProbe || options.sabFrameModelProbe || options.spillMailboxProbe || options.persistedSpillRecoveryProbe || options.persistedSpillCompactionProbe || options.storageLaneSchedulerProbe || options.storageLaneProviderProof || options.storageLaneRetryPolicyProof || options.storageLaneRetryBudgetProof || options.storageLaneRetryBudgetModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof || options.circuitBreakerBulkheadProof || options.resilienceCircuitBreakerBulkheadProof || options.adaptiveConcurrencyProbe || options.priorityFairnessProbe || options.crossLaneSchedulerModelProbe || options.crossLaneModelWalkProbe),
      gpuLane: false,
      browserCdpHarness: Boolean(options.browserCdpBootProbe || options.browserCdpHarness),
      browserCdpBootProbe: Boolean(options.browserCdpBootProbe),
      browserWorkerAgentProbe: Boolean(options.browserWorkerAgentProbe || options.browserKernelKitDemoProof),
      browserOpfsAsyncProbe: Boolean(options.browserOpfsAsyncProbe),
      opfsAsyncBlockStoreProof: Boolean(options.opfsAsyncBlockStoreProof),
      opfsStorageLaneAdapterProof: Boolean(options.opfsStorageLaneAdapterProof || options.browserKernelKitDemoProof),
      browserOpfsSyncWorkerProbe: Boolean(options.browserOpfsSyncWorkerProbe),
      adaptiveConcurrencyController: Boolean(options.adaptiveConcurrencyProbe || options.adaptiveConcurrencyControllerProbe),
      priorityFairScheduler: Boolean(options.priorityFairnessProbe || options.priorityFairnessSchedulerProbe),
      crossLaneScheduler: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof || options.opfsStorageLaneAdapterProof || options.crossLaneSchedulerProbe || options.crossLaneSchedulerModelProbe || options.crossLaneModelWalkProbe || options.storageLaneSchedulerProbe || options.storageLaneProviderProof || options.storageLaneRetryPolicyProof || options.storageLaneRetryBudgetProof || options.storageLaneRetryBudgetModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof || options.storageLaneModelWalkProof || options.crossLaneScheduler),
      storageLaneExecutor: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof || options.opfsStorageLaneAdapterProof || options.storageLaneSchedulerProbe || options.storageLaneProviderProof || options.storageLaneRetryPolicyProof || options.storageLaneRetryBudgetProof || options.storageLaneRetryBudgetModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof || options.storageLaneModelWalkProof || options.storageLaneExecutor),
      circuitBreakerBulkhead: Boolean(options.circuitBreakerBulkheadProof || options.resilienceCircuitBreakerBulkheadProof || options.circuitBreakerBulkheadModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof || options.circuitBreakerBulkhead),
      circuitBreakerBulkheadModelProof: Boolean(options.circuitBreakerBulkheadModelProof),
      testFacility: true
    })
  });
}

export async function boot(options = {}) {
  const trace = new TraceLog();
  const capabilities = detectCapabilities();
  const report = createBootReport({ capabilities, options });
  trace.emit('runtime:boot', { revision: REVISION, version: VERSION, capabilities });
  trace.emit('runtime:boot-report', { report });
  return Object.freeze({
    version: VERSION,
    revision: REVISION,
    options: Object.freeze({ ...options }),
    capabilities,
    report,
    trace,
    channel(config) { return new BoundedChannel({ ...(config || {}), trace }); },
    objectRef(kind, fields) {
      const ref = createObjectRef(kind, fields);
      trace.emit('object:ref', { refKind: ref.kind, id: ref.id, bytes: ref.bytes });
      return ref;
    },
    transferObject(buffer, fields) {
      const obj = createTransferObject(buffer, fields);
      trace.emit('object:transfer-ref', { id: obj.ref.id, bytes: obj.ref.bytes, transferType: obj.ref.transferType });
      return obj;
    },
    opfsObjectRef(path, fields) {
      const ref = createOpfsObjectRef(path, fields);
      trace.emit('object:opfs-ref', { id: ref.id, path: ref.path, bytes: ref.bytes, backend: ref.backend });
      return ref;
    },
    opfsSyncObjectRef(path, fields) {
      const ref = createOpfsSyncObjectRef(path, fields);
      trace.emit('object:opfs-sync-ref', { id: ref.id, path: ref.path, bytes: ref.bytes, backend: ref.backend });
      return ref;
    },
    sharedInt32Ring(config = {}) {
      const ring = createSharedInt32Ring({ ...config, trace: config.trace || trace });
      trace.emit('object:shared-ring-ref', { label: ring.label, capacity: ring.capacity, bytes: ring.sab.byteLength });
      return ring;
    },
    openSharedInt32Ring(sab, config = {}) {
      const ring = openSharedInt32Ring(sab, { ...config, trace: config.trace || trace });
      trace.emit('object:shared-ring-open', { label: ring.label, capacity: ring.capacity, bytes: ring.sab.byteLength });
      return ring;
    },
    sharedFrameRing(config = {}) {
      const ring = createSharedFrameRing({ ...config, trace: config.trace || trace });
      trace.emit('object:shared-frame-ring-ref', { label: ring.label, capacityBytes: ring.capacityBytes, bytes: ring.sab.byteLength });
      return ring;
    },
    openSharedFrameRing(sab, config = {}) {
      const ring = openSharedFrameRing(sab, { ...config, trace: config.trace || trace });
      trace.emit('object:shared-frame-ring-open', { label: ring.label, capacityBytes: ring.capacityBytes, bytes: ring.sab.byteLength });
      return ring;
    },
    spillFrameMailbox(config = {}) {
      const provider = config.provider || createMemoryBlockStore({ name: `${config.label || 'spill-frame-mailbox'}-spill-store`, provider: 'memory-block-spill-provider-v0', trace: config.trace || trace });
      const mailbox = createSpillFrameMailbox({ ...config, provider, trace: config.trace || trace });
      trace.emit('object:spill-mailbox-ref', { label: mailbox.label, memoryCapacityBytes: mailbox.memoryCapacityBytes, maxFrameBytes: mailbox.maxFrameBytes });
      return mailbox;
    },
    persistedSpillMailbox(config = {}) {
      const provider = config.provider || createMemoryBlockStore({ name: `${config.label || 'persisted-spill-mailbox'}-spill-store`, provider: 'memory-block-persisted-spill-provider-v0', trace: config.trace || trace });
      const mailbox = createPersistedSpillMailbox({ ...config, provider, trace: config.trace || trace });
      trace.emit('object:persisted-spill-mailbox-ref', { label: mailbox.label, maxFrameBytes: mailbox.maxFrameBytes, queueDepth: mailbox.snapshot().queueDepth });
      return mailbox;
    },
    async recoverPersistedSpillMailbox(config = {}) {
      const recovered = await recoverPersistedSpillMailbox({ ...config, trace: config.trace || trace });
      trace.emit('object:persisted-spill-mailbox-recovered', { label: recovered.mailbox.label, ...recovered.recovery });
      return recovered;
    },
    admissionController(config = {}) {
      const controller = createWatermarkAdmissionController({ ...config, trace: config.trace || trace });
      trace.emit('object:admission-controller-ref', { label: controller.label, highWatermarkBytes: controller.highWatermarkBytes, lowWatermarkBytes: controller.lowWatermarkBytes, hardLimitBytes: controller.hardLimitBytes });
      return controller;
    },
    adaptiveConcurrencyController(config = {}) {
      const controller = createAdaptiveConcurrencyController({ ...config, trace: config.trace || trace });
      trace.emit('object:adaptive-concurrency-controller-ref', { label: controller.label, limit: controller.limit, minLimit: controller.minLimit, maxLimit: controller.maxLimit });
      return controller;
    },
    priorityFairScheduler(config = {}) {
      const scheduler = createPriorityFairScheduler({ ...config, trace: config.trace || trace });
      trace.emit('object:priority-fair-scheduler-ref', { label: scheduler.label, maxQueuedCost: scheduler.maxQueuedCost, maxFlowQueuedCost: scheduler.maxFlowQueuedCost });
      return scheduler;
    },
    crossLaneScheduler(config = {}) {
      const scheduler = createCrossLaneScheduler({ ...config, trace: config.trace || trace });
      const snapshot = scheduler.snapshot();
      trace.emit('object:cross-lane-scheduler-ref', { label: scheduler.label, laneCount: snapshot.lanes.length, queuedCount: snapshot.queuedCount, inFlightCount: snapshot.inFlightCount });
      return scheduler;
    },
    storageLaneExecutor(config = {}) {
      const provider = config.provider || createMemoryBlockStore({ name: `${config.label || 'storage-lane-executor'}-provider`, provider: 'memory-block-storage-lane-provider-v0', trace: config.trace || trace });
      const mailbox = config.mailbox || createPersistedSpillMailbox({ label: `${config.label || 'storage-lane-executor'}-mailbox`, provider, trace: config.trace || trace, deleteBlockOnAck: false, memoryCapacityBytes: config.memoryCapacityBytes ?? 16 });
      const scheduler = config.scheduler || createCrossLaneScheduler({
        label: `${config.label || 'storage-lane-executor'}:scheduler`,
        trace: config.trace || trace,
        lanes: config.lanes || [
          { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 256 },
          { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
        ]
      });
      const executor = createStorageLaneExecutor({ ...config, scheduler, mailbox, trace: config.trace || trace });
      const snapshot = executor.snapshot();
      trace.emit('object:storage-lane-executor-ref', { label: executor.label, laneCount: snapshot.scheduler.lanes.length, queuedCount: snapshot.scheduler.queuedCount, mailboxQueueDepth: snapshot.mailbox?.queueDepth ?? null, mailboxPendingCount: snapshot.mailbox?.pendingCount ?? null });
      return executor;
    },


    circuitBreakerBulkheadController(config = {}) {
      const controller = createCircuitBreakerBulkheadController({ ...config, trace: config.trace || trace });
      trace.emit('object:circuit-breaker-bulkhead-controller-ref', { label: controller.label, state: controller.state, maxConcurrent: controller.maxConcurrent, slidingWindowSize: controller.slidingWindowSize });
      return controller;
    },

    retryBudgetAdmissionController(config = {}) {
      const controller = createRetryBudgetAdmissionController({ ...config, trace: config.trace || trace });
      trace.emit('object:retry-budget-admission-controller-ref', { label: controller.label, retryCredits: controller.retryCredits, maxRetryCredits: controller.maxRetryCredits, maxActiveRetries: controller.maxActiveRetries });
      return controller;
    },

    storageLaneRetryController(config = {}) {
      const executor = config.executor || this.storageLaneExecutor({ label: `${config.label || 'storage-lane-retry-controller'}:executor`, trace: config.trace || trace });
      const controller = createStorageLaneRetryController({ ...config, executor, trace: config.trace || trace });
      trace.emit('object:storage-lane-retry-controller-ref', { label: controller.label, maxAttempts: controller.policy.maxAttempts, delayedCount: controller.snapshot().delayedCount });
      return controller;
    },
    providerResilienceHistoryRunner(config = {}) {
      const executor = config.executor || this.storageLaneExecutor({ label: `${config.label || 'provider-resilience-history-runner'}:executor`, trace: config.trace || trace });
      const mailbox = config.mailbox || executor.mailbox;
      const breaker = config.breaker || this.circuitBreakerBulkheadController({ label: `${config.label || 'provider-resilience-history-runner'}:breaker`, trace: config.trace || trace, ...(config.breakerOptions || {}) });
      const retryBudget = config.retryBudget || this.retryBudgetAdmissionController({ label: `${config.label || 'provider-resilience-history-runner'}:retry-budget`, trace: config.trace || trace, ...(config.retryBudgetOptions || {}) });
      const runner = createProviderResilienceHistoryRunner({ ...config, executor, mailbox, breaker, retryBudget, trace: config.trace || trace });
      trace.emit('object:provider-resilience-history-runner-ref', { label: runner.label, executor: executor.label, breaker: breaker.label, retryBudget: retryBudget.label });
      return runner;
    },

    providerResilienceModelOracle(config = {}) {
      const oracle = createProviderResilienceModelOracle(config);
      trace.emit('object:storage-lane-admission-history-ref', { historyCount: oracle.snapshot().historyCount, providerBlocks: oracle.snapshot().provider.blockCount });
      return oracle;
    },

    storageLaneAdmissionHistoryRunner(config = {}) {
      const admission = config.admission || this.admissionController({ label: `${config.label || 'storage-lane-admission-history-runner'}:admission`, trace: config.trace || trace, ...(config.admissionOptions || {}) });
      const resilienceRunner = config.resilienceRunner || this.providerResilienceHistoryRunner({ label: `${config.label || 'storage-lane-admission-history-runner'}:resilience`, trace: config.trace || trace, ...(config.resilienceOptions || {}) });
      const mailbox = config.mailbox || resilienceRunner.mailbox;
      const runner = createStorageLaneAdmissionHistoryRunner({ ...config, admission, resilienceRunner, mailbox, trace: config.trace || trace });
      trace.emit('object:storage-lane-admission-history-runner-ref', { label: runner.label, admission: admission.label, resilience: resilienceRunner.label });
      return runner;
    },

    storageLaneAdmissionHistoryModelOracle(config = {}) {
      const oracle = createStorageLaneAdmissionHistoryModelOracle({ ...config, trace: config.trace || trace });
      trace.emit('object:storage-lane-admission-history-model-oracle-ref', { label: oracle.label, highWatermarkBytes: oracle.highWatermarkBytes, hardLimitBytes: oracle.hardLimitBytes });
      return oracle;
    },

    storageLaneOverloadGovernanceModelOracle(config = {}) {
      const oracle = createStorageLaneOverloadGovernanceModelOracle({ ...config, trace: config.trace || trace });
      trace.emit('object:storage-lane-overload-governance-model-oracle-ref', { label: oracle.label, historyCount: oracle.snapshot().historyCount });
      return oracle;
    },

    blockObjectRef(hash, fields) {
      const ref = createBlockObjectRef(hash, fields);
      trace.emit('object:block-ref', { id: ref.id, digest: ref.digest, bytes: ref.bytes, backend: ref.backend });
      return ref;
    },
    blockStore(config = {}) {
      return createMemoryBlockStore({ ...config, trace: config.trace || trace });
    },
    journaledBlockStore(config = {}) {
      return createJournaledMemoryBlockStore({ ...config, trace: config.trace || trace });
    },
    async recoverJournaledBlockStore(config = {}) {
      return await recoverJournaledMemoryBlockStore({ ...config, trace: config.trace || trace });
    },
    opfsAsyncBlockStore(config = {}) {
      const store = createOpfsAsyncBlockStore({ ...config, trace: config.trace || trace });
      trace.emit('object:opfs-async-block-store-ref', { label: store.name, provider: store.provider, prefix: store.prefix });
      return store;
    },
    blockStoreLaneAdapter(config = {}) {
      const adapter = createBlockStoreLaneAdapter({ ...config, trace: config.trace || trace });
      const snapshot = adapter.snapshot();
      trace.emit('object:block-store-lane-adapter-ref', { label: adapter.label, provider: adapter.providerName, lane: adapter.lane, resultCount: snapshot.resultCount });
      return adapter;
    },

    dreamBoundaryMap() {
      const map = createDreamBoundaryMap();
      trace.emit('object:dream-boundary-map-ref', { schema: map.schema, ambitionCount: map.ambitions.length, posture: map.posture });
      return map;
    },
    validateDreamBoundaryMap(map = createDreamBoundaryMap()) {
      const result = validateDreamBoundaryMap(map);
      trace.emit('dream-boundary:validate', { ok: result.ok, errorCount: result.errors.length });
      return result;
    },
    projectContinuationAssessment() {
      const assessment = createProjectContinuationAssessment();
      trace.emit('object:project-continuation-assessment-ref', { revision: assessment.revision, verdict: assessment.verdict, beneficiaryCount: assessment.beneficiaries.length });
      return assessment;
    },
    validateProjectContinuationAssessment(assessment = createProjectContinuationAssessment()) {
      const result = validateProjectContinuationAssessment(assessment);
      trace.emit('project-assessment:validate', { ok: result.ok, errorCount: result.errors.length });
      return result;
    },
    kernelKitDemoPlan() {
      const plan = createKernelKitDemoPlan();
      trace.emit('object:kernel-kit-demo-plan-ref', { codename: plan.codename, stepCount: plan.steps.length, posture: plan.posture });
      return plan;
    },
    validateKernelKitDemoReport(report) {
      const result = validateKernelKitDemoReport(report);
      trace.emit('kernel-kit-demo:validate', { ok: result.ok, errorCount: result.errors.length, stepCount: result.stepCount });
      return result;
    },
    kernelKitDemoTranscript(report) {
      const transcript = createKernelKitDemoTranscript(report);
      trace.emit('kernel-kit-demo:transcript', { status: transcript.status, passedCount: transcript.passedCount, stageCount: transcript.stageCount });
      return transcript;
    },
    validateKernelKitDemoTranscript(transcript) {
      const result = validateKernelKitDemoTranscript(transcript);
      trace.emit('kernel-kit-demo:transcript-validate', { ok: result.ok, errorCount: result.errors.length, passedCount: result.passedCount });
      return result;
    },
    kernelKitDemoUsefulnessScore(report) {
      const result = scoreKernelKitDemoUsefulness(report);
      trace.emit('kernel-kit-demo:usefulness-score', { grade: result.grade, passed: result.passed, total: result.total });
      return result;
    },
    kernelKitDemoTraceSummary(traceKindsOrEvents = []) {
      const result = summarizeKernelKitDemoTrace(traceKindsOrEvents);
      trace.emit('kernel-kit-demo:trace-summary', { traceCount: result.traceCount, uniqueKindCount: result.uniqueKindCount, complete: result.hasRequiredKernelKitTrace });
      return result;
    },

    kernelKitTraceExport(report, fields = {}) {
      const result = createKernelKitTraceExport(report, { revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:trace-export', { traceEventCount: result.chromeTrace.traceEvents.length, uniqueKindCount: result.summary.uniqueKindCount, format: result.format });
      return result;
    },
    validateKernelKitTraceExport(exportReport) {
      const result = validateKernelKitTraceExport(exportReport);
      trace.emit('kernel-kit-demo:trace-export-validate', { ok: result.ok, errorCount: result.errors.length, traceEventCount: result.traceEventCount });
      return result;
    },
    kernelKitDemoExportBundle(report, fields = {}) {
      const bundle = createKernelKitDemoExportBundle(report, { revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:export-bundle', { format: bundle.format, failureMode: bundle.failureMode || null, status: bundle.sourceStatus || null });
      return bundle;
    },
    validateKernelKitDemoExportBundle(bundle) {
      const result = validateKernelKitDemoExportBundle(bundle);
      trace.emit('kernel-kit-demo:export-bundle-validate', { ok: result.ok, errorCount: result.errors.length, failureMode: result.failureMode || null });
      return result;
    },
    kernelKitFailureModeReport(fields = {}) {
      const failureReport = createKernelKitFailureModeReport({ revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:failure-mode', { mode: failureReport.failureMode, status: failureReport.status });
      return failureReport;
    },
    validateKernelKitFailureModeReport(report) {
      const result = validateKernelKitFailureModeReport(report);
      trace.emit('kernel-kit-demo:failure-mode-validate', { ok: result.ok, errorCount: result.errors.length, mode: result.mode || null });
      return result;
    },
    kernelKitTraceComparison(successReport, failureReport, fields = {}) {
      const comparison = createKernelKitTraceComparison(successReport, failureReport, { revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:trace-comparison', { ok: validateKernelKitTraceComparison(comparison).ok, successOnlyTraceKindCount: comparison.diff.successOnlyTraceKinds.length, failureOnlyTraceKindCount: comparison.diff.failureOnlyTraceKinds.length });
      return comparison;
    },
    validateKernelKitTraceComparison(comparison) {
      const result = validateKernelKitTraceComparison(comparison);
      trace.emit('kernel-kit-demo:trace-comparison-validate', { ok: result.ok, errorCount: result.errors.length, successOnlyTraceKindCount: result.successOnlyTraceKindCount });
      return result;
    },
    kernelKitDiagnosticRunbook(comparison, fields = {}) {
      const runbook = createKernelKitDiagnosticRunbook(comparison, { revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:diagnostic-runbook', { ok: validateKernelKitDiagnosticRunbook(runbook).ok, cardCount: runbook.cards.length, commandCount: runbook.exactCommands.length });
      return runbook;
    },
    validateKernelKitDiagnosticRunbook(runbook) {
      const result = validateKernelKitDiagnosticRunbook(runbook);
      trace.emit('kernel-kit-demo:diagnostic-runbook-validate', { ok: result.ok, errorCount: result.errors.length, cardCount: result.cardCount });
      return result;
    },
    kernelKitSupportBundle(fields = {}) {
      const bundle = createKernelKitSupportBundle({ revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:support-bundle', { ok: validateKernelKitSupportBundle(bundle).ok, sectionCount: bundle.sections.length, commandCount: bundle.exactCommands.length });
      return bundle;
    },
    validateKernelKitSupportBundle(bundle) {
      const result = validateKernelKitSupportBundle(bundle);
      trace.emit('kernel-kit-demo:support-bundle-validate', { ok: result.ok, errorCount: result.errors.length, sectionCount: result.sectionCount });
      return result;
    },

    kernelKitGuidedTour(fields = {}) {
      const tour = createKernelKitGuidedTour({ revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:guided-tour', { ok: validateKernelKitGuidedTour(tour).ok, stepCount: tour.tourSteps.length, audience: tour.audience });
      return tour;
    },
    validateKernelKitGuidedTour(tour) {
      const result = validateKernelKitGuidedTour(tour);
      trace.emit('kernel-kit-demo:guided-tour-validate', { ok: result.ok, errorCount: result.errors.length, stepCount: result.stepCount, audience: result.audience });
      return result;
    },
    kernelKitSupportBundleImportReport(input, fields = {}) {
      const report = createKernelKitSupportBundleImportReport(input, { revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:support-bundle-import', { ok: report.status === 'passed', importedRevision: report.imported?.revision || null, versionSkew: report.imported?.versionSkew === true, commandCount: report.imported?.commandCount || 0 });
      return report;
    },
    validateKernelKitSupportBundleImportReport(report) {
      const result = validateKernelKitSupportBundleImportReport(report);
      trace.emit('kernel-kit-demo:support-bundle-import-validate', { ok: result.ok, errorCount: result.errors.length, versionSkew: result.versionSkew === true });
      return result;
    },
    kernelKitSupportBundleDiff(currentBundle, candidateBundle, fields = {}) {
      const diff = createKernelKitSupportBundleDiff(currentBundle, candidateBundle, { revision: REVISION, ...fields });
      const validation = validateKernelKitSupportBundleDiff(diff);
      trace.emit('kernel-kit-demo:support-bundle-diff', { ok: validation.ok, status: diff.status, riskCount: validation.riskCount, proofRowCount: validation.proofRowCount });
      return diff;
    },
    validateKernelKitSupportBundleDiff(diff) {
      const result = validateKernelKitSupportBundleDiff(diff);
      trace.emit('kernel-kit-demo:support-bundle-diff-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, riskCount: result.riskCount });
      return result;
    },

    kernelKitHandoffMarkdown(fields = {}) {
      const report = createKernelKitHandoffMarkdown({ revision: REVISION, ...fields });
      const validation = validateKernelKitHandoffMarkdown(report);
      trace.emit('kernel-kit-demo:handoff-markdown', { ok: validation.ok, status: report.status, commandCount: validation.commandCount, markdownBytes: validation.markdownBytes });
      return report;
    },
    validateKernelKitHandoffMarkdown(report) {
      const result = validateKernelKitHandoffMarkdown(report);
      trace.emit('kernel-kit-demo:handoff-markdown-validate', { ok: result.ok, errorCount: result.errors.length, commandCount: result.commandCount, markdownBytes: result.markdownBytes });
      return result;
    },
    kernelKitDemoHandoff(report, fields = {}) {
      const handoff = createKernelKitDemoHandoff(report, { revision: REVISION, ...fields });
      trace.emit('kernel-kit-demo:handoff', { ok: validateKernelKitDemoHandoff(handoff).ok, hasRef: Boolean(handoff.ref), storageKey: handoff.storageKey });
      return handoff;
    },
    validateKernelKitDemoHandoff(handoff) {
      const result = validateKernelKitDemoHandoff(handoff);
      trace.emit('kernel-kit-demo:handoff-validate', { ok: result.ok, errorCount: result.errors.length, requiredKeyCount: result.requiredKeyCount });
      return result;
    },

    kernelKitDemoUsefulnessReport(report, fields = {}) {
      const usefulness = createKernelKitDemoUsefulnessReport(report, { revision: REVISION, ...fields });
      trace.emit('object:kernel-kit-demo-usefulness-ref', { codename: usefulness.codename, status: usefulness.status, earnedWorkflowCount: usefulness.workflowScorecard.filter((row) => row.status === 'earned').length, strongBeneficiaryCount: usefulness.strongBeneficiaries.length });
      return usefulness;
    },
    validateKernelKitDemoUsefulnessReport(report) {
      const result = validateKernelKitDemoUsefulnessReport(report);
      trace.emit('kernel-kit-demo-usefulness:validate', { ok: result.ok, errorCount: result.errors.length, earnedWorkflowCount: result.earnedWorkflowCount });
      return result;
    },

    kernelKitDemoObservatory(report, fields = {}) {
      const observatory = createKernelKitDemoObservatoryReport(report, { revision: REVISION, ...fields });
      trace.emit('object:kernel-kit-demo-observatory-ref', { codename: observatory.codename, observedStageCount: observatory.proofReceipt?.observedStageCount, traceKindCount: observatory.traceSummary?.uniqueKindCount });
      return observatory;
    },
    validateKernelKitDemoObservatoryReport(report) {
      const result = validateKernelKitDemoObservatoryReport(report);
      trace.emit('kernel-kit-demo-observatory:validate', { ok: result.ok, errorCount: result.errors.length, observedStageCount: result.observedStageCount });
      return result;
    },


    kernelKitGuidedTourReceipt(fields = {}) {
      const receipt = createKernelKitGuidedTourReceipt({ revision: REVISION, ...fields });
      trace.emit('object:kernel-kit-guided-tour-ref', { status: receipt.status, passedCount: receipt.passedCount, stepCount: receipt.stepCount });
      return receipt;
    },
    validateKernelKitGuidedTourReceipt(receipt) {
      const result = validateKernelKitGuidedTourReceipt(receipt);
      trace.emit('kernel-kit-guided-tour:validate', { ok: result.ok, errorCount: result.errors.length, stepCount: result.stepCount });
      return result;
    },

    kernelKitHandoffMarkdownImport(markdown, fields = {}) {
      const report = createKernelKitHandoffMarkdownImportReport(markdown, { revision: REVISION, ...fields });
      trace.emit('object:kernel-kit-handoff-markdown-import-ref', { status: report.status, commandCount: report.resumeCommands.length, riskCount: report.riskFlags.length });
      return report;
    },
    validateKernelKitHandoffMarkdownImportReport(report) {
      const result = validateKernelKitHandoffMarkdownImportReport(report);
      trace.emit('kernel-kit-handoff-markdown-import:validate', { ok: result.ok, errorCount: result.errors.length, commandCount: result.commandCount, riskCount: result.riskCount });
      return result;
    },

    kernelKitReadinessGate(fields = {}) {
      const report = createKernelKitReadinessGate({ revision: REVISION, ...fields });
      trace.emit('object:kernel-kit-readiness-gate-ref', { status: report.status, passedGateCount: report.readinessSummary?.passedGateCount, gateCount: report.readinessSummary?.gateCount });
      return report;
    },
    validateKernelKitReadinessGate(report) {
      const result = validateKernelKitReadinessGate(report);
      trace.emit('kernel-kit-readiness-gate:validate', { ok: result.ok, errorCount: result.errors.length, gateCount: result.gateCount, personaCount: result.personaCount });
      return result;
    },

    kernelKitReadinessContrast(fields = {}) {
      const report = createKernelKitReadinessContrast({ revision: REVISION, ...fields });
      trace.emit('object:kernel-kit-readiness-contrast-ref', { status: report.status, changedGateCount: report.gateDiff?.filter?.((row) => row.changed === true).length || 0, missingGateCount: report.degraded?.missingGateIds?.length || 0 });
      return report;
    },
    validateKernelKitReadinessContrast(report) {
      const result = validateKernelKitReadinessContrast(report);
      trace.emit('kernel-kit-readiness-contrast:validate', { ok: result.ok, errorCount: result.errors.length, changedGateCount: result.changedGateCount, missingGateCount: result.missingGateCount });
      return result;
    },


    opfsBlockStoreStorageLaneAdapter(config = {}) {
      const store = config.store || this.opfsAsyncBlockStore({
        name: `${config.label || 'opfs-storage-lane-adapter'}:store`,
        prefix: config.prefix || `browserrt/${REVISION}/opfs-storage-lane-adapter`,
        trace: config.trace || trace,
        ...(config.storeConfig || {})
      });
      const scheduler = config.scheduler || this.crossLaneScheduler({
        label: `${config.label || 'opfs-storage-lane-adapter'}:scheduler`,
        trace: config.trace || trace,
        lanes: config.lanes || [
          { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
          { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
        ]
      });
      const adapter = createOpfsBlockStoreStorageLaneAdapter({ ...config, store, scheduler, trace: config.trace || trace });
      const snapshot = adapter.snapshot();
      trace.emit('object:opfs-storage-lane-adapter-ref', { label: adapter.label, provider: snapshot.store?.provider, prefix: snapshot.store?.prefix, lane: adapter.lane, supportedOps: OPFS_STORAGE_LANE_ADAPTER_SUPPORTED_OPS });
      return adapter;
    },
    async opfsAsyncWriteReadProbe(config = {}) {
      trace.emit('storage:opfs-async-probe-start', { path: config.path ?? `browserrt/${REVISION}/opfs-async-proof.bin` });
      const result = await opfsAsyncWriteReadProbe(config);
      trace.emit('storage:opfs-async-probe-result', { path: result.path, bytesWritten: result.bytesWritten, bytesRead: result.bytesRead, same: result.same, digest: result.digest });
      return result;
    },
    async spawnAgent(config = {}) { return await spawnWorkerAgent({ ...config, trace: config.trace || trace }); },
    supervisor(config = {}) { return createSupervisor({ ...config, trace: config.trace || trace }); },
    close() {
      trace.emit('runtime:close', { revision: REVISION });
      return trace.snapshot();
    }
  });
}


export { SharedInt32Ring, createSharedInt32Ring, openSharedInt32Ring } from './sab-ring.mjs';
export { SharedFrameRing, createSharedFrameRing, openSharedFrameRing } from './sab-frame-ring.mjs';
export { SpillFrameMailbox, createSpillFrameMailbox, checksumFramePayload32 } from './spill-mailbox.mjs';
export { PersistedSpillMailbox, createPersistedSpillMailbox, recoverPersistedSpillMailbox, checksumPersistedSpillPayload32 } from './persisted-spill-mailbox.mjs';
export { WatermarkAdmissionController, createWatermarkAdmissionController } from './admission-control.mjs';
export { AdaptiveConcurrencyController, createAdaptiveConcurrencyController } from './adaptive-concurrency.mjs';
export { PriorityFairScheduler, createPriorityFairScheduler, PRIORITY_FAIRNESS_ORDER } from './priority-fairness.mjs';

export { CrossLaneScheduler, createCrossLaneScheduler, CROSS_LANE_PRIORITY_ORDER, validateCrossLaneSchedulerSnapshot } from './cross-lane-scheduler.mjs';


export { StorageLaneExecutor, createStorageLaneExecutor, STORAGE_LANE_EXECUTOR_SUPPORTED_OPS, validateStorageLaneExecutorSnapshot } from './storage-lane-scheduler.mjs';
export { BlockStoreLaneAdapter, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, BLOCK_STORE_LANE_ADAPTER_OPS } from './block-store-lane-adapter.mjs';

export { StorageLaneRetryPolicy, StorageLaneRetryController, createStorageLaneRetryPolicy, createStorageLaneRetryController } from './storage-lane-retry.mjs';
export { RetryBudgetAdmissionController, createRetryBudgetAdmissionController, validateRetryBudgetAdmissionSnapshot } from './retry-budget-admission.mjs';
export { CircuitBreakerBulkheadController, createCircuitBreakerBulkheadController, validateCircuitBreakerBulkheadSnapshot } from './circuit-breaker-bulkhead.mjs';
export { ProviderResilienceHistoryRunner, createProviderResilienceHistoryRunner, validateProviderResilienceHistorySnapshot } from './provider-resilience-history.mjs';
export { ProviderResilienceModelOracle, createProviderResilienceModelOracle, compareProviderResilienceHistoryToModel, validateProviderResilienceModelSnapshot } from './provider-resilience-model.mjs';
export { StorageLaneAdmissionHistoryRunner, createStorageLaneAdmissionHistoryRunner, validateStorageLaneAdmissionHistorySnapshot } from './storage-lane-admission-history.mjs';
export { StorageLaneAdmissionHistoryModelOracle, createStorageLaneAdmissionHistoryModelOracle, compareStorageLaneAdmissionHistoryToModel, validateStorageLaneAdmissionHistoryModelSnapshot } from './storage-lane-admission-model.mjs';
export { StorageLaneOverloadGovernanceModelOracle, createStorageLaneOverloadGovernanceModelOracle, compareStorageLaneOverloadGovernanceToRuntime, validateStorageLaneOverloadGovernanceSnapshot } from './storage-lane-overload-governance.mjs';
export { OpfsAsyncBlockStore, createOpfsAsyncBlockStore } from './opfs-block-store.mjs';
export { OpfsBlockStoreStorageLaneAdapter, createOpfsBlockStoreStorageLaneAdapter, validateOpfsStorageLaneAdapterSnapshot, OPFS_STORAGE_LANE_ADAPTER_SUPPORTED_OPS } from './opfs-storage-lane-adapter.mjs';
export { createDreamBoundaryMap, validateDreamBoundaryMap, DREAM_BOUNDARY_CATEGORIES, DREAM_BOUNDARY_AREAS } from './dream-boundary.mjs';
export { createProjectContinuationAssessment, validateProjectContinuationAssessment, PROJECT_ASSESSMENT_AUDIENCES, PROJECT_ASSESSMENT_POSTURES } from './project-assessment.mjs';
export { createKernelKitDemoPlan, validateKernelKitDemoPlan, validateKernelKitDemoProof, validateKernelKitDemoReport, summarizeKernelKitDemoTrace, scoreKernelKitDemoUsefulness, createKernelKitDemoTranscript, validateKernelKitDemoTranscript, createKernelKitTraceExport, validateKernelKitTraceExport, createKernelKitDemoHandoff, validateKernelKitDemoHandoff, KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY, KERNEL_KIT_DEMO_HANDOFF_REQUIRED_KEYS, KERNEL_KIT_DEMO_EXPORT_FORMATS, KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS, KERNEL_KIT_DEMO_FAILURE_MODES, KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT, KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS, createKernelKitDemoExportBundle, validateKernelKitDemoExportBundle, createKernelKitFailureModeReport, validateKernelKitFailureModeReport, createKernelKitTraceComparison, validateKernelKitTraceComparison, createKernelKitDiagnosticRunbook, validateKernelKitDiagnosticRunbook, createKernelKitSupportBundle, validateKernelKitSupportBundle, createKernelKitSupportBundleImportReport, validateKernelKitSupportBundleImportReport, createKernelKitSupportBundleDiff, validateKernelKitSupportBundleDiff, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_NON_CLAIMS, KERNEL_KIT_TRACE_COMPARISON_FORMAT, KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS, createKernelKitGuidedTour, validateKernelKitGuidedTour, createKernelKitGuidedTourReceipt, validateKernelKitGuidedTourReceipt, KERNEL_KIT_GUIDED_TOUR_FORMAT, KERNEL_KIT_GUIDED_TOUR_STEPS, KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS, KERNEL_KIT_DEMO_CODENAME, KERNEL_KIT_DEMO_STEPS, KERNEL_KIT_DEMO_REQUIRED_STEPS, KERNEL_KIT_DEMO_STAGE_LABELS, KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS, KERNEL_KIT_DEMO_NON_CLAIMS };
export { createKernelKitHandoffMarkdown, validateKernelKitHandoffMarkdown, KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT, KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS } from './kernel-kit-handoff-markdown.mjs';
export { createKernelKitHandoffMarkdownImportReport, validateKernelKitHandoffMarkdownImportReport, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS, KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS } from './kernel-kit-handoff-reader.mjs';
export { createKernelKitReadinessGate, validateKernelKitReadinessGate, KERNEL_KIT_READINESS_GATE_FORMAT, KERNEL_KIT_READINESS_GATE_NON_CLAIMS, KERNEL_KIT_READINESS_GATE_REQUIRED_GATES, KERNEL_KIT_READINESS_GATE_PERSONAS } from './kernel-kit-readiness-gate.mjs';
export { createKernelKitReadinessContrast, validateKernelKitReadinessContrast, createDegradedKernelKitReadinessGate, KERNEL_KIT_READINESS_CONTRAST_FORMAT, KERNEL_KIT_READINESS_CONTRAST_NON_CLAIMS, KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES } from './kernel-kit-readiness-contrast.mjs';
export { createKernelKitDemoObservatoryReport, validateKernelKitDemoObservatoryReport, KERNEL_KIT_OBSERVATORY_CODENAME, KERNEL_KIT_OBSERVATORY_REQUIRED_SECTIONS, KERNEL_KIT_OBSERVATORY_NON_CLAIMS };
export { createKernelKitDemoUsefulnessReport, validateKernelKitDemoUsefulnessReport, KERNEL_KIT_USEFULNESS_CODENAME, KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS, KERNEL_KIT_USEFULNESS_AUDIENCES, KERNEL_KIT_USEFULNESS_NON_CLAIMS };
