#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'opfs:block-store-readonly-no-create-proof';
const BROWSER_TASK = 'browser:opfs-block-store-readonly-no-create-proof';
const AUDIT_TASK = 'facility:opfs-block-store-readonly-no-create-contract-audit';
const PACKAGE_SLUG = 'opfs-block-store-readonly-no-create-current-proof';
const SURFACE_IDS = [
  'surface:opfs-block-store-readonly-no-create',
  'surface:browser-opfs-block-store-readonly-no-create',
  'surface:opfs-block-store-readonly-no-create-contract-audit'
];
const DEFAULT_OUT = `artifacts/audit/${PFX}-OPFS-BLOCK-STORE-READONLY-NO-CREATE-CONTRACT-AUDIT.json`;
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
    releaseProof: await text('tools/opfs_block_store_readonly_no_create_probe.mjs'),
    browserProof: await text('tools/browser_opfs_block_store_readonly_no_create_probe.mjs'),
    releaseDoc: await text('docs/40-validation/opfs-block-store-readonly-no-create-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-block-store-readonly-no-create-slice.md'),
    auditDoc: await text('docs/40-validation/opfs-block-store-readonly-no-create-contract-audit-slice.md'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile'),
    checkCube: await text('tools/check_cube.py'),
    currentOffice: await text('tools/current_office_audit.mjs'),
    deepAudit: await text('tools/deep_cube_audit.mjs')
  };
  const pkg = JSON.parse(files.packageJson);
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];

  checks.push(includeAll('runtime:no-create-boundary', files.runtime, [
    'Rev0101 keeps read-only miss paths no-create', 'noCreateMisses', 'storage:opfs-block-no-create-miss',
    '#recordNoCreateMiss', 'existingOnly: true', "source: 'verify'", "source: 'has'", "op: 'delete'"
  ]));
  checks.push(includeAll('browserrt:boot-proof-flag', files.browserrt, ['opfsReadOnlyNoCreateProof', 'opfsRollbackValidBlockPreserveProof', 'createOpfsAsyncBlockStore']));
  checks.push(includeAll('types:revision-and-no-create-anchor', files.types, [`REVISION: '${REVISION}'`, `VERSION: '${VERSION}'`, 'read-only miss paths use no-create', 'noCreateMisses']));
  checks.push(includeAll('fake-harness:mutation-recorder', files.fakeHarness, ['createDirectoryMutationRecorder', 'create-directory', 'create-file', 'remove-entry']));
  checks.push(includeAll('release-proof:no-create-cases', files.releaseProof, [
    RELEASE_TASK, 'missingReadOnly', 'unverifiedHasMissing', 'existingBlockStillWorks', 'createDirectoryMutationRecorder',
    'verify/has/delete/get should each record a no-create miss', 'storage:opfs-block-no-create-miss'
  ]));
  checks.push(includeAll('browser-proof:real-opfs-no-create', files.browserProof, [
    BROWSER_TASK, 'prefixExistsAfterVerify', 'prefixExistsAfterHas', 'prefixExistsAfterDelete', 'prefixExistsAfterGet',
    'opfsReadOnlyNoCreateProof', 'locksAfterGuarded', 'storage:opfs-block-no-create-miss'
  ]));
  checks.push(includeAll('docs:boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, ['no-create', 'empty directories', 'Managed Chromium', 'cross-browser', 'quota/eviction', 'fsync', 'crash']));

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
  checks.push({ label: 'manifest:current-readonly-no-create-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0102-opfs-block-store-readonly-no-create' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0102 read-only no-create slice');
  checks.push({ label: 'impact-map:rev0102-readonly-no-create', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0102-readonly-no-create', status: 'passed' });

  checks.push(includeAll('package:current-office-moved-to-composite-abort-signal', files.packageJson, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof']));
  checks.push(includeAll('makefile:current-routing-moved-to-composite-abort-signal', files.makefile, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs_block_store_raw_composite_abort_signal_contract_audit.mjs']));
  checks.push(includeAll('check-cube:current-composite-abort-signal-needles', files.checkCube, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(includeAll('deep-audit:current-composite-abort-signal-needles', files.deepAudit, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfsRawCompositeAbortSignal']));
  checks.push(includeAll('current-office:composite-abort-signal-needles', files.currentOffice, ['OPFS Raw Composite AbortSignal', 'opfs-block-store-raw-composite-abort-signal-current-proof', 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(rejectAny('package-current-scripts:no-stale-current-slices', `${script(pkg, 'test:current')}\n${script(pkg, 'test:browser:current')}\n${script(pkg, 'audit:current')}\n${script(pkg, 'package:current')}`, ['rollback-valid-block-preserve-current-proof', 'ROLLBACK-VALID-BLOCK-PRESERVE-RUN', 'write-budget-duplicate-bypass-current-proof', 'open-failure-recovery-current-proof']));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the OPFS block-store read-only no-create slice: runtime no-create miss routing, fake-harness mutation recorder refactor, release/browser proof wiring, docs, manifest/impact/inventory rows, and current-office command routing.',
    checks,
    nonClaims: [
      'Audit only; release and managed-browser probes supply behavior evidence.',
      'This does not claim recursive directory compaction, fsync durability, crash/power-loss recovery, quota/eviction survival, cross-browser conformance, Web Locks fairness, or production readiness.'
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
  console.error(`[opfs_block_store_readonly_no_create_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
