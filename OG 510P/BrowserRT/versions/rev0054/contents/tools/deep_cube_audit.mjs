#!/usr/bin/env node
import { readdir, readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, relative } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
};
const CURRENT_PREFIX = `REV${REVISION.slice(3)}`;
const PREVIOUS_REV = `rev${String(Number(REVISION.slice(3)) - 1).padStart(4, '0')}`;
const PREVIOUS_PREFIX = `REV${PREVIOUS_REV.slice(3)}`;
const outPath = argValue('--json', `artifacts/audit/${CURRENT_PREFIX}-DEEP-CUBE-AUDIT.json`);

async function walk(dir = '.') {
  const out = [];
  for (const ent of await readdir(dir, { withFileTypes: true })) {
    if (['.git', 'node_modules', '__pycache__', 'out'].includes(ent.name)) continue;
    const p = `${dir}/${ent.name}`;
    if (ent.isDirectory()) out.push(...await walk(p));
    else out.push(p);
  }
  return out;
}
async function readJson(path) { return JSON.parse(await readFile(path, 'utf8')); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function missingNeedles(text, needles) { return needles.filter((needle) => !text.includes(needle)); }

const files = await walk('.');
const textRows = [];
for (const file of files) {
  if (file.endsWith('.zip')) continue;
  try { textRows.push([relative('.', file), await readFile(file, 'utf8')]); } catch {}
}
const text = new Map(textRows);
const packageJson = await readJson('package.json');
const receipt = await readJson('REVISION-RECEIPT.json');
const reentry = await readJson('REENTRY-CONTRACT.json');
const status = await readJson('SURFACE-STATUS.json');
const validation = await readJson('VALIDATION-INDEX.json');
const manifest = await readJson('test/manifest.json');
const impact = await readJson('test/impact-map.json');
const inventory = await readJson('test/surface-inventory.json');
const quarantine = await readJson('test/quarantine.json');

const centralRevisions = {
  receipt: receipt.revision,
  reentry: reentry.revision,
  status: status.revision,
  validation: validation.revision,
  manifest: manifest.revision,
  impact: impact.revision,
  inventory: inventory.revision,
  quarantine: quarantine.revision
};
const tasks = manifest.tasks || [];
const taskIds = tasks.map((task) => task.id);
const duplicateTaskIds = taskIds.filter((id, index) => taskIds.indexOf(id) !== index);
const releaseTasks = tasks.filter((task) => task.tiers?.includes('release'));
const browserTasks = tasks.filter((task) => task.lane === 'browser');
const releaseBrowserTasks = releaseTasks.filter((task) => task.lane === 'browser');
const releaseEstimateMs = releaseTasks.reduce((sum, task) => sum + (task.estimatedMs || 0), 0);
const releaseTimeoutMs = releaseTasks.reduce((sum, task) => sum + (task.timeoutMs || 0), 0);
const browserEstimateMs = browserTasks.reduce((sum, task) => sum + (task.estimatedMs || 0), 0);

const requiredFields = ['id', 'description', 'command', 'tiers', 'tags', 'areas', 'lane', 'parallelGroup', 'size', 'isolation', 'flakiness', 'risk', 'estimatedMs', 'timeoutMs', 'inputs', 'outputs', 'capabilities', 'cachePolicy', 'evidence'];
const missingManifestFields = [];
for (const task of tasks) for (const field of requiredFields) if (!(field in task)) missingManifestFields.push({ id: task.id || '<missing-id>', field });

const artifactPaths = files.filter((file) => /^\.\/artifacts\/(audit|proof|validation)\//.test(file)).map((file) => relative('.', file));
const oldArtifactPrefixes = artifactPaths.filter((path) => /REV\d{4}-/.test(path) && !path.includes(CURRENT_PREFIX) && !path.includes(PREVIOUS_PREFIX));
const currentOutputProblems = [];
for (const task of tasks) {
  for (const output of task.outputs || []) {
    if (/artifacts\/(audit|proof|validation)\/REV\d{4}-/.test(output) && !output.includes(CURRENT_PREFIX)) currentOutputProblems.push({ id: task.id, output });
  }
  const command = Array.isArray(task.command) ? task.command.join(' ') : String(task.command || '');
  for (const hit of command.match(/REV\d{4}-/g) || []) if (hit !== `${CURRENT_PREFIX}-`) currentOutputProblems.push({ id: task.id, commandHit: hit });
}

const staleCurrentness = [];
for (const [path, body] of textRows) {
  if (path === 'CHANGELOG.md' || path === 'RELEASE-MANIFEST.json' || path.startsWith('artifacts/')) continue;
  const markers = [];
  for (const match of body.matchAll(/Current revision:\s+(rev\d{4})/g)) if (match[1] !== REVISION) markers.push(match[0]);
  for (const match of body.matchAll(/Current packaged head:\s+`(rev\d{4})`/g)) if (match[1] !== REVISION) markers.push(match[0]);
  if (markers.length) staleCurrentness.push({ path, markers: [...new Set(markers)] });
}

const docs = {
  agents: text.get('AGENTS.md') || '',
  readme: text.get('README.md') || '',
  start: text.get('START_HERE.md') || '',
  context: text.get('CONTEXT-PACK.md') || '',
  office: text.get('docs/00-meta/future-session-office-manual.md') || '',
  charter: text.get('docs/00-meta/non-claims-and-goals-charter.md') || '',
  howTo: text.get('docs/40-validation/how-to-add-test-slice.md') || '',
  longRun: text.get('docs/40-validation/testing-facility-long-run-audit.md') || ''
};
const handoffMissing = {
  office: missingNeedles(docs.office, ['How to resume the office', 'Current earned rungs', 'Do not erase non-claims', 'Earn each stair']),
  charter: missingNeedles(docs.charter, ['North-star goal', 'Current non-claims', 'Current claims that are earned', 'Claim promotion rule']),
  howTo: missingNeedles(docs.howTo, ['Checklist', 'Manifest task', 'Artifact', 'Non-claims', 'Impact map']),
  longRun: missingNeedles(docs.longRun, ['Findings', 'Testing optimization posture', 'Refactoring signals', 'Remaining risks'])
};
const impactTaskIds = new Set((impact.rules || []).flatMap((rule) => rule.taskIds || []));
const missingReleaseImpact = releaseTasks.map((task) => task.id).filter((id) => id !== 'cube:audit-surfaces' && !impactTaskIds.has(id));
const tinyEstimateProblems = tasks.filter((task) => task.estimatedMs < 100 || task.timeoutMs <= task.estimatedMs).map((task) => ({ id: task.id, estimatedMs: task.estimatedMs, timeoutMs: task.timeoutMs }));

const checks = [
  check('central-revision-alignment', Object.values(centralRevisions).every((rev) => rev === REVISION), { centralRevisions }),
  check('package-version-alignment', packageJson.version === VERSION, { packageVersion: packageJson.version, runtimeVersion: VERSION }),
  check('changelog-head-current', (text.get('CHANGELOG.md') || '').startsWith(`## ${REVISION} —`)),
  check('agents-current-codename', docs.agents.includes(`Current revision: ${REVISION}`) && docs.agents.includes(receipt.codename), { expectedCodename: receipt.codename }),
  check('readme-and-start-current-head', docs.readme.includes(`Current packaged head: \`${REVISION}\``) && docs.start.includes(`Current packaged head: \`${REVISION}\``)),
  check('context-pack-current', docs.context.startsWith(`# BrowserRT context pack — ${REVISION}`) && docs.context.includes('## Current non-claims')),
  check('future-session-handoff-legible', Object.values(handoffMissing).every((missing) => missing.length === 0), { handoffMissing }),
  check('manifest-unique-ids', duplicateTaskIds.length === 0, { duplicateTaskIds }),
  check('manifest-required-fields', missingManifestFields.length === 0, { missingManifestFields }),
  check('release-browser-light', releaseBrowserTasks.length === 0, { releaseBrowserTasks: releaseBrowserTasks.map((task) => task.id), browserTaskCount: browserTasks.length }),
  check('browser-serial-grouped', browserTasks.every((task) => task.parallelGroup === 'browser-process'), { browserTaskIds: browserTasks.map((task) => task.id) }),
  check('current-artifact-outputs', currentOutputProblems.length === 0, { currentOutputProblems }),
  check('artifact-retention-current-or-previous', oldArtifactPrefixes.length === 0, { oldArtifactPrefixes }),
  check('no-stale-currentness-markers', staleCurrentness.length === 0, { staleCurrentness }),
  check('release-estimate-contained', releaseEstimateMs > 0 && releaseEstimateMs <= 14000, { releaseEstimateMs, releaseTimeoutMs, browserEstimateMs }),
  check('estimate-timeout-sane', tinyEstimateProblems.length === 0, { tinyEstimateProblems }),
  check('impact-map-covers-release', missingReleaseImpact.length === 0, { missingReleaseImpact }),
  check('deep-audit-task-present', taskIds.includes('cube:deep-audit'))
];
const failed = checks.filter((row) => row.status !== 'passed');
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
  purpose: 'Deep office audit for future-session coherence: revision alignment, codename drift, handoff legibility, manifest metadata, browser-light release policy, artifact namespace hygiene, test estimates, impact coverage, and non-claim visibility.',
  counts: { fileCount: files.length, textFileCount: textRows.length, taskCount: tasks.length, releaseTaskCount: releaseTasks.length, browserTaskCount: browserTasks.length, currentArtifactCount: artifactPaths.filter((p) => p.includes(CURRENT_PREFIX)).length, previousArtifactCount: artifactPaths.filter((p) => p.includes(PREVIOUS_PREFIX)).length },
  checks,
  warnings: [
    browserEstimateMs > 20000 ? 'Browser tier remains intentionally outside broad release; run explicit ids.' : null,
    releaseEstimateMs > 10000 ? 'Release estimate is workable but high; prefer --id and --changed while iterating.' : null
  ].filter(Boolean),
  nonClaims: [
    'Deep cube audit does not prove BrowserRT runtime semantics.',
    'Deep cube audit does not prove browser provider behavior, performance, durability, or cross-browser conformance.',
    'Deep cube audit is a guard against cube/documentation/test-facility drift.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
