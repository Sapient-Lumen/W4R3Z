#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-multi-failure-quarantine-contract-audit';
const RELEASE_TASK = 'scheduler:storage-lane-multi-failure-quarantine-proof';
const BROWSER_TASK = 'browser:opfs-web-lock-multi-failure-quarantine-proof';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-MULTI-FAILURE-QUARANTINE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function readText(path) { return await readFile(path, 'utf8'); }
function missing(text, needles) { return needles.filter((needle) => !String(text || '').includes(needle)); }
function check(checks, id, ok, detail = {}) { checks.push(Object.freeze({ id, status: ok ? 'passed' : 'failed', ...detail })); }

export async function runAudit() {
  const started = performance.now();
  const files = {};
  for (const path of ['src/storage-lane-scheduler.mjs','src/block-store-lane-adapter.mjs','src/types.d.ts','tools/storage_lane_multi_failure_quarantine_probe.mjs','tools/browser_opfs_web_lock_multi_failure_quarantine_probe.mjs','docs/40-validation/storage-lane-multi-failure-quarantine-slice.md','docs/40-validation/browser-opfs-web-lock-multi-failure-quarantine-slice.md','docs/40-validation/storage-lane-multi-failure-quarantine-contract-audit-slice.md','package.json','Makefile','test/manifest.json','test/impact-map.json','test/surface-inventory.json','CHANGELOG.md']) files[path] = await readText(path);
  const packageJson = JSON.parse(files['package.json']);
  const manifest = JSON.parse(files['test/manifest.json']);
  const impact = JSON.parse(files['test/impact-map.json']);
  const inventory = JSON.parse(files['test/surface-inventory.json']);
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
  const browserTask = (manifest.tasks || []).find((task) => task.id === BROWSER_TASK);
  const releaseTask = (manifest.tasks || []).find((task) => task.id === RELEASE_TASK);
  const auditTask = (manifest.tasks || []).find((task) => task.id === TASK_ID);
  const checks = [];
  const carriedForwardOrCurrent = packageJson.revision === REVISION && packageJson.version === VERSION && (
    (packageJson.current_task === BROWSER_TASK && packageJson.current_audit === TASK_ID && packageJson.package_slug === 'opfs-web-lock-multi-failure-quarantine-proof') ||
    ((packageJson.carried_forward_browser_proofs || []).includes(BROWSER_TASK) && (packageJson.carried_forward_audits || []).includes(TASK_ID))
  );
  check(checks, 'package-current-or-carried-multi-failure-quarantine', carriedForwardOrCurrent, { observed: { revision: packageJson.revision, version: packageJson.version, current_task: packageJson.current_task, current_audit: packageJson.current_audit, package_slug: packageJson.package_slug, carried_forward_browser_proofs: packageJson.carried_forward_browser_proofs || [], carried_forward_audits: packageJson.carried_forward_audits || [] } });
  check(checks, 'executor-requires-reviewed-scoped-clear', missing(files['src/storage-lane-scheduler.mjs'], ['storage-lane:late-provider-failure-clear-rejected','late-failure-clear-review-required','late-failure-clear-scope-required','reviewedLateProviderFailures','allowLaneWide']).length === 0);
  check(checks, 'adapter-forwards-review-options', missing(files['src/block-store-lane-adapter.mjs'], ['reviewed: options.reviewed === true','reviewToken','allowLaneWide']).length === 0);
  check(checks, 'types-declare-review-options', missing(files['src/types.d.ts'], ['reviewed?: boolean','reviewToken?: string | null','allowLaneWide?: boolean']).length === 0);
  check(checks, 'release-proof-checks-multi-failure', missing(files['tools/storage_lane_multi_failure_quarantine_probe.mjs'], [RELEASE_TASK,'late-failure-clear-review-required','late-failure-clear-scope-required','both failed timed-out operations']).length === 0);
  check(checks, 'browser-proof-checks-real-opfs-multi-failure', missing(files['tools/browser_opfs_web_lock_multi_failure_quarantine_probe.mjs'], [BROWSER_TASK,'providerCommittedBeforeRelease','timedOutVerifiesAfterLateFailures','BRT_OPFS_OPERATION_FAILED','remainingAfterRejectedClears']).length === 0);
  check(checks, 'docs-preserve-nonclaims', missing(files['docs/40-validation/browser-opfs-web-lock-multi-failure-quarantine-slice.md'], ['Managed Chromium','not prove cross-browser','not provider-interruption','exactly-once']).length === 0 && missing(files['docs/40-validation/storage-lane-multi-failure-quarantine-slice.md'], ['late-failure-clear-review-required','late-failure-clear-scope-required','not cancellation']).length === 0);
  check(checks, 'manifest-tasks-present', taskIds.has(RELEASE_TASK) && taskIds.has(BROWSER_TASK) && taskIds.has(TASK_ID));
  check(checks, 'browser-task-explicit-only', browserTask && browserTask.tiers?.includes('browser') && !browserTask.tiers?.includes('release') && browserTask.lane === 'browser' && browserTask.parallelGroup === 'browser-process');
  check(checks, 'release-and-audit-task-release-tier', releaseTask?.tiers?.includes('release') && auditTask?.tiers?.includes('release'));
  check(checks, 'impact-map-wired', [RELEASE_TASK, BROWSER_TASK, TASK_ID].every((id) => impactTaskIds.has(id)), { missing: [RELEASE_TASK, BROWSER_TASK, TASK_ID].filter((id) => !impactTaskIds.has(id)) });
  check(checks, 'surface-inventory-wired', ['surface:storage-lane-multi-failure-quarantine','surface:browser-opfs-web-lock-multi-failure-quarantine','surface:storage-lane-multi-failure-quarantine-contract-audit'].every((id) => surfaceIds.has(id)));
  check(checks, 'scripts-present', files['package.json'].includes('test:storage-lane:multi-failure-quarantine') && files['package.json'].includes('test:browser:opfs-web-lock-multi-failure-quarantine') && files['package.json'].includes('audit:storage-lane-multi-failure-quarantine'), { note: 'historical sidecar package scripts remain; top-level Makefile is reserved for current office and replay shortcuts' });
  check(checks, 'changelog-current-or-carried-anchor', files['CHANGELOG.md'].startsWith(`## ${REVISION} —`) && missing(files['CHANGELOG.md'], ['Historical quarantine/recovery anchors', 'late-failure-clear-review-required', 'late-failure-clear-scope-required']).length === 0, { note: 'carried-forward audit anchor may live below the current revision head; exact task ids live in slice docs, manifest, impact map, and surface inventory' });
  const failed = checks.filter((row) => row.status !== 'passed');
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-multi-failure-quarantine-contract-audit`, task_id: TASK_ID, status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Contract audit for carried-forward multi-failure late-provider quarantine review/scope hardening across runtime, docs, manifest, impact map, and browser-explicit proof surfaces.', checks, nonClaims: ['Audit does not launch Chromium; the browser task remains explicit.', 'Review/scope checks do not prove provider cancellation, rollback, production authorization, or cross-browser behavior.'] };
}
const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runAudit(); assert.equal(report.status, 'passed', report.checks.filter((row) => row.status !== 'passed').map((row) => `${row.id}: ${JSON.stringify(row)}`).join('\n')); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-multi-failure-quarantine-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_multi_failure_quarantine_contract_audit] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
