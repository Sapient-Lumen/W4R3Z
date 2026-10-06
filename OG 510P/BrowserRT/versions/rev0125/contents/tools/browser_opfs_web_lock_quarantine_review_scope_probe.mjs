#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-review-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-REVIEW-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 3000, intervalMs = 25, label = 'condition' } = {}) => {
      const start = performance.now(); let last = null;
      while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last, label }; await sleep(intervalMs); }
      return { ok: false, elapsedMs: performance.now() - start, last, label };
    };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserReviewScopeProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (91 + i * 29 + (i >>> 3)) & 255; return out; };
    const clone = (value) => JSON.parse(JSON.stringify(value));
    const m = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockQuarantineReviewScopeProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-review-scope-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const cleanupBefore = await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-review-scope-guard', lockTimeoutMs: 1000 });
    const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-review-scope-browser-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const releaseSuccess = deferred(); const releaseFailure = deferred();
    const delayedStats = { puts: 0, delayedSuccessPuts: 0, delayedFailurePuts: 0, lateSuccesses: 0, lateFailures: 0, waitForSettledCalls: 0 };
    const refs = { success: null, failure: null };
    const delayedStore = {
      name: '${REVISION}-review-scope-delayed-guarded-store', provider: 'review-scope:' + guard.provider,
      async put(payload, fields = {}) {
        delayedStats.puts += 1;
        const put = await guard.put(payload, fields, { timeoutMs: 1000 });
        const label = String(fields.label || '');
        if (label.includes('success')) { refs.success = put.ref || put; delayedStats.delayedSuccessPuts += 1; await releaseSuccess.promise; delayedStats.lateSuccesses += 1; return put; }
        if (label.includes('failure')) { refs.failure = put.ref || put; delayedStats.delayedFailurePuts += 1; await releaseFailure.promise; delayedStats.lateFailures += 1; throw codedError('BRT_BROWSER_REVIEW_BINDING_LATE_FAILURE', 'browser review-scope late failure after committed guarded OPFS write', { digest: put.digest, bytes: put.bytes }); }
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
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-review-scope-browser-source-adapter', store: delayedStore, scheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const successPayload = bytesFromSeed('${REVISION}:review-scope-success-payload', ${JSON.stringify(payloadBytes)});
    const failurePayload = bytesFromSeed('${REVISION}:review-scope-failure-payload', ${JSON.stringify(payloadBytes)});
    const successDigest = 'sha256:' + await m.digestBytesHex(successPayload);
    const failureDigest = 'sha256:' + await m.digestBytesHex(failurePayload);
    adapter.schedulePut(successPayload, { id: '${REVISION}-review-scope-success-timeout', priority: 'user-visible', label: 'review-scope-success' });
    adapter.schedulePut(failurePayload, { id: '${REVISION}-review-scope-failure-timeout', priority: 'user-visible', label: 'review-scope-failure' });
    const dispatchSuccess = scheduler.dispatchNext(); const dispatchFailure = scheduler.dispatchNext();
    const [timeoutSuccess, timeoutFailure] = await Promise.all([adapter.executor.executeDispatched(dispatchSuccess), adapter.executor.executeDispatched(dispatchFailure)]);
    const providerCommittedBeforeRelease = await waitUntil(async () => {
      const successPresent = await raw.has(successDigest); const failurePresent = await raw.has(failureDigest); const locks = await guard.queryLocks();
      return { ok: successPresent && failurePresent && locks.heldCount === 0 && locks.pendingCount === 0, successPresent, failurePresent, locks };
    }, { timeoutMs: 3000, intervalMs: 25, label: 'both-provider-writes-committed-before-release' });
    releaseSuccess.resolve('browser-release-review-scope-success'); releaseFailure.resolve('browser-release-review-scope-failure');
    const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 10 });
    const successVerifyAfterLate = await raw.verify(successDigest); const failureVerifyAfterLate = await raw.verify(failureDigest);
    const quarantine = adapter.timedOutOperationQuarantine('storage');
    const ledger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-review-scope-export' });
    const tamperedLedger = clone(ledger); tamperedLedger.successfulTimedOutOperations[0].opId = tamperedLedger.successfulTimedOutOperations[0].opId + ':tampered';

    const tamperedScheduler = m.createCrossLaneScheduler({ label: '${REVISION}-review-scope-browser-tampered-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const tamperedAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-review-scope-browser-tampered-adapter', store: guard, scheduler: tamperedScheduler, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const tamperedImport = tamperedAdapter.importTimedOutOperationQuarantine(tamperedLedger, { lane: 'storage', reason: 'browser-reject-tampered-review-scope-ledger' });
    const tamperedQuarantine = tamperedAdapter.timedOutOperationQuarantine('storage');
    const tamperedLane = tamperedAdapter.snapshot().executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;

    const importScheduler = m.createCrossLaneScheduler({ label: '${REVISION}-review-scope-browser-import-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const importAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-review-scope-browser-import-adapter', store: guard, scheduler: importScheduler, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const validImport = importAdapter.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'browser-valid-review-scope-import', markUnhealthy: false });
    const importedQuarantine = importAdapter.timedOutOperationQuarantine('storage');
    const importedLane = importAdapter.snapshot().executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
    const rejectedWhileQuarantined = importAdapter.schedulePut(bytesFromSeed('${REVISION}:should-not-mutate-while-review-bound', 1024), { id: '${REVISION}-review-scope-rejected-while-quarantined', label: 'should-not-mutate' });
    const missingFingerprintClear = importAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reviewed: true, reviewToken: '${REVISION}-missing-fingerprint', requireReviewFingerprint: true, reason: 'browser-missing-review-fingerprint' });
    const staleFingerprintClear = importAdapter.clearTimedOutOperationQuarantine({ lane: 'storage', category: 'all', allowLaneWide: true, reviewed: true, reviewToken: '${REVISION}-stale-fingerprint', reviewFingerprint: 'brt-qfp-v1:0000000000000000', requireReviewFingerprint: true, reason: 'browser-stale-review-fingerprint' });
    const scopedReviewManifest = importAdapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opIds: importedQuarantine.opIds.successful, reviewer: 'rev0078-browser-proof', reviewToken: '${REVISION}-scope-specific-review-token', reason: 'browser-bind-review-to-success-only-scope' });
    const scopeOverrideClear = importAdapter.clearTimedOutOperationQuarantine({ reviewManifest: scopedReviewManifest, category: 'all', allowLaneWide: true, requireReviewFingerprint: true, reason: 'browser-reject-review-manifest-scope-override' });
    const tokenOverrideClear = importAdapter.clearTimedOutOperationQuarantine({ reviewManifest: scopedReviewManifest, reviewToken: '${REVISION}-copied-token-override', requireReviewFingerprint: true, reason: 'browser-reject-review-manifest-token-override' });
    const fingerprintOverrideClear = importAdapter.clearTimedOutOperationQuarantine({ reviewManifest: scopedReviewManifest, reviewFingerprint: scopedReviewManifest.reviewFingerprint, requireReviewFingerprint: true, reason: 'browser-reject-review-manifest-fingerprint-override' });
    const staleCountManifest = clone(scopedReviewManifest); staleCountManifest.counts.total += 1;
    const countMismatchClear = importAdapter.clearTimedOutOperationQuarantine({ reviewManifest: staleCountManifest, requireReviewFingerprint: true, reason: 'browser-reject-review-manifest-count-mismatch' });
    const reviewManifest = importAdapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0078-browser-proof', reviewToken: '${REVISION}-scope-bound-review-token', reason: 'browser-bind-review-to-current-quarantine' });
    const clearWithManifest = importAdapter.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-bound-review-manifest' });
    const recovered = await importAdapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'browser-review-scope-cleared' });
    const recoveryPayload = bytesFromSeed('${REVISION}:review-scope-recovered-payload', 4096);
    const recoverySchedule = importAdapter.schedulePut(recoveryPayload, { id: '${REVISION}-review-scope-recovered-put', priority: 'user-visible', label: 'review-scope-recovered', operationTimeoutMs: 1000 });
    const recoveryDrain = await importAdapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === '${REVISION}-review-scope-recovered-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await raw.verify(recoveredResult.result.ref) : null;
    const finalLocksBeforeCleanup = await guard.queryLocks(); const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 }); const finalLocks = await guard.queryLocks(); const finalSnapshot = importAdapter.snapshot(); const trace = rt.close();
    return JSON.stringify({
      project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, operationTimeoutMs: ${JSON.stringify(operationTimeoutMs)}, payloadBytes: ${JSON.stringify(payloadBytes)}, cleanupBefore, dispatchSuccess, dispatchFailure, timeoutSuccess, timeoutFailure, providerCommittedBeforeRelease, settled, successDigest, failureDigest, successVerifyAfterLate, failureVerifyAfterLate, quarantine, ledger, tamperedImport, tamperedQuarantine, tamperedLane, validImport, importedQuarantine, importedLane, rejectedWhileQuarantined, missingFingerprintClear, staleFingerprintClear, scopedReviewManifest, scopeOverrideClear, tokenOverrideClear, fingerprintOverrideClear, countMismatchClear, reviewManifest, clearWithManifest, recovered, recoverySchedule, recoveryDrain, recoveredResult, recoveredVerify, finalLocksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, delayedStats, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('fingerprint') || event.kind.includes('late-provider') || event.kind.includes('operation-timeout')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, reason: event.reason ?? null, code: event.code ?? null, disposition: event.disposition ?? null, quarantineFingerprint: event.quarantineFingerprint ?? null, reviewFingerprint: event.reviewFingerprint ?? null }))
    });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-review-scope-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-review-scope';
  const lockName = options.lockName || `${REVISION}-quarantine-review-scope-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 8 * 1024);
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 24000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-review-scope.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine review binding proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-opfs-web-lock-quarantine-review-scope-', stderrTerms: ['opfs', 'lock', 'quarantine', 'review'] }, async ({ evalJson, timeoutMs, mark, profileDir }) => {
    const evalStart = performance.now(); const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs); mark('browser-opfs-web-lock-quarantine-review-scope-eval', evalStart); const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 }); return { ...report, profileReap };
  });

  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.timeoutSuccess.ok, false); assert.equal(result.timeoutFailure.ok, false); assert.equal(result.timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(result.timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.providerCommittedBeforeRelease.ok, true); assert.equal(result.settled.ok, true); assert.equal(result.successVerifyAfterLate.ok, true); assert.equal(result.failureVerifyAfterLate.ok, true);
  assert.equal(result.quarantine.successfulCount, 1); assert.equal(result.quarantine.failedCount, 1); assert.match(result.quarantine.quarantineFingerprint, /^brt-qfp-v1:/); assert.equal(result.ledger.quarantineFingerprint, result.quarantine.quarantineFingerprint);
  assert.equal(result.tamperedImport.ok, false); assert.equal(result.tamperedImport.disposition, 'rejected-ledger-integrity'); assert.equal(result.tamperedQuarantine.totalCount, 0); assert.equal(result.tamperedLane.healthy, true);
  assert.equal(result.validImport.ok, true); assert.equal(result.validImport.markUnhealthyRequested, false); assert.equal(result.validImport.markUnhealthyForced, true); assert.equal(result.validImport.quarantineFingerprint, result.ledger.quarantineFingerprint); assert.equal(result.importedQuarantine.totalCount, 2); assert.equal(result.importedLane.healthy, false);
  assert.equal(result.rejectedWhileQuarantined.accepted, false); assert.equal(result.rejectedWhileQuarantined.scheduler.noMutation, true);
  assert.equal(result.missingFingerprintClear.ok, false); assert.equal(result.missingFingerprintClear.code, 'timed-out-quarantine-clear-review-fingerprint-required');
  assert.equal(result.staleFingerprintClear.ok, false); assert.equal(result.staleFingerprintClear.code, 'timed-out-quarantine-clear-review-fingerprint-mismatch');
  assert.equal(result.scopedReviewManifest.reviewFingerprint, result.importedQuarantine.reviewFingerprint); assert.equal(result.scopeOverrideClear.ok, false); assert.equal(result.scopeOverrideClear.code, 'timed-out-quarantine-clear-review-manifest-scope-override'); assert.equal(result.tokenOverrideClear.ok, false); assert.equal(result.tokenOverrideClear.code, 'timed-out-quarantine-clear-review-manifest-scope-override'); assert.equal(result.fingerprintOverrideClear.ok, false); assert.equal(result.fingerprintOverrideClear.code, 'timed-out-quarantine-clear-review-manifest-scope-override');
  assert.equal(result.countMismatchClear.ok, false); assert.equal(result.countMismatchClear.code, 'timed-out-quarantine-clear-review-manifest-count-mismatch');
  assert.equal(result.reviewManifest.reviewFingerprint, result.importedQuarantine.reviewFingerprint); assert.equal(result.clearWithManifest.ok, true); assert.equal(result.clearWithManifest.clearedCount, 2);
  assert.equal(result.recovered.recovered, true); assert.equal(result.recoverySchedule.accepted, true); assert.equal(result.recoveredResult?.ok, true); assert.equal(result.recoveredVerify?.ok, true);
  assert.equal(result.finalSnapshot.executor.timedOutOperationQuarantineCount, 0); assert.equal(result.cleanupAfter, true); assert.equal(result.finalLocks.heldCount, 0); assert.equal(result.finalLocks.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-export', 'storage-lane:timed-out-quarantine-import-rejected', 'storage-lane:timed-out-quarantine-import', 'storage-lane:timed-out-quarantine-clear-rejected', 'storage-lane:timed-out-quarantine-review-created', 'storage-lane:timed-out-quarantine-cleared', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);

  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-review-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that real guarded OPFS/Web Lock timeout quarantine cannot be cleared with a stale/missing review fingerprint or malformed/scope-or-option-overridden review manifest; a review manifest bound to the current quarantine fingerprint gates recovery.', observations: { ...result, harness }, claimsChecked: ['real guarded OPFS writes produce late success/failure quarantine after storage-lane timeout', 'exported quarantine carries a deterministic review fingerprint', 'tampered ledger import fails closed without poisoning fresh lane state', 'missing/stale review fingerprints and malformed/scope-or-option-overridden review manifests are rejected', 'markUnhealthy:false non-empty import forces quarantineLedgerImportBackpressureForced', 'scope-bound review manifest permits explicit recovery and later OPFS write verification'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Fingerprint is deterministic review/scope binding, not cryptographic attestation, tamper-proof storage, or security boundary.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '24000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-review-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser quarantine review binding proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_review_binding_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
