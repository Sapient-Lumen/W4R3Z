#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { cp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join, relative, resolve } from 'node:path';
import { performance } from 'node:perf_hooks';
import { tmpdir } from 'node:os';
import { estimatePlan, selectTasks, summarizeResults, validateImpactMap, validateManifest } from '../src/test-facility.mjs';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const DEFAULT_MANIFEST = 'test/manifest.json';
const DEFAULT_IMPACT_MAP = 'test/impact-map.json';
const DEFAULT_JSON = `artifacts/validation/REV${REVISION.slice(3)}-TEST-HARNESS-RUN.json`;
const DEFAULT_CHUNK_DIR = `artifacts/validation/REV${REVISION.slice(3)}-TEST-HARNESS-RUN.checkpoints/release-chunks`;

function parseArgs(argv) {
  const out = {
    tier: 'release',
    shards: 4,
    jobs: '1',
    json: DEFAULT_JSON,
    chunkDir: DEFAULT_CHUNK_DIR,
    manifest: DEFAULT_MANIFEST,
    impactMap: DEFAULT_IMPACT_MAP,
    quiet: false,
    includeQuarantined: false,
    failFast: false,
    budgetMs: 0,
    chunkTimeoutMs: 180000,
    isolateWorkspaces: true,
    aggregateOnly: false,
    scratchRoot: tmpdir(),
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--tier') out.tier = argv[++i];
    else if (arg === '--shards') out.shards = Number(argv[++i]);
    else if (arg === '--jobs') out.jobs = argv[++i];
    else if (arg === '--json') out.json = argv[++i];
    else if (arg === '--chunk-dir') out.chunkDir = argv[++i];
    else if (arg === '--manifest') out.manifest = argv[++i];
    else if (arg === '--impact-map') out.impactMap = argv[++i];
    else if (arg === '--budget-ms') out.budgetMs = Number(argv[++i]);
    else if (arg === '--chunk-timeout-ms') out.chunkTimeoutMs = Number(argv[++i]);
    else if (arg === '--scratch-root') out.scratchRoot = argv[++i];
    else if (arg === '--no-isolate-workspaces') out.isolateWorkspaces = false;
    else if (arg === '--aggregate-only') out.aggregateOnly = true;
    else if (arg === '--quiet') out.quiet = true;
    else if (arg === '--include-quarantined') out.includeQuarantined = true;
    else if (arg === '--fail-fast') out.failFast = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  if (!Number.isInteger(out.shards) || out.shards < 2 || out.shards > 16) throw new Error('--shards must be an integer from 2 through 16');
  if (!Number.isFinite(out.budgetMs) || out.budgetMs < 0) throw new Error('--budget-ms must be a non-negative number');
  if (!Number.isFinite(out.chunkTimeoutMs) || out.chunkTimeoutMs < 1000) throw new Error('--chunk-timeout-ms must be at least 1000');
  return out;
}

function truncate(text, limit = 2000) {
  if (!text) return '';
  if (text.length <= limit) return text;
  return `${text.slice(0, limit)}\n... truncated ${text.length - limit} bytes ...`;
}

async function readJson(path) {
  return JSON.parse(await readFile(path, 'utf8'));
}

function shouldCopyPath(sourceRoot, sourcePath) {
  const rel = relative(sourceRoot, sourcePath).replace(/\\+/g, '/');
  if (!rel || rel === '.') return true;
  const parts = rel.split('/');
  if (parts.some((part) => part === '.git' || part === 'node_modules' || part === 'out' || part === '__pycache__')) return false;
  if (rel.endsWith('.zip') || rel.endsWith('.tgz') || rel.endsWith('.pyc')) return false;
  return true;
}

async function prepareChunkWorkspace(options, index) {
  const sourceRoot = resolve('.');
  if (!options.isolateWorkspaces) return { cwd: sourceRoot, cleanup: async () => {}, isolated: false };
  const base = join(resolve(options.scratchRoot), `browserrt-release-chunks-${process.pid}`);
  await mkdir(base, { recursive: true });
  const cwd = join(base, `chunk-${String(index).padStart(2, '0')}`);
  await rm(cwd, { recursive: true, force: true });
  await cp(sourceRoot, cwd, {
    recursive: true,
    verbatimSymlinks: true,
    filter: (src) => shouldCopyPath(sourceRoot, src),
  });
  return { cwd, cleanup: async () => { await rm(cwd, { recursive: true, force: true }); }, isolated: true };
}

async function runCommand(args, { quiet = false, timeoutMs = 180000, cwd = resolve('.') } = {}) {
  const started = performance.now();
  const child = spawnSync(process.execPath, args, {
    cwd,
    encoding: 'utf8',
    stdio: quiet ? 'ignore' : ['ignore', 'pipe', 'pipe'],
    timeout: timeoutMs,
  });
  const durationMs = Math.round(performance.now() - started);
  const stdout = truncate(child.stdout || '');
  const stderr = truncate((child.stderr || '') + (child.error ? `\n${child.error.stack || child.error.message}` : ''));
  if (!quiet && stdout.trim()) process.stdout.write(stdout);
  if (!quiet && stderr.trim()) process.stderr.write(stderr);
  const timedOut = child.error?.code === 'ETIMEDOUT';
  return {
    status: child.status === 0 && !timedOut ? 'passed' : 'failed',
    exitCode: child.status,
    signal: child.signal,
    timedOut,
    stdout,
    stderr,
    durationMs,
  };
}

function duplicateIds(ids) {
  const seen = new Set();
  const dupes = new Set();
  for (const id of ids) {
    if (seen.has(id)) dupes.add(id);
    seen.add(id);
  }
  return [...dupes].sort();
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const manifest = await readJson(options.manifest);
  const impactMap = await readJson(options.impactMap);
  const surfaceErrors = [
    ...validateManifest(manifest, { currentRevision: REVISION }),
    ...validateImpactMap(impactMap, manifest, { currentRevision: REVISION }),
  ];
  if (surfaceErrors.length) throw new Error(`test surfaces invalid:\n${surfaceErrors.map((e) => `- ${e}`).join('\n')}`);

  const plannedTasks = selectTasks(manifest, { tier: options.tier, includeQuarantined: options.includeQuarantined });
  const expectedTaskIds = plannedTasks.map((task) => task.id).sort();
  const expectedSet = new Set(expectedTaskIds);
  const chunkDir = options.chunkDir;
  await mkdir(chunkDir, { recursive: true });
  const started = performance.now();
  const chunks = [];
  const tasks = [];

  for (let index = 1; index <= options.shards; index += 1) {
    const shard = `${index}/${options.shards}`;
    const chunkJson = `${chunkDir}/chunk-${String(index).padStart(2, '0')}-of-${String(options.shards).padStart(2, '0')}.json`;
    const args = [
      'tools/run_tests.mjs', '--tier', options.tier, '--shard', shard,
      '--jobs', String(options.jobs), '--quiet', '--json', chunkJson,
      '--manifest', options.manifest, '--impact-map', options.impactMap,
    ];
    if (options.includeQuarantined) args.push('--include-quarantined');
    if (!options.quiet) console.log(`[run_release_chunks] ${options.aggregateOnly ? 'read' : 'start'} shard ${shard}`);
    let child = { status: 'passed', durationMs: 0, exitCode: 0, signal: null, stdout: '', stderr: '', timedOut: false };
    let report = null;
    if (options.aggregateOnly) {
      try { report = await readJson(chunkJson); }
      catch (error) { child = { ...child, status: 'failed', exitCode: 1, stderr: `missing chunk report ${chunkJson}: ${error.message}` }; }
    } else {
      const workspace = await prepareChunkWorkspace(options, index);
      child = await runCommand(args, { quiet: options.quiet, timeoutMs: options.chunkTimeoutMs, cwd: workspace.cwd });
      try {
        const sourceReport = workspace.isolated ? join(workspace.cwd, chunkJson) : chunkJson;
        report = await readJson(sourceReport);
        if (workspace.isolated) await writeFile(chunkJson, JSON.stringify(report, null, 2) + '\n');
      } catch {}
      await workspace.cleanup();
    }
    const reportTasks = Array.isArray(report?.tasks) ? report.tasks : [];
    tasks.push(...reportTasks);
    const chunk = {
      index,
      shard,
      status: child.status === 'passed' && report?.status === 'passed' ? 'passed' : 'failed',
      json: chunkJson,
      durationMs: child.durationMs,
      exitCode: child.exitCode,
      signal: child.signal,
      reportStatus: report?.status || null,
      taskCount: reportTasks.length,
      passedCount: report?.passedCount ?? reportTasks.filter((task) => task.status === 'passed').length,
      failedCount: report?.failedCount ?? reportTasks.filter((task) => task.status !== 'passed').length,
      stdout: child.status === 'passed' ? undefined : child.stdout,
      stderr: child.status === 'passed' ? undefined : child.stderr,
    };
    chunks.push(chunk);
    if (!options.quiet) console.log(`[run_release_chunks] ${chunk.status} shard ${shard} ${chunk.passedCount}/${chunk.taskCount} passed in ${chunk.durationMs}ms`);
    if (options.failFast && chunk.status !== 'passed') break;
  }

  tasks.sort((a, b) => String(a.id).localeCompare(String(b.id)));
  const actualTaskIds = tasks.map((task) => task.id).sort();
  const actualSet = new Set(actualTaskIds);
  const missingTaskIds = expectedTaskIds.filter((id) => !actualSet.has(id));
  const unexpectedTaskIds = actualTaskIds.filter((id) => !expectedSet.has(id));
  const duplicateTaskIds = duplicateIds(actualTaskIds);
  const failed = tasks.filter((task) => task.status !== 'passed');
  const durationMs = Math.round(performance.now() - started);
  const budgetExceeded = options.budgetMs > 0 && durationMs > options.budgetMs;
  const chunkFailures = chunks.filter((chunk) => chunk.status !== 'passed');
  const status = failed.length === 0 && chunkFailures.length === 0 && missingTaskIds.length === 0 && unexpectedTaskIds.length === 0 && duplicateTaskIds.length === 0 && !budgetExceeded ? 'passed' : 'failed';

  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION,
    harness: 'BrowserRT cloudtainer release chunk runner', schema: 2,
    status,
    generatedAt: new Date().toISOString(),
    options: {
      tier: options.tier,
      ids: [],
      tag: null,
      shard: `chunked/${options.shards}`,
      changedFiles: [],
      changedTaskIds: [],
      jobs: options.jobs,
      effectiveJobs: null,
      failFast: options.failFast,
      budgetMs: options.budgetMs,
      chunkTimeoutMs: options.chunkTimeoutMs,
      isolateWorkspaces: options.isolateWorkspaces,
      aggregateOnly: options.aggregateOnly,
      includeQuarantined: options.includeQuarantined,
      onlyAffected: false,
    },
    impact: { changedFiles: [], matchedRuleCount: 0, matchedRules: [], taskIds: [] },
    plan: estimatePlan(plannedTasks),
    durationMs,
    budgetExceeded,
    timingSummary: summarizeResults(plannedTasks, tasks),
    passedCount: tasks.length - failed.length,
    failedCount: failed.length,
    tasks,
    chunks,
    releaseChunkRunner: {
      schema: 1,
      shards: options.shards,
      chunkDir,
      expectedTaskCount: expectedTaskIds.length,
      actualTaskCount: actualTaskIds.length,
      missingTaskIds,
      unexpectedTaskIds,
      duplicateTaskIds,
      chunkFailureCount: chunkFailures.length,
      isolateWorkspaces: options.isolateWorkspaces,
      aggregateOnly: options.aggregateOnly,
      nonClaims: [
        'Chunked execution preserves release task coverage and pass/fail aggregation; it is not a performance benchmark.',
        'Chunking does not change Web Locks, OPFS, quota, eviction, crash, or cross-browser behavior claims.'
      ],
    },
  };

  if (options.json) {
    await mkdir(dirname(options.json), { recursive: true });
    await writeFile(options.json, JSON.stringify(report, null, 2) + '\n');
  }
  if (!options.quiet) console.log(`[run_release_chunks] summary ${status}: ${report.passedCount}/${tasks.length} passed across ${chunks.length}/${options.shards} chunks in ${durationMs}ms`);
  if (status !== 'passed') process.exitCode = 1;
}

main().catch((error) => {
  console.error(`[run_release_chunks] FAIL: ${error.stack || error.message}`);
  process.exitCode = 1;
});
