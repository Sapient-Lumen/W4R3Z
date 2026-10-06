#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-ledger-persistence-integrity-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-LEDGER-PERSISTENCE-INTEGRITY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function jsonBytes(value) { return new TextEncoder().encode(JSON.stringify(value, null, 2) + '\n'); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTSyntheticQuarantinePersistenceIntegrityError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }

function makeStore({ trace = null } = {}) {
  const records = new Map(); const releaseSuccess = deferred(); const releaseFailure = deferred();
  const state = { puts: 0, lateSuccesses: 0, lateFailures: 0, ledgerPuts: 0, corruptLedgerPuts: 0, waitForSettledCalls: 0 };
  return { name: 'synthetic-quarantine-ledger-persistence-store', provider: 'synthetic-quarantine-ledger-persistence-provider-v0', releaseSuccess, releaseFailure, state,
    async put(payload, fields = {}) { const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; records.set(digest, body); state.puts += 1; if (fields.purpose === 'timed-out-operation-quarantine-ledger') state.ledgerPuts += 1; if (fields.purpose === 'malformed-timed-out-operation-quarantine-ledger') state.corruptLedgerPuts += 1; trace?.emit('synthetic-quarantine-ledger-persistence:put', { digest, bytes: body.byteLength, label: fields.label ?? null, purpose: fields.purpose ?? null }); const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null }); if (fields.label === 'persistence-integrity-late-success') { await releaseSuccess.promise; state.lateSuccesses += 1; } if (fields.label === 'persistence-integrity-late-failure') { await releaseFailure.promise; state.lateFailures += 1; throw codedError('BRT_SYNTHETIC_LATE_PROVIDER_FAILURE', 'synthetic late failure after committed block', { digest }); } return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label: fields.label ?? null }); },
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
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }

export async function runProbe() {
  const started = performance.now(); const trace = new TraceLog(); const store = makeStore({ trace });
  const source = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-ledger-persistence-source`, store, scheduler: scheduler(`${REVISION}-qlpi-source-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 100 });
  source.schedulePut(`${REVISION}:quarantine-ledger-persistence-success`, { id: 'qlpi-success-timeout', label: 'persistence-integrity-late-success' });
  source.schedulePut(`${REVISION}:quarantine-ledger-persistence-failure`, { id: 'qlpi-failure-timeout', label: 'persistence-integrity-late-failure' });
  const d1 = source.scheduler.dispatchNext(); const d2 = source.scheduler.dispatchNext();
  const [r1, r2] = await Promise.all([source.executor.executeDispatched(d1), source.executor.executeDispatched(d2)]);
  assert.equal(r1.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(r2.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  store.releaseSuccess.resolve('release-success'); store.releaseFailure.resolve('release-failure');
  const settled = await source.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  const quarantine = source.timedOutOperationQuarantine('storage');
  const persist = await source.persistTimedOutOperationQuarantine({ lane: 'storage', reason: 'release-tier-persist-quarantine-ledger-with-integrity', label: `${REVISION}-quarantine-ledger-persistence-ledger` });
  const persistedVerify = await store.verify(persist.ref);

  const malformedLedger = { ...source.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'malformed-copy-for-restore-integrity' }), counts: { total: 999, unsettled: 0, successful: 1, failed: 1 } };
  const malformedPut = await store.put(jsonBytes(malformedLedger), { label: 'malformed-persistence-integrity-ledger', purpose: 'malformed-timed-out-operation-quarantine-ledger' });
  const malformedAdapter = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-ledger-persistence-malformed-import`, store, scheduler: scheduler(`${REVISION}-qlpi-malformed-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const malformedRestore = await malformedAdapter.restoreTimedOutOperationQuarantineFromBlockStore(malformedPut.ref, { lane: 'storage', reason: 'release-tier-reject-malformed-persisted-quarantine-ledger' });
  const malformedQuarantine = malformedAdapter.timedOutOperationQuarantine('storage');
  const malformedLane = malformedAdapter.snapshot().executor.scheduler.lanes.find((l) => l.id === 'storage');

  const imported = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-ledger-persistence-imported`, store, scheduler: scheduler(`${REVISION}-qlpi-imported-scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
  const restore = await imported.restoreTimedOutOperationQuarantineFromBlockStore(persist.ref, { lane: 'storage', reason: 'release-tier-restore-valid-persisted-quarantine-ledger' });
  const importedQuarantine = imported.timedOutOperationQuarantine('storage');
  const laneAfterRestore = imported.snapshot().executor.scheduler.lanes.find((l) => l.id === 'storage');
  const rejected = imported.schedulePut(`${REVISION}:must-not-mutate-while-imported-quarantined`, { id: 'qlpi-reject-while-restored' });
  const blocked = await imported.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 5, reason: 'persisted-ledger-blocks-recovery' });
  const clearSuccess = imported.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'successful', opId: 'qlpi-success-timeout', reviewed: true, reviewToken: 'rev0075-persisted-ledger-success-review', reason: 'reviewed-success-clear' });
  const blockedAfterOne = await imported.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 5, reason: 'persisted-ledger-failure-still-blocks' });
  const clearFailure = imported.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'failed', opId: 'qlpi-failure-timeout', reviewed: true, reviewToken: 'rev0075-persisted-ledger-failure-review', reason: 'reviewed-failure-clear' });
  const recovered = await imported.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 5, reason: 'persisted-ledger-reviewed-cleared' });
  const rec = imported.schedulePut(`${REVISION}:quarantine-ledger-persistence-recovered`, { id: 'qlpi-recovered-put', label: 'qlpi-recovered', operationTimeoutMs: 1000 });
  const drain = await imported.drain({ maxSteps: 3 }); const recoveredResult = drain.results.find((row) => row.opId === 'qlpi-recovered-put'); const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const traceKinds = trace.kinds();

  assert.equal(settled.ok, true); assert.equal(quarantine.successfulCount, 1); assert.equal(quarantine.failedCount, 1); assert.equal(persist.ok, true); assert.equal(persistedVerify.ok, true); assert.equal(store.state.ledgerPuts, 1);
  assert.equal(malformedRestore.ok, false); assert.equal(malformedRestore.disposition, 'rejected-ledger-integrity'); assert.equal(malformedQuarantine.totalCount, 0); assert.equal(malformedLane.healthy, true);
  assert.equal(restore.ok, true); assert.equal(restore.importResult.importedCount, 2); assert.equal(importedQuarantine.totalCount, 2); assert.equal(laneAfterRestore.healthy, false); assert.equal(rejected.accepted, false); assert.equal(rejected.scheduler.noMutation, true); assert.equal(blocked.recovered, false); assert.equal(blocked.reason, 'timed-out-operation-late-success'); assert.equal(clearSuccess.ok, true); assert.equal(blockedAfterOne.reason, 'timed-out-operation-late-failure'); assert.equal(clearFailure.ok, true); assert.equal(recovered.recovered, true); assert.equal(rec.accepted, true); assert.equal(recoveredResult?.ok, true); assert.equal(recoveredVerify?.ok, true);
  for (const kind of ['block-store-lane:quarantine-ledger-persisted','block-store-lane:quarantine-ledger-restore-rejected','block-store-lane:quarantine-ledger-restored','storage-lane:timed-out-quarantine-import','storage-lane:timed-out-quarantine-import-rejected']) assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-ledger-persistence-integrity-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that mixed timed-out provider-operation quarantine can be persisted as a provider block, malformed persisted ledgers restore fail-closed/atomic, and valid persisted quarantine still requires reviewed/scoped recovery.', observations: { timeoutResults: [r1, r2], settled, quarantine, persist, persistedVerify, malformedPut, malformedRestore, malformedQuarantine, malformedLane, restore, importedQuarantine, laneAfterRestore, rejected, blocked, clearSuccess, blockedAfterOne, clearFailure, recovered, recoveredResult, recoveredVerify, traceKinds, store: store.snapshot() }, claimsChecked: ['quarantine ledger persists through block-store provider data', 'malformed persisted ledger restore is rejected atomically without poisoning lane health', 'fresh adapter restores valid persisted quarantine as unhealthy/backpressured', 'reviewed/scoped clear is still required before recovery'], nonClaims: ['Synthetic release-tier proof only; not OPFS/Web Locks/cross-browser evidence.', 'Persistence is not cryptographic attestation, provider cancellation, rollback, fsync durability, crash safety, exactly-once, quota, eviction, SLO, or production-readiness evidence.'] };
}
const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-ledger-persistence-integrity-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed quarantine ledger persistence-integrity proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_ledger_persistence_integrity_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
