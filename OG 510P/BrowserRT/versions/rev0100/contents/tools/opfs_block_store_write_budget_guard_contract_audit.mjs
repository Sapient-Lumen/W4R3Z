#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-OPFS-BLOCK-STORE-WRITE-BUDGET-GUARD-CONTRACT-AUDIT.json`;
const RELEASE_TASK = 'opfs:block-store-write-budget-guard-proof';
const BROWSER_TASK = 'browser:opfs-block-store-write-budget-guard-proof';
const AUDIT_TASK = 'facility:opfs-block-store-write-budget-guard-contract-audit';
const SURFACE_IDS = [
  'surface:opfs-block-store-write-budget-guard',
  'surface:browser-opfs-block-store-write-budget-guard',
  'surface:opfs-block-store-write-budget-guard-contract-audit'
];
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function includeAll(label, body, needles) {
  const missing = needles.filter((needle) => !String(body).includes(needle));
  assert.deepEqual(missing, [], `${label} missing ${missing.join(', ')}`);
  return Object.freeze({ label, status: 'passed', needles: needles.length });
}
function manifestTask(manifest, id) {
  const task = (manifest.tasks || []).find((row) => row.id === id);
  assert.ok(task, `manifest missing ${id}`);
  return task;
}
function surface(inventory, id) {
  const row = (inventory.surfaces || []).find((item) => item.id === id);
  assert.ok(row, `surface inventory missing ${id}`);
  return row;
}

export async function runAudit() {
  const started = performance.now();
  const files = {
    runtime: await text('src/opfs-block-store.mjs'),
    browserrt: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    fakeHarness: await text('tools/lib/fake_opfs_harness.mjs'),
    releaseProof: await text('tools/opfs_block_store_write_budget_guard_probe.mjs'),
    browserProof: await text('tools/browser_opfs_block_store_write_budget_guard_probe.mjs'),
    releaseDoc: await text('docs/40-validation/opfs-block-store-write-budget-guard-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-block-store-write-budget-guard-slice.md'),
    auditDoc: await text('docs/40-validation/opfs-block-store-write-budget-guard-contract-audit-slice.md'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile'),
    checkCube: await text('tools/check_cube.py')
  };
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];
  checks.push(includeAll('runtime:write-budget-guard', files.runtime, [
    'normalizeWriteBudgetGuard', 'writeBudgetGuardForPut', 'writeBudgetGuardFromConfig', '#checkWriteBudgetBeforePut',
    'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_ESTIMATE_UNAVAILABLE', 'BRT_OPFS_WRITE_BUDGET_INVALID',
    'storage:opfs-block-write-budget-check', 'storage:opfs-block-write-budget-reject', 'storage:opfs-block-write-budget-estimate-unavailable',
    'writeBudgetChecks', 'writeBudgetRejects', 'writeBudgetEstimateUnavailable'
  ]));
  checks.push(includeAll('browserrt:boot-proof-flag', files.browserrt, ['opfsWriteBudgetGuardProof', 'createOpfsAsyncBlockStore']));
  checks.push(includeAll('types:write-budget-surface', files.types, ['RtOpfsWriteBudgetGuard', 'RtOpfsPutOptions', 'writeBudgetGuard?: boolean | RtOpfsWriteBudgetGuard | null', 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_ESTIMATE_UNAVAILABLE']));
  // fake-opfs-harness:storage-estimate-refactor
  checks.push(includeAll('fake-harness:estimate-injection-refactor', files.fakeHarness, ['estimate !== false', "typeof estimate === 'function'", 'storageExtras']));
  checks.push(includeAll('release-proof:write-budget-cases', files.releaseProof, [RELEASE_TASK, 'reserve-budget-reject-before-open', 'per-put-ratio-budget-reject-before-open', 'required-estimate-unavailable-before-open', 'optional-estimate-unavailable-continues', 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_ESTIMATE_UNAVAILABLE']));
  checks.push(includeAll('browser-proof:real-estimate-cases', files.browserProof, [BROWSER_TASK, 'navigator.storage.estimate', 'raw-write-budget-reject-before-open', 'raw-per-put-write-budget-reject-before-open', 'opfsWebLockGuardedBlockStore', 'storage:opfs-web-lock-guard-op-complete']));
  checks.push(includeAll('docs:nonclaim-boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, ['writeBudgetGuard', 'StorageManager.estimate', 'not a reservation', 'cross-browser', 'quota', 'eviction', 'crash']));

  const releaseTask = manifestTask(manifest, RELEASE_TASK);
  const browserTask = manifestTask(manifest, BROWSER_TASK);
  const auditTask = manifestTask(manifest, AUDIT_TASK);
  for (const task of [releaseTask, browserTask, auditTask]) {
    const joined = JSON.stringify(task);
    assert.ok(joined.includes(PFX), `${task.id} must use current artifact prefix ${PFX}`);
    assert.ok((task.currentTaskIds || []).includes(RELEASE_TASK), `${task.id} currentTaskIds missing release task`);
    assert.ok((task.currentTaskIds || []).includes(BROWSER_TASK), `${task.id} currentTaskIds missing browser task`);
    assert.ok((task.currentTaskIds || []).includes(AUDIT_TASK), `${task.id} currentTaskIds missing audit task`);
  }
  checks.push({ label: 'manifest:current-write-budget-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0096-opfs-block-store-write-budget-guard' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0096 write budget guard slice');
  checks.push({ label: 'impact-map:rev0096-write-budget-guard', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0096-write-budget-guard', status: 'passed' });
  checks.push(includeAll('package:carried-forward-write-budget-scripts', files.packageJson, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, 'test:opfs-block-store-write-budget-guard', 'test:browser:opfs-block-store-write-budget-guard', 'audit:opfs-block-store-write-budget-guard']));
  checks.push(includeAll('check-cube:carried-forward-write-budget-needles', files.checkCube, ['tools/opfs_block_store_write_budget_guard_contract_audit.mjs', RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]));
  checks.push(includeAll('makefile:current-office-carried-forward-to-rollback-preserve', files.makefile, ['opfs-block-store-rollback-valid-block-preserve-current-proof']));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the OPFS block-store writeBudgetGuard slice: runtime guard, TypeScript surface, fake-OPFS estimate injection refactor, release/browser proof wiring, manifest/impact/inventory rows, and carried-forward package/check-cube routing while current-office belongs to the active slice.',
    checks,
    nonClaims: [
      'Audit only; runtime and managed browser probes supply behavior evidence.',
      'This does not claim a true storage reservation, quota/eviction survival, OPFS fsync durability, crash safety, production capacity, or cross-browser conformance.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runAudit();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: AUDIT_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_write_budget_guard_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
