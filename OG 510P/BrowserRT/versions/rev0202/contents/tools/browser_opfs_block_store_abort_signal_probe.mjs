#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-ABORT-SIGNAL-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, guardedPrefix, payloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      storageEstimate: typeof navigator.storage?.estimate === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      abortController: typeof AbortController === 'function',
      textEncoder: typeof TextEncoder === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, opfsBlockStoreAbortSignalProof: true });
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const hash = await mod.digestBytesHex(payload);
    const raw = rt.opfsAsyncBlockStore({ name: 'browser-opfs-abort-signal-store', prefix: ${JSON.stringify(prefix)} });

    const prePutController = new AbortController();
    prePutController.abort(new Error('browser caller canceled before put'));
    const rejectedPrePut = await capture('raw-pre-aborted-put', () => raw.put(payload, { label: 'raw-pre-aborted-put' }, { signal: prePutController.signal }));
    const snapshotAfterRejectedPrePut = raw.snapshot();
    const invalidSignal = await capture('raw-invalid-signal-put', () => raw.put(payload, { label: 'raw-invalid-signal-put' }, { signal: 'not-an-abort-signal' }));

    const cleanupBeforeNormal = await raw.cleanupForTest({ signal: null });
    const normalPut = await raw.put(payload, { label: 'raw-valid-after-preabort' }, { signal: null });
    const normalVerify = await raw.verify(normalPut.ref, { signal: null });
    const readController = new AbortController();
    readController.abort('browser caller canceled read');
    const rejectedGet = await capture('raw-pre-aborted-get', () => raw.get(normalPut.ref, { abortSignal: readController.signal }));
    const cleanupAfterRaw = await raw.cleanupForTest({ signal: null });

    const guarded = rt.opfsWebLockGuardedBlockStore({ prefix: ${JSON.stringify(guardedPrefix)}, label: 'browser-opfs-abort-signal-guard', lockPrefix: 'browserrt:${REVISION}:opfs-abort-signal', lockName: '${REVISION}-opfs-abort-signal-lock', lockTimeoutMs: 200 });
    const cleanupBeforeGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 250 });
    const guardedPut = await guarded.put(payload, { label: 'guarded-null-signal-still-valid' }, { signal: null, timeoutMs: 250 });
    const guardedVerify = await guarded.verify(guardedPut.ref, { signal: null, timeoutMs: 250 });
    const cleanupAfterGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 250 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const finalSnapshot = raw.snapshot();
    const guardedSnapshot = guarded.snapshot();
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, hash, rejectedPrePut, snapshotAfterRejectedPrePut, invalidSignal, cleanupBeforeNormal, normalPut: { digest: normalPut.digest, bytes: normalPut.bytes, ref: normalPut.ref, path: normalPut.path }, normalVerify, rejectedGet, cleanupAfterRaw, cleanupBeforeGuarded, guardedPut: { digest: guardedPut.digest, bytes: guardedPut.bytes, ref: guardedPut.ref, path: guardedPut.path }, guardedVerify, cleanupAfterGuarded, locksQuery: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, finalSnapshot, guardedSnapshot, traceKinds });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-abort-signal-proof`;
  const guardedPrefix = options.guardedPrefix || `browserrt/${REVISION}/opfs-block-store-abort-signal-guarded-proof`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser OPFS explicit abort signal proof ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 16000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-abort-signal-probe.html',
    pageTitle: 'BrowserRT OPFS block-store AbortSignal probe',
    profilePrefix: 'browserrt-opfs-block-store-abort-signal-',
    stderrTerms: ['opfs', 'abort', 'signal', 'storage']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, guardedPrefix, payloadText), timeoutMs);
    mark('browser-opfs-block-store-abort-signal-eval', started);
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
  assert.equal(observed.rejectedPrePut.ok, false, 'pre-aborted raw put must reject');
  assert.equal(observed.rejectedPrePut.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(observed.snapshotAfterRejectedPrePut.opened, false, 'pre-aborted raw put must not open OPFS');
  assert.equal(observed.invalidSignal.ok, false, 'invalid signal raw put must reject');
  assert.equal(observed.invalidSignal.error.code, 'BRT_OPFS_ABORT_SIGNAL_INVALID');
  assert.equal(observed.normalVerify.ok, true, 'valid raw put after pre-abort must verify');
  assert.equal(observed.rejectedGet.ok, false, 'pre-aborted raw get must reject');
  assert.equal(observed.rejectedGet.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(observed.cleanupAfterRaw, true, 'raw proof prefix should clean up after normal put');
  assert.equal(observed.guardedVerify.ok, true, 'guarded null-signal OPFS put must still verify');
  assert.equal(observed.cleanupAfterGuarded, true, 'guarded proof prefix should clean up');
  assert.equal(observed.locksQuery?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksQuery?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-abort'), 'browser trace should include OPFS abort rejection');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-abort-signal-invalid'), 'browser trace should include invalid signal rejection');
  assert.ok(observed.traceKinds.includes('storage:opfs-block-put'), 'browser trace should include valid OPFS put after abort cases');
  assert.ok(observed.traceKinds.includes('storage:opfs-web-lock-guard-op-complete'), 'browser trace should include guarded OPFS completion');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-abort-signal-proof`, task_id: 'browser:opfs-block-store-abort-signal-proof', status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that OpfsAsyncBlockStore explicit AbortSignal handling runs in the browser realm: pre-aborted puts fail before provider open, invalid signal values fail closed, valid puts still verify, and the guarded OPFS/Web Locks path remains compatible with null signal options.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'browser raw OPFS pre-aborted put rejects with BRT_OPFS_OPERATION_ABORTED before opening provider state',
      'browser raw OPFS invalid signal rejects with BRT_OPFS_ABORT_SIGNAL_INVALID',
      'browser raw OPFS valid put/verify still works after abort rejections',
      'browser raw OPFS pre-aborted get rejects with BRT_OPFS_OPERATION_ABORTED',
      'guarded OPFS/Web Locks path still accepts adapter-compatible null signal and drains locks'
    ],
    nonClaims: [
      'Managed Chromium only; no cross-browser, production readiness, storage-lane timeout cancellation, OPFS fsync durability, quota/eviction, crash recovery, or sync-access-handle claim.',
      'Mid-write abort rollback is covered by the fake-OPFS release proof because deterministic browser mid-stream abort injection is not portable.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', 16000)), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-block-store-abort-signal-proof`, task_id: 'browser:opfs-block-store-abort-signal-proof', status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_block_store_abort_signal_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
