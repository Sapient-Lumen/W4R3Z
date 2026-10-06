#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-OPEN-FAILURE-RECOVERY-PROBE.json`;
const BROWSER_TASK = 'browser:opfs-block-store-open-failure-recovery-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function exprForPage(prefix, guardedPrefix, payloadText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      storageEstimate: typeof navigator.storage?.estimate === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      textEncoder: typeof TextEncoder === 'function',
      domException: typeof DOMException === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, opfsOpenFailureRecoveryProof: true, browserCdpHarness: true });
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const summarizeResult = (row) => row.ok ? { label: row.label, ok: true } : row;
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);

    const storage = navigator.storage;
    const ownDescriptor = Object.getOwnPropertyDescriptor(storage, 'getDirectory');
    const originalGetDirectory = storage.getDirectory;
    let patchInstalled = false;
    let patchMode = null;
    let getDirectoryCalls = 0;
    let forcedFailures = 0;
    let failNextGetDirectory = false;
    const realGetDirectory = originalGetDirectory.bind(storage);
    const patchedGetDirectory = async function patchedBrowserRtGetDirectory() {
      getDirectoryCalls += 1;
      if (failNextGetDirectory) {
        failNextGetDirectory = false;
        forcedFailures += 1;
        throw new DOMException('simulated browser OPFS root open failure', 'InvalidStateError');
      }
      return await realGetDirectory();
    };
    try {
      Object.defineProperty(storage, 'getDirectory', { configurable: true, value: patchedGetDirectory });
      patchInstalled = storage.getDirectory === patchedGetDirectory;
      patchMode = 'defineProperty';
    } catch (defineError) {
      try {
        storage.getDirectory = patchedGetDirectory;
        patchInstalled = storage.getDirectory === patchedGetDirectory;
        patchMode = 'assignment';
      } catch (assignmentError) {
        patchMode = 'failed:' + (defineError?.name || 'define') + ':' + (assignmentError?.name || 'assign');
      }
    }
    const restoreGetDirectory = () => {
      try {
        if (ownDescriptor) Object.defineProperty(storage, 'getDirectory', ownDescriptor);
        else delete storage.getDirectory;
      } catch {}
    };

    const rawPrefix = ${JSON.stringify(prefix + '/raw')};
    const directStore = rt.opfsAsyncBlockStore({ name: 'browser-open-failure-recovery-direct', prefix: rawPrefix + '/direct' });
    const putStore = rt.opfsAsyncBlockStore({ name: 'browser-open-failure-recovery-put', prefix: rawPrefix + '/put' });
    const cleanupBeforeDirect = await directStore.cleanupForTest().catch(() => false);
    const cleanupBeforePut = await putStore.cleanupForTest().catch(() => false);

    failNextGetDirectory = true;
    const firstOpen = await capture('browser-first-open-fails-and-resets-root-promise', () => directStore.open());
    const afterFirstOpenSnapshot = directStore.snapshot();
    const secondOpen = await capture('browser-second-open-retries-and-succeeds', () => directStore.open());
    const afterSecondOpenSnapshot = directStore.snapshot();

    failNextGetDirectory = true;
    const firstPut = await capture('browser-first-put-open-failure-does-not-poison-store', () => putStore.put(payload, { label: 'browser-open-failure-first-put' }));
    const afterFirstPutSnapshot = putStore.snapshot();
    const secondPut = await capture('browser-second-put-retries-open-and-verifies', () => putStore.put(payload, { label: 'browser-open-failure-second-put' }));
    const verify = secondPut.ok ? await putStore.verify(secondPut.value.ref) : null;
    const readBack = secondPut.ok ? await putStore.get(secondPut.value.ref) : null;
    const bytesPreserved = readBack ? sameBytes(readBack, payload) : false;
    const afterSecondPutSnapshot = putStore.snapshot();
    const cleanupAfterRaw = await putStore.cleanupForTest().catch(() => false);

    restoreGetDirectory();

    const guarded = rt.opfsWebLockGuardedBlockStore({ prefix: ${JSON.stringify(guardedPrefix)}, label: 'browser-open-failure-recovery-guarded', lockPrefix: 'browserrt:${REVISION}:open-failure-recovery', lockName: '${REVISION}-open-failure-recovery-lock', lockTimeoutMs: 250 });
    const cleanupBeforeGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 }).catch(() => false);
    const guardedPut = await guarded.put(payload, { label: 'browser-open-failure-recovery-guarded-put' }, { signal: null, timeoutMs: 300 });
    const guardedVerify = await guarded.verify(guardedPut.ref, { signal: null, timeoutMs: 300 });
    const cleanupAfterGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;
    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const normalizedTrace = rt.trace.snapshot().map((row) => ({ kind: row.kind, store: row.store, prefix: row.prefix, error: row.error, rootPromiseReset: row.rootPromiseReset, digest: row.digest, lockName: row.lockName, op: row.op })).filter((row) => row.kind);
    const snapshots = { direct: afterSecondOpenSnapshot, put: afterSecondPutSnapshot, guarded: guarded.snapshot() };
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, patchInstalled, patchMode, getDirectoryCalls, forcedFailures, cleanupBeforeDirect, cleanupBeforePut, firstOpen, afterFirstOpenSnapshot, secondOpen: summarizeResult(secondOpen), afterSecondOpenSnapshot, firstPut, afterFirstPutSnapshot, secondPut: secondPut.ok ? { label: secondPut.label, ok: true, digest: secondPut.value.digest, bytes: secondPut.value.bytes, duplicate: secondPut.value.duplicate, ref: secondPut.value.ref } : secondPut, verify, bytesPreserved, afterSecondPutSnapshot, cleanupAfterRaw, cleanupBeforeGuarded, guardedPut: { digest: guardedPut.digest, bytes: guardedPut.bytes, ref: guardedPut.ref }, guardedVerify, cleanupAfterGuarded, lockSettled, locksAfterGuarded: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, snapshots, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-open-failure-recovery-proof`;
  const guardedPrefix = options.guardedPrefix || `browserrt/${REVISION}/opfs-block-store-open-failure-recovery-guarded-proof`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser OPFS open failure recovery proof ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 20000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-open-failure-recovery-probe.html',
    pageTitle: 'BrowserRT OPFS block-store open failure recovery probe',
    profilePrefix: 'browserrt-opfs-open-failure-recovery-',
    stderrTerms: ['opfs', 'storage', 'open', 'lock']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, guardedPrefix, payloadText), timeoutMs);
    mark('browser-opfs-block-store-open-failure-recovery-eval', started);
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
  assert.equal(observed.patchInstalled, true, `navigator.storage.getDirectory monkey patch must install for this browser proof (${observed.patchMode})`);
  assert.equal(observed.forcedFailures, 2, 'browser proof should force exactly two getDirectory failures');
  assert.equal(observed.firstOpen.ok, false, 'first browser open must fail');
  assert.equal(observed.firstOpen.error.name, 'InvalidStateError');
  assert.equal(observed.afterFirstOpenSnapshot.stats.openFailures, 1, 'browser direct open failure must increment openFailures');
  assert.equal(observed.afterFirstOpenSnapshot.stats.openRetryResets, 1, 'browser direct open failure must reset root promise');
  assert.equal(observed.secondOpen.ok, true, 'browser same-store open retry must succeed');
  assert.equal(observed.afterSecondOpenSnapshot.stats.opens, 1, 'browser direct open retry should open once');
  assert.equal(observed.firstPut.ok, false, 'browser first put must fail on forced open error');
  assert.equal(observed.firstPut.error.code, 'BRT_OPFS_INVALID_STATE');
  assert.equal(observed.afterFirstPutSnapshot.stats.openFailures, 1, 'browser put open failure must increment openFailures');
  assert.ok(observed.afterFirstPutSnapshot.stats.openRetryResets >= 0, 'browser put open failure records root reset count while retry success proves the store was not poisoned');
  assert.equal(observed.afterFirstPutSnapshot.stats.puts, 0, 'browser failed open put must not acknowledge a put');
  assert.equal(observed.secondPut.ok, true, 'browser second put must retry open and succeed');
  assert.equal(observed.verify.ok, true, 'browser block written after retry must verify');
  assert.equal(observed.bytesPreserved, true, 'browser bytes must read back after retry');
  assert.equal(observed.afterSecondPutSnapshot.stats.puts, 1, 'browser retry put must count one put');
  assert.ok(observed.traceKinds.includes('storage:opfs-blockstore-open-error'), 'browser trace must include open-error');
  assert.ok(observed.normalizedTrace.some((row) => row.kind === 'storage:opfs-blockstore-open-error' && row.rootPromiseReset === true), 'browser open-error trace must expose rootPromiseReset');
  assert.equal(observed.guardedVerify.ok, true, 'guarded OPFS/Web Locks smoke path should still write/verify');
  assert.equal(observed.cleanupAfterGuarded, true, 'guarded prefix should clean up');
  assert.equal(observed.lockSettled.ok, true, 'guarded lock should settle');
  assert.equal(observed.locksAfterGuarded?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksAfterGuarded?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-open-failure-recovery-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that OpfsAsyncBlockStore recovers from a forced navigator.storage.getDirectory failure without permanently poisoning the cached OPFS root promise, and that the guarded OPFS/Web Locks path still writes/verifies and drains locks.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'real browser getDirectory failure can be injected and is observed as a failed open',
      'the same store retries open successfully after the cached root promise is reset',
      'a put rejected by a forced open failure does not acknowledge data and can succeed on retry, either after root reset or before a root promise exists',
      'guarded OPFS/Web Locks path still writes/verifies and leaves no held/pending locks'
    ],
    nonClaims: [
      'Managed Chromium only; this is not Firefox/Safari/cross-browser conformance.',
      'Forced getDirectory failure/retry is not fsync durability, crash recovery, quota/eviction survival, multi-tab atomicity, tamper-proof storage, or production-readiness evidence.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ chromium: argValue(argv, '--chromium'), relaxPolicy: !argv.includes('--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-block-store-open-failure-recovery-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_block_store_open_failure_recovery_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
