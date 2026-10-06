import {
  KERNEL_KIT_DEMO_NON_CLAIMS,
  KERNEL_KIT_SUPPORT_BUNDLE_FORMAT,
  KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS,
  KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS,
  KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS,
  validateKernelKitSupportBundle,
  validateKernelKitSupportBundleDiff,
  validateKernelKitGuidedTourReceipt
} from './kernel-kit-demo.mjs';
export const KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT = 'browserrt-kernel-kit-handoff-markdown-v1';
export const KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS = Object.freeze([
  'No production handoff-markdown claim.',
  'No automated next-session correctness claim.',
  'No support-bundle authenticity or signature claim.',
  'No telemetry backend ingestion claim.',
  'No automated failure triage claim.',
  'No root-cause analysis claim.',
  'No automated failure recovery claim.',
  'No product-market-fit claim.',
  'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
  'No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim.',
  'No throughput, latency, SLO, or real performance claim.',
  'No exactly-once delivery claim.'
]);
function isObj(value) { return value && typeof value === 'object'; }
function unique(list) { return Array.from(new Set((list || []).filter(Boolean))); }
function safeString(value, fallback = '') { return value === undefined || value === null ? fallback : String(value); }
function bool(value) { return value === true; }
function bulletList(items) { return (items || []).map((item) => `- ${safeString(item)}`).join('\n'); }
function commandList(items) { return (items || []).map((item) => `- \`${safeString(item)}\``).join('\n'); }
function section(title, body) { return `## ${title}\n\n${body || '_No content captured._'}\n`; }
function compactProof(bundle = {}) {
  const proof = bundle.proof || {};
  return Object.freeze({
    successPathPresent: bool(proof.successPathPresent),
    reloadReadbackPresent: bool(proof.reloadReadbackPresent),
    controlledFailurePresent: bool(proof.controlledFailurePresent),
    traceComparisonPresent: bool(proof.traceComparisonPresent),
    diagnosticRunbookPresent: bool(proof.diagnosticRunbookPresent),
    exportReceiptPresent: bool(proof.exportReceiptPresent),
    exactCommandsPresent: bool(proof.exactCommandsPresent),
    nonClaimsVisible: bool(proof.nonClaimsVisible)
  });
}
function compactDiff(diff = {}) {
  return Object.freeze({
    present: isObj(diff) && diff.format !== undefined,
    status: diff.status || null,
    riskFlags: Object.freeze(diff.riskFlags || []),
    revisionSkew: diff.diff?.revisionSkew === true,
    candidateValid: diff.proof?.candidateValid === true,
    regressionRisk: diff.proof?.regressionRisk === true
  });
}
function compactTour(tour = {}) {
  return Object.freeze({
    present: isObj(tour) && tour.format !== undefined,
    stepCount: Array.isArray(tour.tourSteps) ? tour.tourSteps.length : Array.isArray(tour.steps) ? tour.steps.length : 0,
    passedCount: tour.validation?.passedCount || tour.proof?.passedCount || 0,
    audience: tour.audience || 'future-session-maintainer',
    supportBundleValidWhenPresent: tour.proof?.supportBundleValidWhenPresent === true
  });
}
export function createKernelKitHandoffMarkdown(fields = {}) {
  const supportBundle = fields.supportBundle || fields.bundle || null;
  const diff = fields.diff || fields.supportBundleDiff || null;
  const guidedTour = fields.guidedTour || fields.tour || null;
  const revision = fields.revision || supportBundle?.revision || guidedTour?.revision || diff?.revision || 'rev0054';
  const bundleValidation = supportBundle ? validateKernelKitSupportBundle(supportBundle) : { ok: false, errors: ['supportBundle missing'], sectionCount: 0, commandCount: 0, format: null };
  const diffValidation = diff ? validateKernelKitSupportBundleDiff(diff) : { ok: false, errors: ['diff missing'], riskCount: 0, proofRowCount: 0, format: null, status: null };
  const tourValidation = guidedTour ? validateKernelKitGuidedTourReceipt(guidedTour) : { ok: false, errors: ['guidedTour missing'], stepCount: 0, passedCount: 0, format: null };
  const proof = compactProof(supportBundle || {});
  const diffSummary = compactDiff(diff || {});
  const tourSummary = compactTour(guidedTour || {});
  const exactCommands = unique([
    ...((supportBundle && supportBundle.exactCommands) || []),
    ...((diff && diff.exactCommands) || []),
    ...((guidedTour && guidedTour.exactCommands) || []),
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-handoff-markdown-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-handoff-markdown-audit --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1',
    'python3 tools/check_cube.py'
  ]);
  const nextSessionChecklist = Object.freeze(fields.nextSessionChecklist || [
    'Run make turn-start or node tools/turn_bootstrap.mjs --write first.',
    'Run the release-tier handoff Markdown proof before editing the demo surface.',
    'Run browser:kernel-kit-demo-proof only when browser budget is intentional.',
    'Read non-claims before promoting any OPFS, durability, performance, or cross-browser statement.',
    'If support-bundle diff risk flags appear, fix docs/receipt/proof surfaces before runtime widening.'
  ]);
  const nonClaims = unique([
    ...KERNEL_KIT_DEMO_NON_CLAIMS,
    ...KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS,
    ...KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS,
    ...KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS,
    ...KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS
  ]);
  const status = bundleValidation.ok && proof.successPathPresent && proof.controlledFailurePresent && proof.diagnosticRunbookPresent && proof.nonClaimsVisible ? 'handoff-ready' : 'incomplete';
  const summaryLines = [
    `Revision: ${revision}`,
    `Status: ${status}`,
    `Support bundle format: ${supportBundle?.format || 'missing'}`,
    `Support bundle validation: ${bundleValidation.ok}`,
    `Guided tour validation: ${tourValidation.ok}`,
    `Diff status: ${diffSummary.status || 'not-provided'}`,
    `Diff risk flags: ${diffSummary.riskFlags.length ? diffSummary.riskFlags.join(', ') : 'none'}`
  ];
  const proofLines = Object.entries(proof).map(([key, value]) => `- ${key}: ${value}`);
  const markdown = [
    `# BrowserRT Kernel Kit Handoff — ${revision}`,
    '',
    'This Markdown brief is generated from the Kernel Kit support bundle, guided tour, and support-bundle diff so a future session can resume the office without reconstructing state from raw JSON panels.',
    '',
    section('Summary', bulletList(summaryLines)),
    section('Proof booleans', proofLines.join('\n')),
    section('Next-session checklist', bulletList(nextSessionChecklist)),
    section('Exact commands', commandList(exactCommands)),
    section('Guided-tour summary', bulletList([
      `present: ${tourSummary.present}`,
      `audience: ${tourSummary.audience}`,
      `stepCount: ${tourSummary.stepCount}`,
      `supportBundleValidWhenPresent: ${tourSummary.supportBundleValidWhenPresent}`
    ])),
    section('Support-bundle diff summary', bulletList([
      `present: ${diffSummary.present}`,
      `status: ${diffSummary.status || 'not-provided'}`,
      `revisionSkew: ${diffSummary.revisionSkew}`,
      `candidateValid: ${diffSummary.candidateValid}`,
      `regressionRisk: ${diffSummary.regressionRisk}`,
      `riskFlags: ${diffSummary.riskFlags.length ? diffSummary.riskFlags.join(', ') : 'none'}`
    ])),
    section('Non-claims', bulletList(nonClaims)),
    '_End of generated BrowserRT Kernel Kit handoff Markdown._'
  ].join('\n');
  return Object.freeze({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT,
    handoffMarkdownId: fields.handoffMarkdownId || `${revision}-kernel-kit-handoff-markdown`,
    generatedAt: fields.generatedAt || 'deterministic-handoff-markdown',
    status,
    purpose: 'Create a human-pasteable next-session brief from the Kernel Kit workbench support bundle, guided tour, diff, commands, proof booleans, and non-claims.',
    posture: 'handoff-markdown-not-authenticity-not-automated-triage-not-production-support',
    supportBundle: Object.freeze({ present: Boolean(supportBundle), format: supportBundle?.format || null, validation: bundleValidation, bundleId: supportBundle?.bundleId || null }),
    guidedTour: Object.freeze({ ...tourSummary, validation: tourValidation }),
    supportBundleDiff: Object.freeze({ ...diffSummary, validation: diffValidation }),
    proof,
    nextSessionChecklist,
    exactCommands: Object.freeze(exactCommands),
    markdown,
    sections: Object.freeze(['summary','proof-booleans','next-session-checklist','exact-commands','guided-tour-summary','support-bundle-diff-summary','non-claims']),
    nonClaims: Object.freeze(nonClaims)
  });
}
export function validateKernelKitHandoffMarkdown(report = {}) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['handoff Markdown report must be an object'], commandCount: 0, markdownBytes: 0, sectionCount: 0 });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.format !== KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT) errors.push(`format must be ${KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT}`);
  if (!['handoff-ready','incomplete'].includes(report.status)) errors.push('status must be handoff-ready or incomplete');
  if (!String(report.markdown || '').includes('# BrowserRT Kernel Kit Handoff')) errors.push('markdown missing title');
  if (!String(report.markdown || '').includes('## Exact commands')) errors.push('markdown missing exact commands section');
  if (!String(report.markdown || '').includes('## Non-claims')) errors.push('markdown missing non-claims section');
  for (const key of ['successPathPresent','controlledFailurePresent','diagnosticRunbookPresent','exactCommandsPresent','nonClaimsVisible']) {
    if (report.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  for (const needle of ['demo:kernel-kit-handoff-markdown-proof','facility:kernel-kit-handoff-markdown-audit','browser:kernel-kit-demo-proof','python3 tools/check_cube.py']) {
    if (!report.exactCommands?.some((cmd) => String(cmd).includes(needle))) errors.push(`missing handoff Markdown command for ${needle}`);
    if (!String(report.markdown || '').includes(needle)) errors.push(`markdown missing command ${needle}`);
  }
  for (const claim of ['No production handoff-markdown claim.','No automated next-session correctness claim.','No support-bundle authenticity or signature claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!report.nonClaims?.includes(claim)) errors.push(`missing handoff Markdown non-claim: ${claim}`);
    if (!String(report.markdown || '').includes(claim)) errors.push(`markdown missing non-claim: ${claim}`);
  }
  if (!Array.isArray(report.sections) || report.sections.length < 6) errors.push('sections must include handoff Markdown sections');
  if (!String(report.markdown || '').includes('Guided-tour summary')) errors.push('markdown missing guided-tour summary');
  if (!String(report.markdown || '').includes('Support-bundle diff summary')) errors.push('markdown missing support-bundle diff summary');
  return Object.freeze({
    ok: errors.length === 0,
    errors,
    commandCount: report.exactCommands?.length || 0,
    markdownBytes: new TextEncoder().encode(String(report.markdown || '')).length,
    sectionCount: report.sections?.length || 0,
    status: report.status || null,
    format: report.format || null
  });
}
