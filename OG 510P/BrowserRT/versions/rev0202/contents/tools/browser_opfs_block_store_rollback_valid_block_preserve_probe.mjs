#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const BROWSER_TASK = 'browser:opfs-block-store-rollback-valid-block-preserve-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function exprForPage(prefix, guardedPrefix, payloadText, guardedPayloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      storageEstimate: typeof navigator.storage?.estimate === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      textEncoder: typeof TextEncoder === 'function',
      cryptoDigest: typeof crypto?.subtle?.digest === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, opfsRollbackValidBlockPreserveProof: true, browserCdpHarness: true });
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const guardedPayload = new TextEncoder().encode(${JSON.stringify(guardedPayloadText)});
    const rawPrefix = ${JSON.stringify(prefix + '/raw')};
    const traceEvents = [];
    let thrown = false;
    const throwingTrace = {
      emit(kind, detail = {}) {
        traceEvents.push({ kind, digest: detail.digest ?? null, hash: detail.hash ?? null, reason: detail.reason ?? null, bytes: detail.bytes ?? null, error: detail.error ?? null });
        if (!thrown && kind === 'storage:opfs-block-write-close') {
          thrown = true;
          throw new Error('intentional browser trace sink failure after valid block close');
        }
      }
    };
    const cleanupStore = rt.opfsAsyncBlockStore({ name: 'browser-rollback-preserve-cleanup', prefix: rawPrefix });
    const cleanupBefore = await cleanupStore.cleanupForTest().catch(() => false);
    const throwingStore = rt.opfsAsyncBlockStore({ name: 'browser-rollback-preserve-throwing-store', prefix: rawPrefix, trace: throwingTrace });
    const hash = await mod.digestBytesHex(payload);
    const ref = { kind: 'block', id: 'block:sha256:' + hash, digest: 'sha256:' + hash, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes: payload.byteLength, path: throwingStore.blockPath(hash) };
    const failedPut = await capture('browser-trace-failure-after-close-preserves-valid-final-block', () => throwingStore.put(payload, { label: 'browser-trace-failure-after-close' }));
    const verifier = rt.opfsAsyncBlockStore({ name: 'browser-rollback-preserve-verifier', prefix: rawPrefix });
    const verifyAfterFailure = await verifier.verify(ref);
    const readAfterFailure = await verifier.get(ref);
    const bytesPreserved = sameBytes(readAfterFailure, payload);
    const cleanupAfterRaw = await verifier.cleanupForTest().catch(() => false);

    const guarded = rt.opfsWebLockGuardedBlockStore({ prefix: ${JSON.stringify(guardedPrefix)}, label: 'browser-rollback-preserve-guarded', lockPrefix: 'browserrt:${REVISION}:rollback-preserve', lockName: '${REVISION}-rollback-preserve-lock', lockTimeoutMs: 250 });
    const cleanupBeforeGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 }).catch(() => false);
    const guardedPut = await guarded.put(guardedPayload, { label: 'browser-rollback-preserve-guarded-put' }, { signal: null, timeoutMs: 300 });
    const guardedVerify = await guarded.verify(guardedPut.ref, { signal: null, timeoutMs: 300 });
    const cleanupAfterGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const snapshots = { throwing: throwingStore.snapshot(), verifier: verifier.snapshot(), guarded: guarded.snapshot() };
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const normalizedRuntimeTrace = rt.trace.snapshot().map((row) => ({ kind: row.kind, store: row.store, prefix: row.prefix, digest: row.digest, lockName: row.lockName, op: row.op })).filter((row) => row.kind);
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, cleanupBefore, failedPut, verifyAfterFailure, bytesPreserved, cleanupAfterRaw, traceEvents, cleanupBeforeGuarded, guardedPut: { digest: guardedPut.digest, bytes: guardedPut.bytes, ref: guardedPut.ref }, guardedVerify, cleanupAfterGuarded, lockSettled, locksAfterGuarded: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, snapshots, traceKinds, normalizedRuntimeTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-rollback-valid-block-preserve-proof`;
  const guardedPrefix = options.guardedPrefix || `browserrt/${REVISION}/opfs-block-store-rollback-valid-block-preserve-guarded-proof`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser rollback valid block preserve proof ${Date.now()}`;
  const guardedPayloadText = options.guardedPayloadText || `BrowserRT ${REVISION} browser rollback valid block preserve guarded proof ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 20000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-rollback-valid-block-preserve-probe.html',
    pageTitle: 'BrowserRT OPFS block-store rollback valid block preserve probe',
    profilePrefix: 'browserrt-opfs-rollback-valid-preserve-',
    stderrTerms: ['opfs', 'storage', 'rollback', 'lock']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, guardedPrefix, payloadText, guardedPayloadText), timeoutMs);
    mark('browser-opfs-block-store-rollback-valid-block-preserve-eval', started);
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
  assert.equal(observed.capabilities.webLocks, true, 'Web Locks must be available for guarded smoke path');
  assert.equal(observed.capabilities.cryptoDigest, true, 'browser proof needs crypto.subtle.digest');
  assert.equal(observed.failedPut.ok, false, 'browser trace failure after close must reject the put');
  assert.equal(observed.failedPut.error.code, 'BRT_OPFS_OPERATION_FAILED');
  assert.equal(observed.failedPut.error.detail.rollback?.attempted, true);
  assert.equal(observed.failedPut.error.detail.rollback?.skipped, true);
  assert.equal(observed.failedPut.error.detail.rollback?.preserved, true, 'browser rollback should preserve the valid final block');
  assert.equal(observed.failedPut.error.detail.rollback?.reason, 'valid-final-block-preserved');
  assert.equal(observed.verifyAfterFailure.ok, true, 'browser real OPFS block should verify after failed put');
  assert.equal(observed.bytesPreserved, true, 'browser real OPFS bytes should be preserved after failed put');
  assert.equal(observed.snapshots.throwing.stats.rollbackValidBlockPreserves, 1);
  assert.equal(observed.snapshots.throwing.stats.rollbackDeletes, 0);
  assert.ok(observed.traceEvents.some((row) => row.kind === 'storage:opfs-block-write-close'), 'throwing trace should see write close');
  assert.ok(observed.traceEvents.some((row) => row.kind === 'storage:opfs-block-put-rollback-preserved'), 'throwing trace should record rollback preservation');
  assert.equal(observed.guardedVerify.ok, true, 'guarded OPFS/Web Locks write must still verify');
  assert.equal(observed.cleanupAfterGuarded, true, 'guarded cleanup should remove proof prefix');
  if (observed.locksAfterGuarded) {
    assert.equal(observed.locksAfterGuarded.heldCount, 0, 'no held Web Locks should remain');
    assert.equal(observed.locksAfterGuarded.pendingCount, 0, 'no pending Web Locks should remain');
  }

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-rollback-valid-block-preserve-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that real OPFS preserves an already-valid content-addressed block when a put fails after close due to a trace/observer error, while the guarded OPFS/Web Locks path still writes/verifies and drains locks.',
    observations: observed,
    harness,
    claimsChecked: [
      'real OPFS write closed a valid block before a trace sink failure rejected the put',
      'failed-put rollback inspected the final file and preserved the valid content-addressed bytes',
      'preservation is visible through rollbackValidBlockPreserves and storage:opfs-block-put-rollback-preserved',
      'guarded OPFS/Web Locks smoke path still writes, verifies, cleans up, and drains locks'
    ],
    nonClaims: [
      'Managed Chromium proof only; this is not cross-browser evidence.',
      'Preserving valid blocks during rollback does not prove transactional put semantics, cancellation, fsync durability, power-loss recovery, quota/eviction survival, Web Locks fairness, or production readiness.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-block-store-rollback-valid-block-preserve-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_block_store_rollback_valid_block_preserve_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
