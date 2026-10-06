#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-multi-failure-quarantine-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-MULTI-FAILURE-QUARANTINE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const waitUntil = async (predicate, { timeoutMs = 2000, intervalMs = 20 } = {}) => { const start = performance.now(); let last = null; while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, last, elapsedMs: performance.now() - start }; await sleep(intervalMs); } return { ok: false, last, elapsedMs: performance.now() - start }; };
    const codedError = (code, message, detail = {}) => { const e = new Error(message); e.name = 'BrowserRTBrowserMultiLateProviderError'; e.code = code; e.storageDisposition = code; e.detail = Object.freeze({ ...detail }); return e; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 17 + (i >>> 2)) & 255; return out; };
    const m = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockMultiFailureQuarantineProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-multi-failure-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open(); await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-multi-failure-guard', lockTimeoutMs: 1000 });
    const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-multi-failure-browser-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const releases = { a: deferred(), b: deferred() };
    const delayedStats = { puts: 0, delayedPuts: 0, lateFailures: 0, waitForSettledCalls: 0 };
    const refs = {};
    const delayedStore = {
      name: '${REVISION}-multi-failure-delayed-guarded-store', provider: 'multi-late-failing:' + guard.provider,
      async put(payload, fields = {}) {
        delayedStats.puts += 1;
        const ref = await guard.put(payload, fields, { timeoutMs: 1000 });
        const label = fields.label || 'unlabeled';
        refs[label] = ref.ref || ref;
        if (label === 'multi-late-failure-a' || label === 'multi-late-failure-b') {
          const key = label.endsWith('-a') ? 'a' : 'b';
          delayedStats.delayedPuts += 1;
          await releases[key].promise;
          delayedStats.lateFailures += 1;
          throw codedError('BRT_OPFS_OPERATION_FAILED', 'browser multi late provider failure after storage-lane timeout', { digest: refs[label].digest, label });
        }
        return ref;
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
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-multi-failure-browser-adapter', store: delayedStore, scheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const payloadA = bytesFromSeed('${REVISION}:multi-late-failure-payload-a', ${JSON.stringify(payloadBytes)});
    const payloadB = bytesFromSeed('${REVISION}:multi-late-failure-payload-b', ${JSON.stringify(payloadBytes)});
    const digestA = 'sha256:' + await m.digestBytesHex(payloadA);
    const digestB = 'sha256:' + await m.digestBytesHex(payloadB);
    const scheduledA = adapter.schedulePut(payloadA, { id: '${REVISION}-multi-late-failing-put-a', priority: 'user-visible', label: 'multi-late-failure-a' });
    const scheduledB = adapter.schedulePut(payloadB, { id: '${REVISION}-multi-late-failing-put-b', priority: 'user-visible', label: 'multi-late-failure-b' });
    const dispatchA = scheduler.dispatchNext();
    const dispatchB = scheduler.dispatchNext();
    const [timeoutA, timeoutB] = await Promise.all([adapter.executor.executeDispatched(dispatchA), adapter.executor.executeDispatched(dispatchB)]);
    const providerCommittedBeforeRelease = await waitUntil(async () => Boolean(refs['multi-late-failure-a'] && refs['multi-late-failure-b']), { timeoutMs: 2500, intervalMs: 20 });
    const firstTimeoutVerify = refs['multi-late-failure-a'] ? await guard.verify(refs['multi-late-failure-a'], { timeoutMs: 1000 }) : null;
    const secondTimeoutVerify = refs['multi-late-failure-b'] ? await guard.verify(refs['multi-late-failure-b'], { timeoutMs: 1000 }) : null;
    const snapshotAfterTimeouts = adapter.snapshot();
    const laneAfterTimeouts = snapshotAfterTimeouts.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
    const locksAfterTimeouts = await guard.queryLocks();
    const blockedWhileUnsettled = await adapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-multi-late-provider-still-unsettled' });
    const unsafeClear = adapter.clearFailedTimedOutOperations({ lane: 'storage', reason: 'browser-unsafe-unreviewed-clear' });
    const ambiguousClear = adapter.clearFailedTimedOutOperations({ lane: 'storage', reviewed: true, reviewToken: '${REVISION}-ambiguous-browser-review', reason: 'browser-ambiguous-reviewed-clear' });
    const remainingAfterRejectedClears = adapter.failedTimedOutOperations('storage');
    releases.a.resolve('release-a'); releases.b.resolve('release-b');
    const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 20 });
    const failedAfterLate = adapter.failedTimedOutOperations('storage');
    const timedOutVerifiesAfterLateFailures = { a: await guard.verify(refs['multi-late-failure-a'], { timeoutMs: 1000 }), b: await guard.verify(refs['multi-late-failure-b'], { timeoutMs: 1000 }) };
    const blockedByTwoFailures = await adapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-multi-late-provider-failures-block-recovery' });
    const rejectedAfterLate = adapter.schedulePut(bytesFromSeed('${REVISION}:must-not-queue-after-multi-failure', 2048), { id: '${REVISION}-reject-after-multi-late-failure', label: 'rejected-after-multi-failure' });
    const clearReviewA = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: '${REVISION}-multi-late-failing-put-a', reviewer: 'legacy-compatible-browser-probe', reviewToken: '${REVISION}-browser-review-a', reason: 'browser-maintenance-reviewed-first-late-provider-failure' });
    const clearA = adapter.clearFailedTimedOutOperations({ reviewManifest: clearReviewA, requireReviewFingerprint: true, reason: 'browser-maintenance-reviewed-first-late-provider-failure' });
    const blockedAfterOneClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-one-late-provider-failure-still-quarantined' });
    const clearReviewB = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: '${REVISION}-multi-late-failing-put-b', reviewer: 'legacy-compatible-browser-probe', reviewToken: '${REVISION}-browser-review-b', reason: 'browser-maintenance-reviewed-second-late-provider-failure' });
    const clearB = adapter.clearFailedTimedOutOperations({ reviewManifest: clearReviewB, requireReviewFingerprint: true, reason: 'browser-maintenance-reviewed-second-late-provider-failure' });
    const recoveredAfterBothClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-multi-late-provider-failures-reviewed-recovery' });
    const recoveryPayload = bytesFromSeed('${REVISION}:multi-failure-recovered-payload', 8192);
    const recoveredSchedule = adapter.schedulePut(recoveryPayload, { id: '${REVISION}-multi-failure-recovered-put', priority: 'user-visible', label: 'recovered-after-multi-late-failure', operationTimeoutMs: 1000 });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === '${REVISION}-multi-failure-recovered-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await guard.verify(recoveredResult.result.ref, { timeoutMs: 1000 }) : null;
    const finalSnapshot = adapter.snapshot();
    const finalLocksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const finalLocks = await guard.queryLocks();
    const trace = rt.close();
    return { capabilities: { opfs: raw.available === true, webLocks: guard.coordinator.available === true, webLocksQuery: typeof navigator.locks?.query === 'function' }, scheduledA, scheduledB, dispatchA, dispatchB, timeoutA, timeoutB, providerCommittedBeforeRelease, firstTimeoutVerify, secondTimeoutVerify, snapshotAfterTimeouts, laneAfterTimeouts, locksAfterTimeouts, blockedWhileUnsettled, unsafeClear, ambiguousClear, remainingAfterRejectedClears, settled, failedAfterLate, timedOutVerifiesAfterLateFailures, blockedByTwoFailures, rejectedAfterLate, clearA, blockedAfterOneClear, clearB, recoveredAfterBothClear, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, finalLocksBeforeCleanup, cleanupAfter, finalLocks, delayedStats, refs: { a: refs['multi-late-failure-a'], b: refs['multi-late-failure-b'] }, traceKinds: trace.map((event) => event.kind) };
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-multi-failure-quarantine-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-multi-failure-quarantine';
  const lockName = options.lockName || `${REVISION}-multi-failure-mutation-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 12 * 1024);
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 22000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-multi-failure-quarantine.html', pageTitle: 'BrowserRT OPFS Web Lock multi-failure quarantine proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-opfs-web-lock-multi-failure-', stderrTerms: ['opfs','lock','timeout','failure'] }, async ({ evalJson, timeoutMs, mark }) => {
    const evalStart = performance.now(); const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs); mark('browser-opfs-web-lock-multi-failure-quarantine-eval', evalStart); return report;
  });
  assert.equal(result.capabilities.opfs, true);
  assert.equal(result.capabilities.webLocks, true);
  assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.scheduledA.accepted, true); assert.equal(result.scheduledB.accepted, true);
  assert.equal(result.dispatchA.dispatched, true); assert.equal(result.dispatchB.dispatched, true);
  assert.equal(result.timeoutA.ok, false); assert.equal(result.timeoutB.ok, false);
  assert.equal(result.timeoutA.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(result.timeoutB.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.providerCommittedBeforeRelease.ok, true);
  assert.equal(result.firstTimeoutVerify?.ok, true); assert.equal(result.secondTimeoutVerify?.ok, true);
  assert.equal(result.snapshotAfterTimeouts.executor.unsettledTimedOutOperationCount, 2);
  assert.equal(result.laneAfterTimeouts.healthy, false); assert.equal(result.laneAfterTimeouts.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.locksAfterTimeouts.heldCount, 0); assert.equal(result.locksAfterTimeouts.pendingCount, 0);
  assert.equal(result.blockedWhileUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(result.unsafeClear.ok, false); assert.equal(result.unsafeClear.code, 'late-failure-clear-review-required');
  assert.equal(result.ambiguousClear.ok, false); assert.equal(result.ambiguousClear.code, 'late-failure-clear-scope-required');
  assert.equal(result.remainingAfterRejectedClears.length, 0);
  assert.equal(result.settled.ok, true); assert.equal(result.settled.count, 0);
  assert.equal(result.failedAfterLate.length, 2);
  assert.equal(result.timedOutVerifiesAfterLateFailures.a.ok, true); assert.equal(result.timedOutVerifiesAfterLateFailures.b.ok, true);
  assert.equal(result.blockedByTwoFailures.recovered, false); assert.equal(result.blockedByTwoFailures.reason, 'timed-out-operation-late-failure');
  assert.equal(result.rejectedAfterLate.accepted, false); assert.equal(result.rejectedAfterLate.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(result.clearA.ok, true); assert.equal(result.clearA.clearedCount, 1); assert.equal(result.blockedAfterOneClear.reason, 'timed-out-operation-late-failure');
  assert.equal(result.clearB.ok, true); assert.equal(result.clearB.clearedCount, 1); assert.equal(result.recoveredAfterBothClear.recovered, true);
  assert.equal(result.recoveredSchedule.accepted, true); assert.equal(result.recoveredResult?.ok, true); assert.equal(result.recoveredVerify?.ok, true);
  assert.equal(result.finalSnapshot.executor.failedTimedOutOperationCount, 0); assert.equal(result.finalSnapshot.executor.stats.lateProviderFailureClearRejected, 2); assert.equal(result.finalSnapshot.executor.stats.reviewedLateProviderFailures, 2);
  assert.equal(result.cleanupAfter, true); assert.equal(result.finalLocks.heldCount, 0); assert.equal(result.finalLocks.pendingCount, 0);
  for (const kind of ['storage-lane:operation-timeout-unsettled', 'storage-lane:operation-timeout', 'storage-lane:late-provider-failure', 'storage-lane:late-provider-failure-clear-rejected', 'storage-lane:late-provider-failures-cleared', 'block-store-lane:recover-settled', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-multi-failure-quarantine-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that two real guarded OPFS provider mutations can time out, later reject, remain separately quarantined, and recover only after scoped reviewed clearing.', observations: { ...result, harness }, claimsChecked: ['Two real guarded OPFS writes can commit before storage-lane operation timeout', 'Two late provider failures remain separate quarantine items', 'Unreviewed and scope-ambiguous clears are rejected', 'Clearing one late failure does not reopen the lane while another remains', 'Explicit scoped review of both failures permits recovery and later guarded OPFS writes verify'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks claim.', 'Timeout and late-failure quarantine are not cancellation, rollback, no-mutation, exactly-once, provider-interruption, durability, quota, eviction, crash, or production readiness evidence.'] };
}
const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '22000')) }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-multi-failure-quarantine-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser multi-failure quarantine proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_multi_failure_quarantine_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
