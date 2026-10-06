#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-recovery-checkpoint-audit. Contract audit for the Kernel Kit recovery checkpoint.
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  validateKernelKitRecoveryCheckpoint
} from '../src/browserrt.mjs';
import { runProbe as runRecoveryProbe } from './kernel_kit_recovery_checkpoint_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-RECOVERY-CHECKPOINT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runRecoveryProbe();
  const validation = validateKernelKitRecoveryCheckpoint(proof.checkpoint);
  const moduleSource = await text('src/kernel-kit-recovery-checkpoint.mjs');
  const lifecycleSource = await text('src/kernel-kit-lifecycle-checkpoint.mjs');
  const demoSource = await text('src/kernel-kit-demo.mjs');
  const runtimeSource = await text('src/browserrt.mjs');
  const typesSource = await text('src/types.d.ts');
  const supportProbe = await text('tools/kernel_kit_support_bundle_probe.mjs');
  const browserProbe = await text('tools/browser_kernel_kit_recovery_checkpoint_probe.mjs');
  const packageRelease = await text('tools/package_release.py');
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const docs = [
    'docs/40-validation/kernel-kit-recovery-checkpoint-slice.md',
    'docs/40-validation/browser-kernel-kit-recovery-checkpoint-slice.md',
    'docs/40-validation/kernel-kit-recovery-checkpoint-contract-audit-slice.md'
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.tasks || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => [...(surface.currentTaskIds || []), ...(surface.manifestTasks || [])]));
  const requiredTasks = ['demo:kernel-kit-recovery-checkpoint-proof', 'facility:kernel-kit-recovery-checkpoint-audit', 'browser:kernel-kit-recovery-checkpoint-proof'];
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true && proof.proof?.syntheticObservedCheckpointValid === true && proof.proof?.supportBundleDefaultDeferredValid === true, { validation }),
    check('module-defines-recovery-rows', missing(moduleSource, ['browserrt-kernel-kit-recovery-checkpoint-v1', 'same-origin-profile-restart-boundary', 'sigkill-interruption-boundary-observed', 'interrupted-write-not-silently-corrupt', 'transient-opfs-open-failure-retry-observed', 'unsettled-orphan-review-gate-observed', 'No automatic unsettled-orphan cleanup', 'No general crash recovery', 'createKernelKitRecoveryCheckpoint', 'validateKernelKitRecoveryCheckpoint']).length === 0),
    check('runtime-imports-exports-methods', missing(runtimeSource, ['createKernelKitRecoveryCheckpoint', 'validateKernelKitRecoveryCheckpoint', 'kernelKitRecoveryCheckpoint', 'kernel-kit-demo:recovery-checkpoint', 'KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT']).length === 0),
    check('types-declare-recovery-checkpoint', missing(typesSource, ['KernelKitRecoveryCheckpoint', 'KERNEL_KIT_RECOVERY_CHECKPOINT_FORMAT', 'createKernelKitRecoveryCheckpoint', 'validateKernelKitRecoveryCheckpoint', 'kernelKitRecoveryCheckpoint']).length === 0),
    check('support-bundle-carries-recovery-checkpoint', missing(demoSource, ['recovery-checkpoint', 'recoveryCheckpointPresent', 'browser:kernel-kit-recovery-checkpoint-proof', 'browser-recovery-artifact', 'createKernelKitRecoveryCheckpoint', 'validateKernelKitRecoveryCheckpoint']).length === 0),
    check('lifecycle-carries-recovery-row', missing(lifecycleSource, ['recovery-interruption-boundary-evidence', 'recovery-orphan-review-gate-evidence', 'browser:kernel-kit-recovery-checkpoint-proof', 'recoveryObservedOrDeferred', 'recoveryOrphanReviewObservedOrDeferred']).length === 0 && proof.proof?.lifecycleCarriesRecoveryRisk === true),
    check('support-probe-asserts-recovery-checkpoint', missing(supportProbe, ['recoveryCheckpointPresent', 'browser-recovery-artifact', 'browser:kernel-kit-recovery-checkpoint-proof', 'recoveryDefaultDeferred']).length === 0),
    check('browser-probe-aggregates-real-browser-heavy-inputs', missing(browserProbe, ['browser_opfs_abrupt_kill_boundary_probe.mjs', 'browser_opfs_block_store_open_failure_recovery_probe.mjs', 'browser_opfs_web_lock_unsettled_orphan_review_probe.mjs', 'BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE', 'sameOriginProfileRestartObserved', 'interruptedWriteNotAcceptedCorrupt', 'transientOpenFailureRetryObserved', 'unsettledOrphanReviewGateObserved']).length === 0),
    check('manifest-tasks-present', requiredTasks.every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-tasks', requiredTasks.every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('package-keeps-current-artifacts', missing(packageRelease, ['KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE.json', 'KERNEL-KIT-RECOVERY-CHECKPOINT-CONTRACT-AUDIT.json', 'BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE.json']).length === 0),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && missing(body, ['recovery checkpoint', 'SIGKILL', 'interrupted write', 'open failure', 'orphan', 'browser-heavy', 'not production', 'fsync']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-recovery-checkpoint-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit that the Kernel Kit recovery checkpoint is executable, support-bundle/lifecycle bound, browser-heavy explicit, package-retained, and honest about crash/fsync/orphan-cleanup/cross-browser non-claims.',
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

// Static audit markers: facility:kernel-kit-recovery-checkpoint-audit; demo:kernel-kit-recovery-checkpoint-proof; browser:kernel-kit-recovery-checkpoint-proof; browserrt-kernel-kit-recovery-checkpoint-v1; browser-recovery-artifact; recovery-interruption-boundary-evidence; recovery-orphan-review-gate-evidence; unsettledOrphanReviewGateObserved; not production recovery.
