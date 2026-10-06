#!/usr/bin/env node
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { REVISION, VERSION } from '../src/browserrt.mjs';

const PREFIX = `REV${REVISION.slice(3)}`;
const DEFAULT_OUT = `artifacts/audit/${PREFIX}-RELEASE-CHUNK-RUNNER-CONTRACT-AUDIT.json`;
function argValue(argv, flag, fallback = null) { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; }
async function readText(path) { return await readFile(path, 'utf8'); }
async function readJson(path) { return JSON.parse(await readText(path)); }
function check(name, passed, detail = {}) { return { name, status: passed ? 'passed' : 'failed', ...detail }; }
function taskIds(manifest, tier = 'release') { return (manifest.tasks || []).filter((task) => (task.tiers || []).includes(tier)).map((task) => task.id).sort(); }

async function runAudit() {
  const runner = await readText('tools/run_release_chunks.mjs');
  const packager = await readText('tools/package_release.py');
  const packageJson = await readJson('package.json');
  const manifest = await readJson('test/manifest.json');
  const impactMap = await readJson('test/impact-map.json');
  const releaseIds = taskIds(manifest, 'release');
  const auditIds = taskIds(manifest, 'audit');
  const manifestTask = (manifest.tasks || []).find((task) => task.id === 'facility:release-chunk-runner-contract-audit');
  const impactRule = (impactMap.rules || []).find((rule) => rule.id === 'impact:release-chunk-runner');
  const scripts = packageJson.scripts || {};
  const checks = [
    check('runner-has-shard-interface', runner.includes('--shards') && runner.includes('--chunk-dir') && runner.includes('--json'), { runner: 'tools/run_release_chunks.mjs' }),
    check('runner-delegates-to-run-tests-shards', runner.includes('tools/run_tests.mjs') && runner.includes('--shard') && runner.includes('--quiet') && runner.includes('--json'), { runner: 'tools/run_release_chunks.mjs' }),
    check('runner-aggregates-coverage', runner.includes('missingTaskIds') && runner.includes('unexpectedTaskIds') && runner.includes('duplicateTaskIds') && runner.includes('expectedTaskCount'), { runner: 'tools/run_release_chunks.mjs' }),
    check('runner-uses-spawnsync-with-timeout', runner.includes('spawnSync') && runner.includes('timeout: timeoutMs') && runner.includes('--chunk-timeout-ms'), { runner: 'tools/run_release_chunks.mjs' }),
    check('runner-uses-quiet-stdio-ignore', runner.includes("stdio: quiet ? 'ignore'"), { runner: 'tools/run_release_chunks.mjs' }),
    check('runner-isolates-shard-workspaces', runner.includes('prepareChunkWorkspace') && runner.includes('isolateWorkspaces') && runner.includes('browserrt-release-chunks'), { runner: 'tools/run_release_chunks.mjs' }),
    check('runner-can-aggregate-materialized-chunks', runner.includes('--aggregate-only') && runner.includes('missing chunk report') && runner.includes('aggregateOnly'), { runner: 'tools/run_release_chunks.mjs' }),
    check('runner-writes-compatible-release-report', runner.includes("harness: 'BrowserRT cloudtainer release chunk runner'") && runner.includes('schema: 2') && runner.includes('tasks,') && runner.includes('timingSummary'), { runner: 'tools/run_release_chunks.mjs' }),
    check('package-release-uses-chunk-runner', packager.includes("tools/run_release_chunks.mjs") && packager.includes('TEST-HARNESS-RUN.json'), { packager: 'tools/package_release.py' }),
    check('package-release-preserves-linked-revision-filename', packager.includes('--linked-revision') && packager.includes('archive_revision') && packager.includes('runtimeRevision') && packager.includes('runtimeVersion'), { packager: 'tools/package_release.py' }),
    check('package-release-compacts-chunk-runner-evidence', packager.includes("parsed.get('releaseChunkRunner')") && packager.includes('missingTaskCount') && packager.includes('duplicateTaskCount'), { packager: 'tools/package_release.py' }),
    check('package-script-registered', scripts['test:release:chunks']?.includes('tools/run_release_chunks.mjs') && scripts['audit:release-chunk-runner']?.includes('tools/release_chunk_runner_contract_audit.mjs'), { scripts: ['test:release:chunks', 'audit:release-chunk-runner'] }),
    check('manifest-audit-task-nonrecursive', Boolean(manifestTask) && (manifestTask.tiers || []).includes('audit') && !(manifestTask.tiers || []).includes('release') && (manifestTask.inputs || []).includes('tools/run_release_chunks.mjs'), { taskId: manifestTask?.id || null, tiers: manifestTask?.tiers || null }),
    check('impact-route-present', Boolean(impactRule) && (impactRule.taskIds || []).includes('facility:release-chunk-runner-contract-audit') && (impactRule.globs || []).includes('tools/run_release_chunks.mjs'), { impactRule: impactRule?.id || null }),
    check('release-tier-has-substance', releaseIds.length >= 200, { releaseTaskCount: releaseIds.length }),
    check('audit-tier-covers-runner', auditIds.includes('facility:release-chunk-runner-contract-audit'), { auditTaskCount: auditIds.length }),
  ];
  const failed = checks.filter((row) => row.status !== 'passed');
  return {
    project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1,
    audit_id: 'facility:release-chunk-runner-contract-audit',
    status: failed.length ? 'failed' : 'passed',
    generatedAt: new Date().toISOString(),
    purpose: 'Ensure broad release validation has a bounded chunked orchestrator that preserves release task coverage without relying on a monolithic cloudtainer command.',
    checks,
    releaseTaskCount: releaseIds.length,
    nonClaims: [
      'This audit verifies release-harness orchestration and task coverage, not BrowserRT runtime correctness by itself.',
      'Chunking does not claim cross-browser, OPFS quota/eviction, crash-durability, Web Locks fairness, or performance guarantees.'
    ],
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
