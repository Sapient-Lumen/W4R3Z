#!/usr/bin/env node
// rev0062 lineage note: parallel rev0061 branches included corrupt-block repair, Web Lock timeout, tab-termination, tab-timeout, and guarded corrupt repair timeout proof surfaces.
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-REVISION-LINEAGE-MERGE-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(checks, id, ok, detail = {}) { checks.push({ id, status: ok ? 'passed' : 'failed', ...detail }); }

const CURRENT_TASK = 'browser:opfs-web-lock-late-failure-quarantine-proof';
const CARRIED_LATE_SETTLEMENT_TASK = 'browser:opfs-web-lock-late-settlement-recovery-gate-proof';
const CODENAME = 'OPFS Web Lock Late Failure Quarantine Proof';
const SLUG = 'opfs-web-lock-late-failure-quarantine-proof';
const CARRIED_OPERATION_TIMEOUT_TASK = 'browser:opfs-web-lock-operation-timeout-boundary-proof';
const CARRIED_SHUTDOWN_TASK = 'browser:opfs-web-lock-service-worker-shutdown-boundary-proof';
const CARRIED_RESTART_UPDATE_TASK = 'browser:opfs-web-lock-service-worker-restart-update-proof';
const PREVIOUS_REV = `rev${String(Number(REVISION.slice(3)) - 1).padStart(4, '0')}`;

export async function runAudit() {
  const started = Date.now();
  const checks = [];
  const packageJson = await json('package.json');
  const centralPaths = ['CUBE-META.json', 'REVISION-RECEIPT.json', 'REENTRY-CONTRACT.json', 'SURFACE-STATUS.json', 'VALIDATION-INDEX.json'];
  const central = Object.fromEntries(await Promise.all(centralPaths.map(async (path) => [path, await json(path)])));
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const opfs = await text('src/opfs-block-store.mjs');
  const coordinator = await text('src/web-lock-coordinator.mjs');
  const scheduler = await text('src/storage-lane-scheduler.mjs');
  const fixture = await text('tools/browser_cdp_fixture.mjs');
  const tabTimeoutProof = await text('tools/browser_opfs_web_lock_tab_timeout_probe.mjs');
  const guardedProof = await text('tools/browser_opfs_guarded_corrupt_repair_timeout_probe.mjs');
  const storageHealthProof = await text('tools/storage_lane_web_lock_timeout_health_probe.mjs');
  const changelog = await text('CHANGELOG.md');
  const lineageNote = await text('docs/00-meta/rev0062-lineage-merge-note.md');

  check(checks, 'runtime-revision-is-current', /^rev\d{4}$/.test(REVISION) && /^\d+\.\d+\.\d+$/.test(VERSION), { observed: { REVISION, VERSION } });
  check(checks, 'package-revision-version-aligned', packageJson.revision === REVISION && packageJson.version === VERSION && packageJson.codename === CODENAME && packageJson.package_slug === SLUG && packageJson.current_task === CURRENT_TASK, { observed: { revision: packageJson.revision, version: packageJson.version, codename: packageJson.codename, package_slug: packageJson.package_slug, current_task: packageJson.current_task } });
  for (const [path, obj] of Object.entries(central)) {
    check(checks, `${path}:revision-version-aligned`, obj.revision === REVISION && obj.version === VERSION && obj.previous_revision === PREVIOUS_REV, { observed: { revision: obj.revision, version: obj.version, previous_revision: obj.previous_revision } });
    check(checks, `${path}:current-slice-late-failure-quarantine`, obj.codename === CODENAME && obj.package_slug === SLUG && obj.current_task === CURRENT_TASK && obj.current_slice === CURRENT_TASK, { observed: { codename: obj.codename, package_slug: obj.package_slug, current_task: obj.current_task, current_slice: obj.current_slice } });
  }
  check(checks, 'manifest-impact-inventory-revision-aligned', manifest.revision === REVISION && impact.revision === REVISION && inventory.revision === REVISION, { observed: { manifest: manifest.revision, impact: impact.revision, inventory: inventory.revision } });
  const manifestIds = new Set((manifest.tasks || []).map((task) => task.id));
  for (const id of [CURRENT_TASK, CARRIED_LATE_SETTLEMENT_TASK, CARRIED_OPERATION_TIMEOUT_TASK, CARRIED_SHUTDOWN_TASK, CARRIED_RESTART_UPDATE_TASK, 'browser:opfs-web-lock-service-worker-lifecycle-proof', 'facility:service-worker-restart-update-contract-audit', 'scheduler:storage-lane-web-lock-settled-recovery-proof', 'facility:service-worker-lifecycle-contract-audit', 'facility:web-lock-settled-recovery-contract-audit', 'scheduler:storage-lane-web-lock-timeout-health-proof', 'browser:opfs-web-lock-tab-timeout-proof', 'scheduler:storage-lane-web-lock-timeout-health-proof', 'browser:opfs-guarded-corrupt-repair-timeout-proof', 'opfs:block-store-corrupt-block-repair-proof', 'browser:opfs-corrupt-block-repair-proof', 'coord:web-lock-timeout-proof', 'browser:opfs-web-lock-timeout-proof', 'browser:opfs-web-lock-tab-termination-proof', 'facility:revision-lineage-merge-audit', 'facility:branch-continuity-audit']) {
    check(checks, `manifest-has-${id}`, manifestIds.has(id));
  }
  check(checks, 'opfs-corrupt-repair-runtime-present', missing(opfs, ['verifyExistingBlocksOnPut', 'repairCorruptOnPut', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'storage:opfs-block-repair', 'storage:opfs-block-integrity-ok', 'exclusiveWriters']).length === 0, { missing: missing(opfs, ['verifyExistingBlocksOnPut', 'repairCorruptOnPut', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'storage:opfs-block-repair', 'storage:opfs-block-integrity-ok', 'exclusiveWriters']) });
  check(checks, 'web-lock-timeout-tab-lifecycle-runtime-present', missing(coordinator, ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCK_ABORTED', 'defaultTimeoutMs', 'coord:web-lock-timeout', 'queryLocks', 'waitForSettled', 'coord:web-lock-wait-settled-complete']).length === 0, { missing: missing(coordinator, ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCK_ABORTED', 'defaultTimeoutMs', 'coord:web-lock-timeout', 'queryLocks', 'waitForSettled', 'coord:web-lock-wait-settled-complete']) });
  check(checks, 'storage-lane-timeout-health-present', missing(scheduler, ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCKS_UNAVAILABLE', 'isStorageHealthFailure', 'storage-lane:provider-unhealthy']).length === 0, { missing: missing(scheduler, ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCKS_UNAVAILABLE', 'isStorageHealthFailure', 'storage-lane:provider-unhealthy']) });
  check(checks, 'browser-cdp-target-helpers-present', missing(fixture, ['connectBrowserCdp', 'openPageTarget', 'closePageTarget', 'Target.createTarget', 'Target.closeTarget']).length === 0, { missing: missing(fixture, ['connectBrowserCdp', 'openPageTarget', 'closePageTarget', 'Target.createTarget', 'Target.closeTarget']) });
  check(checks, 'tab-timeout-browser-proof-present', missing(tabTimeoutProof, ['browser:opfs-web-lock-tab-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'holderStillHeldAfterTimeout', 'lockQueryWhilePending', 'closePageTarget']).length === 0, { missing: missing(tabTimeoutProof, ['browser:opfs-web-lock-tab-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'holderStillHeldAfterTimeout', 'lockQueryWhilePending', 'closePageTarget']) });
  check(checks, 'storage-lane-timeout-health-proof-present', missing(storageHealthProof, ['scheduler:storage-lane-web-lock-timeout-health-proof', 'BRT_WEB_LOCK_TIMEOUT', 'rejected-lane-unhealthy', 'maintenance fallback', 'explicit recovery']).length === 0, { missing: missing(storageHealthProof, ['scheduler:storage-lane-web-lock-timeout-health-proof', 'BRT_WEB_LOCK_TIMEOUT', 'rejected-lane-unhealthy', 'maintenance fallback', 'explicit recovery']) });
  check(checks, 'guarded-corrupt-repair-timeout-branch-retained', missing(guardedProof, ['browser:opfs-guarded-corrupt-repair-timeout-proof', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresentAfterHolder', 'corruptRepairs']).length === 0, { missing: missing(guardedProof, ['browser:opfs-guarded-corrupt-repair-timeout-proof', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresentAfterHolder', 'corruptRepairs']) });
  check(checks, 'changelog-documents-lineage-merge', changelog.startsWith(`## ${REVISION}`) && missing(changelog.slice(0, 3500), ['late-failure', 'timed-out-operation-late-failure', 'BRT_STORAGE_OPERATION_TIMEOUT', CURRENT_TASK]).length === 0 && changelog.includes(CARRIED_SHUTDOWN_TASK) && changelog.includes(CARRIED_RESTART_UPDATE_TASK), { missing: missing(changelog.slice(0, 3500), ['late-failure', 'timed-out-operation-late-failure', 'BRT_STORAGE_OPERATION_TIMEOUT', CURRENT_TASK]).concat(changelog.includes(CARRIED_SHUTDOWN_TASK) ? [] : [CARRIED_SHUTDOWN_TASK]).concat(changelog.includes(CARRIED_RESTART_UPDATE_TASK) ? [] : [CARRIED_RESTART_UPDATE_TASK]) });
  check(checks, 'lineage-note-documents-merged-archives', missing(lineageNote, ['opfs-corrupt-block-repair-proof.zip', 'opfs-web-lock-tab-termination-proof.zip', 'opfs-web-lock-timeout-proof.zip']).length === 0, { missing: missing(lineageNote, ['opfs-corrupt-block-repair-proof.zip', 'opfs-web-lock-tab-termination-proof.zip', 'opfs-web-lock-timeout-proof.zip']) });
  for (const path of ['README.md', 'START_HERE.md', 'AGENTS.md', 'CONTEXT-PACK.md']) {
    const body = await text(path);
    check(checks, `${path}:first-read-current`, body.includes(REVISION) && body.includes(CODENAME) && body.includes(CURRENT_TASK));
  }

  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 2,
    audit_id: 'facility:revision-lineage-merge-audit', status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(), durationMs: Date.now() - started,
    purpose: 'Guard against parallel same-revision cloudtainer branches by allowing the current late-failure quarantine office while keeping Service Worker fetch/update/shutdown, restart/update, settled-recovery, corrupt-repair, worker-timeout, tab-termination, tab-timeout, and guarded-merge branch evidence reachable.',
    checks,
    failed,
    nonClaims: [
      'This audit detects static/currentness drift; it is not a substitute for browser execution of the shutdown-boundary proof.',
      'This audit does not prove cross-browser behavior, OPFS durability, quota, eviction, power-loss safety, fairness, or production readiness.'
    ]
  };
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
try {
  const report = await runAudit();
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
  else console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'passed') process.exitCode = 1;
} catch (error) {
  const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 2, audit_id: 'facility:revision-lineage-merge-audit', status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack } };
  if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); }
  console.error(`[revision_lineage_merge_audit] FAIL: ${error?.stack || error}`);
  process.exitCode = 1;
}
