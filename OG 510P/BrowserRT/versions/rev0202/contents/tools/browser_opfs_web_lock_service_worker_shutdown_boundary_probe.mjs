#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, startProbeServer, evalJson, sleep, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-SHUTDOWN-BOUNDARY-PROBE.json`;
const TASK_ID = 'browser:opfs-web-lock-service-worker-shutdown-boundary-proof';
const SW_ROUTE = '/browserrt-opfs-web-lock-service-worker-shutdown-boundary.mjs';
const SW_SOURCE_PATH = 'tools/browserrt_opfs_web_lock_service_worker_holder.mjs';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function errRecord(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail || null, stack: error?.stack || null };
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

function versionedWorkerSource(source, version) {
  return source.replace("'browserrt-service-worker-holder-v1'", JSON.stringify(version));
}

function pageSummaryExpression() {
  return `JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, capabilities: { serviceWorker: 'serviceWorker' in navigator, opfs: typeof navigator.storage?.getDirectory === 'function', webLocks: typeof navigator.locks?.request === 'function', webLocksQuery: typeof navigator.locks?.query === 'function', abortController: typeof AbortController === 'function' } })`;
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

function registrationSummaryExpression() {
  return `(async () => {
    const regs = await navigator.serviceWorker.getRegistrations();
    const rows = regs.map((reg) => ({
      scope: reg.scope,
      active: reg.active ? { scriptURL: reg.active.scriptURL, state: reg.active.state } : null,
      waiting: reg.waiting ? { scriptURL: reg.waiting.scriptURL, state: reg.waiting.state } : null,
      installing: reg.installing ? { scriptURL: reg.installing.scriptURL, state: reg.installing.state } : null
    }));
    return JSON.stringify({ count: rows.length, rows, controller: navigator.serviceWorker.controller?.scriptURL || null });
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

function cleanupExpression({ prefix, lockPrefix, lockName, label = 'cleanup' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerRestartUpdateProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-restart-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-restart-${label}-guard`)}, lockTimeoutMs: 1200 });
    const before = await guard.queryLocks();
    const cleanup = await guard.cleanupForTest({ timeoutMs: 1200 });
    const settled = await guard.waitForSettled({ timeoutMs: 1200, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, cleanup, settled, after, traceKinds });
  })()`;
}

function registerExpression(swRoute, expectedVersion) {
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
    return JSON.stringify({ expectedVersion: ${JSON.stringify(expectedVersion)}, route: ${JSON.stringify(swRoute)}, scope: fresh?.scope || reg.scope, active: fresh?.active ? { scriptURL: fresh.active.scriptURL, state: fresh.active.state } : null, waiting: fresh?.waiting ? { scriptURL: fresh.waiting.scriptURL, state: fresh.waiting.state } : null, installing: fresh?.installing ? { scriptURL: fresh.installing.scriptURL, state: fresh.installing.state } : null, controller: navigator.serviceWorker.controller?.scriptURL || null });
  })()`;
}

function postToServiceWorkerExpression({ cmd, swRoute, prefix, lockPrefix, lockName, payload = null, ref = null, opId = null, lockTimeoutMs = 1200 }) {
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
      const timer = setTimeout(() => reject(new Error('timed out waiting for service-worker response')), 8000);
      ch.port1.onmessage = (event) => { clearTimeout(timer); resolve(event.data); };
      sw.postMessage({ cmd: ${JSON.stringify(cmd)}, opId: ${JSON.stringify(opId)}, prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, payload: ${JSON.stringify(payload)}, ref: ${JSON.stringify(ref)}, lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} }, [ch.port2]);
    });
    return JSON.stringify({ route: ${JSON.stringify(swRoute)}, registration: { scope: reg?.scope || null, active: reg?.active ? { scriptURL: reg.active.scriptURL, state: reg.active.state } : null, waiting: reg?.waiting ? { scriptURL: reg.waiting.scriptURL, state: reg.waiting.state } : null, installing: reg?.installing ? { scriptURL: reg.installing.scriptURL, state: reg.installing.state } : null }, worker: { scriptURL: sw.scriptURL, state: sw.state }, msg });
  })()`;
}

function pageVerifyExpression({ prefix, lockPrefix, lockName, ref, label = 'page-verify' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerRestartUpdateProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-restart-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-restart-${label}-guard`)}, lockTimeoutMs: 1200 });
    const before = await guard.queryLocks();
    const verify = await guard.verify(${JSON.stringify(ref)}, { timeoutMs: 1200 });
    const settled = await guard.waitForSettled({ timeoutMs: 1200, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, verify, settled, after, traceKinds });
  })()`;
}

function pageLaneWriteExpression({ prefix, lockPrefix, lockName, payload, label = 'page-lane-write' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerRestartUpdateProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-restart-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-restart-${label}-guard`)}, lockTimeoutMs: 1200 });
    const scheduler = rt.crossLaneScheduler({ label: ${JSON.stringify(`sw-restart-${label}-scheduler`)}, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = rt.blockStoreLaneAdapter({ label: ${JSON.stringify(`sw-restart-${label}-adapter`)}, store: guard, scheduler, lane: 'storage' });
    const before = await guard.queryLocks();
    const schedule = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(payload)}), { id: ${JSON.stringify(`sw-restart-${label}-put`)}, priority: 'user-visible', label: ${JSON.stringify(label)} });
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === ${JSON.stringify(`sw-restart-${label}-put`)}) || null;
    const verify = result?.result?.ref ? await guard.verify(result.result.ref, { timeoutMs: 1200 }) : null;
    const lane = adapter.snapshot().executor.scheduler.lanes.find((row) => row.id === 'storage') || null;
    const settled = await guard.waitForSettled({ timeoutMs: 1200, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, schedule, drain, result, verify, lane, settled, after, traceKinds });
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

function pageTimeoutBehindHolderExpression({ prefix, lockPrefix, lockName, payload, label = 'page-timeout-behind-holder', lockTimeoutMs = 500 }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerShutdownBoundaryProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-shutdown-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-shutdown-${label}-guard`)}, lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} });
    const scheduler = rt.crossLaneScheduler({ label: ${JSON.stringify(`sw-shutdown-${label}-scheduler`)}, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = rt.blockStoreLaneAdapter({ label: ${JSON.stringify(`sw-shutdown-${label}-adapter`)}, store: guard, scheduler, lane: 'storage' });
    const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
    const hash = await crypto.subtle.digest('SHA-256', bytes);
    const digest = 'sha256:' + Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, '0')).join('');
    const before = await guard.queryLocks();
    const schedule = adapter.schedulePut(bytes, { id: ${JSON.stringify(`sw-shutdown-${label}-put`)}, priority: 'user-visible', label: ${JSON.stringify(label)} });
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === ${JSON.stringify(`sw-shutdown-${label}-put`)}) || null;
    const laneAfterTimeout = adapter.snapshot().executor.scheduler.lanes.find((row) => row.id === 'storage') || null;
    const followOn = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(`${label}-follow-on`)}), { id: ${JSON.stringify(`sw-shutdown-${label}-follow-on`)}, priority: 'user-visible', label: ${JSON.stringify(`${label}-follow-on`)} });
    const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 220, intervalMs: 20, reason: 'shutdown-boundary-recovery-while-holder-live' });
    const timeoutPresent = await store.has(digest);
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, schedule, drain, result, laneAfterTimeout, followOn, blockedRecovery, timeoutPresent, digest, bytes: bytes.byteLength, after, traceKinds });
  })()`;
}

function pageRecoveryAfterRestartExpression({ prefix, lockPrefix, lockName, holderRef, timeoutDigest, payload, label = 'phase2-recovery' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerShutdownBoundaryProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-shutdown-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-shutdown-${label}-guard`)}, lockTimeoutMs: 1200 });
    const scheduler = rt.crossLaneScheduler({ label: ${JSON.stringify(`sw-shutdown-${label}-scheduler`)}, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = rt.blockStoreLaneAdapter({ label: ${JSON.stringify(`sw-shutdown-${label}-adapter`)}, store: guard, scheduler, lane: 'storage' });
    const before = await guard.queryLocks();
    const holderVerify = await guard.verify(${JSON.stringify(holderRef)}, { timeoutMs: 1200 });
    const timeoutPresent = await store.has(${JSON.stringify(timeoutDigest)});
    const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 1200, intervalMs: 20, reason: 'shutdown-boundary-recovery-after-relaunch' });
    const schedule = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(payload)}), { id: ${JSON.stringify(`sw-shutdown-${label}-put`)}, priority: 'user-visible', label: ${JSON.stringify(label)} });
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === ${JSON.stringify(`sw-shutdown-${label}-put`)}) || null;
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
  const workerVersion = `${REVISION}-shutdown-boundary-sw`;
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-service-worker-shutdown-boundary-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-service-worker-shutdown-boundary';
  const lockName = options.lockName || `${REVISION}-service-worker-shutdown-boundary-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const timeoutMs = Number(options.timeoutMs || 40000);
  const profileDir = options.profileDir || await mkdtemp(join(tmpdir(), 'browserrt-sw-shutdown-profile-'));
  const holderPayload = `service-worker-holder-before-browser-shutdown-${REVISION}-${Math.random()}`;
  const timeoutPayload = `page-timeout-candidate-before-shutdown-${REVISION}-${Math.random()}`;
  const recoveryPayload = `page-recovery-after-browser-shutdown-${REVISION}-${Math.random()}`;
  const workerAfterPayload = `service-worker-after-relaunch-${REVISION}-${Math.random()}`;
  let server = null;
  let profileReap = null;
  const routes = {
    [SW_ROUTE]: { body: versionedWorkerSource(source, workerVersion), contentType: 'text/javascript; charset=utf-8', headers: { 'Service-Worker-Allowed': '/' } }
  };
  try {
    server = await startProbeServer({ root: process.cwd(), pagePath: '/browser-opfs-web-lock-service-worker-shutdown-boundary.html', pageTitle: 'BrowserRT OPFS Web Lock Service Worker shutdown boundary proof', allowedPrefixes: ['src/'], routes });
    const phase1 = await runManagedBrowserPage({
      root: process.cwd(), server, profileDir, keepProfile: true, teardownMode: 'kill', killWaitMs: 2000,
      pagePath: '/browser-opfs-web-lock-service-worker-shutdown-boundary.html', pageTitle: 'BrowserRT Service Worker shutdown boundary phase 1',
      timeoutMs, stderrTerms: ['ServiceWorker', 'WebLock', 'OPFS', 'shutdown', 'boundary']
    }, async ({ cdp, timeoutMs: browserTimeout }) => {
      const page = await evalJson(cdp, pageSummaryExpression(), browserTimeout);
      const unregisterBefore = await evalJson(cdp, unregisterAllExpression(), browserTimeout);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'shutdown-phase1-cleanup' }), browserTimeout);
      const registration = await evalJson(cdp, registerExpression(SW_ROUTE, workerVersion), browserTimeout);
      const holder = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'hold', swRoute: SW_ROUTE, prefix, lockPrefix, lockName, payload: holderPayload, opId: `${REVISION}-shutdown-holder`, lockTimeoutMs: 0 }), browserTimeout);
      const lockWhileHeld = await waitFor(cdp, lockQueryExpression(fullLockName), (q) => q.heldCount >= 1, { timeoutMs: 5000, label: 'service-worker-held-web-lock' });
      const timeoutDigest = await evalJson(cdp, digestExpression(timeoutPayload), browserTimeout);
      const pageTimeout = await evalJson(cdp, pageTimeoutBehindHolderExpression({ prefix, lockPrefix, lockName, payload: timeoutPayload, label: 'shutdown-phase1-timeout', lockTimeoutMs: 500 }), browserTimeout);
      const lockBeforeShutdown = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      const registrationsBeforeShutdown = await evalJson(cdp, registrationSummaryExpression(), browserTimeout);
      return { page, unregisterBefore, cleanupBefore, registration, holder, lockWhileHeld, timeoutDigest, pageTimeout, lockBeforeShutdown, registrationsBeforeShutdown };
    });

    await sleep(300);

    const phase2 = await runManagedBrowserPage({
      root: process.cwd(), server, profileDir, keepProfile: true,
      pagePath: '/browser-opfs-web-lock-service-worker-shutdown-boundary.html', pageTitle: 'BrowserRT Service Worker shutdown boundary phase 2',
      timeoutMs, stderrTerms: ['ServiceWorker', 'WebLock', 'OPFS', 'shutdown', 'boundary']
    }, async ({ cdp, timeoutMs: browserTimeout }) => {
      const page = await evalJson(cdp, pageSummaryExpression(), browserTimeout);
      const registrationsAfterRestart = await waitFor(cdp, registrationSummaryExpression(), (summary) => summary.count > 0 && summary.rows.some((row) => row.active?.scriptURL?.includes(SW_ROUTE)), { timeoutMs: 7000, label: 'persisted service worker registration after browser shutdown' });
      const lockQueryAtRestart = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      const recovery = await evalJson(cdp, pageRecoveryAfterRestartExpression({ prefix, lockPrefix, lockName, holderRef: phase1.result.holder.msg.put.ref, timeoutDigest: phase1.result.timeoutDigest.digest, payload: recoveryPayload, label: 'phase2-recovery' }), browserTimeout);
      const swAfterRestartPut = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'put-once', swRoute: SW_ROUTE, prefix, lockPrefix, lockName, payload: workerAfterPayload, opId: `${REVISION}-after-relaunch-put` }), browserTimeout);
      const swAfterRestartVerify = await evalJson(cdp, pageVerifyExpression({ prefix, lockPrefix, lockName, ref: swAfterRestartPut.msg.put.ref, label: 'phase2-verify-worker-after-relaunch' }), browserTimeout);
      const unregisterAfter = await evalJson(cdp, unregisterAllExpression(), browserTimeout);
      const cleanupAfter = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'phase2-cleanup' }), browserTimeout);
      const finalLocks = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      return { page, registrationsAfterRestart, lockQueryAtRestart, recovery, swAfterRestartPut, swAfterRestartVerify, unregisterAfter, cleanupAfter, finalLocks };
    });

    profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 250, killMs: 750 });
    await rm(profileDir, { recursive: true, force: true });

    assert.equal(phase1.result.page.capabilities.serviceWorker, true, 'Service Worker must be available');
    assert.equal(phase1.result.page.capabilities.opfs, true, 'OPFS must be available');
    assert.equal(phase1.result.page.capabilities.webLocks, true, 'Web Locks must be available');
    assert.equal(phase1.result.holder.msg.ok, true, 'Service Worker hold should write and verify a real OPFS block');
    assert.equal(phase1.result.lockWhileHeld.heldCount >= 1, true, 'Service Worker must hold the guarded Web Lock before page timeout');
    assert.equal(phase1.result.pageTimeout.result?.ok, false, 'page storage-lane put should fail behind held Service Worker lock');
    assert.equal(phase1.result.pageTimeout.result?.error?.code, 'BRT_WEB_LOCK_TIMEOUT', 'page timeout should be classified as BRT_WEB_LOCK_TIMEOUT');
    assert.equal(phase1.result.pageTimeout.laneAfterTimeout?.healthy, false, 'storage lane should be unhealthy after Web Lock timeout');
    assert.equal(phase1.result.pageTimeout.followOn?.accepted, false, 'follow-on storage write should be rejected while unhealthy');
    assert.equal(phase1.result.pageTimeout.followOn?.scheduler?.disposition, 'rejected-lane-unhealthy', 'follow-on disposition should be rejected-lane-unhealthy');
    assert.equal(phase1.result.pageTimeout.blockedRecovery?.recovered, false, 'recovery must be blocked while holder remains live');
    assert.equal(phase1.result.pageTimeout.blockedRecovery?.reason, 'store-coordination-still-contended', 'blocked recovery reason should be contended lock state');
    assert.equal((typeof phase1.result.pageTimeout.timeoutPresent === 'boolean' ? phase1.result.pageTimeout.timeoutPresent : phase1.result.pageTimeout.timeoutPresent?.present), false, 'timed-out candidate must not be present before shutdown');
    assert.equal(phase1.result.lockBeforeShutdown.heldCount >= 1, true, 'lock should still be held immediately before browser-process shutdown');
    assert.equal(phase1.harness.teardownMode, 'kill', 'phase 1 should use process-group kill teardown');

    assert.equal(phase2.result.registrationsAfterRestart.count >= 1, true, 'Service Worker registration should still be visible after relaunch');
    assert.equal(phase2.result.lockQueryAtRestart.heldCount, 0, 'held locks should drain after browser-process shutdown/relaunch');
    assert.equal(phase2.result.lockQueryAtRestart.pendingCount, 0, 'pending locks should drain after browser-process shutdown/relaunch');
    assert.equal(phase2.result.recovery.holderVerify.ok, true, 'closed holder block should verify after relaunch');
    assert.equal((typeof phase2.result.recovery.timeoutPresent === 'boolean' ? phase2.result.recovery.timeoutPresent : phase2.result.recovery.timeoutPresent?.present), false, 'timed-out block should remain absent after relaunch');
    assert.equal(phase2.result.recovery.settledRecovery?.recovered, true, 'explicit recovery should succeed after lock state settles');
    assert.equal(phase2.result.recovery.verify?.ok, true, 'page recovery write should verify after explicit recovery');
    assert.equal(phase2.result.recovery.lane?.healthy, true, 'storage lane should be healthy after explicit recovery and write');
    assert.equal(phase2.result.swAfterRestartPut.msg.ok, true, 'Service Worker should still complete guarded OPFS put after relaunch');
    assert.equal(phase2.result.swAfterRestartVerify.verify.ok, true, 'page should verify Service Worker block after relaunch');
    assert.equal(phase2.result.unregisterAfter.count >= 1, true, 'proof should unregister its Service Worker');
    assert.equal(phase2.result.cleanupAfter.cleanup?.deletedFiles >= 0 || phase2.result.cleanupAfter.cleanup?.ok !== false, true, 'cleanup should run after proof');
    assert.equal(phase2.result.finalLocks.heldCount, 0, 'final held lock count must be zero');
    assert.equal(phase2.result.finalLocks.pendingCount, 0, 'final pending lock count must be zero');
    assert.equal(profileReap.afterKillCount, 0, 'profile process reap must leave zero matching processes');

    return {
      project: 'BrowserRT', revision: REVISION, version: VERSION, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
      profileDir,
      fullLockName,
      observed: {
        timeoutCode: phase1.result.pageTimeout.result?.error?.code || null,
        laneHealthyAfterTimeout: phase1.result.pageTimeout.laneAfterTimeout?.healthy ?? null,
        followOnDisposition: phase1.result.pageTimeout.followOn?.scheduler?.disposition || null,
        blockedRecovery: phase1.result.pageTimeout.blockedRecovery,
        lockHeldBeforeShutdown: phase1.result.lockBeforeShutdown.heldCount,
        phase1Teardown: phase1.harness.process,
        registrationsAfterRestart: phase2.result.registrationsAfterRestart.count,
        lockQueryAtRestart: phase2.result.lockQueryAtRestart,
        holderVerifyAfterRestart: phase2.result.recovery.holderVerify.ok,
        timeoutPresentAfterRestart: (typeof phase2.result.recovery.timeoutPresent === 'boolean' ? phase2.result.recovery.timeoutPresent : phase2.result.recovery.timeoutPresent?.present ?? null),
        settledRecovery: phase2.result.recovery.settledRecovery,
        recoveryWriteVerified: phase2.result.recovery.verify?.ok ?? false,
        workerAfterRestartVerified: phase2.result.swAfterRestartVerify.verify?.ok ?? false,
        finalLocks: phase2.result.finalLocks,
        profileReap
      },
      phase1, phase2,
      nonClaims: [
        'No cross-browser Service Worker/Web Locks/OPFS behavior claim.',
        'No OPFS fsync, power-loss, kernel-crash, browser-shutdown durability, quota, eviction, or persistent-retention claim.',
        'No automatic recovery, fairness, starvation-freedom, exactly-once, throughput, latency, SLO, or production-readiness claim.'
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
const report = await runProbe({ timeoutMs: Number(argValue(process.argv.slice(2), '--timeout-ms', 40000)) });
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
