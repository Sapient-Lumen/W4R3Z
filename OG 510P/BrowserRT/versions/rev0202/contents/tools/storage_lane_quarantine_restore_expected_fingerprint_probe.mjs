#!/usr/bin/env node
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter } from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';
import { assertExpectedFingerprintRestoreReport, EXPECTED_FINGERPRINT_RESTORE_CLAIMS, EXPECTED_FINGERPRINT_RESTORE_NON_CLAIMS } from './lib/quarantine_restore_expected_fingerprint_harness.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-QUARANTINE-RESTORE-EXPECTED-FINGERPRINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const enc = new TextEncoder();
function bytes(value) { return value instanceof Uint8Array ? value : value instanceof ArrayBuffer ? new Uint8Array(value) : ArrayBuffer.isView(value) ? new Uint8Array(value.buffer, value.byteOffset, value.byteLength) : enc.encode(String(value)); }
function sha256Hex(value) { return createHash('sha256').update(Buffer.from(bytes(value))).digest('hex'); }
function makeStore() {
  const records = new Map();
  return {
    name: 'synthetic-expected-fingerprint-store',
    provider: 'synthetic-expected-fingerprint-provider-v0',
    async put(payload, fields = {}) { const body = bytes(payload); const hash = sha256Hex(body); const digest = `sha256:${hash}`; records.set(digest, body); return Object.freeze({ ref: { digest, hash, backend: this.provider, bytes: body.byteLength, label: fields.label ?? null }, digest, hash, bytes: body.byteLength, duplicate: false }); },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; if (!records.has(digest)) throw new Error(`missing block ${digest}`); return records.get(digest); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const body = records.get(digest); const actualDigest = body ? `sha256:${sha256Hex(body)}` : null; const ok = Boolean(body && digest === actualDigest); return Object.freeze({ ok, present: Boolean(body), digest, actualDigest, bytes: body?.byteLength ?? 0, reason: ok ? null : (body ? 'synthetic-integrity-failure' : 'missing') }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, blockCount: records.size }); }
  };
}
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function adapter(label, store, trace) { return createBlockStoreLaneAdapter({ label, store, scheduler: scheduler(`${label}:scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 }); }
function withFingerprint(ledger) { const fp = timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fp, reviewFingerprint: fp }); }
function row({ label, status }) { const now = Date.now(); const opId = `${REVISION}-${label}-${status}`; const epoch = `${REVISION}:${label}:${status}:epoch`; const base = { opId, kind: 'put', lane: 'storage', operationEpoch: epoch, operationReplayKey: `operation:storage:put:${epoch}:${opId}`, timeoutMs: 50, timedOutAtMs: now, settledAtMs: now + 1 }; if (status === 'successful') return Object.freeze({ ...base, result: { digest: `sha256:${label}:${status}`, bytes: 64, disposition: 'synthetic-late-success' } }); return Object.freeze({ ...base, error: { name: 'SyntheticLateFailure', message: `late failure for ${label}`, code: 'BRT_SYNTHETIC_LATE_FAILURE' } }); }
function ledger(label) { const success = row({ label, status: 'successful' }); const failure = row({ label, status: 'failed' }); return withFingerprint({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', exportedAtMs: Date.now(), label: `${REVISION}-${label}-ledger`, reason: `synthetic ${label} quarantine ledger`, counts: { total: 2, unsettled: 0, successful: 1, failed: 1 }, unsettledTimedOutOperations: [], successfulTimedOutOperations: [success], failedTimedOutOperations: [failure] }); }
async function receiptFlow(adapterInstance, sourceLedger, label) {
  const imported = adapterInstance.importTimedOutOperationQuarantine(sourceLedger, { lane: 'storage', reason: `${label}-import-before-clear`, markUnhealthy: false });
  assert.equal(imported.ok, true);
  const review = adapterInstance.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'restore-expected-fingerprint-probe', reviewToken: `${REVISION}-${label}-review`, reason: `${label}-review-all` });
  const clear = adapterInstance.clearTimedOutOperationQuarantine({ reviewManifest: review, requireReviewFingerprint: true, reason: `${label}-clear-all` });
  assert.equal(clear.ok, true);
  const receipt = adapterInstance.createTimedOutOperationQuarantineClearanceReceipt(clear, { reviewer: 'restore-expected-fingerprint-probe', label: `${label}-receipt` });
  return { imported, review, clear, receipt };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore();
  const source = adapter(`${REVISION}-expected-fingerprint-source`, store, trace);
  const ledgerA = ledger('restore-expected-a');
  const ledgerB = ledger('restore-expected-b');
  const persistedLedgerA = await source.persistTimedOutOperationQuarantine({ ledger: ledgerA, label: 'expected-fingerprint-ledger-a' });
  const persistedLedgerB = await source.persistTimedOutOperationQuarantine({ ledger: ledgerB, label: 'expected-fingerprint-ledger-b' });
  const flowA = await receiptFlow(source, ledgerA, 'receipt-a');
  const flowB = await receiptFlow(source, ledgerB, 'receipt-b');
  const persistedReceiptA = await source.persistTimedOutOperationQuarantineClearanceReceipt(flowA.receipt, { label: 'expected-fingerprint-receipt-a' });
  const persistedReceiptB = await source.persistTimedOutOperationQuarantineClearanceReceipt(flowB.receipt, { label: 'expected-fingerprint-receipt-b' });

  const ledgerFresh = adapter(`${REVISION}-expected-fingerprint-ledger-fresh`, store, trace);
  const blankLedgerRestore = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedgerA.ref, { lane: 'storage', reason: 'reject-blank-ledger-expected-fingerprint-intent', expectedQuarantineFingerprint: '   ', markUnhealthy: false });
  assert.equal(blankLedgerRestore.ok, false);
  assert.equal(blankLedgerRestore.disposition, 'rejected-quarantine-ledger-expected-fingerprint');
  assert.equal(ledgerFresh.timedOutOperationQuarantine('storage').totalCount, 0);
  const wrongLedgerRestore = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedgerB.ref, { lane: 'storage', reason: 'reject-valid-but-wrong-ledger-fingerprint', expectedQuarantineFingerprint: ledgerA.quarantineFingerprint, markUnhealthy: false });
  assert.equal(wrongLedgerRestore.ok, false);
  assert.equal(wrongLedgerRestore.disposition, 'rejected-quarantine-ledger-expected-fingerprint');
  const ledgerQuarantineAfterRejected = ledgerFresh.timedOutOperationQuarantine('storage');
  const ledgerLaneAfterRejected = ledgerFresh.scheduler.snapshotLane('storage');
  assert.equal(ledgerQuarantineAfterRejected.totalCount, 0);
  assert.equal(ledgerLaneAfterRejected.healthy, true);
  const rightLedgerRestore = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedgerA.ref, { lane: 'storage', reason: 'restore-expected-ledger-fingerprint-match', expectedQuarantineFingerprint: ledgerA.quarantineFingerprint, markUnhealthy: false });
  assert.equal(rightLedgerRestore.ok, true);
  assert.equal(rightLedgerRestore.importResult.markUnhealthyForced, true);
  const ledgerQuarantineAfterAccepted = ledgerFresh.timedOutOperationQuarantine('storage');
  assert.equal(ledgerQuarantineAfterAccepted.totalCount, 2);

  const receiptFresh = adapter(`${REVISION}-expected-fingerprint-receipt-fresh`, store, trace);
  const blankReceiptRestore = await receiptFresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceiptA.ref, { lane: 'storage', reason: 'reject-blank-receipt-expected-fingerprint-intent', expectedReceiptFingerprint: ' ', expectedPreClearanceFingerprint: flowA.receipt.preClearanceFingerprint });
  assert.equal(blankReceiptRestore.ok, false);
  assert.equal(blankReceiptRestore.disposition, 'rejected-clearance-receipt-expected-fingerprint');
  assert.equal(receiptFresh.clearedTimedOutOperationQuarantineClearanceReceipts('storage').length, 0);
  const wrongReceiptRestore = await receiptFresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceiptB.ref, { lane: 'storage', reason: 'reject-valid-but-wrong-receipt-fingerprint', expectedReceiptFingerprint: flowA.receipt.receiptFingerprint, expectedPreClearanceFingerprint: flowA.receipt.preClearanceFingerprint });
  assert.equal(wrongReceiptRestore.ok, false);
  assert.equal(wrongReceiptRestore.disposition, 'rejected-clearance-receipt-expected-fingerprint');
  const receiptsAfterWrong = receiptFresh.clearedTimedOutOperationQuarantineClearanceReceipts('storage');
  assert.equal(receiptsAfterWrong.length, 0);
  const importAfterRejectedReceipt = receiptFresh.importTimedOutOperationQuarantine(ledgerB, { lane: 'storage', reason: 'ledger-b-imports-after-wrong-receipt-rejected', markUnhealthy: false });
  assert.equal(importAfterRejectedReceipt.ok, true);
  assert.equal(importAfterRejectedReceipt.markUnhealthyForced, true);

  const receiptRestoreAdapter = adapter(`${REVISION}-expected-fingerprint-receipt-restore`, store, trace);
  const wrongPreclearanceRestore = await receiptRestoreAdapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceiptA.ref, { lane: 'storage', reason: 'reject-valid-receipt-wrong-preclearance-fingerprint', expectedReceiptFingerprint: flowA.receipt.receiptFingerprint, expectedPreClearanceFingerprint: flowB.receipt.preClearanceFingerprint });
  assert.equal(wrongPreclearanceRestore.ok, false);
  assert.equal(wrongPreclearanceRestore.disposition, 'rejected-clearance-receipt-expected-fingerprint');
  const rightReceiptRestore = await receiptRestoreAdapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceiptA.ref, { lane: 'storage', reason: 'restore-receipt-expected-fingerprints-match', expectedReceiptFingerprint: flowA.receipt.receiptFingerprint, expectedPreClearanceFingerprint: flowA.receipt.preClearanceFingerprint });
  assert.equal(rightReceiptRestore.ok, true);
  const staleReplay = receiptRestoreAdapter.importTimedOutOperationQuarantine(ledgerA, { lane: 'storage', reason: 'stale-replay-after-expected-fingerprint-restore', markUnhealthy: false });
  assert.equal(staleReplay.ok, false);
  assert.equal(staleReplay.disposition, 'rejected-cleared-quarantine-replay');
  const traceKinds = trace.snapshot().map((row) => row.kind);
  const observations = { ledgerA, ledgerB, blankLedgerRestore, wrongLedgerRestore, ledgerQuarantineAfterRejected, ledgerLaneAfterRejected, rightLedgerRestore, ledgerQuarantineAfterAccepted, blankReceiptRestore, wrongReceiptRestore, receiptsAfterWrong, importAfterRejectedReceipt, wrongPreclearanceRestore, rightReceiptRestore, staleReplay, store: store.snapshot(), traceKinds };
  assertExpectedFingerprintRestoreReport(observations);

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-quarantine-restore-expected-fingerprint`, task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-light proof that provider-backed timeout-quarantine ledger/receipt restore can be pinned to the intended expected fingerprints and rejects blank, valid-but-wrong, or wrong-preclearance restore intent before import/registration.',
    observations,
    claimsChecked: [...EXPECTED_FINGERPRINT_RESTORE_CLAIMS],
    nonClaims: ['Synthetic store only; browser proof covers OPFS/Web Locks.', ...EXPECTED_FINGERPRINT_RESTORE_NON_CLAIMS]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-restore-expected-fingerprint`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed expected-fingerprint restore proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(error?.stack || error);
  process.exitCode = 1;
}
