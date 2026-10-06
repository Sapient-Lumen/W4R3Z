#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const TASK_ID = 'facility:storage-lane-quarantine-review-scope-contract-audit';
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-STORAGE-LANE-QUARANTINE-REVIEW-SCOPE-CONTRACT-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function missing(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(checks, name, passed, detail = {}) { checks.push({ name, status: passed ? 'passed' : 'failed', ...detail }); }

export async function runAudit() {
  const paths = [
    'src/storage-lane-scheduler.mjs','src/block-store-lane-adapter.mjs','src/types.d.ts',
    'tools/storage_lane_quarantine_review_scope_probe.mjs','tools/browser_opfs_web_lock_quarantine_review_scope_probe.mjs',
    'docs/40-validation/storage-lane-quarantine-review-scope-slice.md','docs/40-validation/browser-opfs-web-lock-quarantine-review-scope-slice.md','docs/40-validation/storage-lane-quarantine-review-scope-contract-audit-slice.md',
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
  check(checks, 'runtime-has-review-binding-hooks', missing(files['src/storage-lane-scheduler.mjs'], ['timedOutQuarantineFingerprint','quarantineFingerprint','createTimedOutOperationQuarantineReview','reviewFingerprint','timed-out-quarantine-clear-review-fingerprint-mismatch','timed-out-quarantine-clear-review-manifest-scope-override','timed-out-quarantine-clear-review-manifest-count-mismatch','timedOutOperationReviewManifestRejected','timedOutOperationReviewScopeRejected','storage-lane:timed-out-quarantine-review-created']).length === 0);
  check(checks, 'adapter-exposes-review-binding-hooks', missing(files['src/block-store-lane-adapter.mjs'], ['createTimedOutOperationQuarantineReview','reviewFingerprint','requireReviewFingerprint','reviewManifest','clearTimedOutOperationQuarantine(options = {})']).length === 0);
  check(checks, 'types-advertise-review-binding-hooks', missing(files['src/types.d.ts'], ['createTimedOutOperationQuarantineReview','reviewFingerprint','requireReviewFingerprint','reviewManifest','clearTimedOutOperationQuarantine(options?:']).length === 0);
  check(checks, 'release-proof-covers-stale-review-and-tampered-ledger', missing(files['tools/storage_lane_quarantine_review_scope_probe.mjs'], ['scheduler:storage-lane-quarantine-review-scope-proof','timed-out-quarantine-clear-review-fingerprint-required','timed-out-quarantine-clear-review-fingerprint-mismatch','timed-out-quarantine-clear-review-manifest-scope-override','timed-out-quarantine-clear-review-manifest-count-mismatch','scopedReviewManifest','scopeOverrideClear','tokenOverrideClear','fingerprintOverrideClear','countMismatchClear']).length === 0);
  check(checks, 'browser-proof-covers-opfs-review-binding', missing(files['tools/browser_opfs_web_lock_quarantine_review_scope_probe.mjs'], ['browser:opfs-web-lock-quarantine-review-scope-proof','tamperedLedger','missingFingerprintClear','staleFingerprintClear','scopedReviewManifest','scopeOverrideClear','tokenOverrideClear','fingerprintOverrideClear','countMismatchClear','reviewManifest','clearWithManifest']).length === 0);
  check(checks, 'docs-preserve-narrow-nonclaims', missing(files['docs/40-validation/browser-opfs-web-lock-quarantine-review-scope-slice.md'], ['Managed Chromium only','quarantineFingerprint','reviewFingerprint','scope override','token override','fingerprint override','count mismatch','not cryptographic attestation','not claim rollback']).length === 0);
  check(checks, 'manifest-tasks-present', taskIds.has('scheduler:storage-lane-quarantine-review-scope-proof') && taskIds.has('browser:opfs-web-lock-quarantine-review-scope-proof') && taskIds.has(TASK_ID));
  check(checks, 'impact-map-covers-current-tasks', impactTaskIds.has('scheduler:storage-lane-quarantine-review-scope-proof') && impactTaskIds.has('browser:opfs-web-lock-quarantine-review-scope-proof') && impactTaskIds.has(TASK_ID));
  check(checks, 'surface-inventory-covers-current-surfaces', surfaceIds.has('surface:storage-lane-quarantine-review-scope') && surfaceIds.has('surface:browser-opfs-web-lock-quarantine-review-scope') && surfaceIds.has('surface:storage-lane-quarantine-review-scope-contract-audit'));
  check(checks, 'first-read-docs-carry-current-and-sidecar-visible', ['README.md','START_HERE.md','AGENTS.md','CONTEXT-PACK.md'].every((p) => files[p].includes(REVISION) && files[p].includes('browser:opfs-web-lock-quarantine-clearance-replay-guard-proof')) && files['docs/40-validation/browser-opfs-web-lock-quarantine-review-scope-slice.md'].includes('browser:opfs-web-lock-quarantine-review-scope-proof'));
  check(checks, 'package-sidecar-scripts-present', files['package.json'].includes(REVISION) && files['package.json'].includes('quarantine-review-scope'));
  check(checks, 'makefile-current-office-not-historical-sidecar', files['Makefile'].includes('current_office_audit.mjs') && files['Makefile'].includes('replay:quarantine-clearance-receipt-provenance-binding'), { note: 'top-level Makefile no longer carries every historical sidecar wrapper' });
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: TASK_ID,
    status: checks.every((row) => row.status === 'passed') ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
    purpose: 'Contract audit for carried timeout-quarantine review scope: review manifests are authoritative for clearing scope/options, stale count manifests and scope overrides are rejected, and runtime hooks, proofs, docs, manifest, impact map, surface inventory, sidecar docs, and Makefile/package scripts remain aligned without forcing the sidecar to become the current office.',
    checks,
    nonClaims: ['Audit-only coverage; this audit does not launch Chromium or prove OPFS/Web Locks behavior by itself.', 'The quarantine fingerprint is not a cryptographic attestation or tamper-proof storage guarantee.']
  };
}
const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) { await mkdir(dirname(out), { recursive: true }); await writeFile(out, JSON.stringify(report, null, 2) + '\n'); console.log(out); }
else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
