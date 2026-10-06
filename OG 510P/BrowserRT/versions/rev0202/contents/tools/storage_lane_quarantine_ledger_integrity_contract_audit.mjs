#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-quarantine-ledger-integrity-contract-audit';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-LEDGER-INTEGRITY-CONTRACT-AUDIT.json`;
const CURRENT_BROWSER = 'browser:opfs-web-lock-quarantine-ledger-integrity-proof';
const CURRENT_RELEASE = 'scheduler:storage-lane-quarantine-ledger-integrity-proof';
const CURRENT_OFFICE_BROWSER = 'browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof';
const CURRENT_OFFICE_AUDIT = 'facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit';
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
    releaseProbe: await text('tools/storage_lane_quarantine_ledger_integrity_probe.mjs'),
    browserProbe: await text('tools/browser_opfs_web_lock_quarantine_ledger_integrity_probe.mjs'),
    releaseDoc: await text('docs/40-validation/storage-lane-quarantine-ledger-integrity-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-ledger-integrity-slice.md'),
    auditDoc: await text('docs/40-validation/storage-lane-quarantine-ledger-integrity-contract-audit-slice.md'),
    manifest: await text('test/manifest.json'),
    impact: await text('test/impact-map.json'),
    surfaces: await text('test/surface-inventory.json'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile'),
    readme: await text('README.md'),
    start: await text('START_HERE.md'),
    agents: await text('AGENTS.md'),
    context: await text('CONTEXT-PACK.md')
  };
  const pkg = JSON.parse(files.packageJson); const manifest = JSON.parse(files.manifest); const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  check(checks, 'scheduler-import-fails-closed-atomic', missing(files.scheduler, ['#validateTimedOutQuarantineLedger','counts.total mismatch','duplicate opId','quarantineLedgerImportIntegrityRejected','rejected-ledger-integrity','storage-lane:timed-out-quarantine-import-rejected','Import is atomic']).length === 0);
  check(checks, 'release-proof-wired', missing(files.releaseProbe, [CURRENT_RELEASE,'missing-counts','counts.total mismatch','duplicate-opid','rejected-ledger-integrity','laneHealthy','not cryptographic']).length === 0);
  check(checks, 'browser-proof-wired', missing(files.browserProbe, [CURRENT_BROWSER,'Managed Chromium','badImportResults','counts.total mismatch','rejected-ledger-integrity','real OPFS/Web Lock']).length === 0);
  check(checks, 'docs-preserve-boundaries', missing(files.releaseDoc + files.browserDoc + files.auditDoc, ['fail closed','atomic','not cryptographic','not production','counts.total mismatch','duplicate opId','cross-browser']).length === 0);
  check(checks, 'manifest-current-tasks-present', [CURRENT_RELEASE, CURRENT_BROWSER, TASK_ID].every((id) => taskIds.has(id)), { missing: [CURRENT_RELEASE, CURRENT_BROWSER, TASK_ID].filter((id) => !taskIds.has(id)) });
  for (const [name, body] of Object.entries({ impact: files.impact, surfaces: files.surfaces, makefile: files.makefile, packageJson: files.packageJson })) check(checks, `${name}-references-integrity-slice`, body.includes('quarantine-ledger-integrity') && body.includes('storage-lane-quarantine-ledger-integrity-contract-audit'));
  check(checks, 'first-read-current-office-moved-forward', [files.readme, files.start, files.agents, files.context].every((body) => body.includes('OPFS Web Lock Quarantine Restore Backpressure Binding Proof') && body.includes(CURRENT_OFFICE_BROWSER) && body.includes(CURRENT_OFFICE_AUDIT)));
  check(checks, 'carried-forward-integrity-evidence-visible', [files.manifest, files.packageJson, files.makefile, files.surfaces].every((body) => body.includes(CURRENT_BROWSER) && body.includes(TASK_ID)));
  check(checks, 'package-current-office-moved-forward', pkg.revision === REVISION && pkg.version === VERSION && pkg.current_task === CURRENT_OFFICE_BROWSER && pkg.current_audit === CURRENT_OFFICE_AUDIT, { revision: pkg.revision, version: pkg.version, current_task: pkg.current_task, current_audit: pkg.current_audit });
  check(checks, 'types-current-revision', missing(files.types, [`REVISION: '${REVISION}'`, `VERSION: '${VERSION}'`, 'importTimedOutOperationQuarantine']).length === 0);
  const failed = checks.filter((row) => row.status !== 'passed'); assert.equal(failed.length, 0, failed.map((row) => `${row.name}: ${JSON.stringify(row)}`).join('\n'));
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-quarantine-ledger-integrity-contract-audit`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), checks, purpose: 'Audit that timeout quarantine ledger import integrity checks, fail-closed atomic import, release/browser proofs, docs, and carried-forward integrity evidence stay wired while the current office moves forward to rev0077 restore-backpressure.', nonClaims: ['Contract audit only; not browser execution, not cryptographic attestation, not cancellation, rollback, durability, quota, eviction, SLO, or production-readiness evidence.'] };
}
const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runAudit(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-quarantine-ledger-integrity-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed contract audit is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_ledger_integrity_contract_audit] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
// surface:storage-lane-quarantine-ledger-integrity surface:browser-opfs-web-lock-quarantine-ledger-integrity surface:storage-lane-quarantine-ledger-integrity-contract-audit
