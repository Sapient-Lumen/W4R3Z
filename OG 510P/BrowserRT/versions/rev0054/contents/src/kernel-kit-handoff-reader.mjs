// BrowserRT Kernel Kit handoff Markdown reader/import surface.
// This closes the handoff loop: the demo can generate a human Markdown brief
// and later parse/validate that same brief without claiming authenticity,
// automated next-session correctness, telemetry ingestion, or production support.

import {
  KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT,
  KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS
} from './kernel-kit-handoff-markdown.mjs';
import {
  KERNEL_KIT_DEMO_NON_CLAIMS,
  KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS,
  KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS,
  KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS
} from './kernel-kit-demo.mjs';

export const KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT = 'browserrt-kernel-kit-handoff-markdown-import-v1';

export const KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS = Object.freeze([
  'No production handoff-markdown import claim.',
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

export const KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS = Object.freeze([
  'node tools/run_tests.mjs --tier release --id demo:kernel-kit-handoff-markdown-proof --jobs 1',
  'node tools/run_tests.mjs --tier release --id facility:kernel-kit-handoff-markdown-audit --jobs 1',
  'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1',
  'python3 tools/check_cube.py'
]);

export const KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_REQUIRED_NON_CLAIMS = Object.freeze([
  'No production runtime claim.',
  'No production handoff-markdown claim.',
  'No production handoff-markdown import claim.',
  'No automated next-session correctness claim.',
  'No support-bundle authenticity or signature claim.',
  'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.',
  'No WebGPU, WebNN, WebTransport, WebRTC, mobile lifecycle, or cross-browser conformance claim.',
  'No throughput, latency, SLO, or real performance claim.',
  'No exactly-once delivery claim.'
]);

const SECTION_RE = /^##\s+(.+?)\s*$/gm;

function isObj(value) { return value && typeof value === 'object'; }
function safeString(value) { return value === undefined || value === null ? '' : String(value); }
function unique(list) { return Array.from(new Set((list || []).filter(Boolean))); }
function markdownBytes(markdown) { return new TextEncoder().encode(safeString(markdown)).length; }

function extractRevision(markdown) {
  const title = markdown.match(/^#\s+BrowserRT Kernel Kit Handoff\s+—\s+(rev\d{4})/m);
  if (title) return title[1];
  const summary = markdown.match(/^-\s*Revision:\s*(rev\d{4})\s*$/m);
  return summary ? summary[1] : null;
}

function extractSections(markdown) {
  const headings = [];
  let m;
  while ((m = SECTION_RE.exec(markdown))) headings.push({ title: m[1].trim(), index: m.index, after: SECTION_RE.lastIndex });
  const sections = new Map();
  for (let i = 0; i < headings.length; i++) {
    const h = headings[i];
    const next = headings[i + 1]?.index ?? markdown.length;
    sections.set(h.title.toLowerCase(), markdown.slice(h.after, next).trim());
  }
  return Object.freeze({ headings: headings.map((h) => h.title), sections });
}

function extractBacktickCommands(sectionText) {
  const out = [];
  const re = /`([^`]+)`/g;
  let m;
  while ((m = re.exec(sectionText || ''))) out.push(m[1]);
  return unique(out);
}

function extractBullets(sectionText) {
  return unique((sectionText || '').split('\n').map((line) => line.match(/^\s*-\s+(.*)\s*$/)?.[1]?.trim()).filter(Boolean));
}

function extractProofBooleans(sectionText) {
  const proof = {};
  for (const line of (sectionText || '').split('\n')) {
    const m = line.match(/^\s*-\s+([A-Za-z0-9_-]+):\s*(true|false)\s*$/);
    if (m) proof[m[1]] = m[2] === 'true';
  }
  return Object.freeze(proof);
}

function missingFrom(haystack, required) {
  return required.filter((needle) => !haystack.includes(needle));
}

function summarizeSections(sections) {
  return Object.freeze({
    summary: sections.has('summary'),
    proofBooleans: sections.has('proof booleans'),
    nextSessionChecklist: sections.has('next-session checklist'),
    exactCommands: sections.has('exact commands'),
    guidedTourSummary: sections.has('guided-tour summary'),
    supportBundleDiffSummary: sections.has('support-bundle diff summary'),
    nonClaims: sections.has('non-claims')
  });
}

export function createKernelKitHandoffMarkdownImportReport(input, fields = {}) {
  const markdown = typeof input === 'string' ? input : safeString(input?.markdown ?? input?.handoffMarkdown?.markdown ?? input?.text);
  const parsed = extractSections(markdown);
  const sections = parsed.sections;
  const exactCommands = extractBacktickCommands(sections.get('exact commands'));
  const nextSessionChecklist = extractBullets(sections.get('next-session checklist'));
  const nonClaims = unique([...extractBullets(sections.get('non-claims')), ...KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS]);
  const proofBooleans = extractProofBooleans(sections.get('proof booleans'));
  const revision = fields.revision || extractRevision(markdown) || 'unknown';
  const missingRequiredCommands = missingFrom(exactCommands, KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS);
  const missingRequiredNonClaims = KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_REQUIRED_NON_CLAIMS.filter((claim) => !markdown.includes(claim) && !nonClaims.includes(claim));
  const sectionPresence = summarizeSections(sections);
  const requiredSectionNames = ['Summary','Proof booleans','Next-session checklist','Exact commands','Guided-tour summary','Support-bundle diff summary','Non-claims'];
  const missingSections = requiredSectionNames.filter((title) => !parsed.headings.includes(title));
  const proof = Object.freeze({
    titlePresent: /^#\s+BrowserRT Kernel Kit Handoff/m.test(markdown),
    revisionPresent: /^rev\d{4}$/.test(revision),
    exactCommandsPresent: exactCommands.length >= 4,
    requiredCommandsPresent: missingRequiredCommands.length === 0,
    nonClaimsVisible: nonClaims.length >= 8,
    requiredNonClaimsPresent: missingRequiredNonClaims.length === 0,
    proofBooleansPresent: Object.keys(proofBooleans).length >= 6,
    successPathPresent: proofBooleans.successPathPresent === true,
    controlledFailurePresent: proofBooleans.controlledFailurePresent === true,
    diagnosticRunbookPresent: proofBooleans.diagnosticRunbookPresent === true,
    exportReceiptPresent: proofBooleans.exportReceiptPresent === true,
    supportBundleDiffSummaryPresent: sectionPresence.supportBundleDiffSummary,
    guidedTourSummaryPresent: sectionPresence.guidedTourSummary,
    nextSessionChecklistPresent: nextSessionChecklist.length >= 3,
    notAuthenticity: markdown.includes('No support-bundle authenticity or signature claim.'),
    notProduction: markdown.includes('No production runtime claim.'),
    notAutomatedCorrectness: markdown.includes('No automated next-session correctness claim.')
  });
  const status = Object.values(proof).every(Boolean) && missingSections.length === 0 ? 'handoff-import-ready' : 'handoff-import-needs-attention';
  const riskFlags = unique([
    ...missingSections.map((name) => `missing-section:${name}`),
    ...missingRequiredCommands.map((cmd) => `missing-command:${cmd}`),
    ...missingRequiredNonClaims.map((claim) => `missing-non-claim:${claim}`),
    ...(proof.revisionPresent ? [] : ['missing-revision']),
    ...(proof.requiredCommandsPresent ? [] : ['commands-incomplete']),
    ...(proof.requiredNonClaimsPresent ? [] : ['non-claims-incomplete'])
  ]);
  return Object.freeze({
    project: 'BrowserRT',
    revision,
    schema: 1,
    format: KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT,
    sourceFormat: KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT,
    importId: fields.importId || `${revision}-kernel-kit-handoff-markdown-import`,
    generatedAt: fields.generatedAt || 'deterministic-handoff-markdown-import',
    status,
    purpose: 'Parse and validate a human-pasteable Kernel Kit handoff Markdown brief so a future session can resume from text without claiming authenticity or automated correctness.',
    posture: 'handoff-markdown-import-not-authenticity-not-automated-next-session-correctness-not-production-support',
    input: Object.freeze({ bytes: markdownBytes(markdown), lineCount: markdown.split('\n').length, titlePresent: proof.titlePresent }),
    parsed: Object.freeze({ headings: Object.freeze(parsed.headings), sectionPresence, revision, exactCommands: Object.freeze(exactCommands), nextSessionChecklist: Object.freeze(nextSessionChecklist), proofBooleans }),
    missing: Object.freeze({ sections: Object.freeze(missingSections), commands: Object.freeze(missingRequiredCommands), nonClaims: Object.freeze(missingRequiredNonClaims) }),
    riskFlags: Object.freeze(riskFlags),
    resumeCommands: Object.freeze(unique([...exactCommands, ...KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS])),
    proof,
    nonClaims: Object.freeze(unique([
      ...KERNEL_KIT_DEMO_NON_CLAIMS,
      ...KERNEL_KIT_SUPPORT_BUNDLE_NON_CLAIMS,
      ...KERNEL_KIT_SUPPORT_BUNDLE_DIFF_NON_CLAIMS,
      ...KERNEL_KIT_GUIDED_TOUR_NON_CLAIMS,
      ...KERNEL_KIT_HANDOFF_MARKDOWN_NON_CLAIMS,
      ...KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_NON_CLAIMS,
      ...nonClaims
    ]))
  });
}

export function validateKernelKitHandoffMarkdownImportReport(report = {}) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['handoff Markdown import report must be an object'], commandCount: 0, riskCount: 0, status: null, format: null });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.format !== KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT) errors.push(`format must be ${KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_FORMAT}`);
  if (report.sourceFormat !== KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT) errors.push(`sourceFormat must be ${KERNEL_KIT_HANDOFF_MARKDOWN_FORMAT}`);
  if (!['handoff-import-ready','handoff-import-needs-attention'].includes(report.status)) errors.push('status must be handoff-import-ready or handoff-import-needs-attention');
  if (!report.proof?.titlePresent) errors.push('title must be present');
  if (!report.proof?.revisionPresent) errors.push('revision must be present');
  if (!report.proof?.requiredCommandsPresent) errors.push('required commands must be present');
  if (!report.proof?.requiredNonClaimsPresent) errors.push('required non-claims must be present');
  if (!report.proof?.successPathPresent) errors.push('success path proof boolean must be present');
  if (!report.proof?.controlledFailurePresent) errors.push('controlled failure proof boolean must be present');
  if (!report.proof?.diagnosticRunbookPresent) errors.push('diagnostic runbook proof boolean must be present');
  if (!report.proof?.supportBundleDiffSummaryPresent) errors.push('support-bundle diff summary must be present');
  if (!report.proof?.guidedTourSummaryPresent) errors.push('guided-tour summary must be present');
  if (!report.proof?.notAuthenticity) errors.push('authenticity non-claim must be visible');
  if (!report.proof?.notProduction) errors.push('production non-claim must be visible');
  if (!report.proof?.notAutomatedCorrectness) errors.push('automated correctness non-claim must be visible');
  for (const command of KERNEL_KIT_HANDOFF_MARKDOWN_REQUIRED_COMMANDS) {
    if (!report.resumeCommands?.includes(command)) errors.push(`missing resume command: ${command}`);
  }
  for (const claim of KERNEL_KIT_HANDOFF_MARKDOWN_IMPORT_REQUIRED_NON_CLAIMS) {
    if (!report.nonClaims?.includes(claim)) errors.push(`missing non-claim: ${claim}`);
  }
  if (report.status === 'handoff-import-ready' && (report.riskFlags || []).length !== 0) errors.push('ready report must not carry risk flags');
  return Object.freeze({
    ok: errors.length === 0,
    errors,
    commandCount: report.resumeCommands?.length || 0,
    parsedCommandCount: report.parsed?.exactCommands?.length || 0,
    riskCount: report.riskFlags?.length || 0,
    sectionCount: report.parsed?.headings?.length || 0,
    markdownBytes: report.input?.bytes || 0,
    status: report.status || null,
    format: report.format || null
  });
}

// Static audit markers: browserrt-kernel-kit-handoff-markdown-import-v1; demo:kernel-kit-handoff-markdown-import-proof; facility:kernel-kit-handoff-markdown-import-audit; No production handoff-markdown import claim.
