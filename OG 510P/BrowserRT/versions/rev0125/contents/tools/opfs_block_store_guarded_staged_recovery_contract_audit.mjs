#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:opfs-block-store-guarded-staged-recovery-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-OPFS-BLOCK-STORE-GUARDED-STAGED-RECOVERY-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const text = async (path) => await readFile(path, 'utf8');

function includeAll(name, body, needles) {
  const missing = needles.filter((needle) => !body.includes(needle));
  return Object.freeze({ name, status: missing.length === 0 ? 'passed' : 'failed', missing });
}

export async function runAudit() {
  const started = performance.now();
  const guard = await text('src/opfs-web-lock-guarded-block-store.mjs');
  const probe = await text('tools/opfs_block_store_guarded_staged_recovery_probe.mjs');
  const manifest = await text('test/manifest.json');
  const packageJson = await text('package.json');
  const types = await text('src/types.d.ts');

  const checks = [
    includeAll('guard-exposes-exclusive-staged-recovery', guard, ['async recoverStagedWrites(options = {})', 'this.stats.stagedRecoveries += 1', "this.#run('recoverStagedWrites', 'exclusive'", 'this.store.recoverStagedWrites(providerOptions)']),
    includeAll('guard-stats-and-comment-cover-risk', guard, ['stagedRecoveries: 0', 'same exclusive Web Lock', 'staged-temp cleanup cannot race guarded puts']),
    includeAll('types-expose-guarded-recovery-method', types, ['class WebLockGuardedBlockStore', 'recoverStagedWrites(options?:', 'maxDeletes?: number', 'rev0125: WebLockGuardedBlockStore.recoverStagedWrites']),
    includeAll('probe-demonstrates-unguarded-risk-and-guarded-serialization', probe, ['runUnguardedRecoveryRaceCase', 'runGuardedRecoverySerializationCase', 'QueuedFakeWebLocks', 'guardB.recoverStagedWrites', 'unguarded second provider recovery demonstrates the race', 'recovery must acquire only after put releases']),
    includeAll('manifest-registers-guarded-staged-recovery-proof-and-audit', manifest, ['opfs:block-store-guarded-staged-recovery-proof', 'facility:opfs-block-store-guarded-staged-recovery-contract-audit', 'OPFS-BLOCK-STORE-GUARDED-STAGED-RECOVERY-PROBE', 'OPFS-BLOCK-STORE-GUARDED-STAGED-RECOVERY-CONTRACT-AUDIT']),
    includeAll('package-current-runs-guarded-staged-recovery-wedge', packageJson, ['opfs:block-store-guarded-staged-recovery-proof', 'facility:opfs-block-store-guarded-staged-recovery-contract-audit', 'test:opfs-block-store-guarded-staged-recovery', 'audit:opfs-block-store-guarded-staged-recovery'])
  ];

  for (const check of checks) assert.equal(check.status, 'passed', `${check.name} missing ${check.missing.join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: 'passed', audit_id: `${REVISION}-opfs-block-store-guarded-staged-recovery-contract-audit`, task_id: TASK_ID,
    generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Static contract audit that guarded staged recovery is exposed and serialized through the same exclusive Web Lock as guarded puts, with a runtime probe demonstrating the unguarded race and the guarded fix.',
    checks,
    correctedRiskSeams: [
      'guarded recovery is no longer missing from WebLockGuardedBlockStore even though raw providers expose recoverStagedWrites',
      'staged recovery can now be run through the same cross-provider/cross-tab lock name used by guarded put/delete/cleanupForTest',
      'the new proof catches regressions where recovery would acquire before a live guarded staged publish releases'
    ],
    nonClaims: [
      'Static audit only; runtime probe supplies fake-OPFS/fake-Web-Locks behavior evidence.',
      'This does not protect raw providers that bypass the guard or providers using different lock names.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
runAudit().then(async (report) => {
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
}).catch(async (error) => {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-opfs-block-store-guarded-staged-recovery-contract-audit`, task_id: TASK_ID, generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_guarded_staged_recovery_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
});
