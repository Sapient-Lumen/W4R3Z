#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-quarantine-ledger-persistence-contract-audit';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-LEDGER-PERSISTENCE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(checks, name, passed, detail = {}) { checks.push({ name, status: passed ? 'passed' : 'failed', ...detail }); }

export async function runAudit() {
  const started = performance.now(); const checks = [];
  const files = {
    adapter: await text('src/block-store-lane-adapter.mjs'), scheduler: await text('src/storage-lane-scheduler.mjs'), types: await text('src/types.d.ts'),
    releaseProbe: await text('tools/storage_lane_quarantine_ledger_persistence_probe.mjs'), browserProbe: await text('tools/browser_opfs_web_lock_quarantine_ledger_persistence_probe.mjs'),
    releaseDoc: await text('docs/40-validation/storage-lane-quarantine-ledger-persistence-slice.md'), browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-ledger-persistence-slice.md'), auditDoc: await text('docs/40-validation/storage-lane-quarantine-ledger-persistence-contract-audit-slice.md'),
    manifest: await text('test/manifest.json'), impact: await text('test/impact-map.json'), surfaces: await text('test/surface-inventory.json'), packageJson: await text('package.json'), makefile: await text('Makefile'), readme: await text('README.md'), startHere: await text('START_HERE.md'), agents: await text('AGENTS.md'), context: await text('CONTEXT-PACK.md')
  };
  const pkg = JSON.parse(files.packageJson); const manifest = JSON.parse(files.manifest); const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  check(checks, 'adapter-persistence-runtime-hooks', missing(files.adapter, ['persistTimedOutOperationQuarantine','restoreTimedOutOperationQuarantineFromBlockStore','block-store-lane:quarantine-ledger-persisted','block-store-lane:quarantine-ledger-restored','quarantineLedgerPersists','quarantineLedgerRestores']).length === 0);
  check(checks, 'scheduler-quarantine-ledger-still-present', missing(files.scheduler, ['brt.storageLane.timedOutOperationQuarantine.v1','importTimedOutOperationQuarantine','storage-lane:timed-out-quarantine-import','timed-out-quarantine-clear-review-token-required']).length === 0);
  check(checks, 'types-persistence-surface', missing(files.types, [`REVISION: '${REVISION}'`, `VERSION: '${VERSION}'`, 'persistTimedOutOperationQuarantine','restoreTimedOutOperationQuarantineFromBlockStore']).length === 0);
  check(checks, 'release-proof-wired', missing(files.releaseProbe, ['scheduler:storage-lane-quarantine-ledger-persistence-proof','persistTimedOutOperationQuarantine','restoreTimedOutOperationQuarantineFromBlockStore','block-store-lane:quarantine-ledger-persisted','malformedRestore','rejected-ledger-integrity']).length === 0);
  check(checks, 'browser-proof-wired', missing(files.browserProbe, ['browser:opfs-web-lock-quarantine-ledger-persistence-proof','runManagedBrowserPage','keepProfile: true','restoreTimedOutOperationQuarantineFromBlockStore','same profile']).length === 0);
  check(checks, 'docs-preserve-boundaries', missing(files.releaseDoc + files.browserDoc + files.auditDoc, ['restart','cross-browser','not fsync','not cancellation','not production','rejected-ledger-integrity']).length === 0);
  const requiredTasks = ['scheduler:storage-lane-quarantine-ledger-persistence-proof','browser:opfs-web-lock-quarantine-ledger-persistence-proof',TASK_ID];
  check(checks, 'manifest-current-tasks-present', requiredTasks.every((id) => taskIds.has(id)), { missing: requiredTasks.filter((id) => !taskIds.has(id)) });
  for (const [name, body] of Object.entries({ impact: files.impact, surfaces: files.surfaces, makefile: files.makefile, packageJson: files.packageJson, readme: files.readme, startHere: files.startHere, agents: files.agents, context: files.context })) check(checks, `${name}-references-persistence-slice`, body.includes('quarantine-ledger-persistence') && body.includes(TASK_ID));
  check(checks, 'package-current-office', pkg.revision === REVISION && pkg.version === VERSION && pkg.current_task === 'browser:opfs-web-lock-quarantine-ledger-persistence-proof' && pkg.current_audit === TASK_ID && pkg.package_slug === 'opfs-web-lock-quarantine-ledger-persistence-proof', { revision: pkg.revision, version: pkg.version, current_task: pkg.current_task, current_audit: pkg.current_audit, package_slug: pkg.package_slug });
  const failed = checks.filter((row) => row.status !== 'passed'); assert.equal(failed.length, 0, failed.map((row) => `${row.name}: ${JSON.stringify(row)}`).join('\n'));
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-quarantine-ledger-persistence-contract-audit`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), checks, purpose: 'Audit that timed-out operation quarantine ledger block-store persistence, malformed persisted-ledger restore rejection, browser restart restoration, release/browser proofs, docs, manifest, impact map, surface inventory, Makefile, package metadata, and current office stay wired.', nonClaims: ['Contract audit only; not browser execution, not cross-browser behavior, not fsync durability, not cancellation, not quota/eviction evidence, and not production readiness.'] };
}
const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runAudit(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-quarantine-ledger-persistence-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed persistence contract audit is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_ledger_persistence_contract_audit] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
// surface:storage-lane-quarantine-ledger-persistence surface:browser-opfs-web-lock-quarantine-ledger-persistence surface:storage-lane-quarantine-ledger-persistence-contract-audit
