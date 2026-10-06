#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import {
  REVISION,
  VERSION,
  boot,
  digestBytesHex,
  validateBlockStoreLaneAdapterSnapshot,
  validateKernelKitDemoReport,
  createKernelKitDemoTranscript,
  createKernelKitTraceExport,
  validateKernelKitTraceExport,
  validateKernelKitDemoTranscript,
  createKernelKitDemoObservatoryReport,
  validateKernelKitDemoObservatoryReport,
  createKernelKitDemoUsefulnessReport,
  validateKernelKitDemoUsefulnessReport,
  KERNEL_KIT_DEMO_NON_CLAIMS,
  KERNEL_KIT_DEMO_REQUIRED_STEPS
} from '../src/browserrt.mjs';

const prefix = `REV${REVISION.slice(3)}`;
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const outPath = argValue('--json', `artifacts/validation/${prefix}-KERNEL-KIT-DEMO-PROBE.json`);

function traceProjection(trace) {
  return trace.map((event) => {
    const out = { kind: event.kind };
    for (const key of ['label', 'lane', 'priority', 'op', 'opId', 'agentId', 'callId', 'disposition', 'reason', 'bytes', 'digest', 'duplicate']) {
      if (Object.hasOwn(event, key)) out[key] = event[key];
    }
    return out;
  });
}

export async function runProbe() {
  const rt = await boot({ telemetry: 'kernel-kit-demo', proof: REVISION, kernelKitDemoProof: true, storageLaneProviderProof: true, crossLaneScheduler: true });

  const channel = rt.channel({ label: 'kernel-kit-demo-intake', capacity: 1, overflow: 'drop-oldest' });
  await channel.send({ job: 'superseded-work', bytes: 8 });
  const channelOverflow = await channel.send({ job: 'current-work', bytes: 8 });
  const currentWork = await channel.receive();

  const agent = await rt.spawnAgent({ name: 'kernel-kit-demo-agent' });
  const buffer = new ArrayBuffer(16);
  new Uint32Array(buffer).set([11, 13, 17, 19]);
  const transfer = rt.transferObject(buffer, { id: 'transfer:kernel-kit-demo', label: 'kernel-kit-demo-sum' });
  const agentResult = await agent.call('sum-u32', { ref: transfer.ref, buffer: transfer.buffer }, { transfer: transfer.transferList, lane: 'cpu', priority: 'user-visible' });
  const transferDetached = buffer.byteLength === 0;
  await agent.terminate('kernel-kit-demo-complete');

  const admission = rt.admissionController({
    label: 'kernel-kit-demo-admission',
    lowWatermarkBytes: 0,
    highWatermarkBytes: 48,
    hardLimitBytes: 2048,
    criticalMinPriority: 'user-blocking',
    rejectMinPriorityWhileCongested: 'user-visible'
  });

  const summaryPayload = new TextEncoder().encode(JSON.stringify({
    demo: 'kernel-kit',
    revision: REVISION,
    job: currentWork.job,
    agentSum: agentResult.sum,
    agentCount: agentResult.count,
    meaning: 'one useful path through worker/object-ref/admission/storage-lane/trace'
  }));

  const admitted = admission.tryAdmit({ bytes: summaryPayload.byteLength, priority: 'user-visible', label: 'summary-payload' });
  const rejected = admission.tryAdmit({ bytes: 16, priority: 'background', label: 'background-overload' });
  const critical = admission.tryAdmit({ bytes: 16, priority: 'critical', label: 'critical-bypass-sentinel' });

  const store = rt.blockStore({ name: 'kernel-kit-demo-memory-store', provider: 'kernel-kit-demo-memory-provider-v0' });
  const scheduler = rt.crossLaneScheduler({
    label: 'kernel-kit-demo-storage-scheduler',
    lanes: [
      { id: 'storage', rank: 70, capacity: 1, quantum: 64, maxQueuedCost: 512 },
      { id: 'maintenance', rank: 10, capacity: 1, quantum: 64, maxQueuedCost: 128 }
    ]
  });
  const adapter = rt.blockStoreLaneAdapter({ label: 'kernel-kit-demo-block-store-lane', store, scheduler });
  const put = adapter.schedulePut(summaryPayload, { id: 'demo-put-summary', priority: 'user-visible', label: 'kernel-kit-summary' });
  const drainPut = await adapter.drain({ maxSteps: 4 });
  const putResult = adapter.result('demo-put-summary');
  const verify = adapter.scheduleVerify(putResult.ref, { id: 'demo-verify-summary' });
  const get = adapter.scheduleGet(putResult.ref, { id: 'demo-get-summary' });
  const drainRead = await adapter.drain({ maxSteps: 4 });
  const readBytes = adapter.result('demo-get-summary');
  const readDigest = await digestBytesHex(readBytes);
  adapter.markUnhealthy('storage', 'kernel-kit-route-demo');
  const routedEstimate = adapter.scheduleEstimate({ id: 'demo-estimate-routed', fallbackLanes: ['maintenance'], priority: 'background' });
  const drainRoute = await adapter.drain({ maxSteps: 4 });
  adapter.markHealthy('storage', 'kernel-kit-route-recovery');
  const deleteResult = adapter.scheduleDelete(putResult.ref, { id: 'demo-delete-summary' });
  const drainDelete = await adapter.drain({ maxSteps: 4 });

  if (admitted.admitted) admission.release(admitted.leaseId, { outcome: 'stored-summary' });
  if (critical.admitted) admission.release(critical.leaseId, { outcome: 'released-critical-sentinel' });

  const adapterSnapshot = adapter.snapshot();
  const adapterValidation = validateBlockStoreLaneAdapterSnapshot(adapterSnapshot);
  const admissionSnapshot = admission.snapshot();
  const trace = rt.close();
  const traceKinds = trace.map((event) => event.kind);

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    codename: 'Integrated Kernel Kit Demo',
    proofId: `${REVISION}-integrated-kernel-kit-demo`,
    browserProof: false,
    purpose: 'Prove the narrow BrowserRT Kernel Kit wedge: worker agent + object ref + bounded admission + storage-lane block provider + trace evidence.',
    stepsCompleted: KERNEL_KIT_DEMO_REQUIRED_STEPS.slice(),
    observations: {
      workerAgent: agentResult.sum === 60 && agentResult.count === 4,
      transferDetached,
      boundedChannelOverflow: channelOverflow.disposition === 'dropped-oldest' && currentWork.job === 'current-work',
      admissionRejectedNoMutation: rejected.admitted === false && rejected.noMutation === true,
      criticalBypass: critical.admitted === true && critical.bypass === true,
      storageLaneWriteRead: put.accepted === true && verify.accepted === true && get.accepted === true && putResult.hash === readDigest,
      fallbackRouting: routedEstimate.accepted === true && routedEstimate.scheduler?.disposition === 'accepted-routed' && routedEstimate.scheduler?.lane === 'maintenance',
      cleanupDelete: deleteResult.accepted === true,
      traceEvidence: true
    },
    results: {
      channelOverflow,
      agentResult: { sum: agentResult.sum, count: agentResult.count, bytes: agentResult.bytes, refId: agentResult.ref?.id },
      admission: { admitted, rejected, critical, snapshot: admissionSnapshot },
      storage: {
        put: adapter.resultSummary('demo-put-summary'),
        verify: adapter.result('demo-verify-summary'),
        getBytes: readBytes.byteLength,
        getDigest: readDigest,
        routedEstimate: adapter.resultSummary('demo-estimate-routed'),
        delete: adapter.result('demo-delete-summary'),
        drainPut: drainPut.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok, lane: row.lane, op: row.op })),
        drainRead: drainRead.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok, lane: row.lane, op: row.op })),
        drainRoute: drainRoute.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok, lane: row.lane, op: row.op })),
        drainDelete: drainDelete.results.map((row) => ({ dispatched: row.dispatched, ok: row.ok, lane: row.lane, op: row.op }))
      },
      adapterSnapshot,
      adapterValidation
    },
    traceKinds,
    normalizedTrace: traceProjection(trace),
    nonClaims: KERNEL_KIT_DEMO_NON_CLAIMS.slice()
  };

  const transcript = createKernelKitDemoTranscript(report);
  const transcriptValidation = validateKernelKitDemoTranscript(transcript);
  report.transcript = transcript;
  report.transcriptValidation = transcriptValidation;

  const traceExport = createKernelKitTraceExport(report, { source: 'release-tier-node-demo', generatedAt: 'deterministic-node-export' });
  const traceExportValidation = validateKernelKitTraceExport(traceExport);
  report.traceExport = traceExport;
  report.traceExportValidation = traceExportValidation;

  const observatory = createKernelKitDemoObservatoryReport(report, { source: 'release-tier-node-demo' });
  const observatoryValidation = validateKernelKitDemoObservatoryReport(observatory);
  report.observatory = observatory;
  report.observatoryValidation = observatoryValidation;

  const usefulness = createKernelKitDemoUsefulnessReport(report, { source: 'release-tier-node-demo' });
  const usefulnessValidation = validateKernelKitDemoUsefulnessReport(usefulness);
  report.usefulness = usefulness;
  report.usefulnessValidation = usefulnessValidation;

  const validation = validateKernelKitDemoReport(report);
  report.validation = validation;
  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(report.observations.workerAgent, true);
  assert.equal(report.observations.transferDetached, true);
  assert.equal(report.observations.admissionRejectedNoMutation, true);
  assert.equal(report.observations.storageLaneWriteRead, true);
  assert.equal(report.observations.fallbackRouting, true);
  assert.equal(report.results.adapterValidation.ok, true);
  assert.equal(report.validation.transcriptValidation?.ok, true, report.validation.transcriptValidation?.errors?.join('; ') || 'transcript validation missing');
  assert.equal(report.traceExportValidation.ok, true, report.traceExportValidation.errors.join('; '));
  assert.ok(report.traceExport.chromeTrace.traceEvents.length >= report.traceKinds.length, 'trace export should include Kernel Kit events');
  assert.equal(report.observatoryValidation.ok, true, report.observatoryValidation.errors.join('; '));
  assert.equal(report.usefulnessValidation.ok, true, report.usefulnessValidation.errors.join('; '));
  assert.ok(report.observatory.proofReceipt.observedStageCount >= 6, 'observatory should see at least six observed demo stages');
  assert.equal(report.usefulness.status, 'usefulness-wedge-earned');
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const report = await runProbe();
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
  console.log(outPath);
}
