#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateTimedOutOperationQuarantineClearanceReceipt } from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-operation-replay-key-collision-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-OPERATION-REPLAY-KEY-COLLISION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function bytes(value) { return value instanceof Uint8Array ? value : new TextEncoder().encode(String(value)); }
function makeStore() {
  const records = new Map();
  return {
    name: 'synthetic-operation-replay-key-collision-store',
    provider: 'synthetic-operation-replay-key-collision-provider-v0',
    async put(payload, fields = {}) { const body = bytes(payload); const digest = `sha256:${fields.digestSuffix || records.size + 1}`; records.set(digest, body); return Object.freeze({ ref: { digest, backend: this.provider, bytes: body.byteLength }, digest, bytes: body.byteLength, duplicate: false }); },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing ${digest}`); return row; },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return Object.freeze({ ok: records.has(digest), present: records.has(digest), digest, bytes: records.get(digest)?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, blockCount: records.size }); }
  };
}
function makeScheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeAdapter(label, store, trace) { return createBlockStoreLaneAdapter({ label, store, scheduler: makeScheduler(`${label}:scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 }); }
function withFingerprint(ledger) { const fingerprint = timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint }); }
function successRow({ epoch, opId = 'shared-visible-put-op', suffix, offset = 0 }) {
  const now = Date.now() + offset;
  return Object.freeze({ opId, kind: 'put', lane: 'storage', operationEpoch: epoch, operationReplayKey: `operation:storage:put:${epoch}:${opId}`, timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: Object.freeze({ digest: `sha256:${suffix}`, bytes: 32, disposition: 'synthetic-late-success' }) });
}
function collisionLedger() {
  const first = successRow({ epoch: `${REVISION}:epoch-a`, suffix: 'operation-replay-key-collision-a', offset: 1 });
  const second = successRow({ epoch: `${REVISION}:epoch-b`, suffix: 'operation-replay-key-collision-b', offset: 3 });
  return withFingerprint({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', exportedAtMs: Date.now() + 5, label: `${REVISION}-operation-replay-key-collision-ledger`, reason: 'synthetic-merged-ledger-with-same-visible-opid-distinct-operation-replay-keys', counts: Object.freeze({ total: 2, unsettled: 0, successful: 2, failed: 0 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([first, second]), failedTimedOutOperations: Object.freeze([]) });
}
function duplicateOperationKeyLedger(baseLedger) {
  const dup = baseLedger.successfulTimedOutOperations[0];
  return withFingerprint({ ...baseLedger, reason: 'synthetic-duplicate-operation-replay-key-ledger', successfulTimedOutOperations: Object.freeze([dup, { ...dup, settledAtMs: Number(dup.settledAtMs || Date.now()) + 7 }]) });
}
function singleRowStaleLedger(baseLedger) {
  const row = baseLedger.successfulTimedOutOperations[0];
  return withFingerprint({ ...baseLedger, reason: 'single-cleared-row-replay-with-shared-visible-opid', counts: Object.freeze({ total: 1, unsettled: 0, successful: 1, failed: 0 }), successfulTimedOutOperations: Object.freeze([row]), failedTimedOutOperations: Object.freeze([]), unsettledTimedOutOperations: Object.freeze([]) });
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore();
  const ledger = collisionLedger();
  assert.equal(ledger.successfulTimedOutOperations[0].opId, ledger.successfulTimedOutOperations[1].opId);
  assert.notEqual(ledger.successfulTimedOutOperations[0].operationReplayKey, ledger.successfulTimedOutOperations[1].operationReplayKey);

  const adapter = makeAdapter(`${REVISION}-operation-replay-key-collision-importer`, store, trace);
  const importResult = adapter.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'release-import-merged-duplicate-visible-opid-ledger', markUnhealthy: false });
  assert.equal(importResult.ok, true);
  assert.equal(importResult.importedCount, 2);
  assert.equal(importResult.markUnhealthyForced, true);
  const quarantineAfterImport = adapter.timedOutOperationQuarantine('storage');
  assert.equal(quarantineAfterImport.totalCount, 2);
  assert.equal(quarantineAfterImport.successfulTimedOutOperationCount, 2);
  assert.deepEqual(new Set(quarantineAfterImport.successfulTimedOutOperations.map((row) => row.operationReplayKey)).size, 2);

  const duplicateLedger = duplicateOperationKeyLedger(ledger);
  const duplicateAdapter = makeAdapter(`${REVISION}-operation-replay-key-collision-duplicate`, store, trace);
  const duplicateImport = duplicateAdapter.importTimedOutOperationQuarantine(duplicateLedger, { lane: 'storage', reason: 'release-import-duplicate-operation-replay-key-ledger', markUnhealthy: false });
  assert.equal(duplicateImport.ok, false);
  assert.equal(duplicateImport.disposition, 'rejected-ledger-integrity');
  assert.equal(duplicateAdapter.timedOutOperationQuarantine('storage').totalCount, 0);

  const review = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0087-release-probe', reviewToken: 'operation-replay-key-collision-review-token', reason: 'review-duplicate-visible-opid-quarantine' });
  const clear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: review, requireReviewFingerprint: true, reason: 'clear-duplicate-visible-opid-quarantine' });
  assert.equal(clear.ok, true);
  assert.equal(clear.clearedCount, 2);
  assert.equal(clear.cleared.successful.length, 2);
  assert.equal(new Set(clear.cleared.successful.map((row) => row.operationReplayKey)).size, 2);
  const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clear, { reviewer: 'rev0087-release-probe', label: 'operation-replay-key-collision-receipt' });
  const receiptValidation = validateTimedOutOperationQuarantineClearanceReceipt(receipt);
  assert.equal(receiptValidation.ok, true);
  assert.equal(receipt.cleared.successful.length, 2);
  assert.equal(new Set(receipt.cleared.successful.map((row) => row.opId)).size, 1);
  assert.equal(new Set(receipt.cleared.successful.map((row) => row.operationReplayKey)).size, 2);

  const fresh = makeAdapter(`${REVISION}-operation-replay-key-collision-fresh`, store, trace);
  const provenance = { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: fresh.label, store: fresh.storeName, provider: fresh.providerName };
  const register = fresh.executor.registerTimedOutOperationQuarantineClearanceReceipt(receipt, { lane: 'storage', reason: 'release-register-operation-key-collision-receipt', provenance });
  assert.equal(register.ok, true);
  const exactReplay = fresh.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'release-exact-replay-after-operation-key-collision-clear', markUnhealthy: false });
  assert.equal(exactReplay.ok, false);
  assert.equal(exactReplay.disposition, 'rejected-cleared-quarantine-replay');
  const rowReplay = fresh.importTimedOutOperationQuarantine(singleRowStaleLedger(ledger), { lane: 'storage', reason: 'release-single-row-replay-after-operation-key-collision-clear', markUnhealthy: false });
  assert.equal(rowReplay.ok, false);
  assert.equal(rowReplay.disposition, 'rejected-cleared-quarantine-row-replay');
  assert.equal(fresh.timedOutOperationQuarantine('storage').totalCount, 0);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-operation-replay-key-collision-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that timeout-quarantine import/clearance preserves distinct operationReplayKey rows even when visible opId is reused.', observations: { ledger, importResult, quarantineAfterImport, duplicateImport, review, clear, receipt, receiptValidation, register, exactReplay, rowReplay, freshQuarantine: fresh.timedOutOperationQuarantine('storage'), traceKinds: trace.kinds() }, claimsChecked: ['merged timeout-quarantine ledgers can contain same visible opId with distinct operationReplayKey values without collapsing rows', 'duplicate operationReplayKey rows fail closed atomically', 'clearance receipt validation permits repeated visible opId only when operationReplayKey values are distinct', 'stale exact and single-row replay remain rejected after clearance'], nonClaims: ['Synthetic provider only; browser OPFS/Web Locks coverage is in the browser companion proof.', 'Operation replay keys are collision/replay-scoping metadata, not cryptographic attestation.', 'No provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-operation-replay-key-collision-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed operation replay-key collision proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_operation_replay_key_collision_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
