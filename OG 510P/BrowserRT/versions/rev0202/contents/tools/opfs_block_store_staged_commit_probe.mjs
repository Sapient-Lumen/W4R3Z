#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator, writeFakePath } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'opfs:block-store-staged-commit-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-STAGED-COMMIT-PROBE.json`;
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
  const header = new TextEncoder().encode(`BrowserRT ${REVISION} staged commit proof ${label}`);
  bytes.set(header);
  for (let i = header.length; i < bytes.length; i += 1) bytes[i] = (label.length * 43 + i * 19 + (i >>> 2)) & 255;
  return bytes;
}

function makeRecorder({ abortStageClose = null } = {}) {
  const events = [];
  const push = (event) => events.push(Object.freeze({ seq: events.length + 1, ...event }));
  const hooks = {
    async onCreateFile({ dir, file, name, options }) { push({ kind: 'create-file', name, path: file.path, parentPath: dir.path, options: Object.freeze({ ...(options || {}) }) }); },
    async onWrite({ file, bytes }) { push({ kind: 'write', name: file.name, path: file.path, bytes: bytes.byteLength, staged: file.name.includes('.brt-stage-') }); },
    async onClose({ file, bytes }) {
      push({ kind: 'close', name: file.name, path: file.path, bytes: bytes.byteLength, staged: file.name.includes('.brt-stage-') });
      if (abortStageClose && file.name.includes('.brt-stage-')) abortStageClose.abort(new Error('probe abort after staged file closed before final publish'));
    },
    async onAbort({ file }) { push({ kind: 'stream-abort', name: file.name, path: file.path, staged: file.name.includes('.brt-stage-') }); },
    async onRemoveEntry({ dir, name }) { push({ kind: 'remove-entry', name, path: dir.childPath(name), staged: name.includes('.brt-stage-') }); }
  };
  return { hooks, events };
}

function eventIndex(events, predicate) {
  return events.findIndex(predicate);
}

async function runSuccessfulStagedPublishCase() {
  const payload = payloadOf('successful-staged-publish', 6144);
  const prefix = `browserrt/${REVISION}/fake-staged-commit/success`;
  const trace = new TraceLog({ maxEvents: 8192 });
  const recorder = makeRecorder();
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-commit-success-store`, prefix, trace });
    const result = await store.put(payload, { label: 'successful-staged-publish' });
    const readBack = await store.get(result.ref);
    const verify = await store.verify(result.ref);
    const snapshot = store.snapshot();
    const tree = fakeTreeSummary(root);
    return { result, readBackDigest: `sha256:${await digestBytesHex(readBack)}`, verify, snapshot, tree, events: recorder.events, traceKinds: trace.kinds() };
  }, { hooks: recorder.hooks });
}

async function runAbortAfterStageCase() {
  const payload = payloadOf('abort-after-stage-before-final', 5120);
  const prefix = `browserrt/${REVISION}/fake-staged-commit/abort-after-stage`;
  const trace = new TraceLog({ maxEvents: 8192 });
  const controller = new AbortController();
  const recorder = makeRecorder({ abortStageClose: controller });
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-commit-abort-store`, prefix, trace });
    const hash = await digestBytesHex(payload);
    const put = await capture('abort-after-stage-before-final-publish', () => store.put(payload, { label: 'abort-after-stage-before-final' }, { signal: controller.signal }));
    const verifier = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-commit-abort-verifier`, prefix });
    const verify = await verifier.verify(`sha256:${hash}`);
    return { put, verify, snapshot: store.snapshot(), verifierSnapshot: verifier.snapshot(), tree: fakeTreeSummary(root), events: recorder.events, traceKinds: trace.kinds(), hash };
  }, { hooks: recorder.hooks });
}

async function runCorruptRepairStagesBeforePublishCase() {
  const payload = payloadOf('corrupt-repair-staged-publish', 7168);
  const corrupt = new TextEncoder().encode('BrowserRT corrupt pre-existing canonical block bytes');
  const prefix = `browserrt/${REVISION}/fake-staged-commit/corrupt-repair`;
  const trace = new TraceLog({ maxEvents: 8192 });
  const recorder = makeRecorder();
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-commit-corrupt-repair-store`, prefix, trace });
    const hash = await digestBytesHex(payload);
    const finalPath = store.blockPath(hash);
    await writeFakePath(root, finalPath, corrupt);
    const before = await store.verify(`sha256:${hash}`);
    const result = await store.put(payload, { label: 'corrupt-repair-staged-publish' });
    const after = await store.verify(result.ref);
    const readBack = await store.get(result.ref);
    return { before, result, after, readBackDigest: `sha256:${await digestBytesHex(readBack)}`, snapshot: store.snapshot(), tree: fakeTreeSummary(root), events: recorder.events, traceKinds: trace.kinds(), finalPath };
  }, { hooks: recorder.hooks });
}

export async function runProbe() {
  const started = performance.now();
  const success = await runSuccessfulStagedPublishCase();
  const abortAfterStage = await runAbortAfterStageCase();
  const corruptRepair = await runCorruptRepairStagesBeforePublishCase();

  assert.equal(success.result.staging?.staged, true, 'new put should use staged write receipt');
  assert.equal(success.result.staging?.verified, true, 'staged bytes must be verified before publish');
  assert.equal(success.result.staging?.published, true, 'staged write must publish final canonical block on success');
  assert.equal(success.result.staging?.cleanup?.deleted, true, 'successful put must delete the staged temp file');
  assert.equal(success.tree.fileCount, 1, 'successful staged put should leave exactly one file');
  assert.ok(success.tree.files[0].path.endsWith('.blk'), 'only canonical .blk file should remain after success');
  assert.equal(success.verify.ok, true, 'successful staged put must verify');
  assert.equal(success.readBackDigest, success.result.digest, 'read back digest should match the committed digest');
  assert.ok(success.snapshot.stats.stagedPuts >= 1, 'staged put count missing');
  assert.ok(success.snapshot.stats.stagedWriteVerifications >= 1, 'staged verification count missing');
  assert.ok(success.snapshot.stats.stagedPublishWrites >= 1, 'staged publish count missing');
  assert.ok(success.snapshot.stats.stagedTempDeletes >= 1, 'staged temp delete count missing');
  const successStageCreate = eventIndex(success.events, (row) => row.kind === 'create-file' && row.name.includes('.brt-stage-'));
  const successFinalCreate = eventIndex(success.events, (row) => row.kind === 'create-file' && row.name.endsWith('.blk'));
  const successStageRemove = eventIndex(success.events, (row) => row.kind === 'remove-entry' && row.name.includes('.brt-stage-'));
  assert.ok(successStageCreate >= 0 && successFinalCreate >= 0 && successStageCreate < successFinalCreate, 'staged temp file must be created before final canonical file');
  assert.ok(successStageRemove > successFinalCreate, 'staged temp file must be removed after final publish');
  assert.ok(success.traceKinds.includes('storage:opfs-block-staged-write-start'), 'stage-start trace missing');
  assert.ok(success.traceKinds.includes('storage:opfs-block-staged-publish'), 'stage-publish trace missing');
  assert.ok(success.traceKinds.includes('storage:opfs-block-staged-cleanup'), 'stage-cleanup trace missing');

  assert.equal(abortAfterStage.put.ok, false, 'abort after staged close should reject before final publish');
  assert.equal(abortAfterStage.put.error.code, 'BRT_OPFS_OPERATION_ABORTED');
  assert.equal(abortAfterStage.put.error.detail.context?.staging?.verified, false, 'abort at staged-close checkpoint should not report verified staged commit');
  assert.equal(abortAfterStage.put.error.detail.context?.staging?.published, false, 'abort after stage must not publish final canonical file');
  assert.equal(abortAfterStage.put.error.detail.context?.staging?.cleanup?.deleted, true, 'abort after stage must delete staged temp file');
  assert.equal(abortAfterStage.put.error.detail.rollback?.attempted, false, 'abort before final publish should not need final-path rollback');
  assert.equal(abortAfterStage.verify.present, false, 'fresh provider must not find final digest after staged abort');
  assert.equal(abortAfterStage.tree.fileCount, 0, 'abort after stage should leave no files');
  assert.ok(abortAfterStage.events.some((row) => row.kind === 'remove-entry' && row.staged), 'staged temp cleanup event missing after abort');

  assert.equal(corruptRepair.before.present, true, 'corrupt repair case must start with a present block');
  assert.equal(corruptRepair.before.ok, false, 'corrupt repair case must start with checksum mismatch');
  assert.equal(corruptRepair.result.repairedCorrupt, true, 'put should repair corrupt canonical block');
  assert.equal(corruptRepair.result.staging?.verified, true, 'corrupt repair must also verify staged bytes');
  assert.equal(corruptRepair.result.staging?.published, true, 'corrupt repair must publish through staged path');
  assert.equal(corruptRepair.result.staging?.cleanup?.deleted, true, 'corrupt repair must remove staged temp file');
  assert.equal(corruptRepair.after.ok, true, 'post-repair canonical block must verify');
  assert.equal(corruptRepair.readBackDigest, corruptRepair.result.digest, 'post-repair read must match digest');
  assert.equal(corruptRepair.tree.fileCount, 1, 'corrupt repair should leave one canonical final file');
  assert.ok(corruptRepair.events.some((row) => row.kind === 'remove-entry' && row.name.endsWith('.blk')), 'corrupt canonical final block should be removed before repair');
  assert.ok(corruptRepair.events.some((row) => row.kind === 'remove-entry' && row.staged), 'staged temp should be removed after repair publish');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-staged-commit-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that new OPFS block puts stage bytes under a temporary same-bucket file, verify the staged digest, publish the final content-addressed block only after staging succeeds, and clean temp files on success, abort, and corrupt repair.',
    observations: { success, abortAfterStage, corruptRepair },
    claimsChecked: [
      'new puts create and verify a staged temp file before the final content-addressed .blk file is published',
      'successful puts delete the staged temp file and leave exactly one canonical block file',
      'caller abort after the staged file closes but before final publish deletes the temp file and leaves no final digest',
      'abort before final publish does not need ownership rollback of the canonical final path',
      'corrupt final-block repair also routes through staged verification before republishing the canonical path'
    ],
    nonClaims: [
      'Fake-OPFS release-tier proof only; no browser matrix, fsync, power-loss, renderer-crash, quota/eviction, or cross-browser durability claim.',
      'This is staged publish hardening, not an atomic rename or guaranteed crash-safe transaction across all browser implementations.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-staged-commit-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: captureError(error) };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_staged_commit_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
