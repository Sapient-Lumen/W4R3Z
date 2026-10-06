// BrowserRT Kernel Kit recovery checkpoint.
// This module binds browser-heavy interruption/open-failure evidence into one
// Kernel Kit support-bundle row without claiming general crash recovery,
// fsync durability, power-loss safety, quota/eviction survival, or cross-browser behavior.

export const KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT = 'browserrt-kernel-kit-recovery-checkpoint-v1';

export const KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS = Object.freeze([
  'No production recovery claim.',
  'No general crash recovery, power-loss, kernel panic, drive-cache flush, fsync, or transactional durability claim.',
  'No OPFS quota reservation, organic eviction survival, persistent-storage retention, or Storage Buckets claim.',
  'No cross-browser, mobile, background-tab, or service-worker lifecycle claim.',
  'No Web Locks fairness, abandoned-lock recovery, or multi-tab production coordination claim.',
  'No automatic unsettled-orphan cleanup without reviewed and fingerprint-bound operator action claim.',
  'No artifact authenticity, signing, or tamper-proof evidence claim.'
]);

export const KERNEL_KIT_RECOVERY_CHECKPOINT_REQUIRED_ROWS = Object.freeze([
  'browser-recovery-heavy-command-visible',
  'same-origin-profile-restart-boundary',
  'sigkill-interruption-boundary-observed',
  'acknowledged-blocks-verified-after-restart',
  'interrupted-write-not-silently-corrupt',
  'restart-cleanup-observed',
  'transient-opfs-open-failure-retry-observed',
  'guarded-locks-drain-after-open-failure',
  'unsettled-orphan-review-gate-observed',
  'crash-durability-non-claims-visible',
  'cross-browser-durability-non-claims-visible'
]);

function isObj(value) { return Boolean(value && typeof value === 'object'); }
function asArray(value) { return Array.isArray(value) ? value : []; }
function bool(value) { return value === true; }
function frozen(obj) { return Object.freeze(obj); }
function firstObj(...values) { return values.find(isObj) || null; }
function rowStatus(ok, fallback = 'deferred') { return ok ? 'observed' : fallback; }

function commandVisible(input = {}, source = {}) {
  const commands = [
    ...asArray(input.exactCommands),
    ...asArray(input.supportBundle?.exactCommands),
    ...asArray(source.exactCommands)
  ].map(String);
  return commands.some((cmd) => cmd.includes('browser:kernel-kit-recovery-checkpoint-proof'))
    || commands.some((cmd) => cmd.includes('browser:opfs-abrupt-kill-boundary-proof'))
    || String(source.commandId || source.taskId || '').includes('browser:kernel-kit-recovery-checkpoint-proof')
    || String(source.probe_id || '').includes('browser-kernel-kit-recovery-checkpoint');
}

function nonClaimText(input = {}, source = {}) {
  return [
    ...asArray(input.nonClaims),
    ...asArray(input.supportBundle?.nonClaims),
    ...asArray(source.nonClaims),
    ...KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS
  ].join('\n').toLowerCase();
}

function recoverySource(input = {}) {
  return firstObj(
    input.recoveryCheckpoint,
    input.recovery,
    input.browserRecovery,
    input.kernelKitRecovery,
    input.observations?.recovery,
    input.supportBundle?.recoveryCheckpoint
  ) || {};
}

function allowedInterruptedDisposition(disposition) {
  return [
    'absent-after-unclosed-interrupted-write',
    'complete-valid-after-unclosed-interrupted-write',
    'present-but-checksum-rejected-after-unclosed-interrupted-write',
    'present-but-read-rejected-after-unclosed-interrupted-write'
  ].includes(String(disposition || ''));
}

function allAcknowledgedVerified(rows) {
  return Array.isArray(rows) && rows.length > 0 && rows.every((row) => row && row.hasBefore === true && row.verify?.ok === true && row.digestAfterRead === row.digest && Number.isFinite(row.bytes));
}

function allAcknowledgedDeleted(rows) {
  return Array.isArray(rows) && rows.length > 0 && rows.every((row) => row && row.deleted === true && row.hasAfter === false);
}

function requestedSigkill(harness = {}) {
  const signals = asArray(harness.first?.process?.requestedSignals);
  return signals.some((signal) => String(signal).includes('SIGKILL')) || harness.first?.teardownMode === 'kill';
}


function summarizeUnsettledOrphanReview(source = {}, input = {}, proof = {}) {
  const review = firstObj(
    source.unsettledOrphanReview,
    source.orphanReview,
    source.storageLaneUnsettledOrphanReview,
    source.browserUnsettledOrphanReview,
    input.unsettledOrphanReview,
    input.orphanReview,
    input.storageLaneUnsettledOrphanReview,
    input.browserUnsettledOrphanReview,
    input.observations?.unsettledOrphanReview
  );
  const obs = review?.observations || review || {};
  const finalLocks = obs.finalLocks || obs.locksAfterGuarded || {};
  const importedUnsettledBlocksRecovery = bool(proof.importedUnsettledOrphanBlocksRecovery)
    || obs.blockedUnsettled?.recovered === false
    || obs.blockedUnsettled?.reason === 'timed-out-operation-still-unsettled';
  const reviewManifestRequired = bool(proof.orphanReviewManifestRequired)
    || obs.unsafeFinalize?.code === 'timed-out-quarantine-finalize-review-required';
  const staleFingerprintRejected = bool(proof.orphanStaleFingerprintRejected)
    || obs.staleFinalize?.code === 'timed-out-quarantine-finalize-review-fingerprint-mismatch'
    || obs.oldReviewClear?.code === 'timed-out-quarantine-clear-review-fingerprint-mismatch';
  const authoritativeScopeRejected = bool(proof.orphanReviewScopeOverrideRejected)
    || obs.scopeOverrideClear?.code === 'timed-out-quarantine-finalize-review-manifest-scope-override'
    || obs.countMismatchClear?.code === 'timed-out-quarantine-finalize-review-manifest-count-mismatch';
  const reviewedFinalizationObserved = bool(proof.reviewedOrphanFinalizationObserved)
    || (obs.finalized?.ok === true
      && Number(obs.finalized?.finalizedCount || 0) >= 1
      && (obs.finalized?.finalized?.[0]?.error?.code === 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED'
        || obs.finalized?.failedTimedOutOperationCount >= 1));
  const lateFailureRequiresFreshReview = bool(proof.orphanLateFailureFreshReviewRequired)
    || (obs.blockedLateFailure?.recovered === false
      && obs.blockedLateFailure?.reason === 'timed-out-operation-late-failure'
      && obs.oldReviewClear?.ok === false);
  const freshReviewClearedAndRecovered = bool(proof.orphanFreshReviewClearedAndRecovered)
    || (obs.cleared?.ok === true
      && Number(obs.cleared?.failedClearedCount || 0) >= 1
      && obs.recovered?.recovered === true
      && (obs.recoveryResult?.ok === true || obs.recoveryVerify?.ok === true));
  const guardedLocksDrainAfterOrphanReview = bool(proof.guardedLocksDrainAfterOrphanReview)
    || ((finalLocks.heldCount ?? 0) === 0 && (finalLocks.pendingCount ?? 0) === 0 && (review?.status === 'passed' || obs.cleanupAfter === true));
  const observed = bool(proof.unsettledOrphanReviewGateObserved)
    || (review?.status === 'passed'
      && importedUnsettledBlocksRecovery
      && reviewManifestRequired
      && staleFingerprintRejected
      && authoritativeScopeRejected
      && reviewedFinalizationObserved
      && lateFailureRequiresFreshReview
      && freshReviewClearedAndRecovered);
  return frozen({
    observed,
    source: review?.source || review?.probe_id || 'browser-heavy-unsettled-orphan-review-not-run',
    taskId: review?.task_id || 'browser:opfs-web-lock-unsettled-orphan-review-proof',
    importedUnsettledBlocksRecovery,
    reviewManifestRequired,
    staleFingerprintRejected,
    authoritativeScopeRejected,
    reviewedFinalizationObserved,
    lateFailureRequiresFreshReview,
    freshReviewClearedAndRecovered,
    guardedLocksDrainAfterOrphanReview
  });
}

function summarizeRecovery(input = {}) {
  const source = recoverySource(input);
  const proof = { ...(isObj(source.proof) ? source.proof : {}) };
  const abrupt = firstObj(source.abruptKillBoundary, source.abruptKill, source.browserAbruptKill, input.abruptKillBoundary, input.browserAbruptKill) || {};
  const open = firstObj(source.openFailureRecovery, source.openFailure, source.browserOpenFailureRecovery, input.openFailureRecovery, input.browserOpenFailureRecovery) || {};
  const abruptObs = abrupt.observations || abrupt;
  const openObs = open.observations || open;
  const restart = abruptObs.restartInspection || abruptObs.read || {};
  const write = abruptObs.write || {};
  const interrupted = restart.interrupted || abruptObs.interrupted || {};
  const openSnapshots = openObs;
  const nonClaims = nonClaimText(input, source);
  const orphan = summarizeUnsettledOrphanReview(source, input, proof);

  const sameOriginTwoLaunch = bool(proof.sameOriginTwoLaunch) || abruptObs.sameOrigin === true || write.page?.location === restart.page?.location;
  const profileReusedAcrossKill = bool(proof.profileReusedAcrossKill) || abruptObs.profileReused === true || abrupt.harness?.profile?.reused === true;
  const sigkillObserved = bool(proof.sigkillObserved) || write._teardownMode === 'kill' || requestedSigkill(abrupt.harness || {});
  const acknowledgedBlocksVerifiedAfterRestart = bool(proof.acknowledgedBlocksVerifiedAfterRestart) || allAcknowledgedVerified(restart.acknowledgedChecks);
  const interruptedWriteNotAcceptedCorrupt = bool(proof.interruptedWriteNotAcceptedCorrupt)
    || (allowedInterruptedDisposition(interrupted.disposition) && interrupted.disposition !== 'unexpected-readable-digest-mismatch' && interrupted.disposition !== 'inspection-error');
  const restartCleanupObserved = bool(proof.restartCleanupObserved)
    || (restart.cleanup === true && allAcknowledgedDeleted(restart.acknowledgedChecks) && (interrupted.hasBefore !== true || interrupted.hasAfter === false));

  const directOpenReset = (openSnapshots.afterFirstOpenSnapshot?.stats?.openRetryResets || 0) >= 1;
  const putOpenReset = (openSnapshots.afterFirstPutSnapshot?.stats?.openRetryResets || 0) >= 1;
  const openFailureRootPromiseReset = bool(proof.openFailureRootPromiseReset) || (openObs.patchInstalled === true && (directOpenReset || putOpenReset));
  const openRetrySucceeded = bool(proof.openRetrySucceeded) || openObs.secondOpen?.ok === true;
  const putRetryVerified = bool(proof.putRetryVerified) || (openObs.secondPut?.ok === true && openObs.verify?.ok === true && openObs.bytesPreserved === true);
  const guardedLockDrainedAfterFailure = bool(proof.guardedLockDrainedAfterFailure)
    || (openObs.lockSettled?.ok === true && (openObs.locksAfterGuarded?.heldCount ?? 0) === 0 && (openObs.locksAfterGuarded?.pendingCount ?? 0) === 0);

  const exactCommandVisible = commandVisible(input, source);
  const browserHeavyExplicit = bool(proof.browserHeavyExplicit) || exactCommandVisible || String(source.tier || source.source || source.probe_id || '').includes('browser');
  const crashDurabilityNonClaimsVisible = proof.crashDurabilityNonClaimsVisible !== false && nonClaims.includes('crash') && nonClaims.includes('fsync');
  const crossBrowserNonClaimsVisible = proof.crossBrowserNonClaimsVisible !== false && nonClaims.includes('cross-browser');
  const observed = (source.status === 'passed' || proof.observed === true)
    && sameOriginTwoLaunch
    && profileReusedAcrossKill
    && sigkillObserved
    && acknowledgedBlocksVerifiedAfterRestart
    && interruptedWriteNotAcceptedCorrupt
    && restartCleanupObserved
    && openFailureRootPromiseReset
    && openRetrySucceeded
    && putRetryVerified
    && guardedLockDrainedAfterFailure
    && orphan.observed
    && crashDurabilityNonClaimsVisible
    && crossBrowserNonClaimsVisible;

  return frozen({
    observed,
    status: observed ? 'observed' : (source.status || 'browser-heavy-deferred'),
    source: source.source || source.probe_id || 'browser-heavy-recovery-command-not-run',
    commandId: source.commandId || 'browser:kernel-kit-recovery-checkpoint-proof',
    tier: source.tier || 'browser-heavy-explicit',
    sameOriginTwoLaunch,
    profileReusedAcrossKill,
    sigkillObserved,
    acknowledgedBlocksVerifiedAfterRestart,
    interruptedWriteNotAcceptedCorrupt,
    interruptedDisposition: interrupted.disposition || null,
    restartCleanupObserved,
    openFailureRootPromiseReset,
    openRetrySucceeded,
    putRetryVerified,
    guardedLockDrainedAfterFailure,
    unsettledOrphanReviewGateObserved: orphan.observed,
    importedUnsettledOrphanBlocksRecovery: orphan.importedUnsettledBlocksRecovery,
    orphanReviewManifestRequired: orphan.reviewManifestRequired,
    orphanStaleFingerprintRejected: orphan.staleFingerprintRejected,
    orphanReviewScopeOverrideRejected: orphan.authoritativeScopeRejected,
    reviewedOrphanFinalizationObserved: orphan.reviewedFinalizationObserved,
    orphanLateFailureFreshReviewRequired: orphan.lateFailureRequiresFreshReview,
    orphanFreshReviewClearedAndRecovered: orphan.freshReviewClearedAndRecovered,
    guardedLocksDrainAfterOrphanReview: orphan.guardedLocksDrainAfterOrphanReview,
    orphanReviewSource: orphan.source,
    exactCommandVisible,
    browserHeavyExplicit,
    crashDurabilityNonClaimsVisible,
    crossBrowserNonClaimsVisible
  });
}

function makeRow({ id, title, risk, status, evidence = {}, evidencePaths = [], whyItMatters, nextAction, nonClaim }) {
  return frozen({ id, title, risk, status, evidencePaths: Object.freeze(evidencePaths), evidence: frozen(evidence), whyItMatters, nextAction, nonClaim });
}

export function createKernelKitRecoveryCheckpoint(input = {}, fields = {}) {
  const summary = summarizeRecovery(input);
  const revision = fields.revision || input.revision || input.supportBundle?.revision || 'rev0108';
  const rows = [
    makeRow({
      id: 'browser-recovery-heavy-command-visible',
      title: 'Browser-heavy recovery command is visible',
      risk: 5,
      status: rowStatus(summary.browserHeavyExplicit || summary.exactCommandVisible),
      evidencePaths: ['exactCommands', 'browser:kernel-kit-recovery-checkpoint-proof'],
      evidence: { commandId: summary.commandId, browserHeavyExplicit: summary.browserHeavyExplicit, exactCommandVisible: summary.exactCommandVisible },
      whyItMatters: 'Recovery evidence spends browser/CDP budget and must never be implied by a release-light support bundle.',
      nextAction: summary.browserHeavyExplicit || summary.exactCommandVisible ? 'Keep this command explicit in support bundles and evidence ledgers.' : 'Add browser:kernel-kit-recovery-checkpoint-proof to the support-bundle replay path.',
      nonClaim: 'A visible command is not proof execution, artifact authenticity, or production recovery readiness.'
    }),
    makeRow({
      id: 'same-origin-profile-restart-boundary',
      title: 'Same-origin profile restart boundary is observed or deferred',
      risk: 5,
      status: rowStatus(summary.sameOriginTwoLaunch && summary.profileReusedAcrossKill),
      evidencePaths: ['abruptKill.observations.sameOrigin', 'abruptKill.observations.profileReused'],
      evidence: { sameOriginTwoLaunch: summary.sameOriginTwoLaunch, profileReusedAcrossKill: summary.profileReusedAcrossKill },
      whyItMatters: 'Restart evidence is weak if the relaunch is not the same origin and profile where OPFS state lives.',
      nextAction: summary.sameOriginTwoLaunch && summary.profileReusedAcrossKill ? 'Keep same-origin/profile reuse in the compact browser artifact.' : 'Run the two-launch abrupt-kill proof before claiming restart readback evidence.',
      nonClaim: 'Same-origin/profile reuse is not cross-browser persistence, persistent-storage retention, or eviction survival.'
    }),
    makeRow({
      id: 'sigkill-interruption-boundary-observed',
      title: 'SIGKILL interruption boundary is observed or deferred',
      risk: 5,
      status: rowStatus(summary.sigkillObserved),
      evidencePaths: ['abruptKill.harness.first.process.requestedSignals', 'abruptKill.observations.write._teardownMode'],
      evidence: { sigkillObserved: summary.sigkillObserved },
      whyItMatters: 'Clean shutdown is a much weaker signal than killing the browser process while an in-flight OPFS candidate exists.',
      nextAction: summary.sigkillObserved ? 'Preserve the SIGKILL marker and managed-profile non-claim.' : 'Run browser:kernel-kit-recovery-checkpoint-proof rather than relying on clean reload evidence.',
      nonClaim: 'SIGKILL is not power loss, kernel panic, drive-cache flush, fsync, or transactional durability.'
    }),
    makeRow({
      id: 'acknowledged-blocks-verified-after-restart',
      title: 'Acknowledged blocks verify after restart or remain deferred',
      risk: 5,
      status: rowStatus(summary.acknowledgedBlocksVerifiedAfterRestart),
      evidencePaths: ['abruptKill.observations.restartInspection.acknowledgedChecks[].verify.ok'],
      evidence: { acknowledgedBlocksVerifiedAfterRestart: summary.acknowledgedBlocksVerifiedAfterRestart },
      whyItMatters: 'A Kernel Kit recovery story starts with the narrow boundary that already-acknowledged content-addressed blocks can be reopened and verified.',
      nextAction: summary.acknowledgedBlocksVerifiedAfterRestart ? 'Keep this narrow: acknowledged-and-closed blocks only.' : 'Run browser:opfs-abrupt-kill-boundary-proof through the recovery checkpoint.',
      nonClaim: 'Verified acknowledged blocks are not general crash recovery for arbitrary app state.'
    }),
    makeRow({
      id: 'interrupted-write-not-silently-corrupt',
      title: 'Interrupted write is not silently accepted as corrupt content',
      risk: 5,
      status: rowStatus(summary.interruptedWriteNotAcceptedCorrupt),
      evidencePaths: ['abruptKill.observations.restartInspection.interrupted.disposition'],
      evidence: { interruptedWriteNotAcceptedCorrupt: summary.interruptedWriteNotAcceptedCorrupt, disposition: summary.interruptedDisposition },
      whyItMatters: 'The severe failure would be treating an interrupted partial OPFS write as valid content-addressed data after relaunch.',
      nextAction: summary.interruptedWriteNotAcceptedCorrupt ? 'Keep the allowed-disposition boundary explicit.' : 'Do not widen recovery language until interrupted write disposition is observed.',
      nonClaim: 'This is one in-flight write candidate, not a transactional filesystem guarantee.'
    }),
    makeRow({
      id: 'restart-cleanup-observed',
      title: 'Restart inspection cleans test namespaces or remains deferred',
      risk: 4,
      status: rowStatus(summary.restartCleanupObserved),
      evidencePaths: ['abruptKill.observations.restartInspection.cleanup', 'acknowledgedChecks[].hasAfter=false'],
      evidence: { restartCleanupObserved: summary.restartCleanupObserved },
      whyItMatters: 'Recovery probes that leave stale OPFS proof namespaces can poison later cloudtainer sessions.',
      nextAction: summary.restartCleanupObserved ? 'Keep cleanup proof in the compact recovery artifact.' : 'Require cleanup after restart inspection before sealing the recovery artifact.',
      nonClaim: 'Test namespace cleanup is not eviction survival or production data lifecycle management.'
    }),
    makeRow({
      id: 'transient-opfs-open-failure-retry-observed',
      title: 'Transient OPFS root-open failure retries cleanly or remains deferred',
      risk: 5,
      status: rowStatus(summary.openFailureRootPromiseReset && summary.openRetrySucceeded && summary.putRetryVerified),
      evidencePaths: ['openFailure.afterFirstOpenSnapshot.stats.openRetryResets', 'openFailure.secondOpen.ok', 'openFailure.verify.ok'],
      evidence: { openFailureRootPromiseReset: summary.openFailureRootPromiseReset, openRetrySucceeded: summary.openRetrySucceeded, putRetryVerified: summary.putRetryVerified },
      whyItMatters: 'A cached rejected OPFS root promise can permanently poison a local runtime after one transient failure unless retry reset is proven.',
      nextAction: summary.openFailureRootPromiseReset && summary.openRetrySucceeded && summary.putRetryVerified ? 'Keep retry-reset proof alongside abrupt-kill proof.' : 'Run browser:opfs-block-store-open-failure-recovery-proof through the recovery checkpoint.',
      nonClaim: 'Open-failure retry is not crash recovery, quota recovery, or durability.'
    }),
    makeRow({
      id: 'guarded-locks-drain-after-open-failure',
      title: 'Guarded Web Locks path drains after open-failure recovery',
      risk: 4,
      status: rowStatus(summary.guardedLockDrainedAfterFailure),
      evidencePaths: ['openFailure.lockSettled.ok', 'openFailure.locksAfterGuarded.heldCount=0'],
      evidence: { guardedLockDrainedAfterFailure: summary.guardedLockDrainedAfterFailure },
      whyItMatters: 'Recovery from OPFS open failure is incomplete if guarded storage leaves same-origin locks held or pending.',
      nextAction: summary.guardedLockDrainedAfterFailure ? 'Keep lock drain check in the browser recovery aggregate.' : 'Add guarded lock drain to the recovery checkpoint before widening coordination claims.',
      nonClaim: 'Drained locks after one managed proof are not abandoned-lock recovery, fairness, or production coordination.'
    }),
    makeRow({
      id: 'unsettled-orphan-review-gate-observed',
      title: 'Unsettled timeout orphan review gate is observed or remains deferred',
      risk: 5,
      status: rowStatus(summary.unsettledOrphanReviewGateObserved),
      evidencePaths: ['unsettledOrphanReview.blockedUnsettled.reason', 'unsettledOrphanReview.finalized.finalized[].error.code', 'browser:opfs-web-lock-unsettled-orphan-review-proof'],
      evidence: {
        observed: summary.unsettledOrphanReviewGateObserved,
        importedUnsettledOrphanBlocksRecovery: summary.importedUnsettledOrphanBlocksRecovery,
        orphanReviewManifestRequired: summary.orphanReviewManifestRequired,
        orphanStaleFingerprintRejected: summary.orphanStaleFingerprintRejected,
        orphanReviewScopeOverrideRejected: summary.orphanReviewScopeOverrideRejected,
        reviewedOrphanFinalizationObserved: summary.reviewedOrphanFinalizationObserved,
        orphanLateFailureFreshReviewRequired: summary.orphanLateFailureFreshReviewRequired,
        orphanFreshReviewClearedAndRecovered: summary.orphanFreshReviewClearedAndRecovered,
        guardedLocksDrainAfterOrphanReview: summary.guardedLocksDrainAfterOrphanReview,
        source: summary.orphanReviewSource
      },
      whyItMatters: 'A restarted/local runtime can look healthy while an imported timed-out provider operation is still unsettled. The safe recovery path must force review-bound orphan finalization and a fresh late-failure clear before accepting more work.',
      nextAction: summary.unsettledOrphanReviewGateObserved ? 'Keep orphan-review evidence sealed into the browser recovery aggregate.' : 'Run browser:opfs-web-lock-unsettled-orphan-review-proof through the Kernel Kit recovery aggregate before describing restart cleanup as complete.',
      nonClaim: 'Reviewed orphan finalization is an operator-gated recovery procedure, not automatic cancellation, rollback, abandoned-lock recovery, or production crash repair.'
    }),
    makeRow({
      id: 'crash-durability-non-claims-visible',
      title: 'Crash/durability non-claims are visible',
      risk: 5,
      status: rowStatus(summary.crashDurabilityNonClaimsVisible),
      evidencePaths: ['nonClaims'],
      evidence: { crashDurabilityNonClaimsVisible: summary.crashDurabilityNonClaimsVisible },
      whyItMatters: 'Recovery evidence becomes dangerous if reviewers promote it into fsync, power-loss, or general crash-durability language.',
      nextAction: summary.crashDurabilityNonClaimsVisible ? 'Preserve these non-claims in docs, support bundles, and release artifacts.' : 'Restore crash/fsync/power-loss non-claims before sealing.',
      nonClaim: 'No general crash recovery, power-loss, fsync, or transactional durability claim.'
    }),
    makeRow({
      id: 'cross-browser-durability-non-claims-visible',
      title: 'Cross-browser durability non-claims are visible',
      risk: 4,
      status: rowStatus(summary.crossBrowserNonClaimsVisible),
      evidencePaths: ['nonClaims'],
      evidence: { crossBrowserNonClaimsVisible: summary.crossBrowserNonClaimsVisible },
      whyItMatters: 'The evidence is managed Chromium/CDP only and must not become platform-wide browser recovery language.',
      nextAction: summary.crossBrowserNonClaimsVisible ? 'Keep managed-Chromium scope visible until a real matrix exists.' : 'Restore cross-browser/mobile/background non-claims.',
      nonClaim: 'No Firefox, Safari, mobile, background-tab, or service-worker lifecycle claim.'
    })
  ].sort((a, b) => (b.risk - a.risk) || a.id.localeCompare(b.id));

  const missingRequiredRows = KERNEL_KIT_RECOVERY_CHECKPOINT_REQUIRED_ROWS.filter((id) => !rows.some((row) => row.id === id));
  const failedRowIds = rows.filter((row) => row.status === 'failed').map((row) => row.id);
  const deferredRowIds = rows.filter((row) => row.status === 'deferred').map((row) => row.id);
  const observedRowIds = rows.filter((row) => row.status === 'observed').map((row) => row.id);
  const highRiskRowsBounded = rows.filter((row) => row.risk >= 5).every((row) => ['observed', 'deferred'].includes(row.status) && row.nextAction && row.nonClaim);
  const proof = frozen({
    browserHeavyCommandVisible: summary.browserHeavyExplicit || summary.exactCommandVisible,
    sameOriginProfileRestartObserved: summary.sameOriginTwoLaunch && summary.profileReusedAcrossKill,
    sigkillBoundaryObserved: summary.sigkillObserved,
    acknowledgedBlocksVerifiedAfterRestart: summary.acknowledgedBlocksVerifiedAfterRestart,
    interruptedWriteNotAcceptedCorrupt: summary.interruptedWriteNotAcceptedCorrupt,
    restartCleanupObservedOrDeferred: summary.restartCleanupObserved || deferredRowIds.includes('restart-cleanup-observed'),
    transientOpenFailureRetryObserved: summary.openFailureRootPromiseReset && summary.openRetrySucceeded && summary.putRetryVerified,
    guardedLocksDrainAfterOpenFailure: summary.guardedLockDrainedAfterFailure,
    unsettledOrphanReviewGateObserved: summary.unsettledOrphanReviewGateObserved,
    unsettledOrphanReviewGateObservedOrDeferred: summary.unsettledOrphanReviewGateObserved || deferredRowIds.includes('unsettled-orphan-review-gate-observed'),
    crashDurabilityNonClaimsVisible: summary.crashDurabilityNonClaimsVisible,
    crossBrowserNonClaimsVisible: summary.crossBrowserNonClaimsVisible,
    recoveryObservedOrExplicitlyDeferred: summary.observed || deferredRowIds.length > 0,
    highRiskRowsBounded,
    rowsRankedByRisk: rows.every((row, index) => index === 0 || rows[index - 1].risk >= row.risk),
    noFailedRows: failedRowIds.length === 0,
    requiredRowsPresent: missingRequiredRows.length === 0
  });
  const status = proof.browserHeavyCommandVisible
    && proof.recoveryObservedOrExplicitlyDeferred
    && proof.highRiskRowsBounded
    && proof.rowsRankedByRisk
    && proof.noFailedRows
    && proof.requiredRowsPresent
    && proof.crashDurabilityNonClaimsVisible
    && proof.crossBrowserNonClaimsVisible
    ? 'risk-checkpoint-ready'
    : 'needs-attention';
  return frozen({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT,
    checkpointId: fields.checkpointId || `${revision}-kernel-kit-recovery-checkpoint`,
    generatedAt: fields.generatedAt || 'deterministic-kernel-kit-recovery-checkpoint',
    status,
    purpose: 'Make BrowserRT Kernel Kit interruption recovery evidence explicit: abrupt SIGKILL restart boundary plus OPFS root-open retry recovery, while keeping crash/fsync/cross-browser non-claims visible.',
    posture: 'recovery-risk-checkpoint-not-production-durability',
    source: fields.source || summary.source,
    commandId: summary.commandId,
    tier: summary.tier,
    rows: Object.freeze(rows),
    observedRowIds: Object.freeze(observedRowIds),
    deferredRowIds: Object.freeze(deferredRowIds),
    failedRowIds: Object.freeze(failedRowIds),
    missingRequiredRows: Object.freeze(missingRequiredRows),
    riskSummary: frozen({
      rowCount: rows.length,
      observedCount: observedRowIds.length,
      deferredCount: deferredRowIds.length,
      failedCount: failedRowIds.length,
      riskiestNextAction: rows.find((row) => row.status === 'deferred' && row.risk >= 5)?.nextAction || 'Keep recovery rows bound to browser-heavy artifacts.'
    }),
    summary,
    proof,
    nonClaims: Object.freeze([...KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS])
  });
}

export function validateKernelKitRecoveryCheckpoint(checkpoint = {}) {
  const errors = [];
  if (!isObj(checkpoint)) return frozen({ ok: false, errors: ['recovery checkpoint must be an object'], rowCount: 0, observedCount: 0, deferredCount: 0, failedCount: 0, format: null, status: null });
  if (checkpoint.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (checkpoint.format !== KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT) errors.push(`format must be ${KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT}`);
  if (checkpoint.status !== 'risk-checkpoint-ready') errors.push('status must be risk-checkpoint-ready');
  const rows = asArray(checkpoint.rows);
  if (rows.length < KERNEL_KIT_RECOVERY_CHECKPOINT_REQUIRED_ROWS.length) errors.push('checkpoint rows must cover all required recovery risks');
  for (const id of KERNEL_KIT_RECOVERY_CHECKPOINT_REQUIRED_ROWS) if (!rows.some((row) => row.id === id)) errors.push(`missing recovery row ${id}`);
  for (const row of rows) {
    if (!['observed', 'deferred'].includes(row.status)) errors.push(`row ${row.id || 'unknown'} must be observed or deferred`);
    if (!Number.isFinite(row.risk) || row.risk < 1 || row.risk > 5) errors.push(`row ${row.id || 'unknown'} risk must be 1..5`);
    if (!row.nextAction) errors.push(`row ${row.id || 'unknown'} missing nextAction`);
    if (!row.nonClaim) errors.push(`row ${row.id || 'unknown'} missing nonClaim`);
  }
  if ((checkpoint.failedRowIds || []).length) errors.push('failedRowIds must be empty');
  if ((checkpoint.missingRequiredRows || []).length) errors.push('missingRequiredRows must be empty');
  for (const key of ['browserHeavyCommandVisible','recoveryObservedOrExplicitlyDeferred','unsettledOrphanReviewGateObservedOrDeferred','highRiskRowsBounded','rowsRankedByRisk','noFailedRows','requiredRowsPresent','crashDurabilityNonClaimsVisible','crossBrowserNonClaimsVisible']) {
    if (checkpoint.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const claim of KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS) {
    if (!checkpoint.nonClaims?.includes(claim)) errors.push(`missing recovery non-claim: ${claim}`);
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
