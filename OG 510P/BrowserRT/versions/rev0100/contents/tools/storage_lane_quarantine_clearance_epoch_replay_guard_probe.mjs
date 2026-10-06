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
  validateTimedOutOperationQuarantineClearanceReceipt
} from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-clearance-epoch-replay-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-CLEARANCE-EPOCH-REPLAY-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function deferred() { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; }
function bytes(value) { if (value instanceof Uint8Array) return new Uint8Array(value); if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0)); if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength)); return new TextEncoder().encode(String(value)); }
function codedError(code, message, detail = {}) { const e = new Error(message); e.name = 'BrowserRTEpochReplayGuardSyntheticError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; }
function scheduler(label, trace) { return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] }); }
function makeStore({ trace = null } = {}) {
  const records = new Map();
  const releases = new Map();
  const state = { puts: 0, lateSuccesses: 0, lateFailures: 0 };
  const releaseFor = (label) => { if (!releases.has(label)) releases.set(label, deferred()); return releases.get(label); };
  return {
    name: 'synthetic-clearance-epoch-replay-guard-store', provider: 'synthetic-clearance-epoch-replay-guard-provider-v0', state, releaseFor,
    async put(payload, fields = {}) {
      const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`;
      records.set(digest, body); state.puts += 1;
      const label = String(fields.label || '');
      trace?.emit('synthetic-clearance-epoch-replay-guard:put', { digest, bytes: body.byteLength, label });
      const ref = Object.freeze({ kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength });
      if (label.includes('late-success')) { await releaseFor(label).promise; state.lateSuccesses += 1; }
      if (label.includes('late-failure')) { await releaseFor(label).promise; state.lateFailures += 1; throw codedError('BRT_SYNTHETIC_EPOCH_REPLAY_LATE_FAILURE', 'synthetic epoch replay guard late failure after committed block', { digest }); }
      return Object.freeze({ ref, digest, hash, bytes: body.byteLength, duplicate: false, label });
    },
    async get(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); if (!row) throw new Error(`missing block ${digest}`); return new Uint8Array(row); },
    async has(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.has(digest); },
    async verify(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; const row = records.get(digest); return Object.freeze({ ok: Boolean(row), present: Boolean(row), digest, bytes: row?.byteLength ?? 0 }); },
    async delete(ref) { const digest = typeof ref === 'string' ? ref : ref?.digest ?? ref?.ref?.digest; return records.delete(digest); },
    async estimate() { return Object.freeze({ quota: null, usage: [...records.values()].reduce((sum, row) => sum + row.byteLength, 0), usageDetails: { synthetic: records.size } }); },
    async cleanupForTest() { const had = records.size > 0; records.clear(); return had; },
    async waitForSettled({ timeoutMs = 1000 } = {}) { return Object.freeze({ ok: true, elapsedMs: 0, timeoutMs, last: { heldCount: 0, pendingCount: 0, available: true }, reason: 'synthetic-settled' }); },
    snapshot() { return Object.freeze({ name: this.name, provider: this.provider, available: true, opened: true, blockCount: records.size, stats: { ...state } }); }
  };
}
function makeAdapter(label, store, trace, timeoutMs = 80) { return createBlockStoreLaneAdapter({ label, store, scheduler: scheduler(`${label}:scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: timeoutMs }); }
function withFingerprint(ledger) { const quarantineFingerprint = timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint, reviewFingerprint: quarantineFingerprint }); }
function statusRewriteLedger(staleLedger, { dropEpoch = false } = {}) {
  const source = (staleLedger.failedTimedOutOperations || [])[0] || (staleLedger.successfulTimedOutOperations || [])[0];
  if (!source) throw new Error('status rewrite requires a source row');
  const rewritten = {
    opId: source.opId,
    kind: source.kind || 'put',
    lane: source.lane || 'storage',
    timeoutMs: Number(source.timeoutMs || 80),
    timedOutAtMs: Number(source.timedOutAtMs || Date.now()),
    settledAtMs: Date.now() + 23,
    result: Object.freeze({ digest: 'sha256:epoch-replay-status-rewrite', bytes: 31, disposition: 'synthetic-status-rewrite-success' })
  };
  if (!dropEpoch) { rewritten.operationEpoch = source.operationEpoch ?? null; rewritten.operationReplayKey = source.operationReplayKey ?? null; }
  return withFingerprint({ ...staleLedger, reason: dropEpoch ? 'status-rewrite-with-operation-epoch-stripped' : 'status-rewrite-with-operation-epoch-preserved', counts: Object.freeze({ total: 1, successful: 1, failed: 0, unsettled: 0 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([Object.freeze(rewritten)]), failedTimedOutOperations: Object.freeze([]) });
}
async function createTimedOutLedger({ adapter, store, idPrefix, payloadPrefix }) {
  const successLabel = `${idPrefix}-late-success`;
  const failureLabel = `${idPrefix}-late-failure`;
  adapter.schedulePut(`${payloadPrefix}:success`, { id: 'shared-timeout-success-op', label: successLabel });
  adapter.schedulePut(`${payloadPrefix}:failure`, { id: 'shared-timeout-failure-op', label: failureLabel });
  const d1 = adapter.scheduler.dispatchNext(); const d2 = adapter.scheduler.dispatchNext();
  const [t1, t2] = await Promise.all([adapter.executor.executeDispatched(d1), adapter.executor.executeDispatched(d2)]);
  assert.equal(t1.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(t2.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  store.releaseFor(successLabel).resolve('release-success');
  store.releaseFor(failureLabel).resolve('release-failure');
  const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5 });
  assert.equal(settled.ok, true);
  const quarantine = adapter.timedOutOperationQuarantine('storage');
  assert.equal(quarantine.successfulTimedOutOperationCount, 1);
  assert.equal(quarantine.failedTimedOutOperationCount, 1);
  assert.ok(quarantine.successfulTimedOutOperations.every((row) => row.operationEpoch && row.operationReplayKey));
  assert.ok(quarantine.failedTimedOutOperations.every((row) => row.operationEpoch && row.operationReplayKey));
  const ledger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: `${idPrefix}-export-before-clear` });
  return { t1, t2, settled, quarantine, ledger, successLabel, failureLabel };
}

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const original = makeAdapter(`${REVISION}-epoch-replay-original`, store, trace, 80);
  const originalRun = await createTimedOutLedger({ adapter: original, store, idPrefix: 'epoch-original', payloadPrefix: `${REVISION}:epoch-original` });
  const staleLedger = originalRun.ledger;
  const statusRewritePreserved = statusRewriteLedger(staleLedger, { dropEpoch: false });
  const statusRewriteDowngrade = statusRewriteLedger(staleLedger, { dropEpoch: true });
  const reviewManifest = original.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0082-release-probe', reviewToken: 'epoch-replay-review-token', reason: 'review-before-epoch-replay-guard' });
  const clearResult = original.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'clear-for-epoch-replay-guard' });
  assert.equal(clearResult.ok, true);
  const receipt = original.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0082-release-probe', label: 'epoch-replay-receipt' });
  const validation = validateTimedOutOperationQuarantineClearanceReceipt(receipt);
  assert.equal(validation.ok, true);
  assert.ok(receipt.cleared.successful.concat(receipt.cleared.failed).every((row) => row.operationEpoch && row.operationReplayKey));
  const persisted = await original.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label: 'epoch-replay-receipt-persisted' });
  assert.equal(persisted.ok, true);

  const fresh = makeAdapter(`${REVISION}-epoch-replay-fresh`, store, trace, 1000);
  const restored = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane: 'storage' });
  assert.equal(restored.ok, true);
  assert.equal(restored.registration.ok, true);
  const exactReplay = fresh.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'epoch-exact-stale-replay', markUnhealthy: false });
  assert.equal(exactReplay.ok, false);
  assert.equal(exactReplay.disposition, 'rejected-cleared-quarantine-replay');
  const preservedReplay = fresh.importTimedOutOperationQuarantine(statusRewritePreserved, { lane: 'storage', reason: 'epoch-status-rewrite-preserved-replay', markUnhealthy: false });
  assert.equal(preservedReplay.ok, false);
  assert.equal(preservedReplay.disposition, 'rejected-cleared-quarantine-row-replay');
  const downgradeReplay = fresh.importTimedOutOperationQuarantine(statusRewriteDowngrade, { lane: 'storage', reason: 'epoch-stripped-downgrade-replay', markUnhealthy: false });
  assert.equal(downgradeReplay.ok, false);
  assert.equal(downgradeReplay.disposition, 'rejected-cleared-quarantine-row-replay-downgrade');
  assert.ok(downgradeReplay.matchedRows.some((row) => row.replayKind === 'cleared-operation-identity-downgrade'));

  const collision = makeAdapter(`${REVISION}-epoch-replay-collision`, store, trace, 80);
  const collisionRun = await createTimedOutLedger({ adapter: collision, store, idPrefix: 'epoch-collision', payloadPrefix: `${REVISION}:epoch-collision` });
  const collisionLedger = collisionRun.ledger;
  assert.notEqual(collisionLedger.quarantineFingerprint, staleLedger.quarantineFingerprint);
  assert.notEqual(collisionLedger.successfulTimedOutOperations[0].operationReplayKey, staleLedger.successfulTimedOutOperations[0].operationReplayKey);
  const collisionImport = fresh.importTimedOutOperationQuarantine(collisionLedger, { lane: 'storage', reason: 'epoch-collision-import-same-opids-new-epoch', markUnhealthy: false });
  assert.equal(collisionImport.ok, true);
  assert.equal(collisionImport.markUnhealthyForced, true);
  const freshLaneAfterCollisionImport = fresh.scheduler.snapshotLane('storage');
  assert.equal(freshLaneAfterCollisionImport.healthy, false);
  const freshQuarantineAfterCollisionImport = fresh.timedOutOperationQuarantine('storage');
  assert.equal(freshQuarantineAfterCollisionImport.totalCount, 2);
  const collisionReview = fresh.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0082-release-probe', reviewToken: 'epoch-collision-clear-token', reason: 'review-collision-quarantine' });
  const collisionClear = fresh.clearTimedOutOperationQuarantine({ reviewManifest: collisionReview, requireReviewFingerprint: true, reason: 'clear-collision-quarantine' });
  assert.equal(collisionClear.ok, true);
  assert.equal(collisionClear.clearedCount, 2);
  const recovered = await fresh.recoverWhenStoreSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 5, reason: 'epoch-collision-cleared-recovery' });
  assert.equal(recovered.recovered, true);
  const write = fresh.schedulePut(`${REVISION}:epoch-replay-after-collision`, { id: 'epoch-replay-after-collision-put', label: 'epoch-replay-after-collision', operationTimeoutMs: 1000 });
  assert.equal(write.accepted, true);
  const drain = await fresh.drain({ maxSteps: 3 });
  const writeResult = drain.results.find((row) => row.opId === 'epoch-replay-after-collision-put');
  assert.equal(writeResult?.ok, true);
  const writeVerify = await store.verify(writeResult.result.ref);
  assert.equal(writeVerify.ok, true);
  const traceKinds = trace.kinds();
  for (const kind of ['storage-lane:timed-out-quarantine-import-row-replay-rejected', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'block-store-lane:recover-settled']) assert.ok(traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-epoch-replay-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Release-tier proof that timeout-quarantine clearance row replay guards are bound to operation epochs: stale rows replay, epoch-stripped downgrade rejects, but a fresh same-opId timeout ledger with a new operation epoch imports/backpressures normally.', observations: { originalRun, staleLedger, statusRewritePreserved, statusRewriteDowngrade, reviewManifest, clearResult, receipt, validation, persisted, restored, exactReplay, preservedReplay, downgradeReplay, collisionRun, collisionLedger, collisionImport, freshLaneAfterCollisionImport, freshQuarantineAfterCollisionImport, collisionReview, collisionClear, recovered, writeResult, writeVerify, stats: fresh.snapshot().stats, executorStats: fresh.snapshot().executor.stats, traceKinds }, claimsChecked: ['timed-out quarantine rows carry operationEpoch and operationReplayKey', 'stale exact cleared ledger replay remains rejected', 'status-rewritten stale rows with original operation epoch reject by operation replay key', 'epoch-stripped stale rows reject as downgrade replay', 'fresh same-opId timeout quarantine with a different operation epoch is not mistaken for stale replay', 'collision import still forces backpressure and requires reviewed clearing before recovery'], nonClaims: ['Browser-light synthetic provider only; no OPFS, Web Locks, cross-browser, durability, quota, eviction, or production claim.', 'Operation epochs are collision-avoidance/replay-scoping markers, not cryptographic identity or attestation.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, SLO, or production readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-clearance-epoch-replay-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed epoch replay guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_clearance_epoch_replay_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
