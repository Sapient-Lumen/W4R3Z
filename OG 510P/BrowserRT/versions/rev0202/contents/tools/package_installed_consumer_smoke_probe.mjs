#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { preparePackageTarballForProbe, runNpmForPackageFixture } from './lib/package_installed_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-CONSUMER-SMOKE-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function declaredBrowserRtRuntimeMethods(typesSource) {
  const marker = 'export interface BrowserRTRuntime {';
  const start = typesSource.indexOf(marker);
  assert.ok(start >= 0, 'installed declarations missing BrowserRTRuntime interface');
  const bodyStart = start + marker.length;
  const end = typesSource.indexOf('\n}\n', bodyStart);
  assert.ok(end > bodyStart, 'installed BrowserRTRuntime interface is not structurally readable');
  const body = typesSource.slice(bodyStart, end);
  return [...body.matchAll(/^  ([A-Za-z_$][\w$]*)\s*(?:<[^\n>]+>)?\(/gm)].map((match) => match[1]).sort();
}

const TYPESCRIPT_CONSUMER = String.raw`
import { boot, REVISION, VERSION, createBrowserStorageRecoveryGuidance, BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT, type BrowserRTRuntime } from 'browserrt';
import { boot as bootRuntimeCore, BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT, type BrowserRtRuntimeCore } from 'browserrt/runtime-core';
import { diagnoseBrowserStoragePosture as diagnoseStoragePostureSubpath, BROWSERRT_BROWSER_STORAGE_POSTURE_RECEIPT_FORMAT } from 'browserrt/browser-storage-posture';

const runtime: Readonly<BrowserRTRuntime> = await boot({ telemetry: 'typed-installed-package-consumer' });
const runtimeCore: Readonly<BrowserRtRuntimeCore> = bootRuntimeCore({ telemetry: 'typed-installed-runtime-core-consumer' });
const runtimeCoreEntryFormat: typeof BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT = runtimeCore.entry;
void runtimeCoreEntryFormat;
const storagePostureReceiptFormat: typeof BROWSERRT_BROWSER_STORAGE_POSTURE_RECEIPT_FORMAT = 'browserrt.browser-storage-posture-receipt.v1';
void storagePostureReceiptFormat;
void diagnoseStoragePostureSubpath;
const typedRevision: typeof REVISION = runtime.revision;
const typedVersion: typeof VERSION = runtime.version;
void typedRevision;
void typedVersion;
const guidance = createBrowserStorageRecoveryGuidance({ name: 'BrowserRTWebLockCoordinatorError', code: 'BRT_WEB_LOCK_TIMEOUT', message: 'timeout' }, { op: 'typed-put' });
const guidanceFormat: typeof BROWSERRT_BROWSER_STORAGE_RECOVERY_GUIDANCE_FORMAT = guidance.format;
void guidanceFormat;

const store = runtime.storage.blockStore({ name: 'typed-consumer-store' });
const scheduler = runtime.coordination.crossLaneScheduler({
  label: 'typed-consumer-scheduler',
  lanes: [{ id: 'storage', rank: 50, capacity: 1, quantum: 64, maxQueuedCost: 256 }]
});
const adapter = runtime.storage.blockStoreLaneAdapter({ label: 'typed-consumer-adapter', store, scheduler });
const scheduled = adapter.schedulePut(new Uint8Array([1, 2, 3]), { id: 'typed-put' });
void scheduled;
void adapter.snapshot();
void runtime.core.scope;
void runtime.core.channel;
void runtime.core.spawnAgent;
void runtime.scope;
void runtime.storage.blockStoreLaneAdapter;
void runtime.storage.opfsAsyncBlockStore;
void runtime.storage.opfsAsyncBlockStoreWithPosture;
void runtime.storage.opfsWebLockGuardedBlockStoreWithPosture;
void runtime.storage.opfsWebLockGuardedStorageLaneAdapterWithPosture;
void runtime.storage.browserStoragePosture;
void runtime.storage.browserStorageRecoveryGuidance;
void runtime.coordination.crossLaneScheduler;
void runtime.coordination.webLockCoordinator;
void runtime.diagnostics.kernelKitTraceExport;
void runtime.diagnostics.kernelKitSupportBundle;
void runtime.diagnostics.kernelKitSupportBundleReplayPlan;
void runtime.diagnostics.kernelKitSupportBundleOperatorPreflightDisplaySnapshot;
void runtime.diagnostics.kernelKitSupportBundleOperatorReplayGate;
void runtime.experimental.providerResilienceModelOracle;
void runtimeCore.core.channel;
void runtimeCore.storage.blockStore;
void runtimeCore.storage.blockStoreLaneAdapter;
const runtimeCoreStore = runtimeCore.storage.blockStore({ name: 'typed-runtime-core-store' });
const runtimeCoreScheduler = runtimeCore.coordination.crossLaneScheduler({ label: 'typed-runtime-core-scheduler', lanes: [{ id: 'storage', rank: 50, capacity: 1, quantum: 64, maxQueuedCost: 256 }] });
const runtimeCoreAdapter = runtimeCore.storage.blockStoreLaneAdapter({ label: 'typed-runtime-core-adapter', store: runtimeCoreStore, scheduler: runtimeCoreScheduler });
void runtimeCoreAdapter.scheduleEstimate({ id: 'typed-runtime-core-estimate' });
void runtimeCoreAdapter.scheduleSnapshot({ id: 'typed-runtime-core-snapshot' });
void runtimeCoreAdapter.scheduleCleanupForTest({ id: 'typed-runtime-core-cleanup' });
void runtimeCoreAdapter.submit('estimate', {}, { id: 'typed-runtime-core-submit-estimate' });
void runtimeCore.coordination.admissionController;
void runtimeCore.coordination.crossLaneScheduler;
runtimeCore.close();


// These references make the complete supported boot facade a compile-time
// contract instead of allowing runtime-only methods to drift out of the .d.ts.
void runtime.circuitBreakerBulkheadController;
void runtime.providerResilienceModelOracle;
void runtime.storageLaneAdmissionHistoryRunner;
void runtime.storageLaneAdmissionHistoryModelOracle;
void runtime.storageLaneOverloadGovernanceModelOracle;
void runtime.dreamBoundaryMap;
void runtime.validateDreamBoundaryMap;
void runtime.projectContinuationAssessment;
void runtime.validateProjectContinuationAssessment;
void runtime.kernelKitDemoPlan;
void runtime.validateKernelKitDemoReport;
void runtime.kernelKitDemoTranscript;
void runtime.validateKernelKitDemoTranscript;
void runtime.kernelKitDemoUsefulnessScore;
void runtime.kernelKitDemoTraceSummary;
void runtime.kernelKitTraceExport;
void runtime.validateKernelKitTraceExport;
void runtime.kernelKitDemoExportBundle;
void runtime.validateKernelKitDemoExportBundle;
void runtime.kernelKitFailureModeReport;
void runtime.validateKernelKitFailureModeReport;
void runtime.kernelKitTraceComparison;
void runtime.validateKernelKitTraceComparison;
void runtime.kernelKitDiagnosticRunbook;
void runtime.validateKernelKitDiagnosticRunbook;
void runtime.kernelKitSupportBundle;
void runtime.validateKernelKitSupportBundle;
void runtime.kernelKitSupportBundleReplayPlan;
void runtime.validateKernelKitSupportBundleReplayPlan;
void runtime.kernelKitSupportBundleOperatorPreflightDisplaySnapshot;
void runtime.validateKernelKitSupportBundleOperatorPreflightDisplaySnapshot;
void runtime.kernelKitSupportBundleOperatorReplayGate;
void runtime.validateKernelKitSupportBundleOperatorReplayGate;
void runtime.kernelKitSupportBundleEvidenceLedger;
void runtime.validateKernelKitSupportBundleEvidenceLedger;
void runtime.kernelKitSupportBundleEvidenceCheckpoint;
void runtime.validateKernelKitSupportBundleEvidenceCheckpoint;
void runtime.kernelKitGuidedTour;
void runtime.validateKernelKitGuidedTour;
void runtime.kernelKitSupportBundleImportReport;
void runtime.validateKernelKitSupportBundleImportReport;
void runtime.kernelKitSupportBundleDiff;
void runtime.validateKernelKitSupportBundleDiff;
void runtime.kernelKitHandoffMarkdown;
void runtime.validateKernelKitHandoffMarkdown;
void runtime.kernelKitDemoHandoff;
void runtime.validateKernelKitDemoHandoff;
void runtime.kernelKitDemoUsefulnessReport;
void runtime.validateKernelKitDemoUsefulnessReport;
void runtime.kernelKitDemoObservatory;
void runtime.validateKernelKitDemoObservatoryReport;
void runtime.kernelKitGuidedTourReceipt;
void runtime.validateKernelKitGuidedTourReceipt;
void runtime.kernelKitHandoffMarkdownImport;
void runtime.validateKernelKitHandoffMarkdownImportReport;
void runtime.kernelKitReadinessGate;
void runtime.validateKernelKitReadinessGate;
void runtime.kernelKitReadinessContrast;
void runtime.validateKernelKitReadinessContrast;
void runtime.opfsBlockStoreStorageLaneAdapter;

runtime.close();
`;

const TYPESCRIPT_CONFIG = JSON.stringify({
  compilerOptions: {
    target: 'ES2022',
    module: 'ESNext',
    moduleResolution: 'Bundler',
    lib: ['ES2022', 'DOM'],
    strict: true,
    noEmit: true,
    skipLibCheck: false
  },
  include: ['consumer.ts']
}, null, 2) + '\n';

const CONSUMER = String.raw`
import assert from 'node:assert/strict';
import * as api from 'browserrt';
import * as runtimeCoreApi from 'browserrt/runtime-core';
import * as storagePostureApi from 'browserrt/browser-storage-posture';
import { runProductWedgeWithApi } from './node_modules/browserrt/examples/product-wedge-consumer.mjs';
import { runGoldenWorkloadWithApi } from './node_modules/browserrt/examples/golden-workload-consumer.mjs';
import { runRuntimeCoreConsumerWithApi } from './node_modules/browserrt/examples/runtime-core-consumer.mjs';
const report = await runProductWedgeWithApi(api, { generatedAt: 'deterministic-installed-package-smoke', source: 'installed-package-consumer.mjs', importSpecifier: 'browserrt' });
const golden = await runGoldenWorkloadWithApi(api, { generatedAt: 'deterministic-installed-package-golden-workload', source: 'installed-package-consumer.mjs', importSpecifier: 'browserrt' });
const runtimeCore = await runRuntimeCoreConsumerWithApi(runtimeCoreApi, { generatedAt: 'deterministic-installed-package-runtime-core', source: 'installed-package-consumer.mjs', importSpecifier: 'browserrt/runtime-core' });
const storagePostureSubpathReport = await storagePostureApi.diagnoseBrowserStoragePosture({
  generatedAt: 'deterministic-installed-storage-posture-subpath',
  globalThis: { navigator: { storage: { getDirectory() { return {}; }, async estimate() { return { quota: 4096, usage: 1024, usageDetails: { fileSystem: 1024 } }; }, async persisted() { return false; } }, locks: { async request(_name, callback) { return await callback({ name: _name, mode: 'exclusive' }); }, async query() { return { held: [], pending: [] }; } } } }
});
const surfaceRuntime = await api.boot({ telemetry: 'installed-package-runtime-surface' });
const runtimeMethodNames = Object.entries(surfaceRuntime).filter(([, value]) => typeof value === 'function').map(([name]) => name).sort();
const runtimeNamespaceNames = ['core', 'storage', 'coordination', 'diagnostics', 'experimental'].filter((name) => surfaceRuntime[name] && typeof surfaceRuntime[name] === 'object').sort();
let webLocksRequiredRecovery = null;
try {
  await surfaceRuntime.storage.opfsWebLockGuardedBlockStoreWithPosture({ label: 'installed-web-locks-required-recovery', lockContentionTimeoutMs: 17 });
  assert.fail('postured guarded OPFS factory should reject before mutation when Web Locks are required but unavailable');
} catch (error) {
  webLocksRequiredRecovery = {
    name: error?.name || null,
    code: error?.code || null,
    preMutationRejected: error?.detail?.preMutationRejected === true,
    recoveryCode: error?.detail?.recovery?.code || null,
    recoveryCategory: error?.detail?.recovery?.category || null,
    recoveryPhase: error?.detail?.recovery?.phase || null,
    recoveryAction: error?.detail?.recovery?.action || null,
    shouldRetryAutomatically: error?.detail?.recovery?.shouldRetryAutomatically === true,
    shouldQueryLocks: error?.detail?.recovery?.shouldQueryLocks === true,
    mutationAttempted: error?.detail?.recovery?.mutationAttempted ?? null,
    traceGuidanceObserved: surfaceRuntime.trace.snapshot().some((event) => event.kind === 'runtime:browser-storage-recovery-guidance' && event.code === 'BRT_BROWSER_WEB_LOCKS_REQUIRED')
  };
}
surfaceRuntime.close();
assert.equal(webLocksRequiredRecovery.code, 'BRT_BROWSER_WEB_LOCKS_REQUIRED');
assert.equal(webLocksRequiredRecovery.recoveryCode, 'BRT_BROWSER_WEB_LOCKS_REQUIRED');
assert.equal(webLocksRequiredRecovery.recoveryCategory, 'coordination-unavailable');
assert.equal(webLocksRequiredRecovery.recoveryPhase, 'coordination-admission');
assert.equal(webLocksRequiredRecovery.preMutationRejected, true);
assert.equal(webLocksRequiredRecovery.mutationAttempted, false);
assert.equal(webLocksRequiredRecovery.shouldRetryAutomatically, false);
assert.equal(webLocksRequiredRecovery.traceGuidanceObserved, true);
assert.equal(report.status, 'passed', report.validation.errors.join('; '));
assert.equal(report.receipt.observed.imports.importSpecifier, 'browserrt');
assert.equal(report.receipt.proof.storageLaneWriteRead, true);
assert.equal(golden.status, 'passed', golden.validation.errors.join('; '));
assert.equal(storagePostureSubpathReport.opfsPostureReceipt.format, storagePostureApi.BROWSERRT_BROWSER_STORAGE_POSTURE_RECEIPT_FORMAT);
assert.equal(storagePostureSubpathReport.opfsPostureReceipt.quota.ok, true);
assert.equal(storagePostureSubpathReport.opfsPostureReceipt.internalByteLedger.provided, false);
assert.equal(typeof storagePostureApi.boot, 'undefined', 'storage posture subpath must not expose the full runtime boot facade');
assert.equal(runtimeCore.status, 'passed', runtimeCore.validation.errors.join('; '));
assert.equal(runtimeCore.importSpecifier, 'browserrt/runtime-core');
assert.equal(runtimeCore.receipt.observed.runtime.runtimeCoreEntry, true);
assert.equal(runtimeCore.receipt.observed.imports.rootEntryAvoided, true);
assert.equal(runtimeCore.receipt.proof.storageLaneWriteRead, true);
assert.equal(runtimeCore.receipt.observed.storage.runtimeCoreLightLane, true);
assert.equal(runtimeCore.receipt.observed.storage.scheduledAbortAccepted, false);
assert.equal(runtimeCore.receipt.observed.storage.scheduledAbortRejectedBeforeEnqueue, true);
assert.equal(runtimeCore.receipt.observed.storage.scheduledAbortDispatchEmpty, true);
assert.equal(runtimeCore.receipt.observed.storage.scheduledAbortQueueNeverFilled, true);
assert.equal(runtimeCore.receipt.observed.storage.scheduledAbortNoMutation, true);
assert.equal(runtimeCore.receipt.observed.storage.scheduledAbortErrorName, 'AbortError');
assert.equal(runtimeCore.receipt.observed.storage.queuedAbortAccepted, true);
assert.equal(runtimeCore.receipt.observed.storage.queuedAbortCancelledBeforeDispatch, true);
assert.equal(runtimeCore.receipt.observed.storage.queuedAbortDrainEmpty, true);
assert.equal(runtimeCore.receipt.observed.storage.queuedAbortNoMutation, true);
assert.equal(runtimeCore.receipt.observed.storage.queuedAbortErrorName, 'AbortError');
assert.equal(runtimeCore.receipt.observed.storage.closeAbortAccepted, true);
assert.equal(runtimeCore.receipt.observed.storage.closeAbortCancelledBeforeDispatch, true);
assert.equal(runtimeCore.receipt.observed.storage.closeAbortDrainClosed, true);
assert.equal(runtimeCore.receipt.observed.storage.closeAbortNoMutation, true);
assert.equal(runtimeCore.receipt.observed.storage.closeAbortOwnedQueueEmpty, true);
assert.equal(runtimeCore.receipt.observed.storage.closeAbortScheduleAfterClose, 'rejected-closed');
assert.equal(runtimeCore.receipt.observed.storage.closeAbortScheduleAfterCloseCode, 'BRT_RUNTIME_CORE_LANE_ADAPTER_CLOSED');
assert.equal(runtimeCore.receipt.observed.storage.quotaPreflightRejectedBeforeEnqueue, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaPreflightQueueNeverFilled, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaPreflightNoMutation, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaPreflightRejectsCount, 1);
assert.equal(runtimeCore.receipt.observed.storage.quotaPreflightBudget.fits, false);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationFirstAccepted, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationSecondRejectedBeforeEnqueue, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationRejectedOnPendingBytes, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationQueuedOnlyFirst, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationBeforeDrainReserved, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationReleasedAfterDrain, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationDrainCompletedOnlyFirst, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationOnlyFirstMutated, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationProviderQuotaRejectsAvoided, true);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationRejectsCount, 1);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationBudget.fits, false);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationBudget.reservedBytes, 16);
assert.equal(runtimeCore.receipt.observed.storage.quotaReservationBudget.reason, 'exceeds-reserved-store-budget');
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetFirstAccepted, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetFirstCompletedAtFullQuota, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetSecondAcceptedAtFullQuota, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetSecondReservedZero, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetSecondQueuedDespiteFullQuota, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetSecondCompleted, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetAfterDrainStableUsage, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetHintObserved, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetAdapterSnapshotValid, true);
assert.equal(runtimeCore.receipt.observed.storage.duplicateBudgetQueueEmptyAfterDrain, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelFirstReserved, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelSchedulerCancelledFirst, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelSecondAcceptedAfterReconcile, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelReconciledBeforeSecondBudget, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelNoStaleReservationReject, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelSecondCompletedOnly, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelReleasedAfterDrain, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelAdapterSnapshotValid, true);
assert.equal(runtimeCore.receipt.observed.storage.externalCancelQueueEmptyAfterDrain, true);
assert.equal(runtimeCore.receipt.observed.storage.hintCleanupPutCompleted, true);
assert.equal(runtimeCore.receipt.observed.storage.hintCleanupDeleteClearedHint, true);
assert.equal(runtimeCore.receipt.observed.storage.hintCleanupNoStaleHintAfterDelete, true);
assert.equal(runtimeCore.receipt.observed.storage.hintCleanupAdapterSnapshotValid, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupSubmitPutAccepted, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupEstimateScheduled, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupSnapshotScheduled, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupEstimateUsageVisible, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupSnapshotVisible, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupCleanupScheduled, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupCleanupDeleted, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupFinalEmpty, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupAdapterSnapshotValid, true);
assert.equal(runtimeCore.receipt.observed.storage.telemetryCleanupQueueEmptyAfterDrain, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerForeignQueued, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerOwnedPutAccepted, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerForeignHeadBlocksOwnedDispatch, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerForeignAndOwnedStillQueuedWhileBlocked, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerNoOwnedMutationWhileForeignHead, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerFilteredHeadBlockCounted, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerBlockedLastDispatchVisible, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerBlockedForeignHeadIdentified, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerBlockedDispatchReobserved, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerBlockedDispatchStatsVisible, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerBlockedStatePrunedAfterOwnerComplete, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerForeignCompletedByOwner, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerOwnedDispatchAfterForeignComplete, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerForeignPreserved, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerStoreMutatedOnlyOwned, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerQueueEmptyAfterBothOwners, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerAdapterSnapshotValid, true);
assert.equal(runtimeCore.receipt.observed.storage.sharedSchedulerNoForeignAdapterError, true);
assert.equal(golden.receipt.proof.namespacedFacadeUsed, true);
assert.equal(golden.receipt.proof.abortCancelledBeforeCommit, true);
assert.equal(golden.receipt.proof.recoveryWriteAfterAbort, true);
const runtimeCoreLightProof = {
  runtimeCoreLightLane: runtimeCore.receipt.observed.storage.runtimeCoreLightLane === true,
  scheduledAbortNoMutation: runtimeCore.receipt.observed.storage.scheduledAbortRejectedBeforeEnqueue === true && runtimeCore.receipt.observed.storage.scheduledAbortQueueNeverFilled === true && runtimeCore.receipt.observed.storage.scheduledAbortNoMutation === true,
  queuedAbortNoMutation: runtimeCore.receipt.observed.storage.queuedAbortAccepted === true && runtimeCore.receipt.observed.storage.queuedAbortCancelledBeforeDispatch === true && runtimeCore.receipt.observed.storage.queuedAbortNoMutation === true,
  closeAbortNoMutation: runtimeCore.receipt.observed.storage.closeAbortAccepted === true && runtimeCore.receipt.observed.storage.closeAbortCancelledBeforeDispatch === true && runtimeCore.receipt.observed.storage.closeAbortNoMutation === true && runtimeCore.receipt.observed.storage.closeAbortOwnedQueueEmpty === true,
  quotaPreflightNoQueueNoMutation: runtimeCore.receipt.observed.storage.quotaPreflightRejectedBeforeEnqueue === true && runtimeCore.receipt.observed.storage.quotaPreflightQueueNeverFilled === true && runtimeCore.receipt.observed.storage.quotaPreflightNoMutation === true && runtimeCore.receipt.observed.storage.quotaPreflightRejectsCount === 1,
  quotaReservationNoOverAdmission: runtimeCore.receipt.observed.storage.quotaReservationFirstAccepted === true && runtimeCore.receipt.observed.storage.quotaReservationSecondRejectedBeforeEnqueue === true && runtimeCore.receipt.observed.storage.quotaReservationRejectedOnPendingBytes === true && runtimeCore.receipt.observed.storage.quotaReservationReleasedAfterDrain === true && runtimeCore.receipt.observed.storage.quotaReservationOnlyFirstMutated === true,
  duplicateBudgetFullQuotaAccepted: runtimeCore.receipt.observed.storage.duplicateBudgetSecondAcceptedAtFullQuota === true && runtimeCore.receipt.observed.storage.duplicateBudgetSecondReservedZero === true && runtimeCore.receipt.observed.storage.duplicateBudgetAfterDrainStableUsage === true,
  externalCancelReservationReconciled: runtimeCore.receipt.observed.storage.externalCancelSecondAcceptedAfterReconcile === true && runtimeCore.receipt.observed.storage.externalCancelNoStaleReservationReject === true && runtimeCore.receipt.observed.storage.externalCancelReleasedAfterDrain === true,
  duplicateHintCleanupOnDelete: runtimeCore.receipt.observed.storage.hintCleanupDeleteClearedHint === true && runtimeCore.receipt.observed.storage.hintCleanupNoStaleHintAfterDelete === true,
  telemetryCleanupScheduled: runtimeCore.receipt.observed.storage.telemetryCleanupEstimateUsageVisible === true && runtimeCore.receipt.observed.storage.telemetryCleanupSnapshotVisible === true && runtimeCore.receipt.observed.storage.telemetryCleanupCleanupDeleted === true && runtimeCore.receipt.observed.storage.telemetryCleanupFinalEmpty === true,
  sharedSchedulerForeignHeadFairness: runtimeCore.receipt.observed.storage.sharedSchedulerForeignHeadBlocksOwnedDispatch === true && runtimeCore.receipt.observed.storage.sharedSchedulerNoOwnedMutationWhileForeignHead === true && runtimeCore.receipt.observed.storage.sharedSchedulerForeignCompletedByOwner === true && runtimeCore.receipt.observed.storage.sharedSchedulerOwnedDispatchAfterForeignComplete === true && runtimeCore.receipt.observed.storage.sharedSchedulerNoForeignAdapterError === true,
  sharedSchedulerBlockedDiagnostics: runtimeCore.receipt.observed.storage.sharedSchedulerBlockedLastDispatchVisible === true && runtimeCore.receipt.observed.storage.sharedSchedulerBlockedForeignHeadIdentified === true && runtimeCore.receipt.observed.storage.sharedSchedulerBlockedDispatchReobserved === true && runtimeCore.receipt.observed.storage.sharedSchedulerBlockedDispatchStatsVisible === true && runtimeCore.receipt.observed.storage.sharedSchedulerBlockedStatePrunedAfterOwnerComplete === true,
  closeAbortScheduleAfterClose: runtimeCore.receipt.observed.storage.closeAbortScheduleAfterClose,
  scheduledAbortErrorName: runtimeCore.receipt.observed.storage.scheduledAbortErrorName,
  queuedAbortErrorName: runtimeCore.receipt.observed.storage.queuedAbortErrorName
};
console.log(JSON.stringify({ project: 'BrowserRT', revision: api.REVISION, version: api.VERSION, schema: 1, status: 'passed', importSpecifier: 'browserrt', runtimeMethodNames, runtimeNamespaceNames, storagePostureSubpath: { importSpecifier: 'browserrt/browser-storage-posture', format: storagePostureSubpathReport.opfsPostureReceipt.format, quotaOk: storagePostureSubpathReport.opfsPostureReceipt.quota.ok === true, ledgerProvided: storagePostureSubpathReport.opfsPostureReceipt.internalByteLedger.provided === true, fullBootAbsent: typeof storagePostureApi.boot === 'undefined' }, webLocksRequiredRecovery, receipt: report.receipt, validation: report.validation, golden: { receipt: golden.receipt, validation: golden.validation }, runtimeCoreSubpath: { importSpecifier: runtimeCore.importSpecifier, receipt: runtimeCore.receipt, validation: runtimeCore.validation, lightProof: runtimeCoreLightProof } }, null, 2));
`;


export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-installed-smoke-'));
  const packDir = join(workspace, 'pack');
  const consumerDir = join(workspace, 'consumer');
  await mkdir(packDir, { recursive: true });
  await mkdir(consumerDir, { recursive: true });
  try {
    const prepared = await preparePackageTarballForProbe({ root, packDir });
    const { packInfo, tarball, fileNames } = prepared;
    const requiredTarballFiles = [
      'package.json',
      'src/public-api.mjs',
      'src/public-api.d.ts',
      'src/runtime-core-public.mjs',
      'src/runtime-core-public.d.ts',
      'src/runtime-core-lane-adapter.mjs',
      'src/browser-storage-posture.mjs',
      'src/browser-storage-posture-public.d.ts',
      'src/product-wedge.mjs',
      'src/browserrt.mjs',
      'src/sab-ring.mjs',
      'src/block-store-lane-adapter.mjs',
      'src/agent-worker.mjs',
      'src/node-agent-worker.mjs',
      'src/storage-lane-scheduler.mjs',
      'src/types.d.ts',
      'examples/product-wedge-consumer.mjs',
      'examples/runtime-core-consumer.mjs',
      'examples/golden-workload-consumer.mjs',
      'examples/support-bundle-replay-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing runtime dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    runNpmForPackageFixture('npm', ['init', '-y'], { cwd: consumerDir });
    const install = runNpmForPackageFixture('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    await writeFile(join(consumerDir, 'consumer.mjs'), CONSUMER, 'utf8');
    const consumer = runNpmForPackageFixture('node', ['consumer.mjs'], { cwd: consumerDir });
    const consumerReport = JSON.parse(consumer.stdout);
    await writeFile(join(consumerDir, 'consumer.ts'), TYPESCRIPT_CONSUMER, 'utf8');
    await writeFile(join(consumerDir, 'tsconfig.json'), TYPESCRIPT_CONFIG, 'utf8');
    const typecheck = runNpmForPackageFixture(process.env.BROWSERRT_TSC || 'tsc', ['--project', 'tsconfig.json', '--pretty', 'false'], { cwd: consumerDir });
    assert.equal(consumerReport.status, 'passed');
    assert.equal(consumerReport.importSpecifier, 'browserrt');
    assert.equal(consumerReport.revision, REVISION);
    assert.equal(consumerReport.version, VERSION);
    const installedPackageJsonText = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8');
    const installedPackageJson = JSON.parse(installedPackageJsonText);
    assert.equal(installedPackageJson.exports?.['.']?.import, './src/public-api.mjs');
    assert.equal(installedPackageJson.exports?.['./runtime-core']?.import, './src/runtime-core-public.mjs');
    assert.equal(installedPackageJson.exports?.['./runtime-core']?.types, './src/runtime-core-public.d.ts');
    assert.equal(installedPackageJson.exports?.['./browser-storage-posture']?.import, './src/browser-storage-posture.mjs');
    assert.equal(installedPackageJson.exports?.['./browser-storage-posture']?.types, './src/browser-storage-posture-public.d.ts');
    assert.equal(installedPackageJson.exports?.['./internal'], undefined, 'installed package must not expose ./internal');
    const installedPackageForbiddenKeys = ['scripts', 'browserrt_current', 'added', 'changed', 'artifacts', 'current_commands', 'validation_commands'].filter((key) => Object.prototype.hasOwnProperty.call(installedPackageJson, key));
    assert.deepEqual(installedPackageForbiddenKeys, [], `installed runtime package.json leaked cloudtainer-only keys: ${installedPackageForbiddenKeys.join(', ')}`);
    const installedPackageJsonBytes = Buffer.byteLength(installedPackageJsonText, 'utf8');
    assert.ok(installedPackageJsonBytes <= 8192, `installed runtime package.json too large: ${installedPackageJsonBytes}`);
    const installedTypesSource = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'src', 'types.d.ts'), 'utf8');
    const declarationMethodNames = declaredBrowserRtRuntimeMethods(installedTypesSource);
    assert.deepEqual(declarationMethodNames, consumerReport.runtimeMethodNames, 'installed BrowserRTRuntime declaration method names drifted from boot() runtime methods');
    assert.equal(declarationMethodNames.length, 113, 'unexpected BrowserRTRuntime method count');
    assert.deepEqual(consumerReport.runtimeNamespaceNames, ['coordination', 'core', 'diagnostics', 'experimental', 'storage'], 'installed runtime missing product namespaces');
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-consumer-smoke`,
      purpose: 'Package-installed consumer smoke: npm pack, local install, package-root JavaScript execution, package-root TypeScript compilation, public API product wedge execution, lightweight browser-storage-posture subpath execution, runtime-core subpath execution including quota preflight no-queue, pending-put reservation, and duplicate-aware full-quota proofs, golden bounded local workload execution, and tarball file-boundary hygiene.',
      package: {
        name: packInfo.name,
        version: packInfo.version,
        filename: packInfo.filename,
        fileCount: fileNames.length,
        unpackedSize: packInfo.unpackedSize,
        requiredTarballFiles,
        requiredTarballFilesPresent: true,
        forbiddenFilesAbsent: true,
        source: prepared.source,
        reusedPreparedTarball: prepared.reusedPreparedTarball,
        tarballSha1: prepared.validation?.sha1 || null,
        tarballIntegrityMatchesPackInfo: prepared.validation?.tarballIntegrityMatchesPackInfo ?? null,
        runtimePackageJsonMatchesRootPublicFields: prepared.validation?.runtimePackageJsonMatchesRootPublicFields ?? null,
        tarballPackageJsonRuntimeSlim: prepared.validation?.tarballPackageJsonRuntimeSlim ?? null,
        installedPackageJsonBytes,
        installedPackageForbiddenKeys,
        packageRootExport: installedPackageJson.exports?.['.'] || null,
        internalExportAbsent: installedPackageJson.exports?.['./internal'] === undefined,
        storagePostureSubpathExport: installedPackageJson.exports?.['./browser-storage-posture'] || null
      },
      consumer: {
        importSpecifier: consumerReport.importSpecifier,
        status: consumerReport.status,
        proof: consumerReport.receipt?.proof || null,
        validation: consumerReport.validation || null,
        goldenWorkload: {
          proof: consumerReport.golden?.receipt?.proof || null,
          validation: consumerReport.golden?.validation || null,
          workload: consumerReport.golden?.receipt?.workload || null
        },
        storagePostureSubpath: consumerReport.storagePostureSubpath || null,
        runtimeCoreSubpath: {
          proof: consumerReport.runtimeCoreSubpath?.receipt?.proof || null,
          lightProof: consumerReport.runtimeCoreSubpath?.lightProof || null,
          validation: consumerReport.runtimeCoreSubpath?.validation || null,
          observed: consumerReport.runtimeCoreSubpath?.receipt?.observed || null
        },
        webLocksRequiredRecovery: consumerReport.webLocksRequiredRecovery || null,
        traceKinds: consumerReport.receipt?.traceKinds || [],
        typescript: {
          status: 'passed',
          compiler: process.env.BROWSERRT_TSC || 'tsc',
          command: 'tsc --project tsconfig.json --pretty false',
          declaredRuntimeType: 'BrowserRTRuntime',
          flagshipMethod: 'blockStoreLaneAdapter',
          runtimeMethodCount: consumerReport.runtimeMethodNames.length,
          declarationMethodCount: declarationMethodNames.length,
          runtimeDeclarationMethodParity: true,
          namespaceTypecheck: true,
          methodNames: declarationMethodNames,
          runtimeNamespaceNames: consumerReport.runtimeNamespaceNames,
          stdout: String(typecheck.stdout || '').trim()
        }
      },
      commands: {
        pack: prepared.reusedPreparedTarball ? 'reuse prepared BrowserRT tarball from environment' : 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        run: 'node consumer.mjs',
        typecheck: 'tsc --project tsconfig.json --pretty false'
      },
      nonClaims: [
        'Local tarball install and TypeScript compiler smoke only; it does not publish to a registry, prove semver compatibility, prove every bundler, or prove cross-browser behavior.',
        'The product wedge and golden workload use fast memory-backed storage lanes through the product namespaces; OPFS/Web Locks proofs remain separate explicit browser/runtime tasks.'
      ]
    });
  } finally {
    await rm(workspace, { recursive: true, force: true });
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  try {
    const report = await runProbe();
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-consumer-smoke`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_consumer_smoke_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
