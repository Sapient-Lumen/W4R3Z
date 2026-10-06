#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-admission-cancellation-checkpoint-proof. Release-light Kernel Kit checkpoint for admission AbortSignal release.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitAdmissionCancellationCheckpoint,
  validateKernelKitAdmissionCancellationCheckpoint,
  validateKernelKitSupportBundle,
  validateKernelKitLifecycleCheckpoint,
  KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT,
  KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS
} from '../src/browserrt.mjs';
import { runProbe as runAdmissionAbortReleaseProbe } from './admission_abort_release_probe.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-KERNEL-KIT-ADMISSION-CANCELLATION-CHECKPOINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function compactCheckpoint(checkpoint, validation) {
  return Object.freeze({
    project: checkpoint.project,
    revision: checkpoint.revision,
    schema: checkpoint.schema,
    format: checkpoint.format,
    checkpointId: checkpoint.checkpointId,
    status: checkpoint.status,
    validationOk: validation.ok === true,
    rows: checkpoint.rows,
    observedRowIds: checkpoint.observedRowIds,
    deferredRowIds: checkpoint.deferredRowIds,
    failedRowIds: checkpoint.failedRowIds,
    missingRequiredRows: checkpoint.missingRequiredRows,
    riskSummary: checkpoint.riskSummary,
    summary: checkpoint.summary,
    proof: checkpoint.proof,
    nonClaims: checkpoint.nonClaims
  });
}

export async function runProbe() {
  const exactCommands = Object.freeze([
    'node tools/run_tests.mjs --tier release --id admission:abort-release-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-admission-cancellation-checkpoint-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-admission-cancellation-checkpoint-audit --jobs 1'
  ]);

  const admissionReport = await runAdmissionAbortReleaseProbe();
  assert.equal(admissionReport.status, 'passed');
  const checkpoint = createKernelKitAdmissionCancellationCheckpoint({ admissionCancellation: admissionReport, exactCommands, nonClaims: KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS }, { revision: REVISION, generatedAt: 'deterministic-kernel-kit-admission-cancellation-checkpoint-probe' });
  const validation = validateKernelKitAdmissionCancellationCheckpoint(checkpoint);
  assert.equal(checkpoint.format, KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(checkpoint.status, 'risk-checkpoint-ready');
  for (const key of ['preAbortedRejectedNoMutation','boundLeaseAbortReleasedPermit','dualSignalAbortSourceReleasesOnce','manualReleaseDetachesAbortListener','congestionRecoversAfterAbortRelease','postAbortBackgroundAdmissionRecovers','invalidSignalShapeRejectedLocally','exactlyOnceNonClaimVisible','browserWorkerNonClaimVisible']) assert.equal(checkpoint.proof[key], true, `proof.${key}`);

  const defaultCheckpoint = createKernelKitAdmissionCancellationCheckpoint({ exactCommands, nonClaims: KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS }, { revision: REVISION, generatedAt: 'deterministic-kernel-kit-admission-cancellation-default-deferred' });
  const defaultValidation = validateKernelKitAdmissionCancellationCheckpoint(defaultCheckpoint);
  assert.equal(defaultValidation.ok, true, defaultValidation.errors.join('; '));
  assert.ok(defaultCheckpoint.deferredRowIds.includes('bound-lease-abort-releases-permit'));

  const supportProof = await runSupportBundleProbe();
  const supportBundle = supportProof.supportBundle;
  const supportValidation = validateKernelKitSupportBundle(supportBundle);
  assert.equal(supportValidation.ok, true, supportValidation.errors.join('; '));
  assert.equal(supportBundle.proof.admissionCancellationCheckpointPresent, true);
  assert.equal(supportBundle.admissionCancellation?.commandId, 'admission:abort-release-proof');
  assert.ok(supportBundle.admissionCancellation?.deferredRowIds?.includes('bound-lease-abort-releases-permit'), 'default support bundle should keep release-light admission abort evidence deferred until artifact is run');
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('admission:abort-release-proof')));
  assert.ok(supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'admission-cancellation-artifact'));
  const lifecycleValidation = validateKernelKitLifecycleCheckpoint(supportBundle.lifecycleCheckpoint);
  assert.equal(lifecycleValidation.ok, true, lifecycleValidation.errors.join('; '));
  assert.equal(supportBundle.lifecycleCheckpoint?.proof?.admissionCancellationObservedOrDeferred, true);
  assert.ok(supportBundle.lifecycleCheckpoint?.deferredRowIds?.includes('admission-cancellation-backpressure-evidence'));

  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-admission-cancellation-checkpoint-probe`,
    status: 'passed',
    admissionAbortRelease: Object.freeze({ status: admissionReport.status, probe_id: admissionReport.probe_id, proof: admissionReport.proof }),
    checkpoint: compactCheckpoint(checkpoint, validation),
    defaultCheckpoint: Object.freeze({ status: defaultCheckpoint.status, validationOk: defaultValidation.ok === true, observedRowIds: defaultCheckpoint.observedRowIds, deferredRowIds: defaultCheckpoint.deferredRowIds }),
    supportBundleAdmissionCancellation: Object.freeze({ status: supportBundle.admissionCancellation?.status || null, commandId: supportBundle.admissionCancellation?.commandId || null, validationOk: supportBundle.admissionCancellation?.validationOk === true, deferredRowIds: supportBundle.admissionCancellation?.deferredRowIds || [] }),
    lifecycleAdmissionCancellation: Object.freeze({ status: supportBundle.lifecycleCheckpoint?.status || null, validationOk: lifecycleValidation.ok === true, admissionCancellationObservedOrDeferred: supportBundle.lifecycleCheckpoint?.proof?.admissionCancellationObservedOrDeferred === true, rowDeferred: supportBundle.lifecycleCheckpoint?.deferredRowIds?.includes('admission-cancellation-backpressure-evidence') === true }),
    proof: Object.freeze({
      admissionAbortReleaseProofPassed: admissionReport.status === 'passed',
      observedCheckpointValid: validation.ok === true,
      defaultDeferredCheckpointValid: defaultValidation.ok === true && defaultCheckpoint.deferredRowIds.includes('bound-lease-abort-releases-permit'),
      supportBundleCarriesAdmissionCancellationCheckpoint: supportBundle.proof.admissionCancellationCheckpointPresent === true,
      admissionCancellationLedgerEntryPresent: supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'admission-cancellation-artifact') === true,
      lifecycleCarriesAdmissionCancellationRisk: supportBundle.lifecycleCheckpoint?.proof?.admissionCancellationObservedOrDeferred === true,
      preAbortedRejectedNoMutation: checkpoint.proof.preAbortedRejectedNoMutation === true,
      boundLeaseAbortReleasedPermit: checkpoint.proof.boundLeaseAbortReleasedPermit === true,
      dualSignalAbortSourceReleasesOnce: checkpoint.proof.dualSignalAbortSourceReleasesOnce === true,
      manualReleaseDetachesAbortListener: checkpoint.proof.manualReleaseDetachesAbortListener === true,
      congestionRecoversAfterAbortRelease: checkpoint.proof.congestionRecoversAfterAbortRelease === true,
      postAbortBackgroundAdmissionRecovers: checkpoint.proof.postAbortBackgroundAdmissionRecovers === true,
      invalidSignalShapeRejectedLocally: checkpoint.proof.invalidSignalShapeRejectedLocally === true,
      exactlyOnceNonClaimVisible: checkpoint.proof.exactlyOnceNonClaimVisible === true,
      browserWorkerNonClaimVisible: checkpoint.proof.browserWorkerNonClaimVisible === true
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

// Static audit markers: demo:kernel-kit-admission-cancellation-checkpoint-proof; admission:abort-release-proof; browserrt-kernel-kit-admission-cancellation-checkpoint-v1; admission-cancellation-backpressure-evidence; admission-cancellation-artifact; pre-aborted-admission-rejects-no-mutation; bound-lease-abort-releases-permit; dual-signal-abort-source-releases-once; No exactly-once execution, task preemption, or universal cancellation guarantee.; No browser Worker, cross-tab, cross-browser, or mobile lifecycle cancellation claim.
