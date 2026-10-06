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
  validateKernelKitSupportBundleDiff,
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

function exprForSupportBundleDiff() {
  return `(async()=>{ const bundle = window.__BROWSERRT_KERNEL_KIT_SUPPORT_BUNDLE; return JSON.stringify(window.BrowserRTKernelKitDemo.diffSupportBundle({render:false,input:JSON.stringify(bundle)})); })()`;
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

    const supportDiffStart = performance.now();
    const supportBundleDiff = await evalJson(exprForSupportBundleDiff(), timeoutMs);
    mark('kernel-kit-demo-support-bundle-diff-eval', supportDiffStart);

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

    const readinessContrastStart = performance.now();
    const readinessContrast = await evalJson(exprForReadinessContrast(), timeoutMs);
    mark('kernel-kit-demo-readiness-contrast-eval', readinessContrastStart);

    return { pageUrl, runnerInfo, work, handoffBeforeReload, reload, handoffAfterRead, exportReceipt, failureMode, traceComparison, diagnosticRunbook, supportBundle, supportBundleImport, supportBundleDiff, guidedTour, handoffMarkdown, handoffMarkdownImport, readinessGate, readinessContrast, pageStateAfterReload: pageState };
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
  assert.equal(observed.supportBundleImport?.validation?.ok, true, 'support bundle import should validate');
  assert.equal(validateKernelKitSupportBundleImportReport(observed.supportBundleImport).ok, true, 'support bundle import should validate from Node side');
  assert.equal(observed.supportBundleImport?.proof?.bundleValid ?? observed.supportBundleImport?.proof?.validationOk, true, 'support bundle import should preserve bundle validation');
  assert.equal(observed.supportBundleImport?.proof?.nonClaimsVisible, true, 'support bundle import should preserve non-claims');
  assert.equal(observed.supportBundleDiff?.validation?.ok, true, 'support bundle diff should validate');
  assert.equal(validateKernelKitSupportBundleDiff(observed.supportBundleDiff).ok, true, 'support bundle diff should validate from Node side');
  assert.equal(observed.supportBundleDiff?.status, 'unchanged', 'same-bundle support diff should be unchanged');
  assert.equal(observed.supportBundleDiff?.proof?.nonClaimsCompared, true, 'support bundle diff should compare non-claims');
  assert.equal(observed.supportBundleDiff?.proof?.exactCommandsCompared, true, 'support bundle diff should compare commands');
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

  const allTraceKinds = [...work.traceKinds, ...reload.traceKinds];
  for (const kind of ['runtime:boot','channel:create','channel:send','channel:receive','agent:spawn','agent:ready','agent:call','agent:result','object:transfer-ref','admission:admit','admission:reject','admission:release','object:opfs-storage-lane-adapter-ref','block-store-lane:schedule','storage-lane:dispatch','block-store-lane:op-complete','storage:opfs-block-put','storage:opfs-block-get','runtime:close']) {
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
    purpose: 'Integrated BrowserRT Kernel Kit usefulness proof: boot runtime, spawn Worker agent, transfer object ref, bounded control channel, admission gate, OPFS storage-lane write/read across page reload, trace evidence, transcript/observatory surfaces, local reload handoff, export bundle, controlled failure-mode reporting, trace comparison, diagnostic runbook, support bundle, support-bundle diff, guided tour, handoff Markdown, handoff Markdown import validation, readiness gate evaluation, degraded-readiness contrast, and cleanup.',
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
      supportBundleImport: observed.supportBundleImport?.validation?.ok === true && observed.supportBundleImport?.proof?.nonClaimsVisible === true,
      supportBundleDiff: observed.supportBundleDiff?.validation?.ok === true && observed.supportBundleDiff?.proof?.nonClaimsCompared === true,
      guidedTour: observed.guidedTour?.validation?.ok === true && observed.guidedTour?.proof?.hasExactCommands === true,
      handoffMarkdown: observed.handoffMarkdown?.validation?.ok === true && observed.handoffMarkdown?.status === 'handoff-ready',
      handoffMarkdownImport: observed.handoffMarkdownImport?.validation?.ok === true && observed.handoffMarkdownImport?.status === 'handoff-import-ready',
      readinessGate: observed.readinessGate?.validation?.ok === true && observed.readinessGate?.status === 'ready-for-next-usefulness-pass',
      readinessContrast: observed.readinessContrast?.validation?.ok === true && observed.readinessContrast?.status === 'contrast-ready'
    },
    observations: { ...observed, allTraceKinds },
    server: harness.server,
    cdp: harness.cdp,
    timings: harness.timings,
    durationMs: harness.durationMs,
    chromeStderrSummary: harness.chromeStderrSummary,
    chromeStdoutBytes: harness.chromeStdoutBytes,
    nonClaims: [
      'Integrated demo proof is cloudtainer Chromium evidence, not product-market fit or production runtime evidence.',
      'No production runtime claim.',
      'No product-market-fit claim.',
      'No production guided-tour claim.',
      'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
      'No OPFS sync access handle storage-lane proof and no browser Worker OPFS storage-lane provider proof.',
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
  report.observatory = observatory;
  report.observatoryValidation = observatoryValidation;
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

// Static audit breadcrumb: BrowserRTKernelKitDemo.runWork / BrowserRTKernelKitDemo.runReload / BrowserRTKernelKitDemo.compareTraces / BrowserRTKernelKitDemo.diagnoseTraceComparison / BrowserRTKernelKitDemo.buildSupportBundle / BrowserRTKernelKitDemo.importSupportBundle / BrowserRTKernelKitDemo.diffSupportBundle / BrowserRTKernelKitDemo.runGuidedTour / BrowserRTKernelKitDemo.buildHandoffMarkdown / BrowserRTKernelKitDemo.importHandoffMarkdown / BrowserRTKernelKitDemo.buildReadinessGate / runnerInfo / pageWorkbenchReady / renderedTranscript / passedStages / loadHandoff / clearHandoff.
