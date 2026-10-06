#!/usr/bin/env node
// trace export proof slice for Kernel Kit demo.
// chrome-trace-json-shaped-v1 export envelope. Static audit marker: chrome-trace-shaped-json.
// Manifest slice: demo:kernel-kit-trace-export-proof.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitTraceExport,
  validateKernelKitTraceExport,
  KERNEL_KIT_DEMO_EXPORT_FORMATS,
  KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS
} from '../src/browserrt.mjs';
import { runProbe as runKernelKitDemoProbe } from './kernel_kit_demo_probe.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const outPath = argValue('--json', `artifacts/validation/${PFX}-KERNEL-KIT-TRACE-EXPORT-PROBE.json`);

export async function runProbe() {
  const demo = await runKernelKitDemoProbe();
  const traceExport = createKernelKitTraceExport(demo, {
    revision: REVISION,
    source: 'release-tier-kernel-kit-demo-probe',
    generatedAt: 'deterministic-trace-export-proof'
  });
  const validation = validateKernelKitTraceExport(traceExport);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  for (const format of KERNEL_KIT_DEMO_EXPORT_FORMATS) assert.ok(traceExport.formats.includes(format), `missing export format ${format}`);
  assert.equal(traceExport.browserRtReceipt.status, 'passed');
  assert.equal(traceExport.browserRtReceipt.requiredTraceComplete, true);
  assert.ok(traceExport.chromeTrace.traceEvents.length >= traceExport.summary.uniqueKindCount);
  assert.ok(traceExport.otelSketch.note.includes('not an OpenTelemetry compatibility claim'));
  for (const claim of KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS) assert.ok(traceExport.nonClaims.includes(claim), `missing export non-claim ${claim}`);
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    proof_id: `${REVISION}-kernel-kit-trace-export-proof`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'Release-tier proof that the Kernel Kit demo can emit a compact BrowserRT receipt plus a Chrome-trace-shaped event envelope without claiming production observability, OpenTelemetry compatibility, or DevTools trace-format compatibility.',
    formats: KERNEL_KIT_DEMO_EXPORT_FORMATS.slice(),
    demoProofId: demo.proofId,
    validation,
    traceExport,
    nonClaims: traceExport.nonClaims
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const report = await runProbe();
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
  console.log(outPath);
}
