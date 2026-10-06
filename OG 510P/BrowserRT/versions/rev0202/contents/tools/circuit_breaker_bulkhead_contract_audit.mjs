#!/usr/bin/env node
// BrowserRT rev0031 circuit-breaker/bulkhead contract audit.
// Audit only; no OPFS/browser, SLO, real-time, throughput, or production resilience claim.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-CIRCUIT-BREAKER-BULKHEAD-CONTRACT-AUDIT.json`);
const artifactPath = `artifacts/validation/${PREFIX}-CIRCUIT-BREAKER-BULKHEAD-PROBE.json`;
async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function hasAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function runProof() {
  const result = spawnSync(process.execPath, ['tools/circuit_breaker_bulkhead_probe.mjs', '--json', artifactPath], { cwd: '.', encoding: 'utf8' });
  return { ok: result.status === 0, status: result.status, stdout: result.stdout, stderr: result.stderr };
}

const proofRun = runProof();
let artifact = null;
try { artifact = await json(artifactPath); } catch {}
const source = await text('src/circuit-breaker-bulkhead.mjs');
const runtime = await text('src/browserrt.mjs');
const ipc = await text('src/ipc.mjs');
const types = await text('src/types.d.ts');
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const registry = await json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');
const office = await text('docs/00-meta/future-session-office-manual.md');
const frontier = await text('docs/20-architecture/circuit-breaker-bulkhead-frontier.md');
const slice = await text('docs/40-validation/circuit-breaker-bulkhead-slice.md');
const auditDoc = await text(`docs/40-validation/circuit-breaker-bulkhead-contract-audit-${REVISION}.md`).catch(() => text('docs/40-validation/circuit-breaker-bulkhead-contract-audit-rev0033.md'));
const manifestTask = manifest.tasks.find((task) => task.id === 'scheduler:circuit-breaker-bulkhead-proof');
const auditTask = manifest.tasks.find((task) => task.id === 'facility:circuit-breaker-bulkhead-contract-audit');
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryTaskIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const titles = (registry.families || []).flatMap((family) => family.sources || []).map((source) => source.title);
const observations = artifact?.observations || {};
const requiredObservationKeys = [
  'controllerCreated',
  'bulkheadCapacityRejectsWithoutMutation',
  'failureThresholdOpensCircuit',
  'openCircuitRejectsWithoutLeaseGrowth',
  'virtualTickMovesOpenToHalfOpen',
  'halfOpenProbeLimitRejects',
  'halfOpenSuccessesCloseCircuit',
  'halfOpenFailureReopensCircuit',
  'slowCallRateOpensCircuit',
  'runtimeFactoryIntegration',
  'finalLeaseAccountingEmpty',
  'traceHasRequiredEvents'
];
const checks = [
  check('proof-ran-in-audit', proofRun.ok, { exitStatus: proofRun.status, stderr: proofRun.stderr.slice(0, 1200) }),
  check('artifact-current-passed', artifact?.revision === REVISION && artifact?.status === 'passed', { artifactRevision: artifact?.revision, artifactStatus: artifact?.status }),
  check('required-observations-true', requiredObservationKeys.every((key) => observations[key] === true), { failed: requiredObservationKeys.filter((key) => observations[key] !== true) }),
  check('source-contract-needles-present', hasAll(source, ['class CircuitBreakerBulkheadController','tryAcquire','release','advanceTicks','resilience:state-transition','validateCircuitBreakerBulkheadSnapshot','No OPFS, browser']).length === 0, { missing: hasAll(source, ['class CircuitBreakerBulkheadController','tryAcquire','release','advanceTicks','resilience:state-transition','validateCircuitBreakerBulkheadSnapshot','No OPFS, browser']) }),
  check('runtime-exports-present', ['CircuitBreakerBulkheadController','createCircuitBreakerBulkheadController','validateCircuitBreakerBulkheadSnapshot','circuitBreakerBulkheadProof','circuitBreakerBulkheadController'].every((needle) => runtime.includes(needle)), {}),
  check('ipc-and-types-present', ipc.includes('CircuitBreakerBulkheadController') && types.includes('CircuitBreakerBulkheadController') && types.includes('validateCircuitBreakerBulkheadSnapshot'), {}),
  check('manifest-task-present', Boolean(manifestTask) && manifestTask.outputs.includes(artifactPath) && manifestTask.tiers.includes('release'), { manifestTask: manifestTask?.id ?? null }),
  check('audit-task-present', Boolean(auditTask) && auditTask.outputs.includes(outPath), { auditTask: auditTask?.id ?? null }),
  check('impact-map-covers-resilience-tasks', impactTaskIds.has('scheduler:circuit-breaker-bulkhead-proof') && impactTaskIds.has('facility:circuit-breaker-bulkhead-contract-audit'), {}),
  check('surface-inventory-covers-resilience-tasks', inventoryTaskIds.has('scheduler:circuit-breaker-bulkhead-proof') && inventoryTaskIds.has('facility:circuit-breaker-bulkhead-contract-audit'), {}),
  check('research-registry-covers-resilience-sources', ['Resilience4j CircuitBreaker finite state machine and sliding window','Netflix Hystrix bulkhead isolation','Envoy circuit breakers and retry budget','Azure Circuit Breaker pattern','Azure Bulkhead pattern'].every((title) => titles.includes(title)), { missing: ['Resilience4j CircuitBreaker finite state machine and sliding window','Netflix Hystrix bulkhead isolation','Envoy circuit breakers and retry budget','Azure Circuit Breaker pattern','Azure Bulkhead pattern'].filter((title) => !titles.includes(title)) }),
  check('non-claims-handoff-present', charter.includes('No OPFS circuit-breaker/bulkhead proof') && charter.includes('No production resilience claim') && office.includes('Rev0031 circuit-breaker/bulkhead amendment'), {}),
  check('docs-legible', frontier.includes('CircuitBreakerBulkheadController') && frontier.includes('No OPFS circuit-breaker/bulkhead proof') && slice.includes('scheduler:circuit-breaker-bulkhead-proof') && slice.includes(artifactPath) && auditDoc.includes('future-session'), {})
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
  purpose: 'Audit that the circuit-breaker/bulkhead resilience slice is coherent across source, runtime exports, type surface, docs, manifest, impact map, inventory, proof artifact, research registry, and non-claim handoff surfaces.',
  checks,
  failedCount: failed.length,
  observations: Object.fromEntries(requiredObservationKeys.map((key) => [key, observations[key] === true])),
  nonClaims: [
    'Audit does not prove OPFS/browser circuit-breaker or bulkhead behavior.',
    'Audit does not prove production resilience, latency SLOs, real-time timers, throughput, durability, or cross-browser behavior.',
    'Audit is a future-session coherence guard.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
