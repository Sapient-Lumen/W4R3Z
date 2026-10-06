#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-WRITE-BUDGET-GUARD-PROBE.json`;
const RELEASE_TASK = 'opfs:block-store-write-budget-guard-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

async function capture(label, fn) {
  try { return { label, ok: true, value: await fn(), error: null }; }
  catch (error) { return { label, ok: false, value: null, error: captureError(error) }; }
}

function payloadOf(bytes, seed = 17) {
  const out = new Uint8Array(bytes);
  for (let i = 0; i < out.length; i += 1) out[i] = (seed + i * 31 + (i >>> 3)) & 255;
  out.set(new TextEncoder().encode(`BrowserRT ${REVISION} OPFS write budget guard proof`));
  return out;
}

async function runReserveRejectCase() {
  const trace = new TraceLog();
  const payload = payloadOf(4096, 11);
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-fake-opfs-budget-reserve-reject`, prefix: `browserrt/${REVISION}/fake-opfs-budget-reserve-reject`, trace, writeBudgetGuard: { minFreeBytes: 20_000, requireEstimate: true } });
    const rejected = await capture('reserve-budget-reject-before-open', () => store.put(payload, { label: 'reserve-budget-reject-before-open' }));
    return { rejected, snapshot: store.snapshot(), tree: fakeTreeSummary(root), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: { quota: 24_000, usage: 1_000, usageDetails: { fake: true, case: 'reserve-reject' } } });
}

async function runRatioRejectCase() {
  const trace = new TraceLog();
  const payload = payloadOf(2_048, 23);
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-fake-opfs-budget-ratio-reject`, prefix: `browserrt/${REVISION}/fake-opfs-budget-ratio-reject`, trace });
    const rejected = await capture('per-put-ratio-budget-reject-before-open', () => store.put(payload, { label: 'per-put-ratio-budget-reject-before-open' }, { writeBudgetGuard: { maxUsageRatio: 0.75, requireEstimate: true } }));
    return { rejected, snapshot: store.snapshot(), tree: fakeTreeSummary(root), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: { quota: 10_000, usage: 6_000, usageDetails: { fake: true, case: 'ratio-reject' } } });
}

async function runEstimateUnavailableRequiredCase() {
  const trace = new TraceLog();
  const payload = payloadOf(1024, 37);
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-fake-opfs-budget-estimate-required`, prefix: `browserrt/${REVISION}/fake-opfs-budget-estimate-required`, trace, writeBudgetGuard: { minFreeBytes: 1, requireEstimate: true } });
    const rejected = await capture('required-estimate-unavailable-before-open', () => store.put(payload, { label: 'required-estimate-unavailable-before-open' }));
    return { rejected, snapshot: store.snapshot(), tree: fakeTreeSummary(root), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: false });
}

async function runEstimateUnavailableOptionalCase() {
  const trace = new TraceLog();
  const payload = payloadOf(1536, 41);
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-fake-opfs-budget-estimate-optional`, prefix: `browserrt/${REVISION}/fake-opfs-budget-estimate-optional`, trace, writeBudgetGuard: { minFreeBytes: 1, requireEstimate: false } });
    const put = await store.put(payload, { label: 'optional-estimate-unavailable-continues' });
    const verify = await store.verify(put.ref);
    return { put, verify, snapshot: store.snapshot(), tree: fakeTreeSummary(root), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: false });
}

async function runBudgetPassCase() {
  const trace = new TraceLog();
  const payload = payloadOf(4096, 53);
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-fake-opfs-budget-pass`, prefix: `browserrt/${REVISION}/fake-opfs-budget-pass`, trace, writeBudgetGuard: { minFreeBytes: 1_000, maxUsageRatio: 0.9, requireEstimate: true } });
    const put = await store.put(payload, { label: 'budget-pass-put' });
    const verify = await store.verify(put.ref);
    const estimateAfter = await store.estimate();
    return { put, verify, estimateAfter, snapshot: store.snapshot(), tree: fakeTreeSummary(root), traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { estimate: (root) => ({ quota: 100_000, usage: fakeTreeSummary(root).byteCount, usageDetails: { fake: true, dynamic: true } }) });
}

async function runInvalidGuardCase() {
  return await capture('invalid-write-budget-guard', async () => createOpfsAsyncBlockStore({ writeBudgetGuard: { maxUsageRatio: 1.5 } }));
}

export async function runProbe() {
  const started = performance.now();
  const reserveReject = await runReserveRejectCase();
  const ratioReject = await runRatioRejectCase();
  const estimateRequired = await runEstimateUnavailableRequiredCase();
  const estimateOptional = await runEstimateUnavailableOptionalCase();
  const budgetPass = await runBudgetPassCase();
  const invalidGuard = await runInvalidGuardCase();

  assert.equal(reserveReject.rejected.ok, false, 'reserve budget case must reject');
  assert.equal(reserveReject.rejected.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.equal(reserveReject.snapshot.opened, false, 'reserve budget reject must not open OPFS');
  assert.equal(reserveReject.tree.fileCount, 0, 'reserve budget reject must not create files');
  assert.equal(reserveReject.tree.dirCount, 0, 'reserve budget reject must not create directories');
  assert.equal(reserveReject.snapshot.stats.writeBudgetChecks, 1);
  assert.equal(reserveReject.snapshot.stats.writeBudgetRejects, 1);
  assert.ok(reserveReject.rejected.error.detail.reasons.includes('min-free-bytes'));
  assert.ok(reserveReject.traceKinds.includes('storage:opfs-block-write-budget-check'));
  assert.ok(reserveReject.traceKinds.includes('storage:opfs-block-write-budget-reject'));
  assert.equal(reserveReject.traceKinds.includes('storage:opfs-blockstore-open'), false, 'budget reject should happen before OPFS open');

  assert.equal(ratioReject.rejected.ok, false, 'ratio budget case must reject');
  assert.equal(ratioReject.rejected.error.code, 'BRT_OPFS_WRITE_BUDGET_EXCEEDED');
  assert.ok(ratioReject.rejected.error.detail.reasons.includes('max-usage-ratio'));
  assert.equal(ratioReject.snapshot.opened, false, 'per-put ratio reject must not open OPFS');
  assert.equal(ratioReject.tree.fileCount, 0);

  assert.equal(estimateRequired.rejected.ok, false, 'required estimate unavailable case must reject');
  assert.equal(estimateRequired.rejected.error.code, 'BRT_OPFS_ESTIMATE_UNAVAILABLE');
  assert.equal(estimateRequired.snapshot.opened, false, 'required estimate reject must not open OPFS');
  assert.equal(estimateRequired.snapshot.stats.writeBudgetEstimateUnavailable, 1);
  assert.ok(estimateRequired.traceKinds.includes('storage:opfs-block-write-budget-estimate-unavailable'));

  assert.equal(estimateOptional.verify.ok, true, 'optional estimate unavailable case should still put and verify');
  assert.equal(estimateOptional.snapshot.opened, true, 'optional estimate unavailable case should open for valid put');
  assert.equal(estimateOptional.snapshot.stats.writeBudgetEstimateUnavailable, 1);
  assert.ok(estimateOptional.traceKinds.includes('storage:opfs-block-write-budget-estimate-unavailable'));
  assert.ok(estimateOptional.traceKinds.includes('storage:opfs-block-put'));

  assert.equal(budgetPass.verify.ok, true, 'passing budget guard should allow put/verify');
  assert.equal(budgetPass.snapshot.stats.writeBudgetChecks, 1);
  assert.equal(budgetPass.snapshot.stats.writeBudgetRejects, 0);
  assert.ok(budgetPass.traceKinds.includes('storage:opfs-block-write-budget-check'));
  assert.ok(budgetPass.traceKinds.includes('storage:opfs-block-put'));

  assert.equal(invalidGuard.ok, false, 'invalid budget guard config must reject');
  assert.equal(invalidGuard.error.code, 'BRT_OPFS_WRITE_BUDGET_INVALID');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-write-budget-guard-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that the opt-in OpfsAsyncBlockStore writeBudgetGuard uses StorageManager.estimate()-shaped quota/usage data to reject writes before OPFS open/file mutation when reserve or projected-usage thresholds would be violated, while still allowing callers to treat missing estimate as optional.',
    observations: { reserveReject, ratioReject, estimateRequired, estimateOptional, budgetPass, invalidGuard },
    claimsChecked: [
      'constructor writeBudgetGuard minFreeBytes rejects before OPFS open or file/directory creation',
      'per-put writeBudgetGuard maxUsageRatio rejects before OPFS open or file creation',
      'requireEstimate true rejects when StorageManager.estimate is unavailable',
      'requireEstimate false records unavailable estimate but allows the write to proceed',
      'passing budget guard allows put/verify and emits budget-check telemetry',
      'invalid guard thresholds fail closed with BRT_OPFS_WRITE_BUDGET_INVALID'
    ],
    nonClaims: [
      'Fake StorageManager.estimate release proof only; managed Chromium proof covers the browser realm.',
      'Storage estimates are approximate and not a reservation, fsync, eviction-prevention, crash-recovery, durability, or production-capacity guarantee.',
      'This guard is conservative and opt-in; it does not prove organic browser eviction behavior or cross-browser quota policy.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-write-budget-guard-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: captureError(error) };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_write_budget_guard_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
