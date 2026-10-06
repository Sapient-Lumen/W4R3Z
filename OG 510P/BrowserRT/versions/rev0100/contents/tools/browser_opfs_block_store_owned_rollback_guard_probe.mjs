#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-OWNED-ROLLBACK-GUARD-PROBE.json`;
const BROWSER_TASK = 'browser:opfs-block-store-owned-rollback-guard-proof';
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
      textEncoder: typeof TextEncoder === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, opfsOwnedRollbackGuardProof: true, browserCdpHarness: true });
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const duplicateTraceEvents = [];
    const duplicateTrace = {
      emit(kind, payload = {}) {
        duplicateTraceEvents.push({ kind, duplicate: payload?.duplicate === true, reason: payload?.reason || null, errorCode: payload?.error?.code || null });
        if (kind === 'storage:opfs-block-put' && payload?.duplicate === true) throw new Error('browser intentional trace failure after duplicate put classification');
      }
    };

    const rawSeed = rt.opfsAsyncBlockStore({ name: 'browser-owned-rollback-raw-seed', prefix: ${JSON.stringify(prefix + '/raw')} });
    const cleanupBeforeRaw = await rawSeed.cleanupForTest().catch(() => false);
    const first = await rawSeed.put(payload, { label: 'browser-owned-rollback-seed' });
    const beforeVerify = await rawSeed.verify(first.ref);
    const throwingDuplicateStore = rt.opfsAsyncBlockStore({ name: 'browser-owned-rollback-raw-duplicate-throwing', prefix: ${JSON.stringify(prefix + '/raw')}, trace: duplicateTrace });
    const duplicateFailure = await capture('browser-duplicate-put-trace-failure-must-not-delete-existing-block', () => throwingDuplicateStore.put(payload, { label: 'browser-duplicate-put-trace-failure' }));
    const afterVerify = await rawSeed.verify(first.ref);
    const afterGet = await rawSeed.get(first.ref);
    const bytesPreserved = sameBytes(afterGet, payload);
    const duplicateSnapshot = throwingDuplicateStore.snapshot();
    const rawSeedSnapshot = rawSeed.snapshot();
    const cleanupAfterRaw = await rawSeed.cleanupForTest();

    const guarded = rt.opfsWebLockGuardedBlockStore({ prefix: ${JSON.stringify(guardedPrefix)}, label: 'browser-owned-rollback-guarded', lockPrefix: 'browserrt:${REVISION}:owned-rollback', lockName: '${REVISION}-owned-rollback-lock', lockTimeoutMs: 250 });
    const cleanupBeforeGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 }).catch(() => false);
    const guardedPut = await guarded.put(payload, { label: 'browser-owned-rollback-guarded-put' }, { signal: null, timeoutMs: 300 });
    const guardedVerify = await guarded.verify(guardedPut.ref, { signal: null, timeoutMs: 300 });
    const cleanupAfterGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const normalizedTrace = rt.trace.snapshot().map((row) => ({ kind: row.kind, store: row.store, prefix: row.prefix, digest: row.digest, reason: row.reason, lockName: row.lockName, op: row.op, duplicate: row.duplicate, error: row.error })).filter((row) => row.kind);
    const snapshots = { rawSeed: rawSeedSnapshot, duplicate: duplicateSnapshot, guarded: guarded.snapshot() };
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, cleanupBeforeRaw, first: { digest: first.digest, bytes: first.bytes, path: first.path, ref: first.ref }, beforeVerify, duplicateFailure, afterVerify, bytesPreserved, duplicateTraceEvents, cleanupAfterRaw, cleanupBeforeGuarded, guardedPut: { digest: guardedPut.digest, bytes: guardedPut.bytes, path: guardedPut.path, ref: guardedPut.ref }, guardedVerify, cleanupAfterGuarded, lockSettled, locksAfterGuarded: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, snapshots, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-owned-rollback-guard-proof`;
  const guardedPrefix = options.guardedPrefix || `browserrt/${REVISION}/opfs-block-store-owned-rollback-guarded-proof`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser OPFS owned rollback guard proof ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 18000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-owned-rollback-guard-probe.html',
    pageTitle: 'BrowserRT OPFS block-store owned rollback guard probe',
    profilePrefix: 'browserrt-opfs-owned-rollback-guard-',
    stderrTerms: ['opfs', 'storage', 'rollback', 'lock']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, guardedPrefix, payloadText), timeoutMs);
    mark('browser-opfs-block-store-owned-rollback-guard-eval', started);
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
  assert.equal(observed.beforeVerify.ok, true, 'seeded browser block must verify before duplicate failure');
  assert.equal(observed.duplicateFailure.ok, false, 'browser duplicate trace failure must reject');
  assert.equal(observed.duplicateFailure.error.code, 'BRT_OPFS_OPERATION_FAILED');
  assert.equal(observed.duplicateFailure.error.detail.rollback?.attempted, false, 'browser duplicate failure must not attempt rollback');
  assert.equal(observed.duplicateFailure.error.detail.rollback?.skipped, true, 'browser duplicate failure must record rollback skip');
  assert.equal(observed.duplicateFailure.error.detail.rollback?.reason, 'pre-existing-duplicate-block-not-owned-by-put');
  assert.equal(observed.afterVerify.ok, true, 'browser existing block must verify after duplicate failure');
  assert.equal(observed.bytesPreserved, true, 'browser existing block bytes must remain after duplicate failure');
  assert.equal(observed.snapshots.duplicate.stats.rollbackOwnershipSkips, 1);
  assert.equal(observed.snapshots.duplicate.stats.rollbackAttempts, 0);
  assert.ok(observed.duplicateTraceEvents.some((row) => row.kind === 'storage:opfs-block-put-rollback-skipped'), 'browser duplicate path should emit rollback skipped');
  assert.equal(observed.cleanupAfterRaw, true, 'browser raw prefix should clean up');
  assert.equal(observed.guardedVerify.ok, true, 'guarded OPFS/Web Locks smoke path should still write/verify');
  assert.equal(observed.cleanupAfterGuarded, true, 'guarded prefix should clean up');
  assert.equal(observed.lockSettled.ok, true, 'guarded lock should settle');
  assert.equal(observed.locksAfterGuarded?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksAfterGuarded?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-owned-rollback-guard-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that real OPFS duplicate-put failures do not let OpfsAsyncBlockStore rollback delete a pre-existing valid content-addressed block, while the guarded OPFS/Web Locks path still writes/verifies and drains locks.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'real OPFS duplicate put can classify an existing valid block and then fail without deleting that pre-existing block',
      'duplicate failure records rollback skipped rather than attempted/deleted',
      'the valid block still verifies and reads back byte-for-byte after the duplicate failure',
      'Web-Lock-guarded OPFS store still writes/verifies after the rollback guard change and drains locks'
    ],
    nonClaims: [
      'Managed Chromium only; no cross-browser, production-readiness, durability, fsync, organic eviction, crash/power-loss, quota-policy, or capacity guarantee.',
      'This proves rollback ownership for the duplicate failure path, not atomic multi-tab writes or adversarial storage tamper resistance.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-block-store-owned-rollback-guard-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_block_store_owned_rollback_guard_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
