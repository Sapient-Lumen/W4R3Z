#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createCrossLaneScheduler, createBlockStoreLaneAdapter, validateBlockStoreLaneAdapterSnapshot, digestBytesHex } from '../src/browserrt.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-ledger-integrity-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-LEDGER-INTEGRITY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function bytes(value) { return value instanceof Uint8Array ? value : new TextEncoder().encode(String(value)); }
function makeScheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] }); }
function makeStore() {
  const records = new Map();
  return {
    name: 'integrity-memory-block-store', provider: 'integrity-memory-provider-v1',
    async put(payload, fields = {}) { const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; records.set(digest, body); return Object.freeze({ ref: Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength, path: null }), digest, hash, bytes: body.byteLength, duplicate: false, fields }); },
    async has(ref) { return records.has(typeof ref === 'string' ? ref : ref?.digest); },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const body = records.get(digest); if (!body) throw new Error(`missing ${digest}`); return new Uint8Array(body); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest; const body = records.get(digest); return Object.freeze({ ok: Boolean(body), present: Boolean(body), digest, bytes: body?.byteLength ?? 0 }); },
    async delete(ref) { return records.delete(typeof ref === 'string' ? ref : ref?.digest); },
    async estimate() { return Object.freeze({ usage: [...records.values()].reduce((n, b) => n + b.byteLength, 0), quota: null, usageDetails: { records: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { return Object.freeze({ ok: true, timeoutMs, elapsedMs: 0, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'integrity-memory-store-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, blockCount: records.size }); }
  };
}
function baseRow(opId, status) { return Object.freeze({ opId, kind: 'put', lane: 'storage', timeoutMs: 125, timedOutAtMs: 1700000000000 + opId.length, settledAtMs: status === 'unsettled' ? undefined : 1700000000500 + opId.length, result: status === 'successful' ? { disposition: 'synthetic-late-success' } : undefined, error: status === 'failed' ? { name: 'SyntheticLateFailure', message: 'synthetic late failure', code: 'BRT_OPFS_OPERATION_FAILED', storageDisposition: 'BRT_OPFS_OPERATION_FAILED' } : undefined }); }
function validLedger() {
  const unsettled = [];
  const successful = [baseRow('integrity-success', 'successful')];
  const failed = [baseRow('integrity-failure', 'failed')];
  return Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', exportedAtMs: 1700000001000, label: `${REVISION}-integrity-ledger-source`, reason: 'synthetic-mixed-integrity-ledger', lane: 'storage', counts: Object.freeze({ total: unsettled.length + successful.length + failed.length, unsettled: unsettled.length, successful: successful.length, failed: failed.length }), unsettledTimedOutOperations: unsettled, successfulTimedOutOperations: successful, failedTimedOutOperations: failed });
}
function deepClone(value) { return JSON.parse(JSON.stringify(value)); }
function badLedgerCases(ledger) {
  const cases = [];
  let l = deepClone(ledger); delete l.counts; cases.push(['missing-counts', l]);
  l = deepClone(ledger); l.counts.total += 1; cases.push(['counts.total mismatch', l]);
  l = deepClone(ledger); delete l.failedTimedOutOperations; cases.push(['missing-failed-array', l]);
  l = deepClone(ledger); l.failedTimedOutOperations[0].opId = l.successfulTimedOutOperations[0].opId; cases.push(['duplicate-opid', l]);
  l = deepClone(ledger); delete l.successfulTimedOutOperations[0].opId; cases.push(['missing-opid', l]);
  l = deepClone(ledger); l.schema = 'brt.storageLane.timedOutOperationQuarantine.v999'; cases.push(['wrong-schema', l]);
  return cases;
}
export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore();
  const scheduler = makeScheduler(`${REVISION}-quarantine-ledger-integrity-scheduler`, trace);
  const adapter = createBlockStoreLaneAdapter({ label: `${REVISION}-quarantine-ledger-integrity-adapter`, store, scheduler, trace, lane: 'storage', defaultOperationTimeoutMs: 100 });
  const ledger = validLedger();
  const badResults = [];
  for (const [name, bad] of badLedgerCases(ledger)) {
    const before = adapter.snapshot();
    const rejected = adapter.importTimedOutOperationQuarantine(bad, { lane: 'storage', reason: `reject-${name}`, markUnhealthy: true });
    const after = adapter.snapshot();
    const laneAfter = after.executor.scheduler.lanes.find((row) => row.id === 'storage');
    assert.equal(rejected.ok, false, `${name} should reject`);
    assert.equal(rejected.code, 'timed-out-quarantine-import-rejected');
    assert.equal(rejected.disposition, 'rejected-ledger-integrity');
    assert.equal(after.timedOutOperationQuarantine.totalCount, before.timedOutOperationQuarantine.totalCount, `${name} must be atomic`);
    assert.equal(after.timedOutOperationQuarantine.totalCount, 0, `${name} must not partially import`);
    assert.equal(laneAfter.healthy, true, `${name} must not mark lane unhealthy`);
    badResults.push(Object.freeze({ name, code: rejected.code, disposition: rejected.disposition, message: rejected.error?.message ?? null, quarantineCount: after.timedOutOperationQuarantine.totalCount, laneHealthy: laneAfter.healthy }));
  }
  const validImport = adapter.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'valid-integrity-import', markUnhealthy: true });
  const imported = adapter.snapshot();
  const importedLane = imported.executor.scheduler.lanes.find((row) => row.id === 'storage');
  const rejectedWhileQuarantined = adapter.schedulePut('must-not-queue-while-integrity-quarantine-active', { id: 'integrity-rejected-while-quarantined' });
  const unsafeClear = adapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reason: 'unsafe-integrity-clear' });
  const partialClear = adapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'successful', opId: 'integrity-success', reviewed: true, reviewToken: `${REVISION}-integrity-success-only`, reason: 'integrity-clear-success-only' });
  const stillBlocked = await adapter.recoverWhenStoreSettled({ timeoutMs: 50, intervalMs: 5, reason: 'integrity-partial-clear-still-blocked' });
  const clearRemaining = adapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', opIds: ['integrity-success','integrity-failure'], reviewed: true, reviewToken: `${REVISION}-integrity-reviewed-scoped-clear`, reason: 'integrity-reviewed-scoped-clear' });
  const recovered = await adapter.recoverWhenStoreSettled({ timeoutMs: 50, intervalMs: 5, reason: 'integrity-recover-after-reviewed-clear' });
  const recoveredSchedule = adapter.schedulePut(`BrowserRT ${REVISION} quarantine ledger integrity recovered write`, { id: 'integrity-recovered-put' });
  const drain = await adapter.drain({ maxSteps: 2 });
  const recoveredResult = drain.results.find((row) => row.opId === 'integrity-recovered-put') || null;
  const recoveredVerify = recoveredResult?.result?.ref ? await store.verify(recoveredResult.result.ref) : null;
  const finalSnapshot = adapter.snapshot();
  const validation = validateBlockStoreLaneAdapterSnapshot(finalSnapshot);
  const traceKinds = trace.snapshot().map((event) => event.kind);
  assert.equal(validImport.ok, true); assert.equal(validImport.importedCount, 2); assert.equal(validImport.disposition, 'timed-out-quarantine-imported');
  assert.equal(imported.timedOutOperationQuarantine.totalCount, 2); assert.equal(importedLane.healthy, false); assert.equal(importedLane.healthReason, 'timed-out-operation-quarantine-imported');
  assert.equal(rejectedWhileQuarantined.accepted, false); assert.equal(rejectedWhileQuarantined.scheduler.noMutation, true);
  assert.equal(unsafeClear.ok, false); assert.equal(unsafeClear.code, 'timed-out-quarantine-clear-review-required');
  assert.equal(partialClear.ok, true); assert.equal(partialClear.successfulClearedCount, 1);
  assert.equal(stillBlocked.recovered, false); assert.notEqual(stillBlocked.reason, 'store-settled-recovered');
  assert.equal(clearRemaining.ok, true); assert.equal(clearRemaining.quarantine.totalCount, 0);
  assert.equal(recovered.recovered, true); assert.equal(recoveredSchedule.accepted, true); assert.equal(recoveredResult?.ok, true); assert.equal(recoveredVerify?.ok, true);
  assert.equal(finalSnapshot.executor.stats.quarantineLedgerImportIntegrityRejected, badResults.length);
  assert.equal(finalSnapshot.executor.stats.quarantineLedgerImports, 1);
  assert.equal(validation.ok, true);
  for (const kind of ['storage-lane:timed-out-quarantine-import-rejected','storage-lane:timed-out-quarantine-import','storage-lane:timed-out-quarantine-cleared']) assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-ledger-integrity-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that timed-out provider-operation quarantine ledger import fails closed and atomic for malformed or ambiguous ledgers, while valid reviewed/scoped handoff still recovers.', observations: { badResults, validImport, importedQuarantine: imported.timedOutOperationQuarantine, importedLane, rejectedWhileQuarantined, unsafeClear, partialClear, stillBlocked, clearRemaining, recovered, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, validation, traceKinds }, claimsChecked: ['malformed ledgers reject without partial import', 'counts.total mismatch and duplicate opIds fail closed', 'valid ledger import marks lane unhealthy and blocks mutation', 'reviewed/scoped clear is still required before recovery'], nonClaims: ['Browser-light synthetic proof only.', 'Ledger integrity validation is not cryptographic attestation, cancellation, rollback, no-mutation-on-timeout, durability, or production readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-ledger-integrity-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed quarantine ledger integrity proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_ledger_integrity_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
