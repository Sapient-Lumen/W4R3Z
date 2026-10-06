#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-evidence-file-checkpoint-audit. Contract audit for file-backed evidence checkpoint wiring.
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitSupportBundleEvidenceCheckpoint } from '../src/browserrt.mjs';
import { runProbe as runFileCheckpointProbe } from './kernel_kit_support_bundle_evidence_file_checkpoint_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-FILE-CHECKPOINT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runFileCheckpointProbe();
  const checkpointValidation = validateKernelKitSupportBundleEvidenceCheckpoint(proof.checkpoint || {});
  const source = await text('src/kernel-kit-demo.mjs');
  const fileProbe = await text('tools/kernel_kit_support_bundle_evidence_file_checkpoint_probe.mjs');
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
    check('proof-validates-file-backed-checkpoint', proof.status === 'passed' && checkpointValidation.ok === true && proof.proof?.artifactFilesRead === true && proof.proof?.admissionCancellationProofFileRead === true && proof.proof?.admissionCancellationProofSatisfied === true && proof.proof?.missingImportFileRejected === true, { checkpointValidation }),
    check('ledger-proof-path-matches-actual-readiness-artifact', source.includes('readinessGate.inputProof.evidenceBound') && !source.includes("'inputProof.evidenceBound'])")),
    check('file-probe-reads-bounded-json-artifacts', missing(fileProbe, ['readFile','safeArtifactPath','artifacts/validation/','artifacts/audit/','sha256RecordedForReadFiles','artifactFilesRead','actualReadinessNestedPathChecked','admission-cancellation-artifact','admissionCancellationProofFileRead','admissionCancellationProofSatisfied']).length === 0),
    check('file-probe-nonclaims-command-browser-authenticity', missing(fileProbe, ['No artifact authenticity or signature claim.','No command execution claim.','No browser launch claim.','fileCheckpointDoesNotExecuteCommands','fileCheckpointDoesNotLaunchBrowser']).length === 0),
    check('manifest-task-present', taskIds.has('demo:kernel-kit-support-bundle-evidence-file-checkpoint-proof') && taskIds.has('facility:kernel-kit-support-bundle-evidence-file-checkpoint-audit')),
    check('test-kernel-kit-runs-file-checkpoint-proof-and-audit', testKernelKit.includes('demo:kernel-kit-support-bundle-evidence-file-checkpoint-proof') && testKernelKit.includes('facility:kernel-kit-support-bundle-evidence-file-checkpoint-audit')),
    check('impact-and-inventory-cover-file-checkpoint', impactIds.has('demo:kernel-kit-support-bundle-evidence-file-checkpoint-proof') && impactIds.has('facility:kernel-kit-support-bundle-evidence-file-checkpoint-audit') && inventoryIds.has('demo:kernel-kit-support-bundle-evidence-file-checkpoint-proof') && inventoryIds.has('facility:kernel-kit-support-bundle-evidence-file-checkpoint-audit')),
    check('package-retains-file-checkpoint-artifacts', packageRelease.includes('KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-FILE-CHECKPOINT-PROBE') && packageRelease.includes('KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-FILE-CHECKPOINT-CONTRACT-AUDIT')),
    check('non-claims-preserved', ['No artifact authenticity or signature claim.','No command execution claim.','No browser launch claim.','No durable artifact retention guarantee.'].every((claim) => proof.nonClaims?.includes(claim)))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-support-bundle-evidence-file-checkpoint-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit that the Kernel Kit support-bundle evidence checkpoint can be built from bounded, parsed JSON artifact files named by the ledger while preserving non-claims around authenticity, command execution, and browser launch.',
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

// Static audit markers: facility:kernel-kit-support-bundle-evidence-file-checkpoint-audit; demo:kernel-kit-support-bundle-evidence-file-checkpoint-proof; actualReadinessNestedPathChecked; admission-cancellation-artifact; admissionCancellationProofFileRead; admissionCancellationProofSatisfied; package-retains-file-checkpoint-artifacts; No command execution claim.
