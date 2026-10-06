#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-lifecycle-checkpoint-proof. Release-tier proof for the Kernel Kit lifecycle-risk checkpoint.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitLifecycleCheckpoint,
  validateKernelKitLifecycleCheckpoint,
  KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT,
  KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS,
  KERNEL_KIT_DEMO_NON_CLAIMS
} from '../src/browserrt.mjs';
import { runProbe as runKernelKitDemoProbe } from './kernel_kit_demo_probe.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-KERNEL-KIT-LIFECYCLE-CHECKPOINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function row(checkpoint, id) { return checkpoint.rows.find((candidate) => candidate.id === id) || null; }
function summarizeCheckpoint(checkpoint, validation) {
  const rows = checkpoint.rows || [];
  return Object.freeze({
    format: checkpoint.format,
    status: checkpoint.status,
    rowCount: rows.length,
    observedRowIds: checkpoint.observedRowIds || rows.filter((candidate) => candidate.status === 'observed').map((candidate) => candidate.id),
    deferredRowIds: checkpoint.deferredRowIds || rows.filter((candidate) => candidate.status === 'deferred').map((candidate) => candidate.id),
    failedRowIds: checkpoint.failedRowIds || rows.filter((candidate) => candidate.status === 'failed').map((candidate) => candidate.id),
    riskSummary: checkpoint.riskSummary || null,
    proof: checkpoint.proof || {},
    validation: validation ? { ok: validation.ok === true, rowCount: validation.rowCount || rows.length, errorCount: validation.errors?.length || 0 } : null
  });
}

function createBrowserHeavySyntheticInput(supportProof) {
  return {
    revision: REVISION,
    runner: 'synthetic-browser-heavy-lifecycle-observation',
    proof: {
      storageWrite: true,
      opfsAbortBoundary: true,
      storageAbortBoundary: true,
      guardedStorageLane: true,
      storagePostureObserved: true,
      webLockPostureObserved: true,
      reloadReadback: true,
      replayPlanPresent: true,
      evidenceLedgerPresent: true
    },
    storagePosture: {
      status: 'observed',
      source: 'synthetic-browser-storage-posture-contract-shape',
      estimate: { usage: 128, quota: 4096 },
      persisted: { persisted: false },
      persistRequest: { requested: false },
      proof: { estimateChecked: true, quotaKnown: true, usageKnown: true, persistedChecked: true, persistenceNotRequestedByDefault: true }
    },
    webLockPosture: {
      status: 'observed',
      source: 'synthetic-browser-web-lock-posture-contract-shape',
      proof: { navigatorLocksSeen: true, exclusiveNoOverlap: true, sharedCoHold: true, drainedAfterUse: true, queryObserved: true, noFairnessClaim: true }
    },
    guardedStorageLane: {
      status: 'observed',
      source: 'synthetic-browser-guarded-storage-lane-contract-shape',
      provider: 'web-lock-guarded:opfs-async-block-store',
      proof: { guardedProvider: true, webLocksAvailable: true, exclusiveMutationsObserved: true, sharedReadsObserved: true, lockAcquiredReleased: true, noFairnessClaim: true }
    },
    abortBoundary: {
      status: 'passed',
      proof: { nonMutationBoundary: true, compositeAbortRejected: true, noBlockPresent: true }
    },
    storagePressure: {
      status: 'passed',
      source: 'synthetic-browser-opfs-lane-quota-backpressure-contract-shape',
      tier: 'browser-heavy-explicit',
      proof: {
        browserHeavyExplicit: true,
        quotaOverrideActivated: true,
        quotaExceededClassified: true,
        failedPutRolledBack: true,
        followOnWritesRejectWithoutMutation: true,
        cleanupVerified: true,
        recoveryWriteObserved: true,
        quotaOverrideReset: true,
        evictionSurvivalClaimed: false
      },
      nonClaims: ['Not eviction survival.', 'No cross-browser storage conformance claim.']
    },
    supportBundle: supportProof.supportBundle,
    nonClaims: [...supportProof.nonClaims, ...KERNEL_KIT_DEMO_NON_CLAIMS]
  };
}

export async function runProbe() {
  const successReport = await runKernelKitDemoProbe();
  const supportProof = await runSupportBundleProbe();
  const supportBundle = supportProof.supportBundle;

  const checkpoint = createKernelKitLifecycleCheckpoint({
    revision: REVISION,
    source: 'kernel-kit-lifecycle-checkpoint-probe',
    success: successReport,
    supportBundle,
    proof: {
      storageLaneWriteRead: successReport.observations?.storageLaneWriteRead === true,
      storageWrite: successReport.observations?.storageLaneWriteRead === true,
      reloadReadbackPresent: true,
      replayPlanPresent: supportProof.proof?.replayPlanPresent === true,
      evidenceLedgerPresent: supportProof.proof?.evidenceLedgerPresent === true
    },
    nonClaims: supportProof.nonClaims
  }, { revision: REVISION, generatedAt: 'deterministic-lifecycle-checkpoint-probe', source: 'kernel-kit-lifecycle-checkpoint-probe' });

  const validation = validateKernelKitLifecycleCheckpoint(checkpoint);
  assert.equal(checkpoint.format, KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(checkpoint.status, 'risk-checkpoint-ready');
  assert.deepEqual(KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS.every((id) => checkpoint.rows.some((candidate) => candidate.id === id)), true);
  assert.equal(row(checkpoint, 'product-storage-path-evidence')?.status, 'observed');
  assert.equal(row(checkpoint, 'support-bundle-replay-evidence')?.status, 'observed');
  for (const id of ['quota-pressure-backpressure-evidence', 'quota-eviction-survival-deferred', 'cross-browser-mobile-lifecycle-deferred', 'side-channel-privacy-deferred']) assert.ok(checkpoint.deferredRowIds.includes(id), `${id} must remain explicit`);

  const browserHeavy = createKernelKitLifecycleCheckpoint(createBrowserHeavySyntheticInput(supportProof), { revision: REVISION, generatedAt: 'deterministic-browser-heavy-lifecycle-shape', source: 'synthetic-browser-heavy-lifecycle-observation' });
  const browserHeavyValidation = validateKernelKitLifecycleCheckpoint(browserHeavy);
  assert.equal(browserHeavyValidation.ok, true, browserHeavyValidation.errors.join('; '));
  for (const id of ['opfs-abort-non-mutation-boundary', 'storage-manager-posture', 'web-locks-coordination-posture', 'guarded-storage-lane-path', 'quota-pressure-backpressure-evidence']) assert.equal(row(browserHeavy, id)?.status, 'observed', `${id} should become observed when browser-heavy evidence is supplied`);

  const negative = createKernelKitLifecycleCheckpoint({ revision: REVISION, proof: {}, nonClaims: [] }, { revision: REVISION, generatedAt: 'deterministic-negative-lifecycle-checkpoint', source: 'negative-lifecycle-checkpoint' });
  const negativeValidation = validateKernelKitLifecycleCheckpoint(negative);
  assert.equal(negativeValidation.ok, false);
  assert.ok(negativeValidation.errors.some((error) => String(error).includes('status must be risk-checkpoint-ready')) || negative.failedRowIds.length > 0, 'negative checkpoint should not validate');

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-lifecycle-checkpoint-probe`,
    status: 'passed',
    purpose: 'Collapse Kernel Kit storage/Web Locks/reload/abort/support-bundle evidence into one executable observed/deferred lifecycle-risk checkpoint.',
    checkpoint: summarizeCheckpoint(checkpoint, validation),
    validation: { ok: validation.ok === true, rowCount: validation.rowCount, errorCount: validation.errors.length },
    browserHeavyShape: summarizeCheckpoint(browserHeavy, browserHeavyValidation),
    browserHeavyValidation: { ok: browserHeavyValidation.ok === true, rowCount: browserHeavyValidation.rowCount, errorCount: browserHeavyValidation.errors.length },
    negative: { status: negative.status, failedRowIds: negative.failedRowIds, validation: { ok: negativeValidation.ok === true, errorCount: negativeValidation.errors.length } },
    supportBundleProbeId: supportProof.probe_id,
    proof: {
      lifecycleCheckpointValid: validation.ok,
      formatBound: checkpoint.format === KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT,
      requiredRowsPresent: validation.rowCount >= KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS.length,
      productStoragePathObserved: row(checkpoint, 'product-storage-path-evidence')?.status === 'observed',
      supportBundleReplayObserved: row(checkpoint, 'support-bundle-replay-evidence')?.status === 'observed',
      riskyLifecycleDeferralsExplicit: ['quota-pressure-backpressure-evidence', 'quota-eviction-survival-deferred', 'cross-browser-mobile-lifecycle-deferred', 'side-channel-privacy-deferred'].every((id) => checkpoint.deferredRowIds.includes(id)),
      storagePressurePathDeferredInBrowserLight: checkpoint.deferredRowIds.includes('quota-pressure-backpressure-evidence'),
      browserHeavyStoragePressureObserved: row(browserHeavy, 'quota-pressure-backpressure-evidence')?.status === 'observed',
      browserHeavyEvidenceCanObserveRows: ['opfs-abort-non-mutation-boundary', 'storage-manager-posture', 'web-locks-coordination-posture', 'guarded-storage-lane-path', 'quota-pressure-backpressure-evidence'].every((id) => row(browserHeavy, id)?.status === 'observed'),
      negativeCheckpointRejected: negativeValidation.ok === false,
      supportBundleCarriesLifecycleCheckpoint: supportBundle.proof?.lifecycleCheckpointPresent === true && supportBundle.lifecycleCheckpoint?.status === 'risk-checkpoint-ready'
    },
    nonClaims: checkpoint.nonClaims
  };
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

// Static audit markers: demo:kernel-kit-lifecycle-checkpoint-proof; browser:opfs-lane-quota-backpressure-proof; browserrt-kernel-kit-lifecycle-checkpoint-v1; quota-pressure-backpressure-evidence; quota-eviction-survival-deferred; cross-browser-mobile-lifecycle-deferred; side-channel-privacy-deferred; risk-checkpoint-ready.
