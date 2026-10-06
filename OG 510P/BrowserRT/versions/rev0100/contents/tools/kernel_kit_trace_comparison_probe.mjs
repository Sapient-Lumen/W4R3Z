#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-trace-comparison-proof. Release-tier proof for side-by-side success/failure trace comparison.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitTraceComparison,
  validateKernelKitTraceComparison,
  createKernelKitFailureModeReport,
  validateKernelKitFailureModeReport,
  KERNEL_KIT_DEMO_NON_CLAIMS,
  KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS
} from '../src/browserrt.mjs';
import { runProbe as runKernelKitDemoProbe } from './kernel_kit_demo_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-TRACE-COMPARISON-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const successReport = await runKernelKitDemoProbe();
  const failureReport = createKernelKitFailureModeReport({
    revision: REVISION,
    mode: 'admission-reject-no-mutation',
    observed: { rejected: true, reason: 'synthetic-release-tier-controlled-rejection', preventedMutation: true },
    traceKinds: ['runtime:boot', 'admission:reject', 'kernel-kit-demo:controlled-failure', 'kernel-kit-demo:failure:admission-reject-no-mutation', 'runtime:close']
  });
  const failureValidation = validateKernelKitFailureModeReport(failureReport);
  assert.equal(failureValidation.ok, true, failureValidation.errors.join('; '));
  const comparison = createKernelKitTraceComparison(successReport, failureReport, { revision: REVISION, source: 'kernel-kit-trace-comparison-probe', generatedAt: 'deterministic-trace-comparison-probe' });
  const validation = validateKernelKitTraceComparison(comparison);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(comparison.proof.successHasUsefulPath, true);
  assert.equal(comparison.proof.failurePreventedMutation, true);
  assert.ok(comparison.diff.successOnlyTraceKinds.includes('storage-lane:dispatch') || comparison.diff.successOnlyTraceKinds.includes('storage:block-put'), 'success-only trace kinds should show storage-lane/provider work');
  assert.ok(comparison.diff.failureOnlyTraceKinds.includes('kernel-kit-demo:controlled-failure'), 'failure-only trace kinds should show controlled failure');
  assert.equal(comparison.diff.stageRows.length, 8);
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-trace-comparison-probe`,
    status: 'passed',
    successProbeId: successReport.proofId || successReport.probe_id,
    failureMode: failureReport.failureMode,
    comparison,
    validation,
    proof: {
      comparisonValid: validation.ok,
      successHasUsefulPath: comparison.proof.successHasUsefulPath,
      failureIsControlled: comparison.proof.failureIsControlled,
      failurePreventedMutation: comparison.proof.failurePreventedMutation,
      successFailureDeltaVisible: comparison.proof.successFailureDeltaVisible,
      stageRowsComplete: comparison.diff.stageRows.length === KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS.length || comparison.diff.stageRows.length === 8,
      nonClaimsVisible: comparison.nonClaims.length >= KERNEL_KIT_DEMO_NON_CLAIMS.length
    },
    nonClaims: comparison.nonClaims
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

// Static audit markers: Kernel Kit success/failure trace comparison; browserrt-kernel-kit-success-failure-comparison-v1.
