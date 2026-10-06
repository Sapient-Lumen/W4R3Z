#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, connectBrowserCdp, openPageTarget, closePageTarget, evalJson, sleep } from './browser_cdp_fixture.mjs';

const TASK_ID = 'browser:opfs-web-lock-tab-termination-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-TAB-TERMINATION-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function errRecord(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, stack: error?.stack || null };
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

function cleanupExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true });
    const store = rt.opfsAsyncBlockStore({ name: 'tab-termination-cleanup-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'tab-termination-cleanup-guard' });
    const before = await guard.coordinator.queryLocks(guard.fullLockName);
    const cleanup = await guard.cleanupForTest();
    const settled = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 500, intervalMs: 20 });
    const snapshot = guard.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, cleanup, settled, snapshot, traceKinds });
  })()`;
}

function holderStartExpression({ prefix, lockPrefix, lockName, payload }) {
  return `(() => {
    window.__brtTabTerminationHolder = { events: [], result: null, error: null };
    const state = window.__brtTabTerminationHolder;
    const mark = (event, fields = {}) => state.events.push({ event, t: Math.round(performance.now() * 1000) / 1000, ...fields });
    state.promise = (async () => {
      try {
        mark('holder-start');
        const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
        const rt = await mod.boot({ opfsAsyncBlockStoreProof: true });
        const store = rt.opfsAsyncBlockStore({ name: 'holder-tab-store', prefix: ${JSON.stringify(prefix)} });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'holder-tab-guard' });
        mark('holder-guard-ready', { fullLockName: guard.fullLockName, available: guard.available });
        const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
        await guard.withExclusive(async () => {
          mark('holder-acquired');
          const put = await store.put(bytes, { label: 'holder-before-tab-close' });
          mark('holder-wrote', { put: { digest: put.digest, hash: put.hash, bytes: put.bytes, duplicate: put.duplicate, ref: put.ref, path: put.path } });
          await new Promise(() => {});
        }, { op: 'holder-tab-open-ended-exclusive', role: 'holder' });
        mark('holder-unexpected-release');
        state.result = { unexpectedRelease: true, traceKinds: rt.trace.snapshot().map((row) => row.kind) };
        rt.close();
      } catch (error) {
        state.error = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, stack: error?.stack || null };
        mark('holder-error', { error: state.error });
      }
    })();
    return JSON.stringify({ started: true, href: location.href });
  })()`;
}

function holderStateExpression() {
  return `JSON.stringify({ events: window.__brtTabTerminationHolder?.events || [], result: window.__brtTabTerminationHolder?.result || null, error: window.__brtTabTerminationHolder?.error || null, closed: window.closed })`;
}

function waiterStartExpression({ prefix, lockPrefix, lockName, payload }) {
  return `(() => {
    window.__brtTabTerminationWaiter = { events: [], result: null, error: null };
    const state = window.__brtTabTerminationWaiter;
    const mark = (event, fields = {}) => state.events.push({ event, t: Math.round(performance.now() * 1000) / 1000, ...fields });
    state.promise = (async () => {
      try {
        mark('waiter-start');
        const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
        const rt = await mod.boot({ opfsAsyncBlockStoreProof: true });
        const store = rt.opfsAsyncBlockStore({ name: 'waiter-main-tab-store', prefix: ${JSON.stringify(prefix)} });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'waiter-main-tab-guard' });
        mark('waiter-guard-ready', { fullLockName: guard.fullLockName, available: guard.available });
        const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
        mark('waiter-requesting');
        const put = await guard.withExclusive(async () => {
          mark('waiter-acquired');
          const result = await store.put(bytes, { label: 'waiter-after-holder-tab-close' });
          mark('waiter-wrote', { put: { digest: result.digest, hash: result.hash, bytes: result.bytes, duplicate: result.duplicate, ref: result.ref, path: result.path } });
          return result;
        }, { op: 'waiter-after-holder-tab-close', role: 'waiter' });
        const verify = await guard.verify(put.ref);
        const settled = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 1000, intervalMs: 20 });
        state.result = { put: { digest: put.digest, hash: put.hash, bytes: put.bytes, duplicate: put.duplicate, ref: put.ref, path: put.path }, verify, settled, snapshot: guard.snapshot(), traceKinds: rt.trace.snapshot().map((row) => row.kind) };
        rt.close();
        mark('waiter-done', { put: state.result.put, settled });
      } catch (error) {
        state.error = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, stack: error?.stack || null };
        mark('waiter-error', { error: state.error });
      }
    })();
    return JSON.stringify({ started: true, href: location.href });
  })()`;
}

function waiterStateExpression() {
  return `JSON.stringify({ events: window.__brtTabTerminationWaiter?.events || [], result: window.__brtTabTerminationWaiter?.result || null, error: window.__brtTabTerminationWaiter?.error || null })`;
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

function finalizeExpression({ prefix, lockPrefix, lockName, holderRef, waiterRef }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true });
    const store = rt.opfsAsyncBlockStore({ name: 'tab-termination-final-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'tab-termination-final-guard' });
    const holderVerify = await guard.verify(${JSON.stringify(holderRef)});
    const waiterVerify = await guard.verify(${JSON.stringify(waiterRef)});
    const queryBeforeCleanup = await guard.coordinator.queryLocks(guard.fullLockName);
    const cleanupAfter = await guard.cleanupForTest();
    const settledAfterCleanup = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 1000, intervalMs: 20 });
    const queryAfterCleanup = await guard.coordinator.queryLocks(guard.fullLockName);
    const snapshot = guard.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ holderVerify, waiterVerify, queryBeforeCleanup, cleanupAfter, settledAfterCleanup, queryAfterCleanup, snapshot, traceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-tab-termination-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-tab-termination';
  const lockName = options.lockName || `${REVISION}-tab-lifecycle-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const holderPayload = `holder-tab-termination-${REVISION}-${Math.random()}`;
  const waiterPayload = `waiter-tab-termination-${REVISION}-${Math.random()}`;

  const { result: observed, harness } = await runManagedBrowserPage({
    root: process.cwd(),
    pagePath: '/browser-opfs-web-lock-tab-termination.html',
    pageTitle: 'BrowserRT OPFS Web Lock tab termination proof',
    allowedPrefixes: ['src/'],
    timeoutMs: options.timeoutMs || 18000,
    stderrTerms: ['WebLock', 'OPFS', 'lock', 'target']
  }, async ({ cdp, pageUrl, cdpPort, listUrl, timeoutMs }) => {
    const browser = await connectBrowserCdp(cdpPort, timeoutMs);
    let holder = null;
    try {
      const page = await evalJson(cdp, `JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, capabilities: { opfs: typeof navigator.storage?.getDirectory === 'function', webLocks: typeof navigator.locks?.request === 'function', webLocksQuery: typeof navigator.locks?.query === 'function' } })`, timeoutMs);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName }), timeoutMs);
      holder = await openPageTarget(browser.cdp, { listUrl, url: `${pageUrl}?role=holder`, timeoutMs });
      const holderTargetInfo = { targetId: holder.targetId, url: holder.target?.url || `${pageUrl}?role=holder` };
      const holderStarted = await evalJson(holder.cdp, holderStartExpression({ prefix, lockPrefix, lockName, payload: holderPayload }), timeoutMs);
      const holderAfterWrite = await waitFor(holder.cdp, holderStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'holder-wrote')) || Boolean(state.error), { timeoutMs: 5000, label: 'holder write under lock' });
      if (holderAfterWrite.error) throw new Error(`holder failed: ${holderAfterWrite.error.message}`);
      const waiterStarted = await evalJson(cdp, waiterStartExpression({ prefix, lockPrefix, lockName, payload: waiterPayload }), timeoutMs);
      await waitFor(cdp, waiterStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'waiter-requesting')) || Boolean(state.error), { timeoutMs: 3000, label: 'waiter request' });
      await sleep(150);
      const waiterBeforeClose = await evalJson(cdp, waiterStateExpression(), timeoutMs);
      const lockQueryBeforeClose = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const closeHolder = await closePageTarget(browser.cdp, holder.targetId, timeoutMs);
      holder.cdp.close();
      holder = null;
      const waiterDone = await waitFor(cdp, waiterStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'waiter-done')) || Boolean(state.error), { timeoutMs: 6000, label: 'waiter completion after holder tab close' });
      if (waiterDone.error) throw new Error(`waiter failed: ${waiterDone.error.message}`);
      const holderWrote = holderAfterWrite.events.find((row) => row.event === 'holder-wrote');
      const waiterResult = waiterDone.result;
      const final = await evalJson(cdp, finalizeExpression({ prefix, lockPrefix, lockName, holderRef: holderWrote.put.ref, waiterRef: waiterResult.put.ref }), timeoutMs);
      const lockQueryAfterClose = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      return { page, cleanupBefore, holderTarget: holderTargetInfo, holderStarted, holderAfterWrite, waiterStarted, waiterBeforeClose, lockQueryBeforeClose, closeHolder, waiterDone, final, lockQueryAfterClose };
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
  assert.equal(typeof observed.cleanupBefore.cleanup, 'boolean', 'initial cleanup should complete as boolean deleted/no-op result');
  assert.equal(observed.cleanupBefore.settled.ok, true, 'lock should settle before proof');
  assert.ok(observed.holderAfterWrite.events.some((row) => row.event === 'holder-acquired'), 'holder should acquire lock');
  const holderWrote = observed.holderAfterWrite.events.find((row) => row.event === 'holder-wrote');
  assert.ok(holderWrote?.put?.digest, 'holder should write an OPFS block while holding lock');
  assert.equal(observed.waiterBeforeClose.events.some((row) => row.event === 'waiter-acquired'), false, 'waiter must not acquire before holder tab closes');
  assert.ok(observed.lockQueryBeforeClose.held.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'holder lock should appear held before close');
  assert.ok(observed.lockQueryBeforeClose.pending.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'waiter lock should appear pending before close');
  assert.equal(observed.closeHolder.ok, true, 'holder target should close through CDP');
  assert.ok(observed.waiterDone.events.some((row) => row.event === 'waiter-acquired'), 'waiter should acquire after holder tab close');
  assert.ok(observed.waiterDone.result?.put?.digest, 'waiter should write an OPFS block after holder closes');
  assert.equal(observed.waiterDone.result.verify.ok, true, 'waiter block should verify');
  assert.equal(observed.waiterDone.result.settled.ok, true, 'waiter lock should settle after its callback');
  assert.equal(observed.final.holderVerify.ok, true, 'holder acknowledged block should verify after holder tab closes');
  assert.equal(observed.final.waiterVerify.ok, true, 'waiter acknowledged block should verify');
  assert.equal(observed.final.cleanupAfter, true, 'final cleanup should succeed');
  assert.equal(observed.final.settledAfterCleanup.ok, true, 'locks should settle after cleanup');
  assert.equal(observed.final.queryAfterCleanup.heldCount, 0, 'final held locks should be zero');
  assert.equal(observed.final.queryAfterCleanup.pendingCount, 0, 'final pending locks should be zero');
  for (const kind of ['coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete', 'storage:opfs-web-lock-guard-op-start']) {
    assert.ok(observed.final.traceKinds.includes(kind) || observed.waiterDone.result.traceKinds.includes(kind) || observed.cleanupBefore.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-tab-termination-proof`,
    taskId: TASK_ID,
    status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium proof that a same-origin tab holding BrowserRT WebLockGuardedBlockStore exclusive OPFS mutation does not wedge peers when the tab is closed; a waiting main-page mutation acquires, writes, verifies, settles, and cleans up afterward.',
    observations: {
      prefix, lockPrefix, lockName, fullLockName,
      page: observed.page,
      cleanupBefore: observed.cleanupBefore,
      holder: { events: observed.holderAfterWrite.events, wrote: holderWrote?.put || null },
      waiterBeforeClose: observed.waiterBeforeClose,
      lockQueryBeforeClose: observed.lockQueryBeforeClose,
      closeHolder: observed.closeHolder,
      waiterDone: observed.waiterDone,
      lockQueryAfterClose: observed.lockQueryAfterClose,
      final: observed.final,
      harness
    },
    claimsChecked: [
      'same-origin held Web Lock blocks a second exclusive guarded OPFS mutation before tab close',
      'the pending guarded mutation acquires after the holder tab is closed through CDP',
      'acknowledged OPFS blocks from both holder and waiter verify after holder-tab termination',
      'normalized Web Locks query/wait helpers report no final held/pending lock rows',
      'guarded cleanup removes the proof namespace after lifecycle contention'
    ],
    nonClaims: [
      'Managed Chromium/CDP tab-close proof only; no cross-browser lifecycle or mobile/background suspension claim.',
      'No fairness, starvation freedom, exactly-once, distributed-lock, or service-worker coordination claim.',
      'No OPFS durability, fsync, power-loss, kernel-crash, organic eviction, quota, or persistent-retention claim.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-tab-termination-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: errRecord(error), nonClaims: ['Failed tab-termination probe is not a browser storage/lifecycle claim.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_tab_termination_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
