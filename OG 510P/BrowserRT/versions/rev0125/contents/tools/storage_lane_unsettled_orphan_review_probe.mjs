#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-unsettled-orphan-review-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-UNSETTLED-ORPHAN-REVIEW-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function bytes(v) { return typeof v === 'string' ? new TextEncoder().encode(v) : v instanceof Uint8Array ? v : new Uint8Array(v); }
function makeScheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ name = 'unsettled-orphan-memory-store' } = {}) {
  const records = new Map();
  return {
    name,
    provider: 'memory:unsettled-orphan-review',
    async put(payload, fields = {}) {
      const b = bytes(payload);
      const hash = await digestBytesHex(b);
      const digest = `sha256:${hash}`;
      records.set(digest, b);
      const result = { ref: { id: `block:${digest}`, digest, hash, backend: this.provider, bytes: b.byteLength }, digest, hash, bytes: b.byteLength, duplicate: false, label: fields.label || null };
      if (fields.label === 'orphaned-timeout-put') return await new Promise(() => {});
      return result;
    },
    async get(ref) { const d = typeof ref === 'string' ? ref : ref?.digest; if (!records.has(d)) throw new Error(`missing block ${d}`); return new Uint8Array(records.get(d)); },
    async has(ref) { const d = typeof ref === 'string' ? ref : ref?.digest; return records.has(d); },
    async verify(ref) { const d = typeof ref === 'string' ? ref : ref?.digest; const b = records.get(d); return { ok: Boolean(b), present: Boolean(b), digest: d, bytes: b?.byteLength ?? 0 }; },
    async delete(ref) { const d = typeof ref === 'string' ? ref : ref?.digest; return records.delete(d); },
    async estimate() { return { usage: [...records.values()].reduce((sum, b) => sum + b.byteLength, 0), quota: null, usageDetails: { records: records.size } }; },
    async cleanupForTest() { records.clear(); return true; },
    async waitForSettled() { return { ok: true, reason: 'memory-store-settled', last: { heldCount: 0, pendingCount: 0, available: true } }; },
    snapshot() { return { name: this.name, provider: this.provider, blockCount: records.size, digests: [...records.keys()].sort() }; }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore();
  const source = createBlockStoreLaneAdapter({ label: `${REVISION}-unsettled-orphan-source`, store, scheduler: makeScheduler(`${REVISION}-unsettled-orphan-source-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const payload = `BrowserRT ${REVISION} unsettled orphan timeout payload`;
  const hash = await digestBytesHex(bytes(payload));
  const digest = `sha256:${hash}`;
  const scheduled = source.schedulePut(payload, { id: 'unsettled-orphan-put', priority: 'user-visible', label: 'orphaned-timeout-put', operationTimeoutMs: 180 });
  const drain = await source.drain({ maxSteps: 1 });
  const timeoutResult = drain.results[0];
  const committedBeforeImport = await store.has({ digest });
  const exported = source.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'export-unsettled-orphan-for-handoff' });

  const fresh = createBlockStoreLaneAdapter({ label: `${REVISION}-unsettled-orphan-fresh`, store, scheduler: makeScheduler(`${REVISION}-unsettled-orphan-fresh-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const imported = fresh.importTimedOutOperationQuarantine(exported, { lane: 'storage', reason: 'import-unsettled-orphan-quarantine', markUnhealthy: false });
  const laneAfterImport = fresh.snapshot().executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const blockedUnsettled = await fresh.recoverWhenStoreSettled({ timeoutMs: 45, intervalMs: 5, reason: 'must-block-imported-unsettled-orphan' });
  const unsafeFinalize = fresh.finalizeUnsettledTimedOutOperations({ lane: 'storage', opId: 'unsettled-orphan-put', reason: 'unsafe-finalize-without-review' });
  const review = fresh.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'unsettled', opIds: ['unsettled-orphan-put'], reviewer: 'release-probe', reviewToken: `${REVISION}-unsettled-orphan-finalize-review`, reason: 'review-imported-unsettled-orphan' });
  const staleReview = { ...review, reviewFingerprint: 'brt-qfp-v1:0000000000000000', quarantineFingerprint: 'brt-qfp-v1:0000000000000000' };
  const staleFinalize = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest: staleReview, requireReviewFingerprint: true, reason: 'stale-review-must-not-finalize' });
  const scopeOverrideClear = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest: review, allowLaneWide: true, requireReviewFingerprint: true, reason: 'reject-unsettled-orphan-review-scope-override' });
  const tokenOverrideClear = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest: review, reviewToken: 'copied-token', requireReviewFingerprint: true, reason: 'reject-unsettled-orphan-review-token-override' });
  const fingerprintOverrideClear = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest: review, reviewFingerprint: review.reviewFingerprint, requireReviewFingerprint: true, reason: 'reject-unsettled-orphan-review-fingerprint-override' });
  const staleCountManifest = { ...review, counts: { ...review.counts, total: review.counts.total + 1 } };
  const countMismatchClear = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest: staleCountManifest, requireReviewFingerprint: true, reason: 'reject-unsettled-orphan-review-count-mismatch' });
  const finalized = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest: review, requireReviewFingerprint: true, reason: 'reviewed-finalize-imported-unsettled-orphan' });
  const blockedLateFailure = await fresh.recoverWhenStoreSettled({ timeoutMs: 45, intervalMs: 5, reason: 'must-block-finalized-orphan-late-failure' });
  const oldReviewClear = fresh.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'failed', opIds: ['unsettled-orphan-put'], reviewed: true, reviewToken: review.reviewToken, reviewFingerprint: review.reviewFingerprint, requireReviewFingerprint: true, reason: 'old-unsettled-review-must-not-clear-finalized-failure' });
  const failureReview = fresh.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opIds: ['unsettled-orphan-put'], reviewer: 'release-probe', reviewToken: `${REVISION}-unsettled-orphan-failure-clear-review`, reason: 'review-finalized-orphan-failure' });
  const cleared = fresh.clearTimedOutOperationQuarantine({ reviewManifest: failureReview, requireReviewFingerprint: true, reason: 'reviewed-clear-finalized-orphan-failure' });
  const recovered = await fresh.recoverWhenStoreSettled({ timeoutMs: 45, intervalMs: 5, reason: 'recover-after-finalized-orphan-review-clear' });
  const recoveryPayload = `BrowserRT ${REVISION} unsettled orphan recovery write`;
  const accepted = fresh.schedulePut(recoveryPayload, { id: 'unsettled-orphan-recovered-put', priority: 'user-visible', label: 'recovered-put' });
  const recoveryDrain = await fresh.drain({ maxSteps: 2 });
  const recoveryResult = recoveryDrain.results.find((row) => row.opId === 'unsettled-orphan-recovered-put') ?? null;
  const recoveryVerify = recoveryResult?.result?.ref ? await store.verify(recoveryResult.result.ref) : null;
  const finalSnapshot = fresh.snapshot();
  const traceKinds = trace.snapshot().map((event) => event.kind);

  assert.equal(scheduled.accepted, true);
  assert.equal(timeoutResult.ok, false);
  assert.equal(timeoutResult.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(committedBeforeImport, true, 'provider may commit before timing out');
  assert.equal(exported.unsettledTimedOutOperationCount ?? exported.counts.unsettled, 1);
  assert.equal(imported.ok, true);
  assert.equal(imported.markUnhealthyForced, true);
  assert.equal(laneAfterImport.healthy, false);
  assert.equal(blockedUnsettled.recovered, false);
  assert.equal(blockedUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(unsafeFinalize.ok, false);
  assert.equal(unsafeFinalize.code, 'timed-out-quarantine-finalize-review-required');
  assert.equal(staleFinalize.ok, false);
  assert.equal(staleFinalize.code, 'timed-out-quarantine-finalize-review-fingerprint-mismatch');
  assert.equal(scopeOverrideClear.ok, false);
  assert.equal(scopeOverrideClear.code, 'timed-out-quarantine-finalize-review-manifest-scope-override');
  assert.equal(tokenOverrideClear.ok, false);
  assert.equal(tokenOverrideClear.code, 'timed-out-quarantine-finalize-review-manifest-scope-override');
  assert.equal(fingerprintOverrideClear.ok, false);
  assert.equal(fingerprintOverrideClear.code, 'timed-out-quarantine-finalize-review-manifest-scope-override');
  assert.equal(countMismatchClear.ok, false);
  assert.equal(countMismatchClear.code, 'timed-out-quarantine-finalize-review-manifest-count-mismatch');
  assert.equal(finalized.ok, true);
  assert.equal(finalized.finalizedCount, 1);
  assert.equal(finalized.unsettledTimedOutOperationCount, 0);
  assert.equal(finalized.failedTimedOutOperationCount, 1);
  assert.equal(finalized.finalized[0].error.code, 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED');
  assert.equal(blockedLateFailure.recovered, false);
  assert.equal(blockedLateFailure.reason, 'timed-out-operation-late-failure');
  assert.equal(oldReviewClear.ok, false);
  assert.equal(oldReviewClear.code, 'timed-out-quarantine-clear-review-fingerprint-mismatch');
  assert.equal(cleared.ok, true);
  assert.equal(cleared.failedClearedCount, 1);
  assert.equal(recovered.recovered, true);
  assert.equal(accepted.accepted, true);
  assert.equal(recoveryResult?.ok, true);
  assert.equal(recoveryVerify?.ok, true);
  assert.ok(traceKinds.includes('storage-lane:timed-out-quarantine-orphans-finalized'));
  assert.ok(traceKinds.includes('storage-lane:timed-out-quarantine-finalize-rejected'));

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-unsettled-orphan-review-proof`, task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    observations: { scheduled, timeoutResult, committedBeforeImport, exported, imported, laneAfterImport, blockedUnsettled, unsafeFinalize, review, staleFinalize, scopeOverrideClear, tokenOverrideClear, fingerprintOverrideClear, countMismatchClear, finalized, blockedLateFailure, oldReviewClear, failureReview, cleared, recovered, recoveryResult, recoveryVerify, finalSnapshot, traceKinds },
    claimsChecked: [
      'imported unsettled timed-out operations force backpressure and block recovery',
      'unsettled timeout orphans require reviewed/fingerprint-bound finalization before recovery can proceed',
      'review manifests are authoritative for unsettled-orphan finalization and reject call-site scope/token/fingerprint overrides and stale counts',
      'finalized orphans become late-failure quarantine and require a fresh bound review before lane recovery'
    ],
    nonClaims: ['Synthetic release-tier proof only; no browser, cancellation, rollback, durability, quota, eviction, or production-readiness claim.']
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-unsettled-orphan-review-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[storage_lane_unsettled_orphan_review_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
