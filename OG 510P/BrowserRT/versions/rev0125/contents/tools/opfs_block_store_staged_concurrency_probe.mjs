#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'opfs:block-store-staged-concurrency-proof';
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-STAGED-CONCURRENCY-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function captureError(error) {
  return { name: error?.name || 'Error', message: error?.message || String(error), code: error?.code ?? null, detail: error?.detail ?? null };
}

function deferred(label = 'deferred') {
  let settled = false;
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return {
    label,
    promise,
    resolve(value) { if (!settled) { settled = true; resolve(value); } },
    reject(error) { if (!settled) { settled = true; reject(error); } },
    get settled() { return settled; }
  };
}

function payloadOf(label, size = 4096) {
  const bytes = new Uint8Array(size);
  const header = new TextEncoder().encode(`BrowserRT ${REVISION} staged concurrency proof ${label}`);
  bytes.set(header);
  for (let i = header.length; i < bytes.length; i += 1) bytes[i] = (label.charCodeAt(i % label.length) + i * 19 + (i >>> 2)) & 255;
  return bytes;
}

function makeStagedCloseGate({ releaseAfter = 1 } = {}) {
  const stagedCloses = [];
  const closed = deferred('staged-close-count');
  const release = deferred('release-staged-close');
  const hooks = {
    async onClose({ file, bytes }) {
      if (!String(file?.name || '').includes('.brt-stage-')) return;
      stagedCloses.push(Object.freeze({ name: file.name, path: file.path, bytes: bytes.byteLength }));
      if (stagedCloses.length >= releaseAfter) closed.resolve(Object.freeze([...stagedCloses]));
      await release.promise;
    }
  };
  return { hooks, stagedCloses, closed: closed.promise, release: release.resolve };
}

async function waitFor(predicate, { timeoutMs = 1000, intervalMs = 5, label = 'condition' } = {}) {
  const deadline = performance.now() + timeoutMs;
  while (performance.now() <= deadline) {
    if (predicate()) return true;
    await sleep(intervalMs);
  }
  throw new Error(`timed out waiting for ${label}`);
}

async function runActiveRecoverySkipCase() {
  const payload = payloadOf('active-recovery-skip', 5376);
  const prefix = `browserrt/${REVISION}/fake-staged-concurrency/active-skip`;
  const trace = new TraceLog({ maxEvents: 8192 });
  const gate = makeStagedCloseGate({ releaseAfter: 1 });
  return await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-concurrency-active`, prefix, trace });
    const putPromise = store.put(payload, { label: 'active-recovery-skip' });
    await gate.closed;
    await waitFor(() => store.snapshot().activeStagedWrites === 1, { label: 'active staged write registry' });
    const duringStageTree = fakeTreeSummary(root);
    const recoveryWhileActive = await store.recoverStagedWrites({ reason: 'probe-active-skip' });
    const afterRecoveryTree = fakeTreeSummary(root);
    assert.equal(store.snapshot().activeStagedWrites, 1, 'active staged write should stay registered until put resumes');
    gate.release();
    const committed = await putPromise;
    const afterCommitTree = fakeTreeSummary(root);
    const readBack = await store.get(committed.ref);
    return {
      committed,
      stagedClosed: Object.freeze([...gate.stagedCloses]),
      duringStageTree,
      recoveryWhileActive,
      afterRecoveryTree,
      afterCommitTree,
      readBackDigest: `sha256:${await digestBytesHex(readBack)}`,
      snapshot: store.snapshot(),
      traceKinds: trace.kinds()
    };
  }, { hooks: gate.hooks });
}

async function runTwoProviderSameDigestCase() {
  const payload = payloadOf('two-provider-same-digest', 6144);
  const prefix = `browserrt/${REVISION}/fake-staged-concurrency/two-providers`;
  const traceA = new TraceLog({ maxEvents: 8192 });
  const traceB = new TraceLog({ maxEvents: 8192 });
  const gate = makeStagedCloseGate({ releaseAfter: 2 });
  return await withFakeNavigator(async (root) => {
    const storeA = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-concurrency-a`, prefix, trace: traceA });
    const storeB = createOpfsAsyncBlockStore({ name: `${REVISION}-staged-concurrency-b`, prefix, trace: traceB });
    const putA = storeA.put(payload, { label: 'two-provider-a' });
    const putB = storeB.put(payload, { label: 'two-provider-b' });
    await gate.closed;
    const duringStageTree = fakeTreeSummary(root);
    const stageNames = gate.stagedCloses.map((row) => row.name);
    gate.release();
    const [committedA, committedB] = await Promise.all([putA, putB]);
    const afterTree = fakeTreeSummary(root);
    const readBack = await storeA.get(committedA.ref);
    return {
      committedA,
      committedB,
      stageNames,
      duringStageTree,
      afterTree,
      readBackDigest: `sha256:${await digestBytesHex(readBack)}`,
      snapshotA: storeA.snapshot(),
      snapshotB: storeB.snapshot(),
      traceKindsA: traceA.kinds(),
      traceKindsB: traceB.kinds()
    };
  }, { hooks: gate.hooks });
}

export async function runProbe() {
  const started = performance.now();
  const activeRecoverySkip = await runActiveRecoverySkipCase();
  const twoProviderSameDigest = await runTwoProviderSameDigestCase();

  assert.equal(activeRecoverySkip.recoveryWhileActive.deleted, 0, 'recovery must not delete the active staged temp file');
  assert.equal(activeRecoverySkip.recoveryWhileActive.activeSkipped, 1, 'recovery should report one active staged skip');
  assert.ok(activeRecoverySkip.recoveryWhileActive.skippedPaths.some((row) => row.reason === 'active-staged-write'), 'active skip reason missing');
  assert.equal(activeRecoverySkip.afterRecoveryTree.fileCount, activeRecoverySkip.duringStageTree.fileCount, 'active recovery must leave staged file visible for the live put');
  assert.equal(activeRecoverySkip.readBackDigest, activeRecoverySkip.committed.digest, 'committed block must read back after active recovery skip');
  assert.equal(activeRecoverySkip.snapshot.activeStagedWrites, 0, 'active staged registry must clear after put settles');
  assert.ok(activeRecoverySkip.snapshot.stats.stagedRecoveryActiveSkips >= 1, 'active recovery skip stat missing');
  assert.ok(activeRecoverySkip.traceKinds.includes('storage:opfs-block-staged-active-start'), 'active staged start trace missing');
  assert.ok(activeRecoverySkip.traceKinds.includes('storage:opfs-block-staged-active-settle'), 'active staged settle trace missing');

  assert.equal(twoProviderSameDigest.stageNames.length, 2, 'two providers should create two staged temp files before publish');
  assert.notEqual(twoProviderSameDigest.stageNames[0], twoProviderSameDigest.stageNames[1], 'provider-instance staged temp filenames must be unique for same digest');
  assert.equal(twoProviderSameDigest.committedA.digest, twoProviderSameDigest.committedB.digest, 'same payload should commit to the same canonical digest');
  assert.equal(twoProviderSameDigest.readBackDigest, twoProviderSameDigest.committedA.digest, 'canonical block should survive concurrent same-digest publishes');
  assert.ok(twoProviderSameDigest.afterTree.files.filter((row) => row.path.endsWith('.blk')).length === 1, 'same-digest concurrent puts should leave one canonical block file');
  assert.equal(twoProviderSameDigest.snapshotA.activeStagedWrites, 0, 'provider A active stage registry leaked');
  assert.equal(twoProviderSameDigest.snapshotB.activeStagedWrites, 0, 'provider B active stage registry leaked');
  assert.notEqual(twoProviderSameDigest.snapshotA.stageSessionId, twoProviderSameDigest.snapshotB.stageSessionId, 'store stage session ids must differ');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-staged-concurrency-proof`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that same-runtime staged recovery does not delete a live put staging file and provider-instance staged temp names avoid same-digest collisions.',
    observations: { activeRecoverySkip, twoProviderSameDigest },
    claimsChecked: [
      'recoverStagedWrites skips same-runtime active staged files instead of deleting a live put temp file',
      'active staged write registration clears after success and does not leak across operations',
      'different provider instances choose different staged temp filenames for the same digest',
      'concurrent same-digest staged puts leave one canonical .blk and no staged temp leak'
    ],
    nonClaims: [
      'Fake-OPFS release-tier proof only; no browser matrix, cross-tab lock protocol, power-loss, fsync, quota/eviction, or atomic rename claim.',
      'The active staged registry is in-process protection only; other tabs/processes still require external coordination such as Web Locks.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-staged-concurrency-proof`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: captureError(error) };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_staged_concurrency_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
