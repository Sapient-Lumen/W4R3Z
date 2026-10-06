#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-evidence-ledger-audit. Contract audit for support-bundle expected artifact ledger surfaces.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitSupportBundleEvidenceLedger, validateKernelKitSupportBundleReplayPlan } from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-LEDGER-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runSupportBundleProbe();
  const ledgerValidation = validateKernelKitSupportBundleEvidenceLedger(proof.supportBundle?.evidenceLedger || {});
  const replayValidation = proof.replaySummary?.validation || validateKernelKitSupportBundleReplayPlan(proof.replayPlan || {});
  const replayEvidenceLedgerPresent = proof.proof?.replayPlanReady === true && proof.proof?.evidenceLedgerPresent === true;
  const [source, runtime, types, runner, browserProbe, packageJsonText, packageRelease, manifest, impact, inventory] = await Promise.all([
    text('src/kernel-kit-demo.mjs'),
    text('src/browserrt.mjs'),
    text('src/types.d.ts'),
    text('demo/kernel-kit-demo-runner.mjs'),
    text('tools/browser_kernel_kit_demo_probe.mjs'),
    text('package.json'),
    text('tools/package_release.py'),
    json('test/manifest.json'),
    json('test/impact-map.json'),
    json('test/surface-inventory.json')
  ]);
  const packageJson = JSON.parse(packageJsonText);
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => [...(surface.currentTaskIds || []), ...(surface.manifestTasks || [])]));
  const testKernelKit = String(packageJson.scripts?.['test:kernel-kit'] || '');
  const ledger = proof.supportBundle.evidenceLedger || {};
  const outputNeedles = [
    `${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-PROBE.json`,
    `${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-CONTRACT-AUDIT.json`,
    `${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-IMPORT-PROBE.json`,
    `${PREFIX}-KERNEL-KIT-READINESS-GATE-PROBE.json`,
    `${PREFIX}-BROWSER-KERNEL-KIT-DEMO-PROBE.json`,
    `${PREFIX}-BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE.json`,
    `${PREFIX}-BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE.json`,
    `${PREFIX}-BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE.json`
  ];
  const checks = [
    check('proof-ledger-validates', proof.status === 'passed' && proof.proof?.evidenceLedgerPresent === true && ledgerValidation.ok === true && replayValidation.ok === true && replayEvidenceLedgerPresent === true, { ledgerValidation, replayEvidenceLedgerPresent }),
    check('ledger-names-core-artifact-outputs', outputNeedles.every((needle) => (ledger.outputPaths || []).some((path) => String(path).includes(needle))), { outputCount: ledger.outputPaths?.length || 0 }),
    check('source-exports-evidence-ledger-contract', missing(source, ['createKernelKitSupportBundleEvidenceLedger','validateKernelKitSupportBundleEvidenceLedger','KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT','browserrt-kernel-kit-support-bundle-evidence-ledger-v1','proof.evidenceLedgerPresent','evidenceLedgerPresent']).length === 0),
    check('runtime-exports-evidence-ledger-contract', missing(runtime, ['createKernelKitSupportBundleEvidenceLedger','validateKernelKitSupportBundleEvidenceLedger','kernelKitSupportBundleEvidenceLedger','validateKernelKitSupportBundleEvidenceLedger','KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT']).length === 0),
    check('types-declare-evidence-ledger-contract', missing(types, ['KernelKitSupportBundleEvidenceLedger','createKernelKitSupportBundleEvidenceLedger','validateKernelKitSupportBundleEvidenceLedger','KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER_FORMAT','kernelKitSupportBundleEvidenceLedger']).length === 0),
    check('page-exposes-evidence-ledger', missing(runner, ['buildSupportBundleEvidenceLedger','validateSupportBundleEvidenceLedger','window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_EVIDENCE_LEDGER','Evidence ledger','Evidence ledger outputs']).length === 0),
    check('browser-proof-asserts-ledger', missing(browserProbe, ['validateKernelKitSupportBundleEvidenceLedger','supportBundleEvidenceLedger','evidenceLedgerPresent','BROWSER-KERNEL-KIT-DEMO-PROBE', 'BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE', 'BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE', 'BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE']).length === 0),
    check('manifest-task-present', taskIds.has('facility:kernel-kit-support-bundle-evidence-ledger-audit')),
    check('test-kernel-kit-runs-focused-audit', testKernelKit.includes('facility:kernel-kit-support-bundle-evidence-ledger-audit')),
    check('impact-and-inventory-cover-focused-audit', impactIds.has('facility:kernel-kit-support-bundle-evidence-ledger-audit') && inventoryIds.has('facility:kernel-kit-support-bundle-evidence-ledger-audit')),
    check('package-retains-focused-audit', packageRelease.includes('KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-LEDGER-CONTRACT-AUDIT')),
    check('non-claims-preserved', ['No production evidence-ledger claim.','No artifact authenticity or signature claim.','No command execution claim.','No automated replay execution claim.','No durable artifact retention guarantee.'].every((claim) => ledger.nonClaims?.includes(claim)))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-support-bundle-evidence-ledger-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Audit that the Kernel Kit support-bundle replay path names expected compact proof/audit artifacts and keeps the ledger wired through runtime/types/page/browser/package surfaces without executing commands or claiming artifact authenticity.',
    proofId: proof.probe_id,
    checks,
    nonClaims: ledger.nonClaims || []
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(report, null, 2) + '\n');
console.log(out);
if (report.status !== 'passed') process.exitCode = 1;

// Static audit markers: facility:kernel-kit-support-bundle-evidence-ledger-audit; BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE; browser-storage-pressure-artifact; BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE; browser-session-coordination-artifact; BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE; browser-recovery-artifact; browserrt-kernel-kit-support-bundle-evidence-ledger-v1; buildSupportBundleEvidenceLedger; No artifact authenticity or signature claim.; No durable artifact retention guarantee.
