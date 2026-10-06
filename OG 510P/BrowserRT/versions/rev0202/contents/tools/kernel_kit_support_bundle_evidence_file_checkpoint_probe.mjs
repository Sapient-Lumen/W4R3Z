#!/usr/bin/env node
// Manifest slice: demo:kernel-kit-support-bundle-evidence-file-checkpoint-proof. Release-tier proof that evidence checkpoints can be built from actual compact JSON artifact files.
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve, sep } from 'node:path';
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
import { runProbe as runReadinessGateProbe } from './kernel_kit_readiness_gate_probe.mjs';
import { runProbe as runAdmissionCancellationProbe } from './kernel_kit_admission_cancellation_checkpoint_probe.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/validation/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-EVIDENCE-FILE-CHECKPOINT-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

const OUTPUTS = Object.freeze({
  support: `artifacts/validation/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-PROBE.json`,
  audit: `artifacts/audit/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-CONTRACT-AUDIT.json`,
  import: `artifacts/validation/${PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-IMPORT-PROBE.json`,
  admission: `artifacts/validation/${PREFIX}-KERNEL-KIT-ADMISSION-CANCELLATION-CHECKPOINT-PROBE.json`,
  readiness: `artifacts/validation/${PREFIX}-KERNEL-KIT-READINESS-GATE-PROBE.json`
});

function sha256(buffer) {
  return createHash('sha256').update(buffer).digest('hex');
}

async function writeJson(path, value) {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, JSON.stringify(value, null, 2) + '\n');
}

function safeArtifactPath(root, outputPath) {
  const rel = String(outputPath || '');
  if (!rel.startsWith('artifacts/validation/') && !rel.startsWith('artifacts/audit/')) {
    throw new Error(`refusing to read non-artifact evidence path: ${rel}`);
  }
  if (rel.includes('..') || rel.startsWith('/') || rel.includes('\\')) {
    throw new Error(`refusing unsafe artifact evidence path: ${rel}`);
  }
  const base = resolve(root);
  const abs = resolve(base, rel);
  if (abs !== base && !abs.startsWith(base + sep)) {
    throw new Error(`artifact evidence path escapes root: ${rel}`);
  }
  return abs;
}

async function readEvidenceArtifact(entry, { root = process.cwd(), deferredEntryIds = new Set(), skipEntryIds = new Set() } = {}) {
  const id = String(entry.id || 'unknown');
  if (deferredEntryIds.has(id)) {
    return Object.freeze({ id, outputPath: entry.outputPath || null, status: 'deferred', parsed: null, bytes: 0, sha256: null, reason: 'explicitly-deferred' });
  }
  if (skipEntryIds.has(id)) {
    return Object.freeze({ id, outputPath: entry.outputPath || null, status: 'missing', parsed: null, bytes: 0, sha256: null, reason: 'intentionally-skipped-negative-case' });
  }
  if (!entry.outputPath) {
    return Object.freeze({ id, outputPath: null, status: 'not-file-backed', parsed: null, bytes: 0, sha256: null, reason: 'ledger-entry-has-no-output-path' });
  }
  const abs = safeArtifactPath(root, entry.outputPath);
  try {
    const data = await readFile(abs);
    const parsed = JSON.parse(data.toString('utf8'));
    return Object.freeze({ id, outputPath: entry.outputPath, status: 'read', parsed, bytes: data.length, sha256: sha256(data), reason: null });
  } catch (error) {
    return Object.freeze({ id, outputPath: entry.outputPath, status: 'missing', parsed: null, bytes: 0, sha256: null, reason: error.message });
  }
}

function artifactMapFromRows(rows) {
  const map = {};
  for (const row of rows) {
    if (row.status !== 'read' || !row.parsed) continue;
    const canonical = row.id === 'support-bundle-import-artifact' && row.parsed.reports?.fromObject ? row.parsed.reports.fromObject : row.parsed;
    map[row.id] = canonical;
    if (row.outputPath) {
      map[row.outputPath] = canonical;
      map[row.outputPath.split('/').pop()] = canonical;
    }
    if (row.parsed.probe_id) map[row.parsed.probe_id] = canonical;
    if (row.parsed.audit_id) map[row.parsed.audit_id] = canonical;
  }
  return map;
}

async function materializeFileBackedEvidence() {
  const supportProof = await runSupportBundleProbe();
  await writeJson(OUTPUTS.support, supportProof);
  const supportAudit = await runSupportBundleAudit();
  await writeJson(OUTPUTS.audit, supportAudit);
  const importProof = await runSupportBundleImportProbe();
  await writeJson(OUTPUTS.import, importProof);
  const admissionProof = await runAdmissionCancellationProbe();
  await writeJson(OUTPUTS.admission, admissionProof);
  const readinessProof = await runReadinessGateProbe();
  await writeJson(OUTPUTS.readiness, readinessProof);
  return { supportProof, supportAudit, importProof, admissionProof, readinessProof };
}

async function buildFileBackedCheckpoint(supportBundle, { root = process.cwd(), deferredEntryIds = ['browser-kernel-kit-artifact', 'browser-storage-pressure-artifact', 'browser-session-coordination-artifact', 'browser-recovery-artifact', 'cube-sanity-command'], skipEntryIds = [] } = {}) {
  const ledger = supportBundle.evidenceLedger;
  const deferred = new Set(deferredEntryIds.map(String));
  const skipped = new Set(skipEntryIds.map(String));
  const rows = [];
  for (const entry of ledger.entries || []) {
    rows.push(await readEvidenceArtifact(entry, { root, deferredEntryIds: deferred, skipEntryIds: skipped }));
  }
  const artifacts = artifactMapFromRows(rows);
  const checkpoint = createKernelKitSupportBundleEvidenceCheckpoint(supportBundle, artifacts, {
    revision: REVISION,
    scope: 'artifact-file-backed',
    deferredEntryIds: [...deferred],
    generatedAt: 'deterministic-file-backed-evidence-checkpoint'
  });
  return { rows, artifacts, checkpoint, validation: validateKernelKitSupportBundleEvidenceCheckpoint(checkpoint) };
}

export async function runProbe() {
  const materialized = await materializeFileBackedEvidence();
  const supportBundle = materialized.supportProof.supportBundle;
  const ledgerValidation = validateKernelKitSupportBundleEvidenceLedger(supportBundle.evidenceLedger);
  assert.equal(ledgerValidation.ok, true, ledgerValidation.errors.join('; '));

  const fileBacked = await buildFileBackedCheckpoint(supportBundle);
  const validation = fileBacked.validation;
  const readIds = fileBacked.rows.filter((row) => row.status === 'read').map((row) => row.id);
  const readinessRow = fileBacked.checkpoint.rows.find((row) => row.id === 'readiness-gate-artifact');
  const missingImport = await buildFileBackedCheckpoint(supportBundle, { skipEntryIds: ['support-bundle-import-artifact'] });

  assert.equal(validation.ok, true, validation.errors.join('; '));
  assert.equal(fileBacked.checkpoint.status, 'evidence-checkpoint-ready');
  assert.ok(readIds.includes('support-bundle-proof-artifact'));
  assert.ok(readIds.includes('support-bundle-audit-artifact'));
  assert.ok(readIds.includes('support-bundle-import-artifact'));
  assert.ok(readIds.includes('admission-cancellation-artifact'));
  assert.ok(readIds.includes('readiness-gate-artifact'));
  assert.equal(readinessRow?.proofChecks?.some((check) => check.proofPath === 'readinessGate.inputProof.evidenceBound' && check.ok === true), true, 'readiness checkpoint must bind to actual readiness artifact shape');
  assert.ok(fileBacked.checkpoint.deferredEntryIds.includes('browser-kernel-kit-artifact'), 'browser-heavy artifact must be explicitly deferred in file-backed release scope');
  assert.ok(fileBacked.checkpoint.deferredEntryIds.includes('browser-storage-pressure-artifact'), 'storage pressure browser-heavy artifact must be explicitly deferred in file-backed release scope');
  assert.ok(fileBacked.checkpoint.deferredEntryIds.includes('browser-session-coordination-artifact'), 'session coordination browser-heavy artifact must be explicitly deferred in file-backed release scope');
  assert.ok(fileBacked.checkpoint.deferredEntryIds.includes('browser-recovery-artifact'), 'recovery browser-heavy artifact must be explicitly deferred in file-backed release scope');
  assert.ok(fileBacked.checkpoint.deferredEntryIds.includes('cube-sanity-command'), 'cube sanity command has no JSON artifact and must be explicitly deferred');
  assert.equal(missingImport.checkpoint.status, 'needs-attention');
  assert.ok(missingImport.checkpoint.missingEntryIds.includes('support-bundle-import-artifact'), 'missing import file must be reported');

  const fileRows = fileBacked.rows.map((row) => Object.freeze({
    id: row.id,
    outputPath: row.outputPath,
    status: row.status,
    bytes: row.bytes,
    sha256: row.sha256,
    reason: row.reason
  }));
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    probe_id: `${REVISION}-kernel-kit-support-bundle-evidence-file-checkpoint-probe`,
    status: 'passed',
    purpose: 'Read the compact JSON proof/audit artifact files named by the Kernel Kit evidence ledger and build a checkpoint from their parsed contents, without shelling out, launching Chromium, signing artifacts, or claiming authenticity.',
    materializedOutputs: OUTPUTS,
    fileRows,
    checkpoint: fileBacked.checkpoint,
    validation,
    negativeCases: {
      missingImportFile: {
        status: missingImport.checkpoint.status,
        missingEntryIds: missingImport.checkpoint.missingEntryIds,
        validation: missingImport.validation
      }
    },
    proof: {
      fileBackedCheckpointValid: validation.ok === true,
      ledgerValid: ledgerValidation.ok === true,
      artifactFilesRead: readIds.length >= 4,
      supportProofFileRead: readIds.includes('support-bundle-proof-artifact'),
      supportAuditFileRead: readIds.includes('support-bundle-audit-artifact'),
      importProofFileRead: readIds.includes('support-bundle-import-artifact'),
      admissionCancellationProofFileRead: readIds.includes('admission-cancellation-artifact'),
      readinessProofFileRead: readIds.includes('readiness-gate-artifact'),
      actualReadinessNestedPathChecked: readinessRow?.proofChecks?.some((check) => check.proofPath === 'readinessGate.inputProof.evidenceBound' && check.ok === true) === true,
      requiredProofPathsSatisfiedFromFiles: fileBacked.checkpoint.proof.requiredProofPathsSatisfied === true,
      admissionCancellationProofSatisfied: fileBacked.checkpoint.rows.some((row) => row.id === 'admission-cancellation-artifact' && row.status === 'satisfied'),
      browserHeavyExplicitlyDeferred: fileBacked.checkpoint.deferredEntryIds.includes('browser-kernel-kit-artifact'),
      storagePressureExplicitlyDeferred: fileBacked.checkpoint.deferredEntryIds.includes('browser-storage-pressure-artifact'),
      sessionCoordinationExplicitlyDeferred: fileBacked.checkpoint.deferredEntryIds.includes('browser-session-coordination-artifact'),
      recoveryExplicitlyDeferred: fileBacked.checkpoint.deferredEntryIds.includes('browser-recovery-artifact'),
      cubeSanityExplicitlyDeferred: fileBacked.checkpoint.deferredEntryIds.includes('cube-sanity-command'),
      missingImportFileRejected: missingImport.checkpoint.status === 'needs-attention' && missingImport.checkpoint.missingEntryIds.includes('support-bundle-import-artifact'),
      pathConfinementChecked: fileBacked.rows.every((row) => !row.outputPath || row.outputPath.startsWith('artifacts/validation/') || row.outputPath.startsWith('artifacts/audit/')),
      sha256RecordedForReadFiles: fileBacked.rows.filter((row) => row.status === 'read').every((row) => typeof row.sha256 === 'string' && row.sha256.length === 64),
      fileCheckpointDoesNotExecuteCommands: true,
      fileCheckpointDoesNotLaunchBrowser: true,
      noArtifactAuthenticityClaim: true
    },
    nonClaims: [
      'No artifact authenticity or signature claim.',
      'No artifact signing or tamper-proofing claim.',
      'No command execution claim.',
      'No automated replay execution claim.',
      'No browser launch claim.',
      'No production support/readiness claim.',
      'No durable artifact retention guarantee.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runProbe();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else console.log(JSON.stringify(report, null, 2));

// Static audit markers: demo:kernel-kit-support-bundle-evidence-file-checkpoint-proof; artifactFilesRead; actualReadinessNestedPathChecked; safeArtifactPath; readEvidenceArtifact; admission-cancellation-artifact; admissionCancellationProofFileRead; admissionCancellationProofSatisfied; browser-session-coordination-artifact; browser-recovery-artifact; No artifact authenticity or signature claim.; No command execution claim.
