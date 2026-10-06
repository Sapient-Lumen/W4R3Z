#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-workbench-contract-audit.
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-WORKBENCH-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function has(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

export async function runAudit() {
  const files = {
    source: await text('src/kernel-kit-demo.mjs'),
    runner: await text('demo/kernel-kit-demo-runner.mjs'),
    page: await text('demo/kernel-kit-demo.html'),
    browserProbe: await text('tools/browser_kernel_kit_demo_probe.mjs'),
    failureProbe: await text('tools/kernel_kit_failure_mode_probe.mjs'),
    exportProbe: await text('tools/kernel_kit_export_bundle_probe.mjs'),
    manifest: await text('test/manifest.json'),
    docs: await text('docs/40-validation/kernel-kit-trace-comparison-workbench-slice.md'),
    frontier: await text('docs/20-architecture/kernel-kit-trace-comparison-workbench-frontier.md'),
    receipt: await text('REVISION-RECEIPT.json')
  };
  const checks = [
    ['source-failure-mode-contract', files.source, ['KERNEL_KIT_DEMO_FAILURE_MODES','createKernelKitFailureModeReport','validateKernelKitFailureModeReport','No failure recovery automation claim.']],
    ['source-export-bundle-contract', files.source, ['KERNEL_KIT_DEMO_EXPORT_BUNDLE_FORMAT','createKernelKitDemoExportBundle','validateKernelKitDemoExportBundle','No browser download UX claim.']],
    ['page-api-controls', files.runner, ['runKernelKitControlledFailureMode','exportKernelKitDemoReceipt','window.BrowserRTKernelKitDemo.runFailureMode','window.BrowserRTKernelKitDemo.exportLastReceipt']],
    ['html-controls', files.page, ['export-kernel-kit-receipt','run-kernel-kit-failure','Controlled failure output','Export receipt output']],
    ['browser-proof-drives-page-api', files.browserProbe, ['exprForExport','exprForFailure','validateKernelKitDemoExportBundle','validateKernelKitFailureModeReport']],
    ['release-probes-present', files.manifest, ['demo:kernel-kit-failure-mode-proof','demo:kernel-kit-export-bundle-proof','facility:kernel-kit-workbench-contract-audit']],
    ['docs-legible', files.docs + files.frontier, ['controlled failure','export bundle','No production runtime claim','No OPFS durability']],
    ['receipt-nonclaims', files.receipt, ['No failure recovery automation claim.','No browser download UX claim.']]
  ].map(([name, body, needles]) => {
    const missing = has(body, needles);
    return { name, status: missing.length === 0 ? 'passed' : 'failed', missing };
  });
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-workbench-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit the rev0047 Kernel Kit failure/export workbench contract without launching Chromium.',
    checks,
    nonClaims: [
      'Audit does not prove browser behavior.',
      'Audit does not prove production observability, download UX, failure recovery automation, OPFS durability, or performance.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
assert.equal(report.status, 'passed', JSON.stringify(report.checks.filter((row) => row.status !== 'passed'), null, 2));
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Rev0047 diagnostic runbook carry-forward markers: demo:kernel-kit-diagnostic-runbook-proof, demo:kernel-kit-support-bundle-proof / facility:kernel-kit-diagnostic-runbook-audit, facility:kernel-kit-support-bundle-audit.
// Rev0049 support-bundle import audit carry-forward markers: demo:kernel-kit-support-bundle-import-proof; facility:kernel-kit-support-bundle-import-audit; importSupportBundle.
