#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { createDirectoryMutationRecorder, fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-PROBE.json`;
const TASK_ID = 'opfs:block-store-raw-composite-abort-signal-proof';
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

async function runPreAbortedAbortSignalCase(payload) {
  const trace = new TraceLog();
  const recorder = createDirectoryMutationRecorder(`${REVISION}-raw-composite-preabort-recorder`);
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-raw-composite-preabort-store`, prefix: `browserrt/${REVISION}/raw-composite-preabort`, trace });
    const liveSignal = new AbortController();
    const preAborted = new AbortController();
    preAborted.abort(new Error('secondary abortSignal canceled before provider open'));
    const rejectedPut = await expectReject('pre-aborted-abortSignal-with-live-signal-put', () => store.put(payload, { label: 'pre-aborted-abortSignal-with-live-signal-put' }, { signal: liveSignal.signal, abortSignal: preAborted.signal }));
    const invalidSibling = await expectReject('invalid-abortSignal-with-valid-signal-put', () => store.put(payload, { label: 'invalid-abortSignal-with-valid-signal-put' }, { signal: liveSignal.signal, abortSignal: { aborted: false } }));
    return { rejectedPut, invalidSibling, snapshot: store.snapshot(), tree: fakeTreeSummary(root), recorder: recorder.snapshot(), traceKinds: trace.kinds() };
  }, { hooks: recorder.hooks });
}

async function runMidWriteSecondaryAbortCase(payload) {
  const trace = new TraceLog();
  const primary = new AbortController();
  const secondary = new AbortController();
  const events = [];
  const hooks = {
    async onWrite({ file, bytes }) {
      events.push({ kind: 'write', path: file.path, bytes: bytes.byteLength });
      if (file.name.endsWith('.blk')) secondary.abort('secondary-abortSignal-fired-during-write');
    },
    async onAbort({ file }) { events.push({ kind: 'stream-abort', path: file.path }); },
    async onRemoveEntry({ dir, name }) { events.push({ kind: 'remove-entry', path: dir.childPath(name) }); }
  };
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-raw-composite-midwrite-store`, prefix: `browserrt/${REVISION}/raw-composite-midwrite`, trace });
    const hash = await digestBytesHex(payload);
    const ref = refForPayload(hash, payload.byteLength, store.blockPath(hash));
    const rejectedPut = await expectReject('secondary-abortSignal-mid-write-put', () => store.put(payload, { label: 'secondary-abortSignal-mid-write-put' }, { signal: primary.signal, abortSignal: secondary.signal }));
    const verifyAfterAbort = await store.verify(ref, { signal: null, abortSignal: null });
    return { rejectedPut, verifyAfterAbort, snapshot: store.snapshot(), tree: fakeTreeSummary(root), events, traceKinds: trace.kinds() };
  }, { hooks });
}

async function runReadAbortSignalCompositionCase(payload) {
  const trace = new TraceLog();
  return await withFakeNavigator(async () => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-raw-composite-read-store`, prefix: `browserrt/${REVISION}/raw-composite-read`, trace });
    const put = await store.put(payload, { label: 'raw-composite-read-seed' }, { signal: null, abortSignal: null });
    const liveSignal = new AbortController();
    const readAbort = new AbortController();
    readAbort.abort('secondary abortSignal canceled read before provider open');
    const rejectedGet = await expectReject('pre-aborted-abortSignal-with-live-signal-get', () => store.get(put.ref, { signal: liveSignal.signal, abortSignal: readAbort.signal }));
    const validVerify = await store.verify(put.ref, { signal: null, abortSignal: null });
    return { put: { digest: put.digest, bytes: put.bytes, path: put.path }, rejectedGet, validVerify, snapshot: store.snapshot(), traceKinds: trace.kinds() };
  });
}

export async function runProbe() {
  const started = performance.now();
  const payload = new Uint8Array(4096);
  for (let i = 0; i < payload.length; i += 1) payload[i] = (101 + i * 29 + (i >>> 3)) & 255;
  payload.set(new TextEncoder().encode(`BrowserRT ${REVISION} raw OPFS composite abort signal proof`));

  const preAborted = await runPreAbortedAbortSignalCase(payload);
  const midWrite = await runMidWriteSecondaryAbortCase(payload);
  const readAbort = await runReadAbortSignalCompositionCase(payload);

  assert.equal(preAborted.rejectedPut.ok, false, 'pre-aborted secondary abortSignal must reject raw put');
  assert.equal(preAborted.rejectedPut.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(preAborted.invalidSibling.ok, false, 'invalid abortSignal sibling must not be masked by valid signal');
  assert.equal(preAborted.invalidSibling.error.code, 'BRT_OPFS_ABORT_SIGNAL_INVALID');
  assert.equal(preAborted.snapshot.opened, false, 'pre-aborted/invalid option pair must not open mutable OPFS prefix');
  assert.equal(preAborted.tree.fileCount, 0, 'pre-aborted/invalid option pair must create no files');
  assert.equal(preAborted.tree.dirCount, 0, 'pre-aborted/invalid option pair must create no directories');
  assert.equal(preAborted.snapshot.stats.compositeAbortSignals, 1, 'one valid signal pair should count as a composite abort signal');
  assert.equal(preAborted.snapshot.stats.abortSignalOptionPairs, 1, 'valid signal+abortSignal pair should count option-pair exposure before invalid pair fails closed');
  assert.ok(preAborted.traceKinds.includes('storage:opfs-block-composite-abort-signal'), 'pre-abort case should trace composite raw OPFS signal');
  assert.ok(preAborted.traceKinds.includes('storage:opfs-block-abort-signal-invalid'), 'invalid sibling should trace invalid raw OPFS signal');

  assert.equal(midWrite.rejectedPut.ok, false, 'secondary abortSignal fired during write must reject put');
  assert.equal(midWrite.rejectedPut.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(midWrite.verifyAfterAbort.present, false, 'mid-write secondary abort must leave no valid final block');
  assert.equal(midWrite.tree.fileCount, 0, 'mid-write secondary abort must roll back created block file');
  assert.ok(midWrite.events.some((row) => row.kind === 'stream-abort'), 'mid-write secondary abort must abort open writable stream');
  assert.ok(midWrite.events.some((row) => row.kind === 'remove-entry'), 'mid-write secondary abort must remove created final path');
  assert.ok(midWrite.snapshot.stats.rollbackAttempts >= 1, 'mid-write secondary abort should count rollback');
  assert.ok(midWrite.snapshot.stats.compositeAbortSignals >= 1, 'mid-write secondary abort should count composite signal');
  assert.ok(midWrite.traceKinds.includes('storage:opfs-block-composite-abort-signal'), 'mid-write case should trace composite raw OPFS signal');

  assert.equal(readAbort.rejectedGet.ok, false, 'pre-aborted secondary abortSignal must reject raw get even when signal is live');
  assert.equal(readAbort.rejectedGet.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(readAbort.validVerify.ok, true, 'seeded block remains valid after rejected composite read');
  assert.ok(readAbort.snapshot.stats.compositeAbortSignals >= 1, 'read abort should count composite signal');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-raw-composite-abort-signal-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that raw OpfsAsyncBlockStore calls compose signal and abortSignal instead of silently choosing one caller-owned abort source.',
    observations: { preAborted, midWrite, readAbort },
    claimsChecked: [
      'raw OPFS put rejects when abortSignal is already aborted even if signal is live',
      'raw OPFS invalid abortSignal shape is not masked by a valid signal sibling',
      'raw OPFS mid-write abortSignal reaches provider checkpoints and rolls back created block files',
      'raw OPFS get rejects when abortSignal is already aborted even if signal is live',
      'composite raw OPFS signal decisions are visible in stats and trace output'
    ],
    nonClaims: [
      'Fake-OPFS release-tier proof only; managed Chromium proof covers browser-realm direct OPFS composition.',
      'This does not prove cross-browser OPFS behavior, fsync durability, quota/eviction survival, crash/power-loss safety, Web Locks fairness, or production storage readiness.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-raw-composite-abort-signal-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_raw_composite_abort_signal_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
