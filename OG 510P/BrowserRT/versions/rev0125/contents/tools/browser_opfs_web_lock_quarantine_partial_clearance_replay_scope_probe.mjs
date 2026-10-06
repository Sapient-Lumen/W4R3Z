#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-PARTIAL-CLEARANCE-REPLAY-SCOPE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (97 + i * 13 + (i >>> 1)) & 255; return out; };
    const selfConsistentReceipt = (m, base) => { const draft = { ...base }; draft.receiptFingerprint = m.timedOutOperationQuarantineClearanceReceiptFingerprint(draft); return Object.freeze(draft); };
    const withFingerprint = (s, ledger) => { const fingerprint = s.timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fingerprint, reviewFingerprint: fingerprint }); };
    const registrationProvenance = (adapter, receipt) => ({ schema: 'brt.storageLane.timedOutOperationQuarantine.clearanceReceipt.registrationProvenance.v1', source: 'adapter-create-clearance-receipt', lane: receipt.lane ?? adapter.lane, receiptFingerprint: receipt.receiptFingerprint, preClearanceFingerprint: receipt.preClearanceFingerprint, reviewFingerprint: receipt.reviewFingerprint, adapterLabel: adapter.label, store: adapter.storeName, provider: adapter.providerName });
    const makeLedger = (s, { suffix = 'browser-partial-scope', lane = 'storage', epoch = '${REVISION}-browser-partial-clearance-epoch' } = {}) => { const now = Date.now(); const success = Object.freeze({ opId: '${REVISION}-' + suffix + '-late-success', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-' + suffix + '-late-success', timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: 'sha256:' + suffix + '-success', bytes: 32, disposition: 'browser-synthetic-late-success' } }); const failed = Object.freeze({ opId: '${REVISION}-' + suffix + '-late-failure', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-' + suffix + '-late-failure', timeoutMs: 25, timedOutAtMs: now + 2, settledAtMs: now + 3, error: { name: 'BrowserSyntheticLateFailure', message: 'browser synthetic late failure for partial clearance replay scope proof', code: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE' } }); const base = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, exportedAtMs: now + 4, label: '${REVISION}-browser-partial-clearance-replay-scope-ledger', reason: 'browser-synthetic-partial-clearance-replay-scope-ledger', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failed]) }); return withFingerprint(s, base); };
    const failedOnlyLedger = (s, staleLedger) => withFingerprint(s, { ...staleLedger, label: '${REVISION}-browser-partial-clearance-uncleared-only-ledger', reason: 'browser-uncleared-row-only-after-partial-clearance', counts: Object.freeze({ total: 1, unsettled: 0, successful: 0, failed: 1 }), successfulTimedOutOperations: Object.freeze([]), failedTimedOutOperations: Object.freeze([staleLedger.failedTimedOutOperations[0]]) });
    const forgedFullCountReceiptFrom = (m, partialReceipt, staleLedger) => { const lane = partialReceipt.lane || 'storage'; const epoch = '${REVISION}-browser-forged-partial-clearance-epoch'; const fakeSuccess = Object.freeze({ opId: '${REVISION}-browser-forged-cleared-success', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-browser-forged-cleared-success', disposition: 'forged-success' }); const fakeFailed = Object.freeze({ opId: '${REVISION}-browser-forged-cleared-failure', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-browser-forged-cleared-failure', disposition: 'forged-failure', error: { code: 'BRT_BROWSER_FORGED_FAILURE', storageDisposition: 'BRT_BROWSER_FORGED_FAILURE' } }); return selfConsistentReceipt(m, { ...partialReceipt, label: '${REVISION}-browser-forged-full-count-partial-clearance-receipt', preClearanceFingerprint: staleLedger.quarantineFingerprint, reviewFingerprint: staleLedger.reviewFingerprint, clearedCount: 2, successfulClearedCount: 1, failedClearedCount: 1, counts: Object.freeze({ total: 2, successful: 1, failed: 1 }), opIds: Object.freeze([fakeSuccess.opId, fakeFailed.opId]), categories: Object.freeze(['all']), cleared: Object.freeze({ successful: Object.freeze([fakeSuccess]), failed: Object.freeze([fakeFailed]) }) }); };
    const m = await import('/src/browserrt.mjs');
    const s = await import('/src/storage-lane-scheduler.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockPartialClearanceReplayScopeProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-partial-clearance-scope-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-partial-clearance-scope-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const makeScheduler = (label) => rt.crossLaneScheduler({ label, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const makeAdapter = (label) => rt.blockStoreLaneAdapter({ label, store: guard, scheduler: makeScheduler(label + ':scheduler'), trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const staleLedger = makeLedger(s);
    const unclearedLedger = failedOnlyLedger(s, staleLedger);
    const producer = makeAdapter('${REVISION}-browser-partial-clearance-producer');
    const importOriginal = producer.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-import-before-partial-clearance-scope-proof', markUnhealthy: false });
    const successOpId = staleLedger.successfulTimedOutOperations[0].opId;
    const failedOpId = staleLedger.failedTimedOutOperations[0].opId;
    const partialReview = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opId: successOpId, reviewer: 'rev0087-browser-probe', reviewToken: 'browser-partial-clearance-review-token', reason: 'browser-review-success-row-only' });
    const partialClear = producer.clearTimedOutOperationQuarantine({ reviewManifest: partialReview, requireReviewFingerprint: true, reason: 'browser-clear-only-success-row-for-partial-clearance-scope-proof' });
    const partialReceipt = producer.createTimedOutOperationQuarantineClearanceReceipt(partialClear, { reviewer: 'rev0087-browser-probe', label: 'browser-partial-clearance-receipt' });
    const partialValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(partialReceipt);

    const partialAdapter = makeAdapter('${REVISION}-browser-partial-clearance-fresh');
    const partialRegister = partialAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(partialReceipt, { lane: 'storage', reason: 'browser-register-partial-clearance-receipt', provenance: registrationProvenance(partialAdapter, partialReceipt) });
    const exactAfterPartial = partialAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-exact-stale-ledger-after-partial-clearance', markUnhealthy: false });
    const partialLaneAfterExact = partialAdapter.scheduler.snapshotLane('storage');
    const partialQuarantineAfterExact = partialAdapter.timedOutOperationQuarantine('storage');
    const unclearedImport = partialAdapter.importTimedOutOperationQuarantine(unclearedLedger, { lane: 'storage', reason: 'browser-uncleared-row-only-after-partial-clearance', markUnhealthy: false });
    const partialLaneAfterUncleared = partialAdapter.scheduler.snapshotLane('storage');
    const partialQuarantineAfterUncleared = partialAdapter.timedOutOperationQuarantine('storage');
    const failedReview = partialAdapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'failed', opId: failedOpId, reviewer: 'rev0087-browser-probe', reviewToken: 'browser-partial-clearance-uncleared-row-review-token', reason: 'browser-review-uncleared-failed-row' });
    const failedClear = partialAdapter.clearTimedOutOperationQuarantine({ reviewManifest: failedReview, requireReviewFingerprint: true, reason: 'browser-clear-uncleared-row-after-partial-clearance-scope-proof' });
    const partialHealthy = partialAdapter.executor.markHealthy('storage', 'browser-partial-clearance-recovery');

    const forgedAdapter = makeAdapter('${REVISION}-browser-partial-clearance-forged-full-count');
    const forgedReceipt = forgedFullCountReceiptFrom(m, partialReceipt, staleLedger);
    const forgedValidation = m.validateTimedOutOperationQuarantineClearanceReceipt(forgedReceipt);
    const forgedRegister = forgedAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(forgedReceipt, { lane: 'storage', reason: 'browser-register-forged-full-count-receipt', provenance: registrationProvenance(forgedAdapter, forgedReceipt) });
    const importAfterForgedFullCount = forgedAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-import-after-forged-full-count-receipt-with-wrong-rows', markUnhealthy: false });
    const forgedLaneAfterImport = forgedAdapter.scheduler.snapshotLane('storage');

    const fullProducer = makeAdapter('${REVISION}-browser-full-clearance-producer');
    const importForFull = fullProducer.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-import-before-full-clearance-control', markUnhealthy: false });
    const fullReview = fullProducer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0087-browser-probe', reviewToken: 'browser-full-clearance-control-review-token', reason: 'browser-review-full-clearance-control' });
    const fullClear = fullProducer.clearTimedOutOperationQuarantine({ reviewManifest: fullReview, requireReviewFingerprint: true, reason: 'browser-clear-full-control' });
    const fullReceipt = fullProducer.createTimedOutOperationQuarantineClearanceReceipt(fullClear, { reviewer: 'rev0087-browser-probe', label: 'browser-full-clearance-control-receipt' });
    const fullAdapter = makeAdapter('${REVISION}-browser-full-clearance-fresh');
    const fullRegister = fullAdapter.executor.registerTimedOutOperationQuarantineClearanceReceipt(fullReceipt, { lane: 'storage', reason: 'browser-register-full-clearance-control-receipt', provenance: registrationProvenance(fullAdapter, fullReceipt) });
    const exactAfterFull = fullAdapter.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', reason: 'browser-exact-stale-ledger-after-full-clearance-control', markUnhealthy: false });
    const write = fullAdapter.schedulePut(bytesFromSeed('${REVISION}:browser-partial-clearance-scope-recovery', 4096), { id: '${REVISION}-browser-partial-clearance-scope-recovery-put', label: 'browser-partial-clearance-scope-recovery-put', operationTimeoutMs: 1000 });
    const drain = await fullAdapter.drain({ maxSteps: 3 });
    const writeResult = drain.results.find((row) => row.opId === '${REVISION}-browser-partial-clearance-scope-recovery-put');
    const writeVerify = await raw.verify(writeResult.result.ref);
    const locksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const locksAfterCleanup = await guard.queryLocks();
    const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, staleLedger, unclearedLedger, importOriginal, partialReview, partialClear, partialReceipt, partialValidation, partialRegister, exactAfterPartial, partialLaneAfterExact, partialQuarantineAfterExact, unclearedImport, partialLaneAfterUncleared, partialQuarantineAfterUncleared, failedReview, failedClear, partialHealthy, forgedReceipt, forgedValidation, forgedRegister, importAfterForgedFullCount, forgedLaneAfterImport, importForFull, fullReview, fullClear, fullReceipt, fullRegister, exactAfterFull, write, writeResult, writeVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, opId: event.opId ?? null, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-partial-clearance-replay-scope-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-partial-clearance-replay-scope';
  const lockName = options.lockName || `${REVISION}-quarantine-partial-clearance-replay-scope-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 28000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-partial-clearance-replay-scope.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine partial clearance replay scope proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-partial-clearance-scope-', stderrTerms: ['opfs', 'lock', 'quarantine', 'clearance', 'partial'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.importOriginal.ok, true); assert.equal(result.importOriginal.importedCount, 2); assert.equal(result.importOriginal.markUnhealthyForced, true);
  assert.equal(result.partialClear.ok, true); assert.equal(result.partialClear.clearedCount, 1); assert.equal(result.partialClear.successfulClearedCount, 1); assert.equal(result.partialClear.failedClearedCount, 0);
  assert.equal(result.partialValidation.ok, true); assert.equal(result.partialRegister.ok, true); assert.equal(result.partialRegister.clearedCount, 1);
  assert.equal(result.exactAfterPartial.ok, false); assert.equal(result.exactAfterPartial.disposition, 'rejected-cleared-quarantine-row-replay'); assert.equal(result.exactAfterPartial.matchedRows.length, 1);
  assert.equal(result.partialLaneAfterExact.healthy, true); assert.equal(result.partialQuarantineAfterExact.totalCount, 0);
  assert.equal(result.unclearedImport.ok, true); assert.equal(result.unclearedImport.importedCount, 1); assert.equal(result.unclearedImport.failedCount, 1); assert.equal(result.unclearedImport.markUnhealthyForced, true);
  assert.equal(result.partialLaneAfterUncleared.healthy, false); assert.equal(result.partialQuarantineAfterUncleared.failedTimedOutOperationCount, 1);
  assert.equal(result.failedClear.ok, true); assert.equal(result.failedClear.clearedCount, 1); assert.equal(result.partialHealthy.healthy, true);
  assert.equal(result.forgedValidation.ok, false); assert.ok(result.forgedValidation.errors.some((e) => e.includes('operationReplayKeys must match'))); assert.equal(result.forgedRegister.ok, false); assert.equal(result.forgedRegister.disposition, 'rejected-clearance-receipt-integrity');
  assert.equal(result.importAfterForgedFullCount.ok, true); assert.equal(result.importAfterForgedFullCount.importedCount, 2); assert.equal(result.importAfterForgedFullCount.markUnhealthyForced, true); assert.equal(result.forgedLaneAfterImport.healthy, false);
  assert.equal(result.fullClear.ok, true); assert.equal(result.fullClear.clearedCount, 2); assert.equal(result.fullRegister.ok, true);
  assert.equal(result.exactAfterFull.ok, false); assert.equal(result.exactAfterFull.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(result.exactAfterFull.matchedRows.length, 2);
  assert.equal(result.write.accepted, true); assert.equal(result.writeResult?.ok, true); assert.equal(result.writeVerify.ok, true);
  assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-import-row-replay-rejected', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'storage-lane:timed-out-quarantine-import-replay-rejected', 'storage-lane:timed-out-quarantine-clearance-receipt-registered', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-partial-clearance-replay-scope-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that partial timeout-quarantine clearance receipts cannot suppress still-uncleared rows through full-fingerprint replay rejection over real guarded OPFS/Web Locks.', observations: { ...result, harness }, claimsChecked: ['partial clearance receipt routes exact full stale ledger through row-replay rejection instead of exact replay suppression', 'uncleared row-only ledger still imports and backpressures for review', 'forged full-count receipt with wrong operationReplayKeys is rejected and does not suppress stale ledger import', 'genuine full clearance still rejects exact stale replay', 'later guarded OPFS write verifies and locks drain'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Partial-clearance replay scope is deterministic integrity policy, not cryptographic attestation, tamper-proof storage, or access-control security boundary.', 'No provider cancellation, rollback, no-mutation-on-timeout, exactly-once, durability, quota, eviction, SLO, or production-readiness claim.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '28000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-partial-clearance-replay-scope-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser partial clearance replay scope proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_partial_clearance_replay_scope_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
