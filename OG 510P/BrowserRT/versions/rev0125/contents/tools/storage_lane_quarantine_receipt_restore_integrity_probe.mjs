#!/usr/bin/env node
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter } from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-receipt-restore-integrity-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-QUARANTINE-RECEIPT-RESTORE-INTEGRITY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const enc = new TextEncoder();
function bytes(value) { return value instanceof Uint8Array ? value : value instanceof ArrayBuffer ? new Uint8Array(value) : ArrayBuffer.isView(value) ? new Uint8Array(value.buffer, value.byteOffset, value.byteLength) : enc.encode(String(value)); }
function sha256Hex(value) { return createHash('sha256').update(Buffer.from(bytes(value))).digest('hex'); }

function makeIntegrityStore() {
  const records = new Map();
  const corrupt = new Set();
  const getCounts = new Map();
  return {
    name: 'synthetic-restore-integrity-store',
    provider: 'synthetic-restore-integrity-provider-v0',
    corrupt,
    getCounts,
    async put(payload, fields = {}) {
      const body = bytes(payload);
      const hash = sha256Hex(body);
      const digest = `sha256:${hash}`;
      records.set(digest, body);
      corrupt.delete(digest);
      return Object.freeze({ ref: { digest, hash, backend: this.provider, bytes: body.byteLength, label: fields.label ?? null }, digest, hash, bytes: body.byteLength, duplicate: false });
    },
    async get(ref) {
      const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest;
      getCounts.set(digest, (getCounts.get(digest) || 0) + 1);
      if (!records.has(digest)) throw new Error(`missing block ${digest}`);
      return records.get(digest);
    },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest) && !corrupt.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const body = records.get(digest); const actualDigest = body ? `sha256:${sha256Hex(body)}` : null; const ok = Boolean(body && digest === actualDigest && !corrupt.has(digest)); return Object.freeze({ ok, present: Boolean(body), digest, actualDigest, bytes: body?.byteLength ?? 0, reason: ok ? null : (body ? 'synthetic-block-integrity-failure' : 'missing') }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; corrupt.delete(digest); return records.delete(digest); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); corrupt.clear(); getCounts.clear(); return had; },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, blockCount: records.size, corruptCount: corrupt.size }); }
  };
}
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function adapter(label, store, trace) { return createBlockStoreLaneAdapter({ label, store, scheduler: scheduler(`${label}:scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 }); }
function withFingerprint(ledger) { const fp = timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fp, reviewFingerprint: fp }); }
function row({ opId, epoch, status }) { const now = Date.now(); const base = { opId, kind: 'put', lane: 'storage', operationEpoch: epoch, operationReplayKey: `operation:storage:put:${epoch}:${opId}`, timeoutMs: 50, timedOutAtMs: now, settledAtMs: now + 1 }; if (status === 'successful') return Object.freeze({ ...base, result: Object.freeze({ digest: `sha256:${opId}:${epoch}`, bytes: 64, disposition: 'synthetic-late-success' }) }); return Object.freeze({ ...base, error: Object.freeze({ name: 'SyntheticLateFailure', message: 'late failure for restore-integrity probe', code: 'BRT_SYNTHETIC_LATE_FAILURE' }) }); }
function mixedLedger(label = 'receipt-restore-integrity') { const success = row({ opId: `${label}-success`, epoch: `${REVISION}:${label}:a`, status: 'successful' }); const failure = row({ opId: `${label}-failure`, epoch: `${REVISION}:${label}:b`, status: 'failed' }); return withFingerprint({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', exportedAtMs: Date.now(), label: `${REVISION}-${label}-ledger`, reason: 'synthetic mixed quarantine ledger for restore integrity', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failure]) }); }
async function makeReceipt(adapterInstance, ledger) {
  const imported = adapterInstance.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'import-before-receipt-restore-integrity', markUnhealthy: false });
  assert.equal(imported.ok, true);
  const review = adapterInstance.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'restore-integrity-probe', reviewToken: `${REVISION}-restore-integrity-review`, reason: 'review all rows for restore integrity' });
  const clear = adapterInstance.clearTimedOutOperationQuarantine({ reviewManifest: review, requireReviewFingerprint: true, reason: 'clear-for-restore-integrity-receipt' });
  assert.equal(clear.ok, true);
  assert.equal(clear.clearedCount, 2);
  const receipt = adapterInstance.createTimedOutOperationQuarantineClearanceReceipt(clear, { reviewer: 'restore-integrity-probe', label: 'restore-integrity-receipt' });
  return { imported, review, clear, receipt };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();

  const receiptStore = makeIntegrityStore();
  const source = adapter(`${REVISION}-restore-integrity-source`, receiptStore, trace);
  const ledger = mixedLedger('receipt-restore-integrity');
  const receiptFlow = await makeReceipt(source, ledger);
  const persistedReceipt = await source.persistTimedOutOperationQuarantineClearanceReceipt(receiptFlow.receipt, { label: 'restore-integrity-receipt-block' });
  const receiptDigest = persistedReceipt.digest;
  receiptStore.corrupt.add(receiptDigest);
  const receiptGetCountBeforeReject = receiptStore.getCounts.get(receiptDigest) || 0;
  const fresh = adapter(`${REVISION}-restore-integrity-fresh`, receiptStore, trace);
  const unverifiedReceiptRestore = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceipt.ref, { lane: 'storage', reason: 'reject-unverified-receipt-restore', verifyBeforeRestore: false });
  assert.equal(unverifiedReceiptRestore.ok, false);
  assert.equal(unverifiedReceiptRestore.disposition, 'rejected-unverified-clearance-receipt-restore');
  const rejectedReceiptRestore = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceipt.ref, { lane: 'storage', reason: 'reject-corrupt-receipt-block' });
  assert.equal(rejectedReceiptRestore.ok, false);
  assert.equal(rejectedReceiptRestore.disposition, 'rejected-clearance-receipt-block-integrity');
  assert.equal(rejectedReceiptRestore.blockVerify.ok, false);
  assert.equal(receiptStore.getCounts.get(receiptDigest) || 0, receiptGetCountBeforeReject, 'receipt restore must not call get() after failed verify');
  receiptStore.corrupt.delete(receiptDigest);
  const restoredReceipt = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceipt.ref, { lane: 'storage', reason: 'restore-valid-receipt-block' });
  assert.equal(restoredReceipt.ok, true);
  assert.equal(restoredReceipt.blockVerify.ok, true);
  const staleReplay = fresh.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'stale-replay-after-restored-receipt', markUnhealthy: false });
  assert.equal(staleReplay.ok, false);
  assert.equal(staleReplay.disposition, 'rejected-cleared-quarantine-replay');

  const ledgerStore = makeIntegrityStore();
  const ledgerAdapter = adapter(`${REVISION}-restore-integrity-ledger`, ledgerStore, trace);
  const ledgerToPersist = mixedLedger('ledger-restore-integrity');
  const persistedLedger = await ledgerAdapter.persistTimedOutOperationQuarantine({ ledger: ledgerToPersist, label: 'restore-integrity-ledger-block' });
  const ledgerDigest = persistedLedger.digest;
  ledgerStore.corrupt.add(ledgerDigest);
  const ledgerGetCountBeforeReject = ledgerStore.getCounts.get(ledgerDigest) || 0;
  const ledgerFresh = adapter(`${REVISION}-restore-integrity-ledger-fresh`, ledgerStore, trace);
  const unverifiedLedgerRestore = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedger.ref, { lane: 'storage', reason: 'reject-unverified-ledger-restore', markUnhealthy: false, verifyBeforeRestore: false });
  assert.equal(unverifiedLedgerRestore.ok, false);
  assert.equal(unverifiedLedgerRestore.disposition, 'rejected-unverified-quarantine-ledger-restore');
  const rejectedLedgerRestore = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedger.ref, { lane: 'storage', reason: 'reject-corrupt-ledger-block', markUnhealthy: false });
  assert.equal(rejectedLedgerRestore.ok, false);
  assert.equal(rejectedLedgerRestore.disposition, 'rejected-quarantine-ledger-block-integrity');
  assert.equal(rejectedLedgerRestore.blockVerify.ok, false);
  assert.equal(ledgerStore.getCounts.get(ledgerDigest) || 0, ledgerGetCountBeforeReject, 'ledger restore must not call get() after failed verify');
  ledgerStore.corrupt.delete(ledgerDigest);
  const restoredLedger = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedger.ref, { lane: 'storage', reason: 'restore-valid-ledger-block', markUnhealthy: false });
  assert.equal(restoredLedger.ok, true);
  assert.equal(restoredLedger.importResult.markUnhealthyForced, true);

  const snapshot = fresh.snapshot();
  assert.equal(snapshot.stats.quarantineClearanceReceiptRestoreBlockIntegrityRejected, 1);
  assert.equal(ledgerFresh.snapshot().stats.quarantineLedgerRestoreBlockIntegrityRejected, 1);

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-quarantine-receipt-restore-integrity`, task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-light proof that timeout-quarantine ledger and clearance-receipt restore verify block-store refs before decoding/registering handoff state.',
    observations: { unverifiedReceiptRestore, rejectedReceiptRestore, restoredReceipt, staleReplay, unverifiedLedgerRestore, rejectedLedgerRestore, restoredLedger, receiptStore: receiptStore.snapshot(), ledgerStore: ledgerStore.snapshot(), traceKinds: trace.snapshot().map((row) => row.kind) },
    claimsChecked: ['unverified clearance receipt restore opt-out rejects without unsafe override', 'corrupt clearance receipt block restore rejects before get/register', 'valid restored receipt still rejects stale quarantine replay', 'unverified quarantine ledger restore opt-out rejects without unsafe override', 'corrupt quarantine ledger block restore rejects before get/import', 'valid restored ledger forces backpressure'],
    nonClaims: ['Synthetic store only; managed Chromium proof covers OPFS/Web Locks.', 'Block verification is provider-backed integrity checking, not cryptographic attestation or tamper-proof storage.']
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-receipt-restore-integrity`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed restore-integrity proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(error?.stack || error);
  process.exitCode = 1;
}
