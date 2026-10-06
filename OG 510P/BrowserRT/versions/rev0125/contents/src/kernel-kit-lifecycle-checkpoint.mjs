// BrowserRT Kernel Kit lifecycle checkpoint.
// This module deliberately turns scattered OPFS/Web Locks/storage/reload proof
// booleans into one bounded risk checkpoint. It is not a production readiness,
// durability, quota, eviction, side-channel, or cross-browser claim.

export const KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT = 'browserrt-kernel-kit-lifecycle-checkpoint-v1';

export const KERNEL_KIT_LIFECYCLE_CHECKPOINT_NON_CLAIMS = Object.freeze([
  'No production lifecycle-readiness claim.',
  'No OPFS durability, fsync, quota reservation, eviction-survival, or crash-recovery claim.',
  'No cross-browser, mobile lifecycle, or background-survival claim.',
  'No Web Locks fairness or production multi-tab coordination claim.',
  'No browser side-channel, anti-fingerprinting, or privacy-hardening claim.',
  'No artifact authenticity, signing, or tamper-proof evidence claim.'
]);

export const KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS = Object.freeze([
  'product-storage-path-evidence',
  'opfs-abort-non-mutation-boundary',
  'storage-manager-posture',
  'persistent-storage-not-assumed',
  'web-locks-coordination-posture',
  'guarded-storage-lane-path',
  'reload-readback-evidence',
  'quota-pressure-backpressure-evidence',
  'admission-cancellation-backpressure-evidence',
  'session-coordination-stale-handoff-evidence',
  'recovery-interruption-boundary-evidence',
  'recovery-orphan-review-gate-evidence',
  'quota-eviction-survival-deferred',
  'cross-browser-mobile-lifecycle-deferred',
  'side-channel-privacy-deferred',
  'support-bundle-replay-evidence'
]);

function isObj(value) { return Boolean(value && typeof value === 'object'); }
function bool(value) { return value === true; }
function asArray(value) { return Array.isArray(value) ? value : []; }
function pathList(...paths) { return Object.freeze(paths.filter(Boolean)); }
function frozen(obj) { return Object.freeze(obj); }

function proofBag(report = {}) {
  return {
    ...(isObj(report.observations) ? report.observations : {}),
    ...(isObj(report.proof) ? report.proof : {}),
    ...(isObj(report.success?.proof) ? report.success.proof : {}),
    ...(isObj(report.reload?.proof) ? report.reload.proof : {}),
    ...(isObj(report.supportBundle?.proof) ? report.supportBundle.proof : {}),
    ...(isObj(report.supportBundleProof) ? report.supportBundleProof : {})
  };
}

function firstObj(...values) { return values.find(isObj) || null; }
function rowStatus(ok, fallback = 'deferred') { return ok ? 'observed' : fallback; }

function storagePostureSummary(input = {}) {
  const posture = firstObj(input.storagePosture, input.storagePosture?.success, input.storagePosture?.reload, input.success?.storagePosture, input.reload?.storagePosture, input.observations?.work?.storagePosture);
  if (!posture) return frozen({ observed: false, estimateChecked: false, quotaKnown: false, usageKnown: false, persistedChecked: false, persistentStorageRequested: false, persistenceNotRequestedByDefault: false, status: 'not-observed', source: 'not-supplied' });
  const proof = posture.proof || posture;
  const persistRequest = posture.persistRequest || {};
  const estimate = posture.estimate || posture;
  return frozen({
    observed: bool(proof.estimateChecked) || posture.status === 'observed',
    estimateChecked: bool(proof.estimateChecked),
    quotaKnown: bool(proof.quotaKnown) || Number.isFinite(estimate.quota),
    usageKnown: bool(proof.usageKnown) || Number.isFinite(estimate.usage),
    persistedChecked: bool(proof.persistedChecked),
    persistentStorageRequested: bool(posture.persistentStorageRequested) || bool(persistRequest.requested),
    persistenceNotRequestedByDefault: bool(proof.persistenceNotRequestedByDefault) || posture.persistentStorageRequested === false || persistRequest.requested === false,
    persisted: posture.persisted?.persisted ?? posture.persisted ?? null,
    usage: Number.isFinite(estimate.usage) ? estimate.usage : null,
    quota: Number.isFinite(estimate.quota) ? estimate.quota : null,
    status: posture.status || (bool(proof.estimateChecked) ? 'observed' : 'partial'),
    source: posture.source || posture.runner || posture.label || 'kernel-kit-storage-posture'
  });
}

function webLockPostureSummary(input = {}) {
  const posture = firstObj(input.webLockPosture, input.webLockPosture?.success, input.webLockPosture?.reload, input.success?.webLockPosture, input.reload?.webLockPosture, input.observations?.work?.webLockPosture);
  if (!posture) return frozen({ observed: false, navigatorLocksSeen: false, exclusiveNoOverlap: false, sharedCoHold: false, drainedAfterUse: false, noFairnessClaim: true, status: 'not-observed', source: 'not-supplied' });
  const proof = posture.proof || posture;
  return frozen({
    observed: bool(proof.exclusiveNoOverlap) && bool(proof.sharedCoHold) && bool(proof.drainedAfterUse),
    navigatorLocksSeen: bool(proof.navigatorLocksSeen) || bool(posture.navigatorLocksSeen),
    exclusiveNoOverlap: bool(proof.exclusiveNoOverlap),
    sharedCoHold: bool(proof.sharedCoHold),
    drainedAfterUse: bool(proof.drainedAfterUse),
    queryObserved: bool(proof.queryObserved),
    noFairnessClaim: proof.noFairnessClaim !== false,
    status: posture.status || (bool(proof.exclusiveNoOverlap) ? 'observed' : 'partial'),
    source: posture.source || posture.runner || posture.label || 'kernel-kit-web-lock-posture'
  });
}

function guardedStorageSummary(input = {}) {
  const guarded = firstObj(input.guardedStorageLane, input.guardedStorageLane?.success, input.guardedStorageLane?.reload, input.guardedStorage, input.storage?.guarded, input.success?.guardedStorageLane, input.reload?.guardedStorageLane, input.observations?.work?.guardedStorage);
  if (!guarded) return frozen({ observed: false, guardedProvider: false, webLocksAvailable: false, lockAcquiredReleased: false, noFairnessClaim: true, status: 'not-observed', source: 'not-supplied' });
  const proof = guarded.proof || guarded;
  return frozen({
    observed: bool(proof.guardedProvider) && bool(proof.lockAcquiredReleased),
    guardedProvider: bool(proof.guardedProvider),
    webLocksAvailable: bool(proof.webLocksAvailable) || bool(guarded.webLocksAvailable) || bool(guarded.available),
    exclusiveMutationsObserved: bool(proof.exclusiveMutationsObserved),
    sharedReadsObserved: bool(proof.sharedReadsObserved),
    lockAcquiredReleased: bool(proof.lockAcquiredReleased),
    noFairnessClaim: proof.noFairnessClaim !== false,
    status: guarded.status || (bool(proof.guardedProvider) ? 'observed' : 'partial'),
    provider: guarded.provider || null,
    source: guarded.source || 'kernel-kit-guarded-storage-lane'
  });
}


function storagePressureSummary(input = {}) {
  const pressure = firstObj(input.storagePressure, input.quotaPressure, input.quotaBackpressure, input.browserQuotaPressure, input.supportBundle?.storagePressure, input.observations?.storagePressure, input.observations?.quotaPressure);
  if (!pressure) return frozen({ observed: false, status: 'browser-heavy-deferred', browserHeavyExplicit: true, quotaOverrideActivated: false, quotaExceededClassified: false, failedPutRolledBack: false, followOnWritesRejectWithoutMutation: false, cleanupVerified: false, recoveryWriteObserved: false, quotaOverrideReset: false, evictionSurvivalDeferred: true, source: 'browser-heavy-quota-pressure-command-not-run' });
  const proof = pressure.proof || pressure;
  const observations = pressure.observations || {};
  const lane = observations.lane || pressure.lane || {};
  const writes = observations.writes || pressure.writes || {};
  const cleanup = observations.cleanup || pressure.cleanup || {};
  const quotaOverride = observations.quotaOverride || pressure.quotaOverride || {};
  const quotaReset = observations.quotaReset || pressure.quotaReset || {};
  const failure = lane.failure || writes.failure || pressure.failure || {};
  const failureText = `${failure.stage || ''} ${failure.name || ''} ${failure.message || ''} ${failure.code || ''} ${failure.row?.error?.code || ''} ${failure.row?.error?.storageDisposition || ''}`;
  const nonClaims = [...asArray(pressure.nonClaims), ...asArray(input.nonClaims), ...asArray(input.supportBundle?.nonClaims)].join('\n').toLowerCase();
  const browserHeavyExplicit = bool(proof.browserHeavyExplicit) || String(pressure.tier || pressure.source || pressure.probe_id || '').includes('browser') || String(pressure.probe_id || '').includes('quota');
  const quotaOverrideActivated = bool(proof.quotaOverrideActivated) || quotaOverride.after?.overrideActive === true || observations.quotaOverride?.after?.overrideActive === true;
  const quotaExceededClassified = bool(proof.quotaExceededClassified) || /quota|exceed|BRT_OPFS_QUOTA_EXCEEDED/i.test(failureText);
  const failedPutRolledBack = bool(proof.failedPutRolledBack) || lane.failure?.failedHashAbsentAfterRollback === true || failure.failedHashAbsentAfterRollback === true || lane.failure?.row?.error?.providerDetail?.rollback?.attempted === true;
  const followOnWritesRejectWithoutMutation = bool(proof.followOnWritesRejectWithoutMutation) || lane.postQuotaReject?.scheduler?.noMutation === true || lane.postQuotaReject?.accepted === false;
  const cleanupVerified = bool(proof.cleanupVerified) || bool(proof.maintenanceCleanupObserved) || lane.maintenanceResults?.cleanup === true || cleanup.checks?.every?.((row) => row.deleted === true && row.hasAfter === false) === true;
  const recoveryWriteObserved = bool(proof.recoveryWriteObserved) || lane.recoveredWrite?.accepted === true || lane.recoveredResult?.duplicate === false;
  const quotaOverrideReset = bool(proof.quotaOverrideReset) || quotaReset.after?.overrideActive === false || pressure.quotaReset?.after?.overrideActive === false;
  const evictionSurvivalDeferred = proof.evictionSurvivalClaimed !== true && (!nonClaims || nonClaims.includes('eviction') || nonClaims.includes('organic'));
  const observed = pressure.status === 'passed' && browserHeavyExplicit && quotaOverrideActivated && quotaExceededClassified && cleanupVerified && quotaOverrideReset && evictionSurvivalDeferred;
  return frozen({
    observed,
    status: observed ? 'observed' : (pressure.status || 'browser-heavy-deferred'),
    browserHeavyExplicit,
    quotaOverrideActivated,
    quotaExceededClassified,
    failedPutRolledBack,
    followOnWritesRejectWithoutMutation,
    cleanupVerified,
    recoveryWriteObserved,
    quotaOverrideReset,
    evictionSurvivalDeferred,
    probeId: pressure.probe_id || pressure.proofId || null,
    source: pressure.source || pressure.probe_id || 'kernel-kit-storage-pressure-checkpoint'
  });
}

function nonClaimsVisible(input = {}) {
  const values = [
    ...asArray(input.nonClaims),
    ...asArray(input.supportBundle?.nonClaims),
    ...asArray(input.success?.nonClaims),
    ...asArray(input.reload?.nonClaims)
  ].join('\n').toLowerCase();
  return ['production', 'quota', 'eviction', 'cross-browser'].every((needle) => values.includes(needle));
}

function makeRow({ id, title, risk, status, evidencePaths, evidence, nextAction, whyItMatters, nonClaim, owner = 'kernel-kit-product-path' }) {
  return frozen({
    id,
    title,
    risk,
    status,
    owner,
    evidencePaths: pathList(...(evidencePaths || [])),
    evidence: frozen(evidence || {}),
    whyItMatters,
    nextAction,
    nonClaim
  });
}



function admissionCancellationSummary(input = {}) {
  const admission = firstObj(input.admissionCancellation, input.admissionCancellationCheckpoint, input.admissionAbortRelease, input.supportBundle?.admissionCancellation, input.observations?.admissionCancellation);
  if (!admission) return frozen({ observed: false, status: 'release-light-deferred', commandId: 'admission:abort-release-proof', exactCommandVisible: false, preAbortedRejectedNoMutation: false, boundLeaseAbortReleasedPermit: false, dualSignalAbortSourceReleasesOnce: false, manualReleaseDetachesAbortListener: false, congestionRecoversAfterAbortRelease: false, postAbortBackgroundAdmissionRecovers: false, invalidSignalShapeRejectedLocally: false, exactlyOnceNonClaimVisible: true, browserWorkerNonClaimVisible: true, source: 'release-light-admission-cancellation-command-not-run' });
  const proof = admission.proof || {};
  const summary = admission.summary || admission;
  const rows = Array.isArray(admission.rows) ? admission.rows : [];
  const observedRows = new Set([...(admission.observedRowIds || []), ...rows.filter((row) => row.status === 'observed').map((row) => row.id)]);
  const deferredRows = new Set([...(admission.deferredRowIds || []), ...rows.filter((row) => row.status === 'deferred').map((row) => row.id)]);
  const preAbortedRejectedNoMutation = bool(proof.preAbortedRejectedNoMutation) || bool(summary.preAbortedRejectedNoMutation) || observedRows.has('pre-aborted-admission-rejects-no-mutation');
  const boundLeaseAbortReleasedPermit = bool(proof.boundLeaseAbortReleasedPermit) || bool(summary.boundLeaseAbortReleasedPermit) || observedRows.has('bound-lease-abort-releases-permit');
  const dualSignalAbortSourceReleasesOnce = bool(proof.dualSignalAbortSourceReleasesOnce) || bool(summary.dualSignalAbortSourceReleasesOnce) || observedRows.has('dual-signal-abort-source-releases-once');
  const manualReleaseDetachesAbortListener = bool(proof.manualReleaseDetachesAbortListener) || bool(summary.manualReleaseDetachesAbortListener) || observedRows.has('manual-release-detaches-abort-listener');
  const congestionRecoversAfterAbortRelease = bool(proof.congestionRecoversAfterAbortRelease) || bool(summary.congestionRecoversAfterAbortRelease) || observedRows.has('congestion-recovers-after-abort-release');
  const postAbortBackgroundAdmissionRecovers = bool(proof.postAbortBackgroundAdmissionRecovers) || bool(summary.postAbortBackgroundAdmissionRecovers) || observedRows.has('post-abort-background-admission-recovers');
  const invalidSignalShapeRejectedLocally = bool(proof.invalidSignalShapeRejectedLocally) || bool(summary.invalidSignalShapeRejectedLocally) || observedRows.has('invalid-signal-shape-rejected-locally');
  const exactCommandVisible = bool(proof.releaseLightCommandVisible) || String(admission.commandId || summary.commandId || '').includes('admission:abort-release-proof');
  const observed = admission.status === 'risk-checkpoint-ready' && preAbortedRejectedNoMutation && boundLeaseAbortReleasedPermit && dualSignalAbortSourceReleasesOnce && manualReleaseDetachesAbortListener && congestionRecoversAfterAbortRelease && postAbortBackgroundAdmissionRecovers && invalidSignalShapeRejectedLocally;
  return frozen({
    observed,
    status: observed ? 'observed' : (admission.status || summary.status || 'release-light-deferred'),
    commandId: admission.commandId || summary.commandId || 'admission:abort-release-proof',
    exactCommandVisible,
    preAbortedRejectedNoMutation,
    boundLeaseAbortReleasedPermit,
    dualSignalAbortSourceReleasesOnce,
    manualReleaseDetachesAbortListener,
    congestionRecoversAfterAbortRelease,
    postAbortBackgroundAdmissionRecovers,
    invalidSignalShapeRejectedLocally,
    exactlyOnceNonClaimVisible: proof.exactlyOnceNonClaimVisible !== false,
    browserWorkerNonClaimVisible: proof.browserWorkerNonClaimVisible !== false,
    deferredRowIds: Array.from(deferredRows),
    observedRowIds: Array.from(observedRows),
    source: admission.source || summary.source || 'kernel-kit-admission-cancellation-checkpoint'
  });
}

function sessionCoordinationSummary(input = {}) {
  const coordination = firstObj(input.sessionCoordination, input.sessionCoordinationCheckpoint, input.supportBundle?.sessionCoordination, input.supportBundle?.sessionCoordinationCheckpoint, input.observations?.sessionCoordination);
  if (!coordination) return frozen({ observed: false, status: 'browser-heavy-deferred', commandId: 'browser:kernel-kit-session-coordination-checkpoint-proof', exactCommandVisible: false, localHandoffSingleUseClearObserved: false, staleReadReturnedNull: false, exclusiveLockContentionObserved: false, queuedLockReleaseOrderObserved: false, abandonedLockReleaseDeferred: true, source: 'browser-heavy-session-coordination-command-not-run' });
  const proof = coordination.proof || {};
  const summary = coordination.summary || coordination;
  const rows = Array.isArray(coordination.rows) ? coordination.rows : [];
  const observedRows = new Set([...(coordination.observedRowIds || []), ...rows.filter((row) => row.status === 'observed').map((row) => row.id)]);
  const deferredRows = new Set([...(coordination.deferredRowIds || []), ...rows.filter((row) => row.status === 'deferred').map((row) => row.id)]);
  const localHandoffSingleUseClearObserved = bool(summary.handoffSingleUseClearObserved) || bool(proof.localHandoffSingleUseClearObservedOrDeferred) && observedRows.has('local-handoff-single-use-clear-observed');
  const staleReadReturnedNull = bool(summary.staleReadReturnedNull) || bool(proof.staleHandoffReadNullObservedOrDeferred) && observedRows.has('stale-handoff-read-deferred-or-null');
  const exclusiveLockContentionObserved = bool(summary.exclusiveIfAvailableDenied) || observedRows.has('exclusive-lock-contention-observed');
  const queuedLockReleaseOrderObserved = (bool(summary.queuedWaitedUntilRelease) && bool(summary.queuedAcquiredAfterRelease)) || observedRows.has('queued-lock-release-order-observed');
  const exactCommandVisible = bool(proof.browserHeavyCommandVisible) || String(coordination.commandId || '').includes('browser:kernel-kit-session-coordination-checkpoint-proof');
  const abandonedLockReleaseDeferred = bool(summary.abandonedLockReleaseDeferred) || deferredRows.has('abandoned-lock-release-deferred') || proof.abandonedLockReleaseDeferred === true;
  const observed = coordination.status === 'risk-checkpoint-ready' && localHandoffSingleUseClearObserved && staleReadReturnedNull && exclusiveLockContentionObserved && queuedLockReleaseOrderObserved;
  return frozen({
    observed,
    status: observed ? 'observed' : (coordination.status || summary.status || 'browser-heavy-deferred'),
    commandId: coordination.commandId || summary.commandId || 'browser:kernel-kit-session-coordination-checkpoint-proof',
    exactCommandVisible,
    localHandoffSingleUseClearObserved,
    staleReadReturnedNull,
    exclusiveLockContentionObserved,
    queuedLockReleaseOrderObserved,
    abandonedLockReleaseDeferred,
    deferredRowIds: Array.from(deferredRows),
    observedRowIds: Array.from(observedRows),
    source: coordination.source || summary.source || 'kernel-kit-session-coordination-checkpoint'
  });
}

function recoverySummary(input = {}) {
  const recovery = firstObj(input.recoveryCheckpoint, input.recovery, input.supportBundle?.recoveryCheckpoint, input.observations?.recovery);
  if (!recovery) return frozen({ observed: false, status: 'browser-heavy-deferred', commandId: 'browser:kernel-kit-recovery-checkpoint-proof', exactCommandVisible: false, sameOriginProfileRestartObserved: false, sigkillBoundaryObserved: false, interruptedWriteNotAcceptedCorrupt: false, transientOpenFailureRetryObserved: false, unsettledOrphanReviewGateObserved: false, crashDurabilityNonClaimsVisible: true, crossBrowserNonClaimsVisible: true, source: 'browser-heavy-recovery-command-not-run' });
  const proof = recovery.proof || {};
  const summary = recovery.summary || recovery;
  const rows = Array.isArray(recovery.rows) ? recovery.rows : [];
  const observedRows = new Set([...(recovery.observedRowIds || []), ...rows.filter((row) => row.status === 'observed').map((row) => row.id)]);
  const deferredRows = new Set([...(recovery.deferredRowIds || []), ...rows.filter((row) => row.status === 'deferred').map((row) => row.id)]);
  const sameOriginProfileRestartObserved = bool(proof.sameOriginProfileRestartObserved) || (bool(summary.sameOriginTwoLaunch) && bool(summary.profileReusedAcrossKill)) || observedRows.has('same-origin-profile-restart-boundary');
  const sigkillBoundaryObserved = bool(proof.sigkillBoundaryObserved) || bool(summary.sigkillObserved) || observedRows.has('sigkill-interruption-boundary-observed');
  const acknowledgedBlocksVerifiedAfterRestart = bool(proof.acknowledgedBlocksVerifiedAfterRestart) || bool(summary.acknowledgedBlocksVerifiedAfterRestart) || observedRows.has('acknowledged-blocks-verified-after-restart');
  const interruptedWriteNotAcceptedCorrupt = bool(proof.interruptedWriteNotAcceptedCorrupt) || bool(summary.interruptedWriteNotAcceptedCorrupt) || observedRows.has('interrupted-write-not-silently-corrupt');
  const transientOpenFailureRetryObserved = bool(proof.transientOpenFailureRetryObserved) || (bool(summary.openFailureRootPromiseReset) && bool(summary.openRetrySucceeded) && bool(summary.putRetryVerified)) || observedRows.has('transient-opfs-open-failure-retry-observed');
  const guardedLocksDrainAfterOpenFailure = bool(proof.guardedLocksDrainAfterOpenFailure) || bool(summary.guardedLockDrainedAfterFailure) || observedRows.has('guarded-locks-drain-after-open-failure');
  const unsettledOrphanReviewGateObserved = bool(proof.unsettledOrphanReviewGateObserved) || bool(summary.unsettledOrphanReviewGateObserved) || observedRows.has('unsettled-orphan-review-gate-observed');
  const exactCommandVisible = bool(proof.browserHeavyCommandVisible) || String(recovery.commandId || '').includes('browser:kernel-kit-recovery-checkpoint-proof');
  const observed = recovery.status === 'risk-checkpoint-ready' && sameOriginProfileRestartObserved && sigkillBoundaryObserved && acknowledgedBlocksVerifiedAfterRestart && interruptedWriteNotAcceptedCorrupt && transientOpenFailureRetryObserved && unsettledOrphanReviewGateObserved;
  return frozen({
    observed,
    status: observed ? 'observed' : (recovery.status || summary.status || 'browser-heavy-deferred'),
    commandId: recovery.commandId || summary.commandId || 'browser:kernel-kit-recovery-checkpoint-proof',
    exactCommandVisible,
    sameOriginProfileRestartObserved,
    sigkillBoundaryObserved,
    acknowledgedBlocksVerifiedAfterRestart,
    interruptedWriteNotAcceptedCorrupt,
    transientOpenFailureRetryObserved,
    guardedLocksDrainAfterOpenFailure,
    unsettledOrphanReviewGateObserved,
    crashDurabilityNonClaimsVisible: proof.crashDurabilityNonClaimsVisible !== false,
    crossBrowserNonClaimsVisible: proof.crossBrowserNonClaimsVisible !== false,
    deferredRowIds: Array.from(deferredRows),
    observedRowIds: Array.from(observedRows),
    source: recovery.source || summary.source || 'kernel-kit-recovery-checkpoint'
  });
}

export function createKernelKitLifecycleCheckpoint(input = {}, fields = {}) {
  const revision = fields.revision || input.revision || input.supportBundle?.revision || input.success?.revision || 'rev0054';
  const proof = proofBag(input);
  const storage = storagePostureSummary(input);
  const webLocks = webLockPostureSummary(input);
  const guarded = guardedStorageSummary(input);
  const storagePressure = storagePressureSummary(input);
  const admissionCancellation = admissionCancellationSummary(input);
  const sessionCoordination = sessionCoordinationSummary(input);
  const recovery = recoverySummary(input);
  const abortBoundary = firstObj(input.abortBoundary, input.handoff?.abortBoundary, input.success?.abortBoundary, input.observations?.work?.abortBoundary);
  const abortProof = abortBoundary?.proof || {};
  const storagePathEvidence = bool(proof.storageWrite) || bool(proof.storageLaneWriteRead) || bool(proof.storagePathEvidencePresent) || bool(input.observations?.storageLaneWriteRead) || bool(input.results?.storage?.put?.digest) || bool(input.storage?.result?.digest);
  const abortNonMutation = bool(proof.opfsAbortBoundary) || bool(proof.storageAbortBoundary) || bool(abortProof.nonMutationBoundary) || (bool(abortProof.compositeAbortRejected) && bool(abortProof.noBlockPresent));
  const reloadReadback = bool(proof.reloadReadback) || bool(proof.reloadReadbackPresent) || bool(input.reload?.readbackOk) || bool(input.read?.verify?.ok) || bool(proof.storageWrite);
  const supportBundleReplay = bool(proof.replayPlanPresent) || bool(proof.supportBundleReplay) || input.supportBundle?.replayPlan?.status === 'seeded' || input.replayPlan?.status === 'replay-plan-ready';
  const supportBundleEvidence = bool(proof.evidenceLedgerPresent) || bool(proof.supportBundleEvidenceLedger) || input.supportBundle?.evidenceLedger?.status === 'evidence-ledger-ready';
  const nonClaimOk = nonClaimsVisible(input) || fields.nonClaimsAlreadyVisible === true;

  const rows = [
    makeRow({
      id: 'product-storage-path-evidence',
      title: 'One product-shaped storage path exists',
      risk: 5,
      status: rowStatus(storagePathEvidence, 'failed'),
      evidencePaths: ['proof.storageWrite', 'proof.storageLaneWriteRead', 'observations.storageLaneWriteRead', 'storage.result.digest'],
      evidence: { storagePathEvidence },
      whyItMatters: 'The Kernel Kit must stay anchored in a real write/read path, not a registry-only description.',
      nextAction: storagePathEvidence ? 'Keep this row tied to the demo proof before adding more lifecycle doctrine.' : 'Run or repair the Kernel Kit demo storage-lane write/read proof.',
      nonClaim: 'Storage path evidence is a narrow demo path, not a production storage guarantee.'
    }),
    makeRow({
      id: 'opfs-abort-non-mutation-boundary',
      title: 'OPFS abort boundary prevents mutation on the product path',
      risk: 5,
      status: rowStatus(abortNonMutation),
      evidencePaths: ['proof.opfsAbortBoundary', 'proof.storageAbortBoundary', 'abortBoundary.proof.nonMutationBoundary'],
      evidence: { abortNonMutation },
      whyItMatters: 'Cancellation/non-mutation is the most user-visible storage safety seam when work is abandoned.',
      nextAction: abortNonMutation ? 'Keep the abort boundary in the browser runner and support bundle.' : 'Spend browser budget on the Kernel Kit OPFS abort boundary before widening claims.',
      nonClaim: 'Abort remains cooperative; this does not prove every browser filesystem call is preemptible.'
    }),
    makeRow({
      id: 'storage-manager-posture',
      title: 'StorageManager estimate/persistence posture is captured',
      risk: 5,
      status: rowStatus(storage.observed),
      evidencePaths: ['storagePosture.proof.estimateChecked', 'storagePosture.estimate.quota', 'storagePosture.persisted'],
      evidence: storage,
      whyItMatters: 'Quota and eviction failures are among the riskiest browser-local runtime gaps; the page must at least expose current posture.',
      nextAction: storage.observed ? 'Promote the browser artifact when browser/CDP budget is intentionally spent.' : 'Run explicit browser Kernel Kit proof to capture StorageManager posture.',
      nonClaim: 'Storage posture is advisory estimate evidence, not a quota reservation or eviction-survival proof.'
    }),
    makeRow({
      id: 'persistent-storage-not-assumed',
      title: 'Persistent storage is not silently assumed',
      risk: 5,
      status: storage.persistentStorageRequested ? 'failed' : 'observed',
      evidencePaths: ['storagePosture.persistRequest.requested', 'storagePosture.proof.persistenceNotRequestedByDefault'],
      evidence: { persistentStorageRequested: storage.persistentStorageRequested, persistenceNotRequestedByDefault: storage.persistenceNotRequestedByDefault },
      whyItMatters: 'A hidden persist() request or implied grant would turn advisory evidence into a misleading durability claim.',
      nextAction: storage.persistentStorageRequested ? 'Move persistence requests behind an explicit user/product policy.' : 'Keep persistence requests explicit and separated from default demo proof.',
      nonClaim: 'No persistent-storage grant or durable retention guarantee is claimed.'
    }),
    makeRow({
      id: 'web-locks-coordination-posture',
      title: 'Web Locks coordination posture is observed or explicitly deferred',
      risk: 5,
      status: rowStatus(webLocks.observed),
      evidencePaths: ['webLockPosture.proof.exclusiveNoOverlap', 'webLockPosture.proof.sharedCoHold', 'webLockPosture.proof.drainedAfterUse'],
      evidence: webLocks,
      whyItMatters: 'Same-origin tabs/workers need a visible coordination boundary before BrowserRT is trusted as a local runtime substrate.',
      nextAction: webLocks.observed ? 'Keep Web Locks posture advisory and browser-explicit.' : 'Run the browser Kernel Kit proof to observe Web Locks posture.',
      nonClaim: 'Web Locks posture is not a fairness, background lifecycle, or production multi-tab guarantee.'
    }),
    makeRow({
      id: 'guarded-storage-lane-path',
      title: 'OPFS storage lane uses the guarded provider when browser evidence is present',
      risk: 5,
      status: rowStatus(guarded.observed),
      evidencePaths: ['guardedStorageLane.proof.guardedProvider', 'guardedStorageLane.proof.lockAcquiredReleased', 'storage.guarded.proof'],
      evidence: guarded,
      whyItMatters: 'The useful wedge is guarded storage through the product path, not Web Locks and OPFS as disconnected demos.',
      nextAction: guarded.observed ? 'Keep guarded provider evidence visible in the page, support bundle, and browser artifact.' : 'Route browser Kernel Kit storage through WebLockGuardedBlockStore before asserting multi-context posture.',
      nonClaim: 'Guarded storage-lane evidence is managed-browser evidence only, not a production coordination guarantee.'
    }),
    makeRow({
      id: 'reload-readback-evidence',
      title: 'Reload/readback or same-run readback is visible',
      risk: 4,
      status: rowStatus(reloadReadback),
      evidencePaths: ['proof.reloadReadback', 'proof.reloadReadbackPresent', 'reload.readbackOk', 'read.verify.ok'],
      evidence: { reloadReadback },
      whyItMatters: 'A local runtime story is weak if stored artifacts cannot be re-opened through a reviewer-visible flow.',
      nextAction: reloadReadback ? 'Keep the readback path in the human page and support bundle.' : 'Run the browser reload phase or preserve explicit same-run readback as a fallback only.',
      nonClaim: 'Readback is not a browser-restart, crash-recovery, or durability proof.'
    }),
    makeRow({
      id: 'quota-pressure-backpressure-evidence',
      title: 'Quota pressure/backpressure has a browser-heavy checkpoint path',
      risk: 5,
      status: rowStatus(storagePressure.observed),
      evidencePaths: ['storagePressure.proof.quotaExceededClassified', 'storagePressure.proof.cleanupVerified', 'storagePressure.proof.quotaOverrideReset', 'browser:opfs-lane-quota-backpressure-proof'],
      evidence: storagePressure,
      whyItMatters: 'Quota pressure is the storage failure most likely to be skipped because it spends browser/CDP budget; the Kernel Kit support path must name it directly.',
      nextAction: storagePressure.observed ? 'Keep quota-pressure proof browser-explicit and separate from eviction-survival claims.' : 'Run browser:opfs-lane-quota-backpressure-proof when spending browser budget; keep eviction survival deferred unless directly tested.',
      nonClaim: 'Quota-pressure/backpressure evidence is not eviction survival, quota reservation, fsync, crash recovery, or cross-browser storage conformance.'
    }),
    makeRow({
      id: 'admission-cancellation-backpressure-evidence',
      title: 'Admission cancellation releases watermarks under backpressure',
      risk: 5,
      status: rowStatus(admissionCancellation.observed),
      evidencePaths: ['admissionCancellation.proof.boundLeaseAbortReleasedPermit', 'admissionCancellation.proof.congestionRecoversAfterAbortRelease', 'admission:abort-release-proof'],
      evidence: admissionCancellation,
      whyItMatters: 'A cancelled caller that keeps admission bytes/permits in flight can poison later useful work while all storage proofs still look locally correct.',
      nextAction: admissionCancellation.observed ? 'Keep AbortSignal admission release in release-light Kernel Kit validation.' : 'Run admission:abort-release-proof before widening bounded workbench cancellation language.',
      nonClaim: 'Admission permit release is not exactly-once execution, task preemption, provider rollback, Browser Worker cancellation, fairness, latency, or production cancellation.'
    }),
    makeRow({
      id: 'session-coordination-stale-handoff-evidence',
      title: 'Session coordination and stale local handoff evidence is visible',
      risk: 5,
      status: rowStatus(sessionCoordination.observed),
      evidencePaths: ['sessionCoordination.summary.localHandoffSingleUseClearObserved', 'sessionCoordination.summary.staleReadReturnedNull', 'browser:kernel-kit-session-coordination-checkpoint-proof'],
      evidence: sessionCoordination,
      whyItMatters: 'Kernel Kit handoff state and Web Locks coordination are session-scoped; stale local handoffs or untested tab contention can corrupt future work while looking like proof success.',
      nextAction: sessionCoordination.observed ? 'Keep same-origin browser-heavy coordination evidence separate from fairness/crash claims.' : 'Run browser:kernel-kit-session-coordination-checkpoint-proof before claiming multi-tab or stale-handoff behavior; keep abandoned-lock recovery deferred.',
      nonClaim: 'Session coordination checkpoint is not Web Locks fairness, abandoned-lock recovery, crash recovery, cross-browser lifecycle, or production multi-tab coordination.'
    }),
    makeRow({
      id: 'recovery-interruption-boundary-evidence',
      title: 'Interruption/recovery boundary evidence is visible',
      risk: 5,
      status: rowStatus(recovery.observed),
      evidencePaths: ['recoveryCheckpoint.proof.sameOriginProfileRestartObserved', 'recoveryCheckpoint.proof.interruptedWriteNotAcceptedCorrupt', 'browser:kernel-kit-recovery-checkpoint-proof'],
      evidence: recovery,
      whyItMatters: 'The Kernel Kit can now show a narrow browser-heavy interruption boundary: acknowledged OPFS blocks survive a SIGKILL relaunch, interrupted writes are not silently accepted as corrupt content, and transient OPFS open failure can retry cleanly.',
      nextAction: recovery.observed ? 'Keep recovery evidence scoped to managed Chromium and browser-heavy proof artifacts.' : 'Run browser:kernel-kit-recovery-checkpoint-proof before making any restart, crash, or recovery language broader than deferred.',
      nonClaim: 'Recovery checkpoint is not general crash recovery, fsync durability, power-loss safety, quota/eviction survival, abandoned-lock recovery, or cross-browser conformance.'
    }),
    makeRow({
      id: 'recovery-orphan-review-gate-evidence',
      title: 'Recovery orphan-review gate evidence is visible',
      risk: 5,
      status: rowStatus(recovery.unsettledOrphanReviewGateObserved),
      evidencePaths: ['recoveryCheckpoint.proof.unsettledOrphanReviewGateObserved', 'browser:opfs-web-lock-unsettled-orphan-review-proof'],
      evidence: { unsettledOrphanReviewGateObserved: recovery.unsettledOrphanReviewGateObserved, recoveryCommandId: recovery.commandId, source: recovery.source },
      whyItMatters: 'Restart recovery is incomplete if timed-out provider work can be imported as unsettled local state and silently block or poison later work. The gate must stay visible next to interruption recovery.',
      nextAction: recovery.unsettledOrphanReviewGateObserved ? 'Keep orphan-review evidence in the browser recovery aggregate and package seal.' : 'Run browser:kernel-kit-recovery-checkpoint-proof and ensure it includes browser:opfs-web-lock-unsettled-orphan-review-proof before calling restart cleanup complete.',
      nonClaim: 'Orphan review is reviewed/fingerprint-bound operator recovery, not automatic rollback, abandoned-lock recovery, cancellation, or production crash repair.'
    }),
    makeRow({
      id: 'quota-eviction-survival-deferred',
      title: 'Quota/eviction survival remains deferred, not implied',
      risk: 5,
      status: 'deferred',
      evidencePaths: ['nonClaims', 'storagePosture.nonClaim'],
      evidence: { quotaKnown: storage.quotaKnown, usageKnown: storage.usageKnown },
      whyItMatters: 'Quota pressure and eviction are the highest-risk browser-local storage failure modes after basic correctness.',
      nextAction: storagePressure.observed ? 'Keep quota-pressure observed, but do not erase this eviction-survival deferral without real browser eviction evidence.' : 'Run browser:opfs-lane-quota-backpressure-proof first; eviction survival remains deferred unless directly tested.',
      nonClaim: 'No OPFS quota reservation or eviction-survival claim.'
    }),
    makeRow({
      id: 'cross-browser-mobile-lifecycle-deferred',
      title: 'Cross-browser/mobile lifecycle remains deferred, not implied',
      risk: 5,
      status: 'deferred',
      evidencePaths: ['nonClaims'],
      evidence: { managedBrowserOnly: true },
      whyItMatters: 'A Chromium-only proof can easily be misread as browser platform coverage.',
      nextAction: 'Build a tiny compatibility matrix and run one non-Chromium smoke when the environment supports it.',
      nonClaim: 'No cross-browser, mobile lifecycle, or background-survival claim.'
    }),
    makeRow({
      id: 'side-channel-privacy-deferred',
      title: 'OPFS timing/privacy side-channel risk remains deferred',
      risk: 4,
      status: 'deferred',
      evidencePaths: ['nonClaims'],
      evidence: { sideChannelAuditPresent: false },
      whyItMatters: 'OPFS-backed runtimes create durable/timing surfaces that must not be treated as privacy-hardened by default.',
      nextAction: 'Add a security posture note and keep support-bundle exports free of sensitive local payloads by default.',
      nonClaim: 'No browser side-channel, anti-fingerprinting, or privacy-hardening claim.'
    }),
    makeRow({
      id: 'support-bundle-replay-evidence',
      title: 'Support bundle replay/evidence rows are visible',
      risk: 4,
      status: rowStatus(supportBundleReplay && supportBundleEvidence),
      evidencePaths: ['supportBundle.proof.replayPlanPresent', 'supportBundle.proof.evidenceLedgerPresent', 'supportBundle.evidenceLedger.status'],
      evidence: { supportBundleReplay, supportBundleEvidence },
      whyItMatters: 'Future sessions need one compact recovery path instead of re-reading hundreds of slices.',
      nextAction: supportBundleReplay && supportBundleEvidence ? 'Keep replay/evidence rows package-retained and file-backed.' : 'Run support-bundle evidence proof before widening the product path.',
      nonClaim: 'Replay/evidence rows do not authenticate artifacts or execute commands.'
    })
  ].sort((a, b) => (b.risk - a.risk) || a.id.localeCompare(b.id));

  const missingRequiredRows = KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS.filter((id) => !rows.some((row) => row.id === id));
  const failedRows = rows.filter((row) => row.status === 'failed').map((row) => row.id);
  const deferredRows = rows.filter((row) => row.status === 'deferred').map((row) => row.id);
  const observedRows = rows.filter((row) => row.status === 'observed').map((row) => row.id);
  const highRiskRows = rows.filter((row) => row.risk >= 5);
  const highRiskRowsBounded = highRiskRows.every((row) => ['observed', 'deferred'].includes(row.status) && row.nonClaim && row.nextAction);
  const proofOut = frozen({
    storagePathEvidencePresent: storagePathEvidence,
    abortBoundaryObservedOrDeferred: abortNonMutation || deferredRows.includes('opfs-abort-non-mutation-boundary'),
    storagePostureObservedOrDeferred: storage.observed || deferredRows.includes('storage-manager-posture'),
    quotaPressureObservedOrDeferred: storagePressure.observed || deferredRows.includes('quota-pressure-backpressure-evidence'),
    admissionCancellationObservedOrDeferred: admissionCancellation.observed || deferredRows.includes('admission-cancellation-backpressure-evidence'),
    sessionCoordinationObservedOrDeferred: sessionCoordination.observed || deferredRows.includes('session-coordination-stale-handoff-evidence'),
    recoveryObservedOrDeferred: recovery.observed || deferredRows.includes('recovery-interruption-boundary-evidence'),
    recoveryOrphanReviewObservedOrDeferred: recovery.unsettledOrphanReviewGateObserved || deferredRows.includes('recovery-orphan-review-gate-evidence'),
    guardedStorageObservedOrDeferred: guarded.observed || deferredRows.includes('guarded-storage-lane-path'),
    webLocksObservedOrDeferred: webLocks.observed || deferredRows.includes('web-locks-coordination-posture'),
    highRiskRowsBounded,
    deferredLifecycleRisksExplicit: deferredRows.includes('quota-eviction-survival-deferred') && deferredRows.includes('cross-browser-mobile-lifecycle-deferred') && deferredRows.includes('side-channel-privacy-deferred'),
    nonClaimsVisible: nonClaimOk,
    rowsRankedByRisk: rows.every((row, index) => index === 0 || rows[index - 1].risk >= row.risk),
    noFailedRows: failedRows.length === 0,
    requiredRowsPresent: missingRequiredRows.length === 0
  });
  const status = Object.values(proofOut).every((value) => value === true) ? 'risk-checkpoint-ready' : 'needs-attention';
  return frozen({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT,
    checkpointId: fields.checkpointId || `${revision}-kernel-kit-lifecycle-checkpoint`,
    generatedAt: fields.generatedAt || 'deterministic-kernel-kit-lifecycle-checkpoint',
    status,
    posture: 'lifecycle-risk-checkpoint-not-production-readiness',
    purpose: 'Collapse scattered Kernel Kit OPFS/Web Locks/storage/reload evidence into one risk-ranked checkpoint so future sessions spend effort on the riskiest missing proof instead of registry expansion.',
    source: fields.source || input.runner || input.proofId || input.probe_id || 'kernel-kit-lifecycle-checkpoint',
    rows: Object.freeze(rows),
    observedRowIds: Object.freeze(observedRows),
    deferredRowIds: Object.freeze(deferredRows),
    failedRowIds: Object.freeze(failedRows),
    missingRequiredRows: Object.freeze(missingRequiredRows),
    riskSummary: frozen({
      rowCount: rows.length,
      highRiskCount: highRiskRows.length,
      observedCount: observedRows.length,
      deferredCount: deferredRows.length,
      failedCount: failedRows.length,
      riskiestNextAction: rows.find((row) => row.status === 'deferred' && row.risk >= 5)?.nextAction || rows.find((row) => row.status !== 'observed')?.nextAction || 'Keep lifecycle rows tied to product-path evidence.'
    }),
    proof: proofOut,
    nonClaims: Object.freeze([...KERNEL_KIT_LIFECYCLE_CHECKPOINT_NON_CLAIMS])
  });
}

export function validateKernelKitLifecycleCheckpoint(checkpoint = {}) {
  const errors = [];
  if (!isObj(checkpoint)) return frozen({ ok: false, errors: ['lifecycle checkpoint must be an object'], rowCount: 0, deferredCount: 0, failedCount: 0, format: null, status: null });
  if (checkpoint.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (checkpoint.format !== KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT) errors.push(`format must be ${KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT}`);
  if (checkpoint.status !== 'risk-checkpoint-ready') errors.push('status must be risk-checkpoint-ready');
  const rows = asArray(checkpoint.rows);
  if (rows.length < KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS.length) errors.push('checkpoint rows must cover all required lifecycle risks');
  for (const id of KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS) if (!rows.some((row) => row.id === id)) errors.push(`missing lifecycle row ${id}`);
  for (const row of rows) {
    if (!['observed', 'deferred'].includes(row.status)) errors.push(`row ${row.id || 'unknown'} must be observed or deferred`);
    if (!Number.isFinite(row.risk) || row.risk < 1 || row.risk > 5) errors.push(`row ${row.id || 'unknown'} risk must be 1..5`);
    if (!row.nextAction) errors.push(`row ${row.id || 'unknown'} missing nextAction`);
    if (!row.nonClaim) errors.push(`row ${row.id || 'unknown'} missing nonClaim`);
    if (row.risk >= 5 && row.status === 'deferred' && !String(row.nextAction || '').length) errors.push(`high-risk deferred row ${row.id || 'unknown'} needs nextAction`);
  }
  if ((checkpoint.failedRowIds || []).length) errors.push('failedRowIds must be empty');
  if ((checkpoint.missingRequiredRows || []).length) errors.push('missingRequiredRows must be empty');
  for (const key of ['storagePathEvidencePresent', 'admissionCancellationObservedOrDeferred', 'sessionCoordinationObservedOrDeferred', 'recoveryObservedOrDeferred', 'recoveryOrphanReviewObservedOrDeferred', 'highRiskRowsBounded', 'deferredLifecycleRisksExplicit', 'nonClaimsVisible', 'rowsRankedByRisk', 'noFailedRows', 'requiredRowsPresent']) {
    if (checkpoint.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const claim of KERNEL_KIT_LIFECYCLE_CHECKPOINT_NON_CLAIMS) {
    if (!checkpoint.nonClaims?.includes(claim)) errors.push(`missing lifecycle non-claim: ${claim}`);
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
