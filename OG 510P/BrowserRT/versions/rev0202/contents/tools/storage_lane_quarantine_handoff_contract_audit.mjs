#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-quarantine-handoff-contract-audit';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-HANDOFF-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const started = performance.now();
  const files = {
    scheduler: await text('src/storage-lane-scheduler.mjs'),
    adapter: await text('src/block-store-lane-adapter.mjs'),
    types: await text('src/types.d.ts'),
    releaseProbe: await text('tools/storage_lane_quarantine_handoff_probe.mjs'),
    browserProbe: await text('tools/browser_opfs_web_lock_quarantine_handoff_probe.mjs'),
    releaseDoc: await text('docs/40-validation/storage-lane-quarantine-handoff-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-handoff-slice.md'),
    auditDoc: await text('docs/40-validation/storage-lane-quarantine-handoff-contract-audit-slice.md'),
    manifest: await text('test/manifest.json'),
    impact: await text('test/impact-map.json'),
    surfaces: await text('test/surface-inventory.json'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile'),
    readme: await text('README.md'),
    changelog: await text('CHANGELOG.md')
  };
  const pkg = JSON.parse(files.packageJson);
  const manifest = JSON.parse(files.manifest);
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const checks = [];
  checks.push(check('scheduler-runtime-hooks', missing(files.scheduler, ['exportTimedOutOperationQuarantine','importTimedOutOperationQuarantine','timed-out-operation-quarantine-imported','rejected-timed-out-operation-quarantine','storage-lane:timed-out-quarantine-import','storage-lane:provider-healthy-rejected']).length === 0));
  checks.push(check('adapter-runtime-hooks', missing(files.adapter, ['exportTimedOutOperationQuarantine','importTimedOutOperationQuarantine','timedOutOperationQuarantine','markHealthy(lane = this.lane']).length === 0));
  checks.push(check('types-current-hints', missing(files.types, ['exportTimedOutOperationQuarantine','importTimedOutOperationQuarantine','rejected-timed-out-operation-quarantine']).length === 0));
  checks.push(check('release-proof-wired', missing(files.releaseProbe, ['scheduler:storage-lane-quarantine-handoff-proof','timed-out-operation-quarantine-imported','direct markHealthy','late success and late failure']).length === 0));
  checks.push(check('browser-proof-wired', missing(files.browserProbe, ['browser:opfs-web-lock-quarantine-handoff-proof','Managed Chromium proof','real OPFS/Web Lock','imported quarantine']).length === 0));
  checks.push(check('docs-present-nonclaims', [files.releaseDoc, files.browserDoc, files.auditDoc].every((body) => missing(body.toLowerCase(), ['cross-browser','quota','eviction','crash']).length === 0)));
  checks.push(check('manifest-current-tasks-present', ['scheduler:storage-lane-quarantine-handoff-proof','browser:opfs-web-lock-quarantine-handoff-proof',TASK_ID].every((id) => taskIds.has(id))));
  for (const [name, body] of [['impact', files.impact], ['surfaces', files.surfaces], ['package', files.packageJson], ['makefile', files.makefile]]) {
    checks.push(check(`${name}-references-current-slice`, body.includes('quarantine-handoff')));
  }
  checks.push(check('package-revision-aligned', pkg.revision === REVISION && pkg.version === VERSION, { revision: pkg.revision, version: pkg.version, current_task: pkg.current_task, current_audit: pkg.current_audit }));
  checks.push(check('first-read-sidecar-visible', files.readme.includes('browser:opfs-web-lock-quarantine-handoff-proof') && files.changelog.startsWith(`## ${REVISION} —`)));
  const failed = checks.filter((row) => row.status !== 'passed');
  assert.equal(failed.length, 0, JSON.stringify(failed, null, 2));
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-quarantine-handoff-contract-audit`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), checks, purpose: 'Audit that timeout-quarantine export/import handoff, markHealthy gating, release/browser proofs, docs, manifest, impact map, surface inventory, and operator shortcuts stay wired without forcing this sidecar to be the current office.', nonClaims: ['Contract audit only; not browser execution, provider cancellation, rollback, no-mutation, exactly-once, durability, quota, eviction, crash, throughput, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runAudit(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-storage-lane-quarantine-handoff-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed contract audit is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[storage_lane_quarantine_handoff_contract_audit] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
// surface:storage-lane-quarantine-handoff surface:browser-opfs-web-lock-quarantine-handoff surface:storage-lane-quarantine-handoff-contract-audit
