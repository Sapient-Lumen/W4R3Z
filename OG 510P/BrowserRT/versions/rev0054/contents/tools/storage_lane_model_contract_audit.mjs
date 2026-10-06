#!/usr/bin/env node
// BrowserRT rev0028 storage-lane model contract audit.
// This audit keeps the storage-lane model proof, docs, manifest, artifacts, and non-claims coherent.

import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-STORAGE-LANE-MODEL-CONTRACT-AUDIT.json`);
const proofPath = `artifacts/validation/${PREFIX}-STORAGE-LANE-MODEL-WALK-PROBE.json`;

async function json(path) { return JSON.parse(await readFile(path, 'utf8')); }
async function text(path) { return await readFile(path, 'utf8'); }
function run(cmd, args) {
  const res = spawnSync(cmd, args, { cwd: process.cwd(), encoding: 'utf8' });
  if (res.status !== 0) throw new Error(`${cmd} ${args.join(' ')} failed\n${res.stdout}\n${res.stderr}`);
  return res;
}
function check(condition, checks, id, message, detail = {}) { checks.push({ id, status: condition ? 'passed' : 'failed', message, detail }); }

if (!existsSync(proofPath)) run('node', ['tools/storage_lane_model_walk_probe.mjs', '--json', proofPath]);
const proof = await json(proofPath);
const manifest = await json('test/manifest.json');
const inventory = await json('test/surface-inventory.json');
const impact = await json('test/impact-map.json');
const receipt = await json('REVISION-RECEIPT.json');
const validation = await json('VALIDATION-INDEX.json');
const source = await text('src/storage-lane-scheduler.mjs');
const runtime = await text('src/browserrt.mjs');
const docs = [
  await text('docs/40-validation/storage-lane-model-walk-slice.md'),
  await text('docs/20-architecture/storage-lane-model-oracle-frontier.md'),
  await text('docs/00-meta/non-claims-and-goals-charter.md')
].join('\n');
const manifestTask = manifest.tasks.find((task) => task.id === 'scheduler:storage-lane-model-walk-proof');
const auditTask = manifest.tasks.find((task) => task.id === 'facility:storage-lane-model-contract-audit');
const surfaceRefs = new Set(inventory.surfaces.flatMap((surface) => surface.currentTaskIds || []));
const impactRefs = new Set(impact.rules.flatMap((rule) => rule.taskIds || []));
const checks = [];
check(proof.revision === REVISION && proof.status === 'passed', checks, 'proof-current', 'proof artifact is current and passed', { proofPath, proofRevision: proof.revision });
for (const key of ['deterministicReplayMatches', 'snapshotsValidated', 'modelAgreementEveryStep', 'finalAccountingEmpty', 'healthRejectNoMutation', 'providerFailureObserved', 'capacityBlockObserved', 'dependencyDeferralObserved', 'traceHasRequiredEvents']) {
  check(proof.observations?.[key] === true, checks, `proof-observation-${key}`, `proof observation ${key} is true`);
}
check(Boolean(manifestTask), checks, 'manifest-proof-task', 'manifest contains storage-lane model-walk task');
check(Boolean(auditTask), checks, 'manifest-audit-task', 'manifest contains storage-lane model contract audit task');
check(manifestTask?.tiers?.includes('release') === true, checks, 'manifest-release-tier', 'model-walk proof is release tier');
check(manifestTask?.lane === 'scheduler', checks, 'manifest-lane', 'model-walk proof is scheduler lane');
check(manifestTask?.estimatedMs <= 500, checks, 'manifest-estimate', 'model-walk proof estimate stays small enough for cloudtainer release windows', { estimatedMs: manifestTask?.estimatedMs });
check(surfaceRefs.has('scheduler:storage-lane-model-walk-proof') && surfaceRefs.has('facility:storage-lane-model-contract-audit'), checks, 'surface-inventory', 'surface inventory references proof and audit tasks');
check(impactRefs.has('scheduler:storage-lane-model-walk-proof') && impactRefs.has('facility:storage-lane-model-contract-audit'), checks, 'impact-map', 'impact map references proof and audit tasks');
check(source.includes('validateStorageLaneExecutorSnapshot'), checks, 'snapshot-validator-source', 'storage-lane snapshot validator exists in source');
check(runtime.includes('validateStorageLaneExecutorSnapshot'), checks, 'snapshot-validator-runtime-export', 'runtime exports storage-lane snapshot validator');
for (const phrase of ['No OPFS storage-lane model proof', 'No exhaustive model checking', 'No production storage scheduler claim']) {
  check(docs.includes(phrase) || JSON.stringify(receipt).includes(phrase) || JSON.stringify(proof).includes(phrase), checks, `nonclaim-${phrase}`, `non-claim phrase is legible: ${phrase}`);
}
check(JSON.stringify(validation).includes('scheduler:storage-lane-model-walk-proof'), checks, 'validation-index', 'validation index includes model-walk proof');
check(JSON.stringify(receipt).includes('storage-lane model-walk') || JSON.stringify(receipt).includes('Storage-lane model-walk'), checks, 'receipt-model-surface', 'receipt carries storage-lane model-walk surface even if the revision codename names the retry amendment');
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  status: failed.length ? 'failed' : 'passed',
  generatedAt: new Date().toISOString(),
  audit: 'facility:storage-lane-model-contract-audit',
  codename: 'Storage Lane Model Contract Audit',
  proofPath,
  checkCount: checks.length,
  failedCount: failed.length,
  checks
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
if (failed.length) {
  console.error(JSON.stringify(report, null, 2));
  process.exit(1);
}
console.log(JSON.stringify({ status: report.status, revision: REVISION, audit: report.audit, outPath, checkCount: checks.length }, null, 2));
