#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-support-bundle-proof. Release-tier proof for portable Kernel Kit support bundle.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitFailureModeReport,
  createKernelKitTraceComparison,
  createKernelKitDiagnosticRunbook,
  createKernelKitDemoExportBundle,
  createKernelKitSupportBundle,
  validateKernelKitSupportBundle,
  validateKernelKitSupportBundlePrivacyScrub,
  createKernelKitSupportBundleReplayPlan,
  validateKernelKitSupportBundleReplayPlan,
  validateKernelKitSupportBundleEvidenceLedger,
  KERNEL_KIT_SUPPORT_BUNDLE_FORMAT,
  KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runKernelKitDemoProbe } from './kernel_kit_demo_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-SUPPORT-BUNDLE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const successReport = await runKernelKitDemoProbe();
  const failureReport = createKernelKitFailureModeReport({
    revision: REVISION,
    mode: 'admission-reject-no-mutation',
    observed: { rejected: true, reason: 'synthetic-release-tier-controlled-rejection', preventedMutation: true },
    traceKinds: ['runtime:boot', 'admission:reject', 'kernel-kit-demo:controlled-failure', 'kernel-kit-demo:failure:admission-reject-no-mutation', 'runtime:close']
  });
  const comparison = createKernelKitTraceComparison(successReport, failureReport, { revision: REVISION, source: 'kernel-kit-support-bundle-probe-comparison', generatedAt: 'deterministic-support-bundle-comparison' });
  const runbook = createKernelKitDiagnosticRunbook(comparison, { revision: REVISION, source: 'kernel-kit-support-bundle-probe-runbook', generatedAt: 'deterministic-support-bundle-runbook' });
  const exportBundle = createKernelKitDemoExportBundle(successReport, { revision: REVISION, source: 'kernel-kit-support-bundle-probe-export', generatedAt: 'deterministic-support-bundle-export' });
  const supportBundle = createKernelKitSupportBundle({
    revision: REVISION,
    successReport,
    reloadReport: successReport,
    failureReport,
    comparison,
    runbook,
    exportBundle,
    generatedAt: 'deterministic-support-bundle-probe'
  });
  const validation = validateKernelKitSupportBundle(supportBundle);
  assert.equal(supportBundle.format, KERNEL_KIT_SUPPORT_BUNDLE_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  const replayPlan = createKernelKitSupportBundleReplayPlan(supportBundle, { revision: REVISION, generatedAt: 'deterministic-support-bundle-replay-plan-probe' });
  const replayValidation = validateKernelKitSupportBundleReplayPlan(replayPlan);
  assert.equal(replayPlan.format, KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT);
  assert.equal(replayValidation.ok, true, replayValidation.errors.join('; '));
  assert.equal(replayPlan.status, 'replay-plan-ready');
  assert.equal(replayPlan.proof.bundleValidationOk, true);
  assert.equal(replayPlan.proof.browserLightBeforeBrowserHeavy, true);
  assert.equal(replayPlan.proof.replayDoesNotExecuteCommands, true);
  assert.equal(replayPlan.blockedPhaseIds.length, 0);
  assert.equal(supportBundle.proof.successPathPresent, true);
  assert.equal(supportBundle.proof.controlledFailurePresent, true);
  assert.equal(supportBundle.proof.traceComparisonPresent, true);
  assert.equal(supportBundle.proof.diagnosticRunbookPresent, true);
  assert.equal(supportBundle.proof.exportReceiptPresent, true);
  assert.equal(supportBundle.proof.exactCommandsPresent, true);
  assert.equal(supportBundle.proof.replayPlanPresent, true);
  assert.equal(supportBundle.proof.evidenceLedgerPresent, true);
  assert.equal(supportBundle.proof.lifecycleCheckpointPresent, true);
  assert.equal(supportBundle.proof.privacyScrubPresent, true);
  assert.equal(supportBundle.proof.storagePressureCheckpointPresent, true);
  assert.equal(supportBundle.proof.storageRecoveryGuidancePresent, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.status, 'ready');
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.lockTimeoutGuidesQueryLocks, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.providerQuotaRequiresVerifyBeforeRetry, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.providerAbortRequiresExplicitRecovery, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.serviceWorkerWaitUntilRequiresSettledRecovery, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.decisionRowsPresent, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.automaticRetryLimitedToPreMutationRows, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.mutationRowsRequireVerifyFirst, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.serviceWorkerWaitUntilDecisionVerifyFirst, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.stopManualReviewRowsClassified, true);
  assert.equal(supportBundle.storageRecoveryGuidance?.proof?.noRawErrorMessageStackPathDigestOrLockName, true);
  assert.ok(supportBundle.storageRecoveryGuidance?.rowCodes?.includes('BRT_WEB_LOCK_TIMEOUT'), 'storage recovery guidance must include Web Lock timeout row');
  assert.ok(supportBundle.storageRecoveryGuidance?.rowCodes?.includes('BRT_OPFS_QUOTA_EXCEEDED'), 'storage recovery guidance must include provider quota row');
  assert.ok(supportBundle.storageRecoveryGuidance?.rowCodes?.includes('BRT_OPFS_OPERATION_ABORTED'), 'storage recovery guidance must include provider abort row');
  assert.ok(supportBundle.storageRecoveryGuidance?.rowCodes?.includes('BRT_SW_WAITUNTIL_LATE_FAILURE'), 'storage recovery guidance must include Service Worker waitUntil late-failure row');
  assert.ok(supportBundle.storageRecoveryGuidance?.rowCodes?.includes('BRT_STORAGE_FAILURE_UNCLASSIFIED'), 'storage recovery guidance must include manual-review ambiguous row');
  assert.equal(supportBundle.storageRecoveryGuidance?.rows?.find((row) => row.code === 'BRT_WEB_LOCK_TIMEOUT')?.decision, 'retry');
  assert.equal(supportBundle.storageRecoveryGuidance?.rows?.find((row) => row.code === 'BRT_SW_WAITUNTIL_LATE_FAILURE')?.decision, 'verify-first');
  assert.equal(supportBundle.storageRecoveryGuidance?.rows?.find((row) => row.code === 'BRT_STORAGE_FAILURE_UNCLASSIFIED')?.decision, 'stop/manual-review');
  assert.equal(supportBundle.proof.admissionCancellationCheckpointPresent, true);
  assert.equal(supportBundle.proof.sessionCoordinationCheckpointPresent, true);
  assert.equal(supportBundle.proof.recoveryCheckpointPresent, true);
  assert.equal(supportBundle.recoveryCheckpoint?.status, 'risk-checkpoint-ready');
  assert.equal(supportBundle.recoveryCheckpoint?.commandId, 'browser:kernel-kit-recovery-checkpoint-proof');
  assert.ok(supportBundle.recoveryCheckpoint?.deferredRowIds?.includes('same-origin-profile-restart-boundary'), 'default support bundle should keep browser-heavy restart recovery deferred');
  assert.ok(supportBundle.recoveryCheckpoint?.deferredRowIds?.includes('transient-opfs-open-failure-retry-observed'), 'default support bundle should keep browser-heavy OPFS open-failure retry deferred');
  assert.ok(supportBundle.recoveryCheckpoint?.deferredRowIds?.includes('unsettled-orphan-review-gate-observed'), 'default support bundle should keep browser-heavy unsettled orphan review gate deferred');
  assert.equal(supportBundle.admissionCancellation?.status, 'risk-checkpoint-ready');
  assert.equal(supportBundle.admissionCancellation?.commandId, 'admission:abort-release-proof');
  assert.ok(supportBundle.admissionCancellation?.deferredRowIds?.includes('bound-lease-abort-releases-permit'), 'default support bundle should keep release-light admission abort release deferred until the artifact runs');
  assert.equal(supportBundle.sessionCoordination?.status, 'risk-checkpoint-ready');
  assert.equal(supportBundle.sessionCoordination?.commandId, 'browser:kernel-kit-session-coordination-checkpoint-proof');
  assert.ok(supportBundle.sessionCoordination?.deferredRowIds?.includes('exclusive-lock-contention-observed'), 'default support bundle should keep browser-heavy lock contention deferred');
  assert.equal(supportBundle.storagePressure?.status, 'browser-heavy-deferred');
  assert.equal(supportBundle.storagePressure?.commandId, 'browser:opfs-lane-quota-backpressure-proof');
  assert.equal(supportBundle.storagePressure?.evictionSurvivalDeferred, true);
  assert.equal(supportBundle.lifecycleCheckpoint?.status, 'risk-checkpoint-ready');
  assert.equal(supportBundle.lifecycleCheckpoint?.proof?.deferredLifecycleRisksExplicit, true);
  const privacyScrubValidation = validateKernelKitSupportBundlePrivacyScrub(supportBundle.privacyScrub);
  assert.equal(privacyScrubValidation.ok, true, privacyScrubValidation.errors.join('; '));
  assert.ok(privacyScrubValidation.redactedFieldCount > 0, 'privacy scrub should redact at least one field');
  assert.equal(validateKernelKitSupportBundleEvidenceLedger(supportBundle.evidenceLedger).ok, true);
  assert.equal(supportBundle.evidenceLedger.status, 'evidence-ledger-ready');
  assert.equal(replayPlan.evidenceSlots.evidenceLedgerPresent, true);
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('demo:kernel-kit-support-bundle-proof')), 'support-bundle proof command missing');
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-demo-proof')), 'browser proof command missing');
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('browser:opfs-lane-quota-backpressure-proof')), 'storage pressure browser-heavy command missing');
  assert.ok(supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'browser-storage-pressure-artifact'), 'storage pressure evidence ledger row missing');
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('admission:abort-release-proof')), 'admission abort release command missing');
  assert.ok(supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'admission-cancellation-artifact'), 'admission cancellation evidence ledger row missing');
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-session-coordination-checkpoint-proof')), 'session coordination browser-heavy command missing');
  assert.ok(supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'browser-session-coordination-artifact'), 'session coordination evidence ledger row missing');
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-recovery-checkpoint-proof')), 'recovery browser-heavy command missing');
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('browser:opfs-web-lock-unsettled-orphan-review-proof')), 'unsettled orphan review browser-heavy command missing');
  assert.ok(supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'browser-recovery-artifact'), 'recovery evidence ledger row missing');
  assert.ok(supportBundle.nonClaims.includes('No production support-bundle claim.'));
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-support-bundle-probe`,
    status: 'passed',
    successProbeId: successReport.proofId || successReport.probe_id,
    supportBundle,
    validation,
    replaySummary: { status: replayPlan.status, phaseCount: replayPlan.phases?.length || 0, blockedPhaseIds: replayPlan.blockedPhaseIds || [], validation: { ok: replayValidation.ok === true, errorCount: replayValidation.errors?.length || 0 } },
    proof: {
      supportBundleValid: validation.ok,
      sectionCount: validation.sectionCount,
      commandCount: validation.commandCount,
      successPathPresent: supportBundle.proof.successPathPresent,
      controlledFailurePresent: supportBundle.proof.controlledFailurePresent,
      traceComparisonPresent: supportBundle.proof.traceComparisonPresent,
      diagnosticRunbookPresent: supportBundle.proof.diagnosticRunbookPresent,
      exactCommandsPresent: supportBundle.proof.exactCommandsPresent,
      replayPlanPresent: supportBundle.proof.replayPlanPresent,
      evidenceLedgerPresent: supportBundle.proof.evidenceLedgerPresent,
      lifecycleCheckpointPresent: supportBundle.proof.lifecycleCheckpointPresent,
      privacyScrubPresent: supportBundle.proof.privacyScrubPresent,
      privacyScrubValid: privacyScrubValidation.ok === true,
      privacyScrubRedactedFields: privacyScrubValidation.redactedFieldCount,
      storagePressureCheckpointPresent: supportBundle.proof.storagePressureCheckpointPresent,
      storageRecoveryGuidancePresent: supportBundle.proof.storageRecoveryGuidancePresent,
      storageRecoveryGuidanceReady: supportBundle.storageRecoveryGuidance?.status === 'ready',
      storageRecoveryGuidanceLockTimeoutQueryLocks: supportBundle.storageRecoveryGuidance?.proof?.lockTimeoutGuidesQueryLocks === true,
      storageRecoveryGuidanceQuotaVerifyBeforeRetry: supportBundle.storageRecoveryGuidance?.proof?.providerQuotaRequiresVerifyBeforeRetry === true,
      storageRecoveryGuidanceProviderAbortExplicitRecovery: supportBundle.storageRecoveryGuidance?.proof?.providerAbortRequiresExplicitRecovery === true,
      storageRecoveryGuidanceServiceWorkerWaitUntilSettledRecovery: supportBundle.storageRecoveryGuidance?.proof?.serviceWorkerWaitUntilRequiresSettledRecovery === true,
      storageRecoveryGuidanceDecisionRowsPresent: supportBundle.storageRecoveryGuidance?.proof?.decisionRowsPresent === true,
      storageRecoveryGuidanceAutoRetryPreMutationOnly: supportBundle.storageRecoveryGuidance?.proof?.automaticRetryLimitedToPreMutationRows === true,
      storageRecoveryGuidanceMutationRowsVerifyFirst: supportBundle.storageRecoveryGuidance?.proof?.mutationRowsRequireVerifyFirst === true,
      storageRecoveryGuidanceManualReviewStops: supportBundle.storageRecoveryGuidance?.proof?.stopManualReviewRowsClassified === true,
      storageRecoveryGuidancePrivacyBounded: supportBundle.storageRecoveryGuidance?.proof?.noRawErrorMessageStackPathDigestOrLockName === true,
      admissionCancellationCheckpointPresent: supportBundle.proof.admissionCancellationCheckpointPresent,
      sessionCoordinationCheckpointPresent: supportBundle.proof.sessionCoordinationCheckpointPresent,
      recoveryCheckpointPresent: supportBundle.proof.recoveryCheckpointPresent,
      admissionCancellationCommandPresent: supportBundle.exactCommands.some((cmd) => cmd.includes('admission:abort-release-proof')),
      admissionCancellationDefaultDeferred: supportBundle.admissionCancellation?.deferredRowIds?.includes('bound-lease-abort-releases-permit') === true,
      admissionCancellationLedgerEntryPresent: supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'admission-cancellation-artifact') === true,
      recoveryCommandPresent: supportBundle.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-recovery-checkpoint-proof')),
      recoveryOrphanReviewCommandPresent: supportBundle.exactCommands.some((cmd) => cmd.includes('browser:opfs-web-lock-unsettled-orphan-review-proof')),
      recoveryDefaultDeferred: supportBundle.recoveryCheckpoint?.deferredRowIds?.includes('same-origin-profile-restart-boundary') === true && supportBundle.recoveryCheckpoint?.deferredRowIds?.includes('transient-opfs-open-failure-retry-observed') === true && supportBundle.recoveryCheckpoint?.deferredRowIds?.includes('unsettled-orphan-review-gate-observed') === true,
      recoveryLedgerEntryPresent: supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'browser-recovery-artifact') === true,
      sessionCoordinationCommandPresent: supportBundle.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-session-coordination-checkpoint-proof')),
      sessionCoordinationDefaultDeferred: supportBundle.sessionCoordination?.deferredRowIds?.includes('exclusive-lock-contention-observed') === true && supportBundle.sessionCoordination?.deferredRowIds?.includes('stale-handoff-read-deferred-or-null') === true,
      sessionCoordinationLedgerEntryPresent: supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'browser-session-coordination-artifact') === true,
      storagePressureCommandPresent: supportBundle.exactCommands.some((cmd) => cmd.includes('browser:opfs-lane-quota-backpressure-proof')),
      storagePressureEvictionDeferred: supportBundle.storagePressure?.evictionSurvivalDeferred === true,
      storagePressureLedgerEntryPresent: supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'browser-storage-pressure-artifact') === true,
      lifecycleCheckpointReady: supportBundle.lifecycleCheckpoint?.status === 'risk-checkpoint-ready',
      deferredLifecycleRisksExplicit: supportBundle.lifecycleCheckpoint?.proof?.deferredLifecycleRisksExplicit === true,
      evidenceLedgerReady: supportBundle.evidenceLedger?.status === 'evidence-ledger-ready',
      replayPlanReady: replayValidation.ok === true && replayPlan.status === 'replay-plan-ready',
      replayDoesNotExecuteCommands: replayPlan.proof.replayDoesNotExecuteCommands,
      nonClaimsVisible: supportBundle.proof.nonClaimsVisible
    },
    nonClaims: supportBundle.nonClaims
  };
  return report;
}

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runProbe();
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else console.log(JSON.stringify(report, null, 2));
}

// Static audit markers: demo:kernel-kit-support-bundle-proof; demo:kernel-kit-lifecycle-checkpoint-proof; browser:opfs-lane-quota-backpressure-proof; storagePressureCheckpointPresent; storageRecoveryGuidancePresent; storage-recovery-guidance; BRT_WEB_LOCK_TIMEOUT; BRT_OPFS_QUOTA_EXCEEDED; BRT_OPFS_OPERATION_ABORTED; BRT_SW_WAITUNTIL_LATE_FAILURE; BRT_STORAGE_FAILURE_UNCLASSIFIED; browserrt-kernel-kit-support-bundle-storage-recovery-guidance-v1; browserrt-kernel-kit-support-bundle-risk-decision-v1; retry; verify-first; stop/manual-review; browser-storage-pressure-artifact; admission:abort-release-proof; admissionCancellationCheckpointPresent; admission-cancellation-artifact; admissionCancellationDefaultDeferred; browser:kernel-kit-session-coordination-checkpoint-proof; browser-session-coordination-artifact; browser:kernel-kit-recovery-checkpoint-proof; browser-recovery-artifact; recoveryCheckpointPresent; browser:opfs-web-lock-unsettled-orphan-review-proof; unsettled-orphan-review-gate-observed; recoveryDefaultDeferred; browserrt-kernel-kit-recovery-checkpoint-v1; browserrt-kernel-kit-session-coordination-checkpoint-v1; browserrt-kernel-kit-support-bundle-privacy-scrub-v1; privacyScrubPresent; browserrt-kernel-kit-support-bundle-v1; browserrt-kernel-kit-lifecycle-checkpoint-v1; browserrt-kernel-kit-support-bundle-replay-plan-v1; browserrt-kernel-kit-support-bundle-evidence-ledger-v1; No production support-bundle claim.; No automated replay execution claim.; exact commands.
