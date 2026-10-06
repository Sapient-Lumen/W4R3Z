#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const CURRENT_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${CURRENT_PREFIX}-SERVICE-WORKER-RESTART-UPDATE-CONTRACT-AUDIT.json`;
const TASK_ID = 'facility:service-worker-restart-update-contract-audit';
const BROWSER_TASK = 'browser:opfs-web-lock-service-worker-restart-update-proof';
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const outPath = argValue('--json', DEFAULT_OUT);
const REVISION_NUMBER = Number(REVISION.slice(3));

async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function missingLower(body, needles) { const lower = String(body).toLowerCase(); return needles.filter((needle) => !lower.includes(String(needle).toLowerCase())); }
function check(checks, name, passed, detail = {}) { checks.push({ name, status: passed ? 'passed' : 'failed', ...detail }); }

const checks = [];
const files = {
  worker: await text('tools/browserrt_opfs_web_lock_service_worker_holder.mjs'),
  probe: await text('tools/browser_opfs_web_lock_service_worker_restart_update_probe.mjs'),
  fixture: await text('tools/browser_cdp_fixture.mjs'),
  checkCube: await text('tools/check_cube.py'),
  deepAudit: await text('tools/deep_cube_audit.mjs'),
  doc: await text('docs/40-validation/browser-opfs-web-lock-service-worker-restart-update-slice.md'),
  auditDoc: await text('docs/40-validation/service-worker-restart-update-contract-audit-slice.md'),
  packageJsonText: await text('package.json'),
  makefile: await text('Makefile'),
  readme: await text('README.md'),
  start: await text('START_HERE.md'),
  context: await text('CONTEXT-PACK.md'),
  agents: await text('AGENTS.md'),
  receipt: await text('REVISION-RECEIPT.json')
};
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const cubeMeta = await json('CUBE-META.json');

check(checks, 'runtime-revision-current', REVISION_NUMBER >= 65 && /^0\.0\.\d+$/.test(VERSION), { observed: { REVISION, VERSION } });
check(checks, 'worker-source-supports-restart-update-commands', missing(files.worker, ['BRT_SW_VERSION', "cmd === 'put-once'", "cmd === 'release'", 'workerIdentity', 'createWebLockGuardedBlockStore', 'createOpfsAsyncBlockStore']).length === 0, { missing: missing(files.worker, ['BRT_SW_VERSION', "cmd === 'put-once'", "cmd === 'release'", 'workerIdentity', 'createWebLockGuardedBlockStore', 'createOpfsAsyncBlockStore']) });
check(checks, 'browser-proof-uses-persistent-profile-and-v1-v2-update', missing(files.probe, [BROWSER_TASK, 'startProbeServer', 'profileDir', 'keepProfile: true', 'SW_V1_ROUTE', 'SW_V2_ROUTE', "updateViaCache: 'none'", 'versionedWorkerSource', 'pageLaneWriteExpression', 'reapBrowserProfileProcesses', 'registrationsBefore', 'registrationsAfterUpdate']).length === 0, { missing: missing(files.probe, [BROWSER_TASK, 'startProbeServer', 'profileDir', 'keepProfile: true', 'SW_V1_ROUTE', 'SW_V2_ROUTE', "updateViaCache: 'none'", 'versionedWorkerSource', 'pageLaneWriteExpression', 'reapBrowserProfileProcesses', 'registrationsBefore', 'registrationsAfterUpdate']) });
check(checks, 'fixture-supports-reused-server-and-profile', missing(files.fixture, ['options.server', 'externalServer', 'options.profileDir', 'keepProfile', 'reapBrowserProfileProcesses']).length === 0, { missing: missing(files.fixture, ['options.server', 'externalServer', 'options.profileDir', 'keepProfile', 'reapBrowserProfileProcesses']) });

const tasks = manifest.tasks || [];
const byId = new Map(tasks.map((task) => [task.id, task]));
const browserTask = byId.get(BROWSER_TASK);
const auditTask = byId.get(TASK_ID);
check(checks, 'manifest-has-browser-restart-update-task', Boolean(browserTask), { task: browserTask || null });
check(checks, 'manifest-browser-task-explicit-not-release', Boolean(browserTask && browserTask.lane === 'browser' && browserTask.parallelGroup === 'browser-process' && browserTask.tiers?.includes('browser') && !browserTask.tiers?.includes('release')), { lane: browserTask?.lane, tiers: browserTask?.tiers, parallelGroup: browserTask?.parallelGroup });
check(checks, 'manifest-has-release-audit-task', Boolean(auditTask && auditTask.tiers?.includes('release') && auditTask.lane === 'audit'), { task: auditTask || null });
check(checks, 'manifest-outputs-current-prefix', tasks.every((task) => [...(task.outputs || []), ...(task.command || [])].every((item) => !/REV\d{4}-/.test(String(item)) || String(item).includes(`${CURRENT_PREFIX}-`))), { currentPrefix: CURRENT_PREFIX });

const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
check(checks, 'impact-map-covers-restart-update-tasks', impactTaskIds.has(BROWSER_TASK) && impactTaskIds.has(TASK_ID), { hasBrowser: impactTaskIds.has(BROWSER_TASK), hasAudit: impactTaskIds.has(TASK_ID) });
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
check(checks, 'surface-inventory-covers-restart-update', surfaceIds.has('surface:browser-opfs-web-lock-service-worker-restart-update') && surfaceIds.has('surface:service-worker-restart-update-contract-audit'), { ids: ['surface:browser-opfs-web-lock-service-worker-restart-update', 'surface:service-worker-restart-update-contract-audit'].filter((id) => surfaceIds.has(id)) });

for (const [name, body] of [['doc', files.doc], ['auditDoc', files.auditDoc], ['README', files.readme], ['START_HERE', files.start], ['CONTEXT-PACK', files.context], ['AGENTS', files.agents], ['REVISION-RECEIPT', files.receipt]]) {
  check(checks, `${name}-restart-update-nonclaims-visible`, missingLower(body, ['service worker', 'restart', 'update', 'cross-browser', 'quota', 'eviction', 'persistent', 'production']).length === 0, { missing: missingLower(body, ['service worker', 'restart', 'update', 'cross-browser', 'quota', 'eviction', 'persistent', 'production']) });
}
const restartUpdateIsCurrent = cubeMeta.current_task === BROWSER_TASK && cubeMeta.current_audit === TASK_ID && cubeMeta.package_slug === 'opfs-web-lock-service-worker-restart-update-proof';
const restartUpdateIsCarriedForward = REVISION_NUMBER > 65 && cubeMeta.current_task !== BROWSER_TASK && cubeMeta.current_audit !== TASK_ID;
check(checks, 'restart-update-current-or-carried-forward', restartUpdateIsCurrent || restartUpdateIsCarriedForward, { current_task: cubeMeta.current_task, current_audit: cubeMeta.current_audit, package_slug: cubeMeta.package_slug, carriedForward: restartUpdateIsCarriedForward });
check(checks, 'operator-shortcuts-present', missing(files.packageJsonText, ['test:browser:opfs-web-lock-service-worker-restart-update', 'audit:service-worker-restart-update']).length === 0 && missing(files.makefile, ['test-browser-opfs-web-lock-service-worker-restart-update', 'audit-service-worker-restart-update']).length === 0, { packageMissing: missing(files.packageJsonText, ['test:browser:opfs-web-lock-service-worker-restart-update', 'audit:service-worker-restart-update']), makeMissing: missing(files.makefile, ['test-browser-opfs-web-lock-service-worker-restart-update', 'audit-service-worker-restart-update']) });
check(checks, 'check-cube-and-deep-audit-know-restart-update-slice', missing(files.checkCube, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_restart_update_probe.mjs']).length === 0 && missing(files.deepAudit, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_restart_update_probe.mjs']).length === 0, { checkCubeMissing: missing(files.checkCube, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_restart_update_probe.mjs']), deepAuditMissing: missing(files.deepAudit, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_restart_update_probe.mjs']) });

const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  task_id: TASK_ID,
  status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
  purpose: 'Browser-light contract audit keeping the managed Chromium Service Worker restart/update proof wired into the worker source, profile/server fixture use, manifest, impact map, surface inventory, docs, operator shortcuts, and current-office metadata without moving browser-heavy execution into release.',
  checks,
  nonClaims: [
    'This audit does not launch a browser or prove service-worker runtime behavior.',
    'No cross-browser, mobile/background, fetch-event, push-event, offline, quota, eviction, persistent-retention, OPFS durability, or production-readiness claim.',
    'The managed Chromium browser proof must still be run explicitly by id for runtime evidence.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (failed.length) {
  console.error(`[service_worker_restart_update_contract_audit] FAIL ${failed.length} check(s)`);
  process.exitCode = 1;
}
