#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { readTextWithRevisionFallback } from './revision_doc_fallback.mjs';

const prefix = `REV${REVISION.slice(3)}`;
const proofPath = `artifacts/validation/${prefix}-CROSS-LANE-SCHEDULER-PROBE.json`;

function parseArgs(argv) {
  const out = { json: null };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--json') out.json = argv[++i];
    else throw new Error(`Unknown option: ${argv[i]}`);
  }
  return out;
}
async function text(path) { return await readTextWithRevisionFallback(path); }
async function json(path) { return JSON.parse(await text(path)); }
function requireText(haystack, needle, path, findings) {
  const ok = haystack.includes(needle);
  findings.push({ path, check: `contains ${needle}`, status: ok ? 'passed' : 'failed' });
  return ok;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (!existsSync(proofPath)) {
    const { spawnSync } = await import('node:child_process');
    const result = spawnSync('node', ['tools/cross_lane_scheduler_probe.mjs', '--json', proofPath], { stdio: 'inherit' });
    if (result.status !== 0) throw new Error('failed to regenerate cross-lane scheduler proof before audit');
  }
  const findings = [];
  const proof = await json(proofPath);
  const manifest = await json('test/manifest.json');
  const impact = await json('test/impact-map.json');
  const source = await text('src/cross-lane-scheduler.mjs');
  const browserrt = await text('src/browserrt.mjs');
  const frontier = await text('docs/20-architecture/cross-lane-scheduler-frontier.md');
  const slice = await text('docs/40-validation/cross-lane-scheduler-slice.md');
  const charter = await text('docs/00-meta/non-claims-and-goals-charter.md');

  const taskIds = manifest.tasks.map((task) => task.id);
  findings.push({ path: 'test/manifest.json', check: 'has scheduler:cross-lane-contract-proof', status: taskIds.includes('scheduler:cross-lane-contract-proof') ? 'passed' : 'failed' });
  findings.push({ path: 'test/manifest.json', check: 'has facility:scheduler-contract-audit', status: taskIds.includes('facility:scheduler-contract-audit') ? 'passed' : 'failed' });
  const mapped = new Set(impact.rules.flatMap((rule) => rule.taskIds || []));
  findings.push({ path: 'test/impact-map.json', check: 'impact map covers scheduler proof', status: mapped.has('scheduler:cross-lane-contract-proof') ? 'passed' : 'failed' });
  for (const [key, value] of Object.entries(proof.observations || {})) findings.push({ path: proofPath, check: `observation ${key}`, status: value === true ? 'passed' : 'failed' });
  requireText(source, 'class CrossLaneScheduler', 'src/cross-lane-scheduler.mjs', findings);
  requireText(source, 'crosslane:defer-dependency', 'src/cross-lane-scheduler.mjs', findings);
  requireText(source, 'crosslane:lane-at-capacity', 'src/cross-lane-scheduler.mjs', findings);
  requireText(source, 'crosslane:dispatch', 'src/cross-lane-scheduler.mjs', findings);
  requireText(browserrt, 'CrossLaneScheduler', 'src/browserrt.mjs', findings);
  requireText(frontier, 'CrossLaneScheduler', 'docs/20-architecture/cross-lane-scheduler-frontier.md', findings);
  requireText(frontier, 'No production scheduler claim', 'docs/20-architecture/cross-lane-scheduler-frontier.md', findings);
  requireText(slice, 'scheduler:cross-lane-contract-proof', 'docs/40-validation/cross-lane-scheduler-slice.md', findings);
  requireText(slice, `${prefix}-CROSS-LANE-SCHEDULER-PROBE.json`, 'docs/40-validation/cross-lane-scheduler-slice.md', findings);
  requireText(charter, 'No production scheduler claim', 'docs/00-meta/non-claims-and-goals-charter.md', findings);

  const failed = findings.filter((finding) => finding.status !== 'passed');
  const report = {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    slice: 'facility:scheduler-contract-audit',
    status: failed.length ? 'failed' : 'passed',
    generatedAt: new Date().toISOString(),
    proofPath,
    findingCount: findings.length,
    failedCount: failed.length,
    findings,
    nonClaimsChecked: [
      'No production scheduler claim.',
      'No browser Worker scheduler proof.',
      'No latency, throughput, or fairness-SLO claim.'
    ]
  };
  if (options.json) {
    await mkdir(dirname(options.json), { recursive: true });
    await writeFile(options.json, JSON.stringify(report, null, 2) + '\n');
  }
  console.log(JSON.stringify({ status: report.status, slice: report.slice, failedCount: report.failedCount }, null, 2));
  if (failed.length) process.exitCode = 1;
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
