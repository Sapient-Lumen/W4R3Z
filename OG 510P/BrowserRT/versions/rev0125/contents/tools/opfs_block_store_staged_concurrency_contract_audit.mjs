#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:opfs-block-store-staged-concurrency-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-OPFS-BLOCK-STORE-STAGED-CONCURRENCY-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const text = async (path) => await readFile(path, 'utf8');

function includeAll(name, body, needles) {
  const missing = needles.filter((needle) => !body.includes(needle));
  return Object.freeze({ name, status: missing.length === 0 ? 'passed' : 'failed', missing });
}

export async function runAudit() {
  const started = performance.now();
  const opfsStore = await text('src/opfs-block-store.mjs');
  const probe = await text('tools/opfs_block_store_staged_concurrency_probe.mjs');
  const manifest = await text('test/manifest.json');
  const packageJson = await text('package.json');
  const types = await text('src/types.d.ts');

  const checks = [
    includeAll('provider-uses-instance-unique-staged-temp-names', opfsStore, ['createStageSessionId', '#stageSessionId', '#stagedFileName', 'brt-stage-${this.#stageSessionId}', 'stageSessionId']),
    includeAll('provider-tracks-active-staged-writes', opfsStore, ['#activeStagedWrites', '#markActiveStagedWrite', '#clearActiveStagedWrite', '#isActiveStagedWrite', 'storage:opfs-block-staged-active-start', 'storage:opfs-block-staged-active-settle']),
    includeAll('recovery-skips-active-staged-files', opfsStore, ['active-staged-write', 'stagedRecoveryActiveSkips', 'activeSkipped', 'this.#isActiveStagedWrite(match.hash, fileName)']),
    includeAll('probe-executes-active-recovery-and-two-provider-cases', probe, ['runActiveRecoverySkipCase', 'runTwoProviderSameDigestCase', 'activeRecoverySkip', 'twoProviderSameDigest', 'provider-instance staged temp filenames must be unique for same digest']),
    includeAll('manifest-registers-staged-concurrency-proof-and-audit', manifest, ['opfs:block-store-staged-concurrency-proof', 'facility:opfs-block-store-staged-concurrency-contract-audit', 'OPFS-BLOCK-STORE-STAGED-CONCURRENCY-PROBE', 'OPFS-BLOCK-STORE-STAGED-CONCURRENCY-CONTRACT-AUDIT']),
    includeAll('package-current-runs-staged-concurrency-wedge', packageJson, ['opfs:block-store-staged-concurrency-proof', 'facility:opfs-block-store-staged-concurrency-contract-audit']),
    includeAll('types-mention-staged-concurrency-snapshot-fields', types, ['stageSessionId', 'activeStagedWrites'])
  ];

  for (const check of checks) assert.equal(check.status, 'passed', `${check.name} missing ${check.missing.join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: 'passed', audit_id: `${REVISION}-opfs-block-store-staged-concurrency-contract-audit`, task_id: TASK_ID,
    generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Static contract audit that OPFS staged commit filenames are provider-instance unique and same-runtime staged recovery skips live staged writes instead of deleting active put temp files.',
    checks,
    correctedRiskSeams: [
      'two provider instances no longer derive the same staged temp filename from only digest plus per-instance opSeq',
      'same-runtime recoverStagedWrites cannot delete a temp file currently owned by an in-flight put',
      'active staged ownership is visible in snapshots and trace events and clears when the operation settles'
    ],
    nonClaims: [
      'Static audit only; runtime probe supplies fake-OPFS behavior evidence.',
      'The active staged registry is in-process only and does not replace cross-tab Web Lock coordination.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
runAudit().then(async (report) => {
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
}).catch(async (error) => {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-opfs-block-store-staged-concurrency-contract-audit`, task_id: TASK_ID, generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_staged_concurrency_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
});
