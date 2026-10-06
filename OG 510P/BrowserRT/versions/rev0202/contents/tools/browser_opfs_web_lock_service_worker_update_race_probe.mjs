#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, connectBrowserCdp, closeServiceWorkerTargets, evalJson, sleep } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-UPDATE-RACE-PROBE.json`;
const TASK_ID = 'browser:opfs-web-lock-service-worker-update-race-proof';
const SW_V1_ROUTE = '/browserrt-opfs-web-lock-service-worker-update-race-v1.mjs';
const SW_V2_ROUTE = '/browserrt-opfs-web-lock-service-worker-update-race-v2.mjs';
const SW_SOURCE_PATH = 'tools/browserrt_opfs_web_lock_service_worker_holder.mjs';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function errRecord(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail || null, stack: error?.stack || null };
}

async function waitFor(cdp, expression, predicate, { timeoutMs = 5000, intervalMs = 50, label = 'condition' } = {}) {
  const deadline = Date.now() + timeoutMs;
  let last = null;
  while (Date.now() < deadline) {
    last = await evalJson(cdp, expression, Math.min(1200, timeoutMs));
    if (predicate(last)) return last;
    await sleep(intervalMs);
  }
  throw new Error(`Timed out waiting for ${label}; last=${JSON.stringify(last).slice(0, 2000)}`);
}

function versionedWorkerSource(source, version, { skipWaitingOnInstall = true } = {}) {
  let text = source.replace("'browserrt-service-worker-holder-v1'", JSON.stringify(version));
  if (!skipWaitingOnInstall) {
    text = text.replace('event.waitUntil(self.skipWaiting());', "event.waitUntil(Promise.resolve('install-waiting-for-explicit-update-race-release')); ");
  }
  return text;
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
    const rt = await mod.boot({ opfsWebLockServiceWorkerUpdateRaceProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-update-race-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-update-race-${label}-guard`)}, lockTimeoutMs: 1200 });
    const before = await guard.queryLocks();
    const cleanup = await guard.cleanupForTest({ timeoutMs: 1200 });
    const settled = await guard.waitForSettled({ timeoutMs: 1200, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, cleanup, settled, after, traceKinds });
  })()`;
}

function registerExpression(swRoute, expectedVersion, { waitForActive = false } = {}) {
  return `(async () => {
    const reg = await navigator.serviceWorker.register(${JSON.stringify(swRoute)}, { type: 'module', scope: '/', updateViaCache: 'none' });
    if (${JSON.stringify(waitForActive)}) await navigator.serviceWorker.ready;
    const deadline = Date.now() + 7000;
    let fresh = await navigator.serviceWorker.getRegistration('/');
    while (Date.now() < deadline) {
      fresh = await navigator.serviceWorker.getRegistration('/');
      const slots = [fresh?.active, fresh?.waiting, fresh?.installing].filter(Boolean);
      if (slots.some((slot) => slot.scriptURL.includes(${JSON.stringify(swRoute)}))) break;
      await new Promise((resolve) => setTimeout(resolve, 50));
    }
    fresh = await navigator.serviceWorker.getRegistration('/');
    return JSON.stringify({ expectedVersion: ${JSON.stringify(expectedVersion)}, route: ${JSON.stringify(swRoute)}, scope: fresh?.scope || reg.scope, active: fresh?.active ? { scriptURL: fresh.active.scriptURL, state: fresh.active.state } : null, waiting: fresh?.waiting ? { scriptURL: fresh.waiting.scriptURL, state: fresh.waiting.state } : null, installing: fresh?.installing ? { scriptURL: fresh.installing.scriptURL, state: fresh.installing.state } : null, controller: navigator.serviceWorker.controller?.scriptURL || null });
  })()`;
}

function postToServiceWorkerExpression({ cmd, swRoute, prefix, lockPrefix, lockName, payload = null, ref = null, opId = null, lockTimeoutMs = 1200, reason = null }) {
  return `(async () => {
    let reg = await navigator.serviceWorker.getRegistration('/');
    if (!reg || !(reg.active || reg.waiting || reg.installing)) {
      await navigator.serviceWorker.ready;
      reg = await navigator.serviceWorker.getRegistration('/');
    }
    const deadline = Date.now() + 7000;
    let sw = null;
    let slots = [];
    while (Date.now() < deadline) {
      reg = await navigator.serviceWorker.getRegistration('/');
      slots = [reg?.active, reg?.waiting, reg?.installing].filter(Boolean);
      sw = slots.find((candidate) => candidate.scriptURL.includes(${JSON.stringify(swRoute)})) || null;
      if (sw && sw.state !== 'redundant') break;
      await new Promise((resolve) => setTimeout(resolve, 50));
    }
    if (!sw) throw new Error('no matching service worker available for postMessage: ' + ${JSON.stringify(swRoute)} + '; slots=' + slots.map((row) => row.scriptURL + ':' + row.state).join(','));
    const msg = await new Promise((resolve, reject) => {
      const ch = new MessageChannel();
      const timer = setTimeout(() => reject(new Error('timed out waiting for service-worker response to ' + ${JSON.stringify(cmd)})), 9000);
      ch.port1.onmessage = (event) => { clearTimeout(timer); resolve(event.data); };
      sw.postMessage({ cmd: ${JSON.stringify(cmd)}, opId: ${JSON.stringify(opId)}, prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, payload: ${JSON.stringify(payload)}, ref: ${JSON.stringify(ref)}, lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)}, reason: ${JSON.stringify(reason)} }, [ch.port2]);
    });
    return JSON.stringify({ route: ${JSON.stringify(swRoute)}, registration: { scope: reg?.scope || null, active: reg?.active ? { scriptURL: reg.active.scriptURL, state: reg.active.state } : null, waiting: reg?.waiting ? { scriptURL: reg.waiting.scriptURL, state: reg.waiting.state } : null, installing: reg?.installing ? { scriptURL: reg.installing.scriptURL, state: reg.installing.state } : null }, worker: { scriptURL: sw.scriptURL, state: sw.state }, msg });
  })()`;
}

function pageVerifyExpression({ prefix, lockPrefix, lockName, ref, label = 'page-verify' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerUpdateRaceProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-update-race-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-update-race-${label}-guard`)}, lockTimeoutMs: 1200 });
    const before = await guard.queryLocks();
    const verify = await guard.verify(${JSON.stringify(ref)}, { timeoutMs: 1200 });
    const settled = await guard.waitForSettled({ timeoutMs: 1200, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, verify, settled, after, traceKinds });
  })()`;
}

function mainStartExpression({ prefix, lockPrefix, lockName, payload, lockTimeoutMs }) {
  return `(() => {
    window.__brtSwUpdateRaceMain = { events: [], result: null, error: null, resources: null };
    const state = window.__brtSwUpdateRaceMain;
    const mark = (event, fields = {}) => state.events.push({ event, t: Math.round(performance.now() * 1000) / 1000, ...fields });
    state.promise = (async () => {
      let rt = null;
      try {
        mark('main-start');
        const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
        rt = await mod.boot({ opfsWebLockServiceWorkerUpdateRaceProof: true, phase: 'main-timeout' });
        const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
        const digestBytes = await crypto.subtle.digest('SHA-256', bytes);
        const timeoutDigest = 'sha256:' + Array.from(new Uint8Array(digestBytes)).map((b) => b.toString(16).padStart(2, '0')).join('');
        const store = rt.opfsAsyncBlockStore({ name: 'sw-update-race-main-store', prefix: ${JSON.stringify(prefix)} });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'sw-update-race-main-guard', lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} });
        const scheduler = rt.crossLaneScheduler({
          label: 'sw-update-race-main-scheduler',
          lanes: [
            { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
            { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
          ]
        });
        const adapter = rt.blockStoreLaneAdapter({ label: 'sw-update-race-main-adapter', store: guard, scheduler, lane: 'storage' });
        state.resources = { rt, guard, adapter, timeoutDigest };
        mark('main-ready', { fullLockName: guard.fullLockName, timeoutDigest });
        const scheduledTimeout = adapter.schedulePut(bytes, { id: 'browser-sw-update-race-timeout-put', priority: 'user-visible', label: 'browser-timeout-during-service-worker-update-race' });
        mark('main-scheduled-timeout', { accepted: scheduledTimeout.accepted, disposition: scheduledTimeout.scheduler?.disposition || null });
        const timeoutDrain = await adapter.drain({ maxSteps: 2 });
        const timeoutResult = timeoutDrain.results.find((row) => row.opId === 'browser-sw-update-race-timeout-put') || null;
        const afterTimeout = adapter.snapshot();
        const unhealthyLane = afterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
        const rejectWhileUnhealthy = adapter.schedulePut(new TextEncoder().encode('browser-sw-update-race-reject-while-unhealthy'), { id: 'browser-sw-update-race-reject-while-unhealthy', priority: 'user-visible', label: 'should-not-queue-before-old-service-worker-stop' });
        const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 180, intervalMs: 20, reason: 'browser-service-worker-update-race-old-worker-still-active' });
        state.result = { timeoutDigest, scheduledTimeout, timeoutResult, unhealthyLane, rejectWhileUnhealthy, blockedRecovery, snapshot: afterTimeout, traceKinds: rt.trace.snapshot().map((row) => row.kind), trace: rt.trace.snapshot() };
        mark('main-timeout-done', { code: timeoutResult?.error?.code || null, blockedRecovery: blockedRecovery.recovered });
      } catch (error) {
        state.error = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, stack: error?.stack || null, detail: error?.detail || null };
        mark('main-error', { error: state.error });
        try { rt?.close?.(); } catch {}
      }
    })();
    return JSON.stringify({ started: true, href: location.href });
  })()`;
}

function mainStateExpression() {
  return `JSON.stringify({ events: window.__brtSwUpdateRaceMain?.events || [], result: window.__brtSwUpdateRaceMain?.result || null, error: window.__brtSwUpdateRaceMain?.error || null })`;
}

function finalizeExpression({ holderRef, recoveryPayload }) {
  return `(async () => {
    const state = window.__brtSwUpdateRaceMain;
    if (!state?.resources) throw new Error('service-worker update race resources unavailable');
    const { rt, guard, adapter, timeoutDigest } = state.resources;
    const beforeRecoveryQuery = await guard.queryLocks();
    const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 1800, intervalMs: 20, reason: 'service-worker-update-race-settled-recovery' });
    const holderVerify = await guard.verify(${JSON.stringify(holderRef)}, { timeoutMs: 1200 });
    const timeoutPresent = await guard.has(timeoutDigest, { timeoutMs: 1200 });
    const recoveredSchedule = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(recoveryPayload)}), { id: 'browser-sw-update-race-recovery-put', priority: 'user-visible', label: 'browser-after-service-worker-update-race-settled-recovery' });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'browser-sw-update-race-recovery-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await guard.verify(recoveredResult.result.ref, { timeoutMs: 1200 }) : null;
    const finalSnapshot = adapter.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const closeTraceKinds = rt.close().map((row) => row.kind);
    return JSON.stringify({ beforeRecoveryQuery, settledRecovery, holderVerify, timeoutDigest, timeoutPresent, recoveredSchedule, recoveredResult, recoveredVerify, finalSnapshot, traceKinds, closeTraceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-service-worker-update-race-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-service-worker-update-race';
  const lockName = options.lockName || `${REVISION}-service-worker-update-race-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const lockTimeoutMs = Number(options.lockTimeoutMs || 500);
  const holdId = `${REVISION}-service-worker-update-race-holder-${Math.random().toString(16).slice(2)}`;
  const holderPayload = `service-worker-update-race-holder-${REVISION}-${Math.random()}`;
  const timeoutPayload = `timed-out-service-worker-update-race-${REVISION}-${Math.random()}`;
  const recoveryPayload = `recovery-after-service-worker-update-race-${REVISION}-${Math.random()}`;
  const v2Payload = `service-worker-v2-after-old-holder-stops-${REVISION}-${Math.random()}`;
  const swSource = await readFile(SW_SOURCE_PATH, 'utf8');
  const v1Version = `${REVISION}-update-race-v1`;
  const v2Version = `${REVISION}-update-race-v2`;
  const routes = {
    [SW_V1_ROUTE]: { body: versionedWorkerSource(swSource, v1Version, { skipWaitingOnInstall: true }), contentType: 'text/javascript; charset=utf-8', headers: { 'Service-Worker-Allowed': '/' } },
    [SW_V2_ROUTE]: { body: versionedWorkerSource(swSource, v2Version, { skipWaitingOnInstall: false }), contentType: 'text/javascript; charset=utf-8', headers: { 'Service-Worker-Allowed': '/' } }
  };

  const { result: observed, harness } = await runManagedBrowserPage({
    root: process.cwd(),
    pagePath: '/browser-opfs-web-lock-service-worker-update-race.html',
    pageTitle: 'BrowserRT OPFS Web Lock Service Worker update race proof',
    allowedPrefixes: ['src/'],
    routes,
    timeoutMs: options.timeoutMs || 32000,
    stderrTerms: ['ServiceWorker', 'WebLock', 'OPFS', 'update', 'race', 'worker', 'lock']
  }, async ({ cdp, cdpPort, timeoutMs }) => {
    const browser = await connectBrowserCdp(cdpPort, timeoutMs);
    try {
      const page = await evalJson(cdp, pageSummaryExpression(), timeoutMs);
      const unregisterBefore = await evalJson(cdp, unregisterAllExpression(), timeoutMs);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'pre-cleanup' }), timeoutMs);
      const registerV1 = await evalJson(cdp, registerExpression(SW_V1_ROUTE, v1Version, { waitForActive: true }), timeoutMs);
      const swHold = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'hold', swRoute: SW_V1_ROUTE, prefix, lockPrefix, lockName, payload: holderPayload, opId: holdId }), timeoutMs);
      if (!swHold.msg?.ok) throw new Error(`service worker v1 hold failed: ${JSON.stringify(swHold.msg)}`);
      await sleep(120);
      const lockQueryAfterHold = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const registerV2WhileHeld = await evalJson(cdp, registerExpression(SW_V2_ROUTE, v2Version, { waitForActive: false }), timeoutMs);
      const registrationsAfterV2Install = await waitFor(cdp, registrationSummaryExpression(), (summary) => summary.rows.some((row) => [row.active, row.waiting, row.installing].filter(Boolean).some((slot) => slot.scriptURL.includes(SW_V2_ROUTE))), { timeoutMs: 7000, label: 'service-worker-v2-install-or-wait-while-v1-holds-lock' });
      const lockQueryAfterV2Install = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const swTargetsAfterV2Install = await browser.cdp.send('Target.getTargets', {}, timeoutMs).then((response) => (response.result?.targetInfos || []).filter((row) => row.type === 'service_worker'));

      const mainStarted = await evalJson(cdp, mainStartExpression({ prefix, lockPrefix, lockName, payload: timeoutPayload, lockTimeoutMs }), timeoutMs);
      await waitFor(cdp, mainStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'main-scheduled-timeout')) || Boolean(state.error), { timeoutMs: 2500, label: 'main scheduled timeout behind update-race service worker' });
      await sleep(Math.min(180, Math.max(60, Math.floor(lockTimeoutMs / 3))));
      const lockQueryWhilePending = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const mainTimeoutDone = await waitFor(cdp, mainStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'main-timeout-done')) || Boolean(state.error), { timeoutMs: lockTimeoutMs + 5000, label: 'main storage-lane timeout during service-worker update race' });
      if (mainTimeoutDone.error) throw new Error(`main timeout failed fatally: ${mainTimeoutDone.error.message}`);
      const lockQueryAfterBlockedRecovery = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const closeOldServiceWorker = await closeServiceWorkerTargets(browser.cdp, { urlIncludes: SW_V1_ROUTE, timeoutMs });
      await sleep(200);
      const lockQueryAfterOldClose = await waitFor(cdp, lockQueryExpression(fullLockName), (query) => query.heldCount === 0, { timeoutMs: 5000, label: 'old service-worker lock release after target close' });
      const registrationAfterOldClose = await waitFor(cdp, registrationSummaryExpression(), (summary) => summary.rows.some((row) => row.active?.scriptURL?.includes(SW_V2_ROUTE) || row.waiting?.scriptURL?.includes(SW_V2_ROUTE)), { timeoutMs: 7000, label: 'v2 registration after old worker close' });
      const final = await evalJson(cdp, finalizeExpression({ holderRef: swHold.msg.put.ref, recoveryPayload }), timeoutMs);
      const v2Put = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'put-once', swRoute: SW_V2_ROUTE, prefix, lockPrefix, lockName, payload: v2Payload, opId: `${REVISION}-v2-after-update-race-put` }), timeoutMs);
      const v2Verify = await evalJson(cdp, pageVerifyExpression({ prefix, lockPrefix, lockName, ref: v2Put.msg?.put?.ref, label: 'verify-v2-after-update-race' }), timeoutMs);
      const cleanupAfter = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'post-cleanup' }), timeoutMs);
      const unregisterAfter = await evalJson(cdp, unregisterAllExpression(), timeoutMs);
      const finalLocks = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const finalRegistrations = await evalJson(cdp, registrationSummaryExpression(), timeoutMs);
      return { page, unregisterBefore, cleanupBefore, registerV1, swHold, lockQueryAfterHold, registerV2WhileHeld, registrationsAfterV2Install, lockQueryAfterV2Install, swTargetsAfterV2Install, mainStarted, lockQueryWhilePending, mainTimeoutDone, lockQueryAfterBlockedRecovery, closeOldServiceWorker, lockQueryAfterOldClose, registrationAfterOldClose, final, v2Put, v2Verify, cleanupAfter, unregisterAfter, finalLocks, finalRegistrations };
    } finally {
      browser.cdp.close();
    }
  });

  assert.equal(observed.page.capabilities.serviceWorker, true, 'Service Worker must be available');
  assert.equal(observed.page.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(observed.page.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(observed.page.capabilities.webLocksQuery, true, 'Web Locks query must be available');
  assert.equal(observed.cleanupBefore.settled.ok, true, 'lock should settle before update-race proof');
  assert.ok(observed.registerV1.active?.scriptURL?.includes(SW_V1_ROUTE), 'v1 worker should become active');
  assert.equal(observed.swHold.msg.ok, true, 'v1 service worker should hold the guarded OPFS mutation lock');
  assert.equal(observed.swHold.msg.identity?.version, v1Version, 'holder identity should be v1');
  assert.equal(observed.swHold.msg.verify?.ok, true, 'v1 holder OPFS block should verify');
  assert.ok(observed.lockQueryAfterHold.held.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'v1 should hold exclusive lock before update attempt');
  assert.ok(observed.registrationsAfterV2Install.rows.some((row) => [row.active, row.waiting, row.installing].filter(Boolean).some((slot) => slot.scriptURL.includes(SW_V2_ROUTE))), 'v2 update worker should be installed/waiting/active while v1 holds lock');
  assert.equal(observed.lockQueryAfterV2Install.heldCount, 1, 'v1-held lock should remain held after v2 update attempt');
  assert.ok(observed.lockQueryWhilePending.held.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'old worker should hold lock while page put is pending');
  assert.ok(observed.lockQueryWhilePending.pending.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'page storage-lane put should be pending behind held lock during update race');
  assert.equal(observed.mainTimeoutDone.result?.timeoutResult?.error?.code, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(observed.mainTimeoutDone.result?.unhealthyLane?.healthy, false);
  assert.equal(observed.mainTimeoutDone.result?.unhealthyLane?.healthReason, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(observed.mainTimeoutDone.result?.rejectWhileUnhealthy?.accepted, false);
  assert.equal(observed.mainTimeoutDone.result?.rejectWhileUnhealthy?.scheduler?.disposition, 'rejected-lane-unhealthy');
  assert.equal(observed.mainTimeoutDone.result?.blockedRecovery?.recovered, false);
  assert.equal(observed.mainTimeoutDone.result?.blockedRecovery?.reason, 'store-coordination-still-contended');
  assert.equal(observed.lockQueryAfterBlockedRecovery.heldCount, 1, 'blocked recovery should leave old worker lock held');
  assert.ok(observed.closeOldServiceWorker.closedCount >= 1, 'CDP should close old v1 service worker target');
  assert.equal(observed.lockQueryAfterOldClose.heldCount, 0, 'held locks should drain after old v1 target closes');
  assert.equal(observed.lockQueryAfterOldClose.pendingCount, 0, 'pending locks should drain after old v1 target closes');
  assert.equal(observed.final.settledRecovery.recovered, true, 'same page adapter should recover after update-race lock settlement');
  assert.equal(observed.final.settledRecovery.recovery.healthy, true);
  assert.equal(observed.final.holderVerify.ok, true, 'v1-written holder block should still verify after update race');
  assert.equal(observed.final.timeoutPresent, false, 'timed-out page block should remain absent after update race recovery');
  assert.equal(observed.final.recoveredSchedule.accepted, true, 'recovered storage-lane put should schedule');
  assert.equal(observed.final.recoveredResult?.ok, true, 'recovered storage-lane put should complete');
  assert.equal(observed.final.recoveredVerify?.ok, true, 'recovered storage-lane block should verify');
  assert.equal(observed.v2Put.msg?.ok, true, 'v2 service worker should complete guarded OPFS put after old holder stops');
  assert.equal(observed.v2Put.msg?.identity?.version, v2Version, 'v2 put should be handled by v2 worker');
  assert.equal(observed.v2Verify.verify?.ok, true, 'page should verify v2-written OPFS block');
  assert.equal(observed.cleanupAfter.settled.ok, true, 'cleanup should settle locks');
  assert.equal(observed.finalLocks.heldCount, 0, 'final held lock count must be zero');
  assert.equal(observed.finalLocks.pendingCount, 0, 'final pending lock count must be zero');
  for (const kind of ['block-store-lane:recover-settled-blocked', 'block-store-lane:recover-settled', 'storage:opfs-web-lock-guard-still-contended', 'storage:opfs-web-lock-guard-settled']) {
    assert.ok(observed.final.traceKinds.includes(kind) || observed.mainTimeoutDone.result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-service-worker-update-race-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Managed Chromium proof that a Service Worker script update attempted while the old BrowserRT-compatible Service Worker holds the guarded OPFS mutation Web Lock does not bypass storage-lane timeout/backpressure, blocks recovery while contended, then permits explicit recovery and v2 guarded writes after the old target closes.',
    observations: { prefix, lockPrefix, lockName, fullLockName, lockTimeoutMs, holdId, v1Version, v2Version, page: observed.page, registerV1: observed.registerV1, swHold: observed.swHold, registerV2WhileHeld: observed.registerV2WhileHeld, registrationsAfterV2Install: observed.registrationsAfterV2Install, lockQueryAfterV2Install: observed.lockQueryAfterV2Install, swTargetsAfterV2Install: observed.swTargetsAfterV2Install, lockQueryWhilePending: observed.lockQueryWhilePending, mainTimeoutDone: observed.mainTimeoutDone, lockQueryAfterBlockedRecovery: observed.lockQueryAfterBlockedRecovery, closeOldServiceWorker: observed.closeOldServiceWorker, lockQueryAfterOldClose: observed.lockQueryAfterOldClose, registrationAfterOldClose: observed.registrationAfterOldClose, final: observed.final, v2Put: observed.v2Put, v2Verify: observed.v2Verify, cleanupAfter: observed.cleanupAfter, unregisterAfter: observed.unregisterAfter, finalLocks: observed.finalLocks, finalRegistrations: observed.finalRegistrations, harness },
    claimsChecked: [
      'a v1 module Service Worker can hold BrowserRT guarded OPFS mutation lock while writing a verified OPFS block',
      'a v2 Service Worker update can be installed/waiting/active while v1 still holds the lock without clearing the held lock',
      'a page-side storage-lane guarded OPFS write pending during that update race times out as BRT_WEB_LOCK_TIMEOUT and marks the storage lane unhealthy',
      'settled recovery refuses to reopen while the old service-worker-held lock remains present',
      'after the old service-worker target closes, locks drain, the same adapter recovers explicitly, the v1 block verifies, the timed-out block remains absent, and a v2 guarded OPFS write verifies'
    ],
    nonClaims: [
      'Managed Chromium/CDP Service Worker update-race proof only; no cross-browser Service Worker/Web Locks/OPFS behavior claim.',
      'No mobile/background suspension, fetch-event, push-event, offline, browser-shutdown durability, or full Service Worker update algorithm correctness claim.',
      'No automatic recovery, fairness, starvation-freedom, distributed-lock, exactly-once, throughput, latency, SLO, or production-readiness claim.',
      'No OPFS fsync, power-loss, kernel-crash, organic eviction, quota-survival, or persistent-retention claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '32000'));
const lockTimeoutMs = Number(argValue(argv, '--lock-timeout-ms', '500'));
const prefix = argValue(argv, '--prefix', null);
try {
  const report = await runProbe({ timeoutMs, lockTimeoutMs, prefix });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-service-worker-update-race-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: errRecord(error), nonClaims: ['Failed Service Worker update-race proof is not silently skipped; run it by explicit browser id while debugging.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_service_worker_update_race_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
