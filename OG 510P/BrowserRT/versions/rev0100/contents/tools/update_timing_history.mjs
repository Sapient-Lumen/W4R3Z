#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { appendTimingHistory } from '../src/test-facility.mjs';
import { REVISION, VERSION } from '../src/browserrt.mjs';

function argValue(argv, flag, fallback) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}

async function readJson(path, fallback = null) {
  try { return JSON.parse(await readFile(path, 'utf8')); } catch { return fallback; }
}

const argv = process.argv.slice(2);
const reportPath = argValue(argv, '--report', `artifacts/validation/REV${REVISION.slice(3)}-TEST-HARNESS-RUN.json`);
const outPath = argValue(argv, '--out', `artifacts/validation/REV${REVISION.slice(3)}-TEST-TIMING-HISTORY.json`);
const priorPath = argValue(argv, '--history', outPath);
const report = await readJson(reportPath);
if (!report) throw new Error(`missing test report ${reportPath}`);
const prior = await readJson(priorPath, { runs: [] });
const history = appendTimingHistory(prior, report, { limit: 50 });
history.version = VERSION;
history.revision = REVISION;
history.status = 'passed';
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(history, null, 2) + '\n');
console.log(outPath);
