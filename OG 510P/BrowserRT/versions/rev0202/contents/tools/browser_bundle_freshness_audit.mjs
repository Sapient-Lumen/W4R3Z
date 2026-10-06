#!/usr/bin/env node
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const REQUIRED_CURRENT_IDS = Object.freeze([
  'browser:opfs-block-store-raw-composite-abort-signal-proof',
  'browser:opfs-quota-pressure-proof',
  'browser:storage-posture-managed-proof',
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

const DEFAULT_INPUT = `artifacts/validation/${REVISION.toUpperCase()}-BROWSER-OPFS-BLOCK-STORE-RAW-COMPOSITE-ABORT-SIGNAL-RUN.json`;
const DEFAULT_OUT = `artifacts/audit/${REVISION.toUpperCase()}-BROWSER-BUNDLE-FRESHNESS-AUDIT.json`;

function argValue(argv, flag, fallback = null) {
  const i = argv.indexOf(flag);
  return i >= 0 ? argv[i + 1] : fallback;
}

function hasFlag(argv, flag) {
  return argv.includes(flag);
}

function parseMaxAge(argv) {
  const raw = argValue(argv, '--max-age-ms', null);
  if (raw == null) return null;
  const value = Number(raw);
  if (!Number.isFinite(value) || value <= 0) throw new Error(`Bad --max-age-ms: ${raw}`);
  return value;
}

async function readChildReport(path, label) {
  assert.ok(typeof path === 'string' && path.length > 0, `${label} reportPath must be a non-empty string`);
  assert.ok(!path.startsWith('/tmp/') && !path.includes('/tmp/'), `${label} reportPath must be retained evidence, not a deleted tmp path: ${path}`);
  const parsed = JSON.parse(await readFile(path, 'utf8'));
  assert.equal(parsed.project, 'BrowserRT', `${label} child report must identify BrowserRT`);
  assert.equal(parsed.revision, REVISION, `${label} child report revision must match runtime revision`);
  assert.equal(parsed.version, VERSION, `${label} child report version must match runtime version`);
  assert.ok(['passed', 'failed'].includes(parsed.status), `${label} child report status must be terminal`);
  return parsed;
}

export async function runAudit({ input = DEFAULT_INPUT, maxAgeMs = null, requirePassed = true } = {}) {
  const startedAt = Date.now();
  const report = JSON.parse(await readFile(input, 'utf8'));
  const checks = [];

  assert.equal(report.project, 'BrowserRT', 'browser bundle report must identify BrowserRT');
  assert.equal(report.revision, REVISION, 'browser bundle report revision must match runtime revision');
  assert.equal(report.version, VERSION, 'browser bundle report version must match runtime version');
  assert.equal(report.harness, 'BrowserRT browser product bundle runner', 'browser bundle report must come from the bundle runner');
  assert.ok(Number(report.schema) >= 3, `browser bundle report schema must be >=3, got ${report.schema}`);
  assert.notEqual(report.status, 'retained-evidence-not-fresh-browser-execution', 'retained browser placeholder is not fresh execution');
  assert.notEqual(report.status, 'running', 'checkpoint status=running is not a completed green browser-current claim');
  if (requirePassed) assert.equal(report.status, 'passed', 'browser bundle report must be passed');
  checks.push({ label: 'browser-bundle-report-identity', status: 'passed', schema: report.schema, reportStatus: report.status });

  const generatedAt = Date.parse(report.generatedAt || '');
  assert.ok(Number.isFinite(generatedAt), 'browser bundle report generatedAt must be parseable');
  if (maxAgeMs !== null) {
    const ageMs = startedAt - generatedAt;
    assert.ok(ageMs >= 0 && ageMs <= maxAgeMs, `browser bundle report is stale: ageMs=${ageMs}, maxAgeMs=${maxAgeMs}`);
    checks.push({ label: 'browser-bundle-report-age', status: 'passed', ageMs, maxAgeMs });
  }

  assert.ok(Array.isArray(report.tasks), 'browser bundle report must include task rows');
  const taskById = new Map(report.tasks.map((task) => [task.id, task]));
  const missing = REQUIRED_CURRENT_IDS.filter((id) => !taskById.has(id));
  assert.deepEqual(missing, [], `browser bundle report missing current task rows: ${missing.join(', ')}`);
  const failed = REQUIRED_CURRENT_IDS.filter((id) => taskById.get(id)?.status !== 'passed');
  assert.deepEqual(failed, [], `browser bundle report has non-passed current task rows: ${failed.join(', ')}`);
  checks.push({ label: 'browser-current-task-coverage', status: 'passed', taskCount: REQUIRED_CURRENT_IDS.length });

  assert.equal(report.packageReuse?.enabled, true, 'browser-current package-installed proofs must use the bundle-prepared package tarball instead of repacking per task');
  assert.ok(['browser-bundle-shared-runtime-npm-pack', 'browser-bundle-shared-npm-pack', 'prepared-package-tarball'].includes(report.packageReuse?.source), `unexpected browser-current package reuse source: ${report.packageReuse?.source}`);
  const packageValidation = report.packageReuse?.validation || {};
  assert.equal(packageValidation.tarballExists, true, 'prepared package tarball must have existed when the browser bundle was launched');
  assert.equal(packageValidation.filenameMatchesPath, true, 'prepared package filename must match its tarball path');
  assert.equal(packageValidation.packInfoMatchesRoot, true, 'prepared package metadata must match current source package name/version');
  assert.equal(packageValidation.runtimePackageJsonMatchesRootPublicFields, true, 'prepared runtime package.json public fields must match source package.json');
  assert.equal(packageValidation.tarballPackageJsonRuntimeSlim, true, 'prepared runtime package.json must omit cloudtainer-only metadata');
  assert.deepEqual(packageValidation.tarballPackageJsonForbiddenKeys || [], [], 'prepared runtime package.json must not leak cloudtainer-only keys');
  assert.equal(packageValidation.tarballShasumMatchesPackInfo, true, 'prepared package tarball shasum must match npm pack metadata');
  if (packageValidation.tarballIntegrityMatchesPackInfo !== null) assert.equal(packageValidation.tarballIntegrityMatchesPackInfo, true, 'prepared package tarball integrity must match npm pack metadata');
  checks.push({ label: 'browser-package-tarball-reuse', status: 'passed', source: report.packageReuse.source, filename: report.packageReuse.filename || null, validation: packageValidation });

  const childRows = [...(Array.isArray(report.chunks) ? report.chunks.map((row) => ['chunk', row]) : []), ...(Array.isArray(report.batches) ? report.batches.map((row) => ['batch', row]) : [])];
  assert.ok(childRows.length > 0, 'browser-current aggregate must retain child chunk/batch report rows');
  const retainedChildReports = [];
  for (const [kind, row] of childRows) {
    const child = await readChildReport(row.reportPath, `browser-current-${kind}-${row.index}`);
    if (row.status === 'passed') assert.equal(child.status, 'passed', `retained ${kind} report must agree with passed aggregate row`);
    retainedChildReports.push({ kind, index: row.index, path: row.reportPath, status: child.status });
  }
  checks.push({ label: 'browser-child-report-paths-retained', status: 'passed', retainedChildReportCount: retainedChildReports.length, sample: retainedChildReports.slice(0, 6) });

  const body = JSON.stringify(report);
  for (const token of ['package-installed-opfs-abort-consumer', 'package-installed-opfs-abrupt-kill-consumer', 'opfs-block-store-raw-composite-abort-signal', 'opfs-quota-pressure-proof', 'storage-posture-managed-proof']) {
    assert.ok(body.includes(token), `browser bundle report missing proof token ${token}`);
  }
  checks.push({ label: 'browser-risk-proof-tokens-present', status: 'passed' });

  return {
    project: 'BrowserRT',
    revision: REVISION,
    version: VERSION,
    schema: 1,
    status: 'passed',
    audit_id: `${REVISION}-browser-bundle-freshness-audit`,
    input,
    generatedAt: new Date(startedAt).toISOString(),
    reportGeneratedAt: report.generatedAt,
    reportStatus: report.status,
    reportSchema: report.schema,
    passedCount: report.passedCount ?? null,
    failedCount: report.failedCount ?? null,
    chunkCount: report.chunks?.length ?? null,
    batchCount: report.batches?.length ?? null,
    checks,
    nonClaims: ['This audit only proves the aggregate browser-current receipt is fresh, complete, passed, and using the shared runtime-slim package tarball path; it does not add cross-browser, organic eviction, persistent-storage grant, or power-loss durability claims.']
  };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const argv = process.argv.slice(2);
  const out = argValue(argv, '--json', DEFAULT_OUT);
  try {
    const audit = await runAudit({
      input: argValue(argv, '--input', DEFAULT_INPUT),
      maxAgeMs: parseMaxAge(argv),
      requirePassed: !hasFlag(argv, '--allow-nonpassed')
    });
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(audit, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const audit = {
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'failed',
      audit_id: `${REVISION}-browser-bundle-freshness-audit`,
      input: argValue(argv, '--input', DEFAULT_INPUT),
      generatedAt: new Date().toISOString(),
      error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack }
    };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(audit, null, 2) + '\n');
    console.error(out);
    console.error(`[browser_bundle_freshness_audit] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
