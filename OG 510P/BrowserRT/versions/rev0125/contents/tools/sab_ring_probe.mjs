#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { Worker } from 'node:worker_threads';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION, TraceLog, boot, createSharedInt32Ring } from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-SAB-RING-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function workerResult(worker) {
  return await new Promise((resolve, reject) => {
    worker.once('message', resolve);
    worker.once('error', reject);
    worker.once('exit', (code) => {
      if (code !== 0) reject(new Error(`sab ring worker exited with code ${code}`));
    });
  });
}

async function pushEventually(ring, value, stats) {
  let tries = 0;
  while (!ring.tryPush(value)) {
    tries += 1;
    stats.producerWaits += 1;
    await sleep(1);
    if (tries > 2000) throw new Error(`producer could not push value ${value}`);
  }
  stats.maxPushTries = Math.max(stats.maxPushTries, tries + 1);
}

export async function runSabRingProbe() {
  const started = performance.now();
  const rt = await boot({ sabRingProbe: true });
  const trace = new TraceLog();
  const capacity = 8;
  const messageCount = 64;
  const ring = createSharedInt32Ring({ capacity, label: 'rev0025-sab-ring-proof', trace });

  for (let value = 1; value <= capacity; value += 1) {
    assert.equal(ring.tryPush(value), true, `prefill value ${value}`);
  }
  const fullBeforeConsumer = ring.tryPush(999) === false;
  assert.equal(fullBeforeConsumer, true, 'bounded ring should reject push when full');

  const worker = new Worker(new URL('../src/sab-ring-worker.mjs', import.meta.url), {
    workerData: { sab: ring.sab, label: 'rev0025-sab-ring-worker', timeoutMs: 1000 },
    name: 'browserrt-rev0025-sab-ring-worker'
  });

  const pushStats = { producerWaits: 0, maxPushTries: 0 };
  for (let value = capacity + 1; value <= messageCount; value += 1) {
    await pushEventually(ring, value, pushStats);
  }
  ring.close();

  const result = await workerResult(worker);
  const expectedValues = Array.from({ length: messageCount }, (_, i) => i + 1);
  const expectedSum = expectedValues.reduce((sum, value) => sum + value, 0);
  const valuesInOrder = result.values.length === expectedValues.length && result.values.every((value, i) => value === expectedValues[i]);
  const ringSnapshot = ring.snapshot();
  const traceKinds = trace.kinds();
  const requiredEventKinds = ['ipc:sab-ring-create', 'ipc:sab-ring-open', 'ipc:sab-ring-push', 'ipc:sab-ring-full', 'ipc:sab-ring-close'];
  const missingEvents = requiredEventKinds.filter((kind) => !traceKinds.includes(kind));

  const observations = {
    sharedArrayBufferAvailable: typeof SharedArrayBuffer === 'function',
    atomicsAvailable: typeof Atomics === 'object',
    capacity,
    messageCount,
    fullBeforeConsumer,
    producerBackpressureObserved: pushStats.producerWaits > 0 || ringSnapshot.fullHits > 0,
    wraparoundObserved: ringSnapshot.write > capacity && ringSnapshot.read > capacity,
    allReceived: result.count === messageCount,
    valuesInOrder,
    sumMatches: result.sum === expectedSum,
    ringClosed: ringSnapshot.closed === true,
    noPendingItems: ringSnapshot.size === 0,
    workerPopCountMatches: result.snapshot.popCount === messageCount,
    traceHasRequiredEvents: missingEvents.length === 0
  };

  assert.equal(observations.sharedArrayBufferAvailable, true);
  assert.equal(observations.atomicsAvailable, true);
  assert.equal(observations.allReceived, true);
  assert.equal(observations.valuesInOrder, true);
  assert.equal(observations.sumMatches, true);
  assert.equal(observations.ringClosed, true);
  assert.equal(observations.noPendingItems, true);
  assert.equal(observations.workerPopCountMatches, true);
  assert.equal(observations.traceHasRequiredEvents, true);

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    proof_id: 'storage:journal-recovery-proof'.replace('storage:journal-recovery-proof', 'ipc:sab-ring-proof'),
    status: 'passed',
    generatedAt: new Date().toISOString(),
    durationMs: Math.round(performance.now() - started),
    bootReport: rt.report,
    observations,
    pushStats,
    ringSnapshot,
    workerResult: {
      count: result.count,
      sum: result.sum,
      firstValues: result.values.slice(0, 8),
      lastValues: result.values.slice(-8),
      durationMs: result.durationMs,
      snapshot: result.snapshot
    },
    requiredEventKinds,
    eventKinds: traceKinds,
    trace: trace.snapshot(),
    nonClaims: [
      'SPSC Int32 ring only; no MPSC, MPMC, variable-size frame, or multi-consumer proof.',
      'Node worker_threads proof only; browser Worker SAB ring proof remains separate.',
      'No throughput or latency performance claim.',
      'No waitAsync proof.',
      'No WebAssembly shared-memory integration proof.'
    ]
  };
  return report;
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runSabRingProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
