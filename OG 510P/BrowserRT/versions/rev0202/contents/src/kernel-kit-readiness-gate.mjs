import {
  validateKernelKitSupportBundle,
  validateKernelKitSupportBundleDiff,
  validateKernelKitGuidedTourReceipt,
  validateKernelKitDiagnosticRunbook,
  validateKernelKitTraceComparison,
  validateKernelKitDemoExportBundle,
  KERNEL_KIT_DEMO_NON_CLAIMS,
  KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS,
  KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS,
  KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS
} from './kernel-kit-demo.mjs';
import {
  validateKernelKitHandoffMarkdown,
  KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS
} from './kernel-kit-handoff-markdown.mjs';
import {
  validateKernelKitHandoffMarkdownImportReport,
  KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS
} from './kernel-kit-handoff-reader.mjs';
export const KERNEL_KIT_READINESS_GATE_FORMAT = 'browserrt-kernel-kit-readiness-gate-v1';
export const KERNEL_KIT_READINESS_GATE_PERSONAS = Object.freeze([
  'future-session-maintainer',
  'browser-heavy-app-builder',
  'skeptical-reviewer'
]);
export const KERNEL_KIT_READINESS_GATE_REQUIRED_GATES = Object.freeze([
  'success-path-visible',
  'reload-readback-visible',
  'bounded-failure-visible',
  'trace-comparison-visible',
  'diagnostic-runbook-visible',
  'support-bundle-portable',
  'support-bundle-diff-visible',
  'guided-tour-visible',
  'handoff-markdown-readable',
  'handoff-markdown-importable',
  'exact-commands-present',
  'non-claims-present',
  'readiness-inputs-evidence-bound',
  'browser-light-release-preserved'
]);
export const KERNEL_KIT_READINESS_GATE_NON_CLAIMS = Object.freeze([
  'No production readiness-gate claim.',
  'No automated demo-go/no-go claim.',
  'No product-market-fit claim.',
  'No user-demand proof.',
  'No support-bundle authenticity or signature claim.',
  'No telemetry backend ingestion claim.',
  'No automated failure triage claim.',
  'No root-cause analysis claim.',
  'No automated failure recovery claim.'
]);
function isObj(value) { return value && typeof value === 'object'; }
function uniq(values = []) { return Object.freeze([...new Set(values.filter(Boolean).map(String))]); }
function commandIncludes(commands = [], needle) { return Array.isArray(commands) && commands.some((cmd) => String(cmd).includes(needle)); }
function nonClaimIncludes(nonClaims = [], claim) { return Array.isArray(nonClaims) && nonClaims.map(String).includes(claim); }
function ok(validation) { return validation?.ok === true; }
function compactValidation(name, value, validator) {
  const validation = value ? validator(value) : { ok: false, errors: [`${name} missing`] };
  return Object.freeze({ name, present: Boolean(value), ok: validation.ok === true, errorCount: validation.errors?.length || 0, validation });
}
function gate(id, label, passed, evidence = [], missing = [], owner = 'future-session-maintainer') {
  return Object.freeze({ id, label, passed: passed === true, evidence: Object.freeze(evidence), missing: Object.freeze(missing), owner });
}
function personaTrack(id, label, gateIds = [], gateMap = new Map()) {
  const gates = gateIds.map((gateId) => gateMap.get(gateId)).filter(Boolean);
  const passed = gates.every((row) => row.passed === true);
  return Object.freeze({ id, label, passed, gateIds: Object.freeze(gateIds), passedGateCount: gates.filter((row) => row.passed).length, gateCount: gates.length });
}
function truthyProof(report = {}, keys = []) {
  const sources = [
    report?.proof,
    report?.observations,
    report?.observations?.proof,
    report?.observations?.work,
    report?.observations?.work?.proof,
    report?.observations?.reload,
    report?.observations?.reload?.proof,
    report?.success?.proof,
    report?.reload?.proof
  ].filter(isObj);
  return keys.some((key) => sources.some((source) => source?.[key] === true));
}
function createKernelKitReadinessInputProof(fields = {}, supportProof = {}) {
  const successReport = fields.successReport || fields.workReport || fields.success || fields.work || null;
  const reloadReport = fields.reloadReport || fields.reload || null;
  const failureReport = fields.failureReport || fields.failure || null;
  const explicit = fields.browserProof || fields.browser || fields.inputProof || null;
  const explicitProof = explicit?.proof || explicit || {};
  const sourceReports = Object.freeze({
    success: isObj(successReport),
    reload: isObj(reloadReport),
    failure: isObj(failureReport)
  });
  const storageWrite = truthyProof(successReport, ['storageWrite','storageLaneWriteRead']) || supportProof.successPathPresent === true || explicitProof.storageWrite === true;
  const reloadReadback = truthyProof(reloadReport, ['reloadReadback','storageLaneWriteRead','storageWrite']) || supportProof.reloadReadbackPresent === true || explicitProof.reloadReadback === true;
  const controlledFailureMode = truthyProof(failureReport, ['controlledFailure','preventedMutation','failurePreventedMutation']) || failureReport?.proof?.controlledFailure === true || supportProof.controlledFailurePresent === true || explicitProof.controlledFailureMode === true || explicitProof.controlledFailure === true;
  const explicitEvidenceBound = explicitProof.evidenceBound === true && explicitProof.storageWrite === true && explicitProof.reloadReadback === true && (explicitProof.controlledFailureMode === true || explicitProof.controlledFailure === true);
  const derivedEvidenceBound = sourceReports.success && sourceReports.reload && sourceReports.failure && storageWrite && reloadReadback && controlledFailureMode;
  const evidenceBound = derivedEvidenceBound || explicitEvidenceBound;
  const source = derivedEvidenceBound ? 'derived-from-success-reload-failure-reports' : (explicitEvidenceBound ? 'explicit-evidence-bound-proof' : 'unbound-or-incomplete-proof');
  return Object.freeze({
    source,
    evidenceBound,
    storageWrite,
    reloadReadback,
    controlledFailureMode,
    sourceReports,
    explicitProofSupplied: Boolean(explicit),
    explicitProofEvidenceBound: explicitEvidenceBound,
    missingSourceReports: Object.freeze(Object.entries(sourceReports).filter(([, present]) => !present).map(([name]) => name)),
    nonClaim: 'Readiness input proof is a binding check over supplied success/reload/failure evidence, not a production go/no-go claim.'
  });
}
export function createKernelKitReadinessGate(fields = {}) {
  const revision = fields.revision || fields.supportBundle?.revision || fields.guidedTour?.revision || 'rev0054';
  const supportBundle = fields.supportBundle || null;
  const supportBundleDiff = fields.supportBundleDiff || fields.diff || null;
  const guidedTour = fields.guidedTour || null;
  const handoffMarkdown = fields.handoffMarkdown || null;
  const handoffMarkdownImport = fields.handoffMarkdownImport || fields.importReport || null;
  const traceComparison = fields.traceComparison || fields.comparison || null;
  const diagnosticRunbook = fields.diagnosticRunbook || fields.runbook || null;
  const exportBundle = fields.exportBundle || fields.exportReceipt?.bundle || fields.exportReceipt || null;
  const browserProof = fields.browserProof || fields.browser || fields.inputProof || null;
  const supportValidation = compactValidation('supportBundle', supportBundle, validateKernelKitSupportBundle);
  const diffValidation = compactValidation('supportBundleDiff', supportBundleDiff, validateKernelKitSupportBundleDiff);
  const tourValidation = compactValidation('guidedTour', guidedTour, validateKernelKitGuidedTourReceipt);
  const handoffValidation = compactValidation('handoffMarkdown', handoffMarkdown, validateKernelKitHandoffMarkdown);
  const importValidation = compactValidation('handoffMarkdownImport', handoffMarkdownImport, validateKernelKitHandoffMarkdownImportReport);
  const comparisonValidation = compactValidation('traceComparison', traceComparison, validateKernelKitTraceComparison);
  const runbookValidation = compactValidation('diagnosticRunbook', diagnosticRunbook, validateKernelKitDiagnosticRunbook);
  const exportValidation = compactValidation('exportBundle', exportBundle, validateKernelKitDemoExportBundle);
  const supportProof = supportBundle?.proof || {};
  const inputProof = createKernelKitReadinessInputProof({ ...fields, browserProof }, supportProof);
  const browserProofObj = inputProof;
  const commands = uniq([
    ...(supportBundle?.exactCommands || []),
    ...(supportBundleDiff?.exactCommands || []),
    ...(guidedTour?.exactCommands || []),
    ...(handoffMarkdown?.exactCommands || []),
    ...(handoffMarkdownImport?.resumeCommands || []),
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-readiness-gate-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-readiness-gate-audit --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1',
    'python3 tools/check_cube.py'
  ]);
  const nonClaims = uniq([
    ...KERNEL_KIT_DEMO_NON_CLAIMS,
    ...KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS,
    ...KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS,
    ...KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS,
    ...KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS,
    ...KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS,
    ...KERNEL_KIT_READINESS_GATE_NON_CLAIMS,
    ...(supportBundle?.nonClaims || []),
    ...(handoffMarkdown?.nonClaims || []),
    ...(handoffMarkdownImport?.nonClaims || [])
  ]);
  const gateRows = [
    gate('success-path-visible', 'Success path is visible in bundle/browser proof', supportProof.successPathPresent === true || browserProofObj.storageWrite === true, ['supportBundle.proof.successPathPresent', 'browserProof.storageWrite'], [], 'browser-heavy-app-builder'),
    gate('reload-readback-visible', 'Reload readback is visible', supportProof.reloadReadbackPresent === true || browserProofObj.reloadReadback === true, ['supportBundle.proof.reloadReadbackPresent', 'browserProof.reloadReadback'], [], 'browser-heavy-app-builder'),
    gate('bounded-failure-visible', 'Controlled bounded failure is visible', supportProof.controlledFailurePresent === true || browserProofObj.controlledFailureMode === true, ['supportBundle.proof.controlledFailurePresent', 'browserProof.controlledFailureMode'], [], 'skeptical-reviewer'),
    gate('trace-comparison-visible', 'Trace comparison validates', supportProof.traceComparisonPresent === true && ok(comparisonValidation.validation), ['traceComparison.validation.ok'], [], 'skeptical-reviewer'),
    gate('diagnostic-runbook-visible', 'Diagnostic runbook validates', supportProof.diagnosticRunbookPresent === true && ok(runbookValidation.validation), ['diagnosticRunbook.validation.ok'], [], 'future-session-maintainer'),
    gate('support-bundle-portable', 'Support bundle validates', ok(supportValidation.validation), ['supportBundle.validation.ok'], [], 'future-session-maintainer'),
    gate('support-bundle-diff-visible', 'Support-bundle diff validates', ok(diffValidation.validation), ['supportBundleDiff.validation.ok'], [], 'future-session-maintainer'),
    gate('guided-tour-visible', 'Guided tour validates', ok(tourValidation.validation), ['guidedTour.validation.ok'], [], 'future-session-maintainer'),
    gate('handoff-markdown-readable', 'Handoff Markdown validates', ok(handoffValidation.validation) && handoffMarkdown?.status === 'handoff-ready', ['handoffMarkdown.status=handoff-ready'], [], 'future-session-maintainer'),
    gate('handoff-markdown-importable', 'Handoff Markdown import validates', ok(importValidation.validation) && handoffMarkdownImport?.status === 'handoff-import-ready', ['handoffMarkdownImport.status=handoff-import-ready'], [], 'future-session-maintainer'),
    gate('exact-commands-present', 'Exact commands include release, audit, browser, and cube checks', commandIncludes(commands, 'demo:kernel-kit-readiness-gate-proof') && commandIncludes(commands, 'facility:kernel-kit-readiness-gate-audit') && commandIncludes(commands, 'browser:kernel-kit-demo-proof') && commandIncludes(commands, 'python3 tools/check_cube.py'), ['exactCommands'], [], 'future-session-maintainer'),
    gate('non-claims-present', 'Non-claim boundaries are visible', nonClaimIncludes(nonClaims, 'No production readiness-gate claim.') && nonClaimIncludes(nonClaims, 'No product-market-fit claim.') && nonClaimIncludes(nonClaims, 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'), ['nonClaims'], [], 'skeptical-reviewer'),
    gate('readiness-inputs-evidence-bound', 'Readiness inputs are bound to supplied success/reload/failure evidence rather than a placeholder proof', inputProof.evidenceBound === true, ['successReport', 'reloadReport', 'failureReport', 'inputProof.evidenceBound'], inputProof.missingSourceReports, 'skeptical-reviewer'),
    gate('browser-light-release-preserved', 'Broad release remains browser-light; browser proof is explicit by id', fields.releasePosture === 'browser-light' || fields.browserLightRelease === true, ['releasePosture=browser-light'], [], 'future-session-maintainer')
  ];
  const gateMap = new Map(gateRows.map((row) => [row.id, row]));
  const personaTracks = Object.freeze([
    personaTrack('future-session-maintainer', 'Future session maintainer', ['support-bundle-portable','support-bundle-diff-visible','guided-tour-visible','handoff-markdown-readable','handoff-markdown-importable','exact-commands-present','readiness-inputs-evidence-bound','browser-light-release-preserved'], gateMap),
    personaTrack('browser-heavy-app-builder', 'Browser-heavy app builder', ['success-path-visible','reload-readback-visible','bounded-failure-visible','support-bundle-portable'], gateMap),
    personaTrack('skeptical-reviewer', 'Skeptical reviewer', ['bounded-failure-visible','trace-comparison-visible','non-claims-present','readiness-inputs-evidence-bound','exact-commands-present'], gateMap)
  ]);
  const missingGateIds = gateRows.filter((row) => !row.passed).map((row) => row.id);
  const status = missingGateIds.length === 0 && personaTracks.every((row) => row.passed) ? 'ready-for-next-usefulness-pass' : 'needs-attention';
  const proof = Object.freeze({
    allRequiredGatesPass: missingGateIds.length === 0,
    allPersonasPass: personaTracks.every((row) => row.passed),
    successPathVisible: gateMap.get('success-path-visible').passed,
    reloadReadbackVisible: gateMap.get('reload-readback-visible').passed,
    boundedFailureVisible: gateMap.get('bounded-failure-visible').passed,
    handoffMarkdownRoundTripVisible: gateMap.get('handoff-markdown-readable').passed && gateMap.get('handoff-markdown-importable').passed,
    exactCommandsPresent: gateMap.get('exact-commands-present').passed,
    nonClaimsVisible: gateMap.get('non-claims-present').passed,
    readinessInputsEvidenceBound: gateMap.get('readiness-inputs-evidence-bound').passed,
    browserLightReleasePreserved: gateMap.get('browser-light-release-preserved').passed
  });
  return Object.freeze({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_READINESS_GATE_FORMAT,
    readinessGateId: fields.readinessGateId || `${revision}-kernel-kit-readiness-gate`,
    generatedAt: fields.generatedAt || 'deterministic-kernel-kit-readiness-gate',
    status,
    purpose: 'Evaluate whether the Kernel Kit demo is useful enough for the next session to continue from the workbench instead of reconstructing evidence from raw panels.',
    posture: 'readiness-gate-not-production-go-no-go-not-market-validation',
    validations: Object.freeze({ supportBundle: supportValidation, supportBundleDiff: diffValidation, guidedTour: tourValidation, handoffMarkdown: handoffValidation, handoffMarkdownImport: importValidation, traceComparison: comparisonValidation, diagnosticRunbook: runbookValidation, exportBundle: exportValidation }),
    inputProof,
    gates: Object.freeze(gateRows),
    missingGateIds: Object.freeze(missingGateIds),
    personaTracks,
    proof,
    readinessSummary: Object.freeze({
      passedGateCount: gateRows.filter((row) => row.passed).length,
      gateCount: gateRows.length,
      passedPersonaCount: personaTracks.filter((row) => row.passed).length,
      personaCount: personaTracks.length,
      recommendation: status === 'ready-for-next-usefulness-pass' ? 'Continue improving the Kernel Kit demo through one small earned usefulness slice.' : 'Fix missing gates before widening runtime claims or adding expensive browser/provider slices.'
    }),
    nextUsefulMoves: Object.freeze([
      'Keep the next Kernel Kit demo slice visible in the page, page API, release proof, browser proof, and non-claim charter.',
      'Run demo:kernel-kit-readiness-gate-proof after editing handoff or support-bundle surfaces.',
      'Run browser:kernel-kit-demo-proof only when browser/CDP budget is intentional.',
      'Do not promote OPFS durability, cross-browser, performance, or product-market claims from this gate.'
    ]),
    exactCommands: commands,
    nonClaims
  });
}
export function validateKernelKitReadinessGate(report = {}) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['readiness gate report must be an object'], gateCount: 0, personaCount: 0, commandCount: 0 });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.format !== KERNEL_KIT_READINESS_GATE_FORMAT) errors.push(`format must be ${KERNEL_KIT_READINESS_GATE_FORMAT}`);
  if (report.status !== 'ready-for-next-usefulness-pass') errors.push('status must be ready-for-next-usefulness-pass');
  for (const id of KERNEL_KIT_READINESS_GATE_REQUIRED_GATES) {
    if (!report.gates?.some((row) => row.id === id && row.passed === true)) errors.push(`gate ${id} must pass`);
  }
  for (const persona of KERNEL_KIT_READINESS_GATE_PERSONAS) {
    if (!report.personaTracks?.some((row) => row.id === persona && row.passed === true)) errors.push(`persona ${persona} must pass`);
  }
  for (const key of ['allRequiredGatesPass','allPersonasPass','successPathVisible','reloadReadbackVisible','boundedFailureVisible','handoffMarkdownRoundTripVisible','exactCommandsPresent','nonClaimsVisible','readinessInputsEvidenceBound','browserLightReleasePreserved']) {
    if (report.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const needle of ['demo:kernel-kit-readiness-gate-proof','facility:kernel-kit-readiness-gate-audit','browser:kernel-kit-demo-proof','python3 tools/check_cube.py']) {
    if (!commandIncludes(report.exactCommands, needle)) errors.push(`missing readiness command for ${needle}`);
  }
  if (report.inputProof?.evidenceBound !== true) errors.push('inputProof.evidenceBound must be true');
  if (report.inputProof?.source === 'unbound-or-incomplete-proof') errors.push('readiness input proof must not be a placeholder');
  for (const claim of ['No production readiness-gate claim.','No automated demo-go/no-go claim.','No product-market-fit claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!nonClaimIncludes(report.nonClaims, claim)) errors.push(`missing readiness non-claim: ${claim}`);
  }
  return Object.freeze({ ok: errors.length === 0, errors, gateCount: report.gates?.length || 0, personaCount: report.personaTracks?.length || 0, commandCount: report.exactCommands?.length || 0, status: report.status || null, format: report.format || null });
}
