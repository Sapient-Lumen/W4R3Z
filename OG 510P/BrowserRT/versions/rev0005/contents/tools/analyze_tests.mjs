#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

function argValue(argv, flag, fallback) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}

async function readJson(path, fallback = null) {
  try { return JSON.parse(await readFile(path, 'utf8')); } catch { return fallback; }
}

const argv = process.argv.slice(2);
const reportPath = argValue(argv, '--report', 'artifacts/validation/REV0005-TEST-HARNESS-RUN.json');
const historyPath = argValue(argv, '--history', 'artifacts/validation/REV0005-TEST-TIMING-HISTORY.json');
const outPath = argValue(argv, '--out', 'artifacts/validation/REV0005-TEST-ANALYSIS.json');
const write = argv.includes('--write');
const report = await readJson(reportPath);
const history = await readJson(historyPath, { runs: [] });
if (!report) throw new Error(`missing test report ${reportPath}`);
const tasks = Array.isArray(report.tasks) ? report.tasks : [];
const slowest = tasks.slice().sort((a, b) => b.durationMs - a.durationMs || a.id.localeCompare(b.id)).slice(0, 10);
const failures = tasks.filter((task) => task.status !== 'passed');
const estimateMisses = tasks.filter((task) => task.estimatedMs && task.durationMs > task.estimatedMs * 2).map((task) => ({ id: task.id, durationMs: task.durationMs, estimatedMs: task.estimatedMs }));
const recommendations = [];
if (slowest[0]?.durationMs > 2000) recommendations.push('Inspect the slowest task before adding more browser or GPU probes.');
if (estimateMisses.length) recommendations.push('Update manifest estimatedMs for tasks that exceeded estimates by more than 2x.');
if (failures.length) recommendations.push('Prefer a narrow --id rerun before broad release rerun.');
if (!history?.runs?.length) recommendations.push('Keep appending timing history so sharding can become history-weighted.');
const analysis = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  status: failures.length === 0 ? 'passed' : 'failed',
  generatedAt: new Date().toISOString(),
  sourceReport: reportPath,
  sourceHistory: historyPath,
  run: {
    status: report.status,
    durationMs: report.durationMs,
    taskCount: tasks.length,
    failedCount: failures.length,
    effectiveJobs: report.options?.effectiveJobs ?? null
  },
  slowest,
  estimateMisses,
  historyRunCount: history?.runs?.length || 0,
  recommendations
};
if (write) {
  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, JSON.stringify(analysis, null, 2) + '\n');
  console.log(outPath);
} else {
  console.log(JSON.stringify(analysis, null, 2));
}
if (analysis.status !== 'passed') process.exitCode = 1;
