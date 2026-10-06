#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-status-transition-import-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-STATUS-TRANSITION-IMPORT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) { return `(async () => {
  const m = await import(new URL('/src/browserrt.mjs', location.href).href);
  const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', statusTransitionImportProof: true });
  const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-status-transition-raw-store', prefix: ${JSON.stringify(prefix)} });
  await raw.open(); await raw.cleanupForTest();
  const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-status-transition-guard', lockTimeoutMs: 1000 });
  const scheduler = m.createCrossLaneScheduler({ label: '${REVISION}-status-transition-browser-scheduler', lanes: [{ id:'storage', rank:70, capacity:1, quantum:4096, maxQueuedCost:8192 }, { id:'maintenance', rank:10, capacity:1, quantum:64, maxQueuedCost:128 }] });
  const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-status-transition-browser-adapter', store: guard, scheduler, lane:'storage', defaultOperationTimeoutMs:1000 });
  const withFingerprint = (ledger) => { const fp = m.timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint:fp, reviewFingerprint:fp }); };
  const opId = 'browser-status-transition-visible-put';
  const epoch = '${REVISION}:browser-status-transition-epoch';
  const operationReplayKey = 'operation:storage:put:' + epoch + ':' + opId;
  const now = Date.now();
  const rowFor = (status, offset) => {
    const base = { opId, kind:'put', lane:'storage', operationEpoch:epoch, operationReplayKey, timeoutMs:35, timedOutAtMs:now+offset };
    if (status === 'successful') return Object.freeze({ ...base, settledAtMs:now+offset+1, result:{ digest:'sha256:${REVISION}:browser-status-transition-success', bytes:64, disposition:'browser-status-transition-late-success' } });
    if (status === 'failed') return Object.freeze({ ...base, settledAtMs:now+offset+2, error:{ name:'BrowserSyntheticStatusTransitionFailure', message:'late provider status changed to failure', code:'BRT_BROWSER_STATUS_TRANSITION_FAILURE' } });
    return Object.freeze(base);
  };
  const ledgerFor = (status, row) => {
    const buckets = { unsettled:[], successful:[], failed:[] };
    buckets[status].push(row);
    return withFingerprint({ schema:'brt.storageLane.timedOutOperationQuarantine.v1', lane:'storage', exportedAtMs:Date.now(), label:'${REVISION}-browser-status-transition-' + status + '-ledger', reason:'browser synthetic status transition import ledger: ' + status, counts:{ total:1, unsettled:buckets.unsettled.length, successful:buckets.successful.length, failed:buckets.failed.length }, unsettledTimedOutOperations:buckets.unsettled, successfulTimedOutOperations:buckets.successful, failedTimedOutOperations:buckets.failed });
  };
  const successLedger = ledgerFor('successful', rowFor('successful', 1));
  const failedLedger = ledgerFor('failed', rowFor('failed', 3));
  const unsettledLedger = ledgerFor('unsettled', rowFor('unsettled', 5));

  const importSuccess = adapter.importTimedOutOperationQuarantine(successLedger, { lane:'storage', reason:'browser-import-success-status-transition-row', markUnhealthy:false });
  const quarantineAfterSuccess = adapter.timedOutOperationQuarantine('storage');
  const importFailed = adapter.importTimedOutOperationQuarantine(failedLedger, { lane:'storage', reason:'browser-import-failed-status-transition-row', markUnhealthy:false });
  const quarantineAfterFailed = adapter.timedOutOperationQuarantine('storage');
  const importUnsettled = adapter.importTimedOutOperationQuarantine(unsettledLedger, { lane:'storage', reason:'browser-import-unsettled-status-transition-row', markUnhealthy:false });
  const quarantineAfterUnsettled = adapter.timedOutOperationQuarantine('storage');
  const importSuccessAgain = adapter.importTimedOutOperationQuarantine(successLedger, { lane:'storage', reason:'browser-import-success-status-transition-row-again', markUnhealthy:false });
  const quarantineAfterSuccessAgain = adapter.timedOutOperationQuarantine('storage');

  const review = adapter.createTimedOutOperationQuarantineReview({ lane:'storage', category:'successful', operationReplayKey, reviewer:'rev0090-browser-probe', reviewToken:'browser-status-transition-import-review', reason:'browser-review-transitioned-status-row' });
  const clear = adapter.clearTimedOutOperationQuarantine({ reviewManifest:review, requireReviewFingerprint:true, reason:'browser-clear-transitioned-status-row' });
  const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clear, { reviewer:'rev0090-browser-probe', label:'browser-status-transition-receipt' });
  const receiptValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(receipt);
  const fresh = rt.blockStoreLaneAdapter({ label:'${REVISION}-status-transition-browser-fresh', store: guard, scheduler: m.createCrossLaneScheduler({ label:'${REVISION}-status-transition-browser-fresh-scheduler', lanes:[{ id:'storage', rank:70, capacity:1, quantum:4096, maxQueuedCost:8192 }, { id:'maintenance', rank:10, capacity:1, quantum:64, maxQueuedCost:128 }] }), lane:'storage', defaultOperationTimeoutMs:1000 });
  const provenance = { schema:'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source:'adapter-create-clearance-receipt', lane:'storage', receiptFingerprint:receipt.receiptFingerprint, preClearanceFingerprint:receipt.preClearanceFingerprint, reviewFingerprint:receipt.reviewFingerprint, adapterLabel:fresh.label, store:fresh.storeName, provider:fresh.providerName };
  const register = fresh.executor.registerTimedOutOperationQuarantineClearanceReceipt(receipt, { lane:'storage', reason:'browser-register-status-transition-receipt', provenance });
  const staleReplay = fresh.importTimedOutOperationQuarantine(successLedger, { lane:'storage', reason:'browser-stale-replay-after-status-transition-clear', markUnhealthy:false });
  const recovery = adapter.markHealthy('storage', 'browser-recovery-after-status-transition-clear');
  const put = await guard.put(new TextEncoder().encode('${REVISION}:browser-status-transition-recovery'), { label:'browser-status-transition-recovery-put' }, { timeoutMs:1000 });
  const verify = await raw.verify(put.ref || put);
  const locksBeforeCleanup = await guard.queryLocks();
  const cleanup = await guard.cleanupForTest({ timeoutMs:1000 });
  const locksAfterCleanup = await guard.queryLocks();
  const trace = rt.close();
  return JSON.stringify({ project:'BrowserRT', revision:m.REVISION, version:m.VERSION, taskId:'${TASK_ID}', page:{ location:location.href, crossOriginIsolated, isSecureContext, origin:location.origin }, capabilities:{ ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, importSuccess, quarantineAfterSuccess, importFailed, quarantineAfterFailed, importUnsettled, quarantineAfterUnsettled, importSuccessAgain, quarantineAfterSuccessAgain, review, clear, receipt, receiptValidation, register, staleReplay, recovery, put, verify, locksBeforeCleanup, cleanup, locksAfterCleanup, traceKinds: trace.map((row)=>row.kind) });
})()`; }

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-status-transition-import-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-status-transition-import';
  const lockName = options.lockName || `${REVISION}-status-transition-import-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 30000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath:'/browser-opfs-web-lock-quarantine-status-transition-import.html', pageTitle:'BrowserRT OPFS Web Lock quarantine status transition import proof', allowedPrefixes:['src/'], profilePrefix:'browserrt-status-transition-import-', stderrTerms:['opfs','lock','quarantine','status-transition'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true);
  assert.equal(result.capabilities.webLocks, true);
  assert.equal(result.importSuccess.ok, true);
  assert.equal(result.quarantineAfterSuccess.totalCount, 1);
  assert.equal(result.quarantineAfterSuccess.successfulTimedOutOperationCount, 1);
  assert.equal(result.importFailed.statusTransitionReplacementCount, 1);
  assert.equal(result.quarantineAfterFailed.totalCount, 1);
  assert.equal(result.quarantineAfterFailed.successfulTimedOutOperationCount, 0);
  assert.equal(result.quarantineAfterFailed.failedTimedOutOperationCount, 1);
  assert.equal(result.importUnsettled.statusTransitionReplacementCount, 1);
  assert.equal(result.quarantineAfterUnsettled.totalCount, 1);
  assert.equal(result.quarantineAfterUnsettled.unsettledTimedOutOperationCount, 1);
  assert.equal(result.importSuccessAgain.statusTransitionReplacementCount, 1);
  assert.equal(result.quarantineAfterSuccessAgain.totalCount, 1);
  assert.equal(result.quarantineAfterSuccessAgain.successfulTimedOutOperationCount, 1);
  assert.equal(result.receiptValidation.ok, true);
  assert.equal(result.register.ok, true);
  assert.equal(result.staleReplay.ok, false);
  assert.equal(result.staleReplay.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(result.verify.ok, true);
  assert.equal(result.locksAfterCleanup.held?.length || 0, 0);
  assert.equal(result.locksAfterCleanup.pending?.length || 0, 0);
  assert.ok(result.traceKinds.includes('storage-lane:timed-out-quarantine-import-status-transition-replaced'));
  assert.equal(result.profileReap.afterKillCount, 0);
  return { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-quarantine-status-transition-import`, task_id:TASK_ID, status:'passed', generatedAt:new Date().toISOString(), durationMs:Math.round(performance.now()-started), observations:result, harness, claimsChecked:['same operationReplayKey status import replaces old status bucket row in managed Chromium','successful -> failed -> unsettled -> successful transitions leave one quarantine row','clearance receipt rejects stale replay after transition','later guarded OPFS write verifies and Web Locks drain'], nonClaims:['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.','Synthetic quarantine rows exercise status-transition import policy while OPFS/Web Locks verify the provider path.','No provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '30000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive:true }); await writeFile(out, JSON.stringify(report,null,2)+'\n'); console.log(out); } else console.log(JSON.stringify(report,null,2)); }
catch (error) { const report = { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-quarantine-status-transition-import`, task_id:TASK_ID, status:'failed', generatedAt:new Date().toISOString(), error:{ name:error?.name||'Error', message:error?.message||String(error), stack:error?.stack }, nonClaims:['Failed browser status-transition import proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive:true }); await writeFile(out, JSON.stringify(report,null,2)+'\n'); console.error(out); } console.error(error?.stack || error); process.exitCode = 1; }
