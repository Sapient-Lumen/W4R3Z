#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';
import { assertExpectedFingerprintRestoreReport, EXPECTED_FINGERPRINT_RESTORE_CLAIMS, EXPECTED_FINGERPRINT_RESTORE_NON_CLAIMS } from './lib/quarantine_restore_expected_fingerprint_harness.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-RESTORE-EXPECTED-FINGERPRINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) { return `(async () => {
  const m = await import(new URL('/src/browserrt.mjs', location.href).href);
  const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', quarantineRestoreExpectedFingerprintProof: true });
  const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-restore-expected-fingerprint-raw-store', prefix: ${JSON.stringify(prefix)} });
  await raw.open();
  await raw.cleanupForTest();
  const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-restore-expected-fingerprint-guard', lockTimeoutMs: 1000 });
  const mkScheduler = (label) => m.createCrossLaneScheduler({ label, lanes: [{ id:'storage', rank:70, capacity:1, quantum:4096, maxQueuedCost:8192 }, { id:'maintenance', rank:10, capacity:1, quantum:64, maxQueuedCost:128 }] });
  const adapter = (label) => rt.blockStoreLaneAdapter({ label, store: guard, scheduler: mkScheduler(label + ':scheduler'), lane:'storage', defaultOperationTimeoutMs:1000 });
  const withFingerprint = (ledger) => { const fp = m.timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fp, reviewFingerprint: fp }); };
  const row = (label, status) => {
    const now = Date.now();
    const opId = '${REVISION}-browser-' + label + '-' + status;
    const epoch = '${REVISION}:browser:' + label + ':' + status + ':epoch';
    const base = { opId, kind:'put', lane:'storage', operationEpoch:epoch, operationReplayKey:'operation:storage:put:' + epoch + ':' + opId, timeoutMs:50, timedOutAtMs:now, settledAtMs:now + 1 };
    if (status === 'successful') return Object.freeze({ ...base, result:{ digest:'sha256:browser-' + label + '-successful', bytes:64, disposition:'browser-late-success' } });
    return Object.freeze({ ...base, error:{ name:'BrowserSyntheticLateFailure', message:'late failure for ' + label, code:'BRT_BROWSER_SYNTHETIC_LATE_FAILURE' } });
  };
  const ledger = (label) => withFingerprint({ schema:'brt.storageLane.timedOutOperationQuarantine.v1', lane:'storage', exportedAtMs:Date.now(), label:'${REVISION}-browser-' + label + '-ledger', reason:'browser synthetic expected-fingerprint quarantine ledger ' + label, counts:{ total:2, unsettled:0, successful:1, failed:1 }, unsettledTimedOutOperations:[], successfulTimedOutOperations:[row(label, 'successful')], failedTimedOutOperations:[row(label, 'failed')] });
  const receiptFlow = (adapterInstance, sourceLedger, label) => {
    const imported = adapterInstance.importTimedOutOperationQuarantine(sourceLedger, { lane:'storage', reason:label + '-import-before-clear', markUnhealthy:false });
    const review = adapterInstance.createTimedOutOperationQuarantineReview({ lane:'storage', category:'all', allowLaneWide:true, reviewer:'${REVISION}-browser-expected-fingerprint', reviewToken:'${REVISION}-browser-' + label + '-review', reason:label + '-review-all' });
    const clear = adapterInstance.clearTimedOutOperationQuarantine({ reviewManifest:review, requireReviewFingerprint:true, reason:label + '-clear-all' });
    const receipt = adapterInstance.createTimedOutOperationQuarantineClearanceReceipt(clear, { reviewer:'${REVISION}-browser-expected-fingerprint', label:label + '-receipt' });
    return { imported, review, clear, receipt };
  };
  const source = adapter('${REVISION}-restore-expected-fingerprint-browser-source');
  const ledgerA = ledger('restore-expected-a');
  const ledgerB = ledger('restore-expected-b');
  const persistedLedgerA = await source.persistTimedOutOperationQuarantine({ ledger:ledgerA, label:'browser-expected-fingerprint-ledger-a' });
  const persistedLedgerB = await source.persistTimedOutOperationQuarantine({ ledger:ledgerB, label:'browser-expected-fingerprint-ledger-b' });
  const flowA = receiptFlow(source, ledgerA, 'receipt-a');
  const flowB = receiptFlow(source, ledgerB, 'receipt-b');
  const persistedReceiptA = await source.persistTimedOutOperationQuarantineClearanceReceipt(flowA.receipt, { label:'browser-expected-fingerprint-receipt-a' });
  const persistedReceiptB = await source.persistTimedOutOperationQuarantineClearanceReceipt(flowB.receipt, { label:'browser-expected-fingerprint-receipt-b' });
  const ledgerFresh = adapter('${REVISION}-restore-expected-fingerprint-browser-ledger-fresh');
  const blankLedgerRestore = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedgerA.ref, { lane:'storage', reason:'browser-reject-blank-ledger-expected-fingerprint-intent', expectedQuarantineFingerprint:'   ', markUnhealthy:false });
  const wrongLedgerRestore = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedgerB.ref, { lane:'storage', reason:'browser-reject-valid-but-wrong-ledger-fingerprint', expectedQuarantineFingerprint:ledgerA.quarantineFingerprint, markUnhealthy:false });
  const ledgerQuarantineAfterRejected = ledgerFresh.timedOutOperationQuarantine('storage');
  const ledgerLaneAfterRejected = ledgerFresh.scheduler.snapshotLane('storage');
  const rightLedgerRestore = await ledgerFresh.restoreTimedOutOperationQuarantineFromBlockStore(persistedLedgerA.ref, { lane:'storage', reason:'browser-restore-expected-ledger-fingerprint-match', expectedQuarantineFingerprint:ledgerA.quarantineFingerprint, markUnhealthy:false });
  const ledgerQuarantineAfterAccepted = ledgerFresh.timedOutOperationQuarantine('storage');
  const receiptFresh = adapter('${REVISION}-restore-expected-fingerprint-browser-receipt-fresh');
  const blankReceiptRestore = await receiptFresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceiptA.ref, { lane:'storage', reason:'browser-reject-blank-receipt-expected-fingerprint-intent', expectedReceiptFingerprint:' ', expectedPreClearanceFingerprint:flowA.receipt.preClearanceFingerprint });
  const wrongReceiptRestore = await receiptFresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceiptB.ref, { lane:'storage', reason:'browser-reject-valid-but-wrong-receipt-fingerprint', expectedReceiptFingerprint:flowA.receipt.receiptFingerprint, expectedPreClearanceFingerprint:flowA.receipt.preClearanceFingerprint });
  const receiptsAfterWrong = receiptFresh.clearedTimedOutOperationQuarantineClearanceReceipts('storage');
  const importAfterRejectedReceipt = receiptFresh.importTimedOutOperationQuarantine(ledgerB, { lane:'storage', reason:'browser-ledger-b-imports-after-wrong-receipt-rejected', markUnhealthy:false });
  const receiptRestoreAdapter = adapter('${REVISION}-restore-expected-fingerprint-browser-receipt-restore');
  const wrongPreclearanceRestore = await receiptRestoreAdapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceiptA.ref, { lane:'storage', reason:'browser-reject-valid-receipt-wrong-preclearance-fingerprint', expectedReceiptFingerprint:flowA.receipt.receiptFingerprint, expectedPreClearanceFingerprint:flowB.receipt.preClearanceFingerprint });
  const rightReceiptRestore = await receiptRestoreAdapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persistedReceiptA.ref, { lane:'storage', reason:'browser-restore-receipt-expected-fingerprints-match', expectedReceiptFingerprint:flowA.receipt.receiptFingerprint, expectedPreClearanceFingerprint:flowA.receipt.preClearanceFingerprint });
  const staleReplay = receiptRestoreAdapter.importTimedOutOperationQuarantine(ledgerA, { lane:'storage', reason:'browser-stale-replay-after-expected-fingerprint-restore', markUnhealthy:false });
  const recoveryPayload = new TextEncoder().encode('${REVISION}:browser-restore-expected-fingerprint-recovery');
  const recoveryPut = await guard.put(recoveryPayload, { label:'browser-restore-expected-fingerprint-recovery-put' }, { timeoutMs:1000 });
  const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
  const persistedVerifies = { ledgerA: await raw.verify(persistedLedgerA.ref), ledgerB: await raw.verify(persistedLedgerB.ref), receiptA: await raw.verify(persistedReceiptA.ref), receiptB: await raw.verify(persistedReceiptB.ref) };
  const locksBeforeCleanup = await guard.queryLocks();
  const cleanup = await guard.cleanupForTest({ timeoutMs:1000 });
  const locksAfterCleanup = await guard.queryLocks();
  const trace = rt.close();
  return JSON.stringify({ project:'BrowserRT', revision:m.REVISION, version:m.VERSION, taskId:'${TASK_ID}', page:{ location:location.href, crossOriginIsolated, isSecureContext, origin:location.origin }, capabilities:{ ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, ledgerA, ledgerB, persistedLedgerA, persistedLedgerB, flowA, flowB, persistedReceiptA, persistedReceiptB, blankLedgerRestore, wrongLedgerRestore, ledgerQuarantineAfterRejected, ledgerLaneAfterRejected, rightLedgerRestore, ledgerQuarantineAfterAccepted, blankReceiptRestore, wrongReceiptRestore, receiptsAfterWrong, importAfterRejectedReceipt, wrongPreclearanceRestore, rightReceiptRestore, staleReplay, recoveryPut, recoveryVerify, persistedVerifies, locksBeforeCleanup, cleanup, locksAfterCleanup, traceKinds: trace.map((row)=>row.kind), traceHighlights: trace.filter((row)=>String(row.kind).includes('quarantine') || String(row.kind).includes('clearance') || String(row.kind).includes('web-lock')).map((row)=>({ kind:row.kind, code:row.code ?? null, disposition:row.disposition ?? null, reason:row.reason ?? null })) });
})()`; }

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-restore-expected-fingerprint-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-restore-expected-fingerprint';
  const lockName = options.lockName || `${REVISION}-restore-expected-fingerprint-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 32000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath:'/browser-opfs-web-lock-quarantine-restore-expected-fingerprint.html', pageTitle:'BrowserRT OPFS Web Lock quarantine restore expected fingerprint proof', allowedPrefixes:['src/'], profilePrefix:'browserrt-restore-expected-fingerprint-', stderrTerms:['opfs','lock','quarantine','restore','expected','fingerprint'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assertExpectedFingerprintRestoreReport(result, { browser: true });
  return { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-quarantine-restore-expected-fingerprint`, task_id:TASK_ID, status:'passed', generatedAt:new Date().toISOString(), durationMs:Math.round(performance.now()-started), purpose:'Managed Chromium proof that provider-backed timeout-quarantine ledger/clearance-receipt restore can be pinned to intended expected fingerprints before import or replay-guard registration.', observations:{ ...result, harness }, claimsChecked:[...EXPECTED_FINGERPRINT_RESTORE_CLAIMS, 'later guarded OPFS write verifies'], nonClaims:['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Synthetic timeout-quarantine rows are used.', ...EXPECTED_FINGERPRINT_RESTORE_NON_CLAIMS] };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '32000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') });
  if (out) { await mkdir(dirname(out), { recursive:true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-quarantine-restore-expected-fingerprint`, task_id:TASK_ID, status:'failed', generatedAt:new Date().toISOString(), error:{ name:error?.name || 'Error', message:error?.message || String(error), code:error?.code || null, stack:error?.stack }, nonClaims:['Failed browser expected-fingerprint restore proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive:true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_quarantine_restore_expected_fingerprint_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
