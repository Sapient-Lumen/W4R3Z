#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { boot, createMemoryBlockStore, REVISION, TraceLog, VERSION } from '../src/browserrt.mjs';
import { createWatermarkAdmissionController } from '../src/admission-control.mjs';
import { checksumFramePayload32, createSpillFrameMailbox } from '../src/spill-mailbox.mjs';

const DEFAULT_ARTIFACT = `artifacts/validation/REV${REVISION.slice(3)}-ADMISSION-WATERMARK-PROBE.json`;

function parseArgs(argv) {
  const out = { json: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--json') out.json = argv[++i];
    else throw new Error(`Unknown option: ${argv[i]}`);
  }
  return out;
}

function frame(seq, length = 24) {
  const bytes = new Uint8Array(length);
  for (let i = 0; i < bytes.length; i += 1) bytes[i] = (seq * 19 + i * 11 + 5) & 0xff;
  return bytes;
}

async function admitAndEnqueue({ controller, mailbox, payload, priority, seq, admittedRows, rejectedRows }) {
  const before = controller.snapshot();
  const admission = controller.tryAdmit({ bytes: payload.byteLength, priority, label: `frame-${seq}`, metadata: { seq } });
  if (!admission.admitted) {
    const after = controller.snapshot();
    rejectedRows.push({ seq, priority, bytes: payload.byteLength, disposition: admission.disposition, reason: admission.reason, noMutation: admission.noMutation, before, after });
    return { admission, enqueue: null };
  }
  const enqueue = await mailbox.enqueue(payload, { seq, label: `frame-${seq}` });
  admittedRows.push({ seq, priority, bytes: payload.byteLength, checksum32: checksumFramePayload32(payload), admission, enqueue });
  return { admission, enqueue };
}

async function drainAndRelease({ controller, mailbox }) {
  const rows = [];
  for (;;) {
    const got = await mailbox.dequeue({ consumerId: 'admission-proof-consumer' });
    if (!got) break;
    await mailbox.ack(got.pendingId);
    const release = controller.release(got.seq === 900 ? 'unknown' : `admit:${got.seq + 1}`, { outcome: 'ack' });
    rows.push({ seq: got.seq, source: got.source, bytes: got.bytes, checksum32: checksumFramePayload32(got.payload), release });
  }
  return rows;
}

async function runProof() {
  const trace = new TraceLog();
  const rt = await boot({ admissionWatermarkProbe: true });
  const provider = createMemoryBlockStore({ name: 'rev0025-admission-spill-store', trace });
  const mailbox = createSpillFrameMailbox({ label: 'rev0025-admission-mailbox', memoryCapacityBytes: 48, maxFrameBytes: 128, provider, trace });
  const controller = createWatermarkAdmissionController({ label: 'rev0025-admission-controller', lowWatermarkBytes: 48, highWatermarkBytes: 120, hardLimitBytes: 180, trace });

  const admittedRows = [];
  const rejectedRows = [];

  for (let seq = 0; seq < 5; seq += 1) {
    const { admission } = await admitAndEnqueue({ controller, mailbox, payload: frame(seq), priority: 'background', seq, admittedRows, rejectedRows });
    assert.equal(admission.admitted, true, `background seq ${seq} should admit until high watermark is reached`);
  }

  const atHigh = controller.snapshot();
  const rejectedBackground = await admitAndEnqueue({ controller, mailbox, payload: frame(5), priority: 'background', seq: 5, admittedRows, rejectedRows });
  assert.equal(rejectedBackground.admission.disposition, 'rejected-watermark');
  const afterRejectedBackground = controller.snapshot();

  const critical = await admitAndEnqueue({ controller, mailbox, payload: frame(6, 32), priority: 'critical', seq: 6, admittedRows, rejectedRows });
  assert.equal(critical.admission.disposition, 'admitted-critical-bypass');

  const hardLimit = await admitAndEnqueue({ controller, mailbox, payload: frame(7, 64), priority: 'critical', seq: 7, admittedRows, rejectedRows });
  assert.equal(hardLimit.admission.disposition, 'rejected-hard-limit');

  controller.markProviderUnhealthy('scripted-provider-pressure');
  const providerReject = await admitAndEnqueue({ controller, mailbox, payload: frame(8, 16), priority: 'background', seq: 8, admittedRows, rejectedRows });
  assert.equal(providerReject.admission.disposition, 'rejected-provider-health');
  const providerBypass = await admitAndEnqueue({ controller, mailbox, payload: frame(9, 16), priority: 'critical', seq: 9, admittedRows, rejectedRows });
  assert.equal(providerBypass.admission.admitted, true);
  controller.markProviderHealthy('scripted-recovery');

  // Drain in FIFO order and release matching leases. The lease ids are monotonic in accepted seq order for this proof.
  const acceptedLeaseIds = admittedRows.map((row) => row.admission.leaseId);
  const drained = [];
  for (;;) {
    const got = await mailbox.dequeue({ consumerId: 'admission-proof-consumer' });
    if (!got) break;
    await mailbox.ack(got.pendingId);
    const leaseId = acceptedLeaseIds.shift();
    const release = controller.release(leaseId, { outcome: 'ack' });
    drained.push({ seq: got.seq, source: got.source, bytes: got.bytes, checksum32: checksumFramePayload32(got.payload), release });
  }
  const afterDrain = controller.snapshot();

  const postRecovery = await admitAndEnqueue({ controller, mailbox, payload: frame(10, 24), priority: 'background', seq: 10, admittedRows, rejectedRows });
  assert.equal(postRecovery.admission.admitted, true);
  const postRecoverySnapshot = controller.snapshot();
  const postRecoveryGot = await mailbox.dequeue({ consumerId: 'admission-proof-consumer' });
  await mailbox.ack(postRecoveryGot.pendingId);
  controller.release(postRecovery.admission.leaseId, { outcome: 'ack' });

  const finalSnapshot = controller.snapshot();
  const eventKinds = trace.kinds();
  const requiredEvents = [
    'admission:create',
    'admission:admit',
    'admission:high-watermark',
    'admission:reject',
    'admission:release',
    'admission:low-watermark',
    'admission:provider-unhealthy',
    'admission:provider-healthy',
    'mailbox:enqueue-memory',
    'mailbox:spill-write',
    'mailbox:ack'
  ];
  const missingEvents = requiredEvents.filter((kind) => !eventKinds.includes(kind));

  const rejectedBeforeAfterStable = rejectedRows.every((row) => row.noMutation && row.before.inFlightBytes === row.after.inFlightBytes && row.before.leaseCount === row.after.leaseCount);
  const expectedAcceptedSeqsBeforeRecovery = [0, 1, 2, 3, 4, 6, 9];
  const drainedBeforeRecoverySeqs = drained.map((row) => row.seq);

  const observations = {
    highWatermarkCrossed: atHigh.congested === true && atHigh.stats.highWatermarkCrossings === 1,
    backgroundRejectedDuringCongestion: rejectedBackground.admission.disposition === 'rejected-watermark',
    criticalBypassObserved: critical.admission.disposition === 'admitted-critical-bypass' && providerBypass.admission.disposition === 'admitted-critical-bypass',
    hardLimitRejected: hardLimit.admission.disposition === 'rejected-hard-limit',
    providerHealthRejectionObserved: providerReject.admission.disposition === 'rejected-provider-health',
    noMutationOnReject: rejectedBeforeAfterStable && afterRejectedBackground.inFlightBytes === atHigh.inFlightBytes,
    fifoOrderPreservedForAdmittedFrames: drainedBeforeRecoverySeqs.join(',') === expectedAcceptedSeqsBeforeRecovery.join(','),
    spillPathObserved: admittedRows.some((row) => row.enqueue?.disposition === 'spilled') && drained.some((row) => row.source === 'spill'),
    watermarkRecoveredAfterRelease: afterDrain.congested === false && afterDrain.inFlightBytes === 0 && afterDrain.stats.lowWatermarkRecoveries >= 1,
    postRecoveryBackgroundAdmitted: postRecovery.admission.disposition === 'admitted' && postRecoverySnapshot.congested === false,
    finalEmptyAndRecovered: finalSnapshot.inFlightBytes === 0 && finalSnapshot.leaseCount === 0 && finalSnapshot.congested === false,
    traceHasRequiredEvents: missingEvents.length === 0
  };
  for (const [key, value] of Object.entries(observations)) assert.equal(value, true, key);

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    proof_id: 'ipc:admission-watermark-proof',
    status: 'passed',
    generatedAt: new Date().toISOString(),
    observations,
    acceptedCount: admittedRows.length,
    rejectedCount: rejectedRows.length,
    drainedCount: drained.length,
    admittedRows: admittedRows.map((row) => ({ seq: row.seq, priority: row.priority, bytes: row.bytes, admissionDisposition: row.admission.disposition, leaseId: row.admission.leaseId, enqueueDisposition: row.enqueue.disposition, source: row.enqueue.source ?? row.enqueue.disposition })),
    rejectedRows: rejectedRows.map((row) => ({ seq: row.seq, priority: row.priority, bytes: row.bytes, disposition: row.disposition, reason: row.reason, noMutation: row.noMutation })),
    drained,
    snapshots: { atHigh, afterRejectedBackground, afterDrain, postRecoverySnapshot, finalSnapshot, mailbox: mailbox.snapshot() },
    requiredEventKinds: requiredEvents,
    eventKinds,
    missingEvents,
    trace: trace.snapshot(),
    runtimeExecutableProofs: rt.report.executableProofs,
    nonClaims: [
      'No adaptive latency-based concurrency controller proof.',
      'No browser Worker admission-control proof.',
      'No OPFS spill admission proof.',
      'No multi-producer fairness proof.',
      'No throughput or latency claim.',
      'No cross-browser conformance claim.'
    ]
  };
}

const args = parseArgs(process.argv.slice(2));
const report = await runProof();
if (args.json) {
  const out = args.json === true ? DEFAULT_ARTIFACT : args.json;
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, `${JSON.stringify(report, null, 2)}\n`);
}
console.log(JSON.stringify({ status: report.status, proof_id: report.proof_id, accepted: report.acceptedCount, rejected: report.rejectedCount }, null, 2));
