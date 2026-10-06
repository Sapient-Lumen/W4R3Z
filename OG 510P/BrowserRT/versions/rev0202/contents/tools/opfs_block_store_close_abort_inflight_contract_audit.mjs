#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:opfs-block-store-close-abort-inflight-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-OPFS-BLOCK-STORE-CLOSE-ABORT-INFLIGHT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const text = async (path) => await readFile(path, 'utf8');

function includeAll(name, body, needles) {
  const missing = needles.filter((needle) => !body.includes(needle));
  return Object.freeze({ name, status: missing.length === 0 ? 'passed' : 'failed', missing });
}

export async function runAudit() {
  const started = performance.now();
  const opfsStore = await text('src/opfs-block-store.mjs');
  const probe = await text('tools/opfs_block_store_close_abort_inflight_probe.mjs');
  const smoke = await text('test/smoke.mjs');
  const manifest = await text('test/manifest.json');
  const packageJson = await text('package.json');

  const checks = [
    includeAll('provider-close-aborts-inflight-operations', opfsStore, ['#closeController', '#beginOperation', '#endOperation', 'storage:opfs-block-lifecycle-abort-signal', 'closeAbortSignals', 'closeAbortRejects', 'operationsStarted', 'operationsSettled', 'inFlightAtClose', 'inFlightAfterClose']),
    includeAll('open-and-bucket-paths-share-lifecycle-signal', opfsStore, ['async #openPrefixRoot({ signal', "stage: 'after-open-prefix-part'", 'async open(options = {})', 'async #bucket(hash, create = true, { signal', "stage: 'after-open-first-bucket'", "stage: 'after-open-second-bucket'", "await this.#bucket(hash, true, { signal, op: 'put' })"]),
    includeAll('rollback-can-clean-owned-partial-after-close', opfsStore, ['ignoreClosed = false', 'ignoreClosed: true', 'failed-put-rollback-preserve-check', "reason: 'failed-put-rollback'", 'rollbackDeletes', 'BRT_OPFS_OPERATION_ABORTED']),
    includeAll('probe-executes-close-abort-inflight', probe, ['close-during-inflight-put', 'probe-close-during-inflight-write', 'close-during-bucket-open-put', 'probe-close-during-hash-bucket-open', 'createdSecondBucket', 'BRT_OPFS_OPERATION_ABORTED', 'BRT_OPFS_STORE_CLOSED', 'rollback must delete the owned partial block even though the store is closed', 'fresh provider must not find the unacknowledged close-aborted digest']),
    includeAll('smoke-retains-runtime-close-boundary', smoke, ['runtime-owned-close-opfs-store', 'runtime-owned-close-opfs-adapter', 'runtime-owned-close-opfs-guard']),
    includeAll('manifest-registers-close-abort-inflight', manifest, ['opfs:block-store-close-abort-inflight-proof', 'facility:opfs-block-store-close-abort-inflight-contract-audit', 'OPFS-BLOCK-STORE-CLOSE-ABORT-INFLIGHT-PROBE', 'OPFS-BLOCK-STORE-CLOSE-ABORT-INFLIGHT-CONTRACT-AUDIT']),
    includeAll('package-current-script-runs-close-abort-inflight', packageJson, ['opfs:block-store-close-abort-inflight-proof', 'facility:opfs-block-store-close-abort-inflight-contract-audit', 'OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN'])
  ];

  for (const check of checks) assert.equal(check.status, 'passed', `${check.name} missing ${check.missing.join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: 'passed', audit_id: `${REVISION}-opfs-block-store-close-abort-inflight-contract-audit`, task_id: TASK_ID,
    generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Static contract audit that OPFS provider close is an aborting lifecycle fence for admitted operations, and that owned partial-write rollback still works after the store is closed.',
    checks,
    correctedRiskSeams: [
      'closeAsync now aborts a lifecycle signal observed by admitted OPFS operations.',
      'in-flight operation snapshots expose close-time and post-settlement counts.',
      'rollback paths can bypass the public closed-state gate to remove owned partial files after close-induced aborts.',
      'open and mutable bucket directory paths now share the provider lifecycle abort signal before staged/final file creation.',
      'the release proof distinguishes close-before-commit rollback from the older valid-final-block-preserve contract.'
    ],
    nonClaims: [
      'Static audit only; the close-abort-inflight probe supplies fake-OPFS behavior evidence.',
      'No browser matrix, fsync durability, power-loss safety, quota/eviction survival, renderer-kill recovery, or cross-browser OPFS claim.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
runAudit().then(async (report) => {
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
}).catch(async (error) => {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-opfs-block-store-close-abort-inflight-contract-audit`, task_id: TASK_ID, generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_close_abort_inflight_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
});
