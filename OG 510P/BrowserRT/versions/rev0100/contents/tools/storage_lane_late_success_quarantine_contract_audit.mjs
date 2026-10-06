#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
const TASK_ID = 'facility:storage-lane-late-success-quarantine-contract-audit';
const RELEASE_TASK = 'scheduler:storage-lane-late-success-quarantine-proof';
const BROWSER_TASK = 'browser:opfs-web-lock-late-success-quarantine-proof';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-LATE-SUCCESS-QUARANTINE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function missing(haystack, needles) { return needles.filter((needle) => !haystack.includes(needle)); }
function check(rows, id, ok, detail = {}) { rows.push({ id, ok: Boolean(ok), status: ok ? 'passed' : 'failed', ...detail }); }
export async function runAudit() {
  const started = performance.now();
  const files = Object.fromEntries(await Promise.all(['src/storage-lane-scheduler.mjs','src/block-store-lane-adapter.mjs','src/types.d.ts','tools/storage_lane_late_success_quarantine_probe.mjs','tools/browser_opfs_web_lock_late_success_quarantine_probe.mjs','tools/storage_lane_late_success_quarantine_contract_audit.mjs','docs/40-validation/storage-lane-late-success-quarantine-slice.md','docs/40-validation/browser-opfs-web-lock-late-success-quarantine-slice.md','docs/40-validation/storage-lane-late-success-quarantine-contract-audit-slice.md','test/manifest.json','test/impact-map.json','test/surface-inventory.json','package.json','Makefile','README.md','START_HERE.md','AGENTS.md','CONTEXT-PACK.md'].map(async (path) => [path, await text(path)])));
  const manifest = JSON.parse(files['test/manifest.json']); const impact = JSON.parse(files['test/impact-map.json']); const inventory = JSON.parse(files['test/surface-inventory.json']); const pkg = JSON.parse(files['package.json']);
  const taskById = new Map((manifest.tasks || []).map((task) => [task.id, task])); const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || [])); const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id)); const checks = [];
  check(checks, 'runtime-tracks-late-success', missing(files['src/storage-lane-scheduler.mjs'], ['successfulTimedOutOperations','clearSuccessfulTimedOutOperations','late-provider-success','lateProviderSettlementSuccesses','late-success-clear-review-required','late-success-clear-scope-required']).length === 0);
  check(checks, 'adapter-blocks-late-success-recovery', missing(files['src/block-store-lane-adapter.mjs'], ['timed-out-operation-late-success','recover-timed-out-successes-blocked','clearSuccessfulTimedOutOperations']).length === 0);
  check(checks, 'types-surface-current', missing(files['src/types.d.ts'], [`REVISION: '${REVISION}'`, `VERSION: '${VERSION}'`, 'clearSuccessfulTimedOutOperations', 'timed-out-operation-late-success']).length === 0);
  check(checks, 'release-proof-present', taskById.has(RELEASE_TASK) && taskById.get(RELEASE_TASK).tiers.includes('release'));
  check(checks, 'browser-proof-explicit', taskById.has(BROWSER_TASK) && taskById.get(BROWSER_TASK).tiers.includes('browser') && !taskById.get(BROWSER_TASK).tiers.includes('release'));
  check(checks, 'audit-task-present', taskById.has(TASK_ID) && taskById.get(TASK_ID).tiers.includes('release') && taskById.get(TASK_ID).tiers.includes('audit'));
  check(checks, 'proofs-check-scoped-clear', missing(files['tools/storage_lane_late_success_quarantine_probe.mjs'], ['unreviewedClearRejected','unscopedClearRejected','late-success-clear-review-required','late-success-clear-scope-required','late provider success must not retroactively publish success']).length === 0 && missing(files['tools/browser_opfs_web_lock_late_success_quarantine_probe.mjs'], ['browser:opfs-web-lock-late-success-quarantine-proof','clearSuccessfulTimedOutOperations','timeoutVerifyAfterLateSuccess']).length === 0);
  check(checks, 'impact-wired', [RELEASE_TASK, BROWSER_TASK, TASK_ID].every((id) => impactTaskIds.has(id)));
  check(checks, 'surface-inventory-wired', ['surface:storage-lane-late-success-quarantine','surface:browser-opfs-web-lock-late-success-quarantine','surface:storage-lane-late-success-quarantine-contract-audit'].every((id) => surfaceIds.has(id)));
  check(checks, 'scripts-present', files['package.json'].includes('test:storage-lane:late-success-quarantine') && files['package.json'].includes('test:browser:opfs-web-lock-late-success-quarantine') && files['package.json'].includes('audit:storage-lane-late-success-quarantine'), { note: 'historical sidecar package scripts remain; top-level Makefile is reserved for current office and replay shortcuts' });
  check(checks, 'current-office-aligned-or-carried-forward', (pkg.current_task === BROWSER_TASK && pkg.current_audit === TASK_ID) || ((pkg.carried_forward_browser_proofs || []).includes(BROWSER_TASK) && (pkg.carried_forward_audits || []).includes(TASK_ID)) || pkg.current_task === 'browser:opfs-web-lock-quarantine-ledger-roundtrip-proof', { current_task: pkg.current_task, current_audit: pkg.current_audit, carried_forward_browser_proofs: pkg.carried_forward_browser_proofs || [], carried_forward_audits: pkg.carried_forward_audits || [] });
  const failed = checks.filter((row) => !row.ok);
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-late-success-quarantine-contract-audit`, task_id: TASK_ID, status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Audit that late provider success after operation timeout is quarantined, scoped clear is required, and release/browser proofs are wired.', checks, nonClaims: ['Contract audit does not launch a browser.', 'No cancellation, rollback, exactly-once, cross-browser, durability, quota, eviction, persistent-retention, or production-readiness claim.'] };
  assert.equal(report.status, 'passed', JSON.stringify(failed, null, 2)); return report;
}
const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runAudit(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_late_success_quarantine_contract_audit] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
