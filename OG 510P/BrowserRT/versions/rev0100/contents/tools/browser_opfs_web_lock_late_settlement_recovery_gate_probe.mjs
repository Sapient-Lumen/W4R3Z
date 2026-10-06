#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-late-settlement-recovery-gate-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-LATE-SETTLEMENT-RECOVERY-GATE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const bytesFromSeed = (seed, count) => {
      const out = new Uint8Array(count);
      const enc = new TextEncoder().encode(seed);
      out.set(enc.slice(0, Math.min(enc.length, out.length)));
      for (let i = enc.length; i < out.length; i += 1) out[i] = (61 + i * 17 + (i >>> 2)) & 255;
      return out;
    };
    const moduleUrl = new URL('/src/browserrt.mjs', location.href).href;
    const m = await import(moduleUrl);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockLateSettlementRecoveryGateProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-late-settlement-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const cleanupBefore = await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-late-settlement-guard', lockTimeoutMs: 1000 });
    const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-late-settlement-browser-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const release = deferred();
    const delayedStats = { puts: 0, delayedPuts: 0, lateSettlements: 0, waitForSettledCalls: 0 };
    let timedOutRef = null;
    const delayedStore = {
      name: '${REVISION}-late-settlement-delayed-guarded-store',
      provider: 'late-settling:' + guard.provider,
      get prefix() { return guard.prefix; },
      async put(payload, fields = {}) {
        delayedStats.puts += 1;
        const ref = await guard.put(payload, fields, { timeoutMs: 1000 });
        if (fields.label === 'late-provider-op') {
          timedOutRef = ref.ref || ref;
          delayedStats.delayedPuts += 1;
          await release.promise;
          delayedStats.lateSettlements += 1;
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
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-late-settlement-browser-adapter', store: delayedStore, scheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const payload = bytesFromSeed('${REVISION}:late-settlement-provider-payload', ${JSON.stringify(payloadBytes)});
    const payloadHash = await m.digestBytesHex(payload);
    const timeoutDigest = 'sha256:' + payloadHash;

    const scheduled = adapter.schedulePut(payload, { id: '${REVISION}-late-settling-put', priority: 'user-visible', label: 'late-provider-op' });
    const drain = await adapter.drain({ maxSteps: 2 });
    const timeoutResult = drain.results.find((row) => row.opId === '${REVISION}-late-settling-put') || null;
    const snapshotAfterTimeout = adapter.snapshot();
    const storageLaneAfterTimeout = snapshotAfterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
    const locksAfterTimeout = await guard.queryLocks();
    const timeoutBlockPresentBeforeRelease = await raw.has(timeoutDigest);
    const adapterResultAfterTimeout = adapter.result('${REVISION}-late-settling-put') || null;
    const rejectedWhileUnhealthy = adapter.schedulePut(bytesFromSeed('${REVISION}:reject-while-unhealthy', 1024), { id: '${REVISION}-late-settlement-reject-while-unhealthy', priority: 'user-visible', label: 'must-not-queue' });
    const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 70, intervalMs: 10, reason: 'browser-late-provider-still-unsettled' });
    const snapshotAfterBlockedRecovery = adapter.snapshot();

    release.resolve('browser-release-late-provider');
    const settledWait = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1000, intervalMs: 10 });
    await sleep(20);
    const locksAfterLateSettlement = await guard.queryLocks();
    const timeoutVerifyAfterLateSettlement = timedOutRef ? await raw.verify(timedOutRef) : null;
    const adapterResultAfterLateSettlement = adapter.result('${REVISION}-late-settling-put') || null;
    const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-late-provider-settled-recovery' });
    const recoveryPayload = bytesFromSeed('${REVISION}:late-settlement-recovered-payload', 8192);
    const recoveredSchedule = adapter.schedulePut(recoveryPayload, { id: '${REVISION}-late-settlement-recovered-put', priority: 'user-visible', label: 'recovered-after-late-settlement', operationTimeoutMs: 1000 });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === '${REVISION}-late-settlement-recovered-put') || null;
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
      cleanupBefore, scheduled, timeoutResult, snapshotAfterTimeout, storageLaneAfterTimeout, locksAfterTimeout,
      timeoutDigest, timeoutBlockPresentBeforeRelease, adapterResultAfterTimeout, rejectedWhileUnhealthy, blockedRecovery, snapshotAfterBlockedRecovery,
      settledWait, locksAfterLateSettlement, timeoutVerifyAfterLateSettlement, adapterResultAfterLateSettlement,
      settledRecovery, recoveredSchedule, recoveredResult, recoveredVerify,
      finalLocksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, delayedStats,
      traceKinds: trace.map((event) => event.kind),
      normalizedTrace: trace.map((event) => ({ kind: event.kind, opId: event.opId, op: event.op, lane: event.lane, code: event.code, reason: event.reason, disposition: event.disposition, timeoutMs: event.timeoutMs, cancellation: event.cancellation, name: event.name, mode: event.mode, heldCount: event.heldCount, pendingCount: event.pendingCount, unsettledTimedOutOperationCount: event.unsettledTimedOutOperationCount })).filter((event) => event.kind)
    });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-late-settlement-recovery-gate-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-late-settlement-recovery-gate';
  const lockName = options.lockName || `${REVISION}-late-settlement-mutation-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 16 * 1024);
  const { result, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs || 18000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/browser-opfs-web-lock-late-settlement-recovery-gate.html',
    pageTitle: 'BrowserRT OPFS Web Lock late-settlement recovery gate proof',
    allowedPrefixes: ['src/'],
    profilePrefix: 'browserrt-opfs-web-lock-late-settlement-',
    stderrTerms: ['opfs', 'lock', 'timeout', 'settlement']
  }, async ({ evalJson, timeoutMs, mark }) => {
    const evalStart = performance.now();
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs);
    mark('browser-opfs-web-lock-late-settlement-recovery-gate-eval', evalStart);
    return report;
  });

  assert.equal(result.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(result.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(result.capabilities.webLocksQuery, true, 'Web Locks query must be available');
  assert.equal(result.scheduled.accepted, true, 'late-settling operation should schedule');
  assert.equal(result.timeoutResult?.ok, false, 'late-settling operation should time out');
  assert.equal(result.timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT', 'timeout code should classify storage operation timeout');
  assert.equal(result.snapshotAfterTimeout.executor.unsettledTimedOutOperationCount, 1, 'timed-out provider should remain tracked as unsettled');
  assert.equal(result.snapshotAfterTimeout.executor.stats.operationTimeouts, 1, 'executor should count operation timeout');
  assert.equal(result.storageLaneAfterTimeout.healthy, false, 'storage lane should be unhealthy after operation timeout');
  assert.equal(result.storageLaneAfterTimeout.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.locksAfterTimeout.heldCount, 0, 'Web Lock should be released before recovery gate blocks on late settlement');
  assert.equal(result.locksAfterTimeout.pendingCount, 0, 'no pending Web Lock should remain before recovery gate blocks on late settlement');
  assert.equal(result.timeoutBlockPresentBeforeRelease, true, 'operation timeout is not provider cancellation/no-mutation evidence');
  assert.equal(result.adapterResultAfterTimeout, null, 'timed-out operation should not publish a successful adapter result while unsettled');
  assert.equal(result.rejectedWhileUnhealthy.accepted, false, 'follow-on write should reject while lane unhealthy');
  assert.equal(result.rejectedWhileUnhealthy.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(result.rejectedWhileUnhealthy.scheduler.noMutation, true);
  assert.equal(result.blockedRecovery.recovered, false, 'settled recovery should block while provider operation remains unsettled');
  assert.equal(result.blockedRecovery.reason, 'timed-out-operation-still-unsettled');
  assert.equal(result.blockedRecovery.settled.ok, true, 'guarded store should report Web Lock settled; late provider settlement should be the recovery gate');
  assert.equal(result.blockedRecovery.timeoutSettled.count, 1, 'blocked recovery should report one unsettled timed-out operation');
  assert.equal(result.settledWait.ok, true, 'late provider settlement should drain after explicit release');
  assert.equal(result.settledWait.count, 0);
  assert.equal(result.locksAfterLateSettlement.heldCount, 0, 'locks should remain drained after late provider settlement');
  assert.equal(result.timeoutVerifyAfterLateSettlement?.ok, true, 'real OPFS block written before timeout should verify after late settlement');
  assert.equal(result.adapterResultAfterLateSettlement, null, 'late provider success should not retroactively publish success for the timed-out scheduler op');
  assert.equal(result.settledRecovery.recovered, true, 'settled recovery should reopen lane after late provider settlement');
  assert.equal(result.recoveredSchedule.accepted, true, 'recovery write should schedule after lane recovery');
  assert.equal(result.recoveredResult?.ok, true, 'recovery write should complete');
  assert.equal(result.recoveredVerify?.ok, true, 'recovery block should verify');
  assert.equal(result.finalSnapshot.executor.unsettledTimedOutOperationCount, 0, 'no unsettled timed-out operations should remain');
  assert.equal(result.finalSnapshot.executor.stats.lateProviderSettlements, 1, 'late provider settlement should be counted');
  assert.equal(result.cleanupAfter, true, 'cleanup should delete proof namespace');
  assert.equal(result.finalLocks.heldCount, 0, 'final held lock count should be zero');
  assert.equal(result.finalLocks.pendingCount, 0, 'final pending lock count should be zero');
  for (const kind of ['storage-lane:operation-timeout-unsettled', 'storage-lane:operation-timeout', 'block-store-lane:recover-timed-out-ops-blocked', 'storage-lane:late-provider-settlement', 'block-store-lane:recover-timed-out-ops-settled', 'block-store-lane:recover-settled', 'coord:web-lock-acquired', 'coord:web-lock-released']) {
    assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-late-settlement-recovery-gate-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Managed Chromium proof that a real OPFS/Web Lock guarded provider can commit a block, release the Web Lock, then settle only after the storage-lane operation timeout: BrowserRT tracks the timed-out provider as unsettled, blocks explicit recovery even though lock state is settled, refuses to publish late success for the failed scheduler op, records late settlement, and recovers only after the late provider operation drains.',
    observations: { ...result, harness },
    claimsChecked: [
      'Real OPFS/Web Lock guarded provider work can time out after mutation but before provider settlement',
      'BrowserRT tracks the timed-out provider operation as unsettled after BRT_STORAGE_OPERATION_TIMEOUT',
      'recoverWhenStoreSettled blocks recovery on unsettled timed-out provider work even when Web Lock state is drained',
      'late provider success is traced and does not retroactively publish a successful adapter result for the failed operation',
      'explicit recovery succeeds after late provider settlement and subsequent OPFS writes verify'
    ],
    nonClaims: [
      'Managed Chromium/CDP browser proof only; no cross-browser OPFS/Web Locks behavior claim.',
      'Operation timeout is not cancellation, rollback, no-mutation, exactly-once, or provider interruption evidence.',
      'No automatic recovery, fairness, starvation-freedom, service-worker lifecycle, OPFS durability, quota, eviction, fsync, persistent-retention, throughput, latency, SLO, or production-readiness claim.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-late-settlement-recovery-gate-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser late-settlement recovery-gate proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_late_settlement_recovery_gate_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
