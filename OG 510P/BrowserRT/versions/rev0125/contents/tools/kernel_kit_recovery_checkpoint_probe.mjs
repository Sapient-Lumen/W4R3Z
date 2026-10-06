#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-recovery-checkpoint-proof. Release-light proof for the Kernel Kit recovery checkpoint.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitRecoveryCheckpoint,
  validateKernelKitRecoveryCheckpoint,
  validateKernelKitSupportBundle,
  validateKernelKitLifecycleCheckpoint,
  KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS
} from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function observedRecoveryInput() {
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    status: 'passed',
    source: 'synthetic-browser-heavy-recovery-summary',
    commandId: 'browser:kernel-kit-recovery-checkpoint-proof',
    tier: 'browser-heavy-explicit',
    proof: Object.freeze({
      browserHeavyExplicit: true,
      sameOriginTwoLaunch: true,
      profileReusedAcrossKill: true,
      sigkillObserved: true,
      acknowledgedBlocksVerifiedAfterRestart: true,
      interruptedWriteNotAcceptedCorrupt: true,
      restartCleanupObserved: true,
      openFailureRootPromiseReset: true,
      openRetrySucceeded: true,
      putRetryVerified: true,
      guardedLockDrainedAfterFailure: true,
      unsettledOrphanReviewGateObserved: true,
      importedUnsettledOrphanBlocksRecovery: true,
      orphanReviewManifestRequired: true,
      orphanStaleFingerprintRejected: true,
      orphanReviewScopeOverrideRejected: true,
      reviewedOrphanFinalizationObserved: true,
      orphanLateFailureFreshReviewRequired: true,
      orphanFreshReviewClearedAndRecovered: true,
      guardedLocksDrainAfterOrphanReview: true,
      crashDurabilityNonClaimsVisible: true,
      crossBrowserNonClaimsVisible: true
    }),
    nonClaims: KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS
  });
}

export async function runProbe() {
  const exactCommands = [
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-recovery-checkpoint-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-recovery-checkpoint-audit --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-recovery-checkpoint-proof --jobs 1'
  ];
  const observedInput = observedRecoveryInput();
  const checkpoint = createKernelKitRecoveryCheckpoint({ recovery: observedInput, exactCommands, nonClaims: KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS }, { revision: REVISION, generatedAt: 'deterministic-kernel-kit-recovery-checkpoint-probe' });
  const validation = validateKernelKitRecoveryCheckpoint(checkpoint);

  const defaultCheckpoint = createKernelKitRecoveryCheckpoint({ exactCommands, nonClaims: KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS }, { revision: REVISION, generatedAt: 'deterministic-kernel-kit-recovery-default-deferred' });
  const defaultValidation = validateKernelKitRecoveryCheckpoint(defaultCheckpoint);

  const supportProof = await runSupportBundleProbe();
  const supportBundle = supportProof.supportBundle;
  const supportValidation = validateKernelKitSupportBundle(supportBundle);
  const lifecycleValidation = validateKernelKitLifecycleCheckpoint(supportBundle.lifecycleCheckpoint);

  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(checkpoint.status, 'risk-checkpoint-ready');
  assert.equal(checkpoint.proof.sameOriginProfileRestartObserved, true);
  assert.equal(checkpoint.proof.interruptedWriteNotAcceptedCorrupt, true);
  assert.equal(checkpoint.proof.transientOpenFailureRetryObserved, true);
  assert.equal(checkpoint.proof.unsettledOrphanReviewGateObserved, true);
  assert.equal(checkpoint.proof.crashDurabilityNonClaimsVisible, true);
  assert.equal(defaultValidation.ok, true, defaultValidation.errors.join('; '));
  assert.ok(defaultCheckpoint.deferredRowIds.includes('same-origin-profile-restart-boundary'), 'default checkpoint should defer browser-heavy restart boundary');
  assert.ok(defaultCheckpoint.deferredRowIds.includes('transient-opfs-open-failure-retry-observed'), 'default checkpoint should defer browser-heavy open-failure retry');
  assert.ok(defaultCheckpoint.deferredRowIds.includes('unsettled-orphan-review-gate-observed'), 'default checkpoint should defer browser-heavy unsettled orphan review gate');
  assert.equal(supportValidation.ok, true, supportValidation.errors.join('; '));
  assert.equal(supportBundle.proof.recoveryCheckpointPresent, true);
  assert.equal(supportBundle.recoveryCheckpoint.commandId, 'browser:kernel-kit-recovery-checkpoint-proof');
  assert.equal(lifecycleValidation.ok, true, lifecycleValidation.errors.join('; '));
  assert.equal(supportBundle.lifecycleCheckpoint.proof.recoveryObservedOrDeferred, true);
  assert.ok(supportBundle.lifecycleCheckpoint.deferredRowIds.includes('recovery-interruption-boundary-evidence'));
  assert.ok(supportBundle.evidenceLedger.entries.some((entry) => entry.id === 'browser-recovery-artifact'));

  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-recovery-checkpoint-probe`,
    status: 'passed',
    purpose: 'Build and validate the Kernel Kit recovery checkpoint: synthetic observed browser-heavy recovery summary plus default support-bundle deferred state, without launching Chromium in release-light mode.',
    checkpoint,
    validation,
    defaultCheckpoint: Object.freeze({ status: defaultCheckpoint.status, observedRowIds: defaultCheckpoint.observedRowIds, deferredRowIds: defaultCheckpoint.deferredRowIds, proof: defaultCheckpoint.proof }),
    supportBundle: Object.freeze({ status: 'created', validation: supportValidation, recoveryCheckpoint: supportBundle.recoveryCheckpoint, lifecycleCheckpoint: Object.freeze({ status: supportBundle.lifecycleCheckpoint.status, proof: supportBundle.lifecycleCheckpoint.proof, deferredRowIds: supportBundle.lifecycleCheckpoint.deferredRowIds }), evidenceLedger: Object.freeze({ status: supportBundle.evidenceLedger.status, entries: supportBundle.evidenceLedger.entries.map((entry) => ({ id: entry.id, taskId: entry.taskId, outputPath: entry.outputPath })) }) }),
    proof: Object.freeze({
      syntheticObservedCheckpointValid: validation.ok === true && checkpoint.proof.sameOriginProfileRestartObserved === true && checkpoint.proof.transientOpenFailureRetryObserved === true && checkpoint.proof.unsettledOrphanReviewGateObserved === true,
      supportBundleDefaultDeferredValid: defaultValidation.ok === true && defaultCheckpoint.deferredRowIds.includes('same-origin-profile-restart-boundary'),
      supportBundleCarriesRecoveryCheckpoint: supportBundle.proof.recoveryCheckpointPresent === true && supportBundle.recoveryCheckpoint.commandId === 'browser:kernel-kit-recovery-checkpoint-proof',
      lifecycleCarriesRecoveryRisk: supportBundle.lifecycleCheckpoint.proof.recoveryObservedOrDeferred === true,
      evidenceLedgerNamesBrowserRecoveryArtifact: supportBundle.evidenceLedger.entries.some((entry) => entry.id === 'browser-recovery-artifact'),
      sameOriginProfileRestartObserved: checkpoint.proof.sameOriginProfileRestartObserved === true,
      sigkillBoundaryObserved: checkpoint.proof.sigkillBoundaryObserved === true,
      interruptedWriteNotAcceptedCorrupt: checkpoint.proof.interruptedWriteNotAcceptedCorrupt === true,
      transientOpenFailureRetryObserved: checkpoint.proof.transientOpenFailureRetryObserved === true,
      unsettledOrphanReviewGateObserved: checkpoint.proof.unsettledOrphanReviewGateObserved === true,
      crashDurabilityNonClaimsVisible: checkpoint.proof.crashDurabilityNonClaimsVisible === true,
      crossBrowserNonClaimsVisible: checkpoint.proof.crossBrowserNonClaimsVisible === true
    }),
    nonClaims: checkpoint.nonClaims
  });
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

// Static audit markers: demo:kernel-kit-recovery-checkpoint-proof; browser:kernel-kit-recovery-checkpoint-proof; browserrt-kernel-kit-recovery-checkpoint-v1; interrupted-write-not-silently-corrupt; transient-opfs-open-failure-retry-observed; unsettled-orphan-review-gate-observed; No general crash recovery, power-loss, kernel panic, drive-cache flush, fsync, or transactional durability claim.
