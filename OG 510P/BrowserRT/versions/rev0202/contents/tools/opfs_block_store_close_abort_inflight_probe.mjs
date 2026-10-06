#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'opfs:block-store-close-abort-inflight-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-CLOSE-ABORT-INFLIGHT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

async function capture(label, fn) {
  try { return { label, ok: true, value: await fn() }; }
  catch (error) { return { label, ok: false, error: captureError(error) }; }
}

function payloadOf(label, size = 4096) {
  const bytes = new Uint8Array(size);
  for (let i = 0; i < bytes.length; i += 1) bytes[i] = (label.length * 31 + i * 17 + (i >>> 3)) & 255;
  bytes.set(new TextEncoder().encode(`BrowserRT ${REVISION} close abort in-flight proof ${label}`));
  return bytes;
}

function refForHash(hash, bytes, path) {
  return Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest: `sha256:${hash}`, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes, path });
}

async function runCloseDuringWriteCase() {
  const payload = payloadOf('close-during-write', 8192);
  const prefix = `browserrt/${REVISION}/fake-close-abort-inflight/close-during-write`;
  const trace = new TraceLog({ maxEvents: 8192 });
  const events = [];
  let store;
  let closeReport = null;
  const hooks = {
    async onWrite({ file, bytes }) {
      events.push(Object.freeze({ kind: 'write', path: file.path, bytes: bytes.byteLength }));
      if (file.name.endsWith('.blk') && store && !closeReport) {
        closeReport = await store.closeAsync({ reason: 'probe-close-during-inflight-write' });
        events.push(Object.freeze({ kind: 'close-called-during-write', inFlightAtClose: closeReport.inFlightAtClose, disposition: closeReport.disposition }));
      }
    },
    async onAbort({ file }) { events.push(Object.freeze({ kind: 'stream-abort', path: file.path })); },
    async onRemoveEntry({ dir, name }) { events.push(Object.freeze({ kind: 'remove-entry', path: dir.childPath(name) })); }
  };
  return await withFakeNavigator(async (root) => {
    store = createOpfsAsyncBlockStore({ name: `${REVISION}-close-abort-inflight-store`, prefix, trace });
    const hash = await digestBytesHex(payload);
    const ref = refForHash(hash, payload.byteLength, store.blockPath(hash));
    const rejectedPut = await capture('close-during-inflight-put', () => store.put(payload, { label: 'close-during-inflight-put' }));
    const postCloseGet = await capture('post-close-get-rejects', () => store.get(ref));
    const verifier = createOpfsAsyncBlockStore({ name: `${REVISION}-close-abort-inflight-verifier`, prefix });
    const verifyAfterCloseAbort = await verifier.verify(ref);
    return { rejectedPut, postCloseGet, closeReport, verifyAfterCloseAbort, snapshot: store.snapshot(), verifierSnapshot: verifier.snapshot(), tree: fakeTreeSummary(root), events, traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks });
}


async function runCloseDuringBucketOpenCase() {
  const payload = payloadOf('close-during-bucket-open', 4096);
  const prefix = `browserrt/${REVISION}/fake-close-abort-inflight/close-during-bucket-open`;
  const trace = new TraceLog({ maxEvents: 8192 });
  const events = [];
  let store;
  let closeReport = null;
  let targetFirstBucket = null;
  let targetSecondBucket = null;
  const hooks = {
    async onGetDirectoryHandle(ctx) {
      if (ctx.options?.create === true && ctx.name === targetFirstBucket && store && !closeReport) {
        closeReport = await store.closeAsync({ reason: 'probe-close-during-hash-bucket-open' });
        events.push(Object.freeze({ kind: 'close-called-during-bucket-open', name: ctx.name, parentPath: ctx.dir?.path || '', inFlightAtClose: closeReport.inFlightAtClose }));
      }
    },
    async onCreateDirectory({ dir, child, name, options }) { events.push(Object.freeze({ kind: 'create-directory', parentPath: dir?.path || '', path: child?.path || '', name, create: options?.create === true })); },
    async onCreateFile({ dir, file, name, options }) { events.push(Object.freeze({ kind: 'create-file', parentPath: dir?.path || '', path: file?.path || '', name, create: options?.create === true })); },
    async onRemoveEntry({ dir, name }) { events.push(Object.freeze({ kind: 'remove-entry', path: dir.childPath(name) })); }
  };
  return await withFakeNavigator(async (root) => {
    store = createOpfsAsyncBlockStore({ name: `${REVISION}-close-abort-bucket-open-store`, prefix, trace });
    const hash = await digestBytesHex(payload);
    targetFirstBucket = hash.slice(0, 2);
    targetSecondBucket = hash.slice(2, 4);
    const rejectedPut = await capture('close-during-bucket-open-put', () => store.put(payload, { label: 'close-during-bucket-open-put' }));
    const createdSecondBucket = events.some((row) => row.kind === 'create-directory' && row.name === targetSecondBucket && row.parentPath.endsWith(`/${targetFirstBucket}`));
    return { rejectedPut, closeReport, snapshot: store.snapshot(), tree: fakeTreeSummary(root), events, traceKinds: trace.kinds(), targetFirstBucket, targetSecondBucket, createdSecondBucket, createdFiles: events.filter((row) => row.kind === 'create-file') };
  }, { hooks });
}

export async function runProbe() {
  const started = performance.now();
  const closeDuringWrite = await runCloseDuringWriteCase();
  const closeDuringBucketOpen = await runCloseDuringBucketOpenCase();

  assert.equal(closeDuringWrite.closeReport?.disposition, 'closed', 'closeAsync must close the store during the in-flight put');
  assert.ok(closeDuringWrite.closeReport.inFlightAtClose >= 1, 'close report must expose the in-flight operation count');
  assert.equal(closeDuringWrite.rejectedPut.ok, false, 'in-flight put must reject after closeAsync aborts the lifecycle signal');
  assert.equal(closeDuringWrite.rejectedPut.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(closeDuringWrite.rejectedPut.error.detail.context?.rollbackOwnsFinalBlock, true, 'owned in-flight put should be rollback eligible');
  assert.equal(closeDuringWrite.rejectedPut.error.detail.rollback?.attempted, true, 'owned in-flight put should attempt rollback after close abort');
  assert.equal(closeDuringWrite.rejectedPut.error.detail.rollback?.deleted, true, 'rollback must delete the owned partial block even though the store is closed');
  assert.equal(closeDuringWrite.rejectedPut.error.detail.rollback?.preserved, false, 'partial close-aborted block must not be preserved as an acknowledged commit');
  assert.equal(closeDuringWrite.verifyAfterCloseAbort.present, false, 'fresh provider must not find the unacknowledged close-aborted digest');
  assert.equal(closeDuringWrite.tree.fileCount, 0, 'close-aborted in-flight put must leave no block files');
  assert.equal(closeDuringWrite.postCloseGet.ok, false, 'future operation on closed provider must reject');
  assert.equal(closeDuringWrite.postCloseGet.error.code, 'BRT_OPFS_STORE_CLOSED');
  assert.ok(closeDuringWrite.events.some((row) => row.kind === 'stream-abort'), 'open writable stream must be aborted');
  assert.ok(closeDuringWrite.events.some((row) => row.kind === 'remove-entry'), 'owned partial block path must be removed during rollback');
  assert.ok(closeDuringWrite.traceKinds.includes('storage:opfs-blockstore-close'), 'close trace missing');
  assert.ok(closeDuringWrite.traceKinds.includes('storage:opfs-block-abort'), 'close-induced abort trace missing');
  assert.ok(closeDuringWrite.traceKinds.includes('storage:opfs-block-put-rollback'), 'rollback trace missing');
  assert.equal(closeDuringWrite.snapshot.inFlightOperations, 0, 'operation should be settled after rejected put');
  assert.ok(closeDuringWrite.snapshot.stats.closeAbortSignals >= 1, 'close should abort the lifecycle signal');
  assert.ok(closeDuringWrite.snapshot.stats.closeAbortRejects >= 1, 'operation should observe close-induced abort');
  assert.ok(closeDuringWrite.snapshot.stats.operationsStarted >= 1, 'in-flight put should be counted as a lifecycle operation');
  assert.ok(closeDuringWrite.snapshot.stats.closedOperationRejects >= 1, 'post-close operation should be rejected before admission');
  assert.ok(closeDuringWrite.snapshot.stats.operationsSettled >= 1, 'in-flight put should settle');

  assert.equal(closeDuringBucketOpen.closeReport?.disposition, 'closed', 'closeAsync must close while mutable bucket open is in flight');
  assert.equal(closeDuringBucketOpen.rejectedPut.ok, false, 'bucket-open put must reject after close aborts the lifecycle signal');
  assert.equal(closeDuringBucketOpen.rejectedPut.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(closeDuringBucketOpen.createdSecondBucket, false, 'close-aborted bucket open must not create the second digest bucket');
  assert.equal(closeDuringBucketOpen.createdFiles.length, 0, 'close-aborted bucket open must not create staged or final block files');
  assert.equal(closeDuringBucketOpen.tree.fileCount, 0, 'close-aborted bucket open must leave no block files');
  assert.ok(closeDuringBucketOpen.snapshot.stats.closeAbortRejects >= 1, 'bucket-open path should observe close-induced abort');
  assert.ok(closeDuringBucketOpen.traceKinds.includes('storage:opfs-block-abort'), 'bucket-open abort trace missing');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-close-abort-inflight-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that closeAsync is an aborting lifecycle fence for an in-flight OPFS put, not only a future-operation rejection flag.',
    observations: { closeDuringWrite, closeDuringBucketOpen },
    claimsChecked: [
      'closeAsync aborts the store lifecycle signal while a put is in flight',
      'the in-flight put rejects with BRT_OPFS_OPERATION_ABORTED instead of acknowledging after close',
      'rollback is allowed to clean up the owned partial block even after the store is marked closed',
      'a fresh provider cannot verify the unacknowledged digest after close-induced abort',
      'future operations on the closed provider still reject with BRT_OPFS_STORE_CLOSED',
      'operation snapshots expose close abort counts and zero in-flight operations after settlement',
      'close during mutable bucket open rejects before staged/final block file creation'
    ],
    nonClaims: [
      'Fake-OPFS release-tier proof only; no browser matrix, fsync, power-loss, quota/eviction, organic crash, or cross-browser durability claim.',
      'If the platform has already closed a valid content-addressed final block before an observer/caller abort, the existing rev0100 valid-block-preserve contract still applies.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-close-abort-inflight-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: captureError(error) };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_close_abort_inflight_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
