#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-unsettled-orphan-review-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-UNSETTLED-ORPHAN-REVIEW-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName }) { return `(async () => {
  const m = await import(new URL('/src/browserrt.mjs', location.href).href);
  const rt = await m.boot({ telemetry:'browser-cdp', proof:'${REVISION}', unsettledOrphanReviewProof:true });
  const raw = rt.opfsAsyncBlockStore({ name:'${REVISION}-unsettled-orphan-raw', prefix:${JSON.stringify(prefix)} });
  await raw.open();
  const cleanupBefore = await raw.cleanupForTest();
  const guard = rt.opfsWebLockGuardedBlockStore({ store:raw, lockPrefix:${JSON.stringify(lockPrefix)}, lockName:${JSON.stringify(lockName)}, label:'${REVISION}-unsettled-orphan-guard', lockTimeoutMs:1200 });
  const makeScheduler = (label) => m.createCrossLaneScheduler({ label, lanes:[{id:'storage',rank:70,capacity:1,quantum:4096,maxQueuedCost:8192},{id:'maintenance',rank:10,capacity:1,quantum:64,maxQueuedCost:128}] });
  const stalledStore = {
    name: '${REVISION}-unsettled-orphan-stalled-wrapper',
    provider: 'opfs-web-lock-stalled-wrapper',
    async put(value, fields = {}, options = {}) {
      const result = await guard.put(value, fields, options);
      if (fields.label === 'orphaned-timeout-put') await new Promise(() => {});
      return result;
    },
    get: (...args) => guard.get(...args),
    has: (...args) => guard.has(...args),
    verify: (...args) => guard.verify(...args),
    delete: (...args) => guard.delete(...args),
    estimate: (...args) => guard.estimate(...args),
    cleanupForTest: (...args) => guard.cleanupForTest(...args),
    waitForSettled: (...args) => guard.waitForSettled(...args),
    queryLocks: (...args) => guard.queryLocks(...args),
    snapshot: () => ({ name:'${REVISION}-unsettled-orphan-stalled-wrapper', provider:'opfs-web-lock-stalled-wrapper', guard: guard.snapshot() })
  };
  const source = rt.blockStoreLaneAdapter({ label:'${REVISION}-unsettled-orphan-source-adapter', store:stalledStore, scheduler:makeScheduler('${REVISION}-unsettled-orphan-source-scheduler'), lane:'storage', defaultOperationTimeoutMs:1000 });
  const payload = new TextEncoder().encode('${REVISION}:browser-unsettled-orphan-timeout-payload');
  const digest = 'sha256:' + await m.digestBytesHex(payload);
  const scheduled = source.schedulePut(payload, { id:'browser-unsettled-orphan-put', priority:'user-visible', label:'orphaned-timeout-put', operationTimeoutMs:180 });
  const drain = await source.drain({ maxSteps:1 });
  const timeoutResult = drain.results[0] || null;
  const committedBeforeImport = await guard.has(digest, { timeoutMs:1000 });
  const exported = source.exportTimedOutOperationQuarantine({ lane:'storage', reason:'browser-export-unsettled-orphan-for-handoff' });
  const fresh = rt.blockStoreLaneAdapter({ label:'${REVISION}-unsettled-orphan-fresh-adapter', store:guard, scheduler:makeScheduler('${REVISION}-unsettled-orphan-fresh-scheduler'), lane:'storage', defaultOperationTimeoutMs:1000 });
  const imported = fresh.importTimedOutOperationQuarantine(exported, { lane:'storage', reason:'browser-import-unsettled-orphan-quarantine', markUnhealthy:false });
  const laneAfterImport = fresh.snapshot().executor.scheduler.lanes.find(l => l.id === 'storage');
  const blockedUnsettled = await fresh.recoverWhenStoreSettled({ timeoutMs:120, intervalMs:10, reason:'browser-must-block-imported-unsettled-orphan' });
  const unsafeFinalize = fresh.finalizeUnsettledTimedOutOperations({ lane:'storage', opId:'browser-unsettled-orphan-put', reason:'browser-unsafe-finalize-without-review' });
  const review = fresh.createTimedOutOperationQuarantineReview({ lane:'storage', category:'unsettled', opIds:['browser-unsettled-orphan-put'], reviewer:'browser-probe', reviewToken:'${REVISION}-browser-unsettled-orphan-finalize-review', reason:'browser-review-imported-unsettled-orphan' });
  const staleFinalize = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest:{ ...review, reviewFingerprint:'brt-qfp-v1:0000000000000000', quarantineFingerprint:'brt-qfp-v1:0000000000000000' }, requireReviewFingerprint:true, reason:'browser-stale-review-must-not-finalize' });
  const scopeOverrideClear = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest:review, allowLaneWide:true, requireReviewFingerprint:true, reason:'browser-reject-unsettled-orphan-review-scope-override' });
  const tokenOverrideClear = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest:review, reviewToken:'browser-copied-token', requireReviewFingerprint:true, reason:'browser-reject-unsettled-orphan-review-token-override' });
  const fingerprintOverrideClear = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest:review, reviewFingerprint:review.reviewFingerprint, requireReviewFingerprint:true, reason:'browser-reject-unsettled-orphan-review-fingerprint-override' });
  const staleCountManifest = { ...review, counts:{ ...review.counts, total: review.counts.total + 1 } };
  const countMismatchClear = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest:staleCountManifest, requireReviewFingerprint:true, reason:'browser-reject-unsettled-orphan-review-count-mismatch' });
  const finalized = fresh.finalizeUnsettledTimedOutOperations({ reviewManifest:review, requireReviewFingerprint:true, reason:'browser-reviewed-finalize-imported-unsettled-orphan' });
  const blockedLateFailure = await fresh.recoverWhenStoreSettled({ timeoutMs:120, intervalMs:10, reason:'browser-must-block-finalized-orphan-late-failure' });
  const oldReviewClear = fresh.clearTimedOutOperationQuarantine({ lane:'storage', category:'failed', opIds:['browser-unsettled-orphan-put'], reviewed:true, reviewToken:review.reviewToken, reviewFingerprint:review.reviewFingerprint, requireReviewFingerprint:true, reason:'browser-old-unsettled-review-must-not-clear-finalized-failure' });
  const failureReview = fresh.createTimedOutOperationQuarantineReview({ lane:'storage', category:'failed', opIds:['browser-unsettled-orphan-put'], reviewer:'browser-probe', reviewToken:'${REVISION}-browser-unsettled-orphan-failure-clear-review', reason:'browser-review-finalized-orphan-failure' });
  const cleared = fresh.clearTimedOutOperationQuarantine({ reviewManifest:failureReview, requireReviewFingerprint:true, reason:'browser-reviewed-clear-finalized-orphan-failure' });
  const recovered = await fresh.recoverWhenStoreSettled({ timeoutMs:120, intervalMs:10, reason:'browser-recover-after-finalized-orphan-review-clear' });
  const recoveryPayload = new TextEncoder().encode('${REVISION}:browser-unsettled-orphan-recovery-payload');
  const recoveryAccepted = fresh.schedulePut(recoveryPayload, { id:'browser-unsettled-orphan-recovered-put', priority:'user-visible', label:'browser-recovered-put' });
  const recoveryDrain = await fresh.drain({ maxSteps:2 });
  const recoveryResult = recoveryDrain.results.find(r => r.opId === 'browser-unsettled-orphan-recovered-put') || null;
  const recoveryVerify = recoveryResult?.result?.ref ? await guard.verify(recoveryResult.result.ref, { timeoutMs:1000 }) : null;
  const locksBeforeCleanup = await guard.queryLocks();
  const cleanupAfter = await guard.cleanupForTest({ timeoutMs:1200 });
  const finalLocks = await guard.queryLocks();
  const finalSnapshot = fresh.snapshot();
  const trace = rt.close();
  return { capabilities:{...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function'}, cleanupBefore, scheduled, timeoutResult, committedBeforeImport, exported, imported, laneAfterImport, blockedUnsettled, unsafeFinalize, review, staleFinalize, scopeOverrideClear, tokenOverrideClear, fingerprintOverrideClear, countMismatchClear, finalized, blockedLateFailure, oldReviewClear, failureReview, cleared, recovered, recoveryAccepted, recoveryResult, recoveryVerify, locksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, traceKinds: trace.map(e=>e.kind), page:{location:location.href,isSecureContext,crossOriginIsolated} };
})()`; }

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-unsettled-orphan-review-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:unsettled-orphan-review';
  const lockName = options.lockName || `${REVISION}-unsettled-orphan-review-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 20000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-unsettled-orphan-review.html', pageTitle: 'BrowserRT OPFS Web Lock unsettled orphan review proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-unsettled-orphan-review-', stderrTerms: ['opfs', 'lock', 'quarantine', 'orphan'] }, async ({ evalJson, timeoutMs, mark }) => {
    const t0 = performance.now();
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    mark('browser-unsettled-orphan-review-eval', t0);
    return report;
  });
  assert.equal(result.capabilities.opfs, true);
  assert.equal(result.capabilities.webLocks, true);
  assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.cleanupBefore, true);
  assert.equal(result.scheduled.accepted, true);
  assert.equal(result.timeoutResult?.ok, false);
  assert.equal(result.timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.committedBeforeImport, true, 'provider may commit before storage-lane timeout');
  assert.equal(result.exported.counts.unsettled, 1);
  assert.equal(result.imported.ok, true);
  assert.equal(result.imported.markUnhealthyForced, true);
  assert.equal(result.laneAfterImport.healthy, false);
  assert.equal(result.blockedUnsettled.recovered, false);
  assert.equal(result.blockedUnsettled.reason, 'timed-out-operation-still-unsettled');
  assert.equal(result.unsafeFinalize.ok, false);
  assert.equal(result.unsafeFinalize.code, 'timed-out-quarantine-finalize-review-required');
  assert.equal(result.staleFinalize.ok, false);
  assert.equal(result.staleFinalize.code, 'timed-out-quarantine-finalize-review-fingerprint-mismatch');
  assert.equal(result.scopeOverrideClear.ok, false);
  assert.equal(result.scopeOverrideClear.code, 'timed-out-quarantine-finalize-review-manifest-scope-override');
  assert.equal(result.tokenOverrideClear.ok, false);
  assert.equal(result.tokenOverrideClear.code, 'timed-out-quarantine-finalize-review-manifest-scope-override');
  assert.equal(result.fingerprintOverrideClear.ok, false);
  assert.equal(result.fingerprintOverrideClear.code, 'timed-out-quarantine-finalize-review-manifest-scope-override');
  assert.equal(result.countMismatchClear.ok, false);
  assert.equal(result.countMismatchClear.code, 'timed-out-quarantine-finalize-review-manifest-count-mismatch');
  assert.equal(result.finalized.ok, true);
  assert.equal(result.finalized.finalizedCount, 1);
  assert.equal(result.finalized.finalized[0].error.code, 'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED');
  assert.equal(result.blockedLateFailure.recovered, false);
  assert.equal(result.blockedLateFailure.reason, 'timed-out-operation-late-failure');
  assert.equal(result.oldReviewClear.ok, false);
  assert.equal(result.oldReviewClear.code, 'timed-out-quarantine-clear-review-fingerprint-mismatch');
  assert.equal(result.cleared.ok, true);
  assert.equal(result.cleared.failedClearedCount, 1);
  assert.equal(result.recovered.recovered, true);
  assert.equal(result.recoveryAccepted.accepted, true);
  assert.equal(result.recoveryResult?.ok, true);
  assert.equal(result.recoveryVerify?.ok, true);
  assert.equal(result.cleanupAfter, true);
  assert.equal(result.finalLocks.heldCount, 0);
  assert.equal(result.finalLocks.pendingCount, 0);
  for (const kind of ['storage-lane:operation-timeout','storage-lane:operation-timeout-unsettled','storage-lane:timed-out-quarantine-orphans-finalized','storage-lane:timed-out-quarantine-finalize-rejected','coord:web-lock-acquired','coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-unsettled-orphan-review-proof`, task_id:TASK_ID, status:'passed', generatedAt:new Date().toISOString(), durationMs:Math.round(performance.now()-started), purpose:'Managed Chromium proof that imported unsettled guarded OPFS timeout quarantine cannot deadlock recovery forever; it requires review-bound orphan finalization, then a fresh review-bound late-failure clear.', observations:{...result,harness}, claimsChecked:['real OPFS/Web Locks available','provider may commit before operation timeout','imported unsettled timeout quarantine blocks recovery','review-fingerprint-bound orphan finalization converts unsettled timeout to late-failure quarantine',
    'review manifests are authoritative for unsettled-orphan finalization and reject scope/token/fingerprint overrides plus stale counts','fresh review-bound clear gates later verified guarded OPFS write'], nonClaims:['Managed Chromium only; no cross-browser, cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota/eviction, or production readiness claim.'] };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '20000')) });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-unsettled-orphan-review-proof`, task_id:TASK_ID, status:'failed', generatedAt:new Date().toISOString(), error:{ name:error?.name || 'Error', message:error?.message || String(error), stack:error?.stack }, nonClaims:['Failed browser proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_unsettled_orphan_review_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
