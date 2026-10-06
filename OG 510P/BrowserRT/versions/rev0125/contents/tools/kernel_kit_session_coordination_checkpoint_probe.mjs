#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-session-coordination-checkpoint-proof. Release-tier proof for the Kernel Kit session coordination risk checkpoint.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitSessionCoordinationCheckpoint,
  validateKernelKitSessionCoordinationCheckpoint,
  KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT,
  KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS,
  validateKernelKitSupportBundle,
  validateKernelKitLifecycleCheckpoint
} from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function syntheticObservedCoordination() {
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    status: 'passed',
    source: `${REVISION}-synthetic-browser-session-coordination-summary`,
    probe_id: `${REVISION}-browser-kernel-kit-session-coordination-checkpoint-probe`,
    commandId: 'browser:kernel-kit-session-coordination-checkpoint-proof',
    tier: 'browser-heavy-explicit',
    origin: 'http://127.0.0.1:43107',
    sameOriginPages: true,
    lockContention: Object.freeze({
      sameOrigin: true,
      navigatorLocksSeen: true,
      ifAvailable: Object.freeze({ acquired: false }),
      queue: Object.freeze({ waitedUntilRelease: true, acquiredAfterRelease: true }),
      queryAfter: Object.freeze({ drained: true, heldCount: 0, pendingCount: 0 })
    }),
    handoff: Object.freeze({
      storageEvent: Object.freeze({ observed: true, setEventSeen: true, clearEventSeen: true }),
      singleUseClearObserved: true,
      afterConsume: Object.freeze({ value: null }),
      staleReadReturnedNull: true
    }),
    proof: Object.freeze({
      sameOriginPages: true,
      sameOriginSessionScopeVisible: true,
      navigatorLocksSeen: true,
      exclusiveIfAvailableDenied: true,
      queuedWaitedUntilRelease: true,
      queuedAcquiredAfterRelease: true,
      locksDrainedAfterUse: true,
      crossTabStorageEventObserved: true,
      handoffSingleUseClearObserved: true,
      staleReadReturnedNull: true,
      noFairnessClaim: true,
      noCrashRecoveryClaim: true,
      browserHeavyExplicit: true,
      abandonedLockReleaseClaimed: false
    }),
    nonClaims: KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS
  });
}

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
    proof: checkpoint.proof,
    summary: checkpoint.summary,
    nonClaims: checkpoint.nonClaims
  });
}

export async function runProbe() {
  const exactCommands = Object.freeze(['node tools/run_tests.mjs --tier browser --id browser:kernel-kit-session-coordination-checkpoint-proof --jobs 1']);
  const observedInput = syntheticObservedCoordination();
  const checkpoint = createKernelKitSessionCoordinationCheckpoint({
    sessionCoordination: observedInput,
    exactCommands,
    nonClaims: KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_NON_CLAIMS
  }, { revision: REVISION, generatedAt: 'deterministic-session-coordination-checkpoint-probe', source: 'kernel-kit-session-coordination-checkpoint-probe' });
  const validation = validateKernelKitSessionCoordinationCheckpoint(checkpoint);
  assert.equal(checkpoint.format, KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(checkpoint.status, 'risk-checkpoint-ready');
  assert.equal(checkpoint.proof.exclusiveLockContentionObservedOrDeferred, true);
  assert.equal(checkpoint.proof.queuedLockReleaseOrderObservedOrDeferred, true);
  assert.equal(checkpoint.proof.localHandoffSingleUseClearObservedOrDeferred, true);
  assert.equal(checkpoint.proof.staleHandoffReadNullObservedOrDeferred, true);
  assert.equal(checkpoint.proof.abandonedLockReleaseDeferred, true);
  assert.ok(checkpoint.observedRowIds.includes('exclusive-lock-contention-observed'));
  assert.ok(checkpoint.deferredRowIds.includes('abandoned-lock-release-deferred'));

  const supportProof = await runSupportBundleProbe();
  const supportBundle = supportProof.supportBundle;
  const supportValidation = validateKernelKitSupportBundle(supportBundle);
  assert.equal(supportValidation.ok, true, supportValidation.errors.join('; '));
  assert.equal(supportBundle.proof.sessionCoordinationCheckpointPresent, true);
  assert.equal(supportBundle.sessionCoordination?.commandId, 'browser:kernel-kit-session-coordination-checkpoint-proof');
  assert.equal(supportBundle.sessionCoordination?.status, 'risk-checkpoint-ready');
  assert.ok(supportBundle.sessionCoordination?.deferredRowIds?.includes('exclusive-lock-contention-observed'));
  assert.ok(supportBundle.sessionCoordination?.deferredRowIds?.includes('stale-handoff-read-deferred-or-null'));
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-session-coordination-checkpoint-proof')));
  assert.ok(supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'browser-session-coordination-artifact'));
  const lifecycleValidation = validateKernelKitLifecycleCheckpoint(supportBundle.lifecycleCheckpoint);
  assert.equal(lifecycleValidation.ok, true, lifecycleValidation.errors.join('; '));
  assert.equal(supportBundle.lifecycleCheckpoint?.proof?.sessionCoordinationObservedOrDeferred, true);
  assert.ok(supportBundle.lifecycleCheckpoint?.deferredRowIds?.includes('session-coordination-stale-handoff-evidence'));

  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-session-coordination-checkpoint-probe`,
    status: 'passed',
    checkpoint: compactCheckpoint(checkpoint, validation),
    validation,
    supportBundleSessionCoordination: Object.freeze({
      status: supportBundle.sessionCoordination?.status || null,
      commandId: supportBundle.sessionCoordination?.commandId || null,
      observedRowIds: supportBundle.sessionCoordination?.observedRowIds || [],
      deferredRowIds: supportBundle.sessionCoordination?.deferredRowIds || [],
      validationOk: supportBundle.sessionCoordination?.validationOk === true
    }),
    lifecycleSessionCoordination: Object.freeze({
      status: supportBundle.lifecycleCheckpoint?.status || null,
      validationOk: lifecycleValidation.ok === true,
      sessionCoordinationObservedOrDeferred: supportBundle.lifecycleCheckpoint?.proof?.sessionCoordinationObservedOrDeferred === true,
      rowDeferred: supportBundle.lifecycleCheckpoint?.deferredRowIds?.includes('session-coordination-stale-handoff-evidence') === true
    }),
    proof: Object.freeze({
      syntheticObservedCheckpointValid: validation.ok === true,
      supportBundleDefaultDeferredValid: supportValidation.ok === true && supportBundle.sessionCoordination?.validationOk === true,
      browserHeavyCommandVisible: supportBundle.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-session-coordination-checkpoint-proof')),
      browserSessionCoordinationLedgerEntryPresent: supportBundle.evidenceLedger?.entries?.some((entry) => entry.id === 'browser-session-coordination-artifact') === true,
      lifecycleCarriesSessionCoordinationRisk: supportBundle.lifecycleCheckpoint?.proof?.sessionCoordinationObservedOrDeferred === true,
      exclusiveIfAvailableDenied: observedInput.proof.exclusiveIfAvailableDenied === true,
      queuedAcquiredAfterRelease: observedInput.proof.queuedAcquiredAfterRelease === true,
      handoffSingleUseClearObserved: observedInput.proof.handoffSingleUseClearObserved === true,
      staleReadReturnedNull: observedInput.proof.staleReadReturnedNull === true,
      abandonedLockReleaseDeferred: checkpoint.proof.abandonedLockReleaseDeferred === true,
      fairnessNonClaimVisible: checkpoint.nonClaims.some((claim) => claim.includes('fairness')),
      crashRecoveryNonClaimVisible: checkpoint.nonClaims.some((claim) => claim.includes('crash'))
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

// Static audit markers: demo:kernel-kit-session-coordination-checkpoint-proof; browser:kernel-kit-session-coordination-checkpoint-proof; browserrt-kernel-kit-session-coordination-checkpoint-v1; exclusive-lock-contention-observed; stale-handoff-read-deferred-or-null; No Web Locks fairness, starvation-freedom, or scheduler ordering claim.; No crash, process-kill, browser-restart, or abandoned-native-I/O recovery claim.
