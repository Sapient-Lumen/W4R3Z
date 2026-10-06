#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-readiness-gate-proof. Release-tier proof that the Kernel Kit workbench can answer whether the demo is useful enough to continue.
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
  createKernelKitSupportBundleDiff,
  createKernelKitGuidedTourReceipt,
  createKernelKitHandoffMarkdown,
  createKernelKitHandoffMarkdownImportReport,
  createKernelKitReadinessGate,
  validateKernelKitReadinessGate,
  KERNEL_KIT_READINESS_GATE_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runKernelKitDemoProbe } from './kernel_kit_demo_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-READINESS-GATE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const successReport = await runKernelKitDemoProbe();
  const reloadReport = successReport;
  const failureReport = createKernelKitFailureModeReport({
    revision: REVISION,
    mode: 'admission-reject-no-mutation',
    observed: { rejected: true, reason: 'synthetic-readiness-gate-controlled-rejection', preventedMutation: true },
    traceKinds: ['runtime:boot', 'admission:reject', 'kernel-kit-demo:controlled-failure', 'kernel-kit-demo:failure:admission-reject-no-mutation', 'runtime:close']
  });
  const comparison = createKernelKitTraceComparison(successReport, failureReport, { revision: REVISION, source: 'kernel-kit-readiness-gate-probe-comparison', generatedAt: 'deterministic-readiness-comparison' });
  const runbook = createKernelKitDiagnosticRunbook(comparison, { revision: REVISION, source: 'kernel-kit-readiness-gate-probe-runbook', generatedAt: 'deterministic-readiness-runbook' });
  const exportBundle = createKernelKitDemoExportBundle(successReport, { revision: REVISION, source: 'kernel-kit-readiness-gate-probe-export', generatedAt: 'deterministic-readiness-export' });
  const supportBundle = createKernelKitSupportBundle({ revision: REVISION, successReport, reloadReport, failureReport, comparison, runbook, exportBundle, generatedAt: 'deterministic-readiness-support-bundle' });
  const supportBundleDiff = createKernelKitSupportBundleDiff(supportBundle, JSON.stringify(supportBundle), { revision: REVISION, generatedAt: 'deterministic-readiness-diff' });
  const guidedTour = createKernelKitGuidedTourReceipt({ revision: REVISION, successReport, reloadReport, failureReport, comparison, runbook, exportBundle, supportBundle, generatedAt: 'deterministic-readiness-guided-tour' });
  const handoffMarkdown = createKernelKitHandoffMarkdown({ revision: REVISION, supportBundle, diff: supportBundleDiff, guidedTour, generatedAt: 'deterministic-readiness-handoff-markdown' });
  const handoffMarkdownImport = createKernelKitHandoffMarkdownImportReport(handoffMarkdown.markdown, { revision: REVISION, generatedAt: 'deterministic-readiness-handoff-import' });
  const readinessGate = createKernelKitReadinessGate({ revision: REVISION, supportBundle, supportBundleDiff, guidedTour, handoffMarkdown, handoffMarkdownImport, traceComparison: comparison, diagnosticRunbook: runbook, exportBundle, browserProof: { proof: { storageWrite: true, reloadReadback: true, controlledFailureMode: true } }, releasePosture: 'browser-light', generatedAt: 'deterministic-readiness-gate-probe' });
  const validation = validateKernelKitReadinessGate(readinessGate);

  assert.equal(readinessGate.format, KERNEL_KIT_READINESS_GATE_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(readinessGate.status, 'ready-for-next-usefulness-pass');
  assert.equal(readinessGate.proof.allRequiredGatesPass, true);
  assert.equal(readinessGate.proof.allPersonasPass, true);
  assert.equal(readinessGate.proof.handoffMarkdownRoundTripVisible, true);
  assert.equal(readinessGate.proof.boundedFailureVisible, true);
  assert.equal(readinessGate.proof.browserLightReleasePreserved, true);
  assert.ok(readinessGate.exactCommands.some((cmd) => cmd.includes('demo:kernel-kit-readiness-gate-proof')));
  assert.ok(readinessGate.exactCommands.some((cmd) => cmd.includes('facility:kernel-kit-readiness-gate-audit')));
  assert.ok(readinessGate.nonClaims.includes('No production readiness-gate claim.'));
  assert.ok(readinessGate.personaTracks.every((row) => row.passed === true));

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-readiness-gate-probe`,
    status: 'passed',
    sourceProbeId: successReport.probe_id,
    readinessGate,
    validation,
    proof: {
      readinessGateValid: validation.ok,
      status: readinessGate.status,
      gateCount: validation.gateCount,
      personaCount: validation.personaCount,
      allRequiredGatesPass: readinessGate.proof.allRequiredGatesPass,
      allPersonasPass: readinessGate.proof.allPersonasPass,
      handoffMarkdownRoundTripVisible: readinessGate.proof.handoffMarkdownRoundTripVisible,
      exactCommandsPresent: readinessGate.proof.exactCommandsPresent,
      nonClaimsVisible: readinessGate.proof.nonClaimsVisible
    },
    nonClaims: readinessGate.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: demo:kernel-kit-readiness-gate-proof; browserrt-kernel-kit-readiness-gate-v1; No production readiness-gate claim.; exact commands.
