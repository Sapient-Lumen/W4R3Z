#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD-PROBE.json`;
const RELEASE_TASK = 'opfs:block-store-owned-rollback-guard-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}
async function capture(label, fn) {
  try { return { label, ok: true, value: await fn(), error: null }; }
  catch (error) { return { label, ok: false, value: null, error: captureError(error) }; }
}
function payloadOf(label, bytes = 1536) {
  const out = new Uint8Array(bytes);
  const seed = new TextEncoder().encode(`BrowserRT ${REVISION} OPFS owned rollback guard ${label}`);
  out.set(seed.slice(0, Math.min(seed.byteLength, out.byteLength)));
  for (let i = seed.byteLength; i < out.length; i += 1) out[i] = (i * 29 + label.length * 17) & 255;
  return out;
}
function sameBytes(a, b) {
  if (a.byteLength !== b.byteLength) return false;
  for (let i = 0; i < a.byteLength; i += 1) if (a[i] !== b[i]) return false;
  return true;
}
function throwingDuplicateTrace(events) {
  return {
    emit(kind, payload = {}) {
      events.push({ kind, duplicate: payload?.duplicate === true, reason: payload?.reason ?? null, errorCode: payload?.error?.code ?? null });
      if (kind === 'storage:opfs-block-put' && payload?.duplicate === true) {
        throw new Error('intentional trace failure after duplicate put classification');
      }
    }
  };
}

async function runDuplicateTraceFailureCase() {
  const payload = payloadOf('duplicate-trace-failure');
  const prefix = `browserrt/${REVISION}/fake-owned-rollback-duplicate-trace`;
  const traceEvents = [];
  return await withFakeNavigator(async (root) => {
    const seedStore = createOpfsAsyncBlockStore({ name: `${REVISION}-owned-rollback-seed`, prefix });
    const first = await seedStore.put(payload, { label: 'seed-valid-block' });
    const beforeVerify = await seedStore.verify(first.ref);
    const throwingStore = createOpfsAsyncBlockStore({ name: `${REVISION}-owned-rollback-duplicate-trace`, prefix, trace: throwingDuplicateTrace(traceEvents) });
    const duplicateFailure = await capture('duplicate-put-trace-failure-must-not-delete-existing-block', () => throwingStore.put(payload, { label: 'duplicate-put-trace-failure' }));
    const afterVerify = await seedStore.verify(first.ref);
    const afterGet = await seedStore.get(first.ref);
    return { first, beforeVerify, duplicateFailure, afterVerify, bytesPreserved: sameBytes(afterGet, payload), throwingSnapshot: throwingStore.snapshot(), seedSnapshot: seedStore.snapshot(), tree: fakeTreeSummary(root), traceEvents };
  });
}

async function runDuplicateAbortDuringInspectionCase() {
  const payload = payloadOf('duplicate-abort-during-inspection');
  const prefix = `browserrt/${REVISION}/fake-owned-rollback-duplicate-abort`;
  let controller = null;
  let abortNextDuplicateFileLookup = false;
  const hooks = {
    async onGetFileHandle({ name, options }) {
      if (abortNextDuplicateFileLookup && controller && options?.create === false && String(name).endsWith('.blk')) {
        abortNextDuplicateFileLookup = false;
        controller.abort('duplicate-inspection-abort');
      }
    }
  };
  return await withFakeNavigator(async (root) => {
    const seedStore = createOpfsAsyncBlockStore({ name: `${REVISION}-owned-rollback-abort-seed`, prefix });
    const first = await seedStore.put(payload, { label: 'seed-valid-block-for-abort' });
    controller = new AbortController();
    abortNextDuplicateFileLookup = true;
    const abortingStore = createOpfsAsyncBlockStore({ name: `${REVISION}-owned-rollback-duplicate-abort`, prefix });
    const duplicateAbort = await capture('duplicate-put-abort-during-inspection-must-not-delete-existing-block', () => abortingStore.put(payload, { label: 'duplicate-abort-during-inspection' }, { signal: controller.signal }));
    const afterVerify = await seedStore.verify(first.ref);
    const afterGet = await seedStore.get(first.ref);
    return { first, duplicateAbort, afterVerify, bytesPreserved: sameBytes(afterGet, payload), abortingSnapshot: abortingStore.snapshot(), seedSnapshot: seedStore.snapshot(), tree: fakeTreeSummary(root) };
  }, { hooks });
}

async function runOwnedFailedWriteRollbackCase() {
  const payload = payloadOf('owned-write-failure-rollback');
  const prefix = `browserrt/${REVISION}/fake-owned-rollback-owned-failure`;
  let failClose = true;
  const trace = new TraceLog();
  const hooks = {
    async onBeforeClose() {
      if (failClose) {
        failClose = false;
        throw new Error('intentional fake close failure after final file creation');
      }
    }
  };
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-owned-rollback-owned-write-failure`, prefix, trace });
    const failedPut = await capture('owned-write-failure-still-rolls-back-created-final-block', () => store.put(payload, { label: 'owned-write-failure' }));
    return { failedPut, snapshot: store.snapshot(), tree: fakeTreeSummary(root), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks });
}

export async function runProbe() {
  const started = performance.now();
  const duplicateTraceFailure = await runDuplicateTraceFailureCase();
  const duplicateAbortDuringInspection = await runDuplicateAbortDuringInspectionCase();
  const ownedFailedWriteRollback = await runOwnedFailedWriteRollbackCase();

  assert.equal(duplicateTraceFailure.beforeVerify.ok, true, 'seeded duplicate block should verify before duplicate failure');
  assert.equal(duplicateTraceFailure.duplicateFailure.ok, false, 'intentional trace failure must reject the duplicate put');
  assert.equal(duplicateTraceFailure.duplicateFailure.error.code, 'BRT_OPFS_OPERATION_FAILED');
  assert.equal(duplicateTraceFailure.duplicateFailure.error.detail.rollback?.attempted, false, 'duplicate failure must not attempt final-block rollback');
  assert.equal(duplicateTraceFailure.duplicateFailure.error.detail.rollback?.skipped, true, 'duplicate failure must record rollback skip');
  assert.equal(duplicateTraceFailure.duplicateFailure.error.detail.rollback?.reason, 'pre-existing-duplicate-block-not-owned-by-put');
  assert.equal(duplicateTraceFailure.afterVerify.ok, true, 'valid pre-existing block must still verify after duplicate failure');
  assert.equal(duplicateTraceFailure.bytesPreserved, true, 'valid pre-existing block bytes must be preserved after duplicate failure');
  assert.equal(duplicateTraceFailure.tree.fileCount, 1, 'duplicate failure should leave exactly the seeded block');
  assert.equal(duplicateTraceFailure.throwingSnapshot.stats.rollbackOwnershipSkips, 1);
  assert.equal(duplicateTraceFailure.throwingSnapshot.stats.rollbackAttempts, 0);
  assert.ok(duplicateTraceFailure.traceEvents.some((row) => row.kind === 'storage:opfs-block-put-rollback-skipped'));

  assert.equal(duplicateAbortDuringInspection.duplicateAbort.ok, false, 'duplicate inspection abort must reject');
  assert.equal(duplicateAbortDuringInspection.duplicateAbort.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(duplicateAbortDuringInspection.duplicateAbort.error.detail.rollback?.attempted, false, 'duplicate abort must not attempt final-block rollback');
  assert.equal(duplicateAbortDuringInspection.duplicateAbort.error.detail.rollback?.skipped, true, 'duplicate abort must record rollback skip');
  assert.equal(duplicateAbortDuringInspection.afterVerify.ok, true, 'valid block must verify after duplicate inspection abort');
  assert.equal(duplicateAbortDuringInspection.bytesPreserved, true, 'valid block bytes must remain after duplicate inspection abort');
  assert.equal(duplicateAbortDuringInspection.tree.fileCount, 1);
  assert.equal(duplicateAbortDuringInspection.abortingSnapshot.stats.rollbackOwnershipSkips, 1);
  assert.equal(duplicateAbortDuringInspection.abortingSnapshot.stats.rollbackAttempts, 0);

  assert.equal(ownedFailedWriteRollback.failedPut.ok, false, 'owned failed write must reject');
  assert.equal(ownedFailedWriteRollback.failedPut.error.detail.rollback?.attempted, true, 'owned final-file creation failure must still attempt rollback');
  assert.equal(ownedFailedWriteRollback.failedPut.error.detail.rollback?.deleted, true, 'owned failed write should delete the created final block');
  assert.equal(ownedFailedWriteRollback.snapshot.stats.rollbackAttempts, 1);
  assert.equal(ownedFailedWriteRollback.snapshot.stats.rollbackDeletes, 1);
  assert.equal(ownedFailedWriteRollback.snapshot.stats.rollbackOwnershipSkips, 0);
  assert.equal(ownedFailedWriteRollback.tree.fileCount, 0, 'owned failed write rollback should leave no block files');
  assert.ok(ownedFailedWriteRollback.traceKinds.includes('storage:opfs-block-put-rollback'));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-owned-rollback-guard-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that OpfsAsyncBlockStore failed-put rollback is ownership-aware: late errors/aborts while handling an already-valid duplicate block do not delete pre-existing content, while failures after this put creates the final file still best-effort roll back that owned file.',
    observations: { duplicateTraceFailure, duplicateAbortDuringInspection, ownedFailedWriteRollback },
    claimsChecked: [
      'duplicate put failure after duplicate classification skips final-block rollback and preserves the existing valid block',
      'duplicate put abort during existing-block inspection skips final-block rollback and preserves the existing valid block',
      'failed writes after this put creates the final block still attempt rollback and delete the owned partial/final file',
      'rollback skip is visible in provider stats and trace as rollbackOwnershipSkips / storage:opfs-block-put-rollback-skipped'
    ],
    nonClaims: [
      'Fake-OPFS release proof only; the browser companion proof supplies real OPFS evidence for the duplicate path.',
      'Ownership-aware rollback is a local provider guard, not cross-tab atomicity, fsync durability, crash safety, eviction survival, quota guarantee, or production-readiness evidence.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-owned-rollback-guard-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_owned_rollback_guard_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
