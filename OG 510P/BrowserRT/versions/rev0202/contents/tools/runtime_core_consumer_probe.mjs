#!/usr/bin/env node
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/runtime-core-public.mjs';
import { runRuntimeCoreConsumer } from '../examples/runtime-core-consumer.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-RUNTIME-CORE-CONSUMER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

export async function runProbe() {
  const report = await runRuntimeCoreConsumer({ generatedAt: 'deterministic-runtime-core-consumer-probe', source: 'tools/runtime_core_consumer_probe.mjs' });
  if (report.status !== 'passed') throw new Error(`runtime-core consumer failed: ${(report.validation?.errors || []).join('; ')}`);
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    status: 'passed',
    probe_id: `${REVISION}-runtime-core-consumer-probe`,
    purpose: 'Slim runtime-core subpath consumer proof: import browserrt/runtime-core-style entry, boot the memory-backed runtime core, apply admission, prove pre-aborted put no-mutation, count drop-oldest backpressure, schedule light storage-lane put/verify/get, reject pre-aborted scheduled work before enqueue, cancel queued aborts before dispatch, cancel close-before-dispatch queued work, prove no-mutation for abort/close cases, reject obvious store-budget overflow before scheduler enqueue/provider quota stats, reserve pending put bytes to reject over-admission, admit known duplicate string payloads at full local quota with zero growth reservation, reconcile externally cancelled queued reservations before later quota admission, clear duplicate hints after delete, schedule estimate/snapshot/cleanup telemetry through the light adapter, preserve foreign-head scheduler fairness without adapter leapfrog, surface reobserved/pruned blocked-dispatch diagnostics, and close a trace receipt without importing the root BrowserRT monolith.',
    consumer: report,
    proof: Object.freeze({
      runtimeCoreEntry: report.receipt?.observed?.runtime?.runtimeCoreEntry === true,
      rootEntryAvoided: report.receipt?.observed?.imports?.rootEntryAvoided === true,
      admissionRejectedWithoutMutation: report.receipt?.proof?.admissionRejectedWithoutMutation === true,
      storageLaneWriteRead: report.receipt?.proof?.storageLaneWriteRead === true,
      runtimeCoreLightLane: report.receipt?.observed?.storage?.runtimeCoreLightLane === true,
      scheduledAbortNoMutation: report.receipt?.observed?.storage?.scheduledAbortRejectedBeforeEnqueue === true && report.receipt?.observed?.storage?.scheduledAbortDispatchEmpty === true && report.receipt?.observed?.storage?.scheduledAbortQueueNeverFilled === true && report.receipt?.observed?.storage?.scheduledAbortNoMutation === true,
      queuedAbortNoMutation: report.receipt?.observed?.storage?.queuedAbortAccepted === true && report.receipt?.observed?.storage?.queuedAbortCancelledBeforeDispatch === true && report.receipt?.observed?.storage?.queuedAbortDrainEmpty === true && report.receipt?.observed?.storage?.queuedAbortNoMutation === true,
      closeAbortNoMutation: report.receipt?.observed?.storage?.closeAbortAccepted === true && report.receipt?.observed?.storage?.closeAbortCancelledBeforeDispatch === true && report.receipt?.observed?.storage?.closeAbortDrainClosed === true && report.receipt?.observed?.storage?.closeAbortNoMutation === true && report.receipt?.observed?.storage?.closeAbortOwnedQueueEmpty === true && report.receipt?.observed?.storage?.closeAbortScheduleAfterClose === 'rejected-closed',
      quotaPreflightNoQueueNoMutation: report.receipt?.observed?.storage?.quotaPreflightRejectedBeforeEnqueue === true && report.receipt?.observed?.storage?.quotaPreflightQueueNeverFilled === true && report.receipt?.observed?.storage?.quotaPreflightDrainEmpty === true && report.receipt?.observed?.storage?.quotaPreflightNoMutation === true && report.receipt?.observed?.storage?.quotaPreflightRejectsCount === 1,
      quotaReservationNoOverAdmission: report.receipt?.observed?.storage?.quotaReservationFirstAccepted === true && report.receipt?.observed?.storage?.quotaReservationSecondRejectedBeforeEnqueue === true && report.receipt?.observed?.storage?.quotaReservationRejectedOnPendingBytes === true && report.receipt?.observed?.storage?.quotaReservationBeforeDrainReserved === true && report.receipt?.observed?.storage?.quotaReservationReleasedAfterDrain === true && report.receipt?.observed?.storage?.quotaReservationOnlyFirstMutated === true && report.receipt?.observed?.storage?.quotaReservationProviderQuotaRejectsAvoided === true && report.receipt?.observed?.storage?.quotaReservationRejectsCount === 1,
      duplicateBudgetFullQuotaAccepted: report.receipt?.observed?.storage?.duplicateBudgetFirstAccepted === true && report.receipt?.observed?.storage?.duplicateBudgetFirstCompletedAtFullQuota === true && report.receipt?.observed?.storage?.duplicateBudgetSecondAcceptedAtFullQuota === true && report.receipt?.observed?.storage?.duplicateBudgetSecondReservedZero === true && report.receipt?.observed?.storage?.duplicateBudgetAfterDrainStableUsage === true && report.receipt?.observed?.storage?.duplicateBudgetHintObserved === true,
      externalCancelReservationReconciled: report.receipt?.observed?.storage?.externalCancelSecondAcceptedAfterReconcile === true && report.receipt?.observed?.storage?.externalCancelNoStaleReservationReject === true && report.receipt?.observed?.storage?.externalCancelReleasedAfterDrain === true,
      duplicateHintCleanupOnDelete: report.receipt?.observed?.storage?.hintCleanupDeleteClearedHint === true && report.receipt?.observed?.storage?.hintCleanupNoStaleHintAfterDelete === true,
      telemetryCleanupScheduled: report.receipt?.observed?.storage?.telemetryCleanupEstimateUsageVisible === true && report.receipt?.observed?.storage?.telemetryCleanupSnapshotVisible === true && report.receipt?.observed?.storage?.telemetryCleanupCleanupDeleted === true && report.receipt?.observed?.storage?.telemetryCleanupFinalEmpty === true,
      sharedSchedulerForeignHeadFairness: report.receipt?.observed?.storage?.sharedSchedulerForeignHeadBlocksOwnedDispatch === true && report.receipt?.observed?.storage?.sharedSchedulerForeignAndOwnedStillQueuedWhileBlocked === true && report.receipt?.observed?.storage?.sharedSchedulerNoOwnedMutationWhileForeignHead === true && report.receipt?.observed?.storage?.sharedSchedulerFilteredHeadBlockCounted === true && report.receipt?.observed?.storage?.sharedSchedulerForeignCompletedByOwner === true && report.receipt?.observed?.storage?.sharedSchedulerOwnedDispatchAfterForeignComplete === true && report.receipt?.observed?.storage?.sharedSchedulerNoForeignAdapterError === true,
      sharedSchedulerBlockedDiagnostics: report.receipt?.observed?.storage?.sharedSchedulerBlockedLastDispatchVisible === true && report.receipt?.observed?.storage?.sharedSchedulerBlockedForeignHeadIdentified === true && report.receipt?.observed?.storage?.sharedSchedulerBlockedDispatchReobserved === true && report.receipt?.observed?.storage?.sharedSchedulerBlockedDispatchStatsVisible === true && report.receipt?.observed?.storage?.sharedSchedulerBlockedStatePrunedAfterOwnerComplete === true,
      abortedPutNoMutation: report.receipt?.observed?.storage?.abortedPutNoMutation === true && report.receipt?.observed?.storage?.abortedPutDisposition === 'aborted-before-mutation',
      dropOldestBackpressureCounted: report.receipt?.observed?.channel?.dropOldestReceivedFreshWork === true && report.receipt?.observed?.channel?.dropOldestDroppedCount === 1,
      traceReceiptClosed: report.receipt?.proof?.traceReceiptClosed === true
    }),
    nonClaims: report.nonClaims
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  try {
    const report = await runProbe();
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-runtime-core-consumer-probe`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[runtime_core_consumer_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
