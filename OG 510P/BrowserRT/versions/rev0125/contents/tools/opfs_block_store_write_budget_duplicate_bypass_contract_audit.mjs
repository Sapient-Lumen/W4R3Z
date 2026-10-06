#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-OPFS-BLOCK-STORE-WRITE-BUDGET-DUPLICATE-BYPASS-CONTRACT-AUDIT.json`;
const RELEASE_TASK = 'opfs:block-store-write-budget-duplicate-bypass-proof';
const BROWSER_TASK = 'browser:opfs-block-store-write-budget-duplicate-bypass-proof';
const AUDIT_TASK = 'facility:opfs-block-store-write-budget-duplicate-bypass-contract-audit';
const PACKAGE_SLUG = 'opfs-block-store-write-budget-duplicate-bypass-current-proof';
const SURFACE_IDS = [
  'surface:opfs-block-store-write-budget-duplicate-bypass',
  'surface:browser-opfs-block-store-write-budget-duplicate-bypass',
  'surface:opfs-block-store-write-budget-duplicate-bypass-contract-audit'
];
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function includeAll(label, body, needles) {
  const missing = needles.filter((needle) => !String(body).includes(needle));
  assert.deepEqual(missing, [], `${label} missing ${missing.join(', ')}`);
  return Object.freeze({ label, status: 'passed', needles: needles.length });
}
function rejectAny(label, body, needles) {
  const hits = needles.filter((needle) => String(body).includes(needle));
  assert.deepEqual(hits, [], `${label} contains stale needles ${hits.join(', ')}`);
  return Object.freeze({ label, status: 'passed', rejectedNeedles: needles.length });
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
function script(pkg, name) {
  const body = pkg.scripts?.[name];
  assert.ok(body, `package.json scripts.${name} missing`);
  return body;
}

export async function runAudit() {
  const started = performance.now();
  const files = {
    runtime: await text('src/opfs-block-store.mjs'),
    browserrt: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    fakeHarness: await text('tools/lib/fake_opfs_harness.mjs'),
    releaseProof: await text('tools/opfs_block_store_write_budget_duplicate_bypass_probe.mjs'),
    browserProof: await text('tools/browser_opfs_block_store_write_budget_duplicate_bypass_probe.mjs'),
    releaseDoc: await text('docs/40-validation/opfs-block-store-write-budget-duplicate-bypass-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-block-store-write-budget-duplicate-bypass-slice.md'),
    auditDoc: await text('docs/40-validation/opfs-block-store-write-budget-duplicate-bypass-contract-audit-slice.md'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile'),
    checkCube: await text('tools/check_cube.py'),
    currentOffice: await text('tools/current_office_audit.mjs')
  };
  const pkg = JSON.parse(files.packageJson);
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];

  checks.push(includeAll('runtime:duplicate-aware-write-budget', files.runtime, [
    '#bypassWriteBudgetForDuplicate', '#openExistingPrefix', '#existingBucket', 'existingOnly',
    'writeBudgetDuplicateBypasses', 'storage:opfs-block-write-budget-duplicate-bypass',
    'verified-duplicate-no-op-put', 'before-open-mutable-bucket', 'corrupt-block-repair-put', 'new-block-put'
  ]));
  checks.push(includeAll('browserrt:boot-proof-flag', files.browserrt, ['opfsWriteBudgetDuplicateBypassProof', 'opfsWriteBudgetGuardProof', 'createOpfsAsyncBlockStore']));
  checks.push(includeAll('types:revision-and-budget-surface', files.types, [`revision: '${REVISION}'`, `version: '${VERSION}'`, 'RtOpfsWriteBudgetGuard', 'writeBudgetGuard?: boolean | RtOpfsWriteBudgetGuard | null']));
  checks.push(includeAll('fake-harness:estimate-recorder-refactor', files.fakeHarness, ['createStorageEstimateRecorder', 'byteCountBeforeEstimate', 'fileCountBeforeEstimate', 'storageExtras']));
  checks.push(includeAll('release-proof:duplicate-budget-cases', files.releaseProof, [
    RELEASE_TASK, 'verified-duplicate-budget-bypass', 'unverified-duplicate-budget-bypass',
    'new-write-budget-reject-after-readonly-dedupe-before-mutation', 'corrupt-repair-budget-reject-preserves-corrupt-file',
    'createStorageEstimateRecorder', 'writeBudgetDuplicateBypasses', 'storage:opfs-block-write-budget-duplicate-bypass'
  ]));
  checks.push(includeAll('browser-proof:patched-estimate-duplicate-cases', files.browserProof, [
    BROWSER_TASK, 'patchedEstimate', 'duplicateEstimateCallsDuringPut', 'browser-duplicate-put-bypasses-impossible-budget',
    'browser-new-write-still-rejects-before-mutation', 'opfsWebLockGuardedBlockStore', 'storage:opfs-web-lock-guard-op-complete'
  ]));
  checks.push(includeAll('docs:boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, ['duplicate', 'writeBudgetGuard', 'StorageManager.estimate', 'quota', 'eviction', 'crash', 'cross-browser', 'not a storage reservation']));

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
  checks.push({ label: 'manifest:current-duplicate-budget-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0099-opfs-block-store-write-budget-duplicate-bypass' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0099 duplicate budget bypass slice');
  checks.push({ label: 'impact-map:rev0099-duplicate-budget-bypass', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0099-duplicate-budget-bypass', status: 'passed' });

  checks.push(includeAll('package:carried-forward-duplicate-budget-scripts', files.packageJson, [RELEASE_TASK, BROWSER_TASK, 'tools/opfs_block_store_write_budget_duplicate_bypass_contract_audit.mjs', 'test:opfs-block-store-write-budget-duplicate-bypass', 'test:browser:opfs-block-store-write-budget-duplicate-bypass', 'audit:opfs-block-store-write-budget-duplicate-bypass']));
  checks.push(includeAll('package:current-office-moved-to-composite-abort-signal', files.packageJson, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof']));
  checks.push(includeAll('makefile:current-office-moved-to-composite-abort-signal', files.makefile, ['opfs-block-store-raw-composite-abort-signal-current-proof', 'opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof']));
  checks.push(includeAll('check-cube:current-office-now-composite-abort-signal', files.checkCube, ['opfs-block-store-raw-composite-abort-signal-current-proof', 'OPFS Raw Composite AbortSignal']));
  checks.push(includeAll('current-office:audit-needles', files.currentOffice, ['OPFS Raw Composite AbortSignal', 'opfs-block-store-raw-composite-abort-signal-current-proof']));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Carried-forward contract audit for the OPFS block-store write-budget duplicate-bypass slice: runtime duplicate-aware guard, TypeScript/runtime surface, fake-OPFS estimate recorder refactor, release/browser proof wiring, manifest/impact/inventory rows, and current-office boundary after rev0100 moved current routing.',
    checks,
    nonClaims: [
      'Audit only; runtime and managed browser probes supply behavior evidence.',
      'This does not claim a storage reservation, quota/eviction survival, OPFS fsync durability, crash safety, production capacity, or cross-browser conformance.'
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
  console.error(`[opfs_block_store_write_budget_duplicate_bypass_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
