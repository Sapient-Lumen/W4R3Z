#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile, mkdtemp, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses, startProbeServer } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-CLEARANCE-RECEIPT-PROVENANCE-BINDING-PROBE.json`;
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
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserReceiptRegistrationIntegrityProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 31 + (i >>> 1)) & 255; return out; };
    const makeScheduler = (m, label) => m.createCrossLaneScheduler({ label, lanes: [ { id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const makeSelfConsistentReceipt = (m, base) => { const draft = JSON.parse(JSON.stringify(base)); draft.receiptFingerprint = m.timedOutOperationQuarantineClearanceReceiptFingerprint(draft); return draft; };
    const m = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockQuarantineClearanceReceiptRegistrationIntegrityProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-receipt-provenance-binding-raw-store', prefix: ${JSON.stringify(prefix)} });
    await raw.open();
    const cleanupBefore = await raw.cleanupForTest();
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-receipt-provenance-binding-guard', lockTimeoutMs: 1000 });
    const releaseSuccess = deferred(); const releaseFailure = deferred();
    const delayedStore = {
      name: '${REVISION}-receipt-provenance-binding-delayed-guarded-store', provider: 'receipt-provenance-binding:' + guard.provider,
      async put(payload, fields = {}) { const put = await guard.put(payload, fields, { timeoutMs: 1000 }); const label = String(fields.label || ''); if (label.includes('success')) { await releaseSuccess.promise; return put; } if (label.includes('failure')) { await releaseFailure.promise; throw codedError('BRT_BROWSER_RECEIPT_REGISTRATION_LATE_FAILURE', 'browser receipt provenance binding late failure after committed guarded OPFS write', { digest: put.digest, bytes: put.bytes }); } return put; },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); }, async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); }, async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); }, async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); }, async estimate() { return await guard.estimate({ timeoutMs: 1000 }); }, async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); }, async waitForSettled(options = {}) { return await guard.waitForSettled(options); }, snapshot() { return { name: this.name, provider: this.provider, guard: guard.snapshot() }; }
    };
    const producer = rt.blockStoreLaneAdapter({ label: '${REVISION}-receipt-provenance-binding-browser-producer', store: delayedStore, scheduler: makeScheduler(m, '${REVISION}-receipt-provenance-binding-browser-producer-scheduler'), lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const successPayload = bytesFromSeed('${REVISION}:receipt-provenance-binding-success-payload', ${JSON.stringify(payloadBytes)});
    const failurePayload = bytesFromSeed('${REVISION}:receipt-provenance-binding-failure-payload', ${JSON.stringify(payloadBytes)});
    const successDigest = 'sha256:' + await m.digestBytesHex(successPayload);
    const failureDigest = 'sha256:' + await m.digestBytesHex(failurePayload);
    producer.schedulePut(successPayload, { id: '${REVISION}-receipt-provenance-binding-success-timeout', priority: 'user-visible', label: 'receipt-provenance-binding-success' });
    producer.schedulePut(failurePayload, { id: '${REVISION}-receipt-provenance-binding-failure-timeout', priority: 'user-visible', label: 'receipt-provenance-binding-failure' });
    const dispatchSuccess = producer.scheduler.dispatchNext(); const dispatchFailure = producer.scheduler.dispatchNext();
    const [timeoutSuccess, timeoutFailure] = await Promise.all([producer.executor.executeDispatched(dispatchSuccess), producer.executor.executeDispatched(dispatchFailure)]);
    const providerCommittedBeforeRelease = await waitUntil(async () => { const successPresent = await raw.has(successDigest); const failurePresent = await raw.has(failureDigest); const locks = await guard.queryLocks(); return { ok: successPresent && failurePresent && locks.heldCount === 0 && locks.pendingCount === 0, successPresent, failurePresent, locks }; }, { timeoutMs: 3000, intervalMs: 25, label: 'both-provider-writes-committed-before-release' });
    releaseSuccess.resolve('browser-release-provenance-binding-success'); releaseFailure.resolve('browser-release-provenance-binding-failure');
    const settled = await producer.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 10 });
    const before = producer.timedOutOperationQuarantine('storage');
    const staleLedger = producer.exportTimedOutOperationQuarantine({ lane: 'storage', reason: 'browser-export-before-receipt-provenance-binding' });
    const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0080-browser-probe', reviewToken: 'browser-provenance-binding-review-token', reason: 'browser-review-before-receipt-provenance-binding' });
    const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-for-receipt-provenance-binding' });
    const validReceipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0080-browser-probe', label: 'browser-receipt-provenance-binding-valid-receipt' });
    const validValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(validReceipt);
    const wrongFingerprintReceipt = { ...validReceipt, receiptFingerprint: 'brt-qclear-v1:browserforged0000' };
    const badOpIdsReceipt = makeSelfConsistentReceipt(m, { ...validReceipt, opIds: ['not-the-cleared-browser-op-id'] });
    const preReviewMismatchReceipt = makeSelfConsistentReceipt(m, { ...validReceipt, preClearanceFingerprint: 'brt-qfp-v1:browser-stale-review-mismatch' });
    const forgedAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-receipt-provenance-binding-browser-forged', store: guard, scheduler: makeScheduler(m, '${REVISION}-receipt-provenance-binding-browser-forged-scheduler'), lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const wrongFingerprintRegister = forgedAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(wrongFingerprintReceipt, { lane: 'storage', reason: 'browser-direct-register-wrong-fingerprint' });
    const badOpIdsRegister = forgedAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(badOpIdsReceipt, { lane: 'storage', reason: 'browser-direct-register-opid-mismatch' });
    const preReviewMismatchRegister = forgedAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(preReviewMismatchReceipt, { lane: 'storage', reason: 'browser-direct-register-pre-review-mismatch' });
    const importAfterForgedRegisters = forgedAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-import-after-forged-direct-registers', markUnhealthy: false });
    const forgedLane = forgedAdapter.scheduler.snapshotLane('storage');
    const forgedQuarantine = forgedAdapter.timedOutOperationQuarantine('storage');
    const validAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-receipt-provenance-binding-browser-valid', store: guard, scheduler: makeScheduler(m, '${REVISION}-receipt-provenance-binding-browser-valid-scheduler'), lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const bareValidDirectRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-valid-receipt-without-provenance' });
    const mismatchedProvenanceRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-valid-receipt-with-mismatched-provenance', provenance: { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: 'brt-qclear-v1:not-the-browser-receipt', preClearanceFingerprint: validReceipt.preClearanceFingerprint, adapterLabel: 'browser-manual', store: 'browser-manual', provider: 'browser-manual' } });
    const restoreProvenance = { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'block-store-restore-clearance-receipt', lane: 'storage', receiptFingerprint: validReceipt.receiptFingerprint, preClearanceFingerprint: validReceipt.preClearanceFingerprint, reviewFingerprint: validReceipt.reviewFingerprint, refDigest: 'sha256:browser-provenance-binding-restored-receipt', blockVerifyDigest: 'sha256:browser-provenance-binding-restored-receipt', blockVerifyBytes: 512, blockVerified: true, bytes: 512, adapterLabel: 'browser-provenance-binding-restore-adapter', store: guard.name, provider: guard.provider };
    const missingBlockVerifyRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-restore-provenance-missing-block-verify', provenance: { ...restoreProvenance, blockVerified: false, blockVerifyDigest: undefined } });
    const mismatchedBlockVerifyDigestRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-restore-provenance-digest-mismatch', provenance: { ...restoreProvenance, blockVerifyDigest: 'sha256:not-the-browser-restored-receipt' } });
    const mismatchedBlockVerifyBytesRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-restore-provenance-byte-mismatch', provenance: { ...restoreProvenance, blockVerifyBytes: 1024 } });
    const validRestoreProvenanceRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-valid-receipt-with-bound-restore-provenance', provenance: restoreProvenance });
    const validDirectRegister = validAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(validReceipt, { lane: 'storage', reason: 'browser-direct-register-valid-receipt-with-bound-provenance', provenance: { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: validReceipt.receiptFingerprint, preClearanceFingerprint: validReceipt.preClearanceFingerprint, reviewFingerprint: validReceipt.reviewFingerprint, adapterLabel: 'browser-provenance-binding-valid-adapter', store: guard.name, provider: guard.provider } });
    const replayAfterValidReceipt = validAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-replay-after-valid-direct-register', markUnhealthy: false });
    const laneAfterReplay = validAdapter.scheduler.snapshotLane('storage');
    const quarantineAfterReplay = validAdapter.timedOutOperationQuarantine('storage');
    const recoveryPayload = bytesFromSeed('${REVISION}:receipt-provenance-binding-after-valid-register', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'receipt-provenance-binding-after-valid-register' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const successVerify = await raw.verify(successDigest);
    const failureVerify = await raw.verify(failureDigest);
    const locksBeforeCleanup = await guard.queryLocks(); const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 }); const locksAfterCleanup = await guard.queryLocks(); const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, cleanupBefore, timeoutSuccess, timeoutFailure, providerCommittedBeforeRelease, settled, before, staleLedger, reviewManifest, clearResult, validReceipt, validValidation, wrongFingerprintRegister, badOpIdsRegister, preReviewMismatchRegister, importAfterForgedRegisters, forgedLane, forgedQuarantine, bareValidDirectRegister, mismatchedProvenanceRegister, missingBlockVerifyRegister, mismatchedBlockVerifyDigestRegister, mismatchedBlockVerifyBytesRegister, validRestoreProvenanceRegister, validDirectRegister, replayAfterValidReceipt, laneAfterReplay, quarantineAfterReplay, recoveryPut, recoveryVerify, successVerify, failureVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-clearance-receipt-provenance-binding';
  const lockName = options.lockName || `${REVISION}-quarantine-clearance-receipt-provenance-binding-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 8 * 1024);
  const profileDir = await mkdtemp(join(tmpdir(), 'browserrt-receipt-provenance-binding-profile-'));
  let server = null; let profileReap = null;
  try {
    server = await startProbeServer({ pagePath: '/browser-opfs-web-lock-quarantine-clearance-receipt-provenance-binding.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine clearance receipt provenance binding proof', allowedPrefixes: ['src/'] });
    const page = await runManagedBrowserPage({ server, timeoutMs: options.timeoutMs || 32000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, profileDir, keepProfile: true, profilePrefix: 'browserrt-receipt-provenance-binding-', stderrTerms: ['opfs', 'lock', 'quarantine', 'receipt'] }, async ({ evalJson, timeoutMs }) => await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs));
    const r = page.result;
    assert.equal(r.capabilities.opfs, true); assert.equal(r.capabilities.webLocks, true); assert.equal(r.capabilities.webLocksQuery, true);
    assert.equal(r.timeoutSuccess.ok, false); assert.equal(r.timeoutFailure.ok, false); assert.equal(r.timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(r.timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
    assert.equal(r.providerCommittedBeforeRelease.ok, true); assert.equal(r.settled.ok, true); assert.equal(r.before.successfulTimedOutOperationCount, 1); assert.equal(r.before.failedTimedOutOperationCount, 1);
    assert.equal(r.clearResult.ok, true); assert.equal(r.validValidation.ok, true);
    for (const result of [r.wrongFingerprintRegister, r.badOpIdsRegister, r.preReviewMismatchRegister]) { assert.equal(result.ok, false); assert.equal(result.disposition, 'rejected-clearance-receipt-integrity'); }
    assert.equal(r.importAfterForgedRegisters.ok, true); assert.equal(r.importAfterForgedRegisters.markUnhealthyForced, true); assert.equal(r.forgedLane.healthy, false); assert.equal(r.forgedQuarantine.totalCount, 2);
    assert.equal(r.bareValidDirectRegister.ok, false); assert.equal(r.bareValidDirectRegister.disposition, 'rejected-clearance-receipt-provenance'); assert.equal(r.mismatchedProvenanceRegister.ok, false); assert.equal(r.mismatchedProvenanceRegister.disposition, 'rejected-clearance-receipt-provenance'); for (const result of [r.missingBlockVerifyRegister, r.mismatchedBlockVerifyDigestRegister, r.mismatchedBlockVerifyBytesRegister]) { assert.equal(result.ok, false); assert.equal(result.disposition, 'rejected-clearance-receipt-provenance'); } assert.equal(r.validRestoreProvenanceRegister.ok, true); assert.equal(r.validDirectRegister.ok, true); assert.equal(r.replayAfterValidReceipt.ok, false); assert.equal(r.replayAfterValidReceipt.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(r.laneAfterReplay.healthy, true); assert.equal(r.quarantineAfterReplay.totalCount, 0);
    assert.equal(r.recoveryVerify.ok, true); assert.equal(r.successVerify.ok, true); assert.equal(r.failureVerify.ok, true); assert.equal(r.cleanupAfter, true); assert.equal(r.locksAfterCleanup.heldCount, 0); assert.equal(r.locksAfterCleanup.pendingCount, 0);
    for (const kind of ['storage-lane:timed-out-quarantine-clearance-receipt-rejected', 'storage-lane:timed-out-quarantine-clearance-receipt-registered', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(r.traceKinds.includes(kind), `missing trace ${kind}`);
    profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    assert.equal(profileReap.afterKillCount, 0);
    return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that timeout-quarantine clearance-receipt registration requires bound provenance before installing replay guard state over real guarded OPFS/Web Locks.', observations: { page: r, harness: page.harness, profileReap }, claimsChecked: ['receipt registration without provenance rejects before stale ledger replay guard state is installed', 'rejected forged receipts do not suppress a stale quarantine ledger', 'valid direct receipt registration requires bound provenance before blocking stale replay without poisoning lane health', 'block-store restore provenance must carry verified block digest and byte bindings before registration is accepted', 'real guarded OPFS timeout writes remain verifiable and later guarded writes recover'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Receipt fingerprint is deterministic review/integrity binding, not cryptographic attestation, tamper-proof storage, or security boundary.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness evidence.'] };
  } finally {
    await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 }).catch(() => null);
    if (server) await server.close().catch(() => null);
    await rm(profileDir, { recursive: true, force: true }).catch(() => null);
  }
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '32000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-receipt-provenance-binding-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser receipt provenance binding proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_clearance_receipt_provenance_binding_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
