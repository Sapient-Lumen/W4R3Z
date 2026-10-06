#!/usr/bin/env node
import { availableParallelism } from 'node:os';
import { spawn } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { performance } from 'node:perf_hooks';
import { appendTimingHistory, estimatePlan, explainImpact, impactedTaskIds, normalizeChangedFiles, selectTasks, summarizeResults, validateImpactMap, validateManifest } from '../src/test-facility.mjs';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const DEFAULT_MANIFEST = 'test/manifest.json';
const DEFAULT_IMPACT_MAP = 'test/impact-map.json';

function parseArgs(argv) {
  const out = { tier: 'release', ids: [], tag: null, shard: 'all', jobs: 'auto', json: null, history: null, list: false, explain: false, dryRun: false, failFast: false, budgetMs: 0, manifest: DEFAULT_MANIFEST, impactMap: DEFAULT_IMPACT_MAP, changed: '', changedFile: null, quiet: false, includeQuarantined: false, onlyAffected: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--tier') out.tier = argv[++i];
    else if (arg === '--id') out.ids.push(...String(argv[++i]).split(',').filter(Boolean));
    else if (arg === '--tag') out.tag = argv[++i];
    else if (arg === '--shard') out.shard = argv[++i];
    else if (arg === '--jobs') out.jobs = argv[++i];
    else if (arg === '--json') out.json = argv[++i];
    else if (arg === '--history') out.history = argv[++i];
    else if (arg === '--manifest') out.manifest = argv[++i];
    else if (arg === '--impact-map') out.impactMap = argv[++i];
    else if (arg === '--changed') out.changed = argv[++i];
    else if (arg === '--changed-file') out.changedFile = argv[++i];
    else if (arg === '--budget-ms') out.budgetMs = Number(argv[++i]);
    else if (arg === '--list') out.list = true;
    else if (arg === '--explain') out.explain = true;
    else if (arg === '--dry-run') out.dryRun = true;
    else if (arg === '--only-affected') out.onlyAffected = true;
    else if (arg === '--fail-fast') out.failFast = true;
    else if (arg === '--quiet') out.quiet = true;
    else if (arg === '--include-quarantined') out.includeQuarantined = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  return out;
}

function jobCount(value) {
  if (value === 'auto') return Math.max(1, Math.min(4, (availableParallelism?.() || 2) - 1));
  const n = Number(value);
  if (!Number.isInteger(n) || n < 1) throw new Error(`Bad --jobs value: ${value}`);
  return n;
}

function commandString(task) {
  return task.command.map((part) => /\s/.test(part) ? JSON.stringify(part) : part).join(' ');
}

function truncate(text, limit = 2000) {
  if (!text) return '';
  if (text.length <= limit) return text;
  return text.slice(0, limit) + `\n... truncated ${text.length - limit} bytes ...`;
}

function signalTaskProcess(child, signal) {
  if (process.platform !== 'win32' && child.pid) {
    try {
      process.kill(-child.pid, signal);
      return;
    } catch {}
  }
  try { child.kill(signal); } catch {}
}

function runTask(task) {
  return new Promise((resolveTask) => {
    const started = performance.now();
    const [cmd, ...args] = task.command;
    let stdout = '';
    let stderr = '';
    let timedOut = false;
    let settled = false;
    let exitFallbackTimer = null;
    let timeoutKillTimer = null;
    let hardTimeoutTimer = null;
    const child = spawn(cmd, args, { cwd: resolve('.'), stdio: ['ignore', 'pipe', 'pipe'], detached: process.platform !== 'win32' });
    const finish = ({ code, signal, statusOverride = null, stderrSuffix = '' }) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (exitFallbackTimer) clearTimeout(exitFallbackTimer);
      if (timeoutKillTimer) clearTimeout(timeoutKillTimer);
      if (hardTimeoutTimer) clearTimeout(hardTimeoutTimer);
      const ended = performance.now();
      resolveTask({ id: task.id, status: statusOverride || (code === 0 && !timedOut ? 'passed' : 'failed'), exitCode: code, signal, timedOut, durationMs: Math.round(ended - started), estimatedMs: task.estimatedMs, command: commandString(task), stdout: truncate(stdout), stderr: truncate(stderr + stderrSuffix) });
    };
    const timeoutMs = task.timeoutMs || 30000;
    const timer = setTimeout(() => {
      timedOut = true;
      signalTaskProcess(child, 'SIGTERM');
      timeoutKillTimer = setTimeout(() => signalTaskProcess(child, 'SIGKILL'), 500);
      timeoutKillTimer.unref?.();
      hardTimeoutTimer = setTimeout(() => {
        signalTaskProcess(child, 'SIGKILL');
        finish({ code: null, signal: 'SIGKILL', statusOverride: 'failed', stderrSuffix: `
[run_tests] hard timeout after ${timeoutMs}ms; process group did not exit` });
      }, 2500);
      hardTimeoutTimer.unref?.();
    }, timeoutMs);
    child.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
    child.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
    child.on('error', (error) => {
      finish({ code: null, signal: null, statusOverride: 'failed', stderrSuffix: `\n${error.stack || error.message}` });
    });
    child.on('exit', (code, signal) => {
      // Some browser-heavy probes can let a grandchild briefly inherit stdio,
      // which prevents Node's `close` event from firing even though the task
      // process has exited. Treat a clean process exit as authoritative after a
      // short grace period so the test harness cannot hang on stale pipes.
      exitFallbackTimer = setTimeout(() => {
        finish({ code, signal, stderrSuffix: '\n[run_tests] stdio close fallback after child exit' });
      }, task.stdioCloseGraceMs || 1000);
      exitFallbackTimer.unref?.();
    });
    child.on('close', (code, signal) => {
      finish({ code, signal });
    });
  });
}

async function runTasks(tasks, options) {
  const jobs = jobCount(options.jobs);
  const queue = tasks.slice();
  const activeGroups = new Set();
  const results = [];
  let active = 0;
  let failed = false;
  return await new Promise((resolveRun) => {
    const pump = () => {
      if ((options.failFast && failed) && active === 0) return resolveRun(results);
      while (active < jobs && queue.length && !(options.failFast && failed)) {
        const idx = queue.findIndex((task) => !task.parallelGroup || !activeGroups.has(task.parallelGroup));
        if (idx === -1) break;
        const [task] = queue.splice(idx, 1);
        active += 1;
        if (task.parallelGroup) activeGroups.add(task.parallelGroup);
        if (!options.quiet) console.log(`[run_tests] start ${task.id} :: ${commandString(task)}`);
        runTask(task).then((result) => {
          active -= 1;
          if (task.parallelGroup) activeGroups.delete(task.parallelGroup);
          results.push(result);
          if (!options.quiet) console.log(`[run_tests] ${result.status} ${task.id} ${result.durationMs}ms`);
          if (result.status !== 'passed') failed = true;
          if (queue.length === 0 && active === 0) return resolveRun(results);
          pump();
        });
      }
      if (queue.length === 0 && active === 0) return resolveRun(results);
    };
    pump();
  });
}

async function readJsonMaybe(path) {
  try { return JSON.parse(await readFile(path, 'utf8')); } catch { return null; }
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const manifest = JSON.parse(await readFile(options.manifest, 'utf8'));
  const impactMap = JSON.parse(await readFile(options.impactMap, 'utf8'));
  const errors = [...validateManifest(manifest, { currentRevision: REVISION }), ...validateImpactMap(impactMap, manifest, { currentRevision: REVISION })];
  if (errors.length) throw new Error('test surfaces invalid:\n' + errors.map((e) => `- ${e}`).join('\n'));
  let changedFiles = normalizeChangedFiles(options.changed);
  if (options.changedFile) changedFiles = changedFiles.concat(normalizeChangedFiles(await readFile(options.changedFile, 'utf8')));
  const impact = explainImpact(impactMap, changedFiles);
  const changedTaskIds = changedFiles.length ? impactedTaskIds(impactMap, changedFiles) : [];
  const ids = [...new Set([...options.ids, ...changedTaskIds])];
  if (options.onlyAffected && changedFiles.length === 0 && options.ids.length === 0) {
    throw new Error('--only-affected requires --changed, --changed-file, or --id');
  }
  // Important: keep changedTaskIds in the selector. If we only copy impacted ids
  // into --id and also pass changedFiles, impacted tasks whose own input globs do
  // not match the changed harness file can be filtered out. This made
  // `--only-affected --changed tools/run_tests.mjs` plan an empty run in rev0025.
  const tasks = selectTasks(manifest, { ...options, ids, changedTaskIds: ids.length ? ids : changedTaskIds });
  const plan = estimatePlan(tasks);
  const selectedTaskIds = new Set(tasks.map((task) => task.id));
  const missingExplicitIds = [...new Set(options.ids)].filter((id) => !selectedTaskIds.has(id));
  const explicitSelectionFailed = missingExplicitIds.length > 0;
  const planStatus = explicitSelectionFailed ? 'failed' : (tasks.length ? 'passed' : 'empty');
  const planOnly = {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 3,
    generatedAt: new Date().toISOString(), status: planStatus,
    options: { tier: options.tier, ids, explicitIds: options.ids, missingExplicitIds, tag: options.tag, shard: options.shard, changedFiles, changedTaskIds, jobs: options.jobs, effectiveJobs: jobCount(options.jobs), onlyAffected: options.onlyAffected },
    impact, plan,
    selectedTasks: tasks.map((task) => ({ id: task.id, lane: task.lane, size: task.size, risk: task.risk, estimatedMs: task.estimatedMs, timeoutMs: task.timeoutMs, command: commandString(task) }))
  };
  if (explicitSelectionFailed) {
    if (options.json) {
      await mkdir(dirname(options.json), { recursive: true });
      await writeFile(options.json, JSON.stringify(planOnly, null, 2) + '\n');
    }
    console.error(`[run_tests] FAIL: explicit --id selection matched no task for tier ${options.tier}: ${missingExplicitIds.join(', ')}`);
    process.exitCode = 1;
    return;
  }
  if (options.list) {
    for (const task of tasks) console.log(`${task.id}\t${task.lane}\t${task.size}\t${task.estimatedMs}ms\t${commandString(task)}`);
    return;
  }
  if (options.explain || options.dryRun) {
    if (options.json) {
      await mkdir(dirname(options.json), { recursive: true });
      await writeFile(options.json, JSON.stringify(planOnly, null, 2) + '\n');
    }
    console.log(JSON.stringify(planOnly, null, 2));
    if (planOnly.status !== 'passed') process.exitCode = 1;
    return;
  }
  const started = performance.now();
  const results = await runTasks(tasks, options);
  results.sort((a, b) => a.id.localeCompare(b.id));
  const durationMs = Math.round(performance.now() - started);
  const failed = results.filter((result) => result.status !== 'passed');
  const budgetExceeded = options.budgetMs > 0 && durationMs > options.budgetMs;
  const timingSummary = summarizeResults(tasks, results);
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION,
    harness: 'BrowserRT cloudtainer test facility', schema: 2,
    status: failed.length === 0 && !budgetExceeded ? 'passed' : 'failed',
    generatedAt: new Date().toISOString(),
    options: { tier: options.tier, ids, tag: options.tag, shard: options.shard, changedFiles, changedTaskIds, jobs: options.jobs, effectiveJobs: jobCount(options.jobs), failFast: options.failFast, budgetMs: options.budgetMs, includeQuarantined: options.includeQuarantined, onlyAffected: options.onlyAffected },
    impact, plan, durationMs, budgetExceeded, timingSummary,
    passedCount: results.length - failed.length, failedCount: failed.length,
    tasks: results
  };
  if (options.json) {
    await mkdir(dirname(options.json), { recursive: true });
    await writeFile(options.json, JSON.stringify(report, null, 2) + '\n');
  }
  if (options.history) {
    const history = appendTimingHistory(await readJsonMaybe(options.history), report);
    await mkdir(dirname(options.history), { recursive: true });
    await writeFile(options.history, JSON.stringify(history, null, 2) + '\n');
  }
  if (!options.quiet) {
    console.log(`[run_tests] summary ${report.status}: ${report.passedCount}/${results.length} passed in ${durationMs}ms`);
    if (timingSummary.slowest[0]) console.log(`[run_tests] slowest ${timingSummary.slowest[0].id}: ${timingSummary.slowest[0].durationMs}ms`);
    if (options.json) console.log(`[run_tests] wrote ${options.json}`);
    if (options.history) console.log(`[run_tests] updated ${options.history}`);
  }
  if (report.status !== 'passed') process.exitCode = 1;
}

main().catch((error) => {
  console.error(`[run_tests] FAIL: ${error.stack || error.message}`);
  process.exitCode = 1;
});
