#!/usr/bin/env node
// BrowserRT rev0027 provider-integration contract audit.
// Coherence guard only; no OPFS, durability, browser, throughput, or production scheduler claim.

import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const prefix = `REV${REVISION.slice(3)}`;
const proofPath = `artifacts/validation/${prefix}-STORAGE-LANE-PROVIDER-PROBE.json`;
const outArg = process.argv.indexOf('--json');
const outPath = outArg >= 0 ? process.argv[outArg + 1] : `artifacts/audit/${prefix}-PROVIDER-INTEGRATION-CONTRACT-AUDIT.json`;

async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
function row(path, check, passed, extra = {}) { return { path, check, status: passed ? 'passed' : 'failed', ...extra }; }
function has(body, needle) { return body.includes(needle); }

if (!existsSync(proofPath)) {
  const result = spawnSync('node', ['tools/storage_lane_provider_probe.mjs', '--json', proofPath], { stdio: 'inherit' });
  if (result.status !== 0) throw new Error('failed to regenerate storage-lane provider proof before audit');
}

const proof = await json(proofPath);
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const validation = await json('VALIDATION-INDEX.json');
const receipt = await json('REVISION-RECEIPT.json');
const registry = await json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const runtime = await text('src/browserrt.mjs');
const ipc = await text('src/ipc.mjs');
const types = await text('src/types.d.ts');
const source = await text('src/storage-lane-scheduler.mjs');
const probe = await text('tools/storage_lane_provider_probe.mjs');
const frontier = await text('docs/20-architecture/storage-lane-provider-integration-frontier.md');
const slice = await text('docs/40-validation/storage-lane-provider-slice.md');
const auditDoc = await text(`docs/40-validation/provider-integration-contract-audit-${REVISION}.md`);
const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');
const office = await text('docs/00-meta/future-session-office-manual.md');
const tasks = new Set((manifest.tasks || []).map((task) => task.id));
const mapped = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const surfaceRefs = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const titles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));

const requiredObservations = [
  'storageLaneExecutorCreated',
  'runtimeFactoryIntegration',
  'capacityBlockObserved',
  'healthRejectNoMutation',
  'enqueuesExecutedViaScheduler',
  'dequeueAndAckExecutedViaScheduler',
  'dependencyDeferralObserved',
  'maintenanceLaneCompactionObserved',
  'checkpointExecutedViaStorageLane',
  'snapshotExecutedViaStorageLane',
  'dryRunDidNotDelete',
  'realCompactDeletedAckedOnly',
  'pendingAndReadyProtected',
  'providerBlocksRemainForLiveMessages',
  'providerFailureMarksStorageUnhealthy',
  'unhealthyLaneRejectsWithoutMutation',
  'providerRecoveryRestoresScheduling',
  'finalDeliveriesObserved',
  'finalCompactionReclaimsRemainingBlocks',
  'schedulerSnapshotValid',
  'finalAccountingEmpty',
  'providerEmptyAfterFinalCompaction',
  'runtimeFactoryStorageLaneProofFlag',
  'bootReportRecordsStorageLaneProviderProof',
  'traceHasRequiredEvents'
];
const requiredTitles = [
  'libuv thread pool work scheduling',
  'libuv file system operations',
  'Tokio spawn_blocking',
  'Ray Core Objects',
  'Ray Core Scheduling',
  'Dask Scheduling Policies',
  'Dask Work Stealing'
];
const requiredTraceKinds = [
  'storage-lane:schedule',
  'storage-lane:dispatch',
  'storage-lane:complete',
  'storage-lane:error',
  'storage-lane:provider-unhealthy',
  'storage-lane:provider-healthy',
  'crosslane:defer-dependency',
  'crosslane:lane-at-capacity',
  'mailbox:persisted-compact',
  'storage:block-delete'
];

const findings = [];
findings.push(row('src/storage-lane-scheduler.mjs', 'canonical storage-lane executor source exists', has(source, 'class StorageLaneExecutor') && has(source, 'SUPPORTED_OPS')));
findings.push(row('src/storage-lane-scheduler.mjs', 'executor emits namespaced storage-lane trace events', requiredTraceKinds.slice(0, 6).every((kind) => has(source, kind))));
findings.push(row('src/storage-lane-scheduler.mjs', 'executor prevents trace kind shadowing by operation kind', has(source, 'opKind') && has(source, "delete detail.kind")));
findings.push(row('src/storage-lane-scheduler.mjs', 'executor can drive persisted mailbox ops', has(source, "op === 'enqueue'") && has(source, "op === 'compact'") && has(source, "op === 'checkpoint'")));
findings.push(row('src/storage-lane-scheduler.mjs', 'provider error can mark lane unhealthy only for storage errors', has(source, 'BRT_STORAGE') && has(source, 'markLaneUnhealthy')));
findings.push(row('src/storage-lane-coordinator.mjs', 'obsolete coordinator fork absent until an earned coordinator slice exists', !existsSync('src/storage-lane-coordinator.mjs')));
findings.push(row('src/storage-lane-provider.mjs', 'obsolete duplicate provider file absent', !existsSync('src/storage-lane-provider.mjs')));
findings.push(row('src/browserrt.mjs', 'runtime boot exposes storageLaneProviderProof', has(runtime, 'storageLaneProviderProof') && has(runtime, 'storageLaneExecutor')));
findings.push(row('src/browserrt.mjs', 'runtime exports storage-lane executor', has(runtime, 'StorageLaneExecutor') && has(runtime, 'STORAGE_LANE_EXECUTOR_SUPPORTED_OPS') && has(runtime, 'createStorageLaneExecutor')));
findings.push(row('src/ipc.mjs', 'compat surface exports storage-lane executor', has(ipc, 'createStorageLaneExecutor')));
findings.push(row('src/types.d.ts', 'type surface exposes storage lane submit/execute API', has(types, 'StorageLaneExecutor') && has(types, 'submit(op:') && has(types, 'executeNext')));
findings.push(row('tools/storage_lane_provider_probe.mjs', 'probe asserts provider-driven scheduler observations', requiredObservations.every((key) => has(probe, key))));
findings.push(row(proofPath, 'proof artifact current and passed', proof.revision === REVISION && proof.status === 'passed'));
for (const key of requiredObservations) findings.push(row(proofPath, `observation ${key}`, proof.observations?.[key] === true));
for (const kind of requiredTraceKinds) findings.push(row(proofPath, `trace kind ${kind}`, (proof.traceKinds || []).includes(kind)));
findings.push(row('test/manifest.json', 'manifest includes provider proof task', tasks.has('scheduler:storage-lane-provider-proof')));
findings.push(row('test/manifest.json', 'manifest includes provider audit task', tasks.has('facility:provider-integration-contract-audit')));
findings.push(row('test/impact-map.json', 'impact map covers provider proof', mapped.has('scheduler:storage-lane-provider-proof')));
findings.push(row('test/impact-map.json', 'impact map covers provider audit', mapped.has('facility:provider-integration-contract-audit')));
findings.push(row('test/surface-inventory.json', 'surface inventory covers provider proof', surfaceRefs.has('scheduler:storage-lane-provider-proof')));
findings.push(row('VALIDATION-INDEX.json', 'validation index names provider artifact', JSON.stringify(validation).includes(`${prefix}-STORAGE-LANE-PROVIDER-PROBE.json`)));
findings.push(row('REVISION-RECEIPT.json', 'receipt carries provider non-claims', JSON.stringify(receipt.non_claims || receipt.important_non_claims || []).includes('No OPFS storage-lane provider proof.')));
findings.push(row('docs/20-architecture/storage-lane-provider-integration-frontier.md', 'frontier states provider integration boundary', has(frontier, 'provider-integrated storage-lane scheduling') && has(frontier, 'No OPFS storage-lane provider proof')));
findings.push(row('docs/40-validation/storage-lane-provider-slice.md', 'slice names manifest id and artifact', has(slice, 'scheduler:storage-lane-provider-proof') && has(slice, `${prefix}-STORAGE-LANE-PROVIDER-PROBE.json`)));
findings.push(row(`docs/40-validation/provider-integration-contract-audit-${REVISION}.md`, 'audit doc names facility id', has(auditDoc, 'facility:provider-integration-contract-audit')));
findings.push(row('docs/00-meta/non-claims-and-goals-charter.md', 'charter carries rev0027 non-claims', has(charter, 'Rev0027 storage-lane provider integration amendment') && has(charter, 'No OPFS storage-lane provider proof')));
findings.push(row('docs/00-meta/future-session-office-manual.md', 'office manual carries rev0027 handoff', has(office, 'Rev0027 provider-integration amendment') && has(office, 'scheduler:storage-lane-provider-proof')));
for (const title of requiredTitles) findings.push(row('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json', `registry includes ${title}`, titles.has(title)));
findings.push(row('test/manifest.json', 'release remains browser-light', (manifest.tasks || []).filter((task) => task.tiers.includes('release') && task.lane === 'browser').length === 0));

const failed = findings.filter((finding) => finding.status !== 'passed');
for (const finding of failed) assert.equal(finding.status, 'passed', `${finding.path}: ${finding.check}`);
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  slice: 'facility:provider-integration-contract-audit',
  status: 'passed',
  generatedAt: new Date().toISOString(),
  purpose: 'Coherence audit for the storage-lane provider proof: canonical source shape, runtime exports, manifest/impact/inventory/docs/registry coverage, proof observations, trace-kind hygiene, stale duplicate removal, and non-claim boundaries.',
  proofPath,
  findingCount: findings.length,
  failedCount: 0,
  findings,
  nonClaimsChecked: [
    'No OPFS storage-lane provider proof.',
    'No browser Worker storage-lane provider proof.',
    'No fsync, flush, quota, eviction, or durability claim.',
    'No production storage scheduler claim.',
    'No throughput or latency claim.',
    'No cross-browser conformance claim.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ status: report.status, slice: report.slice, findingCount: report.findingCount }, null, 2));
