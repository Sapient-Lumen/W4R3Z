#!/usr/bin/env node
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';
import { selectTasks, validateManifest } from '../src/test-facility.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-EXPLICIT-ID-SELECTION-AUDIT.json`;
const argv = process.argv.slice(2);
const argValue = (flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };
const outPath = argValue('--json', DEFAULT_OUT);

function tokenize(command) {
  const tokens = [];
  let token = '';
  let quote = null;
  let escaped = false;
  for (const ch of String(command)) {
    if (escaped) { token += ch; escaped = false; continue; }
    if (ch === '\\') { escaped = true; continue; }
    if (quote) {
      if (ch === quote) quote = null;
      else token += ch;
      continue;
    }
    if (ch === '"' || ch === "'") { quote = ch; continue; }
    if (/\s/.test(ch)) {
      if (token) { tokens.push(token); token = ''; }
      continue;
    }
    token += ch;
  }
  if (token) tokens.push(token);
  return tokens;
}

function splitCommands(script) {
  return String(script).split(/\s*&&\s*/).map((row) => row.trim()).filter(Boolean);
}

function parseRunTestsCommand(command) {
  const tokens = tokenize(command);
  const idx = tokens.findIndex((token, i) => token === 'node' && tokens[i + 1] === 'tools/run_tests.mjs');
  if (idx < 0) return null;
  const args = tokens.slice(idx + 2);
  const parsed = { command, tier: 'release', ids: [], hasId: false };
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '--tier') parsed.tier = args[++i] || parsed.tier;
    else if (args[i] === '--id') { parsed.hasId = true; parsed.ids.push(...String(args[++i] || '').split(',').filter(Boolean)); }
  }
  return parsed.hasId ? parsed : null;
}

function packageRows(packageJson, manifest) {
  const rows = [];
  for (const [scriptName, scriptBody] of Object.entries(packageJson.scripts || {})) {
    for (const command of splitCommands(scriptBody)) {
      const parsed = parseRunTestsCommand(command);
      if (!parsed) continue;
      const selected = selectTasks(manifest, { tier: parsed.tier, ids: parsed.ids });
      const selectedIds = new Set(selected.map((task) => task.id));
      const missingIds = parsed.ids.filter((id) => !selectedIds.has(id));
      rows.push({ source: 'package.json', scriptName, tier: parsed.tier, explicitIds: parsed.ids, selectedIds: [...selectedIds].sort(), missingIds, status: missingIds.length ? 'failed' : 'passed', command });
    }
  }
  return rows;
}

function makefileRows(makefileText, manifest) {
  const rows = [];
  for (const line of String(makefileText).split(/\r?\n/)) {
    if (!line.includes('node tools/run_tests.mjs')) continue;
    const command = line.trim();
    const parsed = parseRunTestsCommand(command);
    if (!parsed) continue;
    const selected = selectTasks(manifest, { tier: parsed.tier, ids: parsed.ids });
    const selectedIds = new Set(selected.map((task) => task.id));
    const missingIds = parsed.ids.filter((id) => !selectedIds.has(id));
    rows.push({ source: 'Makefile', tier: parsed.tier, explicitIds: parsed.ids, selectedIds: [...selectedIds].sort(), missingIds, status: missingIds.length ? 'failed' : 'passed', command });
  }
  return rows;
}

const packageJson = JSON.parse(await readFile('package.json', 'utf8'));
const manifest = JSON.parse(await readFile('test/manifest.json', 'utf8'));
const makefileText = await readFile('Makefile', 'utf8');
const runTestsText = await readFile('tools/run_tests.mjs', 'utf8');
const manifestErrors = validateManifest(manifest, { currentRevision: REVISION });
const rows = [...packageRows(packageJson, manifest), ...makefileRows(makefileText, manifest)];
const failedRows = rows.filter((row) => row.status !== 'passed');
const harnessFailClosed = runTestsText.includes('missingExplicitIds') && runTestsText.includes('explicit --id selection matched no task');
const checks = [
  { name: 'manifest-valid', status: manifestErrors.length ? 'failed' : 'passed', errors: manifestErrors },
  { name: 'explicit-id-commands-select-nonempty', status: failedRows.length ? 'failed' : 'passed', failedRows },
  { name: 'run-tests-fails-closed-on-missing-explicit-id', status: harnessFailClosed ? 'passed' : 'failed' }
];
const report = {
  project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
  task_id: 'facility:explicit-id-selection-audit',
  status: checks.every((row) => row.status === 'passed') ? 'passed' : 'failed',
  generatedAt: new Date().toISOString(),
  purpose: 'Audit package and Makefile shortcuts that call run_tests with explicit --id so audit/test commands cannot pass by selecting zero tasks under the requested tier.',
  counts: { explicitRunTestsCommandCount: rows.length, failedCommandCount: failedRows.length },
  checks,
  rows,
  nonClaims: [
    'This audit checks command selection only; it does not execute the selected tests or prove runtime behavior.',
    'This audit does not claim browser behavior, OPFS durability, quota/eviction survival, cross-browser support, or production readiness.'
  ]
};
await mkdir(dirname(outPath), { recursive: true });
await writeFile(outPath, JSON.stringify(report, null, 2) + '\n');
console.log(outPath);
if (report.status !== 'passed') process.exitCode = 1;
