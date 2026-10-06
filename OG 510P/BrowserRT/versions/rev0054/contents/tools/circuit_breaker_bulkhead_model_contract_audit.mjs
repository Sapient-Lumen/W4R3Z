#!/usr/bin/env node
// BrowserRT rev0033 circuit-breaker/bulkhead model contract audit.
// Coherence audit only; no OPFS/browser, production resilience, real-time, throughput, SLO, or formal verification claim.
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-CIRCUIT-BREAKER-BULKHEAD-MODEL-CONTRACT-AUDIT.json`);
const proofPath = `artifacts/validation/${PREFIX}-CIRCUIT-BREAKER-BULKHEAD-MODEL-PROBE.json`;

async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await readFile(path, 'utf8')); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function missing(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

const proofRun = spawnSync(process.execPath, ['tools/circuit_breaker_bulkhead_model_probe.mjs', '--json', proofPath], { cwd: '.', encoding: 'utf8' });
if (proofRun.status !== 0) {
  throw new Error(`circuit-breaker/bulkhead model proof failed before audit\nstdout:\n${proofRun.stdout}\nstderr:\n${proofRun.stderr}`);
}

const [manifest, impact, inventory, proof, source, runtime, ipc, types, frontier, sliceDoc, auditDoc, charter, office, registry] = await Promise.all([
  json('test/manifest.json'),
  json('test/impact-map.json'),
  json('test/surface-inventory.json'),
  json(proofPath),
  text('src/circuit-breaker-bulkhead.mjs'),
  text('src/browserrt.mjs'),
  text('src/ipc.mjs'),
  text('src/types.d.ts'),
  text('docs/20-architecture/circuit-breaker-bulkhead-model-frontier.md'),
  text('docs/40-validation/circuit-breaker-bulkhead-model-slice.md'),
  text(`docs/40-validation/circuit-breaker-bulkhead-model-contract-audit-${REVISION}.md`).catch(() => text('docs/40-validation/circuit-breaker-bulkhead-model-contract-audit-rev0033.md')),
  text('docs/00-meta/non-claims-and-goals-charter.md'),
  text('docs/00-meta/future-session-office-manual.md'),
  json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json')
]);

const taskIds = new Set(manifest.tasks.map((task) => task.id));
const modelTask = manifest.tasks.find((task) => task.id === 'scheduler:circuit-breaker-bulkhead-model-proof');
const auditTask = manifest.tasks.find((task) => task.id === 'facility:circuit-breaker-bulkhead-model-contract-audit');
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryTaskIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const sourceTitles = new Set((registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title));
const obs = proof.observations || {};
const requiredObs = [
  'targetedObservationsHold',
  'deterministicReplayMatches',
  'realModelAgreementEveryStep',
  'finalSnapshotsValidated',
  'finalAccountingEmpty',
  'generatedOpenObserved',
  'generatedHalfOpenObserved',
  'generatedBulkheadRejectObserved',
  'generatedCircuitRejectObserved',
  'generatedForcedOpenRejectObserved',
  'generatedUnknownReleaseObserved',
  'rejectionNoLeaseGrowthObserved',
  'slowCallThresholdObserved',
  'failureThresholdObserved',
  'halfOpenFailureReopensObserved',
  'runtimeBootFlagObserved',
  'traceHasRequiredEvents'
];

const checks = [
  check('proof-ran-in-audit', proofRun.status === 0, { exitStatus: proofRun.status }),
  check('proof-current-passed', proof.revision === REVISION && proof.status === 'passed' && proof.slice === 'scheduler:circuit-breaker-bulkhead-model-proof', { proofRevision: proof.revision, proofStatus: proof.status, proofSlice: proof.slice }),
  check('proof-observations-hold', requiredObs.every((key) => obs[key] === true), { missingTrue: requiredObs.filter((key) => obs[key] !== true) }),
  check('task-present-release-browser-light', taskIds.has('scheduler:circuit-breaker-bulkhead-model-proof') && taskIds.has('facility:circuit-breaker-bulkhead-model-contract-audit') && modelTask?.tiers?.includes('release') && auditTask?.tiers?.includes('release') && modelTask?.lane !== 'browser' && auditTask?.lane !== 'browser', { modelLane: modelTask?.lane, auditLane: auditTask?.lane }),
  check('task-outputs-current-prefix', modelTask?.outputs?.some((out) => out.includes(PREFIX)) && auditTask?.outputs?.some((out) => out.includes(PREFIX)), { prefix: PREFIX }),
  check('impact-map-covers-model', impactTaskIds.has('scheduler:circuit-breaker-bulkhead-model-proof') && impactTaskIds.has('facility:circuit-breaker-bulkhead-model-contract-audit')),
  check('surface-inventory-covers-model', inventoryTaskIds.has('scheduler:circuit-breaker-bulkhead-model-proof') && inventoryTaskIds.has('facility:circuit-breaker-bulkhead-model-contract-audit')),
  check('source-validator-and-controller-present', missing(source, ['class CircuitBreakerBulkheadController', 'validateCircuitBreakerBulkheadSnapshot', 'tryAcquire', 'release', 'advanceTicks']).length === 0),
  check('runtime-boot-flag-present', missing(runtime, ['circuitBreakerBulkheadModelProof', 'CircuitBreakerBulkheadController', 'validateCircuitBreakerBulkheadSnapshot']).length === 0),
  check('ipc-and-types-present', ipc.includes('CircuitBreakerBulkheadController') && types.includes('CircuitBreakerBulkheadController') && types.includes('validateCircuitBreakerBulkheadSnapshot')),
  check('docs-present-current-and-legible', missing(frontier + sliceDoc + auditDoc, ['scheduler:circuit-breaker-bulkhead-model-proof', 'No OPFS circuit-breaker/bulkhead model proof', 'model oracle']).length === 0),
  check('future-session-nonclaims-present', missing(charter + office, ['No OPFS circuit-breaker/bulkhead model proof', 'No browser Worker circuit-breaker/bulkhead model proof', 'No exhaustive model checking or formal verification claim']).length === 0),
  check('research-registry-covers-model-sources', ['Polly resilience pipeline strategies', 'Resilience4j CircuitBreaker finite state machine and sliding window', 'Envoy circuit breakers and retry budget', 'Hystrix bulkhead isolation', 'fast-check model-based testing'].every((title) => sourceTitles.has(title)), { requiredTitles: ['Polly resilience pipeline strategies', 'Resilience4j CircuitBreaker finite state machine and sliding window', 'Envoy circuit breakers and retry budget', 'Hystrix bulkhead isolation', 'fast-check model-based testing'] })
];

const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  status: failed.length === 0 ? 'passed' : 'failed',
  generatedAt: new Date().toISOString(),
  slice: 'facility:circuit-breaker-bulkhead-model-contract-audit',
  purpose: 'Audit circuit-breaker/bulkhead model oracle coherence across proof artifact, manifest, impact map, surface inventory, source/runtime exports, docs, research registry, and future-session non-claim surfaces.',
  proofPath,
  passedCount: checks.length - failed.length,
  failedCount: failed.length,
  checks,
  nonClaims: [
    'This audit proves cube coherence only.',
    'This audit does not prove OPFS/browser circuit-breaker/bulkhead behavior.',
    'This audit does not prove production resilience, real-time timers, SLOs, throughput, or formal verification.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
assert.equal(report.status, 'passed', JSON.stringify(failed, null, 2));
