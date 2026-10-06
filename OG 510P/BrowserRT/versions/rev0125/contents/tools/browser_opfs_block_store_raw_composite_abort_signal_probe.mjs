#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'browser:opfs-block-store-raw-composite-abort-signal-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, guardedPrefix, payloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      webLocksQuery: typeof navigator.locks?.query === 'function',
      abortController: typeof AbortController === 'function',
      abortSignalAny: typeof AbortSignal?.any === 'function',
      fileSystemFileHandle: typeof FileSystemFileHandle === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsRawCompositeAbortSignalProof: true, opfsAsyncBlockStoreProof: true, opfsWebLocksProof: true, browserCdpHarness: true });
    const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null } }; }
    };
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const prefixParts = String(${JSON.stringify(prefix)}).split('/').filter(Boolean);
    const openPrefix = async (suffix = '', create = false) => {
      let dir = await navigator.storage.getDirectory();
      const parts = suffix ? [...prefixParts, ...String(suffix).split('/').filter(Boolean)] : prefixParts;
      for (const part of parts) dir = await dir.getDirectoryHandle(part, { create });
      return dir;
    };
    const treeSummary = async (suffix = '') => {
      try {
        const dir = await openPrefix(suffix, false);
        let dirCount = 0; let fileCount = 0; let byteCount = 0; const files = [];
        const walk = async (node, path = '') => {
          for await (const [name, handle] of node.entries()) {
            const childPath = path ? path + '/' + name : name;
            if (handle.kind === 'directory') { dirCount += 1; await walk(handle, childPath); }
            else if (handle.kind === 'file') { const file = await handle.getFile(); fileCount += 1; byteCount += file.size; files.push({ path: childPath, bytes: file.size }); }
          }
        };
        await walk(dir);
        return { exists: true, dirCount, fileCount, byteCount, files };
      } catch (error) {
        if (error?.name === 'NotFoundError') return { exists: false, dirCount: 0, fileCount: 0, byteCount: 0, files: [] };
        throw error;
      }
    };

    const raw = rt.opfsAsyncBlockStore({ name: 'browser-raw-composite-abort-store', prefix: ${JSON.stringify(prefix)} + '/raw', writeBudgetGuard: false });
    const cleanupBefore = await raw.cleanupForTest({ signal: null }).catch(() => false);
    const liveSignal = new AbortController();
    const preAborted = new AbortController();
    preAborted.abort(new Error('browser secondary abortSignal canceled before raw put'));
    const rejectedPrePut = await capture('browser-pre-aborted-abortSignal-with-live-signal-put', () => raw.put(payload, { label: 'browser-pre-aborted-abortSignal-with-live-signal-put' }, { signal: liveSignal.signal, abortSignal: preAborted.signal }));
    const invalidSibling = await capture('browser-invalid-abortSignal-with-valid-signal-put', () => raw.put(payload, { label: 'browser-invalid-abortSignal-with-valid-signal-put' }, { signal: liveSignal.signal, abortSignal: { aborted: false } }));
    const snapshotAfterRejected = raw.snapshot();
    const treeAfterRejected = await treeSummary('raw');

    const normalPut = await raw.put(payload, { label: 'browser-raw-composite-seed' }, { signal: null, abortSignal: null });
    const normalRead = await raw.get(normalPut.ref, { signal: null, abortSignal: null });
    const normalVerify = await raw.verify(normalPut.ref, { signal: null, abortSignal: null });
    const readLive = new AbortController();
    const readAbort = new AbortController();
    readAbort.abort('browser secondary abortSignal canceled read');
    const rejectedGet = await capture('browser-pre-aborted-abortSignal-with-live-signal-get', () => raw.get(normalPut.ref, { signal: readLive.signal, abortSignal: readAbort.signal }));

    const midStore = rt.opfsAsyncBlockStore({ name: 'browser-raw-composite-midwrite-store', prefix: ${JSON.stringify(prefix)} + '/midwrite', writeBudgetGuard: false });
    const cleanupMidBefore = await midStore.cleanupForTest({ signal: null }).catch(() => false);
    const primary = new AbortController();
    const secondary = new AbortController();
    const originalCreateWritable = FileSystemFileHandle.prototype.createWritable;
    const patchStats = { createWritableCalls: 0, abortsIssued: 0, writeCalls: 0, closeCalls: 0, abortCalls: 0 };
    FileSystemFileHandle.prototype.createWritable = async function patchedCreateWritable(options = {}) {
      patchStats.createWritableCalls += 1;
      const writable = await originalCreateWritable.call(this, options);
      secondary.abort(new Error('browser secondary abortSignal fired after createWritable before write'));
      patchStats.abortsIssued += 1;
      await sleep(20);
      return {
        async write(value) { patchStats.writeCalls += 1; return await writable.write(value); },
        async close() { patchStats.closeCalls += 1; return await writable.close(); },
        async abort(reason) { patchStats.abortCalls += 1; return typeof writable.abort === 'function' ? await writable.abort(reason) : undefined; },
        async seek(position) { return typeof writable.seek === 'function' ? await writable.seek(position) : undefined; },
        async truncate(size) { return typeof writable.truncate === 'function' ? await writable.truncate(size) : undefined; }
      };
    };
    let rejectedMidWrite;
    try {
      // Alias retained for static current-office checks: browser-secondary-abortSignal-mid-write-put.
      rejectedMidWrite = await capture('browser-secondary-abortSignal-before-write-put', () => midStore.put(new TextEncoder().encode('browser raw composite midwrite ' + Date.now()), { label: 'browser-secondary-abortSignal-before-write-put' }, { signal: primary.signal, abortSignal: secondary.signal }));
    } finally {
      FileSystemFileHandle.prototype.createWritable = originalCreateWritable;
    }
    const midSnapshot = midStore.snapshot();
    const midTree = await treeSummary('midwrite');

    const guarded = rt.opfsWebLockGuardedBlockStore({ prefix: ${JSON.stringify(guardedPrefix)}, label: 'browser-raw-composite-guarded-smoke', lockPrefix: 'browserrt:${REVISION}:raw-composite', lockName: '${REVISION}-raw-composite-smoke', lockTimeoutMs: 500 });
    const guardedCleanupBefore = await guarded.cleanupForTest({ timeoutMs: 500 }).catch(() => false);
    const guardedPut = await guarded.put(payload, { label: 'browser-raw-composite-guarded-smoke' }, { signal: null, abortSignal: null, timeoutMs: 500, writeBudgetGuard: false });
    const guardedVerify = await guarded.verify(guardedPut.ref, { timeoutMs: 500, signal: null, abortSignal: null });
    const guardedRead = await guarded.get(guardedPut.ref, { timeoutMs: 500, signal: null, abortSignal: null });
    const guardedCleanupAfter = await guarded.cleanupForTest({ timeoutMs: 500 });
    const guardedSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });

    const cleanupAfter = await raw.cleanupForTest({ signal: null }).catch(() => false);
    const cleanupMidAfter = await midStore.cleanupForTest({ signal: null }).catch(() => false);
    const locksRaw = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const locksAfter = locksRaw ? { heldCount: locksRaw.held?.length ?? null, pendingCount: locksRaw.pending?.length ?? null, held: locksRaw.held, pending: locksRaw.pending } : null;
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, cleanupBefore, rejectedPrePut, invalidSibling, snapshotAfterRejected, treeAfterRejected, normalPut: { digest: normalPut.digest, bytes: normalPut.bytes, ref: normalPut.ref, path: normalPut.path }, normalReadSameBytes: sameBytes(normalRead, payload), normalVerify, rejectedGet, cleanupMidBefore, rejectedMidWrite, patchStats, midSnapshot, midTree, guardedCleanupBefore, guardedPut: { digest: guardedPut.digest, bytes: guardedPut.bytes, ref: guardedPut.ref, path: guardedPut.path }, guardedVerify, guardedReadSameBytes: sameBytes(guardedRead, payload), guardedCleanupAfter, guardedSettled, cleanupAfter, cleanupMidAfter, locksAfter, traceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-raw-composite-abort-signal-proof`;
  const guardedPrefix = options.guardedPrefix || `browserrt/${REVISION}/opfs-block-store-raw-composite-abort-signal-guarded-smoke`;
  const payload = options.payload || `BrowserRT ${REVISION} browser raw OPFS composite abort signal proof ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 18000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-raw-composite-abort-signal-probe.html',
    pageTitle: 'BrowserRT OPFS raw composite abort signal probe',
    profilePrefix: 'browserrt-opfs-block-store-raw-composite-abort-signal-',
    stderrTerms: ['opfs', 'abort', 'signal', 'storage']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, guardedPrefix, payload), timeoutMs);
    mark('browser-opfs-block-store-raw-composite-abort-signal-eval', started);
    out._pageUrl = pageUrl;
    return out;
  });

  assert.equal(observed.project, 'BrowserRT');
  assert.equal(observed.revision, REVISION);
  assert.equal(observed.version, VERSION);
  assert.equal(observed.page.location, observed._pageUrl);
  assert.equal(observed.page.crossOriginIsolated, true);
  assert.equal(observed.page.isSecureContext, true);
  assert.equal(observed.capabilities.opfs, true, 'OPFS must be available');
  assert.equal(observed.capabilities.abortController, true, 'AbortController must be available');
  assert.equal(observed.rejectedPrePut.ok, false, 'pre-aborted secondary abortSignal raw put must reject');
  assert.equal(observed.rejectedPrePut.error?.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(observed.invalidSibling.ok, false, 'invalid abortSignal sibling must reject');
  assert.equal(observed.invalidSibling.error?.code, 'BRT_OPFS_ABORT_SIGNAL_INVALID');
  assert.equal(observed.snapshotAfterRejected.opened, false, 'pre-aborted/invalid raw put must not open provider prefix');
  assert.equal(observed.treeAfterRejected.fileCount, 0, 'pre-aborted/invalid raw put must create no files');
  assert.equal(observed.normalVerify.ok, true, 'normal raw seed put must verify');
  assert.equal(observed.normalReadSameBytes, true, 'normal raw read must match payload');
  assert.equal(observed.rejectedGet.ok, false, 'pre-aborted secondary abortSignal raw get must reject');
  assert.equal(observed.rejectedGet.error?.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(observed.rejectedMidWrite.ok, false, 'secondary abortSignal before browser write must reject raw put');
  assert.equal(observed.rejectedMidWrite.error?.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(observed.patchStats.createWritableCalls >= 1, true, 'browser patch should observe createWritable');
  assert.equal(observed.patchStats.writeCalls, 0, 'secondary abortSignal should fire before browser write()');
  assert.equal(observed.patchStats.abortCalls >= 1, true, 'raw OPFS writer should abort open writable');
  assert.equal(observed.midTree.fileCount, 0, 'mid-write secondary abort must leave no block file');
  assert.equal(observed.midSnapshot.stats.compositeAbortSignals >= 1, true, 'mid-write browser case should count composite signal');
  assert.equal(observed.guardedVerify.ok, true, 'guarded smoke verify should pass');
  assert.equal(observed.guardedReadSameBytes, true, 'guarded smoke read should match payload');
  assert.equal(observed.guardedCleanupAfter, true, 'guarded smoke cleanup should remove prefix');
  assert.equal(observed.guardedSettled.ok, true, 'guarded smoke locks should settle');
  assert.equal(observed.locksAfter?.heldCount ?? 0, 0, 'browser proof should end with no held locks');
  assert.equal(observed.locksAfter?.pendingCount ?? 0, 0, 'browser proof should end with no pending locks');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-composite-abort-signal'), 'trace must expose raw composite abort signal decisions');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-abort-signal-invalid'), 'trace must expose invalid sibling signal');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-abort'), 'trace must include OPFS abort rejection');
  assert.ok(observed.traceKinds.includes('storage:opfs-web-lock-guard-op-complete'), 'guarded smoke should complete');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-raw-composite-abort-signal-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that raw OpfsAsyncBlockStore signal and abortSignal are composed for direct browser OPFS calls and that invalid siblings are not masked.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'browser raw OPFS put rejects when abortSignal is already aborted even if signal is live',
      'browser raw OPFS invalid abortSignal sibling is not masked by a valid signal',
      'browser raw OPFS get rejects when abortSignal is already aborted even if signal is live',
      'browser raw OPFS abortSignal fired after createWritable but before write prevents write() and rolls back the final path',
      'guarded OPFS/Web Locks smoke still writes, verifies, reads, cleans up, and drains locks'
    ],
    nonClaims: [
      'Managed Chromium only; no cross-browser, OPFS fsync durability, crash recovery, quota/eviction, Web Locks fairness, or production readiness claim.',
      'Abort remains cooperative; this proves BrowserRT checkpoints honor composed signals, not that browser filesystem calls are preemptible in every stage.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', 18000)), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-block-store-raw-composite-abort-signal-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_block_store_raw_composite_abort_signal_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
