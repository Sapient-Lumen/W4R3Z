#!/usr/bin/env node
// BrowserRT rev0031 storage-lane retry-budget/admission contract audit.
// Audit only; no OPFS, browser, retry-storm safety, wall-clock, SLO, or production overload-governance claim.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-STORAGE-LANE-RETRY-BUDGET-CONTRACT-AUDIT.json`);
const artifactPath = `artifacts/validation/${PREFIX}-STORAGE-LANE-RETRY-BUDGET-PROBE.json`;
async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function hasAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function runProof() {
  const result = spawnSync(process.execPath, ['tools/storage_lane_retry_budget_probe.mjs', '--json', artifactPath], { cwd: '.', encoding: 'utf8' });
  return { ok: result.status === 0, status: result.status, stdout: result.stdout, stderr: result.stderr };
}

const proofRun = runProof();
let artifact = null;
try { artifact = await json(artifactPath); } catch {}
const budgetSource = await text('src/retry-budget-admission.mjs');
const retrySource = await text('src/storage-lane-retry.mjs');
const runtime = await text('src/browserrt.mjs');
const ipc = await text('src/ipc.mjs');
const types = await text('src/types.d.ts');
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const registry = await json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');
const office = await text('docs/00-meta/future-session-office-manual.md');
const frontier = await text('docs/20-architecture/storage-lane-retry-budget-frontier.md');
const slice = await text('docs/40-validation/storage-lane-retry-budget-slice.md');
const auditDoc = await text(`docs/40-validation/storage-lane-retry-budget-contract-audit-${REVISION}.md`).catch(() => text('docs/40-validation/storage-lane-retry-budget-contract-audit-rev0033.md'));
const manifestTask = manifest.tasks.find((task) => task.id === 'scheduler:storage-lane-retry-budget-proof');
const auditTask = manifest.tasks.find((task) => task.id === 'facility:storage-lane-retry-budget-contract-audit');
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryTaskIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const titles = registry.families.flatMap((family) => family.sources || []).map((source) => source.title);
const observations = artifact?.observations || {};
const requiredObservationKeys = [
  'retryBudgetControllerCreated',
  'storageLaneRetryControllerIntegratesBudget',
  'retryCreditConsumedAndReleased',
  'exhaustedBudgetRejectsRetryWithoutSecondProviderMutation',
  'nonIdempotentRetryRejectedByGate',
  'activeRetryLimitRejectsSecondRetry',
  'providerUnhealthyRejectsRetry',
  'primaryObservationRefillsCredits',
  'criticalBypassUnderCreditExhaustion',
  'traceHasRequiredEvents'
];
const checks = [
  check('proof-ran-in-audit', proofRun.ok, { exitStatus: proofRun.status, stderr: proofRun.stderr.slice(0, 1000) }),
  check('artifact-current-passed', artifact?.revision === REVISION && artifact?.status === 'passed', { artifactRevision: artifact?.revision, artifactStatus: artifact?.status }),
  check('required-observations-true', requiredObservationKeys.every((key) => observations[key] === true), { failed: requiredObservationKeys.filter((key) => observations[key] !== true) }),
  check('budget-source-contract-needles-present', hasAll(budgetSource, ['class RetryBudgetAdmissionController','tryAcquireRetry','observePrimary','releaseRetry','retry-budget:reject','retry-budget:acquire','No OPFS, browser']).length === 0, { missing: hasAll(budgetSource, ['class RetryBudgetAdmissionController','tryAcquireRetry','observePrimary','releaseRetry','retry-budget:reject','retry-budget:acquire','No OPFS, browser']) }),
  check('retry-source-integrates-budget', hasAll(retrySource, ['retryBudget','tryAcquireRetry','releaseRetry','storage-retry:retry-budget-gate','retryBudgetRejected']).length === 0, { missing: hasAll(retrySource, ['retryBudget','tryAcquireRetry','releaseRetry','storage-retry:retry-budget-gate','retryBudgetRejected']) }),
  check('runtime-exports-present', ['RetryBudgetAdmissionController','createRetryBudgetAdmissionController','storageLaneRetryBudgetProof','retryBudgetAdmissionController'].every((needle) => runtime.includes(needle)), {}),
  check('ipc-and-types-present', ipc.includes('RetryBudgetAdmissionController') && types.includes('RetryBudgetAdmissionController') && types.includes('retryBudgetAdmissionController'), {}),
  check('manifest-task-present', Boolean(manifestTask) && manifestTask.outputs.includes(artifactPath) && manifestTask.tiers.includes('release'), { manifestTask: manifestTask?.id ?? null }),
  check('audit-task-present', Boolean(auditTask) && auditTask.outputs.includes(outPath), { auditTask: auditTask?.id ?? null }),
  check('impact-map-covers-budget-tasks', impactTaskIds.has('scheduler:storage-lane-retry-budget-proof') && impactTaskIds.has('facility:storage-lane-retry-budget-contract-audit'), {}),
  check('surface-inventory-covers-budget-tasks', inventoryTaskIds.has('scheduler:storage-lane-retry-budget-proof') && inventoryTaskIds.has('facility:storage-lane-retry-budget-contract-audit'), {}),
  check('research-registry-covers-budget-sources', ['Google SRE cascading failures','Google SRE handling overload and client-side throttling','Envoy circuit breakers and retry budget','Envoy transient failures and outlier detection','Kubernetes API Priority and Fairness','Resilience4j retry circuit breaker bulkhead rate limiter'].every((title) => titles.includes(title)), { missing: ['Google SRE cascading failures','Google SRE handling overload and client-side throttling','Envoy circuit breakers and retry budget','Envoy transient failures and outlier detection','Kubernetes API Priority and Fairness','Resilience4j retry circuit breaker bulkhead rate limiter'].filter((title) => !titles.includes(title)) }),
  check('non-claims-handoff-present', charter.includes('No OPFS storage-lane retry-budget proof') && charter.includes('No retry-storm safety or production overload-governance claim') && office.includes('Rev0029 storage-lane retry-budget amendment'), {}),
  check('docs-legible', frontier.includes('RetryBudgetAdmissionController') && frontier.includes('No OPFS storage-lane retry-budget proof') && slice.includes('scheduler:storage-lane-retry-budget-proof') && slice.includes(artifactPath) && auditDoc.includes('future-session'), {})
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
  purpose: 'Audit that the storage-lane retry-budget/admission slice is coherent across source, runtime exports, type surface, docs, manifest, impact map, inventory, proof artifact, research registry, and non-claim handoff surfaces.',
  checks,
  failedCount: failed.length,
  observations: Object.fromEntries(requiredObservationKeys.map((key) => [key, observations[key] === true])),
  nonClaims: [
    'Audit does not prove OPFS/browser retry-budget behavior.',
    'Audit does not prove retry-storm safety, production overload-governance, wall-clock timers, SLOs, throughput, latency, durability, or exactly-once delivery.',
    'Audit is a future-session coherence guard.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
