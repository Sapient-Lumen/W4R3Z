#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:service-worker-waituntil-late-failure-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-SERVICE-WORKER-WAITUNTIL-LATE-FAILURE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(checks, name, passed, detail = {}) { checks.push({ name, status: passed ? 'passed' : 'failed', ...detail }); }

export async function runAudit() {
  const files = Object.fromEntries(await Promise.all([
    'tools/browserrt_opfs_web_lock_service_worker_holder.mjs',
    'tools/browser_opfs_web_lock_service_worker_waituntil_late_failure_probe.mjs',
    'docs/40-validation/browser-opfs-web-lock-service-worker-waituntil-late-failure-slice.md',
    'docs/40-validation/service-worker-waituntil-late-failure-contract-audit-slice.md',
    'README.md', 'START_HERE.md', 'AGENTS.md', 'CONTEXT-PACK.md', 'package.json'
  ].map(async (p) => [p, await text(p)])));
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
  check(checks, 'worker-has-waituntil-route-and-failure', missing(files['tools/browserrt_opfs_web_lock_service_worker_holder.mjs'], ['handleWaitUntilLateFailureRequest', '/browserrt-sw-waituntil-late-failure', 'event.waitUntil(waitUntil.wait)', 'BRT_SW_WAITUNTIL_LATE_FAILURE', 'service-worker-waituntil-late-failure-holder', 'createBrowserStorageRecoveryGuidance', 'record.recovery']).length === 0);
  check(checks, 'browser-proof-exercises-waituntil-late-failure', missing(files['tools/browser_opfs_web_lock_service_worker_waituntil_late_failure_probe.mjs'], ['browser:opfs-web-lock-service-worker-waituntil-late-failure-proof', 'BRT_WEB_LOCK_TIMEOUT', 'BRT_SW_WAITUNTIL_LATE_FAILURE', 'store-coordination-still-contended', 'opfs-web-lock-waituntil-late-failure', 'event.waitUntil', 'serviceWorkerWaitUntilRecoveryGuidance']).length === 0);
  check(checks, 'docs-preserve-narrow-nonclaims', missing(files['docs/40-validation/browser-opfs-web-lock-service-worker-waituntil-late-failure-slice.md'], ['Managed Chromium only', 'waitUntil', 'BRT_WEB_LOCK_TIMEOUT', 'BRT_SW_WAITUNTIL_LATE_FAILURE', 'not claim cross-browser', 'not claim automatic recovery']).length === 0);
  check(checks, 'audit-doc-wired', missing(files['docs/40-validation/service-worker-waituntil-late-failure-contract-audit-slice.md'], [TASK_ID, 'browser:opfs-web-lock-service-worker-waituntil-late-failure-proof', 'browserrt-sw-waituntil-late-failure']).length === 0);
  check(checks, 'manifest-tasks-present', taskIds.has('browser:opfs-web-lock-service-worker-waituntil-late-failure-proof') && taskIds.has(TASK_ID));
  check(checks, 'impact-map-covers-tasks', impactTaskIds.has('browser:opfs-web-lock-service-worker-waituntil-late-failure-proof') && impactTaskIds.has(TASK_ID));
  check(checks, 'surface-inventory-covers-surfaces', surfaceIds.has('surface:browser-opfs-web-lock-service-worker-waituntil-late-failure') && surfaceIds.has('surface:service-worker-waituntil-late-failure-contract-audit'));
  check(checks, 'first-read-docs-current', ['README.md','START_HERE.md','AGENTS.md','CONTEXT-PACK.md'].every((p) => files[p].includes('browser:opfs-web-lock-service-worker-waituntil-late-failure-proof') && files[p].includes('Service Worker waitUntil')));
  check(checks, 'package-currentness', files['package.json'].includes(REVISION) && files['package.json'].includes('opfs-web-lock-service-worker-waituntil-late-failure-proof'));
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID,
    status: checks.every((row) => row.status === 'passed') ? 'passed' : 'failed',
    generatedAt: new Date().toISOString(),
    purpose: 'Contract audit for the Service Worker waitUntil late-failure browser proof: keep worker route, managed-Chromium proof, docs, manifest, impact map, surface inventory, and first-read currentness aligned without launching Chromium.',
    checks,
    nonClaims: [
      'This audit does not launch a browser or prove Service Worker behavior by itself; it verifies wiring for the explicit browser proof.',
      'This audit does not claim cross-browser behavior, automatic recovery, OPFS durability, quota/eviction survival, or production readiness.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
