#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-handoff-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-HANDOFF-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 2500, intervalMs = 20, label = 'condition' } = {}) => {
      const start = performance.now(); let last = null;
      while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last, label }; await sleep(intervalMs); }
      return { ok: false, elapsedMs: performance.now() - start, last, label };
    };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 17 + (i >>> 2)) & 255; return out; };
    const moduleUrl = new URL('/src/browserrt.mjs', location.href).href;
    const m = await import(moduleUrl);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockQuarantineHandoffProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-quarantine-handoff-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const cleanupBefore = await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-quarantine-handoff-guard', lockTimeoutMs: 1000 });
    const makeScheduler = (label) => m.createCrossLaneScheduler({ label, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const release = deferred();
    const delayedStats = { puts: 0, delayedPuts: 0, waitForSettledCalls: 0 };
    let timedOutRef = null;
    const delayedStore = {
      name: '${REVISION}-quarantine-handoff-delayed-guarded-store',
      provider: 'handoff-late-success:' + guard.provider,
      get prefix() { return guard.prefix; },
      async put(payload, fields = {}) {
        delayedStats.puts += 1;
        const ref = await guard.put(payload, fields, { timeoutMs: 1000 });
        if (fields.label === 'late-success-handoff') { timedOutRef = ref.ref || ref; delayedStats.delayedPuts += 1; await release.promise; return ref; }
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
    const adapter1 = rt.blockStoreLaneAdapter({ label: '${REVISION}-quarantine-handoff-source-adapter', store: delayedStore, scheduler: makeScheduler('${REVISION}-quarantine-handoff-source-scheduler'), lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const payload = bytesFromSeed('${REVISION}:quarantine-handoff-payload', ${JSON.stringify(payloadBytes)});
    const timeoutDigest = 'sha256:' + await m.digestBytesHex(payload);
    const scheduled = adapter1.schedulePut(payload, { id: '${REVISION}-handoff-late-success-put', priority: 'user-visible', label: 'late-success-handoff' });
    const drain = await adapter1.drain({ maxSteps: 2 });
    const timeoutResult = drain.results.find((row) => row.opId === '${REVISION}-handoff-late-success-put') || null;
    const committedAndLockDrained = await waitUntil(async () => { const present = await raw.has(timeoutDigest); const locks = await guard.queryLocks(); return { ok: present === true && locks.heldCount === 0 && locks.pendingCount === 0, present, locks }; }, { timeoutMs: 2500, intervalMs: 25, label: 'opfs-commit-lock-drain-before-release' });
    const sourceSnapshotAfterTimeout = adapter1.snapshot();
    const directMarkHealthySourceRejected = adapter1.markHealthy('storage', 'unsafe-source-reopen-before-provider-settled');
    release.resolve('release-browser-late-success-for-quarantine-handoff');
    const settledWait = await adapter1.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 1500, intervalMs: 10 });
    const timeoutVerifyAfterLateSuccess = timedOutRef ? await raw.verify(timedOutRef) : null;
    const adapterResultAfterLateSuccess = adapter1.result('${REVISION}-handoff-late-success-put') || null;
    const exportedLedger = adapter1.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-export-late-success-quarantine-handoff' });
    const adapter2 = rt.blockStoreLaneAdapter({ label: '${REVISION}-quarantine-handoff-import-adapter', store: delayedStore, scheduler: makeScheduler('${REVISION}-quarantine-handoff-import-scheduler'), lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const importResult = adapter2.importTimedOutOperationQuarantine(exportedLedger, { lane: 'storage', reason: 'browser-import-late-success-quarantine-handoff', markUnhealthy: true });
    const importedSnapshot = adapter2.snapshot();
    const storageLaneAfterImport = importedSnapshot.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
    const rejectedAfterImport = adapter2.schedulePut(bytesFromSeed('${REVISION}:must-not-queue-after-import', 1024), { id: '${REVISION}-reject-after-quarantine-import', priority: 'user-visible', label: 'must-not-queue-after-import' });
    const directMarkHealthyImportRejected = adapter2.markHealthy('storage', 'unsafe-import-reopen-before-review');
    const blockedByImportedSuccess = await adapter2.recoverWhenStoreSettled({ timeoutMs: 300, intervalMs: 10, reason: 'browser-imported-quarantine-not-cleared' });
    const clearReview = adapter2.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opId: '${REVISION}-handoff-late-success-put', reviewer: 'legacy-compatible-browser-probe', reviewToken: '${REVISION}-browser-quarantine-handoff-review', reason: 'browser-reviewed-imported-late-success' });
    const cleared = adapter2.clearSuccessfulTimedOutOperations({ reviewManifest: clearReview, requireReviewFingerprint: true, reason: 'browser-reviewed-imported-late-success' });
    const recoveredAfterClear = await adapter2.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-imported-quarantine-reviewed-recovery' });
    const recoveryPayload = bytesFromSeed('${REVISION}:quarantine-handoff-recovered-payload', 8192);
    const recoveredSchedule = adapter2.schedulePut(recoveryPayload, { id: '${REVISION}-quarantine-handoff-recovered-put', priority: 'user-visible', label: 'recovered-after-quarantine-handoff', operationTimeoutMs: 1000 });
    const recoveryDrain = await adapter2.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === '${REVISION}-quarantine-handoff-recovered-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await raw.verify(recoveredResult.result.ref) : null;
    const finalLocksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const finalLocks = await guard.queryLocks();
    const finalSnapshot = adapter2.snapshot();
    const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, operationTimeoutMs: ${JSON.stringify(operationTimeoutMs)}, payloadBytes: payload.byteLength, cleanupBefore, scheduled, timeoutResult, committedAndLockDrained, sourceSnapshotAfterTimeout, directMarkHealthySourceRejected, settledWait, timeoutDigest, timeoutVerifyAfterLateSuccess, adapterResultAfterLateSuccess, exportedLedger, importResult, importedSnapshot, storageLaneAfterImport, rejectedAfterImport, directMarkHealthyImportRejected, blockedByImportedSuccess, cleared, recoveredAfterClear, recoveredSchedule, recoveredResult, recoveredVerify, finalLocksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, traceKinds: trace.map((row) => row.kind), traceTail: trace.slice(-25) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const suffix = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
  const prefix = `brt-${REVISION}-quarantine-handoff-${suffix}`;
  const lockPrefix = `${REVISION}:quarantine-handoff:${suffix}`;
  const lockName = 'mutation';
  const operationTimeoutMs = 350;
  const payloadBytes = 48 * 1024;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 18000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-handoff.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine handoff proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-opfs-web-lock-quarantine-handoff-', stderrTerms: ['opfs', 'lock', 'timeout', 'quarantine'] }, async ({ evalJson, timeoutMs, mark }) => {
    const evalStart = performance.now();
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs);
    mark('browser-opfs-web-lock-quarantine-handoff-eval', evalStart);
    return report;
  });
  assert.equal(result.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(result.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(result.capabilities.webLocksQuery, true, 'Web Locks query must be available');
  assert.equal(result.scheduled.accepted, true, 'source operation should schedule');
  assert.equal(result.timeoutResult?.ok, false, 'source operation should time out before late success');
  assert.equal(result.timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.committedAndLockDrained.ok, true, 'real OPFS write should commit and Web Lock should drain before releasing provider');
  assert.equal(result.sourceSnapshotAfterTimeout.executor.unsettledTimedOutOperationCount, 1);
  assert.equal(result.directMarkHealthySourceRejected.healthy, false, 'direct source reopen should be blocked while timed-out op unsettled');
  assert.equal(result.directMarkHealthySourceRejected.disposition, 'rejected-timed-out-operation-quarantine');
  assert.equal(result.settledWait.ok, true, 'late success should settle');
  assert.equal(result.timeoutVerifyAfterLateSuccess?.ok, true, 'real OPFS block should verify after late success');
  assert.equal(result.adapterResultAfterLateSuccess, null, 'late success should not retroactively publish adapter result');
  assert.equal(result.exportedLedger.successfulTimedOutOperations.length, 1, 'exported ledger should include late success quarantine');
  assert.equal(result.importResult.ok, true, 'fresh adapter should import quarantine ledger');
  assert.equal(result.importResult.importedCount, 1);
  assert.equal(result.storageLaneAfterImport.healthy, false, 'imported quarantine should mark lane unhealthy');
  assert.equal(result.storageLaneAfterImport.healthReason, 'timed-out-operation-quarantine-imported');
  assert.equal(result.rejectedAfterImport.accepted, false, 'fresh adapter should reject writes while imported quarantine is active');
  assert.equal(result.rejectedAfterImport.scheduler.noMutation, true);
  assert.equal(result.directMarkHealthyImportRejected.healthy, false, 'direct markHealthy should not bypass imported quarantine');
  assert.equal(result.blockedByImportedSuccess.recovered, false);
  assert.equal(result.blockedByImportedSuccess.reason, 'timed-out-operation-late-success');
  assert.equal(result.cleared.clearedCount, 1);
  assert.equal(result.recoveredAfterClear.recovered, true);
  assert.equal(result.recoveredSchedule.accepted, true);
  assert.equal(result.recoveredResult?.ok, true);
  assert.equal(result.recoveredVerify?.ok, true);
  assert.equal(result.finalSnapshot.executor.successfulTimedOutOperationCount, 0);
  assert.equal(result.cleanupAfter, true);
  assert.equal(result.finalLocks.heldCount, 0);
  assert.equal(result.finalLocks.pendingCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-export','storage-lane:timed-out-quarantine-import','storage-lane:provider-healthy-rejected','storage-lane:late-provider-success','coord:web-lock-acquired','coord:web-lock-released','block-store-lane:recover-timed-out-successes-blocked','block-store-lane:recover-settled']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-handoff-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that a real OPFS/Web Lock late-success timeout quarantine can be exported, imported into a fresh adapter, mark that lane unhealthy, block direct markHealthy bypass, and recover only after reviewed/scoped clearing.', observations: { ...result, harness }, claimsChecked: ['Real OPFS/Web Lock provider work can time out after mutation and later succeed', 'The late-success quarantine exports as a ledger', 'A fresh adapter importing the ledger marks the storage lane unhealthy and rejects writes', 'Direct markHealthy cannot bypass imported quarantine', 'Reviewed/scoped clear permits recovery and later OPFS writes verify'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks claim.', 'Quarantine handoff is not automatic persistence, provider cancellation, rollback, no-mutation, exactly-once, durability, quota, eviction, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '18000')) }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-handoff-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser quarantine handoff proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_handoff_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
