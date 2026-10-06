#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:storage-lane-unsettled-orphan-review-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-STORAGE-LANE-UNSETTLED-ORPHAN-REVIEW-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(checks, name, passed, detail = {}) { checks.push({ name, status: passed ? 'passed' : 'failed', ...detail }); }

export async function runAudit() {
  const paths = [
    'src/storage-lane-scheduler.mjs',
    'src/block-store-lane-adapter.mjs',
    'src/types.d.ts',
    'tools/storage_lane_unsettled_orphan_review_probe.mjs',
    'tools/browser_opfs_web_lock_unsettled_orphan_review_probe.mjs',
    'docs/40-validation/storage-lane-unsettled-orphan-review-slice.md',
    'docs/40-validation/browser-opfs-web-lock-unsettled-orphan-review-slice.md',
    'docs/40-validation/storage-lane-unsettled-orphan-review-contract-audit-slice.md',
    'README.md', 'START_HERE.md', 'AGENTS.md', 'CONTEXT-PACK.md', 'package.json'
  ];
  const files = Object.fromEntries(await Promise.all(paths.map(async (p) => [p, await text(p)])));
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
  check(checks, 'runtime-finalizes-unsettled-orphans', missing(files['src/storage-lane-scheduler.mjs'], [
    'finalizeUnsettledTimedOutOperations',
    'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED',
    'timed-out-quarantine-finalize-review-required',
    'timed-out-quarantine-finalize-review-fingerprint-mismatch',
    'storage-lane:timed-out-quarantine-orphans-finalized'
  ]).length === 0);
  check(checks, 'adapter-exposes-finalization', missing(files['src/block-store-lane-adapter.mjs'], [
    'finalizeUnsettledTimedOutOperations',
    'quarantineOrphanFinalizations',
    'requireReviewFingerprint'
  ]).length === 0);
  check(checks, 'types-expose-finalization', files['src/types.d.ts'].includes('finalizeUnsettledTimedOutOperations'));
  check(checks, 'release-proof-covers-orphan-path', missing(files['tools/storage_lane_unsettled_orphan_review_probe.mjs'], [
    'scheduler:storage-lane-unsettled-orphan-review-proof',
    'BRT_STORAGE_OPERATION_TIMEOUT',
    'timed-out-operation-still-unsettled',
    'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED',
    'timed-out-operation-late-failure'
  ]).length === 0);
  check(checks, 'browser-proof-covers-real-opfs-web-lock-path', missing(files['tools/browser_opfs_web_lock_unsettled_orphan_review_probe.mjs'], [
    'browser:opfs-web-lock-unsettled-orphan-review-proof',
    'opfsWebLockGuardedBlockStore',
    'BRT_STORAGE_OPERATION_TIMEOUT',
    'timed-out-operation-still-unsettled',
    'BRT_STORAGE_TIMED_OUT_OPERATION_ORPHANED',
    'coord:web-lock-acquired'
  ]).length === 0);
  check(checks, 'docs-preserve-narrow-nonclaims', missing(files['docs/40-validation/browser-opfs-web-lock-unsettled-orphan-review-slice.md'], [
    'Managed Chromium only',
    'not claim cross-browser',
    'no-mutation-on-timeout',
    'OPFS fsync durability',
    'production readiness'
  ]).length === 0);
  check(checks, 'audit-doc-wired', missing(files['docs/40-validation/storage-lane-unsettled-orphan-review-contract-audit-slice.md'], [TASK_ID, 'browser:opfs-web-lock-unsettled-orphan-review-proof']).length === 0);
  check(checks, 'manifest-tasks-present', taskIds.has('scheduler:storage-lane-unsettled-orphan-review-proof') && taskIds.has('browser:opfs-web-lock-unsettled-orphan-review-proof') && taskIds.has(TASK_ID));
  check(checks, 'impact-map-covers-tasks', impactTaskIds.has('scheduler:storage-lane-unsettled-orphan-review-proof') && impactTaskIds.has('browser:opfs-web-lock-unsettled-orphan-review-proof') && impactTaskIds.has(TASK_ID));
  check(checks, 'surface-inventory-covers-surfaces', surfaceIds.has('surface:storage-lane-unsettled-orphan-review') && surfaceIds.has('surface:browser-opfs-web-lock-unsettled-orphan-review') && surfaceIds.has('surface:storage-lane-unsettled-orphan-review-contract-audit'));
  check(checks, 'first-read-currentness', ['README.md','START_HERE.md','AGENTS.md','CONTEXT-PACK.md'].every((p) => files[p].includes('opfs-block-store-raw-composite-abort-signal') && files[p].includes(REVISION)) && files['docs/40-validation/browser-opfs-web-lock-unsettled-orphan-review-slice.md'].includes('browser:opfs-web-lock-unsettled-orphan-review-proof'));
  check(checks, 'package-currentness', files['package.json'].includes(REVISION) && files['package.json'].includes('opfs-web-lock-quarantine-clearance-replay-guard-proof'));
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID,
    status: checks.every((row) => row.status === 'passed') ? 'passed' : 'failed',
    generatedAt: new Date().toISOString(),
    purpose: 'Contract audit for the carried unsettled timeout orphan-review boundary: runtime finalization, release/browser proofs, docs, manifest, impact map, surface inventory, and first-read currentness.',
    checks,
    nonClaims: [
      'This audit does not launch a browser or prove OPFS/Web Locks behavior by itself; it verifies wiring for explicit proofs.',
      'This audit does not claim provider cancellation, rollback, no-mutation-on-timeout, durability, quota/eviction survival, or production readiness.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
