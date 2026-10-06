#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-lifecycle-checkpoint-audit. Static/runtime contract audit for the Kernel Kit lifecycle-risk checkpoint.
import { writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  validateKernelKitLifecycleCheckpoint,
  KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runLifecycleCheckpointProbe } from './kernel_kit_lifecycle_checkpoint_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-LIFECYCLE-CHECKPOINT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runLifecycleCheckpointProbe();
  const validation = proof.checkpoint?.validation || validateKernelKitLifecycleCheckpoint(proof.checkpoint);
  const moduleSource = await text('src/kernel-kit-lifecycle-checkpoint.mjs');
  const demoSource = await text('src/kernel-kit-demo.mjs');
  const runtimeSource = await text('src/browserrt.mjs');
  const typesSource = await text('src/types.d.ts');
  const browserRunner = await text('src/kernel-kit-demo-browser-runner.mjs');
  const demoRunner = await text('demo/kernel-kit-demo-runner.mjs');
  const browserProbe = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const supportProbe = await text('tools/kernel_kit_support_bundle_probe.mjs');
  const packageRelease = await text('tools/package_release.py');
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const docs = [
    'docs/40-validation/kernel-kit-lifecycle-checkpoint-slice.md',
    'docs/40-validation/kernel-kit-lifecycle-checkpoint-contract-audit-slice.md'
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set(manifest.tasks.map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => [...(surface.currentTaskIds || []), ...(surface.manifestTasks || [])]));
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true && proof.proof?.requiredRowsPresent === true && proof.browserHeavyValidation?.ok === true && proof.proof?.negativeCheckpointRejected === true, { validation, browserHeavyValidation: proof.browserHeavyValidation }),
    check('module-defines-risk-rows', missing(moduleSource, [KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT, 'KERNEL_KIT_LIFECYCLE_CHECKPOINT_REQUIRED_ROWS', 'quota-pressure-backpressure-evidence', 'session-coordination-stale-handoff-evidence', 'browser:kernel-kit-session-coordination-checkpoint-proof', 'browser:opfs-lane-quota-backpressure-proof', 'quota-eviction-survival-deferred', 'cross-browser-mobile-lifecycle-deferred', 'side-channel-privacy-deferred', 'createKernelKitLifecycleCheckpoint', 'validateKernelKitLifecycleCheckpoint', 'risk-checkpoint-ready']).length === 0),
    check('runtime-imports-exports-methods', missing(runtimeSource, ['createKernelKitLifecycleCheckpoint', 'validateKernelKitLifecycleCheckpoint', 'kernelKitLifecycleCheckpoint', 'validateKernelKitLifecycleCheckpoint(checkpoint)', 'kernel-kit-demo:lifecycle-checkpoint']).length === 0),
    check('support-bundle-carries-checkpoint', missing(demoSource, ['lifecycle-checkpoint', 'lifecycleCheckpointPresent', 'createKernelKitLifecycleCheckpoint', 'validateKernelKitLifecycleCheckpoint', 'demo:kernel-kit-lifecycle-checkpoint-proof', 'facility:kernel-kit-lifecycle-checkpoint-audit', 'storage-pressure-checkpoint', 'storagePressureCheckpointPresent', 'session-coordination-checkpoint', 'sessionCoordinationCheckpointPresent', 'browser:kernel-kit-session-coordination-checkpoint-proof', 'browser:opfs-lane-quota-backpressure-proof']).length === 0 && proof.proof?.supportBundleCarriesLifecycleCheckpoint === true),
    check('browser-runner-emits-checkpoint', missing(browserRunner, ['KERNEL_KIT_DEMO_NON_CLAIMS', 'kernelKitLifecycleCheckpoint', 'browser-kernel-kit-work', 'browser-kernel-kit-reload', 'lifecycleCheckpoint']).length === 0),
    check('demo-page-and-browser-probe-bind-checkpoint', missing(demoRunner, ['data-lifecycle-checkpoint-status', 'kernelKitLifecycleCheckpoint', 'demo-page-kernel-kit-work', 'demo-page-kernel-kit-reload', 'lifecycleCheckpoint']).length === 0 && missing(browserProbe, ['validateKernelKitLifecycleCheckpoint', 'work.lifecycleCheckpoint', 'reload.lifecycleCheckpoint', 'supportBundle.lifecycleCheckpoint', 'No production lifecycle-readiness claim.']).length === 0),
    check('types-declare-checkpoint', missing(typesSource, ['KernelKitLifecycleCheckpoint', 'KERNEL_KIT_LIFECYCLE_CHECKPOINT_FORMAT', 'createKernelKitLifecycleCheckpoint', 'validateKernelKitLifecycleCheckpoint', 'kernelKitLifecycleCheckpoint']).length === 0),
    check('support-probe-asserts-checkpoint', missing(supportProbe, ['lifecycleCheckpointPresent', 'lifecycleCheckpointReady', 'deferredLifecycleRisksExplicit', 'storagePressureCheckpointPresent', 'sessionCoordinationCheckpointPresent', 'browser:kernel-kit-session-coordination-checkpoint-proof', 'browser:opfs-lane-quota-backpressure-proof', 'browserrt-kernel-kit-lifecycle-checkpoint-v1']).length === 0),
    check('manifest-tasks-present', ['demo:kernel-kit-lifecycle-checkpoint-proof', 'facility:kernel-kit-lifecycle-checkpoint-audit'].every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-tasks', ['demo:kernel-kit-lifecycle-checkpoint-proof', 'facility:kernel-kit-lifecycle-checkpoint-audit'].every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('package-keeps-current-artifacts', missing(packageRelease, ['KERNEL-KIT-LIFECYCLE-CHECKPOINT-PROBE.json', 'KERNEL-KIT-LIFECYCLE-CHECKPOINT-CONTRACT-AUDIT.json']).length === 0),
    check('docs-explain-risk-refactor', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && missing(body, ['lifecycle checkpoint', 'quota pressure', 'quota/eviction', 'cross-browser/mobile', 'side-channel', 'not production readiness']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-lifecycle-checkpoint-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit that the Kernel Kit lifecycle-risk checkpoint is executable, product-path bound, package-retained, and wired through runtime/support-bundle/browser runner, demo page, and browser probe surfaces without launching Chromium.',
    proofId: proof.probe_id,
    checks,
    nonClaims: proof.nonClaims
  };
}

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runAudit();
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
  if (report.status !== 'passed') process.exitCode = 1;
}

// Static audit markers: facility:kernel-kit-lifecycle-checkpoint-audit; browser:opfs-lane-quota-backpressure-proof; browserrt-kernel-kit-lifecycle-checkpoint-v1; quota-pressure-backpressure-evidence; session-coordination-stale-handoff-evidence; browser:kernel-kit-session-coordination-checkpoint-proof; quota-eviction-survival-deferred; cross-browser-mobile-lifecycle-deferred; side-channel-privacy-deferred; not production readiness.
