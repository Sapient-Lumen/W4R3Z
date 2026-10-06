#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-operation-timeout-contract-audit';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-OPERATION-TIMEOUT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function missing(haystack, needles) { return needles.filter((needle) => !haystack.includes(needle)); }

export async function runAudit() {
  const started = performance.now();
  const files = Object.fromEntries(await Promise.all([
    'src/storage-lane-scheduler.mjs',
    'src/block-store-lane-adapter.mjs',
    'src/types.d.ts',
    'tools/storage_lane_operation_timeout_probe.mjs',
    'tools/browser_opfs_web_lock_operation_timeout_probe.mjs',
    'docs/40-validation/storage-lane-operation-timeout-slice.md',
    'docs/40-validation/browser-opfs-web-lock-operation-timeout-boundary-slice.md',
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

  const checks = [
    { id: 'runtime-executor-timeout-hooks', ok: missing(files['src/storage-lane-scheduler.mjs'], ['defaultOperationTimeoutMs', 'operationTimeoutMs', 'BRT_STORAGE_OPERATION_TIMEOUT', 'storage-lane:operation-timeout', 'cancellation: false']).length === 0 },
    { id: 'adapter-timeout-pass-through', ok: missing(files['src/block-store-lane-adapter.mjs'], ['defaultOperationTimeoutMs', 'operationTimeoutMs', 'schedulePut']).length === 0 },
    { id: 'types-timeout-surface', ok: missing(files['src/types.d.ts'], ['operationTimeoutMs', `revision: '${REVISION}'`, `version: '${VERSION}'`]).length === 0 },
    { id: 'release-proof-present', ok: tasks.has('scheduler:storage-lane-operation-timeout-proof') && tasks.get('scheduler:storage-lane-operation-timeout-proof').tiers.includes('release') },
    { id: 'browser-proof-explicit', ok: tasks.has('browser:opfs-web-lock-operation-timeout-boundary-proof') && tasks.get('browser:opfs-web-lock-operation-timeout-boundary-proof').tiers.includes('browser') && !tasks.get('browser:opfs-web-lock-operation-timeout-boundary-proof').tiers.includes('release') },
    { id: 'impact-map-wired', ok: impactTaskIds.has('scheduler:storage-lane-operation-timeout-proof') && impactTaskIds.has('browser:opfs-web-lock-operation-timeout-boundary-proof') && impactTaskIds.has(TASK_ID) },
    { id: 'surface-inventory-wired', ok: surfaceIds.has('surface:storage-lane-operation-timeout') && surfaceIds.has('surface:browser-opfs-web-lock-operation-timeout-boundary') && surfaceIds.has('surface:storage-lane-operation-timeout-contract-audit') },
    { id: 'docs-state-non-cancellation', ok: missing(files['docs/40-validation/browser-opfs-web-lock-operation-timeout-boundary-slice.md'], ['not a cancellation proof', 'No cross-browser', 'BRT_STORAGE_OPERATION_TIMEOUT']).length === 0 && missing(files['docs/40-validation/storage-lane-operation-timeout-slice.md'], ['not provider cancellation', 'BRT_STORAGE_OPERATION_TIMEOUT']).length === 0 },
    { id: 'scripts-present', ok: files['package.json'].includes('test:storage-lane:operation-timeout') && files['package.json'].includes('test:browser:opfs-web-lock-operation-timeout') && files['package.json'].includes('audit:storage-lane-operation-timeout') && files['Makefile'].includes('test-storage-lane-operation-timeout') && files['Makefile'].includes('test-browser-opfs-web-lock-operation-timeout') }
  ].map((row) => ({ ...row, status: row.ok ? 'passed' : 'failed' }));
  const failed = checks.filter((row) => !row.ok);
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    audit_id: `${REVISION}-storage-lane-operation-timeout-contract-audit`,
    task_id: TASK_ID,
    status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Audit that rev0067 operation-timeout runtime hooks, release/browser proofs, docs, manifest, impact map, surface inventory, and convenience scripts are wired and preserve the non-cancellation boundary.',
    checks,
    nonClaims: [
      'Contract audit does not run a browser or prove OPFS/Web Locks behavior.',
      'Operation timeout remains a bounded scheduler-observation/backpressure boundary, not cancellation, rollback, no-mutation, exactly-once, or production readiness.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-operation-timeout-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[storage_lane_operation_timeout_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
