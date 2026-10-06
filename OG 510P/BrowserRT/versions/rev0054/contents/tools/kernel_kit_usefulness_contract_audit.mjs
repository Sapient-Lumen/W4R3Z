#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitDemoUsefulnessReport,
  validateKernelKitDemoUsefulnessReport,
  KERNEL_KIT_USEFULNESS_NON_CLAIMS
} from '../src/browserrt.mjs';

const prefix = `REV${REVISION.slice(3)}`;
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const outPath = argValue('--json', `artifacts/audit/${prefix}-KERNEL-KIT-USEFULNESS-CONTRACT-AUDIT.json`);
async function text(path) { return await readFile(path, 'utf8'); }
function hasAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(id, ok, detail = {}) { return { id, status: ok ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const sample = createKernelKitDemoUsefulnessReport({
    project: 'BrowserRT',
    revision: REVISION,
    proof: { booted: true, workerPing: true, transferDetached: true, boundedChannel: true, admissionAccepted: true, admissionRejectedNoMutation: true, storageWrite: true, reloadReadback: true, traceComplete: true },
    traceKinds: ['runtime:boot','channel:create','channel:receive','agent:spawn','agent:ready','agent:call','agent:result','object:transfer-ref','admission:admit','admission:reject','admission:release','object:opfs-storage-lane-adapter-ref','block-store-lane:schedule','storage-lane:dispatch','block-store-lane:op-complete','storage:opfs-block-put','storage:opfs-block-get','runtime:close'],
    nonClaims: KERNEL_KIT_USEFULNESS_NON_CLAIMS.slice()
  }, { source: 'contract-audit-sample' });
  const validation = validateKernelKitDemoUsefulnessReport(sample);
  const files = {
    source: await text('src/kernel-kit-demo-usefulness.mjs'),
    runtime: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    page: await text('demo/kernel-kit-demo-runner.mjs'),
    html: await text('demo/kernel-kit-demo.html'),
    probe: await text('tools/kernel_kit_usefulness_probe.mjs'),
    manifest: await text('test/manifest.json'),
    impact: await text('test/impact-map.json'),
    inventory: await text('test/surface-inventory.json'),
    readme: await text('README.md'),
    context: await text('CONTEXT-PACK.md'),
    charter: await text('docs/00-meta/non-claims-and-goals-charter.md')
  };
  const docsNeedles = ['Kernel Kit usefulness scorecard','demo:kernel-kit-usefulness-proof','facility:kernel-kit-usefulness-audit','No user research claim.','No product-market-fit claim.'];
  const checks = [
    check('sample-usefulness-validates', validation.ok, { validation }),
    check('source-has-usefulness-contract', hasAll(files.source, ['createKernelKitDemoUsefulnessReport','validateKernelKitDemoUsefulnessReport','beneficiary-fit','workflow-scorecard','No user research claim.']).length === 0),
    check('runtime-exports-usefulness', hasAll(files.runtime, ['createKernelKitDemoUsefulnessReport','validateKernelKitDemoUsefulnessReport','kernelKitDemoUsefulnessReport','kernel-kit-demo-usefulness:validate']).length === 0),
    check('types-export-usefulness', hasAll(files.types, ['KernelKitDemoUsefulnessReport','createKernelKitDemoUsefulnessReport','validateKernelKitDemoUsefulnessReport']).length === 0),
    check('page-renders-usefulness', hasAll(files.page, ['Usefulness scorecard','Who benefits most','data-usefulness-status','data-workflow-status']).length === 0),
    check('html-names-usefulness', hasAll(files.html, ['Usefulness scorecard','Who benefits most','Kernel Kit Demo Observatory']).length === 0),
    check('probe-writes-usefulness-artifact', hasAll(files.probe, ['KERNEL-KIT-USEFULNESS-PROBE','demo:kernel-kit-usefulness-proof','market validation']).length === 0),
    check('manifest-has-usefulness-proof', files.manifest.includes('demo:kernel-kit-usefulness-proof') && files.manifest.includes('facility:kernel-kit-usefulness-audit')),
    check('impact-covers-usefulness', files.impact.includes('demo:kernel-kit-usefulness-proof') && files.impact.includes('facility:kernel-kit-usefulness-audit')),
    check('inventory-covers-usefulness', files.inventory.includes('demo:kernel-kit-usefulness-proof') && files.inventory.includes('facility:kernel-kit-usefulness-audit')),
    check('handoff-docs-cover-usefulness', ['readme','context','charter'].every((key) => hasAll(files[key], docsNeedles).length === 0)),
    check('nonclaims-preserved', KERNEL_KIT_USEFULNESS_NON_CLAIMS.includes('No user research claim.') && KERNEL_KIT_USEFULNESS_NON_CLAIMS.includes('No claim that this demo is the final product shape.'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-usefulness-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Release-tier audit that the Kernel Kit usefulness scorecard is wired across source/export/type/page/probe/docs/manifest/impact/inventory/non-claims without launching Chromium.',
    checks,
    nonClaims: [
      'This audit does not launch Chromium and does not prove the browser demo; run browser:kernel-kit-demo-proof explicitly.',
      ...KERNEL_KIT_USEFULNESS_NON_CLAIMS
    ]
  };
}

const report = await runAudit();
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
assert.equal(report.status, 'passed', report.checks.filter((row) => row.status !== 'passed').map((row) => row.id).join('; '));
