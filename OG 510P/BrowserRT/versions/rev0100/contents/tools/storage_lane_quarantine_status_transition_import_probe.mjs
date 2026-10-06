#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateTimedOutOperationQuarantineClearanceReceipt } from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-status-transition-import-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-STATUS-TRANSITION-IMPORT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function bytes(value) { return value instanceof Uint8Array ? value : new TextEncoder().encode(String(value)); }
function makeStore() {
  const records = new Map();
  return {
    name: 'synthetic-status-transition-import-store',
    provider: 'synthetic-status-transition-import-provider-v0',
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
function rowFor(status, { opId = 'status-transition-visible-put', epoch = `${REVISION}:status-transition-epoch`, offset = 0 } = {}) {
  const now = Date.now() + offset;
  const base = { opId, kind: 'put', lane: 'storage', operationEpoch: epoch, operationReplayKey: `operation:storage:put:${epoch}:${opId}`, timeoutMs: 35, timedOutAtMs: now };
  if (status === 'successful') return Object.freeze({ ...base, settledAtMs: now + 1, result: Object.freeze({ digest: `sha256:${REVISION}:status-transition-success`, bytes: 64, disposition: 'synthetic-status-transition-late-success' }) });
  if (status === 'failed') return Object.freeze({ ...base, settledAtMs: now + 2, error: Object.freeze({ name: 'SyntheticStatusTransitionFailure', message: 'late provider status changed to failure', code: 'BRT_SYNTHETIC_STATUS_TRANSITION_FAILURE' }) });
  return Object.freeze(base);
}
function ledgerFor(status, row) {
  const buckets = { unsettled: [], successful: [], failed: [] };
  buckets[status].push(row);
  return withFingerprint({
    schema: 'brt.storageLane.timedOutOperationQuarantine.v1',
    lane: 'storage',
    exportedAtMs: Date.now(),
    label: `${REVISION}-status-transition-${status}-ledger`,
    reason: `synthetic status transition import ledger: ${status}`,
    counts: Object.freeze({ total: 1, unsettled: buckets.unsettled.length, successful: buckets.successful.length, failed: buckets.failed.length }),
    unsettledTimedOutOperations: Object.freeze(buckets.unsettled),
    successfulTimedOutOperations: Object.freeze(buckets.successful),
    failedTimedOutOperations: Object.freeze(buckets.failed)
  });
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore();
  const adapter = makeAdapter(`${REVISION}-status-transition-import`, store, trace);
  const successRow = rowFor('successful', { offset: 1 });
  const failedRow = rowFor('failed', { offset: 3 });
  const unsettledRow = rowFor('unsettled', { offset: 5 });
  assert.equal(successRow.operationReplayKey, failedRow.operationReplayKey);
  assert.equal(successRow.operationReplayKey, unsettledRow.operationReplayKey);

  const successLedger = ledgerFor('successful', successRow);
  const failedLedger = ledgerFor('failed', failedRow);
  const unsettledLedger = ledgerFor('unsettled', unsettledRow);

  const importSuccess = adapter.importTimedOutOperationQuarantine(successLedger, { lane: 'storage', reason: 'release-import-success-status-transition-row', markUnhealthy: false });
  assert.equal(importSuccess.ok, true);
  assert.equal(importSuccess.markUnhealthyForced, true);
  let quarantine = adapter.timedOutOperationQuarantine('storage');
  assert.equal(quarantine.totalCount, 1);
  assert.equal(quarantine.successfulTimedOutOperationCount, 1);
  assert.equal(quarantine.failedTimedOutOperationCount, 0);

  const importFailed = adapter.importTimedOutOperationQuarantine(failedLedger, { lane: 'storage', reason: 'release-import-failed-status-transition-row', markUnhealthy: false });
  assert.equal(importFailed.ok, true);
  assert.equal(importFailed.statusTransitionReplacementCount, 1);
  quarantine = adapter.timedOutOperationQuarantine('storage');
  assert.equal(quarantine.totalCount, 1);
  assert.equal(quarantine.successfulTimedOutOperationCount, 0);
  assert.equal(quarantine.failedTimedOutOperationCount, 1);
  assert.equal(quarantine.failedTimedOutOperations[0].operationReplayKey, failedRow.operationReplayKey);

  const importUnsettled = adapter.importTimedOutOperationQuarantine(unsettledLedger, { lane: 'storage', reason: 'release-import-unsettled-status-transition-row', markUnhealthy: false });
  assert.equal(importUnsettled.ok, true);
  assert.equal(importUnsettled.statusTransitionReplacementCount, 1);
  quarantine = adapter.timedOutOperationQuarantine('storage');
  assert.equal(quarantine.totalCount, 1);
  assert.equal(quarantine.unsettledTimedOutOperationCount, 1);
  assert.equal(quarantine.successfulTimedOutOperationCount, 0);
  assert.equal(quarantine.failedTimedOutOperationCount, 0);

  const importSuccessAgain = adapter.importTimedOutOperationQuarantine(successLedger, { lane: 'storage', reason: 'release-import-success-status-transition-row-again', markUnhealthy: false });
  assert.equal(importSuccessAgain.ok, true);
  assert.equal(importSuccessAgain.statusTransitionReplacementCount, 1);
  quarantine = adapter.timedOutOperationQuarantine('storage');
  assert.equal(quarantine.totalCount, 1);
  assert.equal(quarantine.successfulTimedOutOperationCount, 1);
  assert.equal(quarantine.failedTimedOutOperationCount, 0);
  assert.equal(quarantine.unsettledTimedOutOperationCount, 0);

  const review = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', operationReplayKey: successRow.operationReplayKey, reviewer: 'rev0090-release-probe', reviewToken: 'status-transition-import-review', reason: 'review transitioned status row by replay key' });
  const clear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: review, requireReviewFingerprint: true, reason: 'clear transitioned status row by replay key' });
  assert.equal(clear.ok, true);
  assert.equal(clear.clearedCount, 1);
  const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clear, { reviewer: 'rev0090-release-probe', label: 'status-transition-import-receipt' });
  assert.equal(validateTimedOutOperationQuarantineClearanceReceipt(receipt).ok, true);
  const fresh = makeAdapter(`${REVISION}-status-transition-import-fresh`, store, trace);
  const provenance = { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: fresh.label, store: fresh.storeName, provider: fresh.providerName };
  const register = fresh.executor.registerTimedOutOperationQuarantineClearanceReceipt(receipt, { lane: 'storage', reason: 'release-register-status-transition-receipt', provenance });
  assert.equal(register.ok, true);
  const staleReplay = fresh.importTimedOutOperationQuarantine(successLedger, { lane: 'storage', reason: 'release-stale-replay-after-status-transition-clear', markUnhealthy: false });
  assert.equal(staleReplay.ok, false);
  assert.equal(staleReplay.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(fresh.timedOutOperationQuarantine('storage').totalCount, 0);

  const traceKinds = trace.snapshot().map((entry) => entry.kind);
  assert.ok(traceKinds.includes('storage-lane:timed-out-quarantine-import-status-transition-replaced'));

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-quarantine-status-transition-import`,
    task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    observations: { importSuccess, importFailed, importUnsettled, importSuccessAgain, finalQuarantine: quarantine, review, clear, receipt, register, staleReplay, traceKinds },
    claimsChecked: [
      'importing the same operationReplayKey under a new timeout status replaces the old status bucket row',
      'successful -> failed -> unsettled -> successful transitions leave exactly one quarantine row',
      'status-transition replacement emits trace/stat evidence',
      'clearance receipt still rejects stale replay for the final transitioned row'
    ],
    nonClaims: [
      'Release-light synthetic quarantine policy proof; does not launch Chromium.',
      'No provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota/eviction survival, cryptographic attestation, tamper-proof storage, or production readiness claim.'
    ]
  };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-status-transition-import`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed status-transition import proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(error?.stack || error); process.exitCode = 1; }
