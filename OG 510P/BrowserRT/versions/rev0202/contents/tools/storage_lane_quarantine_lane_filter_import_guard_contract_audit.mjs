#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PFX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PFX}-STORAGE-LANE-QUARANTINE-LANE-FILTER-IMPORT-GUARD-CONTRACT-AUDIT.json`);
const CURRENT = 'browser:opfs-web-lock-quarantine-lane-filter-import-guard-proof';
const RELEASE = 'scheduler:storage-lane-quarantine-lane-filter-import-guard-proof';
const AUDIT = 'facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit';
const SURFACES = ['surface:storage-lane-quarantine-lane-filter-import-guard','surface:browser-opfs-web-lock-quarantine-lane-filter-import-guard','surface:storage-lane-quarantine-lane-filter-import-guard-contract-audit'];
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function miss(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(name, ok, detail = {}) { return { name, status: ok ? 'passed' : 'failed', ...detail }; }
const files = {
  scheduler: await text('src/storage-lane-scheduler.mjs'),
  adapter: await text('src/block-store-lane-adapter.mjs'),
  browserrt: await text('src/browserrt.mjs'),
  types: await text('src/types.d.ts'),
  releaseProof: await text('tools/storage_lane_quarantine_lane_filter_import_guard_probe.mjs'),
  browserProof: await text('tools/browser_opfs_web_lock_quarantine_lane_filter_import_guard_probe.mjs'),
  storageDoc: await text('docs/40-validation/storage-lane-quarantine-lane-filter-import-guard-slice.md'),
  browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-lane-filter-import-guard-slice.md'),
  auditDoc: await text('docs/40-validation/storage-lane-quarantine-lane-filter-import-guard-contract-audit-slice.md'),
  readme: await text('README.md'), start: await text('START_HERE.md'), agents: await text('AGENTS.md'), context: await text('CONTEXT-PACK.md'),
  package: await text('package.json'), makefile: await text('Makefile'), changelog: await text('CHANGELOG.md'),
  cubeMeta: await text('CUBE-META.json'), receipt: await text('REVISION-RECEIPT.json'), reentry: await text('REENTRY-CONTRACT.json'), status: await text('SURFACE-STATUS.json'), validation: await text('VALIDATION-INDEX.json')
};
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.run || []));
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
const runtime = files.scheduler + files.adapter + files.types;
const central = files.cubeMeta + files.receipt + files.reentry + files.status + files.validation;
const checks = [
  check('runtime-lane-filter-import-guard', miss(runtime, ['allowPartialImport','allowEmptyImport','filteredOutCount','quarantineLedgerLaneFilterRejected','quarantineLedgerPartialImportRejected','quarantineLedgerEmptyLaneFilterRejected','timed-out-quarantine-import-rejected-lane-filter-empty','timed-out-quarantine-import-rejected-lane-filter-partial','storage-lane:timed-out-quarantine-import-lane-filter-rejected']).length === 0),
  check('adapter-forwards-import-policy-options', miss(files.adapter, ['allowPartialImport: options.allowPartialImport === true','allowEmptyImport: options.allowEmptyImport === true']).length === 0),
  check('proofs', miss(files.releaseProof + files.browserProof, [RELEASE,CURRENT,'rejected-lane-filter-empty-import','rejected-lane-filter-partial-import','allowPartialImport','markUnhealthyForced','rejected-lane-unhealthy']).length === 0),
  check('docs', miss(files.storageDoc + files.browserDoc + files.auditDoc, ['lane-filtered import','wrong-lane','partial import','allowPartialImport','no provider cancellation']).length === 0),
  check('manifest', [RELEASE,AUDIT,CURRENT].every((id) => taskIds.has(id))),
  check('impact-map', [RELEASE,AUDIT,CURRENT].every((id) => impactIds.has(id))),
  check('surface-inventory', SURFACES.every((id) => surfaceIds.has(id))),
  check('first-read-docs-carried-anchor', [files.readme, files.start, files.agents, files.context].every((body) => body.includes(REVISION) && body.includes('Carry-forward linked seam for audits'))),
  check('central-currentness', miss(central, [CURRENT,AUDIT,'OPFS Web Lock Quarantine Lane Filter Import Guard Proof','surface:browser-opfs-web-lock-quarantine-lane-filter-import-guard']).length === 0),
  check('scripts', miss(files.package + files.makefile, ['storage_lane_quarantine_lane_filter_import_guard_probe.mjs','browser_opfs_web_lock_quarantine_lane_filter_import_guard_probe.mjs','storage_lane_quarantine_lane_filter_import_guard_contract_audit.mjs']).length === 0),
  check('changelog-current-head-carried-anchor', files.changelog.startsWith(`## ${REVISION} —`) && files.changelog.includes('Historical quarantine/recovery anchors'))
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: AUDIT, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(), purpose: 'facility:storage-lane-quarantine-lane-filter-import-guard-contract-audit keeps the lane-filtered timeout-quarantine import guard wired through runtime, proofs, docs, manifest, and currentness surfaces.', checks, nonClaims: ['Audit only; does not launch Chromium.', 'No cryptographic attestation, provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, cross-browser behavior, quota/eviction survival, or production readiness claim.'] };
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
