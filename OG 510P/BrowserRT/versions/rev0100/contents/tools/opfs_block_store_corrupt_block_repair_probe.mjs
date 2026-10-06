#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, createOpfsAsyncBlockStore, digestBytesHex } from '../src/browserrt.mjs';
import { withFakeNavigator, writeFakePath } from './lib/fake_opfs_harness.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-OPFS-BLOCK-STORE-CORRUPT-BLOCK-REPAIR-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const started = performance.now();
  const trace = new TraceLog();
  const result = await withFakeNavigator(async (root) => {
    const store = createOpfsAsyncBlockStore({ name: `${REVISION}-fake-opfs-corrupt-repair-store`, prefix: `browserrt/${REVISION}/fake-opfs-corrupt-repair`, trace });
    const payload = new Uint8Array(4096);
    for (let i = 0; i < payload.length; i += 1) payload[i] = (17 + i * 29 + (i >>> 3)) & 255;
    payload.set(new TextEncoder().encode(`BrowserRT ${REVISION} fake OPFS corrupt block repair proof`));
    const hash = await digestBytesHex(payload);
    const digest = `sha256:${hash}`;
    const path = store.blockPath(hash);
    const corruptBytes = new Uint8Array(payload.slice(0, 1024));
    corruptBytes[0] ^= 0xff;
    corruptBytes[13] ^= 0x55;
    const corruptDigest = `sha256:${await digestBytesHex(corruptBytes)}`;
    await writeFakePath(root, path, corruptBytes);
    const ref = Object.freeze({ kind: 'block', id: `block:sha256:${hash}`, digest, hash, algorithm: 'sha256', backend: 'opfs-async-block-store-v0', bytes: payload.byteLength, path });
    const hasBefore = await store.has(ref);
    const verifyBefore = await store.verify(ref);
    let getBeforeError = null;
    try { await store.get(ref); } catch (error) { getBeforeError = { name: error.name, code: error.code || null, message: error.message, detail: error.detail || null }; }
    const repaired = await store.put(payload, { label: 'fake-corrupt-repair' });
    const hasAfter = await store.has(repaired.ref);
    const verifyAfter = await store.verify(repaired.ref);
    const bytesAfter = await store.get(repaired.ref);
    const digestAfter = `sha256:${await digestBytesHex(bytesAfter)}`;
    const duplicate = await store.put(payload, { label: 'fake-verified-duplicate' });
    const snapshot = store.snapshot();
    return { digest, corruptDigest, path, hasBefore, verifyBefore, getBeforeError, repaired, hasAfter, verifyAfter, digestAfter, duplicate, snapshot };
  });
  const traceKinds = trace.kinds();

  assert.equal(result.hasBefore, false, 'corrupt final path must not satisfy has()');
  assert.equal(result.verifyBefore.present, true);
  assert.equal(result.verifyBefore.ok, false);
  assert.equal(result.verifyBefore.actualDigest, result.corruptDigest);
  assert.equal(result.getBeforeError?.code, 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH');
  assert.equal(result.repaired.duplicate, false);
  assert.equal(result.repaired.repairedCorrupt, true);
  assert.equal(result.repaired.repair?.existing?.actualDigest, result.corruptDigest);
  assert.equal(result.hasAfter, true);
  assert.equal(result.verifyAfter.ok, true);
  assert.equal(result.digestAfter, result.digest);
  assert.equal(result.duplicate.duplicate, true);
  assert.equal(result.duplicate.repairedCorrupt, false);
  assert.equal(result.snapshot.stats.corruptRepairs, 1);
  assert.equal(result.snapshot.stats.corruptDeletes, 1);
  assert.ok(result.snapshot.stats.postWriteVerifications >= 1);
  for (const kind of ['storage:opfs-block-corrupt', 'storage:opfs-block-repair', 'storage:opfs-block-write-close', 'storage:opfs-block-integrity-ok', 'storage:opfs-block-put']) {
    assert.ok(traceKinds.includes(kind), `missing trace kind ${kind}`);
  }

  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    probe_id: `${REVISION}-opfs-block-store-corrupt-block-repair-proof`, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started),
    purpose: 'Browser-light fake-OPFS regression proof for OpfsAsyncBlockStore corrupt final-hash repair: has/get/verify fail closed, put repairs, and a later duplicate is accepted only after valid-content verification.',
    observations: result,
    traceKinds,
    nonClaims: [
      'Fake-OPFS release-tier proof only; the managed Chromium proof remains the browser evidence.',
      'This does not prove OPFS fsync durability, crash/power-loss safety, quota/eviction behavior, Web Locks behavior, or cross-browser conformance.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runProbe();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, probe_id: `${REVISION}-opfs-block-store-corrupt-block-repair-proof`, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); }
  console.error(`[opfs_block_store_corrupt_block_repair_probe] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
