#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, startProbeServer, evalJson, sleep } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-READ-TIMEOUT-NONPOISON-PROBE.json`;
const TASK_ID = 'browser:opfs-web-lock-read-timeout-nonpoison-proof';
const SW_ROUTE = '/browserrt-opfs-web-lock-read-timeout-nonpoison-sw.mjs';
const SW_SOURCE_PATH = 'tools/browserrt_opfs_web_lock_service_worker_holder.mjs';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function versionedWorkerSource(source, version) {
  return source.replace("'browserrt-service-worker-holder-v1'", JSON.stringify(version));
}

function lockQueryExpression(fullLockName) {
  return `(async () => {
    const raw = await navigator.locks.query();
    const keep = (row) => row && row.name === ${JSON.stringify(fullLockName)};
    const held = (raw.held || []).filter(keep).map((row) => ({ name: row.name, mode: row.mode, clientId: row.clientId ?? null }));
    const pending = (raw.pending || []).filter(keep).map((row) => ({ name: row.name, mode: row.mode, clientId: row.clientId ?? null }));
    return JSON.stringify({ held, pending, heldCount: held.length, pendingCount: pending.length, rawHeldCount: raw.held?.length ?? null, rawPendingCount: raw.pending?.length ?? null });
  })()`;
}

function registerExpression(swRoute) {
  return `(async () => {
    const reg = await navigator.serviceWorker.register(${JSON.stringify(swRoute)}, { type: 'module', scope: '/', updateViaCache: 'none' });
    await navigator.serviceWorker.ready;
    const deadline = Date.now() + 6000;
    let active = reg.active || null;
    while (Date.now() < deadline) {
      const fresh = await navigator.serviceWorker.getRegistration('/');
      active = fresh?.active || reg.active || null;
      if (active?.scriptURL?.includes(${JSON.stringify(swRoute)})) break;
      await new Promise((resolve) => setTimeout(resolve, 50));
    }
    const fresh = await navigator.serviceWorker.getRegistration('/');
    return JSON.stringify({ route: ${JSON.stringify(swRoute)}, scope: fresh?.scope || reg.scope, active: fresh?.active ? { scriptURL: fresh.active.scriptURL, state: fresh.active.state } : null, waiting: fresh?.waiting ? { scriptURL: fresh.waiting.scriptURL, state: fresh.waiting.state } : null, installing: fresh?.installing ? { scriptURL: fresh.installing.scriptURL, state: fresh.installing.state } : null, controller: navigator.serviceWorker.controller?.scriptURL || null });
  })()`;
}

function postToServiceWorkerExpression({ cmd, swRoute, prefix, lockPrefix, lockName, payload = null, holdId = null, opId = null, timeoutMs = 8000, lockTimeoutMs = 1200, reason = null }) {
  return `(async () => {
    let reg = await navigator.serviceWorker.getRegistration('/');
    if (!reg || !(reg.active || reg.waiting || reg.installing)) {
      await navigator.serviceWorker.ready;
      reg = await navigator.serviceWorker.getRegistration('/');
    }
    const deadline = Date.now() + 6000;
    let sw = null;
    while (Date.now() < deadline) {
      reg = await navigator.serviceWorker.getRegistration('/');
      const candidates = [reg?.active, reg?.waiting, reg?.installing].filter(Boolean);
      sw = candidates.find((candidate) => candidate.scriptURL.includes(${JSON.stringify(swRoute)})) || candidates[0] || null;
      if (sw && sw.state !== 'redundant') break;
      await new Promise((resolve) => setTimeout(resolve, 50));
    }
    if (!sw) throw new Error('no service worker available for postMessage');
    const msg = await new Promise((resolve, reject) => {
      const ch = new MessageChannel();
      const timer = setTimeout(() => reject(new Error('timed out waiting for service-worker response')), ${JSON.stringify(timeoutMs)});
      ch.port1.onmessage = (event) => { clearTimeout(timer); resolve(event.data); };
      sw.postMessage({ cmd: ${JSON.stringify(cmd)}, holdId: ${JSON.stringify(holdId)}, opId: ${JSON.stringify(opId)}, prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, payload: ${JSON.stringify(payload)}, lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)}, reason: ${JSON.stringify(reason)}, timeoutMs: ${JSON.stringify(timeoutMs)} }, [ch.port2]);
    });
    return JSON.stringify({ route: ${JSON.stringify(swRoute)}, registration: { scope: reg?.scope || null, active: reg?.active ? { scriptURL: reg.active.scriptURL, state: reg.active.state } : null }, worker: { scriptURL: sw.scriptURL, state: sw.state }, msg });
  })()`;
}

function unregisterAllExpression() {
  return `(async () => {
    const regs = await navigator.serviceWorker.getRegistrations();
    const rows = [];
    for (const reg of regs) {
      const scriptURL = reg.active?.scriptURL || reg.waiting?.scriptURL || reg.installing?.scriptURL || '';
      if (scriptURL.includes('browserrt-opfs-web-lock-read-timeout-nonpoison') || scriptURL.includes('browserrt-opfs-web-lock-service-worker')) {
        rows.push({ scope: reg.scope, scriptURL, unregistered: await reg.unregister() });
      }
    }
    return JSON.stringify({ count: rows.length, rows });
  })()`;
}

function cleanupExpression({ prefix, lockPrefix, lockName, label = 'cleanup' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockReadTimeoutNonpoisonProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`read-timeout-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`read-timeout-${label}-guard`)}, lockTimeoutMs: 1500 });
    const before = await guard.queryLocks();
    const cleanup = await guard.cleanupForTest({ timeoutMs: 1500 });
    const settled = await guard.waitForSettled({ timeoutMs: 1500, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, cleanup, settled, after, traceKinds });
  })()`;
}

function pageReadTimeoutLaneExpression({ prefix, lockPrefix, lockName, ref }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockReadTimeoutNonpoisonProof: true, phase: 'read-timeout-lane' });
    const store = rt.opfsAsyncBlockStore({ name: 'read-timeout-page-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'read-timeout-page-guard', lockTimeoutMs: 90 });
    const scheduler = rt.crossLaneScheduler({ label: 'read-timeout-nonpoison-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const adapter = rt.blockStoreLaneAdapter({ label: 'read-timeout-nonpoison-adapter', store: guard, scheduler, lane: 'storage' });
    const beforeLocks = await guard.queryLocks();
    const accepted = adapter.scheduleVerify(${JSON.stringify(ref)}, { id: 'held-exclusive-shared-verify-timeout', priority: 'user-visible' });
    await new Promise((resolve) => setTimeout(resolve, 20));
    const duringLocks = await guard.queryLocks();
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === 'held-exclusive-shared-verify-timeout') || null;
    const snapshot = adapter.snapshot();
    const lane = snapshot.executor.scheduler.lanes.find((row) => row.id === 'storage') || null;
    const afterLocks = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ accepted, duringLocks, beforeLocks, drain, result, snapshot, lane, afterLocks, traceKinds });
  })()`;
}

function pageRecoveryWriteExpression({ prefix, lockPrefix, lockName, ref, payload }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockReadTimeoutNonpoisonProof: true, phase: 'recovery-write' });
    const store = rt.opfsAsyncBlockStore({ name: 'read-timeout-recovery-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'read-timeout-recovery-guard', lockTimeoutMs: 1500 });
    const scheduler = rt.crossLaneScheduler({ label: 'read-timeout-recovery-scheduler', lanes: [ { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 } ] });
    const adapter = rt.blockStoreLaneAdapter({ label: 'read-timeout-recovery-adapter', store: guard, scheduler, lane: 'storage' });
    const settledBefore = await guard.waitForSettled({ timeoutMs: 1500, intervalMs: 20 });
    const holderVerify = await guard.verify(${JSON.stringify(ref)}, { timeoutMs: 1500 });
    const accepted = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(payload)}), { id: 'write-after-read-timeout', label: 'write-after-read-timeout', priority: 'user-visible' });
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === 'write-after-read-timeout') || null;
    const writtenVerify = result?.ok ? await guard.verify(result.result.ref, { timeoutMs: 1500 }) : null;
    const settledAfter = await guard.waitForSettled({ timeoutMs: 1500, intervalMs: 20 });
    const snapshot = adapter.snapshot();
    const lane = snapshot.executor.scheduler.lanes.find((row) => row.id === 'storage') || null;
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ settledBefore, holderVerify, accepted, drain, result, writtenVerify, settledAfter, snapshot, lane, traceKinds });
  })()`;
}

export async function runProbe({ chromium = null } = {}) {
  const started = performance.now();
  const swSource = versionedWorkerSource(await readFile(SW_SOURCE_PATH, 'utf8'), `${REVISION}-read-timeout-nonpoison-sw`);
  const server = await startProbeServer({
    root: process.cwd(),
    pagePath: '/read-timeout-nonpoison.html',
    pageTitle: 'BrowserRT OPFS Web Lock read-timeout nonpoison proof',
    body: '<!doctype html><meta charset="utf-8"><title>BrowserRT read timeout nonpoison</title><body>BrowserRT read timeout nonpoison</body>',
    allowedPrefixes: ['src/'],
    routes: { [SW_ROUTE]: { body: swSource, contentType: 'text/javascript; charset=utf-8' } }
  });
  const prefix = `browserrt/${REVISION}/opfs-web-lock-read-timeout-nonpoison-proof/${Date.now()}`;
  const lockPrefix = `browserrt:${REVISION}:opfs-web-lock-read-timeout-nonpoison`;
  const lockName = 'guarded-read-timeout-nonpoison-lock';
  const fullLockName = `${lockPrefix}:${lockName}`;
  let browserReport;
  try {
    browserReport = await runManagedBrowserPage({ chromium, server, timeoutMs: 18000, stderrTerms: ['service worker', 'WebLock', 'OPFS', 'Quota', 'error'] }, async ({ cdp, timeoutMs }) => {
      const pageSummary = await evalJson(cdp, 'JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, capabilities: { serviceWorker: "serviceWorker" in navigator, opfs: typeof navigator.storage?.getDirectory === "function", webLocks: typeof navigator.locks?.request === "function", webLocksQuery: typeof navigator.locks?.query === "function", abortController: typeof AbortController === "function" } })', timeoutMs);
      assert.equal(pageSummary.capabilities.serviceWorker, true, 'Service Worker unavailable');
      assert.equal(pageSummary.capabilities.webLocks, true, 'Web Locks unavailable');
      assert.equal(pageSummary.capabilities.webLocksQuery, true, 'Web Locks query unavailable');
      assert.equal(pageSummary.capabilities.opfs, true, 'OPFS unavailable');
      const preUnregister = await evalJson(cdp, unregisterAllExpression(), timeoutMs);
      const preCleanup = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'pre-cleanup' }), timeoutMs);
      const registration = await evalJson(cdp, registerExpression(SW_ROUTE), timeoutMs);
      const hold = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'hold', swRoute: SW_ROUTE, holdId: 'read-timeout-holder', prefix, lockPrefix, lockName, payload: 'service-worker-holder-for-read-timeout-nonpoison', lockTimeoutMs: 1200 }), timeoutMs);
      assert.equal(hold.msg?.ok, true, 'Service Worker hold command failed');
      assert.equal(hold.msg?.event, 'holding', 'Service Worker did not report holding');
      await sleep(100);
      const locksWhileHeld = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const readTimeout = await evalJson(cdp, pageReadTimeoutLaneExpression({ prefix, lockPrefix, lockName, ref: hold.msg.put.ref }), timeoutMs);
      const locksAfterReadTimeout = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const release = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'release', swRoute: SW_ROUTE, holdId: 'read-timeout-holder', prefix, lockPrefix, lockName, reason: 'read-timeout-nonpoison-proof-release', timeoutMs: 5000 }), timeoutMs);
      await sleep(100);
      const locksAfterRelease = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const recoveryWrite = await evalJson(cdp, pageRecoveryWriteExpression({ prefix, lockPrefix, lockName, ref: hold.msg.put.ref, payload: 'page-write-after-read-timeout-nonpoison' }), timeoutMs);
      const cleanup = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'post-cleanup' }), timeoutMs);
      const unregister = await evalJson(cdp, unregisterAllExpression(), timeoutMs);
      const finalLocks = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      return { pageSummary, preUnregister, preCleanup, registration, hold, locksWhileHeld, readTimeout, locksAfterReadTimeout, release, locksAfterRelease, recoveryWrite, cleanup, unregister, finalLocks };
    });
  } finally {
    await server.close();
  }

  const result = browserReport.result;
  assert.equal(result.locksWhileHeld.heldCount, 1, 'exclusive holder lock should be held');
  assert.equal(result.readTimeout.accepted.accepted, true, 'read verify should be admitted');
  assert.equal(result.readTimeout.result?.ok, false, 'read verify should fail behind held exclusive lock');
  assert.equal(result.readTimeout.result?.error?.code, 'BRT_WEB_LOCK_TIMEOUT', 'read verify should fail as BRT_WEB_LOCK_TIMEOUT');
  assert.equal(result.readTimeout.lane?.healthy, true, 'read-only Web Lock timeout should not mark storage lane unhealthy');
  assert.equal(result.readTimeout.snapshot.executor.stats.laneHealthFailures, 0, 'read-only timeout must not increment laneHealthFailures');
  assert.equal(result.locksAfterReadTimeout.heldCount, 1, 'exclusive holder should still own lock after read timeout');
  assert.equal(result.release.msg?.ok, true, 'release command should complete');
  assert.equal(result.locksAfterRelease.heldCount, 0, 'lock should drain after release');
  assert.equal(result.locksAfterRelease.pendingCount, 0, 'pending locks should drain after release');
  assert.equal(result.recoveryWrite.holderVerify?.ok, true, 'holder-written block should verify after release');
  assert.equal(result.recoveryWrite.accepted.accepted, true, 'follow-on write should be accepted after read-only timeout and release');
  assert.equal(result.recoveryWrite.result?.ok, true, 'follow-on write should complete after read-only timeout and release');
  assert.equal(result.recoveryWrite.writtenVerify?.ok, true, 'follow-on write should verify');
  assert.equal(result.recoveryWrite.lane?.healthy, true, 'storage lane should remain healthy after recovery write');
  assert.equal(result.cleanup.settled.ok, true, 'cleanup should settle locks');
  assert.equal(result.finalLocks.heldCount, 0, 'final held locks should be zero');
  assert.equal(result.finalLocks.pendingCount, 0, 'final pending locks should be zero');

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-read-timeout-nonpoison-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Managed Chromium proof that a shared/read-only guarded OPFS verify queued behind a Service Worker-held exclusive Web Lock times out visibly without poisoning the storage lane; after release, the holder block and a later page write verify.',
    observations: { prefix, lockPrefix, lockName, fullLockName, result, harness: browserReport.harness },
    claimsChecked: [
      'a Service Worker can hold BrowserRT\'s guarded OPFS mutation lock while a page-side shared verify queues behind it',
      'the queued shared/read-only verify times out as BRT_WEB_LOCK_TIMEOUT',
      'the storage lane remains healthy and laneHealthFailures stays zero after the read-only timeout',
      'the Service Worker holder still owns the exclusive lock until explicit release',
      'after release, the holder-written OPFS block verifies and a later page-side guarded write completes and verifies'
    ],
    nonClaims: [
      'Managed Chromium proof only; no cross-browser Web Locks, Service Worker, or OPFS claim.',
      'No fairness, starvation-freedom, mobile/background, fetch/push/offline, automatic recovery, durability, fsync, quota, eviction, or persistent-retention claim.',
      'Mutating Web Lock timeout backpressure remains covered by separate storage-lane and Service Worker lifecycle proofs.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const chromium = argValue(argv, '--chromium', null);
try {
  const report = await runProbe({ chromium });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-read-timeout-nonpoison-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, stack: error?.stack }, nonClaims: ['Failed managed-Chromium read-timeout nonpoison probe is not a cross-browser or production-readiness claim.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_web_lock_read_timeout_nonpoison_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
