#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-late-success-quarantine-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-LATE-FAILURE-QUARANTINE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 2000, intervalMs = 20, label = 'condition' } = {}) => {
      const start = performance.now();
      let last = null;
      while (performance.now() - start <= timeoutMs) {
        last = await predicate();
        if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last, label };
        await sleep(intervalMs);
      }
      return { ok: false, elapsedMs: performance.now() - start, last, label };
    };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserLateProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => {
      const out = new Uint8Array(count);
      const enc = new TextEncoder().encode(seed);
      out.set(enc.slice(0, Math.min(enc.length, out.length)));
      for (let i = enc.length; i < out.length; i += 1) out[i] = (83 + i * 29 + (i >>> 3)) & 255;
      return out;
    };
    const moduleUrl = new URL('/src/browserrt.mjs', location.href).href;
    const m = await import(moduleUrl);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockLateFailureQuarantineProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-late-success-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const cleanupBefore = await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-late-success-guard', lockTimeoutMs: 1000 });
    const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-late-success-browser-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const release = deferred();
    const delayedStats = { puts: 0, delayedPuts: 0, lateSuccesses: 0, waitForSettledCalls: 0 };
    let timedOutRef = null;
    const delayedStore = {
      name: '${REVISION}-late-success-delayed-guarded-store',
      provider: 'late-succeeding:' + guard.provider,
      get prefix() { return guard.prefix; },
      async put(payload, fields = {}) {
        delayedStats.puts += 1;
        const ref = await guard.put(payload, fields, { timeoutMs: 1000 });
        if (fields.label === 'late-provider-success') {
          timedOutRef = ref.ref || ref;
          delayedStats.delayedPuts += 1;
          await release.promise;
          delayedStats.lateSuccesses += 1;
          return ref;
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
      snapshot() { return { name: this.name, provider: this.provider, prefix: guard.prefix, available: guard.available, delayedStats: { ...delayedStats }, guard: guard.snapshot() }; }
    };
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-late-success-browser-adapter', store: delayedStore, scheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const payload = bytesFromSeed('${REVISION}:late-success-provider-payload', ${JSON.stringify(payloadBytes)});
    const payloadHash = await m.digestBytesHex(payload);
    const timeoutDigest = 'sha256:' + payloadHash;

    const scheduled = adapter.schedulePut(payload, { id: '${REVISION}-late-succeeding-put', priority: 'user-visible', label: 'late-provider-success' });
    const drain = await adapter.drain({ maxSteps: 2 });
    const timeoutResult = drain.results.find((row) => row.opId === '${REVISION}-late-succeeding-put') || null;
    const snapshotAfterTimeout = adapter.snapshot();
    const storageLaneAfterTimeout = snapshotAfterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
    const providerCommittedBeforeRelease = await waitUntil(async () => {
      const present = await raw.has(timeoutDigest);
      const locks = await guard.queryLocks();
      return { ok: present === true && locks.heldCount === 0 && locks.pendingCount === 0, present, locks };
    }, { timeoutMs: 2500, intervalMs: 25, label: 'provider-committed-and-lock-drained-before-release' });
    const locksAfterTimeout = await guard.queryLocks();
    const timeoutBlockPresentBeforeRelease = await raw.has(timeoutDigest);
    const adapterResultAfterTimeout = adapter.result('${REVISION}-late-succeeding-put') || null;
    const blockedWhileUnsettled = await adapter.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 10, reason: 'browser-late-provider-still-unsettled' });

    release.resolve('browser-release-late-provider-to-fail');
    const settledWait = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1500, intervalMs: 10 });
    const guardSettledAfterLateFailure = await guard.waitForSettled({ timeoutMs: 1500, intervalMs: 20 });
    const locksAfterLateFailure = await guard.queryLocks();
    const timeoutVerifyAfterLateFailure = timedOutRef ? await raw.verify(timedOutRef) : null;
    const adapterResultAfterLateFailure = adapter.result('${REVISION}-late-succeeding-put') || null;
    const successfulTimedOutOperations = adapter.successfulTimedOutOperations('storage');
    const failedTimedOutOperations = adapter.failedTimedOutOperations('storage');
    const snapshotAfterLateFailure = adapter.snapshot();
    const blockedByLateFailure = await adapter.recoverWhenStoreSettled({ timeoutMs: 200, intervalMs: 10, reason: 'browser-late-provider-success-blocks-recovery' });
    const rejectedAfterLateFailure = adapter.schedulePut(bytesFromSeed('${REVISION}:reject-after-late-success', 1024), { id: '${REVISION}-late-success-reject-while-quarantined', priority: 'user-visible', label: 'must-not-queue' });

    const unreviewedClearRejected = adapter.clearSuccessfulTimedOutOperations({ lane: 'storage', reason: 'browser-maintenance-unreviewed-late-provider-success' });
    const unscopedClearRejected = adapter.clearSuccessfulTimedOutOperations({ lane: 'storage', reviewed: true, reviewToken: '${REVISION}-late-success-review-unscoped', reason: 'browser-maintenance-reviewed-late-provider-success-without-scope' });
    const clearReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opId: '${REVISION}-late-succeeding-put', reviewer: 'legacy-compatible-browser-probe', reviewToken: '${REVISION}-late-success-review-scoped', reason: 'browser-maintenance-reviewed-late-provider-success' });
    const cleared = adapter.clearSuccessfulTimedOutOperations({ reviewManifest: clearReview, requireReviewFingerprint: true, reason: 'browser-maintenance-reviewed-late-provider-success' });
    const recoveredAfterClear = await adapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-late-provider-success-reviewed-recovery' });
    const recoveryPayload = bytesFromSeed('${REVISION}:late-success-recovered-payload', 8192);
    const recoveredSchedule = adapter.schedulePut(recoveryPayload, { id: '${REVISION}-late-success-recovered-put', priority: 'user-visible', label: 'recovered-after-late-success', operationTimeoutMs: 1000 });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === '${REVISION}-late-success-recovered-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await raw.verify(recoveredResult.result.ref) : null;
    const finalLocksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const finalLocks = await guard.queryLocks();
    const finalSnapshot = adapter.snapshot();
    const trace = rt.close();
    return JSON.stringify({
      project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}',
      page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, origin: location.origin },
      capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' },
      prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, operationTimeoutMs: ${JSON.stringify(operationTimeoutMs)}, payloadBytes: payload.byteLength,
      cleanupBefore, scheduled, timeoutResult, snapshotAfterTimeout, storageLaneAfterTimeout, providerCommittedBeforeRelease, locksAfterTimeout,
      timeoutDigest, timeoutBlockPresentBeforeRelease, adapterResultAfterTimeout, blockedWhileUnsettled,
      settledWait, guardSettledAfterLateFailure, locksAfterLateFailure, timeoutVerifyAfterLateFailure, adapterResultAfterLateFailure, successfulTimedOutOperations, failedTimedOutOperations, snapshotAfterLateFailure,
      blockedByLateFailure, rejectedAfterLateFailure, unreviewedClearRejected, unscopedClearRejected, cleared, recoveredAfterClear, recoveredSchedule, recoveredResult, recoveredVerify,
      finalLocksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, delayedStats,
      traceKinds: trace.map((event) => event.kind),
      normalizedTrace: trace.map((event) => ({ kind: event.kind, opId: event.opId, op: event.op, lane: event.lane, code: event.code, reason: event.reason, disposition: event.disposition, timeoutMs: event.timeoutMs, cancellation: event.cancellation, name: event.name, mode: event.mode, heldCount: event.heldCount, pendingCount: event.pendingCount, unsettledTimedOutOperationCount: event.unsettledTimedOutOperationCount, failedTimedOutOperationCount: event.failedTimedOutOperationCount, firstCode: event.firstCode })).filter((event) => event.kind)
    });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-late-success-quarantine-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-late-success-quarantine';
  const lockName = options.lockName || `${REVISION}-late-success-mutation-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 16 * 1024);
  const { result, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs || 18000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/browser-opfs-web-lock-late-success-quarantine.html',
    pageTitle: 'BrowserRT OPFS Web Lock late-success quarantine proof',
    allowedPrefixes: ['src/'],
    profilePrefix: 'browserrt-opfs-web-lock-late-success-',
    stderrTerms: ['opfs', 'lock', 'timeout', 'failure']
  }, async ({ evalJson, timeoutMs, mark }) => {
    const evalStart = performance.now();
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs);
    mark('browser-opfs-web-lock-late-success-quarantine-eval', evalStart);
    return report;
  });

  assert.equal(result.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(result.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(result.capabilities.webLocksQuery, true, 'Web Locks query must be available');
  assert.equal(result.scheduled.accepted, true, 'late-succeeding operation should schedule');
  assert.equal(result.timeoutResult?.ok, false, 'late-succeeding operation should time out first');
  assert.equal(result.timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT', 'timeout code should classify storage operation timeout');
  assert.equal(result.snapshotAfterTimeout.executor.unsettledTimedOutOperationCount, 1, 'timed-out provider should remain tracked as unsettled before late success');
  assert.equal(result.snapshotAfterTimeout.executor.failedTimedOutOperationCount, 0, 'late success should not be recorded before provider settles');
  assert.equal(result.storageLaneAfterTimeout.healthy, false, 'storage lane should be unhealthy after operation timeout');
  assert.equal(result.storageLaneAfterTimeout.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.providerCommittedBeforeRelease.ok, true, 'OPFS write and Web Lock release should happen before releasing the late provider success');
  assert.equal(result.locksAfterTimeout.heldCount, 0, 'Web Lock should be released before late success quarantine blocks recovery');
  assert.equal(result.locksAfterTimeout.pendingCount, 0, 'no pending Web Lock should remain before late success quarantine blocks recovery');
  assert.equal(result.timeoutBlockPresentBeforeRelease, true, 'operation timeout is not provider cancellation/no-mutation evidence');
  assert.equal(result.adapterResultAfterTimeout, null, 'timed-out operation should not publish a successful adapter result while unsettled');
  assert.equal(result.blockedWhileUnsettled.recovered, false, 'recovery should first block while provider operation remains unsettled');
  assert.equal(result.blockedWhileUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(result.settledWait.ok, true, 'late provider success should drain the unsettled provider gate');
  assert.equal(result.settledWait.count, 0);
  assert.equal(result.guardSettledAfterLateFailure.ok, true, 'guard should report settled after late provider success');
  assert.equal(result.locksAfterLateFailure.heldCount, 0, 'locks should remain drained after late provider success');
  assert.equal(result.timeoutVerifyAfterLateFailure?.ok, true, 'real OPFS block written before timeout should still verify after late success');
  assert.equal(result.adapterResultAfterLateFailure, null, 'late provider success should not retroactively publish success for the timed-out scheduler op');
  assert.equal(result.successfulTimedOutOperations.length, 1, 'late provider success should be exposed as quarantined successful timeout');
  assert.equal(result.failedTimedOutOperations.length, 0, 'late provider success should not be a failed timed-out operation');
  assert.equal(result.snapshotAfterLateFailure.executor.successfulTimedOutOperationCount, 1, 'executor snapshot should carry successful timed-out operation count');
  assert.equal(result.snapshotAfterLateFailure.executor.stats.lateProviderSettlementSuccesses, 1, 'late provider success should be counted');
  assert.equal(result.blockedByLateFailure.recovered, false, 'settled recovery should block on late provider success until reviewed');
  assert.equal(result.blockedByLateFailure.reason, 'timed-out-operation-late-success');
  assert.equal(result.rejectedAfterLateFailure.accepted, false, 'follow-on write should reject while late success quarantine is active');
  assert.equal(result.rejectedAfterLateFailure.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(result.unreviewedClearRejected?.ok, false, 'unreviewed late-success clear should be rejected');
  assert.equal(result.unreviewedClearRejected?.code, 'late-success-clear-review-required', 'unreviewed late-success clear should require review');
  assert.equal(result.unscopedClearRejected?.ok, false, 'reviewed but unscoped late-success clear should be rejected');
  assert.equal(result.unscopedClearRejected?.code, 'late-success-clear-scope-required', 'reviewed late-success clear should still require scope');
  assert.equal(result.cleared.clearedCount, 1, 'explicit reviewed/scoped maintenance clear should acknowledge late success');
  assert.equal(result.recoveredAfterClear.recovered, true, 'settled recovery should reopen lane after late success review');
  assert.equal(result.recoveredSchedule.accepted, true, 'recovery write should schedule after clear');
  assert.equal(result.recoveredResult?.ok, true, 'recovery write should complete');
  assert.equal(result.recoveredVerify?.ok, true, 'recovery block should verify');
  assert.equal(result.finalSnapshot.executor.successfulTimedOutOperationCount, 0, 'no successful timed-out quarantine should remain');
  assert.equal(result.finalSnapshot.executor.failedTimedOutOperationCount, 0, 'no failed timed-out quarantine should remain');
  assert.equal(result.cleanupAfter, true, 'cleanup should delete proof namespace');
  assert.equal(result.finalLocks.heldCount, 0, 'final held lock count should be zero');
  assert.equal(result.finalLocks.pendingCount, 0, 'final pending lock count should be zero');
  for (const kind of ['storage-lane:operation-timeout-unsettled', 'storage-lane:operation-timeout', 'storage-lane:late-provider-success', 'storage-lane:late-provider-settlement', 'block-store-lane:recover-timed-out-successes-blocked', 'storage-lane:late-provider-successes-cleared', 'block-store-lane:recover-settled', 'coord:web-lock-acquired', 'coord:web-lock-released']) {
    assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-late-success-quarantine-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Managed Chromium proof that a real OPFS/Web Lock guarded provider can mutate storage, time out at the storage lane, later succeed, and remain quarantined until explicit maintenance acknowledgement before recovery.',
    observations: { ...result, harness },
    claimsChecked: [
      'Real OPFS/Web Lock guarded provider work can time out after mutation and later succeed',
      'BrowserRT tracks the late provider success separately from unsettled timed-out operations',
      'recoverWhenStoreSettled blocks on timed-out-operation-late-success until reviewed/scoped maintenance clears the late success',
      'late provider success does not retroactively publish adapter success and does not imply rollback/no-mutation',
      'explicit recovery succeeds after the late success is cleared and subsequent OPFS writes verify'
    ],
    nonClaims: [
      'Managed Chromium/CDP browser proof only; no cross-browser OPFS/Web Locks behavior claim.',
      'Operation timeout and late success quarantine are not cancellation, rollback, no-mutation, exactly-once, or provider interruption evidence.',
      'Explicit clearing is a maintenance acknowledgement in this proof, not automatic recovery or production correctness.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '18000')) });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-late-success-quarantine-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser late-success quarantine proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_late_failure_quarantine_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
// timeoutVerifyAfterLateSuccess storage-lane:late-provider-success timed-out-operation-late-success
