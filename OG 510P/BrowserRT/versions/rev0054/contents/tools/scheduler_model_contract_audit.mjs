#!/usr/bin/env node
// BrowserRT rev0025 scheduler model-contract audit. It is a coherence guard, not a runtime proof.
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { spawnSync } from 'node:child_process';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const prefix = `REV${REVISION.slice(3)}`;
const proofPath = `artifacts/validation/${prefix}-CROSS-LANE-MODEL-WALK-PROBE.json`;

function argValue(flag, fallback = null) {
  const i = process.argv.indexOf(flag);
  return i >= 0 ? process.argv[i + 1] : fallback;
}
async function text(path) { return await readFile(path, 'utf8'); }
async function json(path) { return JSON.parse(await text(path)); }
function row(path, check, passed, extra = {}) { return { path, check, status: passed ? 'passed' : 'failed', ...extra }; }
function has(body, needle) { return body.includes(needle); }

if (!existsSync(proofPath)) {
  const result = spawnSync('node', ['tools/cross_lane_model_walk_probe.mjs', '--json', proofPath], { stdio: 'inherit' });
  if (result.status !== 0) throw new Error('failed to regenerate cross-lane model-walk proof before audit');
}

const proof = await json(proofPath);
const manifest = await json('test/manifest.json');
const impact = await json('test/impact-map.json');
const inventory = await json('test/surface-inventory.json');
const source = await text('src/cross-lane-scheduler.mjs');
const runtime = await text('src/browserrt.mjs');
const types = await text('src/types.d.ts');
const probe = await text('tools/cross_lane_model_walk_probe.mjs');
const frontier = await text('docs/20-architecture/cross-lane-scheduler-model-frontier.md');
const slice = await text('docs/40-validation/cross-lane-model-walk-slice.md');
const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');
const office = await text('docs/00-meta/future-session-office-manual.md');
const taskIds = (manifest.tasks || []).map((task) => task.id);
const mapped = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const surfaceRefs = new Set((inventory.surfaces || []).flatMap((surface) => surface.currentTaskIds || []));
const findings = [];
findings.push(row('test/manifest.json', 'manifest has scheduler:cross-lane-model-walk-proof', taskIds.includes('scheduler:cross-lane-model-walk-proof')));
findings.push(row('test/manifest.json', 'manifest has facility:scheduler-model-contract-audit', taskIds.includes('facility:scheduler-model-contract-audit')));
findings.push(row('test/impact-map.json', 'impact map covers scheduler model-walk proof', mapped.has('scheduler:cross-lane-model-walk-proof')));
findings.push(row('test/impact-map.json', 'impact map covers scheduler model-contract audit', mapped.has('facility:scheduler-model-contract-audit')));
findings.push(row('test/surface-inventory.json', 'surface inventory covers model-walk proof', surfaceRefs.has('scheduler:cross-lane-model-walk-proof')));
findings.push(row('test/surface-inventory.json', 'surface inventory covers model-contract audit', surfaceRefs.has('facility:scheduler-model-contract-audit')));
findings.push(row('src/cross-lane-scheduler.mjs', 'snapshot validator exported', has(source, 'validateCrossLaneSchedulerSnapshot')));
findings.push(row('src/browserrt.mjs', 'runtime exports snapshot validator', has(runtime, 'validateCrossLaneSchedulerSnapshot')));
findings.push(row('src/types.d.ts', 'types export snapshot validator', has(types, 'validateCrossLaneSchedulerSnapshot')));
findings.push(row('tools/cross_lane_model_walk_probe.mjs', 'probe calls snapshot validator', has(probe, 'validateCrossLaneSchedulerSnapshot')));
findings.push(row('tools/cross_lane_model_walk_probe.mjs', 'probe records deterministicReplayMatches', has(probe, 'deterministicReplayMatches')));
findings.push(row('docs/20-architecture/cross-lane-scheduler-model-frontier.md', 'frontier names model-walk', has(frontier, 'model-walk')));
findings.push(row('docs/40-validation/cross-lane-model-walk-slice.md', 'slice names manifest id', has(slice, 'scheduler:cross-lane-model-walk-proof')));
findings.push(row('docs/40-validation/cross-lane-model-walk-slice.md', 'slice names proof artifact', has(slice, `${prefix}-CROSS-LANE-MODEL-WALK-PROBE.json`)));
findings.push(row('docs/00-meta/non-claims-and-goals-charter.md', 'charter keeps model non-claim', has(charter, 'No exhaustive model checking')));
findings.push(row('docs/00-meta/future-session-office-manual.md', 'office names model-oracle amendment', has(office, 'Rev0025 model-oracle amendment')));
for (const key of ['deterministicReplayMatches','allScenariosFinalZeroPending','allSnapshotsValidated','rejectionNoMutationObserved','dependencyDeferralObserved','capacityBlockObserved','fallbackRouteObserved','traceHasRequiredEvents']) {
  findings.push(row(proofPath, `observation ${key}`, proof.observations?.[key] === true));
}
const failed = findings.filter((finding) => finding.status !== 'passed');
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  slice: 'facility:scheduler-model-contract-audit',
  status: failed.length ? 'failed' : 'passed',
  generatedAt: new Date().toISOString(),
  purpose: 'Coherence audit for the rev0025 scheduler model-walk proof: source, snapshot validator, probe, docs, manifest, impact map, surface inventory, proof artifact, and non-claim boundaries.',
  proofPath,
  findingCount: findings.length,
  failedCount: failed.length,
  findings,
  nonClaimsChecked: [
    'No exhaustive model checking or formal verification claim.',
    'No true concurrent interleaving proof.',
    'No production scheduler claim.',
    'No browser Worker scheduler proof.',
    'No throughput, latency, fairness, or real performance claim.'
  ]
};
const out = argValue('--json');
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
}
console.log(JSON.stringify({ status: report.status, slice: report.slice, failedCount: report.failedCount }, null, 2));
if (failed.length) process.exitCode = 1;
