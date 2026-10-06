#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-operation-replay-key-collision-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-OPERATION-REPLAY-KEY-COLLISION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (17 + i * 29 + (i >>> 2)) & 255; return out; };
    const m = await import('/src/browserrt.mjs');
    const s = await import('/src/storage-lane-scheduler.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockOperationReplayKeyCollisionProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-operation-replay-key-collision-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-operation-replay-key-collision-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const scheduler = (label) => rt.crossLaneScheduler({ label, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = (label) => rt.blockStoreLaneAdapter({ label, store: guard, scheduler: scheduler(label + ':scheduler'), trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const withFingerprint = (ledger) => { const fp = s.timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fp, reviewFingerprint: fp }); };
    const row = (epoch, suffix) => { const opId = '${REVISION}-shared-browser-visible-put-op'; const now = Date.now(); return Object.freeze({ opId, kind: 'put', lane: 'storage', operationEpoch: epoch, operationReplayKey: 'operation:storage:put:' + epoch + ':' + opId, timeoutMs: 35, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: 'sha256:' + suffix, bytes: 64, disposition: 'browser-synthetic-late-success' } }); };
    const ledgerBase = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane: 'storage', exportedAtMs: Date.now(), label: '${REVISION}-browser-operation-replay-key-collision-ledger', reason: 'browser-merged-ledger-same-visible-opid-distinct-operation-replay-keys', counts: Object.freeze({ total: 2, unsettled: 0, successful: 2, failed: 0 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([row('${REVISION}:browser-epoch-a', 'browser-operation-collision-a'), row('${REVISION}:browser-epoch-b', 'browser-operation-collision-b')]), failedTimedOutOperations: Object.freeze([]) });
    const ledger = withFingerprint(ledgerBase);
    const duplicateOperationKeyLedger = withFingerprint({ ...ledgerBase, reason: 'browser-duplicate-operation-replay-key-ledger', successfulTimedOutOperations: Object.freeze([ledgerBase.successfulTimedOutOperations[0], { ...ledgerBase.successfulTimedOutOperations[0], settledAtMs: ledgerBase.successfulTimedOutOperations[0].settledAtMs + 11 }]) });
    const singleRowStaleLedger = withFingerprint({ ...ledgerBase, reason: 'browser-single-row-replay-after-collision-clear', counts: Object.freeze({ total: 1, unsettled: 0, successful: 1, failed: 0 }), successfulTimedOutOperations: Object.freeze([ledgerBase.successfulTimedOutOperations[0]]) });
    const importer = adapter('${REVISION}-browser-operation-replay-key-collision-importer');
    const importResult = importer.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'browser-import-merged-duplicate-visible-opid-ledger', markUnhealthy: false });
    const quarantineAfterImport = importer.timedOutOperationQuarantine('storage');
    const duplicateAdapter = adapter('${REVISION}-browser-operation-replay-key-collision-duplicate');
    const duplicateImport = duplicateAdapter.importTimedOutOperationQuarantine(duplicateOperationKeyLedger, { lane: 'storage', reason: 'browser-import-duplicate-operation-replay-key-ledger', markUnhealthy: false });
    const review = importer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0087-browser-probe', reviewToken: 'browser-operation-replay-key-collision-review-token', reason: 'browser-review-duplicate-visible-opid-quarantine' });
    const clear = importer.clearTimedOutOperationQuarantine({ reviewManifest: review, requireReviewFingerprint: true, reason: 'browser-clear-duplicate-visible-opid-quarantine' });
    const receipt = importer.createTimedOutOperationQuarantineClearanceReceipt(clear, { reviewer: 'rev0087-browser-probe', label: 'browser-operation-replay-key-collision-receipt' });
    const receiptValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(receipt);
    const storageReceipts = importer.executor.clearedTimedOutOperationQuarantineClearanceReceipts('storage');
    const maintenanceReceipts = importer.executor.clearedTimedOutOperationQuarantineClearanceReceipts('maintenance');
    const fresh = adapter('${REVISION}-browser-operation-replay-key-collision-fresh');
    const provenance = { schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: 'storage', receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: fresh.label, store: fresh.storeName, provider: fresh.providerName };
    const register = fresh.executor.registerTimedOutOperationQuarantineClearanceReceipt(receipt, { lane: 'storage', reason: 'browser-register-operation-key-collision-receipt', provenance });
    const exactReplay = fresh.importTimedOutOperationQuarantine(ledger, { lane: 'storage', reason: 'browser-exact-replay-after-operation-key-collision-clear', markUnhealthy: false });
    const rowReplay = fresh.importTimedOutOperationQuarantine(singleRowStaleLedger, { lane: 'storage', reason: 'browser-single-row-replay-after-operation-key-collision-clear', markUnhealthy: false });
    const recoveryPayload = bytesFromSeed('${REVISION}:browser-operation-replay-key-collision-recovery', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'browser-operation-replay-key-collision-recovery-put' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const locksAfterCleanup = await guard.queryLocks();
    const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, ledger, importResult, quarantineAfterImport, duplicateImport, review, clear, receipt, receiptValidation, storageReceipts, maintenanceReceipts, register, exactReplay, rowReplay, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((event) => event.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-operation-replay-key-collision-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-operation-replay-key-collision';
  const lockName = options.lockName || `${REVISION}-quarantine-operation-replay-key-collision-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 30000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-operation-replay-key-collision.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine operation replay-key collision proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-operation-replay-key-collision-', stderrTerms: ['opfs', 'lock', 'quarantine', 'collision'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.ledger.successfulTimedOutOperations[0].opId, result.ledger.successfulTimedOutOperations[1].opId);
  assert.notEqual(result.ledger.successfulTimedOutOperations[0].operationReplayKey, result.ledger.successfulTimedOutOperations[1].operationReplayKey);
  assert.equal(result.importResult.ok, true); assert.equal(result.importResult.importedCount, 2); assert.equal(result.importResult.markUnhealthyForced, true);
  assert.equal(result.quarantineAfterImport.totalCount, 2); assert.equal(result.quarantineAfterImport.successfulTimedOutOperationCount, 2); assert.equal(new Set(result.quarantineAfterImport.successfulTimedOutOperations.map((row) => row.operationReplayKey)).size, 2);
  assert.equal(result.duplicateImport.ok, false); assert.equal(result.duplicateImport.disposition, 'rejected-ledger-integrity');
  assert.equal(result.clear.ok, true); assert.equal(result.clear.clearedCount, 2); assert.equal(result.receiptValidation.ok, true); assert.equal(new Set(result.receipt.cleared.successful.map((row) => row.opId)).size, 1); assert.equal(new Set(result.receipt.cleared.successful.map((row) => row.operationReplayKey)).size, 2);
  assert.equal(result.storageReceipts.length, 1); assert.equal(result.maintenanceReceipts.length, 0);
  assert.equal(result.register.ok, true); assert.equal(result.exactReplay.ok, false); assert.equal(result.exactReplay.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(result.rowReplay.ok, false); assert.equal(result.rowReplay.disposition, 'rejected-cleared-quarantine-row-replay');
  assert.equal(result.recoveryVerify.ok, true); assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-import-backpressure-forced', 'storage-lane:timed-out-quarantine-clearance-receipt-registered', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'storage-lane:timed-out-quarantine-import-row-replay-rejected', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-operation-replay-key-collision-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that timeout-quarantine rows with reused visible opId remain distinct by operationReplayKey over real guarded OPFS/Web Locks.', observations: { ...result, harness }, claimsChecked: ['same visible opId with distinct operationReplayKey imports as two rows instead of collapsing', 'duplicate operationReplayKey import fails closed', 'clearance receipt validation and replay guards preserve distinct rows with reused visible opId', 'lane-wide receipt query remains lane-scoped', 'later guarded OPFS write verifies'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks claim.', 'Synthetic timeout ledger rows are used to exercise import/clearance collision policy while OPFS/Web Locks verify the provider path.', 'Operation replay keys are collision/replay-scoping metadata, not cryptographic attestation or tamper-proof storage.', 'No provider cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '30000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-operation-replay-key-collision-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser operation replay-key collision proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_operation_replay_key_collision_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
