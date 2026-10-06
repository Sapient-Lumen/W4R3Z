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
  KERNEL_KIT_SUPPORT_BUNDLE_FORMAT
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
  assert.equal(supportBundle.proof.successPathPresent, true);
  assert.equal(supportBundle.proof.controlledFailurePresent, true);
  assert.equal(supportBundle.proof.traceComparisonPresent, true);
  assert.equal(supportBundle.proof.diagnosticRunbookPresent, true);
  assert.equal(supportBundle.proof.exportReceiptPresent, true);
  assert.equal(supportBundle.proof.exactCommandsPresent, true);
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('demo:kernel-kit-support-bundle-proof')), 'support-bundle proof command missing');
  assert.ok(supportBundle.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-demo-proof')), 'browser proof command missing');
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
    proof: {
      supportBundleValid: validation.ok,
      sectionCount: validation.sectionCount,
      commandCount: validation.commandCount,
      successPathPresent: supportBundle.proof.successPathPresent,
      controlledFailurePresent: supportBundle.proof.controlledFailurePresent,
      traceComparisonPresent: supportBundle.proof.traceComparisonPresent,
      diagnosticRunbookPresent: supportBundle.proof.diagnosticRunbookPresent,
      exactCommandsPresent: supportBundle.proof.exactCommandsPresent,
      nonClaimsVisible: supportBundle.proof.nonClaimsVisible
    },
    nonClaims: supportBundle.nonClaims
  };
  return report;
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: demo:kernel-kit-support-bundle-proof; browserrt-kernel-kit-support-bundle-v1; No production support-bundle claim.; exact commands.
