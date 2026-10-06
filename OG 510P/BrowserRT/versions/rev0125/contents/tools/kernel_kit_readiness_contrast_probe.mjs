#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-readiness-contrast-proof. Release-tier proof that the Kernel Kit readiness gate also rejects a weaker/degraded handoff.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitReadinessContrast,
  createDegradedKernelKitReadinessGate,
  validateKernelKitReadinessContrast,
  validateKernelKitReadinessGate,
  KERNEL_KIT_READINESS_CONTRAST_FORMAT
} from '../src/browserrt.mjs';
import { runProbe as runReadinessGateProbe } from './kernel_kit_readiness_gate_probe.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-READINESS-CONTRAST-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const readiness = await runReadinessGateProbe();
  const baselineGate = readiness.readinessGate;
  const degradedGate = createDegradedKernelKitReadinessGate(baselineGate, {
    reason: 'rev0054-negative-readiness-demo',
    failGateIds: ['reload-readback-visible', 'handoff-markdown-importable', 'exact-commands-present'],
    generatedAt: 'deterministic-readiness-contrast-degraded'
  });
  const degradedValidation = validateKernelKitReadinessGate(degradedGate);
  const contrast = createKernelKitReadinessContrast({
    revision: REVISION,
    baselineGate,
    degradedGate,
    expectedFailedGateIds: ['reload-readback-visible', 'handoff-markdown-importable', 'exact-commands-present'],
    generatedAt: 'deterministic-readiness-contrast-probe'
  });
  const validation = validateKernelKitReadinessContrast(contrast);

  assert.equal(contrast.format, KERNEL_KIT_READINESS_CONTRAST_FORMAT);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(contrast.status, 'contrast-ready');
  assert.equal(contrast.proof.baselineReady, true);
  assert.equal(contrast.proof.degradedNeedsAttention, true);
  assert.equal(contrast.proof.degradedRejectedByReadinessValidator, true);
  assert.equal(contrast.proof.expectedGatesFailed, true);
  assert.equal(degradedValidation.ok, false, 'degraded readiness gate must not validate as ready');
  assert.equal(degradedGate.status, 'needs-attention');
  assert.ok(degradedGate.missingGateIds.includes('reload-readback-visible'));
  assert.ok(degradedGate.missingGateIds.includes('handoff-markdown-importable'));
  assert.ok(degradedGate.missingGateIds.includes('exact-commands-present'));
  assert.ok(contrast.gateDiff.some((row) => row.id === 'reload-readback-visible' && row.before === true && row.after === false));
  assert.ok(contrast.exactCommands.some((cmd) => cmd.includes('demo:kernel-kit-readiness-contrast-proof')));
  assert.ok(contrast.nonClaims.includes('No production readiness-contrast claim.'));

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-readiness-contrast-probe`,
    status: 'passed',
    sourceProbeId: readiness.probe_id,
    contrast,
    validation,
    degradedValidation,
    proof: {
      baselineReady: contrast.proof.baselineReady,
      degradedNeedsAttention: contrast.proof.degradedNeedsAttention,
      degradedRejectedByReadinessValidator: contrast.proof.degradedRejectedByReadinessValidator,
      expectedGatesFailed: contrast.proof.expectedGatesFailed,
      changedGateCount: validation.changedGateCount,
      missingGateCount: validation.missingGateCount,
      commandsPresent: contrast.proof.commandsPresent,
      nonClaimsPreserved: contrast.proof.nonClaimsPreserved
    },
    nonClaims: contrast.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: demo:kernel-kit-readiness-contrast-proof; browserrt-kernel-kit-readiness-contrast-v1; No production readiness-contrast claim.
