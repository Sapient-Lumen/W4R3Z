#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, connectBrowserCdp, closeServiceWorkerTargets, evalJson, sleep } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-LIFECYCLE-PROBE.json`;
const TASK_ID = 'browser:opfs-web-lock-service-worker-lifecycle-proof';
const SW_ROUTE = '/browserrt-opfs-web-lock-service-worker-holder.mjs';
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

function lockQueryExpression(fullLockName) {
  return `(async () => {
    const raw = await navigator.locks.query();
    const keep = (row) => row && row.name === ${JSON.stringify(fullLockName)};
    const held = (raw.held || []).filter(keep).map((row) => ({ name: row.name, mode: row.mode, clientId: row.clientId ?? null }));
    const pending = (raw.pending || []).filter(keep).map((row) => ({ name: row.name, mode: row.mode, clientId: row.clientId ?? null }));
    return JSON.stringify({ held, pending, heldCount: held.length, pendingCount: pending.length, rawHeldCount: raw.held?.length ?? null, rawPendingCount: raw.pending?.length ?? null });
  })()`;
}

function unregisterExpression(swRoute = SW_ROUTE) {
  return `(async () => {
    const registrations = await navigator.serviceWorker.getRegistrations();
    const rows = [];
    for (const reg of registrations) {
      const scriptURL = reg.active?.scriptURL || reg.waiting?.scriptURL || reg.installing?.scriptURL || '';
      if (scriptURL.includes(${JSON.stringify(swRoute)})) rows.push({ scope: reg.scope, scriptURL, unregistered: await reg.unregister() });
    }
    return JSON.stringify({ rows, count: rows.length });
  })()`;
}

function cleanupExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerLifecycleProof: true, phase: 'cleanup' });
    const store = rt.opfsAsyncBlockStore({ name: 'sw-lifecycle-cleanup-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'sw-lifecycle-cleanup-guard', lockTimeoutMs: 1000 });
    const before = await guard.queryLocks();
    const cleanup = await guard.cleanupForTest({ timeoutMs: 1000 });
    const settled = await guard.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, cleanup, settled, after, traceKinds });
  })()`;
}

function registerAndHoldExpression({ prefix, lockPrefix, lockName, holdId, payload, swRoute = SW_ROUTE }) {
  return `(async () => {
    const capabilities = { serviceWorker: 'serviceWorker' in navigator, webLocks: typeof navigator.locks?.request === 'function', webLocksQuery: typeof navigator.locks?.query === 'function', opfs: typeof navigator.storage?.getDirectory === 'function', abortController: typeof AbortController === 'function' };
    const reg = await navigator.serviceWorker.register(${JSON.stringify(swRoute)}, { type: 'module', scope: '/' });
    await navigator.serviceWorker.ready;
    const sw = reg.active || reg.waiting || reg.installing;
    if (!sw) throw new Error('registered service worker has no active/waiting/installing worker');
    const msg = await new Promise((resolve, reject) => {
      const ch = new MessageChannel();
      const timer = setTimeout(() => reject(new Error('timed out waiting for service-worker hold acknowledgement')), 7000);
      ch.port1.onmessage = (event) => { clearTimeout(timer); resolve(event.data); };
      sw.postMessage({ cmd: 'hold', holdId: ${JSON.stringify(holdId)}, prefix: ${JSON.stringify(prefix)}, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, payload: ${JSON.stringify(payload)} }, [ch.port2]);
    });
    return JSON.stringify({ capabilities, registration: { scope: reg.scope, active: Boolean(reg.active), scriptURL: sw.scriptURL || null }, msg });
  })()`;
}

function mainStartExpression({ prefix, lockPrefix, lockName, payload, lockTimeoutMs }) {
  return `(() => {
    window.__brtSwLifecycleMain = { events: [], result: null, error: null, resources: null };
    const state = window.__brtSwLifecycleMain;
    const mark = (event, fields = {}) => state.events.push({ event, t: Math.round(performance.now() * 1000) / 1000, ...fields });
    state.promise = (async () => {
      let rt = null;
      try {
        mark('main-start');
        const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
        rt = await mod.boot({ opfsWebLockServiceWorkerLifecycleProof: true, phase: 'main' });
        const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
        const digestBytes = await crypto.subtle.digest('SHA-256', bytes);
        const timeoutDigest = 'sha256:' + Array.from(new Uint8Array(digestBytes)).map((b) => b.toString(16).padStart(2, '0')).join('');
        const store = rt.opfsAsyncBlockStore({ name: 'sw-lifecycle-main-store', prefix: ${JSON.stringify(prefix)} });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'sw-lifecycle-main-guard', lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} });
        const scheduler = rt.crossLaneScheduler({
          label: 'sw-lifecycle-main-scheduler',
          lanes: [
            { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
            { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
          ]
        });
        const adapter = rt.blockStoreLaneAdapter({ label: 'sw-lifecycle-main-adapter', store: guard, scheduler, lane: 'storage' });
        state.resources = { rt, guard, adapter, timeoutDigest };
        mark('main-ready', { fullLockName: guard.fullLockName, timeoutDigest });
        const scheduledTimeout = adapter.schedulePut(bytes, { id: 'browser-sw-lifecycle-timeout-put', priority: 'user-visible', label: 'browser-timeout-behind-service-worker' });
        mark('main-scheduled-timeout', { accepted: scheduledTimeout.accepted, disposition: scheduledTimeout.scheduler?.disposition || null });
        const timeoutDrain = await adapter.drain({ maxSteps: 2 });
        const timeoutResult = timeoutDrain.results.find((row) => row.opId === 'browser-sw-lifecycle-timeout-put') || null;
        const afterTimeout = adapter.snapshot();
        const unhealthyLane = afterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
        const rejectWhileUnhealthy = adapter.schedulePut(new TextEncoder().encode('browser-sw-lifecycle-reject-while-unhealthy'), { id: 'browser-sw-reject-while-unhealthy', priority: 'user-visible', label: 'should-not-queue-before-service-worker-stop' });
        const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 140, intervalMs: 20, reason: 'browser-service-worker-still-active' });
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
  return `JSON.stringify({ events: window.__brtSwLifecycleMain?.events || [], result: window.__brtSwLifecycleMain?.result || null, error: window.__brtSwLifecycleMain?.error || null })`;
}

function finalizeExpression({ holderRef, recoveryPayload }) {
  return `(async () => {
    const state = window.__brtSwLifecycleMain;
    if (!state?.resources) throw new Error('service-worker lifecycle resources unavailable');
    const { rt, guard, adapter, timeoutDigest } = state.resources;
    const beforeRecoveryQuery = await guard.queryLocks();
    const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 1800, intervalMs: 20, reason: 'browser-service-worker-stopped-settled-recovery' });
    const holderVerify = await guard.verify(${JSON.stringify(holderRef)}, { timeoutMs: 1000 });
    const timeoutPresent = await guard.has(timeoutDigest, { timeoutMs: 1000 });
    const recoveredSchedule = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(recoveryPayload)}), { id: 'browser-sw-lifecycle-recovery-put', priority: 'user-visible', label: 'browser-after-service-worker-settled-recovery' });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'browser-sw-lifecycle-recovery-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await guard.verify(recoveredResult.result.ref, { timeoutMs: 1000 }) : null;
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const settledAfterCleanup = await guard.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const queryAfterCleanup = await guard.queryLocks();
    const finalSnapshot = adapter.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const closeTraceKinds = rt.close().map((row) => row.kind);
    const registrations = await navigator.serviceWorker.getRegistrations();
    const unregisterRows = [];
    for (const reg of registrations) {
      const scriptURL = reg.active?.scriptURL || reg.waiting?.scriptURL || reg.installing?.scriptURL || '';
      if (scriptURL.includes(${JSON.stringify(SW_ROUTE)})) unregisterRows.push({ scope: reg.scope, scriptURL, unregistered: await reg.unregister() });
    }
    const unregistered = { rows: unregisterRows, count: unregisterRows.length };
    return JSON.stringify({ beforeRecoveryQuery, settledRecovery, holderVerify, timeoutDigest, timeoutPresent, recoveredSchedule, recoveredResult, recoveredVerify, cleanupAfter, settledAfterCleanup, queryAfterCleanup, finalSnapshot, traceKinds, closeTraceKinds, unregistered });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-service-worker-lifecycle-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-service-worker-lifecycle';
  const lockName = options.lockName || `${REVISION}-service-worker-lifecycle-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const lockTimeoutMs = Number(options.lockTimeoutMs || 500);
  const holdId = `${REVISION}-service-worker-holder-${Math.random().toString(16).slice(2)}`;
  const holderPayload = `service-worker-holder-${REVISION}-${Math.random()}`;
  const timeoutPayload = `timed-out-service-worker-lifecycle-${REVISION}-${Math.random()}`;
  const recoveryPayload = `recovery-after-service-worker-stop-${REVISION}-${Math.random()}`;
  const swSource = await readFile(SW_SOURCE_PATH, 'utf8');

  const { result: observed, harness } = await runManagedBrowserPage({
    root: process.cwd(),
    pagePath: '/browser-opfs-web-lock-service-worker-lifecycle.html',
    pageTitle: 'BrowserRT OPFS Web Lock service worker lifecycle proof',
    allowedPrefixes: ['src/'],
    routes: { [SW_ROUTE]: { body: swSource, contentType: 'text/javascript; charset=utf-8', headers: { 'Service-Worker-Allowed': '/' } } },
    timeoutMs: options.timeoutMs || 26000,
    stderrTerms: ['ServiceWorker', 'WebLock', 'OPFS', 'lock', 'worker', 'target']
  }, async ({ cdp, cdpPort, timeoutMs }) => {
    const browser = await connectBrowserCdp(cdpPort, timeoutMs);
    try {
      const page = await evalJson(cdp, `JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, capabilities: { serviceWorker: 'serviceWorker' in navigator, opfs: typeof navigator.storage?.getDirectory === 'function', webLocks: typeof navigator.locks?.request === 'function', webLocksQuery: typeof navigator.locks?.query === 'function', abortController: typeof AbortController === 'function' } })`, timeoutMs);
      const unregisterBefore = await evalJson(cdp, unregisterExpression(), timeoutMs);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName }), timeoutMs);
      const swHold = await evalJson(cdp, registerAndHoldExpression({ prefix, lockPrefix, lockName, holdId, payload: holderPayload }), timeoutMs);
      if (!swHold.msg?.ok) throw new Error(`service worker hold failed: ${JSON.stringify(swHold.msg)}`);
      await sleep(100);
      const lockQueryAfterHold = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const swTargetsAfterHold = await browser.cdp.send('Target.getTargets', {}, timeoutMs).then((response) => (response.result?.targetInfos || []).filter((row) => row.type === 'service_worker'));

      const mainStarted = await evalJson(cdp, mainStartExpression({ prefix, lockPrefix, lockName, payload: timeoutPayload, lockTimeoutMs }), timeoutMs);
      await waitFor(cdp, mainStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'main-scheduled-timeout')) || Boolean(state.error), { timeoutMs: 2500, label: 'main scheduled timeout behind service worker' });
      await sleep(Math.min(150, Math.max(50, Math.floor(lockTimeoutMs / 4))));
      const lockQueryWhilePending = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const mainTimeoutDone = await waitFor(cdp, mainStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'main-timeout-done')) || Boolean(state.error), { timeoutMs: lockTimeoutMs + 5000, label: 'main storage-lane timeout behind service worker' });
      if (mainTimeoutDone.error) throw new Error(`main timeout failed fatally: ${mainTimeoutDone.error.message}`);
      const lockQueryAfterBlockedRecovery = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const closeServiceWorkers = await closeServiceWorkerTargets(browser.cdp, { urlIncludes: SW_ROUTE, timeoutMs });
      await sleep(150);
      const lockQueryAfterStop = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const final = await evalJson(cdp, finalizeExpression({ holderRef: swHold.msg.put.ref, recoveryPayload }), timeoutMs);
      const lockQueryAfterFinal = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      return { page, unregisterBefore, cleanupBefore, swHold, lockQueryAfterHold, swTargetsAfterHold, mainStarted, lockQueryWhilePending, mainTimeoutDone, lockQueryAfterBlockedRecovery, closeServiceWorkers, lockQueryAfterStop, final, lockQueryAfterFinal };
    } finally {
      browser.cdp.close();
    }
  });

  assert.equal(observed.page.capabilities.serviceWorker, true, 'Service Worker must be available');
  assert.equal(observed.page.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(observed.page.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(observed.page.capabilities.webLocksQuery, true, 'Web Locks query must be available');
  assert.equal(observed.cleanupBefore.settled.ok, true, 'lock should settle before service-worker proof');
  assert.equal(observed.swHold.msg.ok, true, 'service worker should acknowledge holding the lock');
  assert.equal(observed.swHold.msg.capabilities.webLocks, true, 'service worker should see Web Locks');
  assert.equal(observed.swHold.msg.capabilities.opfs, true, 'service worker should see OPFS');
  assert.equal(observed.swHold.msg.verify?.ok, true, 'service worker OPFS write should verify');
  assert.ok(observed.lockQueryAfterHold.held.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'service worker should hold exclusive lock');
  assert.ok(observed.swTargetsAfterHold.some((row) => row.type === 'service_worker' && row.url.includes(SW_ROUTE)), 'service worker target should be visible to CDP');
  assert.ok(observed.lockQueryWhilePending.held.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'service worker lock should be held while page put is pending');
  assert.ok(observed.lockQueryWhilePending.pending.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'page storage-lane put should be pending behind service worker lock');
  assert.equal(observed.mainTimeoutDone.result?.timeoutResult?.error?.code, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(observed.mainTimeoutDone.result?.unhealthyLane?.healthy, false);
  assert.equal(observed.mainTimeoutDone.result?.unhealthyLane?.healthReason, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(observed.mainTimeoutDone.result?.rejectWhileUnhealthy?.accepted, false);
  assert.equal(observed.mainTimeoutDone.result?.rejectWhileUnhealthy?.scheduler?.disposition, 'rejected-lane-unhealthy');
  assert.equal(observed.mainTimeoutDone.result?.blockedRecovery?.recovered, false);
  assert.equal(observed.mainTimeoutDone.result?.blockedRecovery?.reason, 'store-coordination-still-contended');
  assert.equal(observed.lockQueryAfterBlockedRecovery.heldCount, 1, 'service worker should still hold lock after blocked recovery');
  assert.ok(observed.closeServiceWorkers.closedCount >= 1, 'CDP should close at least one service worker target');
  assert.equal(observed.closeServiceWorkers.afterCount, 0, 'service worker target should be gone after close');
  assert.equal(observed.lockQueryAfterStop.heldCount, 0, 'lock should release after service worker target close');
  assert.equal(observed.final.settledRecovery.recovered, true, 'settled recovery should reopen storage lane after service worker close');
  assert.equal(observed.final.settledRecovery.recovery.healthy, true);
  assert.equal(observed.final.holderVerify.ok, true, 'service-worker-written block should verify from page after worker close');
  assert.equal(observed.final.timeoutPresent, false, 'timed-out candidate should remain absent');
  assert.equal(observed.final.recoveredSchedule.accepted, true, 'recovered storage-lane put should schedule');
  assert.equal(observed.final.recoveredResult?.ok, true, 'recovered storage-lane put should complete');
  assert.equal(observed.final.recoveredVerify?.ok, true, 'recovered block should verify');
  assert.equal(observed.final.cleanupAfter, true, 'cleanup should succeed');
  assert.equal(observed.final.settledAfterCleanup.ok, true, 'lock should settle after cleanup');
  assert.equal(observed.final.queryAfterCleanup.heldCount, 0);
  assert.equal(observed.final.queryAfterCleanup.pendingCount, 0);
  assert.equal(observed.lockQueryAfterFinal.heldCount, 0);
  assert.equal(observed.lockQueryAfterFinal.pendingCount, 0);
  for (const kind of ['block-store-lane:recover-settled-blocked', 'block-store-lane:recover-settled', 'storage:opfs-web-lock-guard-still-contended', 'storage:opfs-web-lock-guard-settled']) {
    assert.ok(observed.final.traceKinds.includes(kind) || observed.mainTimeoutDone.result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-service-worker-lifecycle-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Managed Chromium proof that a BrowserRT-compatible module Service Worker can hold a real Web Lock while writing a verified OPFS content-addressed block, forcing a page-side storage-lane guarded OPFS mutation to time out/backpressure until CDP closes the service-worker target and explicit settled recovery reopens the lane.',
    observations: { prefix, lockPrefix, lockName, fullLockName, lockTimeoutMs, holdId, page: observed.page, unregisterBefore: observed.unregisterBefore, cleanupBefore: observed.cleanupBefore, swHold: observed.swHold, lockQueryAfterHold: observed.lockQueryAfterHold, swTargetsAfterHold: observed.swTargetsAfterHold, lockQueryWhilePending: observed.lockQueryWhilePending, mainTimeoutDone: observed.mainTimeoutDone, lockQueryAfterBlockedRecovery: observed.lockQueryAfterBlockedRecovery, closeServiceWorkers: observed.closeServiceWorkers, lockQueryAfterStop: observed.lockQueryAfterStop, final: observed.final, lockQueryAfterFinal: observed.lockQueryAfterFinal, harness },
    claimsChecked: [
      'a same-origin module Service Worker can use BrowserRT OPFS block-store and WebLockGuardedBlockStore modules',
      'the service worker can hold the guarded mutation lock while writing and verifying a real OPFS block',
      'a page-side storage-lane guarded OPFS write pending behind that service-worker lock times out as BRT_WEB_LOCK_TIMEOUT and marks the storage lane unhealthy',
      'settled recovery refuses to reopen while the service-worker-held lock remains present',
      'after CDP closes the service-worker target, locks settle, the lane recovers explicitly, the service-worker block verifies, the timed-out candidate remains absent, and a later write verifies'
    ],
    nonClaims: [
      'Managed Chromium/CDP service-worker proof only; no cross-browser service-worker lifecycle claim.',
      'No mobile/background suspend, tab discard, browser shutdown, service-worker update, fetch-event, push-event, or offline lifecycle claim.',
      'Recovery is explicit maintenance-driven recovery, not autonomous healing or a liveness/fairness theorem.',
      'Timeout is an acquisition backstop only; it does not cancel work after a lock has already been granted.',
      'No distributed-lock, exactly-once, OPFS durability, fsync, power-loss, kernel-crash, organic eviction, quota, persistent-retention, throughput, latency, SLO, or production readiness claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '26000'));
const lockTimeoutMs = Number(argValue(argv, '--lock-timeout-ms', '500'));
const prefix = argValue(argv, '--prefix', null);
try {
  const report = await runProbe({ timeoutMs, lockTimeoutMs, prefix });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-service-worker-lifecycle-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: errRecord(error), nonClaims: ['Failed service-worker lifecycle proof is not silently skipped; run it by explicit browser id while debugging.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_service_worker_lifecycle_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
