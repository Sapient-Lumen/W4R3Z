#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-STORAGE-POSTURE-CONTRACT-AUDIT.json`;
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
  const [runtime, types, browserRunner, pageRunner, demoSource, browserProbe, packageJson, packageRelease, manifest, impact, inventory] = await Promise.all([
    text('src/browserrt.mjs'),
    text('src/types.d.ts'),
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
  const task = (manifest.tasks || []).find((row) => row.id === 'facility:kernel-kit-storage-posture-audit');
  const browserTask = (manifest.tasks || []).find((row) => row.id === 'browser:kernel-kit-demo-proof');
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.tasks || []));
  const surface = (inventory.surfaces || []).find((row) => row.id === 'surface:kernel-kit-storage-posture');
  const testKernelKit = packageJson.scripts?.['test:kernel-kit'] || '';
  const checks = [
    sourceCheck('runtime-captures-storage-posture-without-persistence-request', runtime, [
      'async kernelKitStoragePosture',
      'storage.estimate',
      'storage.persisted',
      'config.requestPersistentStorage',
      'persistenceNotRequestedByDefault',
      'kernel-kit-demo:storage-posture',
      'Storage posture is advisory capability/estimate evidence'
    ]),
    sourceCheck('types-expose-storage-posture-method', types, ['kernelKitStoragePosture(config?: Record<string, unknown>)']),
    sourceCheck('browser-runner-carries-storage-posture', browserRunner, ['kernelKitStoragePosture', 'storagePosture', 'storagePostureObserved', 'kernel-kit-demo-work-storage-posture', 'kernel-kit-demo-reload-storage-posture']),
    sourceCheck('page-runner-renders-storage-posture', pageRunner, ['kernelKitStoragePosture', 'storagePostureObserved', 'data-storage-posture-status', 'kernel-kit-demo:storage-posture']),
    sourceCheck('support-bundle-preserves-storage-posture', demoSource, ['storage-posture', 'compactStoragePosture', 'storagePosturePresent', 'persistentStorageRequested', 'No browser StorageManager posture was observed']),
    sourceCheck('browser-probe-enforces-and-compacts-storage-posture', browserProbe, ['work.storagePosture', 'reload.storagePosture', 'supportBundle?.storagePosture?.success?.status', 'compactObservedForArtifact', 'kernel-kit-demo:storage-posture']),
    sourceCheck('package-retains-focused-storage-posture-audit', packageRelease, ['KERNEL-KIT-STORAGE-POSTURE-CONTRACT-AUDIT']),
    check('manifest-audit-task-present', Boolean(task), { task: task?.id || null }),
    check('manifest-audit-task-release-non-browser', Boolean(task) && task.tiers?.includes('release') && task.lane !== 'browser', { tiers: task?.tiers || null, lane: task?.lane || null }),
    check('manifest-browser-task-inputs-include-storage-posture-sources', Boolean(browserTask) && browserTask.inputs?.includes('src/browserrt.mjs') && browserTask.inputs?.includes('demo/kernel-kit-demo-runner.mjs'), { task: browserTask?.id || null }),
    check('package-script-runs-storage-posture-audit', testKernelKit.includes('facility:kernel-kit-storage-posture-audit'), { script: testKernelKit }),
    check('impact-map-routes-storage-posture-to-browser-proof-and-audit', impactIds.has('facility:kernel-kit-storage-posture-audit') && impactIds.has('browser:kernel-kit-demo-proof'), { taskIds: Array.from(impactIds).filter((id) => String(id).includes('storage-posture') || id === 'browser:kernel-kit-demo-proof') }),
    check('surface-inventory-names-storage-posture', Boolean(surface) && surface.currentTaskIds?.includes('facility:kernel-kit-storage-posture-audit') && surface.currentTaskIds?.includes('browser:kernel-kit-demo-proof'), { surface: surface?.id || null })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-storage-posture-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Release-tier static audit that Kernel Kit captures browser StorageManager estimate/persistence posture in the product path without requesting persistent storage or claiming quota reservation/eviction survival.',
    checks,
    nonClaims: [
      'Static audit only; browser:kernel-kit-demo-proof supplies managed Chromium behavior.',
      'Storage posture is advisory capability/estimate evidence, not a quota reservation or eviction-survival proof.',
      'No persistent-storage grant, browser-restart durability, fsync, crash-recovery, or cross-browser conformance claim.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(report, null, 2) + '\n');
console.log(out);
assert.equal(report.status, 'passed', report.checks.filter((row) => row.status !== 'passed').map((row) => `${row.name}: ${(row.missing || []).join(',')}`).join('; '));
