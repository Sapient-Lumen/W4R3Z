#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-trace-comparison-audit. Contract audit for the side-by-side Kernel Kit success/failure trace comparison.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, createKernelKitTraceComparison, validateKernelKitTraceComparison } from '../src/browserrt.mjs';
import { runProbe as runComparisonProbe } from './kernel_kit_trace_comparison_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-KERNEL-KIT-TRACE-COMPARISON-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const text = (path) => readTextWithRevisionFallback(path);
const includesAll = (haystack, needles) => needles.filter((needle) => !haystack.includes(needle));

export async function runAudit() {
  const [source, runtime, types, page, runner, browserProbe, manifestText, impactText, inventoryText, doc1, doc2, doc3] = await Promise.all([
    text('src/kernel-kit-demo.mjs'),
    text('src/browserrt.mjs'),
    text('src/types.d.ts'),
    text('demo/kernel-kit-demo.html'),
    text('demo/kernel-kit-demo-runner.mjs'),
    text('tools/browser_kernel_kit_demo_probe.mjs'),
    text('test/manifest.json'),
    text('test/impact-map.json'),
    text('test/surface-inventory.json'),
    text('docs/20-architecture/kernel-kit-trace-comparison-workbench-frontier.md'),
    text('docs/40-validation/kernel-kit-trace-comparison-slice.md'),
    text(`docs/40-validation/kernel-kit-trace-comparison-contract-audit-${REVISION}.md`)
  ]);
  const manifest = JSON.parse(manifestText);
  const impact = JSON.parse(impactText);
  const inventory = JSON.parse(inventoryText);
  const taskIds = new Set(manifest.tasks.map((task) => task.id));
  const impactIds = new Set(impact.rules.flatMap((rule) => rule.taskIds || rule.tasks || []));
  const inventoryIds = new Set(inventory.surfaces.flatMap((surface) => surface.manifestTasks || []));
  const proof = await runComparisonProbe();
  const validation = validateKernelKitTraceComparison(proof.comparison);
  const checks = [];
  const check = (id, ok, detail = {}) => checks.push({ id, ok: Boolean(ok), detail });
  check('source-exports-comparison', includesAll(source, ['createKernelKitTraceComparison', 'validateKernelKitTraceComparison', 'browserrt-kernel-kit-success-failure-comparison-v1', 'No automated failure recovery claim.']).length === 0);
  check('runtime-imports-and-exports-comparison', includesAll(runtime, ['createKernelKitTraceComparison', 'validateKernelKitTraceComparison', 'kernelKitTraceComparison', 'KERNEL_KIT_TRACE_COMPARISON_FORMAT']).length === 0);
  check('types-declare-comparison', includesAll(types, ['KernelKitTraceComparison', 'createKernelKitTraceComparison', 'validateKernelKitTraceComparison']).length === 0);
  check('page-has-comparison-controls', includesAll(page, ['compare-kernel-kit-traces', 'kernel-kit-comparison-output', 'Kernel Kit success/failure trace comparison']).length === 0);
  check('runner-exposes-comparison-api', includesAll(runner, ['compareKernelKitSuccessFailure', 'renderKernelKitTraceComparison', 'compareTraces', 'window.__BROWSERRT_KERNEL_KIT_TRACE_COMPARISON']).length === 0);
  check('browser-probe-drives-comparison-api', includesAll(browserProbe, ['BrowserRTKernelKitDemo.compareTraces', 'traceComparison', 'validateKernelKitTraceComparison']).length === 0);
  check('manifest-has-proof-and-audit', taskIds.has('demo:kernel-kit-trace-comparison-proof') && taskIds.has('facility:kernel-kit-trace-comparison-audit'));
  check('impact-covers-comparison', impactIds.has('demo:kernel-kit-trace-comparison-proof') && impactIds.has('facility:kernel-kit-trace-comparison-audit'));
  check('inventory-covers-comparison', inventoryIds.has('demo:kernel-kit-trace-comparison-proof') && inventoryIds.has('facility:kernel-kit-trace-comparison-audit'));
  check('docs-cover-comparison-and-nonclaims', [doc1, doc2, doc3].every((doc) => includesAll(doc, ['success/failure trace comparison', 'No root-cause analysis claim', 'No automated failure recovery claim']).length === 0));
  check('dynamic-proof-validates', validation.ok === true && proof.proof.successFailureDeltaVisible === true, { validation });
  const ok = checks.every((row) => row.ok);
  const audit = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-trace-comparison-contract-audit`,
    status: ok ? 'passed' : 'failed',
    checks,
    proof: proof.proof,
    validation,
    nonClaims: [
      'No production observability claim.',
      'No automated failure recovery claim.',
      'No root-cause analysis claim.',
      'No OpenTelemetry compatibility claim.',
      'No Chrome DevTools trace-format compatibility claim.'
    ]
  };
  assert.equal(ok, true, checks.filter((row) => !row.ok).map((row) => row.id).join('; '));
  return audit;
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const audit = await runAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(audit, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(audit, null, 2));
