export const BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT = 'browserrt.browser-storage-recovery-guidance.v1';
function asObject(value) {
  return value && typeof value === 'object' ? value : null;
}
function errorCode(error) {
  if (typeof error?.code === 'string') return error.code;
  if (typeof error?.detail?.code === 'string') return error.detail.code;
  if (typeof error?.detail?.originalDetail?.code === 'string') return error.detail.originalDetail.code;
  return 'BRT_STORAGE_FAILURE_UNCLASSIFIED';
}
function errorName(error) {
  return error?.name || error?.detail?.name || 'Error';
}
function errorMessage(error) {
  return error?.message || error?.detail?.message || String(error);
}
function firstFinite(...values) {
  for (const value of values) {
    const n = Number(value);
    if (Number.isFinite(n) && n >= 0) return Math.floor(n);
  }
  return null;
}
function stringArray(value) {
  return Object.freeze(Array.isArray(value) ? value.filter((row) => typeof row === 'string') : []);
}
function uniqueStrings(values) {
  const out = [];
  const seen = new Set();
  for (const value of values.flat()) {
    if (typeof value !== 'string' || !value || seen.has(value)) continue;
    seen.add(value);
    out.push(value);
  }
  return Object.freeze(out);
}
function compactDetail(detail = {}) {
  const keys = [
    'status', 'riskLevel', 'warningIds', 'reasons', 'reason', 'op', 'stage', 'source', 'lockName', 'name', 'mode', 'timeoutMs',
    'store', 'prefix', 'overrideKeys', 'allowWriteBudgetGuardOverride', 'allowUnboundedLockTimeoutOverride', 'allowUnboundedPostureLockWait', 'allowUnsafeSingleOwnerFallback', 'singleOwnerFallbackRequested', 'lockAvailable', 'requireWebLocks', 'overrideRejected', 'requestedBytes', 'quota', 'usage', 'freeBytes', 'freeBefore', 'projectedWritableBytes', 'projectedFreeBytes',
    'projectedUsageRatio', 'plannedWriteBytes', 'plannedBudgetedBytes', 'quotaKnown', 'mutationSafeDefault', 'valueType', 'disabled', 'hasSignal', 'hasAbortSignal', 'defaultTimeoutMs', 'proposedTimeoutMs', 'selected'
  ];
  const out = {};
  for (const key of keys) {
    if (detail?.[key] !== undefined) out[key] = detail[key];
  }
  const metadata = asObject(detail?.metadata);
  if (metadata) {
    for (const key of ['op', 'store', 'provider', 'lockName']) if (out[key] === undefined && metadata[key] !== undefined) out[key] = metadata[key];
  }
  return Object.freeze(out);
}
const RECOVERY_STEPS = Object.freeze({
  BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED: Object.freeze(['Do not create the postured OPFS store with a factory-level writeBudgetGuard override.','Remove the override and tune budgetPolicy, or opt into the unsafe override explicitly.','Retry only after the posture receipt still shows an enforced guard.']),
  BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED: Object.freeze(['Treat the put as rejected before OPFS file mutation.','Remove the disabling/weaker per-put writeBudgetGuard/minFree/maxUsage override on postured stores.','Create a non-postured raw store only if product policy intentionally accepts unpostured per-write overrides.']),
  BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED: Object.freeze(['Reject before OPFS store creation.','Use bounded lock timeout, or explicit allowUnboundedPostureLockWait policy.','Query locks before retrying.']),
  BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED: Object.freeze(['Reject before Web Lock acquisition and OPFS mutation.','Remove timeoutMs:0 or use a bounded timeout.','Query locks before retrying.']),
  BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED: Object.freeze(['Reject before OPFS store creation.','Provide navigator.locks or a coordinator test double, or set allowUnsafeSingleOwnerFallback:true with requireWebLocks:false deliberately.','Treat fallback as a caller-scoped single-owner mode, not same-origin coordination.']),
  BRT_BROWSER_STORAGE_ADMISSION_REJECTED: Object.freeze(['Do not create the OPFS store for this product write path yet.','Free browser storage, reduce the requested reserve/write size, or relax product budget policy deliberately.','Run browserStoragePosture() again before retrying store creation.']),
  BRT_OPFS_WRITE_BUDGET_EXCEEDED: Object.freeze(['Treat the put as rejected before OPFS file mutation.','Free browser storage, lower the write size, or lower the product reserve only if that is acceptable policy.','Retry the put after a fresh StorageManager.estimate()-backed guard check.']),
  BRT_OPFS_ESTIMATE_UNAVAILABLE: Object.freeze(['Treat the guarded write as not admitted because the required quota estimate was unavailable.','Retry only when StorageManager.estimate() is available or explicitly choose a policy that allows estimate-missing writes.']),
  BRT_WEB_LOCK_TIMEOUT: Object.freeze(['Treat the operation as rejected before entering the OPFS provider callback.','Call queryLocks() or waitForSettled() on the guarded store to observe held/pending same-origin locks.','Retry with backoff after the lock settles, or surface the contended tab/worker state to the user.']),
  BRT_WEB_LOCK_ABORTED: Object.freeze(['Treat the operation as rejected before lock acquisition unless provider traces show otherwise.','Check the caller AbortSignal reason and retry only if the caller still wants the write.']),
  BRT_BROWSER_WEB_LOCKS_REQUIRED: Object.freeze(['Do not share mutable OPFS state across tabs/workers on this path without Web Locks.','Provide navigator.locks, use a coordinator test double, or explicitly opt into a single-owner fallback with requireWebLocks:false and allowUnsafeSingleOwnerFallback:true.']),
  BRT_OPFS_WEB_LOCK_GUARD_CLOSED: Object.freeze(['Treat the operation as rejected by the local guarded-store lifecycle before Web Lock acquisition or OPFS provider mutation.','Create or reopen a fresh guarded store after confirming the caller still owns the runtime lifecycle.','Do not reuse the closed guard; retry only through a new lifecycle owner and preserve the original close reason in support evidence.']),
  BRT_OPFS_QUOTA_EXCEEDED: Object.freeze(['Assume the provider attempted a write and verify the content-addressed digest before retrying.','Run rollback/staged-cleanup evidence for the affected prefix when available.','Free browser storage or reduce payload size before another put.']),
  BRT_OPFS_OPERATION_ABORTED: Object.freeze(['Treat the abort as a cooperative OPFS provider/lifecycle abort, not as proof that the Web Lock request failed before acquisition.','Verify staged cleanup, final digest state, or prefix health before retrying the affected write path.','If this came through a guarded/lane path, wait for lock and timed-out-operation settlement before clearing health or retrying.','Retry only with a fresh caller signal and explicit product/operator policy.']),
  BRT_SW_WAITUNTIL_LATE_FAILURE: Object.freeze(['Treat the Service Worker waitUntil failure as post-response lifecycle work, not as a page-visible pre-mutation rejection.','Call queryLocks() or waitForSettled() before recovering the page-side storage lane.','Verify the waitUntil-written digest/prefix state before retrying or clearing health overrides.','Do not retry automatically; require explicit caller/operator policy after settlement evidence.'])
});
const DEFAULT_RECOVERY_STEPS = Object.freeze(['Preserve the original error and trace rows for review.','Verify whether the failure happened before or after OPFS provider mutation before retrying automatically.']);
function baseStepsFor(code) {
  return RECOVERY_STEPS[code] || DEFAULT_RECOVERY_STEPS;
}
const CLASSIFIED = Object.freeze({
  BRT_BROWSER_STORAGE_GUARD_OVERRIDE_REJECTED: ['posture-guard-policy','posture-guard-override',false,false,'remove-override-or-opt-into-unsafe'],
  BRT_OPFS_WRITE_BUDGET_OVERRIDE_REJECTED: ['posture-guard-policy','write-budget-override',false,false,'remove-per-put-override-or-use-unpostured-raw-store'],
  BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED: ['posture-lock-policy','posture-web-lock-timeout-admission',false,false,'use-bounded-lock-timeout-or-opt-in'],
  BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED: ['posture-lock-policy','postured-web-lock-timeout-override',false,false,'remove-unbounded-per-op-lock-timeout'],
  BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED: ['coordination-fallback-policy','coordination-admission',false,false,'provide-web-locks-or-explicit-unsafe-single-owner-fallback'],
  BRT_BROWSER_STORAGE_ADMISSION_REJECTED: ['quota-admission','posture-admission',true,false,'refresh-posture-after-freeing-storage'],
  BRT_OPFS_WRITE_BUDGET_EXCEEDED: ['quota-budget','write-budget-preflight',true,false,'free-storage-or-reduce-write-and-retry'],
  BRT_OPFS_ESTIMATE_UNAVAILABLE: ['quota-estimate','write-budget-preflight',true,false,'retry-when-storage-estimate-is-available-or-change-policy'],
  BRT_WEB_LOCK_TIMEOUT: ['lock-contention','web-lock-acquisition',true,false,'wait-for-lock-settlement-and-retry'],
  BRT_WEB_LOCK_ABORTED: ['lock-abort','web-lock-acquisition',false,false,'respect-caller-abort-or-retry-with-new-signal'],
  BRT_BROWSER_WEB_LOCKS_REQUIRED: ['coordination-unavailable','coordination-admission',false,false,'provide-web-locks-or-explicit-unsafe-single-owner-fallback'],
  BRT_OPFS_WEB_LOCK_GUARD_CLOSED: ['guard-lifecycle-closed','guard-lifecycle',false,false,'create-fresh-guard-after-lifecycle-review'],
  BRT_OPFS_QUOTA_EXCEEDED: ['provider-quota','opfs-provider-mutation',true,true,'verify-rollback-cleanup-and-free-storage'],
  BRT_OPFS_OPERATION_ABORTED: ['provider-abort','opfs-provider-cooperative-abort',true,true,'verify-settlement-and-retry-only-with-explicit-caller-policy'],
  BRT_SW_WAITUNTIL_LATE_FAILURE: ['service-worker-lifecycle','service-worker-waituntil-post-response',true,true,'wait-for-settlement-verify-digest-and-recover-lane']
});
function classifiedRow(row) {
  return { category: row[0], phase: row[1], retryable: row[2], mutationAttempted: row[3], action: row[4] };
}
function classify(code) {
  const row = CLASSIFIED[code];
  if (row) return classifiedRow(row);
  if (code.startsWith('BRT_OPFS_')) return { category: 'opfs-provider', phase: 'opfs-provider', retryable: false, mutationAttempted: true, action: 'inspect-provider-error-and-prefix-state' };
  return { category: 'unclassified-storage', phase: 'unknown', retryable: false, mutationAttempted: null, action: 'inspect-error-and-trace' };
}
export function createBrowserStorageRecoveryGuidance(error, context = {}) {
  const detail = asObject(error?.detail) || {};
  const originalDetail = asObject(detail.originalDetail) || {};
  const metadata = asObject(detail.metadata) || asObject(originalDetail.metadata) || {};
  const merged = { ...originalDetail, ...detail, ...context };
  const code = errorCode(error);
  const row = classify(code);
  const timeoutMs = firstFinite(merged.timeoutMs, metadata.timeoutMs);
  const warningIds = uniqueStrings([stringArray(detail.warningIds), stringArray(context.warningIds)]);
  const reasons = uniqueStrings([stringArray(detail.reasons), stringArray(context.reasons), detail.reason ? [String(detail.reason)] : []]);
  const lockName = merged.lockName || merged.name || metadata.lockName || metadata.name || null;
  const op = merged.op || metadata.op || null;
  const preMutationRejected = row.mutationAttempted === false;
  const guidance = {
    project: 'BrowserRT',
    schema: 1,
    format: BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT,
    code,
    category: row.category,
    phase: row.phase,
    action: row.action,
    retryable: row.retryable,
    mutationAttempted: row.mutationAttempted,
    mutationCommitted: row.mutationAttempted === false ? false : null,
    preMutationRejected,
    shouldRetryAutomatically: row.retryable === true && preMutationRejected === true,
    shouldQueryLocks: code === 'BRT_WEB_LOCK_TIMEOUT' || code === 'BRT_WEB_LOCK_ABORTED' || code === 'BRT_SW_WAITUNTIL_LATE_FAILURE' || code === 'BRT_BROWSER_WEB_LOCK_UNBOUNDED_TIMEOUT_REJECTED' || code === 'BRT_OPFS_WEB_LOCK_TIMEOUT_OVERRIDE_REJECTED' || code === 'BRT_BROWSER_WEB_LOCK_SINGLE_OWNER_FALLBACK_REJECTED' || (code === 'BRT_OPFS_OPERATION_ABORTED' && Boolean(lockName)),
    shouldRefreshStoragePosture: ['BRT_BROWSER_STORAGE_ADMISSION_REJECTED', 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_ESTIMATE_UNAVAILABLE', 'BRT_OPFS_QUOTA_EXCEEDED'].includes(code),
    shouldVerifyDigestBeforeRetry: code === 'BRT_OPFS_QUOTA_EXCEEDED' || code === 'BRT_SW_WAITUNTIL_LATE_FAILURE' || code === 'BRT_OPFS_OPERATION_ABORTED' || (row.mutationAttempted === true && Boolean(merged.digest || merged.hash)),
    op,
    lock: Object.freeze({ name: lockName, mode: merged.mode || metadata.mode || null, timeoutMs }),
    quota: Object.freeze({
      quota: firstFinite(merged.quota),
      usage: firstFinite(merged.usage),
      freeBytes: firstFinite(merged.freeBytes, merged.freeBefore),
      projectedWritableBytes: firstFinite(merged.projectedWritableBytes),
      projectedFreeBytes: firstFinite(merged.projectedFreeBytes),
      projectedUsageRatio: Number.isFinite(Number(merged.projectedUsageRatio)) ? Number(merged.projectedUsageRatio) : null,
      requestedBytes: firstFinite(merged.requestedBytes),
      quotaKnown: merged.quotaKnown === true ? true : (merged.quotaKnown === false ? false : null),
      reasons,
      warningIds
    }),
    retryHint: Object.freeze({
      waitForSettled: code === 'BRT_WEB_LOCK_TIMEOUT' || code === 'BRT_SW_WAITUNTIL_LATE_FAILURE',
      refreshPosture: ['BRT_BROWSER_STORAGE_ADMISSION_REJECTED', 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_ESTIMATE_UNAVAILABLE', 'BRT_OPFS_QUOTA_EXCEEDED'].includes(code),
      verifyDigest: code === 'BRT_OPFS_QUOTA_EXCEEDED' || code === 'BRT_SW_WAITUNTIL_LATE_FAILURE' || code === 'BRT_OPFS_OPERATION_ABORTED',
      callerMustOptInAfterAbort: code === 'BRT_WEB_LOCK_ABORTED' || code === 'BRT_OPFS_OPERATION_ABORTED',
      providerAbortRequiresExplicitPolicy: code === 'BRT_OPFS_OPERATION_ABORTED',
      serviceWorkerSettlementRequired: code === 'BRT_SW_WAITUNTIL_LATE_FAILURE'
    }),
    recoverySteps: Object.freeze(baseStepsFor(code, detail, context)),
    compactDetail: compactDetail(merged),
    error: Object.freeze({ name: errorName(error), message: errorMessage(error), code }),
    nonClaims: Object.freeze([
      'Recovery guidance is local classification of one BrowserRT storage/lock failure; it is not automatic retry, fairness, storage persistence, quota reservation, eviction survival, fsync, power-loss, or cross-browser proof.',
      'preMutationRejected means BrowserRT rejected before entering the OPFS provider mutation callback for the classified path; provider-level quota failures still require digest/prefix verification.',
      'Service Worker waitUntil late-failure guidance is post-response lifecycle classification; it requires lock-settlement and digest/prefix verification before recovery or retry.',
      'OPFS provider abort guidance preserves the post-acquisition provider boundary; it must not be treated as a Web Lock acquisition abort or as proof that no storage mutation was attempted.'
    ])
  };
  return Object.freeze(guidance);
}
export function attachBrowserStorageRecoveryGuidance(error, context = {}) {
  const guidance = createBrowserStorageRecoveryGuidance(error, context);
  if (error && (typeof error === 'object' || typeof error === 'function')) {
    try { error.browserStorageRecovery = guidance; } catch {}
    const detail = asObject(error.detail);
    if (detail && detail.recovery !== guidance) {
      try { error.detail = { ...detail, recovery: guidance, preMutationRejected: guidance.preMutationRejected }; } catch {}
    }
  }
  return error;
}
