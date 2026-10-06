#!/usr/bin/env node
// BrowserRT rev0035 storage-lane admission-history contract audit.
// Coherence audit only: no OPFS/browser, production overload-governance, throughput, SLO, or formal verification claim.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-STORAGE-LANE-ADMISSION-HISTORY-CONTRACT-AUDIT.json`);
const proofPath = `artifacts/validation/${PREFIX}-STORAGE-LANE-ADMISSION-HISTORY-PROBE.json`;

async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await readFile(path, 'utf8')); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

const proofRun = spawnSync(process.execPath, ['tools/storage_lane_admission_history_probe.mjs', '--json', proofPath], { cwd: '.', encoding: 'utf8' });
if (proofRun.status !== 0) {
  throw new Error(`storage-lane admission-history proof failed before audit\nstdout:\n${proofRun.stdout}\nstderr:\n${proofRun.stderr}`);
}

const [manifest, impact, inventory, proof, source, runtime, ipc, types, frontier, sliceDoc, auditDoc, charter, office, registry] = await Promise.all([
  json('test/manifest.json'),
  json('test/impact-map.json'),
  json('test/surface-inventory.json'),
  json(proofPath),
  text('src/storage-lane-admission-history.mjs'),
  text('src/browserrt.mjs'),
  text('src/ipc.mjs'),
  text('src/types.d.ts'),
  text('docs/20-architecture/storage-lane-admission-history-frontier.md'),
  text('docs/40-validation/storage-lane-admission-history-slice.md'),
  text(`docs/40-validation/storage-lane-admission-history-contract-audit-${REVISION}.md`),
  text('docs/00-meta/non-claims-and-goals-charter.md'),
  text('docs/00-meta/future-session-office-manual.md'),
  json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json')
]);
const taskIds = new Set(manifest.tasks.map((task) => task.id));
const proofTask = manifest.tasks.find((task) => task.id === 'scheduler:storage-lane-admission-history-proof');
const auditTask = manifest.tasks.find((task) => task.id === 'facility:storage-lane-admission-history-contract-audit');
const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const titles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));
const obs = proof.observations || {};
const requiredObs = ['successUnderAdmission', 'transientRetryUnderAdmission', 'watermarkRejectionNoMutation', 'criticalBypassUnderCongestion', 'providerHealthRejectionNoMutation', 'providerHealthRecoveryAdmits', 'hardLimitRejectionNoMutation', 'snapshotsValidate', 'finalLeaseAccountingEmpty', 'bootReportRecordsStorageLaneAdmissionHistoryProof', 'traceHasRequiredEvents'];
const checks = [
  check('proof-ran-in-audit', proofRun.status === 0),
  check('proof-current-passed', proof.revision === REVISION && proof.status === 'passed' && proof.slice === 'scheduler:storage-lane-admission-history-proof', { proofRevision: proof.revision, proofSlice: proof.slice, proofStatus: proof.status }),
  check('proof-observations-hold', requiredObs.every((key) => obs[key] === true), { missingTrue: requiredObs.filter((key) => obs[key] !== true), aggregate: proof.aggregate }),
  check('tasks-present-release-browser-light', taskIds.has('scheduler:storage-lane-admission-history-proof') && taskIds.has('facility:storage-lane-admission-history-contract-audit') && proofTask?.tiers?.includes('release') && auditTask?.tiers?.includes('release') && proofTask?.lane !== 'browser' && auditTask?.lane !== 'browser', { proofLane: proofTask?.lane, auditLane: auditTask?.lane }),
  check('task-outputs-current-prefix', proofTask?.outputs?.some((out) => out.includes(PREFIX)) && auditTask?.outputs?.some((out) => out.includes(PREFIX)), { prefix: PREFIX }),
  check('impact-map-covers-admission-history', impactIds.has('scheduler:storage-lane-admission-history-proof') && impactIds.has('facility:storage-lane-admission-history-contract-audit')),
  check('surface-inventory-covers-admission-history', inventoryIds.has('scheduler:storage-lane-admission-history-proof') && inventoryIds.has('facility:storage-lane-admission-history-contract-audit')),
  check('source-contract-present', missing(source, ['class StorageLaneAdmissionHistoryRunner', 'validateStorageLaneAdmissionHistorySnapshot', 'tryAdmit', 'resilienceRunner.runMailboxEnqueue', 'No OPFS, browser Worker']).length === 0),
  check('runtime-ipc-types-export-admission-history', missing(runtime + ipc + types, ['StorageLaneAdmissionHistoryRunner', 'createStorageLaneAdmissionHistoryRunner', 'validateStorageLaneAdmissionHistorySnapshot', 'storageLaneAdmissionHistoryProof']).length === 0),
  check('docs-present-current-and-legible', missing(frontier + sliceDoc + auditDoc, [REVISION, 'scheduler:storage-lane-admission-history-proof', 'StorageLaneAdmissionHistoryRunner', 'No OPFS storage-lane admission-history proof']).length === 0),
  check('future-session-nonclaims-present', missing(charter + office, ['No OPFS storage-lane admission-history proof', 'No browser Worker storage-lane admission-history proof', 'No production overload-governance']).length === 0),
  check('research-registry-covers-admission-overload-sources', ['Envoy overload manager protects against resource overload', 'Kubernetes API Priority and Fairness queueing and rejection', 'Azure Bulkhead pattern isolates resource pools', 'Reactive Streams non-blocking backpressure'].every((title) => titles.has(title)))
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
  slice: 'facility:storage-lane-admission-history-contract-audit',
  purpose: 'Audit storage-lane admission-history coherence across source, runtime exports, manifest, impact map, inventory, proof artifact, docs, research registry, and future-session non-claims.',
  proofPath,
  passedCount: checks.length - failed.length,
  failedCount: failed.length,
  checks,
  nonClaims: [
    'This audit proves cube coherence only.',
    'This audit does not prove OPFS or browser Worker storage-lane admission behavior.',
    'This audit does not prove production admission-control, overload-governance, throughput, SLOs, exactly-once delivery, or formal verification.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
assert.equal(report.status, 'passed', JSON.stringify(failed, null, 2));
