#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-OPFS-BLOCK-STORE-CLOSE-BOUNDARY-CONTRACT-AUDIT.json`;
const TASK_ID = 'facility:opfs-block-store-close-boundary-contract-audit';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const text = async (path) => await readFile(path, 'utf8');

function includeAll(name, body, needles) {
  const missing = needles.filter((needle) => !body.includes(needle));
  return Object.freeze({ name, status: missing.length === 0 ? 'passed' : 'failed', missing });
}

export async function runAudit() {
  const started = performance.now();
  const opfsStore = await text('src/opfs-block-store.mjs');
  const laneAdapter = await text('src/block-store-lane-adapter.mjs');
  const guardedStore = await text('src/opfs-web-lock-guarded-block-store.mjs');
  const runtime = await text('src/browserrt.mjs');
  const types = await text('src/types.d.ts');
  const probe = await text('tools/opfs_block_store_close_boundary_probe.mjs');
  const smoke = await text('test/smoke.mjs');
  const manifest = await text('test/manifest.json');

  const checks = [
    includeAll('opfs-provider-close-boundary', opfsStore, ['#closed = false', '#throwIfClosed', 'BRT_OPFS_STORE_CLOSED', 'storage:opfs-blockstore-close', 'storage:opfs-blockstore-closed-reject', 'closeAsync({ reason = \'opfs-block-store-close\' }', 'closedOperationRejects']),
    includeAll('storage-lane-adapter-close-boundary', laneAdapter, ['#closed = false', '#ownStore = false', 'BRT_BLOCK_STORE_LANE_ADAPTER_CLOSED', 'block-store-lane:close', 'block-store-lane:closed-reject', 'closeAsync({ reason = \'block-store-lane-adapter-close\' }', 'ownStore']),
    includeAll('web-lock-guard-close-boundary', guardedStore, ['#closed = false', 'ownStore', 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED', 'storage:opfs-web-lock-guard-close', 'storage:opfs-web-lock-guard-closed-reject', 'closeAsync({ reason = \'opfs-web-lock-guard-close\' }']),
    includeAll('runtime-owns-opfs-closeables', runtime, ["track(store, 'opfs-async-block-store'", "track(adapter, 'opfs-storage-lane-adapter'", "track(guard, 'opfs-web-lock-guarded-block-store'", 'owned: false', 'ownStore: config.ownStore ?? !config.store']),
    includeAll('types-expose-close-boundary', types, ['close(reason?: string):', 'closeAsync(options?: { reason?: string }): Promise', 'readonly closed: boolean;', 'ownStore?: boolean']),
    includeAll('probe-executes-close-boundary', probe, ['directProviderCloseCase', 'runtimeOwnershipCloseCase', 'BRT_OPFS_STORE_CLOSED', 'BRT_BLOCK_STORE_LANE_ADAPTER_CLOSED', 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED', 'Provider close is not data deletion']),
    includeAll('smoke-exercises-close-boundary', smoke, ['runtime-owned-close-opfs-store', 'runtime-owned-close-opfs-adapter', 'runtime-owned-close-opfs-guard', 'storage:opfs-blockstore-close', 'block-store-lane:close', 'storage:opfs-web-lock-guard-close']),
    includeAll('manifest-registers-close-boundary', manifest, ['opfs:block-store-close-boundary-proof', 'facility:opfs-block-store-close-boundary-contract-audit', 'OPFS-BLOCK-STORE-CLOSE-BOUNDARY-PROBE', 'OPFS-BLOCK-STORE-CLOSE-BOUNDARY-CONTRACT-AUDIT'])
  ];

  for (const check of checks) assert.equal(check.status, 'passed', `${check.name} missing ${check.missing.join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    status: 'passed', audit_id: `${REVISION}-opfs-block-store-close-boundary-contract-audit`, task_id: TASK_ID,
    generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Static contract audit for OPFS close-boundary runtime ownership: closeable OpfsAsyncBlockStore providers, closeable storage-lane adapters/guards, runtime ownership, declarations, smoke coverage, and release manifest wiring.',
    checks,
    correctedRiskSeams: [
      'OPFS provider objects now have an explicit closed state and reject future operations after close.',
      'Runtime-owned OPFS stores, storage-lane adapters, and Web Lock guards are included in runtime.closeAsync resource ownership.',
      'Adapters/guards that create their own underlying OPFS store own and close that store; wrappers around caller-supplied stores do not take implicit ownership.',
      'Provider close is represented as a lifecycle boundary, not deletion of acknowledged block data.'
    ],
    remainingRisks: [
      'closeAsync prevents new operations; it is not a general cancellation mechanism for arbitrary already-running provider code.',
      'The behavioral proof is fake-OPFS release-tier evidence and must not be inflated into a browser or crash-durability claim.'
    ],
    nonClaims: [
      'Static source/manifest audit only; runtime probe and smoke provide behavioral evidence.',
      'No cross-browser OPFS behavior, fsync durability, quota/eviction survival, Web Locks fairness, or production storage-readiness claim.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
runAudit().then(async (report) => {
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
}).catch(async (error) => {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-opfs-block-store-close-boundary-contract-audit`, task_id: TASK_ID, generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_close_boundary_contract_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
});
