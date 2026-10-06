#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-guided-tour-audit. Contract audit for Kernel Kit guided-tour surfaces.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitGuidedTourReceipt } from '../src/browserrt.mjs';
import { runProbe as runGuidedTourProbe } from './kernel_kit_guided_tour_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-GUIDED-TOUR-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runGuidedTourProbe();
  const validation = validateKernelKitGuidedTourReceipt(proof.guidedTour);
  const source = await text('src/kernel-kit-demo.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const page = await text('demo/kernel-kit-demo.html');
  const browserProbe = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const docs = [
    'docs/20-architecture/kernel-kit-guided-tour-frontier.md',
    'docs/40-validation/kernel-kit-guided-tour-slice.md',
    `docs/40-validation/kernel-kit-guided-tour-contract-audit-${REVISION}.md`,
    `docs/50-roadmap/kernel-kit-guided-tour-roadmap-${REVISION}.md`
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set(manifest.tasks.map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || surface.manifestTasks || []));
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true, { validation }),
    check('source-exports-guided-tour', includesAll(source, ['createKernelKitGuidedTourReceipt', 'validateKernelKitGuidedTourReceipt', 'browserrt-kernel-kit-guided-tour-v1', 'No production guided-tour claim.']).length === 0),
    check('runtime-imports-exports-guided-tour', includesAll(runtime, ['createKernelKitGuidedTourReceipt', 'validateKernelKitGuidedTourReceipt', 'kernelKitGuidedTourReceipt', 'KERNEL_KIT_GUIDED_TOUR_FORMAT']).length === 0),
    check('types-declare-guided-tour', includesAll(types, ['KernelKitGuidedTourReceipt', 'createKernelKitGuidedTourReceipt', 'validateKernelKitGuidedTourReceipt']).length === 0),
    check('page-runner-exposes-guided-tour-api', includesAll(runner, ['runKernelKitGuidedTour', 'renderKernelKitGuidedTourReceipt', 'runGuidedTour', 'window.__BROWSERRT_KERNEL_KIT_GUIDED_TOUR']).length === 0),
    check('html-exposes-guided-tour-controls', includesAll(page, ['run-kernel-kit-guided-tour', 'kernel-kit-guided-tour-output', 'Guided tour']).length === 0),
    check('browser-probe-drives-guided-tour-api', includesAll(browserProbe, ['BrowserRTKernelKitDemo.runGuidedTour', 'guidedTour', 'validateKernelKitGuidedTourReceipt']).length === 0),
    check('manifest-tasks-present', ['demo:kernel-kit-guided-tour-proof','facility:kernel-kit-guided-tour-audit'].every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-guided-tour', ['demo:kernel-kit-guided-tour-proof','facility:kernel-kit-guided-tour-audit'].every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && includesAll(body, ['guided tour', 'No production guided-tour claim.', 'No automated demo correctness claim.', 'browser-light']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) }),
    check('non-claims-preserved', proof.nonClaims.includes('No production runtime claim.') && proof.nonClaims.includes('No production guided-tour claim.') && proof.nonClaims.includes('No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-guided-tour-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Release-tier contract audit for the Kernel Kit guided tour: source/runtime/types/page/browser probe/manifest/docs/non-claim wiring without launching Chromium.',
    proofId: proof.probe_id,
    checks,
    nonClaims: proof.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(report, null, 2) + '\n');
console.log(out);
if (report.status !== 'passed') process.exitCode = 1;

// Static audit markers: facility:kernel-kit-guided-tour-audit; runGuidedTour; No production guided-tour claim.; No automated demo correctness claim.
