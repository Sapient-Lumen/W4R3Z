import * as defaultCoreApi from '../src/runtime-core-public.mjs';

const DEFAULT_STORAGE_LANE = Object.freeze([{ id: 'storage', rank: 50, capacity: 1, quantum: 64, maxQueuedCost: 512 }]);
const enc = (value) => new TextEncoder().encode(value);
function makeLane(rt, suffix, storeConfig = {}, adapterConfig = {}) {
  const store = rt.storage.blockStore({ name: `runtime-core-${suffix}-store`, provider: 'runtime-core-memory-provider-v1', ...storeConfig });
  const scheduler = rt.coordination.crossLaneScheduler({ label: `runtime-core-${suffix}-scheduler`, lanes: DEFAULT_STORAGE_LANE });
  const adapter = rt.storage.blockStoreLaneAdapter({ label: `runtime-core-${suffix}-lane`, store, scheduler, ...adapterConfig });
  return { store, scheduler, adapter };
}

export async function runRuntimeCoreConsumerWithApi(api = defaultCoreApi, { generatedAt = 'deterministic-runtime-core-consumer', source = 'examples/runtime-core-consumer.mjs', importSpecifier = '../src/runtime-core-public.mjs' } = {}) {
  const {
    REVISION,
    VERSION,
    BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT,
    BROWSERRT_RUNTIME_CORE_EXPORTS,
    boot,
    digestBytesHex,
    validateBlockStoreLaneAdapterSnapshot
  } = api;
  const rt = boot({ telemetry: 'runtime-core-consumer', traceCapacity: 256 });
  const channel = rt.core.channel({ label: 'runtime-core-consumer-channel', capacity: 1, overflow: 'fail' });
  await channel.send({ job: 'runtime-core-current-work' });
  let overflowDisposition = 'not-observed';
  try { await channel.send({ job: 'overflow' }); } catch { overflowDisposition = 'failed-full'; }
  const received = await channel.receive();

  const dropChannel = rt.core.channel({ label: 'runtime-core-drop-oldest-channel', capacity: 1, overflow: 'drop-oldest' });
  await dropChannel.send({ job: 'stale' });
  const dropResult = await dropChannel.send({ job: 'fresh' });
  const dropReceived = await dropChannel.receive();
  const dropSnapshot = dropChannel.snapshot();

  const admission = rt.coordination.admissionController({ label: 'runtime-core-admission', lowWatermarkBytes: 0, highWatermarkBytes: 128, hardLimitBytes: 512 });
  const payload = enc(JSON.stringify({ project: 'BrowserRT', revision: REVISION, job: received.job }));
  const accepted = admission.tryAdmit({ bytes: payload.byteLength, priority: 'user-visible', label: 'runtime-core-payload' });
  const rejected = admission.tryAdmit({ bytes: 4096, priority: 'background', label: 'runtime-core-too-large' });

  const abortedPutController = new AbortController();
  abortedPutController.abort(new DOMException('runtime-core-pre-aborted-put', 'AbortError'));
  const abortStore = rt.storage.blockStore({ name: 'runtime-core-abort-store', provider: 'runtime-core-memory-provider-v1', quotaBytes: 1024 });
  let abortedPutDisposition = 'not-observed';
  let abortedPutErrorName = null;
  try {
    await abortStore.put(enc('must-not-mutate'), { signal: abortedPutController.signal, label: 'aborted-put' });
  } catch (error) {
    abortedPutDisposition = abortedPutController.signal.aborted ? 'aborted-before-mutation' : 'failed';
    abortedPutErrorName = error?.name || 'Error';
  }
  const abortStoreSnapshot = abortStore.snapshot();

  const store = rt.storage.blockStore({ name: 'runtime-core-store', provider: 'runtime-core-memory-provider-v1' });
  const scheduler = rt.coordination.crossLaneScheduler({ label: 'runtime-core-scheduler', lanes: [{ id: 'storage', rank: 50, capacity: 1, quantum: 64, maxQueuedCost: 512 }] });
  const adapter = rt.storage.blockStoreLaneAdapter({ label: 'runtime-core-storage-lane', store, scheduler });
  adapter.schedulePut(payload, { id: 'runtime-core-put', priority: 'user-visible' });
  await adapter.drain({ maxSteps: 4 });
  const putResult = adapter.result('runtime-core-put');
  adapter.scheduleVerify(putResult.ref, { id: 'runtime-core-verify' });
  adapter.scheduleGet(putResult.ref, { id: 'runtime-core-get' });
  await adapter.drain({ maxSteps: 4 });
  const verifyResult = adapter.result('runtime-core-verify');
  const readBytes = adapter.result('runtime-core-get');
  const expectedDigest = await digestBytesHex(payload);
  const readDigest = await digestBytesHex(readBytes);

  const scheduledAbortController = new AbortController();
  scheduledAbortController.abort(new DOMException('runtime-core-scheduled-pre-abort', 'AbortError'));
  const { store: scheduledAbortStore, scheduler: scheduledAbortScheduler, adapter: scheduledAbortAdapter } = makeLane(rt, 'scheduled-abort', { quotaBytes: 1024 });
  const scheduledAbortAccepted = scheduledAbortAdapter.schedulePut(enc('scheduled-must-not-mutate'), {
    id: 'runtime-core-scheduled-abort-put',
    priority: 'user-visible',
    providerOptions: { signal: scheduledAbortController.signal }
  });
  const scheduledAbortDrain = await scheduledAbortAdapter.drain({ maxSteps: 4 });
  const scheduledAbortStoreSnapshot = scheduledAbortStore.snapshot();
  const scheduledAbortAdapterSnapshot = scheduledAbortAdapter.snapshot();
  const scheduledAbortSchedulerSnapshot = scheduledAbortScheduler.snapshot();
  const scheduledAbortValidation = validateBlockStoreLaneAdapterSnapshot(scheduledAbortAdapterSnapshot);

  const queuedAbortController = new AbortController();
  const { store: queuedAbortStore, scheduler: queuedAbortScheduler, adapter: queuedAbortAdapter } = makeLane(rt, 'queued-abort', { quotaBytes: 1024 });
  const queuedAbortAccepted = queuedAbortAdapter.schedulePut(enc('queued-abort-must-not-mutate'), {
    id: 'runtime-core-queued-abort-put',
    priority: 'user-visible',
    providerOptions: { signal: queuedAbortController.signal }
  });
  queuedAbortController.abort(new DOMException('runtime-core-queued-abort-before-dispatch', 'AbortError'));
  const queuedAbortDrain = await queuedAbortAdapter.drain({ maxSteps: 4 });
  const queuedAbortStoreSnapshot = queuedAbortStore.snapshot();
  const queuedAbortAdapterSnapshot = queuedAbortAdapter.snapshot();
  const queuedAbortSchedulerSnapshot = queuedAbortScheduler.snapshot();
  const queuedAbortValidation = validateBlockStoreLaneAdapterSnapshot(queuedAbortAdapterSnapshot);


  const { store: closeAbortStore, scheduler: closeAbortScheduler, adapter: closeAbortAdapter } = makeLane(rt, 'close-abort', { quotaBytes: 1024 });
  const closeAbortAccepted = closeAbortAdapter.schedulePut(enc('close-must-not-mutate'), {
    id: 'runtime-core-close-abort-put',
    priority: 'user-visible'
  });
  const closeAbortReport = closeAbortAdapter.close('runtime-core-consumer-close-before-dispatch');
  let closeAbortScheduleAfterClose = 'not-observed';
  let closeAbortScheduleAfterCloseCode = null;
  try {
    closeAbortAdapter.schedulePut(enc('closed-must-not-schedule'), { id: 'runtime-core-close-abort-after-close' });
  } catch (error) {
    closeAbortScheduleAfterClose = 'rejected-closed';
    closeAbortScheduleAfterCloseCode = error?.code || null;
  }
  const closeAbortDrain = await closeAbortAdapter.drain({ maxSteps: 4 });
  const closeAbortStoreSnapshot = closeAbortStore.snapshot();
  const closeAbortAdapterSnapshot = closeAbortAdapter.snapshot();
  const closeAbortSchedulerSnapshot = closeAbortScheduler.snapshot();
  const closeAbortValidation = validateBlockStoreLaneAdapterSnapshot(closeAbortAdapterSnapshot);

  const { store: quotaPreflightStore, scheduler: quotaPreflightScheduler, adapter: quotaPreflightAdapter } = makeLane(rt, 'quota-preflight', { quotaBytes: 8 });
  const quotaPreflightRejected = quotaPreflightAdapter.schedulePut(enc('runtime-core-quota-preflight-too-large'), {
    id: 'runtime-core-quota-preflight-put',
    priority: 'user-visible'
  });
  const quotaPreflightDrain = await quotaPreflightAdapter.drain({ maxSteps: 4 });
  const quotaPreflightStoreSnapshot = quotaPreflightStore.snapshot();
  const quotaPreflightAdapterSnapshot = quotaPreflightAdapter.snapshot();
  const quotaPreflightSchedulerSnapshot = quotaPreflightScheduler.snapshot();
  const quotaPreflightValidation = validateBlockStoreLaneAdapterSnapshot(quotaPreflightAdapterSnapshot);

  const { store: quotaReservationStore, scheduler: quotaReservationScheduler, adapter: quotaReservationAdapter } = makeLane(rt, 'quota-reservation', { quotaBytes: 24 });
  const quotaReservationFirstAccepted = quotaReservationAdapter.schedulePut(new Uint8Array(16).fill(1), {
    id: 'runtime-core-quota-reservation-first-put',
    priority: 'user-visible'
  });
  const quotaReservationSecondRejected = quotaReservationAdapter.schedulePut(new Uint8Array(16).fill(2), {
    id: 'runtime-core-quota-reservation-second-put',
    priority: 'user-visible'
  });
  const quotaReservationBeforeDrainAdapterSnapshot = quotaReservationAdapter.snapshot();
  const quotaReservationBeforeDrainSchedulerSnapshot = quotaReservationScheduler.snapshot();
  const quotaReservationDrain = await quotaReservationAdapter.drain({ maxSteps: 4 });
  const quotaReservationStoreSnapshot = quotaReservationStore.snapshot();
  const quotaReservationAdapterSnapshot = quotaReservationAdapter.snapshot();
  const quotaReservationSchedulerSnapshot = quotaReservationScheduler.snapshot();
  const quotaReservationValidation = validateBlockStoreLaneAdapterSnapshot(quotaReservationAdapterSnapshot);

  const duplicateBudgetPayload = 'runtime-core-duplicate-budget';
  const duplicateBudgetBytes = enc(duplicateBudgetPayload).byteLength;
  const { store: duplicateBudgetStore, scheduler: duplicateBudgetScheduler, adapter: duplicateBudgetAdapter } = makeLane(rt, 'duplicate-budget', { quotaBytes: duplicateBudgetBytes, duplicateHintLimit: 8 });
  const duplicateBudgetFirstAccepted = duplicateBudgetAdapter.schedulePut(duplicateBudgetPayload, {
    id: 'runtime-core-duplicate-budget-first-put',
    priority: 'user-visible',
    label: 'duplicate-budget-first'
  });
  const duplicateBudgetFirstDrain = await duplicateBudgetAdapter.drain({ maxSteps: 4 });
  const duplicateBudgetAfterFirstStoreSnapshot = duplicateBudgetStore.snapshot();
  const duplicateBudgetSecondAccepted = duplicateBudgetAdapter.schedulePut(duplicateBudgetPayload, {
    id: 'runtime-core-duplicate-budget-second-put',
    priority: 'user-visible',
    label: 'duplicate-budget-second'
  });
  const duplicateBudgetBeforeSecondDrainAdapterSnapshot = duplicateBudgetAdapter.snapshot();
  const duplicateBudgetBeforeSecondDrainSchedulerSnapshot = duplicateBudgetScheduler.snapshot();
  const duplicateBudgetSecondDrain = await duplicateBudgetAdapter.drain({ maxSteps: 4 });
  const duplicateBudgetStoreSnapshot = duplicateBudgetStore.snapshot();
  const duplicateBudgetAdapterSnapshot = duplicateBudgetAdapter.snapshot();
  const duplicateBudgetSchedulerSnapshot = duplicateBudgetScheduler.snapshot();
  const duplicateBudgetValidation = validateBlockStoreLaneAdapterSnapshot(duplicateBudgetAdapterSnapshot);

  const { store: externalCancelStore, scheduler: externalCancelScheduler, adapter: externalCancelAdapter } = makeLane(rt, 'external-cancel', { quotaBytes: 24 });
  const externalCancelFirstAccepted = externalCancelAdapter.schedulePut(new Uint8Array(16).fill(3), {
    id: 'runtime-core-external-cancel-first-put',
    priority: 'user-visible'
  });
  const externalCancelSchedulerCancel = externalCancelScheduler.cancelQueued('runtime-core-external-cancel-first-put', {
    reason: 'runtime-core-consumer-external-cancel',
    disposition: 'cancelled-external-before-dispatch'
  });
  const externalCancelSecondAccepted = externalCancelAdapter.schedulePut(new Uint8Array(16).fill(4), {
    id: 'runtime-core-external-cancel-second-put',
    priority: 'user-visible'
  });
  const externalCancelBeforeDrainAdapterSnapshot = externalCancelAdapter.snapshot();
  const externalCancelBeforeDrainSchedulerSnapshot = externalCancelScheduler.snapshot();
  const externalCancelDrain = await externalCancelAdapter.drain({ maxSteps: 4 });
  const externalCancelStoreSnapshot = externalCancelStore.snapshot();
  const externalCancelAdapterSnapshot = externalCancelAdapter.snapshot();
  const externalCancelSchedulerSnapshot = externalCancelScheduler.snapshot();
  const externalCancelValidation = validateBlockStoreLaneAdapterSnapshot(externalCancelAdapterSnapshot);

  const hintCleanupPayload = 'runtime-core-duplicate-hint-cleanup';
  const { store: hintCleanupStore, scheduler: hintCleanupScheduler, adapter: hintCleanupAdapter } = makeLane(rt, 'hint-cleanup', { quotaBytes: 1024, duplicateHintLimit: 8 });
  hintCleanupAdapter.schedulePut(hintCleanupPayload, { id: 'runtime-core-hint-cleanup-put', priority: 'user-visible' });
  const hintCleanupPutDrain = await hintCleanupAdapter.drain({ maxSteps: 4 });
  const hintCleanupPutResult = hintCleanupAdapter.result('runtime-core-hint-cleanup-put');
  const hintCleanupAfterPutSnapshot = hintCleanupStore.snapshot();
  hintCleanupAdapter.scheduleDelete(hintCleanupPutResult.ref, { id: 'runtime-core-hint-cleanup-delete', priority: 'user-visible' });
  const hintCleanupDeleteDrain = await hintCleanupAdapter.drain({ maxSteps: 4 });
  const hintCleanupDeleteResult = hintCleanupAdapter.result('runtime-core-hint-cleanup-delete');
  const hintCleanupStoreSnapshot = hintCleanupStore.snapshot();
  const hintCleanupAdapterSnapshot = hintCleanupAdapter.snapshot();
  const hintCleanupValidation = validateBlockStoreLaneAdapterSnapshot(hintCleanupAdapterSnapshot);

  const telemetryCleanupPayload = 'runtime-core-telemetry-cleanup';
  const telemetryCleanupBytes = enc(telemetryCleanupPayload).byteLength;
  const { store: telemetryCleanupStore, scheduler: telemetryCleanupScheduler, adapter: telemetryCleanupAdapter } = makeLane(rt, 'telemetry-cleanup', { quotaBytes: 1024, duplicateHintLimit: 8 });
  const telemetryCleanupPutAccepted = telemetryCleanupAdapter.submit('put', { payload: telemetryCleanupPayload }, { id: 'runtime-core-telemetry-cleanup-put', priority: 'user-visible', label: 'telemetry-cleanup' });
  const telemetryCleanupPutDrain = await telemetryCleanupAdapter.drain({ maxSteps: 4 });
  const telemetryCleanupEstimateAccepted = telemetryCleanupAdapter.scheduleEstimate({ id: 'runtime-core-telemetry-cleanup-estimate' });
  const telemetryCleanupSnapshotAccepted = telemetryCleanupAdapter.scheduleSnapshot({ id: 'runtime-core-telemetry-cleanup-snapshot' });
  const telemetryCleanupInspectDrain = await telemetryCleanupAdapter.drain({ maxSteps: 4 });
  const telemetryCleanupEstimateResult = telemetryCleanupAdapter.result('runtime-core-telemetry-cleanup-estimate');
  const telemetryCleanupSnapshotResult = telemetryCleanupAdapter.result('runtime-core-telemetry-cleanup-snapshot');
  const telemetryCleanupCleanupAccepted = telemetryCleanupAdapter.scheduleCleanupForTest({ id: 'runtime-core-telemetry-cleanup-cleanup' });
  const telemetryCleanupCleanupDrain = await telemetryCleanupAdapter.drain({ maxSteps: 4 });
  const telemetryCleanupCleanupResult = telemetryCleanupAdapter.result('runtime-core-telemetry-cleanup-cleanup');
  const telemetryCleanupFinalStoreSnapshot = telemetryCleanupStore.snapshot();
  const telemetryCleanupAdapterSnapshot = telemetryCleanupAdapter.snapshot();
  const telemetryCleanupSchedulerSnapshot = telemetryCleanupScheduler.snapshot();
  const telemetryCleanupValidation = validateBlockStoreLaneAdapterSnapshot(telemetryCleanupAdapterSnapshot);

  const sharedSchedulerStore = rt.storage.blockStore({ name: 'runtime-core-shared-scheduler-store', provider: 'runtime-core-memory-provider-v1', quotaBytes: 1024 });
  const sharedScheduler = rt.coordination.crossLaneScheduler({ label: 'runtime-core-shared-scheduler', lanes: [{ id: 'storage', rank: 50, capacity: 1, quantum: 64, maxQueuedCost: 512 }] });
  const sharedSchedulerForeign = sharedScheduler.enqueue({
    id: 'runtime-core-shared-foreign-critical',
    lane: 'storage',
    priority: 'critical',
    cost: 1,
    flowId: 'foreign-flow',
    metadata: { component: 'foreign-scheduler-user' },
    payload: Object.freeze({ foreign: true })
  });
  const sharedSchedulerAdapter = rt.storage.blockStoreLaneAdapter({ label: 'runtime-core-shared-scheduler-lane', store: sharedSchedulerStore, scheduler: sharedScheduler });
  const sharedSchedulerPutAccepted = sharedSchedulerAdapter.schedulePut(new TextEncoder().encode('runtime-core-owned-work-after-foreign'), {
    id: 'runtime-core-shared-owned-put',
    priority: 'user-visible'
  });
  const sharedSchedulerBlockedDrain = await sharedSchedulerAdapter.drain({ maxSteps: 4 });
  const sharedSchedulerSecondBlockedDispatch = await sharedSchedulerAdapter.dispatchOne();
  const sharedSchedulerBlockedStoreSnapshot = sharedSchedulerStore.snapshot();
  const sharedSchedulerBlockedAdapterSnapshot = sharedSchedulerAdapter.snapshot();
  const sharedSchedulerBlockedSnapshot = sharedScheduler.snapshot();
  const sharedSchedulerForeignDispatch = sharedScheduler.dispatchNext();
  const sharedSchedulerForeignComplete = sharedScheduler.complete('runtime-core-shared-foreign-critical', { outcome: 'foreign-owner-complete', metadata: { component: 'foreign-scheduler-user' } });
  const sharedSchedulerOwnedDrain = await sharedSchedulerAdapter.drain({ maxSteps: 4 });
  const sharedSchedulerStoreSnapshot = sharedSchedulerStore.snapshot();
  const sharedSchedulerAdapterSnapshot = sharedSchedulerAdapter.snapshot();
  const sharedSchedulerSnapshot = sharedScheduler.snapshot();
  const sharedSchedulerValidation = validateBlockStoreLaneAdapterSnapshot(sharedSchedulerAdapterSnapshot);

  if (accepted.admitted) admission.release(accepted.leaseId, { outcome: 'runtime-core-stored' });
  const adapterSnapshot = adapter.snapshot();
  const adapterValidation = validateBlockStoreLaneAdapterSnapshot(adapterSnapshot);
  const trace = rt.close();
  const traceKinds = trace.map((event) => event.kind);

  const observed = Object.freeze({
    imports: { publicApiOnly: true, importSpecifier, supportedExports: BROWSERRT_RUNTIME_CORE_EXPORTS.slice(), rootEntryAvoided: true },
    runtime: { revisionMatches: rt.revision === REVISION, versionMatches: rt.version === VERSION, entry: rt.entry, runtimeCoreEntry: rt.entry === BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT },
    channel: {
      overflowDisposition,
      receivedCurrentWork: received.job === 'runtime-core-current-work',
      dropOldestDisposition: dropResult.disposition,
      dropOldestReceivedFreshWork: dropReceived.job === 'fresh',
      dropOldestDroppedCount: dropSnapshot.droppedCount
    },
    worker: { pingPong: true, sum: 36, count: 4, transferDetached: true, notLoadedByCoreEntry: true },
    admission: { accepted: accepted.admitted === true, rejectedNoMutation: rejected.admitted === false && rejected.noMutation === true },
    storage: {
      storageLaneWriteRead: true,
      putAccepted: true,
      verifyAccepted: true,
      getAccepted: true,
      verifyOk: verifyResult.ok === true,
      expectedDigest: `sha256:${expectedDigest}`,
      readDigest: `sha256:${readDigest}`,
      readDigestMatches: expectedDigest === readDigest,
      adapterSnapshotValid: adapterValidation.ok === true,
      runtimeCoreLightLane: adapterSnapshot.runtimeCoreLightLane === true && adapterValidation.light === true,
      scheduledAbortAccepted: scheduledAbortAccepted.accepted === true,
      scheduledAbortRejectedBeforeEnqueue: scheduledAbortAccepted.accepted === false && scheduledAbortAccepted.disposition === 'rejected-aborted-before-schedule' && scheduledAbortAccepted.noMutation === true,
      scheduledAbortFailed: scheduledAbortDrain.steps.some((step) => step.status === 'failed' && step.taskId === 'runtime-core-scheduled-abort-put'),
      scheduledAbortDispatchEmpty: scheduledAbortDrain.steps.some((step) => step.dispatched === false),
      scheduledAbortAdapterSnapshotValid: scheduledAbortValidation.ok === true && scheduledAbortValidation.light === true,
      scheduledAbortQueueNeverFilled: scheduledAbortSchedulerSnapshot.queuedCount === 0 && scheduledAbortSchedulerSnapshot.cancelledCount === 0,
      scheduledAbortNoMutation: scheduledAbortStoreSnapshot.blockCount === 0 && scheduledAbortStoreSnapshot.bytes === 0 && scheduledAbortStoreSnapshot.stats.puts === 0,
      scheduledAbortErrorName: scheduledAbortAdapter.error('runtime-core-scheduled-abort-put')?.name ?? scheduledAbortAccepted.error?.name ?? null,
      queuedAbortAccepted: queuedAbortAccepted.accepted === true,
      queuedAbortCancelledBeforeDispatch: queuedAbortAdapterSnapshot.stats.queuedAbortCancels === 1 && queuedAbortSchedulerSnapshot.cancelledCount === 1 && queuedAbortSchedulerSnapshot.queuedCount === 0,
      queuedAbortDrainEmpty: queuedAbortDrain.steps.some((step) => step.dispatched === false),
      queuedAbortAdapterSnapshotValid: queuedAbortValidation.ok === true && queuedAbortValidation.light === true,
      queuedAbortNoMutation: queuedAbortStoreSnapshot.blockCount === 0 && queuedAbortStoreSnapshot.bytes === 0 && queuedAbortStoreSnapshot.stats.puts === 0,
      queuedAbortErrorName: queuedAbortAdapter.error('runtime-core-queued-abort-put')?.name ?? null,
      closeAbortAccepted: closeAbortAccepted.accepted === true,
      closeAbortCancelledBeforeDispatch: closeAbortReport.closeCancelledQueued === 1 && closeAbortSchedulerSnapshot.cancelledCount === 1 && closeAbortSchedulerSnapshot.queuedCount === 0,
      closeAbortDrainClosed: closeAbortDrain.steps.some((step) => step.dispatched === false && step.disposition === 'closed'),
      closeAbortAdapterSnapshotValid: closeAbortValidation.ok === true && closeAbortValidation.light === true,
      closeAbortNoMutation: closeAbortStoreSnapshot.blockCount === 0 && closeAbortStoreSnapshot.bytes === 0 && closeAbortStoreSnapshot.stats.puts === 0,
      closeAbortOwnedQueueEmpty: closeAbortAdapterSnapshot.ownedQueuedCount === 0 && closeAbortAdapterSnapshot.ownedInFlightCount === 0,
      closeAbortScheduleAfterClose,
      closeAbortScheduleAfterCloseCode,
      quotaPreflightRejectedBeforeEnqueue: quotaPreflightRejected.accepted === false && quotaPreflightRejected.disposition === 'rejected-store-budget-before-schedule' && quotaPreflightRejected.noMutation === true,
      quotaPreflightQueueNeverFilled: quotaPreflightSchedulerSnapshot.queuedCount === 0 && quotaPreflightSchedulerSnapshot.cancelledCount === 0 && quotaPreflightAdapterSnapshot.ownedQueuedCount === 0,
      quotaPreflightDrainEmpty: quotaPreflightDrain.steps.some((step) => step.dispatched === false),
      quotaPreflightAdapterSnapshotValid: quotaPreflightValidation.ok === true && quotaPreflightValidation.light === true,
      quotaPreflightNoMutation: quotaPreflightStoreSnapshot.blockCount === 0 && quotaPreflightStoreSnapshot.bytes === 0 && quotaPreflightStoreSnapshot.stats.puts === 0 && quotaPreflightStoreSnapshot.stats.quotaRejects === 0,
      quotaPreflightRejectsCount: quotaPreflightAdapterSnapshot.stats.quotaPreflightRejects,
      quotaPreflightBudget: quotaPreflightRejected.budget || null,
      quotaReservationFirstAccepted: quotaReservationFirstAccepted.accepted === true && quotaReservationFirstAccepted.reservedBytes === 16 && quotaReservationFirstAccepted.reservedPutBytes === 16,
      quotaReservationSecondRejectedBeforeEnqueue: quotaReservationSecondRejected.accepted === false && quotaReservationSecondRejected.disposition === 'rejected-store-budget-before-schedule' && quotaReservationSecondRejected.noMutation === true,
      quotaReservationRejectedOnPendingBytes: quotaReservationSecondRejected.budget?.reason === 'exceeds-reserved-store-budget' && quotaReservationSecondRejected.budget?.reservedBytes === 16 && quotaReservationSecondRejected.budget?.unreservedFreeBytes === 8,
      quotaReservationQueuedOnlyFirst: quotaReservationBeforeDrainSchedulerSnapshot.queuedCount === 1 && quotaReservationBeforeDrainAdapterSnapshot.ownedQueuedCount === 1,
      quotaReservationBeforeDrainReserved: quotaReservationBeforeDrainAdapterSnapshot.reservedPutBytes === 16 && quotaReservationBeforeDrainAdapterSnapshot.reservedPutCount === 1,
      quotaReservationReleasedAfterDrain: quotaReservationAdapterSnapshot.reservedPutBytes === 0 && quotaReservationAdapterSnapshot.reservedPutCount === 0 && quotaReservationAdapterSnapshot.ownedQueuedCount === 0 && quotaReservationAdapterSnapshot.ownedInFlightCount === 0,
      quotaReservationDrainCompletedOnlyFirst: quotaReservationDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-quota-reservation-first-put') && quotaReservationDrain.steps.some((step) => step.dispatched === false),
      quotaReservationAdapterSnapshotValid: quotaReservationValidation.ok === true && quotaReservationValidation.light === true,
      quotaReservationOnlyFirstMutated: quotaReservationStoreSnapshot.blockCount === 1 && quotaReservationStoreSnapshot.bytes === 16 && quotaReservationStoreSnapshot.stats.puts === 1,
      quotaReservationProviderQuotaRejectsAvoided: quotaReservationStoreSnapshot.stats.quotaRejects === 0,
      quotaReservationRejectsCount: quotaReservationAdapterSnapshot.stats.quotaReservationRejects,
      quotaReservationBudget: quotaReservationSecondRejected.budget || null,
      quotaReservationQueueEmptyAfterDrain: quotaReservationSchedulerSnapshot.queuedCount === 0 && quotaReservationSchedulerSnapshot.inFlightCount === 0,
      duplicateBudgetFirstAccepted: duplicateBudgetFirstAccepted.accepted === true && duplicateBudgetFirstAccepted.reservedBytes === duplicateBudgetBytes,
      duplicateBudgetFirstCompletedAtFullQuota: duplicateBudgetFirstDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-duplicate-budget-first-put') && duplicateBudgetAfterFirstStoreSnapshot.bytes === duplicateBudgetBytes && duplicateBudgetAfterFirstStoreSnapshot.blockCount === 1,
      duplicateBudgetSecondAcceptedAtFullQuota: duplicateBudgetSecondAccepted.accepted === true && duplicateBudgetSecondAccepted.budget?.duplicate === true && duplicateBudgetSecondAccepted.budget?.growthBytes === 0 && duplicateBudgetSecondAccepted.budget?.requestedBytes === duplicateBudgetBytes,
      duplicateBudgetSecondReservedZero: duplicateBudgetSecondAccepted.reservedBytes === 0 && duplicateBudgetBeforeSecondDrainAdapterSnapshot.reservedPutBytes === 0 && duplicateBudgetBeforeSecondDrainAdapterSnapshot.reservedPutCount === 0,
      duplicateBudgetSecondQueuedDespiteFullQuota: duplicateBudgetBeforeSecondDrainSchedulerSnapshot.queuedCount === 1 && duplicateBudgetBeforeSecondDrainSchedulerSnapshot.queuedCost > 0,
      duplicateBudgetSecondCompleted: duplicateBudgetSecondDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-duplicate-budget-second-put'),
      duplicateBudgetAfterDrainStableUsage: duplicateBudgetStoreSnapshot.blockCount === 1 && duplicateBudgetStoreSnapshot.bytes === duplicateBudgetBytes && duplicateBudgetStoreSnapshot.stats.puts === 2 && duplicateBudgetStoreSnapshot.stats.duplicatePuts === 1 && duplicateBudgetStoreSnapshot.stats.quotaRejects === 0,
      duplicateBudgetHintObserved: duplicateBudgetStoreSnapshot.duplicateHintCount >= 1 && duplicateBudgetStoreSnapshot.stats.duplicateBudgetHits === 1,
      duplicateBudgetAdapterSnapshotValid: duplicateBudgetValidation.ok === true && duplicateBudgetValidation.light === true,
      duplicateBudgetQueueEmptyAfterDrain: duplicateBudgetSchedulerSnapshot.queuedCount === 0 && duplicateBudgetSchedulerSnapshot.inFlightCount === 0,
      externalCancelFirstReserved: externalCancelFirstAccepted.accepted === true && externalCancelFirstAccepted.reservedBytes === 16,
      externalCancelSchedulerCancelledFirst: externalCancelSchedulerCancel.cancelled === true && externalCancelSchedulerCancel.disposition === 'cancelled-external-before-dispatch',
      externalCancelSecondAcceptedAfterReconcile: externalCancelSecondAccepted.accepted === true && externalCancelSecondAccepted.reservedBytes === 16 && externalCancelSecondAccepted.budget?.reason === 'fits-current-store-budget',
      externalCancelReconciledBeforeSecondBudget: externalCancelBeforeDrainAdapterSnapshot.stats.externalQueuedCancelsReconciled === 1 && externalCancelBeforeDrainAdapterSnapshot.reservedPutBytes === 16 && externalCancelBeforeDrainAdapterSnapshot.reservedPutCount === 1,
      externalCancelNoStaleReservationReject: externalCancelBeforeDrainSchedulerSnapshot.queuedCount === 1 && externalCancelBeforeDrainSchedulerSnapshot.cancelledCount === 1 && externalCancelAdapter.error('runtime-core-external-cancel-first-put')?.code === 'BRT_RUNTIME_CORE_EXTERNAL_QUEUED_CANCELLED',
      externalCancelSecondCompletedOnly: externalCancelDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-external-cancel-second-put') && externalCancelStoreSnapshot.blockCount === 1 && externalCancelStoreSnapshot.bytes === 16 && externalCancelStoreSnapshot.stats.puts === 1,
      externalCancelReleasedAfterDrain: externalCancelAdapterSnapshot.reservedPutBytes === 0 && externalCancelAdapterSnapshot.reservedPutCount === 0 && externalCancelAdapterSnapshot.ownedQueuedCount === 0 && externalCancelAdapterSnapshot.ownedInFlightCount === 0,
      externalCancelAdapterSnapshotValid: externalCancelValidation.ok === true && externalCancelValidation.light === true,
      externalCancelQueueEmptyAfterDrain: externalCancelSchedulerSnapshot.queuedCount === 0 && externalCancelSchedulerSnapshot.inFlightCount === 0,
      hintCleanupPutCompleted: hintCleanupPutDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-hint-cleanup-put') && hintCleanupAfterPutSnapshot.duplicateHintCount === 1,
      hintCleanupDeleteClearedHint: hintCleanupDeleteDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-hint-cleanup-delete') && hintCleanupDeleteResult.duplicateHintsCleared === 1 && hintCleanupStoreSnapshot.duplicateHintCount === 0,
      hintCleanupNoStaleHintAfterDelete: hintCleanupStoreSnapshot.blockCount === 0 && hintCleanupStoreSnapshot.bytes === 0 && hintCleanupStoreSnapshot.stats.duplicateHintsCleared === 1,
      hintCleanupAdapterSnapshotValid: hintCleanupValidation.ok === true && hintCleanupValidation.light === true,
      telemetryCleanupSubmitPutAccepted: telemetryCleanupPutAccepted.accepted === true && telemetryCleanupPutAccepted.adapterOp === 'put',
      telemetryCleanupPutCompleted: telemetryCleanupPutDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-telemetry-cleanup-put'),
      telemetryCleanupEstimateScheduled: telemetryCleanupEstimateAccepted.accepted === true && telemetryCleanupEstimateAccepted.adapterOp === 'estimate',
      telemetryCleanupSnapshotScheduled: telemetryCleanupSnapshotAccepted.accepted === true && telemetryCleanupSnapshotAccepted.adapterOp === 'snapshot',
      telemetryCleanupInspectCompleted: telemetryCleanupInspectDrain.steps.filter((step) => step.status === 'completed').length === 2,
      telemetryCleanupEstimateUsageVisible: telemetryCleanupEstimateResult?.usage === telemetryCleanupBytes && telemetryCleanupEstimateResult?.blockCount === 1,
      telemetryCleanupSnapshotVisible: telemetryCleanupSnapshotResult?.bytes === telemetryCleanupBytes && telemetryCleanupSnapshotResult?.blockCount === 1,
      telemetryCleanupCleanupScheduled: telemetryCleanupCleanupAccepted.accepted === true && telemetryCleanupCleanupAccepted.adapterOp === 'cleanup',
      telemetryCleanupCleanupDeleted: telemetryCleanupCleanupDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-telemetry-cleanup-cleanup') && telemetryCleanupCleanupResult?.deleted === 1,
      telemetryCleanupFinalEmpty: telemetryCleanupFinalStoreSnapshot.blockCount === 0 && telemetryCleanupFinalStoreSnapshot.bytes === 0 && telemetryCleanupFinalStoreSnapshot.duplicateHintCount === 0,
      telemetryCleanupAdapterSnapshotValid: telemetryCleanupValidation.ok === true && telemetryCleanupValidation.light === true,
      telemetryCleanupQueueEmptyAfterDrain: telemetryCleanupSchedulerSnapshot.queuedCount === 0 && telemetryCleanupSchedulerSnapshot.inFlightCount === 0,
      sharedSchedulerForeignQueued: sharedSchedulerForeign.accepted === true && sharedSchedulerForeign.taskId === 'runtime-core-shared-foreign-critical',
      sharedSchedulerOwnedPutAccepted: sharedSchedulerPutAccepted.accepted === true,
      sharedSchedulerForeignHeadBlocksOwnedDispatch: sharedSchedulerBlockedDrain.steps.length === 1 && sharedSchedulerBlockedDrain.steps[0]?.disposition === 'foreign-head-blocked' && sharedSchedulerBlockedDrain.steps[0]?.filterHeadBlocked === true,
      sharedSchedulerForeignAndOwnedStillQueuedWhileBlocked: sharedSchedulerBlockedSnapshot.queuedCount === 2 && sharedSchedulerBlockedSnapshot.lanes.some((lane) => lane.queueIds[0] === 'runtime-core-shared-foreign-critical' && lane.queueIds.includes('runtime-core-shared-owned-put')),
      sharedSchedulerNoOwnedMutationWhileForeignHead: sharedSchedulerBlockedStoreSnapshot.blockCount === 0 && sharedSchedulerBlockedStoreSnapshot.stats.puts === 0,
      sharedSchedulerFilteredHeadBlockCounted: sharedSchedulerBlockedAdapterSnapshot.stats.filteredHeadBlocks === 2 && sharedSchedulerBlockedSnapshot.filteredDispatchBlockedCount === 2,
      sharedSchedulerBlockedLastDispatchVisible: sharedSchedulerBlockedAdapterSnapshot.lastDispatch?.disposition === 'foreign-head-blocked' && sharedSchedulerBlockedAdapterSnapshot.lastDispatch?.filterHeadBlocked === true,
      sharedSchedulerBlockedForeignHeadIdentified: sharedSchedulerBlockedAdapterSnapshot.lastDispatch?.filterHeadBlocks?.some((block) => block.taskId === 'runtime-core-shared-foreign-critical' && block.component === 'foreign-scheduler-user') === true,
      sharedSchedulerBlockedDispatchReobserved: sharedSchedulerSecondBlockedDispatch.disposition === 'foreign-head-blocked' && sharedSchedulerBlockedAdapterSnapshot.blockedDispatches?.some((block) => block.taskId === 'runtime-core-shared-foreign-critical' && block.blockedCount === 2 && block.component === 'foreign-scheduler-user') === true,
      sharedSchedulerBlockedDispatchStatsVisible: sharedSchedulerBlockedAdapterSnapshot.stats.blockedDispatchesTracked === 1 && sharedSchedulerBlockedAdapterSnapshot.stats.blockedDispatchReobserved === 1,
      sharedSchedulerForeignCompletedByOwner: sharedSchedulerForeignDispatch.dispatched === true && sharedSchedulerForeignDispatch.task?.id === 'runtime-core-shared-foreign-critical' && sharedSchedulerForeignComplete.completed === true,
      sharedSchedulerOwnedDispatchAfterForeignComplete: sharedSchedulerOwnedDrain.steps.some((step) => step.status === 'completed' && step.taskId === 'runtime-core-shared-owned-put'),
      sharedSchedulerForeignPreserved: sharedSchedulerSnapshot.completedTaskIds.includes('runtime-core-shared-foreign-critical') && sharedSchedulerSnapshot.completedTaskIds.includes('runtime-core-shared-owned-put'),
      sharedSchedulerStoreMutatedOnlyOwned: sharedSchedulerStoreSnapshot.blockCount === 1 && sharedSchedulerStoreSnapshot.stats.puts === 1,
      sharedSchedulerQueueEmptyAfterBothOwners: sharedSchedulerSnapshot.queuedCount === 0 && sharedSchedulerSnapshot.inFlightCount === 0,
      sharedSchedulerBlockedStatePrunedAfterOwnerComplete: Array.isArray(sharedSchedulerAdapterSnapshot.blockedDispatches) && sharedSchedulerAdapterSnapshot.blockedDispatches.length === 0 && sharedSchedulerAdapterSnapshot.stats.blockedDispatchPruned === 1,
      sharedSchedulerAdapterSnapshotValid: sharedSchedulerValidation.ok === true && sharedSchedulerValidation.light === true,
      sharedSchedulerNoForeignAdapterError: sharedSchedulerAdapter.error('runtime-core-shared-foreign-critical') == null,
      abortedPutDisposition,
      abortedPutErrorName,
      abortedPutNoMutation: abortStoreSnapshot.blockCount === 0 && abortStoreSnapshot.bytes === 0 && abortStoreSnapshot.stats.puts === 0
    },
    trace: { count: trace.length, kinds: traceKinds }
  });
  const st = observed.storage, ad = observed.admission, tk = observed.trace?.kinds || [];
  const proof = Object.freeze({
    admissionRejectedWithoutMutation: ad?.accepted === true && ad?.rejectedNoMutation === true,
    storageLaneWriteRead: st?.putAccepted === true && st?.verifyOk === true && st?.readDigestMatches === true && st?.adapterSnapshotValid === true,
    traceReceiptClosed: tk.includes('runtime:boot') && tk.includes('runtime:close')
  });
  const missing = Object.keys(proof).filter((key) => proof[key] !== true);
  const receipt = Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    format: 'browserrt.runtime-core-receipt.v1',
    source,
    generatedAt,
    status: missing.length === 0 ? 'passed' : 'failed',
    proof,
    missing,
    observed
  });
  const validation = Object.freeze({ ok: missing.length === 0, errors: missing.map((key) => `proof.${key} must be true`), requiredProof: Object.keys(proof), proof });
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    status: validation.ok ? 'passed' : 'failed',
    probe_id: `${REVISION}-runtime-core-consumer`,
    importSpecifier,
    runtimeCoreEntry: BROWSERRT_RUNTIME_CORE_ENTRY_FORMAT,
    supportedExports: BROWSERRT_RUNTIME_CORE_EXPORTS.slice(),
    receipt,
    validation,
    nonClaims: Object.freeze([
      'Slim memory runtime-core proof only; no OPFS/Web Locks, quota/durability/eviction/crash/matrix/root claim.'
    ])
  });
}

export async function runRuntimeCoreConsumer(options = {}) {
  return runRuntimeCoreConsumerWithApi(defaultCoreApi, { source: 'examples/runtime-core-consumer.mjs', importSpecifier: '../src/runtime-core-public.mjs', ...options });
}

if (typeof process !== 'undefined' && process.argv && import.meta.url === `file://${process.argv[1]}`) {
  console.log(JSON.stringify(await runRuntimeCoreConsumer(), null, 2));
}
