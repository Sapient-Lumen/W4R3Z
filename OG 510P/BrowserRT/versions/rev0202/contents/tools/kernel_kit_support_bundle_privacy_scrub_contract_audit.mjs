#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-support-bundle-privacy-scrub-audit. Contract audit for support-bundle privacy scrub surfaces.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  validateKernelKitSupportBundlePrivacyScrub
} from '../src/browserrt.mjs';
import { runProbe as runPrivacyScrubProbe } from './kernel_kit_support_bundle_privacy_scrub_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-PRIVACY-SCRUB-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runPrivacyScrubProbe();
  const validation = validateKernelKitSupportBundlePrivacyScrub(proof.scrub);
  const source = await text('src/kernel-kit-demo.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const page = await text('demo/kernel-kit-demo.html');
  const browserProbe = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const supportProbe = await text('tools/kernel_kit_support_bundle_probe.mjs');
  const privacyProbe = await text('tools/kernel_kit_support_bundle_privacy_scrub_probe.mjs');
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const packageRelease = await text('tools/package_release.py');
  const docs = [
    'docs/40-validation/kernel-kit-support-bundle-privacy-scrub-slice.md',
    'docs/40-validation/kernel-kit-support-bundle-privacy-scrub-contract-audit-slice.md'
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set(manifest.tasks.map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || surface.manifestTasks || []));
  const requiredTaskIds = ['demo:kernel-kit-support-bundle-privacy-scrub-proof','facility:kernel-kit-support-bundle-privacy-scrub-audit'];
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true && proof.proof?.rawSensitiveTokensAbsent === true, { validation }),
    check('source-implements-privacy-scrub', includesAll(source, ['KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT', 'createKernelKitSupportBundlePrivacyScrub', 'validateKernelKitSupportBundlePrivacyScrub', 'privacy-scrub-checkpoint', 'privacyScrubPresent', 'sensitiveFieldsRedacted', 'exactCommandTextRedacted', 'No production support-bundle privacy claim.', 'No anonymization, differential-privacy, or irreversible de-identification claim.']).length === 0),
    check('runtime-imports-exports-privacy-scrub', includesAll(runtime, ['createKernelKitSupportBundlePrivacyScrub', 'validateKernelKitSupportBundlePrivacyScrub', 'kernelKitSupportBundlePrivacyScrub', 'validateKernelKitSupportBundlePrivacyScrub', 'kernel-kit-demo:support-bundle-privacy-scrub']).length === 0),
    check('types-declare-privacy-scrub', includesAll(types, ['KernelKitSupportBundlePrivacyScrub', 'createKernelKitSupportBundlePrivacyScrub', 'validateKernelKitSupportBundlePrivacyScrub', 'kernelKitSupportBundlePrivacyScrub', 'KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB_FORMAT']).length === 0),
    check('page-runner-exposes-privacy-scrub', includesAll(runner, ['buildKernelKitSupportBundlePrivacyScrub', 'renderKernelKitSupportBundlePrivacyScrub', 'scrubSupportBundle', 'buildSupportBundlePrivacyScrub', 'window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE_PRIVACY_SCRUB', 'kernel-kit-support-privacy-output']).length === 0),
    check('html-exposes-privacy-scrub-control', includesAll(page, ['scrub-kernel-kit-support-bundle', 'kernel-kit-support-privacy-output', 'browserrt-kernel-kit-support-bundle-privacy-scrub-v1']).length === 0),
    check('browser-probe-drives-privacy-scrub', includesAll(browserProbe, ['exprForSupportBundlePrivacyScrub', 'supportBundlePrivacyScrub', 'validateKernelKitSupportBundlePrivacyScrub', 'sensitiveFieldsRedacted', 'exactCommandTextRedacted']).length === 0),
    check('release-probe-requires-embedded-scrub', includesAll(supportProbe, ['validateKernelKitSupportBundlePrivacyScrub', 'privacyScrubPresent', 'privacyScrubRedactedFields']).length === 0),
    check('privacy-probe-contract-present', includesAll(privacyProbe, ['demo:kernel-kit-support-bundle-privacy-scrub-proof', 'rawSensitiveTokensAbsent', 'commandDigestsOnly', 'No production support-bundle privacy claim.']).length === 0),
    check('manifest-tasks-present', requiredTaskIds.every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-privacy-scrub', requiredTaskIds.every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('package-retains-privacy-artifacts', includesAll(packageRelease, ['KERNEL-KIT-SUPPORT-BUNDLE-PRIVACY-SCRUB-PROBE.json', 'KERNEL-KIT-SUPPORT-BUNDLE-PRIVACY-SCRUB-CONTRACT-AUDIT.json']).length === 0),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && includesAll(body, ['privacy scrub', 'No production support-bundle privacy claim.', 'No anonymization', 'not side-channel']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) }),
    check('non-claims-preserved', proof.nonClaims.includes('No production support-bundle privacy claim.') && proof.nonClaims.includes('No side-channel, fingerprinting, or telemetry-ingestion mitigation claim.'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-support-bundle-privacy-scrub-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Contract audit that Kernel Kit support bundles expose an executable privacy scrub path for handoff summaries without converting it into an anonymization, side-channel, authenticity, or production privacy claim.',
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

// Static audit markers: facility:kernel-kit-support-bundle-privacy-scrub-audit; demo:kernel-kit-support-bundle-privacy-scrub-proof; browserrt-kernel-kit-support-bundle-privacy-scrub-v1; privacyScrubPresent; rawSensitiveTokensAbsent; No production support-bundle privacy claim.; No anonymization, differential-privacy, or irreversible de-identification claim.
