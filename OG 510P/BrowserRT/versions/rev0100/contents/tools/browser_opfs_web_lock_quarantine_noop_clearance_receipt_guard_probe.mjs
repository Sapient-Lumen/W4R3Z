#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-NOOP-CLEARANCE-RECEIPT-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const m = await import('/src/browserrt.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-noop-clearance-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-noop-clearance-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const scheduler = rt.crossLaneScheduler({ label: '${REVISION}-noop-clearance-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-noop-clearance-adapter', store: guard, scheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const importedLedger = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', reason: 'browser-imported-quarantine-for-noop-clearance-receipt-guard', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([Object.freeze({ opId: 'browser-noop-guard-success-row', kind: 'put', lane: 'storage', timeoutMs: 100, timedOutAtMs: 1000, settledAtMs: 1100, result: Object.freeze({ disposition: 'stored', digest: 'sha256:browser-noop-guard-success' }) })]), failedTimedOutOperations: Object.freeze([Object.freeze({ opId: 'browser-noop-guard-failure-row', kind: 'put', lane: 'storage', timeoutMs: 100, timedOutAtMs: 2000, settledAtMs: 2100, error: Object.freeze({ name: 'BrowserSyntheticLateFailure', code: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE', message: 'browser synthetic late failure row' }) })]) });
    const importResult = adapter.importTimedOutOperationQuarantine(importedLedger, { lane: 'storage', reason: 'browser-import-noop-clearance-receipt-guard', markUnhealthy: false });
    const importedQuarantine = adapter.timedOutOperationQuarantine('storage');
    const laneAfterImport = scheduler.snapshotLane('storage');
    const staleLedger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-export-before-noop-clear-attempt' });
    const missingScopeReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', opIds: ['browser-definitely-missing-op-id'], reviewer: 'rev0080-browser-proof', reviewToken: 'rev0080-browser-noop-clear-token', reason: 'browser-review-with-nonmatching-scope' });
    const noopClear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: missingScopeReview, requireReviewFingerprint: true, reason: 'browser-attempt-noop-clearance-receipt-guard' });
    const quarantineAfterNoop = adapter.timedOutOperationQuarantine('storage');
    let zeroReceiptError = null;
    try { m.createTimedOutOperationQuarantineClearanceReceipt({ ok: true, lane: 'storage', reviewToken: 'fake-zero', reviewFingerprint: importedQuarantine.reviewFingerprint, requiredReviewFingerprint: importedQuarantine.reviewFingerprint, clearedCount: 0, successfulClearedCount: 0, failedClearedCount: 0, categories: ['successful','failed'], opIds: ['browser-definitely-missing-op-id'], cleared: { successful: [], failed: [] }, quarantine: importedQuarantine }); }
    catch (error) { zeroReceiptError = { name: error.name, message: error.message }; }
    const zeroReceiptValidation = m.validateTimedOutOperationQuarantineClearanceReceipt({ schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.v1', createdAtMs: Date.now(), lane: 'storage', reviewToken: 'fake-zero', reviewFingerprint: importedQuarantine.reviewFingerprint, requiredReviewFingerprint: importedQuarantine.reviewFingerprint, preClearanceFingerprint: importedQuarantine.reviewFingerprint, postClearanceFingerprint: importedQuarantine.reviewFingerprint, categories: ['successful','failed'], opIds: [], allowLaneWide: true, clearedCount: 0, successfulClearedCount: 0, failedClearedCount: 0, counts: { total: 0, successful: 0, failed: 0 }, cleared: { successful: [], failed: [] }, receiptFingerprint: 'intentionally-wrong' });
    const goodReview = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0080-browser-proof', reviewToken: 'rev0080-browser-good-clear-token', reason: 'browser-review-all-for-noop-clearance-receipt-guard' });
    const goodClear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: goodReview, requireReviewFingerprint: true, reason: 'browser-clear-after-noop-guard' });
    const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(goodClear, { reviewer: 'rev0080-browser-proof', label: 'browser-noop-clearance-receipt-guard-good-receipt' });
    const validation = m.validateTimedOutOperationQuarantineClearanceReceipt(receipt);
    const replay = adapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-stale-replay-after-good-clear', markUnhealthy: false });
    const laneAfterReplay = scheduler.snapshotLane('storage');
    const recovery = adapter.markHealthy('storage', 'browser-noop-clearance-receipt-guard-recovered');
    const recoveryPayload = new TextEncoder().encode('${REVISION}:browser-noop-clearance-receipt-guard-after-recovery');
    const scheduled = adapter.schedulePut(recoveryPayload, { id: 'browser-noop-clearance-receipt-guard-after-recovery', label: 'browser-noop-clearance-receipt-guard-after-recovery', operationTimeoutMs: 1000 });
    const drain = await adapter.drain({ maxSteps: 3 });
    const writeResult = drain.results.find((row) => row.opId === 'browser-noop-clearance-receipt-guard-after-recovery') || null;
    const verify = writeResult?.result?.ref ? await raw.verify(writeResult.result.ref) : null;
    const locksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const finalLocks = await guard.queryLocks();
    const finalSnapshot = adapter.snapshot();
    const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, importResult, importedQuarantine, laneAfterImport, staleLedger, missingScopeReview, noopClear, quarantineAfterNoop, zeroReceiptError, zeroReceiptValidation, goodReview, goodClear, receipt, validation, replay, laneAfterReplay, recovery, scheduled, drain, writeResult, verify, locksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-noop-clearance-receipt-guard';
  const lockName = options.lockName || `${REVISION}-quarantine-noop-clearance-receipt-guard-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 24000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine no-op clearance receipt guard proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-opfs-web-lock-quarantine-noop-clearance-receipt-guard-', stderrTerms: ['opfs', 'lock', 'quarantine', 'clearance'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.importResult.ok, true); assert.equal(result.importResult.markUnhealthyForced, true); assert.equal(result.importedQuarantine.totalCount, 2); assert.equal(result.laneAfterImport.healthy, false);
  assert.equal(result.noopClear.ok, false); assert.equal(result.noopClear.code, 'timed-out-quarantine-clear-noop'); assert.equal(result.noopClear.disposition, 'rejected-noop-clear'); assert.equal(result.quarantineAfterNoop.totalCount, 2);
  assert.match(result.zeroReceiptError?.message || '', /at least one cleared/); assert.equal(result.zeroReceiptValidation.ok, false); assert.ok(result.zeroReceiptValidation.errors.some((x) => x.includes('at least one')));
  assert.equal(result.goodClear.ok, true); assert.equal(result.goodClear.clearedCount, 2); assert.equal(result.validation.ok, true); assert.equal(result.replay.ok, false); assert.equal(result.replay.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(result.laneAfterReplay.healthy, false);
  assert.equal(result.recovery.healthy, true); assert.equal(result.scheduled.accepted, true); assert.equal(result.writeResult?.ok, true); assert.equal(result.verify?.ok, true); assert.equal(result.cleanupAfter, true); assert.equal(result.finalLocks.heldCount, 0); assert.equal(result.finalLocks.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-clear-rejected', 'block-store-lane:quarantine-clearance-receipt-created', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that real guarded OPFS/Web Lock storage lanes reject reviewed zero-row timeout-quarantine clears before a bogus clearance receipt can be minted, while valid clearing/recovery remains functional.', observations: { ...result, harness }, claimsChecked: ['non-empty imported timeout quarantine forces lane backpressure', 'reviewed zero-row clear rejects as timed-out-quarantine-clear-noop', 'zero-row clearance receipt creation and validation reject fail-closed', 'valid reviewed clear still creates a receipt that rejects stale ledger replay', 'later guarded OPFS write verifies after explicit recovery'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Receipt fingerprint is deterministic review binding, not cryptographic attestation, tamper-proof storage, or security boundary.', 'No provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '24000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-noop-clearance-receipt-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser no-op clearance receipt guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_noop_clearance_receipt_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
