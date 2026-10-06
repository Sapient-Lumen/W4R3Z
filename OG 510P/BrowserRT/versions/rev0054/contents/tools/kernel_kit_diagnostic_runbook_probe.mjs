#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-diagnostic-runbook-proof. Release-tier proof for actionable Kernel Kit diagnostic runbook.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitDiagnosticRunbook,
  validateKernelKitDiagnosticRunbook,
  KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runTraceComparisonProbe } from './kernel_kit_trace_comparison_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-DIAGNOSTIC-RUNBOOK-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const comparisonReport = await runTraceComparisonProbe();
  const comparison = comparisonReport.comparison;
  const runbook = createKernelKitDiagnosticRunbook(comparison, { revision: REVISION, source: 'kernel-kit-diagnostic-runbook-probe', generatedAt: 'deterministic-diagnostic-runbook-probe' });
  const validation = validateKernelKitDiagnosticRunbook(runbook);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(runbook.format, KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT);
  assert.equal(runbook.proof.successPathVisible, true);
  assert.equal(runbook.proof.failureBounded, true);
  assert.equal(runbook.proof.changedEvidenceVisible, true);
  assert.equal(runbook.proof.exactCommandsPresent, true);
  assert.ok(runbook.cards.find((card) => card.id === 'what-changed'), 'what-changed card missing');
  assert.ok(runbook.cards.find((card) => card.id === 'what-stayed-bounded'), 'what-stayed-bounded card missing');
  assert.ok(runbook.cards.find((card) => card.id === 'what-to-run-next'), 'what-to-run-next card missing');
  assert.ok(runbook.exactCommands.some((cmd) => cmd.includes('demo:kernel-kit-diagnostic-runbook-proof')), 'release proof command missing');
  assert.ok(runbook.exactCommands.some((cmd) => cmd.includes('browser:kernel-kit-demo-proof')), 'browser proof command missing');
  assert.ok(runbook.exactCommands.some((cmd) => cmd.includes('facility:kernel-kit-diagnostic-runbook-audit')), 'audit command missing');
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-diagnostic-runbook-probe`,
    status: 'passed',
    comparisonProbeId: comparisonReport.probe_id,
    runbook,
    validation,
    proof: {
      diagnosticRunbookValid: validation.ok,
      successPathVisible: runbook.proof.successPathVisible,
      failureBounded: runbook.proof.failureBounded,
      exactCommandsPresent: runbook.proof.exactCommandsPresent,
      cardCount: runbook.cards.length,
      commandCount: runbook.exactCommands.length,
      nonClaimsVisible: runbook.proof.nonClaimsVisible
    },
    nonClaims: runbook.nonClaims
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

// Static audit markers: demo:kernel-kit-diagnostic-runbook-proof; browserrt-kernel-kit-diagnostic-runbook-v1; exact next commands; No root-cause analysis claim.
