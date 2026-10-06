#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, createOpfsAsyncBlockStore } from '../src/browserrt.mjs';
import { createFailOnceDirectoryOpenHarness, fakeTreeSummary, withFakeNavigator } from './lib/fake_opfs_harness.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-OPFS-BLOCK-STORE-OPEN-FAILURE-RECOVERY-PROBE.json`;
const RELEASE_TASK = 'opfs:block-store-open-failure-recovery-proof';
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function summarizeError(error) {
  return Object.freeze({
    name: error?.name || 'Error',
    message: error?.message || String(error),
    code: error?.code || null,
    detail: error?.detail || null
  });
}

async function capture(label, fn) {
  try { return Object.freeze({ label, ok: true, value: await fn() }); }
  catch (error) { return Object.freeze({ label, ok: false, error: summarizeError(error) }); }
}

function createTraceRecorder() {
  const events = [];
  return Object.freeze({
    trace: { emit(kind, payload = {}) { events.push(Object.freeze({ kind, ...payload })); } },
    events
  });
}

async function runDirectOpenRetryCase() {
  const failingOpen = createFailOnceDirectoryOpenHarness({ matchName: 'browserrt', message: 'simulated first OPFS root open failure for direct open retry proof' });
  return await withFakeNavigator(async () => {
    const recorder = createTraceRecorder();
    const store = createOpfsAsyncBlockStore({ name: 'fake-opfs-open-retry-direct', prefix: 'browserrt/rev0098/open-failure/direct', trace: recorder.trace });
    const firstOpen = await capture('first-open-fails-and-resets-root-promise', () => store.open());
    const afterFirstSnapshot = store.snapshot();
    const secondOpen = await capture('second-open-retries-and-succeeds', () => store.open());
    const afterSecondSnapshot = store.snapshot();
    const thirdOpen = await capture('third-open-reuses-successful-root-promise', () => store.open());
    const afterThirdSnapshot = store.snapshot();
    return Object.freeze({
      firstOpen,
      afterFirstSnapshot,
      secondOpen: Object.freeze({ label: secondOpen.label, ok: secondOpen.ok }),
      afterSecondSnapshot,
      thirdOpen: Object.freeze({ label: thirdOpen.label, ok: thirdOpen.ok }),
      afterThirdSnapshot,
      failingOpen: failingOpen.snapshot(),
      traceKinds: recorder.events.map((row) => row.kind),
      openErrorEvents: recorder.events.filter((row) => row.kind === 'storage:opfs-blockstore-open-error').map((row) => ({ rootPromiseReset: row.rootPromiseReset, code: row.error?.code || null, name: row.error?.name || null, message: row.error?.message || null })),
      openEvents: recorder.events.filter((row) => row.kind === 'storage:opfs-blockstore-open').map((row) => ({ store: row.store, prefix: row.prefix }))
    });
  }, { hooks: failingOpen.hooks, estimate: false });
}

async function runPutRetryCase() {
  const failingOpen = createFailOnceDirectoryOpenHarness({ matchName: 'browserrt', message: 'simulated first OPFS root open failure for put retry proof' });
  return await withFakeNavigator(async (root) => {
    const recorder = createTraceRecorder();
    const store = createOpfsAsyncBlockStore({ name: 'fake-opfs-open-retry-put', prefix: 'browserrt/rev0098/open-failure/put', trace: recorder.trace });
    const payload = new TextEncoder().encode('BrowserRT rev0098 OPFS open failure recovery payload');
    const firstPut = await capture('first-put-open-failure-rejects-without-poisoning-store', () => store.put(payload, { label: 'first-put-open-failure' }));
    const afterFirstSnapshot = store.snapshot();
    const secondPut = await capture('second-put-retries-open-and-succeeds', () => store.put(payload, { label: 'second-put-after-open-failure' }));
    const verify = secondPut.ok ? await store.verify(secondPut.value.ref) : null;
    const afterSecondSnapshot = store.snapshot();
    const tree = fakeTreeSummary(root);
    return Object.freeze({
      firstPut,
      afterFirstSnapshot,
      secondPut: secondPut.ok ? Object.freeze({ label: secondPut.label, ok: true, digest: secondPut.value.digest, bytes: secondPut.value.bytes, duplicate: secondPut.value.duplicate }) : secondPut,
      verify,
      afterSecondSnapshot,
      tree,
      failingOpen: failingOpen.snapshot(),
      traceKinds: recorder.events.map((row) => row.kind),
      openErrorEvents: recorder.events.filter((row) => row.kind === 'storage:opfs-blockstore-open-error').map((row) => ({ rootPromiseReset: row.rootPromiseReset, code: row.error?.code || null, name: row.error?.name || null })),
      putErrorEvents: recorder.events.filter((row) => row.kind === 'storage:opfs-block-put-error').map((row) => ({ code: row.error?.code || null, rollback: row.error?.rollback || null }))
    });
  }, { hooks: failingOpen.hooks, estimate: false });
}

export async function runProbe() {
  const started = performance.now();
  const directOpenRetry = await runDirectOpenRetryCase();
  const putRetry = await runPutRetryCase();

  assert.equal(directOpenRetry.firstOpen.ok, false, 'first direct open must fail');
  assert.equal(directOpenRetry.firstOpen.error.name, 'InvalidStateError');
  assert.equal(directOpenRetry.afterFirstSnapshot.opened, false, 'failed open must not mark provider opened');
  assert.equal(directOpenRetry.afterFirstSnapshot.stats.openFailures, 1, 'failed open must increment openFailures');
  assert.equal(directOpenRetry.afterFirstSnapshot.stats.openRetryResets, 1, 'failed open must reset cached root promise');
  assert.equal(directOpenRetry.secondOpen.ok, true, 'same store open must retry and succeed after first failure');
  assert.equal(directOpenRetry.afterSecondSnapshot.stats.opens, 1, 'successful retry must increment opens once');
  assert.equal(directOpenRetry.thirdOpen.ok, true, 'subsequent open must still resolve');
  assert.equal(directOpenRetry.afterThirdSnapshot.stats.opens, 1, 'successful cached open must not reopen root');
  assert.equal(directOpenRetry.openErrorEvents[0]?.rootPromiseReset, true, 'open error trace must expose root promise reset');
  assert.ok(directOpenRetry.traceKinds.includes('storage:opfs-blockstore-open-error'), 'direct open retry case must trace open error');
  assert.ok(directOpenRetry.traceKinds.includes('storage:opfs-blockstore-open'), 'direct open retry case must trace successful retry');

  assert.equal(putRetry.firstPut.ok, false, 'first put must fail because opening the prefix failed');
  assert.equal(putRetry.firstPut.error.code, 'BRT_OPFS_INVALID_STATE', 'put failure should remain classified as an OPFS invalid state');
  assert.equal(putRetry.afterFirstSnapshot.stats.openFailures, 1, 'put open failure must increment openFailures');
  assert.equal(putRetry.afterFirstSnapshot.stats.openRetryResets, 0, 'rev0099 put duplicate preflight open failure must not cache a root promise to reset');
  assert.equal(putRetry.afterFirstSnapshot.stats.putFailures, 1, 'failed put must be counted');
  assert.equal(putRetry.afterFirstSnapshot.stats.puts, 0, 'failed open put must not acknowledge a put');
  assert.equal(putRetry.secondPut.ok, true, 'second put must retry root open and succeed');
  assert.equal(putRetry.verify.ok, true, 'block written after retry must verify');
  assert.equal(putRetry.afterSecondSnapshot.stats.opens, 1, 'successful put retry must open once');
  assert.equal(putRetry.afterSecondSnapshot.stats.puts, 1, 'successful put retry must acknowledge one put');
  assert.equal(putRetry.tree.fileCount, 1, 'retry success should leave exactly one content block');
  assert.equal(putRetry.openErrorEvents[0]?.rootPromiseReset, false, 'rev0099 read-only duplicate preflight open error must report no cached root promise reset');
  assert.ok(putRetry.traceKinds.includes('storage:opfs-blockstore-open-error'), 'put retry must trace open error');
  assert.ok(putRetry.traceKinds.includes('storage:opfs-blockstore-open'), 'put retry must trace successful open');

  return Object.freeze({
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-open-failure-recovery-proof`, task_id: RELEASE_TASK, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Release-tier fake-OPFS proof that OpfsAsyncBlockStore resets its cached root open promise after transient getDirectory/getDirectoryHandle failures, allowing the same provider instance to retry direct open() and put() without permanent open-promise poisoning.',
    observations: { directOpenRetry, putRetry },
    claimsChecked: [
      'a failed direct open emits storage:opfs-blockstore-open-error and resets the cached root promise',
      'the same store instance can successfully retry open after the first root/prefix open failure',
      'a put rejected by an open failure does not acknowledge data and does not permanently poison subsequent puts',
      'retry success writes and verifies a content-addressed block after the initial open failure'
    ],
    nonClaims: [
      'Fake-OPFS release proof only; the browser companion proof supplies real Chromium OPFS evidence for monkey-patched getDirectory failures.',
      'Open failure recovery is not cross-browser conformance, fsync durability, crash/power-loss safety, quota/eviction survival, multi-tab atomicity, or production-readiness evidence.'
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
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-open-failure-recovery-proof`, task_id: RELEASE_TASK, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_open_failure_recovery_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
