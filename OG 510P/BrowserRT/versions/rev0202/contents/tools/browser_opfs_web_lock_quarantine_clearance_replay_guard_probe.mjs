#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile, mkdtemp, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses, startProbeServer } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-clearance-replay-guard-proof';
// Managed Chromium same profile replay guard proof.
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-CLEARANCE-REPLAY-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function phase1Expression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 3000, intervalMs = 25, label = 'condition' } = {}) => {
      const start = performance.now(); let last = null;
      while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last, label }; await sleep(intervalMs); }
      return { ok: false, elapsedMs: performance.now() - start, last, label };
    };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserClearanceReceiptProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 17 + (i >>> 2)) & 255; return out; };
    const m = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockQuarantineClearanceReceiptPersistenceProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-clearance-replay-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const cleanupBefore = await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-clearance-replay-guard', lockTimeoutMs: 1000 });
    const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-clearance-replay-browser-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const releaseSuccess = deferred(); const releaseFailure = deferred(); const refs = { success: null, failure: null };
    const delayedStore = {
      name: '${REVISION}-clearance-replay-delayed-guarded-store', provider: 'clearance-replay:' + guard.provider,
      async put(payload, fields = {}) { const put = await guard.put(payload, fields, { timeoutMs: 1000 }); const label = String(fields.label || ''); if (label.includes('success')) { refs.success = put.ref || put; await releaseSuccess.promise; return put; } if (label.includes('failure')) { refs.failure = put.ref || put; await releaseFailure.promise; throw codedError('BRT_BROWSER_CLEARANCE_RECEIPT_LATE_FAILURE', 'browser clearance-replay late failure after committed guarded OPFS write', { digest: put.digest, bytes: put.bytes }); } return put; },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); }, async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); }, async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); }, async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); }, async estimate() { return await guard.estimate({ timeoutMs: 1000 }); }, async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); }, async waitForSettled(options = {}) { return await guard.waitForSettled(options); }, snapshot() { return { name: this.name, provider: this.provider, guard: guard.snapshot() }; }
    };
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-clearance-replay-browser-adapter', store: delayedStore, scheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const successPayload = bytesFromSeed('${REVISION}:clearance-replay-success-payload', ${JSON.stringify(payloadBytes)});
    const failurePayload = bytesFromSeed('${REVISION}:clearance-replay-failure-payload', ${JSON.stringify(payloadBytes)});
    const successDigest = 'sha256:' + await m.digestBytesHex(successPayload);
    const failureDigest = 'sha256:' + await m.digestBytesHex(failurePayload);
    adapter.schedulePut(successPayload, { id: '${REVISION}-clearance-replay-success-timeout', priority: 'user-visible', label: 'clearance-replay-success' });
    adapter.schedulePut(failurePayload, { id: '${REVISION}-clearance-replay-failure-timeout', priority: 'user-visible', label: 'clearance-replay-failure' });
    const dispatchSuccess = scheduler.dispatchNext(); const dispatchFailure = scheduler.dispatchNext();
    const [timeoutSuccess, timeoutFailure] = await Promise.all([adapter.executor.executeDispatched(dispatchSuccess), adapter.executor.executeDispatched(dispatchFailure)]);
    const providerCommittedBeforeRelease = await waitUntil(async () => { const successPresent = await raw.has(successDigest); const failurePresent = await raw.has(failureDigest); const locks = await guard.queryLocks(); return { ok: successPresent && failurePresent && locks.heldCount === 0 && locks.pendingCount === 0, successPresent, failurePresent, locks }; }, { timeoutMs: 3000, intervalMs: 25, label: 'both-provider-writes-committed-before-release' });
    releaseSuccess.resolve('browser-release-clearance-replay-success'); releaseFailure.resolve('browser-release-clearance-replay-failure');
    const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 10 });
    const before = adapter.timedOutOperationQuarantine('storage');
    const staleLedger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-export-before-clearance-replay-guard' });
    const reviewManifest = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0078-browser-probe', reviewToken: 'browser-clearance-replay-review-token', reason: 'browser-review-before-clearance-replay' });
    const clearResult = adapter.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-for-clearance-replay' });
    const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0078-browser-probe', label: 'browser-clearance-replay' });
    const validation = m.validateTimedOutOperationQuarantineClearanceReceipt(receipt);
    const persisted = await adapter.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label: 'browser-clearance-replay-persisted' });
    const recovery = await adapter.recoverWhenStoreSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 10, reason: 'browser-clearance-replay-created' });
    const postPayload = bytesFromSeed('${REVISION}:clearance-replay-post-clear-payload', 4096);
    const postSchedule = adapter.schedulePut(postPayload, { id: '${REVISION}-clearance-replay-post-clear-put', label: 'clearance-replay-post-clear', operationTimeoutMs: 1000 });
    const postDrain = await adapter.drain({ maxSteps: 3 });
    const postResult = postDrain.results.find((row) => row.opId === '${REVISION}-clearance-replay-post-clear-put') || null;
    const postVerify = postResult?.result?.ref ? await raw.verify(postResult.result.ref) : null;
    const locks = await guard.queryLocks(); const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', phase: 'launch-1', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, cleanupBefore, timeoutSuccess, timeoutFailure, providerCommittedBeforeRelease, settled, before, staleLedger, reviewManifest, clearResult, receipt, validation, persisted, recovery, postSchedule, postResult, postVerify, successDigest, failureDigest, locks, traceKinds: trace.map((row) => row.kind) });
  })()`;
}

function phase2Expression({ prefix, lockPrefix, lockName, persistedRef, staleLedger, successDigest, failureDigest }) {
  return `(async () => {
    const clone = (value) => JSON.parse(JSON.stringify(value));
    const m = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockQuarantineClearanceReceiptRestoreProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-clearance-replay-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-clearance-replay-guard', lockTimeoutMs: 1000 });
    const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-clearance-replay-browser-restore-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-clearance-replay-browser-restore-adapter', store: guard, scheduler, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const restored = await adapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(${JSON.stringify(persistedRef)}, { lane: 'storage' });
    const replay = adapter.importTimedOutOperationQuarantine(${JSON.stringify(staleLedger)}, { lane: 'storage', reason: 'browser-stale-cleared-ledger-replay', markUnhealthy: false });
    const laneAfterReplay = scheduler.snapshotLane('storage');
    const quarantineAfterReplay = adapter.timedOutOperationQuarantine('storage');
    const successVerify = await raw.verify(${JSON.stringify(successDigest)});
    const failureVerify = await raw.verify(${JSON.stringify(failureDigest)});
    let tamperedRestore = null; let tamperedPut = null;
    if (restored?.receipt) {
      const tamperedReceipt = clone(restored.receipt); tamperedReceipt.counts.total += 1;
      tamperedPut = await guard.put(new TextEncoder().encode(JSON.stringify(tamperedReceipt, null, 2)), { label: 'tampered-browser-clearance-replay', purpose: 'timed-out-operation-quarantine-clearance-replay' }, { timeoutMs: 1000 });
      tamperedRestore = await adapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(tamperedPut.ref || tamperedPut, { lane: 'storage' });
    } else {
      tamperedRestore = { ok: false, skipped: true, reason: 'restore-produced-no-receipt', restored };
    }
    const recoveryPayload = new TextEncoder().encode('${REVISION}:clearance-replay-recovery-after-restore');
    const recoveryPut = await guard.put(recoveryPayload, { label: 'clearance-replay-recovery-after-restore' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks(); const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 }); const locksAfterCleanup = await guard.queryLocks(); const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', phase: 'launch-2', restored, replay, laneAfterReplay, quarantineAfterReplay, successVerify, failureVerify, tamperedRestore, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-clearance-replay-guard-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-clearance-replay-guard';
  const lockName = options.lockName || `${REVISION}-quarantine-clearance-replay-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 8 * 1024);
  const profileDir = await mkdtemp(join(tmpdir(), 'browserrt-clearance-replay-profile-'));
  let profileReap = null;
  let server = null;
  try {
    server = await startProbeServer({ pagePath: '/browser-opfs-web-lock-quarantine-clearance-replay-guard.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine clearance replay guard proof', allowedPrefixes: ['src/'] });
    const phase1 = await runManagedBrowserPage({ server, timeoutMs: options.timeoutMs || 32000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, profileDir, keepProfile: true, profilePrefix: 'browserrt-clearance-replay-', stderrTerms: ['opfs', 'lock', 'quarantine', 'receipt'] }, async ({ evalJson, timeoutMs }) => await evalJson(phase1Expression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs));
    const r1 = phase1.result;
    assert.equal(r1.capabilities.opfs, true); assert.equal(r1.capabilities.webLocks, true); assert.equal(r1.capabilities.webLocksQuery, true);
    assert.equal(r1.timeoutSuccess.ok, false); assert.equal(r1.timeoutFailure.ok, false); assert.equal(r1.timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(r1.timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
    assert.equal(r1.providerCommittedBeforeRelease.ok, true); assert.equal(r1.settled.ok, true); assert.equal(r1.before.successfulTimedOutOperationCount, 1); assert.equal(r1.before.failedTimedOutOperationCount, 1);
    assert.equal(r1.clearResult.ok, true); assert.equal(r1.validation.ok, true); assert.equal(r1.persisted.ok, true); assert.equal(r1.recovery.recovered, true); assert.equal(r1.postVerify?.ok, true); assert.equal(r1.locks.heldCount, 0); assert.equal(r1.locks.pendingCount, 0);
    for (const kind of ['block-store-lane:quarantine-clearance-receipt-created', 'block-store-lane:quarantine-clearance-receipt-persisted', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(r1.traceKinds.includes(kind), `phase1 missing ${kind}`);
    const phase2 = await runManagedBrowserPage({ server, timeoutMs: options.timeoutMs || 32000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, profileDir, keepProfile: true, profilePrefix: 'browserrt-clearance-replay-', stderrTerms: ['opfs', 'lock', 'quarantine', 'receipt'] }, async ({ evalJson, timeoutMs }) => await evalJson(phase2Expression({ prefix, lockPrefix, lockName, persistedRef: r1.persisted.ref, staleLedger: r1.staleLedger, successDigest: r1.successDigest, failureDigest: r1.failureDigest }), timeoutMs));
    const r2 = phase2.result;
    assert.equal(r2.restored.ok, true); assert.equal(r2.restored.receiptFingerprint, r1.receipt.receiptFingerprint); assert.equal(r2.replay.ok, false); assert.equal(r2.replay.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(r2.laneAfterReplay.healthy, true); assert.equal(r2.quarantineAfterReplay.totalCount, 0); assert.equal(r2.successVerify.ok, true); assert.equal(r2.failureVerify.ok, true);
    assert.equal(r2.tamperedRestore.ok, false); assert.equal(r2.tamperedRestore.disposition, 'rejected-clearance-receipt-integrity');
    assert.equal(r2.recoveryVerify.ok, true); assert.equal(r2.cleanupAfter, true); assert.equal(r2.locksAfterCleanup.heldCount, 0); assert.equal(r2.locksAfterCleanup.pendingCount, 0);
    for (const kind of ['block-store-lane:quarantine-clearance-receipt-restored', 'block-store-lane:quarantine-clearance-receipt-restore-rejected', 'storage-lane:timed-out-quarantine-import-replay-rejected']) assert.ok(r2.traceKinds.includes(kind), `phase2 missing ${kind}`);
    profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    assert.equal(profileReap.afterKillCount, 0);
    return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-replay-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that reviewed/scoped timeout-quarantine clearance receipts guard replay through real guarded OPFS/Web Locks, restore after a clean same-profile browser restart, reject malformed persisted receipts fail-closed, and permit later guarded OPFS writes.', observations: { phase1: r1, phase2: r2, harness: { phase1: phase1.harness, phase2: phase2.harness }, profileReap }, claimsChecked: ['real guarded OPFS timeout-quarantine outcomes can be cleared with a bound review manifest', 'clearanceReceipt.v1 persists as a guarded OPFS block', 'valid persisted receipt restores after same-profile browser restart', 'stale cleared quarantine ledger replay rejects without backpressuring the lane', 'malformed persisted receipt rejects fail-closed', 'later guarded OPFS writes verify after restoration'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Receipt fingerprint is deterministic review binding, not cryptographic attestation, tamper-proof storage, or security boundary.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness evidence.'] };
  } finally {
    await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 }).catch(() => null);
    if (server) await server.close().catch(() => null);
    await rm(profileDir, { recursive: true, force: true }).catch(() => null);
  }
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '32000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-replay-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser clearance replay guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_clearance_replay_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
