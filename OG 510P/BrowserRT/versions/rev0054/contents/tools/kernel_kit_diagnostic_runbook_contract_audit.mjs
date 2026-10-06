#!/usr/bin/env node
// Manifest slice: facility:kernel-kit-diagnostic-runbook-audit. Contract audit for Kernel Kit diagnostic runbook surfaces.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, validateKernelKitDiagnosticRunbook } from '../src/browserrt.mjs';
import { runProbe as runDiagnosticProbe } from './kernel_kit_diagnostic_runbook_probe.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-KERNEL-KIT-DIAGNOSTIC-RUNBOOK-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return readFile(path, 'utf8'); }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const proof = await runDiagnosticProbe();
  const validation = validateKernelKitDiagnosticRunbook(proof.runbook);
  const source = await text('src/kernel-kit-demo.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const page = await text('demo/kernel-kit-demo.html');
  const browserProbe = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const manifest = JSON.parse(await text('test/manifest.json'));
  const impact = JSON.parse(await text('test/impact-map.json'));
  const inventory = JSON.parse(await text('test/surface-inventory.json'));
  const docs = [
    'docs/20-architecture/kernel-kit-diagnostic-runbook-frontier.md',
    'docs/40-validation/kernel-kit-diagnostic-runbook-slice.md',
    `docs/40-validation/kernel-kit-diagnostic-runbook-contract-audit-${REVISION}.md`,
    `docs/50-roadmap/kernel-kit-diagnostic-runbook-roadmap-${REVISION}.md`
  ];
  const docBodies = await Promise.all(docs.map((path) => text(path).then((body) => [path, body]).catch((error) => [path, `__MISSING__ ${error.message}`])));
  const taskIds = new Set(manifest.tasks.map((task) => task.id));
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || surface.manifestTasks || []));
  const checks = [
    check('proof-validates', proof.status === 'passed' && validation.ok === true, { validation }),
    check('source-exports-runbook', includesAll(source, ['createKernelKitDiagnosticRunbook', 'validateKernelKitDiagnosticRunbook', 'browserrt-kernel-kit-diagnostic-runbook-v1', 'No production incident-response claim.']).length === 0),
    check('runtime-imports-exports-runbook', includesAll(runtime, ['createKernelKitDiagnosticRunbook', 'validateKernelKitDiagnosticRunbook', 'kernelKitDiagnosticRunbook', 'KERNEL_KIT_DIAGNOSTIC_RUNBOOK_FORMAT']).length === 0),
    check('types-declare-runbook', includesAll(types, ['KernelKitDiagnosticRunbook', 'createKernelKitDiagnosticRunbook', 'validateKernelKitDiagnosticRunbook', 'kernelKitDiagnosticRunbook']).length === 0),
    check('page-runner-exposes-runbook-api', includesAll(runner, ['diagnoseKernelKitTraceComparison', 'renderKernelKitDiagnosticRunbook', 'diagnoseTraceComparison', 'window.__BROWSERRT_KERNEL_KIT_DIAGNOSTIC_RUNBOOK']).length === 0),
    check('html-exposes-diagnostic-controls', includesAll(page, ['diagnose-kernel-kit-traces', 'kernel-kit-diagnostic-output', 'Kernel Kit diagnostic runbook']).length === 0),
    check('browser-probe-drives-runbook-api', includesAll(browserProbe, ['BrowserRTKernelKitDemo.diagnoseTraceComparison', 'diagnosticRunbook', 'validateKernelKitDiagnosticRunbook']).length === 0),
    check('manifest-tasks-present', ['demo:kernel-kit-diagnostic-runbook-proof','facility:kernel-kit-diagnostic-runbook-audit'].every((id) => taskIds.has(id))),
    check('impact-and-inventory-cover-runbook', ['demo:kernel-kit-diagnostic-runbook-proof','facility:kernel-kit-diagnostic-runbook-audit'].every((id) => impactIds.has(id) && inventoryIds.has(id))),
    check('docs-present-and-nonclaims-visible', docBodies.every(([path, body]) => !body.startsWith('__MISSING__') && includesAll(body, ['diagnostic runbook', 'No root-cause analysis claim.', 'No automated failure recovery claim.', 'browser-light']).length === 0), { docs: docBodies.map(([path, body]) => ({ path, missing: body.startsWith('__MISSING__') })) }),
    check('non-claims-preserved', proof.nonClaims.includes('No production runtime claim.') && proof.nonClaims.includes('No root-cause analysis claim.') && proof.nonClaims.includes('No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-diagnostic-runbook-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Release-tier contract audit for the Kernel Kit diagnostic runbook: source/runtime/types/page/browser probe/manifest/docs/non-claim wiring without launching Chromium.',
    proofId: proof.probe_id,
    checks,
    nonClaims: proof.nonClaims
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(report, null, 2) + '\n');
console.log(out);
if (report.status !== 'passed') process.exitCode = 1;

// Static audit markers: facility:kernel-kit-diagnostic-runbook-audit; diagnoseTraceComparison; No root-cause analysis claim.
