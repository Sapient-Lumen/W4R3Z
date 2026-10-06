#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, startProbeServer, evalJson, sleep, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-FETCH-LIFECYCLE-PROBE.json`;
const TASK_ID = 'browser:opfs-web-lock-service-worker-fetch-lifecycle-proof';
const SW_ROUTE = '/browserrt-opfs-web-lock-service-worker-fetch-lifecycle.mjs';
const SW_SOURCE_PATH = 'tools/browserrt_opfs_web_lock_service_worker_holder.mjs';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function errRecord(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail || null, stack: error?.stack || null };
}

function versionedWorkerSource(source, version) {
  return source.replace("'browserrt-service-worker-holder-v1'", JSON.stringify(version));
}

async function waitFor(cdp, expression, predicate, { timeoutMs = 5000, intervalMs = 50, label = 'condition' } = {}) {
  const deadline = Date.now() + timeoutMs;
  let last = null;
  while (Date.now() < deadline) {
    last = await evalJson(cdp, expression, Math.min(1000, timeoutMs));
    if (predicate(last)) return last;
    await sleep(intervalMs);
  }
  throw new Error(`Timed out waiting for ${label}; last=${JSON.stringify(last).slice(0, 2000)}`);
}

function pageSummaryExpression() {
  return `JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, capabilities: { serviceWorker: 'serviceWorker' in navigator, opfs: typeof navigator.storage?.getDirectory === 'function', webLocks: typeof navigator.locks?.request === 'function', webLocksQuery: typeof navigator.locks?.query === 'function', abortController: typeof AbortController === 'function', fetch: typeof fetch === 'function' } })`;
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

function unregisterAllExpression() {
  return `(async () => {
    const regs = await navigator.serviceWorker.getRegistrations();
    const rows = [];
    for (const reg of regs) {
      const scriptURL = reg.active?.scriptURL || reg.waiting?.scriptURL || reg.installing?.scriptURL || '';
      if (scriptURL.includes('browserrt-opfs-web-lock-service-worker')) rows.push({ scope: reg.scope, scriptURL, unregistered: await reg.unregister() });
    }
    return JSON.stringify({ count: rows.length, rows });
  })()`;
}

function registerExpression(swRoute, expectedVersion) {
  return `(async () => {
    const reg = await navigator.serviceWorker.register(${JSON.stringify(swRoute)}, { type: 'module', scope: '/', updateViaCache: 'none' });
    await navigator.serviceWorker.ready;
    if (!navigator.serviceWorker.controller) {
      await new Promise((resolve) => {
        const timer = setTimeout(resolve, 2500);
        navigator.serviceWorker.addEventListener('controllerchange', () => { clearTimeout(timer); resolve(); }, { once: true });
      });
    }
    const deadline = Date.now() + 6000;
    let fresh = null;
    while (Date.now() < deadline) {
      fresh = await navigator.serviceWorker.getRegistration('/');
      if (fresh?.active?.scriptURL?.includes(${JSON.stringify(swRoute)}) && navigator.serviceWorker.controller?.scriptURL?.includes(${JSON.stringify(swRoute)})) break;
      await new Promise((resolve) => setTimeout(resolve, 50));
    }
    return JSON.stringify({ expectedVersion: ${JSON.stringify(expectedVersion)}, route: ${JSON.stringify(swRoute)}, scope: fresh?.scope || reg.scope, active: fresh?.active ? { scriptURL: fresh.active.scriptURL, state: fresh.active.state } : null, waiting: fresh?.waiting ? { scriptURL: fresh.waiting.scriptURL, state: fresh.waiting.state } : null, installing: fresh?.installing ? { scriptURL: fresh.installing.scriptURL, state: fresh.installing.state } : null, controller: navigator.serviceWorker.controller?.scriptURL || null });
  })()`;
}

function cleanupExpression({ prefix, lockPrefix, lockName, label = 'cleanup' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerFetchLifecycleProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-fetch-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-fetch-${label}-guard`)}, lockTimeoutMs: 1200 });
    const before = await guard.queryLocks();
    const cleanup = await guard.cleanupForTest({ timeoutMs: 1200 });
    const settled = await guard.waitForSettled({ timeoutMs: 1200, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, cleanup, settled, after, traceKinds });
  })()`;
}

function digestExpression(payload) {
  return `(async () => {
    const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
    const hash = await crypto.subtle.digest('SHA-256', bytes);
    const hex = Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, '0')).join('');
    return JSON.stringify({ digest: 'sha256:' + hex, bytes: bytes.byteLength });
  })()`;
}

function startFetchHolderExpression({ prefix, lockPrefix, lockName, payload, opId, holdMs = 1800 }) {
  const params = new URLSearchParams({ prefix, lockPrefix, lockName, payload, opId, holdMs: String(holdMs), lockTimeoutMs: '0' }).toString();
  const path = `/browserrt-sw-fetch-lifecycle?${params}`;
  return `(async () => {
    window.__brtFetchLifecycleResult = null;
    window.__brtFetchLifecyclePromise = fetch(${JSON.stringify(path)}, { cache: 'no-store' })
      .then(async (response) => ({ ok: response.ok, status: response.status, header: response.headers.get('x-browserrt-service-worker-fetch'), body: await response.json() }))
      .then((value) => { window.__brtFetchLifecycleResult = value; return value; })
      .catch((error) => { const value = { ok: false, status: 0, error: { name: error?.name || 'Error', message: error?.message || String(error) } }; window.__brtFetchLifecycleResult = value; return value; });
    return JSON.stringify({ started: true, path: ${JSON.stringify(path)}, controlledBy: navigator.serviceWorker.controller?.scriptURL || null });
  })()`;
}

function awaitFetchHolderExpression() {
  return `(async () => {
    if (!window.__brtFetchLifecyclePromise) return JSON.stringify({ ok: false, error: { message: 'fetch lifecycle promise not started' } });
    const result = await window.__brtFetchLifecyclePromise;
    return JSON.stringify(result);
  })()`;
}

function fetchStatusExpression() {
  return `JSON.stringify({ started: Boolean(window.__brtFetchLifecyclePromise), settled: Boolean(window.__brtFetchLifecycleResult), result: window.__brtFetchLifecycleResult || null })`;
}

function pageTimeoutBehindFetchExpression({ prefix, lockPrefix, lockName, payload, label = 'page-timeout-behind-service-worker-fetch', lockTimeoutMs = 450 }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerFetchLifecycleProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-fetch-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-fetch-${label}-guard`)}, lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} });
    const scheduler = rt.crossLaneScheduler({ label: ${JSON.stringify(`sw-fetch-${label}-scheduler`)}, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = rt.blockStoreLaneAdapter({ label: ${JSON.stringify(`sw-fetch-${label}-adapter`)}, store: guard, scheduler, lane: 'storage' });
    const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
    const hash = await crypto.subtle.digest('SHA-256', bytes);
    const digest = 'sha256:' + Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, '0')).join('');
    const before = await guard.queryLocks();
    const schedule = adapter.schedulePut(bytes, { id: ${JSON.stringify(`sw-fetch-${label}-put`)}, priority: 'user-visible', label: ${JSON.stringify(label)} });
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === ${JSON.stringify(`sw-fetch-${label}-put`)}) || null;
    const laneAfterTimeout = adapter.snapshot().executor.scheduler.lanes.find((row) => row.id === 'storage') || null;
    const followOn = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(`${label}-follow-on`)}), { id: ${JSON.stringify(`sw-fetch-${label}-follow-on`)}, priority: 'user-visible', label: ${JSON.stringify(`${label}-follow-on`)} });
    const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 220, intervalMs: 20, reason: 'fetch-lifecycle-recovery-while-holder-live' });
    const timeoutPresent = await store.has(digest);
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, schedule, drain, result, laneAfterTimeout, followOn, blockedRecovery, timeoutPresent, digest, bytes: bytes.byteLength, after, traceKinds });
  })()`;
}

function pageRecoveryAfterFetchExpression({ prefix, lockPrefix, lockName, holderRef, timeoutDigest, payload, label = 'recovery-after-service-worker-fetch' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerFetchLifecycleProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-fetch-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-fetch-${label}-guard`)}, lockTimeoutMs: 1200 });
    const scheduler = rt.crossLaneScheduler({ label: ${JSON.stringify(`sw-fetch-${label}-scheduler`)}, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = rt.blockStoreLaneAdapter({ label: ${JSON.stringify(`sw-fetch-${label}-adapter`)}, store: guard, scheduler, lane: 'storage' });
    const before = await guard.queryLocks();
    const holderVerify = await guard.verify(${JSON.stringify(holderRef)}, { timeoutMs: 1200 });
    const timeoutPresent = await store.has(${JSON.stringify(timeoutDigest)});
    const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 1200, intervalMs: 20, reason: 'fetch-lifecycle-recovery-after-holder-response' });
    const schedule = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(payload)}), { id: ${JSON.stringify(`sw-fetch-${label}-put`)}, priority: 'user-visible', label: ${JSON.stringify(label)} });
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === ${JSON.stringify(`sw-fetch-${label}-put`)}) || null;
    const verify = result?.result?.ref ? await guard.verify(result.result.ref, { timeoutMs: 1200 }) : null;
    const lane = adapter.snapshot().executor.scheduler.lanes.find((row) => row.id === 'storage') || null;
    const settled = await guard.waitForSettled({ timeoutMs: 1200, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, holderVerify, timeoutPresent, settledRecovery, schedule, drain, result, verify, lane, settled, after, traceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const source = await readFile(SW_SOURCE_PATH, 'utf8');
  const workerVersion = `${REVISION}-fetch-lifecycle-sw`;
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-service-worker-fetch-lifecycle-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-service-worker-fetch-lifecycle';
  const lockName = options.lockName || `${REVISION}-service-worker-fetch-lifecycle-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const timeoutMs = Number(options.timeoutMs || 40000);
  const profileDir = options.profileDir || await mkdtemp(join(tmpdir(), 'browserrt-sw-fetch-profile-'));
  const fetchPayload = `service-worker-fetch-event-holder-${REVISION}-${Math.random()}`;
  const timeoutPayload = `page-timeout-candidate-behind-fetch-${REVISION}-${Math.random()}`;
  const recoveryPayload = `page-recovery-after-service-worker-fetch-${REVISION}-${Math.random()}`;
  const fetchHoldMs = Number(options.fetchHoldMs || 1800);
  let server = null;
  let profileReap = null;
  const routes = {
    [SW_ROUTE]: { body: versionedWorkerSource(source, workerVersion), contentType: 'text/javascript; charset=utf-8', headers: { 'Service-Worker-Allowed': '/' } }
  };
  try {
    server = await startProbeServer({ root: process.cwd(), pagePath: '/browser-opfs-web-lock-service-worker-fetch-lifecycle.html', pageTitle: 'BrowserRT OPFS Web Lock Service Worker fetch lifecycle proof', allowedPrefixes: ['src/'], routes });
    const run = await runManagedBrowserPage({
      root: process.cwd(), server, profileDir, keepProfile: true,
      pagePath: '/browser-opfs-web-lock-service-worker-fetch-lifecycle.html', pageTitle: 'BrowserRT Service Worker fetch lifecycle proof',
      timeoutMs, stderrTerms: ['ServiceWorker', 'WebLock', 'OPFS', 'fetch', 'lifecycle']
    }, async ({ cdp, timeoutMs: browserTimeout }) => {
      const page = await evalJson(cdp, pageSummaryExpression(), browserTimeout);
      const unregisterBefore = await evalJson(cdp, unregisterAllExpression(), browserTimeout);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'fetch-phase-cleanup-before' }), browserTimeout);
      const registration = await evalJson(cdp, registerExpression(SW_ROUTE, workerVersion), browserTimeout);
      const fetchStart = await evalJson(cdp, startFetchHolderExpression({ prefix, lockPrefix, lockName, payload: fetchPayload, opId: `${REVISION}-fetch-holder`, holdMs: fetchHoldMs }), browserTimeout);
      const lockWhileFetchHeld = await waitFor(cdp, lockQueryExpression(fullLockName), (q) => q.heldCount >= 1, { timeoutMs: 6000, label: 'service-worker-fetch-held-web-lock' });
      const fetchStatusWhileHeld = await evalJson(cdp, fetchStatusExpression(), browserTimeout);
      const timeoutDigest = await evalJson(cdp, digestExpression(timeoutPayload), browserTimeout);
      const pageTimeout = await evalJson(cdp, pageTimeoutBehindFetchExpression({ prefix, lockPrefix, lockName, payload: timeoutPayload, label: 'fetch-phase-timeout', lockTimeoutMs: 450 }), browserTimeout);
      const lockAfterTimeout = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      const fetchResult = await evalJson(cdp, awaitFetchHolderExpression(), browserTimeout);
      const lockAfterFetch = await waitFor(cdp, lockQueryExpression(fullLockName), (q) => q.heldCount === 0 && q.pendingCount === 0, { timeoutMs: 5000, label: 'service-worker-fetch-lock-drain' });
      const recovery = await evalJson(cdp, pageRecoveryAfterFetchExpression({ prefix, lockPrefix, lockName, holderRef: fetchResult.body?.put?.ref, timeoutDigest: timeoutDigest.digest, payload: recoveryPayload, label: 'fetch-phase-recovery' }), browserTimeout);
      const unregisterAfter = await evalJson(cdp, unregisterAllExpression(), browserTimeout);
      const cleanupAfter = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'fetch-phase-cleanup-after' }), browserTimeout);
      const finalLocks = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      return { page, unregisterBefore, cleanupBefore, registration, fetchStart, lockWhileFetchHeld, fetchStatusWhileHeld, timeoutDigest, pageTimeout, lockAfterTimeout, fetchResult, lockAfterFetch, recovery, unregisterAfter, cleanupAfter, finalLocks };
    });

    profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 250, killMs: 750 });
    await rm(profileDir, { recursive: true, force: true });

    assert.equal(run.result.page.capabilities.serviceWorker, true, 'Service Worker must be available');
    assert.equal(run.result.page.capabilities.fetch, true, 'fetch must be available');
    assert.equal(run.result.page.capabilities.opfs, true, 'OPFS must be available');
    assert.equal(run.result.page.capabilities.webLocks, true, 'Web Locks must be available');
    assert.ok(run.result.registration.active?.scriptURL?.includes(SW_ROUTE), 'fetch lifecycle Service Worker must be active');
    assert.ok(run.result.registration.controller?.includes(SW_ROUTE), 'page must be controlled by the fetch lifecycle Service Worker');
    assert.equal(run.result.fetchStart.started, true, 'fetch holder should start');
    assert.ok(run.result.fetchStart.controlledBy?.includes(SW_ROUTE), 'fetch should start under Service Worker control');
    assert.equal(run.result.lockWhileFetchHeld.heldCount >= 1, true, 'Service Worker fetch event must hold guarded Web Lock');
    assert.equal(run.result.fetchStatusWhileHeld.settled, false, 'fetch should remain pending while lock is held');
    assert.equal(run.result.pageTimeout.result?.ok, false, 'page storage-lane put should fail behind Service Worker fetch held lock');
    assert.equal(run.result.pageTimeout.result?.error?.code, 'BRT_WEB_LOCK_TIMEOUT', 'page timeout should be classified as BRT_WEB_LOCK_TIMEOUT');
    assert.equal(run.result.pageTimeout.laneAfterTimeout?.healthy, false, 'storage lane should be unhealthy after fetch-held Web Lock timeout');
    assert.equal(run.result.pageTimeout.followOn?.accepted, false, 'follow-on storage write should be rejected while unhealthy');
    assert.equal(run.result.pageTimeout.followOn?.scheduler?.disposition, 'rejected-lane-unhealthy', 'follow-on disposition should be rejected-lane-unhealthy');
    assert.equal(run.result.pageTimeout.blockedRecovery?.recovered, false, 'recovery must be blocked while fetch event still holds the lock');
    assert.equal(run.result.pageTimeout.blockedRecovery?.reason, 'store-coordination-still-contended', 'blocked recovery reason should be contended lock state');
    assert.equal((typeof run.result.pageTimeout.timeoutPresent === 'boolean' ? run.result.pageTimeout.timeoutPresent : run.result.pageTimeout.timeoutPresent?.present), false, 'timed-out candidate must not be present before fetch completes');
    assert.equal(run.result.lockAfterTimeout.heldCount >= 1, true, 'fetch event should still hold the lock immediately after page timeout');
    assert.equal(run.result.fetchResult.ok, true, 'Service Worker fetch response should succeed');
    assert.equal(run.result.fetchResult.header, 'opfs-web-lock-lifecycle', 'fetch response should come from Service Worker proof route');
    assert.equal(run.result.fetchResult.body?.ok, true, 'Service Worker fetch body should report success');
    assert.equal(run.result.fetchResult.body?.verify?.ok, true, 'Service Worker fetch event should verify its OPFS block');
    assert.equal(run.result.lockAfterFetch.heldCount, 0, 'held locks should drain after fetch response');
    assert.equal(run.result.lockAfterFetch.pendingCount, 0, 'pending locks should drain after fetch response');
    assert.equal(run.result.recovery.holderVerify?.ok, true, 'page should verify Service Worker fetch-written block');
    assert.equal((typeof run.result.recovery.timeoutPresent === 'boolean' ? run.result.recovery.timeoutPresent : run.result.recovery.timeoutPresent?.present), false, 'timed-out candidate should remain absent after recovery');
    assert.equal(run.result.recovery.settledRecovery?.recovered, true, 'explicit recovery should succeed after fetch event releases lock');
    assert.equal(run.result.recovery.verify?.ok, true, 'page recovery write should verify after explicit recovery');
    assert.equal(run.result.recovery.lane?.healthy, true, 'storage lane should be healthy after explicit recovery and write');
    assert.equal(run.result.unregisterAfter.count >= 1, true, 'proof should unregister its Service Worker');
    assert.equal(run.result.finalLocks.heldCount, 0, 'final held lock count must be zero');
    assert.equal(run.result.finalLocks.pendingCount, 0, 'final pending lock count must be zero');
    assert.equal(profileReap.afterKillCount, 0, 'profile process reap must leave zero matching processes');

    return {
      project: 'BrowserRT', revision: REVISION, version: VERSION, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
      profileDir,
      fullLockName,
      observed: {
        fetchHoldMs,
        fetchResponseStatus: run.result.fetchResult.status,
        fetchHeader: run.result.fetchResult.header,
        fetchVerified: run.result.fetchResult.body?.verify?.ok ?? false,
        timeoutCode: run.result.pageTimeout.result?.error?.code || null,
        laneHealthyAfterTimeout: run.result.pageTimeout.laneAfterTimeout?.healthy ?? null,
        followOnDisposition: run.result.pageTimeout.followOn?.scheduler?.disposition || null,
        blockedRecovery: run.result.pageTimeout.blockedRecovery,
        lockAfterTimeout: run.result.lockAfterTimeout,
        lockAfterFetch: run.result.lockAfterFetch,
        holderVerifyAfterFetch: run.result.recovery.holderVerify?.ok ?? false,
        timeoutPresentAfterFetch: (typeof run.result.recovery.timeoutPresent === 'boolean' ? run.result.recovery.timeoutPresent : run.result.recovery.timeoutPresent?.present ?? null),
        settledRecovery: run.result.recovery.settledRecovery,
        recoveryWriteVerified: run.result.recovery.verify?.ok ?? false,
        finalLocks: run.result.finalLocks,
        profileReap
      },
      run,
      nonClaims: [
        'No cross-browser Service Worker fetch/Web Locks/OPFS behavior claim.',
        'No push-event, navigation-preload, offline-cache correctness, mobile/background suspension, or Service Worker lifetime guarantee.',
        'No OPFS fsync, power-loss, kernel-crash, browser-shutdown durability, quota, eviction, persistent-retention, fairness, exactly-once, throughput, latency, SLO, or production-readiness claim.'
      ]
    };
  } catch (error) {
    if (profileDir) {
      try { profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 500 }); } catch {}
      try { await rm(profileDir, { recursive: true, force: true }); } catch {}
    }
    return { project: 'BrowserRT', revision: REVISION, version: VERSION, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), error: errRecord(error), profileDir, profileReap };
  } finally {
    if (server) await server.close();
  }
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe({ timeoutMs: Number(argValue(process.argv.slice(2), '--timeout-ms', 40000)), fetchHoldMs: Number(argValue(process.argv.slice(2), '--fetch-hold-ms', 1800)) });
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
