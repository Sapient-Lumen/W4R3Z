#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, createKernelKitDemoPlan, validateKernelKitDemoPlan } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-DEMO-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const plan = createKernelKitDemoPlan({ revision: REVISION });
  const validation = validateKernelKitDemoPlan(plan);
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const receipt = await json('REVISION-RECEIPT.json');
  const browserrt = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const browserTool = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const nodeTool = await text('tools/kernel_kit_demo_probe.mjs');
  const source = await text('src/kernel-kit-demo.mjs');
  const html = await text('demo/kernel-kit-demo.html');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const docs = await Promise.all([
    `docs/20-architecture/integrated-kernel-kit-demo-frontier.md`,
    `docs/40-validation/browser-kernel-kit-demo-slice.md`,
    `docs/40-validation/kernel-kit-demo-contract-audit-${REVISION}.md`,
    `docs/50-roadmap/kernel-kit-demo-usefulness-gate-${REVISION}.md`,
    `docs/00-meta/cube-audit-${REVISION}.md`,
    `docs/00-meta/kernel-kit-demo-${REVISION}.md`
  ].map(async (path) => [path, await text(path)]));
  const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
  const browserTask = tasks.get('browser:kernel-kit-demo-proof');
  const auditTask = tasks.get('facility:kernel-kit-demo-audit');
  const pageAuditTask = tasks.get('facility:kernel-kit-page-contract-audit');
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
  const docNeedles = ['Interactive Kernel Kit Demo', 'browser:kernel-kit-demo-proof', 'facility:kernel-kit-demo-audit', 'facility:kernel-kit-page-contract-audit', 'No production runtime claim.', 'No product-market-fit claim.', 'No OPFS durability'];
  const docsMissing = docs.flatMap(([path, body]) => includesAll(body, docNeedles).map((needle) => ({ path, needle })));
  const nonClaimNeedles = ['No production runtime claim.', 'No product-market-fit claim.', 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.', 'No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim.', 'No cross-browser conformance claim.'];
  const checks = [
    check('plan-validates', validation.ok, { validation }),
    check('source-names-demo-steps-and-transcript', includesAll(source, ['KERNEL_KIT_DEMO_STEPS', 'KERNEL_KIT_DEMO_STAGE_LABELS', 'createKernelKitDemoTranscript', 'validateKernelKitDemoTranscript', 'spawn-worker-agent', 'opfs-storage-lane-write', 'page-reload-readback']).length === 0),
    check('runtime-exports-demo-and-transcript', includesAll(browserrt, ['createKernelKitDemoPlan', 'validateKernelKitDemoPlan', 'validateKernelKitDemoProof', 'createKernelKitDemoTranscript', 'validateKernelKitDemoTranscript', 'kernelKitDemoTranscript', 'kernel-kit-demo:transcript']).length === 0),
    check('types-export-demo-and-transcript', includesAll(types, ['KernelKitDemoPlan', 'KernelKitDemoTranscript', 'createKernelKitDemoTranscript', 'validateKernelKitDemoTranscript']).length === 0),
    check('human-page-loads-runner', includesAll(html, ['run-kernel-kit-demo', 'kernel-kit-output', '/demo/kernel-kit-demo-runner.mjs', 'window.BrowserRTKernelKitDemo.run()']).length === 0),
    check('runner-exposes-human-api', includesAll(runner, ['window.BrowserRTKernelKitDemo', 'runKernelKitDemo', 'reloadKernelKitDemo', 'renderKernelKitDemoReport', 'opfsBlockStoreStorageLaneAdapter', 'createKernelKitDemoTranscript']).length === 0),
    check('browser-tool-drives-human-page-api', includesAll(browserTool, ['BrowserRTKernelKitDemo.run', 'BrowserRTKernelKitDemo.reloadRead', 'renderedTranscript', 'demo/kernel-kit-demo.html']).length === 0),
    check('node-tool-records-transcript', includesAll(nodeTool, ['createKernelKitDemoTranscript', 'validateKernelKitDemoTranscript', 'transcriptValidation']).length === 0),
    check('manifest-browser-task-present', Boolean(browserTask), { task: browserTask?.id }),
    check('manifest-browser-task-not-release', Boolean(browserTask) && browserTask.lane === 'browser' && browserTask.tiers?.includes('browser') && !browserTask.tiers?.includes('release'), { tiers: browserTask?.tiers, lane: browserTask?.lane }),
    check('manifest-audit-task-release-non-browser', Boolean(auditTask) && auditTask.tiers?.includes('release') && auditTask.lane !== 'browser', { tiers: auditTask?.tiers, lane: auditTask?.lane }),
    check('manifest-page-audit-task-release-non-browser', Boolean(pageAuditTask) && pageAuditTask.tiers?.includes('release') && pageAuditTask.lane !== 'browser', { tiers: pageAuditTask?.tiers, lane: pageAuditTask?.lane }),
    check('impact-map-covers-demo', ['browser:kernel-kit-demo-proof', 'facility:kernel-kit-demo-audit', 'facility:kernel-kit-page-contract-audit', 'demo:kernel-kit-proof'].every((id) => impactIds.has(id))),
    check('surface-inventory-covers-demo', ['browser:kernel-kit-demo-proof', 'facility:kernel-kit-demo-audit', 'facility:kernel-kit-page-contract-audit', 'demo:kernel-kit-proof'].every((id) => inventoryIds.has(id))),
    check('docs-cover-demo-and-nonclaims', docsMissing.length === 0, { docsMissing }),
    check('receipt-names-current-slice', receipt.current_runtime_slice === 'browser:kernel-kit-demo-proof' && ['facility:kernel-kit-demo-audit','facility:kernel-kit-usefulness-audit','facility:kernel-kit-trace-export-audit','facility:kernel-kit-workbench-contract-audit','facility:kernel-kit-trace-comparison-audit','facility:kernel-kit-support-bundle-audit','facility:kernel-kit-support-bundle-import-audit','facility:kernel-kit-guided-tour-audit','facility:kernel-kit-support-bundle-diff-audit','facility:kernel-kit-handoff-markdown-audit'].includes(receipt.current_audit_slice), { current_runtime_slice: receipt.current_runtime_slice, current_audit_slice: receipt.current_audit_slice }),
    check('receipt-preserves-nonclaims', nonClaimNeedles.every((claim) => (receipt.non_claims || []).includes(claim) || (receipt.nonClaims || []).includes(claim)), { required: nonClaimNeedles })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 2,
    audit_id: `${REVISION}-kernel-kit-demo-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    generatedAt: new Date().toISOString(),
    purpose: 'Release-tier audit for the integrated BrowserRT Kernel Kit demo contract. It checks source/export/type/doc/manifest/page-runner/impact/inventory/non-claim wiring without launching Chromium.',
    planValidation: validation,
    checks,
    nonClaims: [
      'This audit does not launch Chromium and does not prove the browser demo; run browser:kernel-kit-demo-proof explicitly.',
      ...nonClaimNeedles
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
assert.equal(report.status, 'passed');
