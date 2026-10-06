#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const CURRENT_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${CURRENT_PREFIX}-SERVICE-WORKER-FETCH-LIFECYCLE-CONTRACT-AUDIT.json`;
const TASK_ID = 'facility:service-worker-fetch-lifecycle-contract-audit';
const BROWSER_TASK = 'browser:opfs-web-lock-service-worker-fetch-lifecycle-proof';
const CODENAME = 'OPFS Web Lock Service Worker Fetch Lifecycle Proof';
const SLUG = 'opfs-web-lock-service-worker-fetch-lifecycle-proof';
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
  probe: await text('tools/browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs'),
  worker: await text('tools/browserrt_opfs_web_lock_service_worker_holder.mjs'),
  checkCube: await text('tools/check_cube.py'),
  deepAudit: await text('tools/deep_cube_audit.mjs'),
  doc: await text('docs/40-validation/browser-opfs-web-lock-service-worker-fetch-lifecycle-slice.md'),
  auditDoc: await text('docs/40-validation/service-worker-fetch-lifecycle-contract-audit-slice.md'),
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

check(checks, 'runtime-revision-current', packageJson.revision === REVISION && packageJson.version === VERSION, { observed: { REVISION, VERSION, packageRevision: packageJson.revision, packageVersion: packageJson.version } });
check(checks, 'package-fetch-lifecycle-carried-forward-or-current', packageJson.revision === REVISION && packageJson.version === VERSION && (packageJson.current_task === BROWSER_TASK || packageJson.current_task === 'browser:opfs-web-lock-operation-timeout-boundary-proof' || packageJson.current_task === 'browser:opfs-web-lock-late-settlement-recovery-gate-proof' || (packageJson.carried_forward_browser_proofs || []).includes(BROWSER_TASK)), { observed: { revision: packageJson.revision, version: packageJson.version, codename: packageJson.codename, package_slug: packageJson.package_slug, current_task: packageJson.current_task, current_audit: packageJson.current_audit }, carried_forward: BROWSER_TASK });
check(checks, 'cube-meta-fetch-lifecycle-carried-forward-or-current', cubeMeta.revision === REVISION && cubeMeta.version === VERSION && (cubeMeta.current_task === BROWSER_TASK || cubeMeta.current_task === 'browser:opfs-web-lock-operation-timeout-boundary-proof' || cubeMeta.current_task === 'browser:opfs-web-lock-late-settlement-recovery-gate-proof' || (cubeMeta.carried_forward_browser_proofs || []).includes(BROWSER_TASK)), { observed: { revision: cubeMeta.revision, version: cubeMeta.version, codename: cubeMeta.codename, package_slug: cubeMeta.package_slug, current_task: cubeMeta.current_task, current_audit: cubeMeta.current_audit }, carried_forward: BROWSER_TASK });
check(checks, 'browser-proof-uses-fetch-event-holder-timeout-recovery', missing(files.probe, [BROWSER_TASK, 'SW_ROUTE', 'browserrt-sw-fetch-lifecycle', 'fetch(', 'BRT_WEB_LOCK_TIMEOUT', 'blockedRecovery', 'holderVerify', 'timeoutPresent', 'settledRecovery', 'reapBrowserProfileProcesses']).length === 0, { missing: missing(files.probe, [BROWSER_TASK, 'SW_ROUTE', 'browserrt-sw-fetch-lifecycle', 'fetch(', 'BRT_WEB_LOCK_TIMEOUT', 'blockedRecovery', 'holderVerify', 'timeoutPresent', 'settledRecovery', 'reapBrowserProfileProcesses']) });
check(checks, 'worker-source-supports-fetch-lifecycle-route', missing(files.worker, ['handleFetchLifecycleRequest', "self.addEventListener('fetch'", 'event.respondWith', 'browserrt-sw-fetch-lifecycle', 'service-worker-fetch-lifecycle-holder', 'createWebLockGuardedBlockStore', 'createOpfsAsyncBlockStore']).length === 0, { missing: missing(files.worker, ['handleFetchLifecycleRequest', "self.addEventListener('fetch'", 'event.respondWith', 'browserrt-sw-fetch-lifecycle', 'service-worker-fetch-lifecycle-holder', 'createWebLockGuardedBlockStore', 'createOpfsAsyncBlockStore']) });
const tasks = manifest.tasks || [];
const byId = new Map(tasks.map((task) => [task.id, task]));
const browserTask = byId.get(BROWSER_TASK);
const auditTask = byId.get(TASK_ID);
check(checks, 'manifest-has-explicit-browser-task', Boolean(browserTask && browserTask.lane === 'browser' && browserTask.parallelGroup === 'browser-process' && browserTask.tiers?.includes('browser') && !browserTask.tiers?.includes('release')), { task: browserTask || null });
check(checks, 'manifest-has-release-audit-task', Boolean(auditTask && auditTask.lane === 'audit' && (auditTask.tiers?.includes('release') || auditTask.tiers?.includes('audit'))), { task: auditTask || null });
check(checks, 'manifest-current-output-prefixes', tasks.every((task) => [...(task.outputs || []), ...(task.command || [])].every((item) => !/REV\d{4}-/.test(String(item)) || String(item).includes(`${CURRENT_PREFIX}-`))), { currentPrefix: CURRENT_PREFIX });
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
check(checks, 'impact-map-covers-fetch-lifecycle', impactTaskIds.has(BROWSER_TASK) && impactTaskIds.has(TASK_ID), { hasBrowser: impactTaskIds.has(BROWSER_TASK), hasAudit: impactTaskIds.has(TASK_ID) });
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
check(checks, 'surface-inventory-covers-fetch-lifecycle', surfaceIds.has('surface:browser-opfs-web-lock-service-worker-fetch-lifecycle') && surfaceIds.has('surface:service-worker-fetch-lifecycle-contract-audit'), { ids: ['surface:browser-opfs-web-lock-service-worker-fetch-lifecycle', 'surface:service-worker-fetch-lifecycle-contract-audit'].filter((id) => surfaceIds.has(id)) });
for (const [name, body] of [['doc', files.doc], ['auditDoc', files.auditDoc], ['REVISION-RECEIPT', files.receipt]]) {
  check(checks, `${name}-fetch-lifecycle-nonclaims-visible`, missingLower(body, ['service worker', 'fetch', 'web lock', 'opfs', 'cross-browser', 'durability', 'quota', 'eviction', 'persistent', 'production']).length === 0, { missing: missingLower(body, ['service worker', 'fetch', 'web lock', 'opfs', 'cross-browser', 'durability', 'quota', 'eviction', 'persistent', 'production']) });
}
for (const [name, body] of [['README', files.readme], ['START_HERE', files.start], ['CONTEXT-PACK', files.context], ['AGENTS', files.agents]]) {
  check(checks, `${name}-current-storage-nonclaims-visible`, missingLower(body, ['web lock', 'opfs', 'cross-browser', 'quota', 'eviction', 'production']).length === 0, { missing: missingLower(body, ['web lock', 'opfs', 'cross-browser', 'quota', 'eviction', 'production']) });
}
check(checks, 'operator-shortcuts-present', missing(files.packageJsonText, ['test:browser:opfs-web-lock-service-worker-fetch-lifecycle', 'audit:service-worker-fetch-lifecycle']).length === 0 && missing(files.makefile, ['test-browser-opfs-web-lock-service-worker-fetch-lifecycle', 'audit-service-worker-fetch-lifecycle']).length === 0, { packageMissing: missing(files.packageJsonText, ['test:browser:opfs-web-lock-service-worker-fetch-lifecycle', 'audit:service-worker-fetch-lifecycle']), makeMissing: missing(files.makefile, ['test-browser-opfs-web-lock-service-worker-fetch-lifecycle', 'audit-service-worker-fetch-lifecycle']) });
check(checks, 'check-cube-and-deep-audit-know-fetch-lifecycle', missing(files.checkCube, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs']).length === 0 && missing(files.deepAudit, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs']).length === 0, { checkCubeMissing: missing(files.checkCube, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs']), deepAuditMissing: missing(files.deepAudit, [BROWSER_TASK, TASK_ID, 'browser_opfs_web_lock_service_worker_fetch_lifecycle_probe.mjs']) });

const failed = checks.filter((row) => row.status !== 'passed');
const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(), purpose: 'Release-light contract audit for the carried-forward Service Worker fetch-event lifecycle browser proof.', checks, nonClaims: ['This audit does not launch Chromium or prove Service Worker runtime behavior.', 'No cross-browser, Service Worker lifetime, offline-cache correctness, OPFS durability, quota, eviction, persistent-retention, or production-readiness claim.'] };
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (failed.length) process.exitCode = 1;
