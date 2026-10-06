#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PFX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PFX}-STORAGE-LANE-QUARANTINE-CLEARANCE-REPLAY-GUARD-CONTRACT-AUDIT.json`);
const CURRENT = 'browser:opfs-web-lock-quarantine-clearance-replay-guard-proof';
const RELEASE = 'scheduler:storage-lane-quarantine-clearance-replay-guard-proof';
const AUDIT = 'facility:storage-lane-quarantine-clearance-replay-guard-contract-audit';
const SURFACES = ['surface:storage-lane-quarantine-clearance-replay-guard','surface:browser-opfs-web-lock-quarantine-clearance-replay-guard','surface:storage-lane-quarantine-clearance-replay-guard-contract-audit'];
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function miss(body, needles) { return needles.filter((needle) => !String(body).includes(needle)); }
function check(name, ok, detail = {}) { return { name, status: ok ? 'passed' : 'failed', ...detail }; }
const files = {
  scheduler: await text('src/storage-lane-scheduler.mjs'),
  adapter: await text('src/block-store-lane-adapter.mjs'),
  browserrt: await text('src/browserrt.mjs'),
  types: await text('src/types.d.ts'),
  releaseProof: await text('tools/storage_lane_quarantine_clearance_replay_guard_probe.mjs'),
  browserProof: await text('tools/browser_opfs_web_lock_quarantine_clearance_replay_guard_probe.mjs'),
  storageDoc: await text('docs/40-validation/storage-lane-quarantine-clearance-replay-guard-slice.md'),
  browserDoc: await text('docs/40-validation/browser-opfs-web-lock-quarantine-clearance-replay-guard-slice.md'),
  auditDoc: await text('docs/40-validation/storage-lane-quarantine-clearance-replay-guard-contract-audit-slice.md'),
  readme: await text('README.md'), start: await text('START_HERE.md'), agents: await text('AGENTS.md'), context: await text('CONTEXT-PACK.md'),
  package: await text('package.json'), makefile: await text('Makefile'), changelog: await text('CHANGELOG.md')
};
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || rule.run || []));
const surfaceIds = new Set((inventory.surfaces || []).map((surface) => surface.id));
const runtime = files.scheduler + files.adapter;
const checks = [
  check('runtime-hooks', miss(runtime, ['clearanceReceipt.v1','registerTimedOutOperationQuarantineClearanceReceipt','clearedTimedOutOperationQuarantineClearanceReceipts','timed-out-quarantine-import-rejected-cleared','rejected-cleared-quarantine-replay','quarantineLedgerReplayRejected']).length === 0),
  check('adapter-exports', miss(files.adapter + files.browserrt + files.types, ['createTimedOutOperationQuarantineClearanceReceipt','validateTimedOutOperationQuarantineClearanceReceipt','timedOutOperationQuarantineClearanceReceiptFingerprint','restoreTimedOutOperationQuarantineClearanceReceiptFromBlockStore']).length === 0),
  check('proofs', miss(files.releaseProof + files.browserProof, [RELEASE,CURRENT,'staleLedger','rejected-cleared-quarantine-replay','laneAfterReplay']).length === 0),
  check('docs', miss(files.storageDoc + files.browserDoc + files.auditDoc, ['clearance receipt','stale','replay','not provider cancellation','Managed Chromium','cross-browser']).length === 0),
  check('manifest', [RELEASE,AUDIT,CURRENT].every((id) => taskIds.has(id))),
  check('impact-map', [RELEASE,AUDIT,CURRENT].every((id) => impactIds.has(id))),
  check('surface-inventory', SURFACES.every((id) => surfaceIds.has(id))),
  check('first-read-docs-carried-anchor', [files.readme, files.start, files.agents, files.context].every((body) => body.includes(REVISION) && body.includes('Carry-forward linked seam for audits'))),
  check('manifest-command-wiring', miss(JSON.stringify(manifest), ['storage_lane_quarantine_clearance_replay_guard_probe.mjs','browser_opfs_web_lock_quarantine_clearance_replay_guard_probe.mjs','storage_lane_quarantine_clearance_replay_guard_contract_audit.mjs']).length === 0),
  check('changelog-current-head-carried-anchor', files.changelog.startsWith(`## ${REVISION} —`) && files.changelog.includes('Historical quarantine/recovery anchors'))
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, task_id: AUDIT, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(), purpose: 'facility:storage-lane-quarantine-clearance-replay-guard-contract-audit keeps the clearance receipt replay guard slice wired to runtime, proofs, docs, and cube surfaces.', checks, nonClaims: ['Audit only; does not launch Chromium.', 'No cancellation, rollback, no-mutation-on-timeout, OPFS durability, cross-browser behavior, quota/eviction survival, or production readiness claim.'] };
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
