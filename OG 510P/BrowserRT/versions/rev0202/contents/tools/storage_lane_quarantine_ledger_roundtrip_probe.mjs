#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-ledger-roundtrip-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-LEDGER-ROUNDTRIP-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (typeof value === 'string') return new TextEncoder().encode(value); if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticMixedLateProviderError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }
function makeScheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] }); }
function makeMixedLateStore({ trace = null, mode = 'source' } = {}) {
  const releases = new Map([['success', deferred()], ['failure', deferred()]]);
  const records = new Map();
  const refs = new Map();
  const state = { puts: 0, committedBeforeSettle: 0, lateSuccesses: 0, lateFailures: 0, cleanupCalls: 0, waitForSettledCalls: 0 };
  return {
    name: `synthetic-mixed-late-${mode}-block-store`, provider: `synthetic-mixed-late-${mode}-provider-v1`, releases, refs, state,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; const label = fields.label || 'unlabeled';
      state.puts += 1; state.committedBeforeSettle += 1; records.set(digest, body);
      const ref = Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null });
      refs.set(label, ref);
      trace?.emit('synthetic-mixed-late-store:committed-before-settle', { digest, label, bytes: body.byteLength, mode });
      if (label === 'mixed-late-success') { await releases.get('success').promise; state.lateSuccesses += 1; trace?.emit('synthetic-mixed-late-store:late-success', { digest, label, mode }); return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label }); }
      if (label === 'mixed-late-failure') { await releases.get('failure').promise; state.lateFailures += 1; trace?.emit('synthetic-mixed-late-store:late-failure', { digest, label, mode }); throw codedError('BRT_OPFS_OPERATION_FAILED', 'synthetic late provider failure after timeout', { digest, label, mode }); }
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const row = records.get(digest); return Object.freeze({ digest, present: Boolean(row), ok: Boolean(row), bytes: row?.byteLength ?? 0, path: null }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: Array.from(records.values()).reduce((n, row) => n + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { state.cleanupCalls += 1; const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { state.waitForSettledCalls += 1; return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-store-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const sourceScheduler = makeScheduler(`${REVISION}-quarantine-ledger-source-scheduler`, trace);
  const sourceStore = makeMixedLateStore({ trace, mode: 'source' });
  const sourceAdapter = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-ledger-source-adapter`, store: sourceStore, scheduler: sourceScheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 120 });
  const payloadSuccess = `BrowserRT ${REVISION} mixed late success ledger payload`;
  const payloadFailure = `BrowserRT ${REVISION} mixed late failure ledger payload`;
  const digestSuccess = `sha256:${await digestBytesHex(bytes(payloadSuccess))}`;
  const digestFailure = `sha256:${await digestBytesHex(bytes(payloadFailure))}`;

  const acceptedSuccess = sourceAdapter.schedulePut(payloadSuccess, { id: 'mixed-late-success-put', label: 'mixed-late-success', priority: 'user-visible' });
  const acceptedFailure = sourceAdapter.schedulePut(payloadFailure, { id: 'mixed-late-failure-put', label: 'mixed-late-failure', priority: 'user-visible' });
  const dispatchSuccess = sourceScheduler.dispatchNext();
  const dispatchFailure = sourceScheduler.dispatchNext();
  const [timeoutSuccess, timeoutFailure] = await Promise.all([sourceAdapter.executor.executeDispatched(dispatchSuccess), sourceAdapter.executor.executeDispatched(dispatchFailure)]);
  const committedSuccess = await sourceStore.has(digestSuccess);
  const committedFailure = await sourceStore.has(digestFailure);
  const sourceAfterTimeouts = sourceAdapter.snapshot();
  const exportBeforeSettle = sourceAdapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'source-export-before-late-settlement' });

  sourceStore.releases.get('success').resolve('release-success');
  sourceStore.releases.get('failure').resolve('release-failure');
  const sourceSettled = await sourceAdapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 500, intervalMs: 5 });
  const sourceQuarantine = sourceAdapter.timedOutOperationQuarantine('storage');
  const ledger = sourceAdapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'source-export-mixed-late-outcome-quarantine' });
  const verifySuccessAfterLate = await sourceStore.verify(digestSuccess);
  const verifyFailureAfterLate = await sourceStore.verify(digestFailure);

  const importTrace = new TraceLog();
  const importedScheduler = makeScheduler(`${REVISION}-quarantine-ledger-imported-scheduler`, importTrace);
  const importedStore = makeMixedLateStore({ trace: importTrace, mode: 'imported' });
  const importedAdapter = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-ledger-imported-adapter`, store: importedStore, scheduler: importedScheduler, trace: importTrace, lane: 'storage', defaultOperationTimeoutMs: 120 });
  const importResult = importedAdapter.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'import-mixed-late-outcome-quarantine', markUnhealthy: true });
  const importedQuarantine = importedAdapter.timedOutOperationQuarantine('storage');
  const importedLaneAfterImport = importedAdapter.snapshot().executor.scheduler.lanes.find((lane) => lane.id === 'storage');
  const blockedImportedRecovery = await importedAdapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'imported-quarantine-blocks-recovery' });
  const rejectedWhileImportedQuarantined = importedAdapter.schedulePut('must-not-queue-while-imported-quarantine-active', { id: 'reject-while-imported-quarantine-active' });

  const unreviewedUnifiedClear = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reason: 'unreviewed-unified-clear' });
  const missingTokenUnifiedClear = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reviewed: true, reason: 'missing-token-unified-clear' });
  const unscopedUnifiedClear = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', reviewed: true, reviewToken: 'rev0073-mixed-unscoped-review', reason: 'unscoped-unified-clear' });
  const clearSuccessOnly = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'successful', opId: 'mixed-late-success-put', reviewed: true, reviewToken: 'rev0073-review-success-only', reason: 'review-one-late-success-only' });
  const blockedAfterSuccessOnly = await importedAdapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'failure-still-quarantined-after-success-clear' });
  const clearRemaining = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', opIds: ['mixed-late-success-put', 'mixed-late-failure-put'], reviewed: true, reviewToken: 'rev0073-reviewed-mixed-outcome-quarantine', reason: 'reviewed-scoped-mixed-outcome-quarantine-clear' });
  const recoveredAfterClear = await importedAdapter.recoverWhenStoreSettled({ timeoutMs: 100, intervalMs: 5, reason: 'imported-quarantine-reviewed-recovery' });
  const recoveredSchedule = importedAdapter.schedulePut('BrowserRT mixed outcome quarantine ledger recovered write', { id: 'ledger-roundtrip-recovered-put', label: 'recovered-after-ledger-clear', priority: 'user-visible' });
  const recoveryDrain = await importedAdapter.drain({ maxSteps: 3 });
  const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'ledger-roundtrip-recovered-put');
  const recoveredVerify = recoveredResult?.result?.ref ? await importedStore.verify(recoveredResult.result.ref) : null;
  const finalSnapshot = importedAdapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = [...new Set([...trace.kinds(), ...importTrace.kinds()])];

  assert.equal(acceptedSuccess.accepted, true); assert.equal(acceptedFailure.accepted, true);
  assert.equal(dispatchSuccess.dispatched, true); assert.equal(dispatchFailure.dispatched, true);
  assert.equal(timeoutSuccess.ok, false); assert.equal(timeoutFailure.ok, false);
  assert.equal(timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(committedSuccess, true); assert.equal(committedFailure, true);
  assert.equal(sourceAfterTimeouts.executor.unsettledTimedOutOperationCount, 2);
  assert.equal(exportBeforeSettle.schema, 'brt.storageLane.timedOutOperationQuarantine.v1');
  assert.equal(exportBeforeSettle.counts.unsettled, 2);
  assert.equal(sourceSettled.ok, true);
  assert.equal(sourceQuarantine.successfulCount, 1); assert.equal(sourceQuarantine.failedCount, 1); assert.equal(sourceQuarantine.unsettledCount, 0);
  assert.equal(ledger.schema, 'brt.storageLane.timedOutOperationQuarantine.v1');
  assert.equal(ledger.counts.successful, 1); assert.equal(ledger.counts.failed, 1); assert.equal(ledger.counts.total, 2);
  assert.equal(verifySuccessAfterLate.ok, true); assert.equal(verifyFailureAfterLate.ok, true);
  assert.equal(importResult.ok, true); assert.equal(importResult.importedCount, 2); assert.equal(importResult.successfulCount, 1); assert.equal(importResult.failedCount, 1); assert.deepEqual(importResult.affectedLanes, ['storage']);
  assert.equal(importedQuarantine.successfulCount, 1); assert.equal(importedQuarantine.failedCount, 1); assert.equal(importedQuarantine.totalCount, 2);
  assert.equal(importedLaneAfterImport.healthy, false); assert.equal(importedLaneAfterImport.healthReason, 'timed-out-operation-quarantine-imported');
  assert.equal(blockedImportedRecovery.recovered, false); assert.equal(blockedImportedRecovery.reason, 'timed-out-operation-late-success');
  assert.equal(rejectedWhileImportedQuarantined.accepted, false); assert.equal(rejectedWhileImportedQuarantined.scheduler.noMutation, true);
  assert.equal(unreviewedUnifiedClear.ok, false); assert.equal(unreviewedUnifiedClear.code, 'timed-out-quarantine-clear-review-required');
  assert.equal(missingTokenUnifiedClear.ok, false); assert.equal(missingTokenUnifiedClear.code, 'timed-out-quarantine-clear-review-token-required');
  assert.equal(unscopedUnifiedClear.ok, false); assert.equal(unscopedUnifiedClear.code, 'timed-out-quarantine-clear-scope-required');
  assert.equal(clearSuccessOnly.ok, true); assert.equal(clearSuccessOnly.successfulClearedCount, 1); assert.equal(clearSuccessOnly.failedClearedCount, 0);
  assert.equal(blockedAfterSuccessOnly.recovered, false); assert.equal(blockedAfterSuccessOnly.reason, 'timed-out-operation-late-failure');
  assert.equal(clearRemaining.ok, true); assert.equal(clearRemaining.clearedCount, 1); assert.equal(clearRemaining.failedClearedCount, 1); assert.equal(clearRemaining.quarantine.totalCount, 0);
  assert.equal(recoveredAfterClear.recovered, true); assert.equal(recoveredSchedule.accepted, true); assert.equal(recoveredResult?.ok, true); assert.equal(recoveredVerify?.ok, true);
  assert.equal(finalSnapshot.timedOutOperationQuarantine.totalCount, 0); assert.equal(finalSnapshot.executor.timedOutOperationQuarantineCount, 0); assert.equal(finalSnapshot.executor.stats.quarantineLedgerImports, 1); assert.equal(finalSnapshot.executor.stats.timedOutOperationQuarantineCleared, 2); assert.equal(validation.ok, true, validation.errors.join('; '));
  for (const kind of ['storage-lane:timed-out-quarantine-export', 'storage-lane:timed-out-quarantine-import', 'storage-lane:timed-out-quarantine-clear-rejected', 'storage-lane:timed-out-quarantine-cleared']) assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-quarantine-ledger-roundtrip-proof`, task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier proof that mixed late-success and late-failure timeout quarantine ledgers export with schema, import into a fresh lane, block recovery, reject unsafe unified clears, and recover only after reviewed/scoped clearing.',
    observations: { acceptedSuccess, acceptedFailure, dispatchSuccess, dispatchFailure, timeoutSuccess, timeoutFailure, committedSuccess, committedFailure, sourceAfterTimeouts, exportBeforeSettle, sourceSettled, sourceQuarantine, ledger, verifySuccessAfterLate, verifyFailureAfterLate, importResult, importedQuarantine, importedLaneAfterImport, blockedImportedRecovery, rejectedWhileImportedQuarantined, unreviewedUnifiedClear, missingTokenUnifiedClear, unscopedUnifiedClear, clearSuccessOnly, blockedAfterSuccessOnly, clearRemaining, recoveredAfterClear, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, validation, traceKinds },
    claimsChecked: [
      'Timed-out provider operations can settle into both late-success and late-failure quarantine buckets',
      'Quarantine ledger export carries schema and all three buckets instead of losing mixed state',
      'Quarantine ledger import marks the storage lane unhealthy and blocks recovery',
      'Unified quarantine clearing requires review, review token, and scope',
      'Clearing only one mixed outcome bucket does not reopen the lane while the other remains quarantined'
    ],
    nonClaims: [
      'Synthetic provider proof only; browser OPFS/Web Locks proof is separate.',
      'Timeout quarantine export/import is not cancellation, rollback, exactly-once, durability, or production-operator workflow evidence.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-ledger-roundtrip-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed quarantine ledger proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[storage_lane_quarantine_ledger_roundtrip_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
