#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-OPFS-BLOCK-STORE-OPEN-FAILURE-RECOVERY-CONTRACT-AUDIT.json`;
const RELEASE_TASK = 'opfs:block-store-open-failure-recovery-proof';
const BROWSER_TASK = 'browser:opfs-block-store-open-failure-recovery-proof';
const AUDIT_TASK = 'facility:opfs-block-store-open-failure-recovery-contract-audit';
const PACKAGE_SLUG = 'opfs-block-store-open-failure-recovery-current-proof';
const CODENAME = 'OPFS Block Store Open Failure Recovery';
const SURFACE_IDS = [
  'surface:opfs-block-store-open-failure-recovery',
  'surface:browser-opfs-block-store-open-failure-recovery',
  'surface:opfs-block-store-open-failure-recovery-contract-audit'
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
    releaseProof: await text('tools/opfs_block_store_open_failure_recovery_probe.mjs'),
    browserProof: await text('tools/browser_opfs_block_store_open_failure_recovery_probe.mjs'),
    releaseDoc: await text('docs/40-validation/opfs-block-store-open-failure-recovery-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-block-store-open-failure-recovery-slice.md'),
    auditDoc: await text('docs/40-validation/opfs-block-store-open-failure-recovery-contract-audit-slice.md'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile'),
    checkCube: await text('tools/check_cube.py'),
    currentOfficeAudit: await text('tools/current_office_audit.mjs')
  };
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];
  checks.push(includeAll('runtime:open-failure-recovery', files.runtime, [
    'openFailures', 'openRetryResets', 'storage:opfs-blockstore-open-error', 'rootPromiseReset',
    'Rev0098 resets a failed cached OPFS open promise'
  ]));
  checks.push(includeAll('browserrt:boot-proof-flag', files.browserrt, ['opfsOpenFailureRecoveryProof', 'createOpfsAsyncBlockStore']));
  checks.push(includeAll('types:open-failure-recovery-anchor', files.types, ['rev0098: OpfsAsyncBlockStore resets failed OPFS root open promises', "REVISION: 'rev0087'", `export const REVISION: '${REVISION}'`]));
  checks.push(includeAll('fake-harness:fail-once-directory-open-helper', files.fakeHarness, ['createFailOnceDirectoryOpenHarness', 'remainingFailures', 'onGetDirectoryHandle', 'withFakeNavigator']));
  checks.push(includeAll('release-proof:open-retry-cases', files.releaseProof, [RELEASE_TASK, 'first-open-fails-and-resets-root-promise', 'second-open-retries-and-succeeds', 'first-put-open-failure-rejects-without-poisoning-store', 'second-put-retries-open-and-succeeds', 'openRetryResets']));
  checks.push(includeAll('browser-proof:real-opfs-open-retry-cases', files.browserProof, [BROWSER_TASK, 'browser-first-open-fails-and-resets-root-promise', 'browser-second-open-retries-and-succeeds', 'browser-first-put-open-failure-does-not-poison-store', 'rootPromiseReset', 'locksAfterGuarded']));
  checks.push(includeAll('docs:nonclaim-boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, ['open failure', 'root promise', 'cross-browser', 'fsync', 'crash', 'eviction', 'production readiness']));

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
  checks.push({ label: 'manifest:current-open-failure-recovery-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0098-opfs-block-store-open-failure-recovery' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0098 open failure recovery slice');
  checks.push({ label: 'impact-map:rev0098-open-failure-recovery', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0098-open-failure-recovery', status: 'passed' });
  checks.push(includeAll('package:carried-forward-open-failure-scripts', files.packageJson, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]));
  checks.push(includeAll('makefile:current-routing-moved-to-rollback-preserve', files.makefile, ['opfs-block-store-rollback-valid-block-preserve-current-proof']));
  checks.push(includeAll('check-cube:current-office-now-rollback-preserve', files.checkCube, ['opfs-block-store-rollback-valid-block-preserve-current-proof']));
  checks.push(includeAll('current-office:audit-needles', files.currentOfficeAudit, ['OPFS Block Store Rollback Valid Block Preserve', 'opfs-block-store-rollback-valid-block-preserve-current-proof']));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Carried-forward contract audit for the OPFS block-store open failure recovery slice: runtime cached-root-promise reset, release/browser proofs, docs, manifest/impact/inventory rows, and current-office boundary after rev0100 moved current routing.',
    checks,
    nonClaims: [
      'Audit only; runtime and managed browser probes supply behavior evidence.',
      'This does not claim cross-browser conformance, fsync durability, crash safety, quota/eviction survival, multi-tab atomicity, Web Locks fairness, adversarial tamper resistance, or production readiness.'
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
  console.error(`[opfs_block_store_open_failure_recovery_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
