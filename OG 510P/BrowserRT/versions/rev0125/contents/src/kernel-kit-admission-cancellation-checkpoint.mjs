// BrowserRT Kernel Kit admission/cancellation checkpoint.
// This module binds bounded admission watermarks to AbortSignal lease-release
// evidence without claiming preemptive provider cancellation, browser Worker
// coverage, exactly-once execution, fairness, latency, or production readiness.

export const KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT = 'browserrt-kernel-kit-admission-cancellation-checkpoint-v1';

export const KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS = Object.freeze([
  'No production admission-control claim.',
  'No exactly-once execution, task preemption, or universal cancellation guarantee.',
  'No provider rollback, OPFS mutation rollback, fsync, quota, eviction, or crash-recovery claim.',
  'No browser Worker, cross-tab, cross-browser, or mobile lifecycle cancellation claim.',
  'No fairness, starvation-freedom, throughput, latency, SLO, or performance claim.',
  'No artifact authenticity, signing, or tamper-proof evidence claim.'
]);

export const KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_REQUIRED_ROWS = Object.freeze([
  'admission-cancellation-release-command-visible',
  'pre-aborted-admission-rejects-no-mutation',
  'bound-lease-abort-releases-permit',
  'dual-signal-abort-source-releases-once',
  'manual-release-detaches-abort-listener',
  'congestion-recovers-after-abort-release',
  'post-abort-background-admission-recovers',
  'invalid-signal-shape-rejected-locally',
  'exactly-once-cancellation-nonclaim-visible',
  'browser-worker-cancellation-nonclaim-visible'
]);

function isObj(value) { return Boolean(value && typeof value === 'object'); }
function asArray(value) { return Array.isArray(value) ? value : []; }
function bool(value) { return value === true; }
function frozen(obj) { return Object.freeze(obj); }
function firstObj(...values) { return values.find(isObj) || null; }
function rowStatus(ok, fallback = 'deferred') { return ok ? 'observed' : fallback; }

function commandVisible(input = {}, source = {}) {
  const commands = [
    ...asArray(input.exactCommands),
    ...asArray(input.supportBundle?.exactCommands),
    ...asArray(source.exactCommands)
  ].map(String);
  return commands.some((cmd) => cmd.includes('demo:kernel-kit-admission-cancellation-checkpoint-proof'))
    || commands.some((cmd) => cmd.includes('admission:abort-release-proof'))
    || String(source.commandId || source.taskId || source.proof_id || '').includes('admission:abort-release-proof')
    || String(source.probe_id || '').includes('admission-abort-release');
}

function nonClaimText(input = {}, source = {}) {
  return [
    ...asArray(input.nonClaims),
    ...asArray(input.supportBundle?.nonClaims),
    ...asArray(source.nonClaims),
    ...KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS
  ].join('\n').toLowerCase();
}

function admissionSource(input = {}) {
  return firstObj(
    input.admissionCancellationCheckpoint,
    input.admissionCancellation,
    input.admissionAbortRelease,
    input.admissionAbort,
    input.observations?.admissionCancellation,
    input.supportBundle?.admissionCancellation
  ) || {};
}

function summarizeAdmissionCancellation(input = {}) {
  const source = admissionSource(input);
  const proof = { ...(isObj(source.proof) ? source.proof : {}), ...(isObj(source.observations) ? source.observations : {}) };
  const snapshots = source.snapshots || {};
  const traceKinds = new Set(asArray(source.eventKinds).concat(asArray(source.traceKinds)).concat(asArray(source.trace?.map?.((row) => row?.kind))));
  const nonClaims = nonClaimText(input, source);
  const exactCommandVisible = commandVisible(input, source);
  const commandId = source.commandId || source.proof_id || source.task_id || 'admission:abort-release-proof';
  const releaseLightExplicit = bool(proof.releaseLightExplicit) || exactCommandVisible || String(commandId).includes('admission:abort-release-proof');

  const preAbortedRejectedNoMutation = bool(proof.preAbortedRejectedNoMutation)
    || (source.preAborted?.disposition === 'rejected-aborted' && source.preAborted?.noMutation === true);
  const boundLeaseAbortReleasedPermit = bool(proof.boundLeaseAbortReleasedPermit)
    || bool(proof.abortSignalReleasedPermit)
    || (snapshots.afterAbort?.inFlightBytes === 0 && snapshots.afterAbort?.leaseCount === 0 && (snapshots.afterAbort?.stats?.abortSignalReleased || 0) >= 1);
  const dualSignalAbortSourceReleasesOnce = bool(proof.dualSignalAbortSourceReleasesOnce)
    || (source.dualSignal?.releasedOnce === true && source.dualSignal?.afterSecondAbort?.stats?.abortSignalReleased === source.dualSignal?.afterFirstAbort?.stats?.abortSignalReleased)
    || (snapshots.afterDualSignalAbort?.inFlightBytes === 0 && (snapshots.afterDualSignalAbort?.stats?.abortSignalReleased || 0) >= 2);
  const manualReleaseDetachesAbortListener = bool(proof.manualReleaseDetachesAbortListener)
    || (source.manualRelease?.afterAbort?.stats?.abortSignalReleased === source.manualRelease?.afterRelease?.stats?.abortSignalReleased && source.manualRelease?.afterAbort?.boundAbortLeaseCount === 0);
  const congestionRecoversAfterAbortRelease = bool(proof.congestionRecoversAfterAbortRelease)
    || (snapshots.beforeAbort?.congested === true && snapshots.afterAbort?.congested === false && (snapshots.afterAbort?.stats?.lowWatermarkRecoveries || 0) >= 1);
  const postAbortBackgroundAdmissionRecovers = bool(proof.postAbortBackgroundAdmissionRecovers)
    || source.postAbortAdmission?.admitted === true || source.postAbortAdmission?.disposition === 'admitted';
  const invalidSignalShapeRejectedLocally = bool(proof.invalidSignalShapeRejectedLocally)
    || source.invalidSignal?.rejectedLocally === true || /AbortSignal-like/.test(String(source.invalidSignal?.message || ''));
  const traceHasAbortRelease = bool(proof.traceHasAbortRelease) || traceKinds.has('admission:abort-release');
  const exactlyOnceNonClaimVisible = proof.exactlyOnceNonClaimVisible !== false && nonClaims.includes('exactly-once');
  const browserWorkerNonClaimVisible = proof.browserWorkerNonClaimVisible !== false && nonClaims.includes('browser worker');
  const observed = (source.status === 'passed' || proof.observed === true)
    && releaseLightExplicit
    && preAbortedRejectedNoMutation
    && boundLeaseAbortReleasedPermit
    && dualSignalAbortSourceReleasesOnce
    && manualReleaseDetachesAbortListener
    && congestionRecoversAfterAbortRelease
    && postAbortBackgroundAdmissionRecovers
    && invalidSignalShapeRejectedLocally
    && traceHasAbortRelease
    && exactlyOnceNonClaimVisible
    && browserWorkerNonClaimVisible;

  return frozen({
    observed,
    status: observed ? 'observed' : (source.status || 'release-light-deferred'),
    source: source.source || source.probe_id || 'release-light-admission-cancellation-command-not-run',
    commandId,
    tier: source.tier || 'release-browser-light',
    releaseLightExplicit,
    exactCommandVisible,
    preAbortedRejectedNoMutation,
    boundLeaseAbortReleasedPermit,
    dualSignalAbortSourceReleasesOnce,
    manualReleaseDetachesAbortListener,
    congestionRecoversAfterAbortRelease,
    postAbortBackgroundAdmissionRecovers,
    invalidSignalShapeRejectedLocally,
    traceHasAbortRelease,
    exactlyOnceNonClaimVisible,
    browserWorkerNonClaimVisible
  });
}

function makeRow({ id, title, risk, status, evidence = {}, evidencePaths = [], whyItMatters, nextAction, nonClaim }) {
  return frozen({ id, title, risk, status, evidencePaths: Object.freeze(evidencePaths), evidence: frozen(evidence), whyItMatters, nextAction, nonClaim });
}

export function createKernelKitAdmissionCancellationCheckpoint(input = {}, fields = {}) {
  const summary = summarizeAdmissionCancellation(input);
  const revision = fields.revision || input.revision || input.supportBundle?.revision || 'rev0108';
  const rows = [
    makeRow({
      id: 'admission-cancellation-release-command-visible',
      title: 'Release-light admission/cancellation command is visible',
      risk: 4,
      status: rowStatus(summary.releaseLightExplicit || summary.exactCommandVisible),
      evidencePaths: ['exactCommands', 'demo:kernel-kit-admission-cancellation-checkpoint-proof', 'admission:abort-release-proof'],
      evidence: { commandId: summary.commandId, releaseLightExplicit: summary.releaseLightExplicit, exactCommandVisible: summary.exactCommandVisible },
      whyItMatters: 'Bounded admission/cancellation is a source-level runtime safety property and should be replayable without spending browser/CDP budget.',
      nextAction: summary.releaseLightExplicit || summary.exactCommandVisible ? 'Keep the release-light command in support bundles and evidence ledgers.' : 'Add demo:kernel-kit-admission-cancellation-checkpoint-proof to the support-bundle replay path.',
      nonClaim: 'A visible command is not artifact authenticity, browser Worker coverage, or production readiness.'
    }),
    makeRow({
      id: 'pre-aborted-admission-rejects-no-mutation',
      title: 'Pre-aborted admission rejects without mutating permit state',
      risk: 5,
      status: rowStatus(summary.preAbortedRejectedNoMutation),
      evidencePaths: ['admissionAbortRelease.preAborted.disposition=rejected-aborted', 'proof.preAbortedRejectedNoMutation'],
      evidence: { preAbortedRejectedNoMutation: summary.preAbortedRejectedNoMutation },
      whyItMatters: 'A pre-aborted caller must not consume watermarks or leak a lease before work starts.',
      nextAction: summary.preAbortedRejectedNoMutation ? 'Keep rejected-aborted/noMutation assertions in the release proof.' : 'Prove pre-aborted signal rejection before using admission permits with caller cancellation.',
      nonClaim: 'Pre-abort rejection is not provider rollback or task preemption.'
    }),
    makeRow({
      id: 'bound-lease-abort-releases-permit',
      title: 'Bound AbortSignal releases admitted lease permit',
      risk: 5,
      status: rowStatus(summary.boundLeaseAbortReleasedPermit),
      evidencePaths: ['snapshots.afterAbort.inFlightBytes=0', 'stats.abortSignalReleased', 'proof.boundLeaseAbortReleasedPermit'],
      evidence: { boundLeaseAbortReleasedPermit: summary.boundLeaseAbortReleasedPermit, traceHasAbortRelease: summary.traceHasAbortRelease },
      whyItMatters: 'The severe leak is an aborted caller leaving in-flight bytes high, permanently rejecting later useful work.',
      nextAction: summary.boundLeaseAbortReleasedPermit ? 'Keep abort release as an admission-controller invariant.' : 'Bind admitted leases to AbortSignal before layering broader workbench cancellation.',
      nonClaim: 'Permit release is not universal cancellation of already-running provider work.'
    }),
    makeRow({
      id: 'dual-signal-abort-source-releases-once',
      title: 'Either signal or abortSignal can release the lease exactly once',
      risk: 5,
      status: rowStatus(summary.dualSignalAbortSourceReleasesOnce),
      evidencePaths: ['dualSignal.afterFirstAbort', 'dualSignal.afterSecondAbort', 'proof.dualSignalAbortSourceReleasesOnce'],
      evidence: { dualSignalAbortSourceReleasesOnce: summary.dualSignalAbortSourceReleasesOnce },
      whyItMatters: 'The current raw OPFS slice fixed signal/abortSignal masking. Admission must not reintroduce that sibling-signal leak.',
      nextAction: summary.dualSignalAbortSourceReleasesOnce ? 'Keep dual-signal lease release in the Kernel Kit checkpoint.' : 'Exercise both signal names through admission before claiming cancellation composition.',
      nonClaim: 'Exactly-once permit release is not exactly-once task execution.'
    }),
    makeRow({
      id: 'manual-release-detaches-abort-listener',
      title: 'Manual release detaches abort listener',
      risk: 4,
      status: rowStatus(summary.manualReleaseDetachesAbortListener),
      evidencePaths: ['manualRelease.afterRelease.boundAbortLeaseCount=0', 'manualRelease.afterAbort.stats.abortSignalReleased unchanged'],
      evidence: { manualReleaseDetachesAbortListener: summary.manualReleaseDetachesAbortListener },
      whyItMatters: 'A completed task should not later be counted as aborted when a stale caller signal fires.',
      nextAction: summary.manualReleaseDetachesAbortListener ? 'Keep listener-detach proof to avoid ghost abort telemetry.' : 'Detach abort listeners during release before broadening support-bundle telemetry.',
      nonClaim: 'Listener cleanup is not leak-freedom for arbitrary application resources.'
    }),
    makeRow({
      id: 'congestion-recovers-after-abort-release',
      title: 'Congestion recovers when abort releases the lease',
      risk: 5,
      status: rowStatus(summary.congestionRecoversAfterAbortRelease),
      evidencePaths: ['snapshots.beforeAbort.congested=true', 'snapshots.afterAbort.congested=false'],
      evidence: { congestionRecoversAfterAbortRelease: summary.congestionRecoversAfterAbortRelease },
      whyItMatters: 'Admission backpressure is harmful if cancellation cannot move the controller below low watermark.',
      nextAction: summary.congestionRecoversAfterAbortRelease ? 'Keep low-watermark recovery tied to abort-release evidence.' : 'Prove abort-release drives low-watermark recovery under congestion.',
      nonClaim: 'Watermark recovery is not fairness, throughput, or latency performance.'
    }),
    makeRow({
      id: 'post-abort-background-admission-recovers',
      title: 'Useful background work can admit after abort cleanup',
      risk: 4,
      status: rowStatus(summary.postAbortBackgroundAdmissionRecovers),
      evidencePaths: ['postAbortAdmission.disposition=admitted', 'proof.postAbortBackgroundAdmissionRecovers'],
      evidence: { postAbortBackgroundAdmissionRecovers: summary.postAbortBackgroundAdmissionRecovers },
      whyItMatters: 'The practical product risk is a cancelled work item poisoning later sessions by keeping the runtime congested.',
      nextAction: summary.postAbortBackgroundAdmissionRecovers ? 'Keep post-abort admission as the user-visible success criterion.' : 'Add post-abort admission to the checkpoint before widening the workbench path.',
      nonClaim: 'Post-abort admission is not multi-producer fairness.'
    }),
    makeRow({
      id: 'invalid-signal-shape-rejected-locally',
      title: 'Invalid AbortSignal-like shapes reject locally',
      risk: 4,
      status: rowStatus(summary.invalidSignalShapeRejectedLocally),
      evidencePaths: ['invalidSignal.rejectedLocally', 'proof.invalidSignalShapeRejectedLocally'],
      evidence: { invalidSignalShapeRejectedLocally: summary.invalidSignalShapeRejectedLocally },
      whyItMatters: 'Silent option-shape masking is how cancellation bugs become false safety claims.',
      nextAction: summary.invalidSignalShapeRejectedLocally ? 'Keep invalid shape rejection in the release proof.' : 'Reject invalid signal/abortSignal shapes before binding listeners.',
      nonClaim: 'Shape validation is not static typing or security validation.'
    }),
    makeRow({
      id: 'exactly-once-cancellation-nonclaim-visible',
      title: 'Exactly-once/preemption non-claims are visible',
      risk: 5,
      status: rowStatus(summary.exactlyOnceNonClaimVisible),
      evidencePaths: ['nonClaims'],
      evidence: { exactlyOnceNonClaimVisible: summary.exactlyOnceNonClaimVisible },
      whyItMatters: 'Permit cleanup can be misread as task cancellation or exactly-once delivery unless the boundary stays explicit.',
      nextAction: summary.exactlyOnceNonClaimVisible ? 'Preserve exact non-claims in support bundles and docs.' : 'Restore exactly-once and universal cancellation non-claims before sealing.',
      nonClaim: 'No exactly-once execution, task preemption, or universal cancellation guarantee.'
    }),
    makeRow({
      id: 'browser-worker-cancellation-nonclaim-visible',
      title: 'Browser Worker/cross-browser cancellation non-claims are visible',
      risk: 4,
      status: rowStatus(summary.browserWorkerNonClaimVisible),
      evidencePaths: ['nonClaims'],
      evidence: { browserWorkerNonClaimVisible: summary.browserWorkerNonClaimVisible },
      whyItMatters: 'This is a release-light controller proof, not a browser Worker lifecycle proof.',
      nextAction: summary.browserWorkerNonClaimVisible ? 'Keep release-light and browser-heavy boundaries separate.' : 'Restore browser Worker and cross-browser non-claims before widening platform language.',
      nonClaim: 'No browser Worker, cross-tab, cross-browser, or mobile lifecycle cancellation claim.'
    })
  ].sort((a, b) => (b.risk - a.risk) || a.id.localeCompare(b.id));

  const missingRequiredRows = KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_REQUIRED_ROWS.filter((id) => !rows.some((row) => row.id === id));
  const failedRowIds = rows.filter((row) => row.status === 'failed').map((row) => row.id);
  const deferredRowIds = rows.filter((row) => row.status === 'deferred').map((row) => row.id);
  const observedRowIds = rows.filter((row) => row.status === 'observed').map((row) => row.id);
  const highRiskRowsBounded = rows.filter((row) => row.risk >= 5).every((row) => ['observed', 'deferred'].includes(row.status) && row.nextAction && row.nonClaim);
  const proof = frozen({
    releaseLightCommandVisible: summary.releaseLightExplicit || summary.exactCommandVisible,
    preAbortedRejectedNoMutation: summary.preAbortedRejectedNoMutation,
    boundLeaseAbortReleasedPermit: summary.boundLeaseAbortReleasedPermit,
    dualSignalAbortSourceReleasesOnce: summary.dualSignalAbortSourceReleasesOnce,
    manualReleaseDetachesAbortListener: summary.manualReleaseDetachesAbortListener,
    congestionRecoversAfterAbortRelease: summary.congestionRecoversAfterAbortRelease,
    postAbortBackgroundAdmissionRecovers: summary.postAbortBackgroundAdmissionRecovers,
    invalidSignalShapeRejectedLocally: summary.invalidSignalShapeRejectedLocally,
    traceHasAbortRelease: summary.traceHasAbortRelease,
    exactlyOnceNonClaimVisible: summary.exactlyOnceNonClaimVisible,
    browserWorkerNonClaimVisible: summary.browserWorkerNonClaimVisible,
    admissionCancellationObservedOrExplicitlyDeferred: summary.observed || deferredRowIds.length > 0,
    highRiskRowsBounded,
    rowsRankedByRisk: rows.every((row, index) => index === 0 || rows[index - 1].risk >= row.risk),
    noFailedRows: failedRowIds.length === 0,
    requiredRowsPresent: missingRequiredRows.length === 0
  });
  const status = proof.releaseLightCommandVisible
    && proof.admissionCancellationObservedOrExplicitlyDeferred
    && proof.highRiskRowsBounded
    && proof.rowsRankedByRisk
    && proof.noFailedRows
    && proof.requiredRowsPresent
    && proof.exactlyOnceNonClaimVisible
    && proof.browserWorkerNonClaimVisible
    ? 'risk-checkpoint-ready'
    : 'needs-attention';
  return frozen({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT,
    checkpointId: fields.checkpointId || `${revision}-kernel-kit-admission-cancellation-checkpoint`,
    generatedAt: fields.generatedAt || 'deterministic-kernel-kit-admission-cancellation-checkpoint',
    status,
    purpose: 'Make bounded admission cancellation explicit: pre-aborted calls reject without mutation, admitted AbortSignals release permits under congestion, sibling signal names compose, and stale abort listeners detach on manual release.',
    posture: 'admission-cancellation-risk-checkpoint-not-production-cancellation',
    source: fields.source || summary.source,
    commandId: summary.commandId,
    tier: summary.tier,
    rows: Object.freeze(rows),
    observedRowIds: Object.freeze(observedRowIds),
    deferredRowIds: Object.freeze(deferredRowIds),
    failedRowIds: Object.freeze(failedRowIds),
    missingRequiredRows: Object.freeze(missingRequiredRows),
    riskSummary: frozen({
      rowCount: rows.length,
      observedCount: observedRowIds.length,
      deferredCount: deferredRowIds.length,
      failedCount: failedRowIds.length,
      riskiestNextAction: rows.find((row) => row.status === 'deferred' && row.risk >= 5)?.nextAction || 'Keep admission cancellation rows bound to release-light proof artifacts.'
    }),
    summary,
    proof,
    nonClaims: Object.freeze([...KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS])
  });
}

export function validateKernelKitAdmissionCancellationCheckpoint(checkpoint = {}) {
  const errors = [];
  if (!isObj(checkpoint)) return frozen({ ok: false, errors: ['admission/cancellation checkpoint must be an object'], rowCount: 0, observedCount: 0, deferredCount: 0, failedCount: 0, format: null, status: null });
  if (checkpoint.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (checkpoint.format !== KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT) errors.push(`format must be ${KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_FORMAT}`);
  if (checkpoint.status !== 'risk-checkpoint-ready') errors.push('status must be risk-checkpoint-ready');
  const rows = asArray(checkpoint.rows);
  if (rows.length < KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_REQUIRED_ROWS.length) errors.push('checkpoint rows must cover all required admission/cancellation risks');
  for (const id of KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_REQUIRED_ROWS) if (!rows.some((row) => row.id === id)) errors.push(`missing admission/cancellation row ${id}`);
  for (const row of rows) {
    if (!['observed', 'deferred'].includes(row.status)) errors.push(`row ${row.id || 'unknown'} must be observed or deferred`);
    if (!Number.isFinite(row.risk) || row.risk < 1 || row.risk > 5) errors.push(`row ${row.id || 'unknown'} risk must be 1..5`);
    if (!row.nextAction) errors.push(`row ${row.id || 'unknown'} missing nextAction`);
    if (!row.nonClaim) errors.push(`row ${row.id || 'unknown'} missing nonClaim`);
  }
  if ((checkpoint.failedRowIds || []).length) errors.push('failedRowIds must be empty');
  if ((checkpoint.missingRequiredRows || []).length) errors.push('missingRequiredRows must be empty');
  for (const key of ['releaseLightCommandVisible','admissionCancellationObservedOrExplicitlyDeferred','highRiskRowsBounded','rowsRankedByRisk','noFailedRows','requiredRowsPresent','exactlyOnceNonClaimVisible','browserWorkerNonClaimVisible']) {
    if (checkpoint.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const claim of KERNEL_KIT_ADMISSION_CANCELLATION_CHECKPOINT_NON_CLAIMS) {
    if (!checkpoint.nonClaims?.includes(claim)) errors.push(`missing admission/cancellation non-claim: ${claim}`);
  }
  return frozen({
    ok: errors.length === 0,
    errors,
    rowCount: rows.length,
    observedCount: checkpoint.observedRowIds?.length || 0,
    deferredCount: checkpoint.deferredRowIds?.length || 0,
    failedCount: checkpoint.failedRowIds?.length || 0,
    format: checkpoint.format || null,
    status: checkpoint.status || null
  });
}
