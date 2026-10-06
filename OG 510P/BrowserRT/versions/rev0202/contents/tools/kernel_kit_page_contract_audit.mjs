#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';
const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-PAGE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function missing(text, needles) { return needles.filter((needle) => !text.includes(needle)); }
async function text(path) { return await readTextWithRevisionFallback(path); }
export async function runAudit() {
  const html = await text('demo/kernel-kit-demo.html');
  const runner = await text('demo/kernel-kit-demo-runner.mjs');
  const browserProbe = await text('tools/browser_kernel_kit_demo_probe.mjs');
  const source = await text('src/kernel-kit-demo.mjs');
  const manifest = JSON.parse(await text('test/manifest.json'));
  const tasks = new Map(manifest.tasks.map((task) => [task.id, task]));
  const pageTask = tasks.get('facility:kernel-kit-page-contract-audit');
  const checks = [
    check('html-is-human-clickable', missing(html, ['Run Kernel Kit demo', 'run-kernel-kit-demo', 'kernel-kit-output', 'window.BrowserRTKernelKitDemo']).length === 0),
    check('runner-installs-window-api', missing(runner, ['window.BrowserRTKernelKitDemo', 'runWork', 'runReload', 'runnerInfo']).length === 0),
    check('runner-shares-runtime-proof-path', missing(runner, ['rt.spawnAgent', 'rt.transferObject', 'rt.channel', 'rt.admissionController', 'rt.opfsWebLockGuardedStorageLaneAdapterWithPosture']).length === 0),
    check('runner-renders-transcript', missing(runner, ['renderKernelKitDemoReport', 'data-stage-status', 'createKernelKitDemoTranscript', 'validateKernelKitDemoTranscript']).length === 0),
    check('browser-probe-drives-page-api', missing(browserProbe, ['BrowserRTKernelKitDemo.runWork', 'BrowserRTKernelKitDemo.runReload', 'runnerInfo', 'workbench did not become ready']).length === 0),
    check('source-has-transcript-contract', missing(source, ['KERNEL_KIT_DEMO_STAGE_LABELS', 'createKernelKitDemoTranscript', 'validateKernelKitDemoTranscript']).length === 0),
    check('manifest-task-release-non-browser', Boolean(pageTask) && pageTask.tiers.includes('release') && pageTask.lane !== 'browser', { tiers: pageTask?.tiers, lane: pageTask?.lane })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    audit_id: `${REVISION}-kernel-kit-page-contract-audit`, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Release-tier static audit proving the Kernel Kit demo page is human-clickable and CDP-drivable through the same page API; it does not launch Chromium.',
    checks,
    nonClaims: [
      'This page contract audit is static and does not prove browser execution; run browser:kernel-kit-demo-proof explicitly.',
      'Human-clickable page wiring is not UX validation, user demand, product-market fit, production runtime, OPFS durability, performance, or cross-browser evidence.'
    ]
  };
}
const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
assert.equal(report.status, 'passed');
