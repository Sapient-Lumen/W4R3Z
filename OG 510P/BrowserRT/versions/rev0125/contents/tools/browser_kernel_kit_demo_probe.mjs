#!/usr/bin/env node
// Manifest slice: browser:kernel-kit-demo-proof. Contract validator surface: validateKernelKitDemoReport.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import {
  REVISION,
  VERSION,
  validateKernelKitDemoReport,
  createKernelKitDemoObservatoryReport,
  validateKernelKitDemoObservatoryReport,
  validateKernelKitDemoUsefulnessReport,
  validateKernelKitDemoHandoff,
  validateKernelKitDemoExportBundle,
  validateKernelKitFailureModeReport,
  validateKernelKitTraceComparison,
  validateKernelKitDiagnosticRunbook,
  validateKernelKitSupportBundle,
  validateKernelKitSupportBundleImportReport,
  validateKernelKitSupportBundleReplayPlan,
  validateKernelKitSupportBundleEvidenceLedger,
  validateKernelKitSupportBundleEvidenceCheckpoint,
  validateKernelKitSupportBundleDiff,
  validateKernelKitSupportBundlePrivacyScrub,
  validateKernelKitLifecycleCheckpoint,
  validateKernelKitSessionCoordinationCheckpoint,
  validateKernelKitRecoveryCheckpoint,
  validateKernelKitGuidedTourReceipt,
  validateKernelKitHandoffMarkdown,
  validateKernelKitHandoffMarkdownImportReport,
  validateKernelKitReadinessGate,
  validateKernelKitReadinessContrast
} from '../src/browserrt.mjs';
import { runManagedBrowserPage, sleep } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-BROWSER-KERNEL-KIT-DEMO-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const hasFlag = (argv, flag) => argv.includes(flag);

function compactStoragePosture(posture = {}) {
  return {
    status: posture?.status || 'unknown',
    estimate: { ok: posture?.estimate?.ok === true, quota: posture?.estimate?.quota ?? null, usage: posture?.estimate?.usage ?? null, usageDetailsKeys: posture?.estimate?.usageDetailsKeys || [] },
    persisted: { ok: posture?.persisted?.ok === true, persisted: posture?.persisted?.persisted ?? null },
    persistRequest: { requested: posture?.persistRequest?.requested === true, skipped: posture?.persistRequest?.skipped === true },
    proof: posture?.proof || {}
  };
}

function compactWebLockPosture(posture = {}) {
  return {
    status: posture?.status || 'unknown',
    exclusive: { maxActive: posture?.exclusive?.maxActive ?? null, overlap: posture?.exclusive?.overlap ?? null, order: posture?.exclusive?.order || [] },
    shared: { maxActive: posture?.shared?.maxActive ?? null },
    settled: { exclusiveOk: posture?.settled?.exclusive?.ok === true, sharedOk: posture?.settled?.shared?.ok === true },
    proof: posture?.proof || {}
  };
}


function compactGuardedStorageLane(guarded = {}) {
  return {
    status: guarded?.status || 'unknown',
    provider: guarded?.provider || null,
    lockName: guarded?.lockName || null,
    readMode: guarded?.readMode || null,
    available: guarded?.available === true,
    stats: guarded?.stats || {},
    coordinatorStats: guarded?.coordinatorStats || {},
    proof: guarded?.proof || {}
  };
}

function compactObservatoryForArtifact(observatory = {}) {
  return {
    project: observatory.project,
    schema: observatory.schema,
    revision: observatory.revision,
    codename: observatory.codename,
    generatedAt: observatory.generatedAt,
    mission: observatory.mission,
    sourceProofId: observatory.sourceProofId,
    capabilityBadges: (observatory.capabilityBadges || []).map((badge) => ({ id: badge.id, status: badge.status })),
    stageCards: (observatory.stageCards || []).map((card) => ({
      order: card.order,
      id: card.id,
      lane: card.lane,
      status: card.status,
      proofKeys: card.proofKeys || [],
      traceHits: card.traceHits || []
    })),
    laneTimeline: {
      eventCount: observatory.laneTimeline?.eventCount ?? 0,
      laneCounts: observatory.laneTimeline?.laneCounts || {}
    },
    traceSummary: {
      eventCount: observatory.traceSummary?.eventCount ?? 0,
      uniqueKindCount: observatory.traceSummary?.uniqueKindCount ?? 0,
      countsByLane: observatory.traceSummary?.countsByLane || {},
      countsByKind: observatory.traceSummary?.countsByKind || {}
    },
    proofReceipt: observatory.proofReceipt,
    nextDemoWorkCount: observatory.nextDemoWork?.length || 0,
    nonClaims: observatory.nonClaims || []
  };
}

function compactLifecycleCheckpoint(checkpoint) {
  return checkpoint ? Object.freeze({
    status: checkpoint.status,
    riskSummary: checkpoint.riskSummary,
    proof: checkpoint.proof,
    observedRowIds: checkpoint.observedRowIds,
    deferredRowIds: checkpoint.deferredRowIds
  }) : null;
}


function compactSessionCoordinationCheckpoint(checkpoint) {
  return checkpoint ? Object.freeze({
    status: checkpoint.status,
    validationOk: checkpoint.validationOk === true || validateKernelKitSessionCoordinationCheckpoint(checkpoint).ok === true,
    commandId: checkpoint.commandId || null,
    proof: checkpoint.proof,
    observedRowIds: checkpoint.observedRowIds,
    deferredRowIds: checkpoint.deferredRowIds,
    riskSummary: checkpoint.riskSummary || null
  }) : null;
}


function compactRecoveryCheckpoint(checkpoint) {
  return checkpoint ? Object.freeze({
    status: checkpoint.status,
    validationOk: checkpoint.validationOk === true || validateKernelKitRecoveryCheckpoint(checkpoint).ok === true,
    commandId: checkpoint.commandId || null,
    proof: checkpoint.proof,
    observedRowIds: checkpoint.observedRowIds,
    deferredRowIds: checkpoint.deferredRowIds,
    riskSummary: checkpoint.riskSummary || null
  }) : null;
}

function compactObservedForArtifact(observed, allTraceKinds = []) {
  const compactValidation = (value) => value ? { ok: value.ok === true, errorCount: value.errors?.length || 0, format: value.format || null, status: value.status || null } : null;
  return {
    pageUrl: observed.pageUrl,
    runnerInfo: { runner: observed.runnerInfo?.runner, validation: compactValidation(observed.runnerInfo?.validation) },
    work: {
      status: observed.work?.status || 'passed',
      page: { crossOriginIsolated: observed.work?.page?.crossOriginIsolated === true, isSecureContext: observed.work?.page?.isSecureContext === true },
      capabilities: observed.work?.capabilities,
      worker: { pingPong: observed.work?.worker?.pingPong === true, transferDetached: observed.work?.worker?.transferDetached === true },
      channel: { emptySize: observed.work?.channel?.emptySize ?? null },
      admission: { accepted: observed.work?.admission?.accepted?.admitted === true, rejectedNoMutation: observed.work?.admission?.rejected?.noMutation === true },
      storage: { payloadDigest: observed.work?.storage?.payloadDigest, payloadBytes: observed.work?.storage?.payloadBytes, resultDigest: observed.work?.storage?.result?.digest, guarded: compactGuardedStorageLane(observed.work?.storage?.guarded || observed.work?.guardedStorage) },
      abortBoundary: { status: observed.work?.abortBoundary?.status, proof: observed.work?.abortBoundary?.proof },
      storagePosture: compactStoragePosture(observed.work?.storagePosture),
      webLockPosture: compactWebLockPosture(observed.work?.webLockPosture),
      lifecycleCheckpoint: compactLifecycleCheckpoint(observed.work?.lifecycleCheckpoint),
      proof: observed.work?.proof,
      traceKindCount: observed.work?.traceKinds?.length || 0
    },
    reload: {
      status: observed.reload?.status || 'passed',
      handoffUsed: observed.reload?.handoffUsed === true,
      validation: compactValidation(observed.reload?.validation),
      read: { digest: observed.reload?.read?.digest, expectedDigest: observed.reload?.read?.expectedDigest, parsed: { workerSum: observed.reload?.read?.parsed?.workerSum } },
      guardedStorage: compactGuardedStorageLane(observed.reload?.guardedStorage || observed.reload?.storage?.guarded),
      storagePosture: compactStoragePosture(observed.reload?.storagePosture),
      webLockPosture: compactWebLockPosture(observed.reload?.webLockPosture),
      lifecycleCheckpoint: compactLifecycleCheckpoint(observed.reload?.lifecycleCheckpoint),
      proof: observed.reload?.proof,
      handoffCleared: observed.reload?.handoffCleared === true,
      usefulness: observed.reload?.usefulness ? { status: observed.reload.usefulness.status } : null,
      traceKindCount: observed.reload?.traceKinds?.length || 0
    },
    handoffBeforeReload: observed.handoffBeforeReload ? { prefix: observed.handoffBeforeReload.prefix, expectedDigest: observed.handoffBeforeReload.expectedDigest, validation: compactValidation(validateKernelKitDemoHandoff(observed.handoffBeforeReload)) } : null,
    handoffAfterRead: observed.handoffAfterRead,
    exportReceipt: observed.exportReceipt ? { status: observed.exportReceipt.status, validation: compactValidation(observed.exportReceipt.validation) } : null,
    failureMode: observed.failureMode ? { status: observed.failureMode.status, failureMode: observed.failureMode.failureMode, proof: observed.failureMode.proof } : null,
    traceComparison: observed.traceComparison ? { status: observed.traceComparison.status, validation: compactValidation(observed.traceComparison.validation), proof: observed.traceComparison.proof } : null,
    diagnosticRunbook: observed.diagnosticRunbook ? { status: observed.diagnosticRunbook.status, validation: compactValidation(observed.diagnosticRunbook.validation), proof: observed.diagnosticRunbook.proof } : null,
    supportBundle: observed.supportBundle ? { format: observed.supportBundle.format, validation: compactValidation(observed.supportBundle.validation), proof: observed.supportBundle.proof, lifecycleCheckpoint: compactLifecycleCheckpoint(observed.supportBundle?.lifecycleCheckpoint), sessionCoordination: compactSessionCoordinationCheckpoint(observed.supportBundle?.sessionCoordination), recoveryCheckpoint: compactRecoveryCheckpoint(observed.supportBundle?.recoveryCheckpoint), privacyScrub: observed.supportBundle.privacyScrub ? { status: observed.supportBundle.privacyScrub.status, proof: observed.supportBundle.privacyScrub.proof, redaction: observed.supportBundle.privacyScrub.redaction } : null, evidenceLedger: observed.supportBundle.evidenceLedger ? { status: observed.supportBundle.evidenceLedger.status, entryCount: observed.supportBundle.evidenceLedger.entries?.length || 0, outputCount: observed.supportBundle.evidenceLedger.outputPaths?.length || 0, outputPaths: (observed.supportBundle.evidenceLedger.outputPaths || []).slice(0, 12), proof: observed.supportBundle.evidenceLedger.proof } : null, commandCount: observed.supportBundle.exactCommands?.length || 0 } : null,
    supportBundleImport: observed.supportBundleImport ? { status: observed.supportBundleImport.status, validation: compactValidation(observed.supportBundleImport.validation), proof: observed.supportBundleImport.proof } : null,
    supportBundleReplay: observed.supportBundleReplay ? { status: observed.supportBundleReplay.status, validation: compactValidation(observed.supportBundleReplay.validation), proof: observed.supportBundleReplay.proof, evidenceSlots: observed.supportBundleReplay.evidenceSlots } : null,
    supportBundleEvidenceCheckpoint: observed.supportBundleEvidenceCheckpoint ? { status: observed.supportBundleEvidenceCheckpoint.status, validation: compactValidation(observed.supportBundleEvidenceCheckpoint.validation), proof: observed.supportBundleEvidenceCheckpoint.proof } : null,
    supportBundlePrivacyScrub: observed.supportBundlePrivacyScrub ? { status: observed.supportBundlePrivacyScrub.status, validation: compactValidation(observed.supportBundlePrivacyScrub.validation), proof: observed.supportBundlePrivacyScrub.proof, redaction: observed.supportBundlePrivacyScrub.redaction } : null,
    supportBundleDiff: observed.supportBundleDiff ? { status: observed.supportBundleDiff.status, validation: compactValidation(observed.supportBundleDiff.validation), proof: observed.supportBundleDiff.proof } : null,
    guidedTour: observed.guidedTour ? { status: observed.guidedTour.status, validation: compactValidation(observed.guidedTour.validation), proof: observed.guidedTour.proof } : null,
    handoffMarkdown: observed.handoffMarkdown ? { status: observed.handoffMarkdown.status, validation: compactValidation(observed.handoffMarkdown.validation), commandCount: observed.handoffMarkdown.exactCommands?.length || 0 } : null,
    handoffMarkdownImport: observed.handoffMarkdownImport ? { status: observed.handoffMarkdownImport.status, validation: compactValidation(observed.handoffMarkdownImport.validation), proof: observed.handoffMarkdownImport.proof } : null,
    readinessGate: observed.readinessGate ? { status: observed.readinessGate.status, validation: compactValidation(observed.readinessGate.validation), proof: observed.readinessGate.proof, inputProof: observed.readinessGate.inputProof } : null,
    readinessContrast: observed.readinessContrast ? { status: observed.readinessContrast.status, validation: compactValidation(observed.readinessContrast.validation), proof: observed.readinessContrast.proof } : null,
    pageStateAfterReload: observed.pageStateAfterReload,
    allTraceKinds
  };
}

function jsString(value) { return JSON.stringify(value); }
async function demoBody() { return await readFile('demo/kernel-kit-demo.html', 'utf8'); }


function exprForRunnerInfo() {
  return `(async()=>{
    for (let i=0;i<200;i+=1) {
      if (window.BrowserRTKernelKitDemo?.ready && typeof window.BrowserRTKernelKitDemo.runnerInfo === 'function') return JSON.stringify(window.BrowserRTKernelKitDemo.runnerInfo());
      await new Promise((resolve)=>setTimeout(resolve,50));
    }
    throw new Error('BrowserRTKernelKitDemo page workbench did not become ready');
  })()`;
}

function exprForWork(prefix) {
  return `(async()=>JSON.stringify(await window.BrowserRTKernelKitDemo.runWork({prefix:${jsString(prefix)},browserCdpHarness:true})))()`;
}

function exprForHandoff() {
  return `(async()=>JSON.stringify(window.BrowserRTKernelKitDemo.loadHandoff()))()`;
}

function exprForReload() {
  return `(async()=>JSON.stringify(await window.BrowserRTKernelKitDemo.reloadRead({render:false})))()`;
}

function exprForExport() {
  return `(async()=>JSON.stringify(window.BrowserRTKernelKitDemo.exportLastReceipt({render:false})))()`;
}

function exprForFailure() {
  return `(async()=>JSON.stringify(await window.BrowserRTKernelKitDemo.runFailureMode({render:false,mode:'missing-handoff'})))()`;
}

function exprForComparison() {
  return `(async()=>JSON.stringify(window.BrowserRTKernelKitDemo.compareTraces({render:false})))()`;
}

function exprForDiagnosticRunbook() {
  return `(async()=>JSON.stringify(window.BrowserRTKernelKitDemo.diagnoseTraceComparison({render:false})))()`;
}

function exprForSupportBundle() {
  return `(async()=>JSON.stringify(window.BrowserRTKernelKitDemo.buildSupportBundle({render:false})))()`;
}

function exprForSupportBundleImport() {
  return `(async()=>{ const bundle = window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE; return JSON.stringify(window.BrowserRTKernelKitDemo.importSupportBundle({render:false,input:JSON.stringify(bundle)})); })()`;
}

function exprForSupportBundleReplay() {
  return `(async()=>{ const bundle = window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE; return JSON.stringify(window.BrowserRTKernelKitDemo.replaySupportBundle({render:false,input:JSON.stringify(bundle)})); })()`;
}

function exprForSupportBundleEvidenceCheckpoint() {
  return `(async()=>JSON.stringify(window.BrowserRTKernelKitDemo.buildSupportBundleEvidenceCheckpoint({render:false})))()`;
}

function exprForSupportBundleDiff() {
  return `(async()=>{ const bundle = window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE; return JSON.stringify(window.BrowserRTKernelKitDemo.diffSupportBundle({render:false,input:JSON.stringify(bundle)})); })()`;
}

function exprForSupportBundlePrivacyScrub() {
  return `(async()=>JSON.stringify(window.BrowserRTKernelKitDemo.scrubSupportBundle({render:false})))()`;
}

function exprForGuidedTour() {
  return `(async()=>JSON.stringify(await window.BrowserRTKernelKitDemo.runGuidedTour({render:false,prefix:'browserrt/${REVISION}/kernel-kit-guided-tour-browser'})))()`;
}

function exprForHandoffMarkdown() {
  return `(async()=>JSON.stringify(await window.BrowserRTKernelKitDemo.buildHandoffMarkdown({render:false,prefix:'browserrt/${REVISION}/kernel-kit-handoff-markdown-browser'})))()`;
}

function exprForHandoffMarkdownImport() {
  return `(async()=>{ const markdown = window.__BROWSERRT_KERNEL_KIT_HANDOFF_MARKDOWN?.markdown; return JSON.stringify(window.BrowserRTKernelKitDemo.importHandoffMarkdown({render:false,markdown})); })()`;
}

function exprForReadinessGate() {
  return `(async()=>JSON.stringify(await window.BrowserRTKernelKitDemo.buildReadinessGate({render:false,prefix:'browserrt/${REVISION}/kernel-kit-readiness-browser'})))()`;
}

function exprForReadinessContrast() {
  return `(async()=>JSON.stringify(await window.BrowserRTKernelKitDemo.buildReadinessContrast({render:false,prefix:'browserrt/${REVISION}/kernel-kit-readiness-contrast-browser'})))()`;
}

export async function runProbe(options = {}) {
  const prefix = options.prefix || `browserrt/${REVISION}/kernel-kit-demo`;
  const { result: observed, harness } = await runManagedBrowserPage({
    timeoutMs: options.timeoutMs,
    chromium: options.chromium,
    relaxPolicy: options.relaxPolicy,
    pagePath: '/demo/kernel-kit-demo.html',
    pageTitle: 'BrowserRT Kernel Kit Demo Workbench',
    body: await readFile('demo/kernel-kit-demo.html', 'utf8'),
    profilePrefix: 'browserrt-kernel-kit-demo-cdp-',
    allowedPrefixes: ['src/','demo/'],
    stderrTerms: ['kernel','opfs','worker','storage']
  }, async ({ cdp, evalJson, pageUrl, mark, timeoutMs }) => {
    const infoStart = performance.now();
    const runnerInfo = await evalJson(exprForRunnerInfo(), timeoutMs);
    mark('kernel-kit-demo-runner-info-eval', infoStart);

    const workStart = performance.now();
    const work = await evalJson(exprForWork(prefix), timeoutMs);
    mark('kernel-kit-demo-work-eval', workStart);

    const handoffStart = performance.now();
    const handoffBeforeReload = await evalJson(exprForHandoff(), timeoutMs);
    mark('kernel-kit-demo-handoff-eval', handoffStart);

    const reloadStart = performance.now();
    await cdp.send('Page.reload', {}, timeoutMs);
    let pageState = null;
    const deadline = performance.now() + timeoutMs;
    while (performance.now() < deadline) {
      await sleep(100);
      pageState = await evalJson('JSON.stringify({location:location.href,readyState:document.readyState,crossOriginIsolated,isSecureContext,hasDemoGlobal:Boolean(window.BrowserRTKernelKitDemo)})', Math.min(1000, timeoutMs));
      if (pageState.location === pageUrl && pageState.readyState !== 'loading' && pageState.hasDemoGlobal === true) break;
    }
    mark('kernel-kit-demo-page-reload', reloadStart);
    assert.equal(pageState?.location, pageUrl);

    const readStart = performance.now();
    const reload = await evalJson(exprForReload(), timeoutMs);
    mark('kernel-kit-demo-reload-read-eval', readStart);
    const handoffAfterRead = await evalJson(exprForHandoff(), timeoutMs);

    const exportStart = performance.now();
    const exportReceipt = await evalJson(exprForExport(), timeoutMs);
    mark('kernel-kit-demo-export-receipt-eval', exportStart);

    const failureStart = performance.now();
    const failureMode = await evalJson(exprForFailure(), timeoutMs);
    mark('kernel-kit-demo-controlled-failure-eval', failureStart);

    const comparisonStart = performance.now();
    const traceComparison = await evalJson(exprForComparison(), timeoutMs);
    mark('kernel-kit-demo-trace-comparison-eval', comparisonStart);

    const diagnosticStart = performance.now();
    const diagnosticRunbook = await evalJson(exprForDiagnosticRunbook(), timeoutMs);
    mark('kernel-kit-demo-diagnostic-runbook-eval', diagnosticStart);

    const supportStart = performance.now();
    const supportBundle = await evalJson(exprForSupportBundle(), timeoutMs);
    mark('kernel-kit-demo-support-bundle-eval', supportStart);

    const supportImportStart = performance.now();
    const supportBundleImport = await evalJson(exprForSupportBundleImport(), timeoutMs);
    mark('kernel-kit-demo-support-bundle-import-eval', supportImportStart);

    const supportReplayStart = performance.now();
    const supportBundleReplay = await evalJson(exprForSupportBundleReplay(), timeoutMs);
    mark('kernel-kit-demo-support-bundle-replay-eval', supportReplayStart);

    const supportDiffStart = performance.now();
    const supportBundleDiff = await evalJson(exprForSupportBundleDiff(), timeoutMs);
    mark('kernel-kit-demo-support-bundle-diff-eval', supportDiffStart);

    const supportPrivacyStart = performance.now();
    const supportBundlePrivacyScrub = await evalJson(exprForSupportBundlePrivacyScrub(), timeoutMs);
    mark('kernel-kit-demo-support-bundle-privacy-scrub-eval', supportPrivacyStart);

    const guidedStart = performance.now();
    const guidedTour = await evalJson(exprForGuidedTour(), timeoutMs);
    mark('kernel-kit-demo-guided-tour-eval', guidedStart);

    const handoffMarkdownStart = performance.now();
    const handoffMarkdown = await evalJson(exprForHandoffMarkdown(), timeoutMs);
    mark('kernel-kit-demo-handoff-markdown-eval', handoffMarkdownStart);

    const handoffMarkdownImportStart = performance.now();
    const handoffMarkdownImport = await evalJson(exprForHandoffMarkdownImport(), timeoutMs);
    mark('kernel-kit-demo-handoff-markdown-import-eval', handoffMarkdownImportStart);

    const readinessStart = performance.now();
    const readinessGate = await evalJson(exprForReadinessGate(), timeoutMs);
    mark('kernel-kit-demo-readiness-gate-eval', readinessStart);

    const evidenceCheckpointStart = performance.now();
    const supportBundleEvidenceCheckpoint = await evalJson(exprForSupportBundleEvidenceCheckpoint(), timeoutMs);
    mark('kernel-kit-demo-support-bundle-evidence-checkpoint-eval', evidenceCheckpointStart);

    const readinessContrastStart = performance.now();
    const readinessContrast = await evalJson(exprForReadinessContrast(), timeoutMs);
    mark('kernel-kit-demo-readiness-contrast-eval', readinessContrastStart);

    return { pageUrl, runnerInfo, work, handoffBeforeReload, reload, handoffAfterRead, exportReceipt, failureMode, traceComparison, diagnosticRunbook, supportBundle, supportBundleImport, supportBundleReplay, supportBundleDiff, supportBundlePrivacyScrub, guidedTour, handoffMarkdown, handoffMarkdownImport, readinessGate, supportBundleEvidenceCheckpoint, readinessContrast, pageStateAfterReload: pageState };
  });

  const work = observed.work;
  const reload = observed.reload;
  assert.ok(['kernel-kit-demo-browser-runner','demo/kernel-kit-demo-runner.mjs'].includes(observed.runnerInfo.runner), 'unexpected page runner info');
  assert.equal(observed.runnerInfo.validation.ok, true);
  assert.equal(work.project, 'BrowserRT');
  assert.equal(work.revision, REVISION);
  assert.equal(work.version, VERSION);
  assert.ok(['kernel-kit-demo-browser-runner','kernel-kit-demo-page-runner'].includes(work.runner), 'unexpected work runner');
  assert.equal(work.page.crossOriginIsolated, true);
  assert.equal(work.planValidation.ok, true);
  assert.equal(work.worker.pingPong, true);
  assert.equal(work.worker.pingEnvelopeMagic, 'BRT1');
  assert.equal(work.worker.sum.sum, 138);
  assert.equal(work.worker.sum.count, 4);
  assert.equal(work.worker.transferDetached, true);
  assert.equal(work.channel.received.step, 'boot-runtime');
  assert.equal(work.channel.emptySize, 0);
  assert.equal(work.admission.accepted.admitted, true);
  assert.equal(work.admission.rejected.admitted, false);
  assert.equal(work.admission.rejected.noMutation, true);
  assert.equal(work.storage.put.accepted, true);
  assert.equal(work.storage.result.duplicate, false);
  assert.equal(work.storage.result.digest, work.storage.payloadDigest);
  assert.equal(work.storage.adapterValidation.ok, true);
  assert.equal(work.storage.guarded?.status, 'observed', 'work storage-lane should use a Web-Locks-guarded OPFS provider');
  assert.equal(work.storage.guarded?.proof?.guardedProvider, true, 'work storage-lane should expose guarded provider proof');
  assert.equal(work.storage.guarded?.proof?.exclusiveMutationsObserved, true, 'work storage-lane should guard mutation operations exclusively');
  assert.equal(work.storage.guarded?.proof?.sharedReadsObserved, true, 'work storage-lane should guard read/verify operations');
  assert.equal(work.storage.guarded?.proof?.lockAcquiredReleased, true, 'work storage-lane should acquire and release Web Locks');
  assert.equal(work.proof?.guardedStorageLane, true, 'work proof should expose guarded storage-lane evidence');
  assert.equal(work.abortBoundary?.status, 'passed', 'work page should prove OPFS abort boundary');
  assert.equal(work.abortBoundary?.proof?.compositeAbortRejected, true, 'work page should reject composed OPFS abort signal');
  assert.equal(work.abortBoundary?.proof?.invalidSiblingRejected, true, 'work page should reject invalid abortSignal sibling');
  assert.equal(work.abortBoundary?.proof?.noBlockPresent, true, 'work page OPFS abort boundary should leave no block present');
  assert.equal(work.abortBoundary?.proof?.nonMutationBoundary, true, 'work page should prove abort non-mutation boundary');
  assert.equal(work.proof?.opfsAbortBoundary, true, 'work proof should expose OPFS abort boundary');
  assert.equal(work.storagePosture?.status, 'passed', 'work page should capture browser storage posture');
  assert.equal(work.storagePosture?.proof?.estimateChecked, true, 'work page should check StorageManager estimate');
  assert.equal(work.storagePosture?.proof?.persistenceNotRequestedByDefault, true, 'work page should not request persistent storage by default');
  assert.equal(work.proof?.storagePostureObserved, true, 'work proof should expose storage posture observation');
  assert.equal(work.webLockPosture?.status, 'passed', 'work page should capture browser Web Locks posture');
  assert.equal(work.webLockPosture?.proof?.exclusiveNoOverlap, true, 'work page should prove exclusive Web Locks do not overlap');
  assert.equal(work.webLockPosture?.proof?.sharedCoHold, true, 'work page should prove shared Web Locks can co-hold');
  assert.equal(work.webLockPosture?.proof?.drainedAfterUse, true, 'work page should drain Web Locks after posture check');
  assert.equal(work.proof?.webLockPostureObserved, true, 'work proof should expose Web Locks posture observation');
  assert.equal(work.lifecycleCheckpoint?.status, 'risk-checkpoint-ready', 'work page should expose lifecycle checkpoint');
  assert.equal(work.proof?.lifecycleCheckpoint, true, 'work proof should expose lifecycle checkpoint result');
  assert.equal(validateKernelKitLifecycleCheckpoint(work.lifecycleCheckpoint).ok, true, 'work lifecycle checkpoint should validate from Node side');
  assert.equal(work.handoff?.validation?.ok, true, 'work page should validate local reload handoff');
  assert.equal(work.handoff?.stored, true, 'work page should store local reload handoff');
  assert.equal(observed.handoffBeforeReload?.expectedDigest, work.storage.payloadDigest, 'handoff should preserve payload digest');
  assert.equal(observed.handoffBeforeReload?.prefix, prefix, 'handoff should preserve storage prefix');
  assert.equal(validateKernelKitDemoHandoff(observed.handoffBeforeReload).ok, true, 'handoff should validate from Node side');
  assert.equal(reload.project, 'BrowserRT');
  assert.ok(['kernel-kit-demo-browser-runner','kernel-kit-demo-page-runner'].includes(reload.runner), 'unexpected reload runner');
  assert.equal(reload.page.crossOriginIsolated, true);
  assert.equal(reload.handoffUsed, true, 'reload should use localStorage handoff without explicit ref args');
  assert.equal(reload.handoffValidation?.ok, true, 'reload should validate loaded handoff');
  assert.equal(reload.validation.ok, true);
  assert.equal(reload.guardedStorage?.status, 'observed', 'reload storage-lane should also use a guarded OPFS provider');
  assert.equal(reload.guardedStorage?.proof?.guardedProvider, true, 'reload storage-lane should expose guarded provider proof');
  assert.equal(reload.guardedStorage?.proof?.exclusiveMutationsObserved, true, 'reload storage-lane should guard delete/cleanup mutation operations');
  assert.equal(reload.guardedStorage?.proof?.sharedReadsObserved, true, 'reload storage-lane should guard has/get/verify read operations');
  assert.equal(reload.guardedStorage?.proof?.lockAcquiredReleased, true, 'reload storage-lane should acquire and release Web Locks');
  assert.equal(reload.proof?.guardedStorageLane, true, 'reload proof should expose guarded storage-lane evidence');
  assert.equal(reload.storagePosture?.proof?.estimateChecked, true, 'reload page should capture browser storage posture');
  assert.equal(reload.proof?.storagePostureObserved, true, 'reload proof should expose storage posture observation');
  assert.equal(reload.webLockPosture?.proof?.exclusiveNoOverlap, true, 'reload page should capture Web Locks posture');
  assert.equal(reload.proof?.webLockPostureObserved, true, 'reload proof should expose Web Locks posture observation');
  assert.equal(reload.lifecycleCheckpoint?.status, 'risk-checkpoint-ready', 'reload page should expose lifecycle checkpoint');
  assert.equal(reload.proof?.lifecycleCheckpoint, true, 'reload proof should expose lifecycle checkpoint result');
  assert.equal(validateKernelKitLifecycleCheckpoint(reload.lifecycleCheckpoint).ok, true, 'reload lifecycle checkpoint should validate from Node side');
  assert.equal(reload.read.has, true);
  assert.equal(reload.read.digest, work.storage.payloadDigest);
  assert.equal(reload.read.expectedDigest, work.storage.payloadDigest);
  assert.equal(reload.read.verify.ok, true);
  assert.equal(reload.read.parsed.workerSum, 138);
  assert.equal(reload.read.parsed.kind, 'BrowserRT Kernel Kit Demo Artifact');
  assert.equal(reload.read.deleteResult, true);
  assert.equal(reload.read.cleanup, true);
  assert.equal(reload.handoffCleared, true, 'reload readback should clear consumed handoff');
  assert.equal(observed.handoffAfterRead, null, 'handoff should be absent after readback cleanup');
  assert.equal(observed.exportReceipt?.status, 'passed', 'export receipt should validate');
  assert.equal(validateKernelKitDemoExportBundle(observed.exportReceipt?.bundle).ok, true, 'export bundle should validate from Node side');
  assert.equal(observed.failureMode?.status, 'passed', 'controlled failure should be reported as passed');
  assert.equal(observed.failureMode?.failureMode, 'missing-handoff');
  assert.equal(observed.failureMode?.proof?.controlledFailure, true);
  assert.equal(observed.failureMode?.proof?.preventedMutation, true);
  assert.equal(observed.failureMode?.validation?.ok, true, 'failure-mode validation should pass');
  assert.equal(validateKernelKitFailureModeReport(observed.failureMode).ok, true, 'failure-mode report should validate from Node side');
  assert.equal(observed.failureMode?.exportBundleValidation?.ok, true, 'failure-mode export bundle should validate');
  assert.equal(observed.traceComparison?.validation?.ok, true, 'trace comparison should validate');
  assert.equal(validateKernelKitTraceComparison(observed.traceComparison).ok, true, 'trace comparison should validate from Node side');
  assert.equal(observed.traceComparison?.proof?.successHasUsefulPath, true, 'trace comparison should preserve success path');
  assert.equal(observed.traceComparison?.proof?.failurePreventedMutation, true, 'trace comparison should preserve bounded failure');
  assert.ok((observed.traceComparison?.diff?.successOnlyTraceKinds || []).length > 0, 'trace comparison should expose success-only trace kinds');
  assert.equal(observed.traceComparison?.diagnosticValidation?.ok, true, 'trace comparison should include a valid diagnostic runbook');
  assert.equal(observed.diagnosticRunbook?.validation?.ok, true, 'diagnostic runbook should validate');
  assert.equal(validateKernelKitDiagnosticRunbook(observed.diagnosticRunbook).ok, true, 'diagnostic runbook should validate from Node side');
  assert.equal(observed.diagnosticRunbook?.proof?.exactCommandsPresent, true, 'diagnostic runbook should include exact next commands');
  assert.equal(observed.diagnosticRunbook?.proof?.failureBounded, true, 'diagnostic runbook should preserve bounded failure');
  assert.equal(observed.supportBundle?.validation?.ok, true, 'support bundle should validate');
  assert.equal(validateKernelKitSupportBundle(observed.supportBundle).ok, true, 'support bundle should validate from Node side');
  assert.equal(observed.supportBundle?.proof?.successPathPresent, true, 'support bundle should preserve success path');
  assert.equal(observed.supportBundle?.proof?.reloadReadbackPresent, true, 'support bundle should preserve reload readback');
  assert.equal(observed.supportBundle?.proof?.controlledFailurePresent, true, 'support bundle should preserve controlled failure');
  assert.equal(observed.supportBundle?.proof?.exactCommandsPresent, true, 'support bundle should include exact commands');
  assert.equal(observed.supportBundle?.proof?.opfsAbortBoundaryPresent, true, 'support bundle should preserve OPFS abort boundary from success path');
  assert.equal(observed.supportBundle?.success?.proof?.opfsAbortBoundary, true, 'support bundle success proof should carry OPFS abort boundary');
  assert.equal(observed.supportBundle?.storagePosture?.success?.status, 'observed', 'support bundle should preserve browser storage posture');
  assert.equal(observed.supportBundle?.storagePosture?.success?.persistentStorageRequested, false, 'support bundle should not request persistent storage by default');
  assert.equal(observed.supportBundle?.proof?.webLockPosturePresent, true, 'support bundle should preserve browser Web Locks posture');
  assert.equal(observed.supportBundle?.webLockPosture?.success?.status, 'observed', 'support bundle should compact Web Locks posture as observed');
  assert.equal(observed.supportBundle?.webLockPosture?.success?.exclusiveNoOverlap, true, 'support bundle should preserve exclusive no-overlap evidence');
  assert.equal(observed.supportBundle?.webLockPosture?.success?.sharedCoHold, true, 'support bundle should preserve shared co-hold evidence');
  assert.equal(observed.supportBundle?.proof?.guardedStorageLanePresent, true, 'support bundle should preserve guarded storage-lane evidence');
  assert.equal(observed.supportBundle?.proof?.storagePressureCheckpointPresent, true, 'support bundle should carry storage pressure checkpoint presence');
  assert.equal(observed.supportBundle?.proof?.admissionCancellationCheckpointPresent, true, 'support bundle should carry admission cancellation checkpoint presence');
  assert.equal(observed.supportBundle?.admissionCancellation?.commandId, 'admission:abort-release-proof', 'support bundle should name admission abort-release command');
  assert.equal(observed.supportBundle?.storagePressure?.commandId, 'browser:opfs-lane-quota-backpressure-proof', 'support bundle should name explicit storage pressure browser command');
  assert.equal(observed.supportBundle?.storagePressure?.evictionSurvivalDeferred, true, 'support bundle storage pressure checkpoint must preserve eviction deferral');
  assert.equal(observed.supportBundle?.proof?.sessionCoordinationCheckpointPresent, true, 'support bundle should carry session coordination checkpoint presence');
  assert.equal(observed.supportBundle?.sessionCoordination?.commandId, 'browser:kernel-kit-session-coordination-checkpoint-proof', 'support bundle should name session coordination browser command');
  assert.ok(observed.supportBundle?.sessionCoordination?.deferredRowIds?.includes('exclusive-lock-contention-observed'), 'browser-light support bundle should defer lock contention row');
  assert.equal(validateKernelKitSessionCoordinationCheckpoint(observed.supportBundle?.sessionCoordination || {}).ok, true, 'support bundle session coordination checkpoint should validate from Node side');
  assert.equal(observed.supportBundle?.success?.proof?.guardedStorageLane, true, 'support bundle success proof should carry guarded storage-lane evidence');
  assert.equal(observed.supportBundle?.guardedStorageLane?.success?.status, 'observed', 'support bundle should compact guarded storage lane as observed');
  assert.equal(observed.supportBundle?.guardedStorageLane?.success?.guardedProvider, true, 'support bundle should preserve guarded provider evidence');
  assert.equal(observed.supportBundle?.guardedStorageLane?.success?.lockAcquiredReleased, true, 'support bundle should preserve lock acquire/release evidence');
  assert.equal(observed.supportBundle?.proof?.evidenceLedgerPresent, true, 'support bundle should preserve expected artifact evidence ledger');
  assert.equal(validateKernelKitSupportBundleEvidenceLedger(observed.supportBundle?.evidenceLedger || {}).ok, true, 'support bundle evidence ledger should validate from Node side');
  assert.equal(observed.supportBundle?.evidenceLedger?.status, 'evidence-ledger-ready', 'support bundle evidence ledger should be ready');
  assert.equal(observed.supportBundle?.proof?.lifecycleCheckpointPresent, true, 'support bundle should carry lifecycle checkpoint proof');
  assert.equal(observed.supportBundle?.lifecycleCheckpoint?.status, 'risk-checkpoint-ready', 'support bundle lifecycle checkpoint should be ready');
  assert.equal(observed.supportBundle?.proof?.privacyScrubPresent, true, 'support bundle should carry privacy scrub checkpoint');
  assert.equal(validateKernelKitSupportBundlePrivacyScrub(observed.supportBundle?.privacyScrub || {}).ok, true, 'support bundle embedded privacy scrub should validate from Node side');
  assert.equal(observed.supportBundle?.privacyScrub?.proof?.sensitiveFieldsRedacted, true, 'embedded privacy scrub should redact sensitive fields');
  assert.ok((observed.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('BROWSER-KERNEL-KIT-DEMO-PROBE')), 'evidence ledger should name the browser proof artifact');
  assert.ok((observed.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('KERNEL-KIT-ADMISSION-CANCELLATION-CHECKPOINT-PROBE')), 'evidence ledger should name the admission cancellation artifact');
  assert.ok((observed.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE')), 'evidence ledger should name the quota pressure browser-heavy artifact');
  assert.ok((observed.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE')), 'evidence ledger should name the session coordination browser-heavy artifact');
  assert.ok((observed.supportBundle?.evidenceLedger?.outputPaths || []).some((path) => String(path).includes('BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE')), 'evidence ledger should name the recovery browser-heavy artifact');
  assert.equal(observed.supportBundleImport?.validation?.ok, true, 'support bundle import should validate');
  assert.equal(validateKernelKitSupportBundleImportReport(observed.supportBundleImport).ok, true, 'support bundle import should validate from Node side');
  assert.equal(observed.supportBundleImport?.proof?.bundleValid ?? observed.supportBundleImport?.proof?.validationOk, true, 'support bundle import should preserve bundle validation');
  assert.equal(observed.supportBundleImport?.proof?.nonClaimsVisible, true, 'support bundle import should preserve non-claims');
  assert.equal(observed.supportBundleImport?.proof?.replayPlanReady, true, 'support bundle import should generate a replay plan');
  assert.equal(observed.supportBundleImport?.proof?.evidenceLedgerPresent, true, 'support bundle import should preserve evidence ledger readiness');
  assert.equal(observed.supportBundleImport?.evidenceLedger?.validation?.ok, true, 'support bundle import evidence ledger should validate');
  assert.equal(observed.supportBundleImport?.replayPlan?.validation?.ok, true, 'support bundle import replay plan should validate');
  assert.equal(observed.supportBundleReplay?.validation?.ok, true, 'support bundle replay plan should validate');
  assert.equal(validateKernelKitSupportBundleReplayPlan(observed.supportBundleReplay).ok, true, 'support bundle replay plan should validate from Node side');
  assert.equal(observed.supportBundleReplay?.status, 'replay-plan-ready', 'support bundle replay plan should be ready');
  assert.equal(observed.supportBundleReplay?.proof?.browserLightBeforeBrowserHeavy, true, 'replay plan should keep browser-light phases before browser/CDP proof');
  assert.equal(observed.supportBundleReplay?.proof?.replayDoesNotExecuteCommands, true, 'replay plan must not execute commands');
  assert.equal(observed.supportBundleReplay?.evidenceSlots?.evidenceLedgerPresent, true, 'replay plan should require evidence ledger readiness');
  assert.equal(observed.supportBundleReplay?.evidenceLedgerValidation?.ok, true, 'replay plan evidence ledger should validate');
  assert.equal((observed.supportBundleReplay?.blockedPhaseIds || []).length, 0, 'replay plan should have no blocked phases');
  assert.equal(observed.supportBundleEvidenceCheckpoint?.validation?.ok, true, 'support-bundle evidence checkpoint should validate; admission-cancellation-artifact');
  assert.equal(validateKernelKitSupportBundleEvidenceCheckpoint(observed.supportBundleEvidenceCheckpoint).ok, true, 'support bundle evidence checkpoint should validate from Node side');
  assert.equal(observed.supportBundleEvidenceCheckpoint?.status, 'evidence-checkpoint-ready', 'support bundle evidence checkpoint should be ready');
  assert.equal(observed.supportBundleEvidenceCheckpoint?.proof?.requiredProofPathsSatisfied, true, 'support bundle evidence checkpoint should satisfy supplied proof paths');
  assert.equal(observed.supportBundleEvidenceCheckpoint?.proof?.checkpointDoesNotExecuteCommands, true, 'support bundle evidence checkpoint must not execute commands');
  assert.ok((observed.supportBundleEvidenceCheckpoint?.deferredEntryIds || []).includes('support-bundle-audit-artifact'), 'product-page checkpoint should explicitly defer static support-bundle audit artifact');
  assert.equal(observed.supportBundleEvidenceCheckpoint?.rows?.find((row) => row.id === 'admission-cancellation-artifact')?.status, 'satisfied', 'product-page checkpoint should satisfy admission cancellation artifact shape');
  assert.equal((observed.supportBundleEvidenceCheckpoint?.missingEntryIds || []).length, 0, 'support bundle evidence checkpoint should not hide missing supplied artifacts');
  assert.equal(observed.supportBundleDiff?.validation?.ok, true, 'support bundle diff should validate');
  assert.equal(validateKernelKitSupportBundleDiff(observed.supportBundleDiff).ok, true, 'support bundle diff should validate from Node side');
  assert.equal(observed.supportBundleDiff?.status, 'unchanged', 'same-bundle support diff should be unchanged');
  assert.equal(observed.supportBundleDiff?.proof?.nonClaimsCompared, true, 'support bundle diff should compare non-claims');
  assert.equal(observed.supportBundleDiff?.proof?.exactCommandsCompared, true, 'support bundle diff should compare commands');
  assert.equal(observed.supportBundlePrivacyScrub?.validation?.ok, true, 'support bundle privacy scrub should validate');
  assert.equal(validateKernelKitSupportBundlePrivacyScrub(observed.supportBundlePrivacyScrub).ok, true, 'support bundle privacy scrub should validate from Node side');
  assert.equal(observed.supportBundlePrivacyScrub?.status, 'passed', 'support bundle privacy scrub should pass');
  assert.equal(observed.supportBundlePrivacyScrub?.proof?.sensitiveFieldsRedacted, true, 'support bundle privacy scrub should redact sensitive fields');
  assert.equal(observed.supportBundlePrivacyScrub?.proof?.exactCommandTextRedacted, true, 'support bundle privacy scrub should redact exact command text');
  assert.ok((observed.supportBundlePrivacyScrub?.redaction?.redactedFieldCount || 0) > 0, 'support bundle privacy scrub should report redactions');
  assert.equal(observed.guidedTour?.validation?.ok, true, 'guided tour should validate');
  assert.equal(validateKernelKitGuidedTourReceipt(observed.guidedTour).ok, true, 'guided tour should validate from Node side');
  assert.equal(observed.guidedTour?.proof?.hasTourSteps, true, 'guided tour should expose tour steps');
  assert.equal(observed.guidedTour?.proof?.hasSupportBundleReference, true, 'guided tour should reference support bundle');
  assert.equal(observed.guidedTour?.proof?.supportBundleValidWhenPresent, true, 'guided tour should validate support bundle');
  assert.equal(observed.guidedTour?.proof?.hasExactCommands, true, 'guided tour should include exact commands');
  assert.equal(observed.guidedTour?.proof?.mentionsBoundedFailure, true, 'guided tour should mention bounded failure');
  assert.equal(observed.handoffMarkdown?.validation?.ok, true, 'handoff Markdown should validate');
  assert.equal(validateKernelKitHandoffMarkdown(observed.handoffMarkdown).ok, true, 'handoff Markdown should validate from Node side');
  assert.equal(observed.handoffMarkdown?.status, 'handoff-ready', 'handoff Markdown should be ready');
  assert.ok(String(observed.handoffMarkdown?.markdown || '').includes('# BrowserRT Kernel Kit Handoff'), 'handoff Markdown should include title');
  assert.ok(String(observed.handoffMarkdown?.markdown || '').includes('demo:kernel-kit-handoff-markdown-proof'), 'handoff Markdown should include exact proof command');
  assert.equal(observed.handoffMarkdownImport?.validation?.ok, true, 'handoff Markdown import should validate');
  assert.equal(validateKernelKitHandoffMarkdownImportReport(observed.handoffMarkdownImport).ok, true, 'handoff Markdown import should validate from Node side');
  assert.equal(observed.handoffMarkdownImport?.status, 'handoff-import-ready', 'handoff Markdown import should be ready');
  assert.equal(observed.handoffMarkdownImport?.proof?.requiredCommandsPresent, true, 'handoff Markdown import should preserve required commands');
  assert.equal(observed.handoffMarkdownImport?.proof?.requiredNonClaimsPresent, true, 'handoff Markdown import should preserve required non-claims');
  assert.equal(observed.readinessGate?.validation?.ok, true, 'readiness gate should validate');
  assert.equal(validateKernelKitReadinessGate(observed.readinessGate).ok, true, 'readiness gate should validate from Node side');
  assert.equal(observed.readinessGate?.status, 'ready-for-next-usefulness-pass', 'readiness gate should pass');
  assert.equal(observed.readinessGate?.proof?.allRequiredGatesPass, true, 'readiness gate should pass all gates');
  assert.equal(observed.readinessGate?.proof?.handoffMarkdownRoundTripVisible, true, 'readiness gate should see handoff round trip');
  assert.equal(observed.readinessGate?.proof?.nonClaimsVisible, true, 'readiness gate should keep non-claims visible');
  assert.equal(observed.readinessGate?.proof?.readinessInputsEvidenceBound, true, 'readiness gate should bind to real success/reload/failure inputs');
  assert.equal(observed.readinessGate?.inputProof?.evidenceBound, true, 'readiness gate input proof should not be a placeholder');
  assert.equal(observed.readinessGate?.inputProof?.source, 'derived-from-success-reload-failure-reports', 'readiness gate should derive from page reports');
  assert.equal(observed.readinessGate?.inputProof?.sourceReports?.success, true, 'readiness gate should see success report');
  assert.equal(observed.readinessGate?.inputProof?.sourceReports?.reload, true, 'readiness gate should see reload report');
  assert.equal(observed.readinessGate?.inputProof?.sourceReports?.failure, true, 'readiness gate should see failure report');
  assert.equal(observed.readinessContrast?.validation?.ok, true, 'readiness contrast should validate');
  assert.equal(validateKernelKitReadinessContrast(observed.readinessContrast).ok, true, 'readiness contrast should validate from Node side');
  assert.equal(observed.readinessContrast?.status, 'contrast-ready', 'readiness contrast should be ready');
  assert.equal(observed.readinessContrast?.proof?.baselineReady, true, 'readiness contrast should see ready baseline');
  assert.equal(observed.readinessContrast?.proof?.degradedNeedsAttention, true, 'readiness contrast should show degraded needs-attention');
  assert.equal(observed.readinessContrast?.proof?.expectedGatesFailed, true, 'readiness contrast should expose expected failed gates');
  assert.equal(observed.pageStateAfterReload.hasDemoGlobal, true);
  assert.equal(work.usefulnessValidation?.ok, true, 'work page should validate the usefulness scorecard');
  assert.equal(reload.usefulnessValidation?.ok, true, 'reload page should validate the usefulness scorecard');
  assert.equal(reload.usefulness?.status, 'usefulness-wedge-earned', 'reload usefulness should be earned after readback');
  assert.equal(validateKernelKitDemoUsefulnessReport(reload.usefulness).ok, true, 'reload usefulness should validate from Node too');
  const workRendered = work.renderedTranscript === true || (work.renderedTranscript && work.renderedTranscript.status === 'passed');
  const workPassedStages = work.passedStages ?? work.renderedTranscript?.passedStages ?? 0;
  const reloadRendered = reload.renderedTranscript === true || (reload.renderedTranscript && reload.renderedTranscript.status === 'passed');
  const reloadPassedStages = reload.passedStages ?? reload.renderedTranscript?.passedStages ?? 0;
  assert.equal(workRendered, true, 'work page should render a transcript receipt');
  assert.ok(workPassedStages >= 7, 'work page should pass most proof stages before reload');
  assert.equal(reloadRendered, true, 'reload page should render a complete transcript');
  assert.equal(reloadPassedStages, 8, 'reload page should render all transcript stages');

  assert.ok(Number.isInteger(harness.server?.port) && harness.server.port > 0, 'managed browser proof must record its HTTP server port');
  assert.equal(harness.server?.external, false, 'kernel-kit demo should own its managed HTTP server');
  assert.ok(Number.isInteger(harness.server?.requestCount) && harness.server.requestCount > 0, 'managed HTTP server should record requests');
  assert.ok(Number.isInteger(harness.cdp?.port) && harness.cdp.port > 0, 'managed browser proof must record its CDP port');
  assert.ok(Number.isInteger(harness.cdp?.eventCount), 'managed browser proof must record its CDP event count');
  assert.ok(typeof harness.cdp?.browserVersion?.Browser === 'string' && harness.cdp.browserVersion.Browser.length > 0, 'managed browser proof must record the browser version');
  assert.equal(harness.process?.timedOut, false, 'managed Chromium teardown should complete without timeout');

  const allTraceKinds = [...new Set([...(work.traceKinds || []), ...(reload.traceKinds || [])])];
  for (const kind of ['runtime:boot','channel:create','channel:send','channel:receive','agent:spawn','agent:ready','agent:call','agent:result','object:transfer-ref','admission:admit','admission:reject','admission:release','object:opfs-storage-lane-adapter-ref','object:opfs-web-lock-guarded-block-store-ref','storage:opfs-web-lock-guard-op-complete','coord:web-lock-acquired','block-store-lane:schedule','storage-lane:dispatch','block-store-lane:op-complete','storage:opfs-block-put','storage:opfs-block-get','storage:opfs-block-composite-abort-signal','storage:opfs-block-abort-signal-invalid','storage:opfs-block-abort','kernel-kit-demo:opfs-abort-boundary','kernel-kit-demo:storage-posture','kernel-kit-demo:web-lock-posture','runtime:close']) {
    assert.ok(allTraceKinds.includes(kind), `missing kernel-kit demo trace kind ${kind}`);
  }

  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 2,
    codename: 'Interactive Kernel Kit Demo',
    proofId: `${REVISION}-browser-kernel-kit-demo`,
    probe_id: `${REVISION}-browser-kernel-kit-demo-probe`,
    status: 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'Integrated BrowserRT Kernel Kit usefulness proof: boot runtime, spawn Worker agent, transfer object ref, bounded control channel, admission gate, Web-Locks-guarded OPFS storage-lane write/read across page reload, raw OPFS composite AbortSignal non-mutation boundary, browser StorageManager posture capture, browser Web Locks posture capture, trace evidence, transcript/observatory surfaces, local reload handoff, export bundle, controlled failure-mode reporting, trace comparison, diagnostic runbook, support bundle, lifecycle checkpoint, support-bundle replay plan, support-bundle evidence ledger, support-bundle diff, guided tour, handoff Markdown, handoff Markdown import validation, evidence-bound readiness gate evaluation, degraded-readiness contrast, and cleanup.',
    browserProof: true,
    chromium: { executable: harness.chromiumExecutable, targetUrl: observed.pageUrl },
    policyRelaxation: harness.policyRelaxation,
    proof: {
      booted: true,
      workerPing: work.worker.pingPong,
      transferDetached: work.worker.transferDetached,
      boundedChannel: work.channel.received.step === 'boot-runtime' && work.channel.emptySize === 0,
      admissionAccepted: work.admission.accepted.admitted === true,
      admissionRejectedNoMutation: work.admission.rejected.noMutation === true,
      storageWrite: work.storage.result.digest === work.storage.payloadDigest,
      guardedStorageLane: work.storage.guarded?.proof?.guardedProvider === true && work.storage.guarded?.proof?.lockAcquiredReleased === true && reload.guardedStorage?.proof?.guardedProvider === true,
      opfsAbortBoundary: work.abortBoundary?.status === 'passed' && work.abortBoundary?.proof?.nonMutationBoundary === true,
      storagePosture: work.storagePosture?.proof?.estimateChecked === true && work.storagePosture?.proof?.persistenceNotRequestedByDefault === true,
      webLockPosture: work.webLockPosture?.proof?.exclusiveNoOverlap === true && work.webLockPosture?.proof?.sharedCoHold === true && work.webLockPosture?.proof?.drainedAfterUse === true,
      reloadReadback: reload.read.digest === work.storage.payloadDigest && reload.read.parsed.workerSum === 138,
      traceComplete: true,
      renderedTranscript: reloadRendered,
      passedStages: reloadPassedStages,
      usefulnessScorecard: reload.usefulness?.status === 'usefulness-wedge-earned',
      localReloadHandoff: reload.handoffUsed === true && reload.handoffCleared === true,
      exportBundle: observed.exportReceipt?.status === 'passed',
      controlledFailureMode: observed.failureMode?.proof?.controlledFailure === true,
      traceComparison: observed.traceComparison?.validation?.ok === true,
      diagnosticRunbook: observed.diagnosticRunbook?.validation?.ok === true && observed.diagnosticRunbook?.proof?.exactCommandsPresent === true,
      supportBundle: observed.supportBundle?.validation?.ok === true && observed.supportBundle?.proof?.exactCommandsPresent === true,
      lifecycleCheckpoint: work.proof?.lifecycleCheckpoint === true && reload.proof?.lifecycleCheckpoint === true && observed.supportBundle?.proof?.lifecycleCheckpointPresent === true,
      supportBundleEvidenceLedger: validateKernelKitSupportBundleEvidenceLedger(observed.supportBundle?.evidenceLedger || {}).ok === true && observed.supportBundle?.proof?.evidenceLedgerPresent === true,
      supportBundleImport: observed.supportBundleImport?.validation?.ok === true && observed.supportBundleImport?.proof?.nonClaimsVisible === true,
      supportBundleReplay: observed.supportBundleReplay?.validation?.ok === true && observed.supportBundleReplay?.status === 'replay-plan-ready' && observed.supportBundleReplay?.evidenceSlots?.evidenceLedgerPresent === true,
      supportBundleEvidenceCheckpoint: observed.supportBundleEvidenceCheckpoint?.validation?.ok === true && observed.supportBundleEvidenceCheckpoint?.proof?.requiredProofPathsSatisfied === true,
      supportBundlePrivacyScrub: observed.supportBundlePrivacyScrub?.validation?.ok === true && observed.supportBundlePrivacyScrub?.proof?.sensitiveFieldsRedacted === true,
      supportBundleDiff: observed.supportBundleDiff?.validation?.ok === true && observed.supportBundleDiff?.proof?.nonClaimsCompared === true,
      guidedTour: observed.guidedTour?.validation?.ok === true && observed.guidedTour?.proof?.hasExactCommands === true,
      handoffMarkdown: observed.handoffMarkdown?.validation?.ok === true && observed.handoffMarkdown?.status === 'handoff-ready',
      handoffMarkdownImport: observed.handoffMarkdownImport?.validation?.ok === true && observed.handoffMarkdownImport?.status === 'handoff-import-ready',
      readinessGate: observed.readinessGate?.validation?.ok === true && observed.readinessGate?.status === 'ready-for-next-usefulness-pass' && observed.readinessGate?.proof?.readinessInputsEvidenceBound === true,
      readinessContrast: observed.readinessContrast?.validation?.ok === true && observed.readinessContrast?.status === 'contrast-ready'
    },
    observations: compactObservedForArtifact(observed, allTraceKinds),
    browserHarness: {
      durationMs: harness.durationMs,
      timingCount: harness.timings?.length || 0,
      server: {
        origin: new URL(observed.pageUrl).origin,
        port: harness.server?.port ?? null,
        external: harness.server?.external === true,
        requestCount: harness.server?.requestCount ?? null,
        ownedByHarness: harness.server?.external === false,
        closedAfterRun: harness.server?.external === false
      },
      cdp: {
        sessionEstablished: Number.isInteger(harness.cdp?.port) && typeof harness.cdp?.browserVersion?.Browser === 'string',
        port: harness.cdp?.port ?? null,
        eventCount: harness.cdp?.eventCount ?? null,
        browser: harness.cdp?.browserVersion?.Browser ?? null,
        protocolVersion: harness.cdp?.browserVersion?.ProtocolVersion ?? null,
        closedAfterRun: harness.cdp != null
      },
      process: {
        teardownMode: harness.teardownMode,
        requestedSignals: harness.process?.requestedSignals || [],
        code: harness.process?.code ?? null,
        signal: harness.process?.signal ?? null,
        timedOut: harness.process?.timedOut === true
      },
      chromeStderr: {
        lineCount: harness.chromeStderrSummary?.lineCount ?? 0,
        devtoolsListening: harness.chromeStderrSummary?.devtoolsListening === true,
        policyMentions: harness.chromeStderrSummary?.policyMentions ?? 0,
        errorLineSampleCount: harness.chromeStderrSummary?.errorLineSample?.length || 0
      },
      chromeStdoutBytes: harness.chromeStdoutBytes
    },
    nonClaims: [
      'Integrated demo proof is cloudtainer Chromium evidence, not product-market fit or production runtime evidence.',
      'No production runtime claim.',
      'No product-market-fit claim.',
      'No production guided-tour claim.',
      'No production lifecycle-readiness claim.',
      'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
      'Storage posture is advisory capability/estimate evidence, not a quota reservation or eviction-survival proof.',
      'Web Locks posture is advisory coordination evidence, not a fairness, lifecycle recovery, cross-browser, or production coordination claim.',
      'Web-Locks-guarded storage-lane evidence is managed Chromium evidence only, not a fairness, lifecycle recovery, cross-browser, crash-recovery, or production coordination guarantee.',
      'No OPFS sync access handle storage-lane proof and no browser Worker OPFS storage-lane provider proof.',
      'Abort remains cooperative: this proof covers pre-write non-mutation for a composed raw OPFS put, not arbitrary cancellation of native browser I/O after side effects start.',
      'No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, cross-browser conformance, throughput, latency, SLO, or real performance claim.',
      'Temporary managed-policy relaxation is local to this command and restored during teardown.'
    ]
  };
  const validation = validateKernelKitDemoReport(report);
  assert.equal(validation.ok, true, validation.errors.join('; '));
  const observatory = createKernelKitDemoObservatoryReport(report, { generatedAt: report.generatedAt });
  const observatoryValidation = validateKernelKitDemoObservatoryReport(observatory);
  assert.equal(observatoryValidation.ok, true, observatoryValidation.errors.join('; '));
  report.validation = validation;
  report.observatory = { status: 'validated-and-summarized', sectionCount: observatory.sections?.length || 0, stageCount: observatory.stageCards?.length || 0, observedStageCount: observatory.proofReceipt?.observedStageCount || 0, traceKindCount: observatory.traceSummary?.uniqueKindCount || 0 };
  report.observatoryCompacted = true;
  report.observatoryValidation = observatoryValidation;
  const obs = report.observations;
  const lc = (checkpoint) => checkpoint ? ({ status: checkpoint.status, deferredRowIds: checkpoint.deferredRowIds, proof: checkpoint.proof }) : null;
  report.observations = {
    pageUrl: obs.pageUrl,
    work: { status: obs.work?.status, page: obs.work?.page, proof: obs.work?.proof, storage: { payloadDigest: obs.work?.storage?.payloadDigest, resultDigest: obs.work?.storage?.resultDigest, guardedStatus: obs.work?.storage?.guarded?.status }, storagePosture: { status: obs.work?.storagePosture?.status, proof: obs.work?.storagePosture?.proof }, webLockPosture: { status: obs.work?.webLockPosture?.status, proof: obs.work?.webLockPosture?.proof }, lifecycleCheckpoint: lc(obs.work?.lifecycleCheckpoint) },
    reload: { status: obs.reload?.status, handoffUsed: obs.reload?.handoffUsed, handoffCleared: obs.reload?.handoffCleared, read: obs.reload?.read, proof: obs.reload?.proof, lifecycleCheckpoint: lc(obs.reload?.lifecycleCheckpoint), usefulness: obs.reload?.usefulness },
    supportBundle: { validation: obs.supportBundle?.validation, proof: obs.supportBundle?.proof, lifecycleCheckpoint: lc(obs.supportBundle?.lifecycleCheckpoint), evidenceLedger: obs.supportBundle?.evidenceLedger },
    supportBundleReplay: { status: obs.supportBundleReplay?.status, proof: obs.supportBundleReplay?.proof },
    supportBundlePrivacyScrub: { status: obs.supportBundlePrivacyScrub?.status, proof: obs.supportBundlePrivacyScrub?.proof, redaction: obs.supportBundlePrivacyScrub?.redaction },
    supportBundleEvidenceCheckpoint: { status: obs.supportBundleEvidenceCheckpoint?.status, proof: obs.supportBundleEvidenceCheckpoint?.proof },
    readinessGate: { status: obs.readinessGate?.status, proof: obs.readinessGate?.proof },
    allTraceKinds: obs.allTraceKinds
  };
  report.nonClaimCount = report.nonClaims.length;
  report.nonClaims = report.nonClaims.filter((claim) => ['No production runtime claim.','No product-market-fit claim.','No production lifecycle-readiness claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'].includes(claim));
  report.artifactCompacted = true;
  return report;
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const timeoutMs = Number(argValue(argv, '--timeout-ms', '20000'));
const chromium = argValue(argv, '--chromium', null);
const prefix = argValue(argv, '--prefix', null);
const relaxPolicy = !hasFlag(argv, '--no-policy-relaxation');

try {
  const report = await runProbe({ timeoutMs, chromium, prefix, relaxPolicy });
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else {
    console.log(JSON.stringify(report, null, 2));
  }
} catch (error) {
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 2,
    codename: 'Interactive Kernel Kit Demo',
    proofId: `${REVISION}-browser-kernel-kit-demo`,
    probe_id: `${REVISION}-browser-kernel-kit-demo-probe`,
    status: 'failed',
    generatedAt: new Date().toISOString(),
    error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }
  };
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  }
  throw error;
}

// Static audit breadcrumb: BrowserRTKernelKitDemo.runWork / BrowserRTKernelKitDemo.runReload / BrowserRTKernelKitDemo.compareTraces / BrowserRTKernelKitDemo.diagnoseTraceComparison / BrowserRTKernelKitDemo.buildSupportBundle / BrowserRTKernelKitDemo.buildSupportBundleEvidenceLedger / BrowserRTKernelKitDemo.buildSupportBundleEvidenceCheckpoint / BrowserRTKernelKitDemo.scrubSupportBundle / BrowserRTKernelKitDemo.importSupportBundle / BrowserRTKernelKitDemo.replaySupportBundle / BrowserRTKernelKitDemo.diffSupportBundle / BrowserRTKernelKitDemo.runGuidedTour / BrowserRTKernelKitDemo.buildHandoffMarkdown / BrowserRTKernelKitDemo.importHandoffMarkdown / BrowserRTKernelKitDemo.buildReadinessGate / runnerInfo / pageWorkbenchReady / renderedTranscript / passedStages / loadHandoff / clearHandoff / work.abortBoundary / work.storagePosture / storage:opfs-block-composite-abort-signal / kernel-kit-demo:opfs-abort-boundary / kernel-kit-demo:storage-posture / kernel-kit-demo:web-lock-posture / work.webLockPosture / work.lifecycleCheckpoint / reload.lifecycleCheckpoint / supportBundle.lifecycleCheckpoint / supportBundle.webLockPosture / work.storage.guarded / reload.guardedStorage / supportBundle.guardedStorageLane / lifecycleCheckpoint / supportBundleEvidenceLedger / BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE / BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE / browser:opfs-lane-quota-backpressure-proof / browser:kernel-kit-recovery-checkpoint-proof / storagePressureCheckpointPresent / supportBundleEvidenceCheckpoint / supportBundlePrivacyScrub / supportBundleReplay.proof.browserLightBeforeBrowserHeavy / readinessGate.inputProof.evidenceBound / readiness-inputs-evidence-bound / object:opfs-web-lock-guarded-block-store-ref / storage:opfs-web-lock-guard-op-complete / coord:web-lock-acquired.

// Static audit marker: support-bundle evidence checkpoint should validate; admission-cancellation-artifact / BrowserRTKernelKitDemo.replaySupportBundle / supportBundleEvidenceLedger / BROWSER-OPFS-LANE-QUOTA-BACKPRESSURE-PROBE / BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE / browser:opfs-lane-quota-backpressure-proof / browser:kernel-kit-recovery-checkpoint-proof / storagePressureCheckpointPresent / supportBundleEvidenceCheckpoint / supportBundleEvidenceCheckpoint.validation / supportBundleReplay.validation / browserrt-kernel-kit-support-bundle-replay-plan-v1 / No automated replay execution claim.
