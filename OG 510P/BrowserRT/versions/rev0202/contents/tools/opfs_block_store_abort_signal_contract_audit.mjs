#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-OPFS-BLOCK-STORE-ABORT-SIGNAL-CONTRACT-AUDIT.json`;
const RELEASE_TASK = 'opfs:block-store-abort-signal-proof';
const BROWSER_TASK = 'browser:opfs-block-store-abort-signal-proof';
const AUDIT_TASK = 'facility:opfs-block-store-abort-signal-contract-audit';
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
function surface(surfaces, id) {
  const row = (surfaces.surfaces || []).find((item) => item.id === id);
  assert.ok(row, `surface inventory missing ${id}`);
  return row;
}

export async function runAudit() {
  const started = performance.now();
  const files = {
    runtime: await text('src/opfs-block-store.mjs'),
    types: await text('src/types.d.ts'),
    fakeHarness: await text('tools/lib/fake_opfs_harness.mjs'),
    releaseProof: await text('tools/opfs_block_store_abort_signal_probe.mjs'),
    browserProof: await text('tools/browser_opfs_block_store_abort_signal_probe.mjs'),
    corruptProof: await text('tools/opfs_block_store_corrupt_block_repair_probe.mjs'),
    releaseDoc: await text('docs/40-validation/opfs-block-store-abort-signal-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-block-store-abort-signal-slice.md'),
    auditDoc: await text('docs/40-validation/opfs-block-store-abort-signal-contract-audit-slice.md'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile')
  };
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];
  checks.push(includeAll('runtime:explicit-abort-signal-guard', files.runtime, [
    'abortSignalFromOptions', 'BRT_OPFS_OPERATION_ABORTED', 'BRT_OPFS_ABORT_SIGNAL_INVALID', 'storage:opfs-block-abort', 'storage:opfs-block-abort-signal-invalid', 'async put(value, fields = {}, options = {})', 'this.#throwIfAborted(signal', 'storage:opfs-block-put-rollback'
  ]));
  checks.push(includeAll('types:opfs-options', files.types, ['BRT_OPFS_OPERATION_ABORTED', 'BRT_OPFS_ABORT_SIGNAL_INVALID', 'put(value: string | Uint8Array | ArrayBuffer | ArrayBufferView, fields?: Record<string, unknown>, options?:', 'get(refOrDigest: string | RtBlockRef, options?:', 'cleanupForTest(options?:']));
  checks.push(includeAll('fake-opfs-harness:shared-refactor', files.fakeHarness, ['FakeDirectoryHandle', 'FakeFileHandle', 'withFakeNavigator', 'fakeTreeSummary', 'onBeforeClose', 'onAbort']));
  checks.push(includeAll('corrupt-proof:uses-shared-fake-harness', files.corruptProof, ['from \'./lib/fake_opfs_harness.mjs\'', 'withFakeNavigator', 'writeFakePath']));
  checks.push(includeAll('release-proof:abort-signal-claims', files.releaseProof, [RELEASE_TASK, 'pre-aborted-put', 'invalid-signal-put', 'mid-write-abort-onWrite', 'mid-write-abort-onBeforeClose', 'BRT_OPFS_OPERATION_ABORTED', 'BRT_OPFS_ABORT_SIGNAL_INVALID', 'storage-lane operation timeouts']));
  checks.push(includeAll('browser-proof:abort-signal-claims', files.browserProof, [BROWSER_TASK, 'raw-pre-aborted-put', 'raw-invalid-signal-put', 'raw-pre-aborted-get', 'snapshotAfterRejectedPrePut.opened', 'guarded null-signal OPFS put']));
  checks.push(includeAll('docs:release-browser-audit', `${files.releaseDoc}\n${files.browserDoc}\n${files.auditDoc}`, ['AbortSignal', 'BRT_OPFS_OPERATION_ABORTED', 'not storage-lane timeout cancellation', 'Managed Chromium', 'fake-OPFS harness']));

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
  checks.push({ label: 'manifest:current-abort-signal-tasks', status: 'passed', taskIds: [releaseTask.id, browserTask.id, auditTask.id] });
  assert.ok((impact.impacts || []).some((row) => row.id === 'impact:rev0095-opfs-block-store-abort-signal' && row.required?.includes(RELEASE_TASK) && row.required?.includes(BROWSER_TASK) && row.required?.includes(AUDIT_TASK)), 'impact map missing rev0095 abort signal slice');
  checks.push({ label: 'impact-map:rev0095-abort-signal', status: 'passed' });
  for (const id of ['surface:opfs-block-store-abort-signal', 'surface:browser-opfs-block-store-abort-signal', 'surface:opfs-block-store-abort-signal-contract-audit']) {
    const row = surface(inventory, id);
    assert.ok((row.taskIds || []).some((taskId) => [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK].includes(taskId)), `${id} missing task id`);
  }
  checks.push({ label: 'surface-inventory:rev0095-abort-signal', status: 'passed' });
  checks.push(includeAll('package:carried-forward-abort-signal-scripts', files.packageJson, [RELEASE_TASK, BROWSER_TASK, AUDIT_TASK, 'test:opfs-block-store-abort-signal', 'test:browser:opfs-block-store-abort-signal', 'audit:opfs-block-store-abort-signal']));
  checks.push(includeAll('makefile:current-office-carried-forward-to-composite-abort-signal', files.makefile, ['opfs-block-store-raw-composite-abort-signal-current-proof']));
  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    task_id: AUDIT_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Carried-forward contract audit for the OPFS block-store explicit AbortSignal guard slice and fake-OPFS harness refactor.',
    checks,
    nonClaims: [
      'Audit only; runtime and managed browser probes supply behavior evidence.',
      'This does not claim storage-lane timeout cancellation, OPFS fsync durability, crash safety, quota/eviction behavior, or cross-browser conformance.'
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
  console.error(`[opfs_block_store_abort_signal_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
