#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-support-bundle-diff-proof. Release-tier proof for support-bundle diff/handoff drift reader.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitSupportBundleDiff,
  validateKernelKitSupportBundleDiff,
  KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-SUPPORT-BUNDLE-DIFF-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function clone(value) { return JSON.parse(JSON.stringify(value)); }

export async function runProbe() {
  const source = await runSupportBundleProbe();
  const bundle = source.supportBundle;
  const same = createKernelKitSupportBundleDiff(bundle, JSON.stringify(bundle), { revision: REVISION, generatedAt: 'deterministic-same-bundle-diff' });
  const sameValidation = validateKernelKitSupportBundleDiff(same);

  const degraded = clone(bundle);
  degraded.revision = 'rev0001';
  degraded.nonClaims = degraded.nonClaims.filter((claim) => claim !== 'No automated failure triage claim.');
  degraded.exactCommands = degraded.exactCommands.filter((cmd) => !String(cmd).includes('browser:kernel-kit-demo-proof'));
  degraded.proof.traceComparisonPresent = false;
  const degradedDiff = createKernelKitSupportBundleDiff(bundle, degraded, { revision: REVISION, generatedAt: 'deterministic-degraded-bundle-diff' });

  assert.equal(same.format, KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT);
  assert.equal(sameValidation.ok, true, sameValidation.errors.join('; '));
  assert.equal(same.status, 'unchanged');
  assert.equal(same.proof.currentValid, true);
  assert.equal(same.proof.candidateValid, true);
  assert.equal(same.proof.nonClaimsCompared, true);
  assert.equal(same.proof.exactCommandsCompared, true);
  assert.equal(same.riskFlags.length, 0);
  assert.equal(degradedDiff.status, 'regression-risk');
  assert.ok(degradedDiff.riskFlags.includes('revision-skew'));
  assert.ok(degradedDiff.riskFlags.includes('candidate-validation-failed'));
  assert.ok(degradedDiff.riskFlags.includes('candidate-missing-non-claims'));
  assert.ok(degradedDiff.riskFlags.includes('candidate-missing-commands'));
  assert.ok(degradedDiff.riskFlags.includes('candidate-proof-regression'));
  assert.equal(degradedDiff.proof.boundedReader, true);

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-support-bundle-diff-probe`,
    status: 'passed',
    sourceProbeId: source.probe_id,
    format: KERNEL_KIT_SUPPORT_BUNDLE_DIFF_FORMAT,
    same,
    sameValidation,
    degradedDiff,
    proof: {
      sameBundleDiffValid: sameValidation.ok,
      sameBundleUnchanged: same.status === 'unchanged',
      degradedRevisionSkewVisible: degradedDiff.riskFlags.includes('revision-skew'),
      degradedNonClaimDriftVisible: degradedDiff.riskFlags.includes('candidate-missing-non-claims'),
      degradedCommandDriftVisible: degradedDiff.riskFlags.includes('candidate-missing-commands'),
      degradedProofRegressionVisible: degradedDiff.riskFlags.includes('candidate-proof-regression'),
      boundedReader: same.proof.boundedReader === true && degradedDiff.proof.boundedReader === true,
      exactCommandsPresent: same.exactCommands.some((cmd) => cmd.includes('demo:kernel-kit-support-bundle-diff-proof')),
      nonClaimsVisible: same.nonClaims.includes('No production support-bundle diff claim.') && same.nonClaims.includes('No support-bundle authenticity or signature claim.')
    },
    nonClaims: same.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: demo:kernel-kit-support-bundle-diff-proof; browserrt-kernel-kit-support-bundle-diff-v1; No production support-bundle diff claim.; No automated regression detection claim.
