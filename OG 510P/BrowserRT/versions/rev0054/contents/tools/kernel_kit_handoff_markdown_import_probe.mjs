#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-handoff-markdown-import-proof. Release-tier proof that generated handoff Markdown can be pasted back and validated.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitHandoffMarkdownImportReport,
  validateKernelKitHandoffMarkdownImportReport,
  KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runHandoffMarkdownProbe } from './kernel_kit_handoff_markdown_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-HANDOFF-MARKDOWN-IMPORT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const handoffSource = await runHandoffMarkdownProbe();
  const markdown = handoffSource.handoffMarkdown.markdown;
  const importReport = createKernelKitHandoffMarkdownImportReport(markdown, { revision: REVISION, generatedAt: 'deterministic-handoff-markdown-import-probe' });
  const validation = validateKernelKitHandoffMarkdownImportReport(importReport);

  assert.equal(importReport.format, KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(importReport.status, 'handoff-import-ready');
  assert.equal(importReport.proof.titlePresent, true);
  assert.equal(importReport.proof.revisionPresent, true);
  assert.equal(importReport.proof.requiredCommandsPresent, true);
  assert.equal(importReport.proof.requiredNonClaimsPresent, true);
  assert.equal(importReport.proof.successPathPresent, true);
  assert.equal(importReport.proof.controlledFailurePresent, true);
  assert.equal(importReport.proof.diagnosticRunbookPresent, true);
  assert.equal(importReport.proof.supportBundleDiffSummaryPresent, true);
  assert.equal(importReport.proof.guidedTourSummaryPresent, true);
  assert.equal(importReport.proof.nextSessionChecklistPresent, true);
  assert.equal(importReport.riskFlags.length, 0);
  assert.ok(importReport.resumeCommands.includes('python3 tools/check_cube.py'));
  assert.ok(importReport.nonClaims.includes('No production handoff-markdown import claim.'));

  // Negative evidence: removing a required command must be noticed without claiming automated correctness.
  const damagedMarkdown = markdown.replace('python3 tools/check_cube.py', 'python3 tools/not_the_cube_check.py');
  const damaged = createKernelKitHandoffMarkdownImportReport(damagedMarkdown, { revision: REVISION, generatedAt: 'deterministic-handoff-markdown-import-negative' });
  assert.equal(damaged.status, 'handoff-import-needs-attention');
  assert.equal(damaged.proof.requiredCommandsPresent, false);
  assert.ok(damaged.riskFlags.some((flag) => flag.startsWith('missing-command:python3 tools/check_cube.py')));

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-handoff-markdown-import-probe`,
    status: 'passed',
    sourceProbeId: handoffSource.probe_id,
    importReport,
    validation,
    negative: {
      status: damaged.status,
      requiredCommandsPresent: damaged.proof.requiredCommandsPresent,
      riskFlags: damaged.riskFlags
    },
    proof: {
      handoffMarkdownImportValid: validation.ok,
      importedRevision: importReport.revision,
      requiredCommandsPresent: importReport.proof.requiredCommandsPresent,
      requiredNonClaimsPresent: importReport.proof.requiredNonClaimsPresent,
      negativeMissingCommandDetected: damaged.status === 'handoff-import-needs-attention',
      riskFlagsEmptyForGoodImport: importReport.riskFlags.length === 0,
      resumeCommandCount: importReport.resumeCommands.length
    },
    nonClaims: importReport.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: browserrt-kernel-kit-handoff-markdown-import-v1; No production handoff-markdown import claim.; demo:kernel-kit-handoff-markdown-import-proof.
