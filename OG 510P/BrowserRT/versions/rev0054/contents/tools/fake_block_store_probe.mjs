#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, boot, createMemoryBlockStore } from '../src/browserrt.mjs';

const MANIFEST_ID = 'storage:fake-block-store-proof';
const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-FAKE-BLOCK-STORE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};

function bytesEqual(a, b) {
  if (a.byteLength !== b.byteLength) return false;
  for (let i = 0; i < a.byteLength; i += 1) if (a[i] !== b[i]) return false;
  return true;
}

function deterministicPayload(i) {
  const out = new Uint8Array(12 + (i % 13));
  for (let j = 0; j < out.length; j += 1) out[j] = (i * 37 + j * 17 + out.length) & 0xff;
  return out;
}

async function main() {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const started = performance.now();
  const rt = await boot({ telemetry: 'always', blockStoreProbe: true });
  const store = rt.blockStore({ name: 'rev0025-fake-block-store', provider: 'memory-fake-provider-v0', quotaBytes: 1024 * 1024 });
  const directStore = createMemoryBlockStore({ name: 'rev0025-direct-fake-block-store', trace: rt.trace, provider: 'memory-fake-provider-v0' });

  const firstBytes = new TextEncoder().encode('BrowserRT rev0025 fake block-store proof: stable content addressing.');
  const firstPut = await store.put(firstBytes, { label: 'first' });
  const duplicatePut = await store.put(new Uint8Array(firstBytes), { label: 'duplicate' });
  const model = new Map([[firstPut.digest, Array.from(firstBytes)]]);
  const secondBytes = new Uint8Array([1, 1, 2, 3, 5, 8, 13, 21]);
  const secondPut = await store.put(secondBytes, { label: 'fibonacci' });
  model.set(secondPut.digest, Array.from(secondBytes));

  const modelStore = rt.blockStore({ name: 'rev0025-model-fake-block-store', provider: 'memory-fake-provider-v0' });
  const seedPut = await modelStore.put(firstBytes, { label: 'model-seed' });
  const modelRefs = [seedPut.ref];
  const modelBytes = new Map([[seedPut.digest, Array.from(firstBytes)]]);
  let modelCommandWalkMatched = true;
  let modelCommandCount = 0;
  for (let i = 0; i < 32; i += 1) {
    if (i % 4 === 0) {
      const payload = deterministicPayload(i);
      const put = await modelStore.put(payload, { label: `model-${i}` });
      modelBytes.set(put.digest, Array.from(payload));
      modelRefs.push(put.ref);
      modelCommandCount += 1;
    } else {
      const ref = modelRefs[(i * 7) % modelRefs.length];
      const got = await modelStore.get(ref);
      const expected = modelBytes.get(ref.digest);
      modelCommandWalkMatched = modelCommandWalkMatched && Boolean(expected) && Array.from(got).join(',') === expected.join(',');
      modelCommandCount += 1;
    }
  }

  const roundTrip = await store.get(firstPut.ref);
  const verifyFirst = await store.verify(firstPut.ref);
  const verifySecond = await store.verify(secondPut.digest);
  const directPut = await directStore.put('direct-store-cross-check', { label: 'direct' });
  const directVerify = await directStore.verify(directPut.ref);

  assert.equal(firstPut.digest, duplicatePut.digest, 'same bytes must produce same digest');
  assert.equal(duplicatePut.duplicate, true, 'duplicate put must be recognized');
  assert.equal(await store.has(firstPut.ref), true);
  assert.equal(bytesEqual(roundTrip, firstBytes), true, 'round-trip bytes must match');
  assert.equal(verifyFirst.ok, true);
  assert.equal(verifySecond.ok, true);
  assert.equal(directVerify.ok, true);
  assert.deepEqual(Array.from(await store.get(secondPut.ref)), model.get(secondPut.digest));

  const corruptStore = rt.blockStore({ name: 'rev0025-corrupt-fake-block-store', provider: 'memory-fake-provider-v0' });
  const corruptPut = await corruptStore.put('corrupt me', { label: 'corrupt-target' });
  corruptStore.corrupt(corruptPut.ref);
  let corruptionDetected = false;
  try { await corruptStore.get(corruptPut.ref); } catch (error) { corruptionDetected = error.code === 'BRT_STORAGE_CHECKSUM_MISMATCH' || /checksum mismatch/i.test(error.message); }
  assert.equal(corruptionDetected, true, 'corrupted stored bytes must be detected');

  const faultStore = rt.blockStore({ name: 'rev0025-fault-fake-block-store', provider: 'memory-fake-provider-v0', faults: [{ op: 'put', at: 1, code: 'BRT_STORAGE_FAULT_SCRIPTED', message: 'rev0025 injected put failure' }] });
  let injectedWriteFailureObserved = false;
  try { await faultStore.put('should fail'); } catch (error) { injectedWriteFailureObserved = error.code === 'BRT_STORAGE_FAULT_SCRIPTED'; }
  assert.equal(injectedWriteFailureObserved, true, 'injected provider write failure must be observable');

  const quotaStore = rt.blockStore({ name: 'rev0025-quota-fake-block-store', provider: 'memory-fake-provider-v0', quotaBytes: 4 });
  let quotaFailureObserved = false;
  try { await quotaStore.put(new Uint8Array([1, 2, 3, 4, 5]), { label: 'too-large' }); } catch (error) { quotaFailureObserved = error.code === 'BRT_STORAGE_QUOTA_EXCEEDED'; }
  assert.equal(quotaFailureObserved, true, 'quota failure must be observable');


  assert.equal(await store.delete(secondPut.ref), true);
  model.delete(secondPut.digest);
  assert.equal(await store.has(secondPut.ref), false);
  await assert.rejects(() => store.get(secondPut.ref), /Block not found/);

  const snapshot = store.snapshot();
  const manifest = store.manifest();
  assert.equal(snapshot.blockCount, 1, 'delete leaves only the first unique block');
  assert.equal(manifest.blockCount, 1);
  assert.equal(manifest.blocks[0].digest, firstPut.digest);
  assert.ok(rt.trace.kinds().includes('storage:blockstore-create'));
  assert.ok(rt.trace.kinds().includes('storage:block-put'));
  assert.ok(rt.trace.kinds().includes('storage:block-verify'));
  assert.ok(rt.trace.kinds().includes('storage:block-get-error'));
  assert.ok(rt.trace.kinds().includes('storage:block-fault'));

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    probe: 'fake-block-store-provider-proof',
    status: 'passed',
    generatedAt: new Date().toISOString(),
    durationMs: Math.round(performance.now() - started),
    observations: {
      runtimeStoreCreated: true,
      directStoreCreated: true,
      manifestId: MANIFEST_ID,
      contentAddressStable: firstPut.digest === duplicatePut.digest,
      duplicatePutSameRef: firstPut.digest === duplicatePut.digest,
      duplicateDeduped: duplicatePut.duplicate === true,
      roundTripSameBytes: bytesEqual(roundTrip, firstBytes),
      readAfterWrite: bytesEqual(roundTrip, firstBytes),
      modelCommandWalkMatched: modelCommandWalkMatched && Array.from(await store.get(firstPut.ref)).join(',') === model.get(firstPut.digest).join(','),
      modelCommandCount,
      verifyFirstOk: verifyFirst.ok,
      verifySecondOk: verifySecond.ok,
      corruptionDetected,
      injectedWriteFailureObserved,
      injectedFailureObserved: injectedWriteFailureObserved,
      quotaFailureObserved,
      deleteRemovesBlock: snapshot.blockCount === 1,
      blockRefKind: firstPut.ref.kind,
      blockRefBackend: firstPut.ref.backend,
      manifestKind: manifest.kind,
      traceKinds: rt.trace.kinds()
    },
    blockRefs: { first: firstPut.ref, duplicate: duplicatePut.ref, direct: directPut.ref },
    snapshot,
    manifest,
    nonClaims: [
      'MemoryBlockStore is a fake/in-memory provider proof, not durable storage.',
      'This probe does not prove OPFS block-store durability, crash recovery, quota behavior, encryption, compression, or deduplication across browser sessions.',
      'The content-addressed reference shape is intentionally tiny and may evolve behind the BRT1/versioned provider contract.'
    ]
  };

  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else {
    console.log(JSON.stringify(report, null, 2));
  }
}

await main();
