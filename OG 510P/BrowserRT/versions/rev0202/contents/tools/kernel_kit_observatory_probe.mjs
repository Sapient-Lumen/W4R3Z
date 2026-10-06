#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-observatory-proof.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitDemoObservatoryReport,
  validateKernelKitDemoObservatoryReport
} from '../src/browserrt.mjs';
import { runProbe as runKernelKitDemoProbe } from './kernel_kit_demo_probe.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const outPath = argValue('--json', `artifacts/validation/${PFX}-KERNEL-KIT-OBSERVATORY-PROBE.json`);

export async function runProbe() {
  const demo = await runKernelKitDemoProbe();
  const observatory = createKernelKitDemoObservatoryReport(demo, {
    revision: REVISION,
    source: 'release-tier-kernel-kit-demo-probe',
    generatedAt: new Date().toISOString()
  });
  const validation = validateKernelKitDemoObservatoryReport(observatory);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.ok(observatory.stageCards.length >= 8, 'stage cards should cover the whole demo path');
  assert.ok(observatory.traceSummary.uniqueKindCount >= 8, 'trace summary should expose multiple trace kinds');
  assert.ok(observatory.capabilityBadges.some((badge) => badge.id === 'webgpu-performance' && badge.status === 'not-claimed'));
  assert.ok(observatory.nextDemoWork.some((item) => item.includes('human click')));
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    proof_id: `${REVISION}-kernel-kit-observatory-proof`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'Release-tier proof that the Kernel Kit demo can produce a human-legible observatory receipt: capability badges, stage cards, lane timeline, trace summary, proof receipt, next-demo work, and non-claims.',
    demoProofId: demo.proofId,
    validation,
    observatory,
    nonClaims: observatory.nonClaims
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const report = await runProbe();
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
  console.log(outPath);
}
