#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const PACKAGE_SLUG = 'storage-lane-composite-abort-signal-current-proof';
const RELEASE_TASK = 'storage:composite-abort-signal-proof';
const BROWSER_TASK = 'browser:composite-abort-signal-proof';
const AUDIT_TASK = 'facility:composite-abort-signal-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PFX}-STORAGE-LANE-COMPOSITE-ABORT-SIGNAL-CONTRACT-AUDIT.json`;
const SURFACE_IDS = ['surface:storage-lane-composite-abort-signal', 'surface:browser-storage-lane-composite-abort-signal', 'surface:storage-lane-composite-abort-signal-contract-audit'];
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
    opfsStore: await text('src/opfs-block-store.mjs'),
    browserrt: await text('src/browserrt.mjs'),
    types: await text('src/types.d.ts'),
    fakeHarness: await text('tools/lib/fake_opfs_harness.mjs'),
    releaseProof: await text('tools/storage_lane_composite_abort_signal_probe.mjs'),
    browserProof: await text('tools/browser_storage_lane_composite_abort_signal_probe.mjs'),
    releaseDoc: await text('docs/40-validation/storage-lane-composite-abort-signal-slice.md'),
    browserDoc: await text('docs/40-validation/browser-storage-lane-composite-abort-signal-slice.md'),
    auditDoc: await text('docs/40-validation/storage-lane-composite-abort-signal-contract-audit-slice.md'),
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

  checks.push(includeAll('adapter:composite-abort-runtime', files.adapter, [
    'composeAbortSignals',
    'SCHEDULED_COMPOSITE_ABORT_CLEANUP',
    'AbortSignal.any',
    'providerSignalComposed',
    'compositeAbortSignal',
    'callStoreWithScheduledContextOptions',
    'Preserve invalid caller signal shape',
    'out.signal = composition.signal',
    'out.abortSignal = composition.signal'
  ]));
  checks.push(includeAll('scheduler:timeout-abort-carried-forward', files.scheduler, [
    'abortProviderOnTimeout',
    'providerTimeoutAborts',
    'providerAbortSignaled',
    'signal: timeoutAbortController?.signal ?? null'
  ]));
  checks.push(includeAll('opfs-store:caller-signal-honored', files.opfsStore, [
    'abortSignalFromOptions',
    'BRT_OPFS_OPERATION_ABORTED',
    'stage: \'before-digest\'',
    'abortRejects'
  ]));
  checks.push(includeAll('browserrt:boot-flag', files.browserrt, [
    `REVISION = '${REVISION}'`,
    `VERSION = '${VERSION}'`,
    'storageLaneCompositeAbortSignalProof',
    'storageLaneProviderTimeoutAbortProof',
    'createBlockStoreLaneAdapter'
  ]));
  checks.push(includeAll('types:public-composite-surface', files.types, [
    `REVISION: '${REVISION}'`,
    `VERSION: '${VERSION}'`,
    'compositeAbortSignal?: boolean',
    'providerSignalComposed?: boolean',
    'storageLaneCompositeAbortSignalProof?: boolean',
    'rev0104: scheduled provider AbortSignal composition'
  ]));
  checks.push(includeAll('fake-harness:mutation-recorder', files.fakeHarness, [
    'createDirectoryMutationRecorder',
    'fakeTreeSummary',
    'withFakeNavigator'
  ]));
  checks.push(includeAll('release-proof:composite-abort-cases', files.releaseProof, [
    RELEASE_TASK,
    'runPreAbortedCallerSignalCase',
    'runCallerAbortBeforeTimeoutCase',
    'runDualCallerSignalCase',
    'runTimeoutStillAbortsWithLiveCallerSignalCase',
    'providerSignalComposed',
    'BRT_OPFS_OPERATION_ABORTED',
    'BRT_STORAGE_OPERATION_TIMEOUT',
    'validateBlockStoreLaneAdapterSnapshot'
  ]));
  checks.push(includeAll('browser-proof:managed-opfs-composite-abort', files.browserProof, [
    BROWSER_TASK,
    'storageLaneCompositeAbortSignalProof',
    'browser-preaborted-caller-signal-opfs-put',
    'before-digest',
    'browser-composite-live-signal-put',
    'guarded-smoke',
    'locksAfter'
  ]));
  checks.push(includeAll('docs:boundaries', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, [
    'composite AbortSignal',
    'caller AbortSignal',
    'timeout-owned AbortSignal',
    'pre-aborted',
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
    for (const id of [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK]) assert.ok((task.currentTaskIds || []).includes(id), `${task.id} currentTaskIds missing ${id}`);
  }
  checks.push({ label: 'manifest:current-composite-abort-signal-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok([...(impact.impacts || []), ...(impact.rules || [])].some((row) => (row.id === 'impact:rev0104-storage-lane-composite-abort-signal' || row.id === 'impact:rev0105-storage-lane-composite-abort-signal') && (row.required || row.requiredTaskIds || row.taskIds || []).includes(RELEASE_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(BROWSER_TASK) && (row.required || row.requiredTaskIds || row.taskIds || []).includes(AUDIT_TASK)), 'impact map missing rev0104 composite-abort-signal slice');
  checks.push({ label: 'impact-map:rev0104-composite-abort-signal', status: 'passed' });
  for (const id of SURFACE_IDS) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
    assert.ok(row.phase, `${id} missing phase`);
    assert.ok(Array.isArray(row.requiredEvidence) && row.requiredEvidence.length > 0, `${id} missing requiredEvidence`);
  }
  checks.push({ label: 'surface-inventory:rev0104-composite-abort-signal', status: 'passed' });

  checks.push(includeAll('package:carried-forward-composite-scripts', files.packageJson, ['test:storage-lane-composite-abort-signal', 'test:browser:storage-lane-composite-abort-signal', 'audit:storage-lane-composite-abort-signal']));
  checks.push(includeAll('package-release:dynamic-current-artifact-prune', files.packageRelease, [
    'current_artifact_keep_set',
    'browserrt_current',
    "manifest.get('tasks'",
    'current_task_ids',
    'current_script_names',
    'This prevents the pruning'
  ]));
  checks.push(rejectAny('package-release:no-hardcoded-previous-current-slice-prune', files.packageRelease, [
    'STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-PROBE',
    'STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-RUN',
    'STORAGE-LANE-PROVIDER-TIMEOUT-ABORT-CONTRACT-AUDIT'
  ]));
  checks.push(includeAll('current-office:moved-to-put-timeout-abort-option', `${files.packageJson}
${files.makefile}
${files.checkCube}
${files.currentOffice}`, ['coord:web-lock-guarded-abort-signal-proof', 'browser:opfs-web-lock-guarded-abort-signal-proof', 'facility:web-lock-guarded-abort-signal-contract-audit', 'web-lock-guarded-abort-signal-current-proof']));
  checks.push(rejectAny('package-current-scripts:no-composite-current-alias', `${script(pkg, 'test:current')}
${script(pkg, 'test:browser:current')}
${script(pkg, 'audit:current')}
${script(pkg, 'package:current')}`, ['storage-lane-composite-abort-signal-current-proof', 'storage:composite-abort-signal-proof', 'browser:composite-abort-signal-proof', 'facility:composite-abort-signal-contract-audit']));
  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Contract audit for the storage-lane composite AbortSignal slice: adapter composition runtime, caller/timeout signal precedence proofs, managed Chromium OPFS evidence, docs, manifest/impact/inventory rows, and carried-forward current-office boundary.',
    checks,
    nonClaims: [
      'Audit only; release and managed-browser probes supply behavior evidence.',
      'Abort remains cooperative; providers that ignore AbortSignal may still settle late and require quarantine review.',
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
  console.error(`[storage_lane_composite_abort_signal_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
