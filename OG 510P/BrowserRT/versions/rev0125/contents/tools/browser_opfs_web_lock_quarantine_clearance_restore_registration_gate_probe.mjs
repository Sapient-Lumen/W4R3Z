#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile, mkdtemp, rm } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, startProbeServer, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-CLEARANCE-RESTORE-REGISTRATION-GATE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function phaseOneExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (71 + i * 17 + (i >>> 1)) & 255; return out; };
    const makeLedger = (fingerprintFn, { lane = 'storage', suffix = 'restore-registration-gate', epoch = '${REVISION}-browser-restore-registration-gate-epoch' } = {}) => { const now = Date.now(); const success = Object.freeze({ opId: '${REVISION}-' + suffix + '-late-success', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-' + suffix + '-late-success', timeoutMs: 25, timedOutAtMs: now, settledAtMs: now + 1, result: { digest: 'sha256:' + suffix + '-success', bytes: 64, disposition: 'browser-synthetic-late-success' } }); const failed = Object.freeze({ opId: '${REVISION}-' + suffix + '-late-failure', kind: 'put', lane, operationEpoch: epoch, operationReplayKey: 'operation:' + lane + ':put:' + epoch + ':' + '${REVISION}-' + suffix + '-late-failure', timeoutMs: 25, timedOutAtMs: now + 2, settledAtMs: now + 3, error: { name: 'BrowserSyntheticLateFailure', message: 'browser synthetic late failure for restore registration gate proof', code: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE', storageDisposition: 'BRT_BROWSER_SYNTHETIC_LATE_FAILURE' } }); const base = Object.freeze({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', lane, exportedAtMs: now + 4, label: '${REVISION}-browser-restore-registration-gate-ledger', reason: 'browser-synthetic-restore-registration-gate-ledger', counts: Object.freeze({ total: 2, unsettled: 0, successful: 1, failed: 1 }), unsettledTimedOutOperations: Object.freeze([]), successfulTimedOutOperations: Object.freeze([success]), failedTimedOutOperations: Object.freeze([failed]) }); const fp = fingerprintFn(base); return Object.freeze({ ...base, quarantineFingerprint: fp, reviewFingerprint: fp }); };
    const m = await import('/src/browserrt.mjs');
    const s = await import('/src/storage-lane-scheduler.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsRestoreRegistrationGatePhase: 'persist' });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-restore-registration-gate-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    await raw.open();
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-restore-registration-gate-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    const cleanupBefore = await guard.cleanupForTest({ timeoutMs: 1000 });
    const staleLedger = makeLedger(s.timedOutQuarantineFingerprint);
    const makeScheduler = (label) => rt.crossLaneScheduler({ label, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const producer = rt.blockStoreLaneAdapter({ label: '${REVISION}-restore-registration-gate-browser-producer', store: guard, scheduler: makeScheduler('${REVISION}-restore-registration-gate-browser-producer-scheduler'), trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const imported = producer.importTimedOutOperationQuarantine(staleLedger, { lane: 'storage', markUnhealthy: false, reason: 'browser-import-before-clear-for-restore-registration-gate' });
    const reviewManifest = producer.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'all', allowLaneWide: true, reviewer: 'rev0086-browser-probe', reviewToken: 'browser-restore-registration-gate-review-token', reason: 'browser-review-for-restore-registration-gate' });
    const clearResult = producer.clearTimedOutOperationQuarantine({ reviewManifest, requireReviewFingerprint: true, reason: 'browser-clear-for-restore-registration-gate-receipt' });
    const receipt = producer.createTimedOutOperationQuarantineClearanceReceipt(clearResult, { reviewer: 'rev0086-browser-probe', label: 'browser-restore-registration-gate-receipt' });
    const persisted = await producer.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label: 'browser-restore-registration-gate-persisted-receipt' });
    const persistedVerify = await raw.verify(persisted.ref);
    const seedPut = await guard.put(bytesFromSeed('${REVISION}:restore-registration-gate-seed', 1024), { label: 'browser-restore-registration-gate-seed' }, { timeoutMs: 1000 });
    const seedVerify = await raw.verify(seedPut.ref || seedPut);
    const locksAfterPersist = await guard.queryLocks();
    const trace = rt.close();
    return { capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, cleanupBefore, staleLedger, imported, reviewManifest, clearResult, receipt, persisted, persistedVerify, seedPut, seedVerify, locksAfterPersist, traceKinds: trace.map((event) => event.kind) };
  })()`;
}

function phaseTwoExpression({ prefix, lockPrefix, lockName, staleLedger, receiptRef }) {
  return `(async () => {
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (89 + i * 23 + (i >>> 2)) & 255; return out; };
    const m = await import('/src/browserrt.mjs');
    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsRestoreRegistrationGatePhase: 'restore' });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-restore-registration-gate-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    await raw.open();
    const guard = rt.opfsWebLockGuardedBlockStore({ label: '${REVISION}-restore-registration-gate-restore-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    const makeScheduler = (label) => rt.crossLaneScheduler({ label, trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 2, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const ledger = ${JSON.stringify(staleLedger)};
    const ref = ${JSON.stringify(receiptRef)};
    const receiptVerifyBeforeRestore = await raw.verify(ref);
    const wrongLane = rt.blockStoreLaneAdapter({ label: '${REVISION}-restore-registration-gate-browser-wrong-lane', store: guard, scheduler: makeScheduler('${REVISION}-restore-registration-gate-browser-wrong-lane-scheduler'), trace: rt.trace, lane: 'maintenance', defaultOperationTimeoutMs: 1000 });
    const wrongLaneRestore = await wrongLane.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(ref, { lane: 'maintenance', reason: 'browser-restore-storage-receipt-into-maintenance-lane' });
    const receiptsAfterWrongRestore = wrongLane.clearedTimedOutOperationQuarantineClearanceReceipts('storage');
    const importAfterRejectedRestore = wrongLane.importTimedOutOperationQuarantine(ledger, { lane: 'storage', markUnhealthy: false, reason: 'browser-import-after-rejected-restore-registration' });
    const wrongLaneState = wrongLane.scheduler.snapshotLane('storage');
    const wrongLaneQuarantine = wrongLane.timedOutOperationQuarantine('storage');
    const validAdapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-restore-registration-gate-browser-valid', store: guard, scheduler: makeScheduler('${REVISION}-restore-registration-gate-browser-valid-scheduler'), trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
    const validRestore = await validAdapter.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(ref, { lane: 'storage', reason: 'browser-restore-storage-receipt-into-storage-lane' });
    const replayAfterValidRestore = validAdapter.importTimedOutOperationQuarantine(ledger, { lane: 'storage', markUnhealthy: false, reason: 'browser-replay-after-valid-restore-registration' });
    const laneAfterReplay = validAdapter.scheduler.snapshotLane('storage');
    const quarantineAfterReplay = validAdapter.timedOutOperationQuarantine('storage');
    const recoveryPut = await guard.put(bytesFromSeed('${REVISION}:restore-registration-gate-recovery', 4096), { label: 'browser-restore-registration-gate-recovery' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const locksAfterCleanup = await guard.queryLocks();
    const trace = rt.close();
    return { capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, receiptVerifyBeforeRestore, wrongLaneRestore, receiptsAfterWrongRestore, importAfterRejectedRestore, wrongLaneState, wrongLaneQuarantine, validRestore, replayAfterValidRestore, laneAfterReplay, quarantineAfterReplay, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((event) => event.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('clearance')).map((event) => ({ kind: event.kind, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null, lane: event.lane ?? null })) };
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const profileDir = options.profileDir || await mkdtemp(join(tmpdir(), 'browserrt-restore-registration-gate-profile-'));
  const server = await startProbeServer({ pagePath: '/browser-opfs-web-lock-quarantine-clearance-restore-registration-gate.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine clearance restore registration gate proof', allowedPrefixes: ['src/'] });
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-clearance-restore-registration-gate-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-clearance-restore-registration-gate';
  const lockName = options.lockName || `${REVISION}-quarantine-clearance-restore-registration-gate-lock`;
  let cleanupReap = null;
  try {
    const first = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 26000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, server, pagePath: server.pagePath, profileDir, keepProfile: true, profilePrefix: 'browserrt-restore-registration-gate-', stderrTerms: ['opfs','lock','quarantine','receipt','restore'] }, async ({ evalJson, timeoutMs }) => await evalJson(phaseOneExpression({ prefix, lockPrefix, lockName }), timeoutMs));
    const second = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 26000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, server, pagePath: server.pagePath, profileDir, keepProfile: true, profilePrefix: 'browserrt-restore-registration-gate-', stderrTerms: ['opfs','lock','quarantine','receipt','restore'] }, async ({ evalJson, timeoutMs }) => await evalJson(phaseTwoExpression({ prefix, lockPrefix, lockName, staleLedger: first.result.staleLedger, receiptRef: first.result.persisted.ref }), timeoutMs));
    cleanupReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 250, killMs: 750 });
    const p = first.result;
    const r = second.result;
    assert.equal(p.capabilities.opfs, true); assert.equal(p.capabilities.webLocks, true); assert.equal(r.capabilities.opfs, true); assert.equal(r.capabilities.webLocks, true);
    assert.equal(p.page.origin, r.page.origin);
    assert.equal(p.imported.ok, true); assert.equal(p.imported.markUnhealthyForced, true); assert.equal(p.clearResult.ok, true); assert.equal(p.clearResult.clearedCount, 2); assert.equal(p.persisted.ok, true); assert.equal(p.persistedVerify.ok, true); assert.equal(p.seedVerify.ok, true);
    assert.equal(r.receiptVerifyBeforeRestore.ok, true);
    assert.equal(r.wrongLaneRestore.ok, false); assert.equal(r.wrongLaneRestore.disposition, 'rejected-clearance-receipt-lane-binding'); assert.equal(r.wrongLaneRestore.registration?.ok, false); assert.equal(r.receiptsAfterWrongRestore.length, 0);
    assert.equal(r.importAfterRejectedRestore.ok, true); assert.equal(r.importAfterRejectedRestore.markUnhealthyForced, true); assert.equal(r.wrongLaneState.healthy, false); assert.equal(r.wrongLaneQuarantine.totalCount, 2);
    assert.equal(r.validRestore.ok, true); assert.equal(r.validRestore.registration?.ok, true); assert.equal(r.validRestore.registration?.registrationSource, 'block-store-restore-clearance-receipt');
    assert.equal(r.replayAfterValidRestore.ok, false); assert.equal(r.replayAfterValidRestore.disposition, 'rejected-cleared-quarantine-replay'); assert.equal(r.laneAfterReplay.healthy, true); assert.equal(r.quarantineAfterReplay.totalCount, 0);
    assert.equal(r.recoveryVerify.ok, true); assert.equal(r.cleanupAfter, true); assert.equal(r.locksAfterCleanup.heldCount, 0); assert.equal(r.locksAfterCleanup.pendingCount, 0); assert.equal(cleanupReap.afterKillCount, 0);
    for (const kind of ['block-store-lane:quarantine-clearance-receipt-persisted']) assert.ok(p.traceKinds.includes(kind), `phase1 missing ${kind}`);
    for (const kind of ['block-store-lane:quarantine-clearance-receipt-restore-rejected', 'block-store-lane:quarantine-clearance-receipt-restored', 'storage-lane:timed-out-quarantine-import-replay-rejected']) assert.ok(r.traceKinds.includes(kind), `phase2 missing ${kind}`);
    return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-restore-registration-gate-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that a persisted timeout-quarantine clearance receipt survives a clean profile restart but restore fails closed when registration rejects, so stale replay is blocked only after valid lane/provenance-bound restore.', observations: { persistPhase: p, restorePhase: r, profileReused: true, cleanupReap }, harness: { server: { port: server.port, requestCount: server.requests.length, requests: server.requests.slice(0, 30) }, profile: { path: profileDir, reused: true }, first: first.harness, second: second.harness }, claimsChecked: ['receipt persisted as OPFS content-addressed block survives clean browser/profile restart', 'wrong-lane restore rejects at registration and does not install clearance replay guard state', 'stale timeout quarantine import still backpressures after rejected restore', 'valid block-store restore carries restore provenance and rejects stale replay', 'later guarded OPFS write verifies and Web Locks drain'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior claim.', 'Receipt provenance/fingerprints are deterministic integrity bindings, not cryptographic attestation, tamper-proof storage, or security boundary.', 'Clean restart is not OPFS fsync durability, power-loss safety, crash safety, quota/eviction survival, automatic recovery, no-mutation-on-timeout, SLO, or production-readiness evidence.'] };
  } finally {
    await server.close().catch(() => null);
    await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 }).catch(() => null);
    await rm(profileDir, { recursive: true, force: true }).catch(() => null);
  }
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '28000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-clearance-restore-registration-gate-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser receipt restore registration gate proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_clearance_restore_registration_gate_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
