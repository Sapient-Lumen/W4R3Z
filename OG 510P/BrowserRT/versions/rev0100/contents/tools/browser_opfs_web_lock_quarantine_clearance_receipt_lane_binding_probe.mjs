#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-CLEARANCE-RECEIPT-LANE-BINDING-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 3000, intervalMs = 25, label = 'condition' } = {}) => { const start = performance.now(); let last = null; while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last, label }; await sleep(intervalMs); } return { ok: false, elapsedMs: performance.now() - start, last, label }; };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserReceiptLaneBindingProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 17 + (i >>> 2)) & 255; return out; };
    const selfConsistentReceipt = (m, base) => { const draft = { ...base }; draft.receiptFingerprint = m.timedOutOperationQuarantineClearanceReceiptFingerprint(draft); return draft; };
    const registrationProvenance = (adapter, receipt, source = 'adapter-create-clearance-receipt') => ({ schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source, lane: receipt.lane || adapter.lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: adapter.label, store: adapter.storeName, provider: adapter.providerName, refDigest: source === 'block-store-restore-clearance-receipt' ? 'sha256:browser-receipt-lane-binding' : undefined, bytes: source === 'block-store-restore-clearance-receipt' ? 512 : undefined });
    const m = await import('/src/browserrt.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockReceiptLaneBindingProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-receipt-lane-binding-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-receipt-lane-binding-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const scheduler = rt.crossLaneScheduler({ label: '${REVISION}-receipt-lane-binding-browser-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const releaseSuccess = deferred(); const releaseFailure = deferred(); const refs = { success: null, failure: null };
    const delayedStore = {
      name: '${REVISION}-receipt-lane-binding-delayed-guarded-store', provider: 'receipt-lane-binding:' + guard.provider,
      async put(payload, fields = {}) { const put = await guard.put(payload, fields, { timeoutMs: 1000 }); const label = String(fields.label || ''); if (label.includes('success')) { refs.success = put.ref || put; await releaseSuccess.promise; return put; } if (label.includes('failure')) { refs.failure = put.ref || put; await releaseFailure.promise; throw codedError('BRT_BROWSER_RECEIPT_LANE_BINDING_LATE_FAILURE', 'browser receipt-lane-binding late failure after committed guarded OPFS write', { digest: put.digest, bytes: put.bytes }); } return put; },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); }, async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); }, async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); }, async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); }, async estimate() { return await guard.estimate({ timeoutMs: 1000 }); }, async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); }, async waitForSettled(options = {}) { return await guard.waitForSettled(options); }, snapshot() { return { name: this.name, provider: this.provider, guard: guard.snapshot() }; }
    };
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-receipt-lane-binding-browser-producer', store: delayedStore, scheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const successPayload = bytesFromSeed('${REVISION}:receipt-lane-binding-success-payload', ${JSON.stringify(payloadBytes)});
    const failurePayload = bytesFromSeed('${REVISION}:receipt-lane-binding-failure-payload', ${JSON.stringify(payloadBytes)});
    const successDigest = 'sha256:' + await m.digestBytesHex(successPayload);
    const failureDigest = 'sha256:' + await m.digestBytesHex(failurePayload);
    adapter.schedulePut(successPayload, { id: '${REVISION}-receipt-lane-binding-success-timeout', priority: 'user-visible', label: 'receipt-lane-binding-success' });
    adapter.schedulePut(failurePayload, { id: '${REVISION}-receipt-lane-binding-failure-timeout', priority: 'user-visible', label: 'receipt-lane-binding-failure' });
    const dispatchSuccess = scheduler.dispatchNext(); const dispatchFailure = scheduler.dispatchNext();
    const [timeoutSuccess, timeoutFailure] = await Promise.all([adapter.executor.executeDispatched(dispatchSuccess), adapter.executor.executeDispatched(dispatchFailure)]);
    const providerCommittedBeforeRelease = await waitUntil(async () => { const successPresent = await raw.has(successDigest); const failurePresent = await raw.has(failureDigest); const locks = await guard.queryLocks(); return { ok: successPresent && failurePresent && locks.heldCount === 0 && locks.pendingCount === 0, successPresent, failurePresent, locks }; }, { timeoutMs: 3000, intervalMs: 25, label: 'both-provider-writes-committed-before-release' });
    releaseSuccess.resolve('browser-release-receipt-lane-binding-success'); releaseFailure.resolve('browser-release-receipt-lane-binding-failure');
    const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 10 });
    const before = adapter.timedOutOperationQuarantine('storage');
    const staleLedger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-export-before-receipt-lane-binding' });
    const reviewManifest = adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0084-browser-probe', reviewToken: 'browser-receipt-lane-binding-review-token', reason: 'browser-review-before-receipt-lane-binding' });
    const clearResult = adapter.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-for-receipt-lane-binding' });
    const validReceipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0084-browser-probe', label: 'browser-receipt-lane-binding-valid-receipt' });
    const validValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(validReceipt);
    const rowLaneMismatchReceipt = selfConsistentReceipt(m, { ...validReceipt, lane: 'maintenance' });
    const rowLaneMismatchValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(rowLaneMismatchReceipt);
    const wrongScheduler = rt.crossLaneScheduler({ label: '${REVISION}-receipt-lane-binding-browser-wrong-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const wrongAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-receipt-lane-binding-browser-wrong', store: guard, scheduler: wrongScheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const wrongLaneRegister = wrongAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'maintenance', reason: 'browser-direct-register-valid-receipt-wrong-lane' });
    const rowLaneMismatchRegister = wrongAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(rowLaneMismatchReceipt, { lane: 'maintenance', reason: 'browser-direct-register-row-lane-mismatch-receipt' });
    const importAfterWrongLane = wrongAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-import-after-wrong-lane-registration-rejections', markUnhealthy: false });
    const wrongLaneState = wrongScheduler.snapshotLane('storage');
    const wrongLaneQuarantine = wrongAdapter.timedOutOperationQuarantine('storage');
    const validScheduler = rt.crossLaneScheduler({ label: '${REVISION}-receipt-lane-binding-browser-valid-scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const validAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-receipt-lane-binding-browser-valid', store: guard, scheduler: validScheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const validDirectRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-valid-receipt-correct-lane', provenance: registrationProvenance(validAdapter, validReceipt) });
    const replayAfterValid = validAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-stale-ledger-replay-after-valid-lane-bound-register', markUnhealthy: false });
    const laneAfterReplay = validScheduler.snapshotLane('storage');
    const quarantineAfterReplay = validAdapter.timedOutOperationQuarantine('storage');
    const successVerify = await raw.verify(successDigest); const failureVerify = await raw.verify(failureDigest);
    const recoveryPayload = bytesFromSeed('${REVISION}:receipt-lane-binding-recovery-after-valid-register', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'receipt-lane-binding-recovery-after-valid-register' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks(); const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 }); const locksAfterCleanup = await guard.queryLocks(); const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, timeoutSuccess, timeoutFailure, providerCommittedBeforeRelease, settled, before, staleLedger, reviewManifest, clearResult, validReceipt, validValidation, rowLaneMismatchReceipt, rowLaneMismatchValidation, wrongLaneRegister, rowLaneMismatchRegister, importAfterWrongLane, wrongLaneState, wrongLaneQuarantine, validDirectRegister, replayAfterValid, laneAfterReplay, quarantineAfterReplay, successVerify, failureVerify, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-clearance-receipt-lane-binding';
  const lockName = options.lockName || `${REVISION}-quarantine-clearance-receipt-lane-binding-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 8 * 1024);
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 32000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-clearance-receipt-lane-binding.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine clearance receipt lane binding proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-receipt-lane-binding-', stderrTerms: ['opfs', 'lock', 'quarantine', 'receipt', 'lane'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.timeoutSuccess.ok, false); assert.equal(result.timeoutFailure.ok, false); assert.equal(result.timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(result.timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.providerCommittedBeforeRelease.ok, true); assert.equal(result.settled.ok, true); assert.equal(result.before.successfulTimedOutOperationCount, 1); assert.equal(result.before.failedTimedOutOperationCount, 1);
  assert.equal(result.clearResult.ok, true); assert.equal(result.validValidation.ok, true);
  assert.equal(result.rowLaneMismatchValidation.ok, false); assert.ok(result.rowLaneMismatchValidation.errors.some((message) => String(message).includes('cleared row lane storage must match receipt lane maintenance')));
  assert.equal(result.wrongLaneRegister.ok, false); assert.equal(result.wrongLaneRegister.disposition, 'rejected-clearance-receipt-lane-binding');
  assert.equal(result.rowLaneMismatchRegister.ok, false); assert.equal(result.rowLaneMismatchRegister.disposition, 'rejected-clearance-receipt-integrity');
  assert.equal(result.importAfterWrongLane.ok, true); assert.equal(result.importAfterWrongLane.markUnhealthyForced, true); assert.equal(result.wrongLaneState.healthy, false); assert.equal(result.wrongLaneQuarantine.totalCount, 2);
  assert.equal(result.validDirectRegister.ok, true); assert.equal(result.validDirectRegister.lane, 'storage');
  assert.equal(result.replayAfterValid.ok, false); assert.equal(result.replayAfterValid.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(result.laneAfterReplay.healthy, true); assert.equal(result.quarantineAfterReplay.totalCount, 0);
  assert.equal(result.successVerify.ok, true); assert.equal(result.failureVerify.ok, true); assert.equal(result.recoveryVerify.ok, true); assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-clearance-receipt-rejected', 'storage-lane:timed-out-quarantine-clearance-receipt-registered', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that timeout-quarantine clearance receipt direct registration is bound to the receipt lane and cleared row lanes over real guarded OPFS/Web Locks.', observations: { ...result, harness }, claimsChecked: ['real guarded OPFS timeout-quarantine outcomes can be cleared with a bound review manifest', 'clearance receipts reject row-lane mismatch', 'direct receipt registration cannot override a valid receipt into another lane', 'rejected wrong-lane registration leaves stale quarantine import active/backpressured', 'valid lane-bound registration rejects stale replay without poisoning lane health', 'later guarded OPFS write verifies'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Receipt lane binding and fingerprinting are deterministic integrity checks, not cryptographic attestation, tamper-proof storage, or security boundary.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '32000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-receipt-lane-binding-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser receipt lane-binding proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_clearance_receipt_lane_binding_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
