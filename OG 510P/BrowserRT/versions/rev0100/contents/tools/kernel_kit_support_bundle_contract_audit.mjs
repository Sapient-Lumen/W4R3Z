#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-audit. Contract audit for Kernel Kit support-bundle surfaces.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitSupportBundle } from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runSupportBundleProbe();
  const validation = validateKernelKitSupportBundle(proof.supportBundle);
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
    'docs/20-architecture/kernel-kit-support-bundle-frontier.md',
    'docs/40-validation/kernel-kit-support-bundle-slice.md',
    `docs/40-validation/kernel-kit-support-bundle-contract-audit-${REVISION}.md`,
    `docs/50-roadmap/kernel-kit-support-bundle-roadmap-${REVISION}.md`
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set(manifest.tasks.map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || surface.manifestTasks || []));
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true, { validation }),
    check('source-exports-support-bundle', includesAll(source, ['createKernelKitSupportBundle', 'validateKernelKitSupportBundle', 'browserrt-kernel-kit-support-bundle-v1', 'No production support-bundle claim.']).length === 0),
    check('runtime-imports-exports-support-bundle', includesAll(runtime, ['createKernelKitSupportBundle', 'validateKernelKitSupportBundle', 'kernelKitSupportBundle', 'KERNEL_KIT_SUPPORT_BUNDLE_FORMAT']).length === 0),
    check('types-declare-support-bundle', includesAll(types, ['KernelKitSupportBundle', 'createKernelKitSupportBundle', 'validateKernelKitSupportBundle', 'kernelKitSupportBundle']).length === 0),
    check('page-runner-exposes-support-api', includesAll(runner, ['buildKernelKitSupportBundle', 'renderKernelKitSupportBundle', 'buildSupportBundle', 'window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE']).length === 0),
    check('html-exposes-support-controls', includesAll(page, ['build-kernel-kit-support-bundle', 'kernel-kit-support-output', 'Support bundle']).length === 0),
    check('browser-probe-drives-support-api', includesAll(browserProbe, ['BrowserRTKernelKitDemo.buildSupportBundle', 'supportBundle', 'validateKernelKitSupportBundle']).length === 0),
    check('manifest-tasks-present', ['demo:kernel-kit-support-bundle-proof','facility:kernel-kit-support-bundle-audit'].every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-support-bundle', ['demo:kernel-kit-support-bundle-proof','facility:kernel-kit-support-bundle-audit'].every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && includesAll(body, ['support bundle', 'No production support-bundle claim.', 'No automated failure triage claim.', 'browser-light']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) }),
    check('non-claims-preserved', proof.nonClaims.includes('No production runtime claim.') && proof.nonClaims.includes('No production support-bundle claim.') && proof.nonClaims.includes('No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-support-bundle-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Release-tier contract audit for the Kernel Kit support bundle: source/runtime/types/page/browser probe/manifest/docs/non-claim wiring without launching Chromium.',
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

// Static audit markers: facility:kernel-kit-support-bundle-audit; buildSupportBundle; No production support-bundle claim.; No automated failure triage claim.
