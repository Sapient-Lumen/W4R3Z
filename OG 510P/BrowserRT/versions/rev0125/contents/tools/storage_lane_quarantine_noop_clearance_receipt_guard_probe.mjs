#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import {
  REVISION,
  VERSION,
  TraceLog,
  createCrossLaneScheduler,
  createBlockStoreLaneAdapter,
  digestBytesHex,
  createTimedOutOperationQuarantineClearanceReceipt,
  validateTimedOutOperationQuarantineClearanceReceipt
} from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-noop-clearance-receipt-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-NOOP-CLEARANCE-RECEIPT-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function bytes(value) { return value instanceof Uint8Array ? new Uint8Array(value) : new TextEncoder().encode(String(value)); }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  return {
    name: 'synthetic-noop-clearance-receipt-guard-store', provider: 'synthetic-noop-clearance-receipt-guard-provider-v0',
    async put(payload, fields = {}) { const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; records.set(digest, body); trace?.emit('synthetic-noop-clearance-receipt-guard:put', { digest, bytes: body.byteLength, label: fields.label ?? null }); const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength }); return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null }); },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing block ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); return Object.freeze({ ok: Boolean(row), present: Boolean(row), digest, bytes: row?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: [...records.values()].reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size }); }
  };
}
function importedLedger() {
  return Object.freeze({
    schema: 'brt.storageLane.timedOutOperationQuarantine.v1',
    lane: 'storage',
    reason: 'synthetic-imported-quarantine-for-noop-clearance-receipt-guard',
    counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }),
    unsettledTimedOutOperations: Object.freeze([]),
    successfulTimedOutOperations: Object.freeze([Object.freeze({ opId: 'noop-guard-success-row', kind: 'put', lane: 'storage', timeoutMs: 100, timedOutAtMs: 1000, settledAtMs: 1100, result: Object.freeze({ disposition: 'stored', digest: 'sha256:noop-guard-success' }) })]),
    failedTimedOutOperations: Object.freeze([Object.freeze({ opId: 'noop-guard-failure-row', kind: 'put', lane: 'storage', timeoutMs: 100, timedOutAtMs: 2000, settledAtMs: 2100, error: Object.freeze({ name: 'SyntheticLateFailure', code: 'BRT_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_SYNTHETIC_LATE_FAILURE', message: 'synthetic late failure row' }) })])
  });
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-noop-clearance-receipt-guard`, store, scheduler: scheduler(`${REVISION}-noop-clearance-receipt-guard-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const importResult = adapter.importTimedOutOperationQuarantine(importedLedger(), { lane: 'storage', reason: 'release-import-noop-clearance-receipt-guard', markUnhealthy: false });
  assert.equal(importResult.ok, true); assert.equal(importResult.markUnhealthyForced, true);
  const quarantine = adapter.timedOutOperationQuarantine('storage');
  assert.equal(quarantine.totalCount, 2); assert.equal(quarantine.successfulTimedOutOperationCount, 1); assert.equal(quarantine.failedTimedOutOperationCount, 1);
  const staleLedger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'release-export-before-noop-clear-attempt' });
  const missingScopeReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', opIds: ['definitely-missing-op-id'], reviewer: 'rev0080-release-probe', reviewToken: 'rev0080-noop-clear-token', reason: 'review-with-nonmatching-scope' });
  const noopClear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: missingScopeReview, requireReviewFingerprint: true, reason: 'attempt-noop-clearance-receipt-guard' });
  assert.equal(noopClear.ok, false); assert.equal(noopClear.code, 'timed-out-quarantine-clear-noop'); assert.equal(noopClear.disposition, 'rejected-noop-clear');
  assert.equal(adapter.timedOutOperationQuarantine('storage').totalCount, 2);
  let zeroReceiptError = null;
  try { createTimedOutOperationQuarantineClearanceReceipt({ ok: true, lane: 'storage', reviewToken: 'fake-zero', reviewFingerprint: quarantine.reviewFingerprint, requiredReviewFingerprint: quarantine.reviewFingerprint, clearedCount: 0, successfulClearedCount: 0, failedClearedCount: 0, categories: ['successful','failed'], opIds: ['definitely-missing-op-id'], cleared: { successful: [], failed: [] }, quarantine }); }
  catch (error) { zeroReceiptError = { name: error.name, message: error.message }; }
  assert.match(zeroReceiptError?.message || '', /at least one cleared/);
  const zeroReceiptValidation = validateTimedOutOperationQuarantineClearanceReceipt({ schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.v1', createdAtMs: Date.now(), lane: 'storage', reviewToken: 'fake-zero', reviewFingerprint: quarantine.reviewFingerprint, requiredReviewFingerprint: quarantine.reviewFingerprint, preClearanceFingerprint: quarantine.reviewFingerprint, postClearanceFingerprint: quarantine.reviewFingerprint, categories: ['successful','failed'], opIds: [], allowLaneWide: true, clearedCount: 0, successfulClearedCount: 0, failedClearedCount: 0, counts: { total: 0, successful: 0, failed: 0 }, cleared: { successful: [], failed: [] }, receiptFingerprint: 'intentionally-wrong' });
  assert.equal(zeroReceiptValidation.ok, false); assert.ok(zeroReceiptValidation.errors.some((x) => x.includes('at least one')));
  const goodReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0080-release-probe', reviewToken: 'rev0080-good-clear-token', reason: 'review-all-for-noop-clearance-receipt-guard' });
  const goodClear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: goodReview, requireReviewFingerprint: true, reason: 'clear-after-noop-guard' });
  assert.equal(goodClear.ok, true); assert.equal(goodClear.clearedCount, 2);
  const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(goodClear, { reviewer: 'rev0080-release-probe', label: 'noop-clearance-receipt-guard-good-receipt' });
  const validation = validateTimedOutOperationQuarantineClearanceReceipt(receipt);
  assert.equal(validation.ok, true);
  const replay = adapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'stale-replay-after-good-clear', markUnhealthy: false });
  assert.equal(replay.ok, false); assert.equal(replay.disposition, 'rejected-cleared-quarantine-replay');
  const recovery = adapter.markHealthy('storage', 'release-noop-clearance-receipt-guard-recovered');
  assert.equal(recovery.healthy, true);
  const scheduled = adapter.schedulePut(`${REVISION}:noop-clearance-receipt-guard-after-recovery`, { id: 'noop-clearance-receipt-guard-after-recovery', label: 'noop-clearance-receipt-guard-after-recovery' });
  assert.equal(scheduled.accepted, true);
  const drain = await adapter.drain({ maxSteps: 3 });
  const writeResult = drain.results.find((row) => row.opId === 'noop-clearance-receipt-guard-after-recovery');
  assert.equal(writeResult?.ok, true);
  const verify = await store.verify(writeResult.result.ref);
  assert.equal(verify.ok, true);
  const traceKinds = trace.kinds();
  for (const kind of ['storage-lane:timed-out-quarantine-clear-rejected', 'block-store-lane:quarantine-clearance-receipt-created', 'storage-lane:timed-out-quarantine-import-replay-rejected']) assert.ok(traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-noop-clearance-receipt-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that timeout-quarantine clearance cannot mint a receipt from a reviewed scope that clears zero rows, while normal reviewed clearing and stale-ledger replay rejection still work.', observations: { importResult, quarantine, staleLedger, missingScopeReview, noopClear, zeroReceiptError, zeroReceiptValidation, goodReview, goodClear, receipt, validation, replay, recovery, scheduled, writeResult, verify, snapshot: adapter.snapshot(), traceKinds }, claimsChecked: ['zero-row reviewed timeout-quarantine clear rejects as timed-out-quarantine-clear-noop', 'clearance receipt creation and validation reject zero-cleared receipts', 'valid reviewed/scoped clear still produces a replay-guarding receipt', 'lane can explicitly recover and later writes verify'], nonClaims: ['Release-light synthetic provider only; no browser OPFS/Web Locks claim.', 'No cryptographic attestation, provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-noop-clearance-receipt-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed no-op clearance receipt guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_noop_clearance_receipt_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
