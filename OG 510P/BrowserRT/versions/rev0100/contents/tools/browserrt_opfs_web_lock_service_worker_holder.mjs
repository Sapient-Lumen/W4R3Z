// BrowserRT managed-browser probe service worker.
// Holds or briefly uses a real Web Lock around real OPFS content-addressed
// writes so page-side storage-lane lifecycle boundaries can be proved.

import { createOpfsAsyncBlockStore } from '../src/opfs-block-store.mjs';
import { createWebLockGuardedBlockStore } from '../src/opfs-web-lock-guarded-block-store.mjs';

const BRT_SW_VERSION = 'browserrt-service-worker-holder-v1';

const state = {
  holds: new Map(),
  operations: [],
  seq: 0
};

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
}

function timeout(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function describeError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail || null, stack: error?.stack || null };
}

function reply(port, payload) {
  try { port?.postMessage(payload); } catch {}
}

function bytesFromText(text) {
  return new TextEncoder().encode(String(text ?? ''));
}

function workerIdentity() {
  return { version: BRT_SW_VERSION, scriptURL: self.location?.href || null, scope: self.registration?.scope || null };
}

function createGuard(message, suffix = 'op') {
  const prefix = message.prefix || 'browserrt/service-worker-lifecycle-proof';
  const lockPrefix = message.lockPrefix || 'browserrt:opfs-web-lock-service-worker-lifecycle';
  const lockName = message.lockName || 'service-worker-holder-lock';
  const labelPart = String(message.holdId || message.opId || suffix).replace(/[^a-zA-Z0-9_.:-]+/g, '-');
  const store = createOpfsAsyncBlockStore({ name: `service-worker-store-${labelPart}`, prefix });
  const guard = createWebLockGuardedBlockStore({ store, lockPrefix, lockName, label: `service-worker-guard-${labelPart}`, lockTimeoutMs: Number(message.lockTimeoutMs || 0) });
  return { store, guard, prefix, lockPrefix, lockName };
}

async function handleHold(message, port) {
  const holdId = message.holdId || `sw-hold-${++state.seq}`;
  const payload = message.payload || `service-worker-holder-payload-${holdId}`;
  const { store, guard, prefix, lockPrefix, lockName } = createGuard({ ...message, holdId }, 'hold');
  const release = deferred();
  const done = deferred();
  const record = { holdId, prefix, lockPrefix, lockName, fullLockName: guard.fullLockName, payloadBytes: bytesFromText(payload).byteLength, startedAt: Date.now(), ready: false, released: false, releaseRequested: false, releaseReason: null, done: false, release, doneSignal: done };
  state.holds.set(holdId, record);
  try {
    await guard.withExclusive(async () => {
      const put = await store.put(bytesFromText(payload), { label: `service-worker-holder-${holdId}` });
      const verify = await store.verify(put.ref);
      Object.assign(record, { ready: true, put, verify, acquiredAt: Date.now(), snapshot: guard.snapshot() });
      reply(port, { ok: true, event: 'holding', holdId, identity: workerIdentity(), fullLockName: guard.fullLockName, put, verify, snapshot: guard.snapshot(), capabilities: { webLocks: typeof self.navigator?.locks?.request === 'function', opfs: typeof self.navigator?.storage?.getDirectory === 'function' } });
      const reason = await release.promise;
      Object.assign(record, { released: true, releaseReason: reason || 'release-requested', releasedAt: Date.now() });
    }, { op: 'service-worker-lifecycle-holder', role: 'service-worker', holdId, releasable: true });
    Object.assign(record, { done: true, finishedAt: Date.now(), finalSnapshot: guard.snapshot() });
    done.resolve(record);
    reply(port, { ok: true, event: 'released', holdId, fullLockName: guard.fullLockName, put: record.put, verify: record.verify, releasedAt: record.releasedAt, finishedAt: record.finishedAt, snapshot: guard.snapshot() });
  } catch (error) {
    Object.assign(record, { done: true, error: describeError(error), finishedAt: Date.now() });
    done.reject(error);
    reply(port, { ok: false, event: 'holder-error', holdId, error: describeError(error) });
    throw error;
  } finally {
    record.release = null;
    record.doneSignal = null;
  }
}

async function handleRelease(message, port) {
  const holdId = message.holdId;
  const record = holdId ? state.holds.get(holdId) : Array.from(state.holds.values()).find((row) => row.ready && !row.released && !row.done);
  if (!record) {
    reply(port, { ok: false, event: 'release-miss', holdId: holdId || null, knownHoldIds: Array.from(state.holds.keys()) });
    return;
  }
  if (record.done) {
    reply(port, { ok: true, event: 'already-released', holdId: record.holdId, releasedAt: record.releasedAt || null, finishedAt: record.finishedAt || null });
    return;
  }
  record.releaseRequested = true;
  record.releaseRequestedAt = Date.now();
  record.releaseReason = message.reason || 'release-command';
  record.release?.resolve(record.releaseReason);
  let completed = false;
  try {
    const result = await Promise.race([
      record.doneSignal?.promise.then(() => ({ done: true })),
      timeout(Math.max(1, Number(message.timeoutMs || 2000))).then(() => ({ done: false }))
    ]);
    completed = result.done === true;
  } catch {
    completed = true;
  }
  reply(port, { ok: completed, event: completed ? 'release-complete' : 'release-timeout', holdId: record.holdId, fullLockName: record.fullLockName, releaseRequestedAt: record.releaseRequestedAt, releasedAt: record.releasedAt || null, finishedAt: record.finishedAt || null, done: record.done === true });
}

async function handlePutOnce(message, port) {
  const opId = message.opId || `sw-put-${++state.seq}`;
  const payload = message.payload || `service-worker-put-once-payload-${opId}`;
  const { guard } = createGuard({ ...message, opId }, 'put');
  const queryBefore = await guard.queryLocks();
  const put = await guard.put(bytesFromText(payload), { label: `service-worker-put-once-${opId}`, serviceWorkerRestartUpdate: true });
  const verify = await guard.verify(put.ref);
  const settled = await guard.waitForSettled({ timeoutMs: Number(message.settleTimeoutMs || 1000), intervalMs: 20 });
  const queryAfter = await guard.queryLocks();
  const snapshot = guard.snapshot();
  const row = { opId, event: 'put-once', digest: put.digest, bytes: put.bytes, version: BRT_SW_VERSION, at: Date.now() };
  state.operations.push(row);
  reply(port, {
    ok: true,
    event: 'put-once',
    opId,
    identity: workerIdentity(),
    fullLockName: guard.fullLockName,
    put,
    verify,
    settled,
    queryBefore,
    queryAfter,
    snapshot,
    operation: row,
    capabilities: {
      webLocks: typeof self.navigator?.locks?.request === 'function',
      webLocksQuery: typeof self.navigator?.locks?.query === 'function',
      opfs: typeof self.navigator?.storage?.getDirectory === 'function'
    }
  });
}

async function handleStatus(_message, port) {
  reply(port, { ok: true, event: 'status', identity: workerIdentity(), holds: Array.from(state.holds.values()).map((row) => ({ ...row, release: undefined, doneSignal: undefined, snapshot: undefined })), operations: state.operations.slice(-20) });
}

async function handleSkipWaiting(message, port) {
  const before = workerIdentity();
  try {
    await self.skipWaiting();
    reply(port, { ok: true, event: 'skip-waiting-requested', identity: before, reason: message.reason || null });
  } catch (error) {
    reply(port, { ok: false, event: 'skip-waiting-error', identity: before, error: describeError(error) });
    throw error;
  }
}


async function handleFetchLifecycleRequest(event) {
  const url = new URL(event.request.url);
  if (url.pathname !== '/browserrt-sw-fetch-lifecycle') return null;
  const opId = url.searchParams.get('opId') || `sw-fetch-${++state.seq}`;
  const holdMs = Math.max(0, Math.min(10000, Number(url.searchParams.get('holdMs') || 1200)));
  const payload = url.searchParams.get('payload') || `service-worker-fetch-payload-${opId}`;
  const message = {
    opId,
    prefix: url.searchParams.get('prefix') || undefined,
    lockPrefix: url.searchParams.get('lockPrefix') || undefined,
    lockName: url.searchParams.get('lockName') || undefined,
    lockTimeoutMs: Number(url.searchParams.get('lockTimeoutMs') || 0)
  };
  const { store, guard, prefix, lockPrefix, lockName } = createGuard(message, 'fetch');
  const record = { opId, event: 'fetch-hold', prefix, lockPrefix, lockName, fullLockName: guard.fullLockName, holdMs, payloadBytes: bytesFromText(payload).byteLength, startedAt: Date.now(), acquiredAt: null, releasedAt: null, finishedAt: null };
  state.operations.push(record);
  const queryBefore = await guard.queryLocks();
  let put = null;
  let verify = null;
  let snapshotWhileHeld = null;
  await guard.withExclusive(async () => {
    record.acquiredAt = Date.now();
    put = await store.put(bytesFromText(payload), { label: `service-worker-fetch-${opId}` });
    verify = await store.verify(put.ref);
    snapshotWhileHeld = guard.snapshot();
    record.digest = put.digest;
    record.bytes = put.bytes;
    record.verifyOk = verify.ok === true;
    await timeout(holdMs);
    record.releasedAt = Date.now();
  }, { op: 'service-worker-fetch-lifecycle-holder', role: 'service-worker-fetch', opId, holdMs, releasable: false });
  record.finishedAt = Date.now();
  const settled = await guard.waitForSettled({ timeoutMs: Math.max(500, Number(url.searchParams.get('settleTimeoutMs') || 1500)), intervalMs: 20 });
  const queryAfter = await guard.queryLocks();
  const body = JSON.stringify({
    ok: true,
    event: 'fetch-hold-complete',
    opId,
    identity: workerIdentity(),
    fullLockName: guard.fullLockName,
    holdMs,
    put,
    verify,
    queryBefore,
    snapshotWhileHeld,
    settled,
    queryAfter,
    operation: { ...record },
    capabilities: {
      webLocks: typeof self.navigator?.locks?.request === 'function',
      webLocksQuery: typeof self.navigator?.locks?.query === 'function',
      opfs: typeof self.navigator?.storage?.getDirectory === 'function'
    }
  });
  return new Response(body, { status: 200, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-BrowserRT-Service-Worker-Fetch': 'opfs-web-lock-lifecycle' } });
}


function handleWaitUntilLateFailureRequest(event) {
  const url = new URL(event.request.url);
  if (url.pathname !== '/browserrt-sw-waituntil-late-failure') return null;
  const opId = url.searchParams.get('opId') || `sw-waituntil-${++state.seq}`;
  const holdMs = Math.max(0, Math.min(10000, Number(url.searchParams.get('holdMs') || 1200)));
  const failAfterHold = url.searchParams.get('fail') !== 'false';
  const rejectWaitUntil = url.searchParams.get('rejectWaitUntil') !== 'false';
  const payload = url.searchParams.get('payload') || `service-worker-waituntil-payload-${opId}`;
  const message = {
    opId,
    prefix: url.searchParams.get('prefix') || undefined,
    lockPrefix: url.searchParams.get('lockPrefix') || undefined,
    lockName: url.searchParams.get('lockName') || undefined,
    lockTimeoutMs: Number(url.searchParams.get('lockTimeoutMs') || 0)
  };
  const { store, guard, prefix, lockPrefix, lockName } = createGuard(message, 'waituntil');
  const record = {
    opId,
    event: 'waituntil-late-failure',
    prefix,
    lockPrefix,
    lockName,
    fullLockName: guard.fullLockName,
    holdMs,
    failAfterHold,
    rejectWaitUntil,
    payloadBytes: bytesFromText(payload).byteLength,
    responseAt: Date.now(),
    startedAt: Date.now(),
    acquiredAt: null,
    releasedAt: null,
    finishedAt: null,
    done: false,
    ok: null,
    error: null
  };
  state.operations.push(record);
  const waitWork = (async () => {
    try {
      record.queryBefore = await guard.queryLocks();
      await guard.withExclusive(async () => {
        record.acquiredAt = Date.now();
        const put = await store.put(bytesFromText(payload), { label: `service-worker-waituntil-${opId}` });
        const verify = await store.verify(put.ref);
        record.put = put;
        record.verify = verify;
        record.digest = put.digest;
        record.bytes = put.bytes;
        record.verifyOk = verify.ok === true;
        record.snapshotWhileHeld = guard.snapshot();
        await timeout(holdMs);
        record.releasedAt = Date.now();
        if (failAfterHold) {
          const error = new Error(`Service Worker waitUntil late failure for ${opId}`);
          error.name = 'BrowserRTServiceWorkerWaitUntilError';
          error.code = 'BRT_SW_WAITUNTIL_LATE_FAILURE';
          error.detail = { opId, holdMs, afterResponse: true, digest: put.digest };
          throw error;
        }
      }, { op: 'service-worker-waituntil-late-failure-holder', role: 'service-worker-waituntil', opId, holdMs, waitUntil: true, failAfterHold });
      record.ok = true;
      record.eventResult = 'waituntil-complete';
    } catch (error) {
      record.ok = false;
      record.error = describeError(error);
      record.eventResult = 'waituntil-rejected';
      if (rejectWaitUntil) throw error;
    } finally {
      record.done = true;
      record.finishedAt = Date.now();
      try { record.settled = await guard.waitForSettled({ timeoutMs: Math.max(500, Number(url.searchParams.get('settleTimeoutMs') || 1500)), intervalMs: 20 }); } catch (error) { record.settledError = describeError(error); }
      try { record.queryAfter = await guard.queryLocks(); } catch (error) { record.queryAfterError = describeError(error); }
    }
  })();
  const body = JSON.stringify({
    ok: true,
    event: 'waituntil-started',
    opId,
    identity: workerIdentity(),
    fullLockName: guard.fullLockName,
    holdMs,
    failAfterHold,
    rejectWaitUntil,
    responseAt: record.responseAt,
    capabilities: {
      webLocks: typeof self.navigator?.locks?.request === 'function',
      webLocksQuery: typeof self.navigator?.locks?.query === 'function',
      opfs: typeof self.navigator?.storage?.getDirectory === 'function'
    }
  });
  return {
    response: new Response(body, { status: 200, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-BrowserRT-Service-Worker-WaitUntil': 'opfs-web-lock-waituntil-late-failure' } }),
    wait: waitWork
  };
}

self.addEventListener('install', (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('message', (event) => {
  const message = event.data || {};
  const port = event.ports && event.ports[0];
  const work = (async () => {
    try {
      if (message.cmd === 'hold') return await handleHold(message, port);
      if (message.cmd === 'release') return await handleRelease(message, port);
      if (message.cmd === 'put-once') return await handlePutOnce(message, port);
      if (message.cmd === 'status') return await handleStatus(message, port);
      if (message.cmd === 'skip-waiting') return await handleSkipWaiting(message, port);
      reply(port, { ok: false, event: 'unknown-command', command: message.cmd || null });
    } catch (error) {
      reply(port, { ok: false, event: 'error', error: describeError(error) });
      throw error;
    }
  })();
  event.waitUntil(work);
});


self.addEventListener('fetch', (event) => {
  const waitUntil = handleWaitUntilLateFailureRequest(event);
  if (waitUntil) {
    event.waitUntil(waitUntil.wait);
    event.respondWith(waitUntil.response);
    return;
  }
  const work = handleFetchLifecycleRequest(event).catch((error) => new Response(JSON.stringify({ ok: false, event: 'fetch-error', error: describeError(error) }), { status: 500, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' } }));
  event.respondWith((async () => {
    const response = await work;
    if (response) return response;
    return fetch(event.request);
  })());
});
