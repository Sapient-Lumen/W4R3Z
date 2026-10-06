#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-WEB-LOCK-POSTURE-CONTRACT-AUDIT.json`;
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
  const task = (manifest.tasks || []).find((row) => row.id === 'facility:kernel-kit-web-lock-posture-audit');
  const browserTask = (manifest.tasks || []).find((row) => row.id === 'browser:kernel-kit-demo-proof');
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.tasks || []));
  const surface = (inventory.surfaces || []).find((row) => row.id === 'surface:kernel-kit-web-lock-posture');
  const testKernelKit = packageJson.scripts?.['test:kernel-kit'] || '';
  const checks = [
    sourceCheck('runtime-captures-web-lock-posture-without-fairness-claim', runtime, [
      'async kernelKitWebLockPosture',
      'webLockCoordinator',
      'coordinator.exclusive',
      'coordinator.shared',
      'waitForSettled',
      'exclusiveNoOverlap',
      'sharedCoHold',
      'drainedAfterUse',
      'kernel-kit-demo:web-lock-posture',
      'No OPFS durability, quota, eviction, fsync, exactly-once, or production coordination claim.'
    ]),
    sourceCheck('types-expose-web-lock-posture-method', types, ['kernelKitWebLockPosture(config?: Record<string, unknown>)']),
    sourceCheck('browser-runner-carries-web-lock-posture', browserRunner, ['kernelKitWebLockPosture', 'webLockPosture', 'webLockPostureObserved', 'kernel-kit-demo-work-web-lock-posture', 'kernel-kit-demo-reload-web-lock-posture']),
    sourceCheck('page-runner-renders-web-lock-posture', pageRunner, ['kernelKitWebLockPosture', 'webLockPostureObserved', 'data-web-lock-posture-status', 'kernel-kit-demo:web-lock-posture']),
    sourceCheck('support-bundle-preserves-web-lock-posture', demoSource, ['web-lock-posture', 'compactWebLockPosture', 'webLockPosturePresent', 'noFairnessClaim', 'No browser Web Locks posture was observed']),
    sourceCheck('browser-probe-enforces-and-compacts-web-lock-posture', browserProbe, ['work.webLockPosture', 'reload.webLockPosture', 'supportBundle?.webLockPosture?.success?.status', 'compactWebLockPosture', 'kernel-kit-demo:web-lock-posture']),
    sourceCheck('package-retains-focused-web-lock-posture-audit', packageRelease, ['KERNEL-KIT-WEB-LOCK-POSTURE-CONTRACT-AUDIT']),
    check('manifest-audit-task-present', Boolean(task), { task: task?.id || null }),
    check('manifest-audit-task-release-non-browser', Boolean(task) && task.tiers?.includes('release') && task.lane !== 'browser', { tiers: task?.tiers || null, lane: task?.lane || null }),
    check('manifest-browser-task-inputs-include-web-lock-posture-sources', Boolean(browserTask) && browserTask.inputs?.includes('src/browserrt.mjs') && browserTask.inputs?.includes('demo/kernel-kit-demo-runner.mjs') && browserTask.inputs?.includes('tools/kernel_kit_web_lock_posture_contract_audit.mjs'), { task: browserTask?.id || null }),
    check('package-script-runs-web-lock-posture-audit', testKernelKit.includes('facility:kernel-kit-web-lock-posture-audit'), { script: testKernelKit }),
    check('impact-map-routes-web-lock-posture-to-browser-proof-and-audit', impactIds.has('facility:kernel-kit-web-lock-posture-audit') && impactIds.has('browser:kernel-kit-demo-proof'), { taskIds: Array.from(impactIds).filter((id) => String(id).includes('web-lock-posture') || id === 'browser:kernel-kit-demo-proof') }),
    check('surface-inventory-names-web-lock-posture', Boolean(surface) && surface.currentTaskIds?.includes('facility:kernel-kit-web-lock-posture-audit') && surface.currentTaskIds?.includes('browser:kernel-kit-demo-proof'), { surface: surface?.id || null })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-web-lock-posture-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    purpose: 'Release-tier static audit that Kernel Kit captures live browser Web Locks exclusive/shared coordination posture in the product path without claiming fairness, lifecycle recovery, cross-browser behavior, or production coordination.',
    checks,
    nonClaims: [
      'Static audit only; browser:kernel-kit-demo-proof supplies managed Chromium behavior.',
      'Web Locks posture is advisory coordination evidence, not a fairness, lifecycle recovery, cross-browser, or production coordination claim.',
      'No OPFS durability, quota, eviction, fsync, exactly-once, multi-tab lifecycle recovery, or product-market-fit claim.'
    ]
  });
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
await mkdir(dirname(out), { recursive: true });
await writeFile(out, JSON.stringify(report, null, 2) + '\n');
console.log(out);
assert.equal(report.status, 'passed', report.checks.filter((row) => row.status !== 'passed').map((row) => `${row.name}: ${(row.missing || []).join(',')}`).join('; '));
