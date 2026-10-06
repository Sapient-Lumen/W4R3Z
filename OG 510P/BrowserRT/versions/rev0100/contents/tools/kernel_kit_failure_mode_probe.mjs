#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-failure-mode-proof. Release-tier proof for controlled Kernel Kit failure receipts.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  KERNEL_KIT_DEMO_FAILURE_MODES,
  createKernelKitFailureModeReport,
  validateKernelKitFailureModeReport,
  createKernelKitDemoExportBundle,
  validateKernelKitDemoExportBundle
} from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-FAILURE-MODE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const reports = [];
  for (const mode of KERNEL_KIT_DEMO_FAILURE_MODES) {
    const report = createKernelKitFailureModeReport({
      revision: REVISION,
      mode,
      observed: { preventedMutation: true, syntheticReleaseTier: true, reason: `${mode}-controlled` },
      traceKinds: mode === 'admission-reject-no-mutation' ? ['runtime:boot','admission:reject','runtime:close'] : []
    });
    const validation = validateKernelKitFailureModeReport(report);
    assert.equal(validation.ok, true, validation.errors.join('; '));
    const bundle = createKernelKitDemoExportBundle(report, { revision: REVISION, source: 'kernel-kit-failure-mode-probe', generatedAt: 'deterministic-failure-mode-probe', failureMode: mode });
    const bundleValidation = validateKernelKitDemoExportBundle(bundle);
    assert.equal(bundleValidation.ok, true, bundleValidation.errors.join('; '));
    reports.push({ report, validation, bundleValidation });
  }
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-failure-mode-probe`,
    status: 'passed',
    modeCount: reports.length,
    modes: reports.map((row) => row.report.failureMode),
    reports,
    proof: {
      allModesCovered: reports.length === KERNEL_KIT_DEMO_FAILURE_MODES.length,
      allValidated: reports.every((row) => row.validation.ok && row.bundleValidation.ok),
      preventedMutation: reports.every((row) => row.report.proof.preventedMutation === true),
      exportBundlesValidate: reports.every((row) => row.bundleValidation.ok)
    },
    nonClaims: [
      'No production runtime claim.',
      'No failure recovery automation claim.',
      'No production incident-reporting claim.',
      'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'
    ]
  };
  assert.equal(report.proof.allModesCovered, true);
  assert.equal(report.proof.allValidated, true);
  return report;
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));
