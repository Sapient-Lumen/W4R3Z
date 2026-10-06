#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const ABORT_SIGNAL_CASE_MARKERS = ['mid-write-abort-onWrite', 'mid-write-abort-onBeforeClose'];
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-ABORT-SIGNAL-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

async function expectReject(label, fn) {
  try { await fn(); }
  catch (error) { return { label, ok: false, error: captureError(error) }; }
  return { label, ok: true, error: null };
}

function refForPayload(hash, bytes, path = null) {
  return Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest: `sha256:${hash}`, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes, path });
}

async function runPreAbortedCase(payload) {
  const trace = new TraceLog();
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-fake-opfs-preabort-store`, prefix: `browserrt/${REVISION}/fake-opfs-preabort`, trace });
    const controller = new AbortController();
    controller.abort(new Error('caller canceled before put'));
    const rejectedPut = await expectReject('pre-aborted-put', () => store.put(payload, { label: 'pre-aborted-put' }, { signal: controller.signal }));
    const snapshotAfterRejectedPut = store.snapshot();
    const treeAfterRejectedPut = fakeTreeSummary(root);
    const invalidSignal = await expectReject('invalid-signal-put', () => store.put(payload, { label: 'invalid-signal-put' }, { signal: 'not-an-abort-signal' }));
    const validPut = await store.put(payload, { label: 'valid-after-preabort' }, { signal: null });
    const readController = new AbortController();
    readController.abort('caller canceled read');
    const rejectedGet = await expectReject('pre-aborted-get', () => store.get(validPut.ref, { abortSignal: readController.signal }));
    const verify = await store.verify(validPut.ref, { signal: null });
    return { rejectedPut, snapshotAfterRejectedPut, treeAfterRejectedPut, invalidSignal, validPut, rejectedGet, verify, snapshot: store.snapshot(), traceKinds: trace.kinds() };
  });
}

async function runMidWriteAbortCase(payload, abortHookName) {
  const trace = new TraceLog();
  const controller = new AbortController();
  const events = [];
  const hooks = {
    async onWrite({ file, bytes }) {
      events.push({ kind: 'write', path: file.path, bytes: bytes.byteLength });
      if (abortHookName === 'onWrite' && file.name.endsWith('.blk')) controller.abort(`${abortHookName}:caller-canceled`);
    },
    async onBeforeClose({ file, bytes }) {
      events.push({ kind: 'before-close', path: file.path, bytes: bytes.byteLength });
      if (abortHookName === 'onBeforeClose' && file.name.endsWith('.blk')) controller.abort(`${abortHookName}:caller-canceled`);
    },
    async onAbort({ file }) { events.push({ kind: 'stream-abort', path: file.path }); },
    async onRemoveEntry({ dir, name }) { events.push({ kind: 'remove-entry', path: dir.childPath(name) }); }
  };
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-fake-opfs-${abortHookName}-store`, prefix: `browserrt/${REVISION}/fake-opfs-${abortHookName}`, trace });
    const hash = await digestBytesHex(payload);
    const ref = refForPayload(hash, payload.byteLength, store.blockPath(hash));
    const rejectedPut = await expectReject(`mid-write-abort-${abortHookName}`, () => store.put(payload, { label: `mid-write-abort-${abortHookName}` }, { signal: controller.signal }));
    const verifyAfterAbort = await store.verify(ref, { signal: null });
    const treeAfterAbort = fakeTreeSummary(root);
    return { rejectedPut, verifyAfterAbort, treeAfterAbort, events, snapshot: store.snapshot(), traceKinds: trace.kinds() };
  }, { hooks });
}

export async function runProbe() {
  const started = performance.now();
  const payload = new Uint8Array(8192);
  for (let i = 0; i < payload.length; i += 1) payload[i] = (73 + i * 41 + (i >>> 2)) & 255;
  payload.set(new TextEncoder().encode(`BrowserRT ${REVISION} OPFS explicit abort signal proof`));

  const preAborted = await runPreAbortedCase(payload);
  const abortDuringWrite = await runMidWriteAbortCase(payload, 'onWrite');
  const abortBeforeClose = await runMidWriteAbortCase(payload, 'onBeforeClose');

  assert.equal(preAborted.rejectedPut.ok, false, 'pre-aborted put must reject');
  assert.equal(preAborted.rejectedPut.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(preAborted.snapshotAfterRejectedPut.opened, false, 'pre-aborted put must not open OPFS provider');
  assert.equal(preAborted.treeAfterRejectedPut.fileCount, 0, 'pre-aborted put must not create a block file');
  assert.equal(preAborted.invalidSignal.ok, false, 'invalid signal shape must reject');
  assert.equal(preAborted.invalidSignal.error.code, 'BRT_OPFS_ABORT_SIGNAL_INVALID');
  assert.equal(preAborted.rejectedGet.ok, false, 'pre-aborted get must reject');
  assert.equal(preAborted.rejectedGet.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(preAborted.verify.ok, true, 'valid put after pre-aborted attempt must verify');
  assert.ok(preAborted.traceKinds.includes('storage:opfs-block-abort'), 'pre-abort trace must be recorded');
  assert.ok(preAborted.traceKinds.includes('storage:opfs-block-abort-signal-invalid'), 'invalid signal trace must be recorded');

  for (const result of [abortDuringWrite, abortBeforeClose]) {
    assert.equal(result.rejectedPut.ok, false, `${result.rejectedPut.label} must reject`);
    assert.equal(result.rejectedPut.error.code, 'BRT_OPFS_OPERATION_ABORTED');
    assert.equal(result.rejectedPut.error.detail.rollback?.attempted, true, `${result.rejectedPut.label} should attempt rollback`);
    assert.ok(result.snapshot.stats.rollbackAttempts >= 1, `${result.rejectedPut.label} should count rollback attempt`);
    assert.ok(result.traceKinds.includes('storage:opfs-block-abort'), `${result.rejectedPut.label} abort trace missing`);
  }
  assert.equal(abortDuringWrite.verifyAfterAbort.present, false, `${abortDuringWrite.rejectedPut.label} must not leave a valid final block`);
  assert.equal(abortDuringWrite.treeAfterAbort.fileCount, 0, `${abortDuringWrite.rejectedPut.label} must leave no block files after rollback`);
  assert.ok(abortDuringWrite.events.some((row) => row.kind === 'remove-entry'), `${abortDuringWrite.rejectedPut.label} should remove created block path during rollback`);
  assert.ok(abortDuringWrite.traceKinds.includes('storage:opfs-block-put-rollback'), `${abortDuringWrite.rejectedPut.label} rollback trace missing`);
  assert.ok(abortDuringWrite.events.some((row) => row.kind === 'stream-abort'), 'abort during write must abort the open writable stream before rollback');

  assert.equal(abortBeforeClose.verifyAfterAbort.present, true, `${abortBeforeClose.rejectedPut.label} leaves a valid final block that rev0100 rollback preserves`);
  assert.equal(abortBeforeClose.rejectedPut.error.detail.rollback?.preserved, true, `${abortBeforeClose.rejectedPut.label} should preserve the valid final block`);
  assert.equal(abortBeforeClose.rejectedPut.error.detail.rollback?.reason, 'valid-final-block-preserved', `${abortBeforeClose.rejectedPut.label} preserve reason`);
  assert.ok(abortBeforeClose.snapshot.stats.rollbackValidBlockPreserves >= 1, `${abortBeforeClose.rejectedPut.label} should count rollback valid-block preserve`);
  assert.ok(abortBeforeClose.traceKinds.includes('storage:opfs-block-put-rollback-preserved'), `${abortBeforeClose.rejectedPut.label} preserve trace missing`);

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-abort-signal-proof`, task_id: 'opfs:block-store-abort-signal-proof', status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that OpfsAsyncBlockStore honors explicit caller AbortSignal/abortSignal options before provider checkpoints, rejects invalid signal shapes, and rolls back aborted put writes without claiming storage-lane timeout cancellation.',
    observations: { preAborted, abortDuringWrite, abortBeforeClose },
    claimsChecked: [
      'pre-aborted put fails before opening OPFS or creating a block file',
      'invalid signal values fail closed with BRT_OPFS_ABORT_SIGNAL_INVALID',
      'pre-aborted read operations fail with BRT_OPFS_OPERATION_ABORTED',
      'abort during write aborts the writable stream and rolls back the created block file',
      'abort after close is converted into a failed put and rev0100 preserves the committed valid content-addressed block'
    ],
    nonClaims: [
      'Fake-OPFS release-tier proof only; managed Chromium proof covers browser realm pre-abort behavior.',
      'This does not turn storage-lane operation timeouts into provider cancellation, and does not prove browser fsync durability, crash/power-loss safety, quota/eviction behavior, Web Locks fairness, or cross-browser conformance.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-abort-signal-proof`, task_id: 'opfs:block-store-abort-signal-proof', status: 'failed', generatedAt: new Date().toISOString(), error: captureError(error) };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_abort_signal_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
