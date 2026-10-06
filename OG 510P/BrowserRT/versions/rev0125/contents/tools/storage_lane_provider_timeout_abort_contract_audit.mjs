#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'storage:provider-timeout-abort-proof';
const BROWSER_TASK = 'browser:provider-timeout-abort-proof';
const AUDIT_TASK = 'facility:provider-timeout-abort-contract-audit';
const PACKAGE_SLUG = 'storage-lane-provider-timeout-abort-current-proof';
const SURFACE_IDS = [
  'surface:storage-lane-provider-timeout-abort',
  'surface:browser-storage-lane-provider-timeout-abort',
  'surface:storage-lane-provider-timeout-abort-contract-audit'
];
const DEFAULT_OUT = `artifacts/audit/${PFX}-STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-CONTRACT-AUDIT.json`;
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
    scheduler: await text('src/storage-lane-scheduler.mjs'),
    adapter: await text('src/block-store-lane-adapter.mjs'),
    opfsStore: await text('src/opfs-block-store.mjs'),
    browserrt: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    fakeHarness: await text('tools/lib/fake_opfs_harness.mjs'),
    releaseProof: await text('tools/storage_lane_provider_timeout_abort_probe.mjs'),
    browserProof: await text('tools/browser_storage_lane_provider_timeout_abort_probe.mjs'),
    releaseDoc: await text('docs/40-validation/storage-lane-provider-timeout-abort-slice.md'),
    browserDoc: await text('docs/40-validation/browser-storage-lane-provider-timeout-abort-slice.md'),
    auditDoc: await text('docs/40-validation/storage-lane-provider-timeout-abort-contract-audit-slice.md'),
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

  checks.push(includeAll('scheduler:timeout-abort-runtime', files.scheduler, [
    'abortProviderOnTimeout',
    'abortProviderOnOperationTimeout',
    'BRT_STORAGE_OPERATION_TIMEOUT_ABORT',
    'BRT_STORAGE_OPERATION_TIMEOUT_ABORT_UNAVAILABLE',
    'providerTimeoutAborts',
    'providerAbortSignaled',
    'signal: timeoutAbortController?.signal ?? null',
    'storage-lane:operation-timeout'
  ]));
  checks.push(includeAll('adapter:timeout-abort-pass-through', files.adapter, [
    'abortProviderOnOperationTimeout = false',
    'abortProviderOnOperationTimeout = undefined',
    'abortProviderOnOperationTimeout,',
    'withScheduledContextOptions',
    'scheduledProviderOptions'
  ]));
  checks.push(includeAll('opfs-store:provider-signal-honored', files.opfsStore, [
    'abortSignalFromOptions',
    'BRT_OPFS_OPERATION_ABORTED',
    'rollbackDeletes',
    'rollbackMisses'
  ]));
  checks.push(includeAll('browserrt:boot-flag', files.browserrt, [
    'storageLaneProviderTimeoutAbortProof',
    'createBlockStoreLaneAdapter',
    'createOpfsAsyncBlockStore'
  ]));
  checks.push(includeAll('types:public-timeout-abort-surface', files.types, [
    `REVISION: '${REVISION}'`,
    `VERSION: '${VERSION}'`,
    'abortProviderOnOperationTimeout?: boolean',
    'StorageLaneExecutor',
    'BlockStoreLaneScheduleOptions',
    'rev0103: abortProviderOnOperationTimeout'
  ]));
  checks.push(includeAll('fake-harness:abort-hooks', files.fakeHarness, [
    'FakeDirectoryHandle',
    'onWrite',
    'onAbort',
    'fakeTreeSummary'
  ]));
  checks.push(includeAll('release-proof:timeout-abort-cases', files.releaseProof, [
    RELEASE_TASK,
    'runDefaultNonCancellationCase',
    'runOptInOpfsAbortCase',
    'abortProviderOnOperationTimeout: true',
    'providerTimeoutAborts',
    'BRT_STORAGE_OPERATION_TIMEOUT',
    'BRT_OPFS_OPERATION_ABORTED',
    'validateBlockStoreLaneAdapterSnapshot'
  ]));
  checks.push(includeAll('browser-proof:real-opfs-timeout-abort', files.browserProof, [
    BROWSER_TASK,
    'storageLaneProviderTimeoutAbortProof',
    'abortProviderOnOperationTimeout: true',
    'FileSystemFileHandle.prototype.createWritable',
    'abortCalls',
    'afterSettledTree.fileCount',
    'guarded-smoke',
    'locksAfter'
  ]));
  checks.push(includeAll('docs:boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, [
    'abortProviderOnOperationTimeout',
    'AbortSignal',
    'operation timeout',
    'opt-in',
    'managed Chromium',
    'cooperative',
    'cross-browser',
    'eviction',
    'fsync',
    'crash'
  ]));

  const releaseTask = manifestTask(manifest, RELEASE_TASK);
  const browserTask = manifestTask(manifest, BROWSER_TASK);
  const auditTask = manifestTask(manifest, AUDIT_TASK);
  for (const task of [releaseTask, browserTask, auditTask]) {
    const joined = JSON.stringify(task);
    assert.ok(joined.includes(PFX), `${task.id} must use current artifact prefix ${PFX}`);
    for (const id of [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]) {
      assert.ok((task.currentTaskIds || []).includes(id), `${task.id} currentTaskIds missing ${id}`);
    }
  }
  checks.push({ label: 'manifest:current-provider-timeout-abort-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => row.id === 'impact:rev0103-storage-lane-provider-timeout-abort' && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0103 provider-timeout-abort slice');
  checks.push({ label: 'impact-map:rev0103-provider-timeout-abort', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0103-provider-timeout-abort', status: 'passed' });

  checks.push(includeAll('package:historical-release-script', script(pkg, 'test:storage-lane-provider-timeout-abort'), [RELEASE_TASK, AUDIT_TASK, `${PFX}-STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-RUN.json`]));
  checks.push(includeAll('package:historical-browser-script', script(pkg, 'test:browser:storage-lane-provider-timeout-abort'), [BROWSER_TASK, `${PFX}-BROWSER-STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-RUN.json`]));
  checks.push(includeAll('package:historical-audit-script', script(pkg, 'audit:storage-lane-provider-timeout-abort'), ['tools/storage_lane_provider_timeout_abort_contract_audit.mjs', `${PFX}-STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-CONTRACT-AUDIT.json`]));
  checks.push(includeAll('package:current-package-script-moved-to-composite-abort-signal', script(pkg, 'package:current'), ['opfs-block-store-raw-composite-abort-signal-current-proof', '--reuse-validation']));
  checks.push(includeAll('makefile:current-routing-moved-to-composite-abort-signal', files.makefile, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs_block_store_raw_composite_abort_signal_contract_audit.mjs', 'opfs-block-store-raw-composite-abort-signal-current-proof']));
  checks.push(includeAll('check-cube:current-needles-moved-to-composite-abort-signal', files.checkCube, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof', 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(includeAll('deep-audit:current-needles-moved-to-composite-abort-signal', files.deepAudit, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof', 'opfsRawCompositeAbortSignal']));
  checks.push(includeAll('current-office:current-needles-moved-to-composite-abort-signal', files.currentOffice, ['opfs:block-store-raw-composite-abort-signal-proof', 'browser:opfs-block-store-raw-composite-abort-signal-proof', 'facility:opfs-block-store-raw-composite-abort-signal-contract-audit', 'opfs-block-store-raw-composite-abort-signal-current-proof', 'RAW-COMPOSITE-ABORT-SIGNAL']));
  checks.push(rejectAny('package-current-scripts:no-provider-timeout-current-alias', `${script(pkg, 'test:current')}
${script(pkg, 'test:browser:current')}
${script(pkg, 'audit:current')}
${script(pkg, 'package:current')}`, ['provider-timeout-abort-current-proof', 'storage:provider-timeout-abort-proof', 'browser:provider-timeout-abort-proof', 'facility:provider-timeout-abort-contract-audit']));


  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the storage-lane provider-timeout-abort slice: timeout-owned AbortSignal runtime markers, scheduled adapter pass-through, OPFS cancellation evidence, release/browser proof wiring, docs, manifest/impact/inventory rows, and carried-forward historical command routing plus current-office handoff to the composite AbortSignal slice.',
    checks,
    nonClaims: [
      'Audit only; release and managed-browser probes supply behavior evidence.',
      'Provider abort on timeout is opt-in and cooperative; providers that ignore AbortSignal may still settle late and require quarantine review.',
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
  console.error(`[storage_lane_provider_timeout_abort_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
