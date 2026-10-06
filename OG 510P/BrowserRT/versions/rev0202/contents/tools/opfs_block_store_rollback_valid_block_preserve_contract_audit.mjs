#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-CONTRACT-AUDIT.json`;
const RELEASE_TASK = 'opfs:block-store-rollback-valid-block-preserve-proof';
const BROWSER_TASK = 'browser:opfs-block-store-rollback-valid-block-preserve-proof';
const AUDIT_TASK = 'facility:opfs-block-store-rollback-valid-block-preserve-contract-audit';
const PACKAGE_SLUG = 'opfs-block-store-rollback-valid-block-preserve-current-proof';
const SURFACE_IDS = [
  'surface:opfs-block-store-rollback-valid-block-preserve',
  'surface:browser-opfs-block-store-rollback-valid-block-preserve',
  'surface:opfs-block-store-rollback-valid-block-preserve-contract-audit'
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
    releaseProof: await text('tools/opfs_block_store_rollback_valid_block_preserve_probe.mjs'),
    browserProof: await text('tools/browser_opfs_block_store_rollback_valid_block_preserve_probe.mjs'),
    releaseDoc: await text('docs/40-validation/opfs-block-store-rollback-valid-block-preserve-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-block-store-rollback-valid-block-preserve-slice.md'),
    auditDoc: await text('docs/40-validation/opfs-block-store-rollback-valid-block-preserve-contract-audit-slice.md'),
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

  checks.push(includeAll('runtime:valid-rollback-preserve', files.runtime, [
    'rollbackValidBlockPreserves', 'rollbackIntegrityChecks', 'rollbackIntegrityCheckFailures',
    'failed-put-rollback-preserve-check', 'valid-final-block-preserved',
    'storage:opfs-block-put-rollback-preserved', 'storage:opfs-block-put-rollback-preserve-check-error',
    'integrity.present && integrity.ok', 'preserved: true'
  ]));
  checks.push(includeAll('browserrt:boot-proof-flag', files.browserrt, ['opfsRollbackValidBlockPreserveProof', 'opfsWriteBudgetDuplicateBypassProof', 'createOpfsAsyncBlockStore']));
  checks.push(includeAll('types:revision-and-rollback-anchor', files.types, [`revision: '${REVISION}'`, `version: '${VERSION}'`, 'rollback valid-block preserve', 'RtOpfsBlockStoreErrorCode']));
  checks.push(includeAll('release-proof:valid-preserve-cases', files.releaseProof, [
    RELEASE_TASK, 'trace-failure-after-close-preserves-valid-final-block', 'abort-after-close-preserves-valid-final-block',
    'invalid-owned-failure-still-rolls-back-file', 'rollbackValidBlockPreserves', 'storage:opfs-block-put-rollback-preserved'
  ]));
  checks.push(includeAll('browser-proof:real-opfs-valid-preserve', files.browserProof, [
    BROWSER_TASK, 'browser-trace-failure-after-close-preserves-valid-final-block', 'opfsRollbackValidBlockPreserveProof',
    'rollbackValidBlockPreserves', 'storage:opfs-block-put-rollback-preserved', 'opfsWebLockGuardedBlockStore', 'locksAfterGuarded'
  ]));
  checks.push(includeAll('docs:boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, ['valid-final-block-preserved', 'content-addressed', 'not a transaction', 'Managed Chromium', 'cross-browser', 'quota/eviction', 'fsync']));

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
  checks.push({ label: 'manifest:current-valid-rollback-preserve-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0100-opfs-block-store-rollback-valid-block-preserve' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0100 valid rollback preserve slice');
  checks.push({ label: 'impact-map:rev0100-valid-rollback-preserve', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0100-valid-rollback-preserve', status: 'passed' });

  checks.push(includeAll('manifest:carried-forward-current-prefix', `${JSON.stringify(releaseTask)}\n${JSON.stringify(browserTask)}\n${JSON.stringify(auditTask)}`, [PFX, RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]));
  checks.push(includeAll('package:historical-script-names-present', Object.keys(pkg.scripts || {}).join('\n'), ['test:opfs-block-store-rollback-valid-block-preserve', 'test:browser:opfs-block-store-rollback-valid-block-preserve', 'audit:opfs-block-store-rollback-valid-block-preserve']));
  checks.push(includeAll('current-office:owned-by-rev0102-composite-abort-signal', files.currentOffice, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(includeAll('check-cube:current-composite-abort-signal-needles', files.checkCube, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit']));



  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the OPFS block-store rollback valid-block preserve slice: runtime rollback integrity guard, release/browser proof wiring, docs, manifest/impact/inventory rows, and carried-forward proof wiring while rev0102 owns current-office command routing.',
    checks,
    nonClaims: [
      'Audit only; release and managed-browser probes supply behavior evidence.',
      'This does not claim transactional writes, cancellation, fsync durability, crash/power-loss recovery, quota/eviction survival, cross-browser conformance, or production readiness.'
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
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[opfs_block_store_rollback_valid_block_preserve_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
