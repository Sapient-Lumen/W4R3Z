#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, REVISION, VERSION, checksumPersistedSpillPayload32 } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-PERSISTED-SPILL-RECOVERY-PROBE.json`;

function argValue(argv, flag, fallback = null) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}

function bytesForSeq(seq) {
  const length = 7 + (seq % 5) * 3;
  const bytes = new Uint8Array(length);
  for (let i = 0; i < bytes.length; i += 1) bytes[i] = (seq * 17 + i * 11) & 0xff;
  return bytes;
}

function checksumList(frames) {
  return frames.map((frame) => checksumPersistedSpillPayload32(frame.payload));
}

function corruptManifest(manifest) {
  const copy = JSON.parse(JSON.stringify(manifest));
  copy.payload.queue.push({ seq: 999, ref: { id: 'missing' }, bytes: 1, checksum32: 0, label: 'evil', deliveryCount: 0 });
  return copy;
}

async function drain(mailbox) {
  const rows = [];
  for (;;) {
    const frame = await mailbox.dequeue({ consumerId: 'recovered-consumer' });
    if (!frame) break;
    rows.push(frame);
    await mailbox.ack(frame.pendingId);
  }
  return rows;
}

async function main() {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const rt = await boot({ persistedSpillRecoveryProbe: true });
  const provider = rt.journaledBlockStore({ name: 'persisted-spill-payload-provider', provider: 'journaled-memory-persisted-spill-provider-v0' });
  const mailbox = rt.persistedSpillMailbox({ label: 'persisted-spill-recovery-proof', provider, maxFrameBytes: 128, memoryCapacityBytes: 1, deleteBlockOnAck: true });

  const enqueues = [];
  for (let seq = 1; seq <= 10; seq += 1) enqueues.push(await mailbox.enqueue(bytesForSeq(seq), { label: `before-checkpoint-${seq}` }));
  const d1 = await mailbox.dequeue({ consumerId: 'worker-a' });
  await mailbox.ack(d1.pendingId);
  const d2 = await mailbox.dequeue({ consumerId: 'worker-a' });
  const checkpoint = await mailbox.checkpoint({ label: 'after-one-ack-one-pending' });

  const d3 = await mailbox.dequeue({ consumerId: 'worker-b' });
  await mailbox.ack(d3.pendingId);
  const d4 = await mailbox.dequeue({ consumerId: 'worker-b' });
  const e11 = await mailbox.enqueue(bytesForSeq(11), { label: 'after-checkpoint-11' });
  const e12 = await mailbox.enqueue(bytesForSeq(12), { label: 'after-checkpoint-12' });

  const journal = mailbox.exportJournal();
  const torn = mailbox.tornRecordForTest();
  const recovered = await rt.recoverPersistedSpillMailbox({ manifest: checkpoint, journal: [...journal, torn], provider, label: 'recovered-persisted-spill-proof' });
  const recoveredAgain = await rt.recoverPersistedSpillMailbox({ manifest: checkpoint, journal, provider, label: 'recovered-persisted-spill-proof-repeat' });
  let corruptManifestRejected = false;
  try {
    await rt.recoverPersistedSpillMailbox({ manifest: corruptManifest(checkpoint), journal, provider, label: 'bad-manifest' });
  } catch (error) {
    corruptManifestRejected = /CHECKSUM|BAD_MANIFEST/i.test(error.code || error.message);
  }

  const recovery = recovered.recovery;
  const repeatRecovery = recoveredAgain.recovery;
  const expectedReadySeqs = [2, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  const beforeDrainSnapshot = recovered.mailbox.snapshot();
  const repeatSnapshot = recoveredAgain.mailbox.snapshot();
  const drained = await drain(recovered.mailbox);
  const afterDrainSnapshot = recovered.mailbox.snapshot();
  const drainedSeqs = drained.map((row) => row.seq);
  const drainedChecksums = checksumList(drained);
  const expectedChecksums = expectedReadySeqs.map((seq) => checksumPersistedSpillPayload32(bytesForSeq(seq)));
  const trace = rt.close();
  const eventKinds = [...new Set(trace.map((event) => event.kind))].sort();
  const requiredEvents = [
    'mailbox:persisted-create',
    'mailbox:persisted-journal-append',
    'mailbox:persisted-enqueue',
    'mailbox:persisted-deliver',
    'mailbox:persisted-ack',
    'mailbox:persisted-checkpoint',
    'mailbox:persisted-manifest-recover',
    'mailbox:persisted-journal-replay-apply',
    'mailbox:persisted-torn-record-ignored',
    'mailbox:persisted-requeue-pending',
    'mailbox:persisted-recover'
  ];

  const observations = {
    enqueuedTwelveMessages: enqueues.length === 10 && e11.disposition === 'spilled-persisted' && e12.disposition === 'spilled-persisted',
    checkpointHasReadyAndPending: checkpoint.payload.queue.length === 8 && checkpoint.payload.pending.length === 1,
    checkpointSeqBeforeTail: checkpoint.opSeq < journal.at(-1).opSeq,
    replayedPostCheckpointTail: recovery.appliedJournalRecords > 0,
    tornTailIgnored: recovery.ignoredTailRecords === 1,
    corruptManifestRejected,
    pendingRedeliveredAfterRecovery: recovery.requeuedPending === 2,
    ackedMessagesNotRedelivered: !beforeDrainSnapshot.queueSeqs.includes(1) && !beforeDrainSnapshot.queueSeqs.includes(3),
    readySeqsExpected: JSON.stringify(beforeDrainSnapshot.queueSeqs) === JSON.stringify(expectedReadySeqs),
    repeatRecoveryDeterministic: JSON.stringify(beforeDrainSnapshot.queueSeqs) === JSON.stringify(repeatSnapshot.queueSeqs) && recovery.finalOpSeq === repeatRecovery.finalOpSeq,
    drainedSeqsExpected: JSON.stringify(drainedSeqs) === JSON.stringify(expectedReadySeqs),
    drainedChecksumsMatch: JSON.stringify(drainedChecksums) === JSON.stringify(expectedChecksums),
    finalQueueEmpty: afterDrainSnapshot.queueDepth === 0 && afterDrainSnapshot.pendingCount === 0,
    traceHasRequiredEvents: requiredEvents.every((kind) => eventKinds.includes(kind))
  };
  observations.checkpointCapturedQueueAndPending = observations.checkpointHasReadyAndPending;
  observations.unackedPendingRequeued = observations.pendingRedeliveredAfterRecovery;
  observations.fifoAfterRecovery = observations.readySeqsExpected && observations.drainedSeqsExpected;
  observations.payloadChecksumsMatch = observations.drainedChecksumsMatch;
  observations.ackDeletedRecoveredBlocks = afterDrainSnapshot.providerSnapshot.blockCount === 0;

  for (const [key, value] of Object.entries(observations)) assert.equal(value, true, `observation ${key} must be true`);
  assert.equal(beforeDrainSnapshot.queueDepth, expectedReadySeqs.length);
  assert.equal(drained.length, expectedReadySeqs.length);

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    status: 'passed',
    proof_id: 'ipc:persisted-spill-recovery-proof',
    slice: 'ipc:persisted-spill-recovery-proof',
    generatedAt: new Date().toISOString(),
    purpose: 'Fake-provider persisted spill recovery proof: metadata journal, checkpoint, post-checkpoint replay, at-least-once redelivery of pending deliveries, ack tombstones, torn-tail ignore, corrupt manifest rejection, and deterministic repeat recovery.',
    nonClaims: [
      'No OPFS provider proof.',
      'No browser Worker persisted spill proof.',
      'No fsync, flush, quota, eviction, or crash durability claim.',
      'No exactly-once delivery claim; pending deliveries recover as at-least-once redelivery.',
      'No multi-producer or multi-consumer proof.',
      'No throughput or latency claim.'
    ],
    counts: {
      totalEnqueues: 12,
      journalRecords: journal.length,
      checkpointOpSeq: checkpoint.opSeq,
      appliedJournalRecords: recovery.appliedJournalRecords,
      requeuedPending: recovery.requeuedPending,
      drained: drained.length
    },
    observations,
    checkpointSummary: { opSeq: checkpoint.opSeq, queueDepth: checkpoint.payload.queue.length, pendingCount: checkpoint.payload.pending.length },
    recovery,
    repeatRecovery,
    beforeDrainSnapshot,
    afterDrainSnapshot,
    drainedSeqs,
    expectedReadySeqs,
    drainedChecksums,
    expectedChecksums,
    eventKinds,
    requiredEvents
  };
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
