#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'opfs:block-store-rollback-valid-block-preserve-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-ROLLBACK-VALID-BLOCK-PRESERVE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

async function capture(label, fn) {
  try { return { label, ok: true, value: await fn() }; }
  catch (error) { return { label, ok: false, error: captureError(error) }; }
}

function payloadOf(label, size = 2048) {
  const bytes = new Uint8Array(size);
  for (let i = 0; i < bytes.length; i += 1) bytes[i] = (17 + i * 43 + label.length * 19) & 255;
  bytes.set(new TextEncoder().encode(`BrowserRT ${REVISION} rollback valid block preserve ${label}`));
  return bytes;
}

function sameBytes(a, b) {
  return a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
}

function refForHash(hash, bytes, path) {
  return Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest: `sha256:${hash}`, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes, path });
}

function writeCloseThrowingTrace(events) {
  let thrown = false;
  return {
    emit(kind, detail = {}) {
      events.push(Object.freeze({ kind, digest: detail.digest ?? null, hash: detail.hash ?? null, reason: detail.reason ?? null, bytes: detail.bytes ?? null }));
      if (!thrown && kind === 'storage:opfs-block-write-close' && (detail?.purpose === 'publish-final' || String(detail?.fileName || '').endsWith('.blk'))) {
        thrown = true;
        throw new Error('intentional trace sink failure after valid block close');
      }
    }
  };
}

async function runTraceFailureAfterCloseCase() {
  const payload = payloadOf('trace-failure-after-close', 3072);
  const prefix = `browserrt/${REVISION}/fake-rollback-valid-preserve/trace-failure`;
  const traceEvents = [];
  return await withFakeNavigator(async (root) => {
    const throwingStore = createOpfsAsyncBlockStore({ name: `${REVISION}-rollback-preserve-trace-failure`, prefix, trace: writeCloseThrowingTrace(traceEvents) });
    const hash = await digestBytesHex(payload);
    const ref = refForHash(hash, payload.byteLength, throwingStore.blockPath(hash));
    const failedPut = await capture('trace-failure-after-close-preserves-valid-final-block', () => throwingStore.put(payload, { label: 'trace-failure-after-close' }));
    const verifier = createOpfsAsyncBlockStore({ name: `${REVISION}-rollback-preserve-trace-verifier`, prefix });
    const verifyAfterFailure = await verifier.verify(ref);
    const readAfterFailure = await verifier.get(ref);
    return { failedPut, verifyAfterFailure, bytesPreserved: sameBytes(readAfterFailure, payload), throwingSnapshot: throwingStore.snapshot(), verifierSnapshot: verifier.snapshot(), tree: fakeTreeSummary(root), traceEvents };
  });
}

async function runAbortAfterCloseCase() {
  const payload = payloadOf('abort-after-close', 4096);
  const prefix = `browserrt/${REVISION}/fake-rollback-valid-preserve/abort-after-close`;
  const controller = new AbortController();
  const events = [];
  const hooks = {
    async onClose({ file, bytes }) {
      events.push(Object.freeze({ kind: 'close', path: file.path, bytes: bytes.byteLength }));
      if (file.name.endsWith('.blk')) controller.abort('caller-aborted-after-close');
    },
    async onRemoveEntry({ dir, name }) { events.push(Object.freeze({ kind: 'remove-entry', path: dir.childPath(name) })); }
  };
  return await withFakeNavigator(async (root) => {
    const trace = new TraceLog();
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-rollback-preserve-abort-after-close`, prefix, trace });
    const hash = await digestBytesHex(payload);
    const ref = refForHash(hash, payload.byteLength, store.blockPath(hash));
    const failedPut = await capture('abort-after-close-preserves-valid-final-block', () => store.put(payload, { label: 'abort-after-close' }, { signal: controller.signal }));
    const verifyAfterFailure = await store.verify(ref);
    const readAfterFailure = await store.get(ref);
    return { failedPut, verifyAfterFailure, bytesPreserved: sameBytes(readAfterFailure, payload), snapshot: store.snapshot(), tree: fakeTreeSummary(root), events, traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks });
}

async function runInvalidOwnedFailureStillDeletesCase() {
  const payload = payloadOf('invalid-owned-failure-still-deletes', 2560);
  const prefix = `browserrt/${REVISION}/fake-rollback-valid-preserve/invalid-delete`;
  const events = [];
  let failBeforeClose = true;
  const hooks = {
    async onBeforeClose({ file, bytes }) {
      events.push(Object.freeze({ kind: 'before-close', path: file.path, bytes: bytes.byteLength }));
      if (failBeforeClose && file.name.endsWith('.blk')) {
        failBeforeClose = false;
        throw new Error('intentional fake write failure before final bytes are committed');
      }
    },
    async onAbort({ file }) { events.push(Object.freeze({ kind: 'stream-abort', path: file.path })); },
    async onRemoveEntry({ dir, name }) { events.push(Object.freeze({ kind: 'remove-entry', path: dir.childPath(name) })); }
  };
  return await withFakeNavigator(async (root) => {
    const trace = new TraceLog();
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-rollback-preserve-invalid-delete`, prefix, trace });
    const failedPut = await capture('invalid-owned-failure-still-rolls-back-file', () => store.put(payload, { label: 'invalid-owned-failure' }));
    return { failedPut, snapshot: store.snapshot(), tree: fakeTreeSummary(root), events, traceKinds: trace.kinds(), trace: trace.snapshot() };
  }, { hooks });
}

export async function runProbe() {
  const started = performance.now();
  const traceFailureAfterClose = await runTraceFailureAfterCloseCase();
  const abortAfterClose = await runAbortAfterCloseCase();
  const invalidOwnedFailureStillDeletes = await runInvalidOwnedFailureStillDeletesCase();

  assert.equal(traceFailureAfterClose.failedPut.ok, false, 'trace sink failure after close must reject the put');
  assert.equal(traceFailureAfterClose.failedPut.error.code, 'BRT_OPFS_OPERATION_FAILED');
  assert.equal(traceFailureAfterClose.failedPut.error.detail.rollback?.attempted, true);
  assert.equal(traceFailureAfterClose.failedPut.error.detail.rollback?.skipped, true, 'valid final block rollback must skip deletion');
  assert.equal(traceFailureAfterClose.failedPut.error.detail.rollback?.preserved, true, 'valid final block rollback should preserve valid bytes');
  assert.equal(traceFailureAfterClose.failedPut.error.detail.rollback?.reason, 'valid-final-block-preserved');
  assert.equal(traceFailureAfterClose.verifyAfterFailure.ok, true, 'valid block must verify after trace failure');
  assert.equal(traceFailureAfterClose.bytesPreserved, true, 'valid bytes must be preserved after trace failure');
  assert.equal(traceFailureAfterClose.tree.fileCount, 1, 'trace failure should leave the valid block, not delete it');
  assert.equal(traceFailureAfterClose.throwingSnapshot.stats.rollbackValidBlockPreserves, 1);
  assert.equal(traceFailureAfterClose.throwingSnapshot.stats.rollbackDeletes, 0);
  assert.ok(traceFailureAfterClose.traceEvents.some((row) => row.kind === 'storage:opfs-block-put-rollback-preserved'));

  assert.equal(abortAfterClose.failedPut.ok, false, 'abort after close must reject the put');
  assert.equal(abortAfterClose.failedPut.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(abortAfterClose.failedPut.error.detail.rollback?.preserved, true, 'abort after close should preserve a valid content-addressed block');
  assert.equal(abortAfterClose.verifyAfterFailure.ok, true, 'valid block must verify after abort-after-close failure');
  assert.equal(abortAfterClose.bytesPreserved, true, 'abort-after-close valid bytes must be preserved');
  assert.equal(abortAfterClose.tree.fileCount, 1, 'abort-after-close should leave one valid block file');
  assert.equal(abortAfterClose.snapshot.stats.rollbackValidBlockPreserves, 1);
  assert.equal(abortAfterClose.snapshot.stats.rollbackDeletes, 0);
  assert.ok(!abortAfterClose.events.some((row) => row.kind === 'remove-entry' && String(row.path || '').endsWith('.blk')), 'abort-after-close should not remove a valid final block');
  assert.ok(abortAfterClose.events.some((row) => row.kind === 'remove-entry' && String(row.path || '').includes('.brt-stage-')), 'abort-after-close may clean up the staged temp file');
  assert.ok(abortAfterClose.traceKinds.includes('storage:opfs-block-put-rollback-preserved'));

  assert.equal(invalidOwnedFailureStillDeletes.failedPut.ok, false, 'invalid owned write failure must reject');
  assert.equal(invalidOwnedFailureStillDeletes.failedPut.error.detail.rollback?.attempted, true);
  assert.equal(invalidOwnedFailureStillDeletes.failedPut.error.detail.rollback?.preserved, false, 'invalid owned file must not be preserved');
  assert.equal(invalidOwnedFailureStillDeletes.failedPut.error.detail.rollback?.deleted, true, 'invalid owned file must still be deleted');
  assert.equal(invalidOwnedFailureStillDeletes.tree.fileCount, 0, 'invalid owned failure should leave no block file');
  assert.equal(invalidOwnedFailureStillDeletes.snapshot.stats.rollbackDeletes, 1);
  assert.equal(invalidOwnedFailureStillDeletes.snapshot.stats.rollbackValidBlockPreserves, 0);
  assert.ok(invalidOwnedFailureStillDeletes.events.some((row) => row.kind === 'remove-entry'));
  assert.ok(invalidOwnedFailureStillDeletes.traceKinds.includes('storage:opfs-block-put-rollback'));

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-rollback-valid-block-preserve-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that failed-put rollback no longer deletes already-valid content-addressed final blocks after late aborts or observer failures, while invalid owned files still roll back.',
    observations: { traceFailureAfterClose, abortAfterClose, invalidOwnedFailureStillDeletes },
    claimsChecked: [
      'trace/observer failure after a valid block close rejects the call but preserves the valid final block',
      'caller abort after a valid block close rejects the call but preserves the valid final block',
      'invalid owned files created by failed writes are still deleted by rollback',
      'preserve-vs-delete decisions are exposed via rollbackValidBlockPreserves, rollbackIntegrityChecks, and storage:opfs-block-put-rollback-preserved'
    ],
    nonClaims: [
      'Fake OPFS release proof only; the browser companion proof supplies focused Chromium evidence for the trace-failure path.',
      'Preserving valid content-addressed blocks on failed-put rollback is not a transaction, cancellation guarantee, fsync guarantee, crash-recovery proof, cross-tab atomicity proof, eviction guarantee, or production-readiness claim.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-rollback-valid-block-preserve-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: captureError(error) };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_rollback_valid_block_preserve_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
