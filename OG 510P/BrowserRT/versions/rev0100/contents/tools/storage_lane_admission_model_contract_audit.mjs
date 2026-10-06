#!/usr/bin/env node
// BrowserRT rev0036 storage-lane admission-history model contract audit.
// Cube-surface audit only; it does not prove OPFS/browser/performance/durability behavior.

import { readFile, writeFile, mkdir, access } from 'node:fs/promises';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const PREFIX = `REV${REVISION.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${PREFIX}-STORAGE-LANE-ADMISSION-MODEL-CONTRACT-AUDIT.json`);
const proofPath = `artifacts/validation/${PREFIX}-STORAGE-LANE-ADMISSION-MODEL-PROBE.json`;

async function exists(path) { try { await access(path); return true; } catch { return false; } }
async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function includesAll(body, needles) { return needles.filter((needle) => !body.includes(needle)); }

if (!await exists(proofPath)) {
  const child = spawnSync('node', ['tools/storage_lane_admission_model_probe.mjs', '--json', proofPath], { cwd: '.', encoding: 'utf8' });
  if (child.status !== 0) {
    throw new Error(`could not refresh proof artifact: ${child.stderr || child.stdout}`);
  }
}

const proof = await json(proofPath);
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const registry = await json('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
const receipt = await json('REVISION-RECEIPT.json');
const validation = await json('VALIDATION-INDEX.json');
const meta = await json('CUBE-META.json');
const status = await json('SURFACE-STATUS.json');

const source = await text('src/storage-lane-admission-model.mjs');
const runtime = await text('src/browserrt.mjs');
const ipc = await text('src/ipc.mjs');
const types = await text('src/types.d.ts');
const docs = {
  frontier: await text('docs/20-architecture/storage-lane-admission-model-frontier.md'),
  slice: await text('docs/40-validation/storage-lane-admission-model-slice.md'),
  audit: await text('docs/40-validation/storage-lane-admission-model-contract-audit-rev0036.md'),
  office: await text('docs/00-meta/future-session-office-manual.md'),
  charter: await text('docs/00-meta/non-claims-and-goals-charter.md'),
  context: await text('CONTEXT-PACK.md'),
  readme: await text('README.md'),
  start: await text('START_HERE.md')
};
const tasks = new Map((manifest.tasks || []).map((task) => [task.id, task]));
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const inventoryTaskIds = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const sourceTitles = new Set((registry.families || []).flatMap((family) => (family.sources || []).map((source) => source.title)));
const validationIds = new Set((validation.current_validations || []).map((row) => row.id));
const receiptNonClaims = JSON.stringify(receipt.non_claims || receipt.nonClaims || receipt.non_claims || []);
const nonClaimNeedles = [
  'No OPFS storage-lane admission-history model proof',
  'No browser Worker storage-lane admission-history model proof',
  'No exhaustive model checking',
  'No WebGPU proof'
];

const checks = [
  check('proof-current-and-passed', proof.revision === REVISION && proof.status === 'passed', { proofRevision: proof.revision, proofStatus: proof.status }),
  check('proof-observations-complete', proof.observations?.modelAgreementEveryStep === true && proof.observations?.deterministicReplayMatches === true && proof.observations?.traceHasRequiredEvents === true, { observations: proof.observations }),
  check('source-has-model-oracle', includesAll(source, ['StorageLaneAdmissionHistoryModelOracle', 'observeOperation', 'compareStorageLaneAdmissionHistoryToModel', 'predictAdmission']).length === 0),
  check('runtime-export-wired', includesAll(runtime, ['StorageLaneAdmissionHistoryModelOracle', 'createStorageLaneAdmissionHistoryModelOracle', 'compareStorageLaneAdmissionHistoryToModel', 'storageLaneAdmissionHistoryModelProof']).length === 0),
  check('ipc-and-types-wired', includesAll(ipc, ['StorageLaneAdmissionHistoryModelOracle', 'compareStorageLaneAdmissionHistoryToModel']).length === 0 && includesAll(types, ['StorageLaneAdmissionHistoryModelOracle', 'compareStorageLaneAdmissionHistoryToModel']).length === 0),
  check('manifest-tasks-present', tasks.has('scheduler:storage-lane-admission-model-proof') && tasks.has('facility:storage-lane-admission-model-contract-audit')),
  check('manifest-tasks-release-tier', ['scheduler:storage-lane-admission-model-proof', 'facility:storage-lane-admission-model-contract-audit'].every((id) => tasks.get(id)?.tiers?.includes('release'))),
  check('manifest-current-outputs', ['scheduler:storage-lane-admission-model-proof', 'facility:storage-lane-admission-model-contract-audit'].every((id) => (tasks.get(id)?.outputs || []).some((out) => out.includes(PREFIX)))),
  check('impact-and-inventory-cover-tasks', ['scheduler:storage-lane-admission-model-proof', 'facility:storage-lane-admission-model-contract-audit'].every((id) => impactTaskIds.has(id) && inventoryTaskIds.has(id))),
  check('research-registered', ['Reactive Streams non-blocking backpressure', 'Kubernetes API Priority and Fairness queueing and rejection', 'Google SRE retry budgets and cascading failure pressure', 'Model-based testing generates tests from behavioral models'].every((title) => sourceTitles.has(title))),
  check('docs-legible', Object.values(docs).every((body) => body.includes('StorageLaneAdmissionHistoryModelOracle') || body.includes('storage-lane admission-history model'))),
  check('validation-index-covers-proof', validationIds.has('scheduler:storage-lane-admission-model-proof') && validationIds.has('facility:storage-lane-admission-model-contract-audit')),
  check('current-surfaces-point-at-model-slice', meta.current_runtime_slice === 'scheduler:storage-lane-admission-model-proof' && status.current_runtime_slice === 'scheduler:storage-lane-admission-model-proof'),
  check('non-claims-legible', nonClaimNeedles.every((needle) => receiptNonClaims.includes(needle) && docs.charter.includes(needle) && docs.context.includes(needle)))
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: failed.length ? 'failed' : 'passed', generatedAt: new Date().toISOString(),
  slice: 'facility:storage-lane-admission-model-contract-audit',
  purpose: 'Audit that the rev0036 storage-lane admission-history model oracle has source/runtime/type/docs/manifest/impact/inventory/research/proof/non-claim coherence for future sessions.',
  checks,
  proof: { path: proofPath, status: proof.status, scenarioCount: proof.observations?.scenarioCount, totalSteps: proof.observations?.totalSteps },
  nonClaims: [
    'Contract audit does not prove OPFS, browser Worker, real performance, durability, or production overload-governance behavior.',
    'Contract audit guards cube coherence around the fake-provider model slice.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
