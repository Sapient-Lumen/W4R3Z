#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator, writeFakePath } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'opfs:block-store-staged-recovery-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-STAGED-RECOVERY-PROBE.json`;
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
  const header = new TextEncoder().encode(`BrowserRT ${REVISION} staged recovery proof ${label}`);
  bytes.set(header);
  for (let i = header.length; i < bytes.length; i += 1) bytes[i] = (label.length * 31 + i * 17 + (i >>> 3)) & 255;
  return bytes;
}

function makeRecorder() {
  const events = [];
  const push = (event) => events.push(Object.freeze({ seq: events.length + 1, ...event }));
  const hooks = {
    async onEntries({ dir }) { push({ kind: 'entries', path: dir.path }); },
    async onCreateFile({ dir, file, name, options }) { push({ kind: 'create-file', name, path: file.path, parentPath: dir.path, options: Object.freeze({ ...(options || {}) }) }); },
    async onRemoveEntry({ dir, name, options }) { push({ kind: 'remove-entry', name, path: dir.childPath(name), staged: name.includes('.brt-stage-'), options: Object.freeze({ ...(options || {}) }) }); }
  };
  return { hooks, events };
}

function stagePath(prefix, hash, suffix = 'orphan') {
  return `${prefix}/${hash.slice(0, 2)}/${hash.slice(2, 4)}/${hash}.brt-stage-${suffix}.tmp`;
}

async function runSameBucketRecoveryCase() {
  const payload = payloadOf('same-bucket-recovery', 5632);
  const prefix = `browserrt/${REVISION}/fake-staged-recovery/same-bucket`;
  const trace = new TraceLog({ maxEvents: 8192 });
  const recorder = makeRecorder();
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-recovery-store`, prefix, trace });
    const committed = await store.put(payload, { label: 'same-bucket-recovery-committed' });
    const hash = committed.hash;
    const orphanPath = stagePath(prefix, hash, 'orphan');
    const secondOrphanPath = stagePath(prefix, hash, 'replay7');
    const wrongBucketPath = `${prefix}/ff/ee/${hash}.brt-stage-wrong.tmp`;
    const nonStagePath = `${prefix}/${hash.slice(0, 2)}/${hash.slice(2, 4)}/${hash}.note.tmp`;
    await writeFakePath(root, orphanPath, payloadOf('orphan-stage', 128));
    await writeFakePath(root, secondOrphanPath, payloadOf('second-orphan-stage', 160));
    await writeFakePath(root, wrongBucketPath, payloadOf('wrong-bucket-stage-bait', 192));
    await writeFakePath(root, nonStagePath, payloadOf('non-stage-bait', 96));
    const before = fakeTreeSummary(root);
    const recovery = await store.recoverStagedWrites({ reason: 'probe-same-bucket-recovery' });
    const after = fakeTreeSummary(root);
    const readBack = await store.get(committed.ref);
    const verify = await store.verify(committed.ref);
    return { committed, before, recovery, after, readBackDigest: `sha256:${await digestBytesHex(readBack)}`, verify, snapshot: store.snapshot(), events: recorder.events, traceKinds: trace.kinds(), orphanPath, secondOrphanPath, wrongBucketPath, nonStagePath };
  }, { hooks: recorder.hooks });
}

async function runMissingPrefixCase() {
  const prefix = `browserrt/${REVISION}/fake-staged-recovery/missing-prefix`;
  const trace = new TraceLog({ maxEvents: 4096 });
  const recorder = makeRecorder();
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-recovery-missing-prefix`, prefix, trace });
    const before = fakeTreeSummary(root);
    const recovery = await store.recoverStagedWrites({ reason: 'probe-missing-prefix' });
    const after = fakeTreeSummary(root);
    return { before, recovery, after, snapshot: store.snapshot(), events: recorder.events, traceKinds: trace.kinds() };
  }, { hooks: recorder.hooks });
}

async function runPreAbortedCase() {
  const payload = payloadOf('pre-aborted-recovery', 1024);
  const prefix = `browserrt/${REVISION}/fake-staged-recovery/pre-aborted`;
  const trace = new TraceLog({ maxEvents: 4096 });
  const controller = new AbortController();
  controller.abort(new Error('probe pre-aborted staged recovery'));
  return await withFakeNavigator(async (root) => {
    const hash = await digestBytesHex(payload);
    const orphanPath = stagePath(prefix, hash, 'preabort');
    await writeFakePath(root, orphanPath, payload);
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-recovery-preaborted`, prefix, trace });
    const before = fakeTreeSummary(root);
    const recovery = await capture('pre-aborted-recover-staged-writes', () => store.recoverStagedWrites({ signal: controller.signal, reason: 'probe-pre-aborted' }));
    const after = fakeTreeSummary(root);
    return { before, recovery, after, snapshot: store.snapshot(), traceKinds: trace.kinds(), orphanPath };
  });
}

export async function runProbe() {
  const started = performance.now();
  const sameBucket = await runSameBucketRecoveryCase();
  const missingPrefix = await runMissingPrefixCase();
  const preAborted = await runPreAbortedCase();

  assert.equal(sameBucket.recovery.deleted, 2, 'same-bucket recovery should delete only matching BrowserRT staged temp files');
  assert.equal(sameBucket.recovery.failures, 0, 'same-bucket recovery should not fail');
  assert.equal(sameBucket.recovery.candidates, 2, 'same-bucket recovery should count two staged candidates');
  assert.ok(sameBucket.recovery.deletedPaths.some((row) => row.path === sameBucket.orphanPath), 'first orphan staged temp should be deleted');
  assert.ok(sameBucket.recovery.deletedPaths.some((row) => row.path === sameBucket.secondOrphanPath), 'second orphan staged temp should be deleted');
  assert.ok(sameBucket.after.files.some((row) => row.path.endsWith('.blk')), 'canonical committed block must remain');
  assert.ok(sameBucket.after.files.some((row) => row.path.endsWith(sameBucket.wrongBucketPath)), 'wrong-bucket staged-name bait must not be deleted');
  assert.ok(sameBucket.after.files.some((row) => row.path.endsWith(sameBucket.nonStagePath)), 'non-stage bait must not be deleted');
  assert.equal(sameBucket.readBackDigest, sameBucket.committed.digest, 'committed block must still read after recovery sweep');
  assert.equal(sameBucket.verify.ok, true, 'committed block must verify after recovery sweep');
  assert.ok(sameBucket.snapshot.stats.stagedRecoverySweeps >= 1, 'staged recovery sweep stat missing');
  assert.ok(sameBucket.snapshot.stats.stagedRecoveryDeletes >= 2, 'staged recovery delete stat missing');
  assert.ok(sameBucket.snapshot.stats.stagedRecoverySkips >= 1, 'staged recovery skip stat missing for wrong-bucket staged bait');
  assert.ok(sameBucket.events.some((row) => row.kind === 'entries'), 'fake OPFS entries traversal was not exercised');
  assert.ok(sameBucket.events.filter((row) => row.kind === 'remove-entry' && row.staged).length >= 2, 'staged recovery delete events missing');
  assert.ok(sameBucket.traceKinds.includes('storage:opfs-block-staged-recovery-delete'), 'staged recovery delete trace missing');
  assert.ok(sameBucket.traceKinds.includes('storage:opfs-block-staged-recovery'), 'staged recovery summary trace missing');

  assert.equal(missingPrefix.recovery.prefixMissing, true, 'missing prefix recovery should return a prefixMissing report instead of creating directories');
  assert.equal(missingPrefix.recovery.deleted, 0, 'missing prefix recovery should delete nothing');
  assert.equal(missingPrefix.before.fileCount, 0, 'missing-prefix case should start empty');
  assert.equal(missingPrefix.after.fileCount, 0, 'missing prefix recovery should not create files');
  assert.equal(missingPrefix.after.dirCount, 0, 'missing prefix recovery should not create directories');

  assert.equal(preAborted.recovery.ok, false, 'pre-aborted recovery should reject before mutation');
  assert.equal(preAborted.recovery.error.code, 'BRT_OPFS_OPERATION_ABORTED', 'pre-aborted recovery should surface operation-aborted code');
  assert.equal(preAborted.before.fileCount, preAborted.after.fileCount, 'pre-aborted recovery must not delete staged files');
  assert.ok(preAborted.after.files.some((row) => row.path.endsWith(preAborted.orphanPath)), 'pre-aborted recovery must leave orphan file untouched');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-staged-recovery-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that abandoned BrowserRT staged temp files can be explicitly swept after interrupted staged writes without deleting canonical .blk blocks or staged-looking files outside their digest bucket.',
    observations: { sameBucket, missingPrefix, preAborted },
    claimsChecked: [
      'recoverStagedWrites enumerates existing OPFS prefix directories without creating a missing prefix',
      'only BrowserRT staged temp filenames in the expected content-addressed bucket are deleted',
      'canonical .blk content-addressed blocks remain readable and verifiable after staged recovery',
      'staged-looking names outside the matching digest bucket are skipped rather than deleted',
      'pre-aborted recovery rejects before deletion and leaves orphan temp files untouched'
    ],
    nonClaims: [
      'Fake-OPFS release-tier proof only; no browser matrix, fsync, power-loss, renderer-crash, quota/eviction, or cross-browser durability claim.',
      'Recovery sweep deletes abandoned temp files; it does not prove atomic rename, journal replay, or full database-style crash recovery.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-staged-recovery-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: captureError(error) };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_staged_recovery_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
