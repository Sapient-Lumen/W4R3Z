#!/usr/bin/env node
import { access, mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:storage-lane-quarantine-status-transition-import-contract-audit';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-STORAGE-LANE-QUARANTINE-STATUS-TRANSITION-IMPORT-CONTRACT-AUDIT.json`;
const argValue = (flag, fallback = null) => { const i = process.argv.indexOf(flag); return i >= 0 ? process.argv[i + 1] : fallback; };
async function exists(path) { try { await access(path); return true; } catch { return false; } }
async function text(path) { return await readFile(path, 'utf8'); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(name, ok, detail = {}) { return { name, status: ok ? 'passed' : 'failed', ...detail }; }

const currentTask = 'browser:opfs-web-lock-quarantine-status-transition-import-proof';
const currentAudit = TASK_ID;
const releaseTask = 'scheduler:storage-lane-quarantine-status-transition-import-proof';
const requiredFiles = [
  'src/storage-lane-scheduler.mjs',
  'src/block-store-lane-adapter.mjs',
  'src/types.d.ts',
  'tools/storage_lane_quarantine_status_transition_import_probe.mjs',
  'tools/browser_opfs_web_lock_quarantine_status_transition_import_probe.mjs',
  'tools/storage_lane_quarantine_status_transition_import_contract_audit.mjs',
  'docs/40-validation/storage-lane-quarantine-status-transition-import-slice.md',
  'docs/40-validation/browser-opfs-web-lock-quarantine-status-transition-import-slice.md',
  'docs/40-validation/storage-lane-quarantine-status-transition-import-contract-audit-slice.md',
  'test/manifest.json',
  'test/impact-map.json',
  'test/surface-inventory.json',
  'README.md',
  'START_HERE.md',
  'AGENTS.md',
  'CONTEXT-PACK.md'
];

const started = performance.now();
const checks = [];
for (const file of requiredFiles) checks.push(check(`required file: ${file}`, await exists(file), { file }));
const scheduler = await text('src/storage-lane-scheduler.mjs');
checks.push(check('runtime status-transition replacement hook', missing(scheduler, ['statusTransitionReplacementCount', 'quarantineLedgerStatusTransitionReplacements', 'storage-lane:timed-out-quarantine-import-status-transition-replaced', 'timedOutOperationMapKey(normalized)']).length === 0, { missing: missing(scheduler, ['statusTransitionReplacementCount', 'quarantineLedgerStatusTransitionReplacements', 'storage-lane:timed-out-quarantine-import-status-transition-replaced', 'timedOutOperationMapKey(normalized)']) }));
checks.push(check('runtime removes by operationReplayKey rather than visible opId only', missing(scheduler, ['removeExistingTimedOutRow', 'operationKey', 'legacyOpId', 'this.#successfulTimedOutOps.delete(cleanupKey)', 'this.#failedTimedOutOps.delete(cleanupKey)']).length === 0, { missing: missing(scheduler, ['removeExistingTimedOutRow', 'operationKey', 'legacyOpId', 'this.#successfulTimedOutOps.delete(cleanupKey)', 'this.#failedTimedOutOps.delete(cleanupKey)']) }));
const releaseProbe = await text('tools/storage_lane_quarantine_status_transition_import_probe.mjs');
checks.push(check('release proof covers successful/failed/unsettled transitions', missing(releaseProbe, [releaseTask, 'importFailed.statusTransitionReplacementCount', 'quarantine.totalCount, 1', 'importUnsettled.statusTransitionReplacementCount', 'staleReplay.disposition']).length === 0, { missing: missing(releaseProbe, [releaseTask, 'importFailed.statusTransitionReplacementCount', 'quarantine.totalCount, 1', 'importUnsettled.statusTransitionReplacementCount', 'staleReplay.disposition']) }));
const browserProbe = await text('tools/browser_opfs_web_lock_quarantine_status_transition_import_probe.mjs');
checks.push(check('browser proof uses OPFS/Web Locks guarded store', missing(browserProbe, [currentTask, 'opfsWebLockGuardedBlockStore', 'statusTransitionReplacementCount', 'guard.put', 'queryLocks']).length === 0, { missing: missing(browserProbe, [currentTask, 'opfsWebLockGuardedBlockStore', 'statusTransitionReplacementCount', 'guard.put', 'queryLocks']) }));
const manifest = JSON.parse(await text('test/manifest.json'));
const ids = new Set((manifest.tasks || []).map((task) => task.id));
checks.push(check('manifest wires release/browser/audit tasks', [releaseTask, currentAudit, currentTask].every((id) => ids.has(id)), { missingTaskIds: [releaseTask, currentAudit, currentTask].filter((id) => !ids.has(id)) }));
const inventory = await text('test/surface-inventory.json');
checks.push(check('surface inventory names status-transition import surfaces', missing(inventory, ['surface:storage-lane-quarantine-status-transition-import', 'surface:browser-opfs-web-lock-quarantine-status-transition-import', 'surface:storage-lane-quarantine-status-transition-import-contract-audit']).length === 0, { missing: missing(inventory, ['surface:storage-lane-quarantine-status-transition-import', 'surface:browser-opfs-web-lock-quarantine-status-transition-import', 'surface:storage-lane-quarantine-status-transition-import-contract-audit']) }));
const firstRead = `${await text('README.md')}\n${await text('START_HERE.md')}\n${await text('AGENTS.md')}\n${await text('CONTEXT-PACK.md')}`;
checks.push(check('first-read docs carried anchor', missing(firstRead, [REVISION, 'Carry-forward linked seam for audits', 'browser-light']).length === 0, { missing: missing(firstRead, [REVISION, 'Carry-forward linked seam for audits', 'browser-light']) }));
const docs = `${await text('docs/40-validation/storage-lane-quarantine-status-transition-import-slice.md')}\n${await text('docs/40-validation/browser-opfs-web-lock-quarantine-status-transition-import-slice.md')}\n${await text('docs/40-validation/storage-lane-quarantine-status-transition-import-contract-audit-slice.md')}`;
checks.push(check('docs preserve narrow non-claims', missing(docs, ['operationReplayKey', 'status transition', 'not provider cancellation', 'not rollback', 'Managed Chromium', 'cross-browser']).length === 0, { missing: missing(docs, ['operationReplayKey', 'status transition', 'not provider cancellation', 'not rollback', 'Managed Chromium', 'cross-browser']) }));

const failed = checks.filter((row) => row.status !== 'passed');
const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: TASK_ID, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), checks, failed, nonClaims: ['Contract audit only; does not replace release/browser proofs.', 'No provider cancellation, rollback, no-mutation-on-timeout, durability, quota/eviction survival, cryptographic attestation, tamper-proof storage, or production readiness claim.'] };
const out = argValue('--json', DEFAULT_OUT);
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2));
if (failed.length) process.exitCode = 1;
