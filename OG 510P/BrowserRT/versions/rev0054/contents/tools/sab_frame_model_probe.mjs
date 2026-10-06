#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, boot, createSharedFrameRing } from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-SAB-FRAME-MODEL-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function mulberry32(seed) {
  let t = seed >>> 0;
  return () => {
    t = (t + 0x6d2b79f5) >>> 0;
    let x = t;
    x = Math.imul(x ^ (x >>> 15), x | 1);
    x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

function int(rand, min, max) {
  return min + Math.floor(rand() * (max - min + 1));
}

function makePayload(seed, seq, rand, maxLen) {
  const length = int(rand, 1, maxLen);
  const payload = new Uint8Array(length);
  for (let i = 0; i < payload.length; i += 1) {
    payload[i] = (seed * 17 + seq * 31 + i * 13 + length) & 0xff;
  }
  return payload;
}

function checksum(bytes) {
  let out = 2166136261 >>> 0;
  for (const b of bytes) {
    out ^= b;
    out = Math.imul(out, 16777619) >>> 0;
  }
  return out >>> 0;
}

function descriptor(seq, payload) {
  return { seq, bytes: payload.byteLength, checksum: checksum(payload), payload: new Uint8Array(payload) };
}

function samePayload(a, b) {
  if (!a || !b || a.byteLength !== b.byteLength) return false;
  for (let i = 0; i < a.byteLength; i += 1) if (a[i] !== b[i]) return false;
  return true;
}

function checkSnapshotInvariant(snapshot, modelLength, context) {
  assert.ok(snapshot.usedBytes >= 0, `${context}: usedBytes non-negative`);
  assert.ok(snapshot.usedBytes <= snapshot.capacityBytes, `${context}: usedBytes within capacity`);
  assert.ok(snapshot.freeBytes >= 0, `${context}: freeBytes non-negative`);
  assert.equal(snapshot.pushCount - snapshot.popCount, modelLength, `${context}: push-pop equals model length`);
}

function runScenario({ seed, capacityBytes, steps, maxFrameBytes }) {
  const rand = mulberry32(seed);
  const trace = new TraceLog();
  const ring = createSharedFrameRing({ capacityBytes, label: `rev0025-frame-model-${seed}`, trace });
  const model = [];
  const stats = {
    seed,
    capacityBytes,
    steps,
    pushesAccepted: 0,
    pushRejects: 0,
    oversizeRejects: 0,
    popEmptyChecks: 0,
    popsMatched: 0,
    closeDrainPops: 0,
    snapshotChecks: 0,
    rejectionNoMutationChecks: 0,
    maxModelDepth: 0,
    firstCounterexample: null
  };
  let nextSeq = seed * 10000;

  const rememberFailure = (message, extra = {}) => {
    if (!stats.firstCounterexample) stats.firstCounterexample = { message, extra };
    throw new Error(`${message}: ${JSON.stringify(extra)}`);
  };

  const tryPushAndModel = (payload, seq, expectOversize = false) => {
    const before = ring.snapshot();
    const beforeModelLength = model.length;
    const pushed = ring.tryPushFrame(payload, { seq });
    if (pushed) {
      if (expectOversize) rememberFailure('oversize push unexpectedly accepted', { seed, seq, bytes: payload.byteLength });
      model.push(descriptor(seq, payload));
      stats.pushesAccepted += 1;
      stats.maxModelDepth = Math.max(stats.maxModelDepth, model.length);
    } else {
      stats.pushRejects += 1;
      if (expectOversize) stats.oversizeRejects += 1;
      stats.rejectionNoMutationChecks += 1;
      const after = ring.snapshot();
      assert.equal(model.length, beforeModelLength, 'rejected push must not mutate model queue');
      assert.equal(after.pushCount, before.pushCount, 'rejected push must not increment pushCount');
      assert.equal(after.popCount, before.popCount, 'rejected push must not increment popCount');
    }
    checkSnapshotInvariant(ring.snapshot(), model.length, `after-push-${seed}-${seq}`);
    return pushed;
  };

  const popAndCompare = (context) => {
    const got = ring.popFrame();
    if (model.length === 0) {
      if (got.frame) rememberFailure('ring returned phantom frame', { seed, context, got: { seq: got.frame.seq, bytes: got.frame.payload.byteLength } });
      if (!got.done) stats.popEmptyChecks += 1;
      checkSnapshotInvariant(ring.snapshot(), model.length, `${context}-empty-pop`);
      return got;
    }
    if (!got.frame) rememberFailure('ring failed to return expected model frame', { seed, context, pending: model.length, gotDone: got.done });
    const expected = model.shift();
    if (got.frame.seq !== expected.seq || !samePayload(got.frame.payload, expected.payload)) {
      rememberFailure('ring/model FIFO mismatch', {
        seed,
        context,
        expected: { seq: expected.seq, bytes: expected.bytes, checksum: expected.checksum },
        got: { seq: got.frame.seq, bytes: got.frame.payload.byteLength, checksum: checksum(got.frame.payload) }
      });
    }
    stats.popsMatched += 1;
    checkSnapshotInvariant(ring.snapshot(), model.length, `${context}-pop`);
    return got;
  };

  // Fixed oversize attempt before random walk: proves clean rejection and no mutation.
  tryPushAndModel(new Uint8Array(capacityBytes), nextSeq++, true);

  for (let step = 0; step < steps; step += 1) {
    const roll = rand();
    if (roll < 0.58) {
      tryPushAndModel(makePayload(seed, nextSeq, rand, maxFrameBytes), nextSeq++, false);
    } else if (roll < 0.88) {
      popAndCompare(`step-${step}`);
    } else if (roll < 0.94) {
      tryPushAndModel(new Uint8Array(capacityBytes + int(rand, 1, 16)), nextSeq++, true);
    } else {
      stats.snapshotChecks += 1;
      checkSnapshotInvariant(ring.snapshot(), model.length, `snapshot-step-${step}`);
    }
  }

  const beforeClose = ring.snapshot();
  ring.close();
  const postClosePushRejected = ring.tryPushFrame(makePayload(seed, nextSeq, rand, Math.max(1, Math.min(16, maxFrameBytes))), { seq: nextSeq++ }) === false;
  assert.equal(postClosePushRejected, true, 'post-close push must reject');
  stats.rejectionNoMutationChecks += 1;
  while (model.length > 0) {
    popAndCompare('close-drain');
    stats.closeDrainPops += 1;
  }
  const done = ring.popFrame();
  assert.equal(done.done, true, 'closed empty ring should report done');
  const finalSnapshot = ring.snapshot();
  checkSnapshotInvariant(finalSnapshot, model.length, `final-${seed}`);
  assert.equal(finalSnapshot.usedBytes, 0, 'final snapshot should have zero used bytes');

  const traceKinds = trace.kinds();
  return {
    seed,
    capacityBytes,
    steps,
    status: 'passed',
    stats,
    beforeClose,
    finalSnapshot,
    postClosePushRejected,
    traceKinds,
    wrapObserved: finalSnapshot.wrapCount > 0,
    fullObserved: finalSnapshot.fullHits > 0,
    reservedGapBytesObserved: finalSnapshot.reservedBytes > 0,
    firstEvents: trace.snapshot().slice(0, 8),
    lastEvents: trace.snapshot().slice(-8)
  };
}

export async function runSabFrameModelProbe() {
  const started = performance.now();
  const rt = await boot({ sabFrameModelProbe: true });
  const scenarios = [];
  const seeds = Array.from({ length: 24 }, (_, i) => 0x5a17 + i * 97);
  const capacities = [64, 96, 128, 192];
  for (let i = 0; i < seeds.length; i += 1) {
    scenarios.push(runScenario({
      seed: seeds[i],
      capacityBytes: capacities[i % capacities.length],
      steps: 144,
      maxFrameBytes: i % 3 === 0 ? 48 : 56
    }));
  }

  const aggregate = scenarios.reduce((acc, s) => {
    acc.steps += s.steps;
    acc.pushesAccepted += s.stats.pushesAccepted;
    acc.pushRejects += s.stats.pushRejects;
    acc.oversizeRejects += s.stats.oversizeRejects;
    acc.popsMatched += s.stats.popsMatched;
    acc.closeDrainPops += s.stats.closeDrainPops;
    acc.popEmptyChecks += s.stats.popEmptyChecks;
    acc.snapshotChecks += s.stats.snapshotChecks;
    acc.rejectionNoMutationChecks += s.stats.rejectionNoMutationChecks;
    acc.wrapObserved ||= s.wrapObserved;
    acc.fullObserved ||= s.fullObserved;
    acc.reservedGapBytesObserved ||= s.reservedGapBytesObserved;
    acc.maxModelDepth = Math.max(acc.maxModelDepth, s.stats.maxModelDepth);
    return acc;
  }, {
    steps: 0,
    pushesAccepted: 0,
    pushRejects: 0,
    oversizeRejects: 0,
    popsMatched: 0,
    closeDrainPops: 0,
    popEmptyChecks: 0,
    snapshotChecks: 0,
    rejectionNoMutationChecks: 0,
    wrapObserved: false,
    fullObserved: false,
    reservedGapBytesObserved: false,
    maxModelDepth: 0
  });

  const observations = {
    sharedArrayBufferAvailable: typeof SharedArrayBuffer === 'function',
    atomicsAvailable: typeof Atomics === 'object',
    scenarioCount: scenarios.length,
    scenarioCountMeaningful: scenarios.length >= 16,
    totalStepsMeaningful: aggregate.steps >= 2400,
    acceptedPushesMeaningful: aggregate.pushesAccepted >= 400,
    popsMatchedMeaningful: aggregate.popsMatched >= 300,
    allScenariosPassed: scenarios.every((s) => s.status === 'passed'),
    oversizeRejected: aggregate.oversizeRejects >= scenarios.length,
    fullRejectionObserved: aggregate.fullObserved && aggregate.pushRejects > aggregate.oversizeRejects,
    rejectionNoMutationObserved: aggregate.rejectionNoMutationChecks >= scenarios.length,
    wrapObserved: aggregate.wrapObserved,
    reservedGapBytesObserved: aggregate.reservedGapBytesObserved,
    closeDrainObserved: aggregate.closeDrainPops > 0,
    noPendingBytesAtEnd: scenarios.every((s) => s.finalSnapshot.usedBytes === 0),
    finalPushPopBalancesHold: scenarios.every((s) => s.finalSnapshot.pushCount === s.finalSnapshot.popCount),
    traceHasFrameRingEvents: scenarios.every((s) => s.traceKinds.includes('ipc:sab-frame-ring-push') && s.traceKinds.includes('ipc:sab-frame-ring-close'))
  };

  for (const [key, value] of Object.entries(observations)) {
    if (typeof value === 'boolean') assert.equal(value, true, `observation ${key}`);
  }

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    proof_id: 'ipc:sab-frame-model-proof',
    status: 'passed',
    generatedAt: new Date().toISOString(),
    durationMs: Math.round(performance.now() - started),
    bootReport: rt.report,
    observations,
    aggregate,
    scenarios: scenarios.map((s) => ({
      seed: s.seed,
      capacityBytes: s.capacityBytes,
      steps: s.steps,
      stats: s.stats,
      beforeClose: s.beforeClose,
      finalSnapshot: s.finalSnapshot,
      postClosePushRejected: s.postClosePushRejected,
      wrapObserved: s.wrapObserved,
      fullObserved: s.fullObserved,
      reservedGapBytesObserved: s.reservedGapBytesObserved,
      traceKinds: s.traceKinds,
      firstEvents: s.firstEvents,
      lastEvents: s.lastEvents
    })),
    nonClaims: [
      'Deterministic stateful model walk only; not exhaustive formal model checking.',
      'Single-threaded direct ring operations only; no producer/consumer interleaving exploration.',
      'Node/cloudtainer proof only; no browser Worker variable-frame ring proof.',
      'No MPSC/MPMC, broadcast, schema-zero-copy, waitAsync, WebAssembly shared-memory, throughput, or latency proof.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runSabFrameModelProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
