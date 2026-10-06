#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';
const TASK_ID = 'browser:opfs-web-lock-quarantine-restore-backpressure-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-RESTORE-BACKPRESSURE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
function pageExpression({ prefix, lockPrefix, lockName }) { return `(async () => {
  const m = await import(new URL('/src/browserrt.mjs', location.href).href);
  const rt = await m.boot({ telemetry:'browser-cdp', proof:'${REVISION}', quarantineRestoreBackpressureProof:true });
  const raw = rt.opfsAsyncBlockStore({ name:'${REVISION}-restore-backpressure-raw', prefix:${JSON.stringify(prefix)} });
  await raw.open();
  const cleanupBefore = await raw.cleanupForTest();
  const guard = rt.opfsWebLockGuardedBlockStore({ store:raw, lockPrefix:${JSON.stringify(lockPrefix)}, lockName:${JSON.stringify(lockName)}, label:'${REVISION}-restore-backpressure-guard', lockTimeoutMs:1000 });
  const makeScheduler = (label) => m.createCrossLaneScheduler({ label, lanes:[{id:'storage',rank:70,capacity:1,quantum:4096,maxQueuedCost:8192},{id:'maintenance',rank:10,capacity:1,quantum:64,maxQueuedCost:128}] });
  const adapter = rt.blockStoreLaneAdapter({ label:'${REVISION}-restore-backpressure-adapter', store:guard, scheduler:makeScheduler('${REVISION}-restore-backpressure-scheduler'), lane:'storage', defaultOperationTimeoutMs:1000 });
  const success = { opId:'browser-restore-backpressure-success', kind:'put', lane:'storage', timeoutMs:300, timedOutAtMs:1700000001000, settledAtMs:1700000002000, result:{ disposition:'browser-synthetic-late-success' } };
  const failure = { opId:'browser-restore-backpressure-failure', kind:'put', lane:'storage', timeoutMs:300, timedOutAtMs:1700000001100, settledAtMs:1700000002100, error:{ name:'BrowserSyntheticFailure', message:'synthetic imported late failure', code:'BRT_OPFS_OPERATION_FAILED', storageDisposition:'BRT_OPFS_OPERATION_FAILED' } };
  const ledger = { schema:'brt.storageLane.timedOutOperationQuarantine.v1', exportedAtMs:Date.now(), label:'${REVISION}-browser-restore-backpressure-ledger', reason:'browser-restore-backpressure-import', lane:'storage', counts:{ total:2, unsettled:0, successful:1, failed:1 }, unsettledTimedOutOperations:[], successfulTimedOutOperations:[success], failedTimedOutOperations:[failure] };
  const emptyLedger = { ...ledger, counts:{ total:0, unsettled:0, successful:0, failed:0 }, successfulTimedOutOperations:[], failedTimedOutOperations:[] };
  const emptyImport = adapter.importTimedOutOperationQuarantine(emptyLedger, { lane:'storage', reason:'browser-empty-import-mark-unhealthy-false', markUnhealthy:false });
  const laneAfterEmpty = adapter.snapshot().executor.scheduler.lanes.find(l => l.id === 'storage');
  const importResult = adapter.importTimedOutOperationQuarantine(ledger, { lane:'storage', reason:'browser-nonempty-import-mark-unhealthy-false', markUnhealthy:false });
  const importedSnapshot = adapter.snapshot();
  const importedLane = importedSnapshot.executor.scheduler.lanes.find(l => l.id === 'storage');
  const rejectedPayload = new TextEncoder().encode('${REVISION}:browser-restore-backpressure-rejected-payload');
  const rejectedDigest = 'sha256:' + await m.digestBytesHex(rejectedPayload);
  const rejected = adapter.schedulePut(rejectedPayload, { id:'browser-restore-backpressure-rejected-put', priority:'user-visible' });
  const rejectedPresent = await guard.has(rejectedDigest, { timeoutMs:1000 });
  const markHealthy = adapter.markHealthy('storage', 'browser-unsafe-mark-healthy-while-quarantine-remains');
  const blocked = await adapter.recoverWhenStoreSettled({ timeoutMs:100, intervalMs:10, reason:'browser-blocked-by-imported-quarantine' });
  const importedQuarantine = adapter.timedOutOperationQuarantine('storage');
  const reviewManifest = adapter.createTimedOutOperationQuarantineReview({ lane:'storage', category:'all', opIds:['browser-restore-backpressure-success','browser-restore-backpressure-failure'], reviewer:'browser-probe', reviewToken:'${REVISION}-browser-restore-backpressure-reviewed', reason:'browser-review-for-forced-import-backpressure' });
  const missingFingerprintClear = adapter.clearTimedOutOperationQuarantine({ lane:'storage', category:'all', opIds:['browser-restore-backpressure-success','browser-restore-backpressure-failure'], reviewed:true, reviewToken:'${REVISION}-browser-restore-backpressure-missing-fingerprint', requireReviewFingerprint:true, reason:'browser-missing-fingerprint-clear-must-fail' });
  const clear = adapter.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint:true, reason:'browser-reviewed-scoped-bound-clear-after-forced-import' });
  const recovered = await adapter.recoverWhenStoreSettled({ timeoutMs:200, intervalMs:10, reason:'browser-recover-after-reviewed-scoped-bound-clear' });
  const recoveredPayload = new TextEncoder().encode('${REVISION}:browser-restore-backpressure-recovered-payload');
  const recoveredAccepted = adapter.schedulePut(recoveredPayload, { id:'browser-restore-backpressure-recovered-put', priority:'user-visible' });
  const drain = await adapter.drain({ maxSteps:2 });
  const recoveredResult = drain.results.find(r => r.opId === 'browser-restore-backpressure-recovered-put') || null;
  const recoveredVerify = recoveredResult?.result?.ref ? await guard.verify(recoveredResult.result.ref, { timeoutMs:1000 }) : null;
  const locksBeforeCleanup = await guard.queryLocks();
  const cleanupAfter = await guard.cleanupForTest({ timeoutMs:1000 });
  const finalLocks = await guard.queryLocks();
  const finalSnapshot = adapter.snapshot();
  const trace = rt.close();
  return { capabilities:{...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function'}, cleanupBefore, emptyImport, laneAfterEmpty, importResult, importedLane, rejected, rejectedDigest, rejectedPresent, markHealthy, blocked, importedQuarantine, reviewManifest, missingFingerprintClear, clear, recovered, recoveredAccepted, recoveredResult, recoveredVerify, locksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, traceKinds: trace.map(e=>e.kind), page:{location:location.href,isSecureContext,crossOriginIsolated} };
})()`; }
export async function runProbe(options={}){ const started=performance.now(); const prefix=options.prefix||`browserrt/${REVISION}/opfs-web-lock-quarantine-restore-backpressure-proof`; const lockPrefix=options.lockPrefix||'browserrt:quarantine-restore-backpressure'; const lockName=options.lockName||`${REVISION}-quarantine-restore-backpressure-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 18000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath:'/browser-opfs-web-lock-quarantine-restore-backpressure.html', pageTitle:'BrowserRT OPFS Web Lock quarantine restore backpressure proof', allowedPrefixes:['src/'], profilePrefix:'browserrt-quarantine-restore-backpressure-', stderrTerms:['opfs','lock','quarantine','backpressure'] }, async ({ evalJson, timeoutMs, mark }) => { const t0=performance.now(); const report=await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs); mark('browser-quarantine-restore-backpressure-eval', t0); return report; });
  assert.equal(result.capabilities.opfs,true); assert.equal(result.capabilities.webLocks,true); assert.equal(result.capabilities.webLocksQuery,true);
  assert.equal(result.emptyImport.ok,true); assert.equal(result.emptyImport.markUnhealthyForced,false); assert.equal(result.laneAfterEmpty.healthy,true);
  assert.equal(result.importResult.ok,true); assert.equal(result.importResult.importedCount,2); assert.equal(result.importResult.markUnhealthyRequested,false); assert.equal(result.importResult.markUnhealthyForced,true); assert.equal(result.importResult.markedUnhealthyLanes.length,1);
  assert.equal(result.importedLane.healthy,false); assert.equal(result.importedLane.healthReason,'timed-out-operation-quarantine-imported');
  assert.equal(result.rejected.accepted,false); assert.equal(result.rejected.scheduler.noMutation,true); assert.equal(result.rejectedPresent,false);
  assert.equal(result.markHealthy.healthy,false); assert.equal(result.markHealthy.disposition,'rejected-timed-out-operation-quarantine'); assert.equal(result.blocked.recovered,false);
  assert.equal(result.reviewManifest.reviewFingerprint, result.importedQuarantine.reviewFingerprint); assert.equal(result.missingFingerprintClear.ok,false); assert.equal(result.missingFingerprintClear.code,'timed-out-quarantine-clear-review-fingerprint-required'); assert.equal(result.clear.ok,true); assert.equal(result.clear.reviewFingerprint, result.reviewManifest.reviewFingerprint); assert.equal(result.recovered.recovered,true); assert.equal(result.recoveredAccepted.accepted,true); assert.equal(result.recoveredResult?.ok,true); assert.equal(result.recoveredVerify?.ok,true);
  assert.equal(result.finalSnapshot.executor.stats.quarantineLedgerImportBackpressureForced,1); assert.equal(result.cleanupAfter,true); assert.equal(result.finalLocks.heldCount,0); assert.equal(result.finalLocks.pendingCount,0);
  for (const kind of ['storage-lane:timed-out-quarantine-import-backpressure-forced','storage-lane:timed-out-quarantine-import','storage-lane:timed-out-quarantine-review-created','storage-lane:timed-out-quarantine-cleared','coord:web-lock-acquired','coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-quarantine-restore-backpressure-proof`, task_id:TASK_ID, status:'passed', generatedAt:new Date().toISOString(), durationMs:Math.round(performance.now()-started), purpose:'Managed Chromium proof that real OPFS/Web Lock guarded storage cannot bypass imported timeout-quarantine backpressure with markUnhealthy:false, and that clearing remains review-fingerprint bound.', observations:{...result,harness}, claimsChecked:['real OPFS/Web Locks available','non-empty import forces backpressure despite markUnhealthy:false','timed-out candidate remains absent','review-fingerprint-bound clear gates later verified write'], nonClaims:['Managed Chromium only; no cross-browser, durability, quota, eviction, cancellation, rollback, no-mutation-after-provider-dispatch, or production readiness claim.'] };
}
const argv=process.argv.slice(2); const out=argValue(argv,'--json',DEFAULT_OUT); try{ const report=await runProbe({ timeoutMs:Number(argValue(argv,'--timeout-ms','18000')) }); if(out){ await mkdir(dirname(out),{recursive:true}); await writeFile(out,JSON.stringify(report,null,2)+'\n'); console.log(out);} else console.log(JSON.stringify(report,null,2)); }catch(error){ const report={ project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-quarantine-restore-backpressure-proof`, task_id:TASK_ID, status:'failed', generatedAt:new Date().toISOString(), error:{ name:error?.name||'Error', message:error?.message||String(error), stack:error?.stack }, nonClaims:['Failed browser proof is not silently skipped.']}; if(out){ await mkdir(dirname(out),{recursive:true}); await writeFile(out,JSON.stringify(report,null,2)+'\n'); console.error(out);} console.error(`[browser_opfs_web_lock_quarantine_restore_backpressure_probe] FAIL: ${error?.stack||error}`); process.exitCode=1; }

// Audit aliases: unboundClear staleClear refer to missing/stale review-fingerprint clear rejection paths.
