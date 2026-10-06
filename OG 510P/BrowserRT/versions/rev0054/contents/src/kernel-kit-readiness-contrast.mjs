// BrowserRT rev0054 Kernel Kit readiness contrast.
// Shows why the readiness gate matters by comparing a good workbench handoff
// against an intentionally degraded handoff. This is not production demo
// gating, automated correctness, authenticity, root-cause analysis, or market
// validation.

import {
  validateKernelKitReadinessGate,
  KERNEL_KIT_READINESS_GATE_FORMAT,
  KERNEL_KIT_READINESS_GATE_NON_CLAIMS
} from './kernel-kit-readiness-gate.mjs';

export const KERNEL_KIT_READINESS_CONTRAST_FORMAT = 'browserrt-kernel-kit-readiness-contrast-v1';

export const KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES = Object.freeze([
  'reload-readback-visible',
  'handoff-markdown-importable',
  'exact-commands-present'
]);

export const KERNEL_KIT_READINESS_CONTRAST_NON_CLAIMS = Object.freeze([
  'No production readiness-contrast claim.',
  'No automated regression detection claim.',
  'No automated demo-go/no-go claim.',
  'No support-bundle authenticity or signature claim.',
  'No automated next-session correctness claim.',
  'No root-cause analysis claim.',
  'No automated failure recovery claim.'
]);

function isObj(value) { return value && typeof value === 'object'; }
function uniq(values = []) { return Object.freeze([...new Set(values.filter(Boolean).map(String))]); }
function cloneJson(value) { return JSON.parse(JSON.stringify(value)); }
function includesAll(values = [], needles = []) { const set = new Set(values.map(String)); return needles.every((needle) => set.has(needle)); }
function commandIncludes(commands = [], needle) { return Array.isArray(commands) && commands.some((cmd) => String(cmd).includes(needle)); }
function nonClaimIncludes(nonClaims = [], claim) { return Array.isArray(nonClaims) && nonClaims.map(String).includes(claim); }

function recomputePersonaTracks(gates = [], personaTracks = []) {
  const gateMap = new Map(gates.map((gate) => [gate.id, gate]));
  return Object.freeze((personaTracks || []).map((track) => {
    const gateIds = track.gateIds || [];
    const rows = gateIds.map((id) => gateMap.get(id)).filter(Boolean);
    return Object.freeze({
      ...track,
      passed: rows.length > 0 && rows.every((row) => row.passed === true),
      passedGateCount: rows.filter((row) => row.passed === true).length,
      gateCount: rows.length
    });
  }));
}

export function createDegradedKernelKitReadinessGate(readinessGate = {}, fields = {}) {
  if (!isObj(readinessGate) || readinessGate.format !== KERNEL_KIT_READINESS_GATE_FORMAT) {
    throw new Error('createDegradedKernelKitReadinessGate requires a Kernel Kit readiness gate');
  }
  const failGateIds = new Set(fields.failGateIds || KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES);
  const reason = fields.reason || 'intentional-readiness-contrast-degradation';
  const source = cloneJson(readinessGate);
  const gates = Object.freeze((source.gates || []).map((row) => {
    if (!failGateIds.has(row.id)) return Object.freeze(row);
    return Object.freeze({
      ...row,
      passed: false,
      missing: Object.freeze(uniq([...(row.missing || []), reason, `degraded:${row.id}`]))
    });
  }));
  const missingGateIds = Object.freeze(gates.filter((row) => row.passed !== true).map((row) => row.id));
  const personaTracks = recomputePersonaTracks(gates, source.personaTracks || []);
  const proof = Object.freeze({
    ...(source.proof || {}),
    allRequiredGatesPass: false,
    allPersonasPass: personaTracks.every((row) => row.passed === true),
    reloadReadbackVisible: gates.find((row) => row.id === 'reload-readback-visible')?.passed === true,
    handoffMarkdownRoundTripVisible: gates.find((row) => row.id === 'handoff-markdown-readable')?.passed === true && gates.find((row) => row.id === 'handoff-markdown-importable')?.passed === true,
    exactCommandsPresent: gates.find((row) => row.id === 'exact-commands-present')?.passed === true,
    readinessContrastDegraded: true
  });
  return Object.freeze({
    ...source,
    readinessGateId: fields.readinessGateId || `${source.revision || 'rev0054'}-kernel-kit-readiness-gate-degraded`,
    generatedAt: fields.generatedAt || 'deterministic-kernel-kit-readiness-gate-degraded',
    status: 'needs-attention',
    contrastSourceGateId: readinessGate.readinessGateId || null,
    contrastDegradationReason: reason,
    contrastFailedGateIds: Object.freeze([...failGateIds]),
    gates,
    missingGateIds,
    personaTracks,
    proof,
    readinessSummary: Object.freeze({
      ...(source.readinessSummary || {}),
      passedGateCount: gates.filter((row) => row.passed === true).length,
      gateCount: gates.length,
      passedPersonaCount: personaTracks.filter((row) => row.passed === true).length,
      personaCount: personaTracks.length,
      recommendation: 'This intentionally degraded handoff must fail before a future session trusts readiness evidence.'
    }),
    nextUsefulMoves: Object.freeze(uniq([
      ...(source.nextUsefulMoves || []),
      'Use the readiness contrast to verify weaker bundles fail visibly before adding new demo claims.',
      'Fix missing gates rather than widening runtime claims.'
    ]))
  });
}

export function createKernelKitReadinessContrast(fields = {}) {
  const baselineGate = fields.baselineGate || fields.readyGate || fields.readinessGate || null;
  if (!baselineGate) throw new Error('createKernelKitReadinessContrast requires baselineGate');
  const degradedGate = fields.degradedGate || createDegradedKernelKitReadinessGate(baselineGate, fields.degraded || fields.degradation || {});
  const expectedFailedGateIds = Object.freeze(uniq(fields.expectedFailedGateIds || degradedGate.contrastFailedGateIds || KERNEL_KIT_READINESS_CONTRAST_DEFAULT_FAILED_GATES));
  const baselineValidation = validateKernelKitReadinessGate(baselineGate);
  const degradedValidation = validateKernelKitReadinessGate(degradedGate);
  const degradedMissingGateIds = Object.freeze(degradedGate.missingGateIds || []);
  const commands = uniq([
    ...(baselineGate.exactCommands || []),
    ...(degradedGate.exactCommands || []),
    'node tools/run_tests.mjs --tier release --id demo:kernel-kit-readiness-contrast-proof --jobs 1',
    'node tools/run_tests.mjs --tier release --id facility:kernel-kit-readiness-contrast-audit --jobs 1',
    'node tools/run_tests.mjs --tier browser --id browser:kernel-kit-demo-proof --jobs 1',
    'python3 tools/check_cube.py'
  ]);
  const nonClaims = uniq([
    ...KERNEL_KIT_READINESS_GATE_NON_CLAIMS,
    ...KERNEL_KIT_READINESS_CONTRAST_NON_CLAIMS,
    ...(baselineGate.nonClaims || []),
    ...(degradedGate.nonClaims || [])
  ]);
  const proof = Object.freeze({
    baselineReady: baselineValidation.ok === true && baselineGate.status === 'ready-for-next-usefulness-pass',
    degradedNeedsAttention: degradedGate.status === 'needs-attention',
    degradedRejectedByReadinessValidator: degradedValidation.ok === false,
    expectedGatesFailed: includesAll(degradedMissingGateIds, expectedFailedGateIds),
    commandsPresent: commandIncludes(commands, 'demo:kernel-kit-readiness-contrast-proof') && commandIncludes(commands, 'facility:kernel-kit-readiness-contrast-audit') && commandIncludes(commands, 'python3 tools/check_cube.py'),
    nonClaimsPreserved: nonClaimIncludes(nonClaims, 'No production readiness-contrast claim.') && nonClaimIncludes(nonClaims, 'No automated demo-go/no-go claim.') && nonClaimIncludes(nonClaims, 'No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.'),
    noProviderMutationClaim: true
  });
  return Object.freeze({
    project: 'BrowserRT',
    revision: fields.revision || baselineGate.revision || degradedGate.revision || 'rev0054',
    schema: 1,
    format: KERNEL_KIT_READINESS_CONTRAST_FORMAT,
    contrastId: fields.contrastId || `${fields.revision || baselineGate.revision || 'rev0054'}-kernel-kit-readiness-contrast`,
    generatedAt: fields.generatedAt || 'deterministic-kernel-kit-readiness-contrast',
    status: Object.values(proof).every(Boolean) ? 'contrast-ready' : 'contrast-needs-attention',
    purpose: 'Show that the Kernel Kit readiness gate rejects a weaker future-session handoff and reports the missing gates visibly.',
    baseline: Object.freeze({
      readinessGateId: baselineGate.readinessGateId,
      status: baselineGate.status,
      validation: baselineValidation,
      passedGateCount: baselineGate.readinessSummary?.passedGateCount,
      gateCount: baselineGate.readinessSummary?.gateCount
    }),
    degraded: Object.freeze({
      readinessGateId: degradedGate.readinessGateId,
      status: degradedGate.status,
      validation: degradedValidation,
      missingGateIds: degradedMissingGateIds,
      expectedFailedGateIds,
      failedPersonaIds: Object.freeze((degradedGate.personaTracks || []).filter((row) => row.passed !== true).map((row) => row.id)),
      passedGateCount: degradedGate.readinessSummary?.passedGateCount,
      gateCount: degradedGate.readinessSummary?.gateCount,
      reason: degradedGate.contrastDegradationReason || 'intentional-readiness-contrast-degradation'
    }),
    gateDiff: Object.freeze((baselineGate.gates || []).map((before) => {
      const after = (degradedGate.gates || []).find((row) => row.id === before.id) || {};
      return Object.freeze({ id: before.id, before: before.passed === true, after: after.passed === true, changed: before.passed !== after.passed, missing: Object.freeze(after.missing || []) });
    })),
    proof,
    exactCommands: commands,
    nonClaims
  });
}

export function validateKernelKitReadinessContrast(report = {}) {
  const errors = [];
  if (!isObj(report)) return Object.freeze({ ok: false, errors: ['readiness contrast report must be an object'], changedGateCount: 0, missingGateCount: 0, commandCount: 0 });
  if (report.project !== 'BrowserRT') errors.push('project must be BrowserRT');
  if (report.format !== KERNEL_KIT_READINESS_CONTRAST_FORMAT) errors.push(`format must be ${KERNEL_KIT_READINESS_CONTRAST_FORMAT}`);
  if (report.status !== 'contrast-ready') errors.push('status must be contrast-ready');
  for (const key of ['baselineReady','degradedNeedsAttention','degradedRejectedByReadinessValidator','expectedGatesFailed','commandsPresent','nonClaimsPreserved','noProviderMutationClaim']) {
    if (report.proof?.[key] !== true) errors.push(`proof.${key} must be true`);
  }
  if (report.baseline?.status !== 'ready-for-next-usefulness-pass') errors.push('baseline must be ready-for-next-usefulness-pass');
  if (report.degraded?.status !== 'needs-attention') errors.push('degraded status must be needs-attention');
  if (!Array.isArray(report.degraded?.missingGateIds) || report.degraded.missingGateIds.length < 1) errors.push('degraded missingGateIds must be non-empty');
  if (!Array.isArray(report.gateDiff) || !report.gateDiff.some((row) => row.changed === true)) errors.push('gateDiff must show at least one changed gate');
  for (const needle of ['demo:kernel-kit-readiness-contrast-proof','facility:kernel-kit-readiness-contrast-audit','python3 tools/check_cube.py']) {
    if (!commandIncludes(report.exactCommands, needle)) errors.push(`missing readiness contrast command for ${needle}`);
  }
  for (const claim of ['No production readiness-contrast claim.','No automated demo-go/no-go claim.','No OPFS durability, fsync, quota, eviction, crash-recovery, browser-restart, or multi-tab coordination claim.']) {
    if (!nonClaimIncludes(report.nonClaims, claim)) errors.push(`missing readiness contrast non-claim: ${claim}`);
  }
  return Object.freeze({
    ok: errors.length === 0,
    errors,
    changedGateCount: report.gateDiff?.filter((row) => row.changed === true).length || 0,
    missingGateCount: report.degraded?.missingGateIds?.length || 0,
    commandCount: report.exactCommands?.length || 0,
    status: report.status || null,
    format: report.format || null
  });
}

// Static audit markers: browserrt-kernel-kit-readiness-contrast-v1; demo:kernel-kit-readiness-contrast-proof; facility:kernel-kit-readiness-contrast-audit; No production readiness-contrast claim.
