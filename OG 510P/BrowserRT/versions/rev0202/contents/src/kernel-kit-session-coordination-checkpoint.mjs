export const KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT = 'browserrt-kernel-kit-session-coordination-checkpoint-v1';
export const KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS = Object.freeze([
  'No production multi-tab coordination claim.',
  'No Web Locks fairness, starvation-freedom, or scheduler ordering claim.',
  'No crash, process-kill, browser-restart, or abandoned-native-I/O recovery claim.',
  'No cross-browser, mobile, background-tab, or service-worker lifecycle claim.',
  'No stale-state immunity claim beyond the observed single-use handoff clear path.',
  'No storage durability, fsync, quota, or eviction-survival claim.'
]);
export const KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_REQUIRED_ROWS = Object.freeze([
  'same-origin-session-scope-visible',
  'exclusive-lock-contention-observed',
  'queued-lock-release-order-observed',
  'locks-drained-after-use',
  'local-handoff-cross-tab-event-observed',
  'local-handoff-single-use-clear-observed',
  'stale-handoff-read-deferred-or-null',
  'abandoned-lock-release-deferred',
  'fairness-and-crash-recovery-non-claims-visible',
  'browser-heavy-command-visible'
]);
function isObj(value) { return Boolean(value && typeof value === 'object'); }
function asArray(value) { return Array.isArray(value) ? value : []; }
function bool(value) { return value === true; }
function frozen(obj) { return Object.freeze(obj); }
function firstObj(...values) { return values.find(isObj) || null; }
function rowStatus(ok, fallback = 'deferred') { return ok ? 'observed' : fallback; }
function coordinationSource(input = {}) {
  return firstObj(
    input.sessionCoordination,
    input.sessionCoordinationCheckpoint,
    input.coordination,
    input.browserSessionCoordination,
    input.observations?.sessionCoordination,
    input.observations?.coordination,
    input.supportBundle?.sessionCoordination,
    input.supportBundle?.sessionCoordinationCheckpoint
  ) || {};
}
function proofBag(source = {}) {
  return {
    ...(isObj(source.proof) ? source.proof : {}),
    ...(isObj(source.observations?.proof) ? source.observations.proof : {}),
    ...(isObj(source.lockContention?.proof) ? source.lockContention.proof : {}),
    ...(isObj(source.handoff?.proof) ? source.handoff.proof : {})
  };
}
function commandVisible(input = {}, source = {}) {
  const commands = [
    ...asArray(input.exactCommands),
    ...asArray(input.supportBundle?.exactCommands),
    ...asArray(source.exactCommands)
  ].map(String);
  return commands.some((cmd) => cmd.includes('browser:kernel-kit-session-coordination-checkpoint-proof'))
    || String(source.commandId || source.taskId || '').includes('browser:kernel-kit-session-coordination-checkpoint-proof');
}
function nonClaimText(input = {}, source = {}) {
  return [
    ...asArray(input.nonClaims),
    ...asArray(input.supportBundle?.nonClaims),
    ...asArray(source.nonClaims),
    ...KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS
  ].join('\n').toLowerCase();
}
function makeRow({ id, title, risk, status, evidence = {}, evidencePaths = [], whyItMatters, nextAction, nonClaim }) {
  return frozen({
    id,
    title,
    risk,
    status,
    evidencePaths: Object.freeze(evidencePaths),
    evidence: frozen(evidence),
    whyItMatters,
    nextAction,
    nonClaim
  });
}
function summarizeCoordination(input = {}) {
  const source = coordinationSource(input);
  const proof = proofBag(source);
  const nonClaims = nonClaimText(input, source);
  const lock = source.lockContention || source.locks || source;
  const handoff = source.handoff || source.localHandoff || source;
  const exactCommandVisible = commandVisible(input, source);
  const sameOriginSessionScopeVisible = bool(proof.sameOriginSessionScopeVisible)
    || bool(proof.sameOriginPages)
    || bool(source.sameOriginPages)
    || lock.sameOrigin === true
    || (typeof source.origin === 'string' && source.origin.startsWith('http://127.0.0.1'));
  const navigatorLocksSeen = bool(proof.navigatorLocksSeen) || lock.navigatorLocksSeen === true || source.navigatorLocksSeen === true;
  const exclusiveIfAvailableDenied = bool(proof.exclusiveIfAvailableDenied) || lock.ifAvailableDenied === true || lock.ifAvailable?.acquired === false;
  const queuedWaitedUntilRelease = bool(proof.queuedWaitedUntilRelease) || lock.queuedWaitedUntilRelease === true || lock.queue?.waitedUntilRelease === true;
  const queuedAcquiredAfterRelease = bool(proof.queuedAcquiredAfterRelease) || lock.queuedAcquiredAfterRelease === true || lock.queue?.acquiredAfterRelease === true;
  const locksDrainedAfterUse = bool(proof.locksDrainedAfterUse) || lock.drainedAfterUse === true || lock.queryAfter?.drained === true;
  const crossTabStorageEventObserved = bool(proof.crossTabStorageEventObserved) || handoff.crossTabStorageEventObserved === true || handoff.storageEvent?.observed === true;
  const handoffSingleUseClearObserved = bool(proof.handoffSingleUseClearObserved) || handoff.singleUseClearObserved === true || handoff.consumedOnce === true;
  const staleReadReturnedNull = bool(proof.staleReadReturnedNull) || handoff.staleReadReturnedNull === true || handoff.afterConsume?.value === null;
  const noFairnessClaim = proof.noFairnessClaim !== false && nonClaims.includes('fairness');
  const noCrashRecoveryClaim = proof.noCrashRecoveryClaim !== false && (nonClaims.includes('crash') || nonClaims.includes('process-kill'));
  const browserHeavyExplicit = bool(proof.browserHeavyExplicit)
    || exactCommandVisible
    || String(source.tier || source.source || source.probe_id || '').includes('browser')
    || String(source.taskId || '').includes('browser:');
  const observed = source.status === 'passed'
    && sameOriginSessionScopeVisible
    && navigatorLocksSeen
    && exclusiveIfAvailableDenied
    && queuedWaitedUntilRelease
    && queuedAcquiredAfterRelease
    && locksDrainedAfterUse
    && crossTabStorageEventObserved
    && handoffSingleUseClearObserved
    && staleReadReturnedNull
    && noFairnessClaim
    && noCrashRecoveryClaim;
  return frozen({
    observed,
    status: observed ? 'observed' : (source.status || 'browser-heavy-deferred'),
    source: source.source || source.probe_id || 'browser-heavy-session-coordination-command-not-run',
    commandId: source.commandId || 'browser:kernel-kit-session-coordination-checkpoint-proof',
    tier: source.tier || 'browser-heavy-explicit',
    sameOriginSessionScopeVisible,
    navigatorLocksSeen,
    exclusiveIfAvailableDenied,
    queuedWaitedUntilRelease,
    queuedAcquiredAfterRelease,
    locksDrainedAfterUse,
    crossTabStorageEventObserved,
    handoffSingleUseClearObserved,
    staleReadReturnedNull,
    abandonedLockReleaseDeferred: proof.abandonedLockReleaseClaimed !== true,
    exactCommandVisible,
    browserHeavyExplicit,
    noFairnessClaim,
    noCrashRecoveryClaim
  });
}
export function createKernelKitSessionCoordinationCheckpoint(input = {}, fields = {}) {
  const summary = summarizeCoordination(input);
  const revision = fields.revision || input.revision || input.supportBundle?.revision || 'rev0108';
  const rows = [
    makeRow({
      id: 'same-origin-session-scope-visible',
      title: 'Same-origin session scope is visible',
      risk: 4,
      status: rowStatus(summary.sameOriginSessionScopeVisible),
      evidencePaths: ['sessionCoordination.origin', 'sessionCoordination.proof.sameOriginPages'],
      evidence: { sameOriginSessionScopeVisible: summary.sameOriginSessionScopeVisible, source: summary.source },
      whyItMatters: 'Web Locks and localStorage coordination are origin-scoped; a multi-tab proof is misleading if the origin boundary is invisible.',
      nextAction: summary.sameOriginSessionScopeVisible ? 'Keep same-origin scope explicit in browser-heavy artifacts.' : 'Run the browser session-coordination proof before claiming tab-to-tab behavior.',
      nonClaim: 'Same-origin scope visibility is not cross-origin, cross-browser, or production lifecycle coverage.'
    }),
    makeRow({
      id: 'exclusive-lock-contention-observed',
      title: 'Exclusive Web Lock contention is observed or explicitly deferred',
      risk: 5,
      status: rowStatus(summary.exclusiveIfAvailableDenied),
      evidencePaths: ['sessionCoordination.lockContention.ifAvailable.acquired=false', 'proof.exclusiveIfAvailableDenied'],
      evidence: { navigatorLocksSeen: summary.navigatorLocksSeen, exclusiveIfAvailableDenied: summary.exclusiveIfAvailableDenied },
      whyItMatters: 'A single-page lock smoke can miss the riskiest session failure: another same-origin tab mutating while work is in flight.',
      nextAction: summary.exclusiveIfAvailableDenied ? 'Keep contention proof browser-heavy and same-origin scoped.' : 'Run browser:kernel-kit-session-coordination-checkpoint-proof; keep support bundle default deferred.',
      nonClaim: 'Exclusive contention evidence is not Web Locks fairness, starvation-freedom, or production multi-tab coordination.'
    }),
    makeRow({
      id: 'queued-lock-release-order-observed',
      title: 'Queued lock request waits until release',
      risk: 5,
      status: rowStatus(summary.queuedWaitedUntilRelease && summary.queuedAcquiredAfterRelease),
      evidencePaths: ['sessionCoordination.lockContention.queue.waitedUntilRelease', 'sessionCoordination.lockContention.queue.acquiredAfterRelease'],
      evidence: { queuedWaitedUntilRelease: summary.queuedWaitedUntilRelease, queuedAcquiredAfterRelease: summary.queuedAcquiredAfterRelease },
      whyItMatters: 'Queued request behavior is the smallest useful proxy for tab-to-tab backpressure; it prevents mistaking ifAvailable denial for ordered recovery.',
      nextAction: summary.queuedWaitedUntilRelease && summary.queuedAcquiredAfterRelease ? 'Preserve queue-before-release and acquire-after-release booleans in compact artifacts.' : 'Add or rerun the browser-heavy queued contention path.',
      nonClaim: 'Queue-order observation is not a fairness guarantee and does not prove starvation-freedom.'
    }),
    makeRow({
      id: 'locks-drained-after-use',
      title: 'Lock state is drained after the proof',
      risk: 4,
      status: rowStatus(summary.locksDrainedAfterUse),
      evidencePaths: ['sessionCoordination.lockContention.queryAfter.drained', 'proof.locksDrainedAfterUse'],
      evidence: { locksDrainedAfterUse: summary.locksDrainedAfterUse },
      whyItMatters: 'A browser-heavy lock proof that leaks held/pending locks poisons later browser work in the same profile.',
      nextAction: summary.locksDrainedAfterUse ? 'Keep post-proof lock query in browser artifacts.' : 'Add a final Web Locks query and drain assertion.',
      nonClaim: 'Drained lock state after a managed proof is not crash recovery for arbitrary abandoned native work.'
    }),
    makeRow({
      id: 'local-handoff-cross-tab-event-observed',
      title: 'Local handoff cross-tab storage event is observed or deferred',
      risk: 4,
      status: rowStatus(summary.crossTabStorageEventObserved),
      evidencePaths: ['sessionCoordination.handoff.storageEvent.observed', 'proof.crossTabStorageEventObserved'],
      evidence: { crossTabStorageEventObserved: summary.crossTabStorageEventObserved },
      whyItMatters: 'The Kernel Kit uses local handoff state; future sessions need proof that same-origin tabs can see consumption rather than holding stale assumptions.',
      nextAction: summary.crossTabStorageEventObserved ? 'Keep storage-event evidence compact; do not elevate it to background-tab lifecycle coverage.' : 'Observe same-origin localStorage clear event in the browser-heavy proof.',
      nonClaim: 'A storage event is not a durable, background, service-worker, or cross-browser lifecycle guarantee.'
    }),
    makeRow({
      id: 'local-handoff-single-use-clear-observed',
      title: 'Local handoff is single-use cleared or explicitly deferred',
      risk: 5,
      status: rowStatus(summary.handoffSingleUseClearObserved),
      evidencePaths: ['sessionCoordination.handoff.singleUseClearObserved', 'proof.handoffSingleUseClearObserved'],
      evidence: { handoffSingleUseClearObserved: summary.handoffSingleUseClearObserved },
      whyItMatters: 'Uncleared handoff state is a practical stale-state trap: later sessions can replay old local prefixes or digests by accident.',
      nextAction: summary.handoffSingleUseClearObserved ? 'Keep single-use clear as a support-bundle checkpoint row.' : 'Run the browser proof and reject support bundles that hide handoff cleanup state.',
      nonClaim: 'Single-use clear does not prove stale-state immunity across crashes, multiple profiles, or arbitrary app-level caches.'
    }),
    makeRow({
      id: 'stale-handoff-read-deferred-or-null',
      title: 'Stale handoff read returns null or stays deferred',
      risk: 5,
      status: rowStatus(summary.staleReadReturnedNull),
      evidencePaths: ['sessionCoordination.handoff.afterConsume.value=null', 'proof.staleReadReturnedNull'],
      evidence: { staleReadReturnedNull: summary.staleReadReturnedNull },
      whyItMatters: 'A consumed handoff that still reads as present is exactly the kind of subtle local-state bug that contaminates future proof sessions.',
      nextAction: summary.staleReadReturnedNull ? 'Keep stale-read-null assertion in the cross-tab proof.' : 'Prove consumed local handoff is absent before adding broader recovery language.',
      nonClaim: 'Null stale-read evidence is not a general stale-state immunity or persistence-retention guarantee.'
    }),
    makeRow({
      id: 'abandoned-lock-release-deferred',
      title: 'Abandoned lock release is still deferred, not implied',
      risk: 5,
      status: 'deferred',
      evidencePaths: ['nonClaims', 'proof.abandonedLockReleaseClaimed=false'],
      evidence: { abandonedLockReleaseDeferred: summary.abandonedLockReleaseDeferred },
      whyItMatters: 'Killing a tab or renderer while native/browser I/O is pending is a different risk than orderly lock release.',
      nextAction: 'Add a separate browser-heavy page-close/process-kill lock cleanup probe before making abandoned-lock recovery claims.',
      nonClaim: 'No crash, process-kill, browser-restart, or abandoned-native-I/O recovery claim.'
    }),
    makeRow({
      id: 'fairness-and-crash-recovery-non-claims-visible',
      title: 'Fairness and crash-recovery non-claims are visible',
      risk: 4,
      status: rowStatus(summary.noFairnessClaim && summary.noCrashRecoveryClaim),
      evidencePaths: ['nonClaims'],
      evidence: { noFairnessClaim: summary.noFairnessClaim, noCrashRecoveryClaim: summary.noCrashRecoveryClaim },
      whyItMatters: 'Coordination proof is dangerous if reviewers silently promote it into fairness or crash-recovery language.',
      nextAction: summary.noFairnessClaim && summary.noCrashRecoveryClaim ? 'Preserve non-claims in support bundle, lifecycle checkpoint, and browser artifact.' : 'Restore explicit fairness and crash-recovery non-claims.',
      nonClaim: 'No Web Locks fairness, starvation-freedom, crash recovery, or production coordination claim.'
    }),
    makeRow({
      id: 'browser-heavy-command-visible',
      title: 'Browser-heavy session coordination command is visible',
      risk: 4,
      status: rowStatus(summary.exactCommandVisible || summary.browserHeavyExplicit),
      evidencePaths: ['supportBundle.exactCommands', 'sessionCoordination.commandId'],
      evidence: { exactCommandVisible: summary.exactCommandVisible, commandId: summary.commandId, tier: summary.tier },
      whyItMatters: 'This proof spends browser/CDP budget and should be run intentionally, not hidden inside broad browser-light packaging.',
      nextAction: 'Keep the command explicit in support bundles and evidence ledgers.',
      nonClaim: 'Command visibility is not evidence that the browser-heavy proof has been run in every packaged session.'
    })
  ].sort((a, b) => (b.risk - a.risk) || a.id.localeCompare(b.id));
  const missingRequiredRows = KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_REQUIRED_ROWS.filter((id) => !rows.some((row) => row.id === id));
  const failedRows = rows.filter((row) => row.status === 'failed').map((row) => row.id);
  const deferredRows = rows.filter((row) => row.status === 'deferred').map((row) => row.id);
  const observedRows = rows.filter((row) => row.status === 'observed').map((row) => row.id);
  const highRiskRowsBounded = rows.filter((row) => row.risk >= 5).every((row) => ['observed', 'deferred'].includes(row.status) && row.nextAction && row.nonClaim);
  const proof = frozen({
    sameOriginSessionScopeVisibleOrDeferred: summary.sameOriginSessionScopeVisible || deferredRows.includes('same-origin-session-scope-visible'),
    exclusiveLockContentionObservedOrDeferred: summary.exclusiveIfAvailableDenied || deferredRows.includes('exclusive-lock-contention-observed'),
    queuedLockReleaseOrderObservedOrDeferred: (summary.queuedWaitedUntilRelease && summary.queuedAcquiredAfterRelease) || deferredRows.includes('queued-lock-release-order-observed'),
    locksDrainedObservedOrDeferred: summary.locksDrainedAfterUse || deferredRows.includes('locks-drained-after-use'),
    localHandoffSingleUseClearObservedOrDeferred: summary.handoffSingleUseClearObserved || deferredRows.includes('local-handoff-single-use-clear-observed'),
    staleHandoffReadNullObservedOrDeferred: summary.staleReadReturnedNull || deferredRows.includes('stale-handoff-read-deferred-or-null'),
    abandonedLockReleaseDeferred: deferredRows.includes('abandoned-lock-release-deferred'),
    highRiskRowsBounded,
    nonClaimsVisible: summary.noFairnessClaim && summary.noCrashRecoveryClaim,
    browserHeavyCommandVisible: summary.exactCommandVisible || summary.browserHeavyExplicit,
    noFailedRows: failedRows.length === 0,
    requiredRowsPresent: missingRequiredRows.length === 0
  });
  const status = Object.values(proof).every((value) => value === true) ? 'risk-checkpoint-ready' : 'needs-attention';
  return frozen({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT,
    checkpointId: fields.checkpointId || `${revision}-kernel-kit-session-coordination-checkpoint`,
    generatedAt: fields.generatedAt || 'deterministic-kernel-kit-session-coordination-checkpoint',
    status,
    posture: 'session-coordination-risk-checkpoint-not-production-coordination',
    purpose: 'Make same-origin multi-tab Web Locks contention and local handoff stale-state cleanup visible as executable risk rows while preserving fairness/crash/cross-browser non-claims.',
    source: fields.source || summary.source,
    summary,
    rows: Object.freeze(rows),
    observedRowIds: Object.freeze(observedRows),
    deferredRowIds: Object.freeze(deferredRows),
    failedRowIds: Object.freeze(failedRows),
    missingRequiredRows: Object.freeze(missingRequiredRows),
    riskSummary: frozen({
      rowCount: rows.length,
      observedCount: observedRows.length,
      deferredCount: deferredRows.length,
      failedCount: failedRows.length,
      riskiestNextAction: rows.find((row) => row.status === 'deferred' && row.risk >= 5)?.nextAction || 'Keep session coordination rows tied to browser-heavy evidence.'
    }),
    proof,
    nonClaims: Object.freeze([...KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS])
  });
}
export function validateKernelKitSessionCoordinationCheckpoint(checkpoint = {}) {
  const errors = [];
  if (!isObj(checkpoint)) return frozen({ ok: false, errors: ['session coordination checkpoint must be an object'], rowCount: 0, observedCount: 0, deferredCount: 0, failedCount: 0, format: null, status: null });
  if (checkpoint.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (checkpoint.format !== KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT) errors.push(`format must be ${KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT}`);
  if (checkpoint.status !== 'risk-checkpoint-ready') errors.push('status must be risk-checkpoint-ready');
  const rows = asArray(checkpoint.rows);
  for (const id of KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_REQUIRED_ROWS) if (!rows.some((row) => row.id === id)) errors.push(`missing session coordination row ${id}`);
  for (const row of rows) {
    if (!['observed', 'deferred'].includes(row.status)) errors.push(`row ${row.id || 'unknown'} must be observed or deferred`);
    if (!Number.isFinite(row.risk) || row.risk < 1 || row.risk > 5) errors.push(`row ${row.id || 'unknown'} risk must be 1..5`);
    if (!row.nextAction) errors.push(`row ${row.id || 'unknown'} missing nextAction`);
    if (!row.nonClaim) errors.push(`row ${row.id || 'unknown'} missing nonClaim`);
  }
  if ((checkpoint.failedRowIds || []).length) errors.push('failedRowIds must be empty');
  if ((checkpoint.missingRequiredRows || []).length) errors.push('missingRequiredRows must be empty');
  for (const key of ['sameOriginSessionScopeVisibleOrDeferred', 'exclusiveLockContentionObservedOrDeferred', 'queuedLockReleaseOrderObservedOrDeferred', 'locksDrainedObservedOrDeferred', 'localHandoffSingleUseClearObservedOrDeferred', 'staleHandoffReadNullObservedOrDeferred', 'abandonedLockReleaseDeferred', 'highRiskRowsBounded', 'nonClaimsVisible', 'browserHeavyCommandVisible', 'noFailedRows', 'requiredRowsPresent']) {
    if (checkpoint.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const claim of KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS) {
    if (!checkpoint.nonClaims?.includes(claim)) errors.push(`missing session coordination non-claim: ${claim}`);
  }
  return frozen({
    ok: errors.length === 0,
    errors,
    rowCount: rows.length,
    observedCount: checkpoint.observedRowIds?.length || 0,
    deferredCount: checkpoint.deferredRowIds?.length || 0,
    failedCount: checkpoint.failedRowIds?.length || 0,
    format: checkpoint.format || null,
    status: checkpoint.status || null
  });
}
