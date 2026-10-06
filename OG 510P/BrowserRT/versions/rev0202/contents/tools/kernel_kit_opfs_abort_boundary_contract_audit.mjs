#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PFX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PFX}-KERNEL-KIT-OPFS-ABORT-BOUNDARY-CONTRACT-AUDIT.json`;
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
  const [browserrt, types, browserRunner, pageRunner, browserProbe, demoContractAudit, manifest, impact, inventory] = await Promise.all([
    text('src/browserrt.mjs'),
    text('src/types.d.ts'),
    text('src/kernel-kit-demo-browser-runner.mjs'),
    text('demo/kernel-kit-demo-runner.mjs'),
    text('tools/browser_kernel_kit_demo_probe.mjs'),
    text('tools/kernel_kit_demo_contract_audit.mjs'),
    json('test/manifest.json'),
    json('test/impact-map.json'),
    json('test/surface-inventory.json')
  ]);
  const task = (manifest.tasks || []).find((row) => row.id === 'facility:kernel-kit-opfs-abort-boundary-audit');
  const browserTask = (manifest.tasks || []).find((row) => row.id === 'browser:kernel-kit-demo-proof');
  const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.tasks || []));
  const surface = (inventory.surfaces || []).find((row) => row.id === 'surface:kernel-kit-opfs-abort-boundary');
  const checks = [
    sourceCheck('runtime-exposes-kernel-kit-opfs-abort-boundary', browserrt, [
      'async kernelKitOpfsAbortBoundary',
      'BRT_OPFS_OPERATION_ABORTED',
      'BRT_OPFS_ABORT_SIGNAL_INVALID',
      'kernel-kit-demo:opfs-abort-boundary',
      'store.put(payload'
    ]),
    sourceCheck('types-expose-kernel-kit-opfs-abort-boundary', types, ['kernelKitOpfsAbortBoundary(config?: Record<string, unknown>)']),
    sourceCheck('browser-runner-carries-abort-boundary', browserRunner, ['kernelKitOpfsAbortBoundary', 'abortBoundary', 'opfsAbortBoundary', 'storageAbortBoundary']),
    sourceCheck('page-runner-renders-abort-boundary', pageRunner, ['kernelKitOpfsAbortBoundary', 'abortBoundary', 'data-opfs-abort-boundary-status', 'opfsAbortBoundary', 'storageAbortBoundary']),
    sourceCheck('browser-probe-enforces-abort-boundary', browserProbe, ['work.abortBoundary', 'storage:opfs-block-composite-abort-signal', 'storage:opfs-block-abort-signal-invalid', 'storage:opfs-block-abort', 'kernel-kit-demo:opfs-abort-boundary', 'opfsAbortBoundaryPresent']),
    sourceCheck('kernel-kit-demo-audit-no-longer-owns-current-office', demoContractAudit, ['receipt-current-office-carried-without-kernel-kit-ownership', 'Kernel Kit audit is carried forward even when another slice owns the current office.']),
    check('manifest-audit-task-present', Boolean(task), { task: task?.id || null }),
    check('manifest-audit-task-release-non-browser', Boolean(task) && task.tiers?.includes('release') && task.lane !== 'browser', { tiers: task?.tiers || null, lane: task?.lane || null }),
    check('manifest-browser-task-inputs-include-abort-boundary-runtime', Boolean(browserTask) && browserTask.inputs?.includes('src/opfs-block-store.mjs') && browserTask.inputs?.includes('src/browserrt.mjs'), { task: browserTask?.id || null }),
    check('impact-map-routes-abort-boundary-to-browser-proof-and-audit', impactIds.has('facility:kernel-kit-opfs-abort-boundary-audit') && impactIds.has('browser:kernel-kit-demo-proof'), { taskIds: Array.from(impactIds).filter((id) => String(id).includes('kernel-kit-opfs') || id === 'browser:kernel-kit-demo-proof') }),
    check('surface-inventory-names-abort-boundary', Boolean(surface) && surface.currentTaskIds?.includes('facility:kernel-kit-opfs-abort-boundary-audit') && surface.currentTaskIds?.includes('browser:kernel-kit-demo-proof'), { surface: surface?.id || null })
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return Object.freeze({
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    audit_id: `${REVISION}-kernel-kit-opfs-abort-boundary-contract-audit`,
    status: failed.length === 0 ? 'passed' : 'failed',
    generatedAt: new Date().toISOString(),
    purpose: 'Static contract audit that the product-facing Kernel Kit browser/page path carries the current raw OPFS signal/abortSignal abort non-mutation boundary and that the stale Kernel Kit audit no longer claims global current-office ownership.',
    checks,
    nonClaims: [
      'Static audit only; run browser:kernel-kit-demo-proof for managed Chromium behavior.',
      'This audit does not prove OPFS durability, quota, eviction, crash recovery, browser restart, multi-tab coordination, or cross-browser conformance.',
      'Abort remains cooperative and is only checked at BrowserRT-controlled checkpoints.'
    ]
  });
}

const argv = process.argv.slice(2);
const out = argValue(argv, '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
assert.equal(report.status, 'passed');
