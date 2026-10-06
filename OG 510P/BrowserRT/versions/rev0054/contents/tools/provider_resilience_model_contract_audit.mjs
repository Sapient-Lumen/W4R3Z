#!/usr/bin/env node
// BrowserRT rev0035 provider-resilience model contract audit.
// Coherence audit only; no OPFS/browser, production resilience, throughput, SLO, or formal verification claim.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-PROVIDER-RESILIENCE-MODEL-CONTRACT-AUDIT.json`);
const proofPath = `artifacts/validation/${PREFIX}-PROVIDER-RESILIENCE-MODEL-PROBE.json`;

async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await readFile(path, 'utf8')); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

const proofRun = spawnSync(process.execPath, ['tools/provider_resilience_model_probe.mjs', '--json', proofPath], { cwd: '.', encoding: 'utf8' });
if (proofRun.status !== 0) {
  throw new Error(`provider-resilience model proof failed before audit\nstdout:\n${proofRun.stdout}\nstderr:\n${proofRun.stderr}`);
}

const [manifest, impact, inventory, proof, modelSource, historySource, runtime, ipc, types, frontier, sliceDoc, auditDoc, charter, office, registry] = await Promise.all([
  json('test/manifest.json'),
  json('test/impact-map.json'),
  json('test/surface-inventory.json'),
  json(proofPath),
  text('src/provider-resilience-model.mjs'),
  text('src/provider-resilience-history.mjs'),
  text('src/browserrt.mjs'),
  text('src/ipc.mjs'),
  text('src/types.d.ts'),
  text('docs/20-architecture/provider-resilience-model-frontier.md'),
  text('docs/40-validation/provider-resilience-model-slice.md'),
  text('docs/40-validation/provider-resilience-model-contract-audit-rev0035.md'),
  text('docs/00-meta/non-claims-and-goals-charter.md'),
  text('docs/00-meta/future-session-office-manual.md'),
  json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json')
]);
const taskIds = new Set(manifest.tasks.map((task) => task.id));
const modelTask = manifest.tasks.find((task) => task.id === 'scheduler:provider-resilience-model-proof');
const auditTask = manifest.tasks.find((task) => task.id === 'facility:provider-resilience-model-contract-audit');
const impactIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const titles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));
const obs = proof.observations || {};
const requiredObs = ['aggregateAgreement', 'transientRetryMatched', 'budgetExhaustionMatched', 'nonIdempotentMatched', 'openCircuitMatched', 'primarySuccessMatched', 'failuresAndSuccessesBothPresent', 'allSnapshotsValidate', 'finalLeaseAccountingEmpty', 'bootReportRecordsProviderResilienceModelProof', 'traceHasRequiredEvents'];
const checks = [
  check('proof-ran-in-audit', proofRun.status === 0),
  check('proof-current-passed', proof.revision === REVISION && proof.status === 'passed' && proof.slice === 'scheduler:provider-resilience-model-proof', { proofRevision: proof.revision, proofSlice: proof.slice, proofStatus: proof.status }),
  check('proof-observations-hold', requiredObs.every((key) => obs[key] === true), { missingTrue: requiredObs.filter((key) => obs[key] !== true), totalOperations: obs.totalOperations }),
  check('tasks-present-release-browser-light', taskIds.has('scheduler:provider-resilience-model-proof') && taskIds.has('facility:provider-resilience-model-contract-audit') && modelTask?.tiers?.includes('release') && auditTask?.tiers?.includes('release') && modelTask?.lane !== 'browser' && auditTask?.lane !== 'browser', { modelLane: modelTask?.lane, auditLane: auditTask?.lane }),
  check('task-outputs-current-prefix', modelTask?.outputs?.some((out) => out.includes(PREFIX)) && auditTask?.outputs?.some((out) => out.includes(PREFIX)), { prefix: PREFIX }),
  check('impact-map-covers-model', impactIds.has('scheduler:provider-resilience-model-proof') && impactIds.has('facility:provider-resilience-model-contract-audit')),
  check('surface-inventory-covers-model', inventoryIds.has('scheduler:provider-resilience-model-proof') && inventoryIds.has('facility:provider-resilience-model-contract-audit')),
  check('model-source-contract-present', missing(modelSource, ['class ProviderResilienceModelOracle', 'compareProviderResilienceHistoryToModel', 'validateProviderResilienceModelSnapshot', 'No OPFS, browser']).length === 0),
  check('history-runner-max-attempt-leak-fix-present', missing(historySource, ['attempt >= maxAttempts', 'max-attempts']).length === 0),
  check('runtime-ipc-types-export-model', missing(runtime + ipc + types, ['ProviderResilienceModelOracle', 'createProviderResilienceModelOracle', 'compareProviderResilienceHistoryToModel', 'validateProviderResilienceModelSnapshot', 'providerResilienceModelProof']).length === 0),
  check('docs-present-current-and-legible', missing(frontier + sliceDoc + auditDoc, ['rev0035', 'scheduler:provider-resilience-model-proof', 'ProviderResilienceModelOracle', 'No OPFS provider-resilience model proof']).length === 0),
  check('future-session-nonclaims-present', missing(charter + office, ['No OPFS provider-resilience model proof', 'No browser Worker provider-resilience model proof', 'No exhaustive model checking or formal verification claim']).length === 0),
  check('research-registry-covers-model-sources', ['Porcupine executable model and history checking', 'Knossos validates histories against models', 'Jepsen checker validates histories against models', 'FoundationDB deterministic simulation and reproducible failures', 'Resilience4j finite-state circuit breaker'].every((title) => titles.has(title)))
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
  slice: 'facility:provider-resilience-model-contract-audit',
  purpose: 'Audit provider-resilience model oracle coherence across model source, history-runner leak fix, runtime exports, docs, manifest, impact map, inventory, proof artifact, research registry, and future-session non-claims.',
  proofPath,
  passedCount: checks.length - failed.length,
  failedCount: failed.length,
  checks,
  nonClaims: [
    'This audit proves cube coherence only.',
    'This audit does not prove OPFS or browser Worker provider-resilience behavior.',
    'This audit does not prove production resilience, retry-storm safety, real-time timers, SLOs, throughput, exactly-once delivery, or formal verification.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
assert.equal(report.status, 'passed', JSON.stringify(failed, null, 2));
