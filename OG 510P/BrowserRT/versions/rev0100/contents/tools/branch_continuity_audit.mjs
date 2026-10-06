#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-BRANCH-CONTINUITY-AUDIT.json`);

async function text(path) {
  try { return await readFile(path, 'utf8'); }
  catch { return null; }
}

function missingNeedles(body, needles) {
  if (body === null) return needles;
  return needles.filter((needle) => !body.includes(needle));
}

function check(id, passed, details = {}) {
  return { id, status: passed ? 'passed' : 'failed', ...details };
}

const files = Object.fromEntries(await Promise.all([
  'src/opfs-block-store.mjs',
  'src/web-lock-coordinator.mjs',
  'src/opfs-web-lock-guarded-block-store.mjs',
  'src/types.d.ts',
  'tools/opfs_block_store_corrupt_block_repair_probe.mjs',
  'tools/browser_opfs_corrupt_block_repair_probe.mjs',
  'tools/web_lock_timeout_probe.mjs',
  'tools/browser_opfs_web_lock_timeout_probe.mjs',
  'tools/browser_opfs_web_lock_tab_termination_probe.mjs',
  'tools/storage_lane_web_lock_timeout_health_probe.mjs',
  'src/storage-lane-scheduler.mjs',
  'docs/40-validation/browser-opfs-corrupt-block-repair-slice.md',
  'docs/40-validation/storage-lane-web-lock-timeout-health-slice.md',
  'docs/40-validation/browser-opfs-web-lock-timeout-slice.md',
  'docs/40-validation/browser-opfs-web-lock-tab-termination-slice.md',
  'test/manifest.json',
  'test/impact-map.json',
  'test/surface-inventory.json',
  'README.md',
  'CHANGELOG.md'
].map(async (path) => [path, await text(path)])));

const manifest = files['test/manifest.json'] ? JSON.parse(files['test/manifest.json']) : { tasks: [] };
const impact = files['test/impact-map.json'] ? JSON.parse(files['test/impact-map.json']) : { rules: [] };
const inventory = files['test/surface-inventory.json'] ? JSON.parse(files['test/surface-inventory.json']) : { surfaces: [] };
const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
const impactIds = new Set((impact.rules || []).map((rule) => rule.id));
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));

const checks = [
  check('opfs-corrupt-repair-runtime-present', missingNeedles(files['src/opfs-block-store.mjs'], ['verifyExistingBlocksOnPut', 'repairCorruptOnPut', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'storage:opfs-block-corrupt', 'storage:opfs-block-repair', 'postWriteVerifications', 'exclusiveWriters']).length === 0, { missing: missingNeedles(files['src/opfs-block-store.mjs'], ['verifyExistingBlocksOnPut', 'repairCorruptOnPut', 'BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'storage:opfs-block-corrupt', 'storage:opfs-block-repair', 'postWriteVerifications', 'exclusiveWriters']) }),
  check('web-lock-timeout-runtime-present', missingNeedles(files['src/web-lock-coordinator.mjs'], ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCK_ABORTED', 'defaultTimeoutMs', 'coord:web-lock-timeout-arm', 'coord:web-lock-timeout']).length === 0, { missing: missingNeedles(files['src/web-lock-coordinator.mjs'], ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCK_ABORTED', 'defaultTimeoutMs', 'coord:web-lock-timeout-arm', 'coord:web-lock-timeout']) }),
  check('web-lock-query-wait-runtime-present', missingNeedles(files['src/web-lock-coordinator.mjs'], ['normalizeQueryResult', 'queryLocks', 'waitForSettled', 'coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete']).length === 0, { missing: missingNeedles(files['src/web-lock-coordinator.mjs'], ['normalizeQueryResult', 'queryLocks', 'waitForSettled', 'coord:web-lock-query-normalized', 'coord:web-lock-wait-settled-complete']) }),
  check('guarded-store-timeout-still-present', missingNeedles(files['src/opfs-web-lock-guarded-block-store.mjs'], ['lockTimeoutMs', 'timeoutMs', 'signal', 'storage:opfs-web-lock-guard-op-error']).length === 0, { missing: missingNeedles(files['src/opfs-web-lock-guarded-block-store.mjs'], ['lockTimeoutMs', 'timeoutMs', 'signal', 'storage:opfs-web-lock-guard-op-error']) }),
  check('storage-lane-web-lock-timeout-backpressure-present', missingNeedles(files['src/storage-lane-scheduler.mjs'], ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCKS_UNAVAILABLE', 'storage-lane:provider-unhealthy']).length === 0 && missingNeedles(files['tools/storage_lane_web_lock_timeout_health_probe.mjs'], ['BRT_WEB_LOCK_TIMEOUT', 'rejected-lane-unhealthy', 'storage-lane:provider-unhealthy', 'explicit recovery']).length === 0, { schedulerMissing: missingNeedles(files['src/storage-lane-scheduler.mjs'], ['BRT_WEB_LOCK_TIMEOUT', 'BRT_WEB_LOCKS_UNAVAILABLE', 'storage-lane:provider-unhealthy']), proofMissing: missingNeedles(files['tools/storage_lane_web_lock_timeout_health_probe.mjs'], ['BRT_WEB_LOCK_TIMEOUT', 'rejected-lane-unhealthy', 'storage-lane:provider-unhealthy', 'explicit recovery']) }),
  check('corrupt-repair-proofs-present', missingNeedles(files['tools/opfs_block_store_corrupt_block_repair_probe.mjs'], ['BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'repairedCorrupt', 'valid-content verification']).length === 0 && missingNeedles(files['tools/browser_opfs_corrupt_block_repair_probe.mjs'], ['browser:opfs-corrupt-block-repair-proof', 'inject', 'corrupt']).length === 0, { releaseMissing: missingNeedles(files['tools/opfs_block_store_corrupt_block_repair_probe.mjs'], ['BRT_OPFS_BLOCK_CHECKSUM_MISMATCH', 'repairedCorrupt', 'valid-content verification']), browserMissing: missingNeedles(files['tools/browser_opfs_corrupt_block_repair_probe.mjs'], ['browser:opfs-corrupt-block-repair-proof', 'inject', 'corrupt']) }),
  check('timeout-proofs-present', missingNeedles(files['tools/web_lock_timeout_probe.mjs'], ['FakeWebLocksWithAbort', 'BRT_WEB_LOCK_TIMEOUT', 'recoveryVerify']).length === 0 && missingNeedles(files['tools/browser_opfs_web_lock_timeout_probe.mjs'], ['browser:opfs-web-lock-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresentAfterRelease']).length === 0, { releaseMissing: missingNeedles(files['tools/web_lock_timeout_probe.mjs'], ['FakeWebLocksWithAbort', 'BRT_WEB_LOCK_TIMEOUT', 'recoveryVerify']), browserMissing: missingNeedles(files['tools/browser_opfs_web_lock_timeout_probe.mjs'], ['browser:opfs-web-lock-timeout-proof', 'BRT_WEB_LOCK_TIMEOUT', 'timeoutPresentAfterRelease']) }),
  check('tab-termination-proof-present', missingNeedles(files['tools/browser_opfs_web_lock_tab_termination_probe.mjs'], ['browser-opfs-web-lock-tab-termination-proof', 'openPageTarget', 'closePageTarget', 'queryLocks', 'waitForSettled', 'holder tab']).length === 0, { missing: missingNeedles(files['tools/browser_opfs_web_lock_tab_termination_probe.mjs'], ['browser-opfs-web-lock-tab-termination-proof', 'openPageTarget', 'closePageTarget', 'queryLocks', 'waitForSettled', 'holder tab']) }),
  check('manifest-wires-all-three-branches', ['opfs:block-store-corrupt-block-repair-proof', 'browser:opfs-corrupt-block-repair-proof', 'coord:web-lock-timeout-proof', 'browser:opfs-web-lock-timeout-proof', 'browser:opfs-web-lock-tab-termination-proof', 'scheduler:storage-lane-web-lock-timeout-health-proof'].every((id) => taskIds.has(id)), { missingTaskIds: ['opfs:block-store-corrupt-block-repair-proof', 'browser:opfs-corrupt-block-repair-proof', 'coord:web-lock-timeout-proof', 'browser:opfs-web-lock-timeout-proof', 'browser:opfs-web-lock-tab-termination-proof', 'scheduler:storage-lane-web-lock-timeout-health-proof'].filter((id) => !taskIds.has(id)) }),
  check('impact-map-wires-branches', ['impact:opfs-corrupt-block-repair', 'impact:opfs-web-lock-timeout', 'impact:opfs-web-lock-tab-termination', 'impact:storage-lane-web-lock-timeout-health'].every((id) => impactIds.has(id)), { missingImpactIds: ['impact:opfs-corrupt-block-repair', 'impact:opfs-web-lock-timeout', 'impact:opfs-web-lock-tab-termination', 'impact:storage-lane-web-lock-timeout-health'].filter((id) => !impactIds.has(id)) }),
  check('surface-inventory-wires-branches', ['surface:browser-opfs-corrupt-block-repair', 'surface:browser-opfs-web-lock-timeout', 'surface:browser-opfs-web-lock-tab-termination', 'surface:storage-lane-web-lock-timeout-health'].every((id) => surfaceIds.has(id)), { missingSurfaceIds: ['surface:browser-opfs-corrupt-block-repair', 'surface:browser-opfs-web-lock-timeout', 'surface:browser-opfs-web-lock-tab-termination', 'surface:storage-lane-web-lock-timeout-health'].filter((id) => !surfaceIds.has(id)) }),
  check('docs-call-out-nonclaims', ['cross-browser', 'quota', 'eviction', 'crash'].every((needle) => [files['docs/40-validation/browser-opfs-corrupt-block-repair-slice.md'], files['docs/40-validation/browser-opfs-web-lock-timeout-slice.md'], files['docs/40-validation/browser-opfs-web-lock-tab-termination-slice.md'], files['docs/40-validation/storage-lane-web-lock-timeout-health-slice.md']].every((body) => (body || '').toLowerCase().includes(needle))), { missingTerms: ['cross-browser', 'quota', 'eviction', 'crash'].filter((needle) => ![files['docs/40-validation/browser-opfs-corrupt-block-repair-slice.md'], files['docs/40-validation/browser-opfs-web-lock-timeout-slice.md'], files['docs/40-validation/browser-opfs-web-lock-tab-termination-slice.md'], files['docs/40-validation/storage-lane-web-lock-timeout-health-slice.md']].every((body) => (body || '').toLowerCase().includes(needle))) })
];

const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
  purpose: 'Continuity audit that corrupt-block repair, Web Lock timeout, tab-termination lifecycle, and storage-lane Web Lock timeout backpressure branches are present together after the rev0062 branch split and before packaging the unified revision.',
  checks,
  nonClaims: [
    'Static/source continuity audit only; it does not replace browser proofs.',
    'Does not prove cross-browser Web Locks behavior, OPFS durability, quota, eviction, crash recovery, fairness, service-worker lifecycle, or production readiness.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
