#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-late-settlement-contract-audit';
const RELEASE_TASK = 'scheduler:storage-lane-late-settlement-recovery-gate-proof';
const BROWSER_TASK = 'browser:opfs-web-lock-late-settlement-recovery-gate-proof';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-LATE-SETTLEMENT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function missing(haystack, needles) { return needles.filter((needle) => !haystack.includes(needle)); }
function check(rows, id, ok, detail = {}) { rows.push({ id, ok: Boolean(ok), status: ok ? 'passed' : 'failed', ...detail }); }

export async function runAudit() {
  const started = performance.now();
  const files = Object.fromEntries(await Promise.all([
    'src/storage-lane-scheduler.mjs',
    'src/block-store-lane-adapter.mjs',
    'src/types.d.ts',
    'tools/storage_lane_late_settlement_recovery_gate_probe.mjs',
    'tools/browser_opfs_web_lock_late_settlement_recovery_gate_probe.mjs',
    'tools/storage_lane_late_settlement_contract_audit.mjs',
    'docs/40-validation/storage-lane-late-settlement-recovery-gate-slice.md',
    'docs/40-validation/browser-opfs-web-lock-late-settlement-recovery-gate-slice.md',
    'docs/40-validation/storage-lane-late-settlement-contract-audit-slice.md',
    'test/manifest.json',
    'test/impact-map.json',
    'test/surface-inventory.json',
    'package.json',
    'Makefile'
  ].map(async (path) => [path, await text(path)])));
  const manifest = JSON.parse(files['test/manifest.json']);
  const impact = JSON.parse(files['test/impact-map.json']);
  const inventory = JSON.parse(files['test/surface-inventory.json']);
  const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
  const checks = [];

  check(checks, 'executor-tracks-unsettled-timeouts', missing(files['src/storage-lane-scheduler.mjs'], ['unsettledTimedOutOperations', 'waitForTimedOutOperationsSettled', 'storage-lane:operation-timeout-unsettled', 'storage-lane:late-provider-settlement', 'lateProviderSettlements']).length === 0, { missing: missing(files['src/storage-lane-scheduler.mjs'], ['unsettledTimedOutOperations', 'waitForTimedOutOperationsSettled', 'storage-lane:operation-timeout-unsettled', 'storage-lane:late-provider-settlement', 'lateProviderSettlements']) });
  check(checks, 'adapter-gates-settled-recovery', missing(files['src/block-store-lane-adapter.mjs'], ['requireTimedOutOperationsSettled', 'timed-out-operation-still-unsettled', 'block-store-lane:recover-timed-out-ops-blocked', 'block-store-lane:recover-timed-out-ops-settled']).length === 0, { missing: missing(files['src/block-store-lane-adapter.mjs'], ['requireTimedOutOperationsSettled', 'timed-out-operation-still-unsettled', 'block-store-lane:recover-timed-out-ops-blocked', 'block-store-lane:recover-timed-out-ops-settled']) });
  check(checks, 'adapter-no-late-result-publication', missing(files['src/block-store-lane-adapter.mjs'], ['adapterResultAfterLateSettlement', 'block-store-lane:op-complete']).length === 0 || missing(files['tools/storage_lane_late_settlement_recovery_gate_probe.mjs'], ['adapterResultAfterLateSettlement', 'must not retroactively publish']).length === 0, { note: 'Release proof checks that late provider success does not retroactively publish a successful adapter result.' });
  check(checks, 'types-surface', missing(files['src/types.d.ts'], ['unsettledTimedOutOperations', 'waitForTimedOutOperationsSettled', 'requireTimedOutOperationsSettled', `revision: '${REVISION}'`, `version: '${VERSION}'`]).length === 0, { missing: missing(files['src/types.d.ts'], ['unsettledTimedOutOperations', 'waitForTimedOutOperationsSettled', 'requireTimedOutOperationsSettled', `revision: '${REVISION}'`, `version: '${VERSION}'`]) });
  check(checks, 'release-proof-present', tasks.has(RELEASE_TASK) && tasks.get(RELEASE_TASK).tiers.includes('release'));
  check(checks, 'browser-proof-explicit', tasks.has(BROWSER_TASK) && tasks.get(BROWSER_TASK).tiers.includes('browser') && !tasks.get(BROWSER_TASK).tiers.includes('release'));
  check(checks, 'audit-task-present', tasks.has(TASK_ID) && tasks.get(TASK_ID).tiers.includes('release') && tasks.get(TASK_ID).tiers.includes('audit'));
  check(checks, 'proofs-check-late-settlement', missing(files['tools/storage_lane_late_settlement_recovery_gate_probe.mjs'], ['timed-out-operation-still-unsettled', 'storage-lane:late-provider-settlement', 'adapterResultAfterLateSettlement', 'not retroactively publish']).length === 0 && missing(files['tools/browser_opfs_web_lock_late_settlement_recovery_gate_probe.mjs'], ['locksAfterTimeout.heldCount', 'timeoutBlockPresentBeforeRelease', 'adapterResultAfterLateSettlement', 'storage-lane:late-provider-settlement']).length === 0);
  check(checks, 'docs-preserve-nonclaims', missing(files['docs/40-validation/browser-opfs-web-lock-late-settlement-recovery-gate-slice.md'], ['not cancellation', 'not rollback', 'no cross-browser', 'late provider settlement']).length === 0 && missing(files['docs/40-validation/storage-lane-late-settlement-recovery-gate-slice.md'], ['timed-out-operation-still-unsettled', 'not provider cancellation']).length === 0);
  check(checks, 'impact-wired', impactTaskIds.has(RELEASE_TASK) && impactTaskIds.has(BROWSER_TASK) && impactTaskIds.has(TASK_ID));
  check(checks, 'surface-inventory-wired', ['surface:storage-lane-late-settlement-recovery-gate', 'surface:browser-opfs-web-lock-late-settlement-recovery-gate', 'surface:storage-lane-late-settlement-contract-audit'].every((id) => surfaceIds.has(id)));
  check(checks, 'scripts-present', files['package.json'].includes('test:storage-lane:late-settlement') && files['package.json'].includes('test:browser:opfs-web-lock-late-settlement') && files['package.json'].includes('audit:storage-lane-late-settlement') && files['Makefile'].includes('test-storage-lane-late-settlement') && files['Makefile'].includes('test-browser-opfs-web-lock-late-settlement') && files['Makefile'].includes('audit-storage-lane-late-settlement'));

  const failed = checks.filter((row) => !row.ok);
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    audit_id: `${REVISION}-storage-lane-late-settlement-contract-audit`,
    task_id: TASK_ID,
    status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Audit that late provider settlement tracking, recovery gating, release/browser proofs, docs, manifest, impact map, surface inventory, and scripts are wired while preserving the non-cancellation/non-rollback boundary.',
    checks,
    nonClaims: [
      'Contract audit does not launch a browser or prove OPFS/Web Locks behavior.',
      'Late-settlement recovery gating does not prove cancellation, rollback, no-mutation, exactly-once behavior, OPFS durability, cross-browser behavior, or production readiness.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-late-settlement-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_late_settlement_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
