#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage, connectBrowserCdp, openPageTarget, closePageTarget, evalJson, sleep } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-OPFS-WEB-LOCK-TAB-TIMEOUT-PROBE.json`;
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

function cleanupExpression({ prefix, lockPrefix, lockName }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockTabTimeoutProof: true });
    const store = rt.opfsAsyncBlockStore({ name: 'tab-timeout-cleanup-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'tab-timeout-cleanup-guard', lockTimeoutMs: 1000 });
    const before = await guard.coordinator.queryLocks(guard.fullLockName);
    const cleanup = await guard.cleanupForTest();
    const settled = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 1000, intervalMs: 20 });
    const after = await guard.coordinator.queryLocks(guard.fullLockName);
    const snapshot = guard.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ before, cleanup, settled, after, snapshot, traceKinds });
  })()`;
}

function holderStartExpression({ prefix, lockPrefix, lockName, payload }) {
  return `(() => {
    window.__brtTabTimeoutHolder = { events: [], result: null, error: null };
    const state = window.__brtTabTimeoutHolder;
    const mark = (event, fields = {}) => state.events.push({ event, t: Math.round(performance.now() * 1000) / 1000, ...fields });
    state.promise = (async () => {
      let rt = null;
      try {
        mark('holder-start');
        const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
        rt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockTabTimeoutProof: true });
        const store = rt.opfsAsyncBlockStore({ name: 'tab-timeout-holder-store', prefix: ${JSON.stringify(prefix)} });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'tab-timeout-holder-guard', lockTimeoutMs: 0 });
        mark('holder-guard-ready', { fullLockName: guard.fullLockName, available: guard.available });
        const bytes = new TextEncoder().encode(${JSON.stringify(payload)});
        await guard.withExclusive(async () => {
          mark('holder-acquired');
          const put = await store.put(bytes, { label: 'holder-before-tab-timeout-close' });
          const verify = await store.verify(put.ref);
          mark('holder-wrote', { put: { digest: put.digest, hash: put.hash, bytes: put.bytes, duplicate: put.duplicate, ref: put.ref, path: put.path }, verify });
          await new Promise(() => {});
        }, { op: 'holder-tab-timeout-open-ended-exclusive', role: 'holder' });
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
  return `JSON.stringify({ events: window.__brtTabTimeoutHolder?.events || [], result: window.__brtTabTimeoutHolder?.result || null, error: window.__brtTabTimeoutHolder?.error || null, closed: window.closed })`;
}

function timeoutStartExpression({ prefix, lockPrefix, lockName, payload, lockTimeoutMs }) {
  return `(() => {
    window.__brtTabTimeoutAttempt = { events: [], result: null, error: null };
    const state = window.__brtTabTimeoutAttempt;
    const mark = (event, fields = {}) => state.events.push({ event, t: Math.round(performance.now() * 1000) / 1000, ...fields });
    state.promise = (async () => {
      let rt = null;
      try {
        mark('timeout-start');
        const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
        rt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockTabTimeoutProof: true });
        const payloadText = ${JSON.stringify(payload)};
        const bytes = new TextEncoder().encode(payloadText);
        const digestBytes = await crypto.subtle.digest('SHA-256', bytes);
        const timeoutDigest = 'sha256:' + Array.from(new Uint8Array(digestBytes)).map((b) => b.toString(16).padStart(2, '0')).join('');
        const store = rt.opfsAsyncBlockStore({ name: 'tab-timeout-attempt-store', prefix: ${JSON.stringify(prefix)} });
        const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'tab-timeout-attempt-guard', lockTimeoutMs: ${JSON.stringify(lockTimeoutMs)} });
        mark('timeout-guard-ready', { fullLockName: guard.fullLockName, available: guard.available, timeoutDigest });
        mark('timeout-requesting', { timeoutDigest });
        let put = null;
        let timeoutError = null;
        try {
          put = await guard.put(bytes, { label: 'tab-timeout-candidate' });
          mark('timeout-unexpected-put', { put: { digest: put.digest, bytes: put.bytes, duplicate: put.duplicate, ref: put.ref, path: put.path } });
        } catch (error) {
          timeoutError = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null };
          mark('timeout-error', { error: timeoutError });
        }
        state.result = { timeoutDigest, put: put ? { digest: put.digest, bytes: put.bytes, duplicate: put.duplicate, ref: put.ref, path: put.path } : null, timeoutError, snapshot: guard.snapshot(), traceKinds: rt.trace.snapshot().map((row) => row.kind), trace: rt.trace.snapshot() };
        rt.close();
        mark('timeout-done', { code: timeoutError?.code || null, putDigest: put?.digest || null });
      } catch (error) {
        state.error = { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, stack: error?.stack || null, detail: error?.detail || null };
        mark('timeout-fatal', { error: state.error });
        try { rt?.close?.(); } catch {}
      }
    })();
    return JSON.stringify({ started: true, href: location.href });
  })()`;
}

function timeoutStateExpression() {
  return `JSON.stringify({ events: window.__brtTabTimeoutAttempt?.events || [], result: window.__brtTabTimeoutAttempt?.result || null, error: window.__brtTabTimeoutAttempt?.error || null })`;
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

function finalizeExpression({ prefix, lockPrefix, lockName, holderRef, timeoutDigest, recoveryPayload }) {
  return `(async () => {
    const mod = await import(new URL('/src/browserrt.mjs', location.href).href);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, webLockTabTimeoutProof: true });
    const store = rt.opfsAsyncBlockStore({ name: 'tab-timeout-final-store', prefix: ${JSON.stringify(prefix)} });
    const guard = rt.opfsWebLockGuardedBlockStore({ store, lockPrefix: ${JSON.stringify(lockPrefix)}, lockName: ${JSON.stringify(lockName)}, label: 'tab-timeout-final-guard', lockTimeoutMs: 1000 });
    const settledBefore = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 1500, intervalMs: 20 });
    const queryBeforeOps = await guard.coordinator.queryLocks(guard.fullLockName);
    const holderVerify = await guard.verify(${JSON.stringify(holderRef)});
    const timeoutPresent = await guard.has(${JSON.stringify(timeoutDigest)});
    const recoveryPut = await guard.put(new TextEncoder().encode(${JSON.stringify(recoveryPayload)}), { label: 'tab-timeout-recovery-after-holder-close' });
    const recoveryVerify = await guard.verify(recoveryPut.ref);
    const cleanupAfter = await guard.cleanupForTest();
    const settledAfterCleanup = await guard.coordinator.waitForSettled(guard.fullLockName, { timeoutMs: 1000, intervalMs: 20 });
    const queryAfterCleanup = await guard.coordinator.queryLocks(guard.fullLockName);
    const snapshot = guard.snapshot();
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ settledBefore, queryBeforeOps, holderVerify, timeoutPresent, recoveryPut: { digest: recoveryPut.digest, hash: recoveryPut.hash, bytes: recoveryPut.bytes, duplicate: recoveryPut.duplicate, ref: recoveryPut.ref, path: recoveryPut.path }, recoveryVerify, cleanupAfter, settledAfterCleanup, queryAfterCleanup, snapshot, traceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-web-lock-tab-timeout-proof`;
  const lockPrefix = options.lockPrefix || 'browserrt:opfs-web-lock-tab-timeout';
  const lockName = options.lockName || `${REVISION}-tab-timeout-mutation-lock`;
  const fullLockName = `${lockPrefix}:${lockName}`;
  const lockTimeoutMs = Number(options.lockTimeoutMs || 500);
  const holderPayload = `holder-tab-timeout-${REVISION}-${Math.random()}`;
  const timeoutPayload = `timed-out-tab-mutation-${REVISION}-${Math.random()}`;
  const recoveryPayload = `recovery-tab-timeout-${REVISION}-${Math.random()}`;

  const { result: observed, harness } = await runManagedBrowserPage({
    root: process.cwd(),
    pagePath: '/browser-opfs-web-lock-tab-timeout.html',
    pageTitle: 'BrowserRT OPFS Web Lock tab timeout proof',
    allowedPrefixes: ['src/'],
    timeoutMs: options.timeoutMs || 22000,
    stderrTerms: ['WebLock', 'OPFS', 'lock', 'timeout', 'target']
  }, async ({ cdp, pageUrl, cdpPort, listUrl, timeoutMs }) => {
    const browser = await connectBrowserCdp(cdpPort, timeoutMs);
    let holder = null;
    try {
      const page = await evalJson(cdp, `JSON.stringify({ location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext, capabilities: { opfs: typeof navigator.storage?.getDirectory === 'function', webLocks: typeof navigator.locks?.request === 'function', webLocksQuery: typeof navigator.locks?.query === 'function', abortController: typeof AbortController === 'function' } })`, timeoutMs);
      const cleanupBefore = await evalJson(cdp, cleanupExpression({ prefix, lockPrefix, lockName }), timeoutMs);
      holder = await openPageTarget(browser.cdp, { listUrl, url: `${pageUrl}?role=holder`, timeoutMs });
      const holderTarget = { targetId: holder.targetId, url: holder.target?.url || `${pageUrl}?role=holder` };
      const holderStarted = await evalJson(holder.cdp, holderStartExpression({ prefix, lockPrefix, lockName, payload: holderPayload }), timeoutMs);
      const holderAfterWrite = await waitFor(holder.cdp, holderStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'holder-wrote')) || Boolean(state.error), { timeoutMs: 6000, label: 'holder write under tab lock' });
      if (holderAfterWrite.error) throw new Error(`holder failed: ${holderAfterWrite.error.message}`);

      const timeoutStarted = await evalJson(cdp, timeoutStartExpression({ prefix, lockPrefix, lockName, payload: timeoutPayload, lockTimeoutMs }), timeoutMs);
      await waitFor(cdp, timeoutStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'timeout-requesting')) || Boolean(state.error), { timeoutMs: 2000, label: 'timeout request queued' });
      await sleep(Math.min(125, Math.max(40, Math.floor(lockTimeoutMs / 4))));
      const lockQueryWhilePending = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const timeoutDone = await waitFor(cdp, timeoutStateExpression(), (state) => Boolean(state.events?.some((row) => row.event === 'timeout-done')) || Boolean(state.error), { timeoutMs: lockTimeoutMs + 4000, label: 'tab timeout completion' });
      if (timeoutDone.error) throw new Error(`timeout attempt failed fatally: ${timeoutDone.error.message}`);
      const holderStillHeldAfterTimeout = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      const closeHolder = await closePageTarget(browser.cdp, holder.targetId, timeoutMs);
      holder.cdp.close();
      holder = null;
      await sleep(100);
      const holderWrote = holderAfterWrite.events.find((row) => row.event === 'holder-wrote');
      const final = await evalJson(cdp, finalizeExpression({ prefix, lockPrefix, lockName, holderRef: holderWrote.put.ref, timeoutDigest: timeoutDone.result.timeoutDigest, recoveryPayload }), timeoutMs);
      const lockQueryAfterClose = await evalJson(cdp, lockQueryExpression(fullLockName), timeoutMs);
      return { page, cleanupBefore, holderTarget, holderStarted, holderAfterWrite, timeoutStarted, lockQueryWhilePending, timeoutDone, holderStillHeldAfterTimeout, closeHolder, final, lockQueryAfterClose };
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
  assert.equal(observed.page.capabilities.abortController, true, 'AbortController must be available');
  assert.equal(observed.cleanupBefore.settled.ok, true, 'lock should settle before proof');
  assert.ok(observed.holderAfterWrite.events.some((row) => row.event === 'holder-acquired'), 'holder tab should acquire lock');
  const holderWrote = observed.holderAfterWrite.events.find((row) => row.event === 'holder-wrote');
  assert.ok(holderWrote?.put?.digest, 'holder tab should write acknowledged OPFS block');
  assert.equal(holderWrote.verify?.ok, true, 'holder direct verify should pass before tab close');
  assert.ok(observed.lockQueryWhilePending.held.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'holder lock should appear held while timeout request is pending');
  assert.ok(observed.lockQueryWhilePending.pending.some((row) => row.name === fullLockName && row.mode === 'exclusive'), 'timed request should appear pending while holder tab is open');
  assert.equal(observed.timeoutDone.result?.timeoutError?.code, 'BRT_WEB_LOCK_TIMEOUT', 'main-page guarded put must time out behind holder tab');
  assert.equal(observed.timeoutDone.result?.put, null, 'timed-out tab mutation must not report put success');
  assert.ok(observed.timeoutDone.result?.traceKinds?.includes('coord:web-lock-timeout'), 'timeout trace should be emitted');
  assert.equal(observed.holderStillHeldAfterTimeout.heldCount, 1, 'holder tab should still hold lock after timeout fires');
  assert.equal(observed.closeHolder.ok, true, 'holder target should close through CDP');
  assert.equal(observed.final.settledBefore.ok, true, 'lock should settle after holder tab close');
  assert.equal(observed.final.holderVerify.ok, true, 'holder acknowledged block should verify after close');
  assert.equal(observed.final.timeoutPresent, false, 'timed-out candidate block should not appear after holder close');
  assert.equal(observed.final.recoveryVerify.ok, true, 'recovery write should verify after holder close');
  assert.equal(observed.final.cleanupAfter, true, 'final cleanup should succeed');
  assert.equal(observed.final.settledAfterCleanup.ok, true, 'locks should settle after cleanup');
  assert.equal(observed.final.queryAfterCleanup.heldCount, 0, 'final held locks should be zero');
  assert.equal(observed.final.queryAfterCleanup.pendingCount, 0, 'final pending locks should be zero');
  assert.equal(observed.lockQueryAfterClose.heldCount, 0, 'post-close held locks should be zero');
  assert.equal(observed.lockQueryAfterClose.pendingCount, 0, 'post-close pending locks should be zero');
  for (const kind of ['coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete', 'storage:opfs-web-lock-guard-op-error']) {
    assert.ok(observed.final.traceKinds.includes(kind) || observed.timeoutDone.result.traceKinds.includes(kind) || observed.cleanupBefore.traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-web-lock-tab-timeout-proof`,
    task_id: 'browser:opfs-web-lock-tab-timeout-proof',
    status: 'passed', generatedAt: new Date().toISOString(),
    purpose: 'Managed Chromium proof that a main-page BrowserRT guarded OPFS mutation pending behind a same-origin holder tab times out via Web Locks AbortSignal, leaves no OPFS candidate block, keeps the holder lock intact until CDP closes the holder tab, then recovers with verified OPFS writes and no held/pending locks.',
    observations: { prefix, lockPrefix, lockName, fullLockName, lockTimeoutMs, page: observed.page, cleanupBefore: observed.cleanupBefore, holder: { target: observed.holderTarget, events: observed.holderAfterWrite.events, wrote: holderWrote?.put || null }, lockQueryWhilePending: observed.lockQueryWhilePending, timeoutDone: observed.timeoutDone, holderStillHeldAfterTimeout: observed.holderStillHeldAfterTimeout, closeHolder: observed.closeHolder, final: observed.final, lockQueryAfterClose: observed.lockQueryAfterClose, harness },
    claimsChecked: [
      'a same-origin holder tab can hold BrowserRT WebLockGuardedBlockStore exclusive OPFS mutation lock while writing a verified block',
      'a main-page guarded OPFS put pending on that held tab lock is visible as pending and aborts as BRT_WEB_LOCK_TIMEOUT',
      'the timed-out candidate digest is absent after the holder tab is closed',
      'the holder acknowledged block remains readable/verifiable after tab close',
      'a later guarded OPFS put recovers and navigator.locks query/wait helpers settle to zero held/pending rows'
    ],
    nonClaims: [
      'Managed Chromium/CDP multi-page proof only; no cross-browser lifecycle, mobile/background suspension, or service-worker claim.',
      'Timeout is an acquisition backstop only; it does not cancel work after a lock has already been granted.',
      'No fairness, starvation freedom, exactly-once, distributed-lock, OPFS durability, fsync, power-loss, kernel-crash, organic eviction, quota, persistent-retention, or production readiness claim.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '22000'));
const lockTimeoutMs = Number(argValue(argv, '--lock-timeout-ms', '500'));
const prefix = argValue(argv, '--prefix', null);
try {
  const report = await runProbe({ timeoutMs, lockTimeoutMs, prefix });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-web-lock-tab-timeout-proof`, task_id: 'browser:opfs-web-lock-tab-timeout-proof', status: 'failed', generatedAt: new Date().toISOString(), error: errRecord(error), nonClaims: ['Failed tab-timeout proof is not silently skipped; run it by explicit id while debugging.'] };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[browser_opfs_web_lock_tab_timeout_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
