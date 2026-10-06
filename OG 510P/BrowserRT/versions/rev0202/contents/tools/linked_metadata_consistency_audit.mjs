#!/usr/bin/env node
// Fail-closed linked metadata audit: central package/reentry files must agree on the linked cloudtainer revision.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-LINKED-METADATA-CONSISTENCY-AUDIT.json`;
const METADATA_FILES = Object.freeze(['package.json', 'CUBE-META.json', 'REVISION-RECEIPT.json', 'REENTRY-CONTRACT.json', 'SURFACE-STATUS.json', 'VALIDATION-INDEX.json']);
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const flag = (argv, name) => argv.includes(name);
const readJson = async (path) => JSON.parse(await readFile(path, 'utf8'));
const revPrefix = (rev) => `REV${String(rev).slice(3)}`;

function expectEq(checks, name, actual, expected, details = {}) {
  checks.push(Object.freeze({ name, status: actual === expected ? 'passed' : 'failed', actual, expected, ...details }));
}

function fieldCheck(checks, file, obj, field, expected, { required = false } = {}) {
  if (!(field in obj)) {
    checks.push(Object.freeze({ name: `${file}:${field}`, status: required ? 'failed' : 'skipped', actual: null, expected, reason: 'field-absent' }));
    return;
  }
  expectEq(checks, `${file}:${field}`, obj[field], expected);
}

export async function runAudit({ linkedRevision = null, expectedArchive = null, requirePackageCommand = false, jsonOut = DEFAULT_OUT } = {}) {
  if (!linkedRevision) {
    const current = await readJson('REVISION-RECEIPT.json');
    linkedRevision = current.linkedRevision || current.linked_revision || null;
  }
  if (!/^rev\d{4}$/.test(String(linkedRevision || ''))) throw new Error('linked revision must be supplied as rev#### or present in REVISION-RECEIPT.json linkedRevision');
  const receiptPath = `${revPrefix(linkedRevision)}-LINKED-REVISION-RECEIPT.json`;
  const receipt = await readJson(receiptPath);
  const checks = [];
  const codename = receipt.codename || null;
  const linkedStatus = codename ? `passed-linked-${codename}` : null;
  const archive = expectedArchive || receipt.archiveIntent || null;

  expectEq(checks, 'receipt:linkedRevision', receipt.linkedRevision, linkedRevision, { receiptPath });
  expectEq(checks, 'receipt:status', receipt.status, 'passed', { receiptPath });
  if (archive) expectEq(checks, 'receipt:archiveIntent', receipt.archiveIntent, archive, { receiptPath });

  for (const file of METADATA_FILES) {
    const obj = await readJson(file);
    fieldCheck(checks, file, obj, 'linkedRevision', linkedRevision, { required: true });
    fieldCheck(checks, file, obj, 'linked_revision', linkedRevision, { required: true });
    fieldCheck(checks, file, obj, 'linkedRevisionReceipt', receiptPath, { required: true });
    fieldCheck(checks, file, obj, 'latest_linked_revision_receipt', receiptPath, { required: true });
    if (receipt.linkedRevisionBase) {
      fieldCheck(checks, file, obj, 'linkedRevisionBase', receipt.linkedRevisionBase);
      fieldCheck(checks, file, obj, 'linked_revision_base', receipt.linkedRevisionBase);
    }
    if (codename) {
      fieldCheck(checks, file, obj, 'linkedRevisionCodename', codename, { required: true });
      fieldCheck(checks, file, obj, 'linked_revision_codename', codename, { required: true });
      fieldCheck(checks, file, obj, 'cloudtainerFocus', codename);
    }
    if (linkedStatus) fieldCheck(checks, file, obj, 'linked_revision_status', linkedStatus, { required: true });
    if (receipt.summary) {
      fieldCheck(checks, file, obj, 'linkedRevisionSummary', receipt.summary);
      fieldCheck(checks, file, obj, 'linked_revision_summary', receipt.summary, { required: true });
      fieldCheck(checks, file, obj, 'summary_highlight', receipt.summary);
      fieldCheck(checks, file, obj, 'package_summary', receipt.summary);
      fieldCheck(checks, file, obj, 'validation_summary', receipt.summary);
    }
    if (receipt.linkedWorkNote) fieldCheck(checks, file, obj, 'linked_work_note', receipt.linkedWorkNote);
    if (receipt.forwardMomentumNote) fieldCheck(checks, file, obj, 'linked_forward_momentum_note', receipt.forwardMomentumNote);
    if (archive) {
      fieldCheck(checks, file, obj, 'linked_archive_name', archive, { required: true });
      fieldCheck(checks, file, obj, 'linkedRevisionArchiveIntent', archive);
      fieldCheck(checks, file, obj, 'linked_revision_archive_intent', archive);
    }
    if (requirePackageCommand) {
      const commands = Array.isArray(obj.package_commands) ? obj.package_commands : [];
      const ok = commands.some((cmd) => String(cmd).includes(`--linked-revision ${linkedRevision}`) && (!codename || String(cmd).includes(`--linked-slug ${codename}`)));
      checks.push(Object.freeze({ name: `${file}:package-command-linked`, status: ok ? 'passed' : 'failed', expected: { linkedRevision, codename }, actual: commands }));
    }
  }

  const failed = checks.filter((row) => row.status === 'failed');
  assert.deepEqual(failed.map((row) => row.name), [], `linked metadata consistency failed: ${failed.map((row) => row.name).join(', ')}`);
  const report = Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    linkedRevision,
    linkedRevisionReceipt: receiptPath,
    codename,
    archive,
    schema: 1,
    status: 'passed',
    audit_id: `${REVISION}-linked-metadata-consistency-audit`,
    purpose: 'Fail-closed guard against stale linked_revision / linkedRevision split-brain across central package, cube, receipt, reentry, surface, and validation metadata; when no linked revision is supplied, the audit derives it from REVISION-RECEIPT.json so package scripts do not fossilize an older turn.',
    checks,
    nonClaims: Object.freeze(['Metadata consistency only; this does not promote the runtime office, publish a package, prove browser storage durability, or replace runtime/proof audits.'])
  });
  await mkdir(dirname(jsonOut), { recursive: true });
  await writeFile(jsonOut, JSON.stringify(report, null, 2) + '\n');
  return report;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const argv = process.argv.slice(2);
  const jsonOut = argValue(argv, '--json', DEFAULT_OUT);
  const linkedRevision = argValue(argv, '--linked-revision');
  const expectedArchive = argValue(argv, '--expected-archive');
  const requirePackageCommand = flag(argv, '--require-package-command');
  try {
    const report = await runAudit({ linkedRevision, expectedArchive, requirePackageCommand, jsonOut });
    console.log(jsonOut);
    if (report.status !== 'passed') process.exitCode = 1;
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', audit_id: `${REVISION}-linked-metadata-consistency-audit`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
    await mkdir(dirname(jsonOut), { recursive: true });
    await writeFile(jsonOut, JSON.stringify(report, null, 2) + '\n');
    console.error(jsonOut);
    console.error(`[linked_metadata_consistency_audit] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
