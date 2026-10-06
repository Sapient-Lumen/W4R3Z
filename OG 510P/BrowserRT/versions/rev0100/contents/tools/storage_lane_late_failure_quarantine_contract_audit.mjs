#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-late-failure-quarantine-contract-audit';
const RELEASE_TASK = 'scheduler:storage-lane-late-failure-quarantine-proof';
const BROWSER_TASK = 'browser:opfs-web-lock-late-failure-quarantine-proof';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-LATE-FAILURE-QUARANTINE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function missing(haystack, needles) { return needles.filter((needle) => !haystack.includes(needle)); }
function check(rows, id, ok, detail = {}) { rows.push({ id, ok: Boolean(ok), status: ok ? 'passed' : 'failed', ...detail }); }

export async function runAudit() {
  const started = performance.now();
  const paths = [
    'src/storage-lane-scheduler.mjs',
    'src/block-store-lane-adapter.mjs',
    'src/types.d.ts',
    'tools/storage_lane_late_failure_quarantine_probe.mjs',
    'tools/browser_opfs_web_lock_late_failure_quarantine_probe.mjs',
    'tools/storage_lane_late_failure_quarantine_contract_audit.mjs',
    'docs/40-validation/storage-lane-late-failure-quarantine-slice.md',
    'docs/40-validation/browser-opfs-web-lock-late-failure-quarantine-slice.md',
    'docs/40-validation/storage-lane-late-failure-quarantine-contract-audit-slice.md',
    'test/manifest.json',
    'test/impact-map.json',
    'test/surface-inventory.json',
    'package.json',
    'Makefile'
  ];
  const files = Object.fromEntries(await Promise.all(paths.map(async (path) => [path, await text(path)])));
  const manifest = JSON.parse(files['test/manifest.json']);
  const impact = JSON.parse(files['test/impact-map.json']);
  const inventory = JSON.parse(files['test/surface-inventory.json']);
  const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
  const checks = [];

  check(checks, 'executor-quarantines-late-failures', missing(files['src/storage-lane-scheduler.mjs'], ['failedTimedOutOperations', 'clearFailedTimedOutOperations', 'storage-lane:late-provider-failure', 'storage-lane:late-provider-failures-cleared', 'failedTimedOutOperationCount', 'lateProviderSettlementFailures']).length === 0, { missing: missing(files['src/storage-lane-scheduler.mjs'], ['failedTimedOutOperations', 'clearFailedTimedOutOperations', 'storage-lane:late-provider-failure', 'storage-lane:late-provider-failures-cleared', 'failedTimedOutOperationCount', 'lateProviderSettlementFailures']) });
  check(checks, 'adapter-blocks-recovery-on-late-failure', missing(files['src/block-store-lane-adapter.mjs'], ['requireNoFailedTimedOutOperations', 'timed-out-operation-late-failure', 'block-store-lane:recover-timed-out-failures-blocked', 'clearFailedTimedOutOperations']).length === 0, { missing: missing(files['src/block-store-lane-adapter.mjs'], ['requireNoFailedTimedOutOperations', 'timed-out-operation-late-failure', 'block-store-lane:recover-timed-out-failures-blocked', 'clearFailedTimedOutOperations']) });
  check(checks, 'types-surface', missing(files['src/types.d.ts'], ['failedTimedOutOperations', 'clearFailedTimedOutOperations', 'requireNoFailedTimedOutOperations', `revision: '${REVISION}'`, `version: '${VERSION}'`]).length === 0, { missing: missing(files['src/types.d.ts'], ['failedTimedOutOperations', 'clearFailedTimedOutOperations', 'requireNoFailedTimedOutOperations', `revision: '${REVISION}'`, `version: '${VERSION}'`]) });
  check(checks, 'release-proof-present', tasks.has(RELEASE_TASK) && tasks.get(RELEASE_TASK).tiers.includes('release'));
  check(checks, 'browser-proof-explicit', tasks.has(BROWSER_TASK) && tasks.get(BROWSER_TASK).tiers.includes('browser') && !tasks.get(BROWSER_TASK).tiers.includes('release'));
  check(checks, 'audit-task-present', tasks.has(TASK_ID) && tasks.get(TASK_ID).tiers.includes('release') && tasks.get(TASK_ID).tiers.includes('audit'));
  check(checks, 'release-proof-checks-quarantine', missing(files['tools/storage_lane_late_failure_quarantine_probe.mjs'], ['timed-out-operation-late-failure', 'storage-lane:late-provider-failure', 'clearFailedTimedOutOperations', 'late failure must not publish a successful adapter result']).length === 0);
  check(checks, 'browser-proof-checks-real-opfs-path', missing(files['tools/browser_opfs_web_lock_late_failure_quarantine_probe.mjs'], ['browser:opfs-web-lock-late-failure-quarantine-proof', 'timeoutVerifyAfterLateFailure', 'failedTimedOutOperations', 'coord:web-lock-acquired', 'storage-lane:late-provider-failure']).length === 0);
  check(checks, 'docs-preserve-nonclaims', missing(files['docs/40-validation/browser-opfs-web-lock-late-failure-quarantine-slice.md'], ['Managed Chromium only', 'not prove cross-browser', 'not prove cancellation', 'timed-out-operation-late-failure']).length === 0 && missing(files['docs/40-validation/storage-lane-late-failure-quarantine-slice.md'], ['not cancellation', 'not rollback', 'clearFailedTimedOutOperations']).length === 0);
  check(checks, 'impact-wired', impactTaskIds.has(RELEASE_TASK) && impactTaskIds.has(BROWSER_TASK) && impactTaskIds.has(TASK_ID));
  check(checks, 'surface-inventory-wired', ['surface:storage-lane-late-failure-quarantine', 'surface:browser-opfs-web-lock-late-failure-quarantine', 'surface:storage-lane-late-failure-quarantine-contract-audit'].every((id) => surfaceIds.has(id)));
  check(checks, 'scripts-present', files['package.json'].includes('test:storage-lane:late-failure-quarantine') && files['package.json'].includes('test:browser:opfs-web-lock-late-failure-quarantine') && files['package.json'].includes('audit:storage-lane-late-failure-quarantine'), { note: 'historical sidecar package scripts remain; top-level Makefile is reserved for current office and replay shortcuts' });

  const failed = checks.filter((row) => !row.ok);
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    audit_id: `${REVISION}-storage-lane-late-failure-quarantine-contract-audit`,
    task_id: TASK_ID,
    status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Audit that late provider failure quarantine, recovery gating, explicit maintenance clearing, release/browser proofs, docs, manifest, impact map, surface inventory, and scripts are wired while preserving non-cancellation/non-rollback boundaries.',
    checks,
    nonClaims: [
      'Contract audit does not launch a browser or prove OPFS/Web Locks behavior.',
      'Late-failure quarantine does not prove cancellation, rollback, no-mutation, exactly-once behavior, OPFS durability, cross-browser behavior, or production readiness.'
    ]
  };
  assert.equal(report.status, 'passed', JSON.stringify(failed, null, 2));
  return report;
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runAudit();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-late-failure-quarantine-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_late_failure_quarantine_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
