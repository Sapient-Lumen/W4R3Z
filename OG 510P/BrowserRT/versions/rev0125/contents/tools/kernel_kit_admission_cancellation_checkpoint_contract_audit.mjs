#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-admission-cancellation-checkpoint-audit. Contract audit for release-light Kernel Kit admission/cancellation checkpoint.
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitAdmissionCancellationCheckpoint } from '../src/browserrt.mjs';
import { runProbe as runAdmissionCancellationProbe } from './kernel_kit_admission_cancellation_checkpoint_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-ADMISSION-CANCELLATION-CHECKPOINT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runAdmissionCancellationProbe();
  const validation = validateKernelKitAdmissionCancellationCheckpoint(proof.checkpoint);
  const moduleSource = await text('src/kernel-kit-admission-cancellation-checkpoint.mjs');
  const admissionSource = await text('src/admission-control.mjs');
  const lifecycleSource = await text('src/kernel-kit-lifecycle-checkpoint.mjs');
  const demoSource = await text('src/kernel-kit-demo.mjs');
  const runtimeSource = await text('src/browserrt.mjs');
  const typesSource = await text('src/types.d.ts');
  const supportProbe = await text('tools/kernel_kit_support_bundle_probe.mjs');
  const admissionProbe = await text('tools/admission_abort_release_probe.mjs');
  const packageRelease = await text('tools/package_release.py');
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const docs = [
    'docs/40-validation/admission-abort-release-slice.md',
    'docs/40-validation/kernel-kit-admission-cancellation-checkpoint-slice.md',
    'docs/40-validation/kernel-kit-admission-cancellation-checkpoint-contract-audit-slice.md'
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.tasks || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => [...(surface.currentTaskIds || []), ...(surface.manifestTasks || [])]));
  const requiredTasks = ['admission:abort-release-proof', 'demo:kernel-kit-admission-cancellation-checkpoint-proof', 'facility:kernel-kit-admission-cancellation-checkpoint-audit'];
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true && proof.proof?.observedCheckpointValid === true && proof.proof?.defaultDeferredCheckpointValid === true, { validation }),
    check('module-defines-admission-cancellation-rows', missing(moduleSource, ['browserrt-kernel-kit-admission-cancellation-checkpoint-v1', 'pre-aborted-admission-rejects-no-mutation', 'bound-lease-abort-releases-permit', 'dual-signal-abort-source-releases-once', 'manual-release-detaches-abort-listener', 'No exactly-once execution', 'No browser Worker', 'createKernelKitAdmissionCancellationCheckpoint', 'validateKernelKitAdmissionCancellationCheckpoint']).length === 0),
    check('admission-controller-binds-abort-signal-release', missing(admissionSource, ['signal = null', 'abortSignal = null', 'rejected-aborted', 'admission:abort-release', 'abortSignalReleased', 'abortSignalBindings', 'boundAbortLeaseCount']).length === 0),
    check('runtime-imports-exports-methods', missing(runtimeSource, ['createKernelKitAdmissionCancellationCheckpoint', 'validateKernelKitAdmissionCancellationCheckpoint', 'kernelKitAdmissionCancellationCheckpoint', 'kernel-kit-demo:admission-cancellation-checkpoint', 'KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT']).length === 0),
    check('types-declare-admission-cancellation-checkpoint', missing(typesSource, ['KernelKitAdmissionCancellationCheckpoint', 'KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT', 'createKernelKitAdmissionCancellationCheckpoint', 'validateKernelKitAdmissionCancellationCheckpoint', 'kernelKitAdmissionCancellationCheckpoint', 'abortSignal']).length === 0),
    check('support-bundle-carries-admission-cancellation-checkpoint', missing(demoSource, ['admission-cancellation-checkpoint', 'admissionCancellationCheckpointPresent', 'admission:abort-release-proof', 'admission-cancellation-artifact', 'createKernelKitAdmissionCancellationCheckpoint', 'validateKernelKitAdmissionCancellationCheckpoint']).length === 0),
    check('lifecycle-carries-admission-row', missing(lifecycleSource, ['admission-cancellation-backpressure-evidence', 'admission:abort-release-proof', 'admissionCancellationObservedOrDeferred']).length === 0 && proof.proof?.lifecycleCarriesAdmissionCancellationRisk === true),
    check('support-probe-asserts-admission-cancellation-checkpoint', missing(supportProbe, ['admissionCancellationCheckpointPresent', 'admission-cancellation-artifact', 'admission:abort-release-proof', 'admissionCancellationDefaultDeferred']).length === 0),
    check('admission-probe-exercises-abort-release', missing(admissionProbe, ['preAbortedRejectedNoMutation', 'boundLeaseAbortReleasedPermit', 'dualSignalAbortSourceReleasesOnce', 'manualReleaseDetachesAbortListener', 'invalidSignalShapeRejectedLocally']).length === 0),
    check('manifest-tasks-present', requiredTasks.every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-tasks', requiredTasks.every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('package-keeps-current-artifacts', missing(packageRelease, ['ADMISSION-ABORT-RELEASE-PROBE.json', 'KERNEL-KIT-ADMISSION-CANCELLATION-CHECKPOINT-PROBE.json', 'KERNEL-KIT-ADMISSION-CANCELLATION-CHECKPOINT-CONTRACT-AUDIT.json']).length === 0),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && missing(body, ['admission', 'AbortSignal', 'pre-aborted', 'no mutation', 'release', 'exactly-once', 'Browser Worker', 'not production']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-admission-cancellation-checkpoint-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit that admission/cancellation release is executable, support-bundle/lifecycle bound, release-light, package-retained, and honest about exactly-once, Browser Worker, provider rollback, fairness, and production non-claims.',
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

// Static audit markers: facility:kernel-kit-admission-cancellation-checkpoint-audit; demo:kernel-kit-admission-cancellation-checkpoint-proof; admission:abort-release-proof; browserrt-kernel-kit-admission-cancellation-checkpoint-v1; admission-cancellation-artifact; admission-cancellation-backpressure-evidence; boundAbortLeaseCount; abortSignalReleased; not production cancellation.
