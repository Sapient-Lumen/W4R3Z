#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, startProbeServer, evalJson, sleep, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-RESTART-UPDATE-PROBE.json`;
const TASK_ID = 'browser:opfs-web-lock-service-worker-restart-update-proof';
const SW_V1_ROUTE = '/browserrt-opfs-web-lock-service-worker-restart-v1.mjs';
const SW_V2_ROUTE = '/browserrt-opfs-web-lock-service-worker-restart-v2.mjs';
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

export async function runProbe(options = {}) {
  const started = performance.now();
  const source = await readFile(SW_SOURCE_PATH, 'utf8');
  const versionV1 = `${REVISION}-restart-v1`;
  const versionV2 = `${REVISION}-restart-v2`;
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-service-worker-restart-update-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-service-worker-restart-update';
  const lockName = options.lockName || `${REVISION}-service-worker-restart-update-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const timeoutMs = Number(options.timeoutMs || 32000);
  const profileDir = options.profileDir || await mkdtemp(join(tmpdir(), 'browserrt-sw-restart-profile-'));
  const pagePayload = `page-lane-after-service-worker-restart-update-${REVISION}-${Math.random()}`;
  const phase1Payload = `service-worker-phase1-payload-${REVISION}-${Math.random()}`;
  const restartPayload = `service-worker-after-browser-restart-${REVISION}-${Math.random()}`;
  const updatePayload = `service-worker-after-script-update-${REVISION}-${Math.random()}`;
  let server = null;
  let profileReap = null;
  const routes = {
    [SW_V1_ROUTE]: { body: versionedWorkerSource(source, versionV1), contentType: 'text/javascript; charset=utf-8', headers: { 'Service-Worker-Allowed': '/' } },
    [SW_V2_ROUTE]: { body: versionedWorkerSource(source, versionV2), contentType: 'text/javascript; charset=utf-8', headers: { 'Service-Worker-Allowed': '/' } }
  };
  try {
    server = await startProbeServer({ root: process.cwd(), pagePath: '/browser-opfs-web-lock-service-worker-restart-update.html', pageTitle: 'BrowserRT OPFS Web Lock Service Worker restart/update proof', allowedPrefixes: ['src/'], routes });

    const phase1 = await runManagedBrowserPage({
      root: process.cwd(), server, profileDir, keepProfile: true,
      pagePath: '/browser-opfs-web-lock-service-worker-restart-update.html',
      pageTitle: 'BrowserRT Service Worker restart update phase 1',
      timeoutMs, stderrTerms: ['ServiceWorker', 'WebLock', 'OPFS', 'restart', 'update']
    }, async ({ cdp, timeoutMs: browserTimeout }) => {
      const page = await evalJson(cdp, pageSummaryExpression(), browserTimeout);
      const unregisterBefore = await evalJson(cdp, unregisterAllExpression(), browserTimeout);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'phase1-cleanup' }), browserTimeout);
      const registration = await evalJson(cdp, registerExpression(SW_V1_ROUTE, versionV1), browserTimeout);
      const swPut = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'put-once', swRoute: SW_V1_ROUTE, prefix, lockPrefix, lockName, payload: phase1Payload, opId: `${REVISION}-phase1-put` }), browserTimeout);
      const pageVerify = await evalJson(cdp, pageVerifyExpression({ prefix, lockPrefix, lockName, ref: swPut.msg.put.ref, label: 'phase1-page-verify' }), browserTimeout);
      const lockQueryAfter = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      const registrationsAfter = await evalJson(cdp, registrationSummaryExpression(), browserTimeout);
      return { page, unregisterBefore, cleanupBefore, registration, swPut, pageVerify, lockQueryAfter, registrationsAfter };
    });

    // Give Chromium a short quiet period before relaunching against the same profile.
    await sleep(250);

    const phase2 = await runManagedBrowserPage({
      root: process.cwd(), server, profileDir, keepProfile: true,
      pagePath: '/browser-opfs-web-lock-service-worker-restart-update.html',
      pageTitle: 'BrowserRT Service Worker restart update phase 2',
      timeoutMs, stderrTerms: ['ServiceWorker', 'WebLock', 'OPFS', 'restart', 'update']
    }, async ({ cdp, timeoutMs: browserTimeout }) => {
      const page = await evalJson(cdp, pageSummaryExpression(), browserTimeout);
      const registrationsBefore = await waitFor(cdp, registrationSummaryExpression(), (summary) => summary.count > 0 && summary.rows.some((row) => row.active?.scriptURL?.includes(SW_V1_ROUTE)), { timeoutMs: 6000, label: 'persisted v1 service worker registration after browser restart' });
      const lockQueryBefore = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      const restartSwPut = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'put-once', swRoute: SW_V1_ROUTE, prefix, lockPrefix, lockName, payload: restartPayload, opId: `${REVISION}-restart-put` }), browserTimeout);
      const oldBlockVerifyAfterRestart = await evalJson(cdp, pageVerifyExpression({ prefix, lockPrefix, lockName, ref: phase1.result.swPut.msg.put.ref, label: 'phase2-verify-phase1-block' }), browserTimeout);
      const updateRegistration = await evalJson(cdp, registerExpression(SW_V2_ROUTE, versionV2), browserTimeout);
      const registrationsAfterUpdate = await waitFor(cdp, registrationSummaryExpression(), (summary) => summary.rows.some((row) => row.active?.scriptURL?.includes(SW_V2_ROUTE)), { timeoutMs: 7000, label: 'v2 service worker activation' });
      const updateStatus = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'status', swRoute: SW_V2_ROUTE, prefix, lockPrefix, lockName, opId: `${REVISION}-v2-status` }), browserTimeout);
      const updateSwPut = await evalJson(cdp, postToServiceWorkerExpression({ cmd: 'put-once', swRoute: SW_V2_ROUTE, prefix, lockPrefix, lockName, payload: updatePayload, opId: `${REVISION}-update-put` }), browserTimeout);
      const restartBlockPageVerify = await evalJson(cdp, pageVerifyExpression({ prefix, lockPrefix, lockName, ref: restartSwPut.msg.put.ref, label: 'phase2-verify-restart-block' }), browserTimeout);
      const updateBlockPageVerify = await evalJson(cdp, pageVerifyExpression({ prefix, lockPrefix, lockName, ref: updateSwPut.msg.put.ref, label: 'phase2-verify-update-block' }), browserTimeout);
      const pageLaneWrite = await evalJson(cdp, pageLaneWriteExpression({ prefix, lockPrefix, lockName, payload: pagePayload, label: 'phase2-page-lane-write' }), browserTimeout);
      const lockQueryAfterWrites = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      const cleanupAfter = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'phase2-cleanup' }), browserTimeout);
      const unregisterAfter = await evalJson(cdp, unregisterAllExpression(), browserTimeout);
      const registrationsAfterUnregister = await evalJson(cdp, registrationSummaryExpression(), browserTimeout);
      const lockQueryFinal = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      return { page, registrationsBefore, lockQueryBefore, restartSwPut, oldBlockVerifyAfterRestart, updateRegistration, registrationsAfterUpdate, updateStatus, updateSwPut, restartBlockPageVerify, updateBlockPageVerify, pageLaneWrite, lockQueryAfterWrites, cleanupAfter, unregisterAfter, registrationsAfterUnregister, lockQueryFinal };
    });

    profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 250, killMs: 750 });
    await rm(profileDir, { recursive: true, force: true });
    await server.close();
    server = null;

    const observed = { prefix, lockPrefix, lockName, fullLockName, versionV1, versionV2, profileDir, phase1: phase1.result, phase2: phase2.result, harnesses: { phase1: phase1.harness, phase2: phase2.harness }, profileReap };

    assert.equal(observed.phase1.page.capabilities.serviceWorker, true, 'Service Worker must be available');
    assert.equal(observed.phase1.page.capabilities.opfs, true, 'OPFS must be available');
    assert.equal(observed.phase1.page.capabilities.webLocks, true, 'Web Locks must be available');
    assert.equal(observed.phase1.cleanupBefore.settled.ok, true, 'phase1 cleanup must settle');
    assert.ok(observed.phase1.registration.active?.scriptURL?.includes(SW_V1_ROUTE), 'phase1 active service worker should be v1 route');
    assert.equal(observed.phase1.swPut.msg.ok, true, 'phase1 service worker put should succeed');
    assert.equal(observed.phase1.swPut.msg.identity?.version, versionV1, 'phase1 service worker should report v1 identity');
    assert.equal(observed.phase1.swPut.msg.verify?.ok, true, 'phase1 service worker block verifies');
    assert.equal(observed.phase1.pageVerify.verify?.ok, true, 'phase1 block verifies from page');
    assert.equal(observed.phase1.lockQueryAfter.heldCount, 0, 'phase1 lock should not remain held');
    assert.equal(observed.phase1.lockQueryAfter.pendingCount, 0, 'phase1 lock should not remain pending');

    assert.ok(observed.phase2.registrationsBefore.rows.some((row) => row.active?.scriptURL?.includes(SW_V1_ROUTE)), 'v1 registration should persist after browser restart with same profile/origin');
    assert.equal(observed.phase2.lockQueryBefore.heldCount, 0, 'lock should not be held at phase2 start');
    assert.equal(observed.phase2.restartSwPut.msg.ok, true, 'service worker should respond after browser restart');
    assert.equal(observed.phase2.restartSwPut.msg.identity?.version, versionV1, 'post-restart service worker should still be v1 before update');
    assert.equal(observed.phase2.oldBlockVerifyAfterRestart.verify?.ok, true, 'phase1 OPFS block should verify after browser restart');
    assert.ok(observed.phase2.updateRegistration.active?.scriptURL?.includes(SW_V2_ROUTE) || observed.phase2.registrationsAfterUpdate.rows.some((row) => row.active?.scriptURL?.includes(SW_V2_ROUTE)), 'v2 service worker should activate for same scope');
    assert.equal(observed.phase2.updateStatus.msg.identity?.version, versionV2, 'status should come from v2 worker after update');
    assert.equal(observed.phase2.updateSwPut.msg.identity?.version, versionV2, 'put should come from v2 worker after update');
    assert.equal(observed.phase2.updateSwPut.msg.verify?.ok, true, 'v2 service worker block verifies');
    assert.equal(observed.phase2.restartBlockPageVerify.verify?.ok, true, 'post-restart v1 block verifies from page');
    assert.equal(observed.phase2.updateBlockPageVerify.verify?.ok, true, 'v2 block verifies from page');
    assert.equal(observed.phase2.pageLaneWrite.schedule.accepted, true, 'page storage-lane write should schedule after restart/update');
    assert.equal(observed.phase2.pageLaneWrite.result?.ok, true, 'page storage-lane write should complete after restart/update');
    assert.equal(observed.phase2.pageLaneWrite.verify?.ok, true, 'page storage-lane block should verify');
    assert.equal(observed.phase2.pageLaneWrite.lane?.healthy, true, 'storage lane should remain healthy after restart/update write');
    assert.equal(observed.phase2.lockQueryAfterWrites.heldCount, 0, 'lock should not remain held after phase2 writes');
    assert.equal(observed.phase2.lockQueryAfterWrites.pendingCount, 0, 'lock should not remain pending after phase2 writes');
    assert.equal(observed.phase2.cleanupAfter.settled.ok, true, 'cleanup should settle after restart/update proof');
    assert.ok(observed.phase2.unregisterAfter.count >= 1, 'service worker unregister should remove at least one registration');
    assert.equal(observed.phase2.lockQueryFinal.heldCount, 0, 'final lock held count should be zero');
    assert.equal(observed.phase2.lockQueryFinal.pendingCount, 0, 'final lock pending count should be zero');
    assert.equal(observed.profileReap.afterKillCount, 0, 'profile process reap should leave no browser processes');

    return {
      project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
      probe_id: `${REVISION}-browser-opfs-web-lock-service-worker-restart-update-proof`,
      task_id: TASK_ID,
      status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
      purpose: 'Managed Chromium proof that a BrowserRT-compatible module Service Worker registration survives a clean browser restart with the same profile/origin, can still write and verify guarded OPFS blocks after restart, can be updated to a new script for the same scope, and leaves the guarded OPFS/Web Lock/storage-lane state clean and healthy after explicit cleanup.',
      observations: observed,
      claimsChecked: [
        'module Service Worker v1 writes and verifies a guarded OPFS block before browser restart',
        'the same origin/profile relaunch observes the persisted v1 Service Worker registration',
        'the restarted Service Worker can write another guarded OPFS block and the pre-restart block still verifies from the page',
        'registering a v2 script for the same scope activates the updated Service Worker and it writes/verifies another guarded OPFS block',
        'page-side storage-lane guarded OPFS writes still complete after restart/update with the lane healthy and zero held/pending Web Lock rows',
        'cleanup unregisters the worker, removes OPFS proof data, and reaps browser profile processes'
      ],
      nonClaims: [
        'Managed Chromium/CDP restart/update proof only; no cross-browser Service Worker lifecycle claim.',
        'Clean browser process restart with the same profile/origin is not a power-loss, OS crash, mobile/background suspension, tab discard, fetch-event, push-event, or offline lifecycle proof.',
        'Service Worker script update activation is not a claim about all browser update races or long-lived fetch/event semantics.',
        'No distributed-lock, exactly-once, Web Locks fairness/starvation freedom, OPFS fsync/durability, organic quota/eviction survival, persistent-retention, throughput, latency, SLO, automatic recovery, or production-readiness claim.'
      ]
    };
  } finally {
    if (server) await server.close().catch(() => {});
    await reapBrowserProfileProcesses(profileDir, { graceMs: 100, killMs: 250 }).catch(() => {});
    await rm(profileDir, { recursive: true, force: true }).catch(() => {});
  }
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '32000'));
const prefix = argValue(argv, '--prefix', null);
try {
  const report = await runProbe({ timeoutMs, prefix });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-service-worker-restart-update-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: errRecord(error), nonClaims: ['Failed Service Worker restart/update proof is not silently skipped; run it by explicit browser id while debugging.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_service_worker_restart_update_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
