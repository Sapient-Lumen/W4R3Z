#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-review-replay-key-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-REVIEW-REPLAY-KEY-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (23 + i * 31 + (i >>> 3)) & 255; return out; };
    const m = await import('/src/browserrt.mjs');
    const s = await import('/src/storage-lane-scheduler.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockReviewReplayKeyScopeProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-review-replay-key-scope-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-review-replay-key-scope-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const scheduler = (label) => rt.crossLaneScheduler({ label, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = (label) => rt.blockStoreLaneAdapter({ label, store: guard, scheduler: scheduler(label + ':scheduler'), trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const withFingerprint = (ledger) => { const fp = s.timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fp, reviewFingerprint: fp }); };
    const row = (epoch, suffix) => { const opId = '${REVISION}-shared-browser-review-scope-op'; const now = Date.now(); return Object.freeze({ opId, kind: 'put', lane: 'storage', operationEpoch: epoch, operationReplayKey: 'operation:storage:put:' + epoch + ':' + opId, timeoutMs: 35, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: 'sha256:' + suffix, bytes: 64, disposition: 'browser-synthetic-late-success' } }); };
    const first = row('${REVISION}:browser-review-scope-epoch-a', 'browser-review-scope-a');
    const second = row('${REVISION}:browser-review-scope-epoch-b', 'browser-review-scope-b');
    const ledger = withFingerprint({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', exportedAtMs: Date.now(), label: '${REVISION}-browser-review-replay-key-scope-ledger', reason: 'browser-merged-ledger-same-visible-opid-for-review-scope', counts: Object.freeze({ total: 2, unsettled: 0, successful: 2, failed: 0 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([first, second]), failedTimedOutOperations: Object.freeze([]) });
    const oneRowLedger = (row, label) => withFingerprint({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', exportedAtMs: Date.now(), label, reason: 'browser-single-row-review-scope-ledger', counts: Object.freeze({ total: 1, unsettled: 0, successful: 1, failed: 0 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([row]), failedTimedOutOperations: Object.freeze([]) });
    const importer = adapter('${REVISION}-browser-review-replay-key-scope-importer');
    const importResult = importer.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'browser-import-review-replay-key-scope-ledger', markUnhealthy: false });
    const ambiguousReview = importer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opIds: [first.opId], reviewer: 'rev0088-browser-probe', reviewToken: 'browser-review-replay-key-scope-ambiguous-opid', reason: 'browser-opid-only-review-should-be-ambiguous' });
    const ambiguousClear = importer.clearTimedOutOperationQuarantine({ reviewManifest: ambiguousReview, requireReviewFingerprint: true, reason: 'browser-opid-only-clear-should-fail' });
    const firstReview = importer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', operationReplayKeys: [first.operationReplayKey], reviewer: 'rev0088-browser-probe', reviewToken: 'browser-review-replay-key-scope-first', reason: 'browser-operation-replay-key-scoped-first-clear' });
    const firstClear = importer.clearTimedOutOperationQuarantine({ reviewManifest: firstReview, requireReviewFingerprint: true, reason: 'browser-clear-first-by-operation-replay-key' });
    const quarantineAfterFirstClear = importer.timedOutOperationQuarantine('storage');
    const blockedRecovery = importer.markHealthy('storage', 'browser-recovery-before-second-clear');
    const firstReceipt = importer.createTimedOutOperationQuarantineClearanceReceipt(firstClear, { reviewer: 'rev0088-browser-probe', label: 'browser-review-replay-key-scope-first-receipt' });
    const firstReceiptValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(firstReceipt);
    const fresh = adapter('${REVISION}-browser-review-replay-key-scope-fresh');
    const provenance = { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: firstReceipt.receiptFingerprint, preClearanceFingerprint: firstReceipt.preClearanceFingerprint, reviewFingerprint: firstReceipt.reviewFingerprint, adapterLabel: fresh.label, store: fresh.storeName, provider: fresh.providerName };
    const register = fresh.executor.registerTimedOutOperationQuarantineClearanceReceipt(firstReceipt, { lane: 'storage', reason: 'browser-register-first-replay-key-scoped-receipt', provenance });
    const firstReplay = fresh.importTimedOutOperationQuarantine(oneRowLedger(first, '${REVISION}-browser-first-row-stale-replay'), { lane: 'storage', reason: 'browser-first-row-stale-replay', markUnhealthy: false });
    const secondStillImportable = fresh.importTimedOutOperationQuarantine(oneRowLedger(second, '${REVISION}-browser-second-row-still-active'), { lane: 'storage', reason: 'browser-second-row-not-cleared-yet', markUnhealthy: false });
    const secondReview = importer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', operationReplayKeys: [second.operationReplayKey], reviewer: 'rev0088-browser-probe', reviewToken: 'browser-review-replay-key-scope-second', reason: 'browser-operation-replay-key-scoped-second-clear' });
    const secondClear = importer.clearTimedOutOperationQuarantine({ reviewManifest: secondReview, requireReviewFingerprint: true, reason: 'browser-clear-second-by-operation-replay-key' });
    const recovery = importer.markHealthy('storage', 'browser-recovery-after-replay-key-scoped-clears');
    const recoveryPayload = bytesFromSeed('${REVISION}:browser-review-replay-key-scope-recovery', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'browser-review-replay-key-scope-recovery-put' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const locksAfterCleanup = await guard.queryLocks();
    const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, ledger, importResult, ambiguousReview, ambiguousClear, firstReview, firstClear, quarantineAfterFirstClear, blockedRecovery, firstReceipt, firstReceiptValidation, register, firstReplay, secondStillImportable, secondReview, secondClear, recovery, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((event) => event.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-review-replay-key-scope-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-review-replay-key-scope';
  const lockName = options.lockName || `${REVISION}-quarantine-review-replay-key-scope-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 30000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-review-replay-key-scope.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine review replay-key scope proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-review-replay-key-scope-', stderrTerms: ['opfs', 'lock', 'quarantine', 'replay-key', 'scope'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.importResult.ok, true); assert.equal(result.importResult.importedCount, 2); assert.equal(result.importResult.markUnhealthyForced, true);
  assert.equal(result.ambiguousClear.ok, false); assert.equal(result.ambiguousClear.code, 'timed-out-quarantine-clear-opid-ambiguous'); assert.equal(result.ambiguousClear.disposition, 'rejected-ambiguous-opid-scope');
  assert.equal(result.firstClear.ok, true); assert.equal(result.firstClear.clearedCount, 1); assert.equal(result.firstClear.cleared.successful[0].operationReplayKey, result.ledger.successfulTimedOutOperations[0].operationReplayKey); assert.deepEqual(result.firstClear.operationReplayKeys, [result.ledger.successfulTimedOutOperations[0].operationReplayKey]);
  assert.equal(result.quarantineAfterFirstClear.totalCount, 1); assert.equal(result.quarantineAfterFirstClear.successfulTimedOutOperations[0].operationReplayKey, result.ledger.successfulTimedOutOperations[1].operationReplayKey);
  assert.equal(result.blockedRecovery.healthy, false); assert.equal(result.blockedRecovery.reason, 'timed-out-operation-quarantine-active');
  assert.equal(result.firstReceiptValidation.ok, true); assert.deepEqual(result.firstReceipt.operationReplayKeys, [result.ledger.successfulTimedOutOperations[0].operationReplayKey]);
  assert.equal(result.register.ok, true); assert.equal(result.firstReplay.ok, false); assert.equal(result.firstReplay.disposition, 'rejected-cleared-quarantine-row-replay'); assert.equal(result.secondStillImportable.ok, true); assert.equal(result.secondStillImportable.importedCount, 1); assert.equal(result.secondStillImportable.markUnhealthyForced, true);
  assert.equal(result.secondClear.ok, true); assert.equal(result.secondClear.clearedCount, 1); assert.equal(result.recovery.healthy, true); assert.equal(result.recoveryVerify.ok, true); assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-import-backpressure-forced', 'storage-lane:timed-out-quarantine-clear-rejected', 'storage-lane:timed-out-quarantine-cleared', 'storage-lane:timed-out-quarantine-import-row-replay-rejected', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-review-replay-key-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that timeout-quarantine review and clearance can scope by operationReplayKey over real guarded OPFS/Web Locks.', observations: { ...result, harness }, claimsChecked: ['same visible opId with multiple operationReplayKeys rejects ambiguous opId-only review clear', 'operationReplayKey-scoped review clears exactly one timeout-quarantine row', 'partial replay-key clearance does not suppress uncleared same-opId rows', 'later guarded OPFS write verifies after all replay-key-scoped quarantine is reviewed and cleared'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Synthetic timeout quarantine rows exercise import/clearance policy while OPFS/Web Locks verify the provider path.', 'Operation replay keys are deterministic review scope metadata, not cryptographic attestation or tamper-proof storage.', 'No provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '30000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-review-replay-key-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser review replay-key scope proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_review_replay_key_scope_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
// rev0088/deep-audit carry-forward anchor: maintenanceReceipts distinct operationReplayKey remain visible while this browser proof verifies replay-key-scoped review over guarded OPFS/Web Locks.
