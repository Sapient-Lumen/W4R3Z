#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-review-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-REVIEW-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticReviewScopeError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function clone(value) { return JSON.parse(JSON.stringify(value)); }

function makeStore({ trace = null } = {}) {
  const records = new Map(); const releaseSuccess = deferred(); const releaseFailure = deferred();
  const state = { puts: 0, lateSuccesses: 0, lateFailures: 0, waitForSettledCalls: 0 };
  return { name: 'synthetic-quarantine-review-scope-store', provider: 'synthetic-quarantine-review-scope-provider-v0', releaseSuccess, releaseFailure, state,
    async put(payload, fields = {}) { const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; records.set(digest, body); state.puts += 1; trace?.emit('synthetic-quarantine-review-scope:put', { digest, bytes: body.byteLength, label: fields.label ?? null }); const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength }); if (fields.label === 'review-scope-late-success') { await releaseSuccess.promise; state.lateSuccesses += 1; } if (fields.label === 'review-scope-late-failure') { await releaseFailure.promise; state.lateFailures += 1; throw codedError('BRT_SYNTHETIC_REVIEW_BINDING_LATE_FAILURE', 'synthetic late failure after committed block', { digest }); } return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null }); },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing block ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); return Object.freeze({ ok: Boolean(row), present: Boolean(row), digest, bytes: row?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: [...records.values()].reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { state.waitForSettledCalls += 1; return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}

export async function runProbe() {
  const started = performance.now(); const trace = new TraceLog(); const store = makeStore({ trace });
  const source = createBlockStoreLaneAdapter({ label: `${REVISION}-review-scope-source`, store, scheduler: scheduler(`${REVISION}-review-scope-source-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 100 });
  source.schedulePut(`${REVISION}:quarantine-review-scope-success`, { id: 'review-scope-success-timeout', label: 'review-scope-late-success' });
  source.schedulePut(`${REVISION}:quarantine-review-scope-failure`, { id: 'review-scope-failure-timeout', label: 'review-scope-late-failure' });
  const d1 = source.scheduler.dispatchNext(); const d2 = source.scheduler.dispatchNext();
  const [t1, t2] = await Promise.all([source.executor.executeDispatched(d1), source.executor.executeDispatched(d2)]);
  assert.equal(t1.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(t2.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  store.releaseSuccess.resolve('release-success'); store.releaseFailure.resolve('release-failure');
  const settled = await source.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  const quarantine = source.timedOutOperationQuarantine('storage');
  const ledger = source.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'release-tier-review-scope-export' });
  const tamperedLedger = clone(ledger); tamperedLedger.successfulTimedOutOperations[0].opId = `${tamperedLedger.successfulTimedOutOperations[0].opId}:tampered`;
  const tampered = createBlockStoreLaneAdapter({ label: `${REVISION}-review-scope-tampered-import`, store, scheduler: scheduler(`${REVISION}-review-scope-tampered-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const tamperedImport = tampered.importTimedOutOperationQuarantine(tamperedLedger, { lane: 'storage', reason: 'reject-tampered-fingerprint' });
  const tamperedQuarantine = tampered.timedOutOperationQuarantine('storage');
  const tamperedLane = tampered.snapshot().executor.scheduler.lanes.find((lane) => lane.id === 'storage');

  const imported = createBlockStoreLaneAdapter({ label: `${REVISION}-review-scope-imported`, store, scheduler: scheduler(`${REVISION}-review-scope-imported-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const importedLedger = imported.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'valid-review-scope-import markUnhealthy:false', markUnhealthy: false });
  const importedQuarantine = imported.timedOutOperationQuarantine('storage');
  const rejectedWhileQuarantined = imported.schedulePut(`${REVISION}:review-scope-should-not-mutate`, { id: 'review-scope-rejected-while-quarantined' });
  const missingFingerprintClear = imported.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reviewed: true, reviewToken: 'missing-fingerprint', requireReviewFingerprint: true, reason: 'reject-missing-review-fingerprint' });
  const staleFingerprintClear = imported.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reviewed: true, reviewToken: 'stale-fingerprint', reviewFingerprint: 'brt-qfp-v1:0000000000000000', requireReviewFingerprint: true, reason: 'reject-stale-review-fingerprint' });
  const scopedReviewManifest = imported.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opIds: importedQuarantine.opIds.successful, reviewer: 'rev0078-release-probe', reviewToken: 'scope-specific-review-token', reason: 'bind-review-to-success-only-scope' });
  const scopeOverrideClear = imported.clearTimedOutOperationQuarantine({ reviewManifest: scopedReviewManifest, category: 'all', allowLaneWide: true, requireReviewFingerprint: true, reason: 'reject-review-manifest-scope-override' });
  const tokenOverrideClear = imported.clearTimedOutOperationQuarantine({ reviewManifest: scopedReviewManifest, reviewToken: 'copied-token-override', requireReviewFingerprint: true, reason: 'reject-review-manifest-token-override' });
  const fingerprintOverrideClear = imported.clearTimedOutOperationQuarantine({ reviewManifest: scopedReviewManifest, reviewFingerprint: scopedReviewManifest.reviewFingerprint, requireReviewFingerprint: true, reason: 'reject-review-manifest-fingerprint-override' });
  const staleCountManifest = clone(scopedReviewManifest); staleCountManifest.counts.total += 1;
  const countMismatchClear = imported.clearTimedOutOperationQuarantine({ reviewManifest: staleCountManifest, requireReviewFingerprint: true, reason: 'reject-review-manifest-count-mismatch' });
  const reviewManifest = imported.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0078-release-probe', reviewToken: 'scope-bound-review-token', reason: 'bind-review-to-current-quarantine' });
  const clearWithManifest = imported.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-bound-review-manifest' });
  const recovered = await imported.recoverWhenStoreSettled({ timeoutMs: 500, intervalMs: 5, reason: 'review-scope-cleared' });
  const rec = imported.schedulePut(`${REVISION}:quarantine-review-scope-recovered`, { id: 'review-scope-recovered-put', label: 'review-scope-recovered', operationTimeoutMs: 1000 });
  const drain = await imported.drain({ maxSteps: 3 }); const recoveredResult = drain.results.find((row) => row.opId === 'review-scope-recovered-put'); const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const traceKinds = trace.kinds();

  assert.equal(settled.ok, true); assert.equal(quarantine.successfulCount, 1); assert.equal(quarantine.failedCount, 1); assert.match(quarantine.quarantineFingerprint, /^brt-qfp-v1:/); assert.equal(ledger.quarantineFingerprint, quarantine.quarantineFingerprint);
  assert.equal(tamperedImport.ok, false); assert.equal(tamperedImport.disposition, 'rejected-ledger-integrity'); assert.equal(tamperedQuarantine.totalCount, 0); assert.equal(tamperedLane.healthy, true);
  assert.equal(importedLedger.ok, true); assert.equal(importedLedger.markUnhealthyRequested, false); assert.equal(importedLedger.markUnhealthyForced, true); assert.equal(importedLedger.quarantineFingerprint, ledger.quarantineFingerprint); assert.equal(importedQuarantine.totalCount, 2); assert.equal(importedQuarantine.reviewFingerprint, ledger.quarantineFingerprint);
  assert.equal(rejectedWhileQuarantined.accepted, false); assert.equal(rejectedWhileQuarantined.scheduler.noMutation, true);
  assert.equal(missingFingerprintClear.ok, false); assert.equal(missingFingerprintClear.code, 'timed-out-quarantine-clear-review-fingerprint-required');
  assert.equal(staleFingerprintClear.ok, false); assert.equal(staleFingerprintClear.code, 'timed-out-quarantine-clear-review-fingerprint-mismatch');
  assert.equal(scopedReviewManifest.reviewFingerprint, importedQuarantine.reviewFingerprint); assert.equal(scopeOverrideClear.ok, false); assert.equal(scopeOverrideClear.code, 'timed-out-quarantine-clear-review-manifest-scope-override'); assert.equal(tokenOverrideClear.ok, false); assert.equal(tokenOverrideClear.code, 'timed-out-quarantine-clear-review-manifest-scope-override'); assert.equal(fingerprintOverrideClear.ok, false); assert.equal(fingerprintOverrideClear.code, 'timed-out-quarantine-clear-review-manifest-scope-override');
  assert.equal(countMismatchClear.ok, false); assert.equal(countMismatchClear.code, 'timed-out-quarantine-clear-review-manifest-count-mismatch');
  assert.equal(reviewManifest.reviewFingerprint, importedQuarantine.reviewFingerprint); assert.equal(clearWithManifest.ok, true); assert.equal(clearWithManifest.clearedCount, 2); assert.equal(clearWithManifest.reviewFingerprint, reviewManifest.reviewFingerprint);
  assert.equal(recovered.recovered, true); assert.equal(rec.accepted, true); assert.equal(recoveredResult?.ok, true); assert.equal(recoveredVerify?.ok, true);
  for (const kind of ['storage-lane:timed-out-quarantine-export', 'storage-lane:timed-out-quarantine-import-rejected', 'storage-lane:timed-out-quarantine-import', 'storage-lane:timed-out-quarantine-clear-rejected', 'storage-lane:timed-out-quarantine-review-created', 'storage-lane:timed-out-quarantine-cleared']) assert.ok(traceKinds.includes(kind), `missing trace ${kind}`);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-review-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that timeout-quarantine ledgers carry deterministic review fingerprints: tampered ledgers and missing/stale review fingerprints and malformed/scope-or-option-overridden review manifests fail closed, while a scope-bound review manifest permits explicit recovery.', observations: { timeoutResults: [t1, t2], settled, quarantine, ledger, tamperedImport, tamperedQuarantine, tamperedLane, importedLedger, importedQuarantine, rejectedWhileQuarantined, missingFingerprintClear, staleFingerprintClear, scopedReviewManifest, scopeOverrideClear, tokenOverrideClear, fingerprintOverrideClear, countMismatchClear, reviewManifest, clearWithManifest, recovered, rec, recoveredResult, recoveredVerify, stats: imported.snapshot().executor.stats, traceKinds }, claimsChecked: ['quarantine ledger export includes a brt-qfp-v1 fingerprint', 'tampered ledger rows are rejected without mutating fresh lane state', 'review clearing can require a fingerprint', 'stale review fingerprints and stale/mismatched review manifests are rejected', 'markUnhealthy:false non-empty import forces quarantineLedgerImportBackpressureForced', 'a review manifest bound to the current quarantine fingerprint and scope can clear and permit recovery'], nonClaims: ['Fingerprint is deterministic review/scope binding, not cryptographic attestation or tamper-proof storage.', 'No provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, or production readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-review-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed quarantine review binding proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_review_binding_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
