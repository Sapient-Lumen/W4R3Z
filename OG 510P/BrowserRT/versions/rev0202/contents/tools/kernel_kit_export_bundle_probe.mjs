#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-export-bundle-proof. Release-tier proof for copy/export bundle shape.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS,
  KERNEL_KIT_DEMO_NON_CLAIMS,
  createKernelKitDemoTranscript,
  validateKernelKitDemoTranscript,
  createKernelKitTraceExport,
  validateKernelKitTraceExport,
  createKernelKitDemoExportBundle,
  validateKernelKitDemoExportBundle
} from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-KERNEL-KIT-EXPORT-BUNDLE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function fakeKernelKitReport() {
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    status: 'passed',
    codename: 'Interactive Kernel Kit Demo',
    proof: {
      booted: true,
      workerAgent: true,
      workerPing: true,
      transferDetached: true,
      boundedChannel: true,
      admissionAccepted: true,
      admissionRejectedNoMutation: true,
      storageWrite: true,
      storageLaneWriteRead: true,
      reloadReadback: true,
      traceComplete: true,
      traceEvidence: true,
      cleanupDelete: true
    },
    traceKinds: KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS.slice(),
    normalizedTrace: KERNEL_KIT_DEMO_REQUIRED_TRACE_KINDS.map((kind, index) => ({ kind, seq: index + 1, lane: kind.split(':')[0] })),
    nonClaims: KERNEL_KIT_DEMO_NON_CLAIMS.slice()
  };
}

export async function runProbe() {
  const source = fakeKernelKitReport();
  const transcript = createKernelKitDemoTranscript(source);
  const transcriptValidation = validateKernelKitDemoTranscript(transcript);
  assert.equal(transcriptValidation.ok, true, transcriptValidation.errors.join('; '));
  const traceExport = createKernelKitTraceExport({ ...source, transcript }, { revision: REVISION, source: 'kernel-kit-export-bundle-probe', generatedAt: 'deterministic-export-bundle-probe' });
  const traceValidation = validateKernelKitTraceExport(traceExport);
  assert.equal(traceValidation.ok, true, traceValidation.errors.join('; '));
  const bundle = createKernelKitDemoExportBundle({ ...source, transcript, traceExport }, { revision: REVISION, source: 'kernel-kit-export-bundle-probe', generatedAt: 'deterministic-export-bundle-probe' });
  const bundleValidation = validateKernelKitDemoExportBundle(bundle);
  assert.equal(bundleValidation.ok, true, bundleValidation.errors.join('; '));
  const jsonText = JSON.stringify(bundle, null, 2);
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-export-bundle-probe`,
    status: 'passed',
    bundle,
    transcriptValidation,
    traceValidation,
    bundleValidation,
    proof: {
      bundleFormat: bundle.format,
      bundleBytes: new TextEncoder().encode(jsonText).byteLength,
      transcriptPassed: transcript.status === 'passed',
      traceExportValid: traceValidation.ok,
      bundleValid: bundleValidation.ok,
      browserRtReceiptPresent: Boolean(bundle.traceExport?.browserRtReceipt),
      nonClaimsPresent: bundle.nonClaims.length >= KERNEL_KIT_DEMO_NON_CLAIMS.length
    },
    nonClaims: [
      'No browser download UX claim.',
      'No production observability claim.',
      'No OpenTelemetry compatibility claim.',
      'No Chrome DevTools trace-format compatibility claim.',
      'No Perfetto compatibility claim.'
    ]
  };
  assert.equal(report.proof.bundleValid, true);
  return report;
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit marker: browserrt-kernel-kit-export-bundle-v1
