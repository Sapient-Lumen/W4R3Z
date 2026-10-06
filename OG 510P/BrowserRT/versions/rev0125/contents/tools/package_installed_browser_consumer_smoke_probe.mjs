#!/usr/bin/env node
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { tmpdir } from 'node:os';
import { REVISION, VERSION } from '../src/public-api.mjs';
import { runManagedBrowserPage } from './browser_cdp_fixture.mjs';

const DEFAULT_OUT = `artifacts/validation/REV${REVISION.slice(3)}-PACKAGE-INSTALLED-BROWSER-CONSUMER-SMOKE-PROBE.json`;
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
<title>BrowserRT installed browser consumer smoke</title>
<script>
  window.__BROWSERRT_PACKAGE_BROWSER_ERROR = null;
  window.addEventListener('error', (event) => {
    window.__BROWSERRT_PACKAGE_BROWSER_ERROR = { type: 'error', message: event.message, filename: event.filename, lineno: event.lineno, colno: event.colno };
  });
  window.addEventListener('unhandledrejection', (event) => {
    const reason = event.reason || {};
    window.__BROWSERRT_PACKAGE_BROWSER_ERROR = { type: 'unhandledrejection', message: reason.message || String(reason), stack: reason.stack || null };
  });
</script>
<script type="importmap">
{
  "imports": {
    "browserrt": "/node_modules/browserrt/src/public-api.mjs"
  }
}
</script>
<body>BrowserRT installed browser consumer smoke</body>
<script type="module">
  import * as api from 'browserrt';
  import { runProductWedgeWithApi } from '/node_modules/browserrt/examples/product-wedge-consumer.mjs';

  window.__BROWSERRT_PACKAGE_BROWSER_SMOKE = (async () => {
    const report = await runProductWedgeWithApi(api, {
      generatedAt: 'deterministic-installed-browser-package-smoke',
      source: 'installed-browser-package-consumer.html',
      importSpecifier: 'browserrt'
    });
    const payload = {
      project: 'BrowserRT',
      revision: api.REVISION,
      version: api.VERSION,
      schema: 1,
      status: report.status,
      environment: {
        crossOriginIsolated: globalThis.crossOriginIsolated === true,
        isSecureContext: globalThis.isSecureContext === true,
        hasWorker: typeof Worker === 'function',
        hasImportMap: true
      },
      importSpecifier: 'browserrt',
      receipt: report.receipt,
      validation: report.validation
    };
    window.__BROWSERRT_PACKAGE_BROWSER_REPORT = payload;
    return payload;
  })();
</script>
`;

function browserSmokeExpression(timeoutMs = 10000) {
  return `(async()=>{
    const start = performance.now();
    while (performance.now() - start < ${Number(timeoutMs)}) {
      if (window.__BROWSERRT_PACKAGE_BROWSER_ERROR) throw new Error(JSON.stringify(window.__BROWSERRT_PACKAGE_BROWSER_ERROR));
      if (window.__BROWSERRT_PACKAGE_BROWSER_SMOKE) {
        const result = await window.__BROWSERRT_PACKAGE_BROWSER_SMOKE;
        return JSON.stringify(result);
      }
      await new Promise((resolve)=>setTimeout(resolve, 50));
    }
    throw new Error('Timed out waiting for installed browser package smoke module');
  })()`;
}

export async function runProbe() {
  const root = process.cwd();
  const workspace = await mkdtemp(join(tmpdir(), 'browserrt-package-browser-smoke-'));
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
      'src/product-wedge.mjs',
      'src/browserrt.mjs',
      'src/browser-agent-worker.mjs',
      'src/block-store-lane-adapter.mjs',
      'examples/product-wedge-consumer.mjs'
    ];
    const missingTarballFiles = requiredTarballFiles.filter((name) => !fileNames.includes(name));
    assert.deepEqual(missingTarballFiles, [], `npm package missing browser runtime dependency files: ${missingTarballFiles.join(', ')}`);
    const forbiddenPrefixes = ['artifacts/', 'tools/', 'test/', 'node_modules/'];
    const forbiddenFiles = fileNames.filter((name) => forbiddenPrefixes.some((prefix) => name.startsWith(prefix)));
    assert.deepEqual(forbiddenFiles, [], `npm package leaked development-only files: ${forbiddenFiles.slice(0, 12).join(', ')}`);

    run('npm', ['init', '-y'], { cwd: consumerDir });
    run('npm', ['install', '--ignore-scripts', '--no-audit', '--no-fund', tarball], { cwd: consumerDir });
    const installedExample = await readFile(join(consumerDir, 'node_modules', 'browserrt', 'examples', 'product-wedge-consumer.mjs'), 'utf8');
    assert.match(installedExample, /typeof process !== 'undefined'/, 'browser-importable example must guard the Node CLI process check');
    const installedPackageJson = JSON.parse(await readFile(join(consumerDir, 'node_modules', 'browserrt', 'package.json'), 'utf8'));

    const browser = await runManagedBrowserPage({
      root: consumerDir,
      pagePath: '/installed-browser-consumer.html',
      pageTitle: 'BrowserRT installed browser consumer smoke',
      body: PAGE,
      allowedPrefixes: ['node_modules/browserrt/src/', 'node_modules/browserrt/examples/'],
      timeoutMs: 20000,
      stderrTerms: ['import', 'module', 'worker', 'browserrt']
    }, async ({ evalJson, pageState, pageUrl, browserVersion }) => {
      const consumerReport = await evalJson(browserSmokeExpression(12000), 15000);
      assert.equal(consumerReport.status, 'passed');
      assert.equal(consumerReport.importSpecifier, 'browserrt');
      assert.equal(consumerReport.revision, REVISION);
      assert.equal(consumerReport.version, VERSION);
      assert.equal(consumerReport.environment.crossOriginIsolated, true, 'managed server should enable COOP/COEP isolation');
      assert.equal(consumerReport.environment.hasWorker, true);
      assert.equal(consumerReport.receipt?.proof?.workerAgentRoundTrip, true);
      assert.equal(consumerReport.receipt?.proof?.transferDetached, true);
      assert.equal(consumerReport.receipt?.proof?.storageLaneWriteRead, true);
      return { pageUrl, pageState, browserVersion, consumerReport };
    });

    const consumerReport = browser.result.consumerReport;
    return Object.freeze({
      project: 'BrowserRT',
      revision: REVISION,
      version: VERSION,
      schema: 1,
      status: 'passed',
      probe_id: `${REVISION}-package-installed-browser-consumer-smoke`,
      purpose: 'Package-installed browser consumer smoke: npm pack, local install, import-map package-root import in managed Chromium, module Worker spawn from installed package files, transfer detachment, storage-lane write/read, and receipt validation.',
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
        traceKinds: consumerReport.receipt?.traceKinds || []
      },
      commands: {
        pack: 'npm pack --json --pack-destination <tmp>',
        install: `npm install --ignore-scripts --no-audit --no-fund ${packInfo.filename}`,
        serve: 'managed Chromium via tools/browser_cdp_fixture.mjs',
        run: 'import-map import browserrt from installed package files'
      },
      nonClaims: [
        'Managed Chromium and import-map smoke only; it does not prove bundler compatibility, registry publication, cross-browser behavior, OPFS quota/eviction, fsync durability, or crash recovery.',
        'The product wedge storage path remains memory-backed; dedicated OPFS/Web Locks browser proofs remain separate explicit tasks.'
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
    const report = { project: 'BrowserRT', revision: REVISION, version: VERSION, schema: 1, status: 'failed', probe_id: `${REVISION}-package-installed-browser-consumer-smoke`, error: { name: error?.name || 'Error', message: error?.message || String(error), stack: error?.stack, command: error?.result || null } };
    await mkdir(dirname(out), { recursive: true });
    await writeFile(out, JSON.stringify(report, null, 2) + '\n');
    console.error(out);
    console.error(`[package_installed_browser_consumer_smoke_probe] FAIL: ${error?.stack || error}`);
    process.exitCode = 1;
  }
}
