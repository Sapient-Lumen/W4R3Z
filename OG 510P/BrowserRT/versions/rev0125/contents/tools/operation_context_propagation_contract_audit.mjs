#!/usr/bin/env node
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const TASK_ID = 'facility:operation-context-propagation-contract-audit';
const DEFAULT_OUT = `artifacts/audit/REV${REVISION.slice(3)}-OPERATION-CONTEXT-PROPAGATION-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

export async function runAudit() {
  const started = performance.now();
  const checks = [];
  const check = (name, ok, detail = {}) => { checks.push({ name, ok: Boolean(ok), detail }); if (!ok) assert.fail(`${name}: ${JSON.stringify(detail)}`); };
  const files = {
    scheduler: await text('src/storage-lane-scheduler.mjs'),
    adapter: await text('src/block-store-lane-adapter.mjs'),
    guard: await text('src/opfs-web-lock-guarded-block-store.mjs'),
    types: await text('src/types.d.ts'),
    releaseProbe: await text('tools/storage_lane_operation_context_propagation_probe.mjs'),
    browserProbe: await text('tools/browser_opfs_web_lock_operation_context_propagation_probe.mjs'),
    releaseDoc: await text('docs/40-validation/storage-lane-operation-context-propagation-slice.md'),
    browserDoc: await text('docs/40-validation/browser-opfs-web-lock-operation-context-propagation-slice.md'),
    manifest: await text('test/manifest.json'),
    impact: await text('test/impact-map.json'),
    surfaces: await text('test/surface-inventory.json'),
    packageJson: await text('package.json'),
    makefile: await text('Makefile')
  };
  check('adapter-passes-executor-context-to-run', files.adapter.includes('const value = await run(context);'), { snippet: 'const value = await run(context);' });
  check('guard-forwards-options-to-provider-methods', missing(files.guard, [
    'this.store.put(value, fields, options)',
    'this.store.get(refOrDigest, options)',
    'this.store.has(refOrDigest, options)',
    'this.store.verify(refOrDigest, options)',
    'this.store.delete(refOrDigest, options)',
    'this.store.estimate(options)',
    'this.store.cleanupForTest(options)'
  ]).length === 0, { missing: missing(files.guard, ['this.store.put(value, fields, options)','this.store.get(refOrDigest, options)','this.store.has(refOrDigest, options)','this.store.verify(refOrDigest, options)','this.store.delete(refOrDigest, options)','this.store.estimate(options)','this.store.cleanupForTest(options)']) });
  check('release-proof-wired', missing(files.releaseProbe, ['scheduler:storage-lane-operation-context-propagation-proof', 'operationTimeoutMs reaches the provider', 'WebLockGuardedBlockStore']).length === 0);
  check('browser-proof-wired', missing(files.browserProbe, ['browser:opfs-web-lock-operation-context-propagation-proof', 'Managed Chromium proof', 'recordingCalls']).length === 0);
  check('docs-present-and-nonclaims', missing(files.releaseDoc + files.browserDoc, ['operationTimeoutMs', 'not provider cancellation', 'not durability', 'managed Chromium']).length === 0);
  const manifest = JSON.parse(files.manifest);
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  check('manifest-current-tasks-present', ['scheduler:storage-lane-operation-context-propagation-proof', 'browser:opfs-web-lock-operation-context-propagation-proof', TASK_ID].every((id) => taskIds.has(id)), { missing: ['scheduler:storage-lane-operation-context-propagation-proof', 'browser:opfs-web-lock-operation-context-propagation-proof', TASK_ID].filter((id) => !taskIds.has(id)) });
  for (const rel of ['package.json', 'Makefile', 'test/impact-map.json', 'test/surface-inventory.json']) {
    check(`${rel}-references-current-slice`, files[rel === 'package.json' ? 'packageJson' : rel === 'Makefile' ? 'makefile' : rel === 'test/impact-map.json' ? 'impact' : 'surfaces'].includes('operation-context-propagation'), {});
  }
  const pkg = JSON.parse(files.packageJson);
  const acceptedCurrentTasks = new Set([
    'browser:opfs-web-lock-operation-context-propagation-proof',
    'browser:opfs-web-lock-quarantine-ledger-roundtrip-proof',
    'browser:opfs-web-lock-quarantine-ledger-integrity-proof',
    'browser:opfs-web-lock-quarantine-ledger-persistence-integrity-proof',
    'browser:opfs-web-lock-quarantine-review-binding-proof',
    'browser:opfs-web-lock-quarantine-restore-backpressure-proof',
    'browser:opfs-web-lock-quarantine-restore-backpressure-binding-proof'
  ]);
  const acceptedCurrentAudits = new Set([
    TASK_ID,
    'facility:storage-lane-quarantine-ledger-contract-audit',
    'facility:storage-lane-quarantine-ledger-integrity-contract-audit',
    'facility:storage-lane-quarantine-ledger-persistence-integrity-contract-audit',
    'facility:storage-lane-quarantine-review-binding-contract-audit',
    'facility:storage-lane-quarantine-restore-backpressure-contract-audit',
    'facility:storage-lane-quarantine-restore-backpressure-binding-contract-audit'
  ]);
  check('package-current-or-carried-forward-office', pkg.revision === REVISION && pkg.version === VERSION && acceptedCurrentTasks.has(pkg.current_task) && acceptedCurrentAudits.has(pkg.current_audit), { revision: pkg.revision, version: pkg.version, current_task: pkg.current_task, current_audit: pkg.current_audit, carriedForwardAudit: pkg.current_audit !== TASK_ID });
  return { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-operation-context-propagation-contract-audit`, task_id: TASK_ID, status: 'passed', generatedAt: new Date().toISOString(), durationMs: Math.round(performance.now() - started), checks, purpose: 'Audit that storage-lane operation context propagation runtime fix, proofs, docs, manifest, impact map, surface inventory, and shortcuts stay wired while allowing a later quarantine-ledger slice to be the package current office.', nonClaims: ['Contract audit only; not browser execution, provider cancellation, durability, quota, eviction, throughput, or production-readiness evidence.'] };
}

const argv = process.argv.slice(2); const out = argValue(argv, '--json', DEFAULT_OUT);
try { const report = await runAudit(); if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); } else console.log(JSON.stringify(report, null, 2)); }
catch (error) { const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, audit_id: `${REVISION}-operation-context-propagation-contract-audit`, task_id: TASK_ID, status: 'failed', generatedAt: new Date().toISOString(), error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }, nonClaims: ['Failed contract audit is not silently skipped.'] }; if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.error(out); } console.error(`[operation_context_propagation_contract_audit] FAIL: ${error?.stack || error}`); process.exitCode = 1; }
