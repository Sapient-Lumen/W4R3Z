#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-QUARANTINE-RECEIPT-RESTORE-INTEGRITY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function pageExpression({ prefix, lockPrefix, lockName }) { return `(async () => {
  const m = await import(new URL('/src/browserrt.mjs', location.href).href);
  const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', quarantineReceiptRestoreIntegrityProof: true });
  const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-receipt-restore-integrity-raw-store', prefix: ${JSON.stringify(prefix)} });
  await raw.open();
  await raw.cleanupForTest();
  const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-receipt-restore-integrity-guard', lockTimeoutMs: 1000 });
  const mkScheduler = (label) => m.createCrossLaneScheduler({ label, lanes: [{ id:'storage', rank:70, capacity:1, quantum:4096, maxQueuedCost:8192 }, { id:'maintenance', rank:10, capacity:1, quantum:64, maxQueuedCost:128 }] });
  const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-receipt-restore-integrity-browser-adapter', store: guard, scheduler: mkScheduler('${REVISION}-receipt-restore-integrity-scheduler'), lane:'storage', defaultOperationTimeoutMs: 1000 });
  const withFingerprint = (ledger) => { const fp = m.timedOutQuarantineFingerprint(ledger); return Object.freeze({ ...ledger, quarantineFingerprint: fp, reviewFingerprint: fp }); };
  const now = Date.now();
  const success = Object.freeze({ opId: 'browser-restore-integrity-success', kind:'put', lane:'storage', operationEpoch:'${REVISION}:browser-restore-integrity-a', operationReplayKey:'operation:storage:put:${REVISION}:browser-restore-integrity-a:browser-restore-integrity-success', timeoutMs:25, timedOutAtMs:now, settledAtMs:now+1, result:{ digest:'sha256:browser-restore-integrity-success', bytes:64, disposition:'browser-late-success' } });
  const failure = Object.freeze({ opId: 'browser-restore-integrity-failure', kind:'put', lane:'storage', operationEpoch:'${REVISION}:browser-restore-integrity-b', operationReplayKey:'operation:storage:put:${REVISION}:browser-restore-integrity-b:browser-restore-integrity-failure', timeoutMs:25, timedOutAtMs:now+2, settledAtMs:now+3, error:{ name:'BrowserSyntheticLateFailure', message:'late failure', code:'BRT_BROWSER_SYNTHETIC_LATE_FAILURE' } });
  const ledger = withFingerprint({ schema:'brt.storageLane.timedOutOperationQuarantine.v1', lane:'storage', exportedAtMs:now+5, label:'${REVISION}-browser-restore-integrity-ledger', reason:'browser synthetic mixed ledger for receipt restore block integrity', counts:{ total:2, unsettled:0, successful:1, failed:1 }, unsettledTimedOutOperations:[], successfulTimedOutOperations:[success], failedTimedOutOperations:[failure] });
  const imported = adapter.importTimedOutOperationQuarantine(ledger, { lane:'storage', reason:'browser-import-before-restore-integrity', markUnhealthy:false });
  const review = adapter.createTimedOutOperationQuarantineReview({ lane:'storage', category:'all', allowLaneWide:true, reviewer:'${REVISION}-browser-probe', reviewToken:'browser-receipt-restore-integrity-review', reason:'browser-review-all-rows' });
  const clear = adapter.clearTimedOutOperationQuarantine({ reviewManifest: review, requireReviewFingerprint:true, reason:'browser-clear-for-receipt-restore-integrity' });
  const receipt = adapter.createTimedOutOperationQuarantineClearanceReceipt(clear, { reviewer:'${REVISION}-browser-probe', label:'browser-receipt-restore-integrity-valid' });
  const persisted = await adapter.persistTimedOutOperationQuarantineClearanceReceipt(receipt, { label:'browser-receipt-restore-integrity-block' });
  const hash = (persisted.ref && persisted.ref.hash) || (String(persisted.digest || '').startsWith('sha256:') ? String(persisted.digest).slice('sha256:'.length) : null);
  async function bucketForHash(create = true) {
    const root = await navigator.storage.getDirectory();
    let dir = root;
    for (const part of ${JSON.stringify(prefix)}.split('/').filter(Boolean)) dir = await dir.getDirectoryHandle(part, { create });
    dir = await dir.getDirectoryHandle(hash.slice(0, 2), { create });
    return await dir.getDirectoryHandle(hash.slice(2, 4), { create });
  }
  async function createWritableExclusive(file) { try { return await file.createWritable({ mode:'exclusive' }); } catch (error) { if (error?.name === 'TypeError') return await file.createWritable(); throw error; } }
  const corruptBytes = new TextEncoder().encode('${REVISION}:corrupt-clearance-receipt-block');
  const corruptDigest = 'sha256:' + await m.digestBytesHex(corruptBytes);
  const bucket = await bucketForHash(true);
  const file = await bucket.getFileHandle(hash + '.blk', { create:true });
  const writable = await createWritableExclusive(file);
  await writable.write(corruptBytes);
  await writable.close();
  const verifyCorrupt = await raw.verify(persisted.ref);
  const fresh = rt.blockStoreLaneAdapter({ label:'${REVISION}-receipt-restore-integrity-browser-fresh', store: guard, scheduler: mkScheduler('${REVISION}-receipt-restore-integrity-fresh-scheduler'), lane:'storage', defaultOperationTimeoutMs:1000 });
  const unverifiedRestore = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane:'storage', reason:'browser-reject-unverified-receipt-restore', verifyBeforeRestore:false });
  const rejectedRestore = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane:'storage', reason:'browser-reject-corrupt-receipt-block' });
  const repair = await guard.put(new TextEncoder().encode(JSON.stringify(receipt, null, 2) + '\\n'), { label:'browser-repair-receipt-block-after-corrupt-restore' }, { timeoutMs:1000 });
  const verifyAfterRepair = await raw.verify(persisted.ref);
  const restored = await fresh.restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore(persisted.ref, { lane:'storage', reason:'browser-restore-valid-repaired-receipt-block' });
  const staleReplay = fresh.importTimedOutOperationQuarantine(ledger, { lane:'storage', reason:'browser-stale-replay-after-restored-receipt', markUnhealthy:false });
  const recoveryPayload = new TextEncoder().encode('${REVISION}:browser-receipt-restore-integrity-recovery');
  const recoveryPut = await guard.put(recoveryPayload, { label:'browser-receipt-restore-integrity-recovery-put' }, { timeoutMs:1000 });
  const recoveryVerify = await raw.verify(recoveryPut.ref || recoveryPut);
  const locksBeforeCleanup = await guard.queryLocks();
  const cleanup = await guard.cleanupForTest({ timeoutMs:1000 });
  const locksAfterCleanup = await guard.queryLocks();
  const trace = rt.close();
  return JSON.stringify({ project:'BrowserRT', revision:m.REVISION, version:m.VERSION, taskId:'${TASK_ID}', page:{ location:location.href, crossOriginIsolated, isSecureContext, origin:location.origin }, capabilities:{ ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' }, imported, review, clear, receipt, persisted, hash, corruptDigest, verifyCorrupt, unverifiedRestore, rejectedRestore, repair, verifyAfterRepair, restored, staleReplay, recoveryPut, recoveryVerify, locksBeforeCleanup, cleanup, locksAfterCleanup, snapshot:fresh.snapshot(), traceKinds: trace.map((row)=>row.kind) });
})()`; }

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-quarantine-receipt-restore-integrity-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-quarantine-receipt-restore-integrity';
  const lockName = options.lockName || `${REVISION}-receipt-restore-integrity-lock`;
  const { result, harness } = await runManagedBrowserPage({ timeoutMs: options.timeoutMs || 30000, chromium: options.chromium, relaxPolicy: options.relaxPolicy, pagePath:'/browser-opfs-web-lock-quarantine-receipt-restore-integrity.html', pageTitle:'BrowserRT OPFS Web Lock quarantine receipt restore integrity proof', allowedPrefixes:['src/'], profilePrefix:'browserrt-receipt-restore-integrity-', stderrTerms:['opfs','lock','quarantine','receipt','restore','integrity'] }, async ({ evalJson, timeoutMs, profileDir }) => {
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName }), timeoutMs);
    const profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 300 });
    return { ...report, profileReap };
  });
  assert.equal(result.capabilities.opfs, true);
  assert.equal(result.capabilities.webLocks, true);
  assert.equal(result.imported.ok, true);
  assert.equal(result.verifyCorrupt.ok, false);
  assert.equal(result.verifyCorrupt.reason, 'checksum-mismatch');
  assert.equal(result.unverifiedRestore.ok, false);
  assert.equal(result.unverifiedRestore.disposition, 'rejected-unverified-clearance-receipt-restore');
  assert.equal(result.rejectedRestore.ok, false);
  assert.equal(result.rejectedRestore.disposition, 'rejected-clearance-receipt-block-integrity');
  assert.equal(result.rejectedRestore.blockVerify.ok, false);
  assert.equal(result.verifyAfterRepair.ok, true);
  assert.equal(result.restored.ok, true);
  assert.equal(result.restored.blockVerify.ok, true);
  assert.equal(result.staleReplay.ok, false);
  assert.equal(result.staleReplay.disposition, 'rejected-cleared-quarantine-replay');
  assert.equal(result.recoveryVerify.ok, true);
  assert.equal(result.cleanup, true);
  assert.equal(result.locksAfterCleanup.heldCount, 0);
  assert.equal(result.locksAfterCleanup.pendingCount, 0);
  assert.equal(result.profileReap.afterKillCount, 0);
  for (const kind of ['block-store-lane:quarantine-clearance-receipt-restore-unverified-rejected','block-store-lane:quarantine-clearance-receipt-restore-block-integrity-rejected','storage:opfs-block-corrupt','storage:opfs-block-repair','block-store-lane:quarantine-clearance-receipt-restored']) assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  return { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-quarantine-receipt-restore-integrity`, task_id:TASK_ID, status:'passed', generatedAt:new Date().toISOString(), durationMs:Math.round(performance.now()-started), purpose:'Managed Chromium proof that persisted timeout-quarantine clearance receipt restore verifies the OPFS content-addressed block before decoding/registering replay-guard state.', observations:{ ...result, harness }, claimsChecked:['unverified restore opt-out rejects unless explicitly unsafe','corrupt persisted OPFS clearance receipt block rejects before registration','repairing the content-addressed receipt block permits restore','restored valid receipt still rejects stale quarantine replay','later guarded OPFS write verifies'], nonClaims:['Managed Chromium/CDP only; no cross-browser OPFS/Web Locks claim.','Deliberate OPFS corruption injection; not organic power-loss, crash, quota, or eviction evidence.','Provider-backed block verification is not cryptographic attestation or tamper-proof storage.'] };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '30000')), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-policy-relaxation') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project:'BrowserRT', revision:REVISION, version:VERSION, schema:1, probe_id:`${REVISION}-browser-opfs-web-lock-quarantine-receipt-restore-integrity`, task_id:TASK_ID, status:'failed', generatedAt:new Date().toISOString(), error:{ name:error?.name||'Error', message:error?.message||String(error), stack:error?.stack }, nonClaims:['Failed browser restore-integrity proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive:true }); await writeFile(out, JSON.stringify(report,null,2)+'\n'); console.error(out); }
  console.error(error?.stack || error);
  process.exitCode = 1;
}
