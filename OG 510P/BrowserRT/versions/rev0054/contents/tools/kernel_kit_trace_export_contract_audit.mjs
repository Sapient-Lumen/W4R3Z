#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-TRACE-EXPORT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

export async function runAudit() {
  const source = await text('src/kernel-kit-demo.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const probe = await text('tools/kernel_kit_trace_export_probe.mjs');
  const html = await text('demo/kernel-kit-demo.html');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const manifest = await json('test/manifest.json');
  const tasks = new Map(manifest.tasks.map((task) => [task.id, task]));
  const proofTask = tasks.get('demo:kernel-kit-trace-export-proof');
  const auditTask = tasks.get('facility:kernel-kit-trace-export-audit');
  const checks = [
    check('source-defines-trace-export', missing(source, ['createKernelKitTraceExport', 'validateKernelKitTraceExport', 'browserrt-kernel-kit-trace-export-v1', 'KERNEL_KIT_DEMO_EXPORT_NON_CLAIMS']).length === 0),
    check('runtime-exports-trace-export', missing(runtime, ['createKernelKitTraceExport', 'validateKernelKitTraceExport', 'kernelKitTraceExport', 'kernel-kit-demo:trace-export']).length === 0),
    check('types-export-trace-export', missing(types, ['KernelKitTraceExport', 'createKernelKitTraceExport', 'validateKernelKitTraceExport', 'KERNEL_KIT_DEMO_EXPORT_FORMATS']).length === 0),
    check('probe-validates-trace-export', missing(probe, ['demo:kernel-kit-trace-export-proof', 'validateKernelKitTraceExport', 'chrome-trace-json-shaped-v1']).length === 0),
    check('page-renders-export-receipt', missing(html + runner, ['Trace/export workbench', 'Trace/export receipt', 'createTraceExport', 'Chrome-trace-shaped']).length === 0),
    check('proof-task-release-tier', Boolean(proofTask) && proofTask.tiers.includes('release') && proofTask.lane !== 'browser', { tiers: proofTask?.tiers, lane: proofTask?.lane }),
    check('audit-task-release-tier', Boolean(auditTask) && auditTask.tiers.includes('release') && auditTask.lane !== 'browser', { tiers: auditTask?.tiers, lane: auditTask?.lane })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    audit_id: `${REVISION}-kernel-kit-trace-export-contract-audit`, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Release-tier static audit for the Kernel Kit trace/export workbench. It checks source/export/type/page/manifest wiring without launching Chromium.',
    checks,
    nonClaims: [
      'No production observability claim.',
      'No OpenTelemetry compatibility claim.',
      'No Chrome DevTools trace-format compatibility claim.',
      'No browser performance claim.',
      'No Perfetto compatibility claim.',
      'No production runtime claim.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
assert.equal(report.status, 'passed');
