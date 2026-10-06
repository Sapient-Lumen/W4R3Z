#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:opfs-block-store-staged-recovery-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-OPFS-BLOCK-STORE-STAGED-RECOVERY-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const text = async (path) => await readFile(path, 'utf8');

function includeAll(name, body, needles) {
  const missing = needles.filter((needle) => !body.includes(needle));
  return Object.freeze({ name, status: missing.length === 0 ? 'passed' : 'failed', missing });
}

export async function runAudit() {
  const started = performance.now();
  const opfsStore = await text('src/opfs-block-store.mjs');
  const fakeHarness = await text('tools/lib/fake_opfs_harness.mjs');
  const probe = await text('tools/opfs_block_store_staged_recovery_probe.mjs');
  const manifest = await text('test/manifest.json');
  const packageJson = await text('package.json');
  const types = await text('src/types.d.ts');

  const checks = [
    includeAll('provider-exposes-explicit-staged-recovery-sweep', opfsStore, ['recoverStagedWrites', '#directoryEntries', '#stagedHashFromFileName', '#isStagedFileInExpectedBucket', 'storage:opfs-block-staged-recovery-delete', 'storage:opfs-block-staged-recovery-skip', 'stagedRecoverySweeps', 'stagedRecoveryDeletes']),
    includeAll('provider-fails-closed-for-uniterable-directories-and-delete-failures', opfsStore, ['BRT_OPFS_DIRECTORY_ITERATION_UNAVAILABLE', 'BRT_OPFS_STAGED_RECOVERY_FAILED', 'failOnError', 'maxDeletes', 'prefixMissing', 'truncated']),
    includeAll('provider-preserves-canonical-and-out-of-bucket-files', opfsStore, ['same-bucket-staged-temp', 'staged-name-outside-digest-bucket', 'not-browserrt-staged-name', 'nested-directory-in-block-bucket']),
    includeAll('fake-opfs-harness-supports-directory-iteration', fakeHarness, ['async *entries()', '[Symbol.asyncIterator]()', "this.kind = 'directory'", "this.kind = 'file'", 'onEntries']),
    includeAll('probe-executes-recovery-missing-prefix-and-abort-cases', probe, ['runSameBucketRecoveryCase', 'runMissingPrefixCase', 'runPreAbortedCase', 'wrong-bucket staged-name bait must not be deleted', 'canonical committed block must remain', 'pre-aborted recovery must leave orphan file untouched']),
    includeAll('manifest-registers-staged-recovery-proof-and-audit', manifest, ['opfs:block-store-staged-recovery-proof', 'facility:opfs-block-store-staged-recovery-contract-audit', 'OPFS-BLOCK-STORE-STAGED-RECOVERY-PROBE', 'OPFS-BLOCK-STORE-STAGED-RECOVERY-CONTRACT-AUDIT']),
    includeAll('package-current-runs-staged-recovery-wedge', packageJson, ['opfs:block-store-staged-recovery-proof', 'facility:opfs-block-store-staged-recovery-contract-audit']),
    includeAll('types-expose-recovery-method-and-errors', types, ['recoverStagedWrites', 'BRT_OPFS_STAGED_RECOVERY_FAILED', 'BRT_OPFS_STAGED_RECOVERY_INVALID', 'BRT_OPFS_DIRECTORY_ITERATION_UNAVAILABLE'])
  ];

  for (const check of checks) assert.equal(check.status, 'passed', `${check.name} missing ${check.missing.join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: 'passed', audit_id: `${REVISION}-opfs-block-store-staged-recovery-contract-audit`, task_id: TASK_ID,
    generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Static contract audit that abandoned OPFS staged temp files have an explicit recovery sweep which enumerates the existing prefix without creating it, deletes only same-bucket BrowserRT staged names, preserves canonical .blk blocks, and fails closed on uniterable directories or delete failures.',
    checks,
    correctedRiskSeams: [
      'interrupted staged writes now have an explicit cleanup/recovery path instead of leaving unbounded temp files forever',
      'recovery does not delete canonical .blk blocks or staged-looking files stored outside the digest-derived bucket',
      'a missing prefix is a no-op recovery report rather than a directory-creating side effect',
      'pre-aborted recovery rejects before deletion so lifecycle cancellation remains authoritative'
    ],
    nonClaims: [
      'Static audit only; the staged-recovery probe supplies fake-OPFS behavior evidence.',
      'No atomic rename, fsync durability, power-loss safety, quota/eviction survival, browser matrix, or cross-browser OPFS claim.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
runAudit().then(async (report) => {
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
}).catch(async (error) => {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-opfs-block-store-staged-recovery-contract-audit`, task_id: TASK_ID, generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_staged_recovery_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
});
