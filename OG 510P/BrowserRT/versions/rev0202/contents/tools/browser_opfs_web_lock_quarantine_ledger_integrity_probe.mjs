#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-ledger-integrity-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-LEDGER-INTEGRITY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 2500, intervalMs = 20 } = {}) => {
      const start = performance.now(); let last = null;
      while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last }; await sleep(intervalMs); }
      return { ok: false, elapsedMs: performance.now() - start, last };
    };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserMixedLateProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 17 + (i >>> 2)) & 255; return out; };
    const moduleUrl = new URL('/src/browserrt.mjs', location.href).href;
    const m = await import(moduleUrl);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockQuarantineLedgerRoundtripProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-quarantine-ledger-integrity-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const cleanupBefore = await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-quarantine-ledger-integrity-guard', lockTimeoutMs: 1000 });
    const makeScheduler = (label) => m.createCrossLaneScheduler({ label, lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const releases = { success: deferred(), failure: deferred() };
    const refs = {};
    const delayedStats = { puts: 0, delayedPuts: 0, lateSuccesses: 0, lateFailures: 0, waitForSettledCalls: 0 };
    const delayedStore = {
      name: '${REVISION}-quarantine-ledger-integrity-delayed-guarded-store', provider: 'mixed-late-outcome:' + guard.provider,
      async put(payload, fields = {}) {
        delayedStats.puts += 1;
        const ref = await guard.put(payload, fields, { timeoutMs: 1000 });
        const label = fields.label || 'unlabeled'; refs[label] = ref.ref || ref;
        if (label === 'mixed-late-success') { delayedStats.delayedPuts += 1; await releases.success.promise; delayedStats.lateSuccesses += 1; return ref; }
        if (label === 'mixed-late-failure') { delayedStats.delayedPuts += 1; await releases.failure.promise; delayedStats.lateFailures += 1; throw codedError('BRT_OPFS_OPERATION_FAILED', 'browser mixed late provider failure after storage-lane timeout', { digest: refs[label].digest, label }); }
        return ref;
      },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); }, async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); }, async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); }, async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); }, async estimate() { return await guard.estimate({ timeoutMs: 1000 }); }, async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); },
      async waitForSettled(options = {}) { delayedStats.waitForSettledCalls += 1; return await guard.waitForSettled(options); },
      snapshot() { return { name: this.name, provider: this.provider, delayedStats: { ...delayedStats }, guard: guard.snapshot() }; }
    };
    const sourceScheduler = makeScheduler('${REVISION}-quarantine-ledger-integrity-browser-source-scheduler');
    const sourceAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-quarantine-ledger-integrity-browser-source-adapter', store: delayedStore, scheduler: sourceScheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const payloadSuccess = bytesFromSeed('${REVISION}:browser-mixed-late-success-payload', ${JSON.stringify(payloadBytes)});
    const payloadFailure = bytesFromSeed('${REVISION}:browser-mixed-late-failure-payload', ${JSON.stringify(payloadBytes)});
    const digestSuccess = 'sha256:' + await m.digestBytesHex(payloadSuccess);
    const digestFailure = 'sha256:' + await m.digestBytesHex(payloadFailure);
    const scheduledSuccess = sourceAdapter.schedulePut(payloadSuccess, { id: '${REVISION}-mixed-late-success-put', priority: 'user-visible', label: 'mixed-late-success' });
    const scheduledFailure = sourceAdapter.schedulePut(payloadFailure, { id: '${REVISION}-mixed-late-failure-put', priority: 'user-visible', label: 'mixed-late-failure' });
    const dispatchSuccess = sourceScheduler.dispatchNext();
    const dispatchFailure = sourceScheduler.dispatchNext();
    const [timeoutSuccess, timeoutFailure] = await Promise.all([sourceAdapter.executor.executeDispatched(dispatchSuccess), sourceAdapter.executor.executeDispatched(dispatchFailure)]);
    const providerCommittedBeforeRelease = await waitUntil(async () => Boolean(refs['mixed-late-success'] && refs['mixed-late-failure']), { timeoutMs: 3000, intervalMs: 25 });
    const verifySuccessBeforeRelease = refs['mixed-late-success'] ? await guard.verify(refs['mixed-late-success'], { timeoutMs: 1000 }) : null;
    const verifyFailureBeforeRelease = refs['mixed-late-failure'] ? await guard.verify(refs['mixed-late-failure'], { timeoutMs: 1000 }) : null;
    const sourceSnapshotAfterTimeouts = sourceAdapter.snapshot();
    const locksAfterTimeouts = await guard.queryLocks();
    const exportBeforeSettle = sourceAdapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-export-before-late-settlement' });
    const blockedWhileUnsettled = await sourceAdapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-source-provider-still-unsettled' });
    releases.success.resolve('release-browser-success'); releases.failure.resolve('release-browser-failure');
    const sourceSettled = await sourceAdapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 20 });
    const sourceQuarantine = sourceAdapter.timedOutOperationQuarantine('storage');
    const ledger = sourceAdapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-export-mixed-late-outcome-quarantine' });
    const verifySuccessAfterLate = await guard.verify(refs['mixed-late-success'], { timeoutMs: 1000 });
    const verifyFailureAfterLate = await guard.verify(refs['mixed-late-failure'], { timeoutMs: 1000 });

    const importedScheduler = makeScheduler('${REVISION}-quarantine-ledger-integrity-browser-imported-scheduler');
    const importedStore = {
      name: '${REVISION}-quarantine-ledger-integrity-imported-guarded-store', provider: 'imported-ledger:' + guard.provider,
      async put(payload, fields = {}) { return await guard.put(payload, fields, { timeoutMs: 1000 }); },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); }, async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); }, async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); }, async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); }, async estimate() { return await guard.estimate({ timeoutMs: 1000 }); }, async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); }, async waitForSettled(options = {}) { return await guard.waitForSettled(options); }, snapshot() { return { name: this.name, provider: this.provider, guard: guard.snapshot() }; }
    };
    const importedAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-quarantine-ledger-integrity-browser-imported-adapter', store: importedStore, scheduler: importedScheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const clone = (value) => JSON.parse(JSON.stringify(value));
    const makeBadLedgers = (base) => {
      const cases = [];
      let l = clone(base); delete l.counts; cases.push(['missing-counts', l]);
      l = clone(base); l.counts.total += 1; cases.push(['counts.total mismatch', l]);
      l = clone(base); delete l.failedTimedOutOperations; cases.push(['missing-failed-array', l]);
      l = clone(base); l.failedTimedOutOperations[0].opId = l.successfulTimedOutOperations[0].opId; cases.push(['duplicate-opid', l]);
      l = clone(base); delete l.successfulTimedOutOperations[0].opId; cases.push(['missing-opid', l]);
      l = clone(base); l.schema = 'brt.storageLane.timedOutOperationQuarantine.v999'; cases.push(['wrong-schema', l]);
      return cases;
    };
    const badImportResults = [];
    for (const [name, badLedger] of makeBadLedgers(ledger)) {
      const before = importedAdapter.snapshot();
      const rejected = importedAdapter.importTimedOutOperationQuarantine(badLedger, { lane: 'storage', reason: 'browser-reject-' + name, markUnhealthy: true });
      const after = importedAdapter.snapshot();
      const laneAfter = after.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
      badImportResults.push({ name, rejected, beforeQuarantineCount: before.timedOutOperationQuarantine.totalCount, afterQuarantineCount: after.timedOutOperationQuarantine.totalCount, laneHealthy: laneAfter?.healthy ?? null, healthReason: laneAfter?.healthReason ?? null });
    }
    const importResult = importedAdapter.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'browser-import-mixed-late-outcome-quarantine', markUnhealthy: true });
    const importedQuarantine = importedAdapter.timedOutOperationQuarantine('storage');
    const importedLaneAfterImport = importedAdapter.snapshot().executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
    const blockedImportedRecovery = await importedAdapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-imported-quarantine-blocks-recovery' });
    const rejectedWhileImportedQuarantined = importedAdapter.schedulePut(bytesFromSeed('${REVISION}:reject-imported-quarantine', 1024), { id: '${REVISION}-reject-while-imported-quarantine', label: 'reject-while-imported-quarantine' });
    const unreviewedUnifiedClear = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reason: 'browser-unreviewed-unified-clear' });
    const missingTokenUnifiedClear = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reviewed: true, reason: 'browser-missing-token-unified-clear' });
    const unscopedUnifiedClear = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', reviewed: true, reviewToken: '${REVISION}-browser-unscoped-review', reason: 'browser-unscoped-unified-clear' });
    const clearSuccessOnly = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'successful', opId: '${REVISION}-mixed-late-success-put', reviewed: true, reviewToken: '${REVISION}-browser-success-only-review', reason: 'browser-review-success-only' });
    const blockedAfterSuccessOnly = await importedAdapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-failure-still-quarantined-after-success-clear' });
    const clearRemaining = importedAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', opIds: ['${REVISION}-mixed-late-success-put', '${REVISION}-mixed-late-failure-put'], reviewed: true, reviewToken: '${REVISION}-browser-reviewed-mixed-quarantine', reason: 'browser-reviewed-scoped-mixed-outcome-clear' });
    const recoveredAfterClear = await importedAdapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-imported-quarantine-reviewed-recovery' });
    const recoveryPayload = bytesFromSeed('${REVISION}:quarantine-ledger-recovered-payload', 8192);
    const recoveredSchedule = importedAdapter.schedulePut(recoveryPayload, { id: '${REVISION}-quarantine-ledger-recovered-put', priority: 'user-visible', label: 'recovered-after-ledger-clear', operationTimeoutMs: 1000 });
    const recoveryDrain = await importedAdapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === '${REVISION}-quarantine-ledger-recovered-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await guard.verify(recoveredResult.result.ref, { timeoutMs: 1000 }) : null;
    const finalLocksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const finalLocks = await guard.queryLocks();
    const finalSnapshot = importedAdapter.snapshot();
    const trace = rt.close();
    return { capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, cleanupBefore, scheduledSuccess, scheduledFailure, dispatchSuccess, dispatchFailure, timeoutSuccess, timeoutFailure, providerCommittedBeforeRelease, verifySuccessBeforeRelease, verifyFailureBeforeRelease, sourceSnapshotAfterTimeouts, locksAfterTimeouts, exportBeforeSettle, blockedWhileUnsettled, sourceSettled, sourceQuarantine, ledger, verifySuccessAfterLate, verifyFailureAfterLate, badImportResults, importResult, importedQuarantine, importedLaneAfterImport, blockedImportedRecovery, rejectedWhileImportedQuarantined, unreviewedUnifiedClear, missingTokenUnifiedClear, unscopedUnifiedClear, clearSuccessOnly, blockedAfterSuccessOnly, clearRemaining, recoveredAfterClear, recoveredSchedule, recoveredResult, recoveredVerify, finalLocksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, delayedStats, refs, digestSuccess, digestFailure, traceKinds: trace.map((event) => event.kind) };
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-ledger-integrity-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-ledger-integrity';
  const lockName = options.lockName || `${REVISION}-quarantine-ledger-integrity-mutation-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 12 * 1024);
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 24000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-ledger-integrity.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine ledger integrity proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-opfs-web-lock-quarantine-ledger-', stderrTerms: ['opfs','lock','timeout','quarantine'] }, async ({ evalJson, timeoutMs, mark }) => {
    const evalStart = performance.now(); const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs); mark('browser-opfs-web-lock-quarantine-ledger-integrity-eval', evalStart); return report;
  });

  assert.equal(result.capabilities.opfs, true);
  assert.equal(result.capabilities.webLocks, true);
  assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.scheduledSuccess.accepted, true); assert.equal(result.scheduledFailure.accepted, true);
  assert.equal(result.dispatchSuccess.dispatched, true); assert.equal(result.dispatchFailure.dispatched, true);
  assert.equal(result.timeoutSuccess.ok, false); assert.equal(result.timeoutFailure.ok, false);
  assert.equal(result.timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(result.timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.providerCommittedBeforeRelease.ok, true);
  assert.equal(result.verifySuccessBeforeRelease.ok, true); assert.equal(result.verifyFailureBeforeRelease.ok, true);
  assert.equal(result.sourceSnapshotAfterTimeouts.executor.unsettledTimedOutOperationCount, 2);
  assert.equal(result.exportBeforeSettle.schema, 'brt.storageLane.timedOutOperationQuarantine.v1'); assert.equal(result.exportBeforeSettle.counts.unsettled, 2);
  assert.equal(result.blockedWhileUnsettled.recovered, false); assert.equal(result.blockedWhileUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(result.sourceSettled.ok, true);
  assert.equal(result.sourceQuarantine.successfulCount, 1); assert.equal(result.sourceQuarantine.failedCount, 1); assert.equal(result.sourceQuarantine.unsettledCount, 0);
  assert.equal(result.ledger.schema, 'brt.storageLane.timedOutOperationQuarantine.v1'); assert.equal(result.ledger.counts.successful, 1); assert.equal(result.ledger.counts.failed, 1); assert.equal(result.ledger.counts.total, 2);
  assert.equal(result.verifySuccessAfterLate.ok, true); assert.equal(result.verifyFailureAfterLate.ok, true);
  assert.equal(result.badImportResults.length, 6);
  for (const row of result.badImportResults) { assert.equal(row.rejected.ok, false, row.name); assert.equal(row.rejected.code, 'timed-out-quarantine-import-rejected', row.name); assert.equal(row.rejected.disposition, 'rejected-ledger-integrity', row.name); assert.equal(row.beforeQuarantineCount, 0, row.name); assert.equal(row.afterQuarantineCount, 0, row.name); assert.equal(row.laneHealthy, true, row.name); }
  assert.equal(result.importResult.ok, true); assert.equal(result.importResult.importedCount, 2); assert.equal(result.importResult.successfulCount, 1); assert.equal(result.importResult.failedCount, 1);
  assert.equal(result.importedQuarantine.successfulCount, 1); assert.equal(result.importedQuarantine.failedCount, 1); assert.equal(result.importedQuarantine.totalCount, 2);
  assert.equal(result.importedLaneAfterImport.healthy, false); assert.equal(result.importedLaneAfterImport.healthReason, 'timed-out-operation-quarantine-imported');
  assert.equal(result.blockedImportedRecovery.recovered, false); assert.equal(result.blockedImportedRecovery.reason, 'timed-out-operation-late-success');
  assert.equal(result.rejectedWhileImportedQuarantined.accepted, false); assert.equal(result.rejectedWhileImportedQuarantined.scheduler.noMutation, true);
  assert.equal(result.unreviewedUnifiedClear.ok, false); assert.equal(result.unreviewedUnifiedClear.code, 'timed-out-quarantine-clear-review-required');
  assert.equal(result.missingTokenUnifiedClear.ok, false); assert.equal(result.missingTokenUnifiedClear.code, 'timed-out-quarantine-clear-review-token-required');
  assert.equal(result.unscopedUnifiedClear.ok, false); assert.equal(result.unscopedUnifiedClear.code, 'timed-out-quarantine-clear-scope-required');
  assert.equal(result.clearSuccessOnly.ok, true); assert.equal(result.clearSuccessOnly.successfulClearedCount, 1); assert.equal(result.clearSuccessOnly.failedClearedCount, 0);
  assert.equal(result.blockedAfterSuccessOnly.recovered, false); assert.equal(result.blockedAfterSuccessOnly.reason, 'timed-out-operation-late-failure');
  assert.equal(result.clearRemaining.ok, true); assert.equal(result.clearRemaining.failedClearedCount, 1); assert.equal(result.clearRemaining.quarantine.totalCount, 0);
  assert.equal(result.recoveredAfterClear.recovered, true);
  assert.equal(result.recoveredSchedule.accepted, true); assert.equal(result.recoveredResult?.ok, true); assert.equal(result.recoveredVerify?.ok, true);
  assert.equal(result.finalSnapshot.timedOutOperationQuarantine.totalCount, 0); assert.equal(result.finalSnapshot.executor.stats.quarantineLedgerImports, 1); assert.equal(result.finalSnapshot.executor.stats.quarantineLedgerImportIntegrityRejected, result.badImportResults.length); assert.equal(result.finalSnapshot.executor.stats.timedOutOperationQuarantineCleared, 2);
  assert.equal(result.cleanupAfter, true); assert.equal(result.finalLocks.heldCount, 0); assert.equal(result.finalLocks.pendingCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-export', 'storage-lane:timed-out-quarantine-import-rejected', 'storage-lane:timed-out-quarantine-import', 'storage-lane:timed-out-quarantine-clear-rejected', 'storage-lane:timed-out-quarantine-cleared', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-ledger-integrity-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that a real OPFS/Web Lock guarded provider can produce mixed late-success/late-failure timeout quarantine, reject malformed ledger imports atomically, then export/import the valid ledger, block recovery, reject unsafe unified clears, and recover only after reviewed/scoped clearing.', observations: { ...result, harness }, claimsChecked: ['real OPFS/Web Lock operations can produce mixed late timeout outcomes', 'malformed quarantine ledger imports fail closed without partial mutation', 'quarantine ledger export/import preserves success and failure buckets', 'imported quarantine marks the lane unhealthy and blocks recovery', 'unified clear requires review token and scope', 'clearing only success does not recover while late failure remains'], nonClaims: ['Managed Chromium only; no cross-browser claim.', 'Timeout quarantine is not cancellation, rollback, durability, no-mutation, exactly-once, or production readiness evidence.'] };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '24000')) });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-ledger-integrity-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser quarantine ledger integrity proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_quarantine_ledger_roundtrip_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
