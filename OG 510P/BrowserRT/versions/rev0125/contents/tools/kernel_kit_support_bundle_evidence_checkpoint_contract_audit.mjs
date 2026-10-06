#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-evidence-checkpoint-audit. Contract audit for support-bundle evidence checkpoint wiring.
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitSupportBundleEvidenceCheckpoint } from '../src/browserrt.mjs';
import { runProbe as runEvidenceCheckpointProbe } from './kernel_kit_support_bundle_evidence_checkpoint_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-CHECKPOINT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runEvidenceCheckpointProbe();
  const checkpointValidation = validateKernelKitSupportBundleEvidenceCheckpoint(proof.checkpoint || {});
  const source = await text('src/kernel-kit-demo.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const browserProbe = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const packageJson = JSON.parse(await text('package.json'));
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const packageRelease = await text('tools/package_release.py');
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactIds = new Set([...(impact.tasks || impact.items || []).map((task) => task.id), ...(impact.rules || []).flatMap((rule) => rule.taskIds || rule.tasks || []), ...(impact.impacts || []).flatMap((row) => row.taskIds || row.requiredTaskIds || row.required || [])]);
  const inventoryIds = new Set([...(inventory.surfaces || inventory.tasks || inventory.items || []).map((task) => task.id), ...(inventory.surfaces || []).flatMap((surface) => surface.manifestTasks || surface.currentTaskIds || [])]);
  const testKernelKit = packageJson.scripts?.['test:kernel-kit'] || '';
  const checks = [
    check('proof-validates-checkpoint', proof.status === 'passed' && checkpointValidation.ok === true && proof.proof?.missingImportRejected === true && proof.proof?.fullReplayRequiresBrowserArtifact === true, { checkpointValidation }),
    check('source-exports-evidence-checkpoint-contract', missing(source, ['createKernelKitSupportBundleEvidenceCheckpoint','validateKernelKitSupportBundleEvidenceCheckpoint','KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT','browserrt-kernel-kit-support-bundle-evidence-checkpoint-v1','requiredProofPathsSatisfied','checkpointDoesNotExecuteCommands']).length === 0),
    check('runtime-exports-evidence-checkpoint-contract', missing(runtime, ['createKernelKitSupportBundleEvidenceCheckpoint','validateKernelKitSupportBundleEvidenceCheckpoint','kernelKitSupportBundleEvidenceCheckpoint','validateKernelKitSupportBundleEvidenceCheckpoint','KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT']).length === 0),
    check('types-declare-evidence-checkpoint-contract', missing(types, ['KernelKitSupportBundleEvidenceCheckpoint','createKernelKitSupportBundleEvidenceCheckpoint','validateKernelKitSupportBundleEvidenceCheckpoint','KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT_FORMAT','kernelKitSupportBundleEvidenceCheckpoint']).length === 0),
    check('page-exposes-evidence-checkpoint', missing(runner, ['buildSupportBundleEvidenceCheckpoint','validateSupportBundleEvidenceCheckpoint','window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_CHECKPOINT','Evidence checkpoint','checkpointDoesNotExecuteCommands']).length === 0),
    check('browser-proof-asserts-evidence-checkpoint', missing(browserProbe, ['validateKernelKitSupportBundleEvidenceCheckpoint','supportBundleEvidenceCheckpoint','requiredProofPathsSatisfied','support-bundle evidence checkpoint should validate']).length === 0),
    check('manifest-task-present', taskIds.has('demo:kernel-kit-support-bundle-evidence-checkpoint-proof') && taskIds.has('facility:kernel-kit-support-bundle-evidence-checkpoint-audit')),
    check('test-kernel-kit-runs-focused-proof-and-audit', testKernelKit.includes('demo:kernel-kit-support-bundle-evidence-checkpoint-proof') && testKernelKit.includes('facility:kernel-kit-support-bundle-evidence-checkpoint-audit')),
    check('impact-and-inventory-cover-focused-proof-and-audit', impactIds.has('demo:kernel-kit-support-bundle-evidence-checkpoint-proof') && impactIds.has('facility:kernel-kit-support-bundle-evidence-checkpoint-audit') && inventoryIds.has('demo:kernel-kit-support-bundle-evidence-checkpoint-proof') && inventoryIds.has('facility:kernel-kit-support-bundle-evidence-checkpoint-audit')),
    check('package-retains-focused-artifacts', packageRelease.includes('KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-CHECKPOINT-PROBE') && packageRelease.includes('KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-CHECKPOINT-CONTRACT-AUDIT')),
    check('non-claims-preserved', ['No production evidence-checkpoint claim.','No artifact authenticity or signature claim.','No filesystem artifact discovery claim.','No command execution claim.'].every((claim) => proof.nonClaims?.includes(claim)))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-support-bundle-evidence-checkpoint-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit that the Kernel Kit support-bundle evidence checkpoint machine-checks supplied compact reports against ledger proof paths without executing commands, reading files, or claiming artifact authenticity.',
    proofId: proof.probe_id,
    checks,
    nonClaims: proof.nonClaims || []
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(report, null, 2) + '\n');
console.log(out);
if (report.status !== 'passed') process.exitCode = 1;

// Static audit markers: facility:kernel-kit-support-bundle-evidence-checkpoint-audit; browserrt-kernel-kit-support-bundle-evidence-checkpoint-v1; buildSupportBundleEvidenceCheckpoint; requiredProofPathsSatisfied; No filesystem artifact discovery claim.; No command execution claim.
