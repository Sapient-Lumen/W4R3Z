#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-readiness-gate-audit. Contract audit for the Kernel Kit readiness gate.
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitReadinessGate } from '../src/browserrt.mjs';
import { runProbe as runReadinessGateProbe } from './kernel_kit_readiness_gate_probe.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-KERNEL-KIT-READINESS-GATE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readTextWithRevisionFallback(path); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(id, ok, details = {}) { return { id, ok: ok === true, ...details }; }

export async function runAudit() {
  const proof = await runReadinessGateProbe();
  const validation = validateKernelKitReadinessGate(proof.readinessGate);
  const [source, runtime, types, runner, html, browserProbe, packageRelease, manifest, impactMap, inventory, docsFrontier, docsSlice, receipt, context, nonClaims] = await Promise.all([
    text('src/kernel-kit-readiness-gate.mjs'),
    text('src/browserrt.mjs'),
    text('src/types.d.ts'),
    text('demo/kernel-kit-demo-runner.mjs'),
    text('demo/kernel-kit-demo.html'),
    text('tools/browser_kernel_kit_demo_probe.mjs'),
    text('tools/package_release.py'),
    text('test/manifest.json'),
    text('test/impact-map.json'),
    text('test/surface-inventory.json'),
    text('docs/20-architecture/kernel-kit-readiness-gate-frontier.md'),
    text('docs/40-validation/kernel-kit-readiness-gate-slice.md'),
    text('REVISION-RECEIPT.json'),
    text('CONTEXT-PACK.md'),
    text('docs/00-meta/non-claims-and-goals-charter.md')
  ]);
  const checks = [
    check('proof-validates', validation.ok, { errors: validation.errors }),
    check('source-exports-readiness-gate', missing(source, ['KERNEL_KIT_READINESS_GATE_FORMAT','createKernelKitReadinessGate','validateKernelKitReadinessGate','No production readiness-gate claim.']).length === 0),
    check('source-requires-evidence-bound-inputs', missing(source, ['readiness-inputs-evidence-bound','createKernelKitReadinessInputProof','inputProof.evidenceBound','derived-from-success-reload-failure-reports']).length === 0),
    check('runtime-exports-readiness-gate', missing(runtime, ['createKernelKitReadinessGate','validateKernelKitReadinessGate','kernelKitReadinessGate','KERNEL_KIT_READINESS_GATE_FORMAT']).length === 0),
    check('types-export-readiness-gate', missing(types, ['KernelKitReadinessGate','createKernelKitReadinessGate','validateKernelKitReadinessGate']).length === 0),
    check('page-exposes-readiness-api', missing(runner, ['buildKernelKitReadinessGate','renderKernelKitReadinessGate','BrowserRTKernelKitDemo.buildReadinessGate','window.__BROWSERRT_KERNEL_KIT_READINESS_GATE']).length === 0),
    check('page-readiness-uses-real-reports-not-placeholder-proof', missing(runner, ['successReport','reloadReport','failureReport','createKernelKitReadinessGate']).length === 0 && !runner.includes('storageWrite: true, reloadReadback: true, controlledFailureMode: true')), 
    check('html-has-readiness-controls', missing(html, ['Build readiness gate','kernel-kit-readiness-output','No production readiness-gate claim.']).length === 0),
    check('browser-proof-drives-readiness', missing(browserProbe, ['exprForReadinessGate','validateKernelKitReadinessGate','readinessGate']).length === 0),
    check('browser-proof-enforces-evidence-bound-readiness', missing(browserProbe, ['readinessInputsEvidenceBound','inputProof?.evidenceBound','derived-from-success-reload-failure-reports']).length === 0),
    check('manifest-has-proof-and-audit', missing(manifest, ['demo:kernel-kit-readiness-gate-proof','facility:kernel-kit-readiness-gate-audit']).length === 0),
    check('probe-removes-readiness-placeholder-proof', !(await text('tools/kernel_kit_readiness_gate_probe.mjs')).includes('storageWrite: true, reloadReadback: true, controlledFailureMode: true')), 
    check('package-retains-readiness-evidence', missing(packageRelease, ['KERNEL-KIT-READINESS-GATE-CONTRACT-AUDIT','KERNEL-KIT-READINESS-GATE-PROBE','KERNEL-KIT-READINESS-EVIDENCE-BOUND-RUN']).length === 0),
    check('impact-map-covers-readiness', missing(impactMap, ['demo:kernel-kit-readiness-gate-proof','facility:kernel-kit-readiness-gate-audit']).length === 0),
    check('surface-inventory-covers-readiness', missing(inventory, ['surface:kernel-kit-readiness-gate','demo:kernel-kit-readiness-gate-proof','facility:kernel-kit-readiness-gate-audit']).length === 0),
    check('docs-frontier-explains-readiness', missing(docsFrontier, ['readiness gate','personas','No production readiness-gate claim.']).length === 0),
    check('docs-slice-explains-proof', missing(docsSlice, ['demo:kernel-kit-readiness-gate-proof','facility:kernel-kit-readiness-gate-audit','browser:kernel-kit-demo-proof']).length === 0),
    check('receipt-preserves-readiness-gate-nonclaim', missing(receipt, ['No production readiness-gate claim.']).length === 0),
    check('context-preserves-browser-light-nonclaims', missing(context, ['Current non-claims','No production runtime claim.','browser-light']).length === 0),
    check('non-claims-charter-updated', missing(nonClaims, ['No production readiness-gate claim.']).length === 0 && (nonClaims.includes('No automated demo-go/no-go claim.') || nonClaims.includes('No automated demo/go-no-go claim.')))
  ];
  const ok = checks.every((row) => row.ok);
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-readiness-gate-contract-audit`,
    status: ok ? 'passed' : 'failed',
    proofProbeId: proof.probe_id,
    validation,
    checks,
    proof: {
      readinessGateValid: validation.ok,
      pageApiWired: checks.find((row) => row.id === 'page-exposes-readiness-api')?.ok === true,
      evidenceBoundInputs: checks.find((row) => row.id === 'source-requires-evidence-bound-inputs')?.ok === true && checks.find((row) => row.id === 'page-readiness-uses-real-reports-not-placeholder-proof')?.ok === true,
      browserProofDrivesApi: checks.find((row) => row.id === 'browser-proof-drives-readiness')?.ok === true,
      docsNonClaimsWired: checks.find((row) => row.id === 'non-claims-charter-updated')?.ok === true
    },
    nonClaims: ['No production readiness-gate claim.', 'No automated demo-go/no-go claim.', 'No product-market-fit claim.']
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;

// Static audit markers: facility:kernel-kit-readiness-gate-audit; browserrt-kernel-kit-readiness-gate-v1; readiness-inputs-evidence-bound; inputProof.evidenceBound; No production readiness-gate claim.
