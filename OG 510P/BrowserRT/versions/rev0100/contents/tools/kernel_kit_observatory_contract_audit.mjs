#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  createKernelKitDemoObservatoryReport,
  validateKernelKitDemoObservatoryReport,
  KERNEL_KIT_OBSERVATORY_NON_CLAIMS
} from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const outPath = argValue('--json', `artifacts/audit/${PFX}-KERNEL-KIT-OBSERVATORY-CONTRACT-AUDIT.json`);
const readText = async (path) => await readFile(path, 'utf8');
const readJson = async (path) => JSON.parse(await readText(path));
function hasAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const manifest = await readJson('test/manifest.json');
  const impact = await readJson('test/impact-map.json');
  const inventory = await readJson('test/surface-inventory.json');
  const source = await readText('src/kernel-kit-demo-observatory.mjs');
  const runtime = await readText('src/browserrt.mjs');
  const types = await readText('src/types.d.ts');
  const probe = await readText('tools/kernel_kit_observatory_probe.mjs');
  const html = await readText('demo/kernel-kit-demo.html');
  const docs = await Promise.all([
    'docs/00-meta/kernel-kit-demo-rev0044.md',
    'docs/20-architecture/kernel-kit-demo-observatory-frontier.md',
    'docs/40-validation/kernel-kit-demo-observatory-slice.md',
    'docs/40-validation/kernel-kit-observatory-contract-audit-rev0044.md',
    'docs/50-roadmap/kernel-kit-demo-polish-roadmap-rev0044.md'
  ].map(async (path) => [path, await readText(path)]));
  const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
  const sample = createKernelKitDemoObservatoryReport({
    project: 'BrowserRT',
    revision: REVISION,
    proofId: 'audit-sample',
    status: 'passed',
    proof: { booted: true, workerAgent: true, transferDetached: true, boundedChannel: true, admissionRejectedNoMutation: true, storageWrite: true, reloadReadback: true, traceComplete: true },
    traceKinds: ['runtime:boot','channel:create','channel:send','channel:receive','agent:spawn','agent:ready','agent:call','agent:result','object:transfer-ref','admission:admit','admission:reject','admission:release','object:opfs-storage-lane-adapter-ref','block-store-lane:schedule','storage-lane:dispatch','block-store-lane:op-complete','storage:opfs-block-put','storage:opfs-block-get','runtime:close'],
    nonClaims: ['No production runtime claim.', 'No product-market-fit claim.']
  }, { revision: REVISION, generatedAt: 'audit-sample' });
  const validation = validateKernelKitDemoObservatoryReport(sample);
  const docNeedles = ['Kernel Kit Demo Observatory', 'demo:kernel-kit-observatory-proof', 'facility:kernel-kit-observatory-audit', 'No production observability claim.', 'No browser download UX claim.', 'No failure recovery automation claim.', 'No browser performance claim.', 'No OPFS durability'];
  const docsMissing = docs.flatMap(([path, body]) => hasAll(body, docNeedles).map((needle) => ({ path, needle })));
  const checks = [
    check('sample-observatory-validates', validation.ok, { validation }),
    check('source-has-observatory-contract', hasAll(source, ['createKernelKitDemoObservatoryReport','validateKernelKitDemoObservatoryReport','capability-badges','stage-cards','lane-timeline','proof-receipt']).length === 0),
    check('runtime-exports-observatory', hasAll(runtime, ['createKernelKitDemoObservatoryReport','validateKernelKitDemoObservatoryReport','kernelKitDemoObservatory','kernel-kit-demo-observatory:validate']).length === 0),
    check('types-export-observatory', hasAll(types, ['KernelKitDemoObservatoryReport','createKernelKitDemoObservatoryReport','validateKernelKitDemoObservatoryReport']).length === 0),
    check('probe-produces-observatory', hasAll(probe, ['demo:kernel-kit-observatory-proof','createKernelKitDemoObservatoryReport','validateKernelKitDemoObservatoryReport','webgpu-performance']).length === 0),
    check('html-human-facing-observatory', hasAll(html, ['Kernel Kit Demo Observatory','Expected demo path','Non-claims','Worker agent','OPFS storage lane']).length === 0),
    check('manifest-has-observatory-proof', Boolean(tasks.get('demo:kernel-kit-observatory-proof')) && tasks.get('demo:kernel-kit-observatory-proof')?.tiers?.includes('release')),
    check('manifest-has-observatory-audit', Boolean(tasks.get('facility:kernel-kit-observatory-audit')) && tasks.get('facility:kernel-kit-observatory-audit')?.tiers?.includes('release')),
    check('impact-covers-observatory', impactIds.has('demo:kernel-kit-observatory-proof') && impactIds.has('facility:kernel-kit-observatory-audit')),
    check('inventory-covers-observatory', inventoryIds.has('demo:kernel-kit-observatory-proof') && inventoryIds.has('facility:kernel-kit-observatory-audit')),
    check('docs-cover-observatory-nonclaims', docsMissing.length === 0, { docsMissing }),
    check('observatory-nonclaims-preserved', KERNEL_KIT_OBSERVATORY_NON_CLAIMS.includes('No production observability claim.') && KERNEL_KIT_OBSERVATORY_NON_CLAIMS.includes('No browser download UX claim.') && KERNEL_KIT_OBSERVATORY_NON_CLAIMS.includes('No failure recovery automation claim.') && KERNEL_KIT_OBSERVATORY_NON_CLAIMS.includes('No browser performance claim.'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-observatory-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    generatedAt: new Date().toISOString(),
    purpose: 'Release-tier audit for the Kernel Kit demo observatory: source/export/type/tool/html/docs/manifest/impact/inventory/non-claim coherence without launching Chromium.',
    checks,
    nonClaims: [
      'This audit does not launch Chromium and does not prove the browser demo; run browser:kernel-kit-demo-proof explicitly.',
      ...KERNEL_KIT_OBSERVATORY_NON_CLAIMS
    ]
  };
}

const report = await runAudit();
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
assert.equal(report.status, 'passed');
