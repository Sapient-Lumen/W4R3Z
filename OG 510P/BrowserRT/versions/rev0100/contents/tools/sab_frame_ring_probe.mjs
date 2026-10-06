#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { Worker } from 'node:worker_threads';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, boot, createSharedFrameRing } from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-SAB-FRAME-RING-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function makePayload(seq) {
  const length = 1 + ((seq * 17) % 47);
  const payload = new Uint8Array(length);
  for (let i = 0; i < payload.length; i += 1) payload[i] = (seq * 31 + i * 7 + length) & 0xff;
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

async function workerResult(worker) {
  return await new Promise((resolve, reject) => {
    worker.once('message', resolve);
    worker.once('error', reject);
    worker.once('exit', (code) => {
      if (code !== 0) reject(new Error(`sab frame ring worker exited with code ${code}`));
    });
  });
}

async function pushEventually(ring, frame, stats) {
  let tries = 0;
  while (!ring.tryPushFrame(frame.payload, { seq: frame.seq })) {
    tries += 1;
    stats.producerWaits += 1;
    await sleep(1);
    if (tries > 3000) throw new Error(`producer could not push frame ${frame.seq}`);
  }
  stats.maxPushTries = Math.max(stats.maxPushTries, tries + 1);
}

export async function runSabFrameRingProbe() {
  const started = performance.now();
  const rt = await boot({ sabFrameRingProbe: true });
  const trace = new TraceLog();
  const capacityBytes = 192;
  const frameCount = 72;
  const frames = Array.from({ length: frameCount }, (_, i) => ({ seq: i, payload: makePayload(i) }));
  const ring = createSharedFrameRing({ capacityBytes, label: 'rev0025-sab-frame-ring-proof', trace });

  // Oversize proof is separate from bounded-full proof: it rejects cleanly before producer starts.
  const oversizeRejected = ring.tryPushFrame(new Uint8Array(capacityBytes), { seq: 0x7fff }) === false;

  let prefilled = 0;
  for (; prefilled < frames.length; prefilled += 1) {
    if (!ring.tryPushFrame(frames[prefilled].payload, { seq: frames[prefilled].seq })) break;
  }
  const fullBeforeConsumer = prefilled > 0 && ring.tryPushFrame(new Uint8Array(31), { seq: 0x7ffe }) === false;
  assert.equal(fullBeforeConsumer, true, 'bounded frame ring should reject when full before consumer starts');

  const worker = new Worker(new URL('../src/sab-frame-ring-worker.mjs', import.meta.url), {
    workerData: { sab: ring.sab, label: 'rev0025-sab-frame-ring-worker', timeoutMs: 1000 },
    name: 'browserrt-rev0025-sab-frame-ring-worker'
  });

  const pushStats = { producerWaits: 0, maxPushTries: 0, prefilled };
  for (let i = prefilled; i < frames.length; i += 1) {
    await pushEventually(ring, frames[i], pushStats);
  }
  ring.close();

  const result = await workerResult(worker);
  const expectedDescriptors = frames.map((frame) => ({ seq: frame.seq, bytes: frame.payload.byteLength, checksum: checksum(frame.payload) }));
  const expectedTotalBytes = expectedDescriptors.reduce((sum, frame) => sum + frame.bytes, 0);
  const expectedCombinedChecksum = expectedDescriptors.reduce((sum, frame) => (sum + frame.checksum + frame.seq) >>> 0, 0);
  const seqsInOrder = result.frames.length === expectedDescriptors.length && result.frames.every((frame, i) => frame.seq === expectedDescriptors[i].seq);
  const lengthsMatch = result.frames.length === expectedDescriptors.length && result.frames.every((frame, i) => frame.bytes === expectedDescriptors[i].bytes);
  const checksumsMatch = result.frames.length === expectedDescriptors.length && result.frames.every((frame, i) => frame.checksum === expectedDescriptors[i].checksum);
  const ringSnapshot = ring.snapshot();
  const traceKinds = trace.kinds();
  const requiredEventKinds = ['ipc:sab-frame-ring-create', 'ipc:sab-frame-ring-open', 'ipc:sab-frame-ring-push', 'ipc:sab-frame-ring-full', 'ipc:sab-frame-ring-wrap', 'ipc:sab-frame-ring-close'];
  const missingEvents = requiredEventKinds.filter((kind) => !traceKinds.includes(kind));

  const observations = {
    sharedArrayBufferAvailable: typeof SharedArrayBuffer === 'function',
    atomicsAvailable: typeof Atomics === 'object',
    capacityBytes,
    frameCount,
    variableLengthsObserved: new Set(expectedDescriptors.map((frame) => frame.bytes)).size > 8,
    oversizeRejected,
    fullBeforeConsumer,
    producerBackpressureObserved: pushStats.producerWaits > 0 || ringSnapshot.fullHits > 0,
    wraparoundObserved: ringSnapshot.wrapCount > 0,
    reservedGapBytesObserved: ringSnapshot.reservedBytes > 0,
    allReceived: result.count === frameCount,
    seqsInOrder,
    lengthsMatch,
    checksumsMatch,
    totalBytesMatches: result.totalBytes === expectedTotalBytes,
    combinedChecksumMatches: result.combinedChecksum === expectedCombinedChecksum,
    ringClosed: ringSnapshot.closed === true,
    noPendingBytes: ringSnapshot.usedBytes === 0,
    workerPopCountMatches: result.snapshot.popCount === frameCount,
    traceHasRequiredEvents: missingEvents.length === 0
  };

  for (const [key, value] of Object.entries(observations)) {
    if (typeof value === 'boolean') assert.equal(value, true, `observation ${key}`);
  }

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    proof_id: 'ipc:sab-frame-ring-proof',
    status: 'passed',
    generatedAt: new Date().toISOString(),
    durationMs: Math.round(performance.now() - started),
    bootReport: rt.report,
    observations,
    pushStats,
    ringSnapshot,
    workerResult: {
      count: result.count,
      totalBytes: result.totalBytes,
      combinedChecksum: result.combinedChecksum,
      firstFrames: result.firstFrames,
      lastFrames: result.lastFrames,
      durationMs: result.durationMs,
      snapshot: result.snapshot
    },
    expected: {
      firstFrames: expectedDescriptors.slice(0, 8),
      lastFrames: expectedDescriptors.slice(-8),
      totalBytes: expectedTotalBytes,
      combinedChecksum: expectedCombinedChecksum
    },
    requiredEventKinds,
    eventKinds: traceKinds,
    trace: trace.snapshot(),
    nonClaims: [
      'SPSC variable-size frame ring only; no MPSC, MPMC, broadcast, or multi-consumer proof.',
      'Node worker_threads proof only; browser Worker frame-ring proof remains separate.',
      'Frames are copied into and out of the ring; no zero-copy typed schema claim.',
      'No throughput or latency performance claim.',
      'No waitAsync, WebAssembly shared-memory, or OPFS spill mailbox proof.'
    ]
  };
  return report;
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runSabFrameRingProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
