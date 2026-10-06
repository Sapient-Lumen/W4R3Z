#!/usr/bin/env node
// BrowserRT rev0028 storage-lane retry policy contract audit.
// Audit only; no OPFS, durability, exactly-once, or production retry scheduler claim.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-STORAGE-LANE-RETRY-CONTRACT-AUDIT.json`);
const artifactPath = `artifacts/validation/${PREFIX}-STORAGE-LANE-RETRY-POLICY-PROBE.json`;
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function hasAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }
function runProof() {
  const result = spawnSync(process.execPath, ['tools/storage_lane_retry_policy_probe.mjs', '--json', artifactPath], { cwd: '.', encoding: 'utf8' });
  return { ok: result.status === 0, status: result.status, stdout: result.stdout, stderr: result.stderr };
}

const proofRun = runProof();
let artifact = null;
try { artifact = await json(artifactPath); } catch {}
const source = await text('src/storage-lane-retry.mjs');
const runtime = await text('src/browserrt.mjs');
const ipc = await text('src/ipc.mjs');
const types = await text('src/types.d.ts');
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const registry = await json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');
const office = await text('docs/00-meta/future-session-office-manual.md');
const frontier = await text('docs/20-architecture/storage-lane-retry-policy-frontier.md');
const slice = await text('docs/40-validation/storage-lane-retry-policy-slice.md');
const manifestTask = manifest.tasks.find((task) => task.id === 'scheduler:storage-lane-retry-policy-proof');
const auditTask = manifest.tasks.find((task) => task.id === 'facility:storage-lane-retry-contract-audit');
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryTaskIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const titles = registry.families.flatMap((family) => family.sources || []).map((source) => source.title);
const observations = artifact?.observations || {};
const requiredObservationKeys = ['transientFailureNoProviderMutation','transientFailureScheduledDelayedRetry','retrySucceededOnSecondAttempt','nonRetryableFailsWithoutRetry','maxAttemptsStopsRetryLoop','noDelayedRetriesRemain','traceHasRequiredEvents'];
const checks = [
  check('proof-ran-in-audit', proofRun.ok, { exitStatus: proofRun.status, stderr: proofRun.stderr.slice(0, 1000) }),
  check('artifact-current-passed', artifact?.revision === REVISION && artifact?.status === 'passed', { artifactRevision: artifact?.revision, artifactStatus: artifact?.status }),
  check('required-observations-true', requiredObservationKeys.every((key) => observations[key] === true), { failed: requiredObservationKeys.filter((key) => observations[key] !== true) }),
  check('source-contract-needles-present', hasAll(source, ['class StorageLaneRetryPolicy','class StorageLaneRetryController','storage-retry:schedule-delay','No OPFS retry','No OPFS, durability, exactly-once']).length === 0, { missing: hasAll(source, ['class StorageLaneRetryPolicy','class StorageLaneRetryController','storage-retry:schedule-delay','No OPFS retry','No OPFS, durability, exactly-once']) }),
  check('runtime-exports-present', ['StorageLaneRetryPolicy','StorageLaneRetryController','createStorageLaneRetryController','storageLaneRetryPolicyProof','storageLaneRetryController'].every((needle) => runtime.includes(needle)), {}),
  check('ipc-and-types-present', ipc.includes('StorageLaneRetryController') && types.includes('StorageLaneRetryController') && types.includes('storageLaneRetryController'), {}),
  check('manifest-task-present', Boolean(manifestTask) && manifestTask.outputs.includes(artifactPath) && manifestTask.tiers.includes('release'), { manifestTask: manifestTask?.id ?? null }),
  check('audit-task-present', Boolean(auditTask) && auditTask.outputs.includes(outPath), { auditTask: auditTask?.id ?? null }),
  check('impact-map-covers-retry-tasks', impactTaskIds.has('scheduler:storage-lane-retry-policy-proof') && impactTaskIds.has('facility:storage-lane-retry-contract-audit'), {}),
  check('surface-inventory-covers-retry-tasks', inventoryTaskIds.has('scheduler:storage-lane-retry-policy-proof') && inventoryTaskIds.has('facility:storage-lane-retry-contract-audit'), {}),
  check('research-registry-covers-retry-sources', ['AWS Exponential Backoff and Jitter','Amazon Builders Library timeouts retries and backoff with jitter','Temporal Retry Policies','Kubernetes Jobs backoffLimit','Google SRE handling overload and client-side throttling'].every((title) => titles.includes(title)), { missing: ['AWS Exponential Backoff and Jitter','Amazon Builders Library timeouts retries and backoff with jitter','Temporal Retry Policies','Kubernetes Jobs backoffLimit','Google SRE handling overload and client-side throttling'].filter((title) => !titles.includes(title)) }),
  check('non-claims-handoff-present', charter.includes('No OPFS storage-lane retry proof') && charter.includes('No retry-storm safety or production retry algorithm claim') && office.includes('Rev0028 storage-lane retry amendment'), {}),
  check('docs-legible', frontier.includes('StorageLaneRetryController') && frontier.includes('No OPFS storage-lane retry proof') && slice.includes('scheduler:storage-lane-retry-policy-proof') && slice.includes(artifactPath), {})
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
  purpose: 'Audit that the storage-lane retry policy slice is coherent across source, runtime exports, type surface, docs, manifest, impact map, inventory, proof artifact, research registry, and non-claim handoff surfaces.',
  checks,
  failedCount: failed.length,
  observations: Object.fromEntries(requiredObservationKeys.map((key) => [key, observations[key] === true])),
  nonClaims: [
    'Audit does not prove OPFS/browser retry behavior.',
    'Audit does not prove durability, exactly-once delivery, retry-storm safety, wall-clock timers, throughput, latency, or production retry policy correctness.',
    'Audit is a future-session coherence guard.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
