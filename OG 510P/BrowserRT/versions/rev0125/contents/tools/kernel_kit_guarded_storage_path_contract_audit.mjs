#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-GUARDED-STORAGE-PATH-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function check(name, passed, detail = {}) { return Object.freeze({ name, status: passed ? 'passed' : 'failed', ...detail }); }
function sourceCheck(name, body, needles) {
  const misses = missing(body, needles);
  return check(name, misses.length === 0, { missing: misses, needleCount: needles.length });
}

export async function runAudit() {
  const [runtime, browserRunner, pageRunner, demoSource, browserProbe, packageJson, packageRelease, manifest, impact, inventory] = await Promise.all([
    text('src/browserrt.mjs'),
    text('src/kernel-kit-demo-browser-runner.mjs'),
    text('demo/kernel-kit-demo-runner.mjs'),
    text('src/kernel-kit-demo.mjs'),
    text('tools/browser_kernel_kit_demo_probe.mjs'),
    json('package.json'),
    text('tools/package_release.py'),
    json('test/manifest.json'),
    json('test/impact-map.json'),
    json('test/surface-inventory.json')
  ]);
  const task = (manifest.tasks || []).find((row) => row.id === 'facility:kernel-kit-guarded-storage-path-audit');
  const browserTask = (manifest.tasks || []).find((row) => row.id === 'browser:kernel-kit-demo-proof');
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.tasks || []));
  const surface = (inventory.surfaces || []).find((row) => row.id === 'surface:kernel-kit-guarded-storage-path');
  const testKernelKit = packageJson.scripts?.['test:kernel-kit'] || '';
  const checks = [
    sourceCheck('runtime-exposes-guarded-opfs-provider', runtime, [
      'opfsWebLockGuardedBlockStore(config = {})',
      'createWebLockGuardedBlockStore',
      'object:opfs-web-lock-guarded-block-store-ref',
      'WebLockGuardedBlockStore'
    ]),
    sourceCheck('browser-runner-routes-storage-lane-through-guarded-store', browserRunner, [
      'opfsWebLockGuardedBlockStore',
      'opfsBlockStoreStorageLaneAdapter',
      'store: guardedStore',
      'compactKernelKitGuardedStorageSnapshot',
      'guardedStorageLane',
      'kernel-kit-demo-reload-guarded-store'
    ]),
    sourceCheck('page-runner-routes-human-demo-through-guarded-store', pageRunner, [
      'opfsWebLockGuardedBlockStore',
      'store: guardedStore',
      'data-guarded-storage-lane-status',
      'guardedStorageLane',
      'supportBundle.guardedStorageLane',
      'storage:opfs-web-lock-guard-op-complete'
    ]),
    sourceCheck('support-bundle-preserves-guarded-storage-evidence', demoSource, [
      'guarded-storage-lane',
      'compactGuardedStorageLane',
      'guardedStorageLanePresent',
      'guardedProvider',
      'lockAcquiredReleased',
      'Managed-browser Web-Locks-guarded storage-lane evidence'
    ]),
    sourceCheck('browser-proof-enforces-guarded-storage-behavior', browserProbe, [
      'work.storage.guarded?.status',
      'reload.guardedStorage?.status',
      'supportBundle?.guardedStorageLane?.success?.status',
      'object:opfs-web-lock-guarded-block-store-ref',
      'storage:opfs-web-lock-guard-op-complete',
      'coord:web-lock-acquired'
    ]),
    sourceCheck('package-retains-focused-guarded-storage-audit', packageRelease, ['KERNEL-KIT-GUARDED-STORAGE-PATH-CONTRACT-AUDIT']),
    check('manifest-audit-task-present', Boolean(task), { task: task?.id || null }),
    check('manifest-audit-task-release-non-browser', Boolean(task) && task.tiers?.includes('release') && task.lane !== 'browser', { tiers: task?.tiers || null, lane: task?.lane || null }),
    check('manifest-browser-task-inputs-include-guarded-storage-sources', Boolean(browserTask) && browserTask.inputs?.includes('src/opfs-web-lock-guarded-block-store.mjs') && browserTask.inputs?.includes('src/web-lock-coordinator.mjs') && browserTask.inputs?.includes('tools/kernel_kit_guarded_storage_path_contract_audit.mjs'), { task: browserTask?.id || null }),
    check('package-script-runs-guarded-storage-audit', testKernelKit.includes('facility:kernel-kit-guarded-storage-path-audit'), { script: testKernelKit }),
    check('impact-map-routes-guarded-storage-to-browser-proof-and-audit', impactIds.has('facility:kernel-kit-guarded-storage-path-audit') && impactIds.has('browser:kernel-kit-demo-proof'), { taskIds: Array.from(impactIds).filter((id) => String(id).includes('guarded-storage') || id === 'browser:kernel-kit-demo-proof') }),
    check('surface-inventory-names-guarded-storage-path', Boolean(surface) && surface.currentTaskIds?.includes('facility:kernel-kit-guarded-storage-path-audit') && surface.currentTaskIds?.includes('browser:kernel-kit-demo-proof'), { surface: surface?.id || null })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-guarded-storage-path-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Release-tier static audit that the Kernel Kit product path routes actual OPFS storage-lane work through WebLockGuardedBlockStore and preserves the evidence in browser proof/support bundles.',
    checks,
    nonClaims: [
      'Static audit only; browser:kernel-kit-demo-proof supplies managed Chromium behavior.',
      'Guarded storage-lane evidence does not claim Web Locks fairness, lifecycle recovery, cross-browser behavior, crash recovery, or production multi-tab coordination.',
      'No OPFS durability, fsync, quota, eviction, exactly-once, or product-market-fit claim.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(report, null, 2) + '\n');
console.log(out);
assert.equal(report.status, 'passed', report.checks.filter((row) => row.status !== 'passed').map((row) => `${row.name}: ${(row.missing || []).join(',')}`).join('; '));
