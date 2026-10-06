#!/usr/bin/env node
// BrowserRT rev0033 retry-budget model contract audit.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-STORAGE-LANE-RETRY-BUDGET-MODEL-CONTRACT-AUDIT.json`);
const proofPath = `artifacts/validation/${PREFIX}-STORAGE-LANE-RETRY-BUDGET-MODEL-PROBE.json`;

async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await readFile(path, 'utf8')); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

// Keep the proof artifact fresh for fresh-extract audits without inheriting this audit's argv.
const proofRun = spawnSync('node', ['tools/storage_lane_retry_budget_model_probe.mjs', '--json', proofPath], {
  cwd: '.',
  encoding: 'utf8'
});
if (proofRun.status !== 0) {
  throw new Error(`retry-budget model proof failed before audit\nstdout:\n${proofRun.stdout}\nstderr:\n${proofRun.stderr}`);
}

const [manifest, impact, inventory, proof, runtime, ipc, types, frontier, sliceDoc, auditDoc, charter, office, registry] = await Promise.all([
  json('test/manifest.json'),
  json('test/impact-map.json'),
  json('test/surface-inventory.json'),
  json(proofPath),
  text('src/browserrt.mjs'),
  text('src/ipc.mjs'),
  text('src/types.d.ts'),
  text('docs/20-architecture/storage-lane-retry-budget-model-frontier.md'),
  text('docs/40-validation/storage-lane-retry-budget-model-slice.md'),
  text(`docs/40-validation/storage-lane-retry-budget-model-contract-audit-${REVISION}.md`).catch(() => text('docs/40-validation/storage-lane-retry-budget-model-contract-audit-rev0033.md')),
  text('docs/00-meta/non-claims-and-goals-charter.md'),
  text('docs/00-meta/future-session-office-manual.md'),
  json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json')
]);

const taskIds = new Set(manifest.tasks.map((task) => task.id));
const modelTask = manifest.tasks.find((task) => task.id === 'scheduler:storage-lane-retry-budget-model-proof');
const auditTask = manifest.tasks.find((task) => task.id === 'facility:storage-lane-retry-budget-model-contract-audit');
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryTaskIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const sourceTitles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));
const obs = proof.observations || {};

const checks = [
  check('revision-current', /^rev\d{4}$/.test(REVISION) && /^0\.0\.\d+$/.test(VERSION), { revision: REVISION, version: VERSION }),
  check('task-present', taskIds.has('scheduler:storage-lane-retry-budget-model-proof') && taskIds.has('facility:storage-lane-retry-budget-model-contract-audit')),
  check('task-release-tier-browser-light', modelTask?.tiers?.includes('release') && auditTask?.tiers?.includes('release') && modelTask?.lane !== 'browser' && auditTask?.lane !== 'browser', { modelLane: modelTask?.lane, auditLane: auditTask?.lane }),
  check('impact-map-covers-model-task', impactTaskIds.has('scheduler:storage-lane-retry-budget-model-proof') && impactTaskIds.has('facility:storage-lane-retry-budget-model-contract-audit')),
  check('surface-inventory-covers-model-task', inventoryTaskIds.has('scheduler:storage-lane-retry-budget-model-proof') && inventoryTaskIds.has('facility:storage-lane-retry-budget-model-contract-audit')),
  check('runtime-export-validator', includesAll(runtime, ['validateRetryBudgetAdmissionSnapshot', 'storageLaneRetryBudgetModelProof']).length === 0),
  check('ipc-export-validator', includesAll(ipc, ['validateRetryBudgetAdmissionSnapshot']).length === 0),
  check('types-export-validator', includesAll(types, ['validateRetryBudgetAdmissionSnapshot', 'RetryBudgetAdmissionController']).length === 0),
  check('docs-present-and-current', includesAll(frontier + sliceDoc + auditDoc, ['scheduler:storage-lane-retry-budget-model-proof', 'validateRetryBudgetAdmissionSnapshot', 'No OPFS retry-budget model proof']).length === 0),
  check('non-claim-surfaces-carry-boundary', includesAll(charter + office, ['No OPFS retry-budget model proof', 'No production retry-storm safety claim', 'No exhaustive model checking or formal verification claim']).length === 0),
  check('research-registry-carries-model-sources', ['fast-check model-based testing', 'FoundationDB Simulation and Testing', 'Jepsen safety testing', 'TLA+ finite-model humility'].every((title) => sourceTitles.has(title)), { requiredTitles: ['fast-check model-based testing', 'FoundationDB Simulation and Testing', 'Jepsen safety testing', 'TLA+ finite-model humility'] }),
  check('proof-artifact-current', proof.revision === REVISION && proof.status === 'passed' && proof.slice === 'scheduler:storage-lane-retry-budget-model-proof', { proofRevision: proof.revision, proofStatus: proof.status }),
  check('proof-observations-hold', ['realModelAgreementEveryStep', 'activeLimitRejectObserved', 'budgetExhaustRejectObserved', 'nonIdempotentRejectObserved', 'providerUnhealthyRejectObserved', 'criticalBypassObserved', 'primaryRefillObserved', 'finalAccountingEmpty', 'finalSnapshotsValidated'].every((key) => obs[key] === true), { observationsChecked: Object.keys(obs).length })
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  status: failed.length === 0 ? 'passed' : 'failed',
  generatedAt: new Date().toISOString(),
  slice: 'facility:storage-lane-retry-budget-model-contract-audit',
  purpose: 'Audit retry-budget model/history oracle coherence across source, docs, manifest, impact map, surface inventory, proof artifact, research registry, and future-session non-claim surfaces.',
  proofPath,
  passedCount: checks.length - failed.length,
  failedCount: failed.length,
  checks,
  nonClaims: [
    'This audit proves cube coherence only.',
    'This audit does not prove production retry-storm safety.',
    'This audit does not prove OPFS, browser, latency, throughput, SLO, or formal-verification behavior.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
assert.equal(report.status, 'passed', JSON.stringify(failed, null, 2));
