#!/usr/bin/env node
// BrowserRT rev0039 storage-lane overload-governance contract audit.
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-STORAGE-LANE-OVERLOAD-GOVERNANCE-CONTRACT-AUDIT.json`);
const proofPath = `artifacts/validation/${PREFIX}-STORAGE-LANE-OVERLOAD-GOVERNANCE-PROBE.json`;

async function readJson(path) { return JSON.parse(await readFile(path, 'utf8')); }
async function readText(path) { return await readTextWithRevisionFallback(path); }
function runProof() {
  const result = spawnSync(process.execPath, ['tools/storage_lane_overload_governance_probe.mjs', '--json', proofPath], { cwd: process.cwd(), encoding: 'utf8' });
  if (result.status !== 0) {
    console.error(result.stdout);
    console.error(result.stderr);
    throw new Error(`proof refresh failed with status ${result.status}`);
  }
}
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

runProof();
const [proof, manifest, inventory, impact, receipt, context, charter, frontier, slice] = await Promise.all([
  readJson(proofPath),
  readJson('test/manifest.json'),
  readJson('test/surface-inventory.json'),
  readJson('test/impact-map.json'),
  readJson('REVISION-RECEIPT.json'),
  readText('CONTEXT-PACK.md'),
  readText('docs/00-meta/non-claims-and-goals-charter.md'),
  readText('docs/20-architecture/storage-lane-overload-governance-model-frontier.md'),
  readText('docs/40-validation/storage-lane-overload-governance-model-slice.md')
]);
const taskIds = new Set((manifest.tasks || []).map((task) => task.id));
const task = (manifest.tasks || []).find((row) => row.id === 'scheduler:storage-lane-overload-governance-model-proof');
const auditTask = (manifest.tasks || []).find((row) => row.id === 'facility:storage-lane-overload-governance-contract-audit');
const inventoryTaskIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const nonClaimNeedles = [
  'No OPFS storage-lane overload-governance model proof',
  'No browser Worker storage-lane overload-governance model proof',
  'No production overload-governance',
  'No WebGPU proof'
];
const checks = [
  check('proof-passed-current-revision', proof.revision === REVISION && proof.status === 'passed', { proofRevision: proof.revision, proofStatus: proof.status }),
  check('targeted-and-generated-histories', proof.observations?.targetedScenarioCount >= 8 && proof.observations?.generatedScenarioCount >= 10, { observations: proof.observations }),
  check('governance-outcomes-covered', ['retrySuccessObserved','retryBudgetExhaustionObserved','nonIdempotentRetryRejectObserved','breakerBulkheadRejectObserved','breakerOpenRejectObserved','watermarkRejectObserved','providerHealthRejectObserved','hardLimitRejectObserved','criticalBypassObserved'].every((key) => proof.observations?.[key] === true), { observations: proof.observations }),
  check('rejection-no-mutation-and-leases', proof.observations?.noProviderMutationOnRejectedFinals === true && proof.observations?.admissionLeasesReleased === true, { aggregate: proof.aggregate }),
  check('manifest-tasks-present', taskIds.has('scheduler:storage-lane-overload-governance-model-proof') && taskIds.has('facility:storage-lane-overload-governance-contract-audit')),
  check('release-tier-browser-light', task?.tiers?.includes('release') && auditTask?.tiers?.includes('release') && task?.lane !== 'browser' && auditTask?.lane !== 'browser', { taskLane: task?.lane, auditLane: auditTask?.lane }),
  check('impact-and-inventory-cover', impactTaskIds.has('scheduler:storage-lane-overload-governance-model-proof') && inventoryTaskIds.has('scheduler:storage-lane-overload-governance-model-proof')),
  check('docs-name-current-runtime-noun', frontier.includes('StorageLaneOverloadGovernanceModelOracle') && slice.includes('scheduler:storage-lane-overload-governance-model-proof')),
  check('non-claims-legible', nonClaimNeedles.every((needle) => receipt.non_claims?.join('\n').includes(needle) && context.includes(needle) && charter.includes(needle)), { nonClaimNeedles })
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
  slice: 'facility:storage-lane-overload-governance-contract-audit',
  purpose: 'Audit that rev0039 overload-governance proof, manifest, impact/inventory, docs, and non-claims cohere for future sessions.',
  proofPath,
  checks,
  nonClaims: [
    'This audit does not prove production overload governance.',
    'This audit does not prove OPFS/browser behavior, durability, real timers, throughput, latency, or cross-browser conformance.',
    'This audit verifies cube coherence and proof-surface legibility for a fake-provider model slice.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (failed.length) process.exitCode = 1;
