#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-support-bundle-evidence-checkpoint-proof. Release-tier proof for machine-checking supplied support-bundle evidence reports.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitSupportBundleEvidenceCheckpoint,
  validateKernelKitSupportBundleEvidenceCheckpoint,
  createKernelKitSupportBundleImportReport,
  KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT,
  validateKernelKitSupportBundleEvidenceLedger
} from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-CHECKPOINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function compactSupportAuditArtifact() {
  return {
    id: 'support-bundle-audit-artifact',
    status: 'passed',
    checks: [
      { name: 'proof-validates', status: 'passed' },
      { name: 'evidence-ledger-contract-present', status: 'passed' }
    ],
    proof: { compactAuditShape: true }
  };
}


function compactAdmissionCancellationArtifact() {
  return {
    project: 'BrowserRT',
    revision: REVISION,
    probe_id: `${REVISION}-kernel-kit-admission-cancellation-checkpoint-probe`,
    status: 'passed',
    proof: {
      observedCheckpointValid: true,
      supportBundleCarriesAdmissionCancellationCheckpoint: true,
      admissionAbortReleaseProofPassed: true
    },
    nonClaim: 'Compact admission-cancellation evidence shape only; the release-light proof supplies the full report.'
  };
}

function compactReadinessArtifact() {
  return {
    id: 'readiness-gate-artifact',
    status: 'passed',
    proof: { readinessInputsEvidenceBound: true },
    inputProof: { evidenceBound: true },
    readinessGate: { inputProof: { evidenceBound: true } },
    nonClaim: 'Compact readiness artifact shape only; the readiness-gate proof supplies the full report.'
  };
}

function compactCubeSanityArtifact() {
  return {
    id: 'cube-sanity-command',
    status: 'passed',
    proof: { commandExitsZero: true },
    nonClaim: 'Explicit command-exit sentinel supplied to the checkpoint; the checkpoint itself does not execute tools/check_cube.py.'
  };
}

export async function runProbe() {
  const supportProof = await runSupportBundleProbe();
  const supportBundle = supportProof.supportBundle;
  assert.equal(validateKernelKitSupportBundleEvidenceLedger(supportBundle.evidenceLedger).ok, true);
  const importReport = createKernelKitSupportBundleImportReport(supportBundle, { revision: REVISION, generatedAt: 'deterministic-evidence-checkpoint-import-artifact' });
  const suppliedArtifacts = {
    'support-bundle-proof-artifact': supportProof,
    'support-bundle-audit-artifact': compactSupportAuditArtifact(),
    'support-bundle-import-artifact': importReport,
    'admission-cancellation-artifact': compactAdmissionCancellationArtifact(),
    'readiness-gate-artifact': compactReadinessArtifact(),
    'cube-sanity-command': compactCubeSanityArtifact()
  };
  const checkpoint = createKernelKitSupportBundleEvidenceCheckpoint(supportBundle, suppliedArtifacts, { revision: REVISION, scope: 'release-browser-light', generatedAt: 'deterministic-evidence-checkpoint-probe' });
  const validation = validateKernelKitSupportBundleEvidenceCheckpoint(checkpoint);
  const missingImport = createKernelKitSupportBundleEvidenceCheckpoint(supportBundle, {
    'support-bundle-proof-artifact': supportProof,
    'support-bundle-audit-artifact': compactSupportAuditArtifact(),
    'admission-cancellation-artifact': compactAdmissionCancellationArtifact(),
    'readiness-gate-artifact': compactReadinessArtifact(),
    'cube-sanity-command': compactCubeSanityArtifact()
  }, { revision: REVISION, scope: 'release-browser-light', generatedAt: 'deterministic-evidence-checkpoint-missing-import' });
  const fullWithoutBrowser = createKernelKitSupportBundleEvidenceCheckpoint(supportBundle, suppliedArtifacts, { revision: REVISION, scope: 'full-after-replay', generatedAt: 'deterministic-evidence-checkpoint-full-missing-browser' });

  assert.equal(checkpoint.format, KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(checkpoint.status, 'evidence-checkpoint-ready');
  assert.equal(checkpoint.proof.requiredProofPathsSatisfied, true);
  assert.equal(checkpoint.proof.checkpointDoesNotExecuteCommands, true);
  assert.equal(checkpoint.rows.find((row) => row.id === 'admission-cancellation-artifact')?.status, 'satisfied', 'release checkpoint must satisfy admission cancellation artifact');
  assert.ok(checkpoint.deferredEntryIds.includes('browser-kernel-kit-artifact'), 'release checkpoint must explicitly defer browser-heavy artifact');
  assert.ok(checkpoint.deferredEntryIds.includes('browser-session-coordination-artifact'), 'release checkpoint must explicitly defer session coordination browser-heavy artifact');
  assert.ok(checkpoint.deferredEntryIds.includes('browser-recovery-artifact'), 'release checkpoint must explicitly defer recovery browser-heavy artifact');
  assert.equal(checkpoint.missingEntryIds.length, 0);
  assert.equal(missingImport.status, 'needs-attention');
  assert.ok(missingImport.missingEntryIds.includes('support-bundle-import-artifact'), 'missing import artifact must be reported');
  assert.equal(validateKernelKitSupportBundleEvidenceCheckpoint(missingImport).ok, false);
  assert.equal(fullWithoutBrowser.status, 'needs-attention');
  assert.ok(fullWithoutBrowser.missingEntryIds.includes('browser-kernel-kit-artifact'), 'full checkpoint must require browser artifact');
  assert.ok(fullWithoutBrowser.missingEntryIds.includes('browser-session-coordination-artifact'), 'full checkpoint must require session coordination browser artifact');
  assert.ok(fullWithoutBrowser.missingEntryIds.includes('browser-recovery-artifact'), 'full checkpoint must require recovery browser artifact');

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-support-bundle-evidence-checkpoint-probe`,
    status: 'passed',
    sourceProbeId: supportProof.probe_id,
    checkpoint,
    validation,
    negativeCases: {
      missingImport: { status: missingImport.status, missingEntryIds: missingImport.missingEntryIds, validation: validateKernelKitSupportBundleEvidenceCheckpoint(missingImport) },
      fullWithoutBrowser: { status: fullWithoutBrowser.status, missingEntryIds: fullWithoutBrowser.missingEntryIds, validation: validateKernelKitSupportBundleEvidenceCheckpoint(fullWithoutBrowser) }
    },
    proof: {
      checkpointValid: validation.ok,
      ledgerValid: checkpoint.proof.ledgerValid,
      suppliedReportsChecked: checkpoint.proof.artifactsSupplied,
      requiredProofPathsSatisfied: checkpoint.proof.requiredProofPathsSatisfied,
      admissionCancellationSatisfied: checkpoint.rows.find((row) => row.id === 'admission-cancellation-artifact')?.status === 'satisfied',
      browserHeavyDeferred: checkpoint.deferredEntryIds.includes('browser-kernel-kit-artifact'),
      sessionCoordinationBrowserHeavyDeferred: checkpoint.deferredEntryIds.includes('browser-session-coordination-artifact'),
      recoveryBrowserHeavyDeferred: checkpoint.deferredEntryIds.includes('browser-recovery-artifact'),
      missingImportRejected: missingImport.status === 'needs-attention' && missingImport.missingEntryIds.includes('support-bundle-import-artifact'),
      fullReplayRequiresBrowserArtifact: fullWithoutBrowser.status === 'needs-attention' && fullWithoutBrowser.missingEntryIds.includes('browser-kernel-kit-artifact') && fullWithoutBrowser.missingEntryIds.includes('browser-session-coordination-artifact') && fullWithoutBrowser.missingEntryIds.includes('browser-recovery-artifact'),
      checkpointDoesNotReadArtifacts: checkpoint.proof.checkpointDoesNotReadArtifacts,
      checkpointDoesNotExecuteCommands: checkpoint.proof.checkpointDoesNotExecuteCommands,
      nonClaimsVisible: checkpoint.proof.nonClaimsVisible
    },
    nonClaims: checkpoint.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: demo:kernel-kit-support-bundle-evidence-checkpoint-proof; browserrt-kernel-kit-support-bundle-evidence-checkpoint-v1; requiredProofPathsSatisfied; missingImportRejected; fullReplayRequiresBrowserArtifact; admission-cancellation-artifact; admissionCancellationSatisfied; browser-session-coordination-artifact; browser-recovery-artifact; No command execution claim.
