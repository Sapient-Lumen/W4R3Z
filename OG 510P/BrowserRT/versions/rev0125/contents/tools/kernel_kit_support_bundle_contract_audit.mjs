#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-audit. Contract audit for Kernel Kit support-bundle surfaces.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitSupportBundle, validateKernelKitSupportBundleReplayPlan, validateKernelKitSupportBundlePrivacyScrub } from '../src/browserrt.mjs';
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
  const replayPlan = proof.replayPlan || proof.supportBundle?.replayPlan;
  const replayValidation = proof.replayValidation || proof.replaySummary?.validation || validateKernelKitSupportBundleReplayPlan(replayPlan);
  const privacyScrubValidation = validateKernelKitSupportBundlePrivacyScrub(proof.supportBundle?.privacyScrub || {});
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
    check('proof-validates', proof.status === 'passed' && validation.ok === true && replayValidation?.ok === true && proof.proof?.evidenceLedgerPresent === true && proof.proof?.privacyScrubPresent === true && proof.proof?.sessionCoordinationCheckpointPresent === true && proof.proof?.recoveryCheckpointPresent === true && privacyScrubValidation.ok === true, { validation, replayValidation, privacyScrubValidation }),
    check('source-exports-support-bundle', includesAll(source, ['createKernelKitSupportBundle', 'validateKernelKitSupportBundle', 'createKernelKitSupportBundleReplayPlan', 'validateKernelKitSupportBundleReplayPlan', 'createKernelKitSupportBundleEvidenceLedger', 'validateKernelKitSupportBundleEvidenceLedger', 'browserrt-kernel-kit-support-bundle-v1', 'browserrt-kernel-kit-support-bundle-replay-plan-v1', 'browserrt-kernel-kit-support-bundle-evidence-ledger-v1', 'No production support-bundle claim.', 'No automated replay execution claim.', 'storage-pressure-checkpoint', 'storagePressureCheckpointPresent', 'browser:opfs-lane-quota-backpressure-proof', 'browser-storage-pressure-artifact', 'Quota-pressure/backpressure checkpoint is browser-heavy explicit', 'privacy-scrub-checkpoint', 'privacyScrubPresent', 'session-coordination-checkpoint', 'sessionCoordinationCheckpointPresent', 'browser:kernel-kit-session-coordination-checkpoint-proof', 'browser-session-coordination-artifact', 'browserrt-kernel-kit-session-coordination-checkpoint-v1', 'browserrt-kernel-kit-recovery-checkpoint-v1', 'recovery-checkpoint', 'recoveryCheckpointPresent', 'browser:kernel-kit-recovery-checkpoint-proof', 'browser-recovery-artifact', 'Recovery checkpoint is browser-heavy explicit', 'browserrt-kernel-kit-support-bundle-privacy-scrub-v1']).length === 0),
    check('runtime-imports-exports-support-bundle', includesAll(runtime, ['createKernelKitSupportBundle', 'validateKernelKitSupportBundle', 'createKernelKitSupportBundleReplayPlan', 'validateKernelKitSupportBundleReplayPlan', 'createKernelKitSupportBundleEvidenceLedger', 'validateKernelKitSupportBundleEvidenceLedger', 'kernelKitSupportBundle', 'kernelKitSupportBundleReplayPlan', 'kernelKitSupportBundleEvidenceLedger', 'KERNEL_KIT_SUPPORT_BUNDLE_FORMAT', 'KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_FORMAT', 'createKernelKitSupportBundlePrivacyScrub', 'validateKernelKitSupportBundlePrivacyScrub', 'kernelKitSupportBundlePrivacyScrub', 'createKernelKitSessionCoordinationCheckpoint', 'validateKernelKitSessionCoordinationCheckpoint', 'kernelKitSessionCoordinationCheckpoint', 'createKernelKitRecoveryCheckpoint', 'validateKernelKitRecoveryCheckpoint', 'kernelKitRecoveryCheckpoint']).length === 0),
    check('types-declare-support-bundle', includesAll(types, ['KernelKitSupportBundle', 'KernelKitSupportBundleReplayPlan', 'KernelKitSupportBundleEvidenceLedger', 'createKernelKitSupportBundle', 'validateKernelKitSupportBundle', 'createKernelKitSupportBundleReplayPlan', 'validateKernelKitSupportBundleReplayPlan', 'createKernelKitSupportBundleEvidenceLedger', 'validateKernelKitSupportBundleEvidenceLedger', 'kernelKitSupportBundleReplayPlan', 'kernelKitSupportBundleEvidenceLedger', 'KernelKitSupportBundlePrivacyScrub', 'kernelKitSupportBundlePrivacyScrub', 'KernelKitSessionCoordinationCheckpoint', 'kernelKitSessionCoordinationCheckpoint', 'KernelKitRecoveryCheckpoint', 'kernelKitRecoveryCheckpoint']).length === 0),
    check('page-runner-exposes-support-api', includesAll(runner, ['buildKernelKitSupportBundle', 'renderKernelKitSupportBundle', 'buildSupportBundle', 'buildSupportBundleEvidenceLedger', 'replayKernelKitSupportBundle', 'renderKernelKitSupportBundleReplayPlan', 'window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE', 'window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_REPLAY_PLAN', 'window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB', 'scrubSupportBundle']).length === 0),
    check('html-exposes-support-controls', includesAll(page, ['build-kernel-kit-support-bundle', 'replay-kernel-kit-support-bundle', 'kernel-kit-support-output', 'kernel-kit-support-replay-output', 'Support bundle', 'scrub-kernel-kit-support-bundle', 'kernel-kit-support-privacy-output']).length === 0),
    check('browser-probe-drives-support-api', includesAll(browserProbe, ['BrowserRTKernelKitDemo.buildSupportBundle', 'BrowserRTKernelKitDemo.buildSupportBundleEvidenceLedger', 'BrowserRTKernelKitDemo.replaySupportBundle', 'supportBundleEvidenceLedger', 'supportBundleReplay', 'validateKernelKitSupportBundle', 'validateKernelKitSupportBundleReplayPlan', 'validateKernelKitSupportBundleEvidenceLedger', 'validateKernelKitSupportBundlePrivacyScrub', 'supportBundlePrivacyScrub']).length === 0),
    check('manifest-tasks-present', ['demo:kernel-kit-support-bundle-proof','facility:kernel-kit-support-bundle-audit','demo:kernel-kit-support-bundle-privacy-scrub-proof','facility:kernel-kit-support-bundle-privacy-scrub-audit'].every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-support-bundle', ['demo:kernel-kit-support-bundle-proof','facility:kernel-kit-support-bundle-audit','demo:kernel-kit-support-bundle-privacy-scrub-proof','facility:kernel-kit-support-bundle-privacy-scrub-audit'].every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && includesAll(body, ['support bundle', 'No production support-bundle claim.', 'No automated failure triage claim.', 'browser-light', 'quota pressure']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) }),
    check('evidence-ledger-contract-present', proof.proof?.evidenceLedgerPresent === true && proof.supportBundle?.evidenceLedger?.status === 'evidence-ledger-ready' && (proof.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('BROWSER-KERNEL-KIT-DEMO-PROBE')) && (proof.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE')) && (proof.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE')) && (proof.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE'))),
    check('privacy-scrub-contract-present', proof.proof?.privacyScrubPresent === true && privacyScrubValidation.ok === true && proof.supportBundle?.privacyScrub?.proof?.sensitiveFieldsRedacted === true),
    check('session-coordination-contract-present', proof.proof?.sessionCoordinationCheckpointPresent === true && proof.supportBundle?.sessionCoordination?.commandId === 'browser:kernel-kit-session-coordination-checkpoint-proof' && (proof.supportBundle?.evidenceLedger?.entries || []).some((entry) => entry.id === 'browser-session-coordination-artifact')),
    check('recovery-contract-present', proof.proof?.recoveryCheckpointPresent === true && proof.supportBundle?.recoveryCheckpoint?.commandId === 'browser:kernel-kit-recovery-checkpoint-proof' && (proof.supportBundle?.evidenceLedger?.entries || []).some((entry) => entry.id === 'browser-recovery-artifact')),
    check('non-claims-preserved', proof.nonClaims.includes('No production runtime claim.') && proof.nonClaims.includes('No production support-bundle claim.') && proof.nonClaims.includes('No automated replay execution claim.') && proof.nonClaims.includes('No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'))
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

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runAudit();
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
  if (report.status !== 'passed') process.exitCode = 1;
}

// Static audit markers: facility:kernel-kit-support-bundle-audit; buildSupportBundle; storage-pressure-checkpoint; browser:opfs-lane-quota-backpressure-proof; browser-storage-pressure-artifact; browser:kernel-kit-session-coordination-checkpoint-proof; browser-session-coordination-artifact; browser:kernel-kit-recovery-checkpoint-proof; browser-recovery-artifact; recoveryCheckpointPresent; No production support-bundle claim.; No automated failure triage claim.; No automated replay execution claim.
