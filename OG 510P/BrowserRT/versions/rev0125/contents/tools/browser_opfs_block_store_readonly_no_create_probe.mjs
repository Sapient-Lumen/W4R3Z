#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-BROWSER-OPFS-BLOCK-STORE-READONLY-NO-CREATE-PROBE.json`;
const BROWSER_TASK = 'browser:opfs-block-store-readonly-no-create-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function exprForPage(prefix, unverifiedPrefix, existingPrefix, guardedPrefix, payloadText, missingText) {
  return `(async () => {
    const browserRtUrl = new URL('/src/browserrt.mjs', location.href).href;
    const page = { location: location.href, readyState: document.readyState, crossOriginIsolated, isSecureContext };
    const capabilities = {
      opfs: typeof navigator.storage?.getDirectory === 'function',
      webLocks: typeof navigator.locks?.request === 'function',
      textEncoder: typeof TextEncoder === 'function'
    };
    const mod = await import(browserRtUrl);
    const rt = await mod.boot({ opfsAsyncBlockStoreProof: true, opfsReadOnlyNoCreateProof: true, browserCdpHarness: true });
    const payload = new TextEncoder().encode(${JSON.stringify(payloadText)});
    const missingPayload = new TextEncoder().encode(${JSON.stringify(missingText)});
    const capture = async (label, fn) => {
      try { return { label, ok: true, value: await fn() }; }
      catch (error) { return { label, ok: false, error: { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code || null, detail: error?.detail || null } }; }
    };
    const sameBytes = (a, b) => a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
    const refForHash = (hash, bytes, path = null) => ({ kind: 'block', id: 'block:sha256:' + hash, digest: 'sha256:' + hash, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes, path });
    const pathExists = async (path) => {
      const parts = String(path || '').split('/').filter(Boolean);
      let dir = await navigator.storage.getDirectory();
      try {
        for (const part of parts) dir = await dir.getDirectoryHandle(part, { create: false });
        return true;
      } catch (error) {
        if (error?.name === 'NotFoundError') return false;
        throw error;
      }
    };

    const store = rt.opfsAsyncBlockStore({ name: 'browser-readonly-no-create-missing-store', prefix: ${JSON.stringify(prefix)} });
    const cleanupBeforeMissing = await store.cleanupForTest().catch(() => false);
    const missingHash = await mod.digestBytesHex(missingPayload);
    const missingRef = refForHash(missingHash, missingPayload.byteLength, store.blockPath(missingHash));
    const prefixExistsBefore = await pathExists(${JSON.stringify(prefix)});
    const verifyMissing = await store.verify(missingRef);
    const prefixExistsAfterVerify = await pathExists(${JSON.stringify(prefix)});
    const hasMissing = await store.has(missingRef);
    const prefixExistsAfterHas = await pathExists(${JSON.stringify(prefix)});
    const deleteMissing = await store.delete(missingRef);
    const prefixExistsAfterDelete = await pathExists(${JSON.stringify(prefix)});
    const getMissing = await capture('browser-get-missing-no-create', () => store.get(missingRef));
    const prefixExistsAfterGet = await pathExists(${JSON.stringify(prefix)});
    const missingSnapshot = store.snapshot();

    const looseHasStore = rt.opfsAsyncBlockStore({ name: 'browser-readonly-no-create-loose-has-store', prefix: ${JSON.stringify(unverifiedPrefix)}, verifyOnHas: false });
    const cleanupBeforeLooseHas = await looseHasStore.cleanupForTest().catch(() => false);
    const looseHash = await mod.digestBytesHex(new TextEncoder().encode('loose-' + ${JSON.stringify(missingText)}));
    const looseRef = refForHash(looseHash, 1, looseHasStore.blockPath(looseHash));
    const loosePrefixExistsBefore = await pathExists(${JSON.stringify(unverifiedPrefix)});
    const looseHasMissing = await looseHasStore.has(looseRef);
    const loosePrefixExistsAfter = await pathExists(${JSON.stringify(unverifiedPrefix)});
    const looseSnapshot = looseHasStore.snapshot();

    const existingStore = rt.opfsAsyncBlockStore({ name: 'browser-readonly-no-create-existing-store', prefix: ${JSON.stringify(existingPrefix)} });
    const cleanupBeforeExisting = await existingStore.cleanupForTest().catch(() => false);
    const existingPrefixBefore = await pathExists(${JSON.stringify(existingPrefix)});
    const put = await existingStore.put(payload, { label: 'browser-readonly-no-create-existing-seed' });
    const existingPrefixAfterPut = await pathExists(${JSON.stringify(existingPrefix)});
    const verifyExisting = await existingStore.verify(put.ref);
    const hasExisting = await existingStore.has(put.ref);
    const getExisting = await existingStore.get(put.ref);
    const deleteExisting = await existingStore.delete(put.ref);
    const deleteExistingAgain = await existingStore.delete(put.ref);
    const existingPrefixAfterDeletes = await pathExists(${JSON.stringify(existingPrefix)});
    const existingSnapshot = existingStore.snapshot();
    const cleanupAfterExisting = await existingStore.cleanupForTest().catch(() => false);

    const guarded = rt.opfsWebLockGuardedBlockStore({ prefix: ${JSON.stringify(guardedPrefix)}, label: 'browser-readonly-no-create-guarded', lockPrefix: 'browserrt:${REVISION}:readonly-no-create', lockName: '${REVISION}-readonly-no-create-lock', lockTimeoutMs: 250 });
    const cleanupBeforeGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 }).catch(() => false);
    const guardedPut = await guarded.put(payload, { label: 'guarded-readonly-no-create-pass' }, { signal: null, timeoutMs: 300 });
    const guardedVerify = await guarded.verify(guardedPut.ref, { signal: null, timeoutMs: 300 });
    const cleanupAfterGuarded = await guarded.cleanupForTest({ signal: null, timeoutMs: 300 });
    const lockSettled = await guarded.waitForSettled({ timeoutMs: 1000, intervalMs: 20 });
    const locksQuery = typeof navigator.locks?.query === 'function' ? await navigator.locks.query() : null;

    const traceKinds = rt.trace.snapshot().map((row) => row.kind);
    const normalizedTrace = rt.trace.snapshot().map((row) => ({ kind: row.kind, store: row.store, prefix: row.prefix, digest: row.digest, path: row.path, op: row.op, stage: row.stage, reason: row.reason, created: row.created, present: row.present, deleted: row.deleted, lockName: row.lockName })).filter((row) => row.kind);
    const snapshots = { missing: missingSnapshot, loose: looseSnapshot, existing: existingSnapshot, guarded: guarded.snapshot() };
    rt.close();
    return JSON.stringify({ project: 'BrowserRT', revision: '${REVISION}', version: '${VERSION}', page, capabilities, cleanupBeforeMissing, prefixExistsBefore, verifyMissing, prefixExistsAfterVerify, hasMissing, prefixExistsAfterHas, deleteMissing, prefixExistsAfterDelete, getMissing, prefixExistsAfterGet, missingSnapshot, cleanupBeforeLooseHas, loosePrefixExistsBefore, looseHasMissing, loosePrefixExistsAfter, looseSnapshot, cleanupBeforeExisting, existingPrefixBefore, put: { digest: put.digest, bytes: put.bytes, duplicate: put.duplicate, ref: put.ref }, existingPrefixAfterPut, verifyExisting, hasExisting, getExistingSameBytes: sameBytes(getExisting, payload), deleteExisting, deleteExistingAgain, existingPrefixAfterDeletes, existingSnapshot, cleanupAfterExisting, cleanupBeforeGuarded, guardedPut: { digest: guardedPut.digest, bytes: guardedPut.bytes, ref: guardedPut.ref }, guardedVerify, cleanupAfterGuarded, lockSettled, locksAfterGuarded: locksQuery ? { heldCount: locksQuery.held?.length ?? null, pendingCount: locksQuery.pending?.length ?? null, held: locksQuery.held, pending: locksQuery.pending } : null, snapshots, traceKinds, normalizedTrace });
  })()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/opfs-block-store-readonly-no-create-proof/missing-${Date.now()}`;
  const unverifiedPrefix = options.unverifiedPrefix || `browserrt/${REVISION}/opfs-block-store-readonly-no-create-proof/unverified-${Date.now()}`;
  const existingPrefix = options.existingPrefix || `browserrt/${REVISION}/opfs-block-store-readonly-no-create-proof/existing-${Date.now()}`;
  const guardedPrefix = options.guardedPrefix || `browserrt/${REVISION}/opfs-block-store-readonly-no-create-guarded-proof/${Date.now()}`;
  const payloadText = options.payloadText || `BrowserRT ${REVISION} browser OPFS read-only no-create existing payload ${Date.now()}`;
  const missingText = options.missingText || `BrowserRT ${REVISION} browser OPFS read-only no-create missing payload ${Date.now()}`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs ?? 20000,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/opfs-block-store-readonly-no-create-probe.html',
    pageTitle: 'BrowserRT OPFS block-store read-only no-create probe',
    profilePrefix: 'browserrt-opfs-readonly-no-create-',
    stderrTerms: ['opfs', 'storage', 'readonly', 'no-create', 'locks']
  }, async ({ evalJson, pageUrl, mark, timeoutMs }) => {
    const started = performance.now();
    const out = await evalJson(exprForPage(prefix, unverifiedPrefix, existingPrefix, guardedPrefix, payloadText, missingText), timeoutMs);
    mark('browser-opfs-block-store-readonly-no-create-eval', started);
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

  assert.equal(observed.prefixExistsBefore, false, 'missing prefix should start absent');
  assert.equal(observed.verifyMissing.present, false);
  assert.equal(observed.verifyMissing.ok, false);
  assert.equal(observed.prefixExistsAfterVerify, false, 'verify missing must not create prefix');
  assert.equal(observed.hasMissing, false);
  assert.equal(observed.prefixExistsAfterHas, false, 'has missing must not create prefix');
  assert.equal(observed.deleteMissing, false);
  assert.equal(observed.prefixExistsAfterDelete, false, 'delete missing must not create prefix');
  assert.equal(observed.getMissing.ok, false);
  assert.equal(observed.getMissing.error.name, 'NotFoundError');
  assert.equal(observed.prefixExistsAfterGet, false, 'get missing must not create prefix');
  assert.equal(observed.missingSnapshot.opened, false, 'browser missing read-only calls should not mark store opened');
  assert.equal(observed.missingSnapshot.stats.opens, 0, 'browser missing read-only calls should not run mutable open');
  assert.equal(observed.missingSnapshot.stats.noCreateMisses, 4, 'browser missing read-only calls should record four no-create misses');

  assert.equal(observed.loosePrefixExistsBefore, false);
  assert.equal(observed.looseHasMissing, false, 'browser verifyOnHas:false has should return false');
  assert.equal(observed.loosePrefixExistsAfter, false, 'browser verifyOnHas:false has miss must not create prefix');
  assert.equal(observed.looseSnapshot.stats.opens, 0);
  assert.equal(observed.looseSnapshot.stats.noCreateMisses, 1);

  assert.equal(observed.existingPrefixBefore, false);
  assert.equal(observed.put.duplicate, false, 'browser existing seed put should be new');
  assert.equal(observed.existingPrefixAfterPut, true, 'browser put should create prefix');
  assert.equal(observed.verifyExisting.ok, true, 'browser existing block should verify');
  assert.equal(observed.hasExisting, true, 'browser existing block should be found');
  assert.equal(observed.getExistingSameBytes, true, 'browser existing block should read back');
  assert.equal(observed.deleteExisting, true, 'browser delete existing should remove the file');
  assert.equal(observed.deleteExistingAgain, false, 'browser second delete should be a no-op miss');
  assert.equal(observed.cleanupAfterExisting, true, 'browser existing prefix should clean up');

  assert.equal(observed.guardedVerify.ok, true, 'guarded OPFS/Web Locks path should verify');
  assert.equal(observed.cleanupAfterGuarded, true, 'guarded prefix should clean up');
  assert.equal(observed.lockSettled.ok, true, 'guarded lock should settle');
  assert.equal(observed.locksAfterGuarded?.heldCount ?? 0, 0, 'managed browser should end with no held locks');
  assert.equal(observed.locksAfterGuarded?.pendingCount ?? 0, 0, 'managed browser should end with no pending locks');
  for (const kind of ['storage:opfs-block-no-create-miss', 'storage:opfs-block-put', 'storage:opfs-block-delete', 'storage:opfs-web-lock-guard-op-complete']) {
    assert.ok(observed.traceKinds.includes(kind), `browser trace missing ${kind}`);
  }

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-browser-opfs-block-store-readonly-no-create-proof`, task_id: BROWSER_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: harness.durationMs,
    purpose: 'Managed Chromium proof that OpfsAsyncBlockStore missing get/has/verify/delete paths do not create OPFS prefix directories, while existing put/read/delete and guarded Web Locks paths still work.',
    observations: observed,
    harness: { marks: harness.marks, process: harness.process, pageUrl: observed._pageUrl },
    claimsChecked: [
      'missing verify/has/delete/get keep a real OPFS prefix absent',
      'verifyOnHas:false has miss also keeps a real OPFS prefix absent',
      'existing put/verify/has/get/delete still works in real OPFS',
      'Web-Lock-guarded OPFS store still writes/verifies and leaves no held/pending locks'
    ],
    nonClaims: [
      'Managed Chromium only; no Firefox/Safari/cross-browser conformance claim.',
      'This does not claim recursive empty-directory cleanup, quota/eviction survival, fsync durability, crash/power-loss recovery, tamper-proof storage, Web Locks fairness, multi-tab atomicity, or production readiness.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe({ timeoutMs: Number(argValue(argv, '--timeout-ms', 20000)), chromium: argValue(argv, '--chromium', null), relaxPolicy: !hasFlag(argv, '--no-relax-policy') });
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-browser-opfs-block-store-readonly-no-create-proof`, task_id: BROWSER_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[browser_opfs_block_store_readonly_no_create_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
