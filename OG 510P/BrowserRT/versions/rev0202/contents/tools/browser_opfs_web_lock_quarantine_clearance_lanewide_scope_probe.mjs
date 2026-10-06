#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-clearance-lanewide-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-CLEARANCE-LANEWIDE-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 13 + (i >>> 1)) & 255; return out; };
    const selfConsistentReceipt = (m, base) => { const draft = { ...base }; draft.receiptFingerprint = m.timedOutOperationQuarantineClearanceReceiptFingerprint(draft); return draft; };
    const registrationProvenance = (adapter, receipt) => ({ schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: receipt.lane ?? adapter.lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: adapter.label, store: adapter.storeName, provider: adapter.providerName });
    const makeLedger = (timedOutQuarantineFingerprint, { suffix = 'browser-lanewide-scope', lane = 'storage', epoch = '${REVISION}-browser-lanewide-scope-epoch' } = {}) => { const now = Date.now(); const success = Object.freeze({ opId: '${REVISION}-' + suffix + '-late-success', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-' + suffix + '-late-success', timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: 'sha256:' + suffix + '-success', bytes: 32, disposition: 'browser-synthetic-late-success' } }); const failed = Object.freeze({ opId: '${REVISION}-' + suffix + '-late-failure', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-' + suffix + '-late-failure', timeoutMs: 25, timedOutAtMs: now + 2, settledAtMs: now + 3, error: { name: 'BrowserSyntheticLateFailure', message: 'browser synthetic late failure for lane-wide scope proof', code: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE' } }); const base = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, exportedAtMs: now + 4, label: '${REVISION}-browser-lanewide-scope-ledger', reason: 'browser-synthetic-lanewide-scope-ledger', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failed]) }); const fingerprint = timedOutQuarantineFingerprint(base); return Object.freeze({ ...base, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint }); };
    const m = await import('/src/browserrt.mjs');
    const s = await import('/src/storage-lane-scheduler.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockLaneWideScopeProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-lanewide-scope-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-lanewide-scope-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const staleLedger = makeLedger(s.timedOutQuarantineFingerprint);
    const producerScheduler = rt.crossLaneScheduler({ label: '${REVISION}-lanewide-scope-browser-producer-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const producer = rt.blockStoreLaneAdapter({ label: '${REVISION}-lanewide-scope-browser-producer', store: guard, scheduler: producerScheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const importOriginal = producer.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-import-before-lanewide-scope-clear', markUnhealthy: false });
    const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0085-browser-probe', reviewToken: 'browser-lanewide-scope-review-token', reason: 'browser-review-before-lanewide-scope-clear' });
    const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-for-lanewide-scope-receipt' });
    const validReceipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0085-browser-probe', label: 'browser-lanewide-scope-valid-receipt' });
    const validValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(validReceipt);
    const ambiguousLaneWideReceipt = selfConsistentReceipt(m, { ...validReceipt, lane: null, allowLaneWide: true });
    const ambiguousValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(ambiguousLaneWideReceipt);
    const wrongScheduler = rt.crossLaneScheduler({ label: '${REVISION}-lanewide-scope-browser-ambiguous-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const wrongAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-lanewide-scope-browser-ambiguous', store: guard, scheduler: wrongScheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const ambiguousRegister = wrongAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(ambiguousLaneWideReceipt, { lane: 'maintenance', reason: 'browser-direct-register-lane-ambiguous-lanewide-receipt', provenance: registrationProvenance(wrongAdapter, ambiguousLaneWideReceipt) });
    const importAfterAmbiguousReject = wrongAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-import-after-lane-ambiguous-receipt-rejection', markUnhealthy: false });
    const wrongLaneState = wrongScheduler.snapshotLane('storage');
    const wrongLaneQuarantine = wrongAdapter.timedOutOperationQuarantine('storage');
    const validScheduler = rt.crossLaneScheduler({ label: '${REVISION}-lanewide-scope-browser-valid-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const validAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-lanewide-scope-browser-valid', store: guard, scheduler: validScheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const validRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-valid-lanewide-receipt', provenance: registrationProvenance(validAdapter, validReceipt) });
    const replayAfterValid = validAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-replay-after-valid-lanewide-receipt', markUnhealthy: false });
    const laneAfterReplay = validScheduler.snapshotLane('storage');
    const quarantineAfterReplay = validAdapter.timedOutOperationQuarantine('storage');
    const recoveryPayload = bytesFromSeed('${REVISION}:browser-lanewide-scope-recovery', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'browser-lanewide-scope-recovery-put' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const locksAfterCleanup = await guard.queryLocks();
    const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, staleLedger, importOriginal, reviewManifest, clearResult, validReceipt, validValidation, ambiguousLaneWideReceipt, ambiguousValidation, ambiguousRegister, importAfterAmbiguousReject, wrongLaneState, wrongLaneQuarantine, validRegister, replayAfterValid, laneAfterReplay, quarantineAfterReplay, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-clearance-lanewide-scope-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-clearance-lanewide-scope';
  const lockName = options.lockName || `${REVISION}-quarantine-clearance-lanewide-scope-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 24000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-clearance-lanewide-scope.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine clearance lane-wide scope proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-lanewide-scope-', stderrTerms: ['opfs', 'lock', 'quarantine', 'clearance', 'lanewide'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.importOriginal.ok, true); assert.equal(result.importOriginal.markUnhealthyForced, true);
  assert.equal(result.clearResult.ok, true); assert.equal(result.clearResult.clearedCount, 2); assert.equal(result.clearResult.allowLaneWide, true);
  assert.equal(result.validValidation.ok, true); assert.equal(result.validReceipt.lane, 'storage'); assert.equal(result.validReceipt.allowLaneWide, true);
  assert.equal(result.ambiguousValidation.ok, false); assert.ok(result.ambiguousValidation.errors.some((message) => String(message).includes('lane-wide receipts are lane-scoped')), JSON.stringify(result.ambiguousValidation.errors));
  assert.equal(result.ambiguousRegister.ok, false); assert.equal(result.ambiguousRegister.disposition, 'rejected-clearance-receipt-integrity');
  assert.equal(result.importAfterAmbiguousReject.ok, true); assert.equal(result.importAfterAmbiguousReject.markUnhealthyForced, true); assert.equal(result.wrongLaneState.healthy, false); assert.equal(result.wrongLaneQuarantine.totalCount, 2);
  assert.equal(result.validRegister.ok, true); assert.equal(result.validRegister.lane, 'storage'); assert.equal(result.validRegister.allowLaneWide, true);
  assert.equal(result.replayAfterValid.ok, false); assert.equal(result.replayAfterValid.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(result.laneAfterReplay.healthy, true); assert.equal(result.quarantineAfterReplay.totalCount, 0);
  assert.equal(result.recoveryVerify.ok, true); assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-clearance-receipt-rejected', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'storage-lane:timed-out-quarantine-clearance-receipt-registered', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-lanewide-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that lane-wide timeout-quarantine clearance receipts are lane-scoped, not lane-ambiguous, over real guarded OPFS/Web Locks.', observations: { ...result, harness }, claimsChecked: ['valid lane-wide receipts remain lane-scoped', 'self-consistent lane-ambiguous lane-wide receipts fail validation and direct registration', 'rejected lane-ambiguous receipt registration leaves stale quarantine import active/backpressured', 'valid lane-scoped receipt registration rejects stale replay and a later guarded OPFS write verifies'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Lane-wide receipt scope is deterministic integrity policy, not cryptographic attestation, tamper-proof storage, or access-control security boundary.', 'No provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '24000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-lanewide-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser lane-wide scope proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_clearance_lanewide_scope_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
