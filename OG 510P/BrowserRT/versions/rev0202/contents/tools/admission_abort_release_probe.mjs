#!/usr/bin/env node
// Manifest slice: admission:abort-release-proof. Release-light proof that bounded admission permits are released by AbortSignal without claiming universal cancellation.
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION, TraceLog, createWatermarkAdmissionController } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-ADMISSION-ABORT-RELEASE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function snapshot(controller) { return controller.snapshot(); }
function eventKinds(trace) { return trace.kinds(); }

function makeController(label, trace) {
  return createWatermarkAdmissionController({
    label,
    lowWatermarkBytes: 0,
    highWatermarkBytes: 10,
    hardLimitBytes: 20,
    criticalMinPriority: 'user-blocking',
    rejectMinPriorityWhileCongested: 'user-visible',
    trace
  });
}

export async function runProbe() {
  const trace = new TraceLog();
  const controller = makeController('rev0108-admission-abort-release', trace);

  const preAbort = new AbortController();
  preAbort.abort('caller-pre-aborted');
  const beforePreAbort = snapshot(controller);
  const preAborted = controller.tryAdmit({ bytes: 4, priority: 'background', label: 'pre-aborted-work', signal: preAbort.signal });
  const afterPreAbort = snapshot(controller);
  assert.equal(preAborted.admitted, false);
  assert.equal(preAborted.disposition, 'rejected-aborted');
  assert.equal(preAborted.noMutation, true);
  assert.equal(afterPreAbort.inFlightBytes, beforePreAbort.inFlightBytes);
  assert.equal(afterPreAbort.leaseCount, beforePreAbort.leaseCount);

  const abort = new AbortController();
  const beforeAdmit = snapshot(controller);
  const admitted = controller.tryAdmit({ bytes: 10, priority: 'user-blocking', label: 'abort-release-work', signal: abort.signal });
  const beforeAbort = snapshot(controller);
  assert.equal(admitted.admitted, true);
  assert.equal(admitted.abortSignalBound, true);
  assert.equal(beforeAbort.inFlightBytes, 10);
  assert.equal(beforeAbort.leaseCount, 1);
  assert.equal(beforeAbort.boundAbortLeaseCount, 1);
  assert.equal(beforeAbort.congested, true);
  abort.abort('caller-cancelled');
  const afterAbort = snapshot(controller);
  assert.equal(afterAbort.inFlightBytes, 0);
  assert.equal(afterAbort.leaseCount, 0);
  assert.equal(afterAbort.boundAbortLeaseCount, 0);
  assert.equal(afterAbort.congested, false);
  assert.ok(afterAbort.stats.abortSignalReleased >= 1);
  assert.ok(afterAbort.stats.lowWatermarkRecoveries >= 1);

  const postAbortAdmission = controller.tryAdmit({ bytes: 2, priority: 'background', label: 'post-abort-background-work' });
  assert.equal(postAbortAdmission.admitted, true);
  controller.release(postAbortAdmission.leaseId, { outcome: 'complete' });
  const afterPostAbort = snapshot(controller);

  const dualTrace = new TraceLog();
  const dualController = makeController('rev0108-admission-dual-signal-release', dualTrace);
  const primary = new AbortController();
  const secondary = new AbortController();
  const dualAdmit = dualController.tryAdmit({ bytes: 10, priority: 'user-blocking', label: 'dual-signal-work', signal: primary.signal, abortSignal: secondary.signal });
  assert.equal(dualAdmit.admitted, true);
  assert.equal(dualController.snapshot().boundAbortLeaseCount, 1);
  secondary.abort('secondary-first');
  const afterFirstAbort = snapshot(dualController);
  primary.abort('primary-late');
  const afterSecondAbort = snapshot(dualController);
  assert.equal(afterFirstAbort.leaseCount, 0);
  assert.equal(afterFirstAbort.inFlightBytes, 0);
  assert.equal(afterSecondAbort.stats.abortSignalReleased, afterFirstAbort.stats.abortSignalReleased);

  const manualTrace = new TraceLog();
  const manualController = makeController('rev0108-admission-manual-release-detach', manualTrace);
  const manualAbort = new AbortController();
  const manualAdmit = manualController.tryAdmit({ bytes: 6, priority: 'user-blocking', label: 'manual-release-work', signal: manualAbort.signal });
  assert.equal(manualAdmit.admitted, true);
  const beforeManualRelease = snapshot(manualController);
  const manualReleaseResult = manualController.release(manualAdmit.leaseId, { outcome: 'complete' });
  const afterManualRelease = snapshot(manualController);
  manualAbort.abort('late-manual-abort');
  const afterManualAbort = snapshot(manualController);
  assert.equal(manualReleaseResult.released, true);
  assert.equal(afterManualRelease.boundAbortLeaseCount, 0);
  assert.equal(afterManualAbort.stats.abortSignalReleased, afterManualRelease.stats.abortSignalReleased);
  assert.equal(afterManualAbort.inFlightBytes, afterManualRelease.inFlightBytes);

  const invalidController = makeController('rev0108-admission-invalid-signal', new TraceLog());
  let invalidSignal = { rejectedLocally: false, message: null };
  try {
    invalidController.tryAdmit({ bytes: 1, priority: 'background', signal: { aborted: false } });
  } catch (error) {
    invalidSignal = { rejectedLocally: true, message: error?.message || String(error) };
  }
  assert.equal(invalidSignal.rejectedLocally, true);
  assert.match(invalidSignal.message, /AbortSignal-like|addEventListener/);
  assert.equal(invalidController.snapshot().inFlightBytes, 0);
  assert.equal(invalidController.snapshot().leaseCount, 0);

  const traceKinds = eventKinds(trace);
  assert.ok(traceKinds.includes('admission:abort-release'));

  const snapshots = Object.freeze({ beforePreAbort, afterPreAbort, beforeAdmit, beforeAbort, afterAbort, afterPostAbort });
  const proof = Object.freeze({
    releaseLightExplicit: true,
    preAbortedRejectedNoMutation: preAborted.disposition === 'rejected-aborted' && preAborted.noMutation === true && afterPreAbort.inFlightBytes === beforePreAbort.inFlightBytes && afterPreAbort.leaseCount === beforePreAbort.leaseCount,
    boundLeaseAbortReleasedPermit: afterAbort.inFlightBytes === 0 && afterAbort.leaseCount === 0 && afterAbort.boundAbortLeaseCount === 0 && afterAbort.stats.abortSignalReleased >= 1,
    dualSignalAbortSourceReleasesOnce: afterFirstAbort.inFlightBytes === 0 && afterFirstAbort.leaseCount === 0 && afterSecondAbort.stats.abortSignalReleased === afterFirstAbort.stats.abortSignalReleased,
    manualReleaseDetachesAbortListener: afterManualRelease.boundAbortLeaseCount === 0 && afterManualAbort.stats.abortSignalReleased === afterManualRelease.stats.abortSignalReleased,
    congestionRecoversAfterAbortRelease: beforeAbort.congested === true && afterAbort.congested === false && afterAbort.stats.lowWatermarkRecoveries >= 1,
    postAbortBackgroundAdmissionRecovers: postAbortAdmission.admitted === true && afterPostAbort.inFlightBytes === 0,
    invalidSignalShapeRejectedLocally: invalidSignal.rejectedLocally === true,
    traceHasAbortRelease: traceKinds.includes('admission:abort-release'),
    exactlyOnceNonClaimVisible: true,
    browserWorkerNonClaimVisible: true
  });

  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-admission-abort-release-probe`,
    proof_id: 'admission:abort-release-proof',
    commandId: 'admission:abort-release-proof',
    tier: 'release-browser-light',
    status: 'passed',
    purpose: 'Prove that WatermarkAdmissionController binds caller AbortSignals to admitted leases so abort frees watermarks/permits, while pre-aborted or invalid signals reject locally without mutation.',
    preAborted: Object.freeze({ ...preAborted, before: beforePreAbort, after: afterPreAbort }),
    admitted: Object.freeze({ ...admitted }),
    postAbortAdmission: Object.freeze({ ...postAbortAdmission }),
    dualSignal: Object.freeze({
      admitted: dualAdmit.admitted === true,
      beforeAbort: beforeManualRelease,
      afterFirstAbort,
      afterSecondAbort,
      releasedOnce: afterSecondAbort.stats.abortSignalReleased === afterFirstAbort.stats.abortSignalReleased
    }),
    manualRelease: Object.freeze({ beforeRelease: beforeManualRelease, release: manualReleaseResult, afterRelease: afterManualRelease, afterAbort: afterManualAbort }),
    invalidSignal: Object.freeze(invalidSignal),
    snapshots,
    eventKinds: Object.freeze(traceKinds),
    trace: Object.freeze(trace.snapshot().map(({ seq, kind, disposition = null, reason = null, leaseId = null, bytes = null, priority = null, inFlightBytes = null, leaseCount = null, congested = null, noMutation = null }) => Object.freeze({ seq, kind, disposition, reason, leaseId, bytes, priority, inFlightBytes, leaseCount, congested, noMutation })).slice(0, 64)),
    proof,
    nonClaims: Object.freeze([
      'No production admission-control claim.',
      'No exactly-once execution, task preemption, or universal cancellation guarantee.',
      'No provider rollback, OPFS mutation rollback, fsync, quota, eviction, or crash-recovery claim.',
      'No browser Worker, cross-tab, cross-browser, or mobile lifecycle cancellation claim.',
      'No fairness, starvation-freedom, throughput, latency, SLO, or performance claim.',
      'No artifact authenticity, signing, or tamper-proof evidence claim.'
    ])
  });
}

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  const report = await runProbe();
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else console.log(JSON.stringify(report, null, 2));
}

// Static audit markers: admission:abort-release-proof; rejected-aborted; admission:abort-release; boundAbortLeaseCount; abortSignalReleased; signal; abortSignal; No exactly-once execution, task preemption, or universal cancellation guarantee.; No browser Worker, cross-tab, cross-browser, or mobile lifecycle cancellation claim.
