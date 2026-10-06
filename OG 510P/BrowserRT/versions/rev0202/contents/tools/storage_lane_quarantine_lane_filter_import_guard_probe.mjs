#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createBlockStoreLaneAdapter, createCrossLaneScheduler, digestBytesHex } from '../src/browserrt.mjs';
import { timedOutQuarantineFingerprint } from '../src/storage-lane-scheduler.mjs';

const TASK_ID = 'scheduler:storage-lane-quarantine-lane-filter-import-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-LANE-FILTER-IMPORT-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function bytes(value) {
  if (value instanceof Uint8Array) return new Uint8Array(value);
  if (value instanceof ArrayBuffer) return new Uint8Array(value.slice(0));
  if (ArrayBuffer.isView(value)) return new Uint8Array(value.buffer.slice(value.byteOffset, value.byteOffset + value.byteLength));
  return new TextEncoder().encode(String(value));
}
function operationReplayKey({ lane, kind = 'put', operationEpoch, opId }) {
  return operationEpoch ? `operation:${lane}:${kind}:${operationEpoch}:${opId}` : `operation-legacy:${lane}:${kind}:${opId}`;
}
function makeSuccessRow({ opId, lane, epoch, label }) {
  return Object.freeze({ opId, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: operationReplayKey({ lane, kind: 'put', operationEpoch: epoch, opId }), timeoutMs: 75, timedOutAtMs: 1710000000000, settledAtMs: 1710000000123, result: Object.freeze({ digest: `sha256:${label}`, bytes: label.length, disposition: 'synthetic-late-success' }) });
}
function withFingerprint(ledger) {
  const fp = timedOutQuarantineFingerprint(ledger);
  return Object.freeze({ ...ledger, quarantineFingerprint: fp, reviewFingerprint: fp });
}
function makeLedger({ rows, lane = null, reason = 'synthetic-lane-filter-import-guard-ledger' }) {
  return withFingerprint({
    schema: 'brt.storageLane.timedOutOperationQuarantine.v1',
    reason,
    label: `${REVISION}-lane-filter-ledger`,
    exportedAtMs: Date.now(),
    lane,
    counts: Object.freeze({ total: rows.length, unsettled: 0, successful: rows.length, failed: 0 }),
    unsettledTimedOutOperations: Object.freeze([]),
    successfulTimedOutOperations: Object.freeze(rows),
    failedTimedOutOperations: Object.freeze([])
  });
}
function scheduler(label, trace) {
  return createCrossLaneScheduler({ label, trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
}
function makeStore({ trace = null } = {}) {
  const records = new Map();
  return {
    name: 'synthetic-lane-filter-import-guard-store', provider: 'synthetic-lane-filter-import-guard-provider-v0',
    async put(payload, fields = {}) { const body = bytes(payload); const hash = await digestBytesHex(body); const digest = `sha256:${hash}`; records.set(digest, body); trace?.emit('synthetic-lane-filter:put', { digest, label: fields.label ?? null, bytes: body.byteLength }); return Object.freeze({ ref: { kind: 'block', id: `block:${digest}`, digest, hash, backend: this.provider, bytes: body.byteLength }, digest, hash, bytes: body.byteLength }); },
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
function makeAdapter(label, store, trace) { return createBlockStoreLaneAdapter({ label, store, scheduler: scheduler(`${label}:scheduler`, trace), trace, lane: 'storage', defaultOperationTimeoutMs: 0 }); }

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const store = makeStore({ trace });
  const storageRow = makeSuccessRow({ opId: 'same-visible-op', lane: 'storage', epoch: 'epoch-storage-A', label: 'storage-row' });
  const archiveRow = makeSuccessRow({ opId: 'archive-visible-op', lane: 'archive', epoch: 'epoch-archive-A', label: 'archive-row' });
  const archiveOnlyLedger = makeLedger({ rows: [archiveRow], lane: 'archive', reason: 'archive-only-ledger' });
  const mixedLedger = makeLedger({ rows: [storageRow, archiveRow], lane: null, reason: 'mixed-storage-archive-ledger' });

  const wrongLane = makeAdapter(`${REVISION}-lane-filter-wrong`, store, trace);
  const wrongLaneImport = wrongLane.importTimedOutOperationQuarantine(archiveOnlyLedger, { lane: 'storage', markUnhealthy: false, reason: 'wrong-lane-no-match' });
  assert.equal(wrongLaneImport.ok, false);
  assert.equal(wrongLaneImport.disposition, 'rejected-lane-filter-empty-import');
  assert.equal(wrongLane.timedOutOperationQuarantine('storage').totalCount, 0);
  assert.equal(wrongLane.scheduler.snapshotLane('storage').healthy, true);

  const partialDefault = makeAdapter(`${REVISION}-lane-filter-partial-default`, store, trace);
  const partialDefaultImport = partialDefault.importTimedOutOperationQuarantine(mixedLedger, { lane: 'storage', markUnhealthy: false, reason: 'mixed-lane-default-reject' });
  assert.equal(partialDefaultImport.ok, false);
  assert.equal(partialDefaultImport.disposition, 'rejected-lane-filter-partial-import');
  assert.equal(partialDefaultImport.importedCount, 1);
  assert.equal(partialDefaultImport.filteredOutCount, 1);
  assert.equal(partialDefault.timedOutOperationQuarantine('storage').totalCount, 0);
  assert.equal(partialDefault.scheduler.snapshotLane('storage').healthy, true);

  const partialAllowed = makeAdapter(`${REVISION}-lane-filter-partial-allowed`, store, trace);
  const partialAllowedImport = partialAllowed.importTimedOutOperationQuarantine(mixedLedger, { lane: 'storage', markUnhealthy: false, allowPartialImport: true, reason: 'mixed-lane-explicit-partial-import' });
  assert.equal(partialAllowedImport.ok, true);
  assert.equal(partialAllowedImport.importedCount, 1);
  assert.equal(partialAllowedImport.filteredOutCount, 1);
  assert.equal(partialAllowedImport.markUnhealthyForced, true);
  assert.equal(partialAllowed.scheduler.snapshotLane('storage').healthy, false);
  assert.equal(partialAllowed.timedOutOperationQuarantine('storage').successfulTimedOutOperationCount, 1);

  const review = partialAllowed.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opIds: [storageRow.opId], reviewer: 'rev0084-lane-filter-probe', reviewToken: 'lane-filter-storage-row-review', reason: 'review-explicit-partial-import' });
  const clear = partialAllowed.clearTimedOutOperationQuarantine({ reviewManifest: review, requireReviewFingerprint: true, reason: 'clear-explicit-partial-import' });
  assert.equal(clear.ok, true);
  assert.equal(clear.clearedCount, 1);
  const recovery = await partialAllowed.recoverWhenStoreSettled({ lane: 'storage', reason: 'recover-after-explicit-partial-clear' });
  assert.equal(recovery.recovered, true);
  const put = partialAllowed.schedulePut(`${REVISION}:lane-filter-post-recovery`, { id: 'lane-filter-post-recovery-put', label: 'lane-filter-post-recovery' });
  assert.equal(put.accepted, true);
  const drained = await partialAllowed.executeNext();
  assert.equal(drained.ok, true);
  const verify = await store.verify(drained.result.ref || drained.result);
  assert.equal(verify.ok, true);

  const traceKinds = trace.snapshot().map((row) => row.kind);
  assert.ok(traceKinds.includes('storage-lane:timed-out-quarantine-import-lane-filter-rejected'));
  assert.ok(traceKinds.includes('storage-lane:timed-out-quarantine-import-partial-allowed'));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-storage-lane-quarantine-lane-filter-import-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-light proof that non-empty timeout-quarantine ledgers cannot be silently ignored or partially restored by lane-filtered import unless partial import is explicit.',
    observations: { wrongLaneImport, wrongLaneHealth: wrongLane.scheduler.snapshotLane('storage'), partialDefaultImport, partialDefaultHealth: partialDefault.scheduler.snapshotLane('storage'), partialAllowedImport, partialAllowedHealth: partialAllowed.scheduler.snapshotLane('storage'), review, clear, recovery, postRecoveryPut: drained, verify, traceKinds },
    claimsChecked: ['wrong-lane non-empty timeout quarantine import rejects with no mutation', 'mixed-lane import rejects by default instead of silently dropping filtered rows', 'explicit partial import forces backpressure and still requires reviewed scoped clearing before recovery', 'later write verifies after explicit recovery'],
    nonClaims: ['Synthetic release-light proof only; real OPFS/Web Locks are covered by the browser proof.', 'Lane-filter import guard is not cryptographic attestation, tamper-proof storage, provider cancellation, rollback, or production readiness.']
  });
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-storage-lane-quarantine-lane-filter-import-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed lane-filter import guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_lane_filter_import_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
