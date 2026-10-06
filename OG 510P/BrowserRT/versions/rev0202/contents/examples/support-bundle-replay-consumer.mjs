import * as defaultApi from '../src/public-api.mjs';

export const SUPPORT_BUNDLE_REPLAY_CONSUMER_FORMAT = 'browserrt.support-bundle-replay-consumer.v1';

const REQUIRED_PROOF = Object.freeze([
  'packageRootApiOnly',
  'diagnosticsNamespaceUsed',
  'supportBundleValid',
  'supportBundleReplayPlanReady',
  'displaySnapshotReady',
  'operatorReplayGateReady',
  'retryControlsHiddenForVerifyAndStop',
  'hiddenRowsCarryCanonicalDisplayFields',
  'hiddenRetryRowsShowMissingMarkers',
  'noCommandsExecuted'
]);

const REQUIRED_TRACE_KINDS = Object.freeze([
  'runtime:boot',
  'channel:create',
  'channel:send',
  'channel:receive',
  'agent:spawn',
  'agent:ready',
  'agent:call',
  'agent:result',
  'object:transfer-ref',
  'admission:admit',
  'admission:reject',
  'admission:release',
  'object:opfs-storage-lane-adapter-ref',
  'block-store-lane:schedule',
  'storage-lane:dispatch',
  'block-store-lane:op-complete',
  'storage-lane:complete',
  'storage:opfs-block-put',
  'storage:opfs-block-get',
  'runtime:close'
]);

function syntheticKernelKitSuccessReport(revision) {
  return Object.freeze({
    project: 'BrowserRT',
    revision,
    status: 'passed',
    proofId: `${revision}-package-installed-support-bundle-replay-synthetic-success`,
    proof: Object.freeze({
      workerAgent: true,
      transferDetached: true,
      boundedChannel: true,
      admissionRejectedNoMutation: true,
      storageWrite: true,
      reloadReadback: true,
      opfsAbortBoundary: true,
      guardedStorageLane: true,
      storagePostureObserved: true,
      webLockPostureObserved: true,
      traceComplete: true
    }),
    traceKinds: REQUIRED_TRACE_KINDS.slice(),
    stageReceipt: Object.freeze({ passedCount: 8, status: 'passed' }),
    read: Object.freeze({ verify: Object.freeze({ ok: true }) }),
    storage: Object.freeze({ result: Object.freeze({ digest: 'sha256:redacted-package-installed-support-bundle-replay' }) }),
    storagePosture: Object.freeze({
      proof: Object.freeze({ estimateChecked: true, quotaKnown: true, usageKnown: true, persistedChecked: true, persistenceNotRequestedByDefault: true }),
      estimate: Object.freeze({ usage: 1024, quota: 1048576, usageDetailsKeys: Object.freeze(['opfs']) }),
      persisted: Object.freeze({ persisted: false }),
      persistRequest: Object.freeze({ requested: false })
    }),
    webLockPosture: Object.freeze({
      proof: Object.freeze({ navigatorLocksSeen: true, exclusiveNoOverlap: true, sharedCoHold: true, drainedAfterUse: true, noFairnessClaim: true }),
      exclusive: Object.freeze({ maxActive: 1 }),
      shared: Object.freeze({ maxActive: 2 })
    }),
    guardedStorageLane: Object.freeze({
      proof: Object.freeze({
        webLocksAvailable: true,
        guardedProvider: true,
        exclusiveMutationsObserved: true,
        sharedReadsObserved: true,
        lockAcquiredReleased: true,
        noFairnessClaim: true,
        posturedGuardedFactoryUsed: true,
        posturedLaneAdapterFactoryUsed: true,
        postureGuardPropagated: true,
        boundedLockContentionPolicy: true
      }),
      provider: 'opfs-web-lock-guarded',
      adapterFactorySource: 'postured-web-lock-guarded-storage-lane-adapter-factory',
      writeBudgetGuardSource: 'browser-storage-posture-admission-policy',
      lockContentionPolicySource: 'postured-web-lock-guarded-opfs-factory'
    })
  });
}

function proofFromRows(rowBindings = [], replayPlan = {}, replayGate = {}) {
  const rows = Array.isArray(rowBindings) ? rowBindings : [];
  const hiddenRows = rows.filter((row) => row.retryControlVisible !== true);
  return Object.freeze({
    retryControlsHiddenForVerifyAndStop: rows.filter((row) => row.decision === 'verify-first' || row.decision === 'stop/manual-review').every((row) => row.retryControlVisible === false),
    hiddenRowsCarryCanonicalDisplayFields: hiddenRows.every((row) => typeof row.displayRetryControlText === 'string' && typeof row.expectedMissingEvidenceText === 'string' && Object.hasOwn(row, 'stopReason')),
    hiddenRetryRowsShowMissingMarkers: rows.filter((row) => row.decision === 'retry' && row.retryControlVisible !== true).every((row) => row.displayMissingEvidenceText === row.expectedMissingEvidenceText && String(row.displayMissingEvidenceText || '').length > 0),
    noCommandsExecuted: replayPlan.proof?.replayDoesNotExecuteCommands === true && replayGate.posture === 'operator-replay-gate-not-command-execution-not-automated-repair'
  });
}

export function validateSupportBundleReplayConsumerReport(report = {}) {
  const errors = [];
  if (!report || typeof report !== 'object') errors.push('report must be an object');
  if (report?.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report?.format !== SUPPORT_BUNDLE_REPLAY_CONSUMER_FORMAT) errors.push(`format must be ${SUPPORT_BUNDLE_REPLAY_CONSUMER_FORMAT}`);
  if (report?.schema !== 1) errors.push('schema must be 1');
  if (!/^rev\d{4}$/.test(String(report?.revision || ''))) errors.push('revision must be rev####');
  if (!/^\d+\.\d+\.\d+$/.test(String(report?.version || ''))) errors.push('version must be x.y.z');
  if (report?.status !== 'passed') errors.push('status must be passed');
  const proof = report?.proof && typeof report.proof === 'object' ? report.proof : {};
  for (const key of REQUIRED_PROOF) if (proof[key] !== true) errors.push(`proof.${key} must be true`);
  if (!Array.isArray(report?.nonClaims) || !report.nonClaims.some((claim) => /does not execute commands/.test(claim))) errors.push('command-execution non-claim must be visible');
  return Object.freeze({ ok: errors.length === 0, errors, requiredProof: REQUIRED_PROOF.slice(), proof });
}

export async function runSupportBundleReplayWithApi(api = defaultApi, { generatedAt = 'deterministic-support-bundle-replay-consumer', source = 'examples/support-bundle-replay-consumer.mjs', importSpecifier = '../src/public-api.mjs' } = {}) {
  const { REVISION, VERSION, boot } = api;
  const rt = await boot({ telemetry: 'support-bundle-replay-consumer', supportBundleReplayConsumer: true, proof: REVISION });
  try {
    const successReport = syntheticKernelKitSuccessReport(REVISION);
    const failureReport = rt.kernelKitFailureModeReport({
      mode: 'admission-reject-no-mutation',
      observed: { rejected: true, reason: 'synthetic-package-installed-support-bundle-replay', preventedMutation: true },
      traceKinds: ['runtime:boot', 'admission:reject', 'kernel-kit-demo:controlled-failure', 'kernel-kit-demo:failure:admission-reject-no-mutation', 'runtime:close']
    });
    const comparison = rt.kernelKitTraceComparison(successReport, failureReport, { source: 'support-bundle-replay-consumer-comparison', generatedAt: 'deterministic-support-bundle-replay-consumer-comparison' });
    const runbook = rt.diagnostics.kernelKitDiagnosticRunbook(comparison, { source: 'support-bundle-replay-consumer-runbook', generatedAt: 'deterministic-support-bundle-replay-consumer-runbook' });
    const exportBundle = rt.kernelKitDemoExportBundle(successReport, { source: 'support-bundle-replay-consumer-export', generatedAt: 'deterministic-support-bundle-replay-consumer-export' });
    const supportBundle = rt.diagnostics.kernelKitSupportBundle({
      successReport,
      reloadReport: successReport,
      failureReport,
      comparison,
      runbook,
      exportBundle,
      generatedAt: 'deterministic-support-bundle-replay-consumer-bundle'
    });
    const replayPlan = rt.diagnostics.kernelKitSupportBundleReplayPlan(supportBundle, { generatedAt: 'deterministic-support-bundle-replay-consumer-plan' });
    const displaySnapshot = rt.diagnostics.kernelKitSupportBundleOperatorPreflightDisplaySnapshot(replayPlan.operatorPreflight, { generatedAt: 'deterministic-support-bundle-replay-consumer-display-snapshot' });
    const replayGate = rt.diagnostics.kernelKitSupportBundleOperatorReplayGate({ replayPlan, operatorDisplaySnapshot: displaySnapshot }, { generatedAt: 'deterministic-support-bundle-replay-consumer-gate' });
    const validation = Object.freeze({
      supportBundle: rt.diagnostics.validateKernelKitSupportBundle(supportBundle),
      replayPlan: rt.diagnostics.validateKernelKitSupportBundleReplayPlan(replayPlan),
      displaySnapshot: rt.diagnostics.validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot(displaySnapshot),
      replayGate: rt.diagnostics.validateKernelKitSupportBundleOperatorReplayGate(replayGate)
    });
    const rowBindings = Array.isArray(replayGate.rowBindings) ? replayGate.rowBindings : [];
    const rowProof = proofFromRows(rowBindings, replayPlan, replayGate);
    const proof = Object.freeze({
      packageRootApiOnly: true,
      diagnosticsNamespaceUsed: true,
      supportBundleValid: validation.supportBundle.ok === true,
      supportBundleReplayPlanReady: validation.replayPlan.ok === true && replayPlan.status === 'replay-plan-ready',
      displaySnapshotReady: validation.displaySnapshot.ok === true && displaySnapshot.status === 'ready',
      operatorReplayGateReady: validation.replayGate.ok === true && replayGate.status === 'ready',
      ...rowProof
    });
    const missing = REQUIRED_PROOF.filter((key) => proof[key] !== true);
    const report = Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      format: SUPPORT_BUNDLE_REPLAY_CONSUMER_FORMAT,
      status: missing.length === 0 ? 'passed' : 'failed',
      source,
      generatedAt,
      importSpecifier,
      purpose: 'Installed package consumer path for support-bundle replay gating: package root boot(), runtime diagnostics namespace, support bundle, replay plan, operator display snapshot, and operator replay gate without internal helper imports.',
      proof,
      missing,
      validation,
      counts: Object.freeze({ rowCount: rowBindings.length, blockedCount: replayGate.blockedCount || 0, retryVisibleCount: replayGate.retryVisibleCount || 0, hiddenRowCount: rowBindings.filter((row) => row.retryControlVisible !== true).length }),
      supportBundle: Object.freeze({ format: supportBundle.format, status: validation.supportBundle.ok ? 'valid' : 'invalid', sectionCount: supportBundle.sections?.length || 0 }),
      replayPlan: Object.freeze({ format: replayPlan.format, status: replayPlan.status, phaseCount: replayPlan.phases?.length || 0, blockedPhaseIds: replayPlan.blockedPhaseIds || [] }),
      displaySnapshot: Object.freeze({ format: displaySnapshot.format, status: displaySnapshot.status, rowCount: displaySnapshot.rowCount || 0 }),
      replayGate: Object.freeze({ format: replayGate.format, status: replayGate.status, rowCount: replayGate.rowCount || 0, blockedRowIds: replayGate.blockedRowIds || [] }),
      nonClaims: Object.freeze([
        'Installed support-bundle replay consumer proves package-root wiring and display gating only; it does not publish to a registry, run browser OPFS, claim cross-browser behavior, reserve quota, or survive eviction.',
        'Operator replay gate does not execute commands, repair storage, grant quota, preserve Service Worker lifetime, prove Web Lock fairness, or authorize production retry.'
      ])
    });
    return Object.freeze({ ...report, reportValidation: validateSupportBundleReplayConsumerReport(report) });
  } finally {
    rt.close('support-bundle-replay-consumer-complete');
  }
}

export async function runSupportBundleReplayConsumer(options = {}) {
  return runSupportBundleReplayWithApi(defaultApi, { source: 'examples/support-bundle-replay-consumer.mjs', importSpecifier: '../src/public-api.mjs', ...options });
}

if (typeof process !== 'undefined' && process.argv && import.meta.url === `file://${process.argv[1]}`) {
  console.log(JSON.stringify(await runSupportBundleReplayConsumer(), null, 2));
}
