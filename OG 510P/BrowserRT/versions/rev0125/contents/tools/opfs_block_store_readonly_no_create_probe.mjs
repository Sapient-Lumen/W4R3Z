#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { createDirectoryMutationRecorder, fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const RELEASE_TASK = 'opfs:block-store-readonly-no-create-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-READONLY-NO-CREATE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

async function capture(label, fn) {
  try { return { label, ok: true, value: await fn() }; }
  catch (error) { return { label, ok: false, error: captureError(error) }; }
}

function payloadOf(label) {
  return new TextEncoder().encode(`BrowserRT ${REVISION} OPFS readonly no-create proof ${label}`);
}

function sameBytes(a, b) {
  return a.byteLength === b.byteLength && a.every((x, i) => x === b[i]);
}

function refForHash(hash, bytes = 0, path = null) {
  return Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest: `sha256:${hash}`, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes, path });
}

async function runMissingReadOnlyCase() {
  const payload = payloadOf('missing-read-only');
  const hash = await digestBytesHex(payload);
  const prefix = `browserrt/${REVISION}/fake-readonly-no-create/missing-read-only`;
  const recorder = createDirectoryMutationRecorder('missing-read-only');
  return await withFakeNavigator(async (root) => {
    const trace = new TraceLog();
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-readonly-no-create-missing`, prefix, trace });
    const ref = refForHash(hash, payload.byteLength, store.blockPath(hash));
    const before = fakeTreeSummary(root);
    const verifyMissing = await store.verify(ref);
    const afterVerify = fakeTreeSummary(root);
    const hasMissing = await store.has(ref);
    const afterHas = fakeTreeSummary(root);
    const deleteMissing = await store.delete(ref);
    const afterDelete = fakeTreeSummary(root);
    const getMissing = await capture('get-missing-no-create', () => store.get(ref));
    const afterGet = fakeTreeSummary(root);
    return { before, verifyMissing, afterVerify, hasMissing, afterHas, deleteMissing, afterDelete, getMissing, afterGet, snapshot: store.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot(), mutations: recorder.snapshot() };
  }, { hooks: recorder.hooks });
}

async function runUnverifiedHasMissingCase() {
  const payload = payloadOf('unverified-has-missing');
  const hash = await digestBytesHex(payload);
  const prefix = `browserrt/${REVISION}/fake-readonly-no-create/unverified-has-missing`;
  const recorder = createDirectoryMutationRecorder('unverified-has-missing');
  return await withFakeNavigator(async (root) => {
    const trace = new TraceLog();
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-readonly-no-create-unverified-has`, prefix, verifyOnHas: false, trace });
    const ref = refForHash(hash, payload.byteLength, store.blockPath(hash));
    const before = fakeTreeSummary(root);
    const hasMissing = await store.has(ref);
    const afterHas = fakeTreeSummary(root);
    return { before, hasMissing, afterHas, snapshot: store.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot(), mutations: recorder.snapshot() };
  }, { hooks: recorder.hooks });
}

async function runExistingBlockStillWorksCase() {
  const payload = payloadOf('existing-block-still-works');
  const prefix = `browserrt/${REVISION}/fake-readonly-no-create/existing-block`;
  const recorder = createDirectoryMutationRecorder('existing-block-still-works');
  return await withFakeNavigator(async (root) => {
    const trace = new TraceLog();
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-readonly-no-create-existing`, prefix, trace });
    const put = await store.put(payload, { label: 'readonly-no-create-existing-seed' });
    const afterPut = fakeTreeSummary(root);
    const mutationCountAfterPut = recorder.snapshot().eventCount;
    const verifyExisting = await store.verify(put.ref);
    const hasExisting = await store.has(put.ref);
    const getExisting = await store.get(put.ref);
    const afterReads = fakeTreeSummary(root);
    const mutationCountAfterReads = recorder.snapshot().eventCount;
    const deleteExisting = await store.delete(put.ref);
    const afterDelete = fakeTreeSummary(root);
    const mutationCountAfterDelete = recorder.snapshot().eventCount;
    const deleteMissingAgain = await store.delete(put.ref);
    const afterDeleteAgain = fakeTreeSummary(root);
    const mutationCountAfterDeleteAgain = recorder.snapshot().eventCount;
    return { put: { digest: put.digest, bytes: put.bytes, duplicate: put.duplicate, ref: put.ref }, afterPut, mutationCountAfterPut, verifyExisting, hasExisting, getExistingSameBytes: sameBytes(getExisting, payload), afterReads, mutationCountAfterReads, deleteExisting, afterDelete, mutationCountAfterDelete, deleteMissingAgain, afterDeleteAgain, mutationCountAfterDeleteAgain, snapshot: store.snapshot(), traceKinds: trace.kinds(), trace: trace.snapshot(), mutations: recorder.snapshot() };
  }, { hooks: recorder.hooks });
}

export async function runProbe() {
  const started = performance.now();
  const missingReadOnly = await runMissingReadOnlyCase();
  const unverifiedHasMissing = await runUnverifiedHasMissingCase();
  const existingBlockStillWorks = await runExistingBlockStillWorksCase();

  assert.equal(missingReadOnly.before.dirCount, 0);
  assert.equal(missingReadOnly.afterVerify.dirCount, 0, 'verify missing must not create prefix/bucket directories');
  assert.equal(missingReadOnly.afterHas.dirCount, 0, 'has missing must not create prefix/bucket directories');
  assert.equal(missingReadOnly.afterDelete.dirCount, 0, 'delete missing must not create prefix/bucket directories');
  assert.equal(missingReadOnly.afterGet.dirCount, 0, 'get missing must not create prefix/bucket directories');
  assert.equal(missingReadOnly.afterGet.fileCount, 0, 'missing read-only case must leave no files');
  assert.equal(missingReadOnly.verifyMissing.present, false);
  assert.equal(missingReadOnly.verifyMissing.ok, false);
  assert.equal(missingReadOnly.hasMissing, false);
  assert.equal(missingReadOnly.deleteMissing, false);
  assert.equal(missingReadOnly.getMissing.ok, false);
  assert.equal(missingReadOnly.getMissing.error.name, 'NotFoundError');
  assert.equal(missingReadOnly.snapshot.opened, false, 'read-only misses must not mark store opened');
  assert.equal(missingReadOnly.snapshot.stats.opens, 0, 'read-only misses must not call mutable open()');
  assert.equal(missingReadOnly.snapshot.stats.noCreateMisses, 4, 'verify/has/delete/get should each record a no-create miss');
  assert.equal(missingReadOnly.mutations.byKind['create-directory'] || 0, 0, 'missing read-only case must create zero directories');
  assert.equal(missingReadOnly.mutations.byKind['create-file'] || 0, 0, 'missing read-only case must create zero files');
  assert.ok(missingReadOnly.traceKinds.includes('storage:opfs-block-no-create-miss'), 'missing read-only case should emit no-create miss trace');

  assert.equal(unverifiedHasMissing.before.dirCount, 0);
  assert.equal(unverifiedHasMissing.hasMissing, false, 'unverified has should still return false on missing block');
  assert.equal(unverifiedHasMissing.afterHas.dirCount, 0, 'verifyOnHas:false missing check must not create directories');
  assert.equal(unverifiedHasMissing.snapshot.opened, false, 'verifyOnHas:false missing check must not open mutable prefix');
  assert.equal(unverifiedHasMissing.snapshot.stats.opens, 0);
  assert.equal(unverifiedHasMissing.snapshot.stats.noCreateMisses, 1);
  assert.equal(unverifiedHasMissing.mutations.byKind['create-directory'] || 0, 0);
  assert.equal(unverifiedHasMissing.mutations.byKind['create-file'] || 0, 0);

  assert.equal(existingBlockStillWorks.put.duplicate, false, 'seed put should create a new block');
  assert.equal(existingBlockStillWorks.afterPut.fileCount, 1, 'seed put should create one block file');
  assert.equal(existingBlockStillWorks.verifyExisting.ok, true, 'existing block should still verify');
  assert.equal(existingBlockStillWorks.hasExisting, true, 'existing block should still be found');
  assert.equal(existingBlockStillWorks.getExistingSameBytes, true, 'existing block should still be readable');
  assert.equal(existingBlockStillWorks.afterReads.fileCount, 1, 'read-only existing checks should not remove files');
  assert.equal(existingBlockStillWorks.mutationCountAfterReads, existingBlockStillWorks.mutationCountAfterPut, 'read-only existing checks should not add mutations');
  assert.equal(existingBlockStillWorks.deleteExisting, true, 'delete existing should still remove the file');
  assert.equal(existingBlockStillWorks.afterDelete.fileCount, 0, 'delete existing should remove the block file');
  assert.equal(existingBlockStillWorks.deleteMissingAgain, false, 'second delete should be a no-op miss');
  assert.equal(existingBlockStillWorks.afterDeleteAgain.fileCount, 0, 'second delete miss should leave no files');
  assert.ok((existingBlockStillWorks.mutations.byKind['create-directory'] || 0) > 0, 'seed put should create directories');
  assert.equal(existingBlockStillWorks.mutations.byKind['create-file'] || 0, 2, 'seed put should create one staged temp file and one final block file');
  assert.equal(existingBlockStillWorks.snapshot.stats.stagedTempDeletes, 1, 'seed put should delete the staged temp file after final publish');
  assert.equal(existingBlockStillWorks.mutations.byKind['create-file'] || 0, 2, 'delete miss must not create another file');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-readonly-no-create-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Fake-OPFS proof that OpfsAsyncBlockStore missing get/has/verify and delete paths use no-create prefix/bucket opens and do not litter OPFS with empty directories, while existing put/read/delete behavior still works.',
    cases: { missingReadOnly, unverifiedHasMissing, existingBlockStillWorks },
    claimsChecked: [
      'verify/has/delete/get misses do not create prefix or bucket directories',
      'verifyOnHas:false has misses also avoid mutable prefix creation',
      'existing block verify/has/get paths still work without extra mutations',
      'delete existing still removes the block and repeated delete miss stays no-create',
      'noCreateMisses stat and storage:opfs-block-no-create-miss trace expose this boundary'
    ],
    nonClaims: [
      'Fake OPFS proof only; managed-browser proof covers Chromium OPFS behavior for the current slice.',
      'This does not claim recursive empty-directory cleanup, quota/eviction survival, fsync durability, crash/power-loss recovery, Web Locks fairness, cross-browser conformance, or production readiness.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-readonly-no-create-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[opfs_block_store_readonly_no_create_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
