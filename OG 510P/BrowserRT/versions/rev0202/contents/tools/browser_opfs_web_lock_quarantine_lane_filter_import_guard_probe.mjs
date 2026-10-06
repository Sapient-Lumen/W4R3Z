#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-LANE-FILTER-IMPORT-GUARD-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const m = await import('/src/browserrt.mjs');
    const sched = await import('/src/storage-lane-scheduler.mjs');
    const bytesFromSeed = (seed, count) => { const out = new Uint8Array(count); const enc = new TextEncoder().encode(seed); out.set(enc.slice(0, Math.min(enc.length, out.length))); for (let i = enc.length; i < out.length; i += 1) out[i] = (i * 31 + 17) & 255; return out; };
    const opReplayKey = ({ lane, kind = 'put', operationEpoch, opId }) => operationEpoch ? 'operation:' + lane + ':' + kind + ':' + operationEpoch + ':' + opId : 'operation-legacy:' + lane + ':' + kind + ':' + opId;
    const makeRow = ({ opId, lane, epoch, label }) => Object.freeze({ opId, kind: 'put', lane, operationEpoch: epoch, operationReplayKey: opReplayKey({ lane, kind: 'put', operationEpoch: epoch, opId }), timeoutMs: 75, timedOutAtMs: 1710000000000, settledAtMs: 1710000000123, result: { digest: 'sha256:' + label, bytes: label.length, disposition: 'browser-synthetic-late-success' } });
    const withFingerprint = (ledger) => { const fp = sched.timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fp, reviewFingerprint: fp }); };
    const makeLedger = ({ rows, lane, reason }) => withFingerprint({ schema: 'brt.storageLane.timedOutOperationQuarantine.v1', reason, label: m.REVISION + '-browser-lane-filter-ledger', exportedAtMs: Date.now(), lane, counts: { total: rows.length, unsettled: 0, successful: rows.length, failed: 0 }, unsettledTimedOutOperations: [], successfulTimedOutOperations: rows, failedTimedOutOperations: [] });

    const rt = await m.boot({ storageLane: true, opfsAsyncBlockStoreProof: true, opfsWebLockQuarantineLaneFilterImportGuardProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: m.REVISION + '-lane-filter-import-raw-opfs', prefix: ${JSON.stringify(prefix)}, trace: rt.trace });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: m.REVISION + '-lane-filter-import-guard', store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, lockTimeoutMs: 1000, trace: rt.trace });
    await guard.cleanupForTest({ timeoutMs: 1000 });
    const makeAdapter = (label) => {
      const scheduler = rt.crossLaneScheduler({ label: label + ':scheduler', trace: rt.trace, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
      const adapter = rt.blockStoreLaneAdapter({ label, store: guard, scheduler, trace: rt.trace, lane: 'storage', defaultOperationTimeoutMs: 1000 });
      return { scheduler, adapter };
    };
    const storageRow = makeRow({ opId: 'same-visible-op', lane: 'storage', epoch: 'browser-epoch-storage-A', label: 'browser-storage-row' });
    const archiveRow = makeRow({ opId: 'archive-visible-op', lane: 'archive', epoch: 'browser-epoch-archive-A', label: 'browser-archive-row' });
    const archiveOnlyLedger = makeLedger({ rows: [archiveRow], lane: 'archive', reason: 'browser-archive-only-ledger' });
    const mixedLedger = makeLedger({ rows: [storageRow, archiveRow], lane: null, reason: 'browser-mixed-storage-archive-ledger' });

    const wrong = makeAdapter(m.REVISION + '-browser-lane-filter-wrong');
    const wrongLaneImport = wrong.adapter.importTimedOutOperationQuarantine(archiveOnlyLedger, { lane: 'storage', markUnhealthy: false, reason: 'browser-wrong-lane-no-match' });
    const wrongLaneHealth = wrong.scheduler.snapshotLane('storage');
    const wrongLaneQuarantine = wrong.adapter.timedOutOperationQuarantine('storage');

    const partialDefault = makeAdapter(m.REVISION + '-browser-lane-filter-partial-default');
    const partialDefaultImport = partialDefault.adapter.importTimedOutOperationQuarantine(mixedLedger, { lane: 'storage', markUnhealthy: false, reason: 'browser-mixed-lane-default-reject' });
    const partialDefaultHealth = partialDefault.scheduler.snapshotLane('storage');
    const partialDefaultQuarantine = partialDefault.adapter.timedOutOperationQuarantine('storage');

    const partialAllowed = makeAdapter(m.REVISION + '-browser-lane-filter-partial-allowed');
    const partialAllowedImport = partialAllowed.adapter.importTimedOutOperationQuarantine(mixedLedger, { lane: 'storage', markUnhealthy: false, allowPartialImport: true, reason: 'browser-mixed-lane-explicit-partial-import' });
    const partialAllowedHealth = partialAllowed.scheduler.snapshotLane('storage');
    const partialAllowedQuarantine = partialAllowed.adapter.timedOutOperationQuarantine('storage');
    const rejectedPayload = bytesFromSeed(m.REVISION + ':lane-filter-rejected-write', 2048);
    const rejectedHash = await m.digestBytesHex(rejectedPayload);
    const rejectedWrite = partialAllowed.adapter.schedulePut(rejectedPayload, { id: 'browser-lane-filter-rejected-write', label: 'should-not-mutate-while-imported-quarantine-active' });
    const rejectedPresent = await raw.has('sha256:' + rejectedHash);

    const review = partialAllowed.adapter.createTimedOutOperationQuarantineReview({ lane: 'storage', category: 'successful', opIds: [storageRow.opId], reviewer: 'rev0084-browser-lane-filter-probe', reviewToken: 'browser-lane-filter-storage-row-review', reason: 'browser-review-explicit-partial-import' });
    const clear = partialAllowed.adapter.clearTimedOutOperationQuarantine({ reviewManifest: review, requireReviewFingerprint: true, reason: 'browser-clear-explicit-partial-import' });
    const recovery = await partialAllowed.adapter.recoverWhenStoreSettled({ lane: 'storage', reason: 'browser-recover-after-explicit-partial-clear' });
    const recoveryPayload = bytesFromSeed(m.REVISION + ':lane-filter-import-guard-recovery-write', 4096);
    const recoveryPut = await guard.put(recoveryPayload, { label: 'lane-filter-import-guard-recovery-write' }, { timeoutMs: 1000 });
    const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
    const locksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const locksAfterCleanup = await guard.queryLocks();
    const trace = rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}', page: { location: location.href, crossOriginIsolated, isSecureContext, origin: location.origin }, capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, archiveOnlyLedger, mixedLedger, wrongLaneImport, wrongLaneHealth, wrongLaneQuarantine, partialDefaultImport, partialDefaultHealth, partialDefaultQuarantine, partialAllowedImport, partialAllowedHealth, partialAllowedQuarantine, rejectedWrite, rejectedPresent, review, clear, recovery, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanupAfter, locksAfterCleanup, traceKinds: trace.map((row) => row.kind), traceHighlights: trace.filter((event) => event.kind.includes('quarantine') || event.kind.includes('web-lock')).map((event) => ({ kind: event.kind, code: event.code ?? null, disposition: event.disposition ?? null, reason: event.reason ?? null, importedCount: event.importedCount ?? null, filteredOutCount: event.filteredOutCount ?? null })) });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-lane-filter-import-guard-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-lane-filter-import-guard';
  const lockName = options.lockName || `${REVISION}-quarantine-lane-filter-import-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 30000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath: '/browser-opfs-web-lock-quarantine-lane-filter-import-guard.html', pageTitle: 'BrowserRT OPFS Web Lock quarantine lane-filter import guard proof', allowedPrefixes: ['src/'], profilePrefix: 'browserrt-lane-filter-import-', stderrTerms: ['opfs', 'lock', 'quarantine'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true); assert.equal(result.capabilities.webLocks, true); assert.equal(result.capabilities.webLocksQuery, true);
  assert.equal(result.wrongLaneImport.ok, false); assert.equal(result.wrongLaneImport.disposition, 'rejected-lane-filter-empty-import'); assert.equal(result.wrongLaneHealth.healthy, true); assert.equal(result.wrongLaneQuarantine.totalCount, 0);
  assert.equal(result.partialDefaultImport.ok, false); assert.equal(result.partialDefaultImport.disposition, 'rejected-lane-filter-partial-import'); assert.equal(result.partialDefaultImport.importedCount, 1); assert.equal(result.partialDefaultImport.filteredOutCount, 1); assert.equal(result.partialDefaultHealth.healthy, true); assert.equal(result.partialDefaultQuarantine.totalCount, 0);
  assert.equal(result.partialAllowedImport.ok, true); assert.equal(result.partialAllowedImport.markUnhealthyForced, true); assert.equal(result.partialAllowedImport.importedCount, 1); assert.equal(result.partialAllowedImport.filteredOutCount, 1); assert.equal(result.partialAllowedHealth.healthy, false); assert.equal(result.partialAllowedQuarantine.successfulTimedOutOperationCount, 1);
  assert.equal(result.rejectedWrite.accepted, false); assert.equal(result.rejectedWrite.scheduler.disposition, 'rejected-lane-unhealthy'); assert.equal(result.rejectedWrite.scheduler.noMutation, true); assert.equal(result.rejectedPresent, false);
  assert.equal(result.clear.ok, true); assert.equal(result.clear.clearedCount, 1); assert.equal(result.recovery.recovered, true); assert.equal(result.recoveryVerify.ok, true);
  assert.equal(result.cleanupAfter, true); assert.equal(result.locksAfterCleanup.heldCount, 0); assert.equal(result.locksAfterCleanup.pendingCount, 0); assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['storage-lane:timed-out-quarantine-import-lane-filter-rejected', 'storage-lane:timed-out-quarantine-import-partial-allowed', 'storage-lane:timed-out-quarantine-import-backpressure-forced', 'coord:web-lock-acquired', 'coord:web-lock-released']) assert.ok(result.traceKinds.includes(kind), `missing trace ${kind}`);
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-lane-filter-import-guard-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), purpose: 'Managed Chromium proof that OPFS/Web Lock storage lanes reject wrong-lane and accidental partial timeout-quarantine import while allowing explicit partial import with backpressure and reviewed recovery.', observations: { ...result, harness }, claimsChecked: ['wrong-lane persisted quarantine restore cannot be treated as success', 'mixed-lane quarantine import rejects by default rather than silently dropping filtered rows', 'explicit partial import forces backpressure and rejects writes without mutation', 'reviewed scoped clear and explicit recovery permit a later guarded OPFS write'], nonClaims: ['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks claim.', 'Lane-filter import guard is not cryptographic attestation, tamper-proof storage, cancellation, rollback, no-mutation-on-timeout, durability, quota, eviction, SLO, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '30000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') }); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-quarantine-lane-filter-import-guard-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser lane-filter import guard proof is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[browser_opfs_web_lock_quarantine_lane_filter_import_guard_probe] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
