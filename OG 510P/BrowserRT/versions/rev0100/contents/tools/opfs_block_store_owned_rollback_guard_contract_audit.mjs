#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD-CONTRACT-AUDIT.json`;
const RELEASE_TASK = 'opfs:block-store-owned-rollback-guard-proof';
const BROWSER_TASK = 'browser:opfs-block-store-owned-rollback-guard-proof';
const AUDIT_TASK = 'facility:opfs-block-store-owned-rollback-guard-contract-audit';
const SURFACE_IDS = [
  'surface:opfs-block-store-owned-rollback-guard',
  'surface:browser-opfs-block-store-owned-rollback-guard',
  'surface:opfs-block-store-owned-rollback-guard-contract-audit'
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
    releaseProof: await text('tools/opfs_block_store_owned_rollback_guard_probe.mjs'),
    browserProof: await text('tools/browser_opfs_block_store_owned_rollback_guard_probe.mjs'),
    releaseDoc: await text('docs/40-validation/opfs-block-store-owned-rollback-guard-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-block-store-owned-rollback-guard-slice.md'),
    auditDoc: await text('docs/40-validation/opfs-block-store-owned-rollback-guard-contract-audit-slice.md'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile'),
    checkCube: await text('tools/check_cube.py'),
    currentOfficeAudit: await text('tools/current_office_audit.mjs')
  };
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];
  checks.push(includeAll('runtime:owned-rollback-guard', files.runtime, [
    'rollbackOwnsFinalBlock', 'rollbackOwnershipSkips', 'storage:opfs-block-put-rollback-skipped',
    'pre-existing-duplicate-block-not-owned-by-put', 'final-block-not-created-by-put', 'Rev0097 makes failed-put rollback ownership-aware'
  ]));
  checks.push(includeAll('browserrt:boot-proof-flag', files.browserrt, ['opfsOwnedRollbackGuardProof', 'createOpfsAsyncBlockStore']));
  checks.push(includeAll('types:owned-rollback-anchor', files.types, ['rev0097: OpfsAsyncBlockStore failed-put rollback is ownership-aware', `export const REVISION: '${REVISION}'`, `export const VERSION: '${VERSION}'`]));
  checks.push(includeAll('fake-harness:shared-opfs-harness', files.fakeHarness, ['withFakeNavigator', 'FakeDirectoryHandle', 'fakeTreeSummary', 'hooks']));
  checks.push(includeAll('release-proof:owned-rollback-cases', files.releaseProof, [RELEASE_TASK, 'duplicate-put-trace-failure-must-not-delete-existing-block', 'duplicate-put-abort-during-inspection-must-not-delete-existing-block', 'owned-write-failure-still-rolls-back-created-final-block', 'rollbackOwnershipSkips', 'storage:opfs-block-put-rollback-skipped']));
  checks.push(includeAll('browser-proof:real-opfs-duplicate-case', files.browserProof, [BROWSER_TASK, 'browser-duplicate-put-trace-failure-must-not-delete-existing-block', 'bytesPreserved', 'opfsWebLockGuardedBlockStore', 'locksAfterGuarded', 'rollbackOwnershipSkips']));
  checks.push(includeAll('docs:nonclaim-boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, ['ownership-aware rollback', 'duplicate', 'pre-existing valid block', 'cross-browser', 'fsync', 'crash', 'eviction', 'atomic multi-tab']));

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
  checks.push({ label: 'manifest:current-owned-rollback-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0097-opfs-block-store-owned-rollback-guard' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0097 owned rollback guard slice');
  checks.push({ label: 'impact-map:rev0097-owned-rollback-guard', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0097-owned-rollback-guard', status: 'passed' });
  checks.push(includeAll('package:carried-forward-scripts', files.packageJson, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, 'test:opfs-block-store-owned-rollback-guard', 'test:browser:opfs-block-store-owned-rollback-guard', 'audit:opfs-block-store-owned-rollback-guard']));
  checks.push(includeAll('makefile:current-office-carried-forward-to-rollback-preserve', files.makefile, ['opfs-block-store-rollback-valid-block-preserve-current-proof']));
  checks.push(includeAll('check-cube:carried-forward-needles', files.checkCube, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]));
  checks.push(includeAll('current-office:audit-current-boundary', files.currentOfficeAudit, ['OPFS Block Store Rollback Valid Block Preserve', 'owned-rollback']));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Carried-forward contract audit for the OPFS block-store owned rollback guard slice: runtime rollback ownership guard, release/browser proofs, docs, manifest/impact/inventory rows, and current-office boundary after rev0100 moved current routing.',
    checks,
    nonClaims: [
      'Audit only; runtime and managed browser probes supply behavior evidence.',
      'This does not claim cross-browser conformance, atomic multi-tab writes, fsync durability, crash safety, quota/eviction survival, adversarial tamper resistance, or production readiness.'
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
  console.error(`[opfs_block_store_owned_rollback_guard_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
// current-office:audit-needles carried-forward anchor for deep_cube_audit.mjs
