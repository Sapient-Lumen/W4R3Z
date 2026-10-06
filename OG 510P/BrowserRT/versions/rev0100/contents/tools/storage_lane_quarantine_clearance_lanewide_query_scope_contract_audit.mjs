#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PFX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PFX}-STORAGE-LANE-QUARANTINE-CLEARANCE-LANEWIDE-QUERY-SCOPE-CONTRACT-AUDIT.json`);
const CURRENT = 'browser:opfs-web-lock-quarantine-clearance-lanewide-query-scope-proof';
const RELEASE = 'scheduler:storage-lane-quarantine-clearance-lanewide-query-scope-proof';
const AUDIT = 'facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit';
const SURFACES = ['surface:storage-lane-quarantine-clearance-lanewide-query-scope','surface:browser-opfs-web-lock-quarantine-clearance-lanewide-query-scope','surface:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit'];
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function miss(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(name, ok, detail = {}) { return { name, status: ok ? 'passed' : 'failed', ...detail }; }
const files = {
  scheduler: await text('src/storage-lane-scheduler.mjs'),
  adapter: await text('src/block-store-lane-adapter.mjs'),
  browserrt: await text('src/browserrt.mjs'),
  types: await text('src/types.d.ts'),
  releaseProof: await text('tools/storage_lane_quarantine_clearance_lanewide_query_scope_probe.mjs'),
  browserProof: await text('tools/browser_opfs_web_lock_quarantine_clearance_lanewide_query_scope_probe.mjs'),
  storageDoc: await text('docs/40-validation/storage-lane-quarantine-clearance-lanewide-query-scope-slice.md'),
  browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-lanewide-query-scope-slice.md'),
  auditDoc: await text('docs/40-validation/storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit-slice.md'),
  readme: await text('README.md'), start: await text('START_HERE.md'), agents: await text('AGENTS.md'), context: await text('CONTEXT-PACK.md'),
  package: await text('package.json'), makefile: await text('Makefile'), changelog: await text('CHANGELOG.md')
};
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.run || []));
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
const runtime = files.scheduler + files.adapter + files.types;
const checks = [
  check('runtime-lanewide-query-scope', miss(runtime, ['lane-wide clearance receipts are still lane-scoped','laneFilter == null || row.lane === laneFilter','receipt.lane == null || !laneSet.has(receipt.lane)']).length === 0),
  check('proofs', miss(files.releaseProof + files.browserProof, [RELEASE,CURRENT,'maintenanceReceiptCount','storageReceiptCount','maintenance-import-must-not-be-suppressed','rejected-cleared-quarantine-replay']).length === 0),
  check('docs', miss(files.storageDoc + files.browserDoc + files.auditDoc, ['lane-wide','query','maintenance','storage','not provider cancellation']).length === 0),
  check('manifest', [RELEASE,AUDIT,CURRENT].every((id) => taskIds.has(id))),
  check('impact-map', [RELEASE,AUDIT,CURRENT].every((id) => impactIds.has(id))),
  check('surface-inventory', SURFACES.every((id) => surfaceIds.has(id))),
  check('first-read-docs', miss(files.readme + files.start + files.agents + files.context, [CURRENT,AUDIT,'lane-wide','query-scope','browser-light']).length === 0),
  check('scripts', miss(files.package + files.makefile, ['storage_lane_quarantine_clearance_lanewide_query_scope_probe.mjs','browser_opfs_web_lock_quarantine_clearance_lanewide_query_scope_probe.mjs','storage_lane_quarantine_clearance_lanewide_query_scope_contract_audit.mjs']).length === 0),
  check('changelog', files.changelog.startsWith(`## ${REVISION} —`) && miss(files.changelog, [CURRENT,AUDIT,'lane-wide','query']).length === 0)
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: AUDIT, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(), purpose: 'facility:storage-lane-quarantine-clearance-lanewide-query-scope-contract-audit keeps lane-wide clearance receipt query/replay scope wired to runtime, proofs, docs, and cube surfaces.', checks, nonClaims: ['Audit only; does not launch Chromium.', 'No provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, cross-browser behavior, quota/eviction survival, cryptographic attestation, or production readiness claim.'] };
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
