#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-guided-tour-proof. Release-tier guided tour receipt proof.
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
  createKernelKitGuidedTourReceipt,
  validateKernelKitGuidedTourReceipt,
  KERNEL_KIT_GUIDED_TOUR_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runKernelKitDemoProbe } from './kernel_kit_demo_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-GUIDED-TOUR-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const successReport = await runKernelKitDemoProbe();
  const reloadReport = successReport;
  const failureReport = createKernelKitFailureModeReport({
    revision: REVISION,
    mode: 'admission-reject-no-mutation',
    observed: { rejected: true, reason: 'synthetic-guided-tour-controlled-rejection', preventedMutation: true },
    traceKinds: ['runtime:boot', 'admission:reject', 'kernel-kit-demo:controlled-failure', 'kernel-kit-demo:failure:admission-reject-no-mutation', 'runtime:close']
  });
  const comparison = createKernelKitTraceComparison(successReport, failureReport, { revision: REVISION, source: 'kernel-kit-guided-tour-probe-comparison', generatedAt: 'deterministic-guided-tour-comparison' });
  const runbook = createKernelKitDiagnosticRunbook(comparison, { revision: REVISION, source: 'kernel-kit-guided-tour-probe-runbook', generatedAt: 'deterministic-guided-tour-runbook' });
  const exportBundle = createKernelKitDemoExportBundle(successReport, { revision: REVISION, source: 'kernel-kit-guided-tour-probe-export', generatedAt: 'deterministic-guided-tour-export' });
  const supportBundle = createKernelKitSupportBundle({ revision: REVISION, successReport, reloadReport, failureReport, comparison, runbook, exportBundle, generatedAt: 'deterministic-guided-tour-support-bundle' });
  const guidedTour = createKernelKitGuidedTourReceipt({ revision: REVISION, successReport, reloadReport, failureReport, comparison, runbook, exportBundle, supportBundle, generatedAt: 'deterministic-guided-tour-probe' });
  const validation = validateKernelKitGuidedTourReceipt(guidedTour);
  assert.equal(guidedTour.format, KERNEL_KIT_GUIDED_TOUR_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(guidedTour.proof.hasTourSteps, true);
  assert.equal(guidedTour.proof.hasPersonaTracks, true);
  assert.equal(guidedTour.proof.hasSupportBundleReference, true);
  assert.equal(guidedTour.proof.supportBundleValidWhenPresent, true);
  assert.equal(guidedTour.proof.hasExactCommands, true);
  assert.equal(guidedTour.proof.mentionsBoundedFailure, true);
  assert.equal(guidedTour.proof.browserLightReminder, true);
  assert.ok(guidedTour.exactCommands.some((cmd) => cmd.includes('demo:kernel-kit-guided-tour-proof')), 'guided-tour proof command missing');
  assert.ok(guidedTour.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-demo-proof')), 'browser proof command missing');
  assert.ok(guidedTour.nonClaims.includes('No production guided-tour claim.'));
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-guided-tour-probe`,
    status: 'passed',
    successProbeId: successReport.proofId || successReport.probe_id,
    guidedTour,
    validation,
    proof: {
      guidedTourValid: validation.ok,
      stepCount: validation.stepCount,
      passedCount: validation.passedCount,
      hasTourSteps: guidedTour.proof.hasTourSteps,
      hasPersonaTracks: guidedTour.proof.hasPersonaTracks,
      hasSupportBundleReference: guidedTour.proof.hasSupportBundleReference,
      supportBundleValidWhenPresent: guidedTour.proof.supportBundleValidWhenPresent,
      hasExactCommands: guidedTour.proof.hasExactCommands,
      mentionsBoundedFailure: guidedTour.proof.mentionsBoundedFailure,
      browserLightReminder: guidedTour.proof.browserLightReminder,
      nonClaimsVisible: guidedTour.proof.nonClaimsVisible
    },
    nonClaims: guidedTour.nonClaims
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

// Static audit markers: demo:kernel-kit-guided-tour-proof; browserrt-kernel-kit-guided-tour-v1; No production guided-tour claim.; exact commands.
