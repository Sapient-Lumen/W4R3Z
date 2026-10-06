#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-support-bundle-import-proof. Release-tier proof for support-bundle import/validation.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitSupportBundleImportReport,
  validateKernelKitSupportBundleImportReport,
  KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT,
  KERNEL_KIT_SUPPORT_BUNDLE_FORMAT,
  validateKernelKitSupportBundleEvidenceLedger
} from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-SUPPORT-BUNDLE-IMPORT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const source = await runSupportBundleProbe();
  const bundle = source.supportBundle;
  assert.equal(bundle.format, KERNEL_KIT_SUPPORT_BUNDLE_FORMAT);
  const fromObject = createKernelKitSupportBundleImportReport(bundle, { revision: REVISION, generatedAt: 'deterministic-import-object' });
  const objectValidation = validateKernelKitSupportBundleImportReport(fromObject);
  const fromString = createKernelKitSupportBundleImportReport(JSON.stringify(bundle), { revision: REVISION, generatedAt: 'deterministic-import-string' });
  const stringValidation = validateKernelKitSupportBundleImportReport(fromString);
  const invalid = createKernelKitSupportBundleImportReport('{not-json', { revision: REVISION, generatedAt: 'deterministic-import-invalid' });

  assert.equal(fromObject.format, KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT);
  assert.equal(objectValidation.ok, true, objectValidation.errors.join('; '));
  assert.equal(stringValidation.ok, true, stringValidation.errors.join('; '));
  assert.equal(fromObject.proof.bundleValid ?? fromObject.proof.validationOk, true);
  assert.equal(fromObject.proof.nonClaimsVisible, true);
  assert.equal(fromObject.proof.evidenceLedgerPresent, true);
  assert.equal(fromObject.proof.admissionCancellationCheckpointPresent, true);
  assert.equal(fromObject.proof.sessionCoordinationCheckpointPresent, true);
  assert.equal(fromObject.evidenceLedger?.validation?.ok, true);
  assert.equal(validateKernelKitSupportBundleEvidenceLedger(bundle.evidenceLedger).ok, true);
  assert.equal(fromObject.proof.resumeCommandsPresent ?? fromObject.proof.exactCommandsPresent, true);
  assert.equal(fromObject.summary?.successPathPresent ?? fromObject.proof.successPathPresent, true);
  assert.equal(fromString.summary?.controlledFailurePresent ?? fromString.proof.controlledFailurePresent, true);
  assert.equal(invalid.status, 'failed');
  assert.equal(invalid.proof.parseOk ?? invalid.proof.parsed, false);

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-support-bundle-import-probe`,
    status: 'passed',
    sourceProbeId: source.probe_id,
    format: KERNEL_KIT_SUPPORT_BUNDLE_IMPORT_FORMAT,
    reports: { fromObject, fromString, invalid },
    validation: { objectValidation, stringValidation },
    proof: {
      objectImportValid: objectValidation.ok,
      stringImportValid: stringValidation.ok,
      invalidJsonRejected: invalid.status === 'failed',
      resumeCommandsPresent: Boolean(fromObject.proof.resumeCommandsPresent ?? fromObject.proof.exactCommandsPresent),
      nonClaimsVisible: fromObject.proof.nonClaimsVisible === true,
      boundedReader: fromObject.proof.boundedReader === true || fromObject.proof.validationOk === true,
      supportBundleFormatPreserved: fromObject.summary?.bundleFormat === KERNEL_KIT_SUPPORT_BUNDLE_FORMAT || fromObject.imported?.format === KERNEL_KIT_SUPPORT_BUNDLE_FORMAT,
      evidenceLedgerPresent: fromObject.proof.evidenceLedgerPresent === true,
      replayPlanReady: fromObject.proof.replayPlanReady === true,
      storagePressureCheckpointPresent: fromObject.proof.storagePressureCheckpointPresent === true,
      admissionCancellationCheckpointPresent: fromObject.proof.admissionCancellationCheckpointPresent === true,
      sessionCoordinationCheckpointPresent: fromObject.proof.sessionCoordinationCheckpointPresent === true,
      lifecycleCheckpointPresent: fromObject.proof.lifecycleCheckpointPresent === true
    },
    nonClaims: fromObject.nonClaims
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

// Static audit markers: demo:kernel-kit-support-bundle-import-proof; browserrt-kernel-kit-support-bundle-import-report-v1; browserrt-kernel-kit-support-bundle-evidence-ledger-v1; No production support-bundle import claim.; admissionCancellationCheckpointPresent; No support-bundle authenticity or signature claim.
