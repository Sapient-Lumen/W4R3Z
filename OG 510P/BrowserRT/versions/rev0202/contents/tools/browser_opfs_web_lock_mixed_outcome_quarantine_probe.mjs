#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-mixed-outcome-quarantine-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-MIXED-OUTCOME-QUARANTINE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 2500, intervalMs = 25, label = 'condition' } = {}) => {
      const start = performance.now(); let last = null;
      while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last, label }; await sleep(intervalMs); }
      return { ok: false, elapsedMs: performance.now() - start, last, label };
    };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserMixedOutcomeProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (137 + i * 17 + (i >>> 2)) & 255; return out; };
    const m = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockMixedOutcomeQuarantineProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-mixed-outcome-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const cleanupBefore = await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-mixed-outcome-guard', lockTimeoutMs: 1000 });
    const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-mixed-outcome-browser-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const releaseSuccess = deferred(); const releaseFailure = deferred();
    const delayedStats = { puts: 0, delayedSuccessPuts: 0, delayedFailurePuts: 0, lateSuccesses: 0, lateFailures: 0, waitForSettledCalls: 0 };
    const refs = { success: null, failure: null };
    const delayedStore = {
      name: '${REVISION}-mixed-outcome-delayed-guarded-store', provider: 'mixed-outcome:' + guard.provider,
      async put(payload, fields = {}) {
        delayedStats.puts += 1;
        const put = await guard.put(payload, fields, { timeoutMs: 1000 });
        const label = String(fields.label || '');
        if (label.includes('success')) { refs.success = put.ref || put; delayedStats.delayedSuccessPuts += 1; await releaseSuccess.promise; delayedStats.lateSuccesses += 1; return put; }
        if (label.includes('failure')) { refs.failure = put.ref || put; delayedStats.delayedFailurePuts += 1; await releaseFailure.promise; delayedStats.lateFailures += 1; throw codedError('BRT_BROWSER_MIXED_LATE_FAILURE', 'browser mixed late failure after committed guarded OPFS write', { digest: put.digest, bytes: put.bytes }); }
        return put;
      },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); },
      async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); },
      async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); },
      async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); },
      async estimate() { return await guard.estimate({ timeoutMs: 1000 }); },
      async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); },
      async waitForSettled(options = {}) { delayedStats.waitForSettledCalls += 1; return await guard.waitForSettled(options); },
      snapshot() { return { name: this.name, provider: this.provider, delayedStats: { ...delayedStats }, guard: guard.snapshot() }; }
    };
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-mixed-outcome-browser-adapter', store: delayedStore, scheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const successPayload = bytesFromSeed('${REVISION}:mixed-outcome-success-payload', ${JSON.stringify(payloadBytes)});
    const failurePayload = bytesFromSeed('${REVISION}:mixed-outcome-failure-payload', ${JSON.stringify(payloadBytes)});
    const successDigest = 'sha256:' + await m.digestBytesHex(successPayload);
    const failureDigest = 'sha256:' + await m.digestBytesHex(failurePayload);

    const scheduledSuccess = adapter.schedulePut(successPayload, { id: '${REVISION}-mixed-late-success-put', priority: 'user-visible', label: 'mixed-late-success' });
    const scheduledFailure = adapter.schedulePut(failurePayload, { id: '${REVISION}-mixed-late-failure-put', priority: 'user-visible', label: 'mixed-late-failure' });
    const dispatchSuccess = scheduler.dispatchNext(); const dispatchFailure = scheduler.dispatchNext();
    const [timeoutSuccess, timeoutFailure] = await Promise.all([adapter.executor.executeDispatched(dispatchSuccess), adapter.executor.executeDispatched(dispatchFailure)]);
    const snapshotAfterTimeouts = adapter.snapshot();
    const storageLaneAfterTimeouts = snapshotAfterTimeouts.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
    const providerCommittedBeforeRelease = await waitUntil(async () => {
      const successPresent = await raw.has(successDigest); const failurePresent = await raw.has(failureDigest); const locks = await guard.queryLocks();
      return { ok: successPresent && failurePresent && locks.heldCount === 0 && locks.pendingCount === 0, successPresent, failurePresent, locks };
    }, { timeoutMs: 3000, intervalMs: 25, label: 'both-provider-writes-committed-and-locks-drained-before-release' });
    const quarantineAfterTimeouts = adapter.timedOutOperationQuarantine('storage');
    const missingCategoryClear = adapter.clearTimedOutOperationQuarantine({ lane: 'storage', reviewed: true, reviewToken: '${REVISION}-missing-category', reason: 'browser-reviewed-but-category-missing' });
    const blockedWhileUnsettled = await adapter.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 10, reason: 'browser-mixed-outcome-still-unsettled' });

    releaseSuccess.resolve('browser-release-mixed-late-success'); releaseFailure.resolve('browser-release-mixed-late-failure');
    const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1500, intervalMs: 10 });
    const guardSettled = await guard.waitForSettled({ timeoutMs: 1500, intervalMs: 20 });
    const locksAfterSettlement = await guard.queryLocks();
    const successVerifyAfterLate = await raw.verify(successDigest); const failureVerifyAfterLate = await raw.verify(failureDigest);
    const quarantineAfterSettlement = adapter.timedOutOperationQuarantine('storage');
    const blockedBySuccess = await adapter.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 10, reason: 'browser-mixed-late-success-still-quarantined' });
    const rejectedAfterMixedSettlement = adapter.schedulePut(bytesFromSeed('${REVISION}:reject-after-mixed-late-outcome', 1024), { id: '${REVISION}-mixed-outcome-reject-while-quarantined', priority: 'user-visible', label: 'must-not-queue' });
    const unreviewedSuccessClear = adapter.clearTimedOutOperationQuarantine({ category: 'success', lane: 'storage', opId: '${REVISION}-mixed-late-success-put', reason: 'browser-unreviewed-success-clear' });
    const clearSuccess = adapter.clearTimedOutOperationQuarantine({ category: 'success', lane: 'storage', opId: '${REVISION}-mixed-late-success-put', reviewed: true, reviewToken: '${REVISION}-mixed-success-reviewed', reason: 'browser-reviewed-success-clear' });
    const blockedByFailure = await adapter.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 10, reason: 'browser-mixed-late-failure-still-quarantined' });
    const unscopedFailureClear = adapter.clearTimedOutOperationQuarantine({ category: 'failure', lane: 'storage', reviewed: true, reviewToken: '${REVISION}-mixed-failure-unscoped', reason: 'browser-reviewed-failure-without-scope' });
    const clearFailure = adapter.clearTimedOutOperationQuarantine({ category: 'failure', lane: 'storage', opId: '${REVISION}-mixed-late-failure-put', reviewed: true, reviewToken: '${REVISION}-mixed-failure-reviewed', reason: 'browser-reviewed-failure-clear' });
    const recoveredAfterBothClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-mixed-late-outcomes-reviewed-recovery' });
    const recoveryPayload = bytesFromSeed('${REVISION}:mixed-outcome-recovered-payload', 4096);
    const recoveredSchedule = adapter.schedulePut(recoveryPayload, { id: '${REVISION}-mixed-outcome-recovered-put', priority: 'user-visible', label: 'recovered-after-mixed-outcome', operationTimeoutMs: 1000 });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 }); const recoveredResult = recoveryDrain.results.find((row) => row.opId === '${REVISION}-mixed-outcome-recovered-put') || null; const recoveredVerify = recoveredResult?.result?.ref ? await raw.verify(recoveredResult.result.ref) : null;
    const finalLocksBeforeCleanup = await guard.queryLocks(); const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 }); const finalLocks = await guard.queryLocks(); const finalSnapshot = adapter.snapshot(); const trace = rt.close();
    return JSON.stringify({
      project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}',
      page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' },
      prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, operationTimeoutMs: ${JSON.stringify(operationTimeoutMs)}, payloadBytes: ${JSON.stringify(payloadBytes)},
      cleanupBefore, scheduledSuccess, scheduledFailure, dispatchSuccess, dispatchFailure, timeoutSuccess, timeoutFailure, snapshotAfterTimeouts, storageLaneAfterTimeouts, providerCommittedBeforeRelease, quarantineAfterTimeouts, missingCategoryClear, blockedWhileUnsettled, settled, guardSettled, locksAfterSettlement, successDigest, failureDigest, successVerifyAfterLate, failureVerifyAfterLate, quarantineAfterSettlement, blockedBySuccess, rejectedAfterMixedSettlement, unreviewedSuccessClear, clearSuccess, blockedByFailure, unscopedFailureClear, clearFailure, recoveredAfterBothClear, recoveredSchedule, recoveryDrain, recoveredResult, recoveredVerify, finalLocksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, delayedStats, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('late-provider') || event.kind.includes('timed-out') || event.kind.includes('operation-timeout') || event.kind.includes('recover')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, reason: event.reason ?? null, code: event.code ?? null, successfulTimedOutOperationCount: event.successfulTimedOutOperationCount ?? null, failedTimedOutOperationCount: event.failedTimedOutOperationCount ?? null }))
    });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-mixed-outcome-quarantine-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-mixed-outcome-quarantine';
  const lockName = options.lockName || `${REVISION}-mixed-outcome-mutation-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 8 * 1024);
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 22000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-mixed-outcome-quarantine.html', pageTitle: 'BrowserRT OPFS Web Lock mixed-outcome quarantine proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-opfs-web-lock-mixed-outcome-', stderrTerms: ['opfs', 'lock', 'timeout', 'mixed'] }, async ({ evalJson, timeoutMs, mark }) => {
    const evalStart = performance.now(); const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs); mark('browser-opfs-web-lock-mixed-outcome-quarantine-eval', evalStart); return report;
  });

  assert.equal(result.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(result.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(result.capabilities.webLocksQuery, true, 'Web Locks query must be available');
  assert.equal(result.scheduledSuccess.accepted, true); assert.equal(result.scheduledFailure.accepted, true); assert.equal(result.dispatchSuccess.dispatched, true); assert.equal(result.dispatchFailure.dispatched, true);
  assert.equal(result.timeoutSuccess.ok, false); assert.equal(result.timeoutFailure.ok, false); assert.equal(result.timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(result.timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.snapshotAfterTimeouts.executor.unsettledTimedOutOperationCount, 2); assert.equal(result.storageLaneAfterTimeouts.healthy, false); assert.equal(result.storageLaneAfterTimeouts.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.providerCommittedBeforeRelease.ok, true, 'both OPFS writes should commit and Web Locks should drain before provider releases');
  assert.equal(result.quarantineAfterTimeouts.totalCount, 2); assert.equal(result.quarantineAfterTimeouts.unsettledCount, 2);
  assert.equal(result.missingCategoryClear.ok, false); assert.equal(result.missingCategoryClear.code, 'timed-out-quarantine-clear-scope-required');
  assert.equal(result.blockedWhileUnsettled.recovered, false); assert.equal(result.blockedWhileUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(result.settled.ok, true); assert.equal(result.guardSettled.ok, true); assert.equal(result.locksAfterSettlement.heldCount, 0); assert.equal(result.locksAfterSettlement.pendingCount, 0);
  assert.equal(result.successVerifyAfterLate.ok, true); assert.equal(result.failureVerifyAfterLate.ok, true);
  assert.equal(result.quarantineAfterSettlement.successfulCount, 1); assert.equal(result.quarantineAfterSettlement.failedCount, 1); assert.deepEqual(result.quarantineAfterSettlement.blockedReasons, ['timed-out-operation-late-success', 'timed-out-operation-late-failure']);
  assert.equal(result.blockedBySuccess.recovered, false); assert.equal(result.blockedBySuccess.reason, 'timed-out-operation-late-success');
  assert.equal(result.rejectedAfterMixedSettlement.accepted, false); assert.equal(result.rejectedAfterMixedSettlement.scheduler.noMutation, true);
  assert.equal(result.unreviewedSuccessClear.ok, false); assert.equal(result.unreviewedSuccessClear.code, 'timed-out-quarantine-clear-review-required');
  assert.equal(result.clearSuccess.ok, true); assert.equal(result.clearSuccess.clearedCount, 1);
  assert.equal(result.blockedByFailure.recovered, false); assert.equal(result.blockedByFailure.reason, 'timed-out-operation-late-failure');
  assert.equal(result.unscopedFailureClear.ok, false); assert.equal(result.unscopedFailureClear.code, 'timed-out-quarantine-clear-scope-required');
  assert.equal(result.clearFailure.ok, true); assert.equal(result.clearFailure.clearedCount, 1);
  assert.equal(result.recoveredAfterBothClear.recovered, true); assert.equal(result.recoveredSchedule.accepted, true); assert.equal(result.recoveredResult?.ok, true); assert.equal(result.recoveredVerify?.ok, true);
  assert.equal(result.finalSnapshot.executor.timedOutOperationQuarantineCount, 0); assert.equal(result.finalSnapshot.executor.stats.reviewedLateProviderSuccesses, 1); assert.equal(result.finalSnapshot.executor.stats.reviewedLateProviderFailures, 1); assert.equal(result.cleanupAfter, true); assert.equal(result.finalLocks.heldCount, 0); assert.equal(result.finalLocks.pendingCount, 0);
  for (const kind of ['storage-lane:operation-timeout-unsettled', 'storage-lane:late-provider-success', 'storage-lane:late-provider-failure', 'storage-lane:timed-out-quarantine-clear-rejected', 'storage-lane:timed-out-quarantine-cleared', 'block-store-lane:recover-timed-out-successes-blocked', 'block-store-lane:recover-timed-out-failures-blocked', 'block-store-lane:recover-settled', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-mixed-outcome-quarantine-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that real guarded OPFS writes can time out, then settle as one late success and one late failure, and BrowserRT keeps those quarantine categories separate until reviewed/scoped clearing.', observations: { ...result, harness }, claimsChecked: ['real OPFS/Web Lock guarded writes can produce mixed late success/failure after storage-lane timeout', 'timedOutOperationQuarantine exposes unsettled, late-success, and late-failure categories', 'unified clearing requires category, review, and scope', 'recovery remains blocked until both late success and late failure categories are reviewed/scoped and cleared'], nonClaims: ['Managed Chromium/CDP browser proof only; no cross-browser OPFS/Web Locks behavior claim.', 'Operation timeout and mixed outcome quarantine are not cancellation, rollback, no-mutation, exactly-once, or provider interruption evidence.', 'Explicit clearing is maintenance acknowledgement, not automatic recovery or production correctness.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '22000')) }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-mixed-outcome-quarantine-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser mixed-outcome quarantine proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_mixed_outcome_quarantine_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
