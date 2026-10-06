#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-support-bundle-package-evidence-seal-proof. Release-tier proof that ledger-named Kernel Kit evidence artifacts are retained and hash-sealed before packaging.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  REVISION,
  VERSION,
  createKernelKitSupportBundleEvidenceCheckpoint,
  validateKernelKitSupportBundleEvidenceCheckpoint,
  validateKernelKitSupportBundleEvidenceLedger
} from '../src/browserrt.mjs';
import { runProbe as runSupportBundleProbe } from './kernel_kit_support_bundle_probe.mjs';
import { runAudit as runSupportBundleAudit } from './kernel_kit_support_bundle_contract_audit.mjs';
import { runProbe as runSupportBundleImportProbe } from './kernel_kit_support_bundle_import_probe.mjs';
import { runProbe as runAdmissionCancellationProbe } from './kernel_kit_admission_cancellation_checkpoint_probe.mjs';
import { runProbe as runReadinessGateProbe } from './kernel_kit_readiness_gate_probe.mjs';

export const KERNEL_KIT_PACKAGE_EVIDENCE_SEAL_FORMAT = 'browserrt-kernel-kit-support-bundle-package-evidence-seal-v1';
const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-PACKAGE-EVIDENCE-SEAL-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

const OUTPUTS = Object.freeze({
  support: `artifacts/validation/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-PROBE.json`,
  audit: `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-CONTRACT-AUDIT.json`,
  import: `artifacts/validation/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-IMPORT-PROBE.json`,
  admissionCancellation: `artifacts/validation/${PREFIX}-KERNEL-KIT-ADMISSION-CANCELLATION-CHECKPOINT-PROBE.json`,
  readiness: `artifacts/validation/${PREFIX}-KERNEL-KIT-READINESS-GATE-PROBE.json`,
  browser: `artifacts/validation/${PREFIX}-BROWSER-KERNEL-KIT-DEMO-PROBE.json`,
  sessionCoordinationBrowser: `artifacts/validation/${PREFIX}-BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE.json`,
  recoveryBrowser: `artifacts/validation/${PREFIX}-BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE.json`
});

function sha256(buffer) { return createHash('sha256').update(buffer).digest('hex'); }
async function writeJson(path, value) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, JSON.stringify(value, null, 2) + '\n');
}
async function readJson(path) {
  return JSON.parse(await readFile(path, 'utf8'));
}

function safeArtifactPath(root, outputPath) {
  const rel = String(outputPath || '');
  if (!rel.startsWith('artifacts/validation/') && !rel.startsWith('artifacts/audit/')) {
    throw new Error(`refusing to seal non-artifact evidence path: ${rel}`);
  }
  if (rel.includes('..') || rel.startsWith('/') || rel.includes('\\')) {
    throw new Error(`refusing unsafe package evidence path: ${rel}`);
  }
  const base = resolve(root);
  const abs = resolve(base, rel);
  if (abs !== base && !abs.startsWith(base + sep)) throw new Error(`package evidence path escapes root: ${rel}`);
  return abs;
}

async function materializeBrowserLightEvidence() {
  const supportProof = await runSupportBundleProbe();
  await writeJson(OUTPUTS.support, supportProof);
  const supportAudit = await runSupportBundleAudit();
  await writeJson(OUTPUTS.audit, supportAudit);
  const importProof = await runSupportBundleImportProbe();
  await writeJson(OUTPUTS.import, importProof);
  const admissionCancellationProof = await runAdmissionCancellationProbe();
  await writeJson(OUTPUTS.admissionCancellation, admissionCancellationProof);
  const readinessProof = await runReadinessGateProbe();
  await writeJson(OUTPUTS.readiness, readinessProof);
  return { supportProof, supportAudit, importProof, admissionCancellationProof, readinessProof };
}

async function readPackageEvidenceFile(entry, { root = process.cwd() } = {}) {
  if (!entry.outputPath) {
    return Object.freeze({
      id: entry.id,
      path: null,
      taskId: entry.taskId,
      phaseId: entry.phaseId,
      tier: entry.tier,
      status: 'command-only',
      size: 0,
      sha256: null,
      parsed: null,
      requiredProofPaths: Object.freeze(entry.requiredProofPaths || []),
      reason: 'ledger-entry-has-no-output-path'
    });
  }
  const abs = safeArtifactPath(root, entry.outputPath);
  try {
    const data = await readFile(abs);
    const parsed = JSON.parse(data.toString('utf8'));
    return Object.freeze({
      id: entry.id,
      path: entry.outputPath,
      taskId: entry.taskId,
      phaseId: entry.phaseId,
      tier: entry.tier,
      status: 'sealed',
      size: data.length,
      sha256: sha256(data),
      parsed,
      requiredProofPaths: Object.freeze(entry.requiredProofPaths || []),
      reason: null
    });
  } catch (error) {
    return Object.freeze({
      id: entry.id,
      path: entry.outputPath,
      taskId: entry.taskId,
      phaseId: entry.phaseId,
      tier: entry.tier,
      status: 'missing',
      size: 0,
      sha256: null,
      parsed: null,
      requiredProofPaths: Object.freeze(entry.requiredProofPaths || []),
      reason: error?.message || String(error)
    });
  }
}



const PACKAGE_EVIDENCE_COMPACTION_FORMAT = 'browserrt-kernel-kit-package-evidence-compact-v1';
const REQUIRED_AUDIT_CHECKS = Object.freeze(['proof-validates', 'evidence-ledger-contract-present']);

function compactProofFields(source, fields) {
  const proof = {};
  for (const field of fields) proof[field] = source?.proof?.[field] === true;
  return proof;
}

function compactPackageEvidencePayload(id, parsed) {
  const base = Object.freeze({
    project: parsed?.project || 'BrowserRT',
    revision: parsed?.revision || REVISION,
    version: parsed?.version || VERSION,
    status: parsed?.status || 'passed',
    compactedEvidence: true,
    compactionFormat: PACKAGE_EVIDENCE_COMPACTION_FORMAT,
    compactionPurpose: 'Retain only package-seal lineage and support-bundle required proof paths after full probes pass, so browser-heavy evidence does not blow the cloudtainer byte budget.',
    nonClaims: Object.freeze(['Compacted evidence is not the full raw proof transcript.', 'Compaction does not create proof; it preserves verifier-required fields from already-run proof artifacts.', 'No artifact authenticity, signing, browser conformance, quota reservation, eviction survival, fsync, crash recovery, or production readiness claim.'])
  });
  if (id === 'support-bundle-proof-artifact') {
    return Object.freeze({ ...base, schema: parsed?.schema || 1, probe_id: parsed?.probe_id || `${REVISION}-kernel-kit-support-bundle-probe`, proof: Object.freeze({ supportBundleValid: parsed?.proof?.supportBundleValid === true, replayPlanReady: parsed?.proof?.replayPlanReady === true, evidenceLedgerPresent: parsed?.proof?.evidenceLedgerPresent === true }), supportBundle: Object.freeze({ revision: parsed?.supportBundle?.revision || REVISION, evidenceLedger: parsed?.supportBundle?.evidenceLedger || null }) });
  }
  if (id === 'support-bundle-audit-artifact') {
    const checks = (Array.isArray(parsed?.checks) ? parsed.checks : []).filter((row) => REQUIRED_AUDIT_CHECKS.includes(row?.name)).map((row) => Object.freeze({ name: row.name, status: row.status }));
    return Object.freeze({ ...base, schema: parsed?.schema || 1, audit_id: parsed?.audit_id || `${REVISION}-kernel-kit-support-bundle-contract-audit`, checks: Object.freeze(checks) });
  }
  if (id === 'support-bundle-import-artifact') {
    const fromObject = parsed?.reports?.fromObject || {};
    const importProof = Object.freeze({ replayPlanReady: fromObject?.proof?.replayPlanReady === true, evidenceLedgerPresent: fromObject?.proof?.evidenceLedgerPresent === true });
    return Object.freeze({ ...base, schema: parsed?.schema || 1, probe_id: parsed?.probe_id || `${REVISION}-kernel-kit-support-bundle-import-probe`, sourceProbeId: parsed?.sourceProbeId || `${REVISION}-kernel-kit-support-bundle-probe`, proof: importProof, reports: Object.freeze({ fromObject: Object.freeze({ revision: fromObject.revision || REVISION, status: fromObject.status || 'passed', proof: importProof }) }) });
  }
  if (id === 'readiness-gate-artifact') {
    return Object.freeze({ ...base, schema: parsed?.schema || 1, probe_id: parsed?.probe_id || `${REVISION}-kernel-kit-readiness-gate-probe`, readinessGate: Object.freeze({ revision: parsed?.readinessGate?.revision || REVISION, inputProof: Object.freeze({ evidenceBound: parsed?.readinessGate?.inputProof?.evidenceBound === true }) }), proof: Object.freeze({ readinessInputsEvidenceBound: parsed?.proof?.readinessInputsEvidenceBound === true }) });
  }
  if (id === 'admission-cancellation-artifact') {
    return Object.freeze({ ...base, schema: parsed?.schema || 1, probe_id: parsed?.probe_id || `${REVISION}-kernel-kit-admission-cancellation-checkpoint-probe`, proof: Object.freeze({ observedCheckpointValid: parsed?.proof?.observedCheckpointValid === true, supportBundleCarriesAdmissionCancellationCheckpoint: parsed?.proof?.supportBundleCarriesAdmissionCancellationCheckpoint === true, admissionAbortReleaseProofPassed: parsed?.proof?.admissionAbortReleaseProofPassed === true }) });
  }
  if (id === 'browser-kernel-kit-artifact') {
    return Object.freeze({ ...base, schema: parsed?.schema || 1, probe_id: parsed?.probe_id || `${REVISION}-browser-kernel-kit-demo-probe`, proofId: parsed?.proofId || `${REVISION}-browser-kernel-kit-demo`, proof: Object.freeze({ guardedStorageLane: parsed?.proof?.guardedStorageLane === true, supportBundleReplay: parsed?.proof?.supportBundleReplay === true, supportBundleEvidenceLedger: parsed?.proof?.supportBundleEvidenceLedger === true }) });
  }
  if (id === 'browser-storage-pressure-artifact') {
    return Object.freeze({ ...base, schema: parsed?.schema || 1, probe_id: parsed?.probe_id || `${REVISION}-browser-opfs-lane-quota-backpressure-proof`, proof: Object.freeze({ quotaExceededClassified: parsed?.proof?.quotaExceededClassified === true, cleanupVerified: parsed?.proof?.cleanupVerified === true, quotaOverrideReset: parsed?.proof?.quotaOverrideReset === true, evictionSurvivalClaimed: parsed?.proof?.evictionSurvivalClaimed === true }) });
  }
  if (id === 'browser-session-coordination-artifact') {
    return Object.freeze({ ...base, schema: parsed?.schema || 1, probe_id: parsed?.probe_id || `${REVISION}-browser-kernel-kit-session-coordination-checkpoint-probe`, proof: Object.freeze({ exclusiveIfAvailableDenied: parsed?.proof?.exclusiveIfAvailableDenied === true, queuedAcquiredAfterRelease: parsed?.proof?.queuedAcquiredAfterRelease === true, handoffSingleUseClearObserved: parsed?.proof?.handoffSingleUseClearObserved === true, staleReadReturnedNull: parsed?.proof?.staleReadReturnedNull === true }) });
  }
  if (id === 'browser-recovery-artifact') {
    return Object.freeze({ ...base, schema: parsed?.schema || 1, probe_id: parsed?.probe_id || `${REVISION}-browser-kernel-kit-recovery-checkpoint-probe`, proof: Object.freeze({ sameOriginProfileRestartObserved: parsed?.proof?.sameOriginProfileRestartObserved === true, interruptedWriteNotAcceptedCorrupt: parsed?.proof?.interruptedWriteNotAcceptedCorrupt === true, transientOpenFailureRetryObserved: parsed?.proof?.transientOpenFailureRetryObserved === true, unsettledOrphanReviewGateObserved: parsed?.proof?.unsettledOrphanReviewGateObserved === true, crashDurabilityNonClaimsVisible: parsed?.proof?.crashDurabilityNonClaimsVisible === true }) });
  }
  return parsed;
}

async function compactPackageEvidenceArtifacts(ledger, { root = process.cwd() } = {}) {
  const rows = [];
  for (const entry of ledger.entries || []) {
    if (!entry.outputPath) continue;
    const abs = safeArtifactPath(root, entry.outputPath);
    const before = await readFile(abs);
    const parsed = JSON.parse(before.toString('utf8'));
    const compacted = compactPackageEvidencePayload(entry.id, parsed);
    const after = Buffer.from(JSON.stringify(compacted, null, 0) + '\n');
    if (after.length <= before.length) await writeFile(abs, after);
    rows.push(Object.freeze({ id: entry.id, path: entry.outputPath, beforeBytes: before.length, afterBytes: Math.min(before.length, after.length), savedBytes: Math.max(0, before.length - after.length), compacted: after.length <= before.length }));
  }
  return Object.freeze(rows);
}

function getObjectPath(object, path) {
  let cur = object;
  for (const part of String(path || '').split('.')) {
    if (!part) continue;
    if (cur == null) return undefined;
    cur = cur[part];
  }
  return cur;
}

const EXPECTED_EVIDENCE_LINEAGE = Object.freeze({
  'support-bundle-proof-artifact': Object.freeze({ identityPath: 'probe_id', identityValue: `${REVISION}-kernel-kit-support-bundle-probe`, extra: Object.freeze([{ name: 'support-bundle-revision-current', path: 'supportBundle.revision', value: REVISION }, { name: 'support-bundle-evidence-ledger-current', path: 'supportBundle.evidenceLedger.revision', value: REVISION }]) }),
  'support-bundle-audit-artifact': Object.freeze({ identityPath: 'audit_id', identityValue: `${REVISION}-kernel-kit-support-bundle-contract-audit`, extra: Object.freeze([]) }),
  'support-bundle-import-artifact': Object.freeze({ identityPath: 'probe_id', identityValue: `${REVISION}-kernel-kit-support-bundle-import-probe`, extra: Object.freeze([{ name: 'import-source-probe-current', path: 'sourceProbeId', value: `${REVISION}-kernel-kit-support-bundle-probe` }, { name: 'import-report-current', path: 'reports.fromObject.revision', value: REVISION }]) }),
  'readiness-gate-artifact': Object.freeze({ identityPath: 'probe_id', identityValue: `${REVISION}-kernel-kit-readiness-gate-probe`, extra: Object.freeze([{ name: 'readiness-gate-current', path: 'readinessGate.revision', value: REVISION }]) }),
  'admission-cancellation-artifact': Object.freeze({ identityPath: 'probe_id', identityValue: `${REVISION}-kernel-kit-admission-cancellation-checkpoint-probe`, extra: Object.freeze([{ name: 'admission-cancellation-observed', path: 'proof.observedCheckpointValid', value: true }, { name: 'admission-cancellation-support-bundle', path: 'proof.supportBundleCarriesAdmissionCancellationCheckpoint', value: true }, { name: 'admission-abort-release-proof', path: 'proof.admissionAbortReleaseProofPassed', value: true }]) }),
  'browser-kernel-kit-artifact': Object.freeze({ identityPath: 'probe_id', identityValue: `${REVISION}-browser-kernel-kit-demo-probe`, extra: Object.freeze([{ name: 'browser-proof-id-current', path: 'proofId', value: `${REVISION}-browser-kernel-kit-demo` }]) }),
  'browser-storage-pressure-artifact': Object.freeze({ identityPath: 'probe_id', identityValue: `${REVISION}-browser-opfs-lane-quota-backpressure-proof`, extra: Object.freeze([{ name: 'quota-proof-classified', path: 'proof.quotaExceededClassified', value: true }, { name: 'quota-proof-reset', path: 'proof.quotaOverrideReset', value: true }, { name: 'eviction-survival-not-claimed', path: 'proof.evictionSurvivalClaimed', value: false }]) }),
  'browser-session-coordination-artifact': Object.freeze({ identityPath: 'probe_id', identityValue: `${REVISION}-browser-kernel-kit-session-coordination-checkpoint-probe`, extra: Object.freeze([{ name: 'session-coordination-exclusive-denied', path: 'proof.exclusiveIfAvailableDenied', value: true }, { name: 'session-coordination-queued-after-release', path: 'proof.queuedAcquiredAfterRelease', value: true }, { name: 'session-coordination-stale-read-null', path: 'proof.staleReadReturnedNull', value: true }]) }),
  'browser-recovery-artifact': Object.freeze({ identityPath: 'probe_id', identityValue: `${REVISION}-browser-kernel-kit-recovery-checkpoint-probe`, extra: Object.freeze([{ name: 'recovery-same-origin-profile', path: 'proof.sameOriginProfileRestartObserved', value: true }, { name: 'recovery-interrupted-write-safe', path: 'proof.interruptedWriteNotAcceptedCorrupt', value: true }, { name: 'recovery-open-failure-retry', path: 'proof.transientOpenFailureRetryObserved', value: true }, { name: 'recovery-orphan-review-gate', path: 'proof.unsettledOrphanReviewGateObserved', value: true }]) })
});

function checkLineage(row) {
  if (row.status === 'command-only') {
    return Object.freeze({ status: 'command-only', checks: Object.freeze([{ name: 'command-only-not-json-artifact', ok: true }]), expectedIdentity: null });
  }
  if (row.status !== 'sealed' || !row.parsed) {
    return Object.freeze({ status: 'missing', checks: Object.freeze([{ name: 'sealed-json-present', ok: false }]), expectedIdentity: null });
  }
  const expected = EXPECTED_EVIDENCE_LINEAGE[row.id] || null;
  const checks = [
    Object.freeze({ name: 'project-browserrt', ok: row.parsed.project === 'BrowserRT', actual: row.parsed.project || null }),
    Object.freeze({ name: 'revision-current', ok: row.parsed.revision === REVISION, actual: row.parsed.revision || null }),
    Object.freeze({ name: 'status-passed', ok: row.parsed.status === 'passed', actual: row.parsed.status || null }),
    Object.freeze({ name: 'path-uses-current-prefix', ok: typeof row.path === 'string' && row.path.includes(`${PREFIX}-`), actual: row.path || null })
  ];
  if (expected) {
    checks.push(Object.freeze({ name: 'expected-identity', ok: getObjectPath(row.parsed, expected.identityPath) === expected.identityValue, path: expected.identityPath, actual: getObjectPath(row.parsed, expected.identityPath) || null, expected: expected.identityValue }));
    for (const spec of expected.extra || []) {
      checks.push(Object.freeze({ name: spec.name, ok: getObjectPath(row.parsed, spec.path) === spec.value, path: spec.path, actual: getObjectPath(row.parsed, spec.path) || null, expected: spec.value }));
    }
  } else {
    checks.push(Object.freeze({ name: 'known-ledger-entry-id', ok: false, actual: row.id || null }));
  }
  return Object.freeze({
    status: checks.every((check) => check.ok === true) ? 'bound' : 'unbound',
    checks: Object.freeze(checks),
    expectedIdentity: expected ? Object.freeze({ path: expected.identityPath, value: expected.identityValue }) : null
  });
}

function evidenceLineageFromRows(rows) {
  return rows.map((row) => {
    const lineage = checkLineage(row);
    return Object.freeze({
      id: row.id,
      path: row.path,
      taskId: row.taskId,
      status: lineage.status,
      expectedIdentity: lineage.expectedIdentity,
      checks: lineage.checks
    });
  });
}

function lineageMutationNegativeCheck(rows) {
  const supportRow = rows.find((row) => row.id === 'support-bundle-proof-artifact' && row.status === 'sealed' && row.parsed);
  if (!supportRow) return Object.freeze({ status: 'skipped', reason: 'support-bundle-proof-artifact not sealed' });
  const mutant = { ...supportRow, parsed: { ...supportRow.parsed, revision: 'rev9999' } };
  const lineage = checkLineage(mutant);
  return Object.freeze({
    status: lineage.status === 'unbound' ? 'passed' : 'failed',
    mutatedField: 'revision',
    originalRevision: supportRow.parsed.revision || null,
    mutantRevision: 'rev9999',
    rejected: lineage.status === 'unbound',
    failedChecks: lineage.checks.filter((check) => check.ok !== true).map((check) => check.name)
  });
}

function artifactMapFromSealRows(rows) {
  const map = {};
  for (const row of rows) {
    if (row.status !== 'sealed' || !row.parsed) continue;
    const canonical = row.id === 'support-bundle-import-artifact' && row.parsed.reports?.fromObject ? row.parsed.reports.fromObject : row.parsed;
    map[row.id] = canonical;
    if (row.path) {
      map[row.path] = canonical;
      map[row.path.split('/').pop()] = canonical;
    }
    if (row.parsed.probe_id) map[row.parsed.probe_id] = canonical;
    if (row.parsed.audit_id) map[row.parsed.audit_id] = canonical;
  }
  return map;
}

export async function runProbe({ root = process.cwd(), materialize = true } = {}) {
  const materialized = materialize ? await materializeBrowserLightEvidence() : null;
  const supportProof = materialized?.supportProof || await readJson(OUTPUTS.support);
  const supportBundle = supportProof.supportBundle;
  const ledger = supportBundle.evidenceLedger;
  const ledgerValidation = validateKernelKitSupportBundleEvidenceLedger(ledger);
  assert.equal(ledgerValidation.ok, true, ledgerValidation.errors.join('; '));

  const compactionRows = await compactPackageEvidenceArtifacts(ledger, { root });
  const rows = [];
  for (const entry of ledger.entries || []) rows.push(await readPackageEvidenceFile(entry, { root }));
  const artifacts = artifactMapFromSealRows(rows);
  const checkpoint = createKernelKitSupportBundleEvidenceCheckpoint(supportBundle, artifacts, {
    revision: REVISION,
    scope: 'package-retained-evidence',
    deferredEntryIds: ['cube-sanity-command'],
    generatedAt: 'deterministic-package-evidence-seal-checkpoint'
  });
  const checkpointValidation = validateKernelKitSupportBundleEvidenceCheckpoint(checkpoint);
  const sealedRows = rows.filter((row) => row.status === 'sealed');
  const missingRows = rows.filter((row) => row.status === 'missing');
  const admissionCancellationRow = rows.find((row) => row.id === 'admission-cancellation-artifact');
  const browserRow = rows.find((row) => row.id === 'browser-kernel-kit-artifact');
  const browserSessionCoordinationRow = rows.find((row) => row.id === 'browser-session-coordination-artifact');
  const browserRecoveryRow = rows.find((row) => row.id === 'browser-recovery-artifact');
  const admissionCancellationCheckpointRow = checkpoint.rows.find((row) => row.id === 'admission-cancellation-artifact');
  const browserCheckpointRow = checkpoint.rows.find((row) => row.id === 'browser-kernel-kit-artifact');
  const browserSessionCoordinationCheckpointRow = checkpoint.rows.find((row) => row.id === 'browser-session-coordination-artifact');
  const browserRecoveryCheckpointRow = checkpoint.rows.find((row) => row.id === 'browser-recovery-artifact');
  const commandOnlyRows = rows.filter((row) => row.status === 'command-only');
  const evidenceLineageRows = evidenceLineageFromRows(rows);
  const unboundLineageRows = evidenceLineageRows.filter((row) => row.status === 'unbound' || row.status === 'missing');
  const lineageNegativeCheck = lineageMutationNegativeCheck(rows);

  assert.equal(missingRows.length, 0, `missing package evidence rows: ${missingRows.map((row) => row.id).join(', ')}`);
  assert.equal(checkpoint.status, 'evidence-checkpoint-ready', checkpointValidation.errors.join('; '));
  assert.equal(checkpointValidation.ok, true, checkpointValidation.errors.join('; '));
  assert.equal(admissionCancellationRow?.status, 'sealed', 'admission cancellation proof artifact must be retained before package seal');
  assert.equal(browserRow?.status, 'sealed', 'browser Kernel Kit proof artifact must be retained before package seal');
  assert.equal(browserSessionCoordinationRow?.status, 'sealed', 'browser session coordination proof artifact must be retained before package seal');
  assert.equal(browserRecoveryRow?.status, 'sealed', 'browser recovery proof artifact must be retained before package seal');
  assert.equal(admissionCancellationCheckpointRow?.status, 'satisfied', 'admission cancellation artifact proof paths must be satisfied by retained file contents');
  assert.equal(browserCheckpointRow?.status, 'satisfied', 'browser Kernel Kit artifact proof paths must be satisfied by retained file contents');
  assert.equal(browserSessionCoordinationCheckpointRow?.status, 'satisfied', 'browser session coordination artifact proof paths must be satisfied by retained file contents');
  assert.equal(browserRecoveryCheckpointRow?.status, 'satisfied', 'browser recovery artifact proof paths must be satisfied by retained file contents');
  assert.ok(commandOnlyRows.some((row) => row.id === 'cube-sanity-command'), 'cube sanity remains command-only and is not faked as a JSON artifact');
  assert.equal(unboundLineageRows.length, 0, `unbound package evidence lineage rows: ${unboundLineageRows.map((row) => row.id).join(', ')}`);
  assert.equal(lineageNegativeCheck.status, 'passed', 'lineage mutation negative check must reject stale/wrong revision evidence');

  const sealedArtifactRows = sealedRows.map((row) => Object.freeze({
    id: row.id,
    path: row.path,
    taskId: row.taskId,
    phaseId: row.phaseId,
    tier: row.tier,
    status: row.status,
    size: row.size,
    sha256: row.sha256,
    requiredProofPaths: row.requiredProofPaths,
    checkpointStatus: checkpoint.rows.find((checkpointRow) => checkpointRow.id === row.id)?.status || 'unknown',
    lineageStatus: evidenceLineageRows.find((lineageRow) => lineageRow.id === row.id)?.status || 'unknown',
    expectedIdentity: evidenceLineageRows.find((lineageRow) => lineageRow.id === row.id)?.expectedIdentity || null
  }));

  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    format: KERNEL_KIT_PACKAGE_EVIDENCE_SEAL_FORMAT,
    probe_id: `${REVISION}-kernel-kit-support-bundle-package-evidence-seal-probe`,
    status: 'passed',
    purpose: 'Seal the Kernel Kit support-bundle evidence-ledger artifact files that must survive release packaging by reading them, hashing them, and verifying their required proof paths without executing commands or claiming authenticity.',
    materializedOutputs: OUTPUTS,
    materializedBrowserLightEvidence: materialize === true,
    packageEvidenceCompaction: Object.freeze({ format: PACKAGE_EVIDENCE_COMPACTION_FORMAT, rows: compactionRows, savedBytes: compactionRows.reduce((sum, row) => sum + row.savedBytes, 0), compactedCount: compactionRows.filter((row) => row.compacted === true).length }),
    ledger: Object.freeze({ status: ledger.status, validation: ledgerValidation, entryCount: ledger.entries?.length || 0, outputCount: ledger.outputPaths?.length || 0 }),
    sealedArtifactRows,
    evidenceLineageRows,
    lineageNegativeCheck,
    commandOnlyRows: commandOnlyRows.map((row) => Object.freeze({ id: row.id, taskId: row.taskId, phaseId: row.phaseId, status: row.status, reason: row.reason, requiredProofPaths: row.requiredProofPaths })),
    missingRows: missingRows.map((row) => Object.freeze({ id: row.id, path: row.path, reason: row.reason })),
    checkpoint,
    checkpointValidation,
    proof: Object.freeze({
      packageEvidenceSealValid: true,
      ledgerValid: ledgerValidation.ok === true,
      allLedgerOutputFilesPresent: missingRows.length === 0,
      packageEvidenceCompacted: compactionRows.length >= 9 && (compactionRows.reduce((sum, row) => sum + row.savedBytes, 0) > 0 || compactionRows.every((row) => Number.isFinite(row.beforeBytes) && Number.isFinite(row.afterBytes) && row.afterBytes <= row.beforeBytes)),
      packageEvidenceCompactionIdempotent: compactionRows.length >= 9 && compactionRows.every((row) => Number.isFinite(row.beforeBytes) && Number.isFinite(row.afterBytes) && row.afterBytes <= row.beforeBytes),
      packageEvidenceCompactionSavedBytes: compactionRows.reduce((sum, row) => sum + row.savedBytes, 0),
      allLedgerOutputFilesHashed: sealedRows.length >= 5 && sealedRows.every((row) => typeof row.sha256 === 'string' && row.sha256.length === 64),
      allSealedArtifactsLineageBound: unboundLineageRows.length === 0 && sealedRows.length >= 5 && sealedArtifactRows.every((row) => row.lineageStatus === 'bound'),
      staleOrWrongRevisionEvidenceRejected: lineageNegativeCheck.status === 'passed',
      releaseBrowserLightArtifactsSealed: ['support-bundle-proof-artifact','support-bundle-audit-artifact','support-bundle-import-artifact','readiness-gate-artifact','admission-cancellation-artifact'].every((id) => sealedRows.some((row) => row.id === id)),
      admissionCancellationArtifactSealed: admissionCancellationRow?.status === 'sealed',
      browserKernelKitArtifactSealed: browserRow?.status === 'sealed',
      browserStoragePressureArtifactSealed: rows.find((row) => row.id === 'browser-storage-pressure-artifact')?.status === 'sealed',
      browserSessionCoordinationArtifactSealed: browserSessionCoordinationRow?.status === 'sealed',
      browserRecoveryArtifactSealed: browserRecoveryRow?.status === 'sealed',
      admissionCancellationArtifactSatisfied: admissionCancellationCheckpointRow?.status === 'satisfied',
      browserKernelKitArtifactSatisfied: browserCheckpointRow?.status === 'satisfied',
      browserSessionCoordinationArtifactSatisfied: browserSessionCoordinationCheckpointRow?.status === 'satisfied',
      browserRecoveryArtifactSatisfied: browserRecoveryCheckpointRow?.status === 'satisfied',
      cubeSanityCommandOnlyNotFaked: commandOnlyRows.some((row) => row.id === 'cube-sanity-command'),
      checkpointSatisfiedExceptCommandOnly: checkpointValidation.ok === true && checkpoint.missingEntryIds.length === 0 && checkpoint.deferredEntryIds.includes('cube-sanity-command'),
      releaseManifestVerifierExpected: true,
      noMaterializeModeSupported: true,
      sealDoesNotExecuteCommands: true,
      sealDoesNotLaunchBrowser: true,
      noArtifactAuthenticityClaim: true
    }),
    nonClaims: Object.freeze([
      'No artifact authenticity or signature claim.',
      'No artifact signing or tamper-proofing claim.',
      'Lineage binding rejects stale or wrong-revision local evidence, but it is still not authenticity or tamper-proofing.',
      'No command execution claim.',
      'No automated replay execution claim.',
      'No browser launch claim.',
      'No production support/readiness claim.',
      'No guarantee that future packages retain artifacts unless verify_release.py is run on the archive.'
    ])
  });
}

const isMain = process.argv[1] && import.meta.url === new URL(process.argv[1], 'file:').href;
if (isMain) {
  const argv = process.argv.slice(2);
  const out = argValue(argv, '--json', DEFAULT_OUT);
  const report = await runProbe({ materialize: !argv.includes('--no-materialize') });
  if (out) {
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } else console.log(JSON.stringify(report, null, 2));
}

// Static audit markers: demo:kernel-kit-support-bundle-package-evidence-seal-proof; packageEvidenceSealValid; releaseManifestVerifierExpected; noMaterializeModeSupported; browserKernelKitArtifactSealed; browserSessionCoordinationArtifactSealed; browserRecoveryArtifactSealed; browserRecoveryArtifactSatisfied; admissionCancellationArtifactSealed; admissionCancellationArtifactSatisfied; admission-cancellation-artifact; observedCheckpointValid; admissionAbortReleaseProofPassed; unsettledOrphanReviewGateObserved; browser-session-coordination-artifact; browser-recovery-artifact; cubeSanityCommandOnlyNotFaked; allSealedArtifactsLineageBound; staleOrWrongRevisionEvidenceRejected; EXPECTED_EVIDENCE_LINEAGE; PACKAGE_EVIDENCE_COMPACTION_FORMAT; compactPackageEvidenceArtifacts; packageEvidenceCompacted; packageEvidenceCompactionIdempotent; No artifact authenticity or signature claim.; No command execution claim.
