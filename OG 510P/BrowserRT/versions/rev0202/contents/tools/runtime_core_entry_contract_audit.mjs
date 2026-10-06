#!/usr/bin/env node
// Manifest slice: facility:runtime-core-entry-contract-audit. Fail-closed audit for BrowserRT's slim runtime-core package subpath.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, join, normalize } from 'node:path';
import { REVISION, VERSION, BROWSERRT_RUNTIME_CORE_EXPORTS } from '../src/runtime-core-public.mjs';

const REVISION_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${REVISION_PREFIX}-RUNTIME-CORE-ENTRY-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));
const LIMITS = Object.freeze({ closureBytesMax: 128_500, closureFileCountMax: 7, entryBytesMax: 40_000 });
const FORBIDDEN_CLOSURE = Object.freeze([
  'src/browserrt.mjs',
  'src/product-wedge.mjs',
  'src/block-store-lane-adapter.mjs',
  'src/storage-lane-scheduler.mjs',
  'src/kernel-kit-demo.mjs',
  'src/kernel-kit-demo-observatory.mjs',
  'src/kernel-kit-demo-usefulness.mjs',
  'src/kernel-kit-handoff-markdown.mjs',
  'src/kernel-kit-handoff-reader.mjs',
  'src/kernel-kit-readiness-gate.mjs',
  'src/kernel-kit-readiness-contrast.mjs',
  'src/kernel-kit-lifecycle-checkpoint.mjs',
  'src/kernel-kit-session-coordination-checkpoint.mjs',
  'src/kernel-kit-recovery-checkpoint.mjs',
  'src/kernel-kit-admission-cancellation-checkpoint.mjs',
  'src/project-assessment.mjs',
  'src/dream-boundary.mjs',
  'src/agent-worker.mjs',
  'src/node-agent-worker.mjs',
  'src/browser-agent-worker.mjs'
]);

function importSpecifiers(source) {
  const specs = [];
  for (const match of source.matchAll(/(?:import|export)\s+(?:[^'";]*?\s+from\s+)?['"](\.\.?\/[^'"]+)['"]/g)) specs.push(match[1]);
  for (const match of source.matchAll(/import\(\s*['"](\.\.?\/[^'"]+)['"]\s*\)/g)) specs.push(match[1]);
  return specs;
}

function resolveRelative(fromRel, spec) {
  const base = fromRel.split('/').slice(0, -1).join('/');
  let resolved = normalize(join(base, spec)).replace(/\\/g, '/');
  if (!resolved.startsWith('src/')) return null;
  if (!/\.[cm]?js$/.test(resolved)) resolved += '.mjs';
  return resolved;
}

async function staticClosure(entry) {
  const seen = new Set();
  const queue = [entry];
  const files = [];
  while (queue.length) {
    const rel = queue.shift();
    if (!rel || seen.has(rel)) continue;
    seen.add(rel);
    const source = await readFile(rel, 'utf8');
    files.push(Object.freeze({ path: rel, bytes: Buffer.byteLength(source, 'utf8'), imports: importSpecifiers(source) }));
    for (const spec of importSpecifiers(source)) {
      const child = resolveRelative(rel, spec);
      if (child && !seen.has(child)) queue.push(child);
    }
  }
  return files.sort((a, b) => a.path.localeCompare(b.path));
}

function check(name, ok, details = {}) { return Object.freeze({ name, status: ok ? 'passed' : 'failed', ...details }); }

export async function runAudit() {
  const pkg = await readJson('package.json');
  const manifest = await readJson('test/manifest.json');
  const entry = 'src/runtime-core-public.mjs';
  const entryTypes = 'src/runtime-core-public.d.ts';
  const entryText = await readFile(entry, 'utf8');
  const entryTypeText = await readFile(entryTypes, 'utf8');
  const exampleText = await readFile('examples/runtime-core-consumer.mjs', 'utf8');
  const packageSmokeText = await readFile('tools/package_installed_consumer_smoke_probe.mjs', 'utf8');
  const laneAdapterText = await readFile('src/runtime-core-lane-adapter.mjs', 'utf8');
  const schedulerText = await readFile('src/cross-lane-scheduler.mjs', 'utf8');
  const closure = await staticClosure(entry);
  const closurePaths = closure.map((file) => file.path);
  const closureBytes = closure.reduce((sum, file) => sum + file.bytes, 0);
  const forbiddenPresent = FORBIDDEN_CLOSURE.filter((path) => closurePaths.includes(path));
  const ids = new Set((manifest.tasks || []).map((task) => task.id));
  const namespace = await import('../src/runtime-core-public.mjs');
  const actualExports = Object.keys(namespace).sort();
  const expectedExports = BROWSERRT_RUNTIME_CORE_EXPORTS.slice().sort();
  const checks = [
    check('package-runtime-core-subpath-exported', pkg.exports?.['./runtime-core']?.import === './src/runtime-core-public.mjs' && pkg.exports?.['./runtime-core']?.types === './src/runtime-core-public.d.ts', { export: pkg.exports?.['./runtime-core'] || null }),
    check('runtime-core-entry-does-not-import-root-monolith', !entryText.includes("from './browserrt.mjs'") && !entryText.includes('src/browserrt.mjs') && forbiddenPresent.length === 0, { forbiddenPresent, closurePaths }),
    check('runtime-core-product-wedge-helper-decoupled', !entryText.includes('product-wedge') && !closurePaths.includes('src/product-wedge.mjs') && !actualExports.includes('createBrowserRtProductWedgeReceipt'), { actualExports, closurePaths }),
    check('runtime-core-closure-byte-budget', closureBytes <= LIMITS.closureBytesMax, { actual: closureBytes, limit: LIMITS.closureBytesMax }),
    check('runtime-core-closure-file-count-budget', closure.length <= LIMITS.closureFileCountMax, { actual: closure.length, limit: LIMITS.closureFileCountMax }),
    check('runtime-core-entry-byte-budget', Buffer.byteLength(entryText, 'utf8') <= LIMITS.entryBytesMax, { actual: Buffer.byteLength(entryText, 'utf8'), limit: LIMITS.entryBytesMax }),
    check('runtime-core-export-set-closed', JSON.stringify(actualExports) === JSON.stringify(expectedExports), { actualExports, expectedExports }),
    check('runtime-core-declaration-present', entryTypeText.includes('BrowserRtRuntimeCore') && entryTypeText.includes('bootRuntimeCore') && !entryTypeText.includes("from './types.js'"), { entryTypes }),
    check('runtime-core-example-uses-subpath-source-entry', exampleText.includes('../src/runtime-core-public.mjs') && exampleText.includes('rootEntryAvoided') && exampleText.includes('storageLaneWriteRead'), { example: 'examples/runtime-core-consumer.mjs' }),
    check('runtime-core-light-lane-adapter-split', entryText.includes("'./runtime-core-lane-adapter.mjs'") && closurePaths.includes('src/runtime-core-lane-adapter.mjs') && !closurePaths.includes('src/block-store-lane-adapter.mjs') && !closurePaths.includes('src/storage-lane-scheduler.mjs'), { closurePaths }),
    check('runtime-core-memory-store-abort-no-mutation-guard', entryText.includes('throwIfRuntimeCoreAborted(fields') && entryText.includes('throwIfRuntimeCoreAborted(options') && exampleText.includes('abortedPutNoMutation') && exampleText.includes('aborted-before-mutation'), { guard: 'pre-aborted put must throw before memory store mutation and before stats mutation' }),
    check('runtime-core-light-scheduled-abort-no-mutation-guard', exampleText.includes('scheduledAbortRejectedBeforeEnqueue') && exampleText.includes('scheduledAbortQueueNeverFilled') && exampleText.includes('scheduledAbortNoMutation') && exampleText.includes("providerOptions: { signal: scheduledAbortController.signal }"), { guard: 'pre-aborted scheduled work must reject before enqueue and mutate neither scheduler queue nor memory store' }),
    check('runtime-core-light-queued-abort-cancel-guard', laneAdapterText.includes('#registerQueuedAbortCancel') && laneAdapterText.includes('cancelled-aborted-before-dispatch') && schedulerText.includes('cancelQueued(taskId') && schedulerText.includes('cancelledTaskIds') && exampleText.includes('queuedAbortCancelledBeforeDispatch') && exampleText.includes("providerOptions: { signal: queuedAbortController.signal }"), { guard: 'abort after accepted scheduling but before dispatch must cancel queued work instead of wasting queue capacity until later provider failure' }),
    check('runtime-core-light-close-cancels-queued-no-mutation-guard', laneAdapterText.includes('#ownedQueuedTaskIds') && laneAdapterText.includes('cancelled-close-before-dispatch') && laneAdapterText.includes('dispatch-closed') && exampleText.includes('closeAbortCancelledBeforeDispatch') && exampleText.includes('closeAbortNoMutation') && exampleText.includes('closeAbortScheduleAfterClose'), { guard: 'adapter close before dispatch must cancel owned queued work, leave the memory store untouched, and reject later scheduling' }),
    check('runtime-core-light-quota-preflight-no-queue-guard', laneAdapterText.includes('storeBudgetPreflight') && laneAdapterText.includes('rejected-store-budget-before-schedule') && laneAdapterText.includes('quotaPreflightRejects') && exampleText.includes('quotaPreflightRejectedBeforeEnqueue') && exampleText.includes('quotaPreflightQueueNeverFilled') && exampleText.includes('quotaPreflightNoMutation'), { guard: 'obviously over-budget runtime-core put must reject before scheduler enqueue and before provider quota rejection/stats mutation' }),
    check('runtime-core-light-quota-reservation-no-over-admission-guard', laneAdapterText.includes('#reservedPutBytes') && laneAdapterText.includes('#putReservations') && laneAdapterText.includes('exceeds-reserved-store-budget') && laneAdapterText.includes('quotaReservationRejects') && exampleText.includes('quotaReservationSecondRejectedBeforeEnqueue') && exampleText.includes('quotaReservationRejectedOnPendingBytes') && exampleText.includes('quotaReservationReleasedAfterDrain') && packageSmokeText.includes('quotaReservationNoOverAdmission'), { guard: 'pending runtime-core put bytes must reserve store budget so later puts cannot over-admit into queue capacity before the first put dispatches' }),
    check('runtime-core-light-duplicate-budget-full-quota-guard', entryText.includes('estimatePutGrowth') && entryText.includes('duplicateBudgetHits') && laneAdapterText.includes('storePutGrowthEstimate') && laneAdapterText.includes('growthBytes') && laneAdapterText.includes('duplicateBudget') && exampleText.includes('duplicateBudgetSecondAcceptedAtFullQuota') && exampleText.includes('duplicateBudgetAfterDrainStableUsage') && packageSmokeText.includes('duplicateBudgetFullQuotaAccepted'), { guard: 'known immutable string duplicate puts at full local quota must be admitted with zero growth reservation instead of rejected as wasteful new storage growth' }),
    check('runtime-core-light-external-cancel-reservation-reconcile-guard', laneAdapterText.includes('#reconcileExternallyCancelledQueued') && laneAdapterText.includes('externalQueuedCancelsReconciled') && laneAdapterText.includes('BRT_RUNTIME_CORE_EXTERNAL_QUEUED_CANCELLED') && exampleText.includes('externalCancelSecondAcceptedAfterReconcile') && exampleText.includes('externalCancelNoStaleReservationReject') && packageSmokeText.includes('externalCancelReservationReconciled'), { guard: 'externally cancelled adapter-owned queued work must release put reservations before later store-budget admission runs' }),
    check('runtime-core-memory-store-duplicate-hint-delete-cleanup-guard', entryText.includes('#forgetDuplicateHintsForDigest') && entryText.includes('duplicateHintsCleared') && exampleText.includes('hintCleanupDeleteClearedHint') && exampleText.includes('hintCleanupNoStaleHintAfterDelete') && packageSmokeText.includes('duplicateHintCleanupOnDelete'), { guard: 'duplicate-budget hints must be cleared when their backing content-addressed block is deleted or cleaned up' }),
    check('runtime-core-light-scheduled-telemetry-cleanup-guard', laneAdapterText.includes('scheduleEstimate') && laneAdapterText.includes('scheduleSnapshot') && laneAdapterText.includes('scheduleCleanupForTest') && laneAdapterText.includes('submit(op') && exampleText.includes('telemetryCleanupEstimateUsageVisible') && exampleText.includes('telemetryCleanupCleanupDeleted') && packageSmokeText.includes('telemetryCleanupScheduled'), { guard: 'runtime-core light adapter must expose scheduled estimate/snapshot/cleanup and submit parity so consumers can inspect and clean storage through the bounded lane path' }),
    check('runtime-core-light-shared-scheduler-owner-filter-guard', schedulerText.includes('#dispatchFilter') && schedulerText.includes('preserveFilteredLaneHead') && schedulerText.includes('blocked-dispatch-filter-head') && laneAdapterText.includes('metadataComponent: RUNTIME_CORE_BLOCK_STORE_COMPONENT') && laneAdapterText.includes('preserveFilteredLaneHead: true') && exampleText.includes('sharedSchedulerForeignHeadBlocksOwnedDispatch') && exampleText.includes('sharedSchedulerNoOwnedMutationWhileForeignHead') && packageSmokeText.includes('sharedSchedulerForeignHeadFairness'), { guard: 'runtime-core adapter dispatch must filter for its own scheduled storage work while respecting a foreign task at the lane head, so shared-scheduler owners are not silently leapfrogged by the adapter' }),
    check('runtime-core-light-shared-scheduler-blocked-diagnostics-guard', laneAdapterText.includes('#lastDispatch') && laneAdapterText.includes('#blockedDispatches') && laneAdapterText.includes('#recordBlockedDispatches') && laneAdapterText.includes('#pruneBlockedDispatches') && laneAdapterText.includes('const blockedDispatches = this.#blockedDispatchSnapshot()') && exampleText.includes('sharedSchedulerBlockedDispatchReobserved') && exampleText.includes('sharedSchedulerBlockedStatePrunedAfterOwnerComplete') && packageSmokeText.includes('sharedSchedulerBlockedDiagnostics'), { guard: 'when runtime-core dispatch is blocked by a foreign lane head, the adapter snapshot must make repeated blockers visible and prune the stale blocker after the foreign owner completes, so consumers do not see an unexplained empty drain forever' }),
    check('runtime-core-drop-oldest-backpressure-counted', entryText.includes('#droppedCount += 1') && exampleText.includes('dropOldestDroppedCount') && exampleText.includes("overflow: 'drop-oldest'"), { guard: 'drop-oldest overflow must be observable in channel snapshot' }),
    check('package-installed-smoke-runs-runtime-core-subpath', packageSmokeText.includes("from 'browserrt/runtime-core'") && packageSmokeText.includes('runRuntimeCoreConsumerWithApi') && packageSmokeText.includes('runtimeCoreSubpath'), { packageSmoke: 'tools/package_installed_consumer_smoke_probe.mjs' }),
    check('audit-and-probe-registered', ids.has('facility:runtime-core-entry-contract-audit') && ids.has('product:runtime-core-consumer-proof') && String(pkg.scripts?.['audit:runtime-core-entry'] || '').includes('runtime_core_entry_contract_audit.mjs') && String(pkg.scripts?.['test:runtime-core-entry'] || '').includes('runtime_core_consumer_probe.mjs'))
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  assert.deepEqual(failed.map((row) => row.name), [], `runtime-core entry contract failed: ${failed.map((row) => row.name).join(', ')}`);
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    status: 'passed',
    audit_id: `${REVISION}-runtime-core-entry-contract-audit`,
    purpose: 'Fail-closed audit for the browserrt/runtime-core package subpath: a small adoption entry must avoid the root BrowserRT monolith, product-wedge proof helper, the full block-store lane adapter, and storage-lane timeout/quarantine/recovery closure while still proving admission, pre-aborted no-mutation storage behavior, counted backpressure, light scheduler-backed storage-lane work, pre-enqueue abort rejection, queued-abort cancellation before dispatch, close-before-dispatch queued cancellation, store-budget preflight rejection before queue admission, pending-put reservation rejection before over-admission, duplicate-aware full-quota string payload admission, external queued-cancel reservation reconciliation, duplicate-hint cleanup after delete, scheduled telemetry cleanup, shared-scheduler foreign-head fairness preservation, and reobserved/pruned blocked-dispatch diagnostics.',
    packageSubpath: './runtime-core',
    entry,
    closure: Object.freeze({ fileCount: closure.length, bytes: closureBytes, files: closure }),
    limits: LIMITS,
    forbiddenClosure: FORBIDDEN_CLOSURE,
    checks,
    nonClaims: Object.freeze([
      'Runtime-core entry audit proves only the local static import closure and consumer smoke path; it does not prove bundler tree-shaking, package publication, browser OPFS, Web Locks, durable browser quota reservation, eviction survival, cross-browser behavior, fsync durability, crash recovery, or the full root BrowserRT facade.',
      'The root package entry remains compatibility-heavy in this revision; this subpath is an adoption escape hatch and a ratchet for later root splitting. The runtime-core light adapter intentionally omits timeout quarantine/recovery machinery and product-wedge proof helpers.'
    ])
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  try {
    const report = await runAudit();
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-runtime-core-entry-contract-audit`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[runtime_core_entry_contract_audit] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
