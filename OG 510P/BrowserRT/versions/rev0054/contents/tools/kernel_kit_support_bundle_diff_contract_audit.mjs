#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-diff-audit. Contract audit for support-bundle diff surfaces.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitSupportBundleDiff } from '../src/browserrt.mjs';
import { runProbe as runDiffProbe } from './kernel_kit_support_bundle_diff_probe.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-DIFF-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return readFile(path, 'utf8'); }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runDiffProbe();
  const validation = validateKernelKitSupportBundleDiff(proof.same);
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
    'docs/20-architecture/kernel-kit-support-bundle-diff-frontier.md',
    'docs/40-validation/kernel-kit-support-bundle-diff-slice.md',
    `docs/40-validation/kernel-kit-support-bundle-diff-contract-audit-${REVISION}.md`,
    `docs/50-roadmap/kernel-kit-support-bundle-diff-roadmap-${REVISION}.md`
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set(manifest.tasks.map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || surface.manifestTasks || []));
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true, { validation }),
    check('source-exports-support-bundle-diff', includesAll(source, ['createKernelKitSupportBundleDiff', 'validateKernelKitSupportBundleDiff', 'browserrt-kernel-kit-support-bundle-diff-v1', 'No production support-bundle diff claim.']).length === 0),
    check('runtime-imports-exports-support-bundle-diff', includesAll(runtime, ['createKernelKitSupportBundleDiff', 'validateKernelKitSupportBundleDiff', 'kernelKitSupportBundleDiff', 'KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT']).length === 0),
    check('types-declare-support-bundle-diff', includesAll(types, ['KernelKitSupportBundleDiff', 'createKernelKitSupportBundleDiff', 'validateKernelKitSupportBundleDiff']).length === 0),
    check('page-runner-exposes-diff-api', includesAll(runner, ['diffKernelKitSupportBundle', 'renderKernelKitSupportBundleDiff', 'diffSupportBundle', 'window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_DIFF']).length === 0),
    check('html-exposes-diff-controls', includesAll(page, ['diff-kernel-kit-support-bundle', 'kernel-kit-support-diff-output', 'Support-bundle diff']).length === 0),
    check('browser-probe-drives-diff-api', includesAll(browserProbe, ['BrowserRTKernelKitDemo.diffSupportBundle', 'supportBundleDiff', 'validateKernelKitSupportBundleDiff']).length === 0),
    check('manifest-tasks-present', ['demo:kernel-kit-support-bundle-diff-proof','facility:kernel-kit-support-bundle-diff-audit'].every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-diff', ['demo:kernel-kit-support-bundle-diff-proof','facility:kernel-kit-support-bundle-diff-audit'].every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && includesAll(body, ['support-bundle diff', 'No production support-bundle diff claim.', 'No automated regression detection claim.', 'browser-light']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) }),
    check('non-claims-preserved', proof.nonClaims.includes('No production runtime claim.') && proof.nonClaims.includes('No production support-bundle diff claim.') && proof.nonClaims.includes('No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-support-bundle-diff-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Release-tier contract audit for the Kernel Kit support-bundle diff: source/runtime/types/page/browser probe/manifest/docs/non-claim wiring without launching Chromium.',
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

// Static audit markers: facility:kernel-kit-support-bundle-diff-audit; diffSupportBundle; No production support-bundle diff claim.; No automated regression detection claim.
