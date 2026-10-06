#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const CURRENT_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${CURRENT_PREFIX}-SERVICE-WORKER-SHUTDOWN-BOUNDARY-CONTRACT-AUDIT.json`;
const TASK_ID = 'facility:service-worker-shutdown-boundary-contract-audit';
const BROWSER_TASK = 'browser:opfs-web-lock-service-worker-shutdown-boundary-proof';
const CODENAME = 'OPFS Web Lock Service Worker Shutdown Boundary Proof';
const SLUG = 'opfs-web-lock-service-worker-shutdown-boundary-proof';
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const outPath = argValue('--json', DEFAULT_OUT);
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function missingLower(body, needles) { const lower = String(body).toLowerCase(); return needles.filter((needle) => !lower.includes(String(needle).toLowerCase())); }
function check(checks, name, passed, detail = {}) { checks.push({ name, status: passed ? 'passed' : 'failed', ...detail }); }

const checks = [];
const files = {
  probe: await text('tools/browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs'),
  worker: await text('tools/browserrt_opfs_web_lock_service_worker_holder.mjs'),
  fixture: await text('tools/browser_cdp_fixture.mjs'),
  checkCube: await text('tools/check_cube.py'),
  deepAudit: await text('tools/deep_cube_audit.mjs'),
  doc: await text('docs/40-validation/browser-opfs-web-lock-service-worker-shutdown-boundary-slice.md'),
  auditDoc: await text('docs/40-validation/service-worker-shutdown-boundary-contract-audit-slice.md'),
  packageJsonText: await text('package.json'),
  makefile: await text('Makefile'),
  readme: await text('README.md'),
  start: await text('START_HERE.md'),
  context: await text('CONTEXT-PACK.md'),
  agents: await text('AGENTS.md'),
  receipt: await text('REVISION-RECEIPT.json')
};
const packageJson = JSON.parse(files.packageJsonText);
const cubeMeta = await json('CUBE-META.json');
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');

check(checks, 'runtime-revision-current', /^rev\d{4}$/.test(REVISION) && /^0\.0\.\d+$/.test(VERSION), { observed: { REVISION, VERSION } });
check(checks, 'package-current-revision-keeps-shutdown-carried-forward', packageJson.revision === REVISION && packageJson.version === VERSION, { observed: { revision: packageJson.revision, version: packageJson.version, current_task: packageJson.current_task, current_audit: packageJson.current_audit }, carriedForwardTask: BROWSER_TASK });
check(checks, 'cube-meta-current-revision-keeps-shutdown-carried-forward', cubeMeta.revision === REVISION && cubeMeta.version === VERSION, { observed: { revision: cubeMeta.revision, version: cubeMeta.version, current_task: cubeMeta.current_task, current_audit: cubeMeta.current_audit }, carriedForwardTask: BROWSER_TASK });
check(checks, 'browser-proof-uses-sw-holder-timeout-kill-relaunch-reap', missing(files.probe, [BROWSER_TASK, 'SW_ROUTE', "updateViaCache: 'none'", "cmd: 'hold'", 'BRT_WEB_LOCK_TIMEOUT', "teardownMode: 'kill'", 'lockQueryAtRestart', 'holderVerify', 'timeoutPresent', 'reapBrowserProfileProcesses']).length === 0, { missing: missing(files.probe, [BROWSER_TASK, 'SW_ROUTE', "updateViaCache: 'none'", "cmd: 'hold'", 'BRT_WEB_LOCK_TIMEOUT', "teardownMode: 'kill'", 'lockQueryAtRestart', 'holderVerify', 'timeoutPresent', 'reapBrowserProfileProcesses']) });
check(checks, 'worker-source-supports-hold-release-put-once-status', missing(files.worker, ['BRT_SW_VERSION', "cmd === 'hold'", "cmd === 'release'", "cmd === 'put-once'", "cmd === 'status'", 'createWebLockGuardedBlockStore', 'createOpfsAsyncBlockStore']).length === 0, { missing: missing(files.worker, ['BRT_SW_VERSION', "cmd === 'hold'", "cmd === 'release'", "cmd === 'put-once'", "cmd === 'status'", 'createWebLockGuardedBlockStore', 'createOpfsAsyncBlockStore']) });
check(checks, 'fixture-supports-profile-reaping-and-process-kill', missing(files.fixture, ['killProcessGroup', 'terminateProcessGroup', 'reapBrowserProfileProcesses', 'teardownMode', 'keepProfile', 'options.profileDir']).length === 0, { missing: missing(files.fixture, ['killProcessGroup', 'terminateProcessGroup', 'reapBrowserProfileProcesses', 'teardownMode', 'keepProfile', 'options.profileDir']) });
const tasks = manifest.tasks || [];
const byId = new Map(tasks.map((task) => [task.id, task]));
const browserTask = byId.get(BROWSER_TASK);
const auditTask = byId.get(TASK_ID);
check(checks, 'manifest-has-explicit-browser-task', Boolean(browserTask && browserTask.lane === 'browser' && browserTask.parallelGroup === 'browser-process' && browserTask.tiers?.includes('browser') && !browserTask.tiers?.includes('release')), { task: browserTask || null });
check(checks, 'manifest-has-release-audit-task', Boolean(auditTask && auditTask.lane === 'audit' && (auditTask.tiers?.includes('release') || auditTask.tiers?.includes('audit'))), { task: auditTask || null });
check(checks, 'manifest-current-output-prefixes', tasks.every((task) => [...(task.outputs || []), ...(task.command || [])].every((item) => !/REV\d{4}-/.test(String(item)) || String(item).includes(`${CURRENT_PREFIX}-`))), { currentPrefix: CURRENT_PREFIX });
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
check(checks, 'impact-map-covers-shutdown-boundary', impactTaskIds.has(BROWSER_TASK) && impactTaskIds.has(TASK_ID), { hasBrowser: impactTaskIds.has(BROWSER_TASK), hasAudit: impactTaskIds.has(TASK_ID) });
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
check(checks, 'surface-inventory-covers-shutdown-boundary', surfaceIds.has('surface:browser-opfs-web-lock-service-worker-shutdown-boundary') && surfaceIds.has('surface:service-worker-shutdown-boundary-contract-audit'), { ids: ['surface:browser-opfs-web-lock-service-worker-shutdown-boundary', 'surface:service-worker-shutdown-boundary-contract-audit'].filter((id) => surfaceIds.has(id)) });
for (const [name, body] of [['doc', files.doc], ['auditDoc', files.auditDoc], ['REVISION-RECEIPT', files.receipt]]) {
  check(checks, `${name}-shutdown-boundary-nonclaims-visible`, missingLower(body, ['service worker', 'shutdown', 'web lock', 'opfs', 'cross-browser', 'durability', 'quota', 'eviction', 'persistent', 'production']).length === 0, { missing: missingLower(body, ['service worker', 'shutdown', 'web lock', 'opfs', 'cross-browser', 'durability', 'quota', 'eviction', 'persistent', 'production']) });
}
check(checks, 'operator-shortcuts-present', missing(files.packageJsonText, ['test:browser:opfs-web-lock-service-worker-shutdown-boundary', 'audit:service-worker-shutdown-boundary']).length === 0 && missing(files.makefile, ['test-browser-opfs-web-lock-service-worker-shutdown-boundary', 'audit-service-worker-shutdown-boundary']).length === 0, { packageMissing: missing(files.packageJsonText, ['test:browser:opfs-web-lock-service-worker-shutdown-boundary', 'audit:service-worker-shutdown-boundary']), makeMissing: missing(files.makefile, ['test-browser-opfs-web-lock-service-worker-shutdown-boundary', 'audit-service-worker-shutdown-boundary']) });
check(checks, 'check-cube-and-deep-audit-know-shutdown-boundary', missing(files.checkCube, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs']).length === 0 && missing(files.deepAudit, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs']).length === 0, { checkCubeMissing: missing(files.checkCube, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs']), deepAuditMissing: missing(files.deepAudit, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_shutdown_boundary_probe.mjs']) });

const failed = checks.filter((row) => row.status !== 'passed');
const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(), purpose: 'Release-light carried-forward contract audit for the Service Worker shutdown-boundary browser proof.', checks, nonClaims: ['This audit does not launch Chromium or prove Service Worker runtime behavior.', 'No cross-browser, OPFS durability, browser-shutdown durability, quota, eviction, persistent-retention, or production-readiness claim.'] };
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (failed.length) process.exitCode = 1;
