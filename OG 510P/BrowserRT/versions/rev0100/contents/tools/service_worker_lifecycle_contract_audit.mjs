#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const CURRENT_PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${CURRENT_PREFIX}-SERVICE-WORKER-LIFECYCLE-CONTRACT-AUDIT.json`;
const TASK_ID = 'facility:service-worker-lifecycle-contract-audit';
const BROWSER_TASK = 'browser:opfs-web-lock-service-worker-lifecycle-proof';
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
  worker: await text('tools/browserrt_opfs_web_lock_service_worker_holder.mjs'),
  probe: await text('tools/browser_opfs_web_lock_service_worker_lifecycle_probe.mjs'),
  fixture: await text('tools/browser_cdp_fixture.mjs'),
  checkCube: await text('tools/check_cube.py'),
  deepAudit: await text('tools/deep_cube_audit.mjs'),
  doc: await text('docs/40-validation/browser-opfs-web-lock-service-worker-lifecycle-slice.md'),
  auditDoc: await text('docs/40-validation/service-worker-lifecycle-contract-audit-slice.md'),
  packageJsonText: await text('package.json'),
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

check(checks, 'runtime-revision-current', /^rev\d{4}$/.test(REVISION) && /^\d+\.\d+\.\d+$/.test(VERSION), { observed: { REVISION, VERSION } });
check(checks, 'service-worker-source-imports-browserrt-modules', missing(files.worker, ['createOpfsAsyncBlockStore', 'createWebLockGuardedBlockStore', 'self.addEventListener(\'message\'', 'cmd === \'hold\'', 'cmd === \'put-once\'', 'cmd === \'release\'', 'BRT_SW_VERSION']).length === 0, { missing: missing(files.worker, ['createOpfsAsyncBlockStore', 'createWebLockGuardedBlockStore', 'cmd === \'hold\'', 'cmd === \'put-once\'', 'cmd === \'release\'', 'BRT_SW_VERSION']) });
check(checks, 'browser-fixture-has-route-and-service-worker-target-helpers', missing(files.fixture, ['routes = {}', 'routeEntries', 'listCdpTargets', 'findCdpTargets', 'closeServiceWorkerTargets', 'Target.getTargets', 'Target.closeTarget']).length === 0, { missing: missing(files.fixture, ['routes = {}', 'routeEntries', 'listCdpTargets', 'findCdpTargets', 'closeServiceWorkerTargets', 'Target.getTargets', 'Target.closeTarget']) });
check(checks, 'browser-proof-exercises-service-worker-lock-timeout-recovery', missing(files.probe, [BROWSER_TASK, 'serviceWorker.register', 'Service-Worker-Allowed', 'closeServiceWorkerTargets', 'BRT_WEB_LOCK_TIMEOUT', 'recoverWhenStoreSettled', 'lockQueryWhilePending', 'timeoutPresent', 'holderVerify', 'recoveredVerify']).length === 0, { missing: missing(files.probe, [BROWSER_TASK, 'serviceWorker.register', 'Service-Worker-Allowed', 'closeServiceWorkerTargets', 'BRT_WEB_LOCK_TIMEOUT', 'recoverWhenStoreSettled', 'lockQueryWhilePending', 'timeoutPresent', 'holderVerify', 'recoveredVerify']) });

const tasks = manifest.tasks || [];
const byId = new Map(tasks.map((task) => [task.id, task]));
const browserTask = byId.get(BROWSER_TASK);
const auditTask = byId.get(TASK_ID);
check(checks, 'manifest-has-browser-service-worker-task', Boolean(browserTask), { task: browserTask || null });
check(checks, 'manifest-browser-task-explicit-not-release', Boolean(browserTask && browserTask.lane === 'browser' && browserTask.parallelGroup === 'browser-process' && browserTask.tiers?.includes('browser') && !browserTask.tiers?.includes('release')), { lane: browserTask?.lane, tiers: browserTask?.tiers, parallelGroup: browserTask?.parallelGroup });
check(checks, 'manifest-has-release-audit-task', Boolean(auditTask && auditTask.tiers?.includes('release') && auditTask.lane === 'audit'), { task: auditTask || null });
check(checks, 'manifest-outputs-current-prefix', tasks.every((task) => [...(task.outputs || []), ...(task.command || [])].every((item) => !/REV\d{4}-/.test(String(item)) || String(item).includes(`${CURRENT_PREFIX}-`))), { currentPrefix: CURRENT_PREFIX });

const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
check(checks, 'impact-map-covers-service-worker-tasks', impactTaskIds.has(BROWSER_TASK) && impactTaskIds.has(TASK_ID), { hasBrowser: impactTaskIds.has(BROWSER_TASK), hasAudit: impactTaskIds.has(TASK_ID) });
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
check(checks, 'surface-inventory-covers-service-worker-lifecycle', surfaceIds.has('surface:browser-opfs-web-lock-service-worker-lifecycle') && surfaceIds.has('surface:service-worker-lifecycle-contract-audit'), { ids: ['surface:browser-opfs-web-lock-service-worker-lifecycle', 'surface:service-worker-lifecycle-contract-audit'].filter((id) => surfaceIds.has(id)) });

for (const [name, body] of [['doc', files.doc], ['auditDoc', files.auditDoc], ['README', files.readme], ['START_HERE', files.start], ['CONTEXT-PACK', files.context], ['AGENTS', files.agents], ['REVISION-RECEIPT', files.receipt]]) {
  check(checks, `${name}-service-worker-nonclaims-visible`, missingLower(body, ['service-worker', 'cross-browser', 'quota', 'eviction', 'persistent', 'production']).length === 0, { missing: missingLower(body, ['service-worker', 'cross-browser', 'quota', 'eviction', 'persistent', 'production']) });
}
check(checks, 'service-worker-lifecycle-carried-forward-or-current', Boolean(cubeMeta.current_task === BROWSER_TASK || (cubeMeta.carried_forward_browser_proofs || []).includes(BROWSER_TASK) || (cubeMeta.current_task || '').includes('service-worker')), { current_task: cubeMeta.current_task, current_audit: cubeMeta.current_audit, package_slug: cubeMeta.package_slug, carried_forward_browser_proofs: cubeMeta.carried_forward_browser_proofs || [] });
check(checks, 'plan-surface-mentions-service-worker-files', missing(files.packageJsonText, ['browser_opfs_web_lock_service_worker_lifecycle_probe.mjs', 'browserrt_opfs_web_lock_service_worker_holder.mjs', 'service_worker_lifecycle_contract_audit.mjs']).length === 0, { missing: missing(files.packageJsonText, ['browser_opfs_web_lock_service_worker_lifecycle_probe.mjs', 'browserrt_opfs_web_lock_service_worker_holder.mjs', 'service_worker_lifecycle_contract_audit.mjs']) });
check(checks, 'check-cube-and-deep-audit-know-service-worker-slice', missing(files.checkCube, [BROWSER_TASK, TASK_ID, 'browserrt_opfs_web_lock_service_worker_holder.mjs']).length === 0 && missing(files.deepAudit, [BROWSER_TASK, TASK_ID, 'browserrt_opfs_web_lock_service_worker_holder.mjs']).length === 0, { checkCubeMissing: missing(files.checkCube, [BROWSER_TASK, TASK_ID, 'browserrt_opfs_web_lock_service_worker_holder.mjs']), deepAuditMissing: missing(files.deepAudit, [BROWSER_TASK, TASK_ID, 'browserrt_opfs_web_lock_service_worker_holder.mjs']) });

const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  task_id: TASK_ID,
  status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
  purpose: 'Browser-light contract audit that keeps the managed Chromium OPFS/Web Locks Service Worker lifecycle proof wired into fixture helpers, worker source, manifest, impact map, surface inventory, docs, and carried-forward/current metadata without moving the browser-heavy proof into release.',
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
  console.error(`[service_worker_lifecycle_contract_audit] FAIL ${failed.length} check(s)`);
  process.exitCode = 1;
}
