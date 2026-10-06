#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const PACKAGE_SLUG = 'opfs-block-store-raw-composite-abort-signal-current-proof';
const RELEASE_TASK = 'opfs:block-store-raw-composite-abort-signal-proof';
const BROWSER_TASK = 'browser:opfs-block-store-raw-composite-abort-signal-proof';
const AUDIT_TASK = 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-CONTRACT-AUDIT.json`;
const SURFACE_IDS = ['surface:opfs-block-store-raw-composite-abort-signal', 'surface:browser-opfs-block-store-raw-composite-abort-signal', 'surface:opfs-block-store-raw-composite-abort-signal-contract-audit'];
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
    opfsStore: await text('src/opfs-block-store.mjs'),
    browserrt: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    releaseProof: await text('tools/opfs_block_store_raw_composite_abort_signal_probe.mjs'),
    browserProof: await text('tools/browser_opfs_block_store_raw_composite_abort_signal_probe.mjs'),
    releaseDoc: await text('docs/40-validation/opfs-block-store-raw-composite-abort-signal-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-block-store-raw-composite-abort-signal-slice.md'),
    auditDoc: await text('docs/40-validation/opfs-block-store-raw-composite-abort-signal-contract-audit-slice.md'),
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

  checks.push(includeAll('runtime:raw-opfs-composite-abort-signal', files.opfsStore, [
    'Rev0107 composes raw provider signal and abortSignal',
    'OPFS_COMPOSITE_ABORT_CLEANUP',
    'composeAbortSignals',
    'abortSignalFromOptions',
    'signalOptionSupplied',
    'abortSignalOptionSupplied',
    'storage:opfs-block-composite-abort-signal',
    'compositeAbortSignals',
    'abortSignalOptionPairs',
    'BRT_OPFS_OPERATION_ABORTED',
    'BRT_OPFS_ABORT_SIGNAL_INVALID',
    '#cleanupAbortContext'
  ]));
  checks.push(includeAll('browserrt:version-and-proof-flag', files.browserrt, [
    `REVISION = '${REVISION}'`,
    `VERSION = '${VERSION}'`,
    'opfsRawCompositeAbortSignalProof',
    'opfsAsyncBlockStoreProof'
  ]));
  checks.push(includeAll('types:raw-composite-marker', files.types, [
    `REVISION: '${REVISION}'`,
    `VERSION: '${VERSION}'`,
    'signal?: AbortSignal | null',
    'abortSignal?: AbortSignal | null',
    'opfsRawCompositeAbortSignalProof?: boolean',
    'rev0108: Raw OpfsAsyncBlockStore composes signal/abortSignal'
  ]));
  checks.push(includeAll('release-proof:raw-composite-cases', files.releaseProof, [
    RELEASE_TASK,
    'pre-aborted-abortSignal-with-live-signal-put',
    'invalid-abortSignal-with-valid-signal-put',
    'secondary-abortSignal-mid-write-put',
    'pre-aborted-abortSignal-with-live-signal-get',
    'storage:opfs-block-composite-abort-signal',
    'BRT_OPFS_ABORT_SIGNAL_INVALID'
  ]));
  checks.push(includeAll('browser-proof:managed-raw-composite-cases', files.browserProof, [
    BROWSER_TASK,
    'opfsRawCompositeAbortSignalProof',
    'browser-pre-aborted-abortSignal-with-live-signal-put',
    'browser-invalid-abortSignal-with-valid-signal-put',
    'FileSystemFileHandle.prototype.createWritable',
    'browser-secondary-abortSignal-before-write-put',
    'guarded OPFS/Web Locks smoke',
    'locksAfter'
  ]));
  checks.push(includeAll('docs:raw-composite-boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, [
    'OpfsAsyncBlockStore',
    'signal',
    'abortSignal',
    'BRT_OPFS_OPERATION_ABORTED',
    'BRT_OPFS_ABORT_SIGNAL_INVALID',
    'managed Chromium',
    'real OPFS',
    'cross-browser',
    'fsync',
    'crash',
    'eviction',
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
  checks.push({ label: `${REVISION}:manifest-raw-composite-tasks`, status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });

  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === `impact:${REVISION}-opfs-block-store-raw-composite-abort-signal` && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing current raw composite AbortSignal slice');
  checks.push({ label: `${REVISION}:impact-map-opfs-block-store-raw-composite-abort-signal`, status: 'passed' });

  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok((row.currentTaskIds || []).includes(RELEASE_TASK), `${id} missing current release task anchor`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: `${REVISION}:surface-inventory-raw-composite`, status: 'passed' });

  checks.push(includeAll('package:current-release-script', script(pkg, 'test:current'), [RELEASE_TASK, AUDIT_TASK, `${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  const currentBrowserScript = script(pkg, 'test:browser:current');
  checks.push(includeAll('package:current-browser-script', currentBrowserScript, ['tools/run_browser_bundle.mjs', '--mode current', `${PFX}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`]));
  assert.ok(!/--id\s+/.test(currentBrowserScript), 'package:current-browser-script must not use a hand-maintained --id subset');
  checks.push(includeAll('browser-bundle-runner:current-raw-task', await text('tools/run_browser_bundle.mjs'), [BROWSER_TASK, 'CURRENT_TASKS', 'BATCH_LAYOUT']));
  checks.push(includeAll('package:current-audit-script', script(pkg, 'audit:current'), ['tools/opfs_block_store_raw_composite_abort_signal_contract_audit.mjs', `${PFX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-CONTRACT-AUDIT.json`, 'tools/current_office_audit.mjs']));
  checks.push(includeAll('package:current-package-script', script(pkg, 'package:current'), [PACKAGE_SLUG, '--reuse-validation']));
  checks.push(includeAll('package-release:dynamic-current-artifact-prune', files.packageRelease, [
    'current_artifact_keep_set',
    'browserrt_current',
    "manifest.get('tasks'",
    'current_task_ids',
    'current_script_names'
  ]));
  checks.push(includeAll('makefile:current-routing', files.makefile, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, 'opfs_block_store_raw_composite_abort_signal_contract_audit.mjs', PACKAGE_SLUG]));
  checks.push(includeAll('check-cube:current-needles', files.checkCube, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, PACKAGE_SLUG, 'OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(includeAll('deep-audit:current-needles', files.deepAudit, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, PACKAGE_SLUG, 'opfsRawCompositeAbortSignalProof']));
  checks.push(includeAll('current-office:current-needles', files.currentOffice, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, PACKAGE_SLUG, 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(rejectAny('package-current-scripts:no-stale-current-slices', `${script(pkg, 'test:current')}\n${script(pkg, 'test:browser:current')}\n${script(pkg, 'audit:current')}\n${script(pkg, 'package:current')}`, ['web-lock-guarded-abort-signal-current-proof', 'block-store-lane-put-timeout-abort-option-current-proof', 'storage-lane-composite-abort-signal-current-proof', 'provider-timeout-abort-current-proof', 'readonly-no-create-current-proof']));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for rev0108 raw OPFS signal/abortSignal composition: runtime hooks, release/browser proofs, docs, manifest/impact/surface rows, current-office routing, and package pruning.',
    checks,
    nonClaims: [
      'Contract audit only; release and browser proofs provide executable behavior evidence.',
      'No cross-browser, OPFS fsync durability, crash recovery, quota/eviction, Web Locks fairness, or production-readiness claim.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runAudit();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: AUDIT_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[opfs_block_store_raw_composite_abort_signal_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
