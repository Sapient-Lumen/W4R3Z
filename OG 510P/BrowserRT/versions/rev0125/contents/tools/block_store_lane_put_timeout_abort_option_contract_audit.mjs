#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const PACKAGE_SLUG = 'block-store-lane-put-timeout-abort-option-current-proof';
const RELEASE_TASK = 'storage:block-store-lane-put-timeout-abort-option-proof';
const BROWSER_TASK = 'browser:block-store-lane-put-timeout-abort-option-proof';
const AUDIT_TASK = 'facility:block-store-lane-put-timeout-abort-option-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PFX}-BLOCK-STORE-LANE-PUT-TIMEOUT-ABORT-OPTION-CONTRACT-AUDIT.json`;
const SURFACE_IDS = ['surface:block-store-lane-put-timeout-abort-option', 'surface:browser-block-store-lane-put-timeout-abort-option', 'surface:block-store-lane-put-timeout-abort-option-contract-audit'];
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function includeAll(label, value, needles) {
  const missing = needles.filter((needle) => !String(value).includes(needle));
  assert.deepEqual(missing, [], `${label} missing ${missing.join(', ')}`);
  return Object.freeze({ label, status: 'passed', needles: needles.length });
}
function rejectAny(label, value, needles) {
  const hits = needles.filter((needle) => String(value).includes(needle));
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
    scheduler: await text('src/storage-lane-scheduler.mjs'),
    browserrt: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    releaseProof: await text('tools/block_store_lane_put_timeout_abort_option_probe.mjs'),
    browserProof: await text('tools/browser_block_store_lane_put_timeout_abort_option_probe.mjs'),
    releaseDoc: await text('docs/40-validation/block-store-lane-put-timeout-abort-option-slice.md'),
    browserDoc: await text('docs/40-validation/browser-block-store-lane-put-timeout-abort-option-slice.md'),
    auditDoc: await text('docs/40-validation/block-store-lane-put-timeout-abort-option-contract-audit-slice.md'),
    packageJson: await text('package.json'),
    packageRelease: await text('tools/package_release.py'),
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

  checks.push(includeAll('adapter:schedule-put-forwards-timeout-abort-control', files.adapter, [
    'Rev0105 makes schedulePut honor per-operation',
    'abortProviderOnOperationTimeout = undefined, ...options',
    'abortProviderOnOperationTimeout, metadata',
    'abortProviderOnOperationTimeoutOverride',
    'scheduledProviderOptions(options, \'put\')',
    'callStoreWithScheduledContextOptions'
  ]));
  checks.push(includeAll('scheduler:per-operation-timeout-abort-supported', files.scheduler, [
    'abortProviderOnOperationTimeout = undefined',
    'abortOnTimeout = abortProviderOnOperationTimeout === undefined ? this.abortProviderOnOperationTimeout : abortProviderOnOperationTimeout === true',
    'providerAbortSignaled',
    'providerTimeoutAborts'
  ]));
  checks.push(includeAll('browserrt:current-runtime-version', files.browserrt, [
    `REVISION = '${REVISION}'`,
    `VERSION = '${VERSION}'`,
    'createBlockStoreLaneAdapter'
  ]));
  checks.push(includeAll('types:public-schedule-option', files.types, [
    `REVISION: '${REVISION}'`,
    `VERSION: '${VERSION}'`,
    'abortProviderOnOperationTimeout?: boolean',
    'rev0105: BlockStoreLaneAdapter.schedulePut forwards per-operation abortProviderOnOperationTimeout'
  ]));
  checks.push(includeAll('release-proof:put-timeout-abort-option-cases', files.releaseProof, [
    RELEASE_TASK,
    'runPutLevelOptInCase',
    'runPutLevelOptOutCase',
    'providerAbortSignaled',
    'providerTimeoutAborts',
    'successfulTimedOutOperations',
    'BRT_STORAGE_OPERATION_TIMEOUT',
    'abortProviderOnOperationTimeout',
    'optionKeys.includes(\'abortProviderOnOperationTimeout\')'
  ]));
  checks.push(includeAll('browser-proof:managed-opfs-put-timeout-abort-option', files.browserProof, [
    BROWSER_TASK,
    'blockStoreLanePutTimeoutAbortOptionProof',
    'browser-put-timeout-abort-opt-in',
    'browser-put-timeout-abort-opt-out',
    'FileSystemFileHandle.prototype.createWritable',
    'providerAbortSignaled',
    'successfulTimedOutOperations',
    'guarded-smoke',
    'locksAfter'
  ]));
  checks.push(includeAll('docs:put-timeout-abort-option-boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, [
    'schedulePut',
    'abortProviderOnOperationTimeout',
    'per-operation',
    'adapter default',
    'managed Chromium',
    'real OPFS',
    'cooperative',
    'cross-browser',
    'eviction',
    'fsync',
    'production readiness'
  ]));

  const releaseTask = manifestTask(manifest, RELEASE_TASK);
  const browserTask = manifestTask(manifest, BROWSER_TASK);
  const auditTask = manifestTask(manifest, AUDIT_TASK);
  for (const task of [releaseTask, browserTask, auditTask]) {
    const joined = JSON.stringify(task);
    assert.ok(joined.includes(PFX), `${task.id} must use current artifact prefix ${PFX}`);
    for (const id of [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]) assert.ok((task.currentTaskIds || []).includes(id), `${task.id} currentTaskIds missing ${id}`);
  }
  checks.push({ label: 'manifest:current-put-timeout-abort-option-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0105-block-store-lane-put-timeout-abort-option' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0105 put-timeout-abort-option slice');
  checks.push({ label: 'impact-map:rev0105-put-timeout-abort-option', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0105-put-timeout-abort-option', status: 'passed' });

  checks.push(includeAll('package:current-release-script', script(pkg, 'test:current'), ['opfs:block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', `${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  const currentBrowserScript = script(pkg, 'test:browser:current');
  checks.push(includeAll('package:current-browser-script', currentBrowserScript, ['tools/run_browser_bundle.mjs', '--mode current', `${PFX}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  assert.ok(!/--id\s+/.test(currentBrowserScript), 'package:current-browser-script must not use a hand-maintained --id subset');
  checks.push(includeAll('package:current-browser-script:bundle-runner-contains-raw-browser-task', await text('tools/run_browser_bundle.mjs'), ['browser:opfs-block-store-raw-composite-abort-signal-proof', 'CURRENT_TASKS', 'BATCH_LAYOUT']));
  checks.push(includeAll('package:current-audit-script', script(pkg, 'audit:current'), ['tools/opfs_block_store_raw_composite_abort_signal_contract_audit.mjs', `${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-CONTRACT-AUDIT.json`, 'tools/current_office_audit.mjs']));
  checks.push(includeAll('package:current-package-script', script(pkg, 'package:current'), ['opfs-block-store-raw-composite-abort-signal-current-proof', '--reuse-validation']));
  checks.push(includeAll('package-release:dynamic-current-artifact-prune', files.packageRelease, [
    'current_artifact_keep_set',
    'browserrt_current',
    "manifest.get('tasks'",
    'current_task_ids',
    'current_script_names'
  ]));
  checks.push(includeAll('makefile:current-routing', files.makefile, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs_block_store_raw_composite_abort_signal_contract_audit.mjs', 'opfs-block-store-raw-composite-abort-signal-current-proof']));
  checks.push(includeAll('check-cube:current-needles', files.checkCube, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof', 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(includeAll('deep-audit:current-needles', files.deepAudit, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof', 'opfsRawCompositeAbortSignal']));
  checks.push(includeAll('current-office:current-needles', files.currentOffice, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof', 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(rejectAny('package-current-scripts:no-stale-current-slices', `${script(pkg, 'test:current')}\n${script(pkg, 'test:browser:current')}\n${script(pkg, 'audit:current')}\n${script(pkg, 'package:current')}`, ['storage-lane-composite-abort-signal-current-proof', 'provider-timeout-abort-current-proof', 'block-store-lane-provider-options-current-proof', 'readonly-no-create-current-proof']));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the rev0105 block-store lane schedulePut timeout-abort option slice: runtime forwarding, release/browser proof wiring, docs, manifest/impact/surface rows, current-office routing, and package pruning.',
    checks,
    nonClaims: [
      'Audit only; release and managed-browser probes supply behavior evidence.',
      'Provider cancellation remains cooperative and explicitly configured; providers that ignore AbortSignal may still settle late and require quarantine review.',
      'This does not claim cross-browser conformance, quota reservation, eviction survival, fsync durability, crash recovery, Web Locks fairness, or production readiness.'
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
  console.error(`[block_store_lane_put_timeout_abort_option_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
