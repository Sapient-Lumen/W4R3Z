#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-quarantine-receipt-restore-integrity-contract-audit';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-RECEIPT-RESTORE-INTEGRITY-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function requireNeedles(label, haystack, needles) { const missing = needles.filter((needle) => !haystack.includes(needle)); assert.deepEqual(missing, [], `${label} missing ${missing.join(', ')}`); return needles.length; }

export async function runAudit() {
  const started = performance.now();
  const files = {
    adapter: await text('src/block-store-lane-adapter.mjs'),
    types: await text('src/types.d.ts'),
    release: await text('tools/storage_lane_quarantine_receipt_restore_integrity_probe.mjs'),
    browser: await text('tools/browser_opfs_web_lock_quarantine_receipt_restore_integrity_probe.mjs'),
    manifest: await text('test/manifest.json'),
    impact: await text('test/impact-map.json'),
    inventory: await text('test/surface-inventory.json'),
    readme: await text('README.md'),
    start: await text('START_HERE.md'),
    agents: await text('AGENTS.md'),
    context: await text('CONTEXT-PACK.md')
  };
  const checks = [];
  checks.push({ label: 'runtime-block-integrity-hooks', count: requireNeedles('runtime-block-integrity-hooks', files.adapter, ['verifyBeforeRestore', 'allowUnsafeUnverifiedRestore', 'rejected-unverified-clearance-receipt-restore', 'rejected-unverified-quarantine-ledger-restore', 'rejected-clearance-receipt-block-integrity', 'rejected-quarantine-ledger-block-integrity', 'block-store-lane:quarantine-clearance-receipt-restore-unverified-rejected', 'block-store-lane:quarantine-clearance-receipt-restore-block-integrity-rejected', 'quarantineClearanceReceiptRestoreBlockIntegrityRejected']) });
  checks.push({ label: 'type-surface', count: requireNeedles('type-surface', files.types, ['verifyBeforeRestore?: boolean', 'allowUnsafeUnverifiedRestore?: boolean', 'verifyOptions?: Record<string, unknown>', 'rejected-unverified-clearance-receipt-restore', 'rejected-clearance-receipt-block-integrity']) });
  checks.push({ label: 'release-proof', count: requireNeedles('release-proof', files.release, ['scheduler:storage-lane-quarantine-receipt-restore-integrity-proof', 'rejected-unverified-clearance-receipt-restore', 'rejected-unverified-quarantine-ledger-restore', 'rejected-clearance-receipt-block-integrity', 'rejected-quarantine-ledger-block-integrity', 'must not call get() after failed verify']) });
  checks.push({ label: 'browser-proof', count: requireNeedles('browser-proof', files.browser, ['browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof', 'opfsWebLockGuardedBlockStore', 'storage:opfs-block-corrupt', 'rejected-unverified-clearance-receipt-restore', 'rejected-clearance-receipt-block-integrity']) });
  checks.push({ label: 'manifest', count: requireNeedles('manifest', files.manifest, ['scheduler:storage-lane-quarantine-receipt-restore-integrity-proof', 'browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof', TASK_ID]) });
  checks.push({ label: 'impact-map', count: requireNeedles('impact-map', files.impact, ['storage-lane-quarantine-receipt-restore-integrity', 'src/block-store-lane-adapter.mjs']) });
  checks.push({ label: 'surface-inventory', count: requireNeedles('surface-inventory', files.inventory, ['surface:storage-lane-quarantine-receipt-restore-integrity', 'surface:browser-opfs-web-lock-quarantine-receipt-restore-integrity', 'surface:storage-lane-quarantine-receipt-restore-integrity-contract-audit']) });
  checks.push({ label: 'first-read-carried-anchor', count: requireNeedles('first-read-carried-anchor', files.readme + files.start + files.agents + files.context, [REVISION, 'Carry-forward linked seam for audits']) });
  return Object.freeze({ project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), checks, purpose: 'Audit that rev0091 restore paths verify provider-backed block integrity before decoding/importing timeout-quarantine ledgers or registering clearance receipts.', nonClaims: ['Audit only; release-light and managed Chromium probes supply runtime evidence.', 'No cryptographic attestation, tamper-proof storage, provider cancellation, durability, or production-readiness claim.'] });
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
