#!/usr/bin/env node
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { estimatePlan, explainImpact, impactedTaskIds, normalizeChangedFiles, selectTasks, validateImpactMap, validateManifest } from '../src/test-facility.mjs';

function parseArgs(argv) {
  const out = { tier: 'release', ids: [], tag: null, shard: 'all', manifest: 'test/manifest.json', impactMap: 'test/impact-map.json', changed: '', json: null, list: false, includeQuarantined: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--tier') out.tier = argv[++i];
    else if (arg === '--id') out.ids.push(...String(argv[++i]).split(',').filter(Boolean));
    else if (arg === '--tag') out.tag = argv[++i];
    else if (arg === '--shard') out.shard = argv[++i];
    else if (arg === '--manifest') out.manifest = argv[++i];
    else if (arg === '--impact-map') out.impactMap = argv[++i];
    else if (arg === '--changed') out.changed = argv[++i];
    else if (arg === '--json') out.json = argv[++i];
    else if (arg === '--list') out.list = true;
    else if (arg === '--include-quarantined') out.includeQuarantined = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return out;
}

const options = parseArgs(process.argv.slice(2));
const manifest = JSON.parse(await readFile(options.manifest, 'utf8'));
const impactMap = JSON.parse(await readFile(options.impactMap, 'utf8'));
const manifestErrors = validateManifest(manifest, { currentRevision: REVISION });
const impactErrors = validateImpactMap(impactMap, manifest, { currentRevision: REVISION });
if (manifestErrors.length || impactErrors.length) {
  throw new Error('test planning surfaces invalid:\n' + [...manifestErrors, ...impactErrors].map((e) => `- ${e}`).join('\n'));
}
const changedFiles = normalizeChangedFiles(options.changed);
const impact = explainImpact(impactMap, changedFiles);
const changedTaskIds = changedFiles.length ? impactedTaskIds(impactMap, changedFiles) : [];
const tasks = selectTasks(manifest, { ...options, changedTaskIds });
const plan = estimatePlan(tasks);
const report = {
  project: 'BrowserRT',
  revision: REVISION,
  version: VERSION,
  schema: 1,
  generatedAt: new Date().toISOString(),
  status: tasks.length > 0 ? 'passed' : 'empty',
  options: { tier: options.tier, ids: options.ids, tag: options.tag, shard: options.shard, changedFiles, includeQuarantined: options.includeQuarantined },
  impact,
  plan,
  selectedTasks: tasks.map((task) => ({
    id: task.id,
    lane: task.lane,
    size: task.size,
    risk: task.risk,
    estimatedMs: task.estimatedMs,
    timeoutMs: task.timeoutMs,
    capabilities: task.capabilities || [],
    cachePolicy: task.cachePolicy || 'unspecified',
    inputs: task.inputs || [],
    outputs: task.outputs || []
  }))
};
if (options.json) {
  await mkdir(dirname(options.json), { recursive: true });
  await writeFile(options.json, JSON.stringify(report, null, 2) + '\n');
  console.log(options.json);
} else if (options.list) {
  for (const task of report.selectedTasks) console.log(`${task.id}\t${task.lane}\t${task.size}\t${task.estimatedMs}ms`);
} else {
  console.log(JSON.stringify(report, null, 2));
}
if (report.status === 'empty') process.exitCode = 1;
