#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-package-evidence-seal-audit. Contract audit for package-level evidence seal and release-manifest verifier binding.
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitSupportBundleEvidenceCheckpoint } from '../src/browserrt.mjs';
import { runProbe as runPackageEvidenceSealProbe, KERNEL_KIT_PACKAGE_EVIDENCE_SEAL_FORMAT } from './kernel_kit_support_bundle_package_evidence_seal_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-PACKAGE-EVIDENCE-SEAL-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runPackageEvidenceSealProbe();
  const checkpointValidation = validateKernelKitSupportBundleEvidenceCheckpoint(proof.checkpoint || {});
  const sealProbe = await text('tools/kernel_kit_support_bundle_package_evidence_seal_probe.mjs');
  const verifyRelease = await text('tools/verify_release.py');
  const packageRelease = await text('tools/package_release.py');
  const packageJson = JSON.parse(await text('package.json'));
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const testKernelKit = packageJson.scripts?.['test:kernel-kit'] || '';
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactIds = new Set([...(impact.tasks || impact.items || []).map((task) => task.id), ...(impact.rules || []).flatMap((rule) => rule.taskIds || rule.tasks || []), ...(impact.impacts || []).flatMap((row) => row.taskIds || row.requiredTaskIds || row.required || [])]);
  const inventoryIds = new Set([...(inventory.surfaces || inventory.tasks || inventory.items || []).map((task) => task.id), ...(inventory.surfaces || []).flatMap((surface) => surface.manifestTasks || surface.currentTaskIds || [])]);
  const sealedIds = new Set((proof.sealedArtifactRows || []).map((row) => row.id));
  const lineageRows = Array.isArray(proof.evidenceLineageRows) ? proof.evidenceLineageRows : [];
  const lineageBoundIds = new Set(lineageRows.filter((row) => row.status === 'bound').map((row) => row.id));
  const checks = [
    check('proof-validates-package-evidence-seal', proof.status === 'passed' && proof.format === KERNEL_KIT_PACKAGE_EVIDENCE_SEAL_FORMAT && proof.proof?.packageEvidenceSealValid === true && checkpointValidation.ok === true, { checkpointValidation }),
    check('seal-binds-browser-and-release-light-artifacts', ['support-bundle-proof-artifact','support-bundle-audit-artifact','support-bundle-import-artifact','readiness-gate-artifact','browser-kernel-kit-artifact','browser-session-coordination-artifact','browser-recovery-artifact'].every((id) => sealedIds.has(id)) && proof.proof?.browserKernelKitArtifactSatisfied === true && proof.proof?.browserSessionCoordinationArtifactSatisfied === true && proof.proof?.browserRecoveryArtifactSatisfied === true),
    check('cube-sanity-remains-command-only', proof.proof?.cubeSanityCommandOnlyNotFaked === true && (proof.commandOnlyRows || []).some((row) => row.id === 'cube-sanity-command')),
    check('seal-binds-artifact-lineage-and-rejects-stale-revision', proof.proof?.allSealedArtifactsLineageBound === true && proof.proof?.staleOrWrongRevisionEvidenceRejected === true && ['support-bundle-proof-artifact','support-bundle-audit-artifact','support-bundle-import-artifact','readiness-gate-artifact','browser-kernel-kit-artifact','browser-session-coordination-artifact','browser-recovery-artifact'].every((id) => lineageBoundIds.has(id)) && proof.lineageNegativeCheck?.rejected === true),
    check('seal-probe-hashes-bounded-artifact-files', missing(sealProbe, ['readPackageEvidenceFile','safeArtifactPath','sha256','sealedArtifactRows','browserKernelKitArtifactSealed','browserSessionCoordinationArtifactSealed','browserRecoveryArtifactSealed','browserRecoveryArtifactSatisfied','unsettledOrphanReviewGateObserved','browser-session-coordination-artifact','browser-recovery-artifact','releaseManifestVerifierExpected','EXPECTED_EVIDENCE_LINEAGE','evidenceLineageRows','lineageMutationNegativeCheck']).length === 0),
    check('verify-release-cross-checks-seal-against-manifest', missing(verifyRelease, ['KERNEL-KIT-SUPPORT-BUNDLE-PACKAGE-EVIDENCE-SEAL-PROBE','sealedArtifactRows','manifest_index','package evidence seal','releaseManifestVerifierExpected','allSealedArtifactsLineageBound','staleOrWrongRevisionEvidenceRejected','evidenceLineageRows','lineageNegativeCheck']).length === 0),
    check('package-release-runs-and-retains-seal', missing(packageRelease, ['kernel_kit_support_bundle_package_evidence_seal_probe.mjs','kernel_kit_support_bundle_package_evidence_seal_contract_audit.mjs','KERNEL-KIT-SUPPORT-BUNDLE-PACKAGE-EVIDENCE-SEAL-PROBE','KERNEL-KIT-SUPPORT-BUNDLE-PACKAGE-EVIDENCE-SEAL-CONTRACT-AUDIT']).length === 0),
    check('manifest-tasks-present', taskIds.has('demo:kernel-kit-support-bundle-package-evidence-seal-proof') && taskIds.has('facility:kernel-kit-support-bundle-package-evidence-seal-audit')),
    check('test-kernel-kit-runs-seal-proof-and-audit', testKernelKit.includes('demo:kernel-kit-support-bundle-package-evidence-seal-proof') && testKernelKit.includes('facility:kernel-kit-support-bundle-package-evidence-seal-audit')),
    check('impact-and-inventory-cover-seal', impactIds.has('demo:kernel-kit-support-bundle-package-evidence-seal-proof') && impactIds.has('facility:kernel-kit-support-bundle-package-evidence-seal-audit') && inventoryIds.has('demo:kernel-kit-support-bundle-package-evidence-seal-proof') && inventoryIds.has('facility:kernel-kit-support-bundle-package-evidence-seal-audit')),
    check('non-claims-preserved', ['No artifact authenticity or signature claim.','No command execution claim.','No browser launch claim.'].every((claim) => proof.nonClaims?.includes(claim)))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-support-bundle-package-evidence-seal-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit that Kernel Kit support-bundle evidence artifacts are hash-sealed, lineage-bound to current revision/task identities, and cross-checked by verify_release.py against the final release manifest without claiming authenticity or executing commands.',
    proofId: proof.probe_id,
    checks,
    nonClaims: proof.nonClaims || []
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

// Static audit markers: facility:kernel-kit-support-bundle-package-evidence-seal-audit; demo:kernel-kit-support-bundle-package-evidence-seal-proof; releaseManifestVerifierExpected; package evidence seal; allSealedArtifactsLineageBound; staleOrWrongRevisionEvidenceRejected; EXPECTED_EVIDENCE_LINEAGE; browser-session-coordination-artifact; browser-recovery-artifact; browserSessionCoordinationArtifactSatisfied; browserRecoveryArtifactSatisfied; unsettledOrphanReviewGateObserved; No command execution claim.
