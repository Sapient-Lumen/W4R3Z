#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-quarantine-ledger-contract-audit';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-LEDGER-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(checks, name, passed, detail = {}) { checks.push({ name, status: passed ? 'passed' : 'failed', ...detail }); }

export async function runAudit() {
  const started = performance.now(); const checks = [];
  const files = {
    scheduler: await text('src/storage-lane-scheduler.mjs'),
    adapter: await text('src/block-store-lane-adapter.mjs'),
    types: await text('src/types.d.ts'),
    releaseProbe: await text('tools/storage_lane_quarantine_ledger_roundtrip_probe.mjs'),
    browserProbe: await text('tools/browser_opfs_web_lock_quarantine_ledger_roundtrip_probe.mjs'),
    releaseDoc: await text('docs/40-validation/storage-lane-quarantine-ledger-roundtrip-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-ledger-roundtrip-slice.md'),
    auditDoc: await text('docs/40-validation/storage-lane-quarantine-ledger-contract-audit-slice.md'),
    manifest: await text('test/manifest.json'),
    impact: await text('test/impact-map.json'),
    surfaces: await text('test/surface-inventory.json'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile')
  };
  const pkg = JSON.parse(files.packageJson);
  const manifest = JSON.parse(files.manifest);
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  check(checks, 'scheduler-ledger-runtime-hooks', missing(files.scheduler, ['exportTimedOutOperationQuarantine','importTimedOutOperationQuarantine','brt.storageLane.timedOutOperationQuarantine.v1','storage-lane:timed-out-quarantine-export','storage-lane:timed-out-quarantine-import','timed-out-quarantine-clear-review-token-required','storage-lane:timed-out-quarantine-cleared']).length === 0);
  check(checks, 'adapter-ledger-runtime-hooks', missing(files.adapter, ['exportTimedOutOperationQuarantine','importTimedOutOperationQuarantine','clearTimedOutOperationQuarantine','timedOutOperationQuarantine']).length === 0);
  check(checks, 'types-ledger-surface', missing(files.types, [`REVISION: '${REVISION}'`, `VERSION: '${VERSION}'`, 'exportTimedOutOperationQuarantine','importTimedOutOperationQuarantine','clearTimedOutOperationQuarantine','timedOutOperationQuarantineCount']).length === 0);
  check(checks, 'release-proof-wired', missing(files.releaseProbe, ['scheduler:storage-lane-quarantine-ledger-roundtrip-proof','timed-out-quarantine-clear-review-token-required','storage-lane:timed-out-quarantine-import','quarantine ledger']).length === 0);
  check(checks, 'browser-proof-wired', missing(files.browserProbe, ['browser:opfs-web-lock-quarantine-ledger-roundtrip-proof','Managed Chromium proof','real OPFS/Web Lock','timed-out-quarantine-clear-review-token-required']).length === 0);
  check(checks, 'docs-preserve-nonclaims', missing(files.releaseDoc + files.browserDoc, ['cross-browser','quota','eviction','crash','not cancellation','not prove']).length === 0);
  check(checks, 'manifest-current-tasks-present', ['scheduler:storage-lane-quarantine-ledger-roundtrip-proof','browser:opfs-web-lock-quarantine-ledger-roundtrip-proof',TASK_ID].every((id) => taskIds.has(id)), { missing: ['scheduler:storage-lane-quarantine-ledger-roundtrip-proof','browser:opfs-web-lock-quarantine-ledger-roundtrip-proof',TASK_ID].filter((id) => !taskIds.has(id)) });
  for (const [name, body] of Object.entries({ impact: files.impact, surfaces: files.surfaces, packageJson: files.packageJson })) check(checks, `${name}-references-current-ledger-slice`, body.includes('quarantine-ledger-roundtrip') && body.includes('storage-lane-quarantine-ledger-contract-audit'));
  check(checks, 'makefile-current-office-need-not-route-carried-ledger-slice', files.makefile.includes('opfs-block-store-rollback-valid-block-preserve-current-proof'));
  check(checks, 'package-current-or-carried-ledger-office', pkg.revision === REVISION && pkg.version === VERSION && ((pkg.current_task === 'browser:opfs-web-lock-quarantine-ledger-roundtrip-proof' && pkg.current_audit === TASK_ID) || ((pkg.carried_forward_browser_proofs || []).includes('browser:opfs-web-lock-quarantine-ledger-roundtrip-proof') && (pkg.carried_forward_audits || []).includes(TASK_ID))), { revision: pkg.revision, version: pkg.version, current_task: pkg.current_task, current_audit: pkg.current_audit, carried_forward_browser_proofs: pkg.carried_forward_browser_proofs || [], carried_forward_audits: pkg.carried_forward_audits || [] });
  const failed = checks.filter((row) => row.status !== 'passed');
  assert.equal(failed.length, 0, failed.map((row) => `${row.name}: ${JSON.stringify(row)}`).join('\n'));
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-quarantine-ledger-contract-audit`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), checks, purpose: 'Audit that timeout quarantine ledger export/import, unified reviewed/scoped clear, proofs, docs, manifest, impact map, surface inventory, and package current office stay wired.', nonClaims: ['Contract audit only; not browser execution, not cross-browser behavior, not cancellation, durability, quota, eviction, SLO, or production-readiness evidence.'] };
}
const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runAudit(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-quarantine-ledger-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed contract audit is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_ledger_contract_audit] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
// surface:storage-lane-quarantine-ledger-roundtrip surface:browser-opfs-web-lock-quarantine-ledger-roundtrip surface:storage-lane-quarantine-ledger-contract-audit
