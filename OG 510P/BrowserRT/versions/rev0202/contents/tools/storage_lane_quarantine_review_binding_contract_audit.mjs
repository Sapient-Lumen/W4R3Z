#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:storage-lane-quarantine-review-binding-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-STORAGE-LANE-QUARANTINE-REVIEW-BINDING-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(checks, name, passed, detail = {}) { checks.push({ name, status: passed ? 'passed' : 'failed', ...detail }); }

export async function runAudit() {
  const paths = [
    'src/storage-lane-scheduler.mjs','src/block-store-lane-adapter.mjs','src/types.d.ts',
    'tools/storage_lane_quarantine_review_binding_probe.mjs','tools/browser_opfs_web_lock_quarantine_review_binding_probe.mjs',
    'docs/40-validation/storage-lane-quarantine-review-binding-slice.md','docs/40-validation/browser-opfs-web-lock-quarantine-review-binding-slice.md','docs/40-validation/storage-lane-quarantine-review-binding-contract-audit-slice.md',
    'README.md','START_HERE.md','AGENTS.md','CONTEXT-PACK.md','package.json','Makefile'
  ];
  const files = Object.fromEntries(await Promise.all(paths.map(async (p) => [p, await text(p)])));
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const inventory = await json('test/surface-inventory.json');
  const checks = [];
  const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
  const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.run || []));
  const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
  check(checks, 'runtime-has-review-binding-hooks', missing(files['src/storage-lane-scheduler.mjs'], ['timedOutQuarantineFingerprint','quarantineFingerprint','createTimedOutOperationQuarantineReview','reviewFingerprint','timed-out-quarantine-clear-review-fingerprint-mismatch','storage-lane:timed-out-quarantine-review-created']).length === 0);
  check(checks, 'adapter-exposes-review-binding-hooks', missing(files['src/block-store-lane-adapter.mjs'], ['createTimedOutOperationQuarantineReview','reviewFingerprint','requireReviewFingerprint','reviewManifest']).length === 0);
  check(checks, 'types-advertise-review-binding-hooks', missing(files['src/types.d.ts'], ['createTimedOutOperationQuarantineReview','reviewFingerprint','requireReviewFingerprint','reviewManifest']).length === 0);
  check(checks, 'release-proof-covers-stale-review-and-tampered-ledger', missing(files['tools/storage_lane_quarantine_review_binding_probe.mjs'], ['scheduler:storage-lane-quarantine-review-binding-proof','timed-out-quarantine-clear-review-fingerprint-required','timed-out-quarantine-clear-review-fingerprint-mismatch','tamperedLedger','createTimedOutOperationQuarantineReview']).length === 0);
  check(checks, 'browser-proof-covers-opfs-review-binding', missing(files['tools/browser_opfs_web_lock_quarantine_review_binding_probe.mjs'], ['browser:opfs-web-lock-quarantine-review-binding-proof','tamperedLedger','missingFingerprintClear','staleFingerprintClear','reviewManifest','clearWithManifest']).length === 0);
  check(checks, 'docs-preserve-narrow-nonclaims', missing(files['docs/40-validation/browser-opfs-web-lock-quarantine-review-binding-slice.md'], ['Managed Chromium only','quarantineFingerprint','reviewFingerprint','not cryptographic attestation','not claim rollback']).length === 0);
  check(checks, 'manifest-tasks-present', taskIds.has('scheduler:storage-lane-quarantine-review-binding-proof') && taskIds.has('browser:opfs-web-lock-quarantine-review-binding-proof') && taskIds.has(TASK_ID));
  check(checks, 'impact-map-covers-current-tasks', impactTaskIds.has('scheduler:storage-lane-quarantine-review-binding-proof') && impactTaskIds.has('browser:opfs-web-lock-quarantine-review-binding-proof') && impactTaskIds.has(TASK_ID));
  check(checks, 'surface-inventory-covers-current-surfaces', surfaceIds.has('surface:storage-lane-quarantine-review-binding') && surfaceIds.has('surface:browser-opfs-web-lock-quarantine-review-binding') && surfaceIds.has('surface:storage-lane-quarantine-review-binding-contract-audit'));
  check(checks, 'first-read-docs-current', ['README.md','START_HERE.md','AGENTS.md','CONTEXT-PACK.md'].every((p) => files[p].includes('browser:opfs-web-lock-quarantine-review-binding-proof') && files[p].toLowerCase().includes('quarantine review binding')));
  check(checks, 'package-currentness', files['package.json'].includes(REVISION) && files['package.json'].includes('opfs-web-lock-quarantine-review-binding-proof'));
  check(checks, 'makefile-current-targets', missing(files['Makefile'], ['test-storage-lane-quarantine-review-binding','test-browser-opfs-web-lock-quarantine-review-binding','audit-storage-lane-quarantine-review-binding']).length === 0);
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID,
    status: checks.every((row) => row.status === 'passed') ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
    purpose: 'Contract audit for rev0076 timeout-quarantine review binding: runtime hooks, adapter/types, release proof, browser proof, docs, manifest, impact map, surface inventory, first-read currentness, and Makefile/package scripts remain aligned.',
    checks,
    nonClaims: ['Audit-only coverage; this audit does not launch Chromium or prove OPFS/Web Locks behavior by itself.', 'The quarantine fingerprint is not a cryptographic attestation or tamper-proof storage guarantee.']
  };
}
const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
