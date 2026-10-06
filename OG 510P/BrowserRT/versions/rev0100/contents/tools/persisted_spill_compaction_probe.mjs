#!/usr/bin/env node
// BrowserRT rev0027 persisted-spill retention/compaction proof.
// Fake-provider only. No OPFS, durability, exactly-once, or performance claim.

import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, REVISION, VERSION, checksumPersistedSpillPayload32 } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-PERSISTED-SPILL-COMPACTION-PROBE.json`;

function argValue(argv, flag, fallback = null) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}

function bytes(label) {
  return new TextEncoder().encode(label);
}

function seqs(rows) { return rows.map((row) => row.seq); }
function checksums(rows) { return rows.map((row) => checksumPersistedSpillPayload32(row.payload)); }
function eventKinds(trace) { return [...new Set(trace.map((event) => event.kind))].sort(); }

async function drain(mailbox, { deleteBlock = false } = {}) {
  const rows = [];
  for (;;) {
    const frame = await mailbox.dequeue({ consumerId: 'retention-consumer' });
    if (!frame) break;
    rows.push(frame);
    await mailbox.ack(frame.pendingId, { deleteBlock });
  }
  return rows;
}

async function main() {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const rt = await boot({ persistedSpillCompactionProbe: true });
  const provider = rt.journaledBlockStore({ name: 'persisted-spill-compaction-provider', provider: 'journaled-memory-retention-compaction-provider-v0' });
  const mailbox = rt.persistedSpillMailbox({
    label: 'persisted-spill-compaction-proof',
    provider,
    memoryCapacityBytes: 0,
    maxFrameBytes: 128,
    deleteBlockOnAck: false
  });

  const payloads = new Map([
    [1, bytes('acked-old-unique-1')],
    [2, bytes('duplicate-live-payload')],
    [3, bytes('pending-live-3')],
    [4, bytes('ready-live-4')],
    [5, bytes('duplicate-live-payload')]
  ]);
  for (const [seq, payload] of payloads) await mailbox.enqueue(payload, { seq, label: `seq-${seq}` });

  const delivered1 = await mailbox.dequeue({ consumerId: 'worker-a' });
  await mailbox.ack(delivered1.pendingId, { deleteBlock: false });
  const delivered2 = await mailbox.dequeue({ consumerId: 'worker-a' });
  await mailbox.ack(delivered2.pendingId, { deleteBlock: false });
  const delivered3 = await mailbox.dequeue({ consumerId: 'worker-b' });
  const checkpointBeforeCompact = await mailbox.checkpoint({ label: 'acked-two-pending-one-before-compact' });
  const beforeCompactSnapshot = mailbox.snapshot();
  const providerBeforeCompact = provider.snapshot();

  const dryRun = await mailbox.compact({ dryRun: true, reason: 'retention-dry-run' });
  const providerAfterDryRun = provider.snapshot();
  const compact = await mailbox.compact({ reason: 'delete-unreferenced-acked-blocks' });
  const afterCompactSnapshot = mailbox.snapshot();
  const providerAfterCompact = provider.snapshot();
  const journalAfterCompact = mailbox.exportJournal();

  const recovered = await rt.recoverPersistedSpillMailbox({
    manifest: checkpointBeforeCompact,
    journal: journalAfterCompact,
    provider,
    label: 'recovered-after-compaction'
  });
  const recoveredSnapshot = recovered.mailbox.snapshot();
  const recoveredDrain = await drain(recovered.mailbox, { deleteBlock: false });
  const recoveredAfterDrainSnapshot = recovered.mailbox.snapshot();
  const providerAfterRecoveredDrain = provider.snapshot();
  const finalCompact = await recovered.mailbox.compact({ reason: 'delete-all-acked-after-drain' });
  const finalSnapshot = recovered.mailbox.snapshot();
  const finalProvider = provider.snapshot();

  const trace = rt.close();
  const kinds = eventKinds(trace);
  const requiredEvents = [
    'mailbox:persisted-checkpoint',
    'mailbox:persisted-compact-start',
    'mailbox:persisted-compact-delete',
    'mailbox:persisted-compact',
    'mailbox:persisted-journal-append',
    'mailbox:persisted-journal-replay-apply',
    'mailbox:persisted-requeue-pending',
    'mailbox:persisted-recover'
  ];
  const expectedRecoveredSeqs = [3, 4, 5];
  const expectedChecksums = expectedRecoveredSeqs.map((seq) => checksumPersistedSpillPayload32(payloads.get(seq)));
  const compactDeleteJournalRecords = journalAfterCompact.filter((record) => record.op === 'compact-delete');

  const observations = {
    initialContentAddressedDedupeObserved: providerBeforeCompact.blockCount === 4,
    checkpointCapturedRetainedRefs: checkpointBeforeCompact.payload.retainedRefs.length === 4,
    dryRunFoundOnlyAckedUniqueBlock: dryRun.dryRun === true && dryRun.candidateCount === 1,
    dryRunDidNotDelete: providerAfterDryRun.blockCount === providerBeforeCompact.blockCount,
    firstCompactDeletedOneBlock: compact.deleted === 1 && compact.deleteMisses === 0 && providerAfterCompact.blockCount === 3,
    liveDuplicatePreventedDeletion: afterCompactSnapshot.retainedBlockCount === 3 && afterCompactSnapshot.liveBlockDigests.includes(delivered2.ref.digest),
    pendingAndReadySurvivedCompact: afterCompactSnapshot.queueSeqs.join(',') === '4,5' && afterCompactSnapshot.pendingSeqs.join(',') === '3',
    compactDeleteWasJournaled: compactDeleteJournalRecords.length === 1,
    compactRecordReplayedInRecovery: recovered.recovery.appliedJournalRecords >= 1 && recoveredSnapshot.retainedBlockCount === 3,
    recoveredRequeuedPending: recovered.recovery.requeuedPending === 1 && recoveredSnapshot.queueSeqs.join(',') === expectedRecoveredSeqs.join(','),
    recoveredDrainSeqsExpected: seqs(recoveredDrain).join(',') === expectedRecoveredSeqs.join(','),
    recoveredDrainChecksumsMatch: checksums(recoveredDrain).join(',') === expectedChecksums.join(','),
    recoveredAckWithoutDeleteRetainsBlocksUntilCompaction: recoveredAfterDrainSnapshot.queueDepth === 0 && recoveredAfterDrainSnapshot.retainedBlockCount === 3 && providerAfterRecoveredDrain.blockCount === 3,
    finalCompactionDeletesRemainingBlocks: finalCompact.deleted === 3 && finalSnapshot.retainedBlockCount === 0,
    finalProviderEmpty: finalProvider.blockCount === 0,
    traceHasRequiredEvents: requiredEvents.every((kind) => kinds.includes(kind))
  };

  for (const [key, value] of Object.entries(observations)) assert.equal(value, true, `observation ${key} must be true`);

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    status: 'passed',
    proof_id: 'ipc:persisted-spill-compaction-proof',
    slice: 'ipc:persisted-spill-compaction-proof',
    generatedAt: new Date().toISOString(),
    purpose: 'Fake-provider persisted spill retention/compaction proof: retained refs, dry-run compaction, live-ref protection, compact-delete journal replay, pending redelivery after recovery, and post-ack deletion of unreferenced blocks.',
    nonClaims: [
      'No OPFS persisted-spill proof.',
      'No browser Worker persisted-spill proof.',
      'No fsync, flush, quota, eviction, or durability claim.',
      'No exactly-once delivery claim; pending deliveries recover as at-least-once redelivery.',
      'No production retention, compaction, or garbage-collection algorithm claim.',
      'No multi-producer or multi-consumer proof.',
      'No throughput or latency claim.'
    ],
    observations,
    counts: {
      providerBlocksBeforeCompact: providerBeforeCompact.blockCount,
      retainedBeforeCompact: beforeCompactSnapshot.retainedBlockCount,
      dryRunCandidates: dryRun.candidateCount,
      firstCompactDeleted: compact.deleted,
      compactDeleteJournalRecords: compactDeleteJournalRecords.length,
      recoveredDrained: recoveredDrain.length,
      finalCompactDeleted: finalCompact.deleted
    },
    checkpointSummary: {
      opSeq: checkpointBeforeCompact.opSeq,
      queueDepth: checkpointBeforeCompact.payload.queue.length,
      pendingCount: checkpointBeforeCompact.payload.pending.length,
      retainedRefs: checkpointBeforeCompact.payload.retainedRefs.length
    },
    dryRun,
    compact,
    finalCompact,
    recovery: recovered.recovery,
    beforeCompactSnapshot,
    afterCompactSnapshot,
    recoveredSnapshot,
    recoveredAfterDrainSnapshot,
    finalSnapshot,
    recoveredDrainSeqs: seqs(recoveredDrain),
    expectedRecoveredSeqs,
    eventKinds: kinds,
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
