import { createSharedInt32Ring, openSharedInt32Ring, SharedInt32Ring } from './sab-ring.mjs';
import { createSharedFrameRing, openSharedFrameRing, SharedFrameRing } from './sab-frame-ring.mjs';
import { createSpillFrameMailbox, SpillFrameMailbox } from './spill-mailbox.mjs';
import { createPersistedSpillMailbox, recoverPersistedSpillMailbox, PersistedSpillMailbox } from './persisted-spill-mailbox.mjs'; // PersistedSpillMailbox.compact() retained-ref compaction
import { createWatermarkAdmissionController, WatermarkAdmissionController } from './admission-control.mjs';
import { createAdaptiveConcurrencyController, AdaptiveConcurrencyController } from './adaptive-concurrency.mjs';
import { createPriorityFairScheduler, PriorityFairScheduler, PRIORITY_FAIRNESS_ORDER } from './priority-fairness.mjs';
import { createCrossLaneScheduler, CrossLaneScheduler, CROSS_LANE_PRIORITY_ORDER, validateCrossLaneSchedulerSnapshot } from './cross-lane-scheduler.mjs';
import { createStorageLaneExecutor, StorageLaneExecutor, STORAGE_LANE_EXECUTOR_SUPPORTED_OPS, validateStorageLaneExecutorSnapshot } from './storage-lane-scheduler.mjs';
import { BlockStoreLaneAdapter, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, BLOCK_STORE_LANE_ADAPTER_OPS, createTimedOutOperationQuarantineClearanceReceipt, validateTimedOutOperationQuarantineClearanceReceipt, timedOutOperationQuarantineClearanceReceiptFingerprint } from './block-store-lane-adapter.mjs';
import { createStorageLaneRetryPolicy, createStorageLaneRetryController, StorageLaneRetryPolicy, StorageLaneRetryController } from './storage-lane-retry.mjs';
import { createRetryBudgetAdmissionController, RetryBudgetAdmissionController, validateRetryBudgetAdmissionSnapshot } from './retry-budget-admission.mjs';
import { createCircuitBreakerBulkheadController, CircuitBreakerBulkheadController, validateCircuitBreakerBulkheadSnapshot } from './circuit-breaker-bulkhead.mjs';
import { createProviderResilienceHistoryRunner, ProviderResilienceHistoryRunner, validateProviderResilienceHistorySnapshot } from './provider-resilience-history.mjs';
import { createProviderResilienceModelOracle, ProviderResilienceModelOracle, compareProviderResilienceHistoryToModel, validateProviderResilienceModelSnapshot } from './provider-resilience-model.mjs';
import { createStorageLaneAdmissionHistoryRunner, StorageLaneAdmissionHistoryRunner, validateStorageLaneAdmissionHistorySnapshot } from './storage-lane-admission-history.mjs';
import { createStorageLaneAdmissionHistoryModelOracle, StorageLaneAdmissionHistoryModelOracle, compareStorageLaneAdmissionHistoryToModel, validateStorageLaneAdmissionHistoryModelSnapshot } from './storage-lane-admission-model.mjs';
import { createStorageLaneOverloadGovernanceModelOracle, StorageLaneOverloadGovernanceModelOracle, compareStorageLaneOverloadGovernanceToRuntime, validateStorageLaneOverloadGovernanceSnapshot } from './storage-lane-overload-governance.mjs';
import { createOpfsAsyncBlockStore, OpfsAsyncBlockStore, classifyOpfsBlockStoreError } from './opfs-block-store.mjs';
import { createOpfsBlockStoreStorageLaneAdapter, OpfsBlockStoreStorageLaneAdapter, validateOpfsStorageLaneAdapterSnapshot, OPFS_STORAGE_LANE_ADAPTER_SUPPORTED_OPS } from './opfs-storage-lane-adapter.mjs';
import { createWebLockCoordinator, WebLockCoordinator } from './web-lock-coordinator.mjs';
import { createWebLockGuardedBlockStore, WebLockGuardedBlockStore } from './opfs-web-lock-guarded-block-store.mjs';
import { createDreamBoundaryMap, validateDreamBoundaryMap, DREAM_BOUNDARY_CATEGORIES, DREAM_BOUNDARY_AREAS } from './dream-boundary.mjs';
import { createProjectContinuationAssessment, validateProjectContinuationAssessment, PROJECT_ASSESSMENT_AUDIENCES, PROJECT_ASSESSMENT_POSTURES } from './project-assessment.mjs';
import { createKernelKitDemoPlan, validateKernelKitDemoPlan, validateKernelKitDemoProof, validateKernelKitDemoReport, summarizeKernelKitDemoTrace, scoreKernelKitDemoUsefulness, createKernelKitDemoTranscript, validateKernelKitDemoTranscript, createKernelKitTraceExport, validateKernelKitTraceExport, createKernelKitDemoHandoff, validateKernelKitDemoHandoff, KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY, KERNEL_KIT_DEMO_HANDOFF_REQUIRED_KEYS, KERNEL_KIT_DEMO_EXPORT_FORMATS, KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS, KERNEL_KIT_DEMO_FAILURE_MODES, KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT, KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS, createKernelKitDemoExportBundle, validateKernelKitDemoExportBundle, createKernelKitFailureModeReport, validateKernelKitFailureModeReport, createKernelKitTraceComparison, validateKernelKitTraceComparison, createKernelKitDiagnosticRunbook, validateKernelKitDiagnosticRunbook, createKernelKitSupportBundle, validateKernelKitSupportBundle, createKernelKitSupportBundlePrivacyScrub, validateKernelKitSupportBundlePrivacyScrub, KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_NON_CLAIMS, createKernelKitSupportBundleImportReport, validateKernelKitSupportBundleImportReport, createKernelKitSupportBundleDiff, validateKernelKitSupportBundleDiff, createKernelKitSupportBundleReplayPlan, validateKernelKitSupportBundleReplayPlan, createKernelKitSupportBundleOperatorPreflightDisplaySnapshot, validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot, KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_PREFLIGHT_DISPLAY_SNAPSHOT_FORMAT, createKernelKitSupportBundleOperatorReplayGate, validateKernelKitSupportBundleOperatorReplayGate, KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_REPLAY_GATE_FORMAT, createKernelKitSupportBundleEvidenceLedger, validateKernelKitSupportBundleEvidenceLedger, createKernelKitSupportBundleEvidenceCheckpoint, validateKernelKitSupportBundleEvidenceCheckpoint, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PHASE_IDS, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_NON_CLAIMS, KERNEL_KIT_TRACE_COMPARISON_FORMAT, KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS, createKernelKitGuidedTour, validateKernelKitGuidedTour, createKernelKitGuidedTourReceipt, validateKernelKitGuidedTourReceipt, KERNEL_KIT_GUIDED_TOUR_FORMAT, KERNEL_KIT_GUIDED_TOUR_STEPS, KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS, KERNEL_KIT_DEMO_CODENAME, KERNEL_KIT_DEMO_STEPS, KERNEL_KIT_DEMO_REQUIRED_STEPS, KERNEL_KIT_DEMO_STAGE_LABELS, KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS, KERNEL_KIT_DEMO_NON_CLAIMS } from './kernel-kit-demo.mjs';
import { createKernelKitDemoObservatoryReport, validateKernelKitDemoObservatoryReport, KERNEL_KIT_OBSERVATORY_CODENAME, KERNEL_KIT_OBSERVATORY_REQUIRED_SECTIONS, KERNEL_KIT_OBSERVATORY_NON_CLAIMS } from './kernel-kit-demo-observatory.mjs';
import { createKernelKitHandoffMarkdown, validateKernelKitHandoffMarkdown, KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT, KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS } from './kernel-kit-handoff-markdown.mjs';
import { createKernelKitHandoffMarkdownImportReport, validateKernelKitHandoffMarkdownImportReport, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS, KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS } from './kernel-kit-handoff-reader.mjs';
import { createKernelKitReadinessGate, validateKernelKitReadinessGate, KERNEL_KIT_READINESS_GATE_FORMAT, KERNEL_KIT_READINESS_GATE_NON_CLAIMS, KERNEL_KIT_READINESS_GATE_REQUIRED_GATES, KERNEL_KIT_READINESS_GATE_PERSONAS } from './kernel-kit-readiness-gate.mjs';
import { createKernelKitReadinessContrast, validateKernelKitReadinessContrast, createDegradedKernelKitReadinessGate, KERNEL_KIT_READINESS_CONTRAST_FORMAT, KERNEL_KIT_READINESS_CONTRAST_NON_CLAIMS, KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES } from './kernel-kit-readiness-contrast.mjs';
import { createKernelKitLifecycleCheckpoint, validateKernelKitLifecycleCheckpoint, KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT, KERNEL_KIT_LIFECYCLE_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS } from './kernel-kit-lifecycle-checkpoint.mjs';
import { createKernelKitSessionCoordinationCheckpoint, validateKernelKitSessionCoordinationCheckpoint, KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT, KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_REQUIRED_ROWS } from './kernel-kit-session-coordination-checkpoint.mjs';
import { createKernelKitRecoveryCheckpoint, validateKernelKitRecoveryCheckpoint, KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT, KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_RECOVERY_CHECKPOINT_REQUIRED_ROWS } from './kernel-kit-recovery-checkpoint.mjs';
import { createKernelKitAdmissionCancellationCheckpoint, validateKernelKitAdmissionCancellationCheckpoint, KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT, KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_REQUIRED_ROWS } from './kernel-kit-admission-cancellation-checkpoint.mjs';
import { createKernelKitDemoUsefulnessReport, validateKernelKitDemoUsefulnessReport, KERNEL_KIT_USEFULNESS_CODENAME, KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS, KERNEL_KIT_USEFULNESS_AUDIENCES, KERNEL_KIT_USEFULNESS_NON_CLAIMS } from './kernel-kit-demo-usefulness.mjs';
import { diagnoseBrowserStoragePosture, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT } from './browser-storage-posture.mjs';
import { BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT, createBrowserStorageRecoveryGuidance } from './browser-storage-recovery-guidance.mjs';
export const VERSION = '0.0.125';
export const REVISION = 'rev0125';
export const POSTURED_WEB_LOCK_DEFAULT_TIMEOUT_MS = 15000;
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
  if (errorLike?.code) err.code = errorLike.code;
  return err;
}
function createBrowserRtError(message, { name = 'BrowserRTError', code = null, detail = null } = {}) {
  const err = new Error(message);
  err.name = name;
  if (code) err.code = code;
  if (detail !== null) err.detail = detail;
  return err;
}
function createAbortError(message, detail = null) {
  return createBrowserRtError(message, { name: 'AbortError', code: 'BRT_ABORTED', detail });
}
function assertAbortSignalLike(signal, label = 'signal') {
  if (signal == null) return null;
  if (typeof signal.aborted !== 'boolean' || typeof signal.addEventListener !== 'function' || typeof signal.removeEventListener !== 'function') {
    throw createBrowserRtError(`${label} must be an AbortSignal-like object`, { code: 'BRT_ABORT_SIGNAL_INVALID' });
  }
  return signal;
}
function normalizePositiveInteger(value, fallback, label) {
  if (value === undefined || value === null) return fallback;
  const n = Number(value);
  if (!Number.isInteger(n) || n < 0) throw createBrowserRtError(`${label} must be a non-negative integer`, { code: 'BRT_INVALID_LIMIT' });
  return n;
}
function normalizeTimeoutMs(value, fallback = 0, label = 'timeoutMs') {
  if (value === undefined || value === null) return fallback;
  const n = Number(value);
  if (!Number.isFinite(n) || n < 0) throw createBrowserRtError(`${label} must be a non-negative finite number`, { code: 'BRT_INVALID_TIMEOUT' });
  return Math.floor(n);
}
function hasOwnOption(value, key) {
  return Object.prototype.hasOwnProperty.call(value || {}, key);
}
function posturedWriteBudgetGuardOverride(config = {}) {
  const storeConfig = config.storeConfig && typeof config.storeConfig === 'object' ? config.storeConfig : {};
  const topLevelSupplied = hasOwnOption(config, 'writeBudgetGuard') && config.writeBudgetGuard !== undefined;
  const storeConfigSupplied = hasOwnOption(storeConfig, 'writeBudgetGuard') && storeConfig.writeBudgetGuard !== undefined;
  const supplied = topLevelSupplied || storeConfigSupplied;
  const source = topLevelSupplied ? 'config.writeBudgetGuard' : (storeConfigSupplied ? 'storeConfig.writeBudgetGuard' : null);
  const value = topLevelSupplied ? config.writeBudgetGuard : (storeConfigSupplied ? storeConfig.writeBudgetGuard : undefined);
  return Object.freeze({ supplied, source, value, disabled: value === false || value === null, valueType: value === null ? 'null' : typeof value });
}
function resolvePosturedWriteBudgetGuard(config = {}, admissionPolicy = {}, { label = 'postured-opfs-block-store', trace = null } = {}) {
  const override = posturedWriteBudgetGuardOverride(config);
  const allowUnsafeOverride = config.allowPostureWriteBudgetGuardOverride === true || config.allowUnsafeWriteBudgetGuardOverride === true;
  const policy = Object.freeze({
    format: 'browserrt.postured-write-budget-guard-policy.v1',
    label,
    suppliedOverride: override.supplied,
    overrideSource: override.source,
    overrideDisabled: override.disabled,
    allowUnsafeOverride,
    enforced: !override.supplied || !allowUnsafeOverride,
    guardSource: override.supplied && allowUnsafeOverride ? override.source : (admissionPolicy.writeBudgetGuard?.source || null),
    nonClaims: Object.freeze([
      'Postured guard enforcement is not quota reservation.',
      'Unsafe override is caller-owned; no eviction, fsync, or cross-tab claim.'
    ])
  });
  if (override.supplied && !allowUnsafeOverride) {
    const message = 'BrowserRT postured OPFS factory rejected explicit writeBudgetGuard override';
    const detail = {
      label,
      source: override.source,
      valueType: override.valueType,
      disabled: override.disabled,
      admissionStatus: admissionPolicy.status || null,
      plannedWriteBytes: admissionPolicy.plannedWriteBytes ?? null,
      plannedBudgetedBytes: admissionPolicy.plannedBudgetedBytes ?? null,
      postureGuardPolicy: policy,
      mutationAttempted: false
    };
    detail.recovery = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTStorageGuardOverrideError', code: 'BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED', message, detail }, { op: 'opfsAsyncBlockStoreWithPosture', phase: 'posture-guard-override' });
    detail.preMutationRejected = detail.recovery.preMutationRejected;
    trace?.emit('storage:opfs-block-store-posture-guard-override-rejected', detail);
    trace?.emit('runtime:browser-storage-recovery-guidance', { code: detail.recovery.code, category: detail.recovery.category, phase: detail.recovery.phase, action: detail.recovery.action, preMutationRejected: detail.recovery.preMutationRejected });
    throw createBrowserRtError(message, { name: 'BrowserRTStorageGuardOverrideError', code: 'BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED', detail });
  }
  if (override.supplied && allowUnsafeOverride) {
    trace?.emit('storage:opfs-block-store-posture-guard-override-accepted', { label, source: override.source, disabled: override.disabled, postureGuardPolicy: policy });
    return Object.freeze({ guard: override.value, override, policy });
  }
  return Object.freeze({ guard: admissionPolicy.writeBudgetGuard, override, policy });
}
function normalizePosturedWebLockTimeoutMs(config = {}) {
  const explicitLockTimeout = hasOwnOption(config, 'lockTimeoutMs');
  const explicitContentionTimeout = hasOwnOption(config, 'lockContentionTimeoutMs');
  const selected = explicitLockTimeout ? config.lockTimeoutMs : (explicitContentionTimeout ? config.lockContentionTimeoutMs : POSTURED_WEB_LOCK_DEFAULT_TIMEOUT_MS);
  const label = explicitLockTimeout ? 'lockTimeoutMs' : 'lockContentionTimeoutMs';
  const lockTimeoutMs = normalizeTimeoutMs(selected, POSTURED_WEB_LOCK_DEFAULT_TIMEOUT_MS, label);
  const allowUnbounded = config.allowUnboundedPostureLockWait === true || config.allowUnsafeUnboundedPostureLockWait === true;
  if (lockTimeoutMs <= 0 && !allowUnbounded) {
    const message = 'BrowserRT postured Web-Lock guarded factory rejected unbounded lock acquisition timeout';
    const detail = { source: label, selected, lockTimeoutMs, defaultTimeoutMs: POSTURED_WEB_LOCK_DEFAULT_TIMEOUT_MS, allowUnboundedPostureLockWait: false, mutationAttempted: false };
    detail.recovery = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTWebLockTimeoutPolicyError', code: 'BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED', message, detail }, { op: 'opfsWebLockGuardedBlockStoreWithPosture', phase: 'coordination-admission', timeoutMs: POSTURED_WEB_LOCK_DEFAULT_TIMEOUT_MS });
    detail.preMutationRejected = detail.recovery.preMutationRejected;
    throw createBrowserRtError(message, { name: 'BrowserRTWebLockTimeoutPolicyError', code: 'BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED', detail });
  }
  return Object.freeze({
    enabled: lockTimeoutMs > 0,
    lockTimeoutMs,
    defaulted: !explicitLockTimeout && !explicitContentionTimeout,
    allowUnbounded,
    source: 'postured-web-lock-guarded-opfs-factory',
    reason: 'bound Web Lock acquisition waits before OPFS mutation on the safer shared-state factory',
    nonClaims: Object.freeze([
      'The timeout bounds Web Lock acquisition only; it does not interrupt a callback after the lock has been granted.',
      'A bounded wait is not a fairness, starvation-freedom, tab-lifecycle, durability, quota, or eviction-survival guarantee.'
    ])
  });
}
function normalizePosturedWebLockFallbackPolicy(config = {}, { label = 'postured-web-lock-guarded-opfs', lockAvailable = false, requireWebLocks = true, lockContentionPolicy = null } = {}) {
  const allowUnsafeSingleOwnerFallback = config.allowUnsafeSingleOwnerFallback === true || config.allowPostureSingleOwnerFallback === true || config.allowUnlockedSingleOwnerFallback === true;
  const singleOwnerFallbackRequested = requireWebLocks === false && !lockAvailable;
  const policy = Object.freeze({
    format: 'browserrt.postured-web-lock-fallback-policy.v1',
    label,
    lockAvailable: lockAvailable === true,
    requireWebLocks,
    singleOwnerFallbackRequested,
    allowUnsafeSingleOwnerFallback,
    enforced: !singleOwnerFallbackRequested || !allowUnsafeSingleOwnerFallback,
    source: 'postured-web-lock-guarded-opfs-factory',
    nonClaims: Object.freeze(['Single-owner fallback is caller-scoped only; it is not cross-tab/cross-worker coordination.', 'Fallback still carries quota/durability non-claims.'])
  });
  if (singleOwnerFallbackRequested && !allowUnsafeSingleOwnerFallback) {
    const message = 'BrowserRT postured guarded OPFS store rejected unlocked single-owner fallback';
    const detail = { label, requireWebLocks, lockAvailable: false, lockContentionPolicy, singleOwnerFallbackRequested, allowUnsafeSingleOwnerFallback: false, mutationAttempted: false, fallbackPolicy: policy };
    detail.recovery = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTWebLockFallbackPolicyError', code: 'BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED', message, detail }, { op: 'opfsWebLockGuardedBlockStoreWithPosture', phase: 'coordination-admission', timeoutMs: lockContentionPolicy?.lockTimeoutMs });
    detail.preMutationRejected = detail.recovery.preMutationRejected;
    throw createBrowserRtError(message, { name: 'BrowserRTWebLockFallbackPolicyError', code: 'BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED', detail });
  }
  return policy;
}
function signalReason(signal) {
  return signal?.reason instanceof Error ? signal.reason : signal?.reason || null;
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
  const id = fields.id ?? nextId(kind);
  const ownership = fields.ownership ?? (kind === 'transfer' ? 'owned-main' : 'unspecified');
  const createdAt = fields.createdAt ?? Date.now();
  return Object.freeze({
    ...fields,
    kind,
    id,
    bytes,
    ownership,
    createdAt
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
export function createOpfsObjectRef(path, fields = {}) {
  if (typeof path !== 'string' || !path.length || path.includes('..')) {
    throw new Error('createOpfsObjectRef requires a non-empty relative OPFS path without parent traversal');
  }
  return createObjectRef('opfs', {
    ...fields,
    id: fields.id ?? `opfs:${path}`,
    path,
    backend: fields.backend ?? 'opfs-async',
    ownership: fields.ownership ?? 'origin-private'
  });
}
export function createOpfsSyncObjectRef(path, fields = {}) {
  return createOpfsObjectRef(path, {
    ...fields,
    id: fields.id ?? `opfs-sync:${path}`,
    backend: 'opfs-sync-access-handle',
    ownership: 'origin-private-worker-exclusive'
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
    ...fields,
    id: fields.id ?? `block:sha256:${hash}`,
    digest: `sha256:${hash}`,
    hash,
    algorithm: 'sha256',
    backend: fields.backend ?? 'memory-block-store',
    ownership: fields.ownership ?? 'content-addressed-provider'
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
    ...fields,
    id: fields.id ?? `scheduler:priority-fairness:${id}`,
    schedulerType: 'priority-fairness-drr',
    ownership: 'runtime-scheduler-provider'
  });
}
export function createStorageLaneExecutorObjectRef(id = 'storage-lane-executor', fields = {}) {
  return createObjectRef('inline', {
    ...fields,
    id: fields.id ?? `scheduler:storage-lane:${id}`,
    ownership: 'runtime-scheduler-provider'
  });
}
export class TraceLog {
  #events = [];
  #nextSeq = 1;
  #capacity;
  #droppedCount = 0;
  constructor({ capacity = 4096 } = {}) {
    if (!Number.isInteger(capacity) || capacity < 1) {
      throw new Error('TraceLog capacity must be a positive integer');
    }
    this.#capacity = capacity;
  }
  get capacity() {
    return this.#capacity;
  }
  get droppedCount() {
    return this.#droppedCount;
  }
  emit(kind, detail = {}) {
    if (typeof kind !== 'string' || kind.length === 0) {
      throw new Error('TraceLog kind must be a non-empty string');
    }
    if (!detail || typeof detail !== 'object' || Array.isArray(detail)) {
      throw new Error('TraceLog detail must be an object');
    }
    const event = Object.freeze({ ...detail, seq: this.#nextSeq++, t: Date.now(), kind });
    if (this.#events.length >= this.#capacity) {
      this.#events.shift();
      this.#droppedCount += 1;
    }
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
function normalizeScope(scope, label = 'scope') {
  if (scope == null) return null;
  if (scope instanceof OperationScope) return scope;
  if (typeof scope.signal === 'object' && typeof scope.track === 'function' && typeof scope.closeAsync === 'function') return scope;
  throw createBrowserRtError(`${label} must be an OperationScope-like object`, { code: 'BRT_SCOPE_INVALID' });
}
function scopedAbortSignal({ signal = null, abortSignal = null, scope = null } = {}, label = 'signal') {
  const scoped = normalizeScope(scope, `${label} scope`);
  return assertAbortSignalLike(signal ?? abortSignal ?? scoped?.signal ?? null, label);
}
export class OperationScope {
  #trace;
  #controller = new AbortController();
  #parent = null;
  #children = new Set();
  #resources = [];
  #cleanups = [];
  #signalRemovers = [];
  #timeoutTimer = null;
  #closed = false;
  #operationCount = 0;
  #activeRuns = 0;
  constructor({ label = 'operation-scope', trace = new TraceLog(), parent = null, signal = null, abortSignal = null, timeoutMs = 0, metadata = {} } = {}) {
    this.id = nextId('scope');
    this.label = String(label || 'operation-scope');
    this.createdAt = Date.now();
    this.metadata = Object.freeze({ ...(metadata && typeof metadata === 'object' ? metadata : {}) });
    this.#trace = trace;
    this.#parent = normalizeScope(parent, 'OperationScope parent');
    const normalizedTimeoutMs = normalizeTimeoutMs(timeoutMs, 0, 'OperationScope timeoutMs');
    this.deadlineAt = normalizedTimeoutMs > 0 ? this.createdAt + normalizedTimeoutMs : null;
    if (this.#parent) this.#parent.#adoptChild(this);
    const upstream = scopedAbortSignal({ signal, abortSignal }, 'OperationScope signal');
    this.#linkAbortSignal(upstream, 'signal');
    if (this.#parent?.signal) this.#linkAbortSignal(this.#parent.signal, 'parent');
    if (normalizedTimeoutMs > 0) {
      this.#timeoutTimer = setTimeout(() => this.abort(createBrowserRtError(`OperationScope ${this.label} timed out`, { name: 'AbortError', code: 'BRT_SCOPE_TIMEOUT', detail: { timeoutMs: normalizedTimeoutMs } })), normalizedTimeoutMs);
      this.#timeoutTimer.unref?.();
    }
    this.#trace?.emit('scope:create', { scopeId: this.id, label: this.label, parentId: this.#parent?.id ?? null, timeoutMs: normalizedTimeoutMs, deadlineAt: this.deadlineAt, metadata: this.metadata });
  }
  get signal() { return this.#controller.signal; }
  get closed() { return this.#closed; }
  get aborted() { return this.#controller.signal.aborted; }
  get reason() { return this.#controller.signal.reason ?? null; }
  child(config = {}) {
    if (this.#closed) throw createBrowserRtError(`OperationScope ${this.label} is closed`, { code: 'BRT_SCOPE_CLOSED' });
    return new OperationScope({ ...config, trace: config.trace || this.#trace, parent: this });
  }
  throwIfAborted() {
    if (!this.aborted) return;
    const reason = this.reason;
    if (reason instanceof Error) throw reason;
    throw createAbortError(`OperationScope ${this.label} aborted`, reason);
  }
  track(resource, { kind = 'resource', label = null, owned = true } = {}) {
    if (!owned || !resource || (typeof resource !== 'object' && typeof resource !== 'function')) return resource;
    const closeable = typeof resource.closeAsync === 'function' || typeof resource.close === 'function' || typeof resource.terminate === 'function' || typeof resource.abort === 'function';
    if (!closeable) return resource;
    const row = { resource, kind, label: label ?? resource.label ?? resource.name ?? resource.id ?? kind, addedAt: Date.now() };
    this.#resources.push(row);
    this.#trace?.emit('scope:resource-own', { scopeId: this.id, label: this.label, kind: row.kind, resourceLabel: row.label, count: this.#resources.length });
    return resource;
  }
  onCleanup(callback, { label = 'cleanup' } = {}) {
    if (typeof callback !== 'function') throw createBrowserRtError('OperationScope cleanup callback must be a function', { code: 'BRT_SCOPE_CLEANUP_INVALID' });
    const row = { callback, label: String(label || 'cleanup'), addedAt: Date.now() };
    this.#cleanups.push(row);
    return () => {
      const idx = this.#cleanups.indexOf(row);
      if (idx >= 0) this.#cleanups.splice(idx, 1);
    };
  }
  async run(callback, { label = 'operation' } = {}) {
    if (typeof callback !== 'function') throw createBrowserRtError('OperationScope run callback must be a function', { code: 'BRT_SCOPE_RUN_INVALID' });
    if (this.#closed) throw createBrowserRtError(`OperationScope ${this.label} is closed`, { code: 'BRT_SCOPE_CLOSED' });
    this.throwIfAborted();
    const runId = `${this.id}:run:${++this.#operationCount}`;
    this.#activeRuns += 1;
    this.#trace?.emit('scope:run-start', { scopeId: this.id, runId, label });
    try {
      const value = await callback(this);
      this.#trace?.emit('scope:run-complete', { scopeId: this.id, runId, label });
      return value;
    } catch (error) {
      this.#trace?.emit('scope:run-error', { scopeId: this.id, runId, label, error: describeError(error) });
      throw error;
    } finally {
      this.#activeRuns -= 1;
    }
  }
  abort(reason = 'scope-abort') {
    if (!this.#controller.signal.aborted) {
      const abortReason = reason instanceof Error ? reason : createAbortError(`OperationScope ${this.label} aborted: ${String(reason)}`, reason);
      this.#controller.abort(abortReason);
      this.#trace?.emit('scope:abort', { scopeId: this.id, label: this.label, reason: describeError(abortReason), childCount: this.#children.size, resourceCount: this.#resources.length });
    }
    for (const child of Array.from(this.#children)) child.abort(this.reason || reason);
    return this.snapshot();
  }
  close(reason = 'scope-close') {
    void this.closeAsync({ reason });
    return this.snapshot();
  }
  async closeAsync({ reason = 'scope-close' } = {}) {
    if (this.#closed) return Object.freeze({ disposition: 'already-closed', scopeId: this.id, label: this.label, snapshot: this.snapshot(), children: Object.freeze([]), resources: Object.freeze([]), cleanups: Object.freeze([]) });
    this.#closed = true;
    this.abort(reason);
    if (this.#timeoutTimer) clearTimeout(this.#timeoutTimer);
    for (const remove of this.#signalRemovers.splice(0)) remove();
    const childResults = [];
    for (const child of Array.from(this.#children).reverse()) {
      try {
        childResults.push(await child.closeAsync({ reason }));
      } catch (error) {
        childResults.push(Object.freeze({ disposition: 'failed', scopeId: child.id, label: child.label, error: describeError(error) }));
      }
    }
    const resourceResults = [];
    for (const row of this.#resources.splice(0).reverse()) {
      resourceResults.push(await this.#closeResource(row, reason));
    }
    const cleanupResults = [];
    for (const row of this.#cleanups.splice(0).reverse()) {
      try {
        const value = row.callback({ scope: this, reason });
        cleanupResults.push(Object.freeze({ label: row.label, status: 'completed', result: value && typeof value.then === 'function' ? await value : value ?? null }));
      } catch (error) {
        cleanupResults.push(Object.freeze({ label: row.label, status: 'failed', error: describeError(error) }));
      }
    }
    if (this.#parent) this.#parent.#children.delete(this);
    const failedCount = resourceResults.filter((row) => row.status !== 'closed').length + cleanupResults.filter((row) => row.status === 'failed').length + childResults.filter((row) => row.disposition === 'failed').length;
    const report = Object.freeze({
      disposition: 'closed',
      scopeId: this.id,
      label: this.label,
      aborted: this.aborted,
      reason: describeError(this.reason),
      childCount: childResults.length,
      resourceCount: resourceResults.length,
      cleanupCount: cleanupResults.length,
      failedCount,
      children: Object.freeze(childResults),
      resources: Object.freeze(resourceResults),
      cleanups: Object.freeze(cleanupResults)
    });
    this.#trace?.emit('scope:close', { scopeId: this.id, label: this.label, childCount: report.childCount, resourceCount: report.resourceCount, cleanupCount: report.cleanupCount, failedCount });
    return report;
  }
  snapshot() {
    return Object.freeze({
      id: this.id,
      label: this.label,
      closed: this.#closed,
      aborted: this.aborted,
      reason: this.aborted ? describeError(this.reason) : null,
      createdAt: this.createdAt,
      deadlineAt: this.deadlineAt,
      activeRuns: this.#activeRuns,
      childCount: this.#children.size,
      resourceCount: this.#resources.length,
      cleanupCount: this.#cleanups.length,
      metadata: this.metadata
    });
  }
  #adoptChild(child) {
    this.#children.add(child);
    this.#trace?.emit('scope:child-own', { scopeId: this.id, label: this.label, childId: child.id, childLabel: child.label, childCount: this.#children.size });
  }
  #linkAbortSignal(signal, source) {
    if (!signal) return;
    if (signal.aborted) {
      this.abort(signalReason(signal) || source);
      return;
    }
    const onAbort = () => this.abort(signalReason(signal) || source);
    signal.addEventListener('abort', onAbort, { once: true });
    this.#signalRemovers.push(() => signal.removeEventListener('abort', onAbort));
  }
  async #closeResource(row, reason) {
    try {
      let result = null;
      if (typeof row.resource.closeAsync === 'function') result = row.resource.closeAsync({ reason });
      else if (typeof row.resource.close === 'function') result = row.resource.close(reason);
      else if (typeof row.resource.terminate === 'function') result = row.resource.terminate(reason);
      else if (typeof row.resource.abort === 'function') result = row.resource.abort(reason);
      if (result && typeof result.then === 'function') result = await result;
      this.#trace?.emit('scope:resource-close', { scopeId: this.id, label: this.label, kind: row.kind, resourceLabel: row.label, status: 'closed' });
      return Object.freeze({ kind: row.kind, label: row.label, status: 'closed', result: result ?? null });
    } catch (error) {
      this.#trace?.emit('scope:resource-close', { scopeId: this.id, label: this.label, kind: row.kind, resourceLabel: row.label, status: 'failed', error: describeError(error) });
      return Object.freeze({ kind: row.kind, label: row.label, status: 'failed', error: describeError(error) });
    }
  }
}
export class BoundedChannel {
  #closed = false;
  #closeReason = null;
  constructor({ capacity = 1, overflow = 'wait', label = 'channel', trace = null, maxWaitingSenders = null, maxWaitingReceivers = null } = {}) {
    if (!Number.isInteger(capacity) || capacity < 1) throw new Error('BoundedChannel capacity must be a positive integer');
    if (!CHANNEL_OVERFLOWS.has(overflow)) throw new Error(`Unsupported overflow policy: ${overflow}`);
    this.capacity = capacity;
    this.overflow = overflow;
    this.label = label;
    this.queue = [];
    this.waitingReceivers = [];
    this.waitingSenders = [];
    this.maxWaitingSenders = normalizePositiveInteger(maxWaitingSenders, capacity, 'BoundedChannel maxWaitingSenders');
    this.maxWaitingReceivers = normalizePositiveInteger(maxWaitingReceivers, capacity, 'BoundedChannel maxWaitingReceivers');
    this.trace = trace;
    this.trace?.emit('channel:create', { label: this.label, capacity: this.capacity, overflow: this.overflow, maxWaitingSenders: this.maxWaitingSenders, maxWaitingReceivers: this.maxWaitingReceivers });
  }
  get closed() { return this.#closed; }
  async send(value, options = {}) {
    if (this.#closed) throw createBrowserRtError(`BoundedChannel ${this.label} is closed`, { code: 'BRT_CHANNEL_CLOSED', detail: this.#closeReason });
    while (this.waitingReceivers.length) {
      const receiver = this.waitingReceivers.shift();
      if (receiver.settled) continue;
      receiver.settle({ ok: true, value });
      this.trace?.emit('channel:send', { label: this.label, disposition: 'delivered', size: this.size(), waitingReceivers: this.waitingReceivers.length, waitingSenders: this.waitingSenders.length });
      return { disposition: 'delivered' };
    }
    if (this.queue.length < this.capacity) {
      this.queue.push(value);
      this.trace?.emit('channel:send', { label: this.label, disposition: 'queued', size: this.size(), waitingReceivers: this.waitingReceivers.length, waitingSenders: this.waitingSenders.length });
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
    if (this.waitingSenders.length >= this.maxWaitingSenders) {
      this.trace?.emit('channel:send', { label: this.label, disposition: 'failed-waiter-limit', size: this.size(), waitingSenders: this.waitingSenders.length, maxWaitingSenders: this.maxWaitingSenders });
      throw createBrowserRtError(`BoundedChannel ${this.label} waiting sender limit reached`, { code: 'BRT_CHANNEL_WAITERS_FULL', detail: { maxWaitingSenders: this.maxWaitingSenders } });
    }
    this.trace?.emit('channel:send', { label: this.label, disposition: 'waiting', size: this.size(), waitingSenders: this.waitingSenders.length + 1 });
    return await this.#waitSender(value, options);
  }
  async receive(options = {}) {
    if (this.queue.length) {
      const value = this.queue.shift();
      this.#promoteWaitingSenders();
      this.trace?.emit('channel:receive', { label: this.label, size: this.size(), waitingReceivers: this.waitingReceivers.length, waitingSenders: this.waitingSenders.length });
      return value;
    }
    if (this.#closed) throw createBrowserRtError(`BoundedChannel ${this.label} is closed`, { code: 'BRT_CHANNEL_CLOSED', detail: this.#closeReason });
    if (this.waitingReceivers.length >= this.maxWaitingReceivers) {
      this.trace?.emit('channel:receive-wait', { label: this.label, disposition: 'failed-waiter-limit', size: this.size(), waitingReceivers: this.waitingReceivers.length, maxWaitingReceivers: this.maxWaitingReceivers });
      throw createBrowserRtError(`BoundedChannel ${this.label} waiting receiver limit reached`, { code: 'BRT_CHANNEL_WAITERS_FULL', detail: { maxWaitingReceivers: this.maxWaitingReceivers } });
    }
    this.trace?.emit('channel:receive-wait', { label: this.label, size: this.size(), waitingReceivers: this.waitingReceivers.length + 1 });
    return await this.#waitReceiver(options);
  }
  close(reason = 'channel-close') {
    if (this.#closed) return Object.freeze({ disposition: 'already-closed', queued: this.queue.length, waitingSenders: this.waitingSenders.length, waitingReceivers: this.waitingReceivers.length });
    this.#closed = true;
    this.#closeReason = reason;
    const queued = this.queue.length;
    const senderCount = this.waitingSenders.length;
    const receiverCount = this.waitingReceivers.length;
    const error = createBrowserRtError(`BoundedChannel ${this.label} closed: ${reason}`, { code: 'BRT_CHANNEL_CLOSED', detail: reason });
    for (const sender of this.waitingSenders.splice(0)) sender.settle({ ok: false, error });
    for (const receiver of this.waitingReceivers.splice(0)) receiver.settle({ ok: false, error });
    this.queue.length = 0;
    this.trace?.emit('channel:close', { label: this.label, reason, queued, waitingSenders: senderCount, waitingReceivers: receiverCount });
    return Object.freeze({ disposition: 'closed', queued, waitingSenders: senderCount, waitingReceivers: receiverCount });
  }
  size() {
    return this.queue.length;
  }
  snapshot() {
    return Object.freeze({
      label: this.label,
      capacity: this.capacity,
      overflow: this.overflow,
      closed: this.#closed,
      size: this.queue.length,
      waitingSenders: this.waitingSenders.length,
      waitingReceivers: this.waitingReceivers.length,
      maxWaitingSenders: this.maxWaitingSenders,
      maxWaitingReceivers: this.maxWaitingReceivers
    });
  }
  #waitSender(value, { signal = null, abortSignal = null, scope = null, timeoutMs = 0 } = {}) {
    const chosenSignal = scopedAbortSignal({ signal, abortSignal, scope }, 'BoundedChannel send signal');
    const normalizedTimeoutMs = normalizeTimeoutMs(timeoutMs, 0);
    if (chosenSignal?.aborted) throw createAbortError(`BoundedChannel ${this.label} send aborted before wait`, signalReason(chosenSignal));
    return new Promise((resolve, reject) => {
      let timer = null;
      let onAbort = null;
      const waiter = {
        value,
        settled: false,
        settle: ({ ok, value: settledValue, error }) => {
          if (waiter.settled) return;
          waiter.settled = true;
          if (timer) clearTimeout(timer);
          if (chosenSignal && onAbort) chosenSignal.removeEventListener('abort', onAbort);
          const idx = this.waitingSenders.indexOf(waiter);
          if (idx >= 0) this.waitingSenders.splice(idx, 1);
          if (ok) resolve(settledValue);
          else reject(error);
        }
      };
      if (chosenSignal) {
        onAbort = () => {
          const error = createAbortError(`BoundedChannel ${this.label} send aborted while waiting`, signalReason(chosenSignal));
          this.trace?.emit('channel:send-abort', { label: this.label, size: this.size(), waitingSenders: this.waitingSenders.length });
          waiter.settle({ ok: false, error });
        };
        chosenSignal.addEventListener('abort', onAbort, { once: true });
      }
      if (normalizedTimeoutMs > 0) {
        timer = setTimeout(() => {
          const error = createBrowserRtError(`BoundedChannel ${this.label} send timed out`, { code: 'BRT_CHANNEL_TIMEOUT', detail: { timeoutMs: normalizedTimeoutMs } });
          this.trace?.emit('channel:send-timeout', { label: this.label, timeoutMs: normalizedTimeoutMs, size: this.size(), waitingSenders: this.waitingSenders.length });
          waiter.settle({ ok: false, error });
        }, normalizedTimeoutMs);
      }
      this.waitingSenders.push(waiter);
    });
  }
  #waitReceiver({ signal = null, abortSignal = null, scope = null, timeoutMs = 0 } = {}) {
    const chosenSignal = scopedAbortSignal({ signal, abortSignal, scope }, 'BoundedChannel receive signal');
    const normalizedTimeoutMs = normalizeTimeoutMs(timeoutMs, 0);
    if (chosenSignal?.aborted) throw createAbortError(`BoundedChannel ${this.label} receive aborted before wait`, signalReason(chosenSignal));
    return new Promise((resolve, reject) => {
      let timer = null;
      let onAbort = null;
      const waiter = {
        settled: false,
        settle: ({ ok, value, error }) => {
          if (waiter.settled) return;
          waiter.settled = true;
          if (timer) clearTimeout(timer);
          if (chosenSignal && onAbort) chosenSignal.removeEventListener('abort', onAbort);
          const idx = this.waitingReceivers.indexOf(waiter);
          if (idx >= 0) this.waitingReceivers.splice(idx, 1);
          if (ok) resolve(value);
          else reject(error);
        }
      };
      if (chosenSignal) {
        onAbort = () => {
          const error = createAbortError(`BoundedChannel ${this.label} receive aborted while waiting`, signalReason(chosenSignal));
          this.trace?.emit('channel:receive-abort', { label: this.label, size: this.size(), waitingReceivers: this.waitingReceivers.length });
          waiter.settle({ ok: false, error });
        };
        chosenSignal.addEventListener('abort', onAbort, { once: true });
      }
      if (normalizedTimeoutMs > 0) {
        timer = setTimeout(() => {
          const error = createBrowserRtError(`BoundedChannel ${this.label} receive timed out`, { code: 'BRT_CHANNEL_TIMEOUT', detail: { timeoutMs: normalizedTimeoutMs } });
          this.trace?.emit('channel:receive-timeout', { label: this.label, timeoutMs: normalizedTimeoutMs, size: this.size(), waitingReceivers: this.waitingReceivers.length });
          waiter.settle({ ok: false, error });
        }, normalizedTimeoutMs);
      }
      this.waitingReceivers.push(waiter);
    });
  }
  #promoteWaitingSenders() {
    while (!this.#closed && this.queue.length < this.capacity && this.waitingSenders.length) {
      const sender = this.waitingSenders.shift();
      if (!sender || sender.settled) continue;
      this.queue.push(sender.value);
      sender.settle({ ok: true, value: { disposition: 'queued-after-wait' } });
    }
  }
}
export class WorkerAgent {
  #worker;
  #trace;
  #pending = new Map();
  #cancelledCalls = new Map();
  #cancelledCallOrder = [];
  #readyResolve;
  #readyReject;
  #readyTimer = null;
  #readySettled = false;
  #exitCallbacks = new Set();
  #closed = false;
  #failed = false;
  #exitNotified = false;
  #lateSettlementRetention;
  constructor({ worker, name = 'agent', trace = new TraceLog(), readyTimeoutMs = 30000, lateSettlementRetention = 1024 } = {}) {
    this.name = name;
    this.id = nextId('agent');
    this.#worker = worker;
    this.#trace = trace;
    this.#lateSettlementRetention = normalizePositiveInteger(lateSettlementRetention, 1024, 'WorkerAgent lateSettlementRetention');
    const normalizedReadyTimeoutMs = normalizeTimeoutMs(readyTimeoutMs, 30000, 'WorkerAgent readyTimeoutMs');
    this.ready = new Promise((resolve, reject) => {
      this.#readyResolve = resolve;
      this.#readyReject = reject;
    });
    if (normalizedReadyTimeoutMs > 0) {
      this.#readyTimer = setTimeout(() => this.#handleReadyTimeout(normalizedReadyTimeoutMs), normalizedReadyTimeoutMs);
    }
    this.#wireWorker(worker);
    this.#trace.emit('agent:spawn', { agentId: this.id, name: this.name, readyTimeoutMs: normalizedReadyTimeoutMs });
  }
  get closed() { return this.#closed; }
  get failed() { return this.#failed; }
  get trace() { return this.#trace; }
  onExit(callback) {
    this.#exitCallbacks.add(callback);
    return () => this.#exitCallbacks.delete(callback);
  }
  async call(op, payload = {}, { transfer = [], timeoutMs = 0, lane = 'cpu', priority = 'user-visible', signal = null, abortSignal = null, scope = null, cancelOnTimeout = true, terminateOnCancel = false, cancelGraceMs = 0 } = {}) {
    const chosenSignal = scopedAbortSignal({ signal, abortSignal, scope }, 'WorkerAgent call signal');
    if (this.#closed) throw new Error(`WorkerAgent ${this.name} is closed`);
    await this.#awaitReady(chosenSignal);
    if (this.#closed) throw new Error(`WorkerAgent ${this.name} is closed`);
    if (chosenSignal?.aborted) throw createAbortError(`WorkerAgent call aborted before post: ${op}`, signalReason(chosenSignal));
    const normalizedTimeoutMs = normalizeTimeoutMs(timeoutMs, 0);
    const normalizedCancelGraceMs = normalizeTimeoutMs(cancelGraceMs, 0, 'WorkerAgent cancelGraceMs');
    const terminateCancelledCall = terminateOnCancel === true;
    const id = nextId('call');
    const envelope = createEnvelope(op, { lane, priority, payloadRef: payload?.objectRef || payload?.ref || null });
    const message = { type: 'agent:call', id, envelope, op, payload };
    this.#trace.emit('agent:call', { agentId: this.id, callId: id, op, transferCount: transfer.length, lane, priority, timeoutMs: normalizedTimeoutMs, cancellationLinked: Boolean(chosenSignal) || (normalizedTimeoutMs > 0 && cancelOnTimeout !== false), terminateOnCancel: terminateCancelledCall, cancelGraceMs: normalizedCancelGraceMs });
    return await new Promise((resolve, reject) => {
      let timer = null;
      let onAbort = null;
      const rejectWithCancel = (error, reason, detail = {}) => {
        const pending = this.#pending.get(id);
        if (!pending) return;
        this.#pending.delete(id);
        if (pending.timer) clearTimeout(pending.timer);
        if (pending.signal && pending.onAbort) pending.signal.removeEventListener('abort', pending.onAbort);
        this.#rememberCancelledCall(id, { op, reason, detail, cancelledAt: Date.now(), terminateOnCancel: terminateCancelledCall, cancelGraceMs: normalizedCancelGraceMs });
        this.#sendCancel(id, reason, { op, ...detail });
        this.#scheduleCancelEscalation(id, reason, { op, terminateOnCancel: terminateCancelledCall, cancelGraceMs: normalizedCancelGraceMs });
        reject(error);
      };
      if (chosenSignal) {
        onAbort = () => {
          const err = createAbortError(`WorkerAgent call aborted: ${op}`, signalReason(chosenSignal));
          this.#trace.emit('agent:call-abort', { agentId: this.id, callId: id, op, reason: 'signal' });
          rejectWithCancel(err, 'signal', { signalReason: String(signalReason(chosenSignal) || '') });
        };
        chosenSignal.addEventListener('abort', onAbort, { once: true });
      }
      if (normalizedTimeoutMs > 0) {
        timer = setTimeout(() => {
          const err = createBrowserRtError(`WorkerAgent call timed out: ${op}`, { code: 'BRT_AGENT_CALL_TIMEOUT', detail: { timeoutMs: normalizedTimeoutMs } });
          this.#trace.emit('agent:call-timeout', { agentId: this.id, callId: id, op, timeoutMs: normalizedTimeoutMs, cancelSent: cancelOnTimeout !== false });
          if (cancelOnTimeout === false) {
            const pending = this.#pending.get(id);
            if (!pending) return;
            this.#pending.delete(id);
            if (pending.signal && pending.onAbort) pending.signal.removeEventListener('abort', pending.onAbort);
            this.#rememberCancelledCall(id, { op, reason: 'timeout-no-cancel', detail: { timeoutMs: normalizedTimeoutMs }, cancelledAt: Date.now(), terminateOnCancel: false, cancelGraceMs: 0 });
            reject(err);
            return;
          }
          rejectWithCancel(err, 'timeout', { timeoutMs: normalizedTimeoutMs });
        }, normalizedTimeoutMs);
        timer.unref?.();
      }
      this.#pending.set(id, { resolve, reject, timer, op, signal: chosenSignal, onAbort });
      try {
        if (transfer.length) this.#worker.postMessage(message, transfer);
        else this.#worker.postMessage(message);
      } catch (error) {
        const pending = this.#pending.get(id);
        this.#pending.delete(id);
        if (pending?.timer) clearTimeout(pending.timer);
        if (pending?.signal && pending?.onAbort) pending.signal.removeEventListener('abort', pending.onAbort);
        this.#trace.emit('agent:post-error', { agentId: this.id, callId: id, op, error: describeError(error) });
        reject(error);
      }
    });
  }
  async terminate(reason = 'caller-terminate') {
    if (this.#closed) return { disposition: 'already-closed' };
    this.#trace.emit('agent:terminate', { agentId: this.id, name: this.name, reason });
    this.#closed = true;
    this.#failed = true;
    if (this.#readyTimer) clearTimeout(this.#readyTimer);
    const err = new Error(`WorkerAgent terminated: ${reason}`);
    this.#settleReady({ ok: false, error: err });
    this.#clearCancelledCallTimers();
    this.#rejectPending(err);
    const result = this.#worker.terminate?.();
    if (result && typeof result.then === 'function') await result;
    this.#notifyExit({ code: null, error: err });
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
      this.#settleReady({ ok: true, value: this });
      return;
    }
    if (message.type === 'agent:trace') {
      this.#trace.emit(message.kind || 'agent:trace', { agentId: this.id, ...(message.detail || {}) });
      return;
    }
    if (message.type === 'agent:cancelled') {
      const cancelled = this.#cancelledCalls.get(message.id);
      if (cancelled) cancelled.acknowledgedAt = Date.now();
      this.#trace.emit('agent:cancel-ack', { agentId: this.id, callId: message.id, reason: message.reason || null });
      return;
    }
    if (message.type === 'agent:result' || message.type === 'agent:error') {
      const pending = this.#pending.get(message.id);
      if (!pending) {
        const cancelled = this.#cancelledCalls.get(message.id);
        if (cancelled) {
          if (cancelled.cancelEscalationTimer) clearTimeout(cancelled.cancelEscalationTimer);
          this.#cancelledCalls.delete(message.id);
          this.#trace.emit(message.type === 'agent:result' ? 'agent:late-result-after-cancel' : 'agent:late-error-after-cancel', { agentId: this.id, callId: message.id, op: cancelled.op, reason: cancelled.reason });
        }
        return;
      }
      this.#pending.delete(message.id);
      if (pending.timer) clearTimeout(pending.timer);
      if (pending.signal && pending.onAbort) pending.signal.removeEventListener('abort', pending.onAbort);
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
    if (this.#readyTimer) clearTimeout(this.#readyTimer);
    this.#trace.emit('agent:error', { agentId: this.id, name: this.name, error: describeError(err) });
    this.#settleReady({ ok: false, error: err });
    this.#clearCancelledCallTimers();
    this.#rejectPending(err);
    this.#notifyExit({ code: null, error: err });
  }
  #handleExit({ code = null } = {}) {
    const err = new Error(`WorkerAgent ${this.name} exited with code ${code}`);
    this.#closed = true;
    if (code !== 0) this.#failed = true;
    if (this.#readyTimer) clearTimeout(this.#readyTimer);
    this.#trace.emit('agent:exit', { agentId: this.id, name: this.name, code });
    this.#settleReady({ ok: false, error: err });
    this.#clearCancelledCallTimers();
    this.#rejectPending(err);
    this.#notifyExit({ code, error: err });
  }
  #handleReadyTimeout(timeoutMs) {
    if (this.#readySettled || this.#closed) return;
    const err = createBrowserRtError(`WorkerAgent ${this.name} ready timed out`, { code: 'BRT_AGENT_READY_TIMEOUT', detail: { timeoutMs } });
    this.#failed = true;
    this.#closed = true;
    this.#trace.emit('agent:ready-timeout', { agentId: this.id, name: this.name, timeoutMs });
    this.#settleReady({ ok: false, error: err });
    this.#clearCancelledCallTimers();
    this.#rejectPending(err);
    try { this.#worker.terminate?.(); } catch {}
    this.#notifyExit({ code: null, error: err });
  }
  #settleReady({ ok, value, error }) {
    if (this.#readySettled) return;
    this.#readySettled = true;
    if (this.#readyTimer) clearTimeout(this.#readyTimer);
    if (ok) this.#readyResolve?.(value);
    else this.#readyReject?.(error);
  }
  #awaitReady(signal) {
    if (!signal) return this.ready;
    if (signal.aborted) throw createAbortError(`WorkerAgent ${this.name} call aborted before ready`, signalReason(signal));
    return new Promise((resolve, reject) => {
      const onAbort = () => reject(createAbortError(`WorkerAgent ${this.name} call aborted before ready`, signalReason(signal)));
      signal.addEventListener('abort', onAbort, { once: true });
      this.ready.then((value) => {
        signal.removeEventListener('abort', onAbort);
        resolve(value);
      }, (error) => {
        signal.removeEventListener('abort', onAbort);
        reject(error);
      });
    });
  }
  #sendCancel(id, reason, detail = {}) {
    try {
      this.#worker.postMessage({ type: 'agent:cancel', id, reason, detail });
      this.#trace.emit('agent:cancel-sent', { agentId: this.id, callId: id, reason });
      return true;
    } catch (error) {
      this.#trace.emit('agent:cancel-error', { agentId: this.id, callId: id, reason, error: describeError(error) });
      return false;
    }
  }
  #clearCancelledCallTimers() {
    for (const detail of this.#cancelledCalls.values()) {
      if (detail.cancelEscalationTimer) clearTimeout(detail.cancelEscalationTimer);
      detail.cancelEscalationTimer = null;
    }
  }
  #scheduleCancelEscalation(id, reason, { op, terminateOnCancel = false, cancelGraceMs = 0 } = {}) {
    if (terminateOnCancel !== true) return;
    const cancelled = this.#cancelledCalls.get(id);
    if (!cancelled) return;
    const delayMs = Math.max(0, cancelGraceMs);
    const timer = setTimeout(() => {
      const stillCancelled = this.#cancelledCalls.get(id);
      if (!stillCancelled || this.#closed) return;
      this.#trace.emit('agent:cancel-escalate-terminate', { agentId: this.id, callId: id, op, reason, cancelGraceMs: delayMs });
      void this.terminate(`cancel-escalation:${reason}:${op}`).catch((error) => {
        this.#trace.emit('agent:cancel-escalate-error', { agentId: this.id, callId: id, op, reason, error: describeError(error) });
      });
    }, delayMs);
    timer.unref?.();
    cancelled.cancelEscalationTimer = timer;
  }
  #rememberCancelledCall(id, detail) {
    this.#cancelledCalls.set(id, detail);
    this.#cancelledCallOrder.push(id);
    while (this.#cancelledCallOrder.length > this.#lateSettlementRetention) {
      const oldest = this.#cancelledCallOrder.shift();
      if (oldest) this.#cancelledCalls.delete(oldest);
    }
  }
  #notifyExit({ code, error }) {
    if (this.#exitNotified) return;
    this.#exitNotified = true;
    for (const callback of this.#exitCallbacks) callback({ agent: this, code, error });
  }
  #rejectPending(error) {
    for (const [id, pending] of this.#pending) {
      if (pending.timer) clearTimeout(pending.timer);
      if (pending.signal && pending.onAbort) pending.signal.removeEventListener('abort', pending.onAbort);
      pending.reject(error);
      this.#trace.emit('agent:pending-reject', { agentId: this.id, callId: id, op: pending.op, error: describeError(error) });
    }
    this.#pending.clear();
  }
}
export async function spawnWorkerAgent({ workerURL = null, name = 'browserrt-agent', trace = new TraceLog(), workerOptions = {}, readyTimeoutMs = 30000 } = {}) {
  let worker;
  if (typeof globalThis.Worker === 'function' && environmentName() === 'browser-window') {
    const url = workerURL || new URL('./browser-agent-worker.mjs', import.meta.url);
    worker = new globalThis.Worker(url, { type: 'module', name, ...workerOptions });
  } else {
    const { Worker } = await import('node:worker_threads');
    const url = workerURL || new URL('./node-agent-worker.mjs', import.meta.url);
    worker = new Worker(url, { name, ...workerOptions });
  }
  const agent = new WorkerAgent({ worker, name, trace, readyTimeoutMs });
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
      operationScope: true,
      transferableObjectRef: true,
      workerAgent: true,
      supervisorRestart: true,
      kernelKitDemoProof: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof),
      browserKernelKitDemoProof: Boolean(options.browserKernelKitDemoProof),
      storageLane: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof || options.opfsRawCompositeAbortSignalProof || options.opfsWebLockGuardedAbortSignalProof || options.blockStoreLaneProviderOptionsProof || options.storageLaneProviderTimeoutAbortProof || options.storageLaneCompositeAbortSignalProof || options.opfsStorageLaneAdapterProof || options.opfsAsyncBlockStoreProof || options.opfsAsyncProbe || options.opfsSyncWorkerProbe || options.browserOpfsSyncWorkerProbe || options.blockStoreProbe || options.journalRecoveryProbe || options.journaledBlockStoreProbe || options.spillMailboxProbe || options.persistedSpillRecoveryProbe || options.persistedSpillCompactionProbe || options.storageLaneRetryPolicyProof || options.storageLaneRetryBudgetProof || options.storageLaneRetryBudgetModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof),
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
      opfsWriteBudgetGuardProof: Boolean(options.opfsWriteBudgetGuardProof),
      opfsWriteBudgetDuplicateBypassProof: Boolean(options.opfsWriteBudgetDuplicateBypassProof),
      opfsRollbackValidBlockPreserveProof: Boolean(options.opfsRollbackValidBlockPreserveProof),
      opfsReadOnlyNoCreateProof: Boolean(options.opfsReadOnlyNoCreateProof),
      opfsWebLockGuardedAbortSignalProof: Boolean(options.opfsWebLockGuardedAbortSignalProof),
      opfsRawCompositeAbortSignalProof: Boolean(options.opfsRawCompositeAbortSignalProof),
      blockStoreLaneProviderOptionsProof: Boolean(options.blockStoreLaneProviderOptionsProof),
      storageLaneProviderTimeoutAbortProof: Boolean(options.storageLaneProviderTimeoutAbortProof),
      storageLaneCompositeAbortSignalProof: Boolean(options.storageLaneCompositeAbortSignalProof),
      opfsOwnedRollbackGuardProof: Boolean(options.opfsOwnedRollbackGuardProof),
      opfsOpenFailureRecoveryProof: Boolean(options.opfsOpenFailureRecoveryProof),
      opfsStorageLaneAdapterProof: Boolean(options.opfsStorageLaneAdapterProof || options.browserKernelKitDemoProof),
      browserOpfsSyncWorkerProbe: Boolean(options.browserOpfsSyncWorkerProbe),
      adaptiveConcurrencyController: Boolean(options.adaptiveConcurrencyProbe || options.adaptiveConcurrencyControllerProbe),
      priorityFairScheduler: Boolean(options.priorityFairnessProbe || options.priorityFairnessSchedulerProbe),
      crossLaneScheduler: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof || options.opfsRawCompositeAbortSignalProof || options.opfsWebLockGuardedAbortSignalProof || options.blockStoreLaneProviderOptionsProof || options.storageLaneProviderTimeoutAbortProof || options.storageLaneCompositeAbortSignalProof || options.opfsStorageLaneAdapterProof || options.crossLaneSchedulerProbe || options.crossLaneSchedulerModelProbe || options.crossLaneModelWalkProbe || options.storageLaneSchedulerProbe || options.storageLaneProviderProof || options.storageLaneRetryPolicyProof || options.storageLaneRetryBudgetProof || options.storageLaneRetryBudgetModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof || options.storageLaneModelWalkProof || options.crossLaneScheduler),
      storageLaneExecutor: Boolean(options.kernelKitDemoProof || options.browserKernelKitDemoProof || options.opfsRawCompositeAbortSignalProof || options.opfsWebLockGuardedAbortSignalProof || options.blockStoreLaneProviderOptionsProof || options.storageLaneProviderTimeoutAbortProof || options.storageLaneCompositeAbortSignalProof || options.opfsStorageLaneAdapterProof || options.storageLaneSchedulerProbe || options.storageLaneProviderProof || options.storageLaneRetryPolicyProof || options.storageLaneRetryBudgetProof || options.storageLaneRetryBudgetModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof || options.storageLaneModelWalkProof || options.storageLaneExecutor),
      circuitBreakerBulkhead: Boolean(options.circuitBreakerBulkheadProof || options.resilienceCircuitBreakerBulkheadProof || options.circuitBreakerBulkheadModelProof || options.providerResilienceHistoryProof || options.providerResilienceModelProof || options.storageLaneAdmissionHistoryProof || options.storageLaneAdmissionHistoryModelProof || options.storageLaneOverloadGovernanceModelProof || options.circuitBreakerBulkhead),
      circuitBreakerBulkheadModelProof: Boolean(options.circuitBreakerBulkheadModelProof),
      testFacility: true
    })
  });
}
function attachRuntimeNamespaces(runtime) {
  const namespace = (names) => Object.freeze(Object.fromEntries(names.map((name) => {
    if (typeof runtime[name] !== 'function') throw new Error(`BrowserRT namespace target is not a runtime method: ${name}`);
    return [name, (...args) => runtime[name](...args)];
  })));
  runtime.core = namespace([
    'scope',
    'channel',
    'objectRef',
    'transferObject',
    'blockObjectRef',
    'spawnAgent',
    'supervisor'
  ]);
  runtime.storage = namespace([
    'blockStore',
    'journaledBlockStore',
    'recoverJournaledBlockStore',
    'blockStoreLaneAdapter',
    'opfsObjectRef',
    'opfsSyncObjectRef',
    'opfsAsyncWriteReadProbe',
    'opfsAsyncBlockStore',
    'opfsAsyncBlockStoreWithPosture',
    'opfsBlockStoreStorageLaneAdapter',
    'opfsWebLockGuardedBlockStore',
    'opfsWebLockGuardedBlockStoreWithPosture',
    'opfsWebLockGuardedStorageLaneAdapterWithPosture',
    'browserStoragePosture',
    'browserStorageRecoveryGuidance',
    'kernelKitStoragePosture',
    'kernelKitOpfsAbortBoundary'
  ]);
  runtime.coordination = namespace([
    'admissionController',
    'adaptiveConcurrencyController',
    'priorityFairScheduler',
    'crossLaneScheduler',
    'storageLaneExecutor',
    'retryBudgetAdmissionController',
    'storageLaneRetryController',
    'circuitBreakerBulkheadController',
    'providerResilienceHistoryRunner',
    'storageLaneAdmissionHistoryRunner',
    'webLockCoordinator',
    'kernelKitWebLockPosture'
  ]);
  runtime.diagnostics = namespace([
    'kernelKitLifecycleCheckpoint',
    'kernelKitSessionCoordinationCheckpoint',
    'kernelKitRecoveryCheckpoint',
    'kernelKitAdmissionCancellationCheckpoint',
    'kernelKitDemoTraceSummary',
    'kernelKitTraceExport',
    'validateKernelKitTraceExport',
    'kernelKitSupportBundle',
    'validateKernelKitSupportBundle',
    'kernelKitSupportBundlePrivacyScrub',
    'validateKernelKitSupportBundlePrivacyScrub',
    'kernelKitSupportBundleReplayPlan',
    'validateKernelKitSupportBundleReplayPlan',
    'kernelKitSupportBundleOperatorPreflightDisplaySnapshot',
    'validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot',
    'kernelKitSupportBundleOperatorReplayGate',
    'validateKernelKitSupportBundleOperatorReplayGate',
    'kernelKitSupportBundleEvidenceLedger',
    'validateKernelKitSupportBundleEvidenceLedger',
    'kernelKitSupportBundleEvidenceCheckpoint',
    'validateKernelKitSupportBundleEvidenceCheckpoint',
    'kernelKitDiagnosticRunbook',
    'validateKernelKitDiagnosticRunbook',
    'kernelKitReadinessGate',
    'validateKernelKitReadinessGate'
  ]);
  runtime.experimental = namespace([
    'sharedInt32Ring',
    'openSharedInt32Ring',
    'sharedFrameRing',
    'openSharedFrameRing',
    'spillFrameMailbox',
    'persistedSpillMailbox',
    'recoverPersistedSpillMailbox',
    'providerResilienceModelOracle',
    'storageLaneAdmissionHistoryModelOracle',
    'storageLaneOverloadGovernanceModelOracle',
    'dreamBoundaryMap',
    'validateDreamBoundaryMap',
    'projectContinuationAssessment',
    'validateProjectContinuationAssessment'
  ]);
  return runtime;
}
class RuntimeResourceOwner {
  #trace;
  #records = [];
  #closed = false;
  constructor({ trace = null } = {}) {
    this.#trace = trace;
  }
  get size() {
    return this.#records.length;
  }
  track(resource, { kind = 'resource', label = null, owned = true } = {}) {
    if (!owned || !resource || typeof resource !== 'object') return resource;
    const closeable = typeof resource.closeAsync === 'function' || typeof resource.close === 'function' || typeof resource.terminate === 'function';
    if (!closeable) return resource;
    const row = Object.freeze({ resource, kind, label: label ?? resource.label ?? resource.name ?? resource.id ?? kind, addedAt: Date.now() });
    this.#records.push(row);
    this.#trace?.emit('runtime:resource-own', { kind: row.kind, label: row.label, count: this.#records.length });
    return resource;
  }
  snapshot() {
    return Object.freeze({
      closed: this.#closed,
      count: this.#records.length,
      resources: this.#records.map((row) => Object.freeze({ kind: row.kind, label: row.label }))
    });
  }
  async closeAll({ reason = 'runtime-close' } = {}) {
    if (this.#closed) return Object.freeze({ disposition: 'already-closed', resourceCount: this.#records.length, closedCount: 0, failedCount: 0, resources: Object.freeze([]) });
    this.#closed = true;
    const rows = this.#records.slice().reverse();
    const results = [];
    for (const row of rows) {
      try {
        let result = null;
        if (typeof row.resource.closeAsync === 'function') result = row.resource.closeAsync({ reason });
        else if (typeof row.resource.close === 'function') result = row.resource.close(reason);
        else if (typeof row.resource.terminate === 'function') result = row.resource.terminate(reason);
        if (result && typeof result.then === 'function') result = await result;
        results.push(Object.freeze({ kind: row.kind, label: row.label, status: 'closed', result: result ?? null }));
        this.#trace?.emit('runtime:resource-close', { kind: row.kind, label: row.label, status: 'closed' });
      } catch (error) {
        results.push(Object.freeze({ kind: row.kind, label: row.label, status: 'failed', error: describeError(error) }));
        this.#trace?.emit('runtime:resource-close', { kind: row.kind, label: row.label, status: 'failed', error: describeError(error) });
      }
    }
    return Object.freeze({
      disposition: 'closed',
      resourceCount: rows.length,
      closedCount: results.filter((row) => row.status === 'closed').length,
      failedCount: results.filter((row) => row.status !== 'closed').length,
      resources: Object.freeze(results)
    });
  }
}
export async function boot(options = {}) {
  const trace = new TraceLog({ capacity: options.traceCapacity ?? 4096 });
  const owner = new RuntimeResourceOwner({ trace });
  const capabilities = detectCapabilities();
  const report = createBootReport({ capabilities, options });
  trace.emit('runtime:boot', { revision: REVISION, version: VERSION, capabilities });
  trace.emit('runtime:boot-report', { report });
  const track = (resource, kind, label = null, owned = true) => owner.track(resource, { kind, label, owned });
  const runtime = {
    version: VERSION,
    revision: REVISION,
    options: Object.freeze({ ...options }),
    capabilities,
    report,
    trace,
    scope(config = {}) { const scope = new OperationScope({ ...config, trace: config.trace || trace }); return track(scope, 'operation-scope', scope.label, config?.owned !== false); },
    channel(config) { const channel = new BoundedChannel({ ...(config || {}), trace }); if (config?.scope) normalizeScope(config.scope, 'channel scope').track(channel, { kind: 'channel', label: channel.label }); return track(channel, 'channel', channel.label, config?.owned !== false); },
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
      return track(ring, 'shared-int32-ring', ring.label, config.owned !== false);
    },
    openSharedInt32Ring(sab, config = {}) {
      const ring = openSharedInt32Ring(sab, { ...config, trace: config.trace || trace });
      trace.emit('object:shared-ring-open', { label: ring.label, capacity: ring.capacity, bytes: ring.sab.byteLength });
      return track(ring, 'shared-int32-ring-open', ring.label, config.owned !== false);
    },
    sharedFrameRing(config = {}) {
      const ring = createSharedFrameRing({ ...config, trace: config.trace || trace });
      trace.emit('object:shared-frame-ring-ref', { label: ring.label, capacityBytes: ring.capacityBytes, bytes: ring.sab.byteLength });
      return track(ring, 'shared-frame-ring', ring.label, config.owned !== false);
    },
    openSharedFrameRing(sab, config = {}) {
      const ring = openSharedFrameRing(sab, { ...config, trace: config.trace || trace });
      trace.emit('object:shared-frame-ring-open', { label: ring.label, capacityBytes: ring.capacityBytes, bytes: ring.sab.byteLength });
      return track(ring, 'shared-frame-ring-open', ring.label, config.owned !== false);
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
      return track(store, 'opfs-async-block-store', store.name, config.owned !== false);
    },
    async opfsAsyncBlockStoreWithPosture(config = {}) {
      const postureConfig = config.postureConfig && typeof config.postureConfig === 'object' ? config.postureConfig : {};
      const budgetPolicy = config.budgetPolicy ?? postureConfig.budgetPolicy;
      const labelBase = config.label || config.name || postureConfig.label || 'opfs-async-block-store-with-posture';
      const posture = await this.browserStoragePosture({
        ...postureConfig,
        label: config.postureLabel || postureConfig.label || `${labelBase}-storage-posture`,
        budgetPolicy,
        requestPersistentStorage: config.requestPersistentStorage === true || postureConfig.requestPersistentStorage === true
      });
      const admissionPolicy = posture.admissionPolicy || {};
      const status = String(admissionPolicy.status || 'unknown');
      const allowEstimateRequired = config.allowEstimateRequired === true;
      const admitted = status === 'admit-with-guard' || (status === 'estimate-required' && allowEstimateRequired);
      if (!admitted && config.failOnStorageAdmission !== false) {
        const detail = {
          status,
          label: posture.label,
          riskLevel: posture.riskLevel,
          warningIds: Array.isArray(posture.warnings) ? posture.warnings.map((row) => row.id) : [],
          projectedWritableBytes: admissionPolicy.projectedWritableBytes ?? null,
          plannedWriteBytes: admissionPolicy.plannedWriteBytes ?? null,
          plannedBudgetedBytes: admissionPolicy.plannedBudgetedBytes ?? null,
          transientWriteMultiplier: admissionPolicy.transientWriteMultiplier ?? null,
          plannedWriteFits: admissionPolicy.plannedWriteFits ?? null,
          freeBytes: admissionPolicy.freeBytes ?? null,
          quotaKnown: admissionPolicy.quotaKnown === true,
          mutationSafeDefault: admissionPolicy.mutationSafeDefault === true
        };
        const message = 'BrowserRT OPFS storage posture did not admit guarded block-store creation';
        detail.recovery = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTStorageAdmissionError', code: 'BRT_BROWSER_STORAGE_ADMISSION_REJECTED', message, detail }, { op: 'opfsAsyncBlockStoreWithPosture', phase: 'posture-admission' });
        detail.preMutationRejected = detail.recovery.preMutationRejected;
        trace.emit('storage:opfs-block-store-posture-admission-rejected', detail);
        trace.emit('runtime:browser-storage-recovery-guidance', { code: detail.recovery.code, category: detail.recovery.category, phase: detail.recovery.phase, action: detail.recovery.action, preMutationRejected: detail.recovery.preMutationRejected });
        throw createBrowserRtError(message, { name: 'BrowserRTStorageAdmissionError', code: 'BRT_BROWSER_STORAGE_ADMISSION_REJECTED', detail });
      }
      const storeConfig = config.storeConfig && typeof config.storeConfig === 'object' ? config.storeConfig : {};
      const postureGuard = resolvePosturedWriteBudgetGuard({ ...config, storeConfig }, admissionPolicy, { label: labelBase, trace });
      const store = this.opfsAsyncBlockStore({
        ...storeConfig,
        name: config.name ?? storeConfig.name ?? labelBase,
        prefix: config.prefix ?? storeConfig.prefix ?? `browserrt/${REVISION}/postured-opfs-block-store`,
        provider: config.provider ?? storeConfig.provider,
        verifyExistingBlocksOnPut: config.verifyExistingBlocksOnPut ?? storeConfig.verifyExistingBlocksOnPut,
        verifyAfterWrite: config.verifyAfterWrite ?? storeConfig.verifyAfterWrite,
        verifyOnHas: config.verifyOnHas ?? storeConfig.verifyOnHas,
        repairCorruptOnPut: config.repairCorruptOnPut ?? storeConfig.repairCorruptOnPut,
        exclusiveWriters: config.exclusiveWriters ?? storeConfig.exclusiveWriters,
        writeBudgetGuard: postureGuard.guard,
        minFreeBytesForPut: config.minFreeBytesForPut ?? storeConfig.minFreeBytesForPut,
        maxUsageRatioForPut: config.maxUsageRatioForPut ?? storeConfig.maxUsageRatioForPut,
        requireStorageEstimateForPut: config.requireStorageEstimateForPut ?? storeConfig.requireStorageEstimateForPut,
        allowWriteBudgetGuardOverride: false,
        owned: config.owned ?? storeConfig.owned
      });
      trace.emit('object:opfs-async-block-store-with-posture-ref', { label: store.name, provider: store.provider, prefix: store.prefix, admissionStatus: status, riskLevel: posture.riskLevel, warningIds: posture.warnings.map((row) => row.id), writeBudgetGuard: store.writeBudgetGuard, postureGuardPolicy: postureGuard.policy, postureReceiptFormat: posture.opfsPostureReceipt?.format || null, internalByteLedgerProvided: posture.opfsPostureReceipt?.internalByteLedger?.provided === true, plannedBudgetedBytes: admissionPolicy.plannedBudgetedBytes ?? null });
      return Object.freeze({ store, posture, postureReceipt: posture.opfsPostureReceipt, admissionPolicy, writeBudgetGuard: admissionPolicy.writeBudgetGuard, postureGuardPolicy: postureGuard.policy, status: 'admitted' });
    },
    async kernelKitOpfsAbortBoundary(config = {}) {
      const payload = config.payload instanceof Uint8Array
        ? config.payload
        : new TextEncoder().encode(config.text || `BrowserRT ${REVISION} Kernel Kit OPFS abort-boundary proof`);
      const digest = `sha256:${await digestBytesHex(payload)}`;
      const prefix = config.prefix || `browserrt/${REVISION}/kernel-kit-opfs-abort-boundary`;
      const store = config.store || this.opfsAsyncBlockStore({
        name: config.name || `${REVISION}-kernel-kit-opfs-abort-boundary`,
        prefix,
        verifyOnHas: true,
        verifyExistingBlocksOnPut: true,
        verifyAfterWrite: true,
        writeBudgetGuard: false,
        ...(config.storeConfig || {})
      });
      const capture = (error) => Object.freeze({
        name: error?.name || 'Error',
        message: error?.message || String(error),
        code: error?.code ?? null,
        detail: error?.detail ?? null
      });
      const expectReject = async (label, fn) => {
        try {
          const value = await fn();
          return Object.freeze({ label, ok: true, value });
        } catch (error) {
          return Object.freeze({ label, ok: false, error: capture(error) });
        }
      };
      const liveSignal = new AbortController();
      const preAborted = new AbortController();
      preAborted.abort(new Error('kernel-kit-opfs-abort-boundary-secondary-abortSignal'));
      const rejectedPut = await expectReject('kernel-kit-opfs-pre-aborted-abortSignal-put', () => store.put(payload, { label: 'kernel-kit-opfs-pre-aborted-abortSignal-put' }, { signal: liveSignal.signal, abortSignal: preAborted.signal, writeBudgetGuard: false }));
      const invalidSibling = await expectReject('kernel-kit-opfs-invalid-abortSignal-sibling-put', () => store.put(payload, { label: 'kernel-kit-opfs-invalid-abortSignal-sibling-put' }, { signal: liveSignal.signal, abortSignal: { aborted: false }, writeBudgetGuard: false }));
      const hasAfterAbort = await store.has(digest, { signal: null, abortSignal: null });
      const verifyAfterAbort = await store.verify(digest, { signal: null, abortSignal: null });
      const cleanup = await store.cleanupForTest({ signal: null, abortSignal: null }).catch((error) => ({ ok: false, error: capture(error) }));
      const snapshot = store.snapshot();
      const proof = Object.freeze({
        compositeAbortRejected: rejectedPut.ok === false && rejectedPut.error?.code === 'BRT_OPFS_OPERATION_ABORTED',
        invalidSiblingRejected: invalidSibling.ok === false && invalidSibling.error?.code === 'BRT_OPFS_ABORT_SIGNAL_INVALID',
        noBlockPresent: hasAfterAbort === false && verifyAfterAbort.present === false,
        optionPairCounted: snapshot.stats?.abortSignalOptionPairs >= 1 && snapshot.stats?.compositeAbortSignals >= 1,
        cleanupAttempted: cleanup === true || cleanup === false || cleanup?.ok === false,
        nonMutationBoundary: rejectedPut.ok === false && hasAfterAbort === false && verifyAfterAbort.present === false
      });
      const report = Object.freeze({
        project: 'BrowserRT',
        revision: REVISION,
        version: VERSION,
        schema: 1,
        runner: 'kernel-kit-opfs-abort-boundary',
        status: Object.values(proof).every(Boolean) ? 'passed' : 'failed',
        purpose: 'Exercise the current raw OPFS signal/abortSignal fail-closed boundary inside the product-facing Kernel Kit browser path.',
        prefix,
        digest,
        payloadBytes: payload.byteLength,
        rejectedPut,
        invalidSibling,
        hasAfterAbort,
        verifyAfterAbort,
        cleanup,
        snapshot,
        proof,
        nonClaims: Object.freeze([
          'Abort remains cooperative; this proves BrowserRT checkpoints honor composed signals, not that browser filesystem calls are preemptible in every stage.',
          'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, multi-tab coordination, or cross-browser conformance claim.'
        ])
      });
      trace.emit('kernel-kit-demo:opfs-abort-boundary', { status: report.status, compositeAbortRejected: proof.compositeAbortRejected, invalidSiblingRejected: proof.invalidSiblingRejected, noBlockPresent: proof.noBlockPresent, digest });
      return report;
    },
    async browserStoragePosture(config = {}) {
      const report = await diagnoseBrowserStoragePosture({ ...config, revision: REVISION, version: VERSION, globalThis: config.globalThis || globalThis, trace: config.trace || trace });
      trace.emit('runtime:browser-storage-posture', { label: report.label, status: report.status, riskLevel: report.riskLevel, warningIds: report.warnings.map((row) => row.id), requestPersistentStorage: report.requestPersistentStorage });
      return report;
    },
    browserStorageRecoveryGuidance(error, context = {}) {
      const guidance = createBrowserStorageRecoveryGuidance(error, context);
      trace.emit('runtime:browser-storage-recovery-guidance', { code: guidance.code, category: guidance.category, phase: guidance.phase, action: guidance.action, preMutationRejected: guidance.preMutationRejected, retryable: guidance.retryable });
      return guidance;
    },
    async kernelKitStoragePosture(config = {}) {
      const posture = await this.browserStoragePosture({ ...config, label: config.label || 'kernel-kit-storage-posture' });
      const capabilities = detectCapabilities(config.globalThis || globalThis);
      const proof = Object.freeze({
        storageManagerSeen: posture.capabilities.storageManager === true,
        estimateChecked: posture.estimate.available === true && posture.estimate.ok === true,
        quotaKnown: Number.isFinite(posture.estimate.quota),
        usageKnown: Number.isFinite(posture.estimate.usage),
        persistedChecked: posture.persisted.available ? posture.persisted.ok === true : true,
        persistenceNotRequestedByDefault: config.requestPersistentStorage !== true && posture.persistRequest.skipped === true,
        opfsCapabilityVisible: posture.capabilities.opfs === true,
        admissionPolicyDerived: posture.proof.admissionPolicyDerived === true,
        mutationGuardActionable: posture.proof.mutationGuardActionable === true,
        noEvictionSurvivalClaim: posture.proof.noEvictionSurvivalClaim === true,
        browserStoragePostureDiagnostic: posture.format === BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT
      });
      const report = Object.freeze({
        project: 'BrowserRT',
        revision: REVISION,
        version: VERSION,
        schema: 2,
        runner: 'kernel-kit-storage-posture',
        label: posture.label,
        status: proof.storageManagerSeen && proof.estimateChecked && proof.persistenceNotRequestedByDefault && proof.noEvictionSurvivalClaim ? 'passed' : 'partial',
        purpose: 'Capture browser-local storage posture for the Kernel Kit path without requesting persistent storage or claiming durability, quota reservation, or eviction survival.',
        capabilities,
        estimate: posture.estimate,
        persisted: posture.persisted,
        persistRequest: posture.persistRequest,
        admissionPolicy: posture.admissionPolicy,
        writeBudgetGuard: posture.writeBudgetGuard,
        browserStoragePosture: posture,
        warnings: posture.warnings,
        proof,
        nonClaims: Object.freeze([
          'Storage posture is advisory capability/estimate evidence, not a quota reservation or eviction-survival proof.',
          'Persistent-storage grant is not requested by default and no browser-restart, fsync, crash-recovery, or cross-browser claim is made.'
        ])
      });
      trace.emit('kernel-kit-demo:storage-posture', { label: report.label, status: report.status, estimateChecked: proof.estimateChecked, quotaKnown: proof.quotaKnown, persistedChecked: proof.persistedChecked, persistenceRequested: posture.persistRequest.requested, admissionPolicy: posture.admissionPolicy?.status, mutationGuardActionable: proof.mutationGuardActionable });
      return report;
    },
    async kernelKitWebLockPosture(config = {}) {
      const capabilities = detectCapabilities(globalThis);
      const label = config.label || 'kernel-kit-web-lock-posture';
      const prefix = config.prefix || `browserrt:${REVISION}:kernel-kit-web-lock-posture`;
      const lockName = config.lockName || 'demo-exclusive-and-shared-boundary';
      const sharedLockName = config.sharedLockName || `${lockName}-shared`;
      const timeoutMs = Number.isFinite(config.timeoutMs) ? Math.max(1, Number(config.timeoutMs)) : 1200;
      const holdMs = Number.isFinite(config.holdMs) ? Math.max(1, Number(config.holdMs)) : 35;
      const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, Math.max(1, ms)));
      const capture = (error) => Object.freeze({ name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null });
      const coordinator = config.coordinator || this.webLockCoordinator({ label, prefix, defaultTimeoutMs: timeoutMs, requireAvailable: false });
      if (!coordinator.available) {
        const report = Object.freeze({
          project: 'BrowserRT',
          revision: REVISION,
          version: VERSION,
          schema: 1,
          runner: 'kernel-kit-web-lock-posture',
          label,
          status: 'unavailable',
          purpose: 'Surface whether the Kernel Kit product path can observe browser Web Locks coordination without claiming fairness or lifecycle recovery.',
          capabilities,
          proof: Object.freeze({ navigatorLocksSeen: false, exclusiveNoOverlap: false, sharedCoHold: false, drainedAfterUse: false, noFairnessClaim: true }),
          nonClaims: Object.freeze([
            'Web Locks posture is managed-browser coordination evidence, not a fairness, multi-tab lifecycle, crash-recovery, or cross-browser guarantee.',
            'No OPFS durability, quota, eviction, fsync, exactly-once, or production coordination claim.'
          ])
        });
        trace.emit('kernel-kit-demo:web-lock-posture', { label, status: report.status, available: false });
        return report;
      }
      let activeExclusive = 0;
      let maxExclusiveActive = 0;
      let exclusiveOverlap = false;
      const exclusiveOrder = [];
      const exclusiveEvents = [];
      const enterExclusive = async (name, ms) => await coordinator.exclusive(lockName, async (lock) => {
        activeExclusive += 1;
        maxExclusiveActive = Math.max(maxExclusiveActive, activeExclusive);
        if (activeExclusive > 1) exclusiveOverlap = true;
        exclusiveOrder.push(`${name}:enter`);
        exclusiveEvents.push({ event: 'exclusive-enter', name, lock: lock ? { name: lock.name, mode: lock.mode } : null, activeExclusive });
        await sleep(ms);
        exclusiveOrder.push(`${name}:exit`);
        exclusiveEvents.push({ event: 'exclusive-exit', name, activeExclusive });
        activeExclusive -= 1;
        return name;
      }, { timeoutMs, metadata: { surface: 'kernel-kit-web-lock-posture', phase: name } });
      let exclusiveResults = [];
      let exclusiveError = null;
      try {
        const first = enterExclusive('a', holdMs);
        await sleep(5);
        const second = enterExclusive('b', 2);
        exclusiveResults = await Promise.all([first, second]);
      } catch (error) {
        exclusiveError = capture(error);
      }
      let activeShared = 0;
      let maxSharedActive = 0;
      let releaseShared = null;
      const sharedEvents = [];
      const releaseSharedPromise = new Promise((resolve) => { releaseShared = resolve; });
      const enterShared = async (name) => await coordinator.shared(sharedLockName, async (lock) => {
        activeShared += 1;
        maxSharedActive = Math.max(maxSharedActive, activeShared);
        sharedEvents.push({ event: 'shared-enter', name, lock: lock ? { name: lock.name, mode: lock.mode } : null, activeShared });
        if (activeShared >= 2) releaseShared();
        await Promise.race([releaseSharedPromise, sleep(80)]);
        sharedEvents.push({ event: 'shared-exit', name, activeShared });
        activeShared -= 1;
        return name;
      }, { timeoutMs, metadata: { surface: 'kernel-kit-web-lock-posture', phase: name } });
      let sharedResults = [];
      let sharedError = null;
      try {
        sharedResults = await Promise.all([enterShared('s1'), enterShared('s2')]);
      } catch (error) {
        sharedError = capture(error);
      }
      const exclusiveSettled = await coordinator.waitForSettled(lockName, { timeoutMs: 600, intervalMs: 10 }).catch((error) => Object.freeze({ ok: false, error: capture(error), last: null }));
      const sharedSettled = await coordinator.waitForSettled(sharedLockName, { timeoutMs: 600, intervalMs: 10 }).catch((error) => Object.freeze({ ok: false, error: capture(error), last: null }));
      const snapshot = coordinator.snapshot();
      const proof = Object.freeze({
        navigatorLocksSeen: capabilities.webLocks === true && coordinator.available === true,
        exclusiveNoOverlap: exclusiveError === null && exclusiveOverlap === false && maxExclusiveActive === 1 && exclusiveResults.join(',') === 'a,b',
        exclusiveOrderObserved: exclusiveOrder.join('>') === 'a:enter>a:exit>b:enter>b:exit',
        sharedCoHold: sharedError === null && maxSharedActive >= 2 && sharedResults.slice().sort().join(',') === 's1,s2',
        queryObserved: exclusiveSettled?.last?.available === true && sharedSettled?.last?.available === true,
        drainedAfterUse: exclusiveSettled?.ok === true && sharedSettled?.ok === true,
        noFairnessClaim: true
      });
      const report = Object.freeze({
        project: 'BrowserRT',
        revision: REVISION,
        version: VERSION,
        schema: 1,
        runner: 'kernel-kit-web-lock-posture',
        label,
        status: Object.values(proof).every(Boolean) ? 'passed' : 'partial',
        purpose: 'Exercise same-origin Web Locks coordination inside the product-facing Kernel Kit path: exclusive same-name non-overlap, shared co-holding, query/drain evidence, and explicit non-claims.',
        capabilities,
        locks: Object.freeze({ prefix, exclusiveName: coordinator.lockName(lockName), sharedName: coordinator.lockName(sharedLockName) }),
        exclusive: Object.freeze({ results: Object.freeze(exclusiveResults), maxActive: maxExclusiveActive, overlap: exclusiveOverlap, order: Object.freeze(exclusiveOrder), events: Object.freeze(exclusiveEvents), error: exclusiveError }),
        shared: Object.freeze({ results: Object.freeze(sharedResults), maxActive: maxSharedActive, events: Object.freeze(sharedEvents), error: sharedError }),
        settled: Object.freeze({ exclusive: exclusiveSettled, shared: sharedSettled }),
        snapshot,
        proof,
        nonClaims: Object.freeze([
          'Web Locks posture is managed-browser coordination evidence, not a fairness, multi-tab lifecycle, crash-recovery, or cross-browser guarantee.',
          'Kernel Kit records separate guarded-storage-lane evidence when the product path routes OPFS through WebLockGuardedBlockStore; Web Locks posture alone is still not a fairness, lifecycle, cross-browser, or production coordination claim.',
          'No OPFS durability, quota, eviction, fsync, exactly-once, or production coordination claim.'
        ])
      });
      trace.emit('kernel-kit-demo:web-lock-posture', { label, status: report.status, available: true, exclusiveNoOverlap: proof.exclusiveNoOverlap, sharedCoHold: proof.sharedCoHold, drainedAfterUse: proof.drainedAfterUse });
      return report;
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
    kernelKitSupportBundlePrivacyScrub(input = {}, fields = {}) {
      const report = createKernelKitSupportBundlePrivacyScrub(input, { revision: REVISION, ...fields });
      const result = validateKernelKitSupportBundlePrivacyScrub(report);
      trace.emit('kernel-kit-demo:support-bundle-privacy-scrub', { ok: result.ok, status: report.status, redactedFieldCount: result.redactedFieldCount });
      return report;
    },
    validateKernelKitSupportBundlePrivacyScrub(report) {
      const result = validateKernelKitSupportBundlePrivacyScrub(report);
      trace.emit('kernel-kit-demo:support-bundle-privacy-scrub-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status });
      return result;
    },
    kernelKitLifecycleCheckpoint(input = {}, fields = {}) {
      const checkpoint = createKernelKitLifecycleCheckpoint(input, { revision: REVISION, ...fields });
      const result = validateKernelKitLifecycleCheckpoint(checkpoint);
      trace.emit('kernel-kit-demo:lifecycle-checkpoint', { ok: result.ok, status: checkpoint.status, rowCount: result.rowCount, deferredCount: result.deferredCount, failedCount: result.failedCount });
      return checkpoint;
    },
    validateKernelKitLifecycleCheckpoint(checkpoint) {
      const result = validateKernelKitLifecycleCheckpoint(checkpoint);
      trace.emit('kernel-kit-demo:lifecycle-checkpoint-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, rowCount: result.rowCount });
      return result;
    },
    kernelKitSessionCoordinationCheckpoint(input = {}, fields = {}) {
      const checkpoint = createKernelKitSessionCoordinationCheckpoint(input, { revision: REVISION, ...fields });
      const result = validateKernelKitSessionCoordinationCheckpoint(checkpoint);
      trace.emit('kernel-kit-demo:session-coordination-checkpoint', { ok: result.ok, status: checkpoint.status, rowCount: result.rowCount, deferredCount: result.deferredCount, failedCount: result.failedCount });
      return checkpoint;
    },
    validateKernelKitSessionCoordinationCheckpoint(checkpoint) {
      const result = validateKernelKitSessionCoordinationCheckpoint(checkpoint);
      trace.emit('kernel-kit-demo:session-coordination-checkpoint-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, rowCount: result.rowCount });
      return result;
    },
    kernelKitRecoveryCheckpoint(input = {}, fields = {}) {
      const checkpoint = createKernelKitRecoveryCheckpoint(input, { revision: REVISION, ...fields });
      const result = validateKernelKitRecoveryCheckpoint(checkpoint);
      trace.emit('kernel-kit-demo:recovery-checkpoint', { ok: result.ok, status: checkpoint.status, rowCount: result.rowCount, deferredCount: result.deferredCount, failedCount: result.failedCount });
      return checkpoint;
    },
    validateKernelKitRecoveryCheckpoint(checkpoint) {
      const result = validateKernelKitRecoveryCheckpoint(checkpoint);
      trace.emit('kernel-kit-demo:recovery-checkpoint-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, rowCount: result.rowCount });
      return result;
    },
    kernelKitAdmissionCancellationCheckpoint(input = {}, fields = {}) {
      const checkpoint = createKernelKitAdmissionCancellationCheckpoint(input, { revision: REVISION, ...fields });
      const result = validateKernelKitAdmissionCancellationCheckpoint(checkpoint);
      trace.emit('kernel-kit-demo:admission-cancellation-checkpoint', { ok: result.ok, status: checkpoint.status, rowCount: result.rowCount, deferredCount: result.deferredCount, failedCount: result.failedCount });
      return checkpoint;
    },
    validateKernelKitAdmissionCancellationCheckpoint(checkpoint) {
      const result = validateKernelKitAdmissionCancellationCheckpoint(checkpoint);
      trace.emit('kernel-kit-demo:admission-cancellation-checkpoint-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, rowCount: result.rowCount });
      return result;
    },
    kernelKitSupportBundleReplayPlan(input, fields = {}) {
      const report = createKernelKitSupportBundleReplayPlan(input, { revision: REVISION, ...fields });
      const result = validateKernelKitSupportBundleReplayPlan(report);
      trace.emit('kernel-kit-demo:support-bundle-replay-plan', { ok: result.ok, status: report.status, phaseCount: result.phaseCount, commandCount: result.commandCount });
      return report;
    },
    validateKernelKitSupportBundleReplayPlan(report) {
      const result = validateKernelKitSupportBundleReplayPlan(report);
      trace.emit('kernel-kit-demo:support-bundle-replay-plan-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, phaseCount: result.phaseCount });
      return result;
    },
    kernelKitSupportBundleOperatorPreflightDisplaySnapshot(input = {}, fields = {}) {
      const report = createKernelKitSupportBundleOperatorPreflightDisplaySnapshot(input, { revision: REVISION, ...fields });
      const result = validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot(report);
      trace.emit('kernel-kit-demo:support-bundle-operator-display-snapshot', { ok: result.ok, status: report.status, rowCount: result.rowCount });
      return report;
    },
    validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot(report) {
      const result = validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot(report);
      trace.emit('kernel-kit-demo:support-bundle-operator-display-snapshot-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, rowCount: result.rowCount });
      return result;
    },
    kernelKitSupportBundleOperatorReplayGate(input = {}, fields = {}) {
      const report = createKernelKitSupportBundleOperatorReplayGate(input, { revision: REVISION, ...fields });
      const result = validateKernelKitSupportBundleOperatorReplayGate(report);
      trace.emit('kernel-kit-demo:support-bundle-operator-replay-gate', { ok: result.ok, status: report.status, rowCount: result.rowCount, retryVisibleCount: report.retryVisibleCount || 0, blockedCount: report.blockedCount || 0 });
      return report;
    },
    validateKernelKitSupportBundleOperatorReplayGate(report) {
      const result = validateKernelKitSupportBundleOperatorReplayGate(report);
      trace.emit('kernel-kit-demo:support-bundle-operator-replay-gate-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, rowCount: result.rowCount });
      return result;
    },
    kernelKitSupportBundleEvidenceLedger(input, fields = {}) {
      const report = createKernelKitSupportBundleEvidenceLedger(input, { revision: REVISION, ...fields });
      const result = validateKernelKitSupportBundleEvidenceLedger(report);
      trace.emit('kernel-kit-demo:support-bundle-evidence-ledger', { ok: result.ok, status: report.status, entryCount: result.entryCount, outputCount: result.outputCount });
      return report;
    },
    validateKernelKitSupportBundleEvidenceLedger(report) {
      const result = validateKernelKitSupportBundleEvidenceLedger(report);
      trace.emit('kernel-kit-demo:support-bundle-evidence-ledger-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, entryCount: result.entryCount });
      return result;
    },
    kernelKitSupportBundleEvidenceCheckpoint(input, artifacts = {}, fields = {}) {
      const report = createKernelKitSupportBundleEvidenceCheckpoint(input, artifacts, { revision: REVISION, ...fields });
      const result = validateKernelKitSupportBundleEvidenceCheckpoint(report);
      trace.emit('kernel-kit-demo:support-bundle-evidence-checkpoint', { ok: result.ok, status: report.status, rowCount: result.rowCount, satisfiedCount: result.satisfiedCount, deferredCount: result.deferredCount });
      return report;
    },
    validateKernelKitSupportBundleEvidenceCheckpoint(report) {
      const result = validateKernelKitSupportBundleEvidenceCheckpoint(report);
      trace.emit('kernel-kit-demo:support-bundle-evidence-checkpoint-validate', { ok: result.ok, errorCount: result.errors.length, status: result.status, rowCount: result.rowCount });
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
        owned: false,
        ...(config.storeConfig || {})
      });
      const scheduler = config.scheduler || this.crossLaneScheduler({
        label: `${config.label || 'opfs-storage-lane-adapter'}:scheduler`,
        trace: config.trace || trace,
        lanes: config.lanes || [
          { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
          { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
        ],
        ...(config.schedulerConfig || {})
      });
      const adapter = createOpfsBlockStoreStorageLaneAdapter({ ...config, store, scheduler, trace: config.trace || trace, ownStore: config.ownStore ?? !config.store });
      const snapshot = adapter.snapshot();
      trace.emit('object:opfs-storage-lane-adapter-ref', { label: adapter.label, provider: snapshot.store?.provider, prefix: snapshot.store?.prefix, lane: adapter.lane, supportedOps: OPFS_STORAGE_LANE_ADAPTER_SUPPORTED_OPS });
      return track(adapter, 'opfs-storage-lane-adapter', adapter.label, config.owned !== false);
    },
    webLockCoordinator(config = {}) {
      const coordinator = createWebLockCoordinator({ ...config, trace: config.trace || trace });
      trace.emit('object:web-lock-coordinator-ref', { label: coordinator.label, prefix: coordinator.prefix, available: coordinator.available, defaultTimeoutMs: coordinator.defaultTimeoutMs });
      return coordinator;
    },
    opfsWebLockGuardedBlockStore(config = {}) {
      const store = config.store || this.opfsAsyncBlockStore({
        name: `${config.label || 'opfs-web-lock-guarded-block-store'}:store`,
        prefix: config.prefix || `browserrt/${REVISION}/opfs-web-lock-guarded-block-store`,
        trace: config.trace || trace,
        owned: false,
        ...(config.storeConfig || {})
      });
      const guard = createWebLockGuardedBlockStore({ ...config, store, trace: config.trace || trace, ownStore: config.ownStore ?? !config.store });
      const snapshot = guard.snapshot();
      trace.emit('object:opfs-web-lock-guarded-block-store-ref', { label: guard.label, provider: snapshot.provider, prefix: snapshot.prefix, lockName: snapshot.lockName, available: snapshot.available, lockTimeoutMs: snapshot.lockTimeoutMs });
      return track(guard, 'opfs-web-lock-guarded-block-store', guard.label, config.owned !== false);
    },
    async opfsWebLockGuardedBlockStoreWithPosture(config = {}) {
      const labelBase = config.label || config.name || 'opfs-web-lock-guarded-block-store-with-posture';
      const lockContentionPolicy = normalizePosturedWebLockTimeoutMs(config);
      const lockAvailable = Boolean(
        (config.coordinator && config.coordinator.available === true)
        || (config.locks && typeof config.locks.request === 'function')
        || (globalThis.navigator?.locks && typeof globalThis.navigator.locks.request === 'function')
      );
      const requireWebLocks = config.requireWebLocks !== false;
      if (requireWebLocks && !lockAvailable) {
        const message = 'BrowserRT postured guarded OPFS store requires Web Locks unless requireWebLocks is explicitly false';
        const detail = { label: labelBase, lockPrefix: config.lockPrefix || 'browserrt:opfs-block-store', lockName: config.lockName || null, requireWebLocks, lockContentionPolicy, mutationAttempted: false };
        detail.recovery = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTWebLocksRequiredError', code: 'BRT_BROWSER_WEB_LOCKS_REQUIRED', message, detail }, { op: 'opfsWebLockGuardedBlockStoreWithPosture', phase: 'coordination-admission', lockName: detail.lockName, timeoutMs: lockContentionPolicy.lockTimeoutMs });
        detail.preMutationRejected = detail.recovery.preMutationRejected;
        trace.emit('storage:opfs-web-lock-guarded-posture-web-locks-rejected', detail);
        trace.emit('runtime:browser-storage-recovery-guidance', { code: detail.recovery.code, category: detail.recovery.category, phase: detail.recovery.phase, action: detail.recovery.action, preMutationRejected: detail.recovery.preMutationRejected });
        throw createBrowserRtError(message, { name: 'BrowserRTWebLocksRequiredError', code: 'BRT_BROWSER_WEB_LOCKS_REQUIRED', detail });
      }
      let lockFallbackPolicy = null;
      try {
        lockFallbackPolicy = normalizePosturedWebLockFallbackPolicy(config, { label: labelBase, lockAvailable, requireWebLocks, lockContentionPolicy });
      } catch (error) {
        trace.emit('storage:opfs-web-lock-guarded-posture-fallback-rejected', error?.detail || { label: labelBase, lockAvailable, requireWebLocks });
        trace.emit('runtime:browser-storage-recovery-guidance', { code: error?.detail?.recovery?.code || error?.code || null, category: error?.detail?.recovery?.category || null, phase: error?.detail?.recovery?.phase || null, action: error?.detail?.recovery?.action || null, preMutationRejected: error?.detail?.recovery?.preMutationRejected === true });
        throw error;
      }
      const postured = await this.opfsAsyncBlockStoreWithPosture({
        ...config,
        label: labelBase,
        name: config.name ?? `${labelBase}:store`,
        prefix: config.prefix ?? `browserrt/${REVISION}/postured-web-lock-guarded-opfs-block-store`,
        storeConfig: {
          ...(config.storeConfig || {}),
          owned: false
        },
        owned: false
      });
      let guard = null;
      try {
        guard = this.opfsWebLockGuardedBlockStore({
          ...config,
          store: postured.store,
          label: config.guardLabel || labelBase,
          lockTimeoutMs: lockContentionPolicy.lockTimeoutMs,
          ownStore: config.ownStore ?? true,
          allowUnboundedLockTimeoutOverride: lockContentionPolicy.allowUnbounded === true,
          owned: config.owned
        });
      } catch (error) {
        try { await postured.store.closeAsync?.({ reason: 'postured-web-lock-guard-create-failed' }); } catch {}
        throw error;
      }
      const snapshot = guard.snapshot();
      const status = lockFallbackPolicy.singleOwnerFallbackRequested ? 'admitted-single-owner-fallback' : 'admitted-and-guarded';
      trace.emit('object:opfs-web-lock-guarded-block-store-with-posture-ref', { label: guard.label, provider: snapshot.provider, prefix: snapshot.prefix, lockName: snapshot.lockName, available: snapshot.available, lockTimeoutMs: snapshot.lockTimeoutMs, allowUnboundedLockTimeoutOverride: snapshot.allowUnboundedLockTimeoutOverride === true, lockContentionPolicy, lockFallbackPolicy, admissionStatus: postured.admissionPolicy?.status || null, riskLevel: postured.posture?.riskLevel || null, warningIds: postured.posture?.warnings?.map?.((row) => row.id) || [], postureReceiptFormat: postured.postureReceipt?.format || postured.posture?.opfsPostureReceipt?.format || null, postureGuardPolicy: postured.postureGuardPolicy || null, status });
      return Object.freeze({ store: guard, guardedStore: guard, innerStore: postured.store, posture: postured.posture, postureReceipt: postured.postureReceipt || postured.posture?.opfsPostureReceipt, admissionPolicy: postured.admissionPolicy, writeBudgetGuard: postured.writeBudgetGuard, postureGuardPolicy: postured.postureGuardPolicy, lockName: snapshot.lockName, lockContentionPolicy, lockFallbackPolicy, status });
    },
    async opfsWebLockGuardedStorageLaneAdapterWithPosture(config = {}) {
      const labelBase = config.label || config.name || 'opfs-web-lock-guarded-storage-lane-adapter-with-posture';
      const posturedGuarded = await this.opfsWebLockGuardedBlockStoreWithPosture({
        ...config,
        label: config.guardLabel || labelBase,
        owned: config.owned
      });
      const guardedStore = posturedGuarded.guardedStore || posturedGuarded.store;
      let adapter = null;
      try {
        adapter = this.opfsBlockStoreStorageLaneAdapter({
          ...(config.adapterConfig || {}),
          label: config.adapterLabel || labelBase,
          prefix: config.prefix,
          store: guardedStore,
          scheduler: config.scheduler,
          lanes: config.lanes,
          schedulerConfig: config.schedulerConfig,
          lane: config.lane || config.adapterConfig?.lane,
          trace: config.trace,
          ownStore: false,
          owned: config.adapterOwned
        });
      } catch (error) {
        try { await guardedStore.closeAsync?.({ reason: 'postured-guarded-storage-lane-adapter-create-failed' }); } catch {}
        throw error;
      }
      const adapterSnapshot = adapter.snapshot();
      const storeSnapshot = guardedStore.snapshot?.() || null;
      trace.emit('object:opfs-web-lock-guarded-storage-lane-adapter-with-posture-ref', {
        label: adapter.label,
        lane: adapter.lane,
        provider: adapterSnapshot.provider || null,
        storeProvider: storeSnapshot?.provider || guardedStore.provider || null,
        prefix: storeSnapshot?.prefix || guardedStore.prefix || config.prefix || null,
        lockName: posturedGuarded.lockName || storeSnapshot?.lockName || null,
        admissionStatus: posturedGuarded.admissionPolicy?.status || null,
        writeBudgetGuardSource: posturedGuarded.writeBudgetGuard?.source || null,
        postureGuardPolicy: posturedGuarded.postureGuardPolicy || null,
        lockContentionPolicySource: posturedGuarded.lockContentionPolicy?.source || null,
        lockTimeoutMs: posturedGuarded.lockContentionPolicy?.lockTimeoutMs ?? storeSnapshot?.lockTimeoutMs ?? null,
        lockFallbackPolicy: posturedGuarded.lockFallbackPolicy || null,
        status: posturedGuarded.status === 'admitted-single-owner-fallback' ? 'admitted-single-owner-fallback-lane-adapter' : 'admitted-guarded-lane-adapter',
        source: 'postured-web-lock-guarded-storage-lane-adapter-factory'
      });
      return Object.freeze({
        adapter,
        laneAdapter: adapter,
        store: guardedStore,
        guardedStore,
        innerStore: posturedGuarded.innerStore,
        posturedGuarded,
        posture: posturedGuarded.posture,
        admissionPolicy: posturedGuarded.admissionPolicy,
        writeBudgetGuard: posturedGuarded.writeBudgetGuard,
        postureGuardPolicy: posturedGuarded.postureGuardPolicy,
        postureReceipt: posturedGuarded.postureReceipt || posturedGuarded.posture?.opfsPostureReceipt,
        lockName: posturedGuarded.lockName,
        lockContentionPolicy: posturedGuarded.lockContentionPolicy,
        lockFallbackPolicy: posturedGuarded.lockFallbackPolicy,
        lane: adapter.lane,
        adapterFactorySource: 'postured-web-lock-guarded-storage-lane-adapter-factory',
        status: posturedGuarded.status === 'admitted-single-owner-fallback' ? 'admitted-single-owner-fallback-lane-adapter' : 'admitted-guarded-lane-adapter'
      });
    },
    async opfsAsyncWriteReadProbe(config = {}) {
      trace.emit('storage:opfs-async-probe-start', { path: config.path ?? `browserrt/${REVISION}/opfs-async-proof.bin` });
      const result = await opfsAsyncWriteReadProbe(config);
      trace.emit('storage:opfs-async-probe-result', { path: result.path, bytesWritten: result.bytesWritten, bytesRead: result.bytesRead, same: result.same, digest: result.digest });
      return result;
    },
    async spawnAgent(config = {}) { const agent = await spawnWorkerAgent({ ...config, trace: config.trace || trace }); if (config?.scope) normalizeScope(config.scope, 'spawnAgent scope').track(agent, { kind: 'worker-agent', label: agent.name }); return track(agent, 'worker-agent', agent.name, config.owned !== false); },
    supervisor(config = {}) { const supervisor = createSupervisor({ ...config, trace: config.trace || trace }); return track(supervisor, 'supervisor', supervisor.name, config.owned !== false); },
    ownedResources() { return owner.snapshot(); },
    close(reason = 'runtime-close') {
      trace.emit('runtime:close', { revision: REVISION, resourceCount: owner.size, mode: 'compat-sync-dispatch', reason });
      void owner.closeAll({ reason }).then((resourceClose) => {
        trace.emit('runtime:close-complete', { revision: REVISION, ...resourceClose });
      }).catch((error) => {
        trace.emit('runtime:close-error', { revision: REVISION, error: describeError(error) });
      });
      return trace.snapshot();
    },
    async closeAsync({ reason = 'runtime-close' } = {}) {
      trace.emit('runtime:close', { revision: REVISION, resourceCount: owner.size, mode: 'async', reason });
      const resourceClose = await owner.closeAll({ reason });
      trace.emit('runtime:close-complete', { revision: REVISION, ...resourceClose });
      return Object.freeze({ revision: REVISION, version: VERSION, resourceClose, trace: trace.snapshot() });
    }
  };
  return Object.freeze(attachRuntimeNamespaces(runtime));
}
export { SharedInt32Ring, createSharedInt32Ring, openSharedInt32Ring } from './sab-ring.mjs';
export { SharedFrameRing, createSharedFrameRing, openSharedFrameRing } from './sab-frame-ring.mjs';
export { SpillFrameMailbox, createSpillFrameMailbox, checksumFramePayload32 } from './spill-mailbox.mjs';
export { PersistedSpillMailbox, createPersistedSpillMailbox, recoverPersistedSpillMailbox, checksumPersistedSpillPayload32 } from './persisted-spill-mailbox.mjs';
export { WatermarkAdmissionController, createWatermarkAdmissionController } from './admission-control.mjs';
export { AdaptiveConcurrencyController, createAdaptiveConcurrencyController } from './adaptive-concurrency.mjs';
export { PriorityFairScheduler, createPriorityFairScheduler, PRIORITY_FAIRNESS_ORDER } from './priority-fairness.mjs';
export { CrossLaneScheduler, createCrossLaneScheduler, CROSS_LANE_PRIORITY_ORDER, validateCrossLaneSchedulerSnapshot } from './cross-lane-scheduler.mjs';
export { StorageLaneExecutor, createStorageLaneExecutor, STORAGE_LANE_EXECUTOR_SUPPORTED_OPS, validateStorageLaneExecutorSnapshot, timedOutQuarantineFingerprint } from './storage-lane-scheduler.mjs';
export { BlockStoreLaneAdapter, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, BLOCK_STORE_LANE_ADAPTER_OPS, createTimedOutOperationQuarantineClearanceReceipt, validateTimedOutOperationQuarantineClearanceReceipt, timedOutOperationQuarantineClearanceReceiptFingerprint } from './block-store-lane-adapter.mjs';
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
export { WebLockCoordinator, createWebLockCoordinator } from './web-lock-coordinator.mjs';
export { WebLockGuardedBlockStore, createWebLockGuardedBlockStore } from './opfs-web-lock-guarded-block-store.mjs';
export { createDreamBoundaryMap, validateDreamBoundaryMap, DREAM_BOUNDARY_CATEGORIES, DREAM_BOUNDARY_AREAS } from './dream-boundary.mjs';
export { createProjectContinuationAssessment, validateProjectContinuationAssessment, PROJECT_ASSESSMENT_AUDIENCES, PROJECT_ASSESSMENT_POSTURES } from './project-assessment.mjs';
export { createKernelKitDemoPlan, validateKernelKitDemoPlan, validateKernelKitDemoProof, validateKernelKitDemoReport, summarizeKernelKitDemoTrace, scoreKernelKitDemoUsefulness, createKernelKitDemoTranscript, validateKernelKitDemoTranscript, createKernelKitTraceExport, validateKernelKitTraceExport, createKernelKitDemoHandoff, validateKernelKitDemoHandoff, KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY, KERNEL_KIT_DEMO_HANDOFF_REQUIRED_KEYS, KERNEL_KIT_DEMO_EXPORT_FORMATS, KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS, KERNEL_KIT_DEMO_FAILURE_MODES, KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT, KERNEL_KIT_DEMO_EXPORT_BUNDLE_NON_CLAIMS, createKernelKitDemoExportBundle, validateKernelKitDemoExportBundle, createKernelKitFailureModeReport, validateKernelKitFailureModeReport, createKernelKitTraceComparison, validateKernelKitTraceComparison, createKernelKitDiagnosticRunbook, validateKernelKitDiagnosticRunbook, createKernelKitSupportBundle, validateKernelKitSupportBundle, createKernelKitSupportBundlePrivacyScrub, validateKernelKitSupportBundlePrivacyScrub, KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_NON_CLAIMS, createKernelKitSupportBundleImportReport, validateKernelKitSupportBundleImportReport, createKernelKitSupportBundleDiff, validateKernelKitSupportBundleDiff, createKernelKitSupportBundleReplayPlan, validateKernelKitSupportBundleReplayPlan, createKernelKitSupportBundleOperatorPreflightDisplaySnapshot, validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot, KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_PREFLIGHT_DISPLAY_SNAPSHOT_FORMAT, createKernelKitSupportBundleOperatorReplayGate, validateKernelKitSupportBundleOperatorReplayGate, KERNEL_KIT_SUPPORT_BUNDLE_OPERATOR_REPLAY_GATE_FORMAT, createKernelKitSupportBundleEvidenceLedger, validateKernelKitSupportBundleEvidenceLedger, createKernelKitSupportBundleEvidenceCheckpoint, validateKernelKitSupportBundleEvidenceCheckpoint, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PHASE_IDS, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_NON_CLAIMS, KERNEL_KIT_TRACE_COMPARISON_FORMAT, KERNEL_KIT_TRACE_COMPARISON_NON_CLAIMS, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_NON_CLAIMS, KERNEL_KIT_SUPPORT_BUNDLE_FORMAT, KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS, createKernelKitGuidedTour, validateKernelKitGuidedTour, createKernelKitGuidedTourReceipt, validateKernelKitGuidedTourReceipt, KERNEL_KIT_GUIDED_TOUR_FORMAT, KERNEL_KIT_GUIDED_TOUR_STEPS, KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS, KERNEL_KIT_DEMO_CODENAME, KERNEL_KIT_DEMO_STEPS, KERNEL_KIT_DEMO_REQUIRED_STEPS, KERNEL_KIT_DEMO_STAGE_LABELS, KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS, KERNEL_KIT_DEMO_NON_CLAIMS };
export { createKernelKitHandoffMarkdown, validateKernelKitHandoffMarkdown, KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT, KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS } from './kernel-kit-handoff-markdown.mjs';
export { createKernelKitHandoffMarkdownImportReport, validateKernelKitHandoffMarkdownImportReport, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS, KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS } from './kernel-kit-handoff-reader.mjs';
export { createKernelKitReadinessGate, validateKernelKitReadinessGate, KERNEL_KIT_READINESS_GATE_FORMAT, KERNEL_KIT_READINESS_GATE_NON_CLAIMS, KERNEL_KIT_READINESS_GATE_REQUIRED_GATES, KERNEL_KIT_READINESS_GATE_PERSONAS } from './kernel-kit-readiness-gate.mjs';
export { createKernelKitReadinessContrast, validateKernelKitReadinessContrast, createDegradedKernelKitReadinessGate, KERNEL_KIT_READINESS_CONTRAST_FORMAT, KERNEL_KIT_READINESS_CONTRAST_NON_CLAIMS, KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES } from './kernel-kit-readiness-contrast.mjs';
export { createKernelKitLifecycleCheckpoint, validateKernelKitLifecycleCheckpoint, KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT, KERNEL_KIT_LIFECYCLE_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS } from './kernel-kit-lifecycle-checkpoint.mjs';
export { createKernelKitSessionCoordinationCheckpoint, validateKernelKitSessionCoordinationCheckpoint, KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT, KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_REQUIRED_ROWS } from './kernel-kit-session-coordination-checkpoint.mjs';
export { createKernelKitRecoveryCheckpoint, validateKernelKitRecoveryCheckpoint, KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT, KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_RECOVERY_CHECKPOINT_REQUIRED_ROWS } from './kernel-kit-recovery-checkpoint.mjs';
export { createKernelKitAdmissionCancellationCheckpoint, validateKernelKitAdmissionCancellationCheckpoint, KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT, KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS, KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_REQUIRED_ROWS } from './kernel-kit-admission-cancellation-checkpoint.mjs';
export { createKernelKitDemoObservatoryReport, validateKernelKitDemoObservatoryReport, KERNEL_KIT_OBSERVATORY_CODENAME, KERNEL_KIT_OBSERVATORY_REQUIRED_SECTIONS, KERNEL_KIT_OBSERVATORY_NON_CLAIMS };
export { createKernelKitDemoUsefulnessReport, validateKernelKitDemoUsefulnessReport, KERNEL_KIT_USEFULNESS_CODENAME, KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS, KERNEL_KIT_USEFULNESS_AUDIENCES, KERNEL_KIT_USEFULNESS_NON_CLAIMS };
export { diagnoseBrowserStoragePosture, BROWSERRT_BROWSER_STORAGE_POSTURE_FORMAT } from './browser-storage-posture.mjs';
export { createBrowserStorageRecoveryGuidance, attachBrowserStorageRecoveryGuidance, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT } from './browser-storage-recovery-guidance.mjs';
export { classifyOpfsBlockStoreError };
