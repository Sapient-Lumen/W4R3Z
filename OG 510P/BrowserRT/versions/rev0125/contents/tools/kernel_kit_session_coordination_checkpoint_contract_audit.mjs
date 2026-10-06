#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-session-coordination-checkpoint-audit. Contract audit for the Kernel Kit session coordination checkpoint.
import { writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  validateKernelKitSessionCoordinationCheckpoint
} from '../src/browserrt.mjs';
import { runProbe as runSessionCoordinationProbe } from './kernel_kit_session_coordination_checkpoint_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runSessionCoordinationProbe();
  const validation = validateKernelKitSessionCoordinationCheckpoint(proof.checkpoint);
  const moduleSource = await text('src/kernel-kit-session-coordination-checkpoint.mjs');
  const lifecycleSource = await text('src/kernel-kit-lifecycle-checkpoint.mjs');
  const demoSource = await text('src/kernel-kit-demo.mjs');
  const runtimeSource = await text('src/browserrt.mjs');
  const typesSource = await text('src/types.d.ts');
  const supportProbe = await text('tools/kernel_kit_support_bundle_probe.mjs');
  const browserProbe = await text('tools/browser_kernel_kit_session_coordination_checkpoint_probe.mjs');
  const browserDemoProbe = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const packageRelease = await text('tools/package_release.py');
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const docs = [
    'docs/40-validation/kernel-kit-session-coordination-checkpoint-slice.md',
    'docs/40-validation/browser-kernel-kit-session-coordination-checkpoint-slice.md',
    'docs/40-validation/kernel-kit-session-coordination-checkpoint-contract-audit-slice.md'
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => [...(surface.currentTaskIds || []), ...(surface.manifestTasks || [])]));
  const requiredTasks = ['demo:kernel-kit-session-coordination-checkpoint-proof', 'facility:kernel-kit-session-coordination-checkpoint-audit', 'browser:kernel-kit-session-coordination-checkpoint-proof'];
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true && proof.proof?.syntheticObservedCheckpointValid === true && proof.proof?.supportBundleDefaultDeferredValid === true, { validation }),
    check('module-defines-session-rows', missing(moduleSource, ['browserrt-kernel-kit-session-coordination-checkpoint-v1', 'exclusive-lock-contention-observed', 'queued-lock-release-order-observed', 'local-handoff-single-use-clear-observed', 'stale-handoff-read-deferred-or-null', 'abandoned-lock-release-deferred', 'No Web Locks fairness', 'No crash, process-kill', 'createKernelKitSessionCoordinationCheckpoint', 'validateKernelKitSessionCoordinationCheckpoint']).length === 0),
    check('runtime-imports-exports-methods', missing(runtimeSource, ['createKernelKitSessionCoordinationCheckpoint', 'validateKernelKitSessionCoordinationCheckpoint', 'kernelKitSessionCoordinationCheckpoint', 'kernel-kit-demo:session-coordination-checkpoint', 'KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT']).length === 0),
    check('types-declare-session-checkpoint', missing(typesSource, ['KernelKitSessionCoordinationCheckpoint', 'KERNEL_KIT_SESSION_COORDINATION_CHECKPOINT_FORMAT', 'createKernelKitSessionCoordinationCheckpoint', 'validateKernelKitSessionCoordinationCheckpoint', 'kernelKitSessionCoordinationCheckpoint']).length === 0),
    check('support-bundle-carries-session-checkpoint', missing(demoSource, ['session-coordination-checkpoint', 'sessionCoordinationCheckpointPresent', 'browser:kernel-kit-session-coordination-checkpoint-proof', 'browser-session-coordination-artifact', 'createKernelKitSessionCoordinationCheckpoint', 'validateKernelKitSessionCoordinationCheckpoint']).length === 0),
    check('lifecycle-carries-session-row', missing(lifecycleSource, ['session-coordination-stale-handoff-evidence', 'browser:kernel-kit-session-coordination-checkpoint-proof', 'sessionCoordinationObservedOrDeferred']).length === 0 && proof.proof?.lifecycleCarriesSessionCoordinationRisk === true),
    check('support-probe-asserts-session-checkpoint', missing(supportProbe, ['sessionCoordinationCheckpointPresent', 'browser-session-coordination-artifact', 'browser:kernel-kit-session-coordination-checkpoint-proof', 'sessionCoordinationDefaultDeferred']).length === 0),
    check('browser-probe-is-real-browser-heavy', missing(browserProbe, ['runManagedBrowserPage', 'openPageTarget', 'navigator.locks.request', 'navigator.locks.query', 'localStorage.setItem', 'localStorage.removeItem', 'storage event', 'exclusiveIfAvailableDenied', 'queuedAcquiredAfterRelease', 'handoffSingleUseClearObserved', 'staleReadReturnedNull']).length === 0),
    check('browser-demo-probe-preserves-support-path', missing(browserDemoProbe, ['validateKernelKitSupportBundle', 'supportBundleEvidenceLedger', 'BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE']).length === 0),
    check('manifest-tasks-present', requiredTasks.every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-tasks', requiredTasks.every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('package-keeps-current-artifacts', missing(packageRelease, ['KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE.json', 'KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-CONTRACT-AUDIT.json', 'BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE.json']).length === 0),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && missing(body, ['session coordination checkpoint', 'Web Locks fairness', 'crash recovery', 'stale handoff', 'browser-heavy', 'not production']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-session-coordination-checkpoint-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit that the Kernel Kit session coordination checkpoint is executable, support-bundle/lifecycle bound, browser-heavy explicit, package-retained, and non-claim honest.',
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

// Static audit markers: facility:kernel-kit-session-coordination-checkpoint-audit; demo:kernel-kit-session-coordination-checkpoint-proof; browser:kernel-kit-session-coordination-checkpoint-proof; browserrt-kernel-kit-session-coordination-checkpoint-v1; session-coordination-checkpoint; browser-session-coordination-artifact; session-coordination-stale-handoff-evidence; not production coordination.
