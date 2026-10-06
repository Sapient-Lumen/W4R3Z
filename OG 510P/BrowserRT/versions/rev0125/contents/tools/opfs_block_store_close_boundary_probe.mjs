#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, boot, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-CLOSE-BOUNDARY-PROBE.json`;
const TASK_ID = 'opfs:block-store-close-boundary-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

async function expectReject(label, fn) {
  try {
    const value = await fn();
    return { label, rejected: false, value, error: null };
  } catch (error) {
    return { label, rejected: true, value: null, error: captureError(error) };
  }
}

function refForPayload(hash, bytes, path = null) {
  return Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest: `sha256:${hash}`, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes, path });
}

function summarizeOwnedResources(snapshot) {
  const resources = Array.isArray(snapshot?.resources) ? snapshot.resources.map((row) => ({ kind: row.kind, label: row.label, owned: row.owned, closeable: row.closeable, closed: row.closed ?? null, failed: row.failed ?? null })) : [];
  return Object.freeze({ count: snapshot?.count ?? resources.length, resources: Object.freeze(resources) });
}

function summarizeRuntimeClose(report) {
  const rows = Array.isArray(report?.resourceClose?.results) ? report.resourceClose.results.map((row) => ({ kind: row.kind, label: row.label, ok: row.ok, skipped: row.skipped === true, resultDisposition: row.result?.disposition ?? null, errorCode: row.error?.code ?? null })) : [];
  return Object.freeze({ reason: report?.reason ?? null, resourceClose: { total: report?.resourceClose?.total ?? rows.length, closedCount: report?.resourceClose?.closedCount ?? null, failedCount: report?.resourceClose?.failedCount ?? null, skippedCount: report?.resourceClose?.skippedCount ?? null, results: Object.freeze(rows) } });
}

async function directProviderCloseCase(payload) {
  const trace = new TraceLog();
  return await withFakeNavigator(async (root) => {
    const prefix = `browserrt/${REVISION}/close-boundary/direct`;
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-close-boundary-direct-store`, prefix, trace, verifyAfterWrite: true, verifyOnHas: true });
    const put = await store.put(payload, { label: 'close-boundary-direct-seed' });
    const close = await store.closeAsync({ reason: 'close-boundary-direct-proof' });
    const afterCloseGet = await expectReject('direct-provider-get-after-close', () => store.get(put.ref));
    const afterCloseOpen = await expectReject('direct-provider-open-after-close', () => store.open());

    const reopened = createOpfsAsyncBlockStore({ name: `${REVISION}-close-boundary-reopened-store`, prefix, trace, verifyOnHas: true });
    const verify = await reopened.verify(put.ref);
    const got = await reopened.get(put.ref);
    const gotHash = await digestBytesHex(got);
    const cleanup = await reopened.cleanupForTest();

    return Object.freeze({
      put: { digest: put.digest, bytes: put.bytes, path: put.path },
      close,
      afterCloseGet,
      afterCloseOpen,
      reopenedVerify: verify,
      reopenedGet: { bytes: got.byteLength, hash: gotHash, sameHash: gotHash === put.hash },
      cleanup,
      closedSnapshot: store.snapshot(),
      reopenedSnapshot: reopened.snapshot(),
      treeAfterCleanup: fakeTreeSummary(root),
      traceKinds: trace.kinds()
    });
  });
}

async function runtimeOwnershipCloseCase(payload) {
  return await withFakeNavigator(async () => {
    const rt = await boot({ traceCapacity: 8192 });
    const ownedStore = rt.opfsAsyncBlockStore({ name: `${REVISION}-runtime-owned-close-store`, prefix: `browserrt/${REVISION}/close-boundary/runtime-store` });
    const ownedStorePut = await ownedStore.put(payload, { label: 'runtime-owned-close-store-seed' });
    const adapter = rt.opfsBlockStoreStorageLaneAdapter({ label: `${REVISION}-runtime-owned-close-adapter`, prefix: `browserrt/${REVISION}/close-boundary/runtime-adapter` });
    const guard = rt.opfsWebLockGuardedBlockStore({ label: `${REVISION}-runtime-owned-close-guard`, prefix: `browserrt/${REVISION}/close-boundary/runtime-guard`, requireWebLocks: false });
    const beforeClose = summarizeOwnedResources(rt.ownedResources());
    const closeRaw = await rt.closeAsync({ reason: 'close-boundary-runtime-proof' });
    const close = summarizeRuntimeClose(closeRaw);
    const afterClose = summarizeOwnedResources(rt.ownedResources());
    const closedStoreOpen = await expectReject('runtime-owned-store-open-after-close', () => ownedStore.open());
    const closedStoreVerify = await expectReject('runtime-owned-store-verify-after-close', () => ownedStore.verify(ownedStorePut.ref));
    const closedAdapterPut = await expectReject('runtime-owned-adapter-schedule-after-close', () => adapter.schedulePut(payload));
    const closedGuardQuery = await expectReject('runtime-owned-guard-query-after-close', () => guard.queryLocks());
    return Object.freeze({
      beforeClose,
      close,
      afterClose,
      ownedStorePut: { digest: ownedStorePut.digest, bytes: ownedStorePut.bytes, path: ownedStorePut.path },
      closed: { store: { closed: ownedStore.snapshot().closed, opened: ownedStore.snapshot().opened }, adapter: { closed: adapter.closed, ownStore: adapter.snapshot().ownStore, store: { closed: adapter.snapshot().store.closed } }, guard: { closed: guard.closed, ownStore: guard.snapshot().ownStore, store: { closed: guard.snapshot().store.closed } } },
      rejects: { closedStoreOpen, closedStoreVerify, closedAdapterPut, closedGuardQuery },
      traceKinds: rt.trace.kinds()
    });
  });
}

export async function runProbe() {
  const started = performance.now();
  const payload = new Uint8Array(3072);
  for (let i = 0; i < payload.length; i += 1) payload[i] = (41 + i * 17 + (i >>> 2)) & 255;
  payload.set(new TextEncoder().encode(`BrowserRT ${REVISION} OPFS close boundary proof`));

  const direct = await directProviderCloseCase(payload);
  const runtime = await runtimeOwnershipCloseCase(payload);

  assert.equal(direct.close.disposition, 'closed', 'direct provider close should report closed');
  assert.equal(direct.closedSnapshot.closed, true, 'closed direct provider snapshot must be closed');
  assert.equal(direct.closedSnapshot.opened, false, 'closed direct provider snapshot must clear opened state');
  assert.equal(direct.afterCloseGet.rejected, true, 'get after provider close must reject');
  assert.equal(direct.afterCloseGet.error.code, 'BRT_OPFS_STORE_CLOSED');
  assert.equal(direct.afterCloseOpen.rejected, true, 'open after provider close must reject');
  assert.equal(direct.afterCloseOpen.error.code, 'BRT_OPFS_STORE_CLOSED');
  assert.equal(direct.reopenedVerify.ok, true, 'fresh provider should verify acknowledged block after previous provider close');
  assert.equal(direct.reopenedGet.sameHash, true, 'fresh provider should read same acknowledged block after previous provider close');
  assert.equal(direct.cleanup, true, 'reopened provider should be able to clean up prefix');
  assert.ok(direct.traceKinds.includes('storage:opfs-blockstore-close'), 'direct provider close must be traced');
  assert.ok(direct.traceKinds.includes('storage:opfs-blockstore-closed-reject'), 'direct provider post-close rejection must be traced');

  const kinds = new Set(runtime.beforeClose.resources.map((row) => row.kind));
  assert.ok(kinds.has('opfs-async-block-store'), 'runtime should own direct OPFS store');
  assert.ok(kinds.has('opfs-storage-lane-adapter'), 'runtime should own OPFS storage-lane adapter');
  assert.ok(kinds.has('opfs-web-lock-guarded-block-store'), 'runtime should own OPFS Web Lock guard');
  assert.equal(runtime.close.resourceClose.failedCount, 0, 'runtime close should not fail OPFS resource close');
  assert.equal(runtime.closed.store.closed, true, 'runtime-owned OPFS store must be closed');
  assert.equal(runtime.closed.adapter.closed, true, 'runtime-owned OPFS storage-lane adapter must be closed');
  assert.equal(runtime.closed.guard.closed, true, 'runtime-owned OPFS Web Lock guard must be closed');
  assert.equal(runtime.closed.adapter.store.closed, true, 'adapter-owned internal store must be closed');
  assert.equal(runtime.closed.guard.store.closed, true, 'guard-owned internal store must be closed');
  assert.equal(runtime.rejects.closedStoreOpen.error.code, 'BRT_OPFS_STORE_CLOSED');
  assert.equal(runtime.rejects.closedStoreVerify.error.code, 'BRT_OPFS_STORE_CLOSED');
  assert.equal(runtime.rejects.closedAdapterPut.error.code, 'BRT_BLOCK_STORE_LANE_ADAPTER_CLOSED');
  assert.equal(runtime.rejects.closedGuardQuery.error.code, 'BRT_OPFS_WEB_LOCK_GUARD_CLOSED');
  assert.ok(runtime.traceKinds.includes('storage:opfs-blockstore-close'), 'runtime close should trace OPFS provider close');
  assert.ok(runtime.traceKinds.includes('block-store-lane:close'), 'runtime close should trace adapter close');
  assert.ok(runtime.traceKinds.includes('storage:opfs-web-lock-guard-close'), 'runtime close should trace guard close');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-close-boundary-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that OPFS provider close is an explicit lifecycle boundary, runtime.closeAsync owns OPFS stores/adapters/guards, and post-close operations fail closed without deleting acknowledged blocks.',
    observations: { direct, runtime },
    claimsChecked: [
      'OpfsAsyncBlockStore.closeAsync closes the provider object and rejects future open/read/verify calls with BRT_OPFS_STORE_CLOSED',
      'Provider close is not data deletion; a fresh provider for the same prefix can verify and read the acknowledged block',
      'runtime.closeAsync owns and closes directly-created OPFS stores',
      'runtime.closeAsync owns and closes OPFS storage-lane adapters plus their internally-created stores',
      'runtime.closeAsync owns and closes OPFS Web Lock guards plus their internally-created stores',
      'closed adapters/guards reject future operations with explicit closed-boundary error codes'
    ],
    nonClaims: [
      'Fake-OPFS release-tier proof only; this is not fresh browser OPFS execution.',
      'Provider close does not cancel already-running arbitrary provider code; it prevents future operations and releases cached provider handles.',
      'No cross-browser OPFS behavior, fsync durability, quota/eviction survival, crash/power-loss safety, Web Locks fairness, or production storage readiness claim.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-close-boundary-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_close_boundary_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
