#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-operation-timeout-boundary-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-OPERATION-TIMEOUT-BOUNDARY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }) {
  return `(async () => {
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const bytesFromSeed = (seed, count) => {
      const out = new Uint8Array(count);
      const enc = new TextEncoder().encode(seed);
      out.set(enc.slice(0, Math.min(enc.length, out.length)));
      for (let i = enc.length; i < out.length; i += 1) out[i] = (23 + i * 19 + (i >>> 3)) & 255;
      return out;
    };
    const moduleUrl = new URL('/src/browserrt.mjs', location.href).href;
    const m = await import(moduleUrl);
    const rt = await m.boot({ telemetry: 'browser-cdp', proof: '${REVISION}', opfsWebLockOperationTimeoutBoundaryProof: true });
    const raw = rt.opfsAsyncBlockStore({ name: '${REVISION}-opfs-web-lock-operation-timeout-raw', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store: raw, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: '${REVISION}-operation-timeout-guard', lockTimeoutMs: 0 });
    const cleanupBefore = await guard.cleanupForTest({ timeoutMs: 1000 });
    let releaseProvider;
    const providerRelease = new Promise((resolve) => { releaseProvider = resolve; });
    const providerEvents = [];
    let providerPromise = null;
    let providerPut = null;
    const controlledStore = {
      name: '${REVISION}-controlled-opfs-web-lock-slow-store',
      provider: 'web-lock-guarded:opfs-async-block-store-v0:controlled-slow-provider',
      get prefix() { return raw.prefix; },
      async put(payload, fields = {}) {
        providerPromise = guard.withExclusive(async () => {
          providerEvents.push({ event: 'lock-acquired', at: performance.now() });
          const put = await raw.put(payload, { label: fields.label || 'controlled-opfs-write-before-timeout' });
          const verify = await raw.verify(put.ref);
          providerPut = put;
          providerEvents.push({ event: 'opfs-written-before-release', at: performance.now(), digest: put.digest, verifyOk: verify.ok });
          await providerRelease;
          providerEvents.push({ event: 'provider-released', at: performance.now(), digest: put.digest });
          return put;
        }, { op: 'operation-timeout-controlled-provider', role: 'browser-page', intentionallyHeldAfterWrite: true }, { timeoutMs: 0 });
        return await providerPromise;
      },
      async get(ref) { return await guard.get(ref, { timeoutMs: 1000 }); },
      async has(ref) { return await guard.has(ref, { timeoutMs: 1000 }); },
      async verify(ref) { return await guard.verify(ref, { timeoutMs: 1000 }); },
      async delete(ref) { return await guard.delete(ref, { timeoutMs: 1000 }); },
      async estimate() { return await guard.estimate({ timeoutMs: 1000 }); },
      async cleanupForTest() { return await guard.cleanupForTest({ timeoutMs: 1000 }); },
      async queryLocks() { return await guard.queryLocks(); },
      async waitForSettled(options = {}) { return await guard.waitForSettled(options); },
      snapshot() { const snap = guard.snapshot(); return Object.freeze({ ...snap, name: this.name, provider: this.provider, controlledProviderEvents: providerEvents.slice(), providerPut: providerPut ? { digest: providerPut.digest, bytes: providerPut.bytes, path: providerPut.path } : null }); }
    };
    const scheduler = rt.crossLaneScheduler({
      label: '${REVISION}-operation-timeout-browser-scheduler',
      lanes: [
        { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
        { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
      ]
    });
    const adapter = rt.blockStoreLaneAdapter({ label: '${REVISION}-operation-timeout-browser-adapter', store: controlledStore, scheduler, lane: 'storage', defaultOperationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const payload = bytesFromSeed('BrowserRT ${REVISION} browser OPFS Web Lock operation timeout payload', ${JSON.stringify(payloadBytes)});
    const timeoutHash = await m.digestBytesHex(payload);
    const timeoutDigest = 'sha256:' + timeoutHash;
    const scheduled = adapter.schedulePut(payload, { id: '${REVISION}-browser-opfs-lock-operation-timeout-put', priority: 'user-visible', label: 'browser-opfs-lock-operation-timeout', operationTimeoutMs: ${JSON.stringify(operationTimeoutMs)} });
    const drain = await adapter.drain({ maxSteps: 2 });
    const timeoutResult = drain.results.find((row) => row.opId === '${REVISION}-browser-opfs-lock-operation-timeout-put') || null;
    const snapshotAfterTimeout = adapter.snapshot();
    const storageLaneAfterTimeout = snapshotAfterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
    const providerWroteBeforeTimeout = providerEvents.some((row) => row.event === 'opfs-written-before-release');
    const timeoutBlockPresentBeforeRelease = await raw.has(timeoutDigest);
    const adapterResultAfterTimeout = adapter.result('${REVISION}-browser-opfs-lock-operation-timeout-put') || null;
    const locksWhileProviderHeld = await guard.queryLocks();
    const rejectedWhileUnhealthy = adapter.schedulePut(bytesFromSeed('BrowserRT ${REVISION} reject while operation timeout unhealthy', 4096), { id: '${REVISION}-operation-timeout-reject-while-unhealthy', label: 'reject-while-unhealthy' });
    const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 80, intervalMs: 10, reason: 'operation-timeout-provider-still-held' });
    releaseProvider('release-after-operation-timeout-observed');
    const providerSettled = await Promise.race([
      providerPromise.then((value) => ({ settled: true, ok: true, digest: value.digest, bytes: value.bytes })).catch((error) => ({ settled: true, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null } })),
      sleep(1500).then(() => ({ settled: false }))
    ]);
    const locksAfterRelease = await guard.queryLocks();
    const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 1000, intervalMs: 20, reason: 'operation-timeout-provider-released' });
    const timeoutVerifyAfterRelease = await raw.verify(timeoutDigest);
    const recoveryPayload = bytesFromSeed('BrowserRT ${REVISION} browser operation timeout recovery write', 8192);
    const recoveredSchedule = adapter.schedulePut(recoveryPayload, { id: '${REVISION}-operation-timeout-recovered-put', priority: 'user-visible', label: 'recovered-after-operation-timeout', operationTimeoutMs: 1000 });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === '${REVISION}-operation-timeout-recovered-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await raw.verify(recoveredResult.result.ref) : null;
    const finalLocksBeforeCleanup = await guard.queryLocks();
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const finalLocks = await guard.queryLocks();
    const finalSnapshot = adapter.snapshot();
    const trace = rt.close();
    return JSON.stringify({
      project: 'BrowserRT', revision: m.REVISION, version: m.VERSION, taskId: '${TASK_ID}',
      page: { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, origin: location.origin },
      capabilities: { ...m.detectCapabilities(globalThis), webLocksQuery: typeof navigator.locks?.query === 'function' },
      prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, operationTimeoutMs: ${JSON.stringify(operationTimeoutMs)}, payloadBytes: payload.byteLength,
      cleanupBefore,
      scheduled, timeoutResult, snapshotAfterTimeout, storageLaneAfterTimeout,
      timeoutDigest, providerWroteBeforeTimeout, timeoutBlockPresentBeforeRelease, adapterResultAfterTimeout,
      locksWhileProviderHeld, rejectedWhileUnhealthy, blockedRecovery,
      providerSettled, locksAfterRelease, settledRecovery, timeoutVerifyAfterRelease,
      recoveredSchedule, recoveredResult, recoveredVerify,
      finalLocksBeforeCleanup, cleanupAfter, finalLocks, finalSnapshot, providerEvents,
      traceKinds: trace.map((event) => event.kind),
      normalizedTrace: trace.map((event) => ({ kind: event.kind, opId: event.opId, op: event.op, lane: event.lane, code: event.code, reason: event.reason, disposition: event.disposition, timeoutMs: event.timeoutMs, cancellation: event.cancellation, name: event.name, mode: event.mode, heldCount: event.heldCount, pendingCount: event.pendingCount })).filter((event) => event.kind)
    });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-operation-timeout-boundary-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-operation-timeout-boundary';
  const lockName = options.lockName || `${REVISION}-operation-timeout-mutation-lock`;
  const operationTimeoutMs = Number(options.operationTimeoutMs || 500);
  const payloadBytes = Number(options.payloadBytes || 16 * 1024);
  const { result, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs || 18000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/browser-opfs-web-lock-operation-timeout-boundary.html',
    pageTitle: 'BrowserRT OPFS Web Lock operation timeout boundary proof',
    allowedPrefixes: ['src/'],
    profilePrefix: 'browserrt-opfs-web-lock-operation-timeout-',
    stderrTerms: ['opfs', 'lock', 'timeout', 'storage']
  }, async ({ evalJson, timeoutMs, mark }) => {
    const evalStart = performance.now();
    const report = await evalJson(pageExpression({ prefix, lockPrefix, lockName, operationTimeoutMs, payloadBytes }), timeoutMs);
    mark('browser-opfs-web-lock-operation-timeout-boundary-eval', evalStart);
    return report;
  });

  assert.equal(result.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(result.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(result.capabilities.webLocksQuery, true, 'Web Locks query must be available');
  assert.equal(result.scheduled.accepted, true, 'timed operation should schedule');
  assert.equal(result.timeoutResult?.ok, false, 'timed operation should fail closed');
  assert.equal(result.timeoutResult?.error?.code, 'BRT_STORAGE_OPERATION_TIMEOUT', 'timeout code should classify storage operation timeout');
  assert.equal(result.snapshotAfterTimeout.executor.stats.operationTimeouts, 1, 'executor should count operation timeout');
  assert.equal(result.storageLaneAfterTimeout.healthy, false, 'storage lane should be unhealthy after operation timeout');
  assert.equal(result.storageLaneAfterTimeout.healthReason, 'BRT_STORAGE_OPERATION_TIMEOUT');
  assert.equal(result.providerWroteBeforeTimeout, true, 'provider should have reached real OPFS write before timing out');
  assert.equal(result.timeoutBlockPresentBeforeRelease, true, 'operation timeout is not a provider cancellation/no-mutation guarantee');
  assert.equal(result.adapterResultAfterTimeout, null, 'timed-out operation should not publish a successful adapter result');
  assert.equal(result.locksWhileProviderHeld.heldCount, 1, 'guarded Web Lock should remain held after scheduler timeout until provider releases');
  assert.equal(result.rejectedWhileUnhealthy.accepted, false, 'follow-on write should reject while lane unhealthy');
  assert.equal(result.rejectedWhileUnhealthy.scheduler.disposition, 'rejected-lane-unhealthy');
  assert.equal(result.rejectedWhileUnhealthy.scheduler.noMutation, true);
  assert.equal(result.blockedRecovery.recovered, false, 'settled recovery should block while provider lock remains held');
  assert.equal(result.blockedRecovery.reason, 'store-coordination-still-contended');
  assert.equal(result.providerSettled.settled, true, 'provider promise should settle after explicit release');
  assert.equal(result.providerSettled.ok, true, 'provider should eventually resolve after release');
  assert.equal(result.locksAfterRelease.heldCount, 0, 'lock should drain after provider release');
  assert.equal(result.settledRecovery.recovered, true, 'settled recovery should reopen lane after lock drains');
  assert.equal(result.timeoutVerifyAfterRelease.ok, true, 'OPFS block written before timeout should verify after release');
  assert.equal(result.recoveredSchedule.accepted, true, 'recovery write should schedule after lane recovery');
  assert.equal(result.recoveredResult?.ok, true, 'recovery write should complete');
  assert.equal(result.recoveredVerify?.ok, true, 'recovery block should verify');
  assert.equal(result.cleanupAfter, true, 'cleanup should delete proof namespace');
  assert.equal(result.finalLocks.heldCount, 0, 'final held lock count should be zero');
  assert.equal(result.finalLocks.pendingCount, 0, 'final pending lock count should be zero');
  for (const kind of ['storage-lane:operation-timeout', 'storage-lane:provider-unhealthy', 'block-store-lane:recover-settled-blocked', 'block-store-lane:recover-settled', 'coord:web-lock-acquired', 'coord:web-lock-released']) {
    assert.ok(result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-operation-timeout-boundary-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Managed Chromium proof that a dispatched storage-lane operation can time out after acquiring a BrowserRT guarded Web Lock and writing a real OPFS block: the lane becomes unhealthy, follow-on writes reject without queue mutation, recovery blocks while the Web Lock is still held, then explicit release/settled recovery permits later writes. It deliberately preserves the non-claim that operation timeout is not provider cancellation.',
    observations: { ...result, harness },
    claimsChecked: [
      'Storage-lane operation timeout works in managed Chromium with a real OPFS/Web Lock guarded provider',
      'BRT_STORAGE_OPERATION_TIMEOUT marks the storage lane unhealthy and does not publish a successful adapter result',
      'follow-on writes reject without queue mutation while the storage lane is unhealthy',
      'recoverWhenStoreSettled refuses to reopen the lane while the guarded Web Lock remains held',
      'explicit provider release drains the lock and explicit settled recovery reopens the lane',
      'real OPFS data written before the operation timeout verifies, proving timeout is not a cancellation/no-mutation guarantee'
    ],
    nonClaims: [
      'Managed Chromium/CDP browser proof only; no cross-browser OPFS/Web Locks behavior claim.',
      'Operation timeout is not cancellation, rollback, no-mutation, exactly-once, or provider interruption evidence.',
      'No automatic recovery, fairness, starvation-freedom, service-worker lifecycle, OPFS durability, quota, eviction, fsync, persistent-retention, throughput, latency, SLO, or production-readiness claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', '18000')) });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-operation-timeout-boundary-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed browser operation-timeout proof is not silently skipped.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_operation_timeout_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
