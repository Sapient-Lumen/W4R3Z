#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-WEB-LOCK-READ-TIMEOUT-NONPOISON-CONTRACT-AUDIT.json`;
const TASK_ID = 'facility:web-lock-read-timeout-nonpoison-contract-audit';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missingNeedles(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const started = performance.now();
  const [runtime, releaseProbe, browserProbe, browserDoc, auditDoc, manifest, impact, inventory, packageJson, makefile, readme, startHere, agents, context] = await Promise.all([
    text('src/storage-lane-scheduler.mjs'),
    text('tools/storage_lane_web_lock_read_timeout_nonpoison_probe.mjs'),
    text('tools/browser_opfs_web_lock_read_timeout_nonpoison_probe.mjs'),
    text('docs/40-validation/browser-opfs-web-lock-read-timeout-nonpoison-slice.md'),
    text('docs/40-validation/web-lock-read-timeout-nonpoison-contract-audit-slice.md'),
    json('test/manifest.json'),
    json('test/impact-map.json'),
    json('test/surface-inventory.json'),
    json('package.json'),
    text('Makefile'),
    text('README.md'),
    text('START_HERE.md'),
    text('AGENTS.md'),
    text('CONTEXT-PACK.md')
  ]);
  const taskById = new Map((manifest.tasks || []).map((task) => [task.id, task]));
  const releaseTask = taskById.get('scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof');
  const browserTask = taskById.get('browser:opfs-web-lock-read-timeout-nonpoison-proof');
  const auditTask = taskById.get(TASK_ID);
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
  const firstReadCombined = [readme, startHere, agents, context].join('\n');

  const checks = [
    check('runtime-read-only-timeout-policy-present', missingNeedles(runtime, ['READ_ONLY_WEB_LOCK_OPS', 'isReadOnlyWebLockTimeout', 'BRT_WEB_LOCK_TIMEOUT']).length === 0, { missing: missingNeedles(runtime, ['READ_ONLY_WEB_LOCK_OPS', 'isReadOnlyWebLockTimeout', 'BRT_WEB_LOCK_TIMEOUT']) }),
    check('release-probe-contract-present', missingNeedles(releaseProbe, ['scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof', 'read-only Web Lock timeout', 'laneHealthFailures', 'storage-lane:provider-unhealthy']).length === 0, { missing: missingNeedles(releaseProbe, ['scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof', 'read-only Web Lock timeout', 'laneHealthFailures', 'storage-lane:provider-unhealthy']) }),
    check('browser-probe-contract-present', missingNeedles(browserProbe, ['browser:opfs-web-lock-read-timeout-nonpoison-proof', 'Service Worker', 'BRT_WEB_LOCK_TIMEOUT', 'laneHealthFailures', 'finalLocks']).length === 0, { missing: missingNeedles(browserProbe, ['browser:opfs-web-lock-read-timeout-nonpoison-proof', 'Service Worker', 'BRT_WEB_LOCK_TIMEOUT', 'laneHealthFailures', 'finalLocks']) }),
    check('docs-present-with-nonclaims', missingNeedles(browserDoc + auditDoc, ['cross-browser', 'quota', 'eviction', 'production-readiness', 'read-timeout nonpoison']).length === 0, { missing: missingNeedles(browserDoc + auditDoc, ['cross-browser', 'quota', 'eviction', 'production-readiness', 'read-timeout nonpoison']) }),
    check('manifest-release-and-browser-tasks-present', Boolean(releaseTask && browserTask && auditTask), { releaseTask: releaseTask?.id || null, browserTask: browserTask?.id || null, auditTask: auditTask?.id || null }),
    check('release-task-is-browser-light', Boolean(releaseTask?.tiers?.includes('release') && releaseTask?.lane !== 'browser'), { releaseTask }),
    check('browser-task-explicit-not-release', Boolean(browserTask?.tiers?.includes('browser') && !browserTask?.tiers?.includes('release') && browserTask?.lane === 'browser'), { browserTask }),
    check('audit-task-release-visible', Boolean((auditTask?.tiers?.includes('release') || auditTask?.tiers?.includes('audit')) && auditTask?.tiers?.includes('audit')), { auditTask }),
    check('impact-map-covers-new-tasks', ['scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof', 'browser:opfs-web-lock-read-timeout-nonpoison-proof', TASK_ID].every((id) => impactTaskIds.has(id)), { missing: ['scheduler:storage-lane-web-lock-read-timeout-nonpoison-proof', 'browser:opfs-web-lock-read-timeout-nonpoison-proof', TASK_ID].filter((id) => !impactTaskIds.has(id)) }),
    check('surface-inventory-covers-new-surfaces', ['surface:storage-lane-web-lock-read-timeout-nonpoison', 'surface:browser-opfs-web-lock-read-timeout-nonpoison', 'surface:web-lock-read-timeout-nonpoison-contract-audit'].every((id) => surfaceIds.has(id)), { missing: ['surface:storage-lane-web-lock-read-timeout-nonpoison', 'surface:browser-opfs-web-lock-read-timeout-nonpoison', 'surface:web-lock-read-timeout-nonpoison-contract-audit'].filter((id) => !surfaceIds.has(id)) }),
    check('package-read-timeout-nonpoison-carried-forward-or-current', packageJson.revision === REVISION && (packageJson.current_task === 'browser:opfs-web-lock-read-timeout-nonpoison-proof' || packageJson.current_task === 'browser:opfs-web-lock-operation-timeout-boundary-proof' || packageJson.current_task === 'browser:opfs-web-lock-late-settlement-recovery-gate-proof' || packageJson.current_task === 'browser:opfs-web-lock-late-failure-quarantine-proof' || packageJson.current_task === 'browser:opfs-web-lock-quarantine-ledger-persistence-integrity-proof' || packageJson.current_task === 'browser:opfs-web-lock-quarantine-review-binding-proof' || packageJson.current_task === 'browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof' || (packageJson.carried_forward_browser_proofs || []).includes('browser:opfs-web-lock-read-timeout-nonpoison-proof')), { revision: packageJson.revision, current_task: packageJson.current_task, current_audit: packageJson.current_audit }),
    check('operator-shortcuts-present', ['test:storage-lane:web-lock-read-timeout-nonpoison', 'test:browser:opfs-web-lock-read-timeout-nonpoison', 'audit:web-lock-read-timeout-nonpoison'].every((key) => packageJson.scripts?.[key]) && ['test-storage-lane-web-lock-read-timeout-nonpoison', 'test-browser-opfs-web-lock-read-timeout-nonpoison', 'audit-web-lock-read-timeout-nonpoison'].every((needle) => makefile.includes(needle)), { packageScripts: Object.keys(packageJson.scripts || {}).filter((key) => key.includes('read-timeout-nonpoison')) }),
    check('first-read-docs-current', missingNeedles(firstReadCombined, [REVISION, packageJson.codename || 'OPFS Web Lock Quarantine Ledger Roundtrip Proof', 'read-timeout', 'nonpoison']).length === 0, { missing: missingNeedles(firstReadCombined, [REVISION, packageJson.codename || 'OPFS Web Lock Quarantine Ledger Roundtrip Proof', 'read-timeout', 'nonpoison']) })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    audit_id: `${REVISION}-web-lock-read-timeout-nonpoison-contract-audit`, task_id: TASK_ID,
    status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Browser-light cube wiring audit for the carried-forward read-only Web Lock timeout nonpoison boundary.',
    checks,
    nonClaims: [
      'This audit does not prove browser Web Locks, OPFS, or Service Worker runtime behavior; the managed Chromium proof does that explicitly.',
      'No cross-browser, fairness, starvation-freedom, mobile/background, OPFS durability, fsync, quota, eviction, persistent-retention, SLO, or production-readiness claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runAudit();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'passed') process.exitCode = 1;
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-web-lock-read-timeout-nonpoison-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed contract audit is not runtime evidence.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[web_lock_read_timeout_nonpoison_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
