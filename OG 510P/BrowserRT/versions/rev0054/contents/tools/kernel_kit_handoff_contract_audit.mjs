#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY } from '../src/browserrt.mjs';
const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-HANDOFF-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

export async function runAudit() {
  const source = await text('src/kernel-kit-demo.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const html = await text('demo/kernel-kit-demo.html');
  const browserProbe = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const manifest = await json('test/manifest.json');
  const tasks = new Map(manifest.tasks.map((task) => [task.id, task]));
  const auditTask = tasks.get('facility:kernel-kit-handoff-contract-audit');
  const checks = [
    check('source-defines-handoff-contract', missing(source, ['KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY', 'createKernelKitDemoHandoff', 'validateKernelKitDemoHandoff', 'local reload handoff']).length === 0),
    check('runtime-exports-handoff-contract', missing(runtime, ['createKernelKitDemoHandoff', 'validateKernelKitDemoHandoff', 'kernelKitDemoHandoff', 'kernel-kit-demo:handoff']).length === 0),
    check('types-export-handoff-contract', missing(types, ['KernelKitDemoHandoff', 'createKernelKitDemoHandoff', 'validateKernelKitDemoHandoff', 'KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY']).length === 0),
    check('runner-uses-localstorage-handoff', missing(runner, ['localStorage', 'loadKernelKitDemoHandoff', 'saveKernelKitDemoHandoff', 'clearKernelKitDemoHandoff', KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY]).length === 0),
    check('html-has-human-handoff-controls', missing(html, ['read-kernel-kit-demo', 'clear-kernel-kit-handoff', 'kernel-kit-handoff-status', 'local reload handoff']).length === 0),
    check('browser-proof-asserts-handoff', missing(browserProbe, ['validateKernelKitDemoHandoff', 'handoffBeforeReload', 'handoffAfterRead', 'reload should use localStorage handoff']).length === 0),
    check('audit-task-release-tier', Boolean(auditTask) && auditTask.tiers.includes('release') && auditTask.lane !== 'browser', { tiers: auditTask?.tiers, lane: auditTask?.lane })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    audit_id: `${REVISION}-kernel-kit-handoff-contract-audit`, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
    storageKey: KERNEL_KIT_DEMO_HANDOFF_STORAGE_KEY,
    purpose: 'Release-tier static audit for the Kernel Kit local reload handoff: human page can save an OPFS ref/digest, reload, read back, and clear the handoff without CDP-only hidden arguments.',
    checks,
    nonClaims: [
      'Local reload handoff is same-profile OPFS readback convenience, not crash recovery, durability, browser-restart, quota, eviction, or multi-tab evidence.',
      'No production runtime claim.',
      'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
      'No cross-browser conformance claim.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
assert.equal(report.status, 'passed');
