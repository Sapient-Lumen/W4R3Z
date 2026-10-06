#!/usr/bin/env node
import { availableParallelism } from 'node:os';
import { spawn } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { performance } from 'node:perf_hooks';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const OUT = `artifacts/validation/REV${REVISION.slice(3)}-TURN-BOOTSTRAP-RUN.json`;

function run(command, args) {
  return new Promise((resolveRun) => {
    const started = performance.now();
    let stdout = ''; let stderr = '';
    const child = spawn(command, args, { cwd: process.cwd(), stdio: ['ignore', 'pipe', 'pipe'] });
    child.stdout.on('data', (chunk) => { stdout += chunk.toString(); });
    child.stderr.on('data', (chunk) => { stderr += chunk.toString(); });
    child.on('close', (code, signal) => resolveRun({ command: [command, ...args].join(' '), code, signal, durationMs: Math.round(performance.now() - started), stdout, stderr }));
  });
}

const args = new Set(process.argv.slice(2));
const started = performance.now();
const smokeOut = `artifacts/validation/REV${REVISION.slice(3)}-TURN-SMOKE-RUN.json`;
const smoke = await run('node', ['tools/run_tests.mjs', '--tier', 'smoke', '--jobs', '1', '--json', smokeOut, '--quiet']);
let smokeReport = null;
try { smokeReport = JSON.parse(await readFile(smokeOut, 'utf8')); } catch { smokeReport = null; }
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: smoke.code === 0 && smokeReport?.status === 'passed' ? 'passed' : 'failed',
  generatedAt: new Date().toISOString(),
  purpose: 'Fast per-turn bootstrap: confirm the cube is coherent, gather a timing sample, and avoid spending a turn on the wrong test slice.',
  environment: { node: process.version, availableParallelism: availableParallelism?.() || null, cwd: process.cwd() },
  immediate_process_policy: {
    startLongLivedProcessesAcrossTurns: false,
    reason: 'A cloudtainer turn should not rely on watch servers, browsers, or daemons surviving into the next assistant turn.',
    perTurnFirstMove: 'Run this bootstrap or list the desired test slice before editing deeply.',
    withinTurnReusableProcesses: ['local HTTP server for browser tests', 'single Chromium/CDP session for a selected browser slice', 'one-shot worker pool for timing probes'],
    processesToStartImmediatelyByDefault: [],
    startImmediatelyOnlyWhen: ['the selected manifest slice needs a local browser/CDP page', 'the selected slice explicitly owns setup and teardown in the same command'],
    forbiddenByDefault: ['watch mode', 'unbounded stress loop', 'background daemon waiting for a later turn', 'server or browser process without teardown']
  },
  recommended_next_commands: [
    'node tools/plan_tests.mjs --tier release --changed src/browserrt.mjs,tools/run_tests.mjs',
    'node tools/run_tests.mjs --list --tier release',
    `node tools/run_tests.mjs --tier release --changed tools/run_tests.mjs --only-affected --dry-run --json artifacts/validation/REV${REVISION.slice(3)}-AFFECTED-RUNNER-DRYRUN.json`,
    'node tools/run_tests.mjs --tier release --changed src/test-facility.mjs',
    `node tools/run_tests.mjs --tier release --jobs 1 --json artifacts/validation/REV${REVISION.slice(3)}-TEST-HARNESS-RUN.json`,
    'node tools/run_tests.mjs --tier release --shard 1/2 --jobs auto',
    'node tools/run_tests.mjs --tier release --id runtime:smoke',
    'node tools/run_tests.mjs --tier browser --id browser:cdp-boot-report --jobs 1'
  ],
  smokeCommand: smoke.command, smokeDurationMs: smoke.durationMs, smokeReportPath: smokeOut,
  smokeSummary: smokeReport ? { status: smokeReport.status, taskCount: smokeReport.tasks.length, durationMs: smokeReport.durationMs, failedCount: smokeReport.failedCount } : null,
  durationMs: Math.round(performance.now() - started)
};
if (args.has('--write')) { await mkdir(dirname(OUT), { recursive: true }); await writeFile(OUT, JSON.stringify(report, null, 2) + '\n'); console.log(OUT); }
else console.log(JSON.stringify(report, null, 2));
if (report.status !== 'passed') process.exitCode = 1;
