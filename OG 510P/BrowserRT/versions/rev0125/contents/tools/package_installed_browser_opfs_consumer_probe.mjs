#!/usr/bin/env node
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-BROWSER-OPFS-CONSUMER-PROBE.json`;
const argValue = (argv, flag, fallback = null) => { const i = argv.indexOf(flag); return i >= 0 ? argv[i + 1] : fallback; };

function run(cmd, args, options = {}) {
  const result = spawnSync(cmd, args, {
    cwd: options.cwd || process.cwd(),
    encoding: 'utf8',
    maxBuffer: 16 * 1024 * 1024,
    env: { ...process.env, npm_config_update_notifier: 'false', npm_config_fund: 'false', npm_config_audit: 'false', ...(options.env || {}) }
  });
  if (result.status !== 0) {
    const err = new Error(`${cmd} ${args.join(' ')} failed with ${result.status}`);
    err.result = { status: result.status, signal: result.signal, stdout: result.stdout, stderr: result.stderr };
    throw err;
  }
  return result;
}

function parseNpmPackJson(stdout) {
  const trimmed = String(stdout || '').trim();
  try { return JSON.parse(trimmed); } catch {}
  const first = trimmed.indexOf('[');
  const last = trimmed.lastIndexOf(']');
  if (first >= 0 && last > first) return JSON.parse(trimmed.slice(first, last + 1));
  throw new Error(`npm pack did not return parseable JSON: ${trimmed.slice(0, 400)}`);
}

const PAGE = `<!doctype html>
<meta charset="utf-8">
<title>BrowserRT installed browser OPFS consumer proof</title>
<script>
  window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ERROR = null;
  window.addEventListener('error', (event) => {
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ERROR = { type: 'error', message: event.message, filename: event.filename, lineno: event.lineno, colno: event.colno };
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason || {};
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ERROR = { type: 'unhandledrejection', message: reason.message || String(reason), stack: reason.stack || null, code: reason.code || null };
  });
</script>
<script type="importmap">
{
  "imports": {
    "browserrt": "/node_modules/browserrt/src/public-api.mjs"
  }
}
</script>
<body>BrowserRT installed browser OPFS consumer proof</body>
<script type="module">
  import * as api from 'browserrt';
  import { runBrowserOpfsProductWedgeWithApi } from '/node_modules/browserrt/examples/browser-opfs-product-wedge-consumer.mjs';

  window.__BROWSERRT_PACKAGE_BROWSER_OPFS_SMOKE = (async () => {
    const report = await runBrowserOpfsProductWedgeWithApi(api, {
      generatedAt: 'deterministic-installed-browser-opfs-package-proof',
      source: 'installed-browser-opfs-package-consumer.html',
      importSpecifier: 'browserrt'
    });
    const payload = {
      project: 'BrowserRT',
      revision: api.REVISION,
      version: api.VERSION,
      schema: 1,
      status: report.status,
      environment: report.receipt.observed.environment,
      importSpecifier: 'browserrt',
      receipt: report.receipt,
      validation: report.validation
    };
    window.__BROWSERRT_PACKAGE_BROWSER_OPFS_REPORT = payload;
    return payload;
  })();
</script>
`;

function browserOpfsExpression(timeoutMs = 20000) {
  return `(async()=>{
    const start = performance.now();
    while (performance.now() - start < ${Number(timeoutMs)}) {
      if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_OPFS_ERROR));
      if (window.__BROWSERRT_PACKAGE_BROWSER_OPFS_SMOKE) {
        const result = await window.__BROWSERRT_PACKAGE_BROWSER_OPFS_SMOKE;
        return JSON.stringify(result);
      }
      await new Promise((resolve)=>setTimeout(resolve, 50));
    }
    throw new Error('Timed out waiting for installed browser OPFS package smoke module');
  })()`;
}

export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-browser-opfs-smoke-'));
  const packDir = join(workspace, 'pack');
  const consumerDir = join(workspace, 'consumer');
  await mkdir(packDir, { recursive: true });
  await mkdir(consumerDir, { recursive: true });
  try {
    const pack = run('npm', ['pack', '--json', '--pack-destination', packDir], { cwd: root });
    const packRows = parseNpmPackJson(pack.stdout);
    const packInfo = packRows[0];
    assert.ok(packInfo?.filename, 'npm pack did not report a filename');
    const tarball = join(packDir, packInfo.filename);
    const fileNames = (packInfo.files || []).map((file) => file.path).sort();
    const requiredTarballFiles = [
      'package.json',
      'src/public-api.mjs',
      'src/browserrt.mjs',
      'src/agent-runtime.mjs',
      'src/browser-agent-worker.mjs',
      'src/opfs-block-store.mjs',
      'src/opfs-web-lock-guarded-block-store.mjs',
      'src/web-lock-coordinator.mjs',
      'src/block-store-lane-adapter.mjs',
      'src/storage-lane-scheduler.mjs',
      'examples/browser-opfs-product-wedge-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing browser OPFS runtime dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    run('npm', ['init', '-y'], { cwd: consumerDir });
    run('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    const installedExample = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'examples', 'browser-opfs-product-wedge-consumer.mjs'), 'utf8');
    assert.match(installedExample, /rt\.storage\.opfsWebLockGuardedBlockStore/, 'installed OPFS product wedge example must use the storage namespace guarded OPFS store');
    assert.match(installedExample, /rt\.core\.spawnAgent/, 'installed OPFS product wedge example must run the browser Worker transform through the core namespace');
    assert.match(installedExample, /persistentGoldenWorkload/, 'installed OPFS product wedge example must assert the persistent golden workload proof');
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));

    const browser = await runManagedBrowserPage({
      root: consumerDir,
      pagePath: '/installed-browser-opfs-consumer.html',
      pageTitle: 'BrowserRT installed browser OPFS consumer proof',
      body: PAGE,
      allowedPrefixes: ['node_modules/browserrt/src/', 'node_modules/browserrt/examples/'],
      timeoutMs: 30000,
      stderrTerms: ['import', 'module', 'worker', 'browserrt', 'opfs', 'lock']
    }, async ({ evalJson, pageState, pageUrl, browserVersion }) => {
      const consumerReport = await evalJson(browserOpfsExpression(22000), 25000);
      assert.equal(consumerReport.status, 'passed', consumerReport.validation?.errors?.join('; '));
      assert.equal(consumerReport.importSpecifier, 'browserrt');
      assert.equal(consumerReport.revision, REVISION);
      assert.equal(consumerReport.version, VERSION);
      assert.equal(consumerReport.environment.isSecureContext, true, 'managed server should provide secure localhost context');
      assert.equal(consumerReport.environment.hasOpfs, true, 'managed Chromium should expose OPFS');
      assert.equal(consumerReport.environment.hasWebLocks, true, 'managed Chromium should expose Web Locks');
      assert.equal(consumerReport.receipt?.proof?.namespacedFacadeUsed, true);
      assert.equal(consumerReport.receipt?.proof?.boundedChannelBackpressure, true);
      assert.equal(consumerReport.receipt?.proof?.workerTransformedChunks, true);
      assert.equal(consumerReport.receipt?.proof?.admissionRejectNoMutation, true);
      assert.equal(consumerReport.receipt?.proof?.guardedStoreAvailable, true);
      assert.equal(consumerReport.receipt?.proof?.persistentGoldenWorkload, true);
      assert.equal(consumerReport.receipt?.proof?.opfsWriteVerified, true);
      assert.equal(consumerReport.receipt?.proof?.opfsReadDigestMatches, true);
      assert.equal(consumerReport.receipt?.proof?.writeBudgetEstimated, true);
      assert.equal(consumerReport.receipt?.proof?.webLocksExercised, true);
      assert.equal(consumerReport.receipt?.proof?.cleanupAttempted, true);
      return { pageUrl, pageState, browserVersion, consumerReport };
    });

    const consumerReport = browser.result.consumerReport;
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-browser-opfs-consumer`,
      purpose: 'Package-installed browser OPFS persistent golden workload proof: npm pack, local install, package-root public API import in managed Chromium, bounded queue, Worker transfer transform, admission no-mutation guard, real OPFS write/verify/read/estimate through WebLockGuardedBlockStore and storage-lane scheduling, lock settlement, cleanup, and receipt validation.',
      package: {
        name: packInfo.name,
        version: packInfo.version,
        filename: packInfo.filename,
        fileCount: fileNames.length,
        unpackedSize: packInfo.unpackedSize,
        requiredTarballFiles,
        requiredTarballFilesPresent: true,
        forbiddenFilesAbsent: true,
        packageRootExport: installedPackageJson.exports?.['.'] || null
      },
      browser: {
        pageUrl: browser.result.pageUrl,
        pageState: browser.result.pageState,
        cdp: browser.harness.cdp,
        requestCount: browser.harness.server?.requestCount ?? null,
        durationMs: browser.harness.durationMs,
        chromeStderrSummary: browser.harness.chromeStderrSummary
      },
      consumer: {
        importSpecifier: consumerReport.importSpecifier,
        status: consumerReport.status,
        environment: consumerReport.environment,
        proof: consumerReport.receipt?.proof || null,
        validation: consumerReport.validation || null,
        channel: consumerReport.receipt?.observed?.channel || null,
        worker: consumerReport.receipt?.observed?.worker || null,
        admission: consumerReport.receipt?.observed?.admission || null,
        storage: consumerReport.receipt?.observed?.storage || null,
        locks: consumerReport.receipt?.observed?.locks || null
      },
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        serve: 'managed Chromium via tools/browser_cdp_fixture.mjs',
        run: 'import-map import browserrt, then run installed browser OPFS persistent golden workload example'
      },
      nonClaims: [
        'Managed Chromium OPFS/Web Locks package smoke only; it does not prove registry publication, bundler compatibility, cross-browser behavior, organic quota pressure, eviction, fsync durability, abrupt crash recovery, multi-tab fairness, or production readiness.',
        'The proof uses one same-origin browser profile and cleans up its OPFS prefix after the write/read receipt.'
      ]
    });
  } finally {
    await rm(workspace, { recursive: true, force: true });
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const out = argValue(process.argv.slice(2), '--json', DEFAULT_OUT);
  try {
    const report = await runProbe();
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.log(out);
  } catch (error) {
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-browser-opfs-consumer`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_browser_opfs_consumer_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
