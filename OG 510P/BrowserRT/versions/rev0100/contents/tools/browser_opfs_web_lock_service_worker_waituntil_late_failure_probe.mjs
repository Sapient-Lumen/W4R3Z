#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, startProbeServer, evalJson, sleep, reapBrowserProfileProcesses } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-SERVICE-WORKER-WAITUNTIL-LATE-FAILURE-PROBE.json`;
const TASK_ID = 'browser:opfs-web-lock-service-worker-waituntil-late-failure-proof';
const SW_ROUTE = '/browserrt-opfs-web-lock-service-worker-waituntil-late-failure.mjs';
// event.waitUntil is called by the served Service Worker route; this browser proof validates the page-visible effect.
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
    last = await evalJson(cdp, expression, Math.min(1200, timeoutMs));
    if (predicate(last)) return last;
    await sleep(intervalMs);
  }
  throw new Error(`Timed out waiting for ${label}; last=${JSON.stringify(last).slice(0, 2000)}`);
}

function pageSummaryExpression() {
  return `JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, capabilities: { serviceWorker: 'serviceWorker' in navigator, opfs: typeof navigator.storage?.getDirectory === 'function', webLocks: typeof navigator.locks?.request === 'function', webLocksQuery: typeof navigator.locks?.query === 'function', fetch: typeof fetch === 'function', messageChannel: typeof MessageChannel === 'function' } })`;
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
    const deadline = Date.now() + 7000;
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
    const rt = await mod.boot({ opfsWebLockServiceWorkerWaitUntilLateFailureProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-waituntil-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-waituntil-${label}-guard`)}, lockTimeoutMs: 1200 });
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

function serviceWorkerStatusExpression(swRoute) {
  return `(async () => {
    const reg = await navigator.serviceWorker.getRegistration('/');
    const slots = [reg?.active, reg?.waiting, reg?.installing].filter(Boolean);
    const sw = slots.find((candidate) => candidate.scriptURL.includes(${JSON.stringify(swRoute)})) || slots[0] || navigator.serviceWorker.controller;
    if (!sw) return JSON.stringify({ ok: false, event: 'status-miss', reason: 'no-service-worker' });
    const msg = await new Promise((resolve, reject) => {
      const ch = new MessageChannel();
      const timer = setTimeout(() => reject(new Error('timed out waiting for service-worker status')), 4000);
      ch.port1.onmessage = (event) => { clearTimeout(timer); resolve(event.data); };
      sw.postMessage({ cmd: 'status' }, [ch.port2]);
    });
    return JSON.stringify({ ok: true, worker: { scriptURL: sw.scriptURL, state: sw.state }, msg });
  })()`;
}

function startWaitUntilLateFailureExpression({ prefix, lockPrefix, lockName, payload, opId, holdMs = 1600 }) {
  const params = new URLSearchParams({ prefix, lockPrefix, lockName, payload, opId, holdMs: String(holdMs), lockTimeoutMs: '0', fail: 'true', rejectWaitUntil: 'true' }).toString();
  const path = `/browserrt-sw-waituntil-late-failure?${params}`;
  return `(async () => {
    const response = await fetch(${JSON.stringify(path)}, { cache: 'no-store' });
    const body = await response.json();
    return JSON.stringify({ started: response.ok, status: response.status, header: response.headers.get('x-browserrt-service-worker-waituntil'), path: ${JSON.stringify(path)}, body, controlledBy: navigator.serviceWorker.controller?.scriptURL || null });
  })()`;
}

function pageTimeoutBehindWaitUntilExpression({ prefix, lockPrefix, lockName, payload, label = 'page-timeout-behind-service-worker-waituntil', lockTimeoutMs = 450 }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerWaitUntilLateFailureProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-waituntil-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-waituntil-${label}-guard`)}, lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} });
    const scheduler = rt.crossLaneScheduler({ label: ${JSON.stringify(`sw-waituntil-${label}-scheduler`)}, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = rt.blockStoreLaneAdapter({ label: ${JSON.stringify(`sw-waituntil-${label}-adapter`)}, store: guard, scheduler, lane: 'storage' });
    const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
    const hash = await crypto.subtle.digest('SHA-256', bytes);
    const digest = 'sha256:' + Array.from(new Uint8Array(hash)).map((b) => b.toString(16).padStart(2, '0')).join('');
    const before = await guard.queryLocks();
    const schedule = adapter.schedulePut(bytes, { id: ${JSON.stringify(`sw-waituntil-${label}-put`)}, priority: 'user-visible', label: ${JSON.stringify(label)} });
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === ${JSON.stringify(`sw-waituntil-${label}-put`)}) || null;
    const laneAfterTimeout = adapter.snapshot().executor.scheduler.lanes.find((row) => row.id === 'storage') || null;
    const followOn = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(`${label}-follow-on`)}), { id: ${JSON.stringify(`sw-waituntil-${label}-follow-on`)}, priority: 'user-visible', label: ${JSON.stringify(`${label}-follow-on`)} });
    const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 220, intervalMs: 20, reason: 'waituntil-lifecycle-recovery-while-holder-live' });
    const timeoutPresent = await store.has(digest);
    const after = await guard.queryLocks();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, schedule, drain, result, laneAfterTimeout, followOn, blockedRecovery, timeoutPresent, digest, bytes: bytes.byteLength, after, traceKinds });
  })()`;
}

function pageRecoveryAfterWaitUntilExpression({ prefix, lockPrefix, lockName, holderRef, timeoutDigest, payload, label = 'recovery-after-service-worker-waituntil' }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockServiceWorkerWaitUntilLateFailureProof: true, phase: ${JSON.stringify(label)} });
    const store = rt.opfsAsyncBlockStore({ name: ${JSON.stringify(`sw-waituntil-${label}-store`)}, prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: ${JSON.stringify(`sw-waituntil-${label}-guard`)}, lockTimeoutMs: 1200 });
    const scheduler = rt.crossLaneScheduler({ label: ${JSON.stringify(`sw-waituntil-${label}-scheduler`)}, lanes: [{ id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 }, { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }] });
    const adapter = rt.blockStoreLaneAdapter({ label: ${JSON.stringify(`sw-waituntil-${label}-adapter`)}, store: guard, scheduler, lane: 'storage' });
    const before = await guard.queryLocks();
    const holderVerify = await guard.verify(${JSON.stringify(holderRef)}, { timeoutMs: 1200 });
    const timeoutPresent = await store.has(${JSON.stringify(timeoutDigest)});
    const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 1200, intervalMs: 20, reason: 'waituntil-lifecycle-recovery-after-holder-failure' });
    const schedule = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(payload)}), { id: ${JSON.stringify(`sw-waituntil-${label}-put`)}, priority: 'user-visible', label: ${JSON.stringify(label)} });
    const drain = await adapter.drain({ maxSteps: 3 });
    const result = drain.results.find((row) => row.opId === ${JSON.stringify(`sw-waituntil-${label}-put`)}) || null;
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
  const workerVersion = `${REVISION}-waituntil-late-failure-sw`;
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-service-worker-waituntil-late-failure-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-service-worker-waituntil-late-failure';
  const lockName = options.lockName || `${REVISION}-service-worker-waituntil-late-failure-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const timeoutMs = Number(options.timeoutMs || 45000);
  const profileDir = options.profileDir || await mkdtemp(join(tmpdir(), 'browserrt-sw-waituntil-profile-'));
  const waitUntilPayload = `service-worker-waituntil-event-holder-${REVISION}-${Math.random()}`;
  const timeoutPayload = `page-timeout-candidate-behind-waituntil-${REVISION}-${Math.random()}`;
  const recoveryPayload = `page-recovery-after-service-worker-waituntil-${REVISION}-${Math.random()}`;
  const holdMs = Number(options.holdMs || 1800);
  let server = null;
  let profileReap = null;
  const routes = {
    [SW_ROUTE]: { body: versionedWorkerSource(source, workerVersion), contentType: 'text/javascript; charset=utf-8', headers: { 'Service-Worker-Allowed': '/' } }
  };
  try {
    server = await startProbeServer({ root: process.cwd(), pagePath: '/browser-opfs-web-lock-service-worker-waituntil-late-failure.html', pageTitle: 'BrowserRT OPFS Web Lock Service Worker waitUntil late failure proof', allowedPrefixes: ['src/'], routes });
    const run = await runManagedBrowserPage({
      root: process.cwd(), server, profileDir, keepProfile: true,
      pagePath: '/browser-opfs-web-lock-service-worker-waituntil-late-failure.html', pageTitle: 'BrowserRT Service Worker waitUntil late failure proof',
      timeoutMs, stderrTerms: ['ServiceWorker', 'WebLock', 'OPFS', 'waitUntil', 'lifecycle']
    }, async ({ cdp, timeoutMs: browserTimeout }) => {
      const page = await evalJson(cdp, pageSummaryExpression(), browserTimeout);
      const unregisterBefore = await evalJson(cdp, unregisterAllExpression(), browserTimeout);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'waituntil-phase-cleanup-before' }), browserTimeout);
      const registration = await evalJson(cdp, registerExpression(SW_ROUTE, workerVersion), browserTimeout);
      const startedWaitUntil = await evalJson(cdp, startWaitUntilLateFailureExpression({ prefix, lockPrefix, lockName, payload: waitUntilPayload, opId: `${REVISION}-waituntil-holder`, holdMs }), browserTimeout);
      const lockWhileWaitUntilHeld = await waitFor(cdp, lockQueryExpression(fullLockName), (q) => q.heldCount >= 1, { timeoutMs: 6000, label: 'service-worker-waituntil-held-web-lock' });
      const statusWhileHeld = await evalJson(cdp, serviceWorkerStatusExpression(SW_ROUTE), browserTimeout);
      const timeoutDigest = await evalJson(cdp, digestExpression(timeoutPayload), browserTimeout);
      const pageTimeout = await evalJson(cdp, pageTimeoutBehindWaitUntilExpression({ prefix, lockPrefix, lockName, payload: timeoutPayload, label: 'waituntil-phase-timeout', lockTimeoutMs: 450 }), browserTimeout);
      const lockAfterTimeout = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      const lockAfterWaitUntil = await waitFor(cdp, lockQueryExpression(fullLockName), (q) => q.heldCount === 0 && q.pendingCount === 0, { timeoutMs: 7000, label: 'service-worker-waituntil-lock-drain' });
      const statusAfterWaitUntil = await evalJson(cdp, serviceWorkerStatusExpression(SW_ROUTE), browserTimeout);
      const operation = (statusAfterWaitUntil.msg?.operations || []).find((row) => row.opId === `${REVISION}-waituntil-holder`) || null;
      const recovery = await evalJson(cdp, pageRecoveryAfterWaitUntilExpression({ prefix, lockPrefix, lockName, holderRef: operation?.put?.ref, timeoutDigest: timeoutDigest.digest, payload: recoveryPayload, label: 'waituntil-phase-recovery' }), browserTimeout);
      const unregisterAfter = await evalJson(cdp, unregisterAllExpression(), browserTimeout);
      const cleanupAfter = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName, label: 'waituntil-phase-cleanup-after' }), browserTimeout);
      const finalLocks = await evalJson(cdp, lockQueryExpression(fullLockName), browserTimeout);
      return { page, unregisterBefore, cleanupBefore, registration, startedWaitUntil, lockWhileWaitUntilHeld, statusWhileHeld, timeoutDigest, pageTimeout, lockAfterTimeout, lockAfterWaitUntil, statusAfterWaitUntil, operation, recovery, unregisterAfter, cleanupAfter, finalLocks };
    });

    profileReap = await reapBrowserProfileProcesses(profileDir, { graceMs: 250, killMs: 750 });
    await rm(profileDir, { recursive: true, force: true });

    assert.equal(run.result.page.capabilities.serviceWorker, true, 'Service Worker must be available');
    assert.equal(run.result.page.capabilities.fetch, true, 'fetch must be available');
    assert.equal(run.result.page.capabilities.opfs, true, 'OPFS must be available');
    assert.equal(run.result.page.capabilities.webLocks, true, 'Web Locks must be available');
    assert.ok(run.result.registration.active?.scriptURL?.includes(SW_ROUTE), 'waitUntil late-failure Service Worker must be active');
    assert.ok(run.result.registration.controller?.includes(SW_ROUTE), 'page must be controlled by the waitUntil Service Worker');
    assert.equal(run.result.startedWaitUntil.started, true, 'waitUntil route should respond successfully');
    assert.equal(run.result.startedWaitUntil.header, 'opfs-web-lock-waituntil-late-failure', 'waitUntil response should come from Service Worker route');
    assert.equal(run.result.lockWhileWaitUntilHeld.heldCount >= 1, true, 'Service Worker waitUntil work must hold guarded Web Lock after response');
    assert.equal(run.result.statusWhileHeld.msg?.operations?.some((row) => row.opId === `${REVISION}-waituntil-holder` && row.done === false), true, 'status should show waitUntil operation unfinished while lock held');
    assert.equal(run.result.pageTimeout.result?.ok, false, 'page storage-lane put should fail behind waitUntil-held lock');
    assert.equal(run.result.pageTimeout.result?.error?.code, 'BRT_WEB_LOCK_TIMEOUT', 'page timeout should be BRT_WEB_LOCK_TIMEOUT');
    assert.equal(run.result.pageTimeout.laneAfterTimeout?.healthy, false, 'storage lane should be unhealthy after waitUntil-held Web Lock timeout');
    assert.equal(run.result.pageTimeout.followOn?.accepted, false, 'follow-on storage write should be rejected while unhealthy');
    assert.equal(run.result.pageTimeout.followOn?.scheduler?.disposition, 'rejected-lane-unhealthy', 'follow-on disposition should be rejected-lane-unhealthy');
    assert.equal(run.result.pageTimeout.blockedRecovery?.recovered, false, 'recovery must be blocked while waitUntil still holds the lock');
    assert.equal(run.result.pageTimeout.blockedRecovery?.reason, 'store-coordination-still-contended', 'blocked recovery reason should be contended lock state');
    assert.equal((typeof run.result.pageTimeout.timeoutPresent === 'boolean' ? run.result.pageTimeout.timeoutPresent : run.result.pageTimeout.timeoutPresent?.present), false, 'timed-out candidate must not be present while waitUntil lock is held');
    assert.equal(run.result.lockAfterTimeout.heldCount >= 1, true, 'waitUntil should still hold the lock immediately after page timeout');
    assert.equal(run.result.lockAfterWaitUntil.heldCount, 0, 'held locks should drain after waitUntil promise settles');
    assert.equal(run.result.lockAfterWaitUntil.pendingCount, 0, 'pending locks should drain after waitUntil promise settles');
    assert.equal(run.result.operation?.done, true, 'status should retain completed waitUntil operation');
    assert.equal(run.result.operation?.ok, false, 'waitUntil operation should record its late failure');
    assert.equal(run.result.operation?.error?.code, 'BRT_SW_WAITUNTIL_LATE_FAILURE', 'waitUntil error should be classified');
    assert.equal(run.result.operation?.verify?.ok, true, 'Service Worker waitUntil work should verify its OPFS block before failing');
    assert.equal(run.result.recovery.holderVerify?.ok, true, 'page should verify waitUntil-written block after failure');
    assert.equal((typeof run.result.recovery.timeoutPresent === 'boolean' ? run.result.recovery.timeoutPresent : run.result.recovery.timeoutPresent?.present), false, 'timed-out candidate should remain absent after waitUntil failure');
    assert.equal(run.result.recovery.settledRecovery?.recovered, true, 'explicit recovery should succeed after waitUntil lock drains');
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
        waitUntilHoldMs: holdMs,
        responseStatus: run.result.startedWaitUntil.status,
        responseHeader: run.result.startedWaitUntil.header,
        lockWhileWaitUntilHeld: run.result.lockWhileWaitUntilHeld,
        statusWhileHeld: run.result.statusWhileHeld,
        timeoutCode: run.result.pageTimeout.result?.error?.code || null,
        laneHealthyAfterTimeout: run.result.pageTimeout.laneAfterTimeout?.healthy ?? null,
        followOnDisposition: run.result.pageTimeout.followOn?.scheduler?.disposition || null,
        blockedRecovery: run.result.pageTimeout.blockedRecovery,
        lockAfterTimeout: run.result.lockAfterTimeout,
        lockAfterWaitUntil: run.result.lockAfterWaitUntil,
        waitUntilOperationError: run.result.operation?.error || null,
        waitUntilBlockVerified: run.result.operation?.verify?.ok ?? false,
        timeoutPresentAfterWaitUntil: (typeof run.result.recovery.timeoutPresent === 'boolean' ? run.result.recovery.timeoutPresent : run.result.recovery.timeoutPresent?.present ?? null),
        settledRecovery: run.result.recovery.settledRecovery,
        recoveryWriteVerified: run.result.recovery.verify?.ok ?? false,
        finalLocks: run.result.finalLocks,
        profileReap
      },
      run,
      nonClaims: [
        'No cross-browser Service Worker waitUntil/Web Locks/OPFS behavior claim.',
        'No claim that waitUntil rejection automatically poisons another page runtime; this proof relies on Web Lock settled-state recovery gates.',
        'No mobile/background suspension, push/sync/offline lifecycle completeness, OPFS durability, fsync, power-loss, crash, quota, eviction, persistent-retention, fairness, exactly-once, throughput, latency, SLO, or production-readiness claim.'
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
const report = await runProbe({ timeoutMs: Number(argValue(process.argv.slice(2), '--timeout-ms', 45000)), holdMs: Number(argValue(process.argv.slice(2), '--hold-ms', 1800)) });
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
