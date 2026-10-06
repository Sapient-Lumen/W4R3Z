#!/usr/bin/env node
// Manifest slice: browser:kernel-kit-recovery-checkpoint-proof. Browser-heavy aggregate recovery checkpoint.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import {
  REVISION,
  VERSION,
  createKernelKitRecoveryCheckpoint,
  validateKernelKitRecoveryCheckpoint,
  KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS
} from '../src/browserrt.mjs';

const TASK_ID = 'browser:kernel-kit-recovery-checkpoint-proof';
const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function runNodeJson(script, outPath, extraArgs = [], { timeoutMs = 90000 } = {}) {
  return new Promise((resolve, reject) => {
    const started = performance.now();
    const child = spawn(process.execPath, [script, '--json', outPath, ...extraArgs], { cwd: process.cwd(), stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => {
      child.kill('SIGKILL');
      reject(new Error(`${script} timed out after ${timeoutMs}ms\nstdout=${stdout}\nstderr=${stderr}`));
    }, timeoutMs);
    child.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
    child.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
    child.on('error', (error) => {
      clearTimeout(timer);
      reject(error);
    });
    child.on('close', async (code, signal) => {
      clearTimeout(timer);
      if (code !== 0) {
        reject(new Error(`${script} exited ${code ?? signal}\nstdout=${stdout}\nstderr=${stderr}`));
        return;
      }
      try {
        const parsed = JSON.parse(await readFile(outPath, 'utf8'));
        resolve({ parsed, code, signal, stdout: stdout.trim(), stderr: stderr.trim(), durationMs: performance.now() - started });
      } catch (error) {
        reject(error);
      }
    });
  });
}

function compactAbruptKill(report) {
  const obs = report.observations || {};
  const write = obs.write || {};
  const restart = obs.restartInspection || {};
  const interrupted = restart.interrupted || {};
  const sigkillObserved = write._teardownMode === 'kill' || (report.harness?.first?.process?.requestedSignals || []).some((signal) => String(signal).includes('SIGKILL'));
  const acknowledgedBlocksVerifiedAfterRestart = Array.isArray(restart.acknowledgedChecks) && restart.acknowledgedChecks.length > 0 && restart.acknowledgedChecks.every((row) => row.hasBefore === true && row.verify?.ok === true && row.digestAfterRead === row.digest);
  const interruptedWriteNotAcceptedCorrupt = !['unexpected-readable-digest-mismatch', 'inspection-error'].includes(String(interrupted.disposition || ''));
  const restartCleanupObserved = restart.cleanup === true && restart.acknowledgedChecks?.every?.((row) => row.deleted === true && row.hasAfter === false) === true && (interrupted.hasBefore !== true || interrupted.hasAfter === false);
  return Object.freeze({
    project: report.project,
    revision: report.revision,
    status: report.status,
    probe_id: report.probe_id,
    source: 'browser_opfs_abrupt_kill_boundary_probe.mjs',
    observations: Object.freeze({
      sameOrigin: obs.sameOrigin === true,
      profileReused: obs.profileReused === true,
      acknowledgedCount: obs.acknowledgedCount || 0,
      interruptedDisposition: interrupted.disposition || null,
      sigkillObserved,
      acknowledgedBlocksVerifiedAfterRestart,
      interruptedWriteNotAcceptedCorrupt,
      restartCleanupObserved
    }),
    proof: Object.freeze({
      sameOriginTwoLaunch: obs.sameOrigin === true,
      profileReusedAcrossKill: obs.profileReused === true,
      sigkillObserved,
      acknowledgedBlocksVerifiedAfterRestart,
      interruptedWriteNotAcceptedCorrupt,
      restartCleanupObserved
    }),
    nonClaims: Object.freeze(report.nonClaims || [])
  });
}

function compactOpenFailure(report) {
  const obs = report.observations || {};
  const openFailureRootPromiseReset = obs.patchInstalled === true && ((obs.afterFirstOpenSnapshot?.stats?.openRetryResets || 0) >= 1 || (obs.afterFirstPutSnapshot?.stats?.openRetryResets || 0) >= 1);
  const openRetrySucceeded = obs.secondOpen?.ok === true;
  const putRetryVerified = obs.secondPut?.ok === true && obs.verify?.ok === true && obs.bytesPreserved === true;
  const guardedLockDrainedAfterFailure = obs.lockSettled?.ok === true && (obs.locksAfterGuarded?.heldCount ?? 0) === 0 && (obs.locksAfterGuarded?.pendingCount ?? 0) === 0;
  return Object.freeze({
    project: report.project,
    revision: report.revision,
    status: report.status,
    probe_id: report.probe_id,
    source: 'browser_opfs_block_store_open_failure_recovery_probe.mjs',
    observations: Object.freeze({
      patchInstalled: obs.patchInstalled === true,
      forcedFailures: obs.forcedFailures || 0,
      openFailureRootPromiseReset,
      openRetrySucceeded,
      putRetryVerified,
      guardedLockDrainedAfterFailure
    }),
    proof: Object.freeze({
      openFailureRootPromiseReset,
      openRetrySucceeded,
      putRetryVerified,
      guardedLockDrainedAfterFailure
    }),
    nonClaims: Object.freeze(report.nonClaims || [])
  });
}


function compactUnsettledOrphanReview(report) {
  const obs = report.observations || {};
  const finalLocks = obs.finalLocks || {};
  const postured = obs.posturedFactory || {};
  const posturedFactoryObserved = postured.status === 'admitted-and-guarded'
    && postured.admissionStatus === 'admit-with-guard'
    && postured.writeBudgetGuardSource === 'browser-storage-posture-admission-policy'
    && postured.lockContentionPolicySource === 'postured-web-lock-guarded-opfs-factory';
  const importedUnsettledBlocksRecovery = obs.blockedUnsettled?.recovered === false && obs.blockedUnsettled?.reason === 'timed-out-operation-still-unsettled';
  const orphanReviewManifestRequired = obs.unsafeFinalize?.code === 'timed-out-quarantine-finalize-review-required';
  const orphanStaleFingerprintRejected = obs.staleFinalize?.code === 'timed-out-quarantine-finalize-review-fingerprint-mismatch' && obs.oldReviewClear?.code === 'timed-out-quarantine-clear-review-fingerprint-mismatch';
  const orphanReviewScopeOverrideRejected = obs.scopeOverrideClear?.code === 'timed-out-quarantine-finalize-review-manifest-scope-override' && obs.countMismatchClear?.code === 'timed-out-quarantine-finalize-review-manifest-count-mismatch';
  const reviewedOrphanFinalizationObserved = obs.finalized?.ok === true && Number(obs.finalized?.finalizedCount || 0) >= 1 && obs.finalized?.finalized?.[0]?.error?.code === 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED';
  const orphanLateFailureFreshReviewRequired = obs.blockedLateFailure?.recovered === false && obs.blockedLateFailure?.reason === 'timed-out-operation-late-failure' && obs.oldReviewClear?.ok === false;
  const orphanFreshReviewClearedAndRecovered = obs.cleared?.ok === true && Number(obs.cleared?.failedClearedCount || 0) >= 1 && obs.recovered?.recovered === true && obs.recoveryResult?.ok === true && obs.recoveryVerify?.ok === true;
  const guardedLocksDrainAfterOrphanReview = obs.cleanupAfter === true && (finalLocks.heldCount ?? 0) === 0 && (finalLocks.pendingCount ?? 0) === 0;
  const unsettledOrphanReviewGateObserved = importedUnsettledBlocksRecovery
    && orphanReviewManifestRequired
    && orphanStaleFingerprintRejected
    && orphanReviewScopeOverrideRejected
    && reviewedOrphanFinalizationObserved
    && orphanLateFailureFreshReviewRequired
    && orphanFreshReviewClearedAndRecovered
    && guardedLocksDrainAfterOrphanReview;
  return Object.freeze({
    project: report.project,
    revision: report.revision,
    status: report.status,
    probe_id: report.probe_id,
    task_id: report.task_id,
    source: 'browser_opfs_web_lock_unsettled_orphan_review_probe.mjs',
    observations: Object.freeze({
      importedUnsettledBlocksRecovery,
      orphanReviewManifestRequired,
      orphanStaleFingerprintRejected,
      orphanReviewScopeOverrideRejected,
      reviewedOrphanFinalizationObserved,
      orphanLateFailureFreshReviewRequired,
      orphanFreshReviewClearedAndRecovered,
      guardedLocksDrainAfterOrphanReview,
      posturedFactoryObserved,
      posturedFactory: Object.freeze({
        status: postured.status || null,
        admissionStatus: postured.admissionStatus || null,
        writeBudgetGuardSource: postured.writeBudgetGuardSource || null,
        lockContentionPolicySource: postured.lockContentionPolicySource || null,
        lockTimeoutMs: postured.lockTimeoutMs ?? null
      }),
      traceKinds: (obs.traceKinds || []).filter((kind) => String(kind).includes('orphan') || String(kind).includes('quarantine')).slice(0, 8)
    }),
    proof: Object.freeze({
      unsettledOrphanReviewGateObserved,
      importedUnsettledOrphanBlocksRecovery: importedUnsettledBlocksRecovery,
      orphanReviewManifestRequired,
      orphanStaleFingerprintRejected,
      orphanReviewScopeOverrideRejected,
      reviewedOrphanFinalizationObserved,
      orphanLateFailureFreshReviewRequired,
      orphanFreshReviewClearedAndRecovered,
      guardedLocksDrainAfterOrphanReview,
      posturedFactoryObserved
    }),
    nonClaims: Object.freeze(report.nonClaims || [])
  });
}

export async function runProbe(options = {}) {
  const tmp = await mkdtemp(join(tmpdir(), 'browserrt-kernel-kit-recovery-'));
  const started = performance.now();
  try {
    const abruptOut = join(tmp, 'abrupt-kill.json');
    const openOut = join(tmp, 'open-failure.json');
    const orphanOut = join(tmp, 'unsettled-orphan-review.json');
    const relaxArgs = options.relaxPolicy === false ? ['--no-policy-relaxation'] : [];
    const abrupt = await runNodeJson('tools/browser_opfs_abrupt_kill_boundary_probe.mjs', abruptOut, ['--timeout-ms', String(options.abruptTimeoutMs || 60000), ...relaxArgs], { timeoutMs: options.outerAbruptTimeoutMs || 90000 });
    const open = await runNodeJson('tools/browser_opfs_block_store_open_failure_recovery_probe.mjs', openOut, relaxArgs, { timeoutMs: options.outerOpenTimeoutMs || 45000 });
    const orphan = await runNodeJson('tools/browser_opfs_web_lock_unsettled_orphan_review_probe.mjs', orphanOut, ['--timeout-ms', String(options.orphanTimeoutMs || 22000), ...relaxArgs], { timeoutMs: options.outerOrphanTimeoutMs || 50000 });
    const abruptCompact = compactAbruptKill(abrupt.parsed);
    const openCompact = compactOpenFailure(open.parsed);
    const orphanCompact = compactUnsettledOrphanReview(orphan.parsed);
    const recoveryInput = Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      status: 'passed',
      source: 'browser-kernel-kit-recovery-checkpoint-aggregate',
      commandId: TASK_ID,
      tier: 'browser-heavy-explicit',
      abruptKillBoundary: abruptCompact,
      openFailureRecovery: openCompact,
      unsettledOrphanReview: orphanCompact,
      proof: Object.freeze({
        browserHeavyExplicit: true,
        sameOriginTwoLaunch: abruptCompact.proof.sameOriginTwoLaunch,
        profileReusedAcrossKill: abruptCompact.proof.profileReusedAcrossKill,
        sigkillObserved: abruptCompact.proof.sigkillObserved,
        acknowledgedBlocksVerifiedAfterRestart: abruptCompact.proof.acknowledgedBlocksVerifiedAfterRestart,
        interruptedWriteNotAcceptedCorrupt: abruptCompact.proof.interruptedWriteNotAcceptedCorrupt,
        restartCleanupObserved: abruptCompact.proof.restartCleanupObserved,
        openFailureRootPromiseReset: openCompact.proof.openFailureRootPromiseReset,
        openRetrySucceeded: openCompact.proof.openRetrySucceeded,
        putRetryVerified: openCompact.proof.putRetryVerified,
        guardedLockDrainedAfterFailure: openCompact.proof.guardedLockDrainedAfterFailure,
        unsettledOrphanReviewGateObserved: orphanCompact.proof.unsettledOrphanReviewGateObserved,
        importedUnsettledOrphanBlocksRecovery: orphanCompact.proof.importedUnsettledOrphanBlocksRecovery,
        orphanReviewManifestRequired: orphanCompact.proof.orphanReviewManifestRequired,
        orphanStaleFingerprintRejected: orphanCompact.proof.orphanStaleFingerprintRejected,
        orphanReviewScopeOverrideRejected: orphanCompact.proof.orphanReviewScopeOverrideRejected,
        reviewedOrphanFinalizationObserved: orphanCompact.proof.reviewedOrphanFinalizationObserved,
        orphanLateFailureFreshReviewRequired: orphanCompact.proof.orphanLateFailureFreshReviewRequired,
        orphanFreshReviewClearedAndRecovered: orphanCompact.proof.orphanFreshReviewClearedAndRecovered,
        guardedLocksDrainAfterOrphanReview: orphanCompact.proof.guardedLocksDrainAfterOrphanReview,
        unsettledOrphanPosturedFactoryObserved: orphanCompact.proof.posturedFactoryObserved,
        crashDurabilityNonClaimsVisible: true,
        crossBrowserNonClaimsVisible: true
      }),
      nonClaims: Object.freeze([...KERNEL_KIT_RECOVERY_CHECKPOINT_NON_CLAIMS, ...(abruptCompact.nonClaims || []), ...(openCompact.nonClaims || []), ...(orphanCompact.nonClaims || [])])
    });
    const checkpoint = createKernelKitRecoveryCheckpoint({ recovery: recoveryInput, exactCommands: ['node tools/run_tests.mjs --tier browser --id browser:kernel-kit-recovery-checkpoint-proof --jobs 1'], nonClaims: recoveryInput.nonClaims }, { revision: REVISION, generatedAt: 'deterministic-browser-kernel-kit-recovery-checkpoint' });
    const validation = validateKernelKitRecoveryCheckpoint(checkpoint);

    assert.equal(abruptCompact.status, 'passed');
    assert.equal(openCompact.status, 'passed');
    assert.equal(orphanCompact.status, 'passed');
    assert.equal(validation.ok, true, validation.errors.join('; '));
    assert.equal(checkpoint.proof.sameOriginProfileRestartObserved, true);
    assert.equal(checkpoint.proof.interruptedWriteNotAcceptedCorrupt, true);
    assert.equal(checkpoint.proof.transientOpenFailureRetryObserved, true);
    assert.equal(checkpoint.proof.unsettledOrphanReviewGateObserved, true);
    assert.equal(checkpoint.proof.crashDurabilityNonClaimsVisible, true);

    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      probe_id: `${REVISION}-browser-kernel-kit-recovery-checkpoint-probe`,
      task_id: TASK_ID,
      status: 'passed',
      generatedAt: new Date().toISOString(),
      durationMs: performance.now() - started,
      purpose: 'Managed Chromium aggregate proof that Kernel Kit recovery evidence is browser-heavy explicit: two-launch OPFS abrupt-kill boundary plus transient OPFS root-open failure retry/drained-lock recovery plus reviewed unsettled-orphan cleanup gating, without crash/fsync/cross-browser claims.',
      inputs: Object.freeze({ abruptKill: abruptCompact, openFailureRecovery: openCompact, unsettledOrphanReview: orphanCompact }),
      childRuns: Object.freeze({
        abruptKill: Object.freeze({ durationMs: abrupt.durationMs, stdout: abrupt.stdout.slice(0, 240), stderrDigest: abrupt.stderr ? `len:${abrupt.stderr.length}` : null }),
        openFailureRecovery: Object.freeze({ durationMs: open.durationMs, stdout: open.stdout.slice(0, 240), stderrDigest: open.stderr ? `len:${open.stderr.length}` : null }),
        unsettledOrphanReview: Object.freeze({ durationMs: orphan.durationMs, stdout: orphan.stdout.slice(0, 240), stderrDigest: orphan.stderr ? `len:${orphan.stderr.length}` : null })
      }),
      checkpoint,
      validation,
      proof: Object.freeze({
        sameOriginProfileRestartObserved: checkpoint.proof.sameOriginProfileRestartObserved === true,
        sigkillBoundaryObserved: checkpoint.proof.sigkillBoundaryObserved === true,
        acknowledgedBlocksVerifiedAfterRestart: checkpoint.proof.acknowledgedBlocksVerifiedAfterRestart === true,
        interruptedWriteNotAcceptedCorrupt: checkpoint.proof.interruptedWriteNotAcceptedCorrupt === true,
        restartCleanupObservedOrDeferred: checkpoint.proof.restartCleanupObservedOrDeferred === true,
        transientOpenFailureRetryObserved: checkpoint.proof.transientOpenFailureRetryObserved === true,
        guardedLocksDrainAfterOpenFailure: checkpoint.proof.guardedLocksDrainAfterOpenFailure === true,
        unsettledOrphanReviewGateObserved: checkpoint.proof.unsettledOrphanReviewGateObserved === true,
        unsettledOrphanPosturedFactoryObserved: orphanCompact.proof.posturedFactoryObserved === true,
        crashDurabilityNonClaimsVisible: checkpoint.proof.crashDurabilityNonClaimsVisible === true,
        crossBrowserNonClaimsVisible: checkpoint.proof.crossBrowserNonClaimsVisible === true,
        noProductionRecoveryClaim: checkpoint.nonClaims.includes('No production recovery claim.')
      }),
      nonClaims: checkpoint.nonClaims
    });
  } finally {
    await rm(tmp, { recursive: true, force: true });
  }
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({
    abruptTimeoutMs: Number(argValue(argv, '--abrupt-timeout-ms', '60000')),
    relaxPolicy: !hasFlag(argv, '--no-policy-relaxation'),
    orphanTimeoutMs: Number(argValue(argv, '--orphan-timeout-ms', '22000'))
  });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-kernel-kit-recovery-checkpoint-probe`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed browser Kernel Kit recovery checkpoint is not silently skipped; debug by explicit browser id.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_kernel_kit_recovery_checkpoint_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}

// Static audit markers: browser:kernel-kit-recovery-checkpoint-proof; browser_opfs_abrupt_kill_boundary_probe.mjs; browser_opfs_block_store_open_failure_recovery_probe.mjs; browser_opfs_web_lock_unsettled_orphan_review_probe.mjs; BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE; sameOriginProfileRestartObserved; interruptedWriteNotAcceptedCorrupt; transientOpenFailureRetryObserved; unsettledOrphanReviewGateObserved.
