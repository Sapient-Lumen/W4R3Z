#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit';
const RELEASE = 'scheduler:storage-lane-quarantine-restore-expected-fingerprint-proof';
const BROWSER = 'browser:opfs-web-lock-quarantine-restore-expected-fingerprint-proof';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-RESTORE-EXPECTED-FINGERPRINT-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function requireNeedles(label, haystack, needles) { const missing = needles.filter((needle) => !haystack.includes(needle)); assert.deepEqual(missing, [], `${label} missing ${missing.join(', ')}`); return needles.length; }

export async function runAudit() {
  const started = performance.now();
  const files = {
    adapter: await text('src/block-store-lane-adapter.mjs'),
    types: await text('src/types.d.ts'),
    release: await text('tools/storage_lane_quarantine_restore_expected_fingerprint_probe.mjs'),
    browser: await text('tools/browser_opfs_web_lock_quarantine_restore_expected_fingerprint_probe.mjs'),
    harness: await text('tools/lib/quarantine_restore_expected_fingerprint_harness.mjs'),
    storageDoc: await text('docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-restore-expected-fingerprint-slice.md'),
    auditDoc: await text('docs/40-validation/storage-lane-quarantine-restore-expected-fingerprint-contract-audit-slice.md'),
    manifest: await text('test/manifest.json'),
    impact: await text('test/impact-map.json'),
    inventory: await text('test/surface-inventory.json'),
    package: await text('package.json'),
    makefile: await text('Makefile'),
    readme: await text('README.md'),
    start: await text('START_HERE.md'),
    agents: await text('AGENTS.md'),
    context: await text('CONTEXT-PACK.md'),
    changelog: await text('CHANGELOG.md')
  };
  const checks = [];
  checks.push({ label: 'runtime-expected-fingerprint-hooks', count: requireNeedles('runtime-expected-fingerprint-hooks', files.adapter, ['blankExpectedFingerprintOption', 'timed-out-quarantine-restore-expected-fingerprint-blank', 'timed-out-quarantine-clearance-receipt-restore-expected-fingerprint-blank', 'expectedQuarantineFingerprint', 'expectedReceiptFingerprint', 'expectedPreClearanceFingerprint', 'expectedPostClearanceFingerprint', 'rejected-quarantine-ledger-expected-fingerprint', 'rejected-clearance-receipt-expected-fingerprint', 'block-store-lane:quarantine-ledger-restore-expected-fingerprint-rejected', 'block-store-lane:quarantine-clearance-receipt-restore-expected-fingerprint-rejected']) });
  checks.push({ label: 'type-surface', count: requireNeedles('type-surface', files.types, ['expectedQuarantineFingerprint?: string', 'expectedReceiptFingerprint?: string', 'expectedPreClearanceFingerprint?: string', 'expectedPostClearanceFingerprint?: string', 'rejected-quarantine-ledger-expected-fingerprint', 'rejected-clearance-receipt-expected-fingerprint']) });
  checks.push({ label: 'release-proof', count: requireNeedles('release-proof', files.release, [RELEASE, 'blankLedgerRestore', 'blankReceiptRestore', 'assertExpectedFingerprintRestoreReport', 'wrongLedgerRestore', 'wrongReceiptRestore', 'wrongPreclearanceRestore', 'rejected-quarantine-ledger-expected-fingerprint', 'rejected-clearance-receipt-expected-fingerprint', 'staleReplay']) });
  checks.push({ label: 'browser-proof', count: requireNeedles('browser-proof', files.browser + files.harness, [BROWSER, 'blankLedgerRestore', 'blankReceiptRestore', 'assertExpectedFingerprintRestoreReport', 'opfsWebLockGuardedBlockStore', 'persistTimedOutOperationQuarantine', 'expectedQuarantineFingerprint', 'expectedReceiptFingerprint', 'rejected-quarantine-ledger-expected-fingerprint', 'rejected-clearance-receipt-expected-fingerprint', 'coord:web-lock-acquired']) });
  checks.push({ label: 'shared-harness', count: requireNeedles('shared-harness', files.harness, ['assertExpectedFingerprintRestoreReport', 'EXPECTED_FINGERPRINT_RESTORE_CLAIMS', 'blank expected quarantine/receipt fingerprint intent rejects', 'coord:web-lock-acquired']) });
  checks.push({ label: 'docs', count: requireNeedles('docs', files.storageDoc + files.browserDoc + files.auditDoc, ['expected fingerprint', 'blank', 'valid-but-wrong', 'before import', 'before registration', 'Managed Chromium', 'not cryptographic attestation']) });
  checks.push({ label: 'manifest', count: requireNeedles('manifest', files.manifest, [RELEASE, BROWSER, TASK_ID, 'expected-fingerprint']) });
  checks.push({ label: 'impact-map', count: requireNeedles('impact-map', files.impact, ['storage-lane-quarantine-restore-expected-fingerprint', 'src/block-store-lane-adapter.mjs']) });
  checks.push({ label: 'surface-inventory', count: requireNeedles('surface-inventory', files.inventory, ['surface:storage-lane-quarantine-restore-expected-fingerprint', 'surface:browser-opfs-web-lock-quarantine-restore-expected-fingerprint', 'surface:storage-lane-quarantine-restore-expected-fingerprint-contract-audit']) });
  checks.push({ label: 'manifest-command-wiring', count: requireNeedles('manifest-command-wiring', files.manifest, ['storage_lane_quarantine_restore_expected_fingerprint_probe.mjs', 'browser_opfs_web_lock_quarantine_restore_expected_fingerprint_probe.mjs', 'storage_lane_quarantine_restore_expected_fingerprint_contract_audit.mjs']) });
  checks.push({ label: 'first-read-currentness', count: requireNeedles('first-read-currentness', files.readme + files.start + files.agents + files.context, [REVISION, BROWSER, TASK_ID, 'expected fingerprint']) });
  checks.push({ label: 'changelog', count: requireNeedles('changelog', files.changelog, [`## ${REVISION}`, BROWSER, TASK_ID, 'blank expected-fingerprint']) });
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), checks, purpose: 'Audit that timeout-quarantine ledger and clearance receipt restore expected-fingerprint gates reject blank intent, stay wired through the shared proof harness, and remain covered by release-light and managed Chromium proof surfaces.', nonClaims: ['Audit only; runtime probes supply evidence.', 'Expected fingerprint pinning is not cryptographic attestation, tamper-proof storage, provider cancellation, durability, or production readiness.'] });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runAudit();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(error?.stack || error);
  process.exitCode = 1;
}
