#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore } from '../src/browserrt.mjs';
import { createStorageEstimateRecorder, fakeTreeSummary, withFakeNavigator, writeFakePath } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-WRITE-BUDGET-DUPLICATE-BYPASS-PROBE.json`;
const RELEASE_TASK = 'opfs:block-store-write-budget-duplicate-bypass-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

async function capture(label, fn) {
  try { return { label, ok: true, value: await fn(), error: null }; }
  catch (error) { return { label, ok: false, value: null, error: captureError(error) }; }
}

function payloadOf(bytes, seed = 17, label = 'payload') {
  const out = new Uint8Array(bytes);
  for (let i = 0; i < out.length; i += 1) out[i] = (seed + i * 29 + (i >>> 2)) & 255;
  out.set(new TextEncoder().encode(`BrowserRT ${REVISION} ${label}`));
  return out;
}

function impossibleBudgetRecorder() {
  return createStorageEstimateRecorder(() => ({ quota: 10_000, usage: 9_900, usageDetails: { fake: true, case: 'impossible-budget' } }));
}

async function runVerifiedDuplicateBypassCase() {
  const trace = new TraceLog();
  const payload = payloadOf(2048, 11, 'verified duplicate write budget bypass');
  const estimateRecorder = impossibleBudgetRecorder();
  return await withFakeNavigator(async (root) => {
    const prefix = `browserrt/${REVISION}/fake-opfs-write-budget-duplicate-bypass/verified`;
    const seeder = createOpfsAsyncBlockStore({ name: `${REVISION}-seed-verified-duplicate`, prefix, trace });
    const seedPut = await seeder.put(payload, { label: 'seed-verified-duplicate' });
    const before = fakeTreeSummary(root);
    const guarded = createOpfsAsyncBlockStore({ name: `${REVISION}-budgeted-verified-duplicate`, prefix, trace, writeBudgetGuard: { minFreeBytes: 1_000, maxUsageRatio: 0.5, requireEstimate: true } });
    const duplicate = await guarded.put(payload, { label: 'verified-duplicate-budget-bypass' });
    const readBack = await guarded.get(duplicate.ref);
    const after = fakeTreeSummary(root);
    return { seedPut, duplicate, bytesPreserved: readBack.byteLength === payload.byteLength && readBack.every((x, i) => x === payload[i]), before, after, estimate: estimateRecorder.snapshot(), snapshot: guarded.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: estimateRecorder.estimate });
}

async function runUnverifiedDuplicateBypassCase() {
  const trace = new TraceLog();
  const payload = payloadOf(1536, 23, 'unverified duplicate write budget bypass');
  const estimateRecorder = impossibleBudgetRecorder();
  return await withFakeNavigator(async (root) => {
    const prefix = `browserrt/${REVISION}/fake-opfs-write-budget-duplicate-bypass/unverified`;
    const seeder = createOpfsAsyncBlockStore({ name: `${REVISION}-seed-unverified-duplicate`, prefix, trace });
    const seedPut = await seeder.put(payload, { label: 'seed-unverified-duplicate' });
    const before = fakeTreeSummary(root);
    const guarded = createOpfsAsyncBlockStore({ name: `${REVISION}-budgeted-unverified-duplicate`, prefix, trace, verifyExistingBlocksOnPut: false, writeBudgetGuard: { minFreeBytes: 1_000, maxUsageRatio: 0.5, requireEstimate: true } });
    const duplicate = await guarded.put(payload, { label: 'unverified-duplicate-budget-bypass' });
    const verify = await guarded.verify(duplicate.ref);
    const after = fakeTreeSummary(root);
    return { seedPut, duplicate, verify, before, after, estimate: estimateRecorder.snapshot(), snapshot: guarded.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: estimateRecorder.estimate });
}

async function runNewWriteRejectStillPreMutationCase() {
  const trace = new TraceLog();
  const payload = payloadOf(1024, 37, 'new write budget reject still pre mutation');
  const estimateRecorder = impossibleBudgetRecorder();
  return await withFakeNavigator(async (root) => {
    const prefix = `browserrt/${REVISION}/fake-opfs-write-budget-duplicate-bypass/new-write-reject`;
    const guarded = createOpfsAsyncBlockStore({ name: `${REVISION}-budgeted-new-write-reject`, prefix, trace, writeBudgetGuard: { minFreeBytes: 1_000, maxUsageRatio: 0.5, requireEstimate: true } });
    const rejected = await capture('new-write-budget-reject-after-readonly-dedupe-before-mutation', () => guarded.put(payload, { label: 'new-write-budget-reject-after-readonly-dedupe-before-mutation' }));
    return { rejected, tree: fakeTreeSummary(root), estimate: estimateRecorder.snapshot(), snapshot: guarded.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: estimateRecorder.estimate });
}

async function runCorruptRepairBudgetRejectPreservesFileCase() {
  const trace = new TraceLog();
  const payload = payloadOf(1792, 41, 'corrupt repair budget reject preserves file');
  const corruptBytes = payloadOf(256, 99, 'wrong corrupt bytes');
  const estimateRecorder = impossibleBudgetRecorder();
  return await withFakeNavigator(async (root) => {
    const prefix = `browserrt/${REVISION}/fake-opfs-write-budget-duplicate-bypass/corrupt-repair`;
    const seeder = createOpfsAsyncBlockStore({ name: `${REVISION}-seed-corrupt-budget-repair`, prefix, trace });
    const seedPut = await seeder.put(payload, { label: 'seed-corrupt-budget-repair' });
    await writeFakePath(root, seedPut.path, corruptBytes);
    const before = fakeTreeSummary(root);
    const guarded = createOpfsAsyncBlockStore({ name: `${REVISION}-budgeted-corrupt-repair`, prefix, trace, writeBudgetGuard: { minFreeBytes: 1_000, maxUsageRatio: 0.5, requireEstimate: true } });
    const rejected = await capture('corrupt-repair-budget-reject-preserves-corrupt-file', () => guarded.put(payload, { label: 'corrupt-repair-budget-reject-preserves-corrupt-file' }));
    const verifyAfterReject = await guarded.verify(seedPut.ref);
    const after = fakeTreeSummary(root);
    return { seedPut, before, rejected, verifyAfterReject, after, estimate: estimateRecorder.snapshot(), snapshot: guarded.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: estimateRecorder.estimate });
}

async function runBudgetPassStillWritesCase() {
  const trace = new TraceLog();
  const payload = payloadOf(1408, 53, 'write budget duplicate bypass pass case');
  const estimateRecorder = createStorageEstimateRecorder((root, before) => ({ quota: 100_000, usage: before.byteCount, usageDetails: { fake: true, case: 'budget-pass' } }));
  return await withFakeNavigator(async (root) => {
    const prefix = `browserrt/${REVISION}/fake-opfs-write-budget-duplicate-bypass/pass`;
    const guarded = createOpfsAsyncBlockStore({ name: `${REVISION}-budget-pass-after-dedupe`, prefix, trace, writeBudgetGuard: { minFreeBytes: 1_000, maxUsageRatio: 0.9, requireEstimate: true } });
    const put = await guarded.put(payload, { label: 'budget-pass-after-readonly-dedupe' });
    const verify = await guarded.verify(put.ref);
    return { put, verify, tree: fakeTreeSummary(root), estimate: estimateRecorder.snapshot(), snapshot: guarded.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: estimateRecorder.estimate });
}

export async function runProbe() {
  const started = performance.now();
  const verifiedDuplicate = await runVerifiedDuplicateBypassCase();
  const unverifiedDuplicate = await runUnverifiedDuplicateBypassCase();
  const newWriteReject = await runNewWriteRejectStillPreMutationCase();
  const corruptRepairReject = await runCorruptRepairBudgetRejectPreservesFileCase();
  const budgetPass = await runBudgetPassStillWritesCase();

  assert.equal(verifiedDuplicate.duplicate.duplicate, true, 'verified duplicate put should remain duplicate');
  assert.equal(verifiedDuplicate.duplicate.budget.bypassed, true, 'verified duplicate should bypass budget');
  assert.equal(verifiedDuplicate.bytesPreserved, true, 'verified duplicate bytes should read back');
  assert.deepEqual(verifiedDuplicate.after, verifiedDuplicate.before, 'verified duplicate budget bypass must not mutate fake OPFS tree');
  assert.equal(verifiedDuplicate.estimate.callCount, 0, 'verified duplicate bypass should not call storage.estimate');
  assert.equal(verifiedDuplicate.snapshot.stats.writeBudgetDuplicateBypasses, 1);
  assert.equal(verifiedDuplicate.snapshot.stats.writeBudgetChecks, 0);
  assert.ok(verifiedDuplicate.traceKinds.includes('storage:opfs-block-write-budget-duplicate-bypass'));

  assert.equal(unverifiedDuplicate.duplicate.duplicate, true, 'unverified duplicate put should still be duplicate by file presence');
  assert.equal(unverifiedDuplicate.duplicate.budget.bypassed, true, 'unverified duplicate should bypass budget');
  assert.equal(unverifiedDuplicate.verify.ok, true, 'seeded duplicate should still verify');
  assert.deepEqual(unverifiedDuplicate.after, unverifiedDuplicate.before, 'unverified duplicate budget bypass must not mutate fake OPFS tree');
  assert.equal(unverifiedDuplicate.estimate.callCount, 0, 'unverified duplicate bypass should not call storage.estimate');
  assert.equal(unverifiedDuplicate.snapshot.stats.writeBudgetDuplicateBypasses, 1);

  assert.equal(newWriteReject.rejected.ok, false, 'new write should still reject under impossible budget');
  assert.equal(newWriteReject.rejected.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.equal(newWriteReject.tree.fileCount, 0, 'new write reject must not create a block file');
  assert.equal(newWriteReject.tree.dirCount, 0, 'new write reject must not create prefix/bucket directories');
  assert.equal(newWriteReject.estimate.callCount, 1, 'new write reject should call storage.estimate once');
  assert.equal(newWriteReject.snapshot.opened, false, 'new write budget reject should not open mutable OPFS prefix');
  assert.equal(newWriteReject.snapshot.stats.writeBudgetRejects, 1);
  assert.ok(newWriteReject.traceKinds.includes('storage:opfs-block-write-budget-reject'));

  assert.equal(corruptRepairReject.rejected.ok, false, 'corrupt repair should reject under impossible budget');
  assert.equal(corruptRepairReject.rejected.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.equal(corruptRepairReject.verifyAfterReject.present, true, 'corrupt file should remain present after budget rejection');
  assert.equal(corruptRepairReject.verifyAfterReject.ok, false, 'corrupt file should not be silently repaired after budget rejection');
  assert.equal(corruptRepairReject.after.fileCount, corruptRepairReject.before.fileCount, 'corrupt repair budget reject must not delete the existing file');
  assert.equal(corruptRepairReject.estimate.callCount, 1, 'corrupt repair budget reject should call storage.estimate once');
  assert.equal(corruptRepairReject.snapshot.stats.corruptBlocksDetected >= 1, true, 'corrupt file should be detected');
  assert.equal(corruptRepairReject.snapshot.stats.corruptDeletes, 0, 'budget rejection must happen before corrupt repair delete');
  assert.equal(corruptRepairReject.snapshot.stats.corruptRepairs, 0, 'budget rejection must happen before corrupt repair counter increments');

  assert.equal(budgetPass.verify.ok, true, 'passing budget should still write and verify');
  assert.equal(budgetPass.estimate.callCount, 1, 'passing new write should call estimate once');
  assert.equal(budgetPass.snapshot.stats.writeBudgetChecks, 1);
  assert.equal(budgetPass.snapshot.stats.writeBudgetRejects, 0);
  assert.equal(budgetPass.tree.fileCount, 1, 'passing budget should create one block file');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-write-budget-duplicate-bypass-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that OpfsAsyncBlockStore writeBudgetGuard is duplicate-aware: verified/idempotent duplicate puts bypass quota estimates and do not mutate OPFS, while new writes and corrupt-block repairs still reject before provider mutation under impossible budgets.',
    observations: { verifiedDuplicate, unverifiedDuplicate, newWriteReject, corruptRepairReject, budgetPass },
    claimsChecked: [
      'verified duplicate put bypasses write budget without calling navigator.storage.estimate',
      'file-presence duplicate put with verifyExistingBlocksOnPut false also bypasses write budget without mutation',
      'new non-duplicate writes still reject before creating prefix, bucket, or block files when budget is exceeded',
      'corrupt-block repair checks budget before deleting the corrupt existing block',
      'passing budget guard still allows a new block write and verification'
    ],
    nonClaims: [
      'This is still an estimate-based preflight, not a quota reservation or eviction guarantee.',
      'Fake OPFS release proof only; managed browser proof supplies the focused Chromium check, and neither proof claims cross-browser behavior, fsync durability, crash recovery, multi-tab atomicity, or production readiness.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-write-budget-duplicate-bypass-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_write_budget_duplicate_bypass_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
