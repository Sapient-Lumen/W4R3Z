#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, createMemoryBlockStore, REVISION, TraceLog, VERSION } from '../src/browserrt.mjs';
import { checksumFramePayload32, createSpillFrameMailbox } from '../src/spill-mailbox.mjs';

const DEFAULT_ARTIFACT = `artifacts/validation/REV${REVISION.slice(3)}-SPILL-MAILBOX-PROBE.json`;

function parseArgs(argv) {
  const out = { json: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--json') out.json = argv[++i];
    else throw new Error(`Unknown option: ${argv[i]}`);
  }
  return out;
}

function makeFrame(seq) {
  const length = 9 + ((seq * 17) % 53);
  const bytes = new Uint8Array(length);
  for (let i = 0; i < bytes.length; i += 1) bytes[i] = (seq * 31 + i * 7 + 13) & 0xff;
  return bytes;
}

async function drain(mailbox) {
  const rows = [];
  for (;;) {
    const got = await mailbox.dequeue({ consumerId: 'proof-consumer' });
    if (!got) break;
    rows.push({
      seq: got.seq,
      bytes: got.bytes,
      checksum32: checksumFramePayload32(got.payload),
      source: got.source,
      pendingId: got.pendingId
    });
    assert.equal(await mailbox.ack(got.pendingId), true);
  }
  return rows;
}

async function runProof() {
  const trace = new TraceLog();
  const rt = await boot({ spillMailboxProbe: true });
  const provider = createMemoryBlockStore({ name: 'rev0025-spill-mailbox-store', trace });
  const mailbox = createSpillFrameMailbox({
    label: 'rev0025-spill-mailbox',
    memoryCapacityBytes: 96,
    maxFrameBytes: 128,
    provider,
    trace
  });

  const enqueued = [];
  for (let seq = 0; seq < 42; seq += 1) {
    const payload = makeFrame(seq);
    const checksum32 = checksumFramePayload32(payload);
    const result = await mailbox.enqueue(payload, { seq, label: `frame-${seq}` });
    assert.ok(['memory', 'spilled'].includes(result.disposition));
    enqueued.push({ seq, bytes: payload.byteLength, checksum32, disposition: result.disposition, digest: result.digest ?? null });
  }

  const preDrain = mailbox.snapshot();
  const oversized = await mailbox.enqueue(new Uint8Array(256), { seq: 999 });
  assert.equal(oversized.disposition, 'rejected-oversize');

  const dequeued = await drain(mailbox);
  const postDrain = mailbox.snapshot();
  const emptyPoll = await mailbox.dequeue({ consumerId: 'proof-consumer' });
  assert.equal(emptyPoll, null);

  const reclaimProvider = createMemoryBlockStore({ name: 'rev0025-reclaim-provider', trace });
  const reclaimMailbox = createSpillFrameMailbox({ label: 'rev0025-reclaim-mailbox', memoryCapacityBytes: 4, provider: reclaimProvider, trace });
  await reclaimMailbox.enqueue(new Uint8Array([1, 2, 3, 4, 5, 6]), { seq: 700 });
  const pending = await reclaimMailbox.dequeue({ consumerId: 'slow-consumer' });
  const reclaimed = reclaimMailbox.reclaimPending({ max: 1 });
  const redelivered = await reclaimMailbox.dequeue({ consumerId: 'retry-consumer' });
  assert.equal(redelivered.seq, pending.seq);
  await reclaimMailbox.ack(redelivered.pendingId);

  const quotaTrace = new TraceLog();
  const quotaProvider = createMemoryBlockStore({ name: 'rev0025-spill-quota-store', quotaBytes: 16, trace: quotaTrace });
  const quotaMailbox = createSpillFrameMailbox({ label: 'rev0025-spill-quota-mailbox', memoryCapacityBytes: 8, provider: quotaProvider, trace: quotaTrace });
  const quotaMemory = await quotaMailbox.enqueue(new Uint8Array(8), { seq: 0 });
  const quotaRejected = await quotaMailbox.enqueue(new Uint8Array(48), { seq: 1 });
  assert.equal(quotaMemory.disposition, 'memory');
  assert.equal(quotaRejected.disposition, 'rejected-spill');
  assert.equal(quotaRejected.reason, 'BRT_STORAGE_QUOTA_EXCEEDED');

  const eventKinds = trace.kinds();
  const requiredEvents = [
    'mailbox:spill-create',
    'mailbox:enqueue-memory',
    'mailbox:spill-write',
    'mailbox:dequeue',
    'mailbox:ack',
    'mailbox:spill-reject',
    'mailbox:pending-reclaim',
    'storage:block-put',
    'storage:block-get',
    'storage:block-delete'
  ];
  const missingEvents = requiredEvents.filter((kind) => !eventKinds.includes(kind));

  const observations = {
    memoryEnqueueObserved: enqueued.some((row) => row.disposition === 'memory'),
    spillEnqueueObserved: enqueued.some((row) => row.disposition === 'spilled'),
    blockRefsObserved: enqueued.some((row) => row.digest),
    fifoOrderPreserved: dequeued.length === enqueued.length && dequeued.every((row, i) => row.seq === enqueued[i].seq),
    lengthsMatch: dequeued.length === enqueued.length && dequeued.every((row, i) => row.bytes === enqueued[i].bytes),
    checksumsMatch: dequeued.length === enqueued.length && dequeued.every((row, i) => row.checksum32 === enqueued[i].checksum32),
    spilledDequeuesObserved: dequeued.some((row) => row.source === 'spill'),
    ackDeletedSpilledBlocks: postDrain.providerSnapshot?.blockCount === 0,
    emptyPollObserved: emptyPoll === null,
    oversizeRejected: oversized.disposition === 'rejected-oversize',
    providerQuotaRejectionObserved: quotaRejected.reason === 'BRT_STORAGE_QUOTA_EXCEEDED',
    reclaimRedeliveryObserved: reclaimed.reclaimed === 1 && redelivered.seq === 700,
    traceHasRequiredEvents: missingEvents.length === 0
  };
  for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    proof_id: 'ipc:spill-mailbox-fake-proof',
    status: 'passed',
    generatedAt: new Date().toISOString(),
    observations,
    enqueuedCount: enqueued.length,
    dequeuedCount: dequeued.length,
    memoryEnqueueCount: enqueued.filter((row) => row.disposition === 'memory').length,
    spilledEnqueueCount: enqueued.filter((row) => row.disposition === 'spilled').length,
    preDrainSnapshot: preDrain,
    postDrainSnapshot: postDrain,
    quotaRejected,
    reclaim: { reclaimed, pendingSeq: pending.seq, redeliveredSeq: redelivered.seq, snapshot: reclaimMailbox.snapshot() },
    requiredEventKinds: requiredEvents,
    eventKinds,
    missingEvents,
    trace: trace.snapshot(),
    quotaTrace: quotaTrace.snapshot(),
    runtimeExecutableProofs: rt.report.executableProofs,
    nonClaims: [
      'No OPFS spill mailbox proof.',
      'No browser Worker spill mailbox proof.',
      'No persisted queue recovery proof.',
      'No multi-producer or multi-consumer proof.',
      'No throughput or latency claim.',
      'No cross-browser conformance claim.'
    ]
  };
}

const args = parseArgs(process.argv.slice(2));
const report = await runProof();
if (args.json) {
  await mkdir(dirname(args.json), { recursive: true });
  await writeFile(args.json, `${JSON.stringify(report, null, 2)}\n`);
}
console.log(JSON.stringify({ status: report.status, proof_id: report.proof_id, enqueued: report.enqueuedCount, spilled: report.spilledEnqueueCount }, null, 2));
