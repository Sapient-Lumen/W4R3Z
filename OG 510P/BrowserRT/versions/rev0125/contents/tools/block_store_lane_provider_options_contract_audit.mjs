#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'storage:block-store-lane-provider-options-proof';
const BROWSER_TASK = 'browser:block-store-lane-provider-options-proof';
const AUDIT_TASK = 'facility:block-store-lane-provider-options-contract-audit';
const PACKAGE_SLUG = 'block-store-lane-provider-options-current-proof';
const SURFACE_IDS = [
  'surface:block-store-lane-provider-options',
  'surface:browser-block-store-lane-provider-options',
  'surface:block-store-lane-provider-options-contract-audit'
];
const DEFAULT_OUT = `artifacts/audit/${PFX}-BLOCK-STORE-LANE-PROVIDER-OPTIONS-CONTRACT-AUDIT.json`;
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
    adapter: await text('src/block-store-lane-adapter.mjs'),
    opfsStore: await text('src/opfs-block-store.mjs'),
    browserrt: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    fakeHarness: await text('tools/lib/fake_opfs_harness.mjs'),
    releaseProof: await text('tools/block_store_lane_provider_options_probe.mjs'),
    browserProof: await text('tools/browser_block_store_lane_provider_options_probe.mjs'),
    releaseDoc: await text('docs/40-validation/block-store-lane-provider-options-slice.md'),
    browserDoc: await text('docs/40-validation/browser-block-store-lane-provider-options-slice.md'),
    auditDoc: await text('docs/40-validation/block-store-lane-provider-options-contract-audit-slice.md'),
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

  checks.push(includeAll('adapter:scheduled-provider-options', files.adapter, [
    'scheduledProviderOptions', 'withScheduledContextOptions', 'providerOptions', 'storeOptions', 'putOptions', 'getOptions', 'hasOptions', 'verifyOptions', 'deleteOptions', 'estimateOptions', 'cleanupOptions', 'providerOptionKeys'
  ]));
  checks.push(includeAll('adapter:all-schedule-methods-pass-options', files.adapter, [
    'schedulePut(payload', 'this.#store.put(payload', 'this.#store.get(ref', 'this.#store.has(ref', 'this.#store.verify(ref', 'this.#store.delete(ref', 'this.#store.estimate(scheduledOptions', 'cleanupForTest(scheduledOptions', 'callStoreWithScheduledContextOptions'
  ]));
  checks.push(includeAll('opfs-store:safety-options-exist', files.opfsStore, [
    'writeBudgetGuardForPut', 'BRT_OPFS_WRITE_BUDGET_EXCEEDED', 'BRT_OPFS_OPERATION_ABORTED', 'abortSignalFromOptions'
  ]));
  checks.push(includeAll('browserrt:boot-flag-and-factory', files.browserrt, ['blockStoreLaneProviderOptionsProof', 'createBlockStoreLaneAdapter', 'createOpfsAsyncBlockStore']));
  checks.push(includeAll('types:schedule-option-surface', files.types, [`REVISION: '${REVISION}'`, `VERSION: '${VERSION}'`, 'BlockStoreLaneProviderOptions', 'BlockStoreLaneScheduleOptions', 'providerOptions?', 'storeOptions?', 'putOptions?', 'getOptions?']));
  checks.push(includeAll('fake-harness:estimate-recorder', files.fakeHarness, ['createStorageEstimateRecorder', 'estimateCalls', 'navigatorStorage']));
  checks.push(includeAll('release-proof:provider-option-cases', files.releaseProof, [
    RELEASE_TASK, 'runProviderBudgetRejectCase', 'runNamedPutOptionsOverrideCase', 'runProviderAbortReadCase', 'runNamedOptionBagsCase', 'providerOptions.writeBudgetGuard', 'putOptions.writeBudgetGuard', 'providerOptions.signal'
  ]));
  checks.push(includeAll('browser-proof:real-opfs-provider-options', files.browserProof, [
    BROWSER_TASK, 'providerOptions.writeBudgetGuard', 'putOptions.writeBudgetGuard', 'providerOptions.signal', 'maxUsageRatio: 1e-30', 'guarded-smoke', 'locksAfter'
  ]));
  checks.push(includeAll('docs:boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, ['providerOptions', 'storeOptions', 'writeBudgetGuard', 'signal', 'scheduled', 'Managed Chromium', 'cross-browser', 'quota', 'eviction', 'fsync', 'crash']));

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
  checks.push({ label: 'manifest:current-provider-options-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0102-block-store-lane-provider-options' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0102 provider-options slice');
  checks.push({ label: 'impact-map:rev0102-provider-options', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0102-provider-options', status: 'passed' });

  checks.push(includeAll('package:carried-forward-release-script', script(pkg, 'test:block-store-lane-provider-options'), [RELEASE_TASK, AUDIT_TASK, `${PFX}-BLOCK-STORE-LANE-PROVIDER-OPTIONS-RUN.json`]));
  checks.push(includeAll('package:carried-forward-browser-script', script(pkg, 'test:browser:block-store-lane-provider-options'), [BROWSER_TASK, `${PFX}-BROWSER-BLOCK-STORE-LANE-PROVIDER-OPTIONS-RUN.json`]));
  checks.push(includeAll('package:carried-forward-audit-script', script(pkg, 'audit:block-store-lane-provider-options'), ['tools/block_store_lane_provider_options_contract_audit.mjs', `${PFX}-BLOCK-STORE-LANE-PROVIDER-OPTIONS-CONTRACT-AUDIT.json`]));
  checks.push(rejectAny('package-current-scripts:no-provider-options-masquerading-current', `${script(pkg, 'test:current')}
${script(pkg, 'test:browser:current')}
${script(pkg, 'audit:current')}
${script(pkg, 'package:current')}`, [PACKAGE_SLUG, RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the block-store lane provider-options slice: scheduled option pass-through runtime markers, typed surface, release/browser proof wiring, docs, manifest/impact/inventory rows, and carried-forward command routing.',
    checks,
    nonClaims: [
      'Audit only; release and managed-browser probes supply behavior evidence.',
      'This does not claim cross-browser conformance, quota reservation, eviction survival, fsync durability, crash/power-loss recovery, Web Locks fairness, or production readiness.'
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
  console.error(`[block_store_lane_provider_options_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
