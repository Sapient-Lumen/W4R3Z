#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { mkdir, readFile, writeFile, rm, readdir } from 'node:fs/promises';
import { basename, dirname, join } from 'node:path';
import { performance } from 'node:perf_hooks';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { prepareSharedPackageTarballForBrowserBundle, envForPreparedPackage } from './lib/package_installed_fixture.mjs';

const RAW_TASK = 'browser:opfs-block-store-raw-composite-abort-signal-proof';
const QUOTA_PRESSURE_TASK = 'browser:opfs-quota-pressure-proof';
const STORAGE_POSTURE_TASK = 'browser:storage-posture-managed-proof';
const PRODUCT_TASKS = Object.freeze([
  'browser:package-installed-consumer-smoke-proof',
  'browser:package-installed-opfs-consumer-proof',
  'browser:package-installed-cross-tab-opfs-consumer-proof',
  'browser:package-installed-opfs-reopen-consumer-proof',
  'browser:package-installed-tab-close-opfs-consumer-proof',
  'browser:package-installed-opfs-budget-consumer-proof',
  'browser:package-installed-opfs-abort-consumer-proof',
  'browser:package-installed-opfs-abrupt-kill-consumer-proof',
  'browser:package-installed-opfs-corruption-consumer-proof'
]);
const CURRENT_TASKS = Object.freeze([RAW_TASK, QUOTA_PRESSURE_TASK, STORAGE_POSTURE_TASK, ...PRODUCT_TASKS]);
const DEFAULT_CURRENT_OUT = `artifacts/validation/${REVISION.toUpperCase()}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`;
const DEFAULT_PRODUCT_OUT = `artifacts/validation/${REVISION.toUpperCase()}-PRODUCT-WEDGE-BROWSER-RUN.json`;
const DEFAULT_CHUNK_SIZE = Math.max(1, Number(process.env.BROWSERRT_BROWSER_BUNDLE_CHUNK_SIZE || 4));
const DEFAULT_MAX_CHUNKS = process.env.BROWSERRT_BROWSER_BUNDLE_MAX_CHUNKS ? Number(process.env.BROWSERRT_BROWSER_BUNDLE_MAX_CHUNKS) : null;
const BATCH_LAYOUT = Object.freeze([
  [RAW_TASK],
  [QUOTA_PRESSURE_TASK],
  [STORAGE_POSTURE_TASK],
  ['browser:package-installed-consumer-smoke-proof'],
  ['browser:package-installed-opfs-consumer-proof'],
  ['browser:package-installed-cross-tab-opfs-consumer-proof'],
  ['browser:package-installed-opfs-reopen-consumer-proof'],
  ['browser:package-installed-tab-close-opfs-consumer-proof'],
  ['browser:package-installed-opfs-budget-consumer-proof'],
  ['browser:package-installed-opfs-abort-consumer-proof'],
  ['browser:package-installed-opfs-corruption-consumer-proof'],
  ['browser:package-installed-opfs-abrupt-kill-consumer-proof']
]);

function parseArgs(argv) {
  const out = { mode: 'current', json: null, ids: null, quiet: false, chunkChild: false, chunkSize: DEFAULT_CHUNK_SIZE, resume: true, resumeFrom: null, maxChunks: DEFAULT_MAX_CHUNKS, checkpointDir: null };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--mode') out.mode = argv[++i];
    else if (arg === '--json') out.json = argv[++i];
    else if (arg === '--id') out.ids = String(argv[++i]).split(',').filter(Boolean);
    else if (arg === '--quiet') out.quiet = true;
    else if (arg === '--chunk-child') out.chunkChild = true;
    else if (arg === '--chunk-size') out.chunkSize = Number(argv[++i]);
    else if (arg === '--no-resume') out.resume = false;
    else if (arg === '--resume-from') out.resumeFrom = argv[++i];
    else if (arg === '--max-chunks') out.maxChunks = Number(argv[++i]);
    else if (arg === '--checkpoint-dir') out.checkpointDir = argv[++i];
    else throw new Error(`Unknown option: ${arg}`);
  }
  if (!['current', 'product'].includes(out.mode)) throw new Error(`Bad --mode: ${out.mode}`);
  if (!Number.isInteger(out.chunkSize) || out.chunkSize < 1) throw new Error(`Bad --chunk-size: ${out.chunkSize}`);
  if (out.maxChunks !== null && (!Number.isInteger(out.maxChunks) || out.maxChunks < 1)) throw new Error(`Bad --max-chunks: ${out.maxChunks}`);
  return out;
}

function defaultCheckpointDir(out) {
  const name = basename(out).replace(/\.json$/i, '');
  return join(dirname(out), `${name}.checkpoints`);
}

function packageReuseSummary(packageTarball, packageEnv = {}) {
  if (packageTarball) {
    return {
      enabled: true,
      source: packageTarball.source || null,
      filename: packageTarball.packInfo?.filename || null,
      reusedPreparedTarball: packageTarball.reusedPreparedTarball === true,
      validation: packageTarball.validation || null
    };
  }
  if (Object.keys(packageEnv || {}).length) {
    return {
      enabled: true,
      source: packageEnv.BROWSERRT_PREPARED_PACKAGE_SOURCE || null,
      filename: packageEnv.BROWSERRT_PREPARED_PACKAGE_FILENAME || null,
      reusedPreparedTarball: true,
      validation: null
    };
  }
  return { enabled: false };
}

function signalTree(child, signal) {
  if (process.platform !== 'win32' && child.pid) {
    try { process.kill(-child.pid, signal); return; } catch {}
  }
  try { child.kill(signal); } catch {}
}

async function loadManifestTimeouts() {
  const manifest = JSON.parse(await readFile('test/manifest.json', 'utf8'));
  const map = new Map();
  for (const task of manifest.tasks || []) map.set(task.id, Number(task.timeoutMs || 30000));
  return map;
}

function runCommand(args, { timeoutMs, quiet, reportPath, env = {} }) {
  return new Promise((resolve) => {
    const started = performance.now();
    let stdout = '';
    let stderr = '';
    let timedOut = false;
    let settled = false;
    let timer = null;
    let hardTimer = null;
    let closeFallback = null;
    let reportPoll = null;
    let heartbeat = null;
    const child = spawn(process.execPath, args, { cwd: '.', stdio: ['ignore', 'pipe', 'pipe'], detached: process.platform !== 'win32', env: { ...process.env, ...env } });
    const finish = (code, signal, suffix = '') => {
      if (settled) return;
      settled = true;
      if (timer) clearTimeout(timer);
      if (hardTimer) clearTimeout(hardTimer);
      if (closeFallback) clearTimeout(closeFallback);
      if (reportPoll) clearInterval(reportPoll);
      if (heartbeat) clearInterval(heartbeat);
      resolve({ code, signal, timedOut, durationMs: Math.round(performance.now() - started), stdout, stderr: `${stderr}${suffix}` });
    };
    if (!quiet) {
      heartbeat = setInterval(() => {
        if (!settled) console.log(`[run_browser_bundle] waiting for child process group ${Math.round((performance.now() - started) / 1000)}s`);
      }, 10000);
    }
    if (reportPath) {
      reportPoll = setInterval(async () => {
        if (settled) return;
        try {
          const report = JSON.parse(await readFile(reportPath, 'utf8'));
          if (report?.status === 'passed' || report?.status === 'failed') {
            const code = report.status === 'passed' ? 0 : 1;
            signalTree(child, 'SIGTERM');
            const detachedKill = setTimeout(() => {
              signalTree(child, 'SIGKILL');
            }, 1000);
            detachedKill.unref?.();
            finish(code, null, '\n[run_browser_bundle] resolved from completed batch report while child process group was still open');
          }
        } catch {}
      }, 1000);
    }
    timer = setTimeout(() => {
      timedOut = true;
      signalTree(child, 'SIGTERM');
      hardTimer = setTimeout(() => {
        signalTree(child, 'SIGKILL');
        finish(null, 'SIGKILL', `\n[run_browser_bundle] hard timeout after ${timeoutMs}ms`);
      }, 3000);
    }, timeoutMs);
    child.stdout.on('data', (chunk) => {
      const text = chunk.toString();
      stdout += text;
      if (!quiet) process.stdout.write(text);
    });
    child.stderr.on('data', (chunk) => {
      const text = chunk.toString();
      stderr += text;
      if (!quiet) process.stderr.write(text);
    });
    child.on('error', (error) => finish(null, null, `\n${error.stack || error.message}`));
    child.on('exit', (code, signal) => {
      closeFallback = setTimeout(() => finish(code, signal, '\n[run_browser_bundle] stdio close fallback after child exit'), 1500);
    });
    child.on('close', finish);
  });
}

function truncate(text, limit = 2000) {
  if (!text) return '';
  return text.length <= limit ? text : `${text.slice(0, limit)}\n... truncated ${text.length - limit} bytes ...`;
}

function pickIds(options) {
  const defaultIds = options.mode === 'current' ? CURRENT_TASKS : PRODUCT_TASKS;
  const ids = options.ids?.length ? options.ids : defaultIds;
  const allowed = new Set(defaultIds);
  const unknown = ids.filter((id) => !allowed.has(id));
  if (unknown.length) throw new Error(`Task ids are not in browser ${options.mode} bundle: ${unknown.join(', ')}`);
  return [...new Set(ids)];
}

function makeBatches(ids) {
  const wanted = new Set(ids);
  return BATCH_LAYOUT.map((batch) => batch.filter((id) => wanted.has(id))).filter((batch) => batch.length);
}

function flattenBatches(batches) {
  return batches.flat();
}

function sameIdList(a = [], b = []) {
  return Array.isArray(a) && Array.isArray(b) && a.length === b.length && a.every((id, index) => id === b[index]);
}

function dedupeTasksById(tasks = []) {
  const byId = new Map();
  for (const task of tasks) {
    if (!task?.id) continue;
    const prior = byId.get(task.id);
    if (!prior || prior.status !== 'passed' || task.status === 'passed') byId.set(task.id, task);
  }
  return [...byId.values()];
}

async function recoverChunkReportsFromCheckpointDir({ checkpointDir, ids, existingChunkReports = [], existingBatches = [], quiet }) {
  const allowedIds = new Set(ids);
  const seenChunkPaths = new Set(existingChunkReports.map((chunk) => chunk.reportPath).filter(Boolean));
  const seenBatchPaths = new Set(existingBatches.map((batch) => batch.reportPath).filter(Boolean));
  const recovered = { chunks: [], tasks: [], batches: [] };
  let entries = [];
  try { entries = await readdir(checkpointDir, { withFileTypes: true }); } catch { return recovered; }
  const files = entries
    .filter((entry) => entry.isFile() && /^chunk-\d+\.json$/.test(entry.name))
    .map((entry) => entry.name)
    .sort();
  for (const file of files) {
    const reportPath = join(checkpointDir, file);
    if (seenChunkPaths.has(reportPath)) continue;
    let report = null;
    try { report = JSON.parse(await readFile(reportPath, 'utf8')); } catch { continue; }
    if (report?.project !== 'BrowserRT' || report?.revision !== REVISION || report?.version !== VERSION) continue;
    if (report?.harness !== 'BrowserRT browser product bundle runner') continue;
    if (!['passed', 'failed'].includes(report?.status)) continue;
    const chunkIds = Array.isArray(report?.options?.ids) ? report.options.ids : (Array.isArray(report.tasks) ? report.tasks.map((task) => task.id).filter(Boolean) : []);
    if (!chunkIds.length || chunkIds.some((id) => !allowedIds.has(id))) continue;
    const index = Number((/^chunk-(\d+)\.json$/.exec(file) || [])[1] || recovered.chunks.length + existingChunkReports.length + 1);
    recovered.chunks.push({
      index,
      ids: chunkIds,
      status: report.status,
      exitCode: report.status === 'passed' ? 0 : 1,
      signal: null,
      timedOut: false,
      durationMs: Number(report.durationMs) || 0,
      stdout: '',
      stderr: '[run_browser_bundle] recovered terminal chunk report from persistent checkpoint directory after interrupted parent aggregate',
      reportPath
    });
    if (Array.isArray(report.tasks)) recovered.tasks.push(...report.tasks);
    if (Array.isArray(report.batches)) {
      for (const batch of report.batches) {
        if (batch?.reportPath && seenBatchPaths.has(batch.reportPath)) continue;
        if (batch?.reportPath) seenBatchPaths.add(batch.reportPath);
        recovered.batches.push({ ...batch, chunkIndex: index });
      }
    }
    seenChunkPaths.add(reportPath);
  }
  recovered.chunks.sort((a, b) => a.index - b.index);
  if (recovered.chunks.length && !quiet) console.log(`[run_browser_bundle] recovered ${recovered.chunks.length} terminal chunk report(s) from ${checkpointDir}`);
  return recovered;
}

async function loadResumeState({ options, ids, out, checkpointDir, quiet }) {
  if (!options.resume || options.chunkChild) return null;
  const input = options.resumeFrom || out;
  try {
    const report = JSON.parse(await readFile(input, 'utf8'));
    if (report?.project !== 'BrowserRT' || report?.revision !== REVISION || report?.version !== VERSION) return null;
    if (report?.harness !== 'BrowserRT browser product bundle runner') return null;
    if (!['running', 'failed'].includes(report?.status)) return null;
    if (!sameIdList(report?.options?.ids || [], ids)) return null;
    const chunkReports = Array.isArray(report.chunks) ? [...report.chunks] : [];
    const aggregateBatches = Array.isArray(report.batches) ? [...report.batches] : [];
    const recovered = await recoverChunkReportsFromCheckpointDir({ checkpointDir, ids, existingChunkReports: chunkReports, existingBatches: aggregateBatches, quiet });
    chunkReports.push(...recovered.chunks);
    chunkReports.sort((a, b) => a.index - b.index);
    aggregateBatches.push(...recovered.batches);
    const tasks = dedupeTasksById([...(Array.isArray(report.tasks) ? report.tasks : []), ...recovered.tasks]);
    const passedTaskIds = new Set(tasks.filter((task) => task.status === 'passed').map((task) => task.id));
    if (!passedTaskIds.size) return null;
    if (!quiet) console.log(`[run_browser_bundle] resuming from ${input}: ${passedTaskIds.size}/${ids.length} passed task rows recorded after checkpoint recovery`);
    return { input, report, tasks, passedTaskIds, chunkReports, aggregateBatches };
  } catch {
    return null;
  }
}

function computeChunkedSummary({ options, ids, batches, chunkReports, tasks, aggregateBatches, started, statusOverride = null, packageReuse = { enabled: false } }) {
  const order = new Map(ids.map((id, index) => [id, index]));
  const sortedTasks = dedupeTasksById(tasks).sort((a, b) => (order.get(a.id) ?? 999) - (order.get(b.id) ?? 999));
  const failed = sortedTasks.filter((task) => task.status !== 'passed');
  const missing = ids.filter((id) => !sortedTasks.some((task) => task.id === id));
  const passedTaskIds = new Set(sortedTasks.filter((task) => task.status === 'passed').map((task) => task.id));
  const failedChunks = chunkReports.filter((chunk) => chunk.status !== 'passed' || chunk.exitCode !== 0 || chunk.timedOut);
  const failedBatches = aggregateBatches.filter((batch) => batch.status !== 'passed' || batch.exitCode !== 0 || batch.timedOut);
  const blockingFailedChunks = failedChunks.filter((chunk) => !(Array.isArray(chunk.ids) && chunk.ids.length && chunk.ids.every((id) => passedTaskIds.has(id))));
  const blockingFailedBatches = failedBatches.filter((batch) => !(Array.isArray(batch.ids) && batch.ids.length && batch.ids.every((id) => passedTaskIds.has(id))));
  const computedStatus = failed.length === 0 && missing.length === 0 && blockingFailedChunks.length === 0 && blockingFailedBatches.length === 0 ? 'passed' : 'failed';
  const status = statusOverride || computedStatus;
  const processDurationMs = Math.round(performance.now() - started);
  const cumulativeChunkDurationMs = chunkReports.reduce((sum, chunk) => sum + (Number(chunk.durationMs) || 0), 0);
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION,
    harness: 'BrowserRT browser product bundle runner', schema: 4,
    status, generatedAt: new Date().toISOString(),
    options: { mode: options.mode, ids, jobs: 'checkpointed-chunked-batched-serial', batchCount: batches.length, chunkCount: chunkReports.length, plannedChunkCount: Math.ceil(batches.length / options.chunkSize), chunkSize: options.chunkSize, maxChunks: options.maxChunks, resumeEnabled: options.resume !== false },
    packageReuse,
    durationMs: Math.max(processDurationMs, cumulativeChunkDurationMs),
    processDurationMs,
    cumulativeChunkDurationMs,
    passedCount: sortedTasks.filter((task) => task.status === 'passed').length,
    failedCount: failed.length + blockingFailedChunks.length + blockingFailedBatches.length + (status === 'failed' ? missing.length : 0),
    supersededFailedChunkCount: failedChunks.length - blockingFailedChunks.length,
    supersededFailedBatchCount: failedBatches.length - blockingFailedBatches.length,
    missingTaskIds: missing,
    tasks: sortedTasks,
    chunks: chunkReports,
    batches: aggregateBatches,
    checkpoint: { complete: status !== 'running', completedChunkCount: chunkReports.length, completedTaskCount: sortedTasks.length },
    nonClaims: ['Checkpointed chunked browser bundle execution is a harness reliability measure for cloudtainer Chromium/npm-pack workloads; each chunk delegates to the same batch runner, individual proof semantics remain owned by each task receipt, --max-chunks can intentionally leave status=running for a later resume, and status=running is not a green browser-current claim.']
  };
}

async function writeChunkedSummary(args) {
  const report = computeChunkedSummary(args);
  await mkdir(dirname(args.out), { recursive: true });
  await writeFile(args.out, JSON.stringify(report, null, 2) + '\n');
  return report;
}

async function runChunkedBundle({ options, ids, batches, out, checkpointDir, timeouts, started, resumeState = null, packageEnv = {}, packageReuse = { enabled: false } }) {
  const chunkSize = options.chunkSize;
  const chunkReports = resumeState?.chunkReports ? [...resumeState.chunkReports] : [];
  const tasks = resumeState?.tasks ? [...resumeState.tasks] : [];
  const aggregateBatches = resumeState?.aggregateBatches ? [...resumeState.aggregateBatches] : [];
  const completedTaskIds = new Set(tasks.filter((task) => task.status === 'passed').map((task) => task.id));
  let startOffset = 0;
  while (startOffset < batches.length && batches[startOffset].every((id) => completedTaskIds.has(id))) startOffset += 1;
  if (resumeState && startOffset > 0 && !options.quiet) console.log(`[run_browser_bundle] resume skip: ${startOffset}/${batches.length} batches already passed`);
  let executedChunks = 0;
  for (let offset = startOffset; offset < batches.length; offset += chunkSize) {
    const chunkBatches = batches.slice(offset, offset + chunkSize);
    const chunkIds = flattenBatches(chunkBatches);
    const chunkLabel = `chunk-${String(chunkReports.length + 1).padStart(2, '0')}`;
    const chunkJson = join(checkpointDir, `${chunkLabel}.json`);
    const chunkTimeout = chunkIds.reduce((sum, id) => sum + (timeouts.get(id) || 30000), 0) + 60000;
    if (!options.quiet) console.log(`[run_browser_bundle] chunk ${chunkReports.length + 1}/${Math.ceil(batches.length / chunkSize)}: ${chunkIds.join(', ')}`);
    const childCheckpointDir = join(checkpointDir, `${chunkLabel}-batches`);
    const result = await runCommand(['tools/run_browser_bundle.mjs', '--mode', options.mode, '--id', chunkIds.join(','), '--json', chunkJson, '--checkpoint-dir', childCheckpointDir, '--chunk-child', '--quiet', '--chunk-size', String(options.chunkSize)], { timeoutMs: chunkTimeout, quiet: options.quiet, reportPath: chunkJson, env: packageEnv });
    let report = null;
    try { report = JSON.parse(await readFile(chunkJson, 'utf8')); } catch {}
    chunkReports.push({ index: chunkReports.length + 1, ids: chunkIds, status: report?.status || (result.code === 0 ? 'passed' : 'failed'), exitCode: result.code, signal: result.signal, timedOut: result.timedOut, durationMs: result.durationMs, stdout: truncate(result.stdout), stderr: truncate(result.stderr), reportPath: chunkJson });
    if (report?.tasks) tasks.push(...report.tasks);
    if (report?.batches) {
      for (const batch of report.batches) aggregateBatches.push({ ...batch, index: aggregateBatches.length + 1, chunkIndex: chunkReports.length });
    }
    const failedOrTimedOut = result.code !== 0 || result.timedOut || report?.status === 'failed';
    const lastChunk = offset + chunkSize >= batches.length;
    executedChunks += 1;
    if (!failedOrTimedOut && !lastChunk) {
      await writeChunkedSummary({ options, ids, batches, out, chunkReports, tasks, aggregateBatches, started, statusOverride: 'running', packageReuse });
      if (options.maxChunks !== null && executedChunks >= options.maxChunks) {
        if (!options.quiet) console.log(`[run_browser_bundle] checkpoint stop after ${executedChunks} chunk(s); rerun with the same --json path to resume`);
        return 0;
      }
    }
    if (failedOrTimedOut) break;
  }
  const report = await writeChunkedSummary({ options, ids, batches, out, chunkReports, tasks, aggregateBatches, started, packageReuse });
  if (!options.quiet) console.log(`[run_browser_bundle] summary ${report.status}: ${report.passedCount}/${ids.length} passed in ${report.durationMs}ms`);
  return report.status === 'passed' ? 0 : 1;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const ids = pickIds(options);
  const batches = makeBatches(ids);
  const out = options.json || (options.mode === 'current' ? DEFAULT_CURRENT_OUT : DEFAULT_PRODUCT_OUT);
  const checkpointDir = options.checkpointDir || defaultCheckpointDir(out);
  const tempDir = join(tmpdir(), `browserrt-${REVISION}-browser-bundle-${process.pid}`);
  const timeouts = await loadManifestTimeouts();
  const started = performance.now();
  const resumeState = await loadResumeState({ options, ids, out, checkpointDir, quiet: options.quiet });
  const batchReports = [];
  const tasks = [];
  let packageTarball = null;
  let packageEnv = {};
  let packageReuse = { enabled: false };
  try {
    await mkdir(tempDir, { recursive: true });
    if (!resumeState && !options.chunkChild) await rm(checkpointDir, { recursive: true, force: true });
    await mkdir(checkpointDir, { recursive: true });
    const resumePassedIds = new Set((resumeState?.tasks || []).filter((task) => task.status === 'passed').map((task) => task.id));
    const pendingIds = ids.filter((id) => !resumePassedIds.has(id));
    if (pendingIds.some((id) => PRODUCT_TASKS.includes(id))) {
      packageTarball = await prepareSharedPackageTarballForBrowserBundle({ root: process.cwd(), tempDir });
      packageEnv = envForPreparedPackage(packageTarball);
      packageReuse = packageReuseSummary(packageTarball, packageEnv);
      if (!options.quiet) console.log(`[run_browser_bundle] prepared package tarball once for ${pendingIds.filter((id) => PRODUCT_TASKS.includes(id)).length} pending package browser task(s): ${packageTarball.packInfo.filename}`);
    } else if (resumeState?.report?.packageReuse?.enabled) {
      packageReuse = resumeState.report.packageReuse;
      if (!options.quiet) console.log('[run_browser_bundle] all package browser tasks already passed in resume state; preserving prior package reuse evidence without repacking');
    }
    if (!options.chunkChild && batches.length > options.chunkSize) {
      const exitCode = await runChunkedBundle({ options, ids, batches, out, checkpointDir, timeouts, started, resumeState, packageEnv, packageReuse });
      process.exit(exitCode);
    }
    for (let i = 0; i < batches.length; i += 1) {
      const batchIds = batches[i];
      const batchJson = join(checkpointDir, `batch-${String(i + 1).padStart(2, '0')}.json`);
      const batchTimeout = batchIds.reduce((sum, id) => sum + (timeouts.get(id) || 30000), 0) + 30000;
      if (!options.quiet) console.log(`[run_browser_bundle] batch ${i + 1}/${batches.length}: ${batchIds.join(', ')}`);
      let result = null;
      let report = null;
      const attempts = [];
      for (let attempt = 1; attempt <= 2; attempt += 1) {
        result = await runCommand(['tools/run_tests.mjs', '--tier', 'browser', '--id', batchIds.join(','), '--jobs', '1', '--quiet', '--json', batchJson], { timeoutMs: batchTimeout, quiet: options.quiet, reportPath: batchJson, env: packageEnv });
        try { report = JSON.parse(await readFile(batchJson, 'utf8')); } catch { report = null; }
        attempts.push({ attempt, status: report?.status || (result.code === 0 ? 'passed' : 'failed'), exitCode: result.code, signal: result.signal, timedOut: result.timedOut, durationMs: result.durationMs, stdout: truncate(result.stdout), stderr: truncate(result.stderr) });
        if (result.code === 0 && report?.status !== 'failed' && !result.timedOut) break;
        if (!options.quiet) console.warn(`[run_browser_bundle] retrying batch ${i + 1} after ${attempts.at(-1).status}`);
      }
      if (report?.tasks) tasks.push(...report.tasks);
      batchReports.push({ index: i + 1, ids: batchIds, status: report?.status || (result?.code === 0 ? 'passed' : 'failed'), exitCode: result?.code ?? null, signal: result?.signal ?? null, timedOut: result?.timedOut || false, durationMs: attempts.reduce((sum, item) => sum + item.durationMs, 0), attempts, reportPath: batchJson });
      if (result?.code !== 0 || report?.status === 'failed' || result?.timedOut) break;
    }
  } finally {
    await rm(tempDir, { recursive: true, force: true });
  }
  const order = new Map(ids.map((id, index) => [id, index]));
  tasks.splice(0, tasks.length, ...dedupeTasksById(tasks));
  tasks.sort((a, b) => (order.get(a.id) ?? 999) - (order.get(b.id) ?? 999));
  const failed = tasks.filter((task) => task.status !== 'passed');
  const missing = ids.filter((id) => !tasks.some((task) => task.id === id));
  const failedBatches = batchReports.filter((batch) => batch.status !== 'passed' || batch.exitCode !== 0 || batch.timedOut);
  const status = failed.length === 0 && missing.length === 0 && failedBatches.length === 0 ? 'passed' : 'failed';
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION,
    harness: 'BrowserRT browser product bundle runner', schema: options.chunkChild ? 2 : 3,
    status, generatedAt: new Date().toISOString(),
    options: { mode: options.mode, ids, jobs: 'batched-serial', batchCount: batches.length, chunkSize: options.chunkSize },
    packageReuse,
    durationMs: Math.round(performance.now() - started),
    passedCount: tasks.filter((task) => task.status === 'passed').length,
    failedCount: failed.length + missing.length + failedBatches.length,
    missingTaskIds: missing,
    tasks,
    batches: batchReports,
    nonClaims: ['Batched browser bundle execution is a harness reliability measure for cloudtainer Chromium/npm-pack workloads; each batch is a direct Node child process group with bundle-owned timeout escalation and completed-report polling, and individual proof semantics remain owned by each task receipt.']
  };
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  if (!options.quiet) console.log(`[run_browser_bundle] summary ${status}: ${report.passedCount}/${ids.length} passed in ${report.durationMs}ms`);
  process.exit(status === 'passed' ? 0 : 1);
}

main().catch((error) => {
  console.error(`[run_browser_bundle] FAIL: ${error.stack || error.message}`);
  process.exit(1);
});
