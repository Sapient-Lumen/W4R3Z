#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-usefulness-proof.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitDemoUsefulnessReport,
  validateKernelKitDemoUsefulnessReport,
  KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS,
  KERNEL_KIT_USEFULNESS_NON_CLAIMS
} from '../src/browserrt.mjs';
import { runProbe as runKernelKitDemoProbe } from './kernel_kit_demo_probe.mjs';

const prefix = `REV${REVISION.slice(3)}`;
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const outPath = argValue('--json', `artifacts/validation/${prefix}-KERNEL-KIT-USEFULNESS-PROBE.json`);

export async function runProbe() {
  const demo = await runKernelKitDemoProbe();
  const usefulness = createKernelKitDemoUsefulnessReport(demo, { source: 'kernel-kit-usefulness-probe', revision: REVISION });
  const validation = validateKernelKitDemoUsefulnessReport(usefulness);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(usefulness.status, 'usefulness-wedge-earned');
  assert.ok(usefulness.strongBeneficiaries.length >= 3, 'expected at least three strong beneficiary fits');
  assert.ok(usefulness.earnedEvidence.includes('transcript:valid'), 'transcript evidence should be earned');
  for (const section of KERNEL_KIT_USEFULNESS_REQUIRED_SECTIONS) assert.ok(usefulness.sections.includes(section), `missing usefulness section ${section}`);
  for (const claim of ['No user research claim.', 'No product-market-fit claim.', 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    assert.ok(KERNEL_KIT_USEFULNESS_NON_CLAIMS.includes(claim), `missing non-claim constant ${claim}`);
    assert.ok(usefulness.nonClaims.includes(claim), `missing report non-claim ${claim}`);
  }
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-usefulness-probe`,
    status: 'passed',
    purpose: 'Release-tier proof that the Kernel Kit demo has a legible usefulness scorecard: beneficiary fit, workflow evidence, earned/missing evidence, acceptance gate, and non-claim boundaries.',
    sourceProofId: demo.proofId,
    usefulness,
    validation,
    observed: {
      workflowCount: usefulness.workflowScorecard.length,
      earnedWorkflowCount: validation.earnedWorkflowCount,
      strongBeneficiaryCount: validation.strongBeneficiaryCount,
      missingEvidenceCount: usefulness.missingEvidence.length,
      nonClaimCount: usefulness.nonClaims.length
    },
    nonClaims: [
      'This proof does not provide market validation, user research, adoption evidence, pricing evidence, or product-market fit.',
      'This proof does not add production, durability, performance, cross-browser, or mobile lifecycle claims.'
    ]
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const report = await runProbe();
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
  console.log(outPath);
}
