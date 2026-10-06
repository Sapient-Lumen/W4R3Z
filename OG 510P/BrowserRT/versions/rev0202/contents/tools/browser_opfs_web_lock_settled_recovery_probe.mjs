#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, connectBrowserCdp, openPageTarget, closePageTarget, evalJson, sleep } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-SETTLED-RECOVERY-PROBE.json`;
const TASK_ID = 'browser:opfs-web-lock-settled-recovery-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function errRecord(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, stack: error?.stack || null, detail: error?.detail || null };
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

function cleanupExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsWebLockSettledRecoveryProof: true });
    const store = rt.opfsAsyncBlockStore({ name: 'settled-recovery-cleanup-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'settled-recovery-cleanup-guard', lockTimeoutMs: 1000 });
    const before = await guard.queryLocks();
    const cleanup = await guard.cleanupForTest({ timeoutMs: 1000 });
    const settled = await guard.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const after = await guard.queryLocks();
    const snapshot = guard.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, cleanup, settled, after, snapshot, traceKinds });
  })()`;
}

function holderStartExpression({ prefix, lockPrefix, lockName, payload }) {
  return `(() => {
    window.__brtSettledRecoveryHolder = { events: [], result: null, error: null };
    const state = window.__brtSettledRecoveryHolder;
    const mark = (event, fields = {}) => state.events.push({ event, t: Math.round(performance.now() * 1000) / 1000, ...fields });
    state.promise = (async () => {
      let rt = null;
      try {
        mark('holder-start');
        const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
        rt = await mod.boot({ opfsWebLockSettledRecoveryProof: true, role: 'holder' });
        const store = rt.opfsAsyncBlockStore({ name: 'settled-recovery-holder-store', prefix: ${JSON.stringify(prefix)} });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'settled-recovery-holder-guard', lockTimeoutMs: 0 });
        mark('holder-guard-ready', { fullLockName: guard.fullLockName, available: guard.available });
        const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
        await guard.withExclusive(async () => {
          mark('holder-acquired');
          const put = await store.put(bytes, { label: 'holder-before-settled-recovery-close' });
          const verify = await store.verify(put.ref);
          mark('holder-wrote', { put: { digest: put.digest, hash: put.hash, bytes: put.bytes, duplicate: put.duplicate, ref: put.ref, path: put.path }, verify });
          await new Promise(() => {});
        }, { op: 'settled-recovery-open-ended-holder', role: 'holder' });
        mark('holder-unexpected-release');
        state.result = { unexpectedRelease: true, traceKinds: rt.trace.snapshot().map((row) => row.kind) };
        rt.close();
      } catch (error) {
        state.error = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, stack: error?.stack || null, detail: error?.detail || null };
        mark('holder-error', { error: state.error });
        try { rt?.close?.(); } catch {}
      }
    })();
    return JSON.stringify({ started: true, href: location.href });
  })()`;
}

function holderStateExpression() {
  return `JSON.stringify({ events: window.__brtSettledRecoveryHolder?.events || [], result: window.__brtSettledRecoveryHolder?.result || null, error: window.__brtSettledRecoveryHolder?.error || null, closed: window.closed })`;
}

function mainStartExpression({ prefix, lockPrefix, lockName, payload, lockTimeoutMs }) {
  return `(() => {
    window.__brtSettledRecoveryMain = { events: [], result: null, error: null, resources: null };
    const state = window.__brtSettledRecoveryMain;
    const mark = (event, fields = {}) => state.events.push({ event, t: Math.round(performance.now() * 1000) / 1000, ...fields });
    state.promise = (async () => {
      let rt = null;
      try {
        mark('main-start');
        const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
        rt = await mod.boot({ opfsWebLockSettledRecoveryProof: true, role: 'main' });
        const payloadText = ${JSON.stringify(payload)};
        const bytes = new TextEncoder().encode(payloadText);
        const digestBytes = await crypto.subtle.digest('SHA-256', bytes);
        const timeoutDigest = 'sha256:' + Array.from(new Uint8Array(digestBytes)).map((b) => b.toString(16).padStart(2, '0')).join('');
        const store = rt.opfsAsyncBlockStore({ name: 'settled-recovery-main-store', prefix: ${JSON.stringify(prefix)} });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'settled-recovery-main-guard', lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} });
        const scheduler = rt.crossLaneScheduler({
          label: 'settled-recovery-main-scheduler',
          lanes: [
            { id: 'storage', rank: 70, capacity: 1, quantum: 4096, maxQueuedCost: 8192 },
            { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
          ]
        });
        const adapter = rt.blockStoreLaneAdapter({ label: 'settled-recovery-main-adapter', store: guard, scheduler, lane: 'storage' });
        state.resources = { rt, guard, adapter, timeoutDigest };
        mark('main-ready', { fullLockName: guard.fullLockName, timeoutDigest });
        const scheduledTimeout = adapter.schedulePut(bytes, { id: 'browser-settled-recovery-timeout-put', priority: 'user-visible', label: 'browser-timeout-behind-holder' });
        mark('main-scheduled-timeout', { accepted: scheduledTimeout.accepted, disposition: scheduledTimeout.scheduler?.disposition || null });
        const timeoutDrain = await adapter.drain({ maxSteps: 2 });
        const timeoutResult = timeoutDrain.results.find((row) => row.opId === 'browser-settled-recovery-timeout-put') || null;
        const afterTimeout = adapter.snapshot();
        const unhealthyLane = afterTimeout.executor.scheduler.lanes.find((lane) => lane.id === 'storage') || null;
        const rejectWhileUnhealthy = adapter.schedulePut(new TextEncoder().encode('browser-reject-while-unhealthy'), { id: 'browser-reject-while-unhealthy', priority: 'user-visible', label: 'should-not-queue-before-recovery' });
        const blockedRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 120, intervalMs: 20, reason: 'browser-holder-still-active' });
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
  return `JSON.stringify({ events: window.__brtSettledRecoveryMain?.events || [], result: window.__brtSettledRecoveryMain?.result || null, error: window.__brtSettledRecoveryMain?.error || null })`;
}

function finalizeExpression({ holderRef, recoveryPayload }) {
  return `(async () => {
    const state = window.__brtSettledRecoveryMain;
    if (!state?.resources) throw new Error('settled recovery resources unavailable');
    const { rt, guard, adapter, timeoutDigest } = state.resources;
    const beforeRecoveryQuery = await guard.queryLocks();
    const settledRecovery = await adapter.recoverWhenStoreSettled({ timeoutMs: 1500, intervalMs: 20, reason: 'browser-web-lock-settled-maintenance-recovery' });
    const holderVerify = await guard.verify(${JSON.stringify(holderRef)}, { timeoutMs: 1000 });
    const timeoutPresent = await guard.has(timeoutDigest, { timeoutMs: 1000 });
    const recoveredSchedule = adapter.schedulePut(new TextEncoder().encode(${JSON.stringify(recoveryPayload)}), { id: 'browser-settled-recovery-success-put', priority: 'user-visible', label: 'browser-after-settled-recovery' });
    const recoveryDrain = await adapter.drain({ maxSteps: 3 });
    const recoveredResult = recoveryDrain.results.find((row) => row.opId === 'browser-settled-recovery-success-put') || null;
    const recoveredVerify = recoveredResult?.result?.ref ? await guard.verify(recoveredResult.result.ref, { timeoutMs: 1000 }) : null;
    const cleanupAfter = await guard.cleanupForTest({ timeoutMs: 1000 });
    const settledAfterCleanup = await guard.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const queryAfterCleanup = await guard.queryLocks();
    const finalSnapshot = adapter.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const closeTraceKinds = rt.close().map((row) => row.kind);
    return JSON.stringify({ beforeRecoveryQuery, settledRecovery, holderVerify, timeoutDigest, timeoutPresent, recoveredSchedule, recoveredResult, recoveredVerify, cleanupAfter, settledAfterCleanup, queryAfterCleanup, finalSnapshot, traceKinds, closeTraceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const started = performance.now();
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-settled-recovery-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-settled-recovery';
  const lockName = options.lockName || `${REVISION}-settled-recovery-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const lockTimeoutMs = Number(options.lockTimeoutMs || 500);
  const holderPayload = `holder-settled-recovery-${REVISION}-${Math.random()}`;
  const timeoutPayload = `timed-out-settled-recovery-${REVISION}-${Math.random()}`;
  const recoveryPayload = `recovery-after-settled-lock-${REVISION}-${Math.random()}`;

  const { result: observed, harness } = await runManagedBrowserPage({
    root: process.cwd(),
    pagePath: '/browser-opfs-web-lock-settled-recovery.html',
    pageTitle: 'BrowserRT OPFS Web Lock settled recovery proof',
    allowedPrefixes: ['src/'],
    timeoutMs: options.timeoutMs || 24000,
    stderrTerms: ['WebLock', 'OPFS', 'lock', 'settled', 'target']
  }, async ({ cdp, pageUrl, cdpPort, listUrl, timeoutMs }) => {
    const browser = await connectBrowserCdp(cdpPort, timeoutMs);
    let holder = null;
    try {
      const page = await evalJson(cdp, `JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, capabilities: { opfs: typeof navigator.storage?.getDirectory === 'function', webLocks: typeof navigator.locks?.request === 'function', webLocksQuery: typeof navigator.locks?.query === 'function', abortController: typeof AbortController === 'function' } })`, timeoutMs);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName }), timeoutMs);
      holder = await openPageTarget(browser.cdp, { listUrl, url: `${pageUrl}?role=holder`, timeoutMs });
      const holderTarget = { targetId: holder.targetId, url: holder.target?.url || `${pageUrl}?role=holder` };
      const holderStarted = await evalJson(holder.cdp, holderStartExpression({ prefix, lockPrefix, lockName, payload: holderPayload }), timeoutMs);
      const holderAfterWrite = await waitFor(holder.cdp, holderStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'holder-wrote')) || Boolean(state.error), { timeoutMs: 6000, label: 'holder write under settled-recovery lock' });
      if (holderAfterWrite.error) throw new Error(`holder failed: ${holderAfterWrite.error.message}`);

      const mainStarted = await evalJson(cdp, mainStartExpression({ prefix, lockPrefix, lockName, payload: timeoutPayload, lockTimeoutMs }), timeoutMs);
      await waitFor(cdp, mainStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'main-scheduled-timeout')) || Boolean(state.error), { timeoutMs: 2500, label: 'main scheduled timeout put' });
      await sleep(Math.min(125, Math.max(40, Math.floor(lockTimeoutMs / 4))));
      const lockQueryWhilePending = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const mainTimeoutDone = await waitFor(cdp, mainStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'main-timeout-done')) || Boolean(state.error), { timeoutMs: lockTimeoutMs + 4500, label: 'main storage-lane timeout completion' });
      if (mainTimeoutDone.error) throw new Error(`main timeout failed fatally: ${mainTimeoutDone.error.message}`);
      const holderStillHeldAfterBlockedRecovery = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const closeHolder = await closePageTarget(browser.cdp, holder.targetId, timeoutMs);
      holder.cdp.close();
      holder = null;
      await sleep(100);
      const holderWrote = holderAfterWrite.events.find((row) => row.event === 'holder-wrote');
      const final = await evalJson(cdp, finalizeExpression({ holderRef: holderWrote.put.ref, recoveryPayload }), timeoutMs);
      const lockQueryAfterClose = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      return { page, cleanupBefore, holderTarget, holderStarted, holderAfterWrite, mainStarted, lockQueryWhilePending, mainTimeoutDone, holderStillHeldAfterBlockedRecovery, closeHolder, final, lockQueryAfterClose };
    } finally {
      if (holder) {
        try { await holder.close(); } catch {}
      }
      browser.cdp.close();
    }
  });

  assert.equal(observed.page.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(observed.page.capabilities.webLocks, true, 'Web Locks must be available');
  assert.equal(observed.page.capabilities.webLocksQuery, true, 'Web Locks query must be available');
  assert.equal(observed.cleanupBefore.settled.ok, true, 'lock should settle before proof');
  const holderWrote = observed.holderAfterWrite.events.find((row) => row.event === 'holder-wrote');
  assert.ok(holderWrote?.put?.digest, 'holder tab should write acknowledged OPFS block');
  assert.equal(holderWrote.verify?.ok, true, 'holder direct verify should pass');
  assert.ok(observed.lockQueryWhilePending.held.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'holder lock should be held while storage-lane op is pending');
  assert.ok(observed.lockQueryWhilePending.pending.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'storage-lane op should appear as pending Web Lock request');
  assert.equal(observed.mainTimeoutDone.result?.timeoutResult?.error?.code, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(observed.mainTimeoutDone.result?.unhealthyLane?.healthy, false);
  assert.equal(observed.mainTimeoutDone.result?.unhealthyLane?.healthReason, 'BRT_WEB_LOCK_TIMEOUT');
  assert.equal(observed.mainTimeoutDone.result?.rejectWhileUnhealthy?.accepted, false);
  assert.equal(observed.mainTimeoutDone.result?.rejectWhileUnhealthy?.scheduler?.disposition, 'rejected-lane-unhealthy');
  assert.equal(observed.mainTimeoutDone.result?.blockedRecovery?.recovered, false);
  assert.equal(observed.mainTimeoutDone.result?.blockedRecovery?.reason, 'store-coordination-still-contended');
  assert.equal(observed.holderStillHeldAfterBlockedRecovery.heldCount, 1, 'holder should still hold lock after blocked recovery');
  assert.equal(observed.closeHolder.ok, true, 'holder target should close through CDP');
  assert.equal(observed.final.settledRecovery.recovered, true, 'settled recovery should reopen storage lane after holder tab close');
  assert.equal(observed.final.settledRecovery.recovery.healthy, true);
  assert.equal(observed.final.holderVerify.ok, true, 'holder block should verify after tab close');
  assert.equal(observed.final.timeoutPresent, false, 'timed-out candidate should remain absent');
  assert.equal(observed.final.recoveredSchedule.accepted, true, 'recovered storage-lane put should schedule');
  assert.equal(observed.final.recoveredResult?.ok, true, 'recovered storage-lane put should complete');
  assert.equal(observed.final.recoveredVerify?.ok, true, 'recovered block should verify');
  assert.equal(observed.final.cleanupAfter, true, 'cleanup should succeed');
  assert.equal(observed.final.settledAfterCleanup.ok, true, 'lock should settle after cleanup');
  assert.equal(observed.final.queryAfterCleanup.heldCount, 0);
  assert.equal(observed.final.queryAfterCleanup.pendingCount, 0);
  assert.equal(observed.lockQueryAfterClose.heldCount, 0);
  assert.equal(observed.lockQueryAfterClose.pendingCount, 0);
  for (const kind of ['block-store-lane:recover-settled-blocked', 'block-store-lane:recover-settled', 'storage:opfs-web-lock-guard-still-contended', 'storage:opfs-web-lock-guard-settled']) {
    assert.ok(observed.final.traceKinds.includes(kind) || observed.mainTimeoutDone.result.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-settled-recovery-proof`,
    task_id: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Managed Chromium proof that a BrowserRT storage lane made unhealthy by a guarded OPFS Web Lock timeout does not reopen while the holder tab still owns the lock, then reopens through explicit wait-for-settled maintenance recovery after CDP closes the holder tab and completes a verified OPFS write.',
    observations: { prefix, lockPrefix, lockName, fullLockName, lockTimeoutMs, page: observed.page, cleanupBefore: observed.cleanupBefore, holder: { target: observed.holderTarget, events: observed.holderAfterWrite.events, wrote: holderWrote?.put || null }, lockQueryWhilePending: observed.lockQueryWhilePending, mainTimeoutDone: observed.mainTimeoutDone, holderStillHeldAfterBlockedRecovery: observed.holderStillHeldAfterBlockedRecovery, closeHolder: observed.closeHolder, final: observed.final, lockQueryAfterClose: observed.lockQueryAfterClose, harness },
    claimsChecked: [
      'a real same-origin holder tab can block a storage-lane scheduled guarded OPFS put at the Web Lock boundary',
      'the blocked scheduled put times out as BRT_WEB_LOCK_TIMEOUT and marks the storage lane unhealthy',
      'settled-lock maintenance recovery refuses to reopen the lane while the holder lock remains held',
      'after CDP closes the holder tab, settled-lock maintenance recovery reopens the lane',
      'a later scheduled guarded OPFS put completes and verifies, while the timed-out candidate remains absent'
    ],
    nonClaims: [
      'Managed Chromium/CDP multi-page proof only; no cross-browser lifecycle, mobile/background suspension, or service-worker claim.',
      'Recovery is explicit maintenance-driven recovery, not autonomous background healing or a liveness theorem.',
      'Timeout is an acquisition backstop only; it does not cancel work after a lock has already been granted.',
      'No fairness, starvation freedom, exactly-once, distributed-lock, OPFS durability, fsync, power-loss, kernel-crash, organic eviction, quota, persistent-retention, throughput, latency, SLO, or production readiness claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '24000'));
const lockTimeoutMs = Number(argValue(argv, '--lock-timeout-ms', '500'));
const prefix = argValue(argv, '--prefix', null);
try {
  const report = await runProbe({ timeoutMs, lockTimeoutMs, prefix });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-settled-recovery-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: errRecord(error), nonClaims: ['Failed settled-recovery proof is not silently skipped; run it by explicit id while debugging.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_settled_recovery_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
