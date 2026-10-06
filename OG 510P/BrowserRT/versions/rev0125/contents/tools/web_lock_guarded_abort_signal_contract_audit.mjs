#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const PACKAGE_SLUG = 'web-lock-guarded-abort-signal-current-proof';
const RELEASE_TASK = 'coord:web-lock-guarded-abort-signal-proof';
const BROWSER_TASK = 'browser:opfs-web-lock-guarded-abort-signal-proof';
const AUDIT_TASK = 'facility:web-lock-guarded-abort-signal-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PFX}-WEB-LOCK-GUARDED-ABORT-SIGNAL-CONTRACT-AUDIT.json`;
const SURFACE_IDS = ['surface:web-lock-guarded-abort-signal', 'surface:browser-opfs-web-lock-guarded-abort-signal', 'surface:web-lock-guarded-abort-signal-contract-audit'];
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
    guardedStore: await text('src/opfs-web-lock-guarded-block-store.mjs'),
    coordinator: await text('src/web-lock-coordinator.mjs'),
    browserrt: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    releaseProof: await text('tools/web_lock_guarded_abort_signal_probe.mjs'),
    browserProof: await text('tools/browser_opfs_web_lock_guarded_abort_signal_probe.mjs'),
    releaseDoc: await text('docs/40-validation/web-lock-guarded-abort-signal-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-web-lock-guarded-abort-signal-slice.md'),
    auditDoc: await text('docs/40-validation/web-lock-guarded-abort-signal-contract-audit-slice.md'),
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

  checks.push(includeAll('guarded-store:abort-signal-composition', files.guardedStore, [
    'Rev0106 composes signal/abortSignal',
    'guardedAbortOptions',
    'composeGuardedAbortSignals',
    'storage:opfs-web-lock-guard-abort-signal',
    'abortSignalOperations',
    'compositeAbortSignals',
    'invalidAbortSignalsPreserved',
    'guardedAbortSignalComposed'
  ]));
  checks.push(includeAll('coordinator:preserves-provider-errors-after-acquisition', files.coordinator, [
    'Rev0106 only classifies external AbortSignal as lock-aborted before acquisition',
    '&& !abortState.acquired',
    'BRT_WEB_LOCK_ABORTED',
    'acquired: abortState.acquired === true'
  ]));
  checks.push(includeAll('browserrt:current-runtime-version-and-proof-flag', files.browserrt, [
    `REVISION = '${REVISION}'`,
    `VERSION = '${VERSION}'`,
    'opfsWebLockGuardedAbortSignalProof',
    'createWebLockGuardedBlockStore'
  ]));
  checks.push(includeAll('types:public-current-markers', files.types, [
    `REVISION: '${REVISION}'`,
    `VERSION: '${VERSION}'`,
    'opfsWebLockGuardedAbortSignalProof?: boolean',
    'rev0106: WebLockGuardedBlockStore composes signal/abortSignal'
  ]));
  checks.push(includeAll('release-proof:guarded-abort-signal-cases', files.releaseProof, [
    RELEASE_TASK,
    'AbortableQueuedLocks',
    'queued-put-abortSignal-only',
    'withShared-abortSignal-only',
    'dual-signal-provider-abort',
    'BRT_FAKE_PROVIDER_ABORTED',
    'BRT_WEB_LOCK_SIGNAL_INVALID'
  ]));
  checks.push(includeAll('browser-proof:managed-opfs-guarded-abort-signal', files.browserProof, [
    BROWSER_TASK,
    'opfsWebLockGuardedAbortSignalProof',
    'browser-abortSignal-only-pending-put',
    'browser-dual-signal-provider-abort',
    'FileSystemFileHandle.prototype.createWritable',
    'BRT_OPFS_OPERATION_ABORTED',
    'locksAfter'
  ]));
  checks.push(includeAll('docs:guarded-abort-signal-boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, [
    'WebLockGuardedBlockStore',
    'abortSignal',
    'signal',
    'BRT_WEB_LOCK_ABORTED',
    'BRT_OPFS_OPERATION_ABORTED',
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
  checks.push({ label: 'manifest:current-guarded-abort-signal-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => (row.id === 'impact:rev0106-web-lock-guarded-abort-signal' || row.id === 'impact:rev0108-web-lock-guarded-abort-signal') && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0106 Web Lock guarded AbortSignal slice');
  checks.push({ label: 'impact-map:rev0106-web-lock-guarded-abort-signal', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0106-web-lock-guarded-abort-signal', status: 'passed' });

  checks.push(includeAll('package:current-release-script-carried-forward-to-rev0108', script(pkg, 'test:current'), ['opfs:block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', `${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  const currentBrowserScript = script(pkg, 'test:browser:current');
  checks.push(includeAll('package:current-browser-script-carried-forward-to-rev0108', currentBrowserScript, ['tools/run_browser_bundle.mjs', '--mode current', `${PFX}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  assert.ok(!/--id\s+/.test(currentBrowserScript), 'package:current-browser-script-carried-forward-to-rev0108 must not use a hand-maintained --id subset');
  checks.push(includeAll('package:current-browser-script-carried-forward-to-rev0108:bundle-runner-contains-raw-browser-task', await text('tools/run_browser_bundle.mjs'), ['browser:opfs-block-store-raw-composite-abort-signal-proof', 'CURRENT_TASKS', 'BATCH_LAYOUT']));
  checks.push(includeAll('package:current-audit-script-carried-forward-to-rev0108', script(pkg, 'audit:current'), ['tools/opfs_block_store_raw_composite_abort_signal_contract_audit.mjs', `${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-CONTRACT-AUDIT.json`, 'tools/current_office_audit.mjs']));
  checks.push(includeAll('package:current-package-script-carried-forward-to-rev0108', script(pkg, 'package:current'), ['opfs-block-store-raw-composite-abort-signal-current-proof', '--reuse-validation']));
  checks.push(includeAll('package-release:dynamic-current-artifact-prune', files.packageRelease, [
    'current_artifact_keep_set',
    'browserrt_current',
    "manifest.get('tasks'",
    'current_task_ids',
    'current_script_names'
  ]));
  checks.push(includeAll('makefile:current-routing-carried-forward-to-rev0108', files.makefile, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs_block_store_raw_composite_abort_signal_contract_audit.mjs', 'opfs-block-store-raw-composite-abort-signal-current-proof']));
  checks.push(includeAll('check-cube:carried-forward-needles', files.checkCube, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, 'surface:web-lock-guarded-abort-signal']));
  checks.push(includeAll('deep-audit:carried-forward-needles', files.deepAudit, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, 'opfsWebLockGuardedAbortSignal']));
  checks.push(includeAll('current-office:current-needles-carried-forward-to-rev0108', files.currentOffice, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof', 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(rejectAny('package-current-scripts:no-stale-current-slices', `${script(pkg, 'test:current')}\n${script(pkg, 'test:browser:current')}\n${script(pkg, 'audit:current')}\n${script(pkg, 'package:current')}`, ['block-store-lane-put-timeout-abort-option-current-proof', 'storage-lane-composite-abort-signal-current-proof', 'provider-timeout-abort-current-proof', 'block-store-lane-provider-options-current-proof', 'readonly-no-create-current-proof']));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the rev0106 Web Lock guarded AbortSignal slice: runtime signal/abortSignal composition, coordinator post-acquisition provider-error preservation, release/browser proof wiring, docs, manifest/impact/surface rows, current-office routing, and package pruning.',
    checks,
    nonClaims: [
      'Audit only; release and managed-browser probes supply behavior evidence.',
      'Abort remains cooperative; lock manager and provider code must observe the signal to prevent late mutation.',
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
  console.error(`[web_lock_guarded_abort_signal_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
