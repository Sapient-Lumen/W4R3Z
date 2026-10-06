#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-clearance-row-replay-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-CLEARANCE-ROW-REPLAY-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 3000, intervalMs = 25, label = 'condition' } = {}) => { const start = performance.now(); let last = null; while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last, label }; await sleep(intervalMs); } return { ok: false, elapsedMs: performance.now() - start, last, label }; };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserClearanceRowReplayProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 17 + (i >>> 2)) & 255; return out; };
    const m = await import('/src/browserrt.mjs');
    const sched = await import('/src/storage-lane-scheduler.mjs');
    const withFingerprint = (ledger) => { const quarantineFingerprint = sched.timedOutQuarantineFingerprint(ledger); return { ...ledger, quarantineFingerprint, reviewFingerprint: quarantineFingerprint }; };
    const modifiedLedgerWithClearedRows = (ledger) => { const successfulTimedOutOperations = [...(ledger.successfulTimedOutOperations || []), { opId: '${REVISION}-browser-clearance-row-replay-extra-timeout', kind: 'put', lane: 'storage', timeoutMs: ${JSON.stringify(operationTimeoutMs)}, timedOutAtMs: Date.now() + 17, settledAtMs: Date.now() + 19, result: { digest: 'sha256:browser-row-replay-extra', bytes: 23, disposition: 'browser-extra-success' } }]; const failedTimedOutOperations = [...(ledger.failedTimedOutOperations || [])]; const unsettledTimedOutOperations = [...(ledger.unsettledTimedOutOperations || [])]; return withFingerprint({ ...ledger, reason: 'browser-modified-stale-ledger-with-cleared-rows-plus-fresh-row', counts: { total: successfulTimedOutOperations.length + failedTimedOutOperations.length + unsettledTimedOutOperations.length, successful: successfulTimedOutOperations.length, failed: failedTimedOutOperations.length, unsettled: unsettledTimedOutOperations.length }, successfulTimedOutOperations, failedTimedOutOperations, unsettledTimedOutOperations }); };
    const modifiedLedgerWithStatusRewrite = (ledger) => { const source = (ledger.failedTimedOutOperations || [])[0] || (ledger.successfulTimedOutOperations || [])[0]; if (!source) throw new Error('browser status rewrite proof requires a cleared row'); const rewritten = { opId: source.opId, kind: source.kind || 'put', lane: source.lane || 'storage', operationEpoch: source.operationEpoch ?? null, operationReplayKey: source.operationReplayKey ?? null, timeoutMs: Number(source.timeoutMs || ${JSON.stringify(operationTimeoutMs)}), timedOutAtMs: Number(source.timedOutAtMs || Date.now()), settledAtMs: Date.now() + 23, result: { digest: 'sha256:browser-row-replay-status-rewrite', bytes: 31, disposition: 'browser-status-rewrite-success' } }; return withFingerprint({ ...ledger, reason: 'browser-modified-stale-ledger-with-cleared-row-status-rewrite', counts: { total: 1, successful: 1, failed: 0, unsettled: 0 }, successfulTimedOutOperations: [rewritten], failedTimedOutOperations: [], unsettledTimedOutOperations: [] }); };
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockQuarantineClearanceRowReplayProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-clearance-row-replay-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-clearance-row-replay-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const scheduler = rt.crossLaneScheduler({ label: '${REVISION}-clearance-row-replay-browser-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const releaseSuccess = deferred(); const releaseFailure = deferred(); const refs = { success: null, failure: null };
    const delayedStore = {
      name: '${REVISION}-clearance-row-replay-delayed-guarded-store', provider: 'clearance-row-replay:' + guard.provider,
      async put(payload, fields = {}) { const put = await guard.put(payload, fields, { timeoutMs: 1000 }); const label = String(fields.label || ''); if (label.includes('success')) { refs.success = put.ref || put; await releaseSuccess.promise; return put; } if (label.includes('failure')) { refs.failure = put.ref || put; await releaseFailure.promise; throw codedError('BRT_BROWSER_CLEARANCE_ROW_REPLAY_LATE_FAILURE', 'browser clearance-row-replay late failure after committed guarded OPFS write', { digest: put.digest, bytes: put.bytes }); } return put; },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); }, async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); }, async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); }, async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); }, async estimate() { return await guard.estimate({ timeoutMs: 1000 }); }, async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); }, async waitForSettled(options = {}) { return await guard.waitForSettled(options); }, snapshot() { return { name: this.name, provider: this.provider, guard: guard.snapshot() }; }
    };
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-clearance-row-replay-browser-adapter', store: delayedStore, scheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const successPayload = bytesFromSeed('${REVISION}:clearance-row-replay-success-payload', ${JSON.stringify(payloadBytes)});
    const failurePayload = bytesFromSeed('${REVISION}:clearance-row-replay-failure-payload', ${JSON.stringify(payloadBytes)});
    const successDigest = 'sha256:' + await m.digestBytesHex(successPayload);
    const failureDigest = 'sha256:' + await m.digestBytesHex(failurePayload);
    adapter.schedulePut(successPayload, { id: '${REVISION}-clearance-row-replay-success-timeout', priority: 'user-visible', label: 'clearance-row-replay-success' });
    adapter.schedulePut(failurePayload, { id: '${REVISION}-clearance-row-replay-failure-timeout', priority: 'user-visible', label: 'clearance-row-replay-failure' });
    const dispatchSuccess = scheduler.dispatchNext(); const dispatchFailure = scheduler.dispatchNext();
    const [timeoutSuccess, timeoutFailure] = await Promise.all([adapter.executor.executeDispatched(dispatchSuccess), adapter.executor.executeDispatched(dispatchFailure)]);
    const providerCommittedBeforeRelease = await waitUntil(async () => { const successPresent = await raw.has(successDigest); const failurePresent = await raw.has(failureDigest); const locks = await guard.queryLocks(); return { ok: successPresent && failurePresent && locks.heldCount === 0 && locks.pendingCount === 0, successPresent, failurePresent, locks }; }, { timeoutMs: 3000, intervalMs: 25, label: 'both-provider-writes-committed-before-release' });
    releaseSuccess.resolve('browser-release-clearance-row-replay-success'); releaseFailure.resolve('browser-release-clearance-row-replay-failure');
    const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 10 });
    const before = adapter.timedOutOperationQuarantine('storage');
    const staleLedger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-export-before-clearance-row-replay-guard' });
    const modifiedLedger = modifiedLedgerWithClearedRows(staleLedger);
    const statusRewriteLedger = modifiedLedgerWithStatusRewrite(staleLedger);
    const reviewManifest = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0081-browser-probe', reviewToken: 'browser-clearance-row-replay-review-token', reason: 'browser-review-before-clearance-row-replay' });
    const clearResult = adapter.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-for-clearance-row-replay' });
    const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0081-browser-probe', label: 'browser-clearance-row-replay' });
    const validation = m.validateTimedOutOperationQuarantineClearanceReceipt(receipt);
    const persisted = await adapter.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label: 'browser-clearance-row-replay-persisted' });
    const freshScheduler = rt.crossLaneScheduler({ label: '${REVISION}-clearance-row-replay-browser-fresh-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const fresh = rt.blockStoreLaneAdapter({ label: '${REVISION}-clearance-row-replay-browser-fresh-adapter', store: guard, scheduler: freshScheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const restored = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane: 'storage' });
    const exactReplay = fresh.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-exact-stale-row-replay-ledger', markUnhealthy: false });
    const rowReplay = fresh.importTimedOutOperationQuarantine(modifiedLedger, { lane: 'storage', reason: 'browser-modified-stale-row-replay-ledger', markUnhealthy: false });
    const statusRewriteReplay = fresh.importTimedOutOperationQuarantine(statusRewriteLedger, { lane: 'storage', reason: 'browser-status-rewritten-stale-row-replay-ledger', markUnhealthy: false });
    const laneAfterReplay = freshScheduler.snapshotLane('storage');
    const quarantineAfterReplay = fresh.timedOutOperationQuarantine('storage');
    const successVerify = await raw.verify(successDigest); const failureVerify = await raw.verify(failureDigest);
    const recoveryPayload = bytesFromSeed('${REVISION}:clearance-row-replay-recovery-after-restore', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'clearance-row-replay-recovery-after-restore' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks(); const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 }); const locksAfterCleanup = await guard.queryLocks(); const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, timeoutSuccess, timeoutFailure, providerCommittedBeforeRelease, settled, before, staleLedger, modifiedLedger, statusRewriteLedger, reviewManifest, clearResult, receipt, validation, persisted, restored, exactReplay, rowReplay, statusRewriteReplay, laneAfterReplay, quarantineAfterReplay, successVerify, failureVerify, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-clearance-row-replay-guard-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-clearance-row-replay-guard';
  const lockName = options.lockName || `${REVISION}-quarantine-clearance-row-replay-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 8 * 1024);
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 32000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-clearance-row-replay-guard.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine clearance row replay guard proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-clearance-row-replay-', stderrTerms: ['opfs', 'lock', 'quarantine', 'receipt'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.timeoutSuccess.ok, false); assert.equal(result.timeoutFailure.ok, false); assert.equal(result.timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(result.timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.providerCommittedBeforeRelease.ok, true); assert.equal(result.settled.ok, true); assert.equal(result.before.successfulTimedOutOperationCount, 1); assert.equal(result.before.failedTimedOutOperationCount, 1);
  assert.equal(result.clearResult.ok, true); assert.equal(result.validation.ok, true); assert.equal(result.persisted.ok, true); assert.equal(result.restored.ok, true); assert.equal(result.restored.registration.ok, true);
  assert.ok(result.restored.registration.clearedRowKeys.length >= 2); assert.ok(result.restored.registration.clearedOperationKeys.length >= 2);
  assert.equal(result.exactReplay.ok, false); assert.equal(result.exactReplay.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(result.rowReplay.ok, false); assert.equal(result.rowReplay.disposition, 'rejected-cleared-quarantine-row-replay'); assert.ok(result.rowReplay.matchedRows.length >= 1);
  assert.equal(result.statusRewriteReplay.ok, false); assert.equal(result.statusRewriteReplay.disposition, 'rejected-cleared-quarantine-row-replay'); assert.ok(result.statusRewriteReplay.matchedRows.some((row) => row.operationKey && row.statusKey), 'status rewrite replay should match by operation key');
  assert.equal(result.laneAfterReplay.healthy, true); assert.equal(result.quarantineAfterReplay.totalCount, 0); assert.equal(result.successVerify.ok, true); assert.equal(result.failureVerify.ok, true);
  assert.equal(result.recoveryVerify.ok, true); assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['block-store-lane:quarantine-clearance-receipt-persisted', 'block-store-lane:quarantine-clearance-receipt-restored', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'storage-lane:timed-out-quarantine-import-row-replay-rejected', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-row-replay-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that reviewed/scoped timeout-quarantine clearance receipts guard exact, modified-row, and status-rewritten row replay through real guarded OPFS/Web Locks.', observations: { ...result, harness }, claimsChecked: ['real guarded OPFS timeout-quarantine outcomes can be cleared with a bound review manifest', 'clearanceReceipt.v1 persists as a guarded OPFS block and restores into a fresh adapter', 'exact stale cleared quarantine ledger replay rejects', 'modified row-level replay rejects without backpressuring the lane', 'status-rewritten cleared operation replay rejects by operation identity', 'later guarded OPFS writes verify after restoration'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Receipt fingerprint is deterministic review binding, not cryptographic attestation, tamper-proof storage, or security boundary.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '32000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-row-replay-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser clearance row replay guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_clearance_row_replay_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
