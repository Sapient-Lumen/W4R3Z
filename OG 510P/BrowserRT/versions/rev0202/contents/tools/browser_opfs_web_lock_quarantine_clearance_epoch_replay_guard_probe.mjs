#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-CLEARANCE-EPOCH-REPLAY-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const waitUntil = async (predicate, { timeoutMs = 3000, intervalMs = 25, label = 'condition' } = {}) => { const start = performance.now(); let last = null; while (performance.now() - start <= timeoutMs) { last = await predicate(); if (last === true || last?.ok === true) return { ok: true, elapsedMs: performance.now() - start, last, label }; await sleep(intervalMs); } return { ok: false, elapsedMs: performance.now() - start, last, label }; };
    const deferred = () => { let resolve; let reject; const promise = new Promise((res, rej) => { resolve = res; reject = rej; }); return { promise, resolve, reject }; };
    const codedError = (code, message, detail = {}) => { const error = new Error(message); error.name = 'BrowserRTBrowserEpochReplayGuardProviderError'; error.code = code; error.storageDisposition = code; error.detail = Object.freeze({ ...detail }); return error; };
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 17 + (i >>> 2)) & 255; return out; };
    const m = await import('/src/browserrt.mjs');
    const sched = await import('/src/storage-lane-scheduler.mjs');
    const withFingerprint = (ledger) => { const quarantineFingerprint = sched.timedOutQuarantineFingerprint(ledger); return { ...ledger, quarantineFingerprint, reviewFingerprint: quarantineFingerprint }; };
    const statusRewriteLedger = (ledger, { dropEpoch = false } = {}) => { const source = (ledger.failedTimedOutOperations || [])[0] || (ledger.successfulTimedOutOperations || [])[0]; if (!source) throw new Error('status rewrite proof requires a cleared row'); const rewritten = { opId: source.opId, kind: source.kind || 'put', lane: source.lane || 'storage', timeoutMs: Number(source.timeoutMs || ${JSON.stringify(operationTimeoutMs)}), timedOutAtMs: Number(source.timedOutAtMs || Date.now()), settledAtMs: Date.now() + 23, result: { digest: 'sha256:browser-epoch-replay-status-rewrite', bytes: 31, disposition: 'browser-status-rewrite-success' } }; if (!dropEpoch) { rewritten.operationEpoch = source.operationEpoch ?? null; rewritten.operationReplayKey = source.operationReplayKey ?? null; } return withFingerprint({ ...ledger, reason: dropEpoch ? 'browser-status-rewrite-with-operation-epoch-stripped' : 'browser-status-rewrite-with-operation-epoch-preserved', counts: { total: 1, successful: 1, failed: 0, unsettled: 0 }, successfulTimedOutOperations: [rewritten], failedTimedOutOperations: [], unsettledTimedOutOperations: [] }); };
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockQuarantineClearanceEpochReplayProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-clearance-epoch-replay-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-clearance-epoch-replay-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const releases = new Map();
    const releaseFor = (label) => { if (!releases.has(label)) releases.set(label, deferred()); return releases.get(label); };
    const refs = {};
    const delayedStore = {
      name: '${REVISION}-clearance-epoch-replay-delayed-guarded-store', provider: 'clearance-epoch-replay:' + guard.provider,
      async put(payload, fields = {}) { const put = await guard.put(payload, fields, { timeoutMs: 1000 }); const label = String(fields.label || ''); refs[label] = put.ref || put; if (label.includes('late-success')) { await releaseFor(label).promise; return put; } if (label.includes('late-failure')) { await releaseFor(label).promise; throw codedError('BRT_BROWSER_EPOCH_REPLAY_LATE_FAILURE', 'browser clearance epoch replay late failure after committed guarded OPFS write', { digest: put.digest, bytes: put.bytes }); } return put; },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); }, async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); }, async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); }, async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); }, async estimate() { return await guard.estimate({ timeoutMs: 1000 }); }, async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); }, async waitForSettled(options = {}) { return await guard.waitForSettled(options); }, snapshot() { return { name: this.name, provider: this.provider, guard: guard.snapshot() }; }
    };
    const makeScheduler = (label) => rt.crossLaneScheduler({ label, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 16384 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const makeAdapter = (label, timeout = ${JSON.stringify(operationTimeoutMs)}) => rt.blockStoreLaneAdapter({ label, store: delayedStore, scheduler: makeScheduler(label + ':scheduler'), trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: timeout });
    const createTimedOutLedger = async (adapter, idPrefix, payloadPrefix) => {
      const successLabel = idPrefix + '-late-success'; const failureLabel = idPrefix + '-late-failure';
      const successPayload = bytesFromSeed(payloadPrefix + ':success', ${JSON.stringify(payloadBytes)}); const failurePayload = bytesFromSeed(payloadPrefix + ':failure', ${JSON.stringify(payloadBytes)});
      const successDigest = 'sha256:' + await m.digestBytesHex(successPayload); const failureDigest = 'sha256:' + await m.digestBytesHex(failurePayload);
      adapter.schedulePut(successPayload, { id: 'shared-timeout-success-op', priority: 'user-visible', label: successLabel });
      adapter.schedulePut(failurePayload, { id: 'shared-timeout-failure-op', priority: 'user-visible', label: failureLabel });
      const dispatchSuccess = adapter.scheduler.dispatchNext(); const dispatchFailure = adapter.scheduler.dispatchNext();
      const [timeoutSuccess, timeoutFailure] = await Promise.all([adapter.executor.executeDispatched(dispatchSuccess), adapter.executor.executeDispatched(dispatchFailure)]);
      const committedBeforeRelease = await waitUntil(async () => { const successPresent = await raw.has(successDigest); const failurePresent = await raw.has(failureDigest); const locks = await guard.queryLocks(); return { ok: successPresent && failurePresent && locks.heldCount === 0 && locks.pendingCount === 0, successPresent, failurePresent, locks }; }, { timeoutMs: 3000, intervalMs: 25, label: idPrefix + '-provider-committed-before-release' });
      releaseFor(successLabel).resolve('browser-release-' + successLabel); releaseFor(failureLabel).resolve('browser-release-' + failureLabel);
      const settled = await adapter.executor.waitForTimedOutOperationsSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 10 });
      const quarantine = adapter.timedOutOperationQuarantine('storage');
      const ledger = adapter.exportTimedOutOperationQuarantine({ lane: 'storage', reason: idPrefix + '-export-before-clear' });
      const successVerify = await raw.verify(successDigest); const failureVerify = await raw.verify(failureDigest);
      return { timeoutSuccess, timeoutFailure, committedBeforeRelease, settled, quarantine, ledger, successDigest, failureDigest, successVerify, failureVerify };
    };
    const original = makeAdapter('${REVISION}-clearance-epoch-replay-original-adapter');
    const originalRun = await createTimedOutLedger(original, 'epoch-original', '${REVISION}:epoch-original');
    const staleLedger = originalRun.ledger;
    const statusRewritePreserved = statusRewriteLedger(staleLedger, { dropEpoch: false });
    const statusRewriteDowngrade = statusRewriteLedger(staleLedger, { dropEpoch: true });
    const reviewManifest = original.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0082-browser-probe', reviewToken: 'browser-epoch-replay-review-token', reason: 'browser-review-before-epoch-replay' });
    const clearResult = original.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-for-epoch-replay' });
    const receipt = original.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0082-browser-probe', label: 'browser-epoch-replay-receipt' });
    const validation = m.validateTimedOutOperationQuarantineClearanceReceipt(receipt);
    const persisted = await original.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label: 'browser-epoch-replay-receipt-persisted' });
    const fresh = makeAdapter('${REVISION}-clearance-epoch-replay-fresh-adapter', 1000);
    const restored = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane: 'storage' });
    const exactReplay = fresh.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-epoch-exact-stale-replay', markUnhealthy: false });
    const preservedReplay = fresh.importTimedOutOperationQuarantine(statusRewritePreserved, { lane: 'storage', reason: 'browser-epoch-status-rewrite-preserved-replay', markUnhealthy: false });
    const downgradeReplay = fresh.importTimedOutOperationQuarantine(statusRewriteDowngrade, { lane: 'storage', reason: 'browser-epoch-stripped-downgrade-replay', markUnhealthy: false });
    const collision = makeAdapter('${REVISION}-clearance-epoch-replay-collision-adapter');
    const collisionRun = await createTimedOutLedger(collision, 'epoch-collision', '${REVISION}:epoch-collision');
    const collisionLedger = collisionRun.ledger;
    const collisionImport = fresh.importTimedOutOperationQuarantine(collisionLedger, { lane: 'storage', reason: 'browser-epoch-collision-import-same-opids-new-epoch', markUnhealthy: false });
    const laneAfterCollisionImport = fresh.scheduler.snapshotLane('storage');
    const quarantineAfterCollisionImport = fresh.timedOutOperationQuarantine('storage');
    const collisionReview = fresh.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0082-browser-probe', reviewToken: 'browser-epoch-collision-clear-token', reason: 'browser-review-collision-quarantine' });
    const collisionClear = fresh.clearTimedOutOperationQuarantine({ reviewManifest: collisionReview, requireReviewFingerprint: true, reason: 'browser-clear-collision-quarantine' });
    const recovered = await fresh.recoverWhenStoreSettled({ lane: 'storage', timeoutMs: 2000, intervalMs: 10, reason: 'browser-epoch-collision-cleared-recovery' });
    const recoveryPayload = bytesFromSeed('${REVISION}:epoch-replay-after-collision', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'epoch-replay-after-collision' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks(); const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 }); const locksAfterCleanup = await guard.queryLocks(); const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, originalRun, staleLedger, statusRewritePreserved, statusRewriteDowngrade, reviewManifest, clearResult, receipt, validation, persisted, restored, exactReplay, preservedReplay, downgradeReplay, collisionRun, collisionLedger, collisionImport, laneAfterCollisionImport, quarantineAfterCollisionImport, collisionReview, collisionClear, recovered, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-clearance-epoch-replay-guard';
  const lockName = options.lockName || `${REVISION}-quarantine-clearance-epoch-replay-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 350);
  const payloadBytes = Number(options.payloadBytes || 8 * 1024);
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 36000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine clearance epoch replay guard proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-clearance-epoch-replay-', stderrTerms: ['opfs', 'lock', 'quarantine', 'receipt'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  for (const run of [result.originalRun, result.collisionRun]) {
    assert.equal(run.timeoutSuccess.ok, false); assert.equal(run.timeoutFailure.ok, false); assert.equal(run.timeoutSuccess.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT'); assert.equal(run.timeoutFailure.error.code, 'BRT_STORAGE_OPERATION_TIMEOUT');
    assert.equal(run.committedBeforeRelease.ok, true); assert.equal(run.settled.ok, true); assert.equal(run.quarantine.successfulTimedOutOperationCount, 1); assert.equal(run.quarantine.failedTimedOutOperationCount, 1); assert.equal(run.successVerify.ok, true); assert.equal(run.failureVerify.ok, true);
    assert.ok(run.ledger.successfulTimedOutOperations.every((row) => row.operationEpoch && row.operationReplayKey)); assert.ok(run.ledger.failedTimedOutOperations.every((row) => row.operationEpoch && row.operationReplayKey));
  }
  assert.equal(result.clearResult.ok, true); assert.equal(result.validation.ok, true); assert.equal(result.persisted.ok, true); assert.equal(result.restored.ok, true); assert.equal(result.restored.registration.ok, true);
  assert.equal(result.exactReplay.ok, false); assert.equal(result.exactReplay.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(result.preservedReplay.ok, false); assert.equal(result.preservedReplay.disposition, 'rejected-cleared-quarantine-row-replay');
  assert.equal(result.downgradeReplay.ok, false); assert.equal(result.downgradeReplay.disposition, 'rejected-cleared-quarantine-row-replay-downgrade'); assert.ok(result.downgradeReplay.matchedRows.some((row) => row.replayKind === 'cleared-operation-identity-downgrade'));
  assert.notEqual(result.collisionLedger.quarantineFingerprint, result.staleLedger.quarantineFingerprint);
  assert.notEqual(result.collisionLedger.successfulTimedOutOperations[0].operationReplayKey, result.staleLedger.successfulTimedOutOperations[0].operationReplayKey);
  assert.equal(result.collisionImport.ok, true); assert.equal(result.collisionImport.markUnhealthyForced, true); assert.equal(result.laneAfterCollisionImport.healthy, false); assert.equal(result.quarantineAfterCollisionImport.totalCount, 2);
  assert.equal(result.collisionClear.ok, true); assert.equal(result.collisionClear.clearedCount, 2); assert.equal(result.recovered.recovered, true); assert.equal(result.recoveryVerify.ok, true);
  assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['block-store-lane:quarantine-clearance-receipt-persisted', 'block-store-lane:quarantine-clearance-receipt-restored', 'storage-lane:timed-out-quarantine-import-row-replay-rejected', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that timeout-quarantine clearance row replay guards are operation-epoch scoped over real guarded OPFS/Web Locks.', observations: { ...result, harness }, claimsChecked: ['real guarded OPFS timeout-quarantine rows carry operationEpoch and operationReplayKey', 'stale exact ledger replay remains rejected', 'status-rewritten rows with preserved operation epoch reject by operation replay key', 'epoch-stripped stale replay rejects as downgrade', 'fresh same-opId timeout quarantine with a different operation epoch imports/backpressures normally', 'later guarded OPFS write verifies after reviewed clearing and explicit recovery'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Operation epochs are replay-scoping/collision-avoidance markers, not cryptographic attestation or tamper-proof storage.', 'Operation timeout is not provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '36000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-epoch-replay-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser clearance epoch replay guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_clearance_epoch_replay_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
