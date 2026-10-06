#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { mkdir, readFile, writeFile, rm } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const RAW_TASK = 'browser:opfs-block-store-raw-composite-abort-signal-proof';
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
const CURRENT_TASKS = Object.freeze([RAW_TASK, ...PRODUCT_TASKS]);
const DEFAULT_CURRENT_OUT = `artifacts/validation/${REVISION.toUpperCase()}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`;
const DEFAULT_PRODUCT_OUT = `artifacts/validation/${REVISION.toUpperCase()}-PRODUCT-WEDGE-BROWSER-RUN.json`;
const BATCH_LAYOUT = Object.freeze([
  [RAW_TASK],
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
  const out = { mode: 'current', json: null, ids: null, quiet: false, chunkChild: false };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--mode') out.mode = argv[++i];
    else if (arg === '--json') out.json = argv[++i];
    else if (arg === '--id') out.ids = String(argv[++i]).split(',').filter(Boolean);
    else if (arg === '--quiet') out.quiet = true;
    else if (arg === '--chunk-child') out.chunkChild = true;
    else throw new Error(`Unknown option: ${arg}`);
  }
  if (!['current', 'product'].includes(out.mode)) throw new Error(`Bad --mode: ${out.mode}`);
  return out;
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

function runCommand(args, { timeoutMs, quiet, reportPath }) {
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
    const child = spawn(process.execPath, args, { cwd: '.', stdio: ['ignore', 'pipe', 'pipe'], detached: process.platform !== 'win32' });
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
            hardTimer = setTimeout(() => {
              signalTree(child, 'SIGKILL');
            }, 1000);
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

async function runChunkedBundle({ options, ids, batches, out, tempDir, timeouts, started }) {
  const chunkSize = 6;
  const chunkReports = [];
  const tasks = [];
  const aggregateBatches = [];
  for (let offset = 0; offset < batches.length; offset += chunkSize) {
    const chunkBatches = batches.slice(offset, offset + chunkSize);
    const chunkIds = flattenBatches(chunkBatches);
    const chunkJson = join(tempDir, `chunk-${String(chunkReports.length + 1).padStart(2, '0')}.json`);
    const chunkTimeout = chunkIds.reduce((sum, id) => sum + (timeouts.get(id) || 30000), 0) + 60000;
    if (!options.quiet) console.log(`[run_browser_bundle] chunk ${chunkReports.length + 1}/${Math.ceil(batches.length / chunkSize)}: ${chunkIds.join(', ')}`);
    const result = await runCommand(['tools/run_browser_bundle.mjs', '--mode', options.mode, '--id', chunkIds.join(','), '--json', chunkJson, '--chunk-child', '--quiet'], { timeoutMs: chunkTimeout, quiet: options.quiet, reportPath: chunkJson });
    let report = null;
    try { report = JSON.parse(await readFile(chunkJson, 'utf8')); } catch {}
    chunkReports.push({ index: chunkReports.length + 1, ids: chunkIds, status: report?.status || (result.code === 0 ? 'passed' : 'failed'), exitCode: result.code, signal: result.signal, timedOut: result.timedOut, durationMs: result.durationMs, stdout: truncate(result.stdout), stderr: truncate(result.stderr), reportPath: chunkJson });
    if (report?.tasks) tasks.push(...report.tasks);
    if (report?.batches) {
      for (const batch of report.batches) aggregateBatches.push({ ...batch, index: aggregateBatches.length + 1, chunkIndex: chunkReports.length });
    }
    if (result.code !== 0 || result.timedOut || report?.status === 'failed') break;
  }
  const order = new Map(ids.map((id, index) => [id, index]));
  tasks.sort((a, b) => (order.get(a.id) ?? 999) - (order.get(b.id) ?? 999));
  const failed = tasks.filter((task) => task.status !== 'passed');
  const missing = ids.filter((id) => !tasks.some((task) => task.id === id));
  const failedChunks = chunkReports.filter((chunk) => chunk.status !== 'passed' || chunk.exitCode !== 0 || chunk.timedOut);
  const failedBatches = aggregateBatches.filter((batch) => batch.status !== 'passed' || batch.exitCode !== 0 || batch.timedOut);
  const status = failed.length === 0 && missing.length === 0 && failedChunks.length === 0 && failedBatches.length === 0 ? 'passed' : 'failed';
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION,
    harness: 'BrowserRT browser product bundle runner', schema: 3,
    status, generatedAt: new Date().toISOString(),
    options: { mode: options.mode, ids, jobs: 'chunked-batched-serial', batchCount: batches.length, chunkCount: chunkReports.length },
    durationMs: Math.round(performance.now() - started),
    passedCount: tasks.filter((task) => task.status === 'passed').length,
    failedCount: failed.length + missing.length + failedChunks.length + failedBatches.length,
    missingTaskIds: missing,
    tasks,
    chunks: chunkReports,
    batches: aggregateBatches,
    nonClaims: ['Chunked browser bundle execution is a harness reliability measure for cloudtainer Chromium/npm-pack workloads; each chunk delegates to the same batch runner, and individual proof semantics remain owned by each task receipt.']
  };
  await mkdir(dirname(out), { recursive: true });
  await writeFile(out, JSON.stringify(report, null, 2) + '\n');
  if (!options.quiet) console.log(`[run_browser_bundle] summary ${status}: ${report.passedCount}/${ids.length} passed in ${report.durationMs}ms`);
  return status === 'passed' ? 0 : 1;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const ids = pickIds(options);
  const batches = makeBatches(ids);
  const out = options.json || (options.mode === 'current' ? DEFAULT_CURRENT_OUT : DEFAULT_PRODUCT_OUT);
  const tempDir = join(tmpdir(), `browserrt-${REVISION}-browser-bundle-${process.pid}`);
  const timeouts = await loadManifestTimeouts();
  const started = performance.now();
  const batchReports = [];
  const tasks = [];
  try {
    await mkdir(tempDir, { recursive: true });
    if (!options.chunkChild && batches.length > 6) {
      const exitCode = await runChunkedBundle({ options, ids, batches, out, tempDir, timeouts, started });
      process.exit(exitCode);
    }
    for (let i = 0; i < batches.length; i += 1) {
      const batchIds = batches[i];
      const batchJson = join(tempDir, `batch-${String(i + 1).padStart(2, '0')}.json`);
      const batchTimeout = batchIds.reduce((sum, id) => sum + (timeouts.get(id) || 30000), 0) + 30000;
      if (!options.quiet) console.log(`[run_browser_bundle] batch ${i + 1}/${batches.length}: ${batchIds.join(', ')}`);
      let result = null;
      let report = null;
      const attempts = [];
      for (let attempt = 1; attempt <= 2; attempt += 1) {
        result = await runCommand(['tools/run_tests.mjs', '--tier', 'browser', '--id', batchIds.join(','), '--jobs', '1', '--quiet', '--json', batchJson], { timeoutMs: batchTimeout, quiet: options.quiet, reportPath: batchJson });
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
  tasks.sort((a, b) => (order.get(a.id) ?? 999) - (order.get(b.id) ?? 999));
  const failed = tasks.filter((task) => task.status !== 'passed');
  const missing = ids.filter((id) => !tasks.some((task) => task.id === id));
  const failedBatches = batchReports.filter((batch) => batch.status !== 'passed' || batch.exitCode !== 0 || batch.timedOut);
  const status = failed.length === 0 && missing.length === 0 && failedBatches.length === 0 ? 'passed' : 'failed';
  const report = {
    project: 'BrowserRT', revision: REVISION, version: VERSION,
    harness: 'BrowserRT browser product bundle runner', schema: options.chunkChild ? 2 : 3,
    status, generatedAt: new Date().toISOString(),
    options: { mode: options.mode, ids, jobs: 'batched-serial', batchCount: batches.length },
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
