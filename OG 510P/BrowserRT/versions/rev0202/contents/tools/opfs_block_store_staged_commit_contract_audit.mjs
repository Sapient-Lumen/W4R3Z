#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:opfs-block-store-staged-commit-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-OPFS-BLOCK-STORE-STAGED-COMMIT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const text = async (path) => await readFile(path, 'utf8');

function includeAll(name, body, needles) {
  const missing = needles.filter((needle) => !body.includes(needle));
  return Object.freeze({ name, status: missing.length === 0 ? 'passed' : 'failed', missing });
}

export async function runAudit() {
  const started = performance.now();
  const opfsStore = await text('src/opfs-block-store.mjs');
  const probe = await text('tools/opfs_block_store_staged_commit_probe.mjs');
  const closeProbe = await text('tools/opfs_block_store_close_abort_inflight_probe.mjs');
  const manifest = await text('test/manifest.json');
  const packageJson = await text('package.json');
  const types = await text('src/types.d.ts');

  const checks = [
    includeAll('provider-stages-before-publishing-final-block', opfsStore, ['#stagedFileName', '#stagedBlockPath', 'storage:opfs-block-staged-write-start', 'storage:opfs-block-staged-write-verified', 'storage:opfs-block-staged-publish', 'stagedPuts', 'stagedWriteVerifications', 'stagedPublishWrites']),
    includeAll('provider-cleans-staged-files-on-success-and-failure', opfsStore, ['#cleanupStagedWrite', 'staged-put-published', 'failed-staged-put-cleanup', 'storage:opfs-block-staged-cleanup', 'stagedTempDeletes', 'stagedTempDeleteFailures', 'stagedTempDeleteMisses']),
    includeAll('provider-does-not-own-final-before-publish', opfsStore, ['stage: \'before-final-publish\'', 'rollbackOwnsFinalBlock = true', 'final-block-not-created-by-put', 'BRT_OPFS_STAGED_WRITE_VERIFY_FAILED']),
    includeAll('probe-executes-success-abort-and-corrupt-repair-cases', probe, ['successful-staged-publish', 'abort-after-stage-before-final-publish', 'corrupt-repair-staged-publish', 'staged temp file must be created before final canonical file', 'abort before final publish should not need final-path rollback', 'corrupt repair must also verify staged bytes']),
    includeAll('close-abort-proof-observes-staged-cleanup-context', closeProbe, ['close-during-inflight-put', 'rollback must delete the owned partial block even though the store is closed', 'fresh provider must not find the unacknowledged close-aborted digest']),
    includeAll('manifest-registers-staged-commit-proof-and-audit', manifest, ['opfs:block-store-staged-commit-proof', 'facility:opfs-block-store-staged-commit-contract-audit', 'OPFS-BLOCK-STORE-STAGED-COMMIT-PROBE', 'OPFS-BLOCK-STORE-STAGED-COMMIT-CONTRACT-AUDIT']),
    includeAll('package-current-runs-staged-commit-wedge', packageJson, ['opfs:block-store-staged-commit-proof', 'facility:opfs-block-store-staged-commit-contract-audit']),
    includeAll('types-expose-staging-receipt-and-error', types, ['BRT_OPFS_STAGED_WRITE_VERIFY_FAILED', 'staging?: Readonly<Record<string, unknown>> | null'])
  ];

  for (const check of checks) assert.equal(check.status, 'passed', `${check.name} missing ${check.missing.join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: 'passed', audit_id: `${REVISION}-opfs-block-store-staged-commit-contract-audit`, task_id: TASK_ID,
    generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Static contract audit that OPFS puts stage bytes in a temporary same-bucket block, verify the staged digest, publish the canonical content-addressed path only after staging succeeds, and clean temporary staged files across success, abort, and repair paths.',
    checks,
    correctedRiskSeams: [
      'new content-addressed puts no longer expose the canonical final block path as the first writable target',
      'caller abort after staged close but before final publish leaves no canonical digest and requires no final-path rollback',
      'successful puts and corrupt repairs carry a staging receipt and remove the temporary file after publish',
      'the close-abort in-flight path remains covered while now also producing staged cleanup context'
    ],
    nonClaims: [
      'Static audit only; the staged-commit probe supplies fake-OPFS behavior evidence.',
      'No atomic rename, fsync durability, power-loss safety, quota/eviction survival, browser matrix, or cross-browser OPFS claim.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
runAudit().then(async (report) => {
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
}).catch(async (error) => {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-opfs-block-store-staged-commit-contract-audit`, task_id: TASK_ID, generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_staged_commit_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
});
