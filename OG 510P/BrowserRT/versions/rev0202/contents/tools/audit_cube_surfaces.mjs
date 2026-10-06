#!/usr/bin/env node
import { readdir, readFile, stat, writeFile, mkdir } from 'node:fs/promises';
import { dirname, relative } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-CUBE-AUDIT.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

async function walk(dir) {
  const rows = [];
  for (const ent of await readdir(dir, { withFileTypes: true })) {
    const p = `${dir}/${ent.name}`;
    if (ent.name === '.git' || ent.name === 'node_modules' || ent.name === '__pycache__' || ent.name === 'out') continue;
    if (ent.isDirectory()) rows.push(...await walk(p));
    else rows.push(p);
  }
  return rows;
}
async function readJson(path) { return JSON.parse(await readFile(path, 'utf8')); }
async function maybeReadJson(path) { try { return await readJson(path); } catch { return null; } }
function ok(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }

export async function runAudit() {
  const files = await walk('.');
  const textFiles = [];
  for (const file of files) {
    if (file.endsWith('.zip')) continue;
    try { textFiles.push([file, await readFile(file, 'utf8')]); } catch {}
  }
  const packageJson = await readJson('package.json');
  const receipt = await readJson('REVISION-RECEIPT.json');
  const reentry = await readJson('REENTRY-CONTRACT.json');
  const status = await readJson('SURFACE-STATUS.json');
  const validation = await readJson('VALIDATION-INDEX.json');
  const manifest = await readJson('test/manifest.json');
  const registry = await readJson('artifacts/research/RELATED-WORK-SOURCE-REGISTRY.json');
  const browserTasks = manifest.tasks.filter((task) => task.lane === 'browser');
  const releaseTasks = manifest.tasks.filter((task) => task.tiers.includes('release'));
  const releaseBrowserTasks = browserTasks.filter((task) => task.tiers.includes('release'));
  const browserSerialProblems = browserTasks.filter((task) => task.parallelGroup !== 'browser-process').map((task) => task.id);
  const releaseEstimateMs = releaseTasks.reduce((sum, task) => sum + (task.estimatedMs || 0), 0);
  const releaseBrowserTaskEstimateMs = releaseBrowserTasks.reduce((sum, task) => sum + (task.estimatedMs || 0), 0);
  const expectedArtifactOutputs = [...new Set(manifest.tasks.flatMap((task) => task.outputs || []).filter((out) => out.startsWith('artifacts/')))].sort();
  const artifactStatuses = [];
  for (const path of expectedArtifactOutputs) {
    const row = await maybeReadJson(path);
    artifactStatuses.push({ path, exists: Boolean(row), revision: row?.revision ?? null, status: row?.status || (row ? 'present' : 'missing') });
  }
  const textByPath = new Map(textFiles.map(([file, txt]) => [relative('.', file), txt]));
  const currentnessScanPaths = [
    'README.md', 'START_HERE.md', 'CONTEXT-PACK.md', 'AGENTS.md',
    'docs/00-meta/future-session-office-manual.md', 'docs/00-meta/non-claims-and-goals-charter.md',
    'docs/40-validation/browser-opfs-restart-persistence-slice.md', 'docs/40-validation/browser-web-locks-coordination-slice.md'
  ];
  const staleCurrentness = currentnessScanPaths.flatMap((rel) => {
    const txt = textByPath.get(rel) || '';
    const hits = [];
    for (const match of txt.matchAll(/Current revision:\s+(rev\d{4})/g)) if (match[1] !== REVISION) hits.push(match[0]);
    for (const match of txt.matchAll(/Current packaged head:\s+`(rev\d{4})`/g)) if (match[1] !== REVISION) hits.push(match[0]);
    return hits.length ? [{ file: rel, hits: [...new Set(hits)] }] : [];
  });
  const currentOutputViolations = [];
  for (const task of manifest.tasks) {
    for (const output of task.outputs || []) if (/artifacts\/(audit|proof|validation)\/REV\d{4}-/.test(output) && !output.includes(PREFIX)) currentOutputViolations.push({ task: task.id, output });
    const cmd = (task.command || []).join(' ');
    for (const hit of cmd.match(/REV\d{4}-/g) || []) if (hit !== `${PREFIX}-`) currentOutputViolations.push({ task: task.id, commandHit: hit });
  }
  const requiredTaskIds = ['ipc:persisted-spill-recovery-proof', 'ipc:spill-mailbox-fake-proof', 'scheduler:priority-fairness-proof', 'cube:deep-audit', 'facility:foundation-audit', 'browser:opfs-restart-persistence-proof', 'browser:web-locks-coordination-proof', 'cube:artifact-budget-audit'];
  const taskIds = new Set(manifest.tasks.map((task) => task.id));
  const missingRequiredTasks = requiredTaskIds.filter((id) => !taskIds.has(id));
  const requiredSourceTitles = ['Redis Streams Pending Entries List', 'NATS JetStream persistence and consumers', 'PostgreSQL Write-Ahead Logging', 'Apache Flink state backends and checkpointing'];
  const titles = registry.families.flatMap((family) => family.sources || []).map((source) => source.title);
  const missingSourceTitles = requiredSourceTitles.filter((title) => !titles.includes(title));
  const checks = [
    ok('core-json-revision-alignment', [receipt, reentry, status, validation, manifest, registry].every((obj) => obj.revision === REVISION), { revisions: { receipt: receipt.revision, reentry: reentry.revision, status: status.revision, validation: validation.revision, manifest: manifest.revision, registry: registry.revision } }),
    ok('package-version-alignment', packageJson.version === VERSION, { packageVersion: packageJson.version, runtimeVersion: VERSION }),
    ok('no-stale-currentness-markers', staleCurrentness.length === 0, { staleCurrentness }),
    ok('current-output-prefixes', currentOutputViolations.length === 0, { currentOutputViolations }),
    ok('browser-tasks-serial-grouped', browserSerialProblems.length === 0, { browserSerialProblems, browserTaskCount: browserTasks.length }),
    ok('browser-release-cost-contained', releaseBrowserTaskEstimateMs === 0 && releaseEstimateMs > 0, { releaseBrowserTaskEstimateMs, releaseEstimateMs }),
    ok('required-current-tasks-present', missingRequiredTasks.length === 0, { missingRequiredTasks }),
    ok('persisted-spill-research-registered', missingSourceTitles.length === 0, { missingSourceTitles }),
    ok('no-external-dependencies', Object.keys(packageJson.dependencies || {}).length === 0 && Object.keys(packageJson.devDependencies || {}).length === 0)
  ];
  const warnings = [];
  const missingReleaseArtifacts = artifactStatuses.filter((row) => row.exists === false && !row.path.includes('BROWSER-'));
  if (missingReleaseArtifacts.length) warnings.push(`missing non-browser artifacts before package validation: ${missingReleaseArtifacts.map((row) => row.path).slice(0, 5).join(', ')}`);
  if (releaseEstimateMs > 14000) warnings.push('release estimate is high; use --id/--changed while iterating');
  const failed = checks.filter((check) => check.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 2,
    status: failed.length === 0 ? 'passed' : 'failed', generatedAt: new Date().toISOString(),
    purpose: 'Audit current cube surfaces for revision alignment, stale currentness, current artifact output prefixes, browser task serial grouping, browser-light release cost, persisted-spill recovery registration, current browser-storage/coordination proofs, artifact-budget audit registration, and dependency drift.',
    counts: { fileCount: files.length, textFileCount: textFiles.length, releaseTaskCount: releaseTasks.length, browserTaskCount: browserTasks.length, expectedArtifactOutputCount: expectedArtifactOutputs.length },
    checks,
    warnings,
    artifactStatuses,
    nonClaims: [
      'Audit is a cube-surface sanity check, not a semantic proof of BrowserRT correctness.',
      'Audit does not prove cross-browser behavior, OPFS durability, or real performance.',
      'Audit intentionally treats browser proof artifacts as explicit-tier evidence, not broad release requirements.'
    ]
  };
}

const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
const report = await runAudit();
if (out) {
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  console.log(out);
} else {
  console.log(JSON.stringify(report, null, 2));
}
if (report.status !== 'passed') process.exitCode = 1;
