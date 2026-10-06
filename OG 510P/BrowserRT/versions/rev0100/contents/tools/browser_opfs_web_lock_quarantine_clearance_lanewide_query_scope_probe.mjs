#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-CLEARANCE-LANEWIDE-QUERY-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 11 + (i >>> 1)) & 255; return out; };
    const makeScheduler = (rt, label) => rt.crossLaneScheduler({ label, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const makeLedger = (fingerprintFn, { suffix = 'browser-query-scope', lane = 'storage', opSuffix = suffix, epoch = '${REVISION}-browser-lanewide-query-scope-epoch' } = {}) => { const now = Date.now(); const success = Object.freeze({ opId: '${REVISION}-' + opSuffix + '-late-success', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-' + opSuffix + '-late-success', timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: 'sha256:' + suffix + '-success', bytes: 32, disposition: 'browser-synthetic-late-success' } }); const failed = Object.freeze({ opId: '${REVISION}-' + opSuffix + '-late-failure', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-' + opSuffix + '-late-failure', timeoutMs: 25, timedOutAtMs: now + 2, settledAtMs: now + 3, error: { name: 'BrowserSyntheticLateFailure', message: 'browser synthetic late failure for lane-wide query scope proof', code: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE' } }); const base = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, exportedAtMs: now + 4, label: '${REVISION}-browser-lanewide-query-scope-ledger:' + lane, reason: 'browser-synthetic-lanewide-query-scope-ledger', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failed]) }); const fingerprint = fingerprintFn(base); return Object.freeze({ ...base, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint }); };
    const registrationProvenance = (adapter, receipt) => ({ schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: receipt.lane ?? adapter.lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: adapter.label, store: adapter.storeName, provider: adapter.providerName });
    const m = await import('/src/browserrt.mjs');
    const s = await import('/src/storage-lane-scheduler.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockLaneWideQueryScopeProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-lanewide-query-scope-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-lanewide-query-scope-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const storageLedger = makeLedger(s.timedOutQuarantineFingerprint, { lane: 'storage', suffix: 'storage', opSuffix: 'same-visible-op' });
    const producer = rt.blockStoreLaneAdapter({ label: '${REVISION}-lanewide-query-scope-browser-producer', store: guard, scheduler: makeScheduler(rt, '${REVISION}-lanewide-query-scope-browser-producer-scheduler'), trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const importOriginal = producer.importTimedOutOperationQuarantine(storageLedger, { lane: 'storage', reason: 'browser-import-before-lanewide-query-scope-clear', markUnhealthy: false });
    const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0087-browser-probe', reviewToken: 'browser-lanewide-query-scope-review-token', reason: 'browser-review-before-lanewide-query-scope-clear' });
    const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-for-lanewide-query-scope-receipt' });
    const receipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0087-browser-probe', label: 'browser-lanewide-query-scope-receipt' });
    const freshScheduler = makeScheduler(rt, '${REVISION}-lanewide-query-scope-browser-fresh-scheduler');
    const fresh = rt.blockStoreLaneAdapter({ label: '${REVISION}-lanewide-query-scope-browser-fresh', store: guard, scheduler: freshScheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const register = fresh.executor.registerTimedOutOperationQuarantineClearanceReceipt(receipt, { lane: 'storage', reason: 'browser-register-lanewide-query-scope-receipt', provenance: registrationProvenance(fresh, receipt) });
    const allReceipts = fresh.executor.clearedTimedOutOperationQuarantineClearanceReceipts(null);
    const storageReceipts = fresh.clearedTimedOutOperationQuarantineClearanceReceipts('storage');
    const maintenanceReceipts = fresh.clearedTimedOutOperationQuarantineClearanceReceipts('maintenance');
    const storageReplay = fresh.importTimedOutOperationQuarantine(storageLedger, { lane: 'storage', reason: 'browser-storage-replay-after-storage-receipt', markUnhealthy: false });
    const maintenanceLedger = makeLedger(s.timedOutQuarantineFingerprint, { lane: 'maintenance', suffix: 'maintenance', opSuffix: 'same-visible-op', epoch: '${REVISION}-browser-lanewide-query-scope-maintenance-epoch' });
    const maintenanceImport = fresh.importTimedOutOperationQuarantine(maintenanceLedger, { lane: 'maintenance', reason: 'browser-maintenance-import-must-not-be-suppressed-by-storage-lanewide-receipt', markUnhealthy: false });
    const maintenanceLane = freshScheduler.snapshotLane('maintenance');
    const maintenanceQuarantine = fresh.timedOutOperationQuarantine('maintenance');
    const maintenanceReceiptsAfterMaintenance = fresh.clearedTimedOutOperationQuarantineClearanceReceipts('maintenance');
    const storageReceiptsAfterMaintenance = fresh.clearedTimedOutOperationQuarantineClearanceReceipts('storage');
    const recoveryPayload = bytesFromSeed('${REVISION}:browser-lanewide-query-scope-recovery', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'browser-lanewide-query-scope-recovery-put' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const locksAfterCleanup = await guard.queryLocks();
    const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, importOriginal, clearResult, receipt: { lane: receipt.lane, allowLaneWide: receipt.allowLaneWide, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint }, register, allReceiptCount: allReceipts.length, storageReceiptCount: storageReceipts.length, maintenanceReceiptCount: maintenanceReceipts.length, storageReceiptFromStorageQuery: storageReceipts[0] || null, storageReceiptFromMaintenanceQuery: maintenanceReceipts[0] || null, maintenanceReceiptFromMaintenanceQuery: maintenanceReceiptsAfterMaintenance[0] || null, storageReplay, maintenanceImport, importAfterWrongLaneRegistration: maintenanceImport, maintenanceLane, maintenanceQuarantine, maintenanceReceiptsAfterMaintenance: maintenanceReceiptsAfterMaintenance.length, storageReceiptsAfterMaintenance: storageReceiptsAfterMaintenance.length, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-clearance-lanewide-query-scope';
  const lockName = options.lockName || `${REVISION}-quarantine-clearance-lanewide-query-scope-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 24000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-clearance-lanewide-query-scope.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine clearance lane-wide query scope proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-lanewide-query-scope-', stderrTerms: ['opfs', 'lock', 'quarantine', 'clearance', 'lanewide'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.importOriginal.ok, true); assert.equal(result.importOriginal.markUnhealthyForced, true);
  assert.equal(result.clearResult.ok, true); assert.equal(result.clearResult.allowLaneWide, true); assert.equal(result.clearResult.clearedCount, 2);
  assert.equal(result.receipt.lane, 'storage'); assert.equal(result.receipt.allowLaneWide, true);
  assert.equal(result.register.ok, true);
  assert.equal(result.allReceiptCount, 1); assert.equal(result.storageReceiptCount, 1); assert.equal(result.maintenanceReceiptCount, 0);
  assert.equal(result.storageReplay.ok, false); assert.equal(result.storageReplay.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(result.maintenanceImport.ok, true); assert.equal(result.maintenanceImport.markUnhealthyForced, true); assert.equal(result.maintenanceLane.healthy, false); assert.equal(result.maintenanceQuarantine.totalCount, 2);
  assert.equal(result.maintenanceReceiptsAfterMaintenance, 0); assert.equal(result.storageReceiptsAfterMaintenance, 1);
  assert.equal(result.recoveryVerify.ok, true); assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-clearance-receipt-registered', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that lane-wide timeout-quarantine clearance receipts remain query/replay scoped to their concrete lane over real guarded OPFS/Web Locks.', observations: { ...result, harness }, claimsChecked: ['lane-specific receipt queries do not return lane-wide receipts from other lanes', 'storage stale replay remains rejected by the storage receipt', 'maintenance quarantine with the same visible op ids imports/backpressures rather than being suppressed by the storage receipt', 'later guarded OPFS write verifies'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Lane-wide query scope is deterministic integrity policy, not cryptographic attestation, tamper-proof storage, or access-control security boundary.', 'No provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '24000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser lane-wide query-scope proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_clearance_lanewide_query_scope_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
