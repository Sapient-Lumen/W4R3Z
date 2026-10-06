#!/usr/bin/env node
import { readFile, readdir, mkdir, writeFile, stat } from 'node:fs/promises';
import { dirname, relative } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const PREVIOUS_REV = `rev${String(Number(REVISION.slice(3)) - 1).padStart(4, '0')}`;
const PREVIOUS_PREFIX = `REV${PREVIOUS_REV.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-FOUNDATION-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

async function readText(path) { return await readFile(path, 'utf8'); }
async function readJson(path) { return JSON.parse(await readText(path)); }
async function exists(path) { try { await stat(path); return true; } catch { return false; } }

async function walk(dir) {
  const rows = [];
  for (const ent of await readdir(dir, { withFileTypes: true })) {
    if (ent.name === '.git' || ent.name === 'node_modules' || ent.name === '__pycache__' || ent.name === 'out') continue;
    const p = `${dir}/${ent.name}`;
    if (ent.isDirectory()) rows.push(...await walk(p));
    else rows.push(p.replace(/^\.\//, ''));
  }
  return rows.sort();
}

function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function unique(values) { return [...new Set(values)]; }

function commandString(task) { return (task.command || []).join(' '); }

function taskMap(manifest) { return new Map((manifest.tasks || []).map((task) => [task.id, task])); }

export async function runFoundationAudit() {
  const files = await walk('.');
  const packageJson = await readJson('package.json');
  const cubeMeta = await readJson('CUBE-META.json');
  const receipt = await readJson('REVISION-RECEIPT.json');
  const reentry = await readJson('REENTRY-CONTRACT.json');
  const surface = await readJson('SURFACE-STATUS.json');
  const validation = await readJson('VALIDATION-INDEX.json');
  const manifest = await readJson('test/manifest.json');
  const impact = await readJson('test/impact-map.json');
  const inventory = await readJson('test/surface-inventory.json');
  const quarantine = await readJson('test/quarantine.json');
  const tasks = manifest.tasks || [];
  const byId = taskMap(manifest);
  const releaseTasks = tasks.filter((task) => (task.tiers || []).includes('release'));
  const browserTasks = tasks.filter((task) => task.lane === 'browser');
  const releaseBrowserTasks = releaseTasks.filter((task) => task.lane === 'browser');
  const releaseEstimateMs = releaseTasks.reduce((sum, task) => sum + (task.estimatedMs || 0), 0);
  const releaseTimeoutMs = releaseTasks.reduce((sum, task) => sum + (task.timeoutMs || 0), 0);
  const duplicateTaskIds = tasks.map((task) => task.id).filter((id, i, arr) => arr.indexOf(id) !== i);
  const missingImpactTaskIds = unique((impact.rules || []).flatMap((rule) => rule.taskIds || []).filter((id) => !byId.has(id)));
  const currentOutputViolations = tasks.flatMap((task) => (task.outputs || []).filter((out) => out.startsWith('artifacts/') && !out.includes(PREFIX)).map((out) => ({ task: task.id, out })));
  const timeoutProblems = tasks.filter((task) => Number(task.timeoutMs || 0) <= Number(task.estimatedMs || 0)).map((task) => ({ id: task.id, estimatedMs: task.estimatedMs, timeoutMs: task.timeoutMs }));
  const missingFields = tasks.filter((task) => !(task.id && task.command?.length && task.tiers?.length && task.tags?.length && task.areas?.length && task.lane && task.parallelGroup && task.size && task.isolation && task.flakiness && Number.isFinite(task.risk) && Number.isFinite(task.estimatedMs) && Number.isFinite(task.timeoutMs) && task.capabilities?.length && task.cachePolicy)).map((task) => task.id);
  const browserGroupingProblems = browserTasks.filter((task) => task.parallelGroup !== 'browser-process' || (task.tiers || []).includes('release')).map((task) => task.id);
  const releaseHugeTasks = releaseTasks.filter((task) => (task.estimatedMs || 0) > 1000).map((task) => ({ id: task.id, estimatedMs: task.estimatedMs }));
  const artifactFiles = files.filter((f) => f.startsWith('artifacts/'));
  const staleCurrentArtifacts = artifactFiles.filter((f) => /REV\d{4}/.test(f) && !f.includes(PREFIX) && !f.includes(PREVIOUS_PREFIX));
  const artifactBudgetBytes = (await Promise.all(artifactFiles.map(async (f) => (await stat(f)).size))).reduce((a, b) => a + b, 0);
  const docs = {
    start: await readText('START_HERE.md'),
    context: await readText('CONTEXT-PACK.md'),
    future: await readText('docs/00-meta/future-session-office-manual.md'),
    charter: await readText('docs/00-meta/non-claims-and-goals-charter.md'),
    testArchitecture: await readText('docs/40-validation/test-facility-architecture.md'),
    artifactPolicy: await readText('docs/40-validation/test-artifact-policy.md'),
    newSliceChecklist: await readText('docs/40-validation/new-slice-checklist.md').catch?.(() => '') ?? ''
  };
  const docsText = Object.values(docs).join('\n');
  const requiredDocNeedles = [
    'browser-light',
    'no cross-browser conformance',
    'No WebGPU proof',
    'manifest task',
    'artifact',
    'non-claims',
    'make turn-start',
    'persisted-spill recovery'
  ];
  const missingDocNeedles = requiredDocNeedles.filter((needle) => !docsText.includes(needle));
  const affectedArtifactPath = `artifacts/validation/${PREFIX}-AFFECTED-RUNNER-DRYRUN.json`;
  let affectedDryRun = null;
  if (await exists(affectedArtifactPath)) affectedDryRun = await readJson(affectedArtifactPath);
  const affectedSelectedIds = affectedDryRun?.selectedTasks?.map((task) => task.id) || [];
  const expectedAffectedIds = ['facility:plan-sanity', 'harness:selftest', 'ipc:sab-ring-proof', 'ipc:sab-frame-ring-proof', 'ipc:sab-frame-model-proof', 'ipc:spill-mailbox-fake-proof', 'scheduler:adaptive-concurrency-proof', 'scheduler:priority-fairness-proof', 'storage:journal-recovery-proof'];
  const missingAffectedIds = expectedAffectedIds.filter((id) => !affectedSelectedIds.includes(id));
  const checks = [
    check('core-revision-alignment', [cubeMeta, receipt, reentry, surface, validation, manifest, impact, inventory, quarantine].every((obj) => obj.revision === REVISION), { revision: REVISION }),
    check('package-version-alignment', packageJson.version === VERSION && cubeMeta.version === VERSION, { packageVersion: packageJson.version, runtimeVersion: VERSION, cubeMetaVersion: cubeMeta.version }),
    check('unique-task-ids', duplicateTaskIds.length === 0, { duplicateTaskIds }),
    check('impact-map-task-ids-exist', missingImpactTaskIds.length === 0, { missingImpactTaskIds }),
    check('task-metadata-complete', missingFields.length === 0, { missingFields }),
    check('task-timeout-exceeds-estimate', timeoutProblems.length === 0, { timeoutProblems }),
    check('release-browser-light', releaseBrowserTasks.length === 0, { releaseBrowserTasks: releaseBrowserTasks.map((task) => task.id), releaseEstimateMs, releaseTimeoutMs }),
    check('browser-tasks-explicit-and-serial', browserGroupingProblems.length === 0, { browserGroupingProblems }),
    check('current-output-prefixes', currentOutputViolations.length === 0, { currentOutputViolations }),
    check('current-artifact-retention', staleCurrentArtifacts.length === 0, { currentPrefix: PREFIX, previousPrefix: PREVIOUS_PREFIX, staleCurrentArtifacts: staleCurrentArtifacts.slice(0, 40), staleCurrentArtifactCount: staleCurrentArtifacts.length, artifactBudgetBytes }),
    check('future-session-doc-needles', missingDocNeedles.length === 0, { missingDocNeedles }),
    check('affected-runner-dryrun-nonempty', Boolean(affectedDryRun) && affectedDryRun.status === 'passed' && affectedSelectedIds.length > 0 && missingAffectedIds.length === 0, { artifact: affectedArtifactPath, selectedCount: affectedSelectedIds.length, missingAffectedIds }),
    check('no-external-dependencies', Object.keys(packageJson.dependencies || {}).length === 0 && Object.keys(packageJson.devDependencies || {}).length === 0),
    check('next-slice-reminder-preserved', (() => { const text = JSON.stringify([cubeMeta, reentry, surface, validation]).toLowerCase(); return text.includes('cross-lane scheduler') && text.includes('persisted-spill'); })())
  ];
  const warnings = [];
  if (releaseEstimateMs > 12000) warnings.push('release estimate exceeds 12s; consider moving non-current semantic proofs to audit/full or splitting release shards');
  if (releaseHugeTasks.length) warnings.push(`release has >1s tasks: ${releaseHugeTasks.map((x) => `${x.id}:${x.estimatedMs}`).join(', ')}`);
  if (artifactBudgetBytes > 600_000) warnings.push(`artifact budget is ${artifactBudgetBytes} bytes; revisit retention if the zip grows too fast`);
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    generatedAt: new Date().toISOString(),
    status: failed.length ? 'failed' : 'passed',
    purpose: 'Deep foundation audit for future-session coherence, test-facility fitness, artifact hygiene, affected-runner correctness, non-claim legibility, and browser-light release posture.',
    counts: { fileCount: files.length, artifactFileCount: artifactFiles.length, taskCount: tasks.length, releaseTaskCount: releaseTasks.length, browserTaskCount: browserTasks.length },
    releaseEconomics: { releaseEstimateMs, releaseTimeoutMs, releaseTaskIds: releaseTasks.map((task) => task.id), releaseHugeTasks },
    affectedRunnerDryRun: affectedDryRun ? { status: affectedDryRun.status, selectedTaskIds: affectedSelectedIds, taskCount: affectedSelectedIds.length, artifact: affectedArtifactPath } : { status: 'missing', artifact: affectedArtifactPath },
    checks,
    warnings,
    nonClaims: [
      'Foundation audit is a guardrail proof, not a proof of BrowserRT semantic correctness.',
      'Foundation audit does not prove browser correctness, cross-browser conformance, durability, or performance.',
      'Passing release still means browser-light release; browser/CDP slices remain explicit.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runFoundationAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
if (report.status !== 'passed') process.exitCode = 1;
